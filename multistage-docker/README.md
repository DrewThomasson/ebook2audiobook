You're absolutely right about that! When using multiple `RUN` commands in a Dockerfile, each creates a new layer. If we install requirements.txt (which includes torch) and then install a different torch version in separate layers, both versions will be stored in the image, taking up extra space.

Let's fix that by combining the commands into a single `RUN` instruction:

```dockerfile
ARG BASE=python:3.12
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
# Copy the application
WORKDIR /app
COPY . /app
# Install UniDic (non-torch dependent)
RUN pip install --no-cache-dir unidic-lite unidic && \
    python3 -m unidic download && \
    mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Second stage for PyTorch installation
FROM base AS pytorch
# Add parameter for PyTorch version with a default empty value
ARG TORCH_VERSION=""

# Extract torch versions from requirements.txt
RUN TORCH_VERSION_REQ=$(grep -E "^torch==" requirements.txt | cut -d'=' -f3) && \
    TORCHAUDIO_VERSION_REQ=$(grep -E "^torchaudio==" requirements.txt | cut -d'=' -f3) && \
    TORCHVISION_VERSION_REQ=$(grep -E "^torchvision==" requirements.txt | cut -d'=' -f3) && \
    echo "Found in requirements: torch==$TORCH_VERSION_REQ torchaudio==$TORCHAUDIO_VERSION_REQ torchvision==$TORCHVISION_VERSION_REQ"

# Install PyTorch with CUDA support if specified
RUN if [ ! -z "$TORCH_VERSION" ]; then \
        TORCH_VERSION_REQ=$(grep -E "^torch==" requirements.txt | cut -d'=' -f3) && \
        TORCHAUDIO_VERSION_REQ=$(grep -E "^torchaudio==" requirements.txt | cut -d'=' -f3) && \
        TORCHVISION_VERSION_REQ=$(grep -E "^torchvision==" requirements.txt | cut -d'=' -f3) && \
        case "$TORCH_VERSION" in \
            "cuda12") \
                pip install --no-cache-dir torch==${TORCH_VERSION_REQ} torchvision==${TORCHVISION_VERSION_REQ} torchaudio==${TORCHAUDIO_VERSION_REQ} --extra-index-url https://download.pytorch.org/whl/cu121 \
                ;; \
            "cuda11") \
                pip install --no-cache-dir torch==${TORCH_VERSION_REQ} torchvision==${TORCHVISION_VERSION_REQ} torchaudio==${TORCHAUDIO_VERSION_REQ} --extra-index-url https://download.pytorch.org/whl/cu118 \
                ;; \
            "cpu") \
                pip install --no-cache-dir torch==${TORCH_VERSION_REQ} torchvision==${TORCHVISION_VERSION_REQ} torchaudio==${TORCHAUDIO_VERSION_REQ} --extra-index-url https://download.pytorch.org/whl/cpu \
                ;; \
            *) \
                pip install --no-cache-dir $TORCH_VERSION \
                ;; \
        esac && \
        # Install remaining requirements, skipping torch packages
        grep -v -E "^torch==|^torchvision==|^torchaudio==" requirements.txt > requirements_no_torch.txt && \
        pip install --no-cache-dir --upgrade -r requirements_no_torch.txt && \
        rm requirements_no_torch.txt; \
    else \
        # Install all requirements as specified
        pip install --no-cache-dir --upgrade -r requirements.txt; \
    fi

# Do a test run to pre-download and bake base models into the image
RUN echo "This is a test sentence." > test.txt && \
    python app.py --headless --ebook test.txt --script_mode full_docker && \
    rm test.txt
# Expose the required port
EXPOSE 7860
# Start the Gradio app with the required flag
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]

```

```text
.git
.github
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.dockerignore
.pytest_cache
.coverage
htmlcov/
.vscode/
.idea/
docker-cache/

```

