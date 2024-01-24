#!/bin/bash

sts_name=$1

kubectl delete sts "$sts_name"-sts

kubectl get sts
