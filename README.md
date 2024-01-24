## Project Description
In this project, a pipeline using Kafka server which is containersied by Docker and orchestrated by Kubernetes has been implemented. The pipeline consitutes of four statges: Request, Producer, Consumer, Application, and Merge. 
Eech stage passes the result to the next statge.

## Insatllation
For ruuning pipeline correctly, you need to first install these packages:
- Kafka-python
- Python 3.7.16
- Kubernetes
- Docker
  


## Running The Code

For running the code in each stage, we need to run the .sh files in each stage. Follow the below running in order:

- ./runrequest
- ./runproducer 
- ./runconsumer.sh
