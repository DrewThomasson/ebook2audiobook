#!/usr/bin/env bash
# Runs refresh.sh against a scratch repository whose baton/voice-bridge-tools.mjs exports a
# small TOOLS, so no real Code Conductor checkout is read and the real bridge-tools.json is
# left as it is.
# usage: bash scripts/bridge-tools/refresh_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
mkdir -p "$HOME" "$SANDBOX/tool"
cp "$HERE/refresh.sh" "$SANDBOX/tool/"
SCRIPT="$SANDBOX/tool/refresh.sh"
OUT="$SANDBOX/tool/bridge-tools.json"

CC="$SANDBOX/cc"
mkdir -p "$CC/baton"
git -C "$CC" init -q -b main
# A tool with no inputSchema, one whose arguments are not in sorted order, and tools out of
# alphabetical order; a sibling module the tools module imports.
cat >"$CC/baton/helper.mjs" <<'JS'
export const repoArg = { type: 'string' };
JS
cat >"$CC/baton/voice-bridge-tools.mjs" <<'JS'
import { repoArg } from './helper.mjs';
export const TOOLS = [
  { name: 'send', inputSchema: { type: 'object', properties: { text: {}, session: {} } } },
  { name: 'needs_attention', inputSchema: { type: 'object', properties: {} } },
  { name: 'read_issue', inputSchema: { type: 'object', properties: { repo: repoArg, number: {} } } },
  { name: 'bare' },
];
JS
git -C "$CC" add -A
git -C "$CC" commit -q -m one
SHA="$(git -C "$CC" rev-parse HEAD)"

fails=0
check() { # name expected actual
  if [ "$2" != "$3" ]; then
    echo "FAIL $1: expected [$2] got [$3]" >&2
    fails=$((fails + 1))
  fi
}
field() { node -e 'const d = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")); console.log(JSON.stringify(eval(process.argv[2])))' "$OUT" "$1"; }

bash "$SCRIPT" "$CC" HEAD >/dev/null 2>&1
check "exit status of a good refresh" 0 $?
check "source is the commit" "\"$SHA\"" "$(field d.source)"
check "tools are sorted by name" '["bare","needs_attention","read_issue","send"]' "$(field 'Object.keys(d.tools)')"
check "arguments are sorted" '["number","repo"]' "$(field 'd.tools.read_issue')"
check "a tool with no schema has no arguments" '[]' "$(field 'd.tools.bare')"
check "an empty schema has no arguments" '[]' "$(field 'd.tools.needs_attention')"

# A third argument names the file to write, and the file beside the script is left alone.
before="$(cat "$OUT")"
echo "export const TOOLS = [{ name: 'only' }];" >"$CC/baton/voice-bridge-tools.mjs"
git -C "$CC" commit -q -am elsewhere
bash "$SCRIPT" "$CC" HEAD "$SANDBOX/elsewhere.json" >/dev/null 2>&1
check "a refresh to another file exits 0" 0 $?
check "the other file is written" '["only"]' "$(node -e 'console.log(JSON.stringify(Object.keys(JSON.parse(require("fs").readFileSync(process.argv[1], "utf8")).tools)))' "$SANDBOX/elsewhere.json")"
check "the file beside the script is untouched" "$before" "$(cat "$OUT")"
git -C "$CC" reset -q --hard HEAD~1

# The ref decides what is read, not the working tree.
echo "export const TOOLS = [];" >"$CC/baton/voice-bridge-tools.mjs"
bash "$SCRIPT" "$CC" HEAD >/dev/null 2>&1
check "the working tree is not read" '["bare","needs_attention","read_issue","send"]' "$(field 'Object.keys(d.tools)')"
git -C "$CC" commit -q -am two
SECOND="$(git -C "$CC" rev-parse HEAD)"
bash "$SCRIPT" "$CC" HEAD >/dev/null 2>&1
check "a new commit is read" '[]' "$(field 'Object.keys(d.tools)')"
check "its source changes" "\"$SECOND\"" "$(field d.source)"

# A failure leaves the file as the last good run wrote it.
before="$(cat "$OUT")"
bash "$SCRIPT" "$CC" no-such-ref >/dev/null 2>&1
check "an unknown ref fails" 1 $?
bash "$SCRIPT" "$SANDBOX/not-a-repo" >/dev/null 2>&1
check "a folder that is not a repository fails" 1 $?
check "a failed refresh keeps the file" "$before" "$(cat "$OUT")"

git -C "$CC" rm -q -r baton
git -C "$CC" commit -q -m three
bash "$SCRIPT" "$CC" HEAD >/dev/null 2>&1
check "a commit with no baton folder fails" 1 $?
check "and keeps the file" "$before" "$(cat "$OUT")"

if [ "$fails" -eq 0 ]; then
  echo "all passed"
else
  echo "$fails failed" >&2
  exit 1
fi
