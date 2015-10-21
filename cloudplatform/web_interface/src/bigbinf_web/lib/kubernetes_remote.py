from pykube.http import HTTPClient

def create_pod(host, pod_config):
	k8s_client = HTTPClient(host)

	response = k8s_client.post(url='/pods', data=pod_config)
	#print(response.content)


def watch_pods(host, labelSelector):
	k8s_client = HTTPClient(host)
	params = {"labelSelector": labelSelector, "watch": "true"}
	response = k8s_client.get(url='/pods', params=params, stream=True)
	return response

def delete_pod(host, pod_name):
	k8s_client = HTTPClient(host)
	url = '%s/%s' % ('/pods', pod_name)
	response = k8s_client.delete(url=url)
	return response