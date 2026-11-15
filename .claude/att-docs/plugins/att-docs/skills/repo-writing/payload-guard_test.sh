#!/usr/bin/env bash
# Tests payload-guard.sh, the PreToolUse hook that lets a write through the
# tunnel only when its payload carries a stamp: read ops and unrelated commands
# pass, unstamped, tampered, banned, stdin-fed and unparsable calls exit 2 with
# the reason, and a broken config exits 64.
# Run: bash plugins/att-docs/skills/repo-writing/payload-guard_test.sh
set -u
export PYTHONDONTWRITEBYTECODE=1
here="$(cd "$(dirname "$0")" && pwd)"
guard="$here/payload-guard.sh"
stamp="$here/stamp-payload.sh"
root_repo="$(cd "$here/../../../.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
mkdir -p "$HOME"

repo="$tmp/repo"
mkdir -p "$repo/lib" "$repo/bin"
git -C "$repo" init -q
cp "$root_repo/scripts/lib/hook-tool.sh" "$root_repo/scripts/lib/heredoc.py" "$repo/lib/"
printf 'ban\tall\tforbidden-everywhere\tnote\nban\ttracker\tsecret-tracker-word\tnote\n' >"$repo/terms.tsv"
cat >"$repo/read-ops.sh" <<'SH'
is_read_op() { case "$1" in list | show) return 0 ;; *) return 1 ;; esac; }
SH
printf '#!/bin/sh\necho lint-ran-ok\nexit 0\n' >"$repo/bin/lint-ok"
printf '#!/bin/sh\necho lint-found-problem\nexit 1\n' >"$repo/bin/lint-bad"
chmod +x "$repo/bin/lint-ok" "$repo/bin/lint-bad"

write_config() { # <file> <lintCommand>
  cat >"$1" <<JSON
{
  "terms": "terms.tsv",
  "trackerScope": "tracker",
  "payloadGuard": {
    "workSide": "the Work Tracker",
    "tunnel": "scripts/tunnel.sh",
    "workflowName": "tunnel",
    "stampCommand": "$stamp",
    "stampDir": ".stamps",
    "readOps": "read-ops.sh",
    "hookLib": "lib",
    "lintOp": "push",
    "lintCommand": "$2",
    "lintConfig": "lint.json"
  }
}
JSON
}
write_config "$repo/config.json" bin/lint-ok
write_config "$repo/config-badlint.json" bin/lint-bad
write_config "$repo/config-nolint.json" bin/missing
printf '{"tunnel":"scripts/tunnel.sh"}' >"$repo/config-partial.json"
printf '{"payloadGuard":{"workSide":"x"}}' >"$repo/config-short.json"

fail=0
check() {
  if [ "$2" = "$3" ]; then
    echo "ok   $1"
  else
    echo "FAIL $1: expected [$2] got [$3]"
    fail=1
  fi
}

# guard <config> <command>: sets status and err from the hook run.
guard() {
  local payload
  payload=$(jq -n --arg c "$2" --arg d "$repo" '{tool_name:"Bash",cwd:$d,tool_input:{command:$c}}')
  err=$(printf '%s' "$payload" | "$guard" --config "$repo/$1" 2>&1 >/dev/null)
  status=$?
}
expect_allow() { # <name> <command> [config]
  guard "${3:-config.json}" "$2"
  check "$1: exit 0" 0 "$status"
}
expect_block() { # <name> <command> <fact> [config]
  guard "${4:-config.json}" "$2"
  check "$1: exit 2" 2 "$status"
  check "$1: message carries [$3]" yes "$(grep -qF -- "$3" <<<"$err" && echo yes || echo no)"
}

stampit() { (cd "$repo" && "$stamp" --config config.json "$1" >/dev/null 2>&1); }

# --- pass-through -----------------------------------------------------------
expect_allow "unrelated command" "ls -la"
expect_allow "command that only names no tunnel word" "git status"
expect_allow "read op" "scripts/tunnel.sh list"
expect_allow "script named as a file" "cat scripts/tunnel.sh"
payload=$(jq -n '{tool_name:"Write",tool_input:{file_path:"a",content:"scripts/tunnel.sh push"}}')
printf '%s' "$payload" | "$guard" --config "$repo/config.json" >/dev/null 2>&1
check "non-shell tool: exit 0" 0 "$?"

