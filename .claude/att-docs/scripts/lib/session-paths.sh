#!/usr/bin/env bash
# Paths the session scripts share. Sourced, never run.
# usage: . "$(dirname "$0")/lib/session-paths.sh"

# The clone does not always sit under $HOME, so the main checkout is read from
# git rather than assembled from a constant. --git-common-dir names the main
# checkout's .git from inside a worktree as well as from the checkout itself,
# and it can answer with a path relative to the directory asked about, so the
# answer is resolved by cd rather than by string handling.
session_main_checkout() {
  local from="$1" common
  common="$(git -C "$from" rev-parse --git-common-dir 2>/dev/null)" || return 1
  [ -n "$common" ] || return 1
  (cd "$from" && cd "$common" && cd .. && pwd)
}
