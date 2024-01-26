#!/bin/bash

# Define the namespace and keyword to search for in pod names
namespace="kafkastreamingdata"
keyword="sts"
consumer_keyword="consumer"

# List pods in the specified namespace with the keyword in their name
matching_pods=$(kubectl get pods -n "$namespace" -o custom-columns=":metadata.name" | grep "$keyword")

if [ -n "$matching_pods" ]; then
    for matching_pod in $matching_pods; do
        # Check if the directory /app/logs exists in the pod
        if kubectl exec -n "$namespace" "$matching_pod" -- stat -t /app/logs &> /dev/null; then
            echo "Deleting log files in /app/logs for $matching_pod"
            kubectl exec -n "$namespace" "$matching_pod" -- find /app/logs -mindepth 1 -delete
            echo "Log files in /app/logs for $matching_pod deleted."
            echo "**************************************************************************" 
            if [[ "$matching_pod" == *"$consumer_keyword"* ]]; then 
            echo "Deleting log files in /app/logs for $matching_pod container application-sts"
            kubectl exec -n "$namespace" "$matching_pod" -c application-container -- find /app/logs -mindepth 1 -delete
            echo "Log files in /app/logs for $matching_pod container application-sts deleted."
            echo "**************************************************************************"
            fi

        else
            echo "Directory /app/logs does not exist in $matching_pod."
        fi
    done
else
    echo "No pods with '$keyword' in their name found in namespace '$namespace'."
fi

