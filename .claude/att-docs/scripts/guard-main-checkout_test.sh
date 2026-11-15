#!/usr/bin/env bash
# Feeds hook payloads to guard-main-checkout.sh and checks each exit code.
# The guard runs from a copy inside a throwaway repository with one worktree,
# so the cases do not depend on where this clone sits.
# usage: scripts/guard-main-checkout_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

M="$SANDBOX/main"
W="$M/.claude/worktrees/wt"
OUT="$SANDBOX/scratchpad"
mkdir -p "$M/scripts/lib" "$M/node_modules" "$OUT"
cp "$HERE/guard-main-checkout.sh" "$M/scripts/"
cp "$HERE/lib/session-paths.sh" "$HERE/lib/hook-tool.sh" "$HERE/lib/heredoc.py" \
  "$HERE/lib/git-targets.py" \
  "$M/scripts/lib/"
git -C "$M" init -q -b main
git -C "$M" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
git -C "$M" config branch.main.remote origin
git -C "$M" config branch.main.merge refs/heads/main
git -C "$M" worktree add -q -b wt "$W"
ln -s "$M/node_modules" "$W/node_modules"

G="$M/scripts/guard-main-checkout.sh"
fails=0

# usage: run <wanted exit> <cwd> <tool> <file path, or command for Bash>
run() {
  local want=$1 cwd=$2 tool=$3 arg=$4 payload got
  if [ "$tool" = Bash ]; then
    payload=$(jq -n --arg c "$cwd" --arg a "$arg" \
      '{cwd:$c,tool_name:"Bash",tool_input:{command:$a}}')
  else
    payload=$(jq -n --arg c "$cwd" --arg t "$tool" --arg a "$arg" \
      '{cwd:$c,tool_name:$t,tool_input:{file_path:$a}}')
  fi
  check "$want" "$cwd" "$tool" "$arg" "$payload"
}

# usage: run_input <wanted exit> <cwd> <tool> <tool_input as JSON>
run_input() {
  local want=$1 cwd=$2 tool=$3 input=$4 payload
  payload=$(jq -n --arg c "$cwd" --arg t "$tool" --argjson i "$input" \
    '{cwd:$c,tool_name:$t,tool_input:$i}')
  check "$want" "$cwd" "${tool#"$DC"}" "$input" "$payload"
}

check() {
  local want=$1 cwd=$2 tool=$3 arg=$4 payload=$5 got
  "$G" <<<"$payload" 2>/dev/null
  got=$?
  if [ "$got" = "$want" ]; then
    echo "ok   $tool $arg (cwd ${cwd#"$SANDBOX"/})"
  else
    echo "FAIL $tool $arg (cwd ${cwd#"$SANDBOX"/}): wanted $want, got $got"
    fails=$((fails + 1))
  fi
}

DC=mcp__plugin_desktop-commander_desktop-commander__
T=mcp__terminal__run_in_terminal

# Edit tools from the main checkout: judged by where the write lands.
run 0 "$M" Write "$OUT/stalled-1.md"
run 2 "$M" Write "$M/src/a.ts"
run 2 "$M" Edit src/a.ts
run 2 "$M/src" Edit ../README.md
run 2 "$M" Write "$M"
run 0 "$M" Edit "$W/scripts/x.sh"
run 2 "$M" Edit "$W/../../../src/a.ts"
run 2 "$M" Write "$W/node_modules/x.js"
run 0 "$M" Write ""

# Edit tools from a worktree: the same rule, whatever the cwd.
run 0 "$W" Write "$W/src/a.ts"
run 0 "$W" Write src/a.ts
run 0 "$W" Write "$OUT/pr-body.md"
run 2 "$W" Write "$M/src/a.ts"
run 2 "$W" Write node_modules/x.js

# Bash from the main checkout: bare branch-mutating git only.
run 2 "$M" Bash "git checkout main"
run 0 "$M" Bash "git -C $W checkout main"
run 0 "$M" Bash "ls"
run 0 "$W" Bash "git checkout main"

# A heredoc body is text, so a line in it is never read as a command.
run 0 "$M" Bash $'cat > x.md <<\'EOF\'\ngit stash pop\nEOF'
run 0 "$M" Bash $'cat > x.md <<-EOF\n\tgit checkout main\n\tEOF'
run 0 "$M" Bash $'cat <<A > a.md; cat <<"B" > b.md\ngit reset\nA\nrm x.yml\nB'
run 0 "$W" Bash $'git commit -F - <<\'EOF\'\nnpm run build\nEOF'
run 2 "$M" Bash $'cat > x.md <<\'EOF\'\ntext\nEOF\ngit stash pop'
run 2 "$M" Bash $'grep x <<< "a"\ngit checkout main'
run 0 "$M" Bash $'x="$(cat <<-E\n\tgit reset\n\tE\n)"'
# A `<<` in a string, a comment, or a shift opens no heredoc.
run 2 "$M" Bash $'grep -n "<<" a.sh\ngit checkout main'
run 2 "$M" Bash $'echo $((1<<2))\ngit checkout main'
run 2 "$M" Bash $'ls # <<X\ngit checkout main'

