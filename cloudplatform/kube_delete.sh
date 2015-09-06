#!/bin/bash
# kill and remove kubernetes containers
docker ps | awk '{ print $1,$2 }' | grep gcr.io | awk '{print $1 }' | xargs -I {} docker kill {}

docker ps -a | awk '{ print $1,$2 }' | grep gcr.io | awk '{print $1 }' | xargs -I {} docker rm {}
