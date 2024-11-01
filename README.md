
# Data Streaming Pipeline 
=======
## Introduction
In this project, we creat a data streaming pipeline using Kafka, Dockerized and orchestrated with Kubernetes. It has five main phases: Request, Producer, Kafak Brokers, Consumer-Application, and Merge. Each section is neatly organized in Kubernetes using statefulsets. Each section sends the data to the next section. In the Application and Merge phases, we apply the Pascal-G algorithm on a Twitter dataset to find out how many clusters this Tweeter data set has.

We've provided a figure below and more explanations later on for those who want to understand our system better.
## Architecture
 


#### Request Pod
To mimic data streaming in a more stable environment, we created an API simulator to input data into our system. This simulator has an API server that works in the background and can reach the raw data stored in a Pod's local storage area. A Request Client gets data from the API server and keeps it in a common storage area, which is also shared with the Producer Pods. After this, the request pod waits until it gets a signal from the merge pod, the final step in our system. This signal tells the request pod to send the next set of data.

#### Producer Pods
Each Producer Pod, which runs in a computing node, has a Producer container, which can start up a number of Producer processes. This is how parallelism takes place at the Producer stage of the pipeline. Producer processes retrieve the data from the source, in this case the API simulator which is running in the Request Pod, clean it with standard text preprocessing techniques (lemmatization, removing stop words, etc.) and accommodating it into Kafka brokers at the next stage. The data received by the Request Pod is systematically indexed, ensuring that each Producer Pod can accurately identify and access its corresponding data. Producers process their data and read a bach of tweets to form an array consisting of two elements: the first element is the hash value of each word in a tweet, obtained by applying a hash function that converts each word into a number, and the second element is a list of all words that co-occur with that word in the same tweet. 

#### Kafka Broker Pods
The arrays created by the Producer Pods are then passed into a stack of Kafka brokers. The topics within the brokers are designated by specific numbers, such as 10, 100, or 1000. Each array is assigned to a particular topic based on the remainder obtained from dividing the first element of the array, which is the hash value, by the total number of topics. For example, if the hash value of a hashtag is 2040 and there are 1000 topics, the array containing this hash value as its first element, along with the corresponding co-occurring words array as the second element, would be assigned to topic number 40. This assignment is determined because the remainder of 2040 divided by 1000 is 40. In this setup, each Kafka broker operates within its own pod, meticulously deployed using the Bitnami Helm chart. Following a similar deployment strategy, every Zookeeper instance is also encapsulated in a dedicated pod, mirroring the individualized approach taken for the Kafka brokers. Also, for containerization, we employed Docker containers to ensure efficient and isolated environments. The parallelism parameter in Kafka is determined by the number of topic partitions. By adjusting this variable, we can effectively control the level of parallelism within the Kafka system. The hashing mechanism is explained in details below. 

#### Consumer-Application Pods
Each Consumer-Application Pod in our system has two parts: a Consumer Container and an Application Container. Both share a storage space for better data handling within the pod. The Consumer Containers can run several Consumer processes at once. They connect to different topics in the Kafka brokers, with each consumer handling a specific set of topics. They process data batches made by Producers and put into Kafka brokers. The consumers turn these batches into CSR (Compressed Sparse Row) matrices, where the first part of each batch is a row and the second part (the array of co-occurring words) makes the columns. Every time a word pair occurs, we add one to their spot in the matrix. These CSR matrices are then stored in the shared space with the Application Containers, each file being part of the whole matrix.
The Application Container waits until it has all parts of the CSR matrix. It regularly checks the shared space for new data. If it finds new data, it waits for more. If there's no new data for a while, it starts processing. It combines all the CSR matrix parts into a big CSR matrix. Then, the "find-clusters" process inside this container does the first clustering on this big matrix. The results are saved to the shared storage, which the merge pod can also access.

#### Merge Pod
The merge pod consists of a single merge container and includes a local persistent volume dedicated to storing the final clustering results. Additionally, this merge pod is configured to share the persistent volume with the application containers within the consumer-App pod, facilitating data access. The merge-clusters process inside of the merge container reads from the shared persistent volume, computes the final clustering step and writes the final result to its locally mounted persistent volume. The merge pod also waits until it is certain that it has received all initial clustering results, employing the same data reception mechanism as the application containers, as previously described. Once the clustering results are complete, the merge pod then sends a notification to the request pod. This notification signals the request pod to send the next batch of data to the producer pods.

