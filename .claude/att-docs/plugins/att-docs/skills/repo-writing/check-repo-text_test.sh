#!/usr/bin/env bash
# Cases for check-repo-text.sh: the four scans (reference, history, voice,
# spelling), the escapes (kept identifiers, verbatim marker, skip and exempt
# paths, converted documents), the changed-files default, and the exit codes.
# Every case runs in a scratch git repository with no real git config.
#
# Run: bash plugins/att-docs/skills/repo-writing/check-repo-text_test.sh
set -u

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-repo-text.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com
export GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com
mkdir -p "$HOME"
fail=0

check() { # name expected actual
  if [ "$2" = "$3" ]; then
    echo "ok   $1"
  else
    echo "FAIL $1: expected [$2] got [$3]"
    fail=1
  fi
}
contains() { # name needle haystack
  case "$3" in
    *"$2"*) echo "ok   $1" ;;
    *) echo "FAIL $1: [$2] not in [$3]"; fail=1 ;;
  esac
}
lacks() { # name needle haystack
  case "$3" in
    *"$2"*) echo "FAIL $1: [$2] found in [$3]"; fail=1 ;;
    *) echo "ok   $1" ;;
  esac
}

repo="$tmp/repo"
mkdir -p "$repo/docs" "$repo/gen" "$repo/tools"
cd "$repo" || exit 1
git init -q -b main . && git commit -q --allow-empty -m init

printf '%s\n' \
  'ban	all	issue #[0-9]+' \
  'ban-cs	all	SecretTool' \
  'keep	all	keepme-[0-9]+' \
  'ban	trackeronly	trackerword' \
  'ban	gen/*	globword' >terms.tsv
cat >cfg.json <<'JSON'
{
  "terms": "terms.tsv",
  "trackerScope": "trackeronly",
  "guide": "docs/guide.md",
  "verbatimMarker": "VERBATIM",
  "mainBranch": "main",
  "shipping": "\\.(md|txt)$",
  "notShipping": "^tools/",
  "skipPaths": ["^gen/skipped"],
  "exemptPaths": [{"path": "^docs/exempt/", "except": "keep\\.md$"}],
  "voiceWords": ["leverage", "delve"]
}
JSON

run() { out="$("$SCRIPT" --config "$repo/cfg.json" "$@" 2>&1)"; rc=$?; }
scan() { # file contents -> run on that file
  printf '%s\n' "$2" >"$repo/$1"
  run "$1"
}

# --- config failures
out="$("$SCRIPT" 2>&1)"; rc=$?
check "no config exits 64" 64 "$rc"
contains "no config says so" "--config <file> is required" "$out"
out="$("$SCRIPT" --config "$tmp/absent.json" 2>&1)"; rc=$?
check "absent config exits 64" 64 "$rc"
printf '[1]' >"$tmp/arr.json"
out="$("$SCRIPT" --config "$tmp/arr.json" 2>&1)"; rc=$?
check "non-object config outside a repo exits 2" 2 "$rc"
printf '[1]' >"$repo/arr.json"
out="$("$SCRIPT" --config "$repo/arr.json" 2>&1)"; rc=$?
check "non-object config exits 2" 2 "$rc"
contains "non-object config message" "not a JSON object" "$out"
rm "$repo/arr.json"
printf '{}' >"$repo/noterms.json"
out="$("$SCRIPT" --config "$repo/noterms.json" 2>&1)"; rc=$?
check "config with no terms table exits 2" 2 "$rc"
contains "no terms table message" "names no terms table" "$out"
rm "$repo/noterms.json"

# --- main path: clean and each scan
scan a.md "The worker opens the report."
check "clean exits 0" 0 "$rc"
contains "clean reports count" "clean (1 file(s))" "$out"

scan a.md $'fine line\nsee issue #42 for details'
check "reference hit exits 1" 1 "$rc"
contains "reference hit names path:line" "[reference] a.md:2:see issue #42" "$out"
contains "reference summary" "1 line(s) name a record" "$out"
contains "guide printed" "See docs/guide.md." "$out"
scan a.md "uses secrettool here"
check "case-sensitive ban ignores other case" 0 "$rc"
scan a.md "uses SecretTool here"
check "case-sensitive ban hits" 1 "$rc"

