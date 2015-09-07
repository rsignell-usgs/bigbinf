FROM ubuntu:14.04.3
MAINTAINER Brendan Ball

RUN sudo apt-get update
RUN sudo apt-get -y install curl

RUN curl -sSL https://get.docker.com/ | sh

RUN apt-get update -qq && apt-get install -qqy \
    apt-transport-https \
    ca-certificates \
    curl \
    lxc \
    iptables

ADD ./wrapdocker.sh /usr/local/bin/wrapdocker
RUN chmod +x /usr/local/bin/wrapdocker

VOLUME /var/lib/docker
CMD ["wrapdocker"]