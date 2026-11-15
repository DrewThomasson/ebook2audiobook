#!/usr/bin/env bash
# usage: bash run_test.sh
# Tests run.sh against stand-in scripts, so no real hook script runs.
set -u
here=$(dirname "$(readlink -f "$0")")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
fail=0

mkdir -p "$work/plugin/hooks"
cp "$here/run.sh" "$work/plugin/hooks/run.sh"
printf '%s\n' 'import os, sys; print("py", *sys.argv[1:], os.getcwd(), sys.stdin.read().strip())' \
  >"$work/plugin/hooks/probe.py"
printf '%s\n' 'echo "sh $* $PWD $(cat)"' >"$work/plugin/hooks/probe.sh"
run="$work/plugin/hooks/run.sh"

# usage: check <name> <expected> <actual>
check() {
  if [[ $2 != "$3" ]]; then
    echo "FAIL $1: expected [$2] got [$3]" >&2
    fail=1
  fi
}

mkdir -p "$work/bare"
out=$(CLAUDE_PROJECT_DIR=$work/bare "$run" gate probe.py <<<payload)
check "quiet when the project has no extension file" "" "$out"
CLAUDE_PROJECT_DIR=$work/bare "$run" gate probe.py <<<payload
check "exit 0 when the project has no extension file" 0 $?

mkdir -p "$work/own/.claude/skills/repo-hooks"
cfg=$work/own/.claude/skills/repo-hooks/extension.json
printf '%s\n' '{"gate":{},"other":"text"}' >"$cfg"
check "python script gets --config and runs in the project" \
  "py --config $cfg $work/own payload" \
  "$(CLAUDE_PROJECT_DIR=$work/own "$run" gate probe.py <<<payload)"
check "shell script gets --config and extra arguments" \
  "sh --config $cfg x $work/own payload" \
  "$(CLAUDE_PROJECT_DIR=$work/own "$run" gate probe.sh x <<<payload)"
check "quiet when the file has no section for the hook" "" \
  "$(CLAUDE_PROJECT_DIR=$work/own "$run" missing probe.py <<<payload)"
check "quiet when the section is not an object" "" \
  "$(CLAUDE_PROJECT_DIR=$work/own "$run" other probe.py <<<payload)"

printf '%s\n' 'not json' >"$cfg"
check "quiet when the extension file is not JSON" "" \
  "$(CLAUDE_PROJECT_DIR=$work/own "$run" gate probe.py <<<payload)"

printf '%s\n' '{"gate":{}}' >"$cfg"
(cd "$work/own" && "$run" gate probe.py <<<payload >"$work/fallback.out")
check "the working directory stands in for CLAUDE_PROJECT_DIR" \
  "py --config $cfg $work/own payload" "$(cat "$work/fallback.out")"

mkdir -p "$work/vendored/.claude/att-docs/plugins/general" "$work/vendored/.claude/skills/repo-hooks"
cp -r "$work/plugin/hooks" "$work/vendored/.claude/att-docs/plugins/general/hooks"
printf '%s\n' '{"gate":{}}' >"$work/vendored/.claude/skills/repo-hooks/extension.json"
printf '%s\n' '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command","command":"bash .claude/att-docs/plugins/general/hooks/run.sh gate probe.py"}]}]}}' \
  >"$work/vendored/.claude/settings.json"
check "the plugin copy steps aside when the project registers its vendored copy" "" \
  "$(CLAUDE_PROJECT_DIR=$work/vendored "$run" gate probe.py <<<payload)"
check "the vendored copy runs" \
  "py --config $work/vendored/.claude/skills/repo-hooks/extension.json $work/vendored payload" \
  "$(CLAUDE_PROJECT_DIR=$work/vendored "$work/vendored/.claude/att-docs/plugins/general/hooks/run.sh" gate probe.py <<<payload)"

mkdir -p "$work/perm/.claude/skills/repo-hooks"
printf '%s\n' '{"gate":{}}' >"$work/perm/.claude/skills/repo-hooks/extension.json"
printf '%s\n' '{"permissions":{"allow":["Bash(bash plugins/general/hooks/run.sh *)"]}}' \
  >"$work/perm/.claude/settings.local.json"
