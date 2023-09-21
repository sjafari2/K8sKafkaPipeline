#!/bin/bash

# 1 is the network
# 2 is first similarity metric
# 3 is second similarity metric

echo "Creating directories for" $1
echo ""

FILE=save_runs
if [ -d "$FILE" ]; then
    echo "$FILE exists"
else
    mkdir save_runs
fi

# i.e. save_runs/dotsim_dotsim
FILE=save_runs/$2_$3
if [ -d "$FILE" ]; then
    echo "$FILE exists"
else
    mkdir save_runs/$2_$3
fi

# i.e. save_runs/dotsim_dotsim/network
FILE=save_runs/$2_$3/$1
if [ -d "$FILE" ]; then
    echo "$FILE exists"
    # rm save_runs/$2_$3/$1/*
else
    mkdir save_runs/$2_$3/$1
fi

# -------------------------------------------------

FILE=save_scores
if [ -d "$FILE" ]; then
    echo ""
    echo "$FILE exists"
else
    mkdir save_scores
fi

# i.e. save_scores/dotsim_dotsim
FILE=save_scores/$2_$3
if [ -d "$FILE" ]; then
    echo "$FILE exists"
else
    mkdir save_scores/$2_$3
fi

# i.e. save_scores/dotsim_dotsim/network
FILE=save_scores/$2_$3/$1
if [ -d "$FILE" ]; then
    echo "$FILE exists"
    # rm save_scores/$2_$3/$1/*
else
    mkdir save_scores/$2_$3/$1
fi

echo ""
echo "STARTING GRAPH SCAN"

for thc in {0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9}
do
    for thm in {0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9}
    do
    echo $thc $thm
    echo ""
    mkdir save_runs/$2_$3/$1/th_${thc}_${thm}
    
    python3 run_probabilistic_clustering.py -n $1 -t1 $thc -t2 $thm -sim1 $2 -sim2 $3
   
    done
done