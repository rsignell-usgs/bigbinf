from docker import Client

def remote_build(jobfile, builder_url, registry_url, imagename):
	c = Client(base_url=builder_url)
	tag = '%s/%s' % (registry_url, imagename)
	response = c.build(fileobj=jobfile, tag=tag, custom_context=True, stream=True)
	return response
		

def remote_push_registry(builder_url, registry_url, imagename):
	c = Client(base_url=builder_url)
	tag = '%s/%s' % (registry_url, imagename)
	response = c.push(tag, stream=True)
	return response
