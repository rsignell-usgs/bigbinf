import requests

def get_clouds(host):
	url = '%s/%s' % (host, 'getclouds')
	r = requests.get(url)

	return r.text