#!/usr/bin/env bash
# Runs tools/translate_ebook.py with e2a's python_env, every argument forwarded (--help lists the options).
# Paths are taken from the folder it is started from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" >/dev/null 2>&1 && pwd -P)"
PY_CMD="$SCRIPT_DIR/python_env/bin/python"
if [[ ! -x "$PY_CMD" ]]; then
	echo "$SCRIPT_DIR/python_env not found: run ./ebook2audiobook.sh once to install ebook2audiobook." >&2
	exit 1
fi
exec "$PY_CMD" "$SCRIPT_DIR/tools/translate_ebook.py" "$@"
