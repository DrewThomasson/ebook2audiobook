#!/usr/bin/env bash
# Reads the banned-terms table for a grep or sed caller. Source it, run
# terms_use_config once with the skill's config (or set TERMS_FILE and
# TERMS_TRACKER yourself), then read_terms once, then select_terms for each
# scope set. select_terms fills three alternations:
#   TERMS_BAN     case-insensitive bans
#   TERMS_BAN_CS  case-sensitive bans
#   TERMS_KEEP    identifiers cut from a line before the bans are tested
# A scope argument is "all", the tracker scope, or a path a glob row has to
# match. The tracker scope names the rows that apply only to text sent to the
# work tracker.

TERMS_KINDS=() TERMS_SCOPES=() TERMS_PATTERNS=()

# Sets TERMS_FILE from the config's "terms" path, unless TERMS_FILE is already
# set, and TERMS_TRACKER from its "trackerScope". Returns non-zero when the
# config cannot be read.
terms_use_config() {
  # shellcheck source=config.sh
  . "$(dirname "${BASH_SOURCE[0]}")/config.sh"
  config_open terms.sh --config "$1" || return
  config_read terms trackerScope
  [ "${#CONFIG_VALUES[@]}" -eq 2 ] || return 2
  if [ -z "${CONFIG_VALUES[0]}" ]; then
    echo "terms.sh: the config $CONFIG_FILE names no terms table" >&2
    return 2
  fi
  TERMS_FILE="${TERMS_FILE:-$CONFIG_ROOT/${CONFIG_VALUES[0]}}"
  TERMS_TRACKER="${CONFIG_VALUES[1]}"
}

# Returns 1 and names the row when a pattern falls outside the shared subset,
# does not compile, or carries a kind the file does not define.
read_terms() {
  local kind scope pattern note lineno=0 label="${TERMS_FILE##*/}"
  TERMS_KINDS=() TERMS_SCOPES=() TERMS_PATTERNS=()
  while IFS=$'\t' read -r kind scope pattern note; do
    lineno=$((lineno + 1))
    case "$kind" in '' | '#'*) continue ;; esac
    case "$kind" in
      ban | ban-cs | keep) ;;
      *)
        echo "$label:$lineno: unknown kind '$kind'" >&2
        return 1
        ;;
    esac
    if [ -z "$scope" ] || [ -z "$pattern" ]; then
      echo "$label:$lineno: row needs a scope and a pattern" >&2
      return 1
    fi
    if grep -qE '\[\[:|\\d|(^|[^\\])\(\?' <<<"$pattern"; then
      echo "$label:$lineno: pattern outside the shared subset" >&2
      return 1
    fi
    grep -E -- "$pattern" </dev/null >/dev/null 2>&1
    if [ "$?" -eq 2 ]; then
      echo "$label:$lineno: pattern does not compile" >&2
      return 1
    fi
    TERMS_KINDS+=("$kind") TERMS_SCOPES+=("$scope") TERMS_PATTERNS+=("$pattern")
  done <"$TERMS_FILE"
  : "${note:=}"
  [ "${#TERMS_PATTERNS[@]}" -gt 0 ] || { echo "$label: no rows" >&2; return 1; }
}

# True when a scope is one of the two named scopes rather than a path glob.
terms_named_scope() {
  [ "$1" = all ] || { [ -n "${TERMS_TRACKER:-}" ] && [ "$1" = "$TERMS_TRACKER" ]; }
}

select_terms() {
  TERMS_BAN='' TERMS_BAN_CS='' TERMS_KEEP=''
  local i scope wanted applies group
  for i in "${!TERMS_PATTERNS[@]}"; do
    scope="${TERMS_SCOPES[$i]}"
    applies=0
    for wanted in "$@"; do
      if terms_named_scope "$scope"; then
        [ "$scope" = "$wanted" ] && applies=1
      # shellcheck disable=SC2053
      elif [[ "$wanted" == $scope ]]; then
        applies=1
      fi
    done
    [ "$applies" -eq 1 ] || continue
    group="(${TERMS_PATTERNS[$i]})"
    case "${TERMS_KINDS[$i]}" in
      ban) TERMS_BAN+="${TERMS_BAN:+|}$group" ;;
      ban-cs) TERMS_BAN_CS+="${TERMS_BAN_CS:+|}$group" ;;
      keep) TERMS_KEEP+="${TERMS_KEEP:+|}$group" ;;
    esac
  done
}

# True when some row is scoped to a path glob, so a caller has to select per
# file rather than once.
terms_have_globs() {
  local scope
  for scope in "${TERMS_SCOPES[@]}"; do
    terms_named_scope "$scope" || return 0
  done
  return 1
}

# Prints the text on stdin with the kept identifiers cut. The separator is a
# control character, so a slash inside a pattern needs no escaping.
cut_kept() {
  local sep=$'\001'
  if [ -z "$TERMS_KEEP" ]; then
    cat
  else
    sed -E "s${sep}${TERMS_KEEP}${sep}${sep}Ig"
  fi
}

# Prints the numbers of the stdin lines that carry a selected ban. Pipe the
# text through cut_kept first.
terms_hit_lines() {
  local text
  text="$(cat)"
  {
    [ -n "$TERMS_BAN" ] && grep -nIiE -- "$TERMS_BAN" <<<"$text" | cut -d: -f1
    [ -n "$TERMS_BAN_CS" ] && grep -nIE -- "$TERMS_BAN_CS" <<<"$text" | cut -d: -f1
  } | sort -nu
}

# terms_hit_lines over files: prints file:line for every line carrying a
# selected ban. The file names may not contain a colon. terms_hit_lines reads
# its input after the shell has dropped any NUL byte, so a caller wanting the
# same answer drops them from the files first.
terms_hit_files() {
  [ "$#" -gt 0 ] || return 0
  {
    [ -n "$TERMS_BAN" ] && grep -HnIiE -- "$TERMS_BAN" "$@" | cut -d: -f1,2
    [ -n "$TERMS_BAN_CS" ] && grep -HnIE -- "$TERMS_BAN_CS" "$@" | cut -d: -f1,2
  } | sort -u
}
