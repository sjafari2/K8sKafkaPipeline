#!/bin/bash

# Function to wait for pod to be in Running condition
wait_for_pod_running() {
  local pod_name="$1"
  while true; do
    pod_status=$(kubectl get pod "$pod_name" -o jsonpath='{.status.phase}')
    if [ "$pod_status" == "Running" ]; then
      break
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
  kubectl exec "$pod_name" -c "$container_name" -- pkill -f "$script"

  # Execute the script in the pod
  if [ "$container_name" != "request-container" ]; then
    script="$script $pod_index"
  fi
  kubectl exec "$pod_name" -c "$container_name" -- $script
}

# Define the order of scripts and their labels/containers
script_order=("./runrequest.sh" "./runproducer.sh" "./runconsumer.sh" "./runapplication.sh" "./runmerge.sh")

# Check if the input is "all" or a list of pod names
if [ "$1" == "all" ]; then
  # Execute scripts in all pods
  pod_labels=("app=request-sts" "app=producer-sts" "app=consumer-sts" "app=application-sts" "app=merge-sts")
  containers=("request-container" "producer-container" "consumer-container" "application-container" "merge-container")

  for ((i = 0; i < ${#script_order[@]}; i++)); do
    script="${script_order[i]}"
    label="${pod_labels[i]}"
    container="${containers[i]}"

    pod_names=($(kubectl get pods --selector="$label" -o jsonpath="{.items[?(@.metadata.name ends with '-sts')].metadata.name}"))
    echo "${pod_names[@]}"

    for pod_name in "${pod_names[@]}"; do
      pod_index=$(echo "$pod_name" | grep -oP 'sts-\K\d+')
      wait_for_pod_running "$pod_name"
      execute_script_in_pod "$pod_name" "$container" "$script" "$pod_index"
    done
  done
else
  # Execute scripts in the specified list of pods
  for pod_name in "$@"; do
    for script in "${script_order[@]}"; do
      wait_for_pod_running "$pod_name"
      pod_index=$(echo "$pod_name" | grep -oP 'sts-\K\d+')
      execute_script_in_pod "$pod_name" "$pod_name" "$script" "$pod_index"
      echo Running pod "$pod_name" is done
    done
  done
fi
