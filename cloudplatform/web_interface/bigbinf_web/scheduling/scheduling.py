from bigbinf_web.lib.docker_remote import *
from bigbinf_web.lib.kubernetes_remote import *
from Queue import Queue
from bigbinf_web.config import config
from bigbinf_web.config import job_config
from uuid import uuid4
from threading import Thread, Lock, Condition
from job import Job
from datetime import datetime
from collections import deque
import time
import json
import copy


class BuildScheduler(Thread):
	"""Schedules dockerfiles to be built"""
	def __init__(self, build_queue, ready_queue):
		super(BuildScheduler, self).__init__(group=None, target=None, name=None, verbose=None)
		self.build_queue = build_queue
		self.ready_queue = ready_queue

	def build_image(self, job):
		"""build image from dockerfile"""
		response = remote_build(job.job_file, job.builder_url, job.registry_url, job.image_name)
		# close file to flush from memory as soon as its been sent
		job.job_file.close()
		for line in response:
			build_status = line
			#print(line)


		build_success_str = 'Successfully built'
		if not build_success_str in build_status:
			return False
		return True

	def push_image(self, job):
		"""push image to the private registry"""
		response = remote_push_registry(job.builder_url, job.registry_url, job.image_name)
		response = list(response)
		for line in response:
			#print(line)
			pass
		push_success_str = 'Image successfully pushed'
		if not push_success_str in response[-2]:
			return False
		return True

	def run(self):
		while True:
			try:
				job = self.build_queue.get(block=True)
				print('found a job to build')
				success = self.build_image(job)
				if success:
					success = self.push_image(job)
				if success:
					self.build_queue.task_done()
					job.status = 'ready'
					print('build successful')
					self.ready_queue.put(job)

					print 'ready queue size:', self.ready_queue.qsize()
			except Exception as e:
				print e


class RunQueue(object):
	def __init__(self, maxsize, ready_queue):
		self.maxsize = maxsize
		self.size = 0
		self.ready_queue = ready_queue
		self.queue = {}
		self.mutex = Lock()
		self.mutex2 = Lock()
		self.not_full = Condition(self.mutex)

	def list_queue(self):
		with self.mutex:
			return self.queue.values()

	def put(self, job):
		with self.mutex:
			self.queue[job.image_name] = job

	def remove(self, job_name):
		with self.mutex:
			if self.queue.get(job_name, None):
				print 'removing job:', job_name
				del self.queue[job_name]
				self.size -= 1
				self.not_full.notify()

	def new_job(self):
		""""
		the not_full threading condition waits until a slot is available on the running queue.
		this function is only called by one thread from the run scheduler so it does not need to 
		be synchronized. only mutation on the queue must be synchronized which is handled in the other
		methods.
		"""
		with self.not_full:
			while self.size >= self.maxsize:
				self.not_full.wait()
		job = self.ready_queue.get(block=True)
		print 'new job:', job.image_name
		self.ready_queue.task_done()
		job.status = 'running'
		self.put(job)
		self.size += 1
		return job


class RunScheduler(Thread):
	"""schedules built images to be executed"""
	def __init__(self, ready_queue, running_queue):
		super(RunScheduler, self).__init__(group=None, target=None, name=None, verbose=None)
		self.ready_queue = ready_queue
		self.running_queue = running_queue

	def run_job(self, job):
		"""run job by creating a k8s pod from the template"""
		k8s_url = 'http://%s:%s' % (config.kubernetes_host, config.kubernetes_port)
		registry_url = '%s:%s' % (config.node_registry_host, config.registry_port)
		image_name = '%s/%s' % (registry_url, job.image_name)
		pod_config = copy.deepcopy(job_config.pod)


		pod_config['metadata']['name'] = job.image_name
		pod_config['spec']['containers'][0]['name'] = job.image_name
		pod_config['spec']['containers'][0]['image'] = image_name
		pod_config['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = job.datapath
		pod_config['spec']['containers'][0]['volumeMounts'][1]['mountPath'] = job.resultspath
		pod_config['spec']['volumes'][0]['hostPath']['path'] = config.rawdata_hostpath
		pod_config['spec']['volumes'][1]['hostPath']['path'] = config.results_hostpath


		

		if job.datapath is None:
			if job.resultspath is None:
				del pod_config['spec']['containers'][0]['volumeMounts']
				del pod_config['spec']['volumes']
			else:
				del pod_config['spec']['containers'][0]['volumeMounts'][0]
				del pod_config['spec']['volumes'][0]
		elif job.resultspath is None:
			del pod_config['spec']['containers'][0]['volumeMounts'][1]
			del pod_config['spec']['volumes'][1]


		print pod_config
		pod_config = json.dumps(pod_config)
		create_pod(k8s_url, pod_config)
		return True

	def run(self):
		while True:
			try:
				job = self.running_queue.new_job()
				success = self.run_job(job)	
				print 'running job'
			except Exception as e:
				print e
			

class JobWatcher(Thread):
	"""This class watches a kubernetes stream to see when jobs complete 
	and removes completed jobs from the running queue"""

	def __init__(self, running_queue):
			super(JobWatcher, self).__init__(group=None, target=None, name=None, verbose=None)
			self.running_queue = running_queue

	def run(self):
		try:
			k8s_url = 'http://%s:%s' % (config.kubernetes_host, config.kubernetes_port)
			stream = watch_pods(k8s_url, config.job_label)
			for event in stream.iter_lines():
				event = json.loads(event)
				job_name = event['object']['metadata']['name']
				job_state = event['object']['status']
				#print json.dumps(job_state, indent=4)

				if job_state['phase'] == 'Succeeded':
					delete_pod(k8s_url, job_name)
					self.running_queue.remove(job_name)
		except Exception as e:
			print e

		
build_queue = Queue()
ready_queue = Queue()
running_queue = RunQueue(config.num_worker_nodes, ready_queue)


def add_job(file, datapath, resultspath):
	builder_url = '%s:%s' % (config.builder_host, config.builder_port)
	registry_url = '%s:%s' % (config.registry_host, config.registry_port)
	image_name = str(uuid4())
	timestamp = datetime.now()
	job = Job(file, builder_url, registry_url, image_name, timestamp, datapath, resultspath)
	job.status = 'build'
	build_queue.put(job)

	print('added job to build queue')


def get_schedule():
	schedule =  list(build_queue.queue)
	schedule.extend(list(ready_queue.queue))
	schedule.extend(running_queue.list_queue())

	return schedule

build_scheduler = BuildScheduler(build_queue, ready_queue)
build_scheduler.daemon = True
build_scheduler.start()

run_scheduler = RunScheduler(ready_queue, running_queue)
run_scheduler.daemon = True
run_scheduler.start()

job_watcher = JobWatcher(running_queue)
job_watcher.daemon = True
job_watcher.start()