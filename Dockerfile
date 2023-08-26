# Use python as the base image
FROM python:3.10.8-slim-buster

# Update the package list and install dependencies
# Note: apt-get doesn't support '>=', so it'll always install the latest version available
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    libreoffice \
    tesseract-ocr \
    libtesseract-dev \
    build-essential \
    poppler-utils \
    libsm6 \
    libxext6 \
    libxrender-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
# For pip, you can specify version like pip>=21.0
RUN python3 -m pip install "pip>=21.0" --no-cache-dir && \
    pip install "wheel>=0.36.0" --no-cache-dir

# Copy the requirements.txt and mini-iron-ripper.py files
COPY requirements.txt /app/requirements.txt
COPY mini-iron-ripper.py /app/mini-iron-ripper.py

COPY utils /app/utils

# Set the working directory
WORKDIR /app

# Install Python dependencies
# In your requirements.txt, you can specify packages like:
# package_name>=1.0.0
RUN pip install -r requirements.txt --no-cache-dir

# Set the default command to run when the container starts
CMD ["/bin/bash"]
