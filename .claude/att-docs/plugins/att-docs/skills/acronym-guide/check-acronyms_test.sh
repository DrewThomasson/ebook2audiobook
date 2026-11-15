#!/usr/bin/env bash
# usage: bash plugins/att-docs/skills/acronym-guide/check-acronyms_test.sh
# Tests check-acronyms.sh against a scratch git repository with its own config,
# dictionary, and rendered page, so no real documents are read or written.
set -u
here=$(dirname "$(readlink -f "$0")")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
fail=0
export HOME=$work/nohome
mkdir -p "$HOME"
export PYTHONDONTWRITEBYTECODE=1
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

script="$here/check-acronyms.sh"
repo=$work/repo
mkdir -p "$repo/docs"
cd "$repo" || exit 1
git init -q -b main .
printf '%s\n' '{"terms":"terms.tsv","ignore":"ignore.txt","unknown":"unknown.txt",' \
  '"page":"docs/Acronyms.md","docsRoot":"docs","covered":"^docs/.*\\.md$",' \
  '"skipPaths":"^docs/dump/","guide":"docs/Guide.md","mainBranch":"main"}' >extension.json
printf 'ABC\tAlpha Beta Charlie\t*\tdocs/a.md\n' >terms.tsv
printf 'NOISE\n' >ignore.txt
printf 'PEND\n' >unknown.txt
printf 'Alpha Beta Charlie (ABC) opens.\n' >docs/a.md
python3 "$here/write-acronyms.py" --config extension.json >/dev/null
git add -A && git commit -q -m base

# usage: check <name> <expected> <actual>
check() {
  if [[ $2 != "$3" ]]; then
    echo "FAIL $1: expected [$2] got [$3]" >&2
    fail=1
  fi
}
# usage: has <name> <needle> <haystack>
has() {
  if [[ $3 != *"$2"* ]]; then
    echo "FAIL $1: expected [$2] in [$3]" >&2
    fail=1
  fi
}
run() { out=$(bash "$script" --config extension.json "$@" 2>&1); code=$?; }

# Clean branch with nothing changed.
run
check "clean exit" 0 "$code"
has "clean message" "nothing to cover" "$out"

# Named path using a defined acronym.
printf 'The ABC step.\n' >docs/b.md
run docs/b.md
check "defined exit" 0 "$code"
has "defined message" "clean (1 file(s))" "$out"

# Undefined acronym fails with 2 and names file, line, word and the guide.
printf 'line one\nThe XYZ step.\n' >docs/c.md
run docs/c.md
check "undefined exit" 2 "$code"
has "undefined location" "docs/c.md:2" "$out"
has "undefined word" "XYZ" "$out"
has "undefined guide" "See docs/Guide.md." "$out"
has "undefined terms hint" "no definition in terms.tsv" "$out"

# Default scope picks up the untracked, changed file; unrelated files are left out.
run
check "untracked exit" 2 "$code"
has "untracked covered" "docs/c.md" "$out"
printf 'The QRS step.\n' >notes.txt
run
case $out in *QRS*) echo "FAIL uncovered file scanned: $out" >&2; fail=1 ;; esac
check "uncovered file: exit stays the undefined word's" 2 "$code"
has "uncovered file: undefined word still reported" "XYZ" "$out"

# Pending and ignored words pass; --list marks the undefined.
rm docs/c.md notes.txt
printf 'PEND and NOISE appear.\n' >docs/d.md
run docs/d.md
check "pending exit" 0 "$code"
run --list docs/b.md docs/d.md
check "list exit" 0 "$code"
has "list shows acronym" "ABC" "$out"
has "list shows pending" "PEND" "$out"

# skipPaths leaves a path out even when named.
mkdir -p docs/dump
printf 'The XYZ dump.\n' >docs/dump/e.md
run docs/dump/e.md
check "skip exit" 0 "$code"
has "skip message" "nothing to cover" "$out"
rm -r docs/dump docs/d.md docs/b.md

# A branch edit is covered, committed on a feature branch too.
git checkout -q -b feature
printf 'The QRS step.\n' >docs/f.md
git add -A && git commit -q -m feature
run
check "branch exit" 2 "$code"
has "branch file" "docs/f.md" "$out"
git rm -q docs/f.md && git commit -q -m drop

# A stale page exits 3 with and without documents; --write repairs it.
printf 'NEW\tNew Word\t*\tdocs/a.md\n' >>terms.tsv
run
check "stale exit" 3 "$code"
has "stale message" "does not match the dictionary" "$out"
run docs/a.md
check "stale with file exit" 3 "$code"
run --write
check "write exit" 0 "$code"
has "write message" "docs/Acronyms.md: written" "$out"
has "page has row" "| NEW | New Word |" "$(cat docs/Acronyms.md)"
run
check "after write exit" 0 "$code"

# --verify delegates to verify-terms: a row its source does not state fails.
run --verify
check "verify failing exit" 1 "$code"
has "verify names row" "NEW: docs/a.md does not state" "$out"
printf 'New Word (NEW) is stated.\n' >>docs/a.md
run --verify
check "verify exit" 0 "$code"
has "verify summary" "2 row(s) checked against their source, 0 failed." "$out"

# A row citing a file that is gone fails --verify and names the row and the path.
cp terms.tsv terms.keep
printf 'GONE\tGone Word\t*\tdocs/gone.md\n' >>terms.tsv
run --verify
check "verify missing source exit" 1 "$code"
has "verify names missing source" "GONE: docs/gone.md does not exist" "$out"
mv terms.keep terms.tsv

# Bad invocations exit 64.
out=$(bash "$script" docs/a.md 2>&1); check "no config exit" 64 $?
has "no config message" "--config <file> is required" "$out"
run_bad() { out=$(bash "$script" "$@" 2>&1); code=$?; }
run_bad --config "$work/missing.json"
check "missing config exit" 64 "$code"
has "missing config message" "does not exist" "$out"
run --bogus
check "unknown option exit" 64 "$code"
has "unknown option message" "unknown option: --bogus" "$out"

if [[ $fail -ne 0 ]]; then
  echo "check-acronyms_test.sh: FAILED" >&2
  exit 1
fi
echo "check-acronyms_test.sh: all passed"
