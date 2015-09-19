from bigbinf_web.lib.docker_remote import *
from Queue import Queue
from bigbinf_web import config
from bigbinf_web.lib.jobs import Job
from uuid import uuid4
from threading import Thread


build_queue = Queue()
run_queue 	= Queue()

def add_job(file):
	builder_url = '%s:%s' % (config.builder_host, config.builder_port)
	registry_url = '%s:%s' % (config.registry_host, config.registry_port)
	image_name = str(uuid4())

	job = Job(file, builder_url, registry_url, image_name)

	build_queue.put(job)
	print 'added to build queue'


class BuildScheduler(Thread):
	def __init__(self, build_queue, run_queue):
		super(BuildScheduler,self).__init__(group=None, target=None, name=None, verbose=None)
		self.build_queue = build_queue
		self.run_queue = run_queue
		print('hellow build build_scheduler')
	

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
			success = self.build_image(job)
			if success:
				success = self.push_image(job)
			if success:
				self.build_queue.task_done()


build_scheduler = BuildScheduler(build_queue, run_queue)
build_scheduler.daemon = True
build_scheduler.start()