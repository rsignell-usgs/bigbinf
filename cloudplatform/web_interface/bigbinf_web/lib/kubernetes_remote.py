from pykube.http import HTTPClient

def create_pod(host, pod_config):
	k8s_client = HTTPClient(host)

	response = k8s_client.post(url='/pods', data=pod_config)
	print(response.content)
