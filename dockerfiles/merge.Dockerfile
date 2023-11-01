# Use the python alpine base container, it's very light weight.
FROM python:slim-bullseye
RUN apt update \
    && apt install -y \
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
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get install libopenmpi-dev
WORKDIR /kafka
RUN wget -O - https://downloads.apache.org/kafka/3.4.1/kafka_2.13-3.4.1.tgz | tar xzf - -C /kafka --strip-components=1

WORKDIR /install
COPY dockerfiles/requirements.txt .
# Install any dependencies you need
RUN pip install --upgrade setuptools wheel \
    && pip install -r requirements.txt \
    && pip3 install requests \
    && pip3 install mpi4py

# Where your code will be located on the container
WORKDIR /app
ENV IS_CONTAINERIZED True
ENV KAFKA_INSTALL_PATH /kafka/bin/

# Copy all files from the directory where the dockerfile is located except anything added to a .dockerignore file
# You can also specify files you want moved vs files you do not want moved and their destination directories
COPY  ./src/merge .
COPY ./src/pipeline-configmap.yaml .

# Do any compilation or other things you need to do here with RUN and ENV commands
# Run the application as a list of arguments
#CMD ["bash", "./examplerun.sh"]
CMD ["bash", "sleep infinity"]
