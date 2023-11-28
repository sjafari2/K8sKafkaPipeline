#!/bin/bash

# Define keywords to match in the command lines of processes you want to kill
keywords=("findClusters.py" "[python3]" "[orted]" "runapplication.")

# Iterate through the keywords and kill matching processes
for keyword in "${keywords[@]}"; do
    pids=$(ps aux | grep -E "$keyword" | grep -v "grep" | awk '{print $2}')
    if [ -n "$pids" ]; then
        kill -9 $pids
        echo "Killed processes matching keyword: $keyword"
    else
        echo "No processes found matching keyword: $keyword"
    fi
done

echo "Process termination complete."

