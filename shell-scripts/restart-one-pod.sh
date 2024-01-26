#!/bin/bash

pod_name=$1

kubectl rollout restart statefulset "${pod_name}"-sts

kubectl get pods --watch