from bigbinf_web.lib.docker_remote import *
from bigbinf_web.lib.kubernetes_remote import *
from Queue import Queue
from bigbinf_web.config import config
from bigbinf_web.config import job_config
from uuid import uuid4
from threading import Thread
from job import Job
from datetime import datetime
from collections import deque
import time
import json
import copy

build_queue = Queue()
ready_queue = Queue()
running_queue = deque()


class BuildScheduler(Thread):
	def __init__(self, build_queue, ready_queue):
		super(BuildScheduler, self).__init__(group=None, target=None, name=None, verbose=None)
		self.build_queue = build_queue
		self.ready_queue = ready_queue

	def build_image(self, job):
		response = remote_build(job.job_file, job.builder_url, job.registry_url, job.image_name)
		# close file to flush from memory as soon as its been sent
		job.job_file.close()
		for line in response:
			build_status = line
			print(line)

		build_success_str = 'Successfully built'
		if not build_success_str in build_status:
			return False
		return True

	def push_image(self, job):
		response = remote_push_registry(job.builder_url, job.registry_url, job.image_name)
		response = list(response)
		for line in response:
			print(line)
		push_success_str = 'Image successfully pushed'
		if not push_success_str in response[-2]:
			return False
		return True

	def run(self):
		while True:
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


class RunScheduler(Thread):
	def __init__(self, ready_queue, running_queue):
		super(RunScheduler, self).__init__(group=None, target=None, name=None, verbose=None)
		self.ready_queue = ready_queue
		self.running_queue = running_queue

	def run_job(self, job):
		k8s_url = 'http://%s:%s' % (config.kubernetes_host, config.kubernetes_port)
		registry_url = '%s:%s' % (config.node_registry_host, config.registry_port)
		image_name = '%s/%s' % (registry_url, job.image_name)
		pod_config = copy.deepcopy(job_config.pod)
		pod_config['metadata']['name'] = job.image_name
		pod_config['spec']['containers'][0]['name'] = job.image_name
		pod_config['spec']['containers'][0]['image'] = image_name
		print(pod_config)
		pod_config = json.dumps(pod_config)
		create_pod(k8s_url, pod_config)
		#print('running job')
		#time.sleep(10)
		return True

	def run(self):
		while True:
			job = self.ready_queue.get(block=True)
			self.ready_queue.task_done()
			self.running_queue.append(job)
			job.status = 'running'
			success = self.run_job(job)	
			if success:
				self.running_queue.remove(job)
				job.status = 'complete'



def add_job(file):
	builder_url = '%s:%s' % (config.builder_host, config.builder_port)
	registry_url = '%s:%s' % (config.registry_host, config.registry_port)
	image_name = str(uuid4())
	timestamp = datetime.now()
	job = Job(file, builder_url, registry_url, image_name, timestamp)
	job.status = 'build'
	build_queue.put(job)

	print('added job to build queue')


def get_schedule():
	schedule =  list(build_queue.queue)
	schedule.extend(list(ready_queue.queue))
	schedule.extend(running_queue)

	return schedule

build_scheduler = BuildScheduler(build_queue, ready_queue)
build_scheduler.daemon = True
build_scheduler.start()

run_scheduler = RunScheduler(ready_queue, running_queue)
run_scheduler.daemon = True
run_scheduler.start()