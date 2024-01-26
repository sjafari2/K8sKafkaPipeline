## Insatllation
For ruuning pipeline correctly, you need to first install these packages:
- Python 3.7.16
- Kafka-python 2.0.2
- Kubernetes  v1.28.3
- Docker 0.19.0
  


## Running The Code

For running the code in each stage, we need to run the .sh files in each stage. Follow the below running in order:

- ./shell-scripts/docker-all-pods.sh
- ./shell-scripts/helm-install.sh
- ./shell-scripts/deploy-all-pods.sh
- ./shell-scripts/run-all-pods.sh

## The Results

The final result would be in the last pod, Merge Pod in path ./request-data.
