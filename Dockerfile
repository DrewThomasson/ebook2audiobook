ARG BASE=python:3.12
ARG BASE_IMAGE=base
FROM ${BASE} AS base

# Set environment PATH for local installations
ENV PATH="/root/.local/bin:$PATH"
# Set non-interactive mode to prevent tzdata prompt
ENV DEBIAN_FRONTEND=noninteractive
# Install system packages
RUN apt-get update && \
    apt-get install -y gcc g++ make wget git calibre ffmpeg libmecab-dev mecab mecab-ipadic-utf8 libsndfile1-dev libc-dev curl espeak-ng sox && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Install Rust compiler
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
WORKDIR /app
# Install UniDic (non-torch dependent)
RUN pip install --no-cache-dir unidic-lite unidic && \
    python3 -m unidic download && \
    mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Second stage for PyTorch installation + swappable base image if you want to use a pulled image
FROM $BASE_IMAGE AS pytorch
# Add parameter for PyTorch version with a default empty value
ARG TORCH_VERSION=""
# Add parameter to control whether to skip the XTTS test
ARG SKIP_XTTS_TEST="false"

# Copy the application
WORKDIR /app
COPY . /app

# Install requirements.txt
pip install --no-cache-dir --upgrade -r requirements.txt; \

# Do a test run to pre-download and bake base models into the image, but only if SKIP_XTTS_TEST is not true
RUN if [ "$SKIP_XTTS_TEST" != "true" ]; then \
        echo "Running XTTS test to pre-download models..."; \
        if [ "$TORCH_VERSION" = "xpu" ]; then \
            TORCH_DEVICE_BACKEND_AUTOLOAD=0 python app.py --headless --ebook test.txt --script_mode full_docker; \
        else \
            python app.py --headless --language eng --ebook "tools/workflow-testing/test1.txt" --tts_engine XTTSv2 --script_mode full_docker; \
        fi; \
    else \
        echo "Skipping XTTS test run as requested."; \
    fi

# Expose the required port
EXPOSE 7860
# Start the Gradio app with the required flag
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]


#docker build --pull --build-arg BASE_IMAGE=athomasson2/ebook2audiobook:latest -t your-image-name .
#The --pull flag forces Docker to always try to pull the latest version of the image, even if it already exists locally.
#Without --pull, Docker will only use the local version if it exists, which might not be the latest.

# Example build commands:
# For CUDA 11.8: docker build --build-arg TORCH_VERSION=cuda118 -t your-image-name .
# For CUDA 12.8: docker build --build-arg TORCH_VERSION=cuda128 -t your-image-name .
# For CUDA 12.1: docker build --build-arg TORCH_VERSION=cuda121 -t your-image-name .
# For ROCm: docker build --build-arg TORCH_VERSION=rocm -t your-image-name .
# For CPU: docker build --build-arg TORCH_VERSION=cpu -t your-image-name .
# For XPU: docker build --build-arg TORCH_VERSION=xpu -t your-image-name .
# Default (no TORCH_VERSION): docker build -t your-image-name .
