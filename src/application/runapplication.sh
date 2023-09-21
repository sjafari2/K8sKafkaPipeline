#!/bin/bash

source parseYaml.sh
eval $(parse_yaml pipeline-configmap.yaml)
trap "exit" INT TERM
trap "kill 0" EXIT
pod_index=$1
topic_title=${data_TOPIC_TITLE}
h5pypath=${data_H5PY_PATH}
localclstrpath="${data_local_clstr_path}"
thr1="${data_thr1}"
thr2="${data_thr2}"
sim1="${data_sim1}"
sim2="${data_sim2}"
fps="${data_fps}"

mkdir -p $localclstrpath
mkdir -p $h5pypath


CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")
CURRENT_TIME=$(TZ=America/Denver date +"%H-%M-%S")
findCl_log_path="${data_log_path_findCl}/${CURRENT_DATE}/${CURRENT_TIME}/pod-${pod_index}"
output_log_path="./logs/pascal-g/clustering-results/${CURRENT_DATE}/${CURRENT_TIME}/pod-${pod_index}"

mkdir -p "${findCl_log_path}"
mkdir -p "${output_log_path}"

echo Running local clustering algorithm in pod $pod_index
 python3 findClusters.py -pypath "${h5pypath}" -t1 "${thr1}" -t2 "${thr2}" -sim1 "${sim1}" -sim2 "${sim2}" -fps "${fps}" -podindex "${pod_index}" -logpath "${findCl_log_path}" -localclstrpath "${localclstrpath}">"${output_log_path}/clusters.out"

echo Done
