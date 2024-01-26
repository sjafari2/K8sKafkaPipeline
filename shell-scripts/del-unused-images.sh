#!/bin/bash

# Define the threshold date (1 month ago) for BSD date command
THRESHOLD_DATE=$(date -v-1m +"%Y-%m-%dT%H:%M:%S.%NZ")

# Get a list of all Docker image IDs that are not associated with any containers
unused_images=$(docker images -q --filter "dangling=true")

# Iterate through the list of unused images
for image_id in $unused_images; do
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

