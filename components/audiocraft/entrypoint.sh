#!/bin/sh
set -e

echo "🚀 Starting Audiocraft container..."
echo "🔍 Checking Torch backend:"

python3 - <<'PYCODE'
import torch
print("Torch version:", torch.__version__)
print("Device:", "GPU" if torch.cuda.is_available() else "CPU")
PYCODE

exec python3 "$@"