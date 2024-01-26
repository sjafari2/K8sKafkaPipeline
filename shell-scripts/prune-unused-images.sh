#!/bin/bash

# Calculate the date for 30 days ago in the format Docker expects
# For BSD systems like macOS
thirty_days_ago=$(date -v-30d +'%Y-%m-%dT%H:%M:%S')

# Prune images older than 30 days
docker image prune -a --force --filter "until=$thirty_days_ago"

# Prune all dangling images
docker image prune --all --force
