#!/bin/bash


source parseYaml.sh
eval $(parse_yaml pipeline-configmap.yaml)
trap "exit" INT TERM
trap "kill 0" EXIT

topic_title=${data_TOPIC_TITLE}
source kafka-list-topics.sh
TOPICS=$(printf "%s\n" "${TOPICS[@]}" | grep ${topic_title})
TOPICS=($TOPICS)
topics_len=${#TOPICS[@]}
#echo There are ${topics_len} related to this Title which are: "${TOPICS[@]}"


nconsumers=${data_CONSUMER_COUNT}
pod_count=${data_CONSUMER_POD_COUNT}
col_range=${data_Column_Range}
pod_index=$1

# If no value is passed as the first argument, set podindex to 0
#if [ -z "$1" ]; then
#    podindex=0
#fi

chmod +x get_kafka_consumer_dns.sh
server_uri=$(bash get_kafka_consumer_dns.sh)

tpcs_per_pod=$((topics_len / pod_count))
tpcs_extra_pod=$((topics_len % pod_count))
if [ "$pod_index" -lt "$tpcs_extra_pod" ]; then
    ((tpcs_per_pod++))
    spoint=$((pod_index * tpcs_per_pod))
elif [ "$pod_index" -eq "$tpcs_extra_pod" ]; then
    spoint=$((pod_index * (tpcs_per_pod+1)))

else
    spoint=$((tpcs_extra_pod * (tpcs_per_pod + 1) + (pod_index - tpcs_extra_pod) * tpcs_per_pod))
fi
tpcs_per_consr=$((tpcs_per_pod / nconsumers))
tpcs_extra=$((tpcs_per_pod % nconsumers))
#spoint=0


CURRENT_DATE=$(TZ=America/Denver date +"%Y-%m-%d")
CURRENT_TIME=$(TZ=America/Denver date +"%H-%M-%S")
log_path="./logs/consumer/Pod_${pod_index}/${CURRENT_DATE}/${CURRENT_TIME}"
h5py_path="${data_H5PY_PATH}/Pod_${pod_index}"

mkdir -p ${log_path}
mkdir -p ${h5py_path}




for ((i = 0; i < nconsumers; i++)); do
  num_topics=$tpcs_per_consr
  if [ $i -lt $tpcs_extra ]; then
    ((num_topics++))
  fi
#  echo topics are ${TOPICS[@]:$spoint:$num_topics}
  echo Running Consumer[$i][pod_${pod_index}][Topic$spoint][Topic$(("$spoint + $num_topics"))]
  python3 mainConsumer.py  -topics "${TOPICS[@]:$spoint:$num_topics}" -topictitle "${topic_title}" -consindex "$i" -hpath "${h5py_path}" -colrange "${col_range}" -pi "${pod_index}" -uris "${server_uri}" >&"${log_path}/consumer.$i.$((nconsumers - 1)).out"  &
  spoint=$(("$spoint + $num_topics"))
done

# TODO: add waits for PIDs here

wait
