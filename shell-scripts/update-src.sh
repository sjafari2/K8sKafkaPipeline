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
#        echo "Copied $file from $pod_name to $destination_path/$file"
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
    echo "List of files copied  in $destination_path:"
    echo "$files_list"
    echo "Total number of files copied: $num_files"
    echo "###############################################################################"
}



# Define the pods and their corresponding destination paths
pods=("consumer-sts" "producer-sts" "request-sts" "merge-sts")
destinations=("src/consumer" "src/producer" "src/request" "src/merge")


# Loop through the pods and copy files based on their extensions
for ((i=0; i<${#pods[@]}; i++)); do
    
    pod="${pods[i]}"-0
    destination="${destinations[i]}"
    
    echo "Copying files for $pod"
    copy_files "$pod" "py" "$destination"
    copy_files "$pod" "sh" "$destination"
    copy_files "$pod" "yaml" "$destination"
    copy_files "$pod" "yml" "$destination"
 
    # List and count files for this pod
    list_and_count_files "$destination"
 
    echo "Finished copying files for $pod"

    if [ "$pod" == "consumer-sts-0" ]; then
        # Copy .py, .sh, and .yaml files for "application" pod
        app_destination="src/application"
        kubectl cp "$pod:/app/"*.py "$app_destination/*.py" -c application-sts
        kubectl cp "$pod:/app/"*.sh "$app_destination/*.sh" -c application-sts
        kubectl cp "$pod:/app/"*.yaml "$app_destination/*.yaml" -c application-sts
        kubectl cp "$pod:/app/"*.yml "$app_destination/*.yml" -c application-sts

       # echo "Copied .py, .sh, .yaml and .yml files from $pod to $app_destination -c application-sts"
        # List and count files for the application container
        list_and_count_files "$app_destination"
   
    echo "Finished copying files for $pod container application-sts"
    fi
    echo "*********************************************************************************************"
done

