#!/bin/bash

source parseYaml.sh
eval $(parse_yaml pipeline-configmap.yaml)
trap "exit" INT TERM
trap "kill 0" EXIT
pod_index=$1

CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")
CURRENT_TIME=$(TZ=America/Denver date +"%H-%M-%S")
logpath="${data_log_path_mergeCl}/${CURRENT_DATE}/${CURRENT_TIME}"
mergedpath="${data_merge_path}/${CURRENT_DATE}/${CURRENT_TIME}"
outputlog="./logs/pascal-g/mergedResult/${CURRENT_DATE}/${CURRENT_TIME}"

thr1="${data_thr1}"
thr2="${data_thr2}"
sim1="${data_sim1}"
sim2="${data_sim2}"

datetime=$(bash latestDateTime.sh)
datapath="${data_local_clstr_path}/$datetime"
echo Data path is ${datapath}

podcount="${data_CONSUMER_POD_COUNT}"
conscount="${data_CONSUMER_COUNT}"
wait_time="${data_MERGE_WAIT_TIME}"

mkdir -p "$outputlog"
mkdir -p "$logpath"
mkdir -p "$mergedpath"

#while true; do
    all_files_found=true

    # Check for all required files
#    for pod in $(seq 1 $podcount); do
#for cons in $(seq 1 $conscount); do
#            fps_file="consumer-${cons}-pod-${pod}_*_fps_temp.pickle"
#            fmap_file="consumer-${cons}-pod-${pod}_*_fmap_temp.pickle"
            
#            if [[ ! -f "${logpath}/${fps_file}" ]] || [[ ! -f "${logpath}/${fmap_file}" ]]; then
#               all_files_found=false
#	       echo Files not found 
 #               break
 #           fi
 #       done
 #       if [[ "$all_files_found" == "false" ]]; then
#	   echo All files for merging found
 #           break
 #       fi
 #   done

    if [[ "$all_files_found" == "true" ]]; then
        echo Running Merge Clustering Algorithm in Merge-Pod $pod_index
        python3  merge_step.py -datapath "$datapath" -t1 "$thr1" -t2 "$thr2" -sim1 "$sim1" -sim2 "$sim2"  -logpath "${logpath}" -mergedpath "${mergedpath}" > "${outputlog}/mergedClstr.out"

        echo Done with Merging

        # Remove all the files
#        rm "${logpath}/*_temp.pickle"

 #       echo Start Sending Notification to the Request Pod
 #       curl -X POST http://request-notification-svc:8080/notification
 #       echo Done with Sending Notification to the Request Pod
    fi

    sleep $wait_time # Wait for $wait_time seconds before checking again
#done
