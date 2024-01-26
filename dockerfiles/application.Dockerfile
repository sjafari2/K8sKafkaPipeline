
FROM python:3.7-slim-bullseye

# Set work directory and copy only the necessary files for requirements installation
WORKDIR /install
COPY dockerfiles/requirements.txt .

# Combine installation commands and clean-up in one layer to minimize layering
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    openjdk-17-jdk \
    openmpi-bin \
    libopenmpi-dev \
    mpich \
    bash \
    wget \
    pkg-config \
    libhdf5-dev \
    nano \
    vim \
    screen \
    procps \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt mpi4py jupyterlab \
    && python -m spacy download en_core_web_sm \
    && python -m nltk.downloader stopwords

# Create user and group
RUN groupadd -g 1000 sjafari && \
    useradd -m -u 1000 -g sjafari -s /bin/bash sjafari

# Set Kafka work directory, download and extract Kafka, and change ownership
WORKDIR /kafka
RUN wget -O - https://downloads.apache.org/kafka/3.4.1/kafka_2.13-3.4.1.tgz | tar xzf - -C /kafka --strip-components=1 \
    && chown -R sjafari:sjafari /kafka /install

# Set the work directory for the application
WORKDIR /app
COPY ./src/application .
COPY ./src/run-jupyterlab.sh .
COPY ./dockerfiles/pipeline-configmap.yaml .

# Change the owner of all files under /app and /install to sjafari and give necessary permissions
RUN chown -R sjafari:sjafari /app \
    && chmod 755 runapplication.sh

# Environment variables
ENV KAFKA_INSTALL_PATH /kafka/bin/

# Switch to non-root user
USER sjafari

# Command to run
CMD ["bash", "sleep infinity"]
