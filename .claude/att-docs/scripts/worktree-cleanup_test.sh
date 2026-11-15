#!/usr/bin/env bash
# Runs worktree-cleanup.sh against a scratch repository with one worktree per case and a stub
# gh that answers from files, so no real worktree, remote or pull request is touched.
# usage: bash scripts/worktree-cleanup_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
export HOME="$SANDBOX/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
mkdir -p "$HOME"

M="$SANDBOX/main"
REMOTE="$SANDBOX/remote.git"
PRS="$SANDBOX/prs"
mkdir -p "$M/scripts" "$SANDBOX/bin" "$PRS"
cp "$HERE/worktree-cleanup.sh" "$M/scripts/"
SCRIPT="$M/scripts/worktree-cleanup.sh"

# gh pr list --head <branch> ...: print the file for that branch, or fail when it holds FAIL.
cat >"$SANDBOX/bin/gh" <<'SH'
#!/usr/bin/env bash
branch=
while [ $# -gt 0 ]; do
  [ "$1" = --head ] && branch=$2
  shift
done
file="$PRS_DIR/${branch//\//_}.json"
[ -f "$file" ] || { echo '[]'; exit 0; }
grep -q FAIL "$file" && exit 1
cat "$file"
# A <branch>.then file replaces the answer after the first call.
[ -f "${file%.json}.then" ] && mv "${file%.json}.then" "$file"
exit 0
SH
chmod +x "$SANDBOX/bin/gh"
export PATH="$SANDBOX/bin:$PATH" PRS_DIR="$PRS"

git init -q --bare "$REMOTE"
git -C "$M" init -q -b main
git -C "$M" commit -q --allow-empty -m init
git -C "$M" remote add origin "$REMOTE"
git -C "$M" push -q origin main

fails=0
check() { # name expected actual
  if [ "$2" != "$3" ]; then
    echo "FAIL $1: expected [$2] got [$3]" >&2
    fails=$((fails + 1))
  else
    echo "ok   $1"
  fi
}
has() { # name needle haystack
  case "$3" in *"$2"*) echo "ok   $1" ;; *) echo "FAIL $1: [$2] not in [$3]" >&2; fails=$((fails + 1)) ;; esac
}

# usage: wt <branch>   a worktree under .claude/worktrees with one pushed commit
wt() {
  git -C "$M" worktree add -q -b "$1" "$M/.claude/worktrees/$1"
  git -C "$M/.claude/worktrees/$1" commit -q --allow-empty -m "work on $1"
  git -C "$M" push -q origin "$1"
}
head_of() { git -C "$M/.claude/worktrees/$1" rev-parse HEAD; }
# usage: pr <branch> <state> <number> [oid]
pr() {
  printf '[{"number":%s,"state":"%s","isCrossRepository":false,"headRefOid":"%s"}]\n' "$3" "$2" "${4:-$(head_of "$1")}" \
    >"$PRS/${1//\//_}.json"
}
row() { grep -E "^$1 " <<<"$out"; }
# A setting that hides untracked files from a plain `git status` must not hide them here.
git -C "$M" config status.showUntrackedFiles no

wt merged-clean;  pr merged-clean MERGED 11
wt merged-dirty;  pr merged-dirty MERGED 12
echo scratch >"$M/.claude/worktrees/merged-dirty/notes.txt"
wt merged-ahead;  pr merged-ahead MERGED 13
git -C "$M/.claude/worktrees/merged-ahead" commit -q --allow-empty -m "after the merge"
wt merged-then-open; pr merged-then-open MERGED 14
jq '. + [{"number":15,"state":"OPEN","isCrossRepository":false,"headRefOid":"abc"}]' "$PRS/merged-then-open.json" \
  >"$PRS/x" && mv "$PRS/x" "$PRS/merged-then-open.json"
wt still-open;    pr still-open OPEN 16
wt abandoned;     pr abandoned CLOSED 17
wt no-pr
wt offline;       echo FAIL >"$PRS/offline.json"
wt locked-one;    pr locked-one MERGED 18
git -C "$M" worktree lock "$M/.claude/worktrees/locked-one"
wt race;          pr race MERGED 21
printf '[{"number":21,"state":"OPEN","isCrossRepository":false,"headRefOid":"x"}]\n' >"$PRS/race.then"
wt feat/slashed;  pr feat/slashed MERGED 19
git -C "$M" worktree add -q --detach "$M/.claude/worktrees/loose"
wt forked;        printf '[{"number":22,"state":"MERGED","isCrossRepository":true,"headRefOid":"%s"}]\n' \
  "$(head_of forked)" >"$PRS/forked.json"
wt broken-index;  pr broken-index MERGED 23
echo garbage >"$(git -C "$M/.claude/worktrees/broken-index" rev-parse --absolute-git-dir)/index"

