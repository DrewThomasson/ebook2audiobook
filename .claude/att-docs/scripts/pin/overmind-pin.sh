#!/usr/bin/env bash
# Move the Overmind pin in consumer repositories to a tag, one pull request each.
#
# usage: overmind-pin.sh <vMAJOR.MINOR.PATCH> <consumer>...
#
# A consumer is a repository name without its owner. For each one the script clones the
# default branch, runs the sync script from this checkout against the tag, runs the check
# script on the result, writes the notes from the tag's changelog, commits the move to the
# branch overmind/pin-<tag>, pushes it, and opens a pull request unless one is already open
# for that branch. A consumer that fails does not stop the others, and its result line
# carries the failing script's output; the exit status is 1 if any failed, and 2 for a bad
# argument.
#
# Rerunning for the same tag adds nothing when the branch already holds the move. A branch
# that holds other commits keeps them: the move goes on top and the push is never forced.
# Pull requests for older tags are not touched, and nothing is merged.
#
#   OVERMIND_DIR     a checkout of this repository with its tags; default: the one this
#                    script lives in. The sync, check and notes scripts are read from its
#                    working tree, which may be newer than the tag, so an old tag can be
#                    pinned with today's scripts. The tag itself is fetched from it, and the
#                    changelog is read from the tag, never from the consumer.
#   PIN_OWNER        owner of the consumers; default merph518
#   PIN_CLONE_BASE   where consumers are cloned from; default https://github.com
#   GH_TOKEN         a token with contents and pull request write access to the consumers;
#                    used for the clone and push as well as for gh
#   GITHUB_STEP_SUMMARY  when set, one result line per consumer is appended to it
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERMIND_DIR="${OVERMIND_DIR:-$(cd "$HERE/../.." && pwd)}"
PIN_OWNER="${PIN_OWNER:-merph518}"
PIN_CLONE_BASE="${PIN_CLONE_BASE:-https://github.com}"
TAG_PATTERN='^v[0-9]+\.[0-9]+\.[0-9]+$'

# usage: fail_with <headline> <output>; prints the output, then one last line holding the
# headline and the output squeezed to a single line, which is what the run summary shows.
fail_with() {
  local squeezed
  [ -z "$2" ] || printf '%s\n' "$2" >&2
  squeezed="$(printf '%s' "$2" | tr '\n\r\t' '   ' | tr -s ' ' | cut -c1-300)"
  echo "$1: $squeezed" >&2
}

