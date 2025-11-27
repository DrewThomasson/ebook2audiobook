#!/bin/bash

set -euo pipefail

###############################################################################
# CONFIG (URLs must match EXACTLY your original Python definitions)
###############################################################################

DEFAULT_PYTORCH_URL="https://download.pytorch.org/whl"
DEFAULT_JETSON_URL="https://developer.download.nvidia.com/compute/redist/jp"
DEFAULT_COMPILED_URL="https://xxxxxxxxxx/jetson/whl"

# Jetson fixed versions
DEFAULT_JETSON5_TORCH="2.1.0"
DEFAULT_JETSON60_TORCH="2.4.0a0+3bcc3cddb5.nv24.07.16234504"
DEFAULT_JETSON61_TORCH="2.5.0a0+872d972e41.nv24.08.17622132"

###############################################################################
# Extract torch==VERSION from requirements.txt 
###############################################################################
TORCH_VERSION=$(grep -i "^torch==" requirements.txt | head -n1 | cut -d'=' -f3)

if [[ -z "$TORCH_VERSION" ]]; then
    echo "ERROR: torch==X.Y.Z not found in requirements.txt"
    exit 1
fi

echo "Torch base version: $TORCH_VERSION"

###############################################################################
# Python ABI tag
###############################################################################
PYTAG=$(python3 - <<EOF
import sys
print(f"cp{sys.version_info[0]}{sys.version_info[1]}")
EOF
)

echo "Python tag: $PYTAG"

###############################################################################
# STEP 1 — Get backend specs (OS, arch, tag, URL, device)
###############################################################################
JSON=$(python3 - << 'EOF'
import json
from app import detect_device, detect_platform_tag, detect_arch_tag, torch_matrix

device = detect_device()
spec = {
    "device": device,
    "platform": detect_platform_tag(),
    "arch": detect_arch_tag(),
    "tag": torch_matrix.get(device, {}).get("tag"),
    "url": torch_matrix.get(device, {}).get("url"),
}
print(json.dumps(spec))
EOF
)

echo "Python backend JSON: $JSON"

DEVICE=$(echo "$JSON" | jq -r '.device')
PLATFORM=$(echo "$JSON" | jq -r '.platform')
ARCH=$(echo "$JSON" | jq -r '.arch')
TAG=$(echo "$JSON" | jq -r '.tag')
BASE_URL=$(echo "$JSON" | jq -r '.url')

echo "----------------------------------------"
echo "Detected backend:       $DEVICE"
echo "Platform tag:           $PLATFORM"
echo "Architecture:           $ARCH"
echo "Backend tag:            $TAG"
echo "Base URL:               $BASE_URL"
echo "----------------------------------------"


TORCH_WHEEL=""
TORCHAUDIO_WHEEL=""

###############################################################################
# 1) CUDA / ROCm / MPS / XPU (use dynamic torch version)
###############################################################################
if [[ "$DEVICE" =~ ^cu[0-9]+$ ]] || \
   [[ "$DEVICE" =~ ^rocm ]] || \
   [[ "$DEVICE" == "mps" ]] || \
   [[ "$DEVICE" == "xpu" ]]; then

    # SAME FORMAT AS PYTHON CODE:
    # f'{backend_url}/torch/torch-{torch_version_parsed}+{backend_tag}-{default_py_tag}-{backend_os}_{backend_arch}.whl'
    TORCH_WHEEL="${BASE_URL}/torch/torch-${TORCH_VERSION}+${TAG}-${PYTAG}-${PLATFORM}_${ARCH}.whl"

    TORCHAUDIO_WHEEL="${BASE_URL}/torchaudio/torchaudio-${TORCH_VERSION}+${TAG}-${PYTAG}-${PLATFORM}_${ARCH}.whl"
fi

###############################################################################
# 2) Jetson — STRICT mapping from your Python logic
###############################################################################
if [[ "$DEVICE" =~ ^jetson- ]]; then
    JP="${DEVICE#jetson-}"

    case "$JP" in
        51)
            # Python expected: f'{default_compiled_url}/v{tag}/pytorch/...'
            TORCH_WHEEL="${DEFAULT_COMPILED_URL}/v51/pytorch/torch-${DEFAULT_JETSON5_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            TORCHAUDIO_WHEEL="${DEFAULT_COMPILED_URL}/v51/pytorch/torchaudio-${DEFAULT_JETSON5_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            ;;

        60)
            # EXACT original python path:
            # f'{default_jetson_url}/v{backend_tag}/pytorch/torch-{jetson_torch_version}-{default_py_tag}-linux_{backend_arch}.whl'
            TORCH_WHEEL="${DEFAULT_JETSON_URL}/v60/pytorch/torch-${DEFAULT_JETSON60_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            TORCHAUDIO_WHEEL="${DEFAULT_JETSON_URL}/v60/pytorch/torchaudio-${DEFAULT_JETSON60_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            ;;

        61|62|621)
            TORCH_WHEEL="${DEFAULT_JETSON_URL}/v61/pytorch/torch-${DEFAULT_JETSON61_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            TORCHAUDIO_WHEEL="${DEFAULT_JETSON_URL}/v61/pytorch/torchaudio-${DEFAULT_JETSON61_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            ;;

        *)
            echo "Unknown Jetson version: $JP → fallback to CPU"
            DEVICE="cpu"
            ;;
    esac
fi

###############################################################################
# 3) CPU fallback
###############################################################################
if [[ "$DEVICE" == "cpu" ]]; then
    TORCH_WHEEL="${DEFAULT_PYTORCH_URL}/torch-${TORCH_VERSION}+cpu-${PYTAG}-${PLATFORM}_${ARCH}.whl"
    TORCHAUDIO_WHEEL="${DEFAULT_PYTORCH_URL}/torchaudio-${TORCH_VERSION}+cpu-${PYTAG}-${PLATFORM}_${ARCH}.whl"
fi

echo "----------------------------------------"
echo "Torch wheel:     $TORCH_WHEEL"
echo "Torchaudio:      $TORCHAUDIO_WHEEL"
echo "----------------------------------------"

###############################################################################
# STEP 3 — Docker build
###############################################################################
docker build \
    --build-arg TORCH_WHEEL="$TORCH_WHEEL" \
    --build-arg TORCHAUDIO_WHEEL="$TORCHAUDIO_WHEEL" \
    --build-arg DEVICE="$DEVICE" \
    -t ebook2audiobook:"$DEVICE" \
    .

echo "Built image: ebook2audiobook:$DEVICE"
