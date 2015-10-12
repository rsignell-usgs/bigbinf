#!/bin/bash
# kill and remove kubernetes containers
docker ps | awk '{ print $1,$2 }' | grep gcr.io | awk '{print $1 }' | xargs -I {} docker kill {}
docker ps | awk '{ print $1,$2 }' | grep bigbinf | awk '{print $1 }' | xargs -I {} docker kill {}
docker ps | awk '{ print $1,$2 }' | grep kubernetes | awk '{print $1 }' | xargs -I {} docker kill {}

docker ps -a | awk '{ print $1,$2 }' | grep gcr.io | awk '{print $1 }' | xargs -I {} docker rm {}

docker ps | awk '{ print $1,$2 }' | grep kubernetes | awk '{print $1 }' | xargs -I {} docker rm {}
docker ps -a | awk '{ print $1,$2 }' | grep bigbinf  | awk '{print $1 }' | xargs -I {} docker rm {}
