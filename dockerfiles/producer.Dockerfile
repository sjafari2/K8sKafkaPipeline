# Use a more specific base image if possible, otherwise use the slim version for minimal footprint
FROM python:3.7-slim-bullseye

# Set work directory and copy only the necessary files for requirements installation
WORKDIR /install
COPY dockerfiles/requirements.txt .

# Combine installation commands and clean-up in one layer to minimize layering
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    openjdk-17-jdk \
    bash \
    wget \
    pkg-config \
    libhdf5-dev \
    nano \
    vim \
    screen \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir nltk jupyterlab \
    && python3 -m spacy download en_core_web_sm \
    && python3 -m nltk.downloader stopwords

# Create user and group
RUN groupadd -g 1000 sjafari && \
    useradd -m -u 1000 -g sjafari -s /bin/bash sjafari

# Set work directories and change ownership
WORKDIR /kafka
RUN chown -R sjafari:sjafari /kafka /install

WORKDIR /app
COPY ./src/producer .
COPY ./src/run-jupyterlab.sh .
COPY ./src/pipeline-configmap.yaml .

# Change the owner of all files under /app and /install to sjafari and give necessary permissions
RUN chown -R sjafari:sjafari /app /install \
    && chmod 755 /app/runproducer.sh

# Environment variables
ENV KAFKA_INSTALL_PATH /kafka/bin/

# Switch to non-root user
USER sjafari

# Command to run
CMD ["bash", "sleep infinity"]
