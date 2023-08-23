# Use the official Ubuntu base image
FROM ubuntu:latest

# Update the package list and install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip libreoffice tesseract-ocr libtesseract-dev build-essential \
    poppler-utils libsm6 libxext6 libxrender-dev 

# Upgrade pip and install wheel
RUN python3 -m pip install --upgrade pip && \
    pip install wheel

# Copy the requirements.txt and mini-iron-ripper.py files
COPY requirements.txt /app/requirements.txt
COPY mini-iron-ripper.py /app/mini-iron-ripper.py

COPY utils /app/utils

# Set the working directory
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Set the default command to run when the container starts
CMD ["/bin/bash"]
