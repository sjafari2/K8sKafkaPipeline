#!/bin/bash

pod_names=("consumer" "producer" "request" "merge")

for pod_name in "${pod_names[@]}";do
# shellcheck disable=SC1073
 kubectl rollout restart statefulset "${pod_name}"-sts
done

kubectl get pods --watch
