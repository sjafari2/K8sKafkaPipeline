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
processed_dir="${logpath}/processed"

thr1="${data_thr1}"
thr2="${data_thr2}"
sim1="${data_sim1}"
sim2="${data_sim2}"
datapath="${data_local_clstr_path}"
podcount="${data_CONSUMER_POD_COUNT}"
conscount="${data_CONSUMER_COUNT}"
wait_time="${MERGE_WAIT_TIME}"
wait_threshold="${MERGE_WAIT_THRESHOLD}"

mkdir -p "$outputlog"
mkdir -p "$logpath"
mkdir -p "$mergedpath"
mkdir -p "$processed_dir"

while true; do
    files_processed_in_this_iteration=false

    # Process all available files
    for pod in $(seq 1 $podcount); do
        for cons in $(seq 1 $conscount); do
            fps_file="${logpath}/consumer-${cons}-pod-${pod}_*_fps_temp.pickle"
            fmap_file="${logpath}/consumer-${cons}-pod-${pod}_*_fmap_temp.pickle"
            
            # If both files exist, process them
            if [[ -f "${fps_file}" ]] && [[ -f "${fmap_file}" ]]; then
                echo Processing files: "${fps_file}" and "${fmap_file}"
                
                python3 merge_step.py -datapath "$datapath" -t1 "$thr1" -t2 "$thr2" -sim1 "$sim1" -sim2 "$sim2" -logpath "${logpath}" -mergedpath "${mergedpath}" > "${outputlog}/mergedClstr.out"
                
                # processed files
                #rm "${fps_file}"
                #rm "${fmap_file}"
#                mv "${fps_file}" "${fps_file}_processed"
#                mv "${fmap_file}" "${fmap_file}_processed"
 
                mv "${fps_file}" "${fps_file}_processed"
                mv "${fmap_file}" "${fmap_file}_processed"
                
                files_processed_in_this_iteration=true
            fi
        done
    done

    if [[ "$files_processed_in_this_iteration" == "true" ]]; then
        # Reset the no-new-files duration
        no_new_files_duration=0
    else
        # Increment the no-new-files duration with some seconds
        no_new_files_duration=$((no_new_files_duration + ${wait_time}))
        
        # Wait for 10 seconds before checking again, since no new files were found
        sleep ${wait_time}
    fi

    # If the waiting threshold is exceeded, send a notification
    if [[ no_new_files_duration -ge ${wait_threshold} ]]; then
        echo Start Sending Notification to the Request Pod
        curl -X POST http://request-notification-svc:8080/notification
        echo Done with Sending Notification to the Request Pod

        # Reset the no-new-files duration
        no_new_files_duration=0
    fi
done

