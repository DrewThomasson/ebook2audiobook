# Use NVIDIA CUDA base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    wget \
    git \
    ffmpeg \
    libegl1 \
    libopengl0 \
    libxcb-cursor0 \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    && rm -rf /var/lib/apt/lists/*

# Install Calibre using the official installer
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin

# Create and set working directory
WORKDIR /app

# Clone the repository (fixed mv command)
RUN git clone https://github.com/DrewThomasson/ebook2audiobook.git temp_repo && \
    mv temp_repo/* ./ 2>/dev/null || true && \
    mv temp_repo/.[!.]* ./ 2>/dev/null || true && \
    rm -rf temp_repo

# Install Python dependencies
RUN pip install mecab-python3
RUN pip install -r requirements.txt

# Expose the Gradio port
EXPOSE 7860

# Start the app with GPU support and public sharing
CMD ["python3", "app.py", "--share"]
