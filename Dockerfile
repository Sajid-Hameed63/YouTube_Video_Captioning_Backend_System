# Base image from nvidia for GPU support, but will also work on CPU
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Set environment variable to allow PyTorch to decide whether to use GPU or CPU
ENV TORCH_CUDA_ARCH_LIST="All"

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install whisper dependencies
RUN pip3 install --upgrade pip

# Install PyTorch with CUDA support if GPU is available
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other Python dependencies
COPY requirements_YouTube_Video_Captioning_Backend_System.txt /youtube_video_captioning_system/requirements.txt
RUN pip3 install -r /youtube_video_captioning_system/requirements.txt

# Set up working directory
WORKDIR /youtube_video_captioning_system

# Copy all application files
COPY . /youtube_video_captioning_system

# Expose the port that Flask will run on
EXPOSE 5000

# Run the Flask app
CMD ["python3", "app.py"]
