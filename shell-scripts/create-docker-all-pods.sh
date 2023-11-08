#!/bin/bash

pods=( "request" "producer" "consumer" "merge" )

for pod in "${pods[@]}"; do
 echo Start creaing docker $pod-sts 

 bash shell-scripts/docker-one-pod.sh $pod
 echo Done with creaing docker $pod-sts 
 
 if [[ $pod == "consumer" ]]; then
   
     echo Start creaing docker application-sts 
     bash shell/script/docker-one-pod.sh "application"
     echo Done with creaing docker application-sts 
  fi
done
