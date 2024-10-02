# Use the NVIDIA CUDA base image that matches your requirements
FROM nvidia/cuda:12.1.0-runtime-ubuntu20.04

# Set the working directory
WORKDIR /app

# Install necessary packages and Python 3.8.10
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    gnupg \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    software-properties-common && \
    # Add deadsnakes PPA for Python 3.8
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-distutils python3-pip && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-cli && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Update alternatives to set python3 to python3.8
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-deps -r requirements.txt

# Copy application files
COPY . .

# Additional setup steps
RUN apt-get update && \
    cp chromedriver /usr/bin/chromedriver && \
    ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && \
    DEBIAN_FRONTEND=noninteractive apt --assume-yes install ./google-chrome-stable_current_amd64.deb

# Authenticate using the service account
RUN gcloud auth activate-service-account --key-file=/app/bb-hackathon-app.json

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/bb-hackathon-app.json

# Expose the application port
EXPOSE 8000

CMD ["python3", "main.py"]
