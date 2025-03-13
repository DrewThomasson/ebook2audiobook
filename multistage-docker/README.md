I'll provide you with all the files and commands needed to efficiently build multi-architecture Docker images with different PyTorch versions.

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
RUN curl --proto '=https' --tlsv1.2 -sSf "https://sh.rustup.rs" | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy everything except requirements.txt
WORKDIR /app
COPY . /app
RUN if [ -f requirements.txt ]; then cp requirements.txt requirements.txt.orig; fi

# Install UniDic (non-torch dependent)
RUN pip install --no-cache-dir unidic-lite unidic
RUN python3 -m unidic download
RUN mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Second stage for PyTorch installation
FROM base AS pytorch

# Add parameter for PyTorch version
ARG TORCH_VERSION=default

# Define torch versions
RUN echo '#!/bin/bash \n\
declare -A TORCH_VERSIONS \n\
TORCH_VERSIONS["default"]="torch" \n\
TORCH_VERSIONS["cuda12"]="torch==2.2.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121" \n\
TORCH_VERSIONS["cuda11"]="torch==2.2.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118" \n\
TORCH_VERSIONS["cpu"]="torch==2.2.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu" \n\
\n\
if [ -n "${TORCH_VERSIONS[$TORCH_VERSION]}" ]; then \n\
  echo "Using predefined torch version: $TORCH_VERSION -> ${TORCH_VERSIONS[$TORCH_VERSION]}" \n\
  TORCH_LINE="${TORCH_VERSIONS[$TORCH_VERSION]}" \n\
else \n\
  echo "Using custom torch version: $TORCH_VERSION" \n\
  TORCH_LINE="$TORCH_VERSION" \n\
fi \n\
\n\
cp requirements.txt.orig requirements.txt \n\
sed -i "s|^torch.*$|${TORCH_LINE}|" requirements.txt \n\
cat requirements.txt | grep torch \n\
' > /app/update_torch.sh && chmod +x /app/update_torch.sh

# Replace torch line in requirements.txt
RUN /app/update_torch.sh $TORCH_VERSION

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Do a test run to pre-download and bake base models into the image
RUN echo "This is a test sentence." > test.txt 
RUN python app.py --headless --ebook test.txt --script_mode full_docker
RUN rm test.txt

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

# Create the builder instance
docker buildx create --name multi-arch-builder --use --bootstrap || true
echo "Created and bootstrapped multi-arch-builder"

# Build the base image first (all architectures, no torch-specific stuff)
echo "Building base image for all architectures..."
docker buildx build \
  --platform=$PLATFORMS \
  --target base \
  --tag $REPOSITORY/$IMAGE_NAME:base \
  --push \
  --cache-to=type=registry,ref=$REPOSITORY/$IMAGE_NAME:base-cache \
  .

echo "Base image built and pushed"

# Build variants for each torch version
for VARIANT in default cuda12 cuda11 cpu; do
  echo "Building $VARIANT variant for all architectures..."
  docker buildx build \
    --platform=$PLATFORMS \
    --build-arg TORCH_VERSION=$VARIANT \
    --tag $REPOSITORY/$IMAGE_NAME:$VARIANT \
    --cache-from=type=registry,ref=$REPOSITORY/$IMAGE_NAME:base-cache \
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
PLATFORMS="linux/amd64,linux/arm64"
IMAGE_NAME="myapp"

# Create a local cache directory
mkdir -p ./docker-cache

# Create the builder instance
docker buildx create --name local-builder --use --bootstrap || true
echo "Created and bootstrapped local-builder"

# Build the base image first (all architectures, no torch-specific stuff)
echo "Building base image for all architectures..."
docker buildx build \
  --platform=$PLATFORMS \
  --target base \
  --tag $IMAGE_NAME:base \
  --cache-to=type=local,dest=./docker-cache \
  --output=type=docker \
  .

echo "Base image built locally"

# Build variants for each torch version
for VARIANT in default cuda12 cuda11 cpu; do
  echo "Building $VARIANT variant for all architectures..."
  docker buildx build \
    --platform=$PLATFORMS \
    --build-arg TORCH_VERSION=$VARIANT \
    --tag $IMAGE_NAME:$VARIANT \
    --cache-from=type=local,src=./docker-cache \
    --output=type=docker \
    .
  
  echo "$VARIANT variant built locally"
done

# Clean up
docker buildx rm local-builder
echo "Build complete for all variants"

```

## Usage Instructions

1. Save the Dockerfile to your project directory
2. Save the `.dockerignore` file to your project directory
3. Choose one of the build scripts based on your needs:
   - Use `build-script.sh` if you want to push to a registry (recommended for best caching)
   - Use `local-build-script.sh` if you want to build locally without a registry

4. Make the script executable and run it:

```bash
# For registry-based builds
chmod +x build-script.sh
./build-script.sh

# For local builds
chmod +x local-build-script.sh
./local-build-script.sh
```

## Important Notes

1. **Registry Setup**: For the registry-based script, replace `myrepo` with your actual Docker registry/repository name. You'll need to be logged in to this registry:
   ```bash
   docker login your-registry.com
   ```

2. **ARM Compatibility**: Make sure your application and dependencies are compatible with ARM architecture. Some Python packages might not have ARM versions.

3. **Build Time**: The first build will take longer as it needs to download and compile everything. Subsequent builds will be faster.

4. **Caching Efficiency**: The registry-based method is more efficient for multi-architecture builds as it can reuse layers across architectures.

5. **Local Testing**: Before pushing to a registry, you can test locally with:
   ```bash
   docker run --rm -it myapp:default
   ```

This setup ensures that the base image with all the non-PyTorch dependencies is built only once per architecture, and then each PyTorch variant builds on top of that base image, maximizing cache reuse and minimizing build time.