#!/bin/bash

#pod_name=${1}
#pod_number=${2}
#container_name=$3-sts
#:${pod_name}-sts}
#echo ${container_name}

#kubectl exec -it ${pod_name}-sts-${pod_number} -c ${container_name} -- bash


# Another Approach

pod_name=${1}
pod_number=${2}
#container_name=${3:${pod_name}-sts}
#echo ${container_name}

if [[ $pod_name == "application" ]]; then
   kubectl exec -it consumer-sts-${pod_number} -c application-sts  -- bash
else 
   kubectl exec -it ${pod_name}-sts-${pod_number}  -- bash
fi
