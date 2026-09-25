#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." >/dev/null 2>&1 && pwd -P)"

# Automatically find the nvidia CUDA runtime libs in the virtual environment
NVIDIA_DIR=$(find "$PROJECT_ROOT/python_env" -type d -path "*/nvidia/cu[0-9]*/lib" -print -quit)
if [[ -n "$NVIDIA_DIR" ]]; then
  export LD_LIBRARY_PATH="$NVIDIA_DIR:${LD_LIBRARY_PATH:-}"
fi

# Ignore conflicting local user-site packages
export PYTHONNOUSERSITE=1

# Execute the headless CLI using the virtualenv python interpreter
exec "$PROJECT_ROOT/python_env/bin/python" "$SCRIPT_DIR/headless_cli.py" "$@"
