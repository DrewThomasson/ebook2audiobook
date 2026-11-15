#!/usr/bin/env bash
# Fail when the vendored Overmind copy differs from the tree the lock pins. A pull request
# cannot weaken the check by editing the vendored script: the script from the base commit
# runs when the base has one. With no base at all, the vendored script runs.
# usage: scripts/overmind-check.sh
set -euo pipefail
S=.claude/att-docs/scripts/consumer/overmind-check.sh
BASE="${ATT_DOCS_BASE:-$(git merge-base HEAD origin/main 2>/dev/null || true)}"
if [ -n "${ATT_DOCS_BASE:-}" ] && ! git cat-file -e "$BASE^{commit}" 2> /dev/null; then
  echo "att-docs: ATT_DOCS_BASE '$BASE' is not a commit in this repository"
  exit 1
fi
if [ -n "$BASE" ] && git cat-file -e "$BASE:$S" 2> /dev/null; then
  git show "$BASE:$S" | bash -s -- "$@"
else
  exec "$(git rev-parse --show-toplevel)/$S" "$@"
fi
