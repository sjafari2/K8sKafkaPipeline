#!/bin/bash

# Function to wait for a pod to be in the Running condition
wait_for_pod_running() {
  local pod_name="$1"
  local start_time=$(date +%s)
  local timeout=60  # 1 minute

  while true; do
    pod_status=$(kubectl get pod "$pod_name" -o jsonpath='{.status.phase}')
    current_time=$(date +%s)
    if [[ "$pod_status" == "Error" || "$pod_status" == "Failed" ]]; then
      echo "Pod $pod_name is in error state."
      return 1
    fi
    if [ "$pod_status" == "Running" ]; then
      echo "$pod_name is running."
      return 0
    fi
    if ((current_time - start_time > timeout)); then
      echo "Timeout reached. $pod_name did not reach Running state."
      return 1
    echo "Waiting for $pod_name to be running..."
    fi
    sleep 5
  done
}

# Function to execute a script in a pod
execute_script_in_pod() {
  local pod_name="$1"
  local container_name="$2"
  local script="$3"
  local pod_index="$4"

  # Kill existing processes with the same script name
  if ! kubectl exec "$pod_name" -c "$container_name" -- pkill -f "$script"; then
    echo "Error killing existing process in $pod_name"
    return 1
  fi

  # Execute the script in the pod
  if [ "$container_name" != "request-container" ]; then
    script="$script $pod_index"
  fi
  if ! kubectl exec "$pod_name" -c "$container_name" -- $script; then
    echo "Error executing $script in $pod_name"
    return 1
  fi

  return 0
}

# Define the order of scripts and their labels/containers
script_order=("./runrequest.sh" "./runproducer.sh" "./runconsumer.sh" "./runapplication.sh" "./runmerge.sh")
pod_labels=("app=request-sts" "app=producer-sts" "app=consumer-sts" "app=application-sts" "app=merge-sts")
containers=("request-container" "producer-container" "consumer-container" "application-container" "merge-container")
wait_times=(0 10 60 90 120)  # Delay times in seconds for each pod type
global_error=0

# Execute scripts in all pods
for ((i = 0; i < ${#script_order[@]}; i++)); do
  script="${script_order[i]}"
  label="${pod_labels[i]}"
  container="${containers[i]}"
  wait_time="${wait_times[i]}"

  pod_names=($(kubectl get pods --selector="$label" -o jsonpath="{.items[*].metadata.name}"))
  for pod_name in "${pod_names[@]}"; do
    pod_index=$(echo "$pod_name" | grep -oP 'sts-\K\d+')
    if ! wait_for_pod_running "$pod_name"; then
      global_error=1
      break
    fi
    sleep "$wait_time"
    if ! execute_script_in_pod "$pod_name" "$container" "$script" "$pod_index"; then
      global_error=1
      break
    fi
  done
  if [ $global_error -eq 1 ]; then
    break
  fi
done

# Check for any global errors
if [ $global_error -eq 1 ]; then
    echo "One or more operations failed."
    exit 1
else
    echo "All operations completed successfully."
    exit 0
fi
