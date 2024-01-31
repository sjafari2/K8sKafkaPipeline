#!/bin/bash

# Define the threshold date (2 months ago) for macOS
THRESHOLD_DATE=$(date -v-2m +"%Y-%m-%dT%H:%M:%S")

# Function to delete a specific image
delete_image() {
    local image_id=$1
    local image_repo_tag=$2
    local image_created=$(docker inspect --format='{{.Created}}' "$image_id")

    if [[ "$image_created" < "$THRESHOLD_DATE" ]] && [[ "$image_repo_tag" == "sjafari2/kafka"* ]]; then
        echo "Deleting unused image: $image_repo_tag (created on $image_created)"
        docker rmi -f "$image_id"
    else
        echo "Image $image_repo_tag (created on $image_created) is not older than $THRESHOLD_DATE and will not be deleted."
    fi
}

# Delete dangling images and specific images older than 2 months matching the pattern sjafari2/kafka*
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | while read -r line; do
    image_repo_tag=$(echo "$line" | awk '{print $1}')
    image_id=$(echo "$line" | awk '{print $2}')

    # Check if the image is either dangling or matches the pattern sjafari2/kafka*
    if [[ "$image_repo_tag" == "<none>" ]]; then
        delete_image "$image_id" "$image_repo_tag"
    fi
done
