#!/bin/bash

# Set the release name and namespace
RELEASE_NAME="pipe"
NAMESPACE="kafkastreamingdata"
#NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
#RELEASE_NAME=$(kubectl get pods -n $NAMESPACE -o=jsonpath='{.items[0].metadata.labels.helm\.sh/release}')

# Number of Kafka brokers (replicas)
BROKER_COUNT=3

# Initialize an empty array to hold DNS names
dns_names=()

# Construct the DNS names and add them to the array
for ((i=0; i<$BROKER_COUNT; i++)); do
    DNS_NAME="\"${RELEASE_NAME}-kafka-controller-${i}.${RELEASE_NAME}-kafka-controller-headless.${NAMESPACE}.svc.cluster.local:9092\""
    dns_names+=("$DNS_NAME")
done

# Convert the array to a string and print it in the desired format
echo -n "["
echo -n "$(IFS=, ; echo "${dns_names[*]}")"
echo "]"
