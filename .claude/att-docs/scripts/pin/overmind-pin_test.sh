#!/usr/bin/env bash
# Cases for overmind-pin.sh. A local git repository stands in for this repository's
# checkout at the new tag, bare repositories stand in for the consumers' remotes, and a
# stub gh records the pull request calls, so nothing touches the network.
# usage: bash overmind-pin_test.sh
set -uo pipefail

for bin in git python3; do
  command -v "$bin" > /dev/null || { echo "$bin is required"; exit 1; }
done

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

export HOME="$SANDBOX/home"
mkdir -p "$HOME"
export GIT_CONFIG_GLOBAL="$SANDBOX/gitconfig"
git config --global user.name tester
git config --global user.email tester@example.com
git config --global init.defaultBranch main
unset ATT_DOCS_REPO ATT_DOCS_URL ATT_DOCS_PREFIX ATT_DOCS_PATHS ATT_DOCS_LOCK ATT_DOCS_BASE ATT_DOCS_REMOTE GH_TOKEN

fails=0
check() {
  if [ "$1" = "$2" ]; then echo "ok   $3"; else
    echo "FAIL $3: got [$1], wanted [$2]"; fails=$((fails + 1)); fi
}

# usage: has <text> <needle> <name>; passes when the text holds the needle. On a failure
# the text follows, each line marked FAIL, so output filtered down to its FAIL lines still
# shows the text the needle was looked for in.
has() {
  case "$1" in
    *"$2"*) echo "ok   $3" ;;
    *)
      echo "FAIL $3: [$2] is not in:"
      printf '%s\n' "$1" | sed 's/^/FAIL   /'
      fails=$((fails + 1))
      ;;
  esac
}

# The upstream carries the scripts under test and a changelog, as the real repository does.
UP="$SANDBOX/upstream"
git init -q "$UP"
mkdir -p "$UP/scripts/consumer" "$UP/scripts/pin" "$UP/plugins/general"
cp "$REPO_ROOT"/scripts/consumer/overmind-sync.sh "$REPO_ROOT"/scripts/consumer/overmind-check.sh \
  "$REPO_ROOT"/scripts/consumer/overmind-lock-convert.sh "$UP/scripts/consumer/"
cp "$HERE"/pin_notes.py "$UP/scripts/pin/"
echo one > "$UP/plugins/general/a.md"
git -C "$UP" add -A && git -C "$UP" commit -q -m one && git -C "$UP" tag v0.1.0
echo two > "$UP/plugins/general/a.md"
git -C "$UP" add -A && git -C "$UP" commit -q -m two && git -C "$UP" tag v0.1.1
echo three > "$UP/plugins/general/a.md"
cat > "$UP/CHANGELOG.md" << 'CHANGELOG'
# Changelog

## [0.2.0](https://github.com/acme/skills/compare/v0.1.1...v0.2.0) (2026-03-01)


### Features

