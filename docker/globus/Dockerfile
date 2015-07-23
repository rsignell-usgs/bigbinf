FROM phusion/baseimage
MAINTAINER wraith.andrew@gmail.com

# Download and install the globus toolkit
RUN apt-get update
RUN apt-get install -y wget
WORKDIR /tmp
RUN wget http://www.globus.org/ftppub/gt6/installers/repo/globus-toolkit-repo_latest_all.deb
RUN dpkg -i globus-toolkit-repo_latest_all.deb
RUN apt-get update
RUN apt-get install -y \
globus-gram5 \
globus-gridftp \
globus-gsi \
myproxy \
myproxy-admin \
myproxy-server

# Set up the certs for myproxy
RUN install -o myproxy -m 644 \
/etc/grid-security/hostcert.pem \
/etc/grid-security/myproxy/hostcert.pem
RUN install -o myproxy -m 600 \
/etc/grid-security/hostkey.pem \
/etc/grid-security/myproxy/hostkey.pem

# Set up the config for myproxy
ADD myproxy-server.config /etc/

# Add the myproxy user to the simpleca group so that the myproxy server can create certificates
RUN usermod -a -G simpleca myproxy

# Set up env variables for myproxy
RUN echo "/etc/grid-security/myproxy/hostcert.pem" > /etc/container_environment/X509_USER_CERT
RUN echo "/etc/grid-security/myproxy/hostkey.pem" > /etc/container_environment/X509_USER_KEY
RUN echo `grid-cert-info -subject -file /etc/grid-security/hostcert.pem` > /etc/container_environment/MYPROXY_SERVER_DN 

# Set up the myproxy user
ADD setup_user.sh /etc/my_init.d/01_setup_user.sh
# Set up the runit daemon scripts
ADD run_myproxy.sh /etc/my_init.d/02_run_myproxy.sh
ADD run_globus.sh /etc/my_init.d/03_run_globus.sh

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
WORKDIR /

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]
