#!/bin/sh

helm_release=$1
kubectl config set-context $(kubectl config current-context) --namespace=kafkastreamingdata
helm delete "${helm_release}"
helm install "${helm_release}" oci://registry-1.docker.io/bitnamicharts/kafka

kubectl get pods --watch