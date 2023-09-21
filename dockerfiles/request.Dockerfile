# Use the python alpine base container, it's very light weight.
FROM python:slim-bullseye
RUN apt update \
    && apt install -y \
    build-essential \
    python3-dev \
    openjdk-17-jdk \
    libopenmpi-dev \
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

WORKDIR /install
COPY dockerfiles/request-requirements.txt .

# Install any dependencies you need
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools wheel \
    && pip install -r request-requirements.txt

# Where your code will be located on the container
WORKDIR /app
ENV IS_CONTAINERIZED True
ENV KAFKA_INSTALL_PATH /kafka/bin/

# Copy all files from the directory where the dockerfile is located except anything added to a .dockerignore file
# You can also specify files you want moved vs files you do not want moved and their destination directories

RUN mkdir -p ./request-data
COPY ./dockerfiles/pipeline-configmap.yaml .
COPY  ./src/request .
COPY  ./data/simulator request-data

# Do any compilation or other things you need to do here with RUN and ENV commands
# Run the application as a list of arguments
#CMD ["bash", "./runuvicorn.sh"]
#CMD ["bash", "sleep infinity"]

