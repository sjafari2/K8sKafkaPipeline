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
        break
    else
        echo "$apply_output"

        # Check for StatefulSets and whether to restart
        if [[ "$part" = "statefullsets" ]] && ([[ $restart_statefulsets -eq 1 ]] || [[ $apply_output == *"configured"* ]]); then
            echo "Restarting StatefulSets..."
            kubectl rollout restart statefulset -n "$namespace"
        fi
    fi
done

# Function to check if all pods are running
all_pods_running() {
     echo "Checking if all pods are running in namespace $namespace..."
    non_running_pods=$(kubectl get pods  -n $namespace --field-selector status.phase!="Running" -o=jsonpath='{.items[*].metadata.name}')
    #if [[ "$non_running_pods" == "!" ]]; then
    #  return 0
    #fi
    if [[ -z "$non_running_pods" ]]; then
        return 0
    else
        echo "Non-running pods: $non_running_pods"
        return 1
    fi
    }

# Check if any error occurred
if [ $error_occurred -eq 1 ]; then
    echo "One or more operations failed."
    exit 1
fi

# Check pods status after configuration

echo "Checking pods status..."
while true; do
    if all_pods_running; then
        echo "All pods are running."
        exit 0
    else
        echo "Waiting for pods to be in the running state..."
    fi

    # Watching pods status
    kubectl get pods -n "$namespace" --watch &

    # Wait for a short period before checking again
    sleep 5

    # Kill the kubectl watch process to refresh the watch on the next iteration
    pkill -f "kubectl get pods -n $namespace --watch"
done

echo "All operations completed successfully."
exit 0
