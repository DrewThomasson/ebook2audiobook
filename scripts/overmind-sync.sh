#!/usr/bin/env bash
# Vendor a tagged Overmind snapshot into .claude/att-docs and move the pin.
# usage: scripts/overmind-sync.sh [<tag>]
# Settings live in .claude/att-docs.lock; set any override here, for example:
#   export ATT_DOCS_PATHS="plugins/general plugins/voice/skills"
set -euo pipefail
exec "$(git rev-parse --show-toplevel)/.claude/att-docs/scripts/consumer/overmind-sync.sh" "$@"
