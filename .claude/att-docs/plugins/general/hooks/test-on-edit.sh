#!/usr/bin/env bash
# usage: test-on-edit.sh --config <extension.json> < <PostToolUse payload>
# PostToolUse hook on Edit|Write. After an edit to a source file, runs the unit test file
# that belongs to it, if one exists, and tells the session when that test fails. A passing
# run, a file with no test, and a file outside the repository stay quiet.
#
# Reads the `testOnEdit` section of the extension file:
#   testDir      the folder searched for the test file, relative to the repository root
#   testName     the test file's name, with <name> for the edited file's name without its
#                extension and <ext> for its extension (default <name>.test<ext>)
#   extensions   the edited files that have tests, with the dot (default [".ts"])
#   command      the test command as a list of words; the test file's path is added last
#   tailLines    how many of the last output lines to show when the test fails (default 10)
set -uo pipefail

[[ ${1:-} == --config && -f ${2:-} ]] || { echo "usage: $0 --config <extension.json>" >&2; exit 64; }
config=$2

file=$(jq -r '.tool_input.file_path // ""' || true)
[[ -n $file ]] || exit 0

test_dir=$(jq -r '.testOnEdit.testDir // ""' "$config")
mapfile -t command < <(jq -r '.testOnEdit.command // [] | .[]' "$config")
[[ -n $test_dir && ${#command[@]} -gt 0 ]] || exit 0
name_pattern=$(jq -r '.testOnEdit.testName // "<name>.test<ext>"' "$config")
tail_lines=$(jq -r '.testOnEdit.tailLines // 10' "$config")
mapfile -t extensions < <(jq -r '.testOnEdit.extensions // [".ts"] | .[]' "$config")

# Only a file under the repository the hook runs in.
root=$(pwd -P)
[[ $file == /* ]] || file=$root/$file
file=$(readlink -m "$file")
[[ $file == "$root"/* ]] || exit 0

base=$(basename "$file")
ext=
for candidate in "${extensions[@]}"; do
  if [[ $base == *"$candidate" && ${#candidate} -gt ${#ext} ]]; then ext=$candidate; fi
done
[[ -n $ext ]] || exit 0
name=${base%"$ext"}
test_name=${name_pattern//<name>/$name}
test_name=${test_name//<ext>/$ext}

[[ -d $test_dir ]] || exit 0
test_file=$(find "$test_dir" -name "$test_name" -type f 2>/dev/null | sort | head -1)
[[ -n $test_file ]] || exit 0

output=$("${command[@]}" "$test_file" 2>&1)
status=$?
[[ $status -ne 0 ]] || exit 0

msg="The test file $test_file failed after the edit to ${file#"$root"/} (exit $status). Last ${tail_lines} lines:"$'\n'$(tail -n "$tail_lines" <<<"$output")
jq -n --arg m "$msg" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $m}}'