# usage: pin_one <tag> <consumer>; prints one result line on success.
pin_one() {
  set -euo pipefail
  local tag="$1" name="$2" work
  work="$(mktemp -d)"
  # Expanded now: $work is local, so it is out of scope when the trap runs at exit, and
  # under set -u the unbound name would turn a success into exit status 1.
  trap "rm -rf '$work'" EXIT

  if [ -n "${GH_TOKEN:-}" ]; then
    # The header goes through the environment, never the command line.
    local basic
    basic="$(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
    export GIT_CONFIG_COUNT=1
    export GIT_CONFIG_KEY_0="http.https://github.com/.extraheader"
    export GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $basic"
  fi
  export GIT_TERMINAL_PROMPT=0

  git clone -q -- "$PIN_CLONE_BASE/$PIN_OWNER/$name.git" "$work/c"
  cd "$work/c"
  # Always the bot, whatever identity the runner's own git configuration holds.
  git config user.name "overmind-automation[bot]"
  git config user.email "overmind-automation[bot]@users.noreply.github.com"

  local default
  default="$(git symbolic-ref --short HEAD)"
  if [ ! -f .claude/att-docs.lock ]; then
    echo "no .claude/att-docs.lock on $default" >&2
    return 1
  fi
  local pinned repo
  pinned="$(sed -n 's/^tag=//p' .claude/att-docs.lock | head -n 1 | tr -d '\r')"
  repo="$(sed -n 's/^repo=//p' .claude/att-docs.lock | head -n 1 | tr -d '\r')"
  if ! [[ "$pinned" =~ $TAG_PATTERN ]]; then
    echo "the pinned tag '$pinned' is not vMAJOR.MINOR.PATCH" >&2
    return 1
  fi
  if [ "$pinned" = "$tag" ]; then
    echo "unchanged: already on $tag"
    return 0
  fi
  if [ "$(printf '%s\n%s\n' "$pinned" "$tag" | sort -V | tail -n 1)" = "$pinned" ]; then
    echo "unchanged: already on $pinned, which is newer"
    return 0
  fi

  local branch="overmind/pin-$tag" title="chore: Move the Overmind pin to $tag"
  # The full ref names exactly this branch; a bare name would also match a branch that
  # only ends in it, such as topic/overmind/pin-<tag>. Exit status 2 is "no such branch";
  # any other failure is a failed lookup, never a reason to start a fresh branch.
  local lookup=0
  git ls-remote --exit-code --heads origin "refs/heads/$branch" > /dev/null 2>&1 || lookup=$?
  if [ "$lookup" -eq 0 ]; then
    git fetch -q origin "refs/heads/$branch"
    git checkout -q -B "$branch" FETCH_HEAD
  elif [ "$lookup" -eq 2 ]; then
    git checkout -q -b "$branch"
  else
    echo "could not look up $branch on origin (git ls-remote exit status $lookup)" >&2
    return 1
  fi

  # The scripts come from this checkout, which also serves the tag, so no consumer
  # wrapper runs and the source repository needs no read credential here.
  # Their output is kept: on a failure it is the diagnostic, and the last line, which
  # the summary shows, carries it too.
  local step_out
  if ! step_out="$(ATT_DOCS_URL="$OVERMIND_DIR" bash "$OVERMIND_DIR/scripts/consumer/overmind-sync.sh" "$tag" 2>&1)"; then
    fail_with "overmind-sync.sh failed" "$step_out"
    return 1
  fi
  if ! step_out="$(ATT_DOCS_URL="$OVERMIND_DIR" ATT_DOCS_REMOTE=require ATT_DOCS_BASE="$(git merge-base HEAD "origin/$default")" \
    bash "$OVERMIND_DIR/scripts/consumer/overmind-check.sh" 2>&1)"; then
    fail_with "overmind-check.sh failed" "$step_out"
    return 1
  fi

  # The notes come before the commit and push, so a missing changelog fails the consumer
  # with nothing pushed. The tag's changelog lists the entries up to the tag, whatever
  # the checkout holds. A changelog that cannot be read is a failure, never "no entries".
  if ! git -C "$OVERMIND_DIR" show "refs/tags/$tag:CHANGELOG.md" > "$work/changelog.md" 2> "$work/changelog.err"; then
    fail_with "could not read CHANGELOG.md at $tag" "$(cat "$work/changelog.err")"
    return 1
  fi
  if ! step_out="$(python3 -I "$OVERMIND_DIR/scripts/pin/pin_notes.py" --changelog "$work/changelog.md" \
    --from "$pinned" --to "$tag" --repo "$repo" 2>&1 > "$work/body.md")"; then
    fail_with "could not write the pull request notes" "$step_out"
    return 1
  fi

  if ! git diff --cached --quiet; then
    git commit -q -m "$title"
  fi
  if [ "$(git rev-parse HEAD)" != "$(git rev-parse -q --verify "origin/$branch" || true)" ]; then
    git push -q origin "HEAD:refs/heads/$branch"
  fi

  local slug="$PIN_OWNER/$name" existing
  existing="$(gh pr list --repo "$slug" --head "$branch" --state open --json number --jq '.[0].number // empty')"
  if [ -n "$existing" ]; then
    echo "branch $branch is current; pull request #$existing is already open"
    return 0
  fi
  local url
  url="$(gh pr create --repo "$slug" --base "$default" --head "$branch" --title "$title" --body-file "$work/body.md")"
  echo "opened $url"
}

main() {
  if [ "${1:-}" = "--one" ]; then
    shift
    pin_one "$@"
    exit $?
  fi
  if [ "$#" -lt 2 ]; then
    echo "usage: overmind-pin.sh <vMAJOR.MINOR.PATCH> <consumer>..." >&2
    exit 2
  fi
  local tag="$1" name out rc failed=0
  shift
  if ! [[ "$tag" =~ $TAG_PATTERN ]]; then
    echo "refusing tag '$tag': expected vMAJOR.MINOR.PATCH" >&2
    exit 2
  fi
  for name in "$@"; do
    if ! [[ "$name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || [[ "$name" == *..* ]]; then
      echo "refusing consumer '$name': expected a repository name without its owner" >&2
      exit 2
    fi
  done
  for name in "$@"; do
    rc=0
    out="$(bash "${BASH_SOURCE[0]}" --one "$tag" "$name" 2>&1)" || rc=$?
    printf '%s\n' "$out" | sed "s/^/$name: /"
    if [ "$rc" -eq 0 ]; then
      line="$name: $(printf '%s\n' "$out" | tail -n 1)"
    else
      line="$name: failed: $(printf '%s\n' "$out" | tail -n 1)"
      failed=1
    fi
    if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then printf -- '- %s\n' "$line" >> "$GITHUB_STEP_SUMMARY"; fi
  done
  exit "$failed"
}

main "$@"