* move the extension folder ([#30](https://github.com/acme/skills/issues/30)) ([abc1234](https://github.com/acme/skills/commit/abc1234))
* open a pull request for each consumer ([#31](https://github.com/acme/skills/issues/31))

## [0.1.1](https://github.com/acme/skills/compare/v0.1.0...v0.1.1) (2026-02-01)


### Bug Fixes

* stop the sync from dropping a file ([#20](https://github.com/acme/skills/issues/20)) ([def5678](https://github.com/acme/skills/commit/def5678))
CHANGELOG
git -C "$UP" add -A && git -C "$UP" commit -q -m three && git -C "$UP" tag v0.2.0
UP_V020="$(git -C "$UP" rev-parse v0.2.0)"

REMOTES="$SANDBOX/remotes"
mkdir -p "$REMOTES/merph518"

# usage: make_consumer <name> <tag>; a consumer repository pinned to the tag, with its
# bare remote under $REMOTES/merph518/<name>.git.
make_consumer() {
  local w="$SANDBOX/work/$1"
  git init -q "$w"
  echo hello > "$w/README.md"
  git -C "$w" add -A && git -C "$w" commit -q -m init
  (cd "$w" && ATT_DOCS_REPO=acme/skills ATT_DOCS_URL="$UP" bash "$UP/scripts/consumer/overmind-sync.sh" "$2" > /dev/null) || exit 1
  git -C "$w" commit -q -m "vendor $2"
  git clone -q --bare "$w" "$REMOTES/merph518/$1.git"
}

# The stub answers `pr list` from a file per consumer and records every call.
export GH_LOG="$SANDBOX/gh.log"
export GH_STATE="$SANDBOX/gh-state"
mkdir -p "$GH_STATE" "$SANDBOX/bin"
: > "$GH_LOG"
cat > "$SANDBOX/bin/gh" << 'STUB'
#!/usr/bin/env bash
echo "$*" >> "$GH_LOG"
repo="" head="" title="" bodyfile=""
args=("$@")
for ((i = 0; i < ${#args[@]}; i++)); do
  case "${args[$i]}" in
    --repo) repo="${args[$((i + 1))]}" ;;
    --head) head="${args[$((i + 1))]}" ;;
    --title) title="${args[$((i + 1))]}" ;;
    --body-file) bodyfile="${args[$((i + 1))]}" ;;
  esac
done
key="$GH_STATE/open-$(printf '%s-%s' "$repo" "$head" | tr '/' '_')"
case "$1 $2" in
  "pr list") if [ -f "$key" ]; then cat "$key"; fi ;;
  "pr create")
    echo 7 > "$key"
    printf '%s' "$title" > "$key.title"
    cat "$bodyfile" > "$key.body"
    echo "https://github.com/$repo/pull/7"
    ;;
  *) echo "unexpected gh call: $*" >&2; exit 1 ;;
esac
STUB
chmod +x "$SANDBOX/bin/gh"
export PATH="$SANDBOX/bin:$PATH"

export OVERMIND_DIR="$UP"
export PIN_CLONE_BASE="$REMOTES"
export GITHUB_STEP_SUMMARY="$SANDBOX/summary.md"

pin() { bash "$HERE/overmind-pin.sh" "$@"; }
remote() { git --git-dir="$REMOTES/merph518/$1.git" "${@:2}"; }
pr_creates() { grep -c '^pr create' "$GH_LOG" || true; }
BRANCH=overmind/pin-v0.2.0
TITLE="chore: Move the Overmind pin to v0.2.0"

# Creation.
make_consumer alpha v0.1.0
pin v0.2.0 alpha > "$SANDBOX/out" 2>&1
check "$?" 0 "a pin move succeeds"
check "$(remote alpha show "$BRANCH:.claude/att-docs.lock" | sed -n 's/^tag=//p')" v0.2.0 "the branch holds the new tag"
check "$(remote alpha show "$BRANCH:.claude/att-docs.lock" | sed -n 's/^commit=//p')" "$UP_V020" "the branch holds the new commit"
check "$(remote alpha show "$BRANCH:.claude/att-docs/plugins/general/a.md")" three "the branch holds the new snapshot"
check "$(remote alpha log -1 --format=%s "$BRANCH")" "$TITLE" "the commit subject is the pin move"
check "$(remote alpha show main:.claude/att-docs.lock | sed -n 's/^tag=//p')" v0.1.0 "the default branch keeps its pin"
check "$(pr_creates)" 1 "one pull request is opened"
check "$(cat "$GH_STATE/open-merph518_alpha-overmind_pin-v0.2.0.title")" "$TITLE" "the pull request title is the pin move"
BODY="$(cat "$GH_STATE/open-merph518_alpha-overmind_pin-v0.2.0.body")"
case "$BODY" in *"stop the sync from dropping a file"*"move the extension folder"*|*"move the extension folder"*"stop the sync from dropping a file"*) r=yes ;; *) r=no ;; esac
check "$r" yes "the body lists the changelog since the pinned tag"
case "$BODY" in *"extension contract changed"*) r=yes ;; *) r=no ;; esac
check "$r" yes "the body notes the contract change when the minor version moved"
case "$BODY" in *"/issues/"*|*"/commit/"*) r=no ;; *) r=yes ;; esac
check "$r" yes "the body carries no issue or commit links"
case "$BODY" in *"http"*|*"releases/tag"*) r=no ;; *) r=yes ;; esac
check "$r" yes "the body links nothing, not even the release"
case "$BODY" in *"pull request for each consumer"*) r=no ;; *) r=yes ;; esac
check "$r" yes "the body leaves out an entry that names the tracker"
case "$BODY" in *"1 changelog entry is left out"*) r=yes ;; *) r=no ;; esac
check "$r" yes "the body says an entry was left out"
check "$(remote alpha log -1 --format='%an <%ae>' "$BRANCH")" "overmind-automation[bot] <overmind-automation[bot]@users.noreply.github.com>" "the commit author is the bot, not the runner's identity"
check "$(remote alpha log -1 --format='%cn' "$BRANCH")" "overmind-automation[bot]" "the committer is the bot"
check "$(grep -c 'alpha' "$GITHUB_STEP_SUMMARY")" 1 "the run summary has one line for the consumer"

