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