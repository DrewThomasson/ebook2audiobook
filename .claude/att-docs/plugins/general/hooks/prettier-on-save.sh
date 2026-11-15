#!/usr/bin/env bash
# usage: prettier-on-save.sh --config <extension.json> < <PostToolUse payload>
# PostToolUse hook on Edit|Write. Formats the file that was just edited, when it matches
# one of the configured globs and the repository has a Prettier config. A failure of the
# formatter never blocks the edit.
#
# Reads the `prettierOnSave` section of the extension file; every key is optional:
#   globs        bash patterns for the files to format, matched against the path relative
#                to the repository root, where * also matches a slash (default
#                ["*.ts", "*.tsx"])
#   command      the formatter as a list of words; the file's path is added last
#                (default ["npx", "prettier", "--write"])
#   configFiles  the file names that count as a Prettier config, looked for in the edited
#                file's folder and each folder above it up to the repository root
#                (default: the names Prettier itself reads). A package.json with a
#                "prettier" key also counts
set -uo pipefail

[[ ${1:-} == --config && -f ${2:-} ]] || { echo "usage: $0 --config <extension.json>" >&2; exit 64; }
config=$2

file=$(jq -r '.tool_input.file_path // ""' || true)
[[ -n $file ]] || exit 0

mapfile -t globs < <(jq -r '.prettierOnSave.globs // ["*.ts", "*.tsx"] | .[]' "$config")
mapfile -t command < <(jq -r '.prettierOnSave.command // ["npx", "prettier", "--write"] | .[]' "$config")
mapfile -t config_files < <(jq -r '.prettierOnSave.configFiles // [
  ".prettierrc", ".prettierrc.json", ".prettierrc.yml", ".prettierrc.yaml",
  ".prettierrc.json5", ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.mjs",
  ".prettierrc.ts", ".prettierrc.cts", ".prettierrc.mts", ".prettierrc.toml",
  "prettier.config.js", "prettier.config.cjs", "prettier.config.mjs",
  "prettier.config.ts", "prettier.config.cts", "prettier.config.mts"] | .[]' "$config")
[[ ${#command[@]} -gt 0 ]] || exit 0

# Only an existing file under the repository the hook runs in.
root=$(pwd -P)
[[ $file == /* ]] || file=$root/$file
file=$(readlink -m "$file")
[[ $file == "$root"/* && -f $file ]] || exit 0
rel=${file#"$root"/}

matched=
for glob in "${globs[@]}"; do
  # shellcheck disable=SC2053
  if [[ $rel == $glob ]]; then matched=1; break; fi
done
[[ -n $matched ]] || exit 0

has_config() {
  local dir=$1 name
  for name in "${config_files[@]}"; do
    [[ -f $dir/$name ]] && return 0
  done
  [[ -f $dir/package.json ]] && jq -e 'has("prettier")' "$dir/package.json" >/dev/null 2>&1
}
dir=$(dirname "$file")
while :; do
  has_config "$dir" && break
  [[ $dir == "$root" || $dir == / ]] && exit 0
  dir=$(dirname "$dir")
done

"${command[@]}" "$file" >/dev/null 2>&1 || true
exit 0
