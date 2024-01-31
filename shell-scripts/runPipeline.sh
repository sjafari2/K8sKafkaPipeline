#!/bin/bash

# Define the function parameters defined in scripts
restart_statefullsets=1     # This parameter determines if restarting of pods is required or not
results_path="./results"     # Path of saving pods' results
logs_path="./logs"           # Path of saving pods' logs
minikube_cpu=4
minikube_memory=4000     # it is in MG


## If you use the minikube cluster you can check it's status with script minikube-status-check.sh
## This script checks minikube status and if it is not running, starts it
## ./shellscripts/minikube-status-check.sh
## If you want to delete images that are dangling or older than 2 months you can run uncomment
## one of the following based on your os, . Linux, or Mac.
## This helps to release some space for developing the new images

#  ./shell-script/delete-unused-images-linux.sh
#  ./shell-script/delete-unused-images-mac.sh

## Another option is to call delete-dangling-img.sh to delete all dangling images and images with tag=none
#  ./shell-scripts/delete-dangling-img.sh

## docker-all-pods.sh develops all docker images we need for running kafka pipeline including
## request, producer, consumer, application, merge and push them to docker hub sjafari2 with tag latest
## If you already have the images you need, you can keep it commented
# "./shell-scripts/docker-all-pods.sh"

## helm-install.sh checks if kafka pods are running and if they are not all running base on their status
## which can be pending or error it waits or echo error message. If not all pods are present in any status
## it deletes the helm and install it again
## We defined the default values of helm number which carries the number of kafka pods is 3
# "./shell-scripts/helm-install.sh"

## deploy-cluster.sh deploys all cluster components and if you set restart_statefulsets to 1, it also
## restarts all statefulsets, if if you set restart_statefullsets to 0, it just restart statefullsets which have changed.
## We set restart_statefullsets to 0 as the default value
# "./shell-scripts/deploy-cluster.sh ${restart_statefullsets}"

## run-all-pods.sh runs the shell scripts in each pod across the pipeline. These shell scripts run
## python functions in each component of the pipeline (request, producer, consumer, application, merge)
#./shell-scripts/run-all-pods-scripts.sh


## copy-pods-result.sh saves the results of all pods in the parameter you call the function with
## as a path. Here we define this parameter as result_path

# "./shell-scripts/copy-pods-result.sh ${results_path}"


## copy-pods-logs.sh saves the logs of all pods in the parameter you call the function with
## as a path. Here we define this parameter as logs_path

# "./shell-scripts/copy-pods-logs.sh ${logs_path}"

# Define an array of scripts to be executed in sequence.
# You can add whatever script you need from above instruction.
# The order of running scrips matters

scripts=(
 ./shell-scripts/delete-dangling-img.sh
  # "./shell-scripts/docker-all-pods.sh"
 ./shell-scripts/minikube-status-check.sh "${minikube_cpu}" "${minikube_memory}"
  #./shell-scripts/namespace-config.sh
  # "./shell-scripts/helm-install.sh"
  ./shell-scripts/deploy-cluster.sh "${restart_statefullsets}"
  ./shell-scripts/run-all-pods-scripts.sh
)

# Execute each script in the array
for script in "${scripts[@]}"; do
    echo "Running $script..."
    if [ $? -ne 0 ]; then
        echo "Error occurred in $script. Exiting..."
        exit 1
    fi
    echo "$script completed successfully."
done

echo "All scripts completed successfully."