# Rerun for the same tag.
TIP="$(remote alpha rev-parse "$BRANCH")"
pin v0.2.0 alpha > "$SANDBOX/out" 2>&1
check "$?" 0 "a rerun succeeds"
check "$(remote alpha rev-parse "$BRANCH")" "$TIP" "a rerun leaves the branch as it was"
check "$(pr_creates)" 1 "a rerun opens no second pull request"
check "$(remote alpha branch --list | wc -l)" 2 "a rerun adds no other branch"

# A human commit on the pin branch survives the rerun.
git clone -q "$REMOTES/merph518/alpha.git" "$SANDBOX/human"
(cd "$SANDBOX/human" && git checkout -q "$BRANCH" && echo note > notes.txt && git add notes.txt && git commit -q -m "human note" && git push -q origin "$BRANCH")
HUMAN="$(remote alpha rev-parse "$BRANCH")"
pin v0.2.0 alpha > "$SANDBOX/out" 2>&1
check "$?" 0 "a rerun after a human commit succeeds"
check "$(remote alpha rev-parse "$BRANCH")" "$HUMAN" "a rerun leaves a branch with a human commit as it was"
check "$(remote alpha show "$BRANCH:notes.txt")" note "the human commit's file is still there"

# A pin branch that has only a human commit gets the pin move on top of it.
make_consumer beta v0.1.0
remote beta branch "$BRANCH" main
git clone -q "$REMOTES/merph518/beta.git" "$SANDBOX/human-beta"
(cd "$SANDBOX/human-beta" && git checkout -q "$BRANCH" && echo note > notes.txt && git add notes.txt && git commit -q -m "human note" && git push -q origin "$BRANCH")
HUMAN="$(remote beta rev-parse "$BRANCH")"
pin v0.2.0 beta > "$SANDBOX/out" 2>&1
check "$?" 0 "a pin move onto a branch with a human commit succeeds"
check "$(remote beta merge-base --is-ancestor "$HUMAN" "$BRANCH" && echo yes)" yes "the human commit stays in the branch history"
check "$(remote beta show "$BRANCH:.claude/att-docs.lock" | sed -n 's/^tag=//p')" v0.2.0 "the pin move lands on top of it"
check "$(remote beta show "$BRANCH:notes.txt")" note "the human file is kept"

# An older pin branch and its pull request are left alone.
make_consumer gamma v0.1.0
(cd "$SANDBOX/work/gamma" && git remote add r "$REMOTES/merph518/gamma.git" && git push -q r main:overmind/pin-v0.1.1)
echo 5 > "$GH_STATE/open-merph518_gamma-overmind_pin-v0.1.1"
: > "$GH_LOG"
pin v0.2.0 gamma > "$SANDBOX/out" 2>&1
check "$?" 0 "a pin move beside an older pin branch succeeds"
check "$(grep -cE 'pr (close|edit|merge)|--delete-branch|--auto|--merge' "$GH_LOG" || true)" 0 "no pull request is closed, edited or merged"
check "$(remote gamma rev-parse --verify -q overmind/pin-v0.1.1 > /dev/null && echo yes)" yes "the older pin branch is kept"

