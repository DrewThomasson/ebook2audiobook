#!/usr/bin/env bash
# Convert a JSON lock file to the key=value lock the sync and check scripts use.
# One-time, and safe to repeat: a lock that is already key=value is left alone.
#
# usage: overmind-lock-convert.sh [<lock file> [<output file>]]
#
# The lock file defaults to $ATT_DOCS_LOCK, then .claude/att-docs.lock. The result
# replaces the input unless an output file is named; "-" writes to standard output.
# String fields repo, url, prefix, tag, commit, tree, copy_tree are copied, and a
# paths string or array becomes a space-separated paths= line. The commit and tree
# values must be 40 hex digits. Needs only grep and sed.
set -euo pipefail

# Relative names resolve from the repository root, as the sync and check scripts do.
if root="$(git rev-parse --show-toplevel 2> /dev/null)"; then cd "$root"; fi
IN="${1:-${ATT_DOCS_LOCK:-.claude/att-docs.lock}}"
OUT="${2:-$IN}"

if [ ! -f "$IN" ]; then
  echo "no lock file: $IN" >&2
  exit 1
fi
if ! grep -q '^[[:space:]]*{' "$IN"; then
  echo "$IN is not JSON; nothing to convert" >&2
  exit 0
fi

# The file on one line with nested objects removed, so only top-level keys match.
FLAT="$(tr -d '\r' < "$IN" | tr '\n' ' ' | sed 's/^[[:space:]]*{//; s/{[^{}]*}//g')"

# usage: json_string <key>; prints the first top-level string value of the key.
json_string() {
  { printf '%s\n' "$FLAT" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" || true; } |
    head -n 1 | sed 's/^[^:]*:[[:space:]]*"\(.*\)"$/\1/'
}

# usage: json_paths; prints the paths value, string or array, space separated.
json_paths() {
  local array
  array="$(printf '%s\n' "$FLAT" | { grep -o '"paths"[[:space:]]*:[[:space:]]*\[[^]]*\]' || true; })"
  if [ -n "$array" ]; then
    printf '%s\n' "$array" | sed 's/^[^[]*\[//; s/\]$//' | { grep -o '"[^"]*"' || true; } |
      tr -d '"' | tr '\n' ' ' | sed 's/ $//'
    echo
  else
    json_string paths
  fi
}

repo="$(json_string repo)"
tag="$(json_string tag)"
commit="$(json_string commit)"
tree="$(json_string tree)"
for pair in "repo:$repo" "tag:$tag" "commit:$commit" "tree:$tree"; do
  if [ -z "${pair#*:}" ]; then
    echo "$IN has no ${pair%%:*} value" >&2
    exit 1
  fi
done
copy_tree="$(json_string copy_tree)"
for pair in "commit:$commit" "tree:$tree" ${copy_tree:+"copy_tree:$copy_tree"}; do
  if ! printf '%s' "${pair#*:}" | grep -Eq '^[0-9a-f]{40}$'; then
    echo "$IN: ${pair%%:*} is not a 40-digit hex SHA" >&2
    exit 1
  fi
done

url="$(json_string url)"
prefix="$(json_string prefix)"
paths="$(json_paths)"

result="$(
  printf 'repo=%s\n' "$repo"
  if [ -n "$url" ]; then printf 'url=%s\n' "$url"; fi
  if [ -n "$prefix" ]; then printf 'prefix=%s\n' "$prefix"; fi
  printf 'tag=%s\ncommit=%s\ntree=%s\n' "$tag" "$commit" "$tree"
  if [ -n "$paths" ]; then printf 'paths=%s\n' "$paths"; fi
  if [ -n "$copy_tree" ]; then printf 'copy_tree=%s\n' "$copy_tree"; fi
)"

if [ "$OUT" = "-" ]; then
  printf '%s\n' "$result"
else
  printf '%s\n' "$result" > "$OUT"
  echo "wrote $OUT"
fi