check "a permission naming the runner is not a hook" "yes" \
  "$([[ $(CLAUDE_PROJECT_DIR=$work/perm "$run" gate probe.py <<<payload) == py* ]] && echo yes)"

printf '%s\n' 'import sys; sys.exit(3)' >"$work/plugin/hooks/fail.py"
CLAUDE_PROJECT_DIR=$work/own "$run" gate fail.py </dev/null
check "the script's exit code passes through" 3 $?

mkdir -p "$work/always/.claude/skills/repo-hooks" "$work/noext"
cfg=$work/always/.claude/skills/repo-hooks/extension.json
check "--default-on runs without an extension file, with no --config" \
  "py $work/noext payload" \
  "$(CLAUDE_PROJECT_DIR=$work/noext "$run" --default-on gate probe.py <<<payload)"
printf '%s\n' '{"other":{}}' >"$cfg"
check "--default-on runs when the file has no section for the hook" \
  "py --config $cfg $work/always payload" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on gate probe.py <<<payload)"
printf '%s\n' '{"gate":false}' >"$cfg"
check "--default-on is off when the section is false" "" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on gate probe.py <<<payload)"
printf '%s\n' 'not json' >"$cfg"
check "--default-on runs with defaults when the file is not JSON" \
  "py $work/always payload" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on gate probe.py <<<payload)"
check "without --default-on a project with no extension file stays quiet" "" \
  "$(CLAUDE_PROJECT_DIR=$work/noext "$run" gate probe.py <<<payload)"
printf '%s\n' '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command","command":"bash .claude/att-docs/plugins/general/hooks/run.sh --default-on gate probe.py"}]}]}}' \
  >"$work/always/.claude/settings.json"
check "--default-on steps aside when the project registers its vendored copy" "" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on gate probe.py <<<payload)"
printf '%s\n' '{"hooks":{"PreToolUse":[{"hooks":[{"type":"command","command":"bash \"$CLAUDE_PROJECT_DIR/.claude/att-docs/plugins/general/hooks/run.sh\" other probe.py"}]}]}}' \
  >"$work/always/.claude/settings.json"
check "--default-on still runs when the project registers only other hooks" \
  "py $work/always payload" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on gate probe.py <<<payload)"
check "a default-on hook the project does register steps aside, quoted path included" "" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on other probe.py <<<payload)"
check "a section that only starts with a registered name still runs" \
  "py $work/always payload" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on oth probe.py <<<payload)"
printf '%s\n' '{"gate":{},"gate2":{}}' >"$work/vendored/.claude/skills/repo-hooks/extension.json"
check "a hook that is not default-on steps aside when the project registers any hook" "" \
  "$(CLAUDE_PROJECT_DIR=$work/vendored "$run" gate2 probe.py <<<payload)"

printf '%s\n' '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"bash .claude/att-docs/plugins/general/hooks/run.sh --default-on implementLoop probe.py"}]}]}}' \
  >"$work/always/.claude/settings.json"
printf '%s\n' '{"other":{}}' >"$cfg"
check "loop Stop steps aside for its vendored registration" "" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on implementLoop probe.py <<<'{"hook_event_name":"Stop"}')"
check "loop SessionStart still runs when only Stop is vendored" \
  "py --config $cfg $work/always {\"hook_event_name\":\"SessionStart\"}" \
  "$(CLAUDE_PROJECT_DIR=$work/always "$run" --default-on implementLoop probe.py <<<'{"hook_event_name":"SessionStart"}')"

check "hooks.json names a section and script that exist" "" "$(
  jq -r '.hooks[][].hooks[].command' "$here/hooks.json" |
    sed -nE 's#.*run\.sh" (--default-on )?([A-Za-z]+) ([^ "]+).*#\2 \3#p' |
    while read -r section script; do
      [[ -f $here/$script ]] || echo "missing $script"
      [[ -n $section ]] || echo "no section for $script"
    done
)"

exit $fail
