#!/bin/bash

sts_name=$1

kubectl apply -f k8s/statefullsets/"$sts_name"-sts.yaml

kubectl get sts

kubectl get pods --watch