# A consumer already on the tag, or ahead of it, gets nothing.
make_consumer delta v0.2.0
: > "$GH_LOG"
pin v0.2.0 delta > "$SANDBOX/out" 2>&1
check "$?" 0 "a consumer on the tag succeeds"
check "$(remote delta branch --list | wc -l)" 1 "a consumer on the tag gets no branch"
check "$(pr_creates)" 0 "a consumer on the tag gets no pull request"
make_consumer eps v0.2.0
pin v0.1.1 eps > "$SANDBOX/out" 2>&1
check "$?" 0 "a consumer ahead of the tag succeeds"
check "$(remote eps branch --list | wc -l)" 1 "a consumer ahead of the tag gets no branch"

# One consumer failing does not stop the others, and the run still fails.
make_consumer zeta v0.1.0
git init -q "$SANDBOX/work/nolock"
(cd "$SANDBOX/work/nolock" && echo x > f && git add f && git commit -q -m init)
git clone -q --bare "$SANDBOX/work/nolock" "$REMOTES/merph518/nolock.git"
: > "$GITHUB_STEP_SUMMARY"
pin v0.2.0 ghost nolock zeta > "$SANDBOX/out" 2>&1
check "$?" 1 "a run with a failing consumer fails"
check "$(remote zeta show "$BRANCH:.claude/att-docs.lock" | sed -n 's/^tag=//p')" v0.2.0 "a consumer after the failures is still pinned"
check "$(grep -c 'failed' "$GITHUB_STEP_SUMMARY")" 2 "the summary marks each failed consumer"
check "$(grep -c 'zeta' "$GITHUB_STEP_SUMMARY")" 1 "the summary lists the passing consumer"

# A tag that is not strict semver, or not in the checkout, is refused before any clone.
make_consumer eta v0.1.0
for bad in v0.2 0.2.0 v0.2.0-rc1 v0.2.0.1 'v0.2.0;x'; do
  pin "$bad" eta > "$SANDBOX/out" 2>&1
  check "$?" 2 "the tag '$bad' is refused"
done
check "$(remote eta branch --list | wc -l)" 1 "a refused tag leaves the consumer alone"
pin v0.9.9 eta > "$SANDBOX/out" 2>&1
check "$?" 1 "a tag missing from the checkout fails"
check "$(remote eta branch --list | wc -l)" 1 "a missing tag pushes nothing"
pin v0.2.0 '../etc' > "$SANDBOX/out" 2>&1
check "$?" 2 "a consumer name with a path is refused"

# A branch that only ends in the pin branch's name is not the pin branch.
make_consumer theta v0.1.0
(cd "$SANDBOX/work/theta" && git remote add r "$REMOTES/merph518/theta.git" && git push -q r "main:topic/$BRANCH")
pin v0.2.0 theta > "$SANDBOX/out" 2>&1
check "$?" 0 "a pin move beside a branch that merely ends in its name succeeds"
check "$(remote theta show "$BRANCH:.claude/att-docs.lock" | sed -n 's/^tag=//p')" v0.2.0 "the exact branch is created from the default branch"
check "$(remote theta rev-parse "topic/$BRANCH")" "$(remote theta rev-parse main)" "the branch that merely ends in the name is untouched"

# A failing check keeps its diagnostic in the log and in the summary. The upstream's
# working-tree copy of the check script is swapped for one that fails, then restored.
make_consumer iota v0.1.0
printf '#!/usr/bin/env bash\necho "att-docs: untracked files under .claude/att-docs"\necho "att-docs: forced failure"\nexit 1\n' > "$UP/scripts/consumer/overmind-check.sh"
: > "$GITHUB_STEP_SUMMARY"
pin v0.2.0 iota > "$SANDBOX/out" 2>&1
rc=$?
cp "$REPO_ROOT/scripts/consumer/overmind-check.sh" "$UP/scripts/consumer/overmind-check.sh"
check "$rc" 1 "a consumer whose check fails fails"
case "$(cat "$SANDBOX/out")" in *"iota: att-docs: untracked files under"*"iota: att-docs: forced failure"*"iota: overmind-check.sh failed: att-docs: untracked files"*) r=yes ;; *) r=no ;; esac
check "$r" yes "the log carries the check's diagnostic"
has "$(cat "$GITHUB_STEP_SUMMARY")" "iota: failed: overmind-check.sh failed: att-docs: untracked files under .claude/att-docs att-docs: forced failure" "the summary line carries the whole diagnostic"
check "$(remote iota branch --list | wc -l)" 1 "a failed check pushes nothing"

