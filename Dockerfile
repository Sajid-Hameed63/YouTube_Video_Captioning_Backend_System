
#########################################################################################################################################
# this is giving 2.78 gb image size
# Stage 1: Use lightweight Python Alpine for building the application
FROM python:3.10-alpine AS builder

# Install essential Alpine packages for building
RUN apk add --no-cache \
    bash \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    g++ \
    make \
    openssl-dev \
    ffmpeg \
    git

# Upgrade pip and set up working directory
RUN python3 -m ensurepip && pip3 install --no-cache --upgrade pip
WORKDIR /youtube_video_captioning_system

# Copy requirements.txt but do not install dependencies yet
COPY requirements_YouTube_Video_Captioning_Backend_System.txt .

# Copy the application files
COPY . .

# Stage 2: Switch to NVIDIA CUDA image for GPU support
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04 AS runtime

# Install Python and necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /youtube_video_captioning_system

# Copy the application from the builder stage
COPY --from=builder /youtube_video_captioning_system /youtube_video_captioning_system

# Expose the port Flask will use
EXPOSE 5000

# Show a message to manually install the requirements
CMD ["sh", "-c", "echo 'Please run pip3 install -r requirements_YouTube_Video_Captioning_Backend_System.txt to install the necessary packages' && /bin/bash"]
#########################################################################################################################################

