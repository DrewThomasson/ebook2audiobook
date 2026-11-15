#!/usr/bin/env bash
# Checks that the dictionary has a definition for every acronym the Markdown
# that ships uses. See the SKILL.md beside this file for the rules and the
# dictionary. The one thing it writes into the shipped documents is the
# rendered dictionary page, which carries the dictionary to the reader on the
# work side.
#
#   check-acronyms.sh --config <file> [--list | --verify | --write] [path...]
#
# With no paths it covers the files this branch changed that the config's
# "covered" pattern matches, including uncommitted ones. With paths it covers
# exactly the paths given. Either way a path matching "skipPaths" is left out.
# --list prints what each file uses, marking the undefined ones. Without it,
# only the undefined ones are reported. The paths are read from the top of the
# git work tree this runs in; config.py lists the config's keys.
#
# --verify is the other direction: it reads every row of the dictionary back
# against the file that row cites, and fails on any expansion that file does
# not state for that acronym.
#
# --write renders the dictionary into the page the config names, which is the
# one shipped file any of this writes. It is generated whole from the
# dictionary and the pending list, so a hand edit to it is undone by the next
# run.
#
# Exits 0 clean, 2 an acronym has no definition, 3 the rendered page is behind
# the dictionary, 64 an unknown option or no config. An acronym on the pending
# list, meaning a real short form nobody has found the words for, is reported
# and does not fail the run.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

config=''
if [ "${1:-}" = --config ] && [ "$#" -ge 2 ]; then
  config="$2"
  shift 2
fi
if [ -z "$config" ]; then
  echo "check-acronyms: --config <file> is required" >&2
  exit 64
fi
if [ ! -f "$config" ]; then
  echo "check-acronyms: the config $config does not exist" >&2
  exit 64
fi
config="$(cd "$(dirname "$config")" && pwd)/$(basename "$config")"
# The keys this script reads.
values="$(python3 "$HERE/config.py" --config "$config" get \
  skipPaths covered guide mainBranch terms)" || exit
mapfile -t values <<<"${values//$'\r'/}"
# Paths read rather than written, such as schema dumps.
SKIP_PATHS="${values[0]:-}"
COVERED="${values[1]:-}"
GUIDE="${values[2]:-}"
MAIN_BRANCH="${values[3]:-main}"
TERMS_NAME="${values[4]:-}"
TERMS_NAME="${TERMS_NAME##*/}"

cd "$(git rev-parse --show-toplevel)" || exit 1

mode=check
paths=()
for arg in "$@"; do
  case "$arg" in
    --list) mode=list ;;
    --verify) exec python3 "$HERE/verify-terms.py" --config "$config" ;;
    --write) exec python3 "$HERE/write-acronyms.py" --config "$config" ;;
    -*) echo "unknown option: $arg" >&2; exit 64 ;;
    *) paths+=("$arg") ;;
  esac
done

if [ "${#paths[@]}" -eq 0 ]; then
  base="$(git merge-base HEAD "origin/$MAIN_BRANCH" 2>/dev/null ||
    git merge-base HEAD "$MAIN_BRANCH")"
  exact='--find-renames=100% --diff-filter=ACMT'
  while IFS= read -r path; do
    [ -n "$path" ] && [ -f "$path" ] && paths+=("$path")
  done < <(
    {
      # A file moved without an edit brings no new text, so an exact rename is
      # left out; one moved and edited reads as added and is scanned.
      [ -n "$base" ] && git -c core.quotepath=off diff --name-only $exact "$base"...HEAD
      git -c core.quotepath=off diff --name-only $exact HEAD
      git -c core.quotepath=off ls-files --others --exclude-standard
    } | sort -u | grep -E -- "$COVERED"
  )
fi

files=()
for path in "${paths[@]}"; do
  [ -n "$SKIP_PATHS" ] && printf '%s' "$path" | grep -qE -- "$SKIP_PATHS" && continue
  files+=("$path")
done

# The shipped copy of the dictionary is generated, so it goes stale the moment
# a row is added. Every run says so, whether or not the branch touched a
# document.
python3 "$HERE/write-acronyms.py" --config "$config" --check
stale=$?

if [ "${#files[@]}" -eq 0 ]; then
  [ "$stale" -ne 0 ] && exit 3
  echo "check-acronyms: nothing to cover"
  exit 0
fi

# The paths go on stdin: a Windows runner caps a command line at 32767
# characters, which a branch touching a few hundred documents passes.
printf '%s\n' "${files[@]}" | python3 "$HERE/acronyms.py" --config "$config" "$mode" -
status=$?

if [ "$status" -eq 2 ]; then
  echo
  echo "An acronym above has no definition in $TERMS_NAME."
  echo "Find it in the documentation, add the row with its source, and rerun."
  [ -z "$GUIDE" ] || echo "See $GUIDE."
elif [ "$status" -eq 0 ] && [ "$stale" -eq 0 ] && [ "$mode" = check ]; then
  echo "check-acronyms: clean (${#files[@]} file(s))"
fi

[ "$status" -eq 0 ] && [ "$stale" -ne 0 ] && exit 3

exit "$status"
