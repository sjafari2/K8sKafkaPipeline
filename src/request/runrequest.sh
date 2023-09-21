#!/bin/bash

source parseYaml.sh
eval $(parse_yaml pipeline-configmap.yaml)
trap "exit" INT TERM
trap "kill 0" EXIT

input_path=${data_RequestInputPath}
output_path=${data_RequestOutputPath}
start_date=${data_StartDate}
end_date=${data_EndDate}
window=${data_RequestWindow}
wait_time=${data_Wait}
pod_count=${data_PRODUCER_POD_COUNT}
prod_count=${data_PRODUCER_COUNT}
total_prod=$((pod_count * prod_count)) 
#pod_index=$1
#prod_index=$2


CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")
CURRENT_TIME=$(TZ=America/Denver date +"%H-%M-%S")
log_path="./logs/request/${CURRENT_DATE}/${CURRENT_TIME}"


mkdir -p "${log_path}"
mkdir -p "$output_path/"
chmod -R 777 ./logs/request
#sudo chmod 777 "${output_path}"


echo Running API Server and Request Script to Call Pascal-G Simulator 

uvicorn main:app --reload &
sleep 5

python3 request-notification.py &


first_iteration=true

while true; do
    # Skip waiting for notification on the first iteration
    if [ "$first_iteration" = true ]; then
        first_iteration=false
    else
        # Wait for the notification flag
        while [ ! -f /tmp/notification_received ]; do
            sleep 1
        done
    fi

    # Remove the flag to reset the notification state
    rm -f /tmp/notification_received

    # Run request_extended.py
    python3 request_extended.py -podcount "${pod_count}" -prodcount "${prod_count}" -totalprod "${total_prod}" -ipath "${input_path}" -opath "${output_path}" -start "${start_date}" -end "${end_date}" -window "${window}" -wait "${wait_time}" >"${log_path}/simulator.out"

done





