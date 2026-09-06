#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image_tag="${BREEZE_IMAGE:-breeze-pytorch-infer:latest}"
flash_attn_cuda_archs="${FLASH_ATTN_CUDA_ARCHS:-90}"

docker build \
  --file "$repo_dir/docker/Dockerfile" \
  --tag "$image_tag" \
  --build-arg "FLASH_ATTN_CUDA_ARCHS=$flash_attn_cuda_archs" \
  "$repo_dir"