# A git command is judged where it acts: after a `cd`, and through `-C`.
run 2 "$W" Bash "cd $M && git checkout -b x"
run 2 "$W" Bash "git -C $M checkout -b y"
run 2 "$W" Bash "git -C $M pull"
run 2 "$M" Bash "git -C $M switch -c z"
run 2 "$M" Bash "git -c core.x=1 checkout -b q"
run 0 "$M" Bash "cd $W && git switch -c ok"
run 0 "$M" Bash "cd $W && git merge origin/main"
run 2 "$W" Bash "cd ../../.. && git stash pop"
run 0 "$W" Bash "git -C $M status && git switch main"
run 2 "$W" Bash "git -C $W -C ../../.. reset --hard"
run 2 "$W" Bash $'cd '"$M"$'\ngit pull'
run 2 "$M" Bash $'git \\\n  checkout main'
run 2 "$W" Bash "env -i git -C $M checkout x"
run 2 "$W" Bash "sudo -u me git -C $M pull"
run 0 "$W" Bash "env -i git -C $W checkout x"
# A fast-forward-only pull of main from origin keeps the main checkout current.
run 0 "$M" Bash "git pull --ff-only origin main"
run 0 "$M" Bash "git pull --ff-only"
run 0 "$W" Bash "git -C $M pull -q --ff-only origin"
run 0 "$M" Bash "cd $M && git pull --ff-only origin main && git log -1"
run 0 "$M" Bash "git pull --ff-only --prune origin main 2>&1 | tail -3"
run 0 "$M" Bash "git pull --ff-only origin main >/dev/null"
run 0 "$M" Bash "git pull --ff-only origin main > out.txt"
# Every other pull, and every other verb, is still refused there.
run 2 "$M" Bash "git pull"
run 2 "$M" Bash "git pull origin main"
run 2 "$M" Bash "git pull --ff-only origin fix/1-old"
run 2 "$M" Bash "git pull --ff-only origin main:main"
run 2 "$M" Bash "git pull --ff-only upstream main"
run 2 "$M" Bash "git pull --ff-only --rebase origin main"
run 2 "$M" Bash "git pull --ff-only origin main && git merge x"
run 2 "$M" Bash "git merge --ff-only origin/main"
run 2 "$M" Bash "git reset --hard origin/main"
run 2 "$M" Bash "git rebase origin/main"
run 2 "$M" Bash "git stash"
run 2 "$M" Bash "git restore ."
run 2 "$M" Bash "git switch main"
# A global option can point the pull somewhere else, so it rules the pull out.
run 2 "$M" Bash "git -c branch.main.merge=refs/heads/fix/x pull --ff-only"
run 2 "$M" Bash "git -c remote.origin.url=/x pull --ff-only origin main"
run 2 "$M" Bash "git --work-tree=$M pull --ff-only origin main"
run 2 "$M" Bash 'cd "$WT" && git pull --ff-only origin main'
# So can the environment git starts with.
run 2 "$M" Bash "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=branch.main.merge git pull --ff-only"
run 2 "$M" Bash "env GIT_WORK_TREE=/tmp git pull --ff-only"
# A redirection mid-command is one word, so the words after it are still read.
run 2 "$M" Bash "git pull --ff-only 2>&1 origin fix/1-old"
run 2 "$M" Bash "git pull --ff-only >&2 --rebase origin main"
run 2 "$M" Bash "git pull --ff-only &>/dev/null origin fix/1-old"
run 2 "$M" Bash "git pull --ff-only >| out origin fix/1-old"
# `&>out` and `& >out` lex alike, so a pull before either is refused.
run 2 "$M" Bash "git pull --ff-only &>/dev/null origin main"
# Only a cd may come before the pull: anything else can retarget it.
run 2 "$M" Bash "git config branch.main.merge refs/heads/fix/x; git pull --ff-only"
run 2 "$M" Bash "export GIT_DIR=/x; git pull --ff-only"
run 2 "$M" Bash "git remote set-url origin /x && git pull --ff-only origin main"
# A redirection before git, or before its verb, hides no verb.
run 2 "$M" Bash "git 2>/dev/null checkout x"
run 2 "$M" Bash ">/dev/null git checkout x"
run 2 "$M" Bash "true & >log git checkout main"
# The pull is only of main: off main, or tracking another branch, it is refused.
git -C "$M" config branch.main.merge refs/heads/fix/x
run 2 "$M" Bash "git pull --ff-only"
git -C "$M" config --add branch.main.merge refs/heads/main
run 2 "$M" Bash "git pull --ff-only"
git -C "$M" config --replace-all branch.main.merge refs/heads/main
git -C "$M" switch -q -c other
run 2 "$M" Bash "git pull --ff-only origin main"
git -C "$M" switch -q main
# A subshell's cd ends with the subshell.
run 0 "$W" Bash "(cd $M && git status); git switch main"
run 2 "$W" Bash "(cd $M && git switch main)"
# A directory the text cannot settle is judged from where the command starts.
run 0 "$W" Bash 'cd "$WT" && git switch main'
run 2 "$M" Bash 'cd "$WT" && git switch main'
# Text that only mentions git is not a git command.
run 0 "$M" Bash "echo 'cd $M && git pull'"
# A command that will not split is read line by line from where it starts.
run 2 "$M" Bash $'echo "open\ngit checkout main'
run 0 "$W" Bash $'echo "open\ngit checkout main'
# Without python3, a bare git verb is judged from where the command starts.
NOPY="$SANDBOX/nopython"
mkdir -p "$NOPY"
printf '#!/bin/sh\nexit 127\n' >"$NOPY/python3"
chmod +x "$NOPY/python3"
PATH="$NOPY:$PATH" run 2 "$M" Bash "git -c a=b checkout main"
PATH="$NOPY:$PATH" run 0 "$W" Bash "git checkout main"

