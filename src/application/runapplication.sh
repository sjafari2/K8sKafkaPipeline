#!/bin/bash

source parseYaml.sh
eval $(parse_yaml pipeline-configmap.yaml)
trap "exit" INT TERM
trap "kill 0" EXIT

pod_index=$1
topic_title=${data_TOPIC_TITLE}
h5py_path="${data_H5PY_PATH}/Pod_${pod_index}/"
localclstrpath="${data_local_clstr_path}"
thr1="${data_thr1}"
thr2="${data_thr2}"
sim1="${data_sim1}"
sim2="${data_sim2}"
fps="${data_fps}"
wait_time="${data_APPLICATION_WAIT_TIME}"
app_count="${data_APPLICATION_COUNT}"

CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")
CURRENT_TIME=$(TZ=America/Denver date +"%H-%M-%S")
findCl_log_path="${data_log_path_findCl}/${CURRENT_DATE}/${CURRENT_TIME}"
output_log_path="./logs/${topic_title}/clustering_result/${CURRENT_DATE}/${CURRENT_TIME}"

mkdir -p "${findCl_log_path}"
mkdir -p "${output_log_path}"
mkdir -p "${localclstrpath}"

while true; do
    # Check the number of files in the directory
    num_files_before=$(ls "${h5py_path}" | wc -l)

    # Sleep for a while
    sleep $wait_time

    # Check the number of files in the directory again
    num_files_after=$(ls "${h5py_path}" | wc -l)

    # If the number of files hasn't changed, run the clustering algorithm
    
    if [ "$num_files_before" -eq "$num_files_after" ] && [ "$num_files_before" -ne 0 ]; then

        echo Running local clustering algorithm in pod $pod_index
	for ((i = 0; i < app_count; i++)); do
	      python3 findClusters.py -pypath "${h5py_path}" -t1 "${thr1}" -t2 "${thr2}" -sim1 "${sim1}" -sim2 "${sim2}" -appindex "${i}" -fps "${fps}" -logpath "${findCl_log_path}" -localclstrpath "${localclstrpath}">"${output_log_path}/findcluster.out" &

       	done   
    fi
done