scan a.md "the helper was removed last week"
check "history hit exits 1" 1 "$rc"
contains "history label" "[history]" "$out"
scan a.md "the worker was removed from the case"
check "history needs code vocabulary" 0 "$rc"

scan a.md "we leverage the grid"
check "voice hit exits 1" 1 "$rc"
contains "voice label" "[voice]" "$out"
scan a.md "the behaviour is odd"
check "spelling hit exits 1" 1 "$rc"
contains "spelling label" "[spelling]" "$out"
scan a.md "the behavior is fine and authorIsWorker is a method"
check "american spelling and camel case clean" 0 "$rc"

# --- escapes
scan a.md "issue #7 and keepme-12"
contains "ban still hit beside kept id" "a.md:1:" "$out"
scan a.md "see keepme-12"
check "kept identifier passes" 0 "$rc"
scan a.md "quote: issue #9 VERBATIM"
check "verbatim marker passes the line" 0 "$rc"
scan a.md "trackerword here"
check "tracker-scope row does not apply to files" 0 "$rc"

scan a.md $'### TS-AB-01 We leverage things\nit(`we leverage the grid`, () => {})'
check "voice skips test titles" 0 "$rc"
printf '%s\n' 'prose' '```' 'we leverage this output' '```' >a.md
run a.md
check "voice skips fenced blocks" 0 "$rc"
printf '%s\n' '```' 'issue #5 in a fence' '```' >a.md
run a.md
check "reference still read inside fences" 1 "$rc"
scan a.md "“We leverage the screen”"
check "voice skips typographic-quote lines" 0 "$rc"

# glob-scoped rows
scan gen/g.md "globword"
check "glob row applies to matching path" 1 "$rc"
scan a.md "globword"
check "glob row skips other paths" 0 "$rc"

# skip, exempt, converted documents
scan gen/skipped.md "issue #1"
check "skipPaths leaves file alone" 0 "$rc"
mkdir -p docs/exempt
printf 'issue #1\n' >docs/exempt/x.md
printf 'issue #1\n' >docs/exempt/keep.md
run docs/exempt/x.md
check "exempt path left alone" 0 "$rc"
run docs/exempt/keep.md
check "exempt path's exception is scanned" 1 "$rc"

printf 'issue #1\n' >conv.md
: >conv.docx
run conv.md
check "markdown beside its docx is skipped" 0 "$rc"
printf '%s\n' '**Document provenance**' '' '- Source: `x.docx`' 'issue #1' >prov.md
run prov.md
check "provenance block marks converted document" 0 "$rc"
printf '%s\n' '- Source: `x.docx`' 'issue #1' >half.md
run half.md
check "source line alone is not converted" 1 "$rc"
rm -f conv.md conv.docx prov.md half.md

# --- bad terms table
cp terms.tsv terms.good
printf 'bogus\tall\tx\n' >terms.tsv
scan a.md "hello"
check "unknown term kind exits 2" 2 "$rc"
contains "unknown kind named" "unknown kind 'bogus'" "$out"
printf 'ban\tall\t(?i)x\n' >terms.tsv
run a.md
check "pattern outside subset exits 2" 2 "$rc"
mv terms.good terms.tsv

# --- default: files changed on the branch
rm -f a.md gen/g.md
rm -rf docs/exempt
git add -A && git commit -q -m base
run
contains "nothing changed" "nothing to scan" "$out"
check "nothing to scan exits 0" 0 "$rc"

git checkout -q -b topic
printf 'issue #3 committed\n' >c.md
git add c.md && git commit -q -m c
printf 'issue #4 untracked\n' >u.md
printf 'issue #5 not shipping\n' >tools/n.md
printf 'issue #6 wrong ext\n' >w.sh
run
check "changed files scanned exits 1" 1 "$rc"
contains "committed file scanned" "c.md:1:" "$out"
contains "untracked file scanned" "u.md:1:" "$out"
lacks "notShipping excluded" "tools/n.md" "$out"
lacks "non-shipping extension excluded" "w.sh" "$out"
rm -f u.md tools/n.md w.sh
git rm -q c.md && git commit -q -m rm
run
check "clean branch exits 0" 0 "$rc"

exit "$fail"
