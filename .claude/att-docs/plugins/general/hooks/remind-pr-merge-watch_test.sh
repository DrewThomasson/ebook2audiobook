#!/usr/bin/env bash
# usage: bash remind-pr-merge-watch_test.sh
# Tests remind-pr-merge-watch.sh with canned PostToolUse payloads.
set -u
here=$(dirname "$(readlink -f "$0")")
hook="$here/remind-pr-merge-watch.sh"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
fail=0

# usage: check <name> <expected> <actual>
check() {
  if [[ $2 != "$3" ]]; then
    echo "FAIL $1: expected [$2] got [$3]" >&2
    fail=1
  fi
}

cfg=$work/ledger.json
printf '%s\n' '{"mergeWatchReminder":{"ledgerTool":"scripts/catchup.py"}}' >"$cfg"
custom=$work/custom.json
printf '%s\n' '{"mergeWatchReminder":{"message":"PR <N> is open: run <ledgerTool> now.","ledgerTool":"bin/led"}}' >"$custom"
messageonly=$work/messageonly.json
printf '%s\n' '{"mergeWatchReminder":{"message":"PR <N> is open."}}' >"$messageonly"
empty=$work/empty.json
printf '%s\n' '{"mergeWatchReminder":{}}' >"$empty"

# usage: payload <command> <stdout>
payload() {
  jq -n --arg c "$1" --arg o "$2" \
    '{tool_name: "Bash", tool_input: {command: $c}, tool_response: {stdout: $o}}'
}
# usage: context <config> <command> <stdout>
context() {
  payload "$2" "$3" | bash "$hook" --config "$1" | jq -r '.hookSpecificOutput.additionalContext // empty'
}
url=https://github.com/o/r/pull/42

out=$(context "$cfg" "gh pr create --title t --body-file b.md" "$url")
check "the default reminder names the pull request" "yes" \
  "$([[ $out == "Pull request 42 was opened."* ]] && echo yes)"
check "the default reminder names the ledger tool" "yes" \
  "$([[ $out == *'`scripts/catchup.py add-pr <ledger> 42 "<label>"`'* ]] && echo yes)"
check "the output is PostToolUse additionalContext" "PostToolUse" \
  "$(payload "gh pr create" "$url" | bash "$hook" --config "$cfg" | jq -r .hookSpecificOutput.hookEventName)"

check "a custom message fills <N> and <ledgerTool>" "PR 42 is open: run bin/led now." \
  "$(context "$custom" "git push && gh pr create --fill" "$url")"
ampersand=$work/ampersand.json
printf '%s\n' '{"mergeWatchReminder":{"message":"PR <N>: <ledgerTool>","ledgerTool":"a&b"}}' >"$ampersand"
check "an ampersand in the tool is kept as written" "PR 42: a&b" \
  "$(context "$ampersand" "gh pr create --fill" "$url")"
check "a message alone is enough" "PR 42 is open." \
  "$(context "$messageonly" "gh pr create --fill" "$url")"
check "a section with no tool and no message stays quiet" "" \
  "$(context "$empty" "gh pr create --fill" "$url")"

check "one reminder per pull request" "PR 1 is open.

PR 2 is open." \
  "$(context "$messageonly" "gh pr create --fill" "https://github.com/o/r/pull/1
https://github.com/o/r/pull/2")"
check "a repeated URL reminds once" "PR 42 is open." \
  "$(context "$messageonly" "gh pr create --fill" "$url
$url")"

check "a command that only mentions gh pr create stays quiet" "" \
  "$(context "$cfg" "grep -n 'gh pr create' CLAUDE.md" "$url")"
check "a URL inside other output stays quiet" "" \
  "$(context "$cfg" "gh pr create --fill" "see $url for details")"
check "no URL stays quiet" "" "$(context "$cfg" "gh pr create --fill" "failed")"
check "a different command stays quiet" "" "$(context "$cfg" "gh pr view 42" "$url")"
check "a string tool_response is read" "PR 42 is open." \
  "$(jq -n --arg u "$url" '{tool_input:{command:"gh pr create"},tool_response:$u}' |
    bash "$hook" --config "$messageonly" | jq -r '.hookSpecificOutput.additionalContext')"

bash "$hook" </dev/null 2>/dev/null
check "no --config exits 64" 64 $?

exit $fail
