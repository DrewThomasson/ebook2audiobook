# Use NVIDIA CUDA base image with Python 3.12 (ensure the correct version)
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 and dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-distutils \
    python3.12-dev \
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

# Update alternatives to use Python 3.12 as the default python3 version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Upgrade pip and setuptools for Python 3.12
RUN python3 -m pip install --upgrade pip setuptools

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
