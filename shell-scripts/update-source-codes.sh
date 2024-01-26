#!/bin/bash

# Define a function to copy files from a pod to a destination directory
copy_files() {
    local pod_name="$1"
    local file_extension="$2"
    local destination_path="$3"
    local container_name="$4"  # Optional container name

    # Get a list of files with the specified file extension in the pod
    files_to_copy=$(kubectl exec "$pod_name" -c "$container_name" -- ls "/app" | grep -E "\.${file_extension}$")

    if [ -z "$files_to_copy" ]; then
        echo "No files with extension .$file_extension found in pod $pod_name"
        return
    fi

    # Copy each file to the destination directory
    for file in $files_to_copy; do
        kubectl cp "$pod_name:/app/$file" "$destination_path/$file" -c "$container_name" 2>/dev/null
    done
}

# Define a function to list and count files in a directory and display them
list_and_count_files() {
    local destination_path="$1"

    # List the files in the destination directory
    files_list=$(ls "$destination_path")

    # Count the number of files in the destination directory
    num_files=$(ls -1 "$destination_path" | wc -l)

    # Display the list of files and the total count
    echo "List of files copied in $destination_path:"
    echo "$files_list"
    echo "Total number of files copied: $num_files"
    #echo "###############################################################################"
}

# Define the pods and their corresponding destination paths
#pods=("consumer-sts" "consumer-sts" "producer-sts" "request-sts" "merge-sts")
#destinations=("src/consumer" "src/application" "src/producer" "src/request" "src/merge")
#containers=("consumer-sts" "application-sts" "producer-container" "request-container" "merge-sts") # Add a list of containers
pods=("request-sts")
destinations=("../src/request")
containers=("request-container")
# Loop through the pods and copy files based on their extensions
for ((i=0; i<${#pods[@]}; i++)); do
    pod="${pods[i]}"-0
    destination="${destinations[i]}"
    container="${containers[i]}"

    echo "Copying files for $pod"
    copy_files "$pod" "py" "$destination" "$container"
    copy_files "$pod" "sh" "$destination" "$container"
    copy_files "$pod" "yaml" "$destination" "$container"
    copy_files "$pod" "yml" "$destination" "$container"
    copy_files "$pod" "properties" "$destination" "$container"


    # List and count files for this pod
    list_and_count_files "$destination"

    echo "Finished copying files from $pod"
    echo "*********************************************************************************************"
done

