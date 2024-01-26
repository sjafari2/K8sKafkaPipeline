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
datapath="${data_local_clstr_path}"

mkdir -p "$outputlog"
mkdir -p "$logpath"
mkdir -p "$mergedpath"

echo Running Merge Clustering Algorithm in Merge-Pod $pod_index
python3  merge_step.py -datapath "$datapath" -t1 "$thr1" -t2 "$thr2" -sim1 "$sim1" -sim2 "$sim2"  -logpath "${logpath}" -mergedpath "${mergedpath}"> "${outputlog}/mergedClstr.out"

echo Done
