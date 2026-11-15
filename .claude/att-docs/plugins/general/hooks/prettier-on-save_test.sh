#!/usr/bin/env bash
# usage: bash prettier-on-save_test.sh
# Tests prettier-on-save.sh in a throwaway repository whose "formatter" is a stub script.
set -u
here=$(dirname "$(readlink -f "$0")")
hook="$here/prettier-on-save.sh"
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

cat >"$work/fmt.sh" <<STUB
#!/usr/bin/env bash
echo "\$*" >>"$work/fmt.log"
STUB
chmod +x "$work/fmt.sh"
: >"$work/fmt.log"

new_repo() {
  rm -rf "$work/repo"
  mkdir -p "$work/repo/src/deep" "$work/repo/docs"
  : >"$work/repo/src/a.ts"
  : >"$work/repo/src/b.tsx"
  : >"$work/repo/src/deep/c.ts"
  : >"$work/repo/src/d.js"
  : >"$work/repo/docs/e.md"
}
# usage: edit <config> <file>   (prints the hook's stdout)
edit() {
  jq -n --arg f "$2" '{tool_name: "Write", tool_input: {file_path: $f}}' |
    (cd "$work/repo" && bash "$hook" --config "$1")
}
formatted() { cat "$work/fmt.log"; : >"$work/fmt.log"; }

jq -n --arg c "$work/fmt.sh" '{prettierOnSave: {command: [$c, "--write"]}}' >"$work/cfg.json"
r=$work/repo

new_repo
edit "$work/cfg.json" "$r/src/a.ts"
check "a repository with no Prettier config is skipped" "" "$(formatted)"

touch "$r/.prettierrc"
check "no output ever" "" "$(edit "$work/cfg.json" "$r/src/a.ts")"
check "a .ts file is formatted when the repository has a config" "--write $r/src/a.ts" "$(formatted)"
edit "$work/cfg.json" "$r/src/b.tsx"
check "a .tsx file is formatted" "--write $r/src/b.tsx" "$(formatted)"
edit "$work/cfg.json" "src/deep/c.ts"
check "a relative path is formatted by its full path" "--write $r/src/deep/c.ts" "$(formatted)"
edit "$work/cfg.json" "$r/src/d.js"
check "a .js file is outside the default globs" "" "$(formatted)"
edit "$work/cfg.json" "$r/src/missing.ts"
check "a file that does not exist is skipped" "" "$(formatted)"
edit "$work/cfg.json" "/elsewhere/x.ts"
check "a file outside the repository is skipped" "" "$(formatted)"
ln -sfn "$r" "$work/link"
jq -n --arg f "$work/link/src/a.ts" '{tool_input: {file_path: $f}}' | (cd "$work/link" && bash "$hook" --config "$work/cfg.json")
check "a file reached through a symlinked folder is formatted" "--write $r/src/a.ts" "$(formatted)"
echo '{"tool_input":{}}' | (cd "$r" && bash "$hook" --config "$work/cfg.json")
check "a payload with no file path is skipped" "" "$(formatted)"

new_repo
printf '{"name":"x","prettier":{"semi":false}}\n' >"$r/package.json"
edit "$work/cfg.json" "$r/src/a.ts"
check "a package.json prettier key counts as a config" "--write $r/src/a.ts" "$(formatted)"
printf '{"name":"x"}\n' >"$r/package.json"
edit "$work/cfg.json" "$r/src/a.ts"
check "a package.json without the key does not" "" "$(formatted)"

new_repo
touch "$r/src/prettier.config.mjs"
edit "$work/cfg.json" "$r/src/deep/c.ts"
check "a config in a folder above the file counts" "--write $r/src/deep/c.ts" "$(formatted)"
edit "$work/cfg.json" "$r/docs/e.md"
check "a config in another folder does not" "" "$(formatted)"

new_repo
touch "$r/.fmtrc"
jq -n --arg c "$work/fmt.sh" \
  '{prettierOnSave: {command: [$c], globs: ["docs/*.md", "src/*.js"], configFiles: [".fmtrc"]}}' >"$work/custom.json"
edit "$work/custom.json" "$r/docs/e.md"
check "globs, command and configFiles come from the config" "$r/docs/e.md" "$(formatted)"
edit "$work/custom.json" "$r/src/a.ts"
check "a file outside the configured globs is skipped" "" "$(formatted)"
rm "$r/.fmtrc"
edit "$work/custom.json" "$r/docs/e.md"
check "the default config names no longer count when configFiles is set" "" "$(formatted)"

new_repo
touch "$r/.prettierrc"
jq -n '{prettierOnSave: {command: ["false"]}}' >"$work/failing.json"
edit "$work/failing.json" "$r/src/a.ts"
check "a failing formatter does not fail the hook" 0 $?
jq -n '{prettierOnSave: {command: []}}' >"$work/nocmd.json"
edit "$work/nocmd.json" "$r/src/a.ts"
check "an empty command means no hook" 0 $?
check "and nothing ran" "" "$(formatted)"

echo '{}' | bash "$hook" >/dev/null 2>&1
check "no --config exits 64" 64 $?

exit $fail
