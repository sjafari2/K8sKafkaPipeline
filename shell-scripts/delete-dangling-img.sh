#!/bin/bash

## Delete dangling images
docker rmi $(docker images -f "dangling=true" -q)

## Delete images with tag = none
docker images | grep "<none>" | awk '{print $3}' | xargs docker rmi --force

