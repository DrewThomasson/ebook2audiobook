#!/usr/bin/env bash
# Stamps a payload as checked for the work tracker: it has to pass the
# repository text scan and the terms scoped to the tracker. The payload guard
# looks the stamp up by the SHA-256 of the payload, so the payload is sent
# exactly as stamped.
# Usage: stamp-payload.sh --config <file> <payload file | inline JSON>
# Run the prose pass of SKILL.md on the text first; this checks the terms.
#
# Reads from the config, beside what check-repo-text.sh reads:
#   payloadGuard.workSide     the tracker's name, as the messages print it
#   payloadGuard.stampDir     where stamps go, relative to the top of the git
#                             work tree this runs in, since the guard reads
#                             them from the tree the command runs in
#   payloadGuard.stampDirEnv  an environment variable that, when set, names
#                             the stamp folder instead

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=config.sh
. "$HERE/config.sh"
config_open stamp-payload "$@" || exit
set -- "${CONFIG_ARGS[@]}"
config=$CONFIG_FILE
config_read payloadGuard.workSide payloadGuard.stampDir payloadGuard.stampDirEnv
[ "${#CONFIG_VALUES[@]}" -eq 3 ] || { echo "stamp-payload: the config does not read" >&2; exit 2; }
work_side="${CONFIG_VALUES[0]}"
stamp_dir="${CONFIG_VALUES[1]}"
stamp_env="${CONFIG_VALUES[2]}"
arg="${1:?usage: stamp-payload.sh --config <file> <payload file | inline JSON>}"
root=$(git rev-parse --show-toplevel) || exit 1
stamps="$root/$stamp_dir"
[ -n "$stamp_env" ] && [ -n "${!stamp_env:-}" ] && stamps="${!stamp_env}"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
if [ -f "$arg" ]; then
  sha=$(sha256sum "$arg" | cut -d' ' -f1)
  cp "$arg" "$work/payload.md"
else
  sha=$(printf '%s' "$arg" | sha256sum | cut -d' ' -f1)
  printf '%s\n' "$arg" >"$work/payload.md"
fi

"$HERE/check-repo-text.sh" --config "$config" "$work/payload.md" || exit 1
# shellcheck source=terms.sh
. "$HERE/terms.sh"
terms_use_config "$config" || exit 2
read_terms || exit 2
select_terms all "$TERMS_TRACKER"
hits=$(cut_kept <"$work/payload.md" | terms_hit_lines)
if [ -n "$hits" ]; then
  echo "payload line(s) $hits carry a term scoped to $work_side:" >&2
  for line in $hits; do sed -n "${line}p" "$work/payload.md" >&2; done
  exit 1
fi

mkdir -p "$stamps"
printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$arg" >"$stamps/$sha"
echo "stamped $sha"
