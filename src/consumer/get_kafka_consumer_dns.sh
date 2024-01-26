#!/bin/bash

# Set the release name and namespace
RELEASE_NAME="pipe"
NAMESPACE="kafkastreamingadata"
#NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
#RELEASE_NAME=$(kubectl get pods -n $NAMESPACE -o=jsonpath='{.items[0].metadata.labels.helm\.sh/release}')


# Construct and print the DNS name for consumers
DNS_NAME="${RELEASE_NAME}-kafka.${NAMESPACE}.svc.cluster.local:9092"

echo "[\"$DNS_NAME\"]"
