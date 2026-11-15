#!/usr/bin/env bash
# usage: bash run_test.sh
# Tests run.sh against a stand-in skill folder, so no real hook script runs.
set -u
here=$(dirname "$(readlink -f "$0")")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
fail=0
export HOME=$work/nohome
mkdir -p "$HOME"
# A running Baton's voice-bridge/plugin would hand every call to the real runner.
export XDG_RUNTIME_DIR=$work/runtime
unset VOICE_HOOKS_LIVE

mkdir -p "$work/plugin/hooks" "$work/plugin/skills/voice-bridge-hooks"
cp "$here/run.sh" "$work/plugin/hooks/run.sh"
printf '{}\n' >"$work/plugin/skills/voice-bridge-hooks/defaults.json"
printf '%s\n' 'import sys; print("py", *sys.argv[1:], sys.stdin.read().strip())' \
  >"$work/plugin/skills/voice-bridge-hooks/probe.py"
printf '%s\n' 'echo "sh $* $(cat)"' >"$work/plugin/skills/voice-bridge-hooks/probe.sh"
run="$work/plugin/hooks/run.sh"
defaults="$work/plugin/skills/voice-bridge-hooks/defaults.json"

# usage: check <name> <expected> <actual>
check() {
  if [[ $2 != "$3" ]]; then
    echo "FAIL $1: expected [$2] got [$3]" >&2
    fail=1
  fi
}

mkdir -p "$work/bare"
check "defaults when the project has no extension" "py --config $defaults attention payload" \
  "$(CLAUDE_PROJECT_DIR=$work/bare "$run" probe.py attention <<<payload)"

mkdir -p "$work/own/.claude/skills/voice-bridge-hooks"
printf '{}\n' >"$work/own/.claude/skills/voice-bridge-hooks/extension.json"
check "the project's extension wins" \
  "sh --config $work/own/.claude/skills/voice-bridge-hooks/extension.json x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/own "$run" probe.sh x <<<payload)"

mkdir -p "$work/hooked/.claude"
printf '%s\n' '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"x/voice_bridge_reply.py"}]}]}}' \
  >"$work/hooked/.claude/settings.json"
out=$(CLAUDE_PROJECT_DIR=$work/hooked "$run" probe.py attention <<<payload)
check "steps aside when the project registers the hooks" "" "$out"
CLAUDE_PROJECT_DIR=$work/hooked "$run" probe.py attention <<<payload
check "the step-aside exit code" 0 $?

mkdir -p "$work/local/.claude"
printf '%s\n' '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"x/speak-attention.sh"}]}]}}' \
  >"$work/local/.claude/settings.local.json"
check "steps aside for local settings too" "" \
  "$(CLAUDE_PROJECT_DIR=$work/local "$run" probe.py attention <<<payload)"

mkdir -p "$work/allowed/.claude"
printf '%s\n' '{"permissions":{"allow":["Bash(scripts/speak-attention_test.sh)"]}}' \
  >"$work/allowed/.claude/settings.json"
check "a permission naming a script is not a hook" "py --config $defaults x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/allowed "$run" probe.py x <<<payload)"

mkdir -p "$work/titled/.claude"
printf '%s\n' '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"x/session_title.py hook stop"}]}]}}' \
  >"$work/titled/.claude/settings.json"
check "steps aside when the project registers the title hook" "" \
  "$(CLAUDE_PROJECT_DIR=$work/titled "$run" probe.py x <<<payload)"
CLAUDE_PROJECT_DIR=$work/titled "$run" probe.py x </dev/null
check "and exits 0" 0 $?

mkdir -p "$work/titleperm/.claude"
printf '%s\n' '{"permissions":{"allow":["Bash(python3 x/session_title.py show)"]}}' \
  >"$work/titleperm/.claude/settings.json"
check "a permission naming the title script is not a hook" "py --config $defaults x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/titleperm "$run" probe.py x <<<payload)"

# Every hook the plugin registers names a script that sits in the skill folder.
for entry in "session_title.py hook prompt" "session_title.py hook stop"; do
  found=$(jq -r --arg e "$entry" '[.hooks[][].hooks[].command | select(contains($e))] | length' \
    "$here/hooks.json")
  check "hooks.json registers $entry once" 1 "$found"
done
scanned=$(jq -r '.hooks[][].hooks[].command | scan("run\\.sh\\\\?\"? ([A-Za-z0-9_.-]+)") | .[0]' \
  "$here/hooks.json")
check "the scan names a script for every hook that runs one" \
  "$(jq '[.hooks[][].hooks[].command | select(contains("run.sh"))] | length' "$here/hooks.json")" \
  "$(printf '%s\n' "$scanned" | grep -c .)"
for script in $(printf '%s\n' "$scanned" | sort -u); do
  [[ -f $here/../skills/voice-bridge-hooks/$script ]] ||
    { echo "FAIL hooks.json names $script, which is not in the skill folder" >&2; fail=1; }
done

mkdir -p "$work/home/.claude"
printf '%s\n' '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"x/speak-attention.sh"}]}]}}' \
  >"$work/home/.claude/settings.json"
check "steps aside for user-scope settings" "" \
  "$(HOME=$work/home CLAUDE_PROJECT_DIR=$work/bare "$run" probe.py x <<<payload)"

printf '%s\n' 'import sys; sys.exit(3)' >"$work/plugin/skills/voice-bridge-hooks/fail.py"
CLAUDE_PROJECT_DIR=$work/bare "$run" fail.py </dev/null
check "the script's exit code passes through" 3 $?

# Baton's plugin folder: a second copy whose probe says which copy ran.
mkdir -p "$work/live/hooks" "$work/live/skills/voice-bridge-hooks" "$XDG_RUNTIME_DIR/voice-bridge"
cp "$here/run.sh" "$work/live/hooks/run.sh"
printf '{}\n' >"$work/live/skills/voice-bridge-hooks/defaults.json"
printf '%s\n' 'import sys; print("live", *sys.argv[1:], sys.stdin.read().strip())' \
  >"$work/live/skills/voice-bridge-hooks/probe.py"
live_defaults="$work/live/skills/voice-bridge-hooks/defaults.json"
pointer=$XDG_RUNTIME_DIR/voice-bridge/plugin
printf '%s\n' "$work/live" >"$pointer"
check "Baton's plugin folder runs the hook" "live --config $live_defaults x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/bare "$run" probe.py x <<<payload)"
check "Baton's runner runs its own copy" "live --config $live_defaults x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/bare "$work/live/hooks/run.sh" probe.py x <<<payload)"
check "Baton's runner still steps aside" "" \
  "$(CLAUDE_PROJECT_DIR=$work/hooked "$run" probe.py x <<<payload)"

printf '%s\n' "$work/plugin" >"$pointer"
check "a folder naming this copy runs it" "py --config $defaults x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/bare "$run" probe.py x <<<payload)"

printf '%s\n' "$work/gone" >"$pointer"
check "a folder that is gone leaves the installed copy" "py --config $defaults x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/bare "$run" probe.py x <<<payload)"

mkdir -p "$work/norunner/skills/voice-bridge-hooks"
printf '%s\n' "$work/norunner" >"$pointer"
check "a folder with no runner leaves the installed copy" "py --config $defaults x payload" \
  "$(CLAUDE_PROJECT_DIR=$work/bare "$run" probe.py x <<<payload)"
rm -f "$pointer"

exit $fail
