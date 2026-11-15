#!/usr/bin/env bash
# Lists every worktree of this repository with its branch, the state of its pull request,
# and whether it holds work that exists nowhere else, then offers to remove the ones that
# are done.
#
#   scripts/worktree-cleanup.sh            list, change nothing
#   scripts/worktree-cleanup.sh --remove   list, then ask about each removable worktree
#
# A worktree is removable when its pull request merged, it has no uncommitted or untracked
# file, every commit on it is at or below the head the pull request merged, and it is not
# the one the script runs from, locked, or missing. Anything else is kept, and the row says
# why. A pull request state the script cannot read (gh missing, not signed in, no network)
# is never a reason to remove.
#
# --remove asks `Remove <path>, with any files git ignores in it? [y/N]` for each removable
# worktree and reads the answer from standard input, so an empty input removes nothing. It
# checks the worktree again after the answer and removes with `git worktree remove` without
# --force, which git itself refuses for a worktree with changes. The branch stays. Files
# that git ignores, such as node_modules, go with the worktree, and the prompt says so.
#
# Needs git, gh and jq; column lines up the table when it is installed.
#
# Exit status: 0 after a listing or a removal run, 64 for a bad option or when run outside
# a git repository.
set -uo pipefail

remove=0
case "${1:-}" in
  '') ;;
  --remove) remove=1 ;;
  *) echo "usage: $0 [--remove]" >&2; exit 64 ;;
esac

main=$(git worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p')
if [ -z "$main" ]; then
  echo "$0: not inside a git repository" >&2
  exit 64
fi
here=$(git rev-parse --show-toplevel 2>/dev/null || true)

# Sets PR_STATE (MERGED, OPEN, CLOSED, NONE, or UNKNOWN) and PR_NUMBER and PR_HEAD from the
# pull requests whose head branch is $1. An open pull request outranks a merged one, since
# the branch is still in use.
read_pr() {
  PR_STATE=UNKNOWN PR_NUMBER='' PR_HEAD=''
  local json
  json=$(cd "$main" && gh pr list --head "$1" --state all --limit 20 \
    --json number,state,headRefOid,isCrossRepository 2>/dev/null) || return 0
  local pick
  pick=$(jq -r '
    map(select(.isCrossRepository == false))
    | (map(select(.state == "OPEN")) + map(select(.state == "MERGED")) + .)
    | first // empty | [.state, (.number | tostring), .headRefOid] | @tsv' <<<"$json" 2>/dev/null) \
    || return 0
  if [ -z "$pick" ]; then
    PR_STATE=NONE
    return 0
  fi
  IFS=$'\t' read -r PR_STATE PR_NUMBER PR_HEAD <<<"$pick"
}

# Sets DIRTY (changed and untracked paths, however git is configured to show them, or ?
# when git cannot tell) and UNPUSHED (commits that exist nowhere but in this worktree, or ?
# when that cannot be told) for the worktree at $1.
inspect() {
  local status
  if status=$(git -C "$1" status --porcelain --untracked-files=all --ignore-submodules=none 2>/dev/null); then
    DIRTY=$(printf '%s' "$status" | grep -c '^' || true)
  else
    DIRTY='?'
  fi
  local head
  head=$(git -C "$1" rev-parse HEAD 2>/dev/null) || { UNPUSHED='?'; return 0; }
  if [ -n "$PR_HEAD" ] && [ "$PR_STATE" = MERGED ]; then
    if [ "$head" = "$PR_HEAD" ] ||
      { git -C "$1" cat-file -e "$PR_HEAD^{commit}" 2>/dev/null &&
        git -C "$1" merge-base --is-ancestor "$head" "$PR_HEAD" 2>/dev/null; }; then
      UNPUSHED=0
    elif git -C "$1" cat-file -e "$PR_HEAD^{commit}" 2>/dev/null; then
      UNPUSHED=$(git -C "$1" rev-list --count "$PR_HEAD..$head" 2>/dev/null || echo '?')
    else
      UNPUSHED='?'
    fi
  else
    UNPUSHED=$(git -C "$1" rev-list --count "$head" --not --remotes 2>/dev/null || echo '?')
  fi
}

# Prints why the worktree is kept, or nothing when it can go. Reads the globals set above.
keep_reason() {
  local reasons=()
  [ "$IS_HERE" = 1 ] && reasons+=("this is where the script runs")
  [ "$LOCKED" = 1 ] && reasons+=("locked")
  [ "$MISSING" = 1 ] && reasons+=("directory missing, git worktree prune clears it")
  case "$PR_STATE" in
    MERGED) ;;
    OPEN) reasons+=("pull request open") ;;
    CLOSED) reasons+=("pull request closed without merging") ;;
    NONE) reasons+=("no pull request") ;;
    *) reasons+=("pull request state unknown") ;;
  esac
  [ "$MISSING" = 1 ] || {
    [ "$DIRTY" = '?' ] && reasons+=("uncommitted changes cannot be ruled out")
    [ "$DIRTY" != '?' ] && [ "$DIRTY" != 0 ] && reasons+=("$DIRTY uncommitted path(s)")
    [ "$UNPUSHED" = '?' ] && reasons+=("unpushed commits cannot be ruled out")
    [ "$UNPUSHED" != '?' ] && [ "$UNPUSHED" != 0 ] && reasons+=("$UNPUSHED unpushed commit(s)")
  }
  local IFS=';'
  echo "${reasons[*]:-}" | sed 's/;/; /g'
}

