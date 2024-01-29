#!/bin/bash

cluster_parts=("namespace" "claims" "services" "serviceaccount" "statefullsets")
error_occurred=0
namespace=kafkastreamingdata
restart_statefulsets=$1  # Default to not restarting

# Check if the restart argument is provided
if [ "$1" = "1" ]; then
    restart_statefulsets=1
fi

for part in "${cluster_parts[@]}"; do
    echo "Applying configuration for $part..."

    # Capture the output of kubectl apply
    apply_output=$(kubectl apply -f k8s/"${part}" -n "$namespace" 2>&1)

    if [[ $? -ne 0 ]]; then
        echo "Error applying $part."
        echo "$apply_output"
        error_occurred=1  # Set the error flag
    else
        echo "$apply_output"

        # Check for StatefulSets and whether to restart
        if [[ "$part" = "statefullsets" ]] && ([[ $restart_statefulsets -eq 1 ]] || [[ $apply_output == *"configured"* ]]); then
            echo "Restarting StatefulSets..."
            kubectl rollout restart statefulset -n "$namespace"
        fi
    fi
done

# Additional parts of your script remain the same...

# Function to check if all pods are running
all_pods_running() {
    ! kubectl get pods -n "$namespace" -o jsonpath='{.items[?(@.status.phase!="Running")].metadata.name}' | grep -q .
}

# Check if any StatefulSet was restarted and if so, check all pods
if [[ $restart_statefulsets -eq 1 ]]; then
    echo "Waiting for all pods to be running..."
    start_time=$(date +%s)
    while ! all_pods_running; do
        current_time=$(date +%s)
        if [[ $((current_time - start_time)) -gt 120 ]]; then  # 2 minutes timeout
            echo "Timeout reached. Not all pods are running."
            exit 1
        fi
        sleep 5
    done
    echo "All pods are running."
fi

# Check if any error occurred
if [ $error_occurred -eq 1 ]; then
    echo "One or more operations failed."
    exit 1
else
    echo "All operations completed successfully."
    exit 0
fi
