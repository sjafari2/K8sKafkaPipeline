#!/bin/bash

# Define the threshold date (2 months ago) for Linux
THRESHOLD_DATE=$(date --date="2 months ago" +"%Y-%m-%dT%H:%M:%S")

# Get a list of all Docker image IDs
all_images=$(docker images -q)

# Iterate through the list of all images
for image_id in $all_images; do
    # Check if the image is dangling
    is_dangling=$(docker inspect --format="{{.RepoTags}}" "$image_id" | grep "<none>:<none>")

    # If the image is not dangling, skip it
    if [[ -z "$is_dangling" ]]; then
        continue
    fi

    # Get the creation date of the image
    image_created=$(docker inspect --format "{{.Created}}" "$image_id")

    # Compare the creation date with the threshold date
    if [[ "$image_created" < "$THRESHOLD_DATE" ]]; then
        echo "Deleting unused image: $image_id (created on $image_created)"
        docker rmi -f "$image_id"
    else
        echo "Image $image_id (created on $image_created) is not older than $THRESHOLD_DATE and will not be deleted."
    fi
done
