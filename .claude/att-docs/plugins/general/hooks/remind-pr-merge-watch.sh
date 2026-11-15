#!/usr/bin/env bash
# usage: remind-pr-merge-watch.sh --config <extension.json> < <PostToolUse payload>
# PostToolUse hook on Bash. After a `gh pr create` that printed a pull request URL, tells
# the session to record the pull request in its catch-up ledger and keep one `wait`
# running, so the merge reaches the session without the user reporting it.
#
# Reads the `mergeWatchReminder` section of the extension file:
#   ledgerTool  the repository's catch-up ledger script, as a command (for example
#               scripts/catchup.py). Its `add-pr <ledger> <N> "<label>"` records a pull
#               request and its `wait <ledger>` blocks until one merges
#   message     optional: the whole reminder, with <N> for the pull request number and
#               <ledgerTool> for the tool. Without it the reminder is the short default
set -euo pipefail

[[ ${1:-} == --config && -f ${2:-} ]] || { echo "usage: $0 --config <extension.json>" >&2; exit 64; }
config=$2

input=$(cat)
command=$(jq -r '.tool_input.command // ""' <<<"$input")
# Only a command that runs `gh pr create`, at its start or after a shell separator, not
# one that merely mentions it (a grep of the docs, a commit message).
grep -qE '(^|[;&|(])[[:space:]]*gh pr create' <<<"$command" || exit 0

tool=$(jq -r '.mergeWatchReminder.ledgerTool // ""' "$config")
template=$(jq -r '.mergeWatchReminder.message // ""' "$config")
if [[ -z $template ]]; then
  [[ -n $tool ]] || exit 0
  template='Pull request <N> was opened. Before ending the turn, record it with `<ledgerTool> add-pr <ledger> <N> "<label>"` and make sure one `<ledgerTool> wait <ledger>` runs in the background, so its merge reaches you without the user reporting it. When `wait` prints `pr: <N> merged`, run the after-merge steps straight away.'
fi

# gh pr create prints the new URL on a line of its own; a URL inside other output
# (test data, a grep of the docs) is not a pull request this command opened.
stdout=$(jq -r '.tool_response
  | if type == "object" then (.stdout // "") | tostring
    elif type == "string" then . else tostring end' <<<"$input")
url_re='https://github\.com/[^/[:space:]]+/[^/[:space:]]+/pull/([0-9]+)'
numbers=$(sed -nE "s#^[[:space:]]*${url_re}[[:space:]]*\$#\\1#p" <<<"$stdout" \
  | awk '!seen[$0]++')
test -n "$numbers" || exit 0

# One reminder per pull request, so a command that opens several records each.
msg=""
for number in $numbers; do
  test -z "$msg" || msg+=$'\n\n'
  one=${template//<ledgerTool>/"$tool"}
  msg+=${one//<N>/"$number"}
done

jq -n --arg m "$msg" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $m}}'
