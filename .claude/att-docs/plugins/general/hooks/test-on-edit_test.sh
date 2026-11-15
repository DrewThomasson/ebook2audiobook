#!/usr/bin/env bash
# usage: bash test-on-edit_test.sh
# Tests test-on-edit.sh in a throwaway repository whose "test command" is a stub script.
set -u
here=$(dirname "$(readlink -f "$0")")
hook="$here/test-on-edit.sh"
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

repo=$work/repo
mkdir -p "$repo/src/tests/sub" "$repo/lib"
# The stub test command passes unless the test file says FAIL, and records what it ran.
cat >"$work/runner.sh" <<STUB
#!/usr/bin/env bash
echo "ran \$1" >>"$work/ran.log"
cat "\$1"
! grep -q FAIL "\$1"
STUB
chmod +x "$work/runner.sh"
: >"$work/ran.log"
printf 'ok\n' >"$repo/src/tests/widget.test.ts"
printf 'line1\nFAIL here\n' >"$repo/src/tests/sub/broken.test.ts"
printf 'ok\n' >"$repo/src/tests/styles.spec.js"
: >"$repo/lib/widget.ts"

cfg=$work/ext.json
jq -n --arg r "$work/runner.sh" \
  '{testOnEdit: {testDir: "src/tests", command: [$r], tailLines: 5}}' >"$cfg"

# usage: edit <config> <file_path>   (prints the hook's stdout)
edit() {
  jq -n --arg f "$2" '{tool_name: "Edit", tool_input: {file_path: $f}}' |
    (cd "$repo" && bash "$hook" --config "$1")
}
ran() { cat "$work/ran.log"; : >"$work/ran.log"; }

check "a passing test is silent" "" "$(edit "$cfg" "$repo/lib/widget.ts")"
check "the test beside the name was run" "ran src/tests/widget.test.ts" "$(ran)"

check "a relative path is accepted" "" "$(edit "$cfg" "lib/widget.ts")"
check "a relative path runs the same test" "ran src/tests/widget.test.ts" "$(ran)"

out=$(edit "$cfg" "$repo/lib/broken.ts")
check "a failing test reports additionalContext" "PostToolUse" \
  "$(jq -r .hookSpecificOutput.hookEventName <<<"$out")"
ctx=$(jq -r .hookSpecificOutput.additionalContext <<<"$out")
check "the report names the test file" "yes" "$([[ $ctx == *"src/tests/sub/broken.test.ts failed"* ]] && echo yes)"
check "the report includes the test output" "yes" "$([[ $ctx == *"FAIL here"* ]] && echo yes)"
check "the report names the edited file" "yes" "$([[ $ctx == *"lib/broken.ts"* ]] && echo yes)"
ran >/dev/null

check "a file with no test is silent" "" "$(edit "$cfg" "$repo/lib/none.ts")"
check "no test was run for it" "" "$(ran)"
check "an extension outside the list is skipped" "" "$(edit "$cfg" "$repo/lib/widget.md")"
check "nothing ran for the other extension" "" "$(ran)"
check "a file outside the repository is skipped" "" "$(edit "$cfg" "/elsewhere/widget.ts")"
check "nothing ran outside the repository" "" "$(ran)"
ln -s "$repo" "$work/link"
out=$(jq -n --arg f "$work/link/lib/broken.ts" '{tool_input: {file_path: $f}}' | (cd "$work/link" && bash "$hook" --config "$cfg"))
check "an edit reached through a symlinked folder still runs its test" "yes" \
  "$([[ $out == *"failed after the edit to lib/broken.ts"* ]] && echo yes)"
ran >/dev/null
check "a payload with no file path is skipped" "" \
  "$(echo '{"tool_input":{}}' | (cd "$repo" && bash "$hook" --config "$cfg"))"

jq -n --arg r "$work/runner.sh" \
  '{testOnEdit: {testDir: "src/tests", testName: "<name>.spec<ext>", extensions: [".js", ".ts"], command: [$r]}}' \
  >"$work/other.json"
check "testName and extensions come from the config" "" "$(edit "$work/other.json" "$repo/lib/styles.js")"
check "the configured name was found" "ran src/tests/styles.spec.js" "$(ran)"
: >"$repo/lib/dotted.test.ts"
jq -n --arg r "$work/runner.sh" \
  '{testOnEdit: {testDir: "src/tests", extensions: [".test.ts", ".ts"], testName: "<name>.check.ts", command: [$r]}}' \
  >"$work/longest.json"
printf 'ok\n' >"$repo/src/tests/dotted.check.ts"
check "the longest matching extension wins" "" "$(edit "$work/longest.json" "$repo/lib/dotted.test.ts")"
check "so <name> drops all of it" "ran src/tests/dotted.check.ts" "$(ran)"

jq -n '{testOnEdit: {testDir: "src/tests"}}' >"$work/nocmd.json"
check "no command means no hook" "" "$(edit "$work/nocmd.json" "$repo/lib/broken.ts")"
jq -n '{testOnEdit: {command: ["true"]}}' >"$work/nodir.json"
check "no test folder means no hook" "" "$(edit "$work/nodir.json" "$repo/lib/broken.ts")"
jq -n --arg r "$work/runner.sh" '{testOnEdit: {testDir: "missing", command: [$r]}}' >"$work/gone.json"
check "a test folder that does not exist is skipped" "" "$(edit "$work/gone.json" "$repo/lib/widget.ts")"

echo '{}' | bash "$hook" >/dev/null 2>&1
check "no --config exits 64" 64 $?

exit $fail
