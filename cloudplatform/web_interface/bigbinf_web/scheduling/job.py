from flask.json import JSONEncoder


class Job:
	def __init__(self, file, builder_url, registry_url, image_name, timestamp):
		self.job_file = file
		self.builder_url = builder_url
		self.registry_url = registry_url
		self.image_name = image_name
		self.user = 'user1'
		self.timestamp = timestamp
		self.status = 'init'


class ExtendedJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Job):
            return {'job':{
                'user': obj.user, 
                'timestamp': obj.timestamp,
                'status': obj.status,
                }
            }
        return super(ExtendedJsonEncoder, self).default(obj)