#!/usr/bin/env bash
# Runs drift.sh with a fake gh that "clones" a scratch Code Conductor repository, so no
# network is used and the real bridge-tools.json is left as it is. Every case checks that
# the script exits 0 and prints what the case needs.
# usage: bash scripts/bridge-tools/drift_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
mkdir -p "$HOME" "$SANDBOX/tool" "$SANDBOX/bin" "$SANDBOX/tmp"
# Every scratch folder the scripts make lands here, so the end of the run can check that
# none is left.
export TMPDIR="$SANDBOX/tmp"
# A run inside GitHub Actions sets GITHUB_ACTIONS, and drift.sh prints annotations when it
# does. A user of gh often exports a token, and the scratch tools module refuses to load
# when one reaches it. Each case that needs one of them sets it itself.
unset GITHUB_ACTIONS GH_TOKEN GITHUB_TOKEN
cp "$HERE/drift.sh" "$HERE/drift.py" "$HERE/refresh.sh" "$SANDBOX/tool/"
SCRIPT="$SANDBOX/tool/drift.sh"
COMMITTED="$SANDBOX/committed.json"
GH_LOG="$SANDBOX/gh-args.log"

CC="$SANDBOX/cc"
mkdir -p "$CC/baton"
git -C "$CC" init -q -b main
# The tools module throws when the token reaches the rebuild.
write_tools() {
  cat >"$CC/baton/voice-bridge-tools.mjs" <<JS
if (process.env.GH_TOKEN || process.env.GITHUB_TOKEN) throw new Error('token reached the rebuild');
export const TOOLS = [
$1
];
JS
}
BASE="  { name: 'send', inputSchema: { properties: { text: {}, session: {} } } },
  { name: 'read_issue', inputSchema: { properties: { repo: {}, number: {} } } },
  { name: 'summary' },"
write_tools "$BASE"
git -C "$CC" add -A
git -C "$CC" commit -q -m one

# gh repo clone <repo> <dir> -- --depth 1 copies the scratch repository, unless FAKE_GH=fail.
cat >"$SANDBOX/bin/gh" <<'SH'
#!/usr/bin/env bash
echo "$*" >>"$GH_LOG"
if [ "${FAKE_GH:-ok}" = fail ]; then
  echo "authentication failed for token $GH_TOKEN" >&2
  exit 1
fi
[ "$1 $2" = "repo clone" ] || exit 64
git clone -q --depth 1 "file://$CC" "$4"
SH
chmod +x "$SANDBOX/bin/gh"
export PATH="$SANDBOX/bin:$PATH" CC GH_LOG

fails=0
check() { # name expected actual
  if [ "$2" != "$3" ]; then
    echo "FAIL $1: expected [$2] got [$3]" >&2
    fails=$((fails + 1))
  fi
}
has() { # name text output
  case "$3" in
    *"$2"*) ;;
    *) echo "FAIL $1: [$2] not in output:" >&2; echo "$3" >&2; fails=$((fails + 1)) ;;
  esac
}
lacks() { # name text output
  case "$3" in
    *"$2"*) echo "FAIL $1: [$2] is in output:" >&2; echo "$3" >&2; fails=$((fails + 1)) ;;
  esac
}
run() { # prints the output; the exit status is left in $status
  out="$(BRIDGE_TOOLS_JSON="$COMMITTED" "$@" bash "$SCRIPT" 2>&1)"
  status=$?
}

bash "$HERE/refresh.sh" "$CC" HEAD "$COMMITTED" >/dev/null 2>&1
check "the committed snapshot is built" 0 $?

# No token: a notice, and gh is never called.
run env -u GH_TOKEN
check "no token exits 0" 0 $status
has "no token notice" "Notice: the Baton tool snapshot was not compared" "$out"
check "no token never calls gh" "no" "$([ -e "$GH_LOG" ] && echo yes || echo no)"

