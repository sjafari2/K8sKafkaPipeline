#!/bin/bash

# Define the namespace and paths to source directories within the pods
namespace="kafkastreamingdata"
source_paths=("app/request-data" "/app/request-producer-data" "app/consumer-app-data" "app/app-merge-data" "app/merged-clstr-data")
selector_pods=("request" "producer" "consumer" "consumer" "merge")
container_names=("request-container" "producer-container" "consumer-container" "application-container" "merge-container")

# Loop through the source paths and pods
for i in "${!source_paths[@]}"; do
    source_path="${source_paths[i]}"
    selector_pod="${selector_pods[i]}"
    container_name="${container_names[i]}"
    
    # Get a list of pods in the specified namespace that match the source path
    matching_pods=$(kubectl get pods -n "$namespace" --selector=app="$selector_pod-sts" -o custom-columns=":metadata.name" --no-headers)

    if [ -n "$matching_pods" ]; then
        for pod in $matching_pods; do
            # Use kubectl exec to run a command in the specified container to delete the contents inside the subfolders
            kubectl exec -n "$namespace" -c "$container_name" "$pod" -- find "/$source_path" -mindepth 2 -delete
            echo "Deleted contents inside $pod:/$source_path (subfolders preserved)"
        done
    else
        echo "No pods with the specified source path '$source_path' found in namespace '$namespace'."
    fi
done

