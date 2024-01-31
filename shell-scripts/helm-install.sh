#!/bin/sh

helm_release=pipe-kafka-controller
helm_number=3
namespace=kafkastreamingdata
error_occurred=0

# Set Kubernetes namespace
if ! kubectl config set-context $(kubectl config current-context) --namespace="$namespace"; then
    echo "Error setting Kubernetes context."
    exit 1
fi

# Function to check the status of all expected pods
check_pods() {
    local total_found=0
    local failed_pods=""
    local pending_pods=""
    local all_pods_present=true

    # Loop through the range of numbers to check each expected pod
    for i in $(seq 0 $(($helm_number - 1))); do
        local pattern="${helm_release}-${i}"
        pod_name=$(kubectl get pods -o name | grep "$pattern")

        if [ -z "$pod_name" ]; then
            all_pods_present=false
        else
            total_found=$((total_found + 1))
            echo $pod_name
            pod_status=$(kubectl get "$pod_name" -o jsonpath='{.status.phase}')
            if [ "$pod_status" = "Pending" ] || [ "$pod_status" = "ContainerCreating" ] || [ "$pod_status" = "Terminating" ]; then
                pending_pods="${pending_pods}${pod_name}\n"
            elif [ "$pod_status" != "Running" ]; then
                failed_pods="${failed_pods}${pod_name}: ${pod_status}\n"
            fi
        fi
    done

    if [ $total_found -ne $helm_number ]; then
        echo "Not all pods are present."
        echo $total_found
        return 1
    elif [ -n "$failed_pods" ]; then
        echo -e "Some pods have failed:\n$failed_pods"
        return 2
    elif [ -n "$pending_pods" ]; then
        echo -e "Some pods are pending:\n$pending_pods"
        return 3
    elif $all_pods_present; then
        return 0
    fi
}

# Main loop to check pods status, with a timeout of 2 minutes
start_time=$(date +%s)
timeout=120 # 2 minutes

while true; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [ $elapsed_time -ge $timeout ]; then
        echo "Timeout reached. Not all pods are present or in the desired state. Recreating the Helm release."
        error_occurred=1
        break
    fi

    check_pods
    pod_status=$?

    case $pod_status in
        0) echo "All matching pods are running. Nothing to do."
           exit 0;;
        1) echo "Waiting for all pods to be present..."
           sleep 10
           continue;;
        2) echo "Some pods have failed. Exiting."
           exit 1;;
        3) echo "Waiting for pending pods to start running..."
           sleep 10
           continue;;
    esac
done

# Delete and reinstall the Helm release if necessary
if [ $error_occurred -eq 1 ]; then
    if ! helm delete "${helm_release}"; then
        echo "Error deleting existing Helm release ${helm_release}."
        exit 1
    fi

    if ! helm install "${helm_release}" oci://registry-1.docker.io/bitnamicharts/kafka; then
        echo "Error installing Helm release ${helm_release}."
        exit 1
    fi

    echo "Helm release reinstalled successfully."
fi

exit 0
