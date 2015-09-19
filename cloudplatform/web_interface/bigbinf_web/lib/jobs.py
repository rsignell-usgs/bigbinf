

class Job:
	def __init__(self, file, builder_url, registry_url, image_name):
		self.job_file 		= file
		self.builder_url 	= builder_url
		self.registry_url 	= registry_url
		self.image_name 	= image_name
		self.user			= None
