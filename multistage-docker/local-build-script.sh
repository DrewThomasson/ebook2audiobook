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