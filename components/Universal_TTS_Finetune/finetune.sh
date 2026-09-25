#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Automatically find the nvidia CUDA runtime libs in the virtual environment
NVIDIA_DIR=$(find "$VENV_DIR" -type d -path "*/nvidia/cu[0-9]*/lib" -print -quit)
if [[ -n "$NVIDIA_DIR" ]]; then
  export LD_LIBRARY_PATH="$NVIDIA_DIR:${LD_LIBRARY_PATH:-}"
fi

# Ignore conflicting local user-site packages
export PYTHONNOUSERSITE=1

# Execute the headless CLI using the virtualenv python interpreter
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/headless_cli.py" "$@"
