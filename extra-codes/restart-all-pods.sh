#!/bin/bash

pods=( "merge" "producer" "consumer" "merge" )

echo Copy updated pods code
bash update-src.sh

echo Copy all pods results
bash copy-pods-result

echo Delete all pods logs
bash delete-pod-logs.sh

echo Restart all pods
for pod in "${pods[@]}"; do
    restart-one-pod.sh $pod
done
