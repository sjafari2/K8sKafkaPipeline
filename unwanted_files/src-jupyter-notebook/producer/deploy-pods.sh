#!/bin/bash

# Retrieve PRODUCER_COUNT vnd CONSUMER_COUNT alue from ConfigMap
#prodcount=$(kubectl get configmap.yaml -ojsonpath='{.data.PRODUCER_COUNT}')
#conscount=$(kubectl get configmap.yaml -ojsonpath='{.data.CONSUMER_COUNT}')

source parseYaml.sh
eval $(parse_yaml ../pipeline-configmap.yaml)
prodcount=${PRODUCER_COUNT}
conscount=${CONSUMER_COUNT}


# Deploy Kafka Cluster
#kubectl apply -f kafka-cluster.yaml

# Wait for Kafka Cluster to be ready 
#kubectl wait kafka/my-kafka-cluster --for=condition=Ready --timeout=300s

# Create Request Pod
#kubectl apply -f request-sts.yaml

# Create Producer Pods
#kubectl apply -f producer-statefulset-pod.yaml


# Create Consumer Pods
#kubectl apply -f consumer-sts.yaml


# Create Merge Pod
#kubectl apply -f merge-sts.yaml

# Wait for Request Pod be ready
kubectl wait pod request-sts-0 --for=condition=Ready --timeout=300s

# Wait for Producer Pods to start
for ((i=1; i<=prodcount; i++)); do
  kubectl wait pod producer-sts-$i --for=condition=Ready --timeout=300s
done

# Wait for Consumer Pods to start
for ((i=1; i<=conscount; i++)); do
  kubectl wait pod consumer-sts-$i --for=condition=Ready --timeout=300s  
done

# Wait for Merge Pod to be ready
kubectl wait pod merge-sts-0 --for=condition=Ready --timeout=300s
echo all pods are ready

# Start command for Request Pod
kubectl exec -i request-sts-0 -- ./runrequest.sh &

# Sleep for a few seconds to allow Request Pod to start
sleep 5


# Start command for Producer Pods

for ((i=1; i<=prodcount; i++)); do
  pod_name=$(kubectl get pod -l app="producer-sts",instance=$i )
  ordinal=$(echo "$pod_name" | rev | cut -d '-' -f 1 | rev)
  echo "Pod ordinal value is: $ordinal"
  kubectl exec -i "$pod_name" -- /bin/bash -c "./runproducer.sh $ordinal" &
done

# Sleep for a few seconds to allow Producer Pods to start
sleep 5

# Start command for Consumer Pods
for ((i=1; i<=numconsumer; i++)); do
  pod_name=$(kubectl get pod -l app="cons-sts",instance=$i )
  ordinal=$(echo "$pod_name" | rev | cut -d '-' -f 1 | rev)
  echo "Pod ordinal value is: $ordinal"
  kubectl exec -i "$pod_name" -c "cosnumer-sts" -- /bin/bash -c "./runconsumer.sh $ordinal" &
  kubectl exec -i "$pod_name" -c "application-sts" -- /bin/bash -c "./runapplication.sh $ordinal" &
done

sleep 10

# Start command for Merge Pod
pod_name=$(kubectl get pod -l app="merge-sts")
#,instance=$i -o jsonpath='{.metadata.name}')
if [ -n "$pod_name" ]; then
    ordinal=$(echo "$pod_name" | rev | cut -d '-' -f 1 | rev)
    echo "Merge Pod ordinal value is: $ordinal"
    kubectl exec -i "$pod_name"  -- /bin/bash -c "./runmerge.sh $ordinal" &
else
    echo Pod not found
fi
# Sleep for a few seconds to allow Merge Pod to start
sleep 5

wait