# --- unstamped write --------------------------------------------------------
printf '{"title":"fix login"}\n' >"$repo/p.json"
sha=$(sha256sum "$repo/p.json" | cut -d' ' -f1)
expect_block "unstamped file payload" "scripts/tunnel.sh create --payload p.json" "has no repo-writing stamp"
check "unstamped message names the hash" yes "$(grep -qF "$sha" <<<"$err" && echo yes || echo no)"
check "unstamped message names the work side" yes "$(grep -qF 'the Work Tracker' <<<"$err" && echo yes || echo no)"
expect_block "write names no payload" "scripts/tunnel.sh create" "writes and names no payload"
expect_block "dispatch without op" "gh workflow run tunnel.yml -f payload=x" "op could not be read"

# --- stamped write ----------------------------------------------------------
stampit p.json
expect_allow "stamped file payload" "scripts/tunnel.sh create --payload p.json"
expect_allow "stamped payload through env and timeout" "env A=1 timeout 5 scripts/tunnel.sh create --payload p.json"
expect_allow "stamped payload through bash -c" "bash -c 'scripts/tunnel.sh create --payload p.json'"

# A changed payload no longer matches its stamp.
printf '{"title":"changed after stamp"}\n' >"$repo/p.json"
expect_block "payload edited after stamp" "scripts/tunnel.sh create --payload p.json" "has no repo-writing stamp"

# Inline JSON is stamped by the bytes of the argument.
stampit '{"title":"inline"}'
expect_allow "stamped inline payload" "scripts/tunnel.sh create --payload '{\"title\":\"inline\"}'"
expect_block "unstamped inline payload" "scripts/tunnel.sh create --payload '{\"title\":\"other\"}'" "has no repo-writing stamp"

# gh dispatch carries the op and payload in fields.
expect_allow "gh dispatch with read op" "gh workflow run tunnel.yml -f op=list"
expect_block "gh dispatch with unstamped payload" "gh workflow run tunnel.yml -f op=create -f 'payload={\"t\":1}'" "has no repo-writing stamp"
expect_block "gh dispatch reading stdin" "gh workflow run tunnel.yml --json" "takes its inputs from stdin or a file"

# --- terms ------------------------------------------------------------------
printf 'this has a secret-tracker-word\n' >"$repo/t.md"
stampedsha=$(sha256sum "$repo/t.md" | cut -d' ' -f1)
mkdir -p "$repo/.stamps"
echo forged >"$repo/.stamps/$stampedsha"
expect_block "stamped payload still carrying a tracker term" "scripts/tunnel.sh create --payload t.md" "banned term on line(s) 1"

# --- unreadable commands ----------------------------------------------------
expect_block "heredoc fed to a write op" "scripts/tunnel.sh create <<EOF
{\"a\":1}
EOF" "reads a heredoc"
expect_block "heredoc body holding the script" "cat <<EOF
scripts/tunnel.sh create --payload p.json
EOF" "heredoc carries a tunnel call"
expect_block "tunnel named in an unreadable position" "FOO=scripts/tunnel.sh bash -c 'x' ; xargs scripts/tunnel.sh" "no tunnel call can be read"
expect_block "unbalanced quote" "scripts/tunnel.sh create --payload 'p.json" "could not parse"

# --- lint on a tree send ----------------------------------------------------
printf '{"title":"push me"}\n' >"$repo/q.json"
stampit q.json
expect_allow "push passing the lint" "scripts/tunnel.sh push --payload q.json"
expect_block "push failing the lint" "scripts/tunnel.sh push --payload q.json" "lint-found-problem" config-badlint.json
expect_block "push with the lint missing" "scripts/tunnel.sh push --payload q.json" "needs missing installed" config-nolint.json

# --- config -----------------------------------------------------------------
printf '{}' | "$guard" >/dev/null 2>&1
check "no --config: exit 64" 64 "$?"
printf '{}' | "$guard" --config "$repo/nope.json" >/dev/null 2>&1
check "missing config file: exit 64" 64 "$?"
printf '{}' | "$guard" --config "$repo/config-partial.json" >/dev/null 2>"$tmp/e"
check "config without tunnel keys: exit 64" 64 "$?"
check "config without tunnel keys: says what it needs" yes "$(grep -q 'needs payloadGuard tunnel' "$tmp/e" && echo yes || echo no)"

[ "$fail" = 0 ] && echo "all passed"
exit "$fail"