# MCP file tools get the edit rule, judged by every path they name.
run_input 2 "$M" "${DC}write_file" "{\"path\":\"$M/src/a.ts\"}"
run_input 0 "$W" "${DC}write_file" "{\"path\":\"src/a.ts\"}"
HOME="$SANDBOX" run_input 2 "$W" "${DC}write_file" "{\"path\":\"~/${M#"$SANDBOX"/}/src/a.ts\"}"
run_input 2 "$W" "${DC}edit_block" "{\"file_path\":\"$M/src/a.ts\"}"
run_input 2 "$W" "${DC}write_pdf" "{\"path\":\"$W/a.pdf\",\"outputPath\":\"$M/a.pdf\"}"
run_input 2 "$W" "${DC}move_file" "{\"source\":\"$W/a\",\"destination\":\"$M/a\"}"
run_input 2 "$W" "${DC}create_directory" "{\"path\":\"$M/new\"}"
run_input 0 "$W" "${DC}move_file" "{\"source\":\"$W/a\",\"destination\":\"$W/b\"}"

# MCP shell tools get the shell rule; a terminal tab is judged from its own cwd.
run_input 2 "$M" "${DC}start_process" '{"command":"git checkout main"}'
run_input 2 "$M" "${DC}interact_with_process" '{"input":"git stash pop"}'
run_input 0 "$W" "${DC}interact_with_process" '{"input":"git stash pop"}'
run_input 2 "$W" "$T" "{\"command\":\"git switch main\",\"cwd\":\"$M\"}"
run_input 0 "$M" "$T" "{\"command\":\"git switch main\",\"cwd\":\"$W\"}"
# A tab cwd that climbs out of a worktree is judged where it lands.
run_input 2 "$W" "$T" '{"command":"git switch main","cwd":"../../.."}'
run_input 2 "$W" "$T" "{\"command\":\"git switch main\",\"cwd\":\"$W/../../..\"}"
# The same server registered as a plain MCP server is read the same way.
run_input 2 "$W" mcp__desktop-commander__write_file "{\"path\":\"$M/src/a.ts\"}"
run_input 2 "$M" mcp__desktop-commander__start_process '{"command":"git checkout main"}'

# The settings.json entry: its matcher picks the tools, its command runs the guard.
SETTINGS="$HERE/../.claude/settings.json"
MATCHER=$(jq -r '.hooks.PreToolUse[0].matcher' "$SETTINGS")
HOOK_CMD=$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$SETTINGS")

# usage: match <wanted: yes|no> <tool name>
match() {
  local want=$1 tool=$2 got=no
  if grep -Eq "^($MATCHER)\$" <<<"$tool"; then got=yes; fi
  if [ "$got" = "$want" ]; then
    echo "ok   matcher $want: $tool"
  else
    echo "FAIL matcher $tool: wanted $want, got $got"
    fails=$((fails + 1))
  fi
}

# usage: hook_exit <wanted exit> <label> <project dir>
hook_exit() {
  local want=$1 label=$2 dir=$3 payload got
  payload=$(jq -n --arg c "$M" '{cwd:$c,tool_name:"Bash",tool_input:{command:"git checkout x"}}')
  CLAUDE_PROJECT_DIR="$dir" bash -c "$HOOK_CMD" <<<"$payload" >/dev/null 2>&1
  got=$?
  if [ "$got" = "$want" ]; then
    echo "ok   hook command $label"
  else
    echo "FAIL hook command $label: wanted $want, got $got"
    fails=$((fails + 1))
  fi
}

for t in Bash Edit Write NotebookEdit "$T" "${DC}write_file"; do match yes "$t"; done
match no Read

hook_exit 2 "blocks git checkout in the main checkout" "$M"
chmod -x "$G"
hook_exit 0 "skips a guard that is not executable" "$M"
chmod +x "$G"
mkdir -p "$SANDBOX/noguard"
hook_exit 0 "skips a project with no guard" "$SANDBOX/noguard"

if [ "$fails" -gt 0 ]; then
  echo "$fails case(s) failed"
  exit 1
fi
echo "all cases passed"
