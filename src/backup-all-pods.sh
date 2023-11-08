#!/bin/bash

# Define a function to copy files from a pod to a destination directory
copy_files() {
    local pod_name="$1"
    local file_extension="$2"
    local destination_path="$3"
    
    # Get a list of files with the specified file extension in the pod
    files_to_copy=$(kubectl exec "$pod_name" -- ls "/app" | grep -E "\.${file_extension}$")
    
    # Copy each file to the destination directory
    for file in $files_to_copy; do
        kubectl cp "$pod_name:/app/$file" "$destination_path/$file"
        echo "Copied $file from $pod_name to $destination_path/$file"
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
    echo "List of files in $destination_path:"
    echo "$files_list"
    echo "Total number of files copied: $num_files"
}


# Define the pods and their corresponding destination paths
pods=("consumer" "producer" "request" "merge" )
destinations=("src/consumer" "src/producer" "src/request" "src/merge" )


# Loop through the pods and copy files based on their extensions
for ((i=0; i<${#pods[@]}; i++)); do
    
    pod="${pods[i]}"-sts-0
    destination="${destinations[i]}"
    # Copy .py, .sh, and .yaml files for other pods

    echo "Copying files for $pod"
    copy_files "$pod" "py" "$destination"
    copy_files "$pod" "sh" "$destination"
    copy_files "$pod" "yaml" "$destination"
 
    echo "Copying files for $pod"
    echo "***************************************************************"
    if [ "$pod" == "consumer" ]; then
        # Copy .py, .sh, and .yaml files for "application" pod
        destination="src/application"
        kubectl cp "consumer-sts-0:/app/"*.py "$destination/*.py" -c application-sts
        echo "Copied .py files from consumer-sts-0 to $destination -c application-sts"
        kubectl cp "consumer-sts-0:/app/"*.sh "$destination" -c application-sts
        echo "Copied .sh files from consumer-sts-0 to $destination -c application-sts"
        kubectl cp "consumer-sts-0:/app/"*.yaml "$destination" -c application-sts
        echo "Copied .yaml files from consumer-sts-0 to $destination -c application-sts"
     fi
    
    echo "Finished copying files for $pod" container application-sts
done

