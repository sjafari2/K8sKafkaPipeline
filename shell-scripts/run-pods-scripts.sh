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
  # Kill existing processes with the same script name
  kubectl exec "$pod_name" -c "$container_name" -- pkill -f "$script"
  # Execute the script in the pod
  kubectl exec "$pod_name" -c "$container_name" -- "$script"
}

# Define the order of scripts and their labels/containers
script_order=("./runrequest.sh" "./runproducer.sh" "./runconsumer.sh" "./runapplication.sh" "./runmerge.sh")

# Function to find pods by keyword and execute scripts on them
find_pods_by_keyword_and_execute_scripts() {
  local keyword="$1"
  local label_selector="$2"
  local container_name="$3"

  pod_names=($(kubectl get pods --selector="$label_selector" -o json | jq -r '.items[].metadata.name'))
  n=0
  for pod_name in "${pod_names[@]}"; do
    wait_for_pod_running "$pod_name"
    execute_script_in_pod "$pod_name" "$container_name" "${script_order[$n % ${#script_order[@]}]} $n"
    n=$((n + 1))
  done
}

# Check if the input is "all" or a list of keywords
if [ "$1" == "all" ]; then
  # Execute scripts in all pods
  pod_labels=("app=request-sts" "app=producer-sts" "app=consumer-sts" "app=consumer-sts" "app=merge-sts")
  containers=("request-container" "producer-container" "consumer-container" "application-container" "merge-container")

  for ((i = 0; i < ${#script_order[@]}; i++)); do
    keyword="${pod_labels[i]%-sts}"  # Extract keyword from label
    label="${pod_labels[i]}"
    container="${containers[i]}"
    find_pods_by_keyword_and_execute_scripts "$keyword" "$label" "$container"
  done
else
  # Execute scripts based on provided keywords
  for keyword in "$@"; do
    label="app=${keyword}-sts"
    container="${keyword}-sts"
    find_pods_by_keyword_and_execute_scripts "$keyword" "$label" "$container"
  done
fi