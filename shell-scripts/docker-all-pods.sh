#!/bin/bash

# Define an array of pod names
pod_names=("request" "producer" "consumer" "merge")

#docker_path="/Users/soheila/PycharmProjects/pipelineProject/RealTime-Streaming-Pipeline"
#cd "${docker_path}"

for image_name in "${pod_names[@]}"; do
    CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")
    echo  creating docker "$image_name"
    docker build -t "${image_name}:${CURRENT_DATE}" -f dockerfiles/"${image_name}.Dockerfile" .
    docker tag "${image_name}:${CURRENT_DATE}" "sjafari2/kafka${image_name}:latest"
    docker push "sjafari2/kafka${image_name}:latest"
    if [[ "$image_name" == "consumer" ]]; then
     image_name="application"
     echo creating docker "$image_name"
     docker build  -t "${image_name}:${CURRENT_DATE}" -f dockerfiles/"${image_name}.Dockerfile" .
     docker tag "${image_name}:${CURRENT_DATE}" "sjafari2/kafka${image_name}:latest"
     docker push "sjafari2/kafka${image_name}:latest"
    fi 
 done

