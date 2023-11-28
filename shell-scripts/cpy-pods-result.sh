#!/bin/bash

# Define the namespace and paths to source directories within the pods
namespace="kafkastreamingdata"
source_paths=("app/consumer-app-data" "app/merged-clstr-data")
selector_pods=("consumer" "merge")

# Define the destination directory on the local machine
destination="./data/result-11-14-2023"

# Loop through the source paths and pods
for source_path in "${source_paths[@]}"; do
    selector_pod="${selector_pods[i]}"
    # Get a list of pods in the specified namespace that match the source path
    matching_pods=$(kubectl get pods -n "$namespace" --selector=app=$selector_pod-sts -o custom-columns=":metadata.name" --no-headers)

    if [ -n "$matching_pods" ]; then
        for pod in $matching_pods; do
            # Use kubectl cp to copy the entire folder from the pod to the local destination directory
            kubectl cp -n "$namespace" "$pod:/$source_paths" "$destination"
            echo "Copied data from $pod:/$source_paths to $destination"
            if [[ $pod == *"consumer-sts"* ]]; then
               source_path="app/app-merge-data" 
               kubectl cp -n "$namespace" "$pod:/$source_path" "$destination" -c application-sts
               echo "Copied data from $pod:/$source_path container application-sts to $destination"
            fi
        done
    else
        echo "No pods with the specified source path '$source_path' found in namespace '$namespace'."
    fi
done

