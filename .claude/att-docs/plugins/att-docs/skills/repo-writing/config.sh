#!/usr/bin/env bash
# Reads the --config file the scripts beside this one take. Source it, then:
#
#   config_open <name> "$@"   takes --config <file> off the front of the
#                             arguments, and sets CONFIG_FILE (absolute),
#                             CONFIG_ROOT and CONFIG_ARGS (the arguments left)
#   config_read <key.path>[=default]...
#                             fills CONFIG_VALUES with one entry per key path:
#                             a string as it is, an array of strings joined
#                             with |, an array of {path, except} objects as
#                             one tab-separated line each, and a missing value
#                             as its default or ''
#
# A path in the config is relative to CONFIG_ROOT, the git toplevel of the
# config file's folder. config_open returns 64 when no config is given or the
# file does not exist, and 2 when it cannot be read.

config_open() {
  local name="$1" dir
  shift
  CONFIG_FILE='' CONFIG_ROOT='' CONFIG_ARGS=()
  if [ "${1:-}" = --config ] && [ "$#" -ge 2 ]; then
    CONFIG_FILE="$2"
    shift 2
  fi
  CONFIG_ARGS=("$@")
  if [ -z "$CONFIG_FILE" ]; then
    echo "$name: --config <file> is required" >&2
    return 64
  fi
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "$name: the config $CONFIG_FILE does not exist" >&2
    return 64
  fi
  dir="$(cd "$(dirname "$CONFIG_FILE")" && pwd)" || return 2
  CONFIG_FILE="$dir/$(basename "$CONFIG_FILE")"
  if ! CONFIG_ROOT="$(cd "$dir" && git rev-parse --show-toplevel 2>/dev/null)"; then
    echo "$name: the config $CONFIG_FILE is not inside a git work tree" >&2
    return 2
  fi
  if ! python3 "$CONFIG_READER" "$CONFIG_FILE" >/dev/null 2>&1; then
    echo "$name: the config $CONFIG_FILE is not a JSON object" >&2
    return 2
  fi
}

CONFIG_READER="$(dirname "${BASH_SOURCE[0]}")/config-read.py"

config_read() {
  local value
  CONFIG_VALUES=()
  while IFS= read -r -d '' value; do
    CONFIG_VALUES+=("$value")
  done < <(python3 "$CONFIG_READER" "$CONFIG_FILE" "$@")
}
