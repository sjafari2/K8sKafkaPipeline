#!/bin/sh
kubectl config set-context $(kubectl config current-context) --namespace=kafkastreamingdata