```bash
#!/bin/bash
set -e

# Configuration
PLATFORMS="linux/amd64,linux/arm64"
IMAGE_NAME="myapp"
REPOSITORY="myrepo"  # Replace with your registry/repo name

# Create the builder instance if it doesn't exist
docker buildx create --name multi-arch-builder --use --bootstrap || true
echo "Created and bootstrapped multi-arch-builder"

# Build the base image first (all architectures, no torch-specific stuff)
echo "Building base image for all architectures..."
docker buildx build \
  --platform=$PLATFORMS \
  --target base \
  --tag $REPOSITORY/$IMAGE_NAME:base \
  --push \
  .

echo "Base image built and pushed"

# Build default version (using torch from requirements.txt)
echo "Building default variant..."
docker buildx build \
  --platform=$PLATFORMS \
  --tag $REPOSITORY/$IMAGE_NAME:default \
  --push \
  .

# Build variants for each torch version
for VARIANT in cuda12 cuda11 cpu; do
  echo "Building $VARIANT variant for all architectures..."
  docker buildx build \
    --platform=$PLATFORMS \
    --build-arg TORCH_VERSION=$VARIANT \
    --tag $REPOSITORY/$IMAGE_NAME:$VARIANT \
    --push \
    .
  
  echo "$VARIANT variant built and pushed"
done

# Clean up
docker buildx rm multi-arch-builder
echo "Build complete for all variants"

```

```bash
#!/bin/bash
set -e

# Configuration 
IMAGE_NAME="myapp"

# Create the builder instance if it doesn't exist
docker buildx create --name local-builder --use --bootstrap || true
echo "Created and bootstrapped local-builder"

# Build the base image first (all architectures, no torch-specific stuff)
echo "Building base image..."
docker buildx build \
  --load \
  --target base \
  --tag $IMAGE_NAME:base \
  .

echo "Base image built locally"

# Build default version (using torch from requirements.txt)
echo "Building default variant..."
docker buildx build \
  --load \
  --tag $IMAGE_NAME:default \
  .

# Build variants for each torch version
for VARIANT in cuda12 cuda11 cpu; do
  echo "Building $VARIANT variant..."
  docker buildx build \
    --load \
    --build-arg TORCH_VERSION=$VARIANT \
    --tag $IMAGE_NAME:$VARIANT \
    .
  
  echo "$VARIANT variant built locally"
done

# Clean up
docker buildx rm local-builder
echo "Build complete for all variants"

```

## Updated Usage Guide

This improved approach addresses the storage efficiency issue by making these key changes:

1. When a custom torch version is specified, we:
   - Create a temporary requirements file without the torch line
   - Install all requirements except torch
   - Install the specific torch version
   - Remove the temporary file

2. We use a single `RUN` instruction for the entire process, ensuring that only one layer is created and only one torch version is stored in the image.

### Setup Instructions

1. Save the Dockerfile to your project directory
2. Save the `.dockerignore` file to your project directory
3. Choose one of the build scripts based on your needs:
   - Use `buildx-script-final.sh` for multi-architecture builds with registry push
   - Use `local-buildx-script-final.sh` for local single-architecture builds

4. Make the script executable and run it:

```bash
# For multi-architecture builds
chmod +x buildx-script-final.sh
./buildx-script-final.sh

# For local builds
chmod +x local-buildx-script-final.sh
./local-buildx-script-final.sh
```

### How It Works

1. The optimization uses `grep -v "^torch"` to create a temporary requirements file without the torch line
2. This ensures we only install the specific torch version we want
3. All installation happens in a single `RUN` instruction, creating only one layer
4. The temporary file is removed at the end of the same `RUN` instruction

### Example Commands

You can also run individual builds manually:

```bash
# Build with CUDA 12
docker build --build-arg TORCH_VERSION=cuda12 -t myapp:cuda12 .

# Build with a custom torch version string
docker build --build-arg TORCH_VERSION="torch==2.0.0+cu117 --extra-index-url https://download.pytorch.org/whl/cu117" -t myapp:custom .
```

```bash
docker build -t your-image-name . # Should also work
```



### Benefits of This Approach

1. **Storage Efficiency**: Only one torch version is stored in the image
2. **Simplicity**: No complex file manipulation or shell scripts
3. **Layer Efficiency**: Uses a single layer for all Python dependencies
4. **Flexibility**: Works with both predefined and custom torch versions

This approach gives you the best of both worlds: the storage efficiency of modifying requirements.txt, but with the simplicity of a direct pip install.
