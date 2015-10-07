FROM gcr.io/google_containers/hyperkube:v1.0.1

ADD ceph_pgp.key /ceph_pgp.key
RUN cat /ceph_pgp.key | apt-key add -
RUN echo deb http://ceph.com/debian/ wheezy  main | tee /etc/apt/sources.list.d/ceph.list
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y \
	&& DEBIAN_FRONTEND=noninteractive apt-get -yy install ceph-common

COPY master.json /etc/kubernetes/manifests/master.json