# A checkout that is a partial clone cannot serve the history it lacks, so the consumer
# fails with the git error in its log and nothing is pushed. The fetch, its relay of the
# server's messages, and the server each write lines of that error to the same stream,
# so their order varies from run to run, and the summary line keeps only the first 300
# characters. The checks hold for every order: the line that names the cause is looked
# for in the log, which has every line, and the summary line must open with whichever
# line came first. Completing the checkout lets the same pin succeed, and a rerun adds
# no second pull request. The server must allow filtered clones, or the clone comes out
# complete and proves nothing.
git -C "$UP" config uploadpack.allowFilter true
git -C "$UP" config uploadpack.allowAnySHA1InWant true
UPP="$SANDBOX/upstream-partial"
git clone -q --filter=blob:none "file://$UP" "$UPP" 2> /dev/null
check "$([ "$(git -C "$UPP" rev-list --objects --all --missing=print | grep -c '^?' || true)" -gt 0 ] && echo yes)" yes "the partial checkout lacks objects"
make_consumer lambda v0.1.0
: > "$GITHUB_STEP_SUMMARY"
: > "$GH_LOG"
OVERMIND_DIR="$UPP" pin v0.2.0 lambda > "$SANDBOX/out" 2>&1
check "$?" 1 "a pin from a partial checkout fails"
LOG="$(cat "$SANDBOX/out")"
has "$LOG" "promisor remote" "the log carries the git error"
FIRST="$(printf '%s\n' "$LOG" | sed -n -e '1s/^lambda: //' -e '1s/[[:space:]]*$//p')"
has "$(cat "$GITHUB_STEP_SUMMARY")" "- lambda: failed: overmind-sync.sh failed: $FIRST" "the summary line opens with the first line of the git error"
check "$(remote lambda branch --list | wc -l)" 1 "a pin from a partial checkout pushes nothing"
bash "$HERE/overmind-complete-clone.sh" "$UPP" > /dev/null 2>&1
check "$?" 0 "the partial checkout is completed"
OVERMIND_DIR="$UPP" pin v0.2.0 lambda > "$SANDBOX/out" 2>&1
check "$?" 0 "the same pin succeeds from the completed checkout"
check "$(remote lambda show "$BRANCH:.claude/att-docs.lock" | sed -n 's/^tag=//p')" v0.2.0 "the branch holds the new tag"
check "$(remote lambda show "$BRANCH:.claude/att-docs/plugins/general/a.md")" three "the branch holds the new snapshot"
check "$(pr_creates)" 1 "one pull request is opened"
OVERMIND_DIR="$UPP" pin v0.2.0 lambda > "$SANDBOX/out" 2>&1
check "$?" 0 "a rerun from the completed checkout succeeds"
check "$(pr_creates)" 1 "a rerun opens no second pull request"

# A tag whose changelog cannot be read fails the consumer before anything is pushed.
git -C "$UP" rm -q CHANGELOG.md
git -C "$UP" commit -q -m "drop the changelog"
git -C "$UP" tag v0.2.1
make_consumer kappa v0.1.0
: > "$GITHUB_STEP_SUMMARY"
pin v0.2.1 kappa > "$SANDBOX/out" 2>&1
check "$?" 1 "a tag with no changelog fails"
has "$(cat "$GITHUB_STEP_SUMMARY")" "kappa: failed: could not read CHANGELOG.md at v0.2.1" "the summary says the changelog could not be read"
check "$(remote kappa branch --list | wc -l)" 1 "a missing changelog pushes nothing"

if [ "$fails" -gt 0 ]; then echo "$fails failed"; exit 1; fi
echo "all passed"
