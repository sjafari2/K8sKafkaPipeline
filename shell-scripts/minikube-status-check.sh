#!/bin/bash

# Check if Minikube is running
minikube_status=$(minikube status --format="{{.Host}}")
num_cpus=$1
memory=$2

if [ "$minikube_status" == "Running" ]; then
    echo "Minikube is already running."
else
    echo "Starting Minikube with 4 CPUs and 5000MB of memory..."
    minikube start --cpus "${num_cpus}" --memory "${memory}"
    if [ $? -ne 0 ]; then
        echo "Failed to start Minikube."
        exit 1
    fi
    echo "Minikube started successfully."
fi
