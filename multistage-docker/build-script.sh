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