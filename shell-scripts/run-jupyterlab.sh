#!/bin/sh

pod_name=$1
pod_number=$2

kubectl port-forward "$pod_name"-sts-"$pod_number" 9093:9093