out="$(cd "$M" && "$SCRIPT" 2>&1 </dev/null)"; rc=$?
check "listing exits 0" 0 "$rc"
has "header names the columns" "pull request" "$out"
has "merged and clean can go" "merged-clean" "$(row .claude/worktrees/merged-clean)"
check "merged and clean verdict" 1 "$(row .claude/worktrees/merged-clean | grep -c 'remove$')"
has "merged row shows the pull request number" "MERGED #11" "$out"
has "uncommitted work keeps it" "1 uncommitted path(s)" "$(row .claude/worktrees/merged-dirty)"
has "a commit after the merge keeps it" "1 unpushed commit(s)" "$(row .claude/worktrees/merged-ahead)"
has "an open pull request wins over a merged one" "pull request open" "$(row .claude/worktrees/merged-then-open)"
has "open pull request keeps it" "pull request open" "$(row .claude/worktrees/still-open)"
has "closed pull request keeps it" "closed without merging" "$(row .claude/worktrees/abandoned)"
has "no pull request keeps it" "no pull request" "$(row .claude/worktrees/no-pr)"
has "an unreadable pull request state keeps it" "pull request state unknown" "$(row .claude/worktrees/offline)"
has "a merged pull request from a fork does not count" "no pull request" "$(row .claude/worktrees/forked)"
has "git status failing keeps it" "uncommitted changes cannot be ruled out" "$(row .claude/worktrees/broken-index)"
has "a locked worktree is kept" "locked" "$(row .claude/worktrees/locked-one)"
has "a detached worktree is listed" "(detached)" "$(row .claude/worktrees/loose)"
check "a branch with a slash can go" 1 "$(row .claude/worktrees/feat/slashed | grep -c 'remove$')"
has "listing offers --remove" "Run with --remove" "$out"
check "the listing removes nothing" yes "$([ -d "$M/.claude/worktrees/merged-clean" ] && echo yes || echo no)"

# --remove with no answer removes nothing.
exists() { [ -d "$M/.claude/worktrees/$1" ] && echo yes || echo no; }
out="$(cd "$M" && "$SCRIPT" --remove 2>&1 </dev/null)"
check "empty input keeps merged-clean" yes "$(exists merged-clean)"
has "empty input says kept" "kept $M/.claude/worktrees/merged-clean" "$out"
# The listing above used up the race answer; put it back for the run that removes.
printf '[{"number":21,"state":"MERGED","isCrossRepository":false,"headRefOid":"%s"}]\n' "$(head_of race)" >"$PRS/race.json"
printf '[{"number":21,"state":"OPEN","isCrossRepository":false,"headRefOid":"x"}]\n' >"$PRS/race.then"

out="$(cd "$M" && printf 'n\nn\nn\n' | "$SCRIPT" --remove 2>&1)"
check "no answers keep merged-clean" yes "$(exists merged-clean)"
check "no answers keep the slashed branch" yes "$(exists feat/slashed)"
printf '[{"number":21,"state":"MERGED","isCrossRepository":false,"headRefOid":"%s"}]\n' "$(head_of race)" >"$PRS/race.json"
printf '[{"number":21,"state":"OPEN","isCrossRepository":false,"headRefOid":"x"}]\n' >"$PRS/race.then"

# Yes to everything: the removable ones go, a worktree whose pull request reopened between the
# listing and the answer is kept, and nothing else is touched.
out="$(cd "$M" && printf 'y\ny\ny\ny\n' | "$SCRIPT" --remove 2>&1)"
check "merged-clean is removed" no "$(exists merged-clean)"
check "the slashed branch's worktree is removed" no "$(exists feat/slashed)"
has "removal is reported" "removed $M/.claude/worktrees/merged-clean" "$out"
check "a pull request that reopened keeps its worktree" yes "$(exists race)"
has "the recheck names the reason" "kept $M/.claude/worktrees/race: pull request open" "$out"
for d in merged-dirty merged-ahead merged-then-open still-open abandoned no-pr offline locked-one loose forked broken-index; do
  check "$d is untouched" yes "$(exists $d)"
done
check "the branch of a removed worktree stays" merged-clean \
  "$(git -C "$M" branch --list merged-clean --format '%(refname:short)')"

# Running from inside a worktree never removes that worktree.
wt inside; pr inside MERGED 20
out="$(cd "$M/.claude/worktrees/inside" && "$SCRIPT" 2>&1 </dev/null)"
has "the current worktree is kept" "this is where the script runs" "$(grep -E 'worktrees/inside ' <<<"$out")"
out="$(cd "$M/.claude/worktrees/inside" && printf 'y\ny\ny\n' | "$SCRIPT" --remove 2>&1)"
check "the current worktree stays after --remove" yes "$([ -d "$M/.claude/worktrees/inside" ] && echo yes || echo no)"

# A bad option exits 64.
"$SCRIPT" --bogus >/dev/null 2>&1
check "unknown option exits 64" 64 "$?"

# A repository with no other worktree.
SOLO="$SANDBOX/solo"
git init -q -b main "$SOLO"
git -C "$SOLO" commit -q --allow-empty -m init
out="$(cd "$SOLO" && "$SCRIPT" 2>&1)"
has "no worktrees says so" "No worktrees besides the main checkout" "$out"

if [ "$fails" -ne 0 ]; then
  echo "worktree-cleanup_test.sh: $fails failed" >&2
  exit 1
fi
echo "worktree-cleanup_test.sh: all passed"
