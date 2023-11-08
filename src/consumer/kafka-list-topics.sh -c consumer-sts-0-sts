#!/bin/bash

chmod +x get_kafka_producer_list.sh
server_uri=$(bash get_kafka_producer_list.sh)

export TOPICS=$(${KAFKA_INSTALL_PATH}/kafka-topics.sh --list --bootstrap-server ${server_uri} --command-config ./consumer.properties)
TOPICS=($TOPICS)
topics=("${TOPICS[@]}")
topics_len=${#topics[@]}
echo Topics are: ${TOPICS[@]}
#echo Number of All Topics: $topics_len
