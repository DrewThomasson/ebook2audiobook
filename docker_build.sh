#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# Ensure required Python module exists (needed for detect_device)
###############################################################################
if ! python3 -c "import packaging" 2>/dev/null; then
    echo "Installing missing Python module: packaging"
    pip3 install --user packaging
fi

###############################################################################
# CONFIG — exact URLs from your Python script
###############################################################################

DEFAULT_PYTORCH_URL="https://download.pytorch.org/whl"
DEFAULT_JETSON_URL="https://developer.download.nvidia.com/compute/redist/jp"
DEFAULT_COMPILED_URL="https://xxxxxxxxxx/jetson/whl"

# Jetson version → fixed torch versions
DEFAULT_JETSON5_TORCH="2.1.0"
DEFAULT_JETSON60_TORCH="2.4.0a0+3bcc3cddb5.nv24.07.16234504"
DEFAULT_JETSON61_TORCH="2.5.0a0+872d972e41.nv24.08.17622132"

###############################################################################
# Extract torch base version from requirements.txt
###############################################################################

TORCH_VERSION=$(grep -i "^torch" requirements.txt \
    | head -n1 \
    | sed 's/[<>=!]*//g' \
    | sed 's/torch//I' \
    | sed 's/[[:space:]]*//g' \
    | sed 's/+.*//')

if [[ -z "$TORCH_VERSION" ]]; then
    echo "❌ ERROR: Cannot detect torch version from requirements.txt"
    exit 1
fi

echo "✔ Torch version extracted: ${TORCH_VERSION}"

###############################################################################
# Detect Python ABI Tag (e.g., cp312)
###############################################################################

PYTAG=$(python3 - <<EOF
import sys
print(f"cp{sys.version_info[0]}{sys.version_info[1]}")
EOF
)

echo "✔ Python ABI tag: ${PYTAG}"

###############################################################################
# STEP 1 — Python GPU/Backend Detection
###############################################################################

echo "Running Python backend detection..."

JSON=$(python3 - << 'EOF'
import json
from app import detect_device, detect_platform_tag, detect_arch_tag, torch_matrix

device = detect_device()
spec = {
    "device": device,
    "platform": detect_platform_tag(),
    "arch": detect_arch_tag(),
    "tag": torch_matrix.get(device, {}).get("tag"),
    "url": torch_matrix.get(device, {}).get("url")
}
print(json.dumps(spec))
EOF
)

echo "✔ Backend JSON: $JSON"

DEVICE=$(echo "$JSON" | jq -r '.device')
PLATFORM=$(echo "$JSON" | jq -r '.platform')
ARCH=$(echo "$JSON" | jq -r '.arch')
TAG=$(echo "$JSON" | jq -r '.tag')
BASE_URL=$(echo "$JSON" | jq -r '.url')

echo "---------------------------------------------"
echo "Detected backend device: $DEVICE"
echo "Platform tag:            $PLATFORM"
echo "Architecture:            $ARCH"
echo "Backend tag:             $TAG"
echo "Base URL:                $BASE_URL"
echo "---------------------------------------------"

###############################################################################
# STEP 2 — Build Torch / Torchaudio wheel URLs
###############################################################################

TORCH_WHEEL=""
TORCHAUDIO_WHEEL=""

### CUDA / ROCm / MPS / XPU — dynamic torch version
if [[ "$DEVICE" =~ ^cu[0-9]+$ ]] || \
   [[ "$DEVICE" =~ ^rocm ]] || \
   [[ "$DEVICE" == "mps" ]] || \
   [[ "$DEVICE" == "xpu" ]]; then

    TORCH_WHEEL="${BASE_URL}/torch/torch-${TORCH_VERSION}+${TAG}-${PYTAG}-${PLATFORM}_${ARCH}.whl"
    TORCHAUDIO_WHEEL="${BASE_URL}/torchaudio/torchaudio-${TORCH_VERSION}+${TAG}-${PYTAG}-${PLATFORM}_${ARCH}.whl"
fi

### Jetson — fixed versions & strict URL structure
if [[ "$DEVICE" =~ ^jetson- ]]; then
    JP="${DEVICE#jetson-}"

    case "$JP" in
        51)
            TORCH_WHEEL="${DEFAULT_COMPILED_URL}/v51/pytorch/torch-${DEFAULT_JETSON5_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            TORCHAUDIO_WHEEL="${DEFAULT_COMPILED_URL}/v51/pytorch/torchaudio-${DEFAULT_JETSON5_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            ;;

        60)
            TORCH_WHEEL="${DEFAULT_JETSON_URL}/v60/pytorch/torch-${DEFAULT_JETSON60_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            TORCHAUDIO_WHEEL="${DEFAULT_JETSON_URL}/v60/pytorch/torchaudio-${DEFAULT_JETSON60_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            ;;

        61|62|621)
            TORCH_WHEEL="${DEFAULT_JETSON_URL}/v61/pytorch/torch-${DEFAULT_JETSON61_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            TORCHAUDIO_WHEEL="${DEFAULT_JETSON_URL}/v61/pytorch/torchaudio-${DEFAULT_JETSON61_TORCH}-${PYTAG}-linux_${ARCH}.whl"
            ;;

        *)
            echo "⚠ Unknown Jetson version $JP → fallback to CPU"
            DEVICE="cpu"
            ;;
    esac
fi

### CPU fallback
if [[ "$DEVICE" == "cpu" ]]; then
    TORCH_WHEEL="${DEFAULT_PYTORCH_URL}/torch-${TORCH_VERSION}+cpu-${PYTAG}-${PLATFORM}_${ARCH}.whl"
    TORCHAUDIO_WHEEL="${DEFAULT_PYTORCH_URL}/torchaudio-${TORCH_VERSION}+cpu-${PYTAG}-${PLATFORM}_${ARCH}.whl"
fi

echo "---------------------------------------------"
echo "Torch wheel URL:        $TORCH_WHEEL"
echo "Torchaudio wheel URL:   $TORCHAUDIO_WHEEL"
echo "---------------------------------------------"

###############################################################################
# STEP 3 — WRITE .env for Docker Compose
###############################################################################

cat > .env <<EOF
TORCH_WHEEL=${TORCH_WHEEL}
TORCHAUDIO_WHEEL=${TORCHAUDIO_WHEEL}
DEVICE=${DEVICE}
EOF

echo "✔ .env written:"
cat .env

###############################################################################
# STEP 4 — DOCKER COMPOSE BUILD
###############################################################################

echo "🚀 Building image using docker compose…"
docker compose build --progress plain --no-cache

echo "✔ Build complete."
echo "✔ Image built: ebook2audiobook:${DEVICE}"