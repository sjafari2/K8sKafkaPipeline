#!/bin/bash

# Define the names of the processes you want to kill
process_names=("python3" "orted" "runapplication.")

# Iterate through the process names and kill matching processes
for name in "${process_names[@]}"; do
    pids=$(pgrep "$name")
    if [ -n "$pids" ]; then
        kill -9 $pids
        echo "Killed processes with name: $name"
    else
        echo "No processes found with name: $name"
    fi
done

echo "Process termination complete."

