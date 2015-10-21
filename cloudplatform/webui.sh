#!/bin/bash
# Run the containerized web interface. it needs access to the RBD storage to create result folders.
# It needs to run in the host network to access the kubernetes API. I haven't been able to access
# the kubernetes API from within a kubernetes pod
docker run --net=host  -v /mnt:/mnt -d bigbinf/web-ui