# Use an official NVIDIA CUDA image with cudnn8 and Ubuntu 20.04 as the base
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# Set non-interactive installation to avoid timezone and other prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages including Miniconda
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    espeak \
    espeak-ng \
    ffmpeg \
    tk \
    mecab \
    libmecab-dev \
    libegl1 \
    libopengl0 \
    libxcb-cursor0 \
    mecab-ipadic-utf8 \
    build-essential \
    calibre \
    && rm -rf /var/lib/apt/lists/*

RUN ebook-convert --version

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh


# Set PATH to include conda
ENV PATH=/opt/conda/bin:$PATH

# Create a conda environment with Python 3.12
RUN conda create -n ebookenv python=3.12 -y

# Clone the ebook2audiobookXTTS repository
RUN git clone https://github.com/DrewThomasson/ebook2audiobook.git .

# Set the working directory in the container
WORKDIR /ebook2audiobook

# Activate the conda environment
SHELL ["conda", "run", "-n", "ebookenv", "/bin/bash", "-c"]

# Install Python dependencies using conda and pip
RUN conda install -n ebookenv -c conda-forge \
    pydub \
    nltk \
    mecab-python3 \
    && pip install --no-cache-dir -r requirements.txt

# Expose the Gradio port
EXPOSE 7860

# Set the command to run your GUI application using the conda environment
CMD ["conda", "run", "--no-capture-output", "-n", "ebookenv", "python", "app.py"]