# Judges the worktree collected in path, branch, locked and missing, and adds its row to the
# table and, when it can go, to the removable list.
rows=()
removable=()
path='' branch='' locked=0 missing=0
flush() {
  [ -n "$path" ] || return 0
  if [ "$path" != "$main" ]; then
    IS_HERE=0 LOCKED=$locked MISSING=$missing
    [ "$path" = "$here" ] && IS_HERE=1
    name=${branch:-"(detached)"}
    PR_STATE=UNKNOWN PR_NUMBER='' PR_HEAD=''
    DIRTY=0 UNPUSHED=0
    if [ "$MISSING" = 0 ]; then
      [ -n "$branch" ] && read_pr "$branch"
      inspect "$path"
    fi
    reason=$(keep_reason)
    if [ -z "$reason" ]; then
      verdict=remove
      removable+=("$path")
    else
      verdict="keep: $reason"
    fi
    pr="$PR_STATE"
    [ -n "$PR_NUMBER" ] && pr="$PR_STATE #$PR_NUMBER"
    rows+=("${path#"$main"/}"$'\t'"$name"$'\t'"$pr"$'\t'"$DIRTY"$'\t'"$UNPUSHED"$'\t'"$verdict")
  fi
  path='' branch='' locked=0 missing=0
}

while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    "worktree "*) flush; path=${line#worktree } ;;
    "branch refs/heads/"*) branch=${line#branch refs/heads/} ;;
    locked*) locked=1 ;;
    prunable*) missing=1 ;;
  esac
done < <(git worktree list --porcelain)
flush

if [ "${#rows[@]}" -eq 0 ]; then
  echo "No worktrees besides the main checkout."
  exit 0
fi

{
  printf 'worktree\tbranch\tpull request\tuncommitted\tunpushed\tverdict\n'
  printf '%s\n' "${rows[@]}"
} | if command -v column >/dev/null; then column -t -s $'\t'; else tr '\t' ' '; fi

if [ "${#removable[@]}" -eq 0 ]; then
  echo
  echo "Nothing to remove."
  exit 0
fi
if [ "$remove" = 0 ]; then
  echo
  echo "${#removable[@]} worktree(s) can go. Run with --remove to be asked about each."
  exit 0
fi

echo
for dir in "${removable[@]}"; do
  printf 'Remove %s, with any files git ignores in it? [y/N] ' "$dir"
  answer=''
  read -r answer || answer=''
  echo
  case "$answer" in
    y | Y | yes) ;;
    *) echo "kept $dir"; continue ;;
  esac
  # The listing can be old by now: read the worktree again before deleting it.
  branch=$(git -C "$dir" symbolic-ref --quiet --short HEAD 2>/dev/null || true)
  PR_STATE=UNKNOWN PR_NUMBER='' PR_HEAD=''
  [ -n "$branch" ] && read_pr "$branch"
  inspect "$dir"
  IS_HERE=0 LOCKED=0 MISSING=0
  reason=$(keep_reason)
  if [ -n "$reason" ]; then
    echo "kept $dir: $reason"
    continue
  fi
  if git worktree remove "$dir"; then
    echo "removed $dir"
  else
    echo "kept $dir: git refused to remove it"
  fi
done
exit 0
