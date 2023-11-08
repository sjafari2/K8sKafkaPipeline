#!/bin/bash
source parseYaml.sh
eval $(parse_yaml pipeline-configmap.yaml)
trap "exit" INT TERM
trap "kill 0" EXIT

## Get number of producers, number of topics, number of producer pods, producer input path, server uris,batch size, wait time, and pod ordinal values from values.yaml file ##
nproducers=${data_PRODUCER_COUNT}
num_topics=${data_PRODUCER_TOPIC_COUNT}
pod_count=${data_PRODUCER_POD_COUNT}
input_path=${data_PRODUCER_INPUT_PATH}
batch_size=${data_BATCH_SIZE}
wait_time=${data_WAITE_TIME}
topic_title=${data_TOPIC_TITLE}
col_range=${data_Column_Range}
pod_index=$1

chmod +x get_kafka_producer_dns.sh
server_uri=$(bash get_kafka_producer_dns.sh)
#echo $server_uri


((np = nproducers))
((nt = num_topics))
((pc = pod_count))
((bs = batch_size))
((wt = wait_time))
((pi = pod_index))


## Get current date and time
CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")
CURRENT_TIME=$(TZ=America/Denver date +"%H-%M-%S")

## Create path for logs with current date and time
log_path="./logs/producer/${topic_title}/${CURRENT_DATE}/${CURRENT_TIME}/Pod_$pi"
mkdir -p ${log_path}


for ((i = 0; i < np; i++));do
  echo Running Producer[$i]
  python3 mainProducer.py -topicTitle "${topic_title}" -np "$np" -nt "$nt" -pi "$pi" -pri "$i" -inputpath "${input_path}" -bs "${batch_size}" -wtime "$wt" -cr "${col_range}" -uris "${server_uri}">&"${log_path}/producer.$i.$((np - 1)).out"&
done



        #    pids[${i}]=$!
        #    ((si = ei))
        #   ((ei = si + batchsize))

#for pid in ${pids[*]}; do
#    wait $pid
 # done
#done

wait