### Hashing Technique
In our system's first three stages, we create a weighted word co-occurrence graph. This graph shows words as nodes, and edges link nodes when their corresponding words appear together in a document, like tweets on social media. We assign weights to these edges based on the frequency of word pairs occurring together within a certain timeframe, such as an hour or a day. A higher frequency results in a stronger edge weight, crucial for the graph clustering algorithm's effectiveness.
For graph representation, we use sparse adjacency vectors instead of traditional edge lists or adjacency matrices. This approach is key to handling streaming data, as it allows for independent node processing and parallel clustering tasks. Each vector represents a node and includes a weight for each co-occurrence with another node. To efficiently construct these vectors, we implement a hashing mechanism. Words are hashed into numeric indices for the vectors, managing potential collisions by using a broad range of hash values. This ensures minimal overlap of different words into the same hash value, keeping the system efficient and accurate.

## Data Set
Twitter/X, initially known as Twitter, is a widely-used social network and a key platform for online communication and information spread. It has been a focal point for studying information dissemination during political crises, as highlighted in several academic works. For our project, Twitter/X serves as a primary data source.
We sourced data from two repositories. First is the Github Russo Ukrainian War Dataset, providing tweet IDs. Using the Twitter API, we retrieved 57,384,192 tweets from 7,744,714 users, spanning from February 24, 2022, to February 14, 2023. The second repository is the COVID-19 Tweets repository, noted in a study by Chen E, Lerman K, and Ferrara E. This collection focuses on COVID-19 related tweets, totaling 1,785,043,839 English tweets gathered from January 2020 to February 2023, also retrieved using the Twitter API. These extensive datasets form the foundation of our analysis.

# Technologies Used
1. Prgramming Language: Python
2. Data Streaming Architecture: Kafka
3. Scripting Language: Shell Scripting
4. Containerization: Docker
5. Container Orchestration Tool: Kubernetes
6. Cloud Space for running the Pipeline: Nautilus https://ucsd-prp.gitlab.io/
   
## Prerequisites
- Python 3.8.x
- Kafka-python 2.0.2
- Kubernetes  v1.28.3
- Docker 0.19.0
  
All the other required packages would be installed by developing the docker images. The list of these packages for producer, consumer, application, and merge pods are in requirments.txt file. For request pod, the list of packages are in request-requirments.txt file.


## Running Pipeline
For running the whole pipeline, you need to run the runPipeline.sh file in shell-scripts directory by this command:
#### ./shell-scripts/runPipeline.sh

There are multiple stages defined in runPipeline.sh file. Here we describe some of the main import ones in order. For a comprehensive explaination of the commands, read runPipeline.sh file.

#### Deleting Dangling Images
To make enough space for developying new images, we first delete dangling images.
- ./shell-scripts/delete-dangling-img.sh

##### Creating Docker Images 
We create the required images by running this command:
- ./shell-scripts/docker-all-pods.sh

##### Creating Minikube Kubernetes Cluster
In order to create a Kubernetes Cluster with one node, we use Minikube. You can use any other package.
- ./shell-scripts/minikube-status-check.sh "${minikube_cpu}" "${minikube_memory}"

##### Deploying Kafka Bitnami Helm Chart (Kafka-Python) 
We deploy Kafka Bitnami Helm Chart for installing Kafak-Python. In the latest published version, Kafka does not need Zookeepr. 
- ./shell-scripts/helm-install.sh
  
##### Deploying Cluster 
- ./shell-scripts/deploy-cluster.sh "${restart_statefullsets}"
  
##### Running Pods  
Running all pods scripts.
- ./shell-scripts/run-all-pods-scripts.sh

### Results

The final result would be in the last pod, which is Merge Pod in path ./request-data.

### Contributaions
Dr. Patrick Bridges, University of New Mexico
Dr. Trilce Estrada, University of New Mexico
Soheila Jafari Khouzani, University of New Mexico
Nidia Vaquera Chavez, University of New Mexico

