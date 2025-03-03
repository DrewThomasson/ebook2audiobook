#!/bin/bash
set -e

echo "Selected PyTorch variant: $PYTORCH_VARIANT"

case "$PYTORCH_VARIANT" in
    cuda11)
        pip install /pytorch_wheels/torch_cuda11.whl
        ;;
    cuda12)
        pip install /pytorch_wheels/torch_cuda12.whl
        ;;
    amd)
        pip install /pytorch_wheels/torch_amd.whl
        ;;
    intel)
        pip install /pytorch_wheels/torch_intel.whl
        ;;
    *)
        echo "Invalid PYTORCH_VARIANT: $PYTORCH_VARIANT"
        exit 1
        ;;
esac

# Execute the command passed as arguments to the entrypoint.
exec "$@"
