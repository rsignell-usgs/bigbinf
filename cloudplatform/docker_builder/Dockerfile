FROM ubuntu:14.04.3

# Let's start with some basic stuff.
RUN apt-get update -qq && apt-get install -qqy \
    apt-transport-https \
    ca-certificates \
    curl \
    lxc \
    iptables
    
# Install Docker from Docker Inc. repositories.
RUN curl -sSL https://get.docker.com/ubuntu/ | sh

# Install the magic wrapper.
ADD ./wrapdocker /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker

#ADD ./registry.crt /etc/docker/certs.d/10.0.0.47:5000/ca.crt

# Define additional metadata for our image.
VOLUME /var/lib/docker

CMD ["wrapdocker"]
