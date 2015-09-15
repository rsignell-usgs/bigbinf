#!/bin/bash
# Create a local kubernetes cluster with one node via dockerized kubernetes.

set -e

# Make sure docker daemon is running
if ( ! ps -ef | grep "/usr/bin/docker" | grep -v 'grep' &> /dev/null ); then
    echo "Docker is not running on this machine!"
    exit 1
fi

echo "Starting ectd container"
docker run --net=host -d gcr.io/google_containers/etcd:2.0.12 /usr/local/bin/etcd --addr=127.0.0.1:4001 --bind-addr=0.0.0.0:4001 --data-dir=/var/etcd/data

echo "Starting master kube"
# to allow docker in docker we have to allow privileged in kubernetes. This however requires to modify the manifest specified in --config below which is bundled with the image.
# to get around this we modify the manifest and volume mount it to replace the bundled manifest.
docker run --privileged --net=host -d -v /var/run/docker.sock:/var/run/docker.sock  \
-v `pwd`/manifests:/etc/kubernetes/manifests \
gcr.io/google_containers/hyperkube:v1.0.1 /hyperkube kubelet --api-servers=http://localhost:8080 \
--v=2 --address=0.0.0.0 --allow-privileged=true --enable-server --hostname-override=127.0.0.1 --config=/etc/kubernetes/manifests

echo "Starting service proxy"
docker run -d --net=host --privileged gcr.io/google_containers/hyperkube:v1.0.1 /hyperkube proxy --master=http://127.0.0.1:8080 --v=2