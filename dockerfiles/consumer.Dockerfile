FROM python:slim-bullseye
RUN apt-get update \
    && apt-get install -y \
    build-essential \
    python3-dev \
    openjdk-17-jdk \
    bash \
    wget \
    uuid-runtime \
    pkg-config \
    libhdf5-dev \
    nano \
    vim \
    screen \
    procps

WORKDIR /kafka
RUN wget -O - https://downloads.apache.org/kafka/3.4.1/kafka_2.13-3.4.1.tgz | tar xzf - -C /kafka --strip-components=1

#WORKDIR /install
COPY dockerfiles/requirements.txt .
#COPY src/hdf5.py .

# Install any dependencies you need
RUN pip install --upgrade setuptools wheel \
    && pip install -r requirements.txt

# Where your code will be located on the container

WORKDIR /app
ENV IS_CONTAINERIZED True
ENV KAFKA_INSTALL_PATH /kafka/bin/
#ENV PYCHARM_PROJECT_PATH /home/soheila/PycharmProjects/PipelineProject
# Copy all files from the directory where the dockerfile is located except anything added to a .dockerignore file
# You can also specify files you want moved vs files you do not want moved and their destination directories

COPY ./src/consumer .
COPY ./src/pipeline-configmap.yaml .

# Run the application as a list of arguments
CMD ["bash", "sleep infinity"]
