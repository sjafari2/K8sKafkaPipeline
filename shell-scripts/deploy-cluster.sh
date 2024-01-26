#!/bin/bash

cluster_parts=("namespace" "claims" "services" "serviceaccount" "roles" "statefullsets")



for part in "${cluster_parts[@]}"; do
  kubectl apply -f k8s/"${part}" -n kafkastreamingdata
done

kubectl apply -f k8s/configmap/pipeline-configmap.yaml -n kafkastreamingdata
kubectl apply -f k8s/secrets/pod-manager-sa-token.yaml -n kafkastreamingdata

echo Lets modify the default namespace to kafkastreamingdata
kubectl config set-context $(kubectl config current-context) --namespace=kafkastreamingdata

echo Here are the running pods
kubectl get pods

