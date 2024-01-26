#!/bash/sh

./shell-scripts/docker-all-pods.sh
./shell-scripts/helm-install.sh
./shell-scripts/deploy-sts.sh
./shell-scripts/run-all-pods-scripts.sh