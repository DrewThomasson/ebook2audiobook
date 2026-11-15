#!/usr/bin/env bash
# Tests stamp-payload.sh: a payload that passes the text scan and the tracker
# terms is stamped under the SHA-256 of its bytes, and one that fails either is
# refused without a stamp.
# Run: bash plugins/att-docs/skills/repo-writing/stamp-payload_test.sh
set -u
export PYTHONDONTWRITEBYTECODE=1
here="$(cd "$(dirname "$0")" && pwd)"
script="$here/stamp-payload.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
mkdir -p "$HOME"

repo="$tmp/repo"
mkdir -p "$repo"
git -C "$repo" init -q
printf 'ban\tall\tforbidden-everywhere\tnote\nban\ttracker\tsecret-tracker-word\tnote\n' >"$repo/terms.tsv"
cat >"$repo/config.json" <<'JSON'
{
  "terms": "terms.tsv",
  "trackerScope": "tracker",
  "payloadGuard": { "workSide": "the Work Tracker", "stampDir": ".stamps", "stampDirEnv": "STAMP_TEST_DIR" }
}
JSON

fail=0
check() {
  if [ "$2" = "$3" ]; then
    echo "ok   $1"
  else
    echo "FAIL $1: expected [$2] got [$3]"
    fail=1
  fi
}

run() { (cd "$repo" && "$script" --config config.json "$@" 2>"$tmp/err"); }

# A clean payload file is stamped under the hash of the file.
printf '{"title":"fix the login page"}\n' >"$repo/ok.json"
sha=$(sha256sum "$repo/ok.json" | cut -d' ' -f1)
out=$(run ok.json | tail -n 1)
check "file: exit 0 and prints the stamp" "stamped $sha" "$out"
check "file: stamp exists" yes "$([ -f "$repo/.stamps/$sha" ] && echo yes || echo no)"
check "file: stamp records the payload argument" ok.json "$(cut -d' ' -f2- "$repo/.stamps/$sha")"

# An inline payload is hashed without a trailing newline.
inline='{"title":"hello"}'
sha=$(printf '%s' "$inline" | sha256sum | cut -d' ' -f1)
out=$(run "$inline" | tail -n 1)
check "inline: prints the stamp" "stamped $sha" "$out"
check "inline: stamp holds the JSON" "$inline" "$(cut -d' ' -f2- "$repo/.stamps/$sha")"

# The stamp folder can be redirected through the named environment variable.
printf '{"title":"redirected"}\n' >"$repo/env.json"
sha=$(sha256sum "$repo/env.json" | cut -d' ' -f1)
(cd "$repo" && STAMP_TEST_DIR="$tmp/elsewhere" "$script" --config config.json env.json >/dev/null 2>&1)
check "env: stamp lands in the named folder" yes "$([ -f "$tmp/elsewhere/$sha" ] && echo yes || echo no)"
check "env: no stamp in the default folder" no "$([ -f "$repo/.stamps/$sha" ] && echo yes || echo no)"

# A term scoped to the tracker refuses the payload and names the line.
printf 'line one\nthis has a secret-tracker-word in it\n' >"$repo/bad.md"
sha=$(sha256sum "$repo/bad.md" | cut -d' ' -f1)
run bad.md >"$tmp/out"
status=$?
check "tracker term: exit 1" 1 "$status"
check "tracker term: names the line" yes "$(grep -q 'line(s) 2 carry a term scoped to the Work Tracker' "$tmp/err" && echo yes || echo no)"
check "tracker term: no stamp" no "$([ -f "$repo/.stamps/$sha" ] && echo yes || echo no)"

# A term that only the shared scan flags refuses the payload too.
printf 'the behaviour is odd\n' >"$repo/scan.md"
sha=$(sha256sum "$repo/scan.md" | cut -d' ' -f1)
run scan.md >"$tmp/out"
status=$?
check "scan term: exit 1" 1 "$status"
check "scan term: no stamp" no "$([ -f "$repo/.stamps/$sha" ] && echo yes || echo no)"

# No argument, and no config, both fail.
(cd "$repo" && "$script" --config config.json >/dev/null 2>"$tmp/err")
check "no payload: non-zero exit" yes "$([ $? -ne 0 ] && echo yes || echo no)"
(cd "$repo" && "$script" ok.json >/dev/null 2>"$tmp/err")
check "no config: exit 64" 64 "$?"

[ "$fail" = 0 ] && echo "all passed"
exit "$fail"
