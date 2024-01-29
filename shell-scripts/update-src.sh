#!/bin/bash

# Define a function to copy files from a pod to a destination directory
copy_files() {
    local pod_name="$1"
    local file_extension="$2"
    local destination_path="$3"
    local container_name="$4"  # Optional container name

    # Modify the kubectl command based on whether a container name is provided
    if [ -z "$container_name" ]; then
        files_to_copy=$(kubectl exec "$pod_name" -- ls "/app" | grep -E "\.${file_extension}$")
    else
        files_to_copy=$(kubectl exec "$pod_name" -c "$container_name" -- ls "/app" | grep -E "\.${file_extension}$")
    fi

    # Copy each file to the destination directory
    for file in $files_to_copy; do
        if [ -z "$container_name" ]; then
            kubectl cp "$pod_name:/app/$file" "$destination_path/$file"
        else
            kubectl cp "$pod_name:/app/$file" "$destination_path/$file" -c "$container_name"
        fi
        # echo "Copied $file from $pod_name to $destination_path/$file"
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
    echo "###############################################################################"
}

# Define the base names for the pods and their corresponding destination paths
pod_bases=("request" "producer" "consumer" "merge")
destinations=("src/request" "src/producer" "src/consumer" "src/merge")

# Loop through the pod bases and copy files based on their extensions
for ((i=0; i<${#pod_bases[@]}; i++)); do
    pod_base="${pod_bases[i]}-sts"
    destination="${destinations[i]}"

    # Process pods with pattern pod-name-sts-number
    for pod_name in $(kubectl get pods -o name | grep "${pod_base}-[0-9]\+" | sed 's|^pod/||')
    do
        echo "Copying files for $pod_name"

        # Special handling for consumer-sts pods
        if [[ "$pod_base" == "consumer-sts" ]]; then

            # Copy files from the application container
            app_destination="src/application"
            copy_files "$pod_name" "py" "$app_destination" "application"
            copy_files "$pod_name" "sh" "$app_destination" "application"
            copy_files "$pod_name" "yaml" "$app_destination" "application"
            copy_files "$pod_name" "yml" "$app_destination" "application"

            list_and_count_files "$app_destination"
        fi
            # Process for other containers
        copy_files "$pod_name" "py" "$destination"
        copy_files "$pod_name" "sh" "$destination"
        copy_files "$pod_name" "yaml" "$destination"
        copy_files "$pod_name" "yml" "$destination"
        list_and_count_files "$destination"
        echo "Finished copying files for $pod_name"
    done

    echo "*********************************************************************************************"
done