# The same tools: no warning, and the clone is the Code-Conductor main branch at depth 1.
run env GH_TOKEN=ghs_SECRET
check "no drift exits 0" 0 $status
has "no drift says so" "matches merph518/Code-Conductor main" "$out"
lacks "no drift has no warning" "Warning" "$out"
gh_args="$(cat "$GH_LOG")"
has "the clone is of Code-Conductor" "repo clone merph518/Code-Conductor " "$gh_args"
has "the clone is shallow" " -- --depth 1" "$gh_args"
has "the clone reads main" " --branch main" "$gh_args"

# A different commit with the same tools in another order is not drift.
write_tools "  { name: 'summary' },
  { name: 'read_issue', inputSchema: { properties: { number: {}, repo: {} } } },
  { name: 'send', inputSchema: { properties: { session: {}, text: {} } } },"
git -C "$CC" commit -q -am two
run env GH_TOKEN=ghs_SECRET
check "a reordered list exits 0" 0 $status
lacks "a reordered list has no warning" "Warning" "$out"

# An added tool, a removed tool, an added argument and a removed argument.
write_tools "  { name: 'send', inputSchema: { properties: { text: {}, anyway: {} } } },
  { name: 'summary' },
  { name: 'follow', inputSchema: { properties: { session: {} } } },
  { name: 'odd%name' },"
git -C "$CC" commit -q -am three
run env GH_TOKEN=ghs_SECRET
check "drift exits 0" 0 $status
has "drift warns" "Warning: bridge-tools.json differs from merph518/Code-Conductor main" "$out"
has "an added tool is named" "tool follow: added" "$out"
has "a removed tool is named" "tool read_issue: removed" "$out"
has "an added argument is named" "tool send: argument anyway added" "$out"
has "a removed argument is named" "tool send: argument session removed" "$out"
lacks "drift prints no annotation outside Actions" "::warning" "$out"

run env GH_TOKEN=ghs_SECRET GITHUB_ACTIONS=true
check "drift in Actions exits 0" 0 $status
has "drift in Actions is an annotation" \
  "::warning title=Baton tool snapshot is behind Code Conductor::" "$out"
has "the annotation joins lines with %0A and escapes a percent sign" \
  "tool follow: added%0Atool odd%25name: added%0Atool read_issue: removed" "$out"

# A clone that fails: a notice with the token blanked out.
run env GH_TOKEN=ghs_SECRET FAKE_GH=fail
check "a failed clone exits 0" 0 $status
has "a failed clone says what failed" "merph518/Code-Conductor main could not be fetched" "$out"
has "a failed clone shows gh's message" "authentication failed" "$out"
lacks "a failed clone hides the token" "ghs_SECRET" "$out"

# A rebuild that fails: Code Conductor main with no Baton folder.
git -C "$CC" rm -q -r baton
git -C "$CC" commit -q -m four
run env GH_TOKEN=ghs_SECRET
check "a failed rebuild exits 0" 0 $status
has "a failed rebuild says what failed" \
  "could not be rebuilt from merph518/Code-Conductor main" "$out"
has "a failed rebuild shows the reason" "has no baton/voice-bridge-tools.mjs" "$out"
lacks "a failed rebuild has no warning" "Warning" "$out"
git -C "$CC" reset -q --hard HEAD~1

# A committed snapshot that cannot be read.
echo '{ not json' >"$COMMITTED"
run env GH_TOKEN=ghs_SECRET
check "an unreadable snapshot exits 0" 0 $status
has "an unreadable snapshot notice" "the snapshots could not be read" "$out"
rm "$COMMITTED"
run env GH_TOKEN=ghs_SECRET
check "a missing snapshot exits 0" 0 $status
has "a missing snapshot notice" "the snapshots could not be read" "$out"

# Every scratch folder is removed.
check "no scratch folder is left" "" "$(ls -A "$TMPDIR")"

if [ "$fails" -eq 0 ]; then
  echo "all passed"
else
  echo "$fails failed" >&2
  exit 1
fi
