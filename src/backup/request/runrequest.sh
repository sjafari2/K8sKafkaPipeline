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


# Check if port 80 is occupied and if so, kill the process occupying it
if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null; then
    echo "Port 80 is occupied. Killing the process..."
    kill -9 $(lsof -t -i:80)
fi


echo Running API Server and Request Script to Call Pascal-G Simulator 

uvicorn main:app --reload &
sleep 5

python3 request-notification.py &


first_iteration=true

add_window_to_date() {
    date -d "$1 + $window hours" +"%Y-%m-%d %H:%M:%S"
}

while true; do
    # Check if there are new files in the directory
    if [[ $(ls -A "$input_path") ]]; then
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

        # Update start and end dates for the next iteration
        start_date="$end_date"
        end_date=$(add_window_to_date "$end_date")
    else
        sleep 10  # Wait for some time before checking again
    fi
done


