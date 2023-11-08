#!/bin/bash

# Define the threshold date (1 month ago)
THRESHOLD_DATE=$(date -d "1 month ago" --utc +"%Y-%m-%dT%H:%M:%S.%NZ")

# Get a list of all Docker image IDs that are not associated with any containers
unused_images=$(docker images -q --filter "dangling=true")

# Iterate through the list of unused images
for image_id in $unused_images; do
    # Get the creation date of the image
    image_created=$(docker inspect --format "{{.Created}}" "$image_id")

    # Convert the creation date to a format that can be compared
    image_created_date=$(date -d "$image_created" --utc +"%Y-%m-%dT%H:%M:%S.%NZ")

    # Compare the creation date with the threshold date
    if [[ "$image_created_date" > "$THRESHOLD_DATE" ]]; then
      echo "Deleting unused image: $image_id (created on $image_created)"
      docker rmi -f "$image_id"
    else
     echo "Image $image_id (created on $image_created) is not older than $THRESHOLD_DATE and will not be deleted."
    fi
done

