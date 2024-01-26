#!/bin/bash

# Define the directory path
directory_path="./app-merge-data"

# Use the ls command to list directories in the specified path
latest_date=$(ls -1dt "$directory_path"/* | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -n 1)

if [ -n "$latest_date" ]; then
    latest_time=$(ls -1dt "$latest_date"/*/ | head -n 1)
    
    if [ -n "$latest_time" ]; then
        latest_date=$(basename "$latest_date")
        latest_time=$(basename "$latest_time")
        echo "$latest_date/$latest_time"  # Format as "date/time"
    else
        echo "No time directories found under the latest date directory."
    fi
else
    echo "No date directories found under the specified path."
fi

