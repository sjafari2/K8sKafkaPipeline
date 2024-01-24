#!/bin/bash

docker image prune -a --filter "until=$(date +'%Y-%m-%dT%H:%M:%S' --date='-60 days')"
#docker image prune -a --filter "until=$(date -d '5 weeks ago' +%s)"
docker image prune --all --force --filter "dangling=true"
#docker system prune -a
