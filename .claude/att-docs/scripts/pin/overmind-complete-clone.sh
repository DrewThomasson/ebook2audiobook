#!/usr/bin/env bash
# Make a checkout of this repository able to serve every object of its history.
#
# usage: overmind-complete-clone.sh [<directory>]
#
# The exit status is 0 when the checkout is complete, the fetch failure's status when it
# fails, and 2 for a bad argument. The directory defaults to the current one.
#
# A sparse checkout, which some workflows make on a reused runner workspace, clones
# without file contents and marks the workspace as a partial clone. A partial clone
# cannot serve the contents it lacks, so a consumer whose history needs one fails with
# "bad pack header". This script drops the mark and fetches every object from origin. A
# checkout that is not a partial clone is left as it is, with no network access.
#
#   GH_TOKEN   a token that can read origin on github.com; optional. It reaches git
#              through the environment for the one fetch, and nothing is written to the
#              repository's configuration.
set -euo pipefail

if [ "$#" -gt 1 ]; then
  echo "usage: overmind-complete-clone.sh [<directory>]" >&2
  exit 2
fi
dir="${1:-.}"

if [ "$(git -C "$dir" config --get remote.origin.promisor || true)" != true ]; then
  echo "skipped: full checkout"
  exit 0
fi

if [ -n "${GH_TOKEN:-}" ]; then
  basic="$(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
  export GIT_CONFIG_COUNT=1
  export GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
  export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $basic"
fi
export GIT_TERMINAL_PROMPT=0

filter="$(git -C "$dir" config --get remote.origin.partialclonefilter || true)"

# usage: restore_mark; puts the partial clone mark back. Safe to run twice.
restore_mark() {
  # A second signal must not cut the restore short.
  trap '' INT TERM HUP
  git -C "$dir" config remote.origin.promisor true
  if [ -n "$filter" ]; then git -C "$dir" config remote.origin.partialclonefilter "$filter"; fi
}

# The mark is dropped before the fetch: --refetch of a partial clone fetches with the
# filter the clone was made with, which would leave the same objects missing. A fetch
# that fails or is interrupted puts the mark back, so a later run still sees a partial
# clone and tries again.
#
# Each signal handler restores the mark itself, then exits. A signal can land while the
# exit trap is restoring, before restore_mark has ignored signals. Its handler then runs
# inside the trap, and the handler's exit ends the trap, so the handler has to restore
# the mark before it exits.
trap 'restore_mark' EXIT
trap 'restore_mark; exit 130' INT
trap 'restore_mark; exit 143' TERM
trap 'restore_mark; exit 129' HUP
git -C "$dir" config --unset remote.origin.partialclonefilter || true
git -C "$dir" config --unset remote.origin.promisor
git -C "$dir" fetch --quiet --refetch --no-tags origin
trap - EXIT INT TERM HUP
echo "completed: fetched every object"
