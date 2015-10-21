To create the cluster you must first build the necessary docker images.
Docker images to build:
* docker_builder
* docker_k8s
* docker_registry
* discovery_service
* web_interface

Go to each of the above directories and run `make` to build the images

##Creating the cluster
Start by running the `kube_local_up.sh` script.
This starts the kubernetes 1 node local cluster.
Once it is running you can use the kubectl CLI by downloading it ([kubectl](https://storage.googleapis.com/kubernetes-release/release/v1.0.1/bin/linux/amd64/kubectl)).
`kubectl` is used to create the pods.
run `kubectl create -f /cluster_up` to create the required pods and services.
Lastly run `webui.sh` to start the containerized web interface. 

The web interface is unfortunately not running inside kubernetes because it needs to access the kubernetes REST API and I was unable to get this working from within kubernetes.

The web interface should be available on port 5001.

##Run Job
You can only submit a job by a tar archived dockerfile. The archive should contain any source code that is added using the dockerfile.

The web page gives text input for a data path and results path. These are the respective mount points inside the job container. The raw data that is mounted is fixed for this proof of concept.

##Dockerfiles
To learn how to create a dockerfile go to [Dockerfiles](https://docs.docker.com/reference/builder/)