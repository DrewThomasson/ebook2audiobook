#!/usr/bin/env bash
# Feeds hook payloads to hook_tool and checks the kind, command, and cwd it reads.
# The main-checkout guard classifies tools through it.
# usage: scripts/lib/hook-tool_test.sh

. "$(dirname "$0")/hook-tool.sh"
fails=0
DC=mcp__plugin_desktop-commander_desktop-commander__
T=mcp__terminal__run_in_terminal

# usage: want <kind> <cmd> <cwd> <tool> <tool_input as JSON>
want() {
  local kind=$1 cmd=$2 cwd=$3 tool=$4 input=$5 got
  hook_tool "$(jq -n --arg t "$tool" --argjson i "$input" \
    '{cwd:"/s",tool_name:$t,tool_input:$i}')"
  got="$HOOK_KIND|$HOOK_CMD|$HOOK_CWD"
  if [ "$got" = "$kind|$cmd|$cwd" ]; then
    echo "ok   $tool $input"
  else
    echo "FAIL $tool $input: wanted $kind|$cmd|$cwd, got $got"
    fails=$((fails + 1))
  fi
}

want shell "ls" /s Bash '{"command":"ls"}'
want shell "ls" /s "${DC}start_process" '{"command":"ls"}'
want shell "ls" /s mcp__desktop-commander__start_process '{"command":"ls"}'
want shell "q" /s "${DC}interact_with_process" '{"pid":1,"input":"q"}'
want shell "ls" /s "$T" '{"command":"ls"}'
want shell "ls" /t "$T" '{"command":"ls","cwd":"/t"}'
want shell "ls" / "$T" '{"command":"ls","cwd":"../.."}'
want shell "ls" /s/a "$T" '{"command":"ls","cwd":"a/b/.."}'
HOME=/h want shell "ls" /h/x "$T" '{"command":"ls","cwd":"~/x"}'
want shell "ls" /s Bash '{"command":"ls","cwd":"/t"}'
want edit "" /s Write '{"file_path":"a"}'
want edit "" /s "${DC}move_file" '{"source":"a","destination":"b"}'
want edit "" /s mcp__desktop-commander__write_file '{"path":"a"}'
want edit "" /s "${DC}write_pdf" '{"path":"a"}'
want "" "" /s "${DC}read_file" '{"path":"a"}'
want "" "" /s Read '{"file_path":"a"}'
want "" "" /s mcp__other__write_file '{"path":"a"}'
L="$(mktemp -d)"
ln -s / "$L/root"
hook_tool "$(jq -n --arg c "$L/root/tmp" '{cwd:$c,tool_name:"Bash",tool_input:{}}')"
if [ "$HOOK_CWD" = /tmp ]; then
  echo "ok   session cwd through a link resolves"
else
  echo "FAIL session cwd through a link: wanted /tmp, got $HOOK_CWD"
  fails=$((fails + 1))
fi
rm -rf "$L"

if [ "$fails" -gt 0 ]; then
  echo "$fails case(s) failed"
  exit 1
fi
echo "all cases passed"
