#!/bin/bash

image_name=$1
CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")

docker build -t ${image_name}:${CURRENT_DATE} -f dockerfiles/${image_name}.Dockerfile .
docker tag ${image_name}:${CURRENT_DATE} sjafari2/kafka${image_name}:latest
docker push sjafari2/kafka${image_name}:latest
