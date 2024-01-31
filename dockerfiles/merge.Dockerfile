# Using Python slim-bullseye for a lightweight image
FROM python:3.7-slim-bullseye

# Create a non-root user in a single command
RUN groupadd -g 1000 sjafari && \
    useradd -m -u 1000 -g sjafari -s /bin/bash sjafari

# Install necessary packages in one layer and perform cleanup to reduce image size
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    openjdk-17-jdk \
    libopenmpi-dev \
    bash \
    wget \
    pkg-config \
    libhdf5-dev \
    nano \
    vim \
    screen \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download and setup Kafka
WORKDIR /kafka
RUN wget -O - https://downloads.apache.org/kafka/3.4.1/kafka_2.13-3.4.1.tgz | tar xzf - -C /kafka --strip-components=1 \
    && chown -R sjafari:sjafari /kafka

# Install Python dependencies
WORKDIR /install
COPY dockerfiles/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir requests mpi4py jupyterlab \
    && chown -R sjafari:sjafari /install

# Set the working directory for your code
WORKDIR /app
COPY ./src/merge .
COPY ./src/run-jupyterlab.sh .
COPY ./src/pipeline-configmap.yaml .
RUN chown -R sjafari:sjafari /app \
    && chmod 755 runmerge.sh

# Environment variables
ENV KAFKA_INSTALL_PATH /kafka/bin/

# Switch to the non-root user
USER sjafari

# Command to run
CMD ["bash", "sleep infinity"]
