#!/usr/bin/env bash
# Cases for overmind-sync.sh, overmind-check.sh and overmind-lock-convert.sh. A local git
# repository stands in for the upstream skills repository and a second one for the
# consuming repository, so nothing touches the network.
# usage: bash overmind-consumer_test.sh
set -uo pipefail

for bin in git tar; do
  command -v "$bin" > /dev/null || { echo "$bin is required"; exit 1; }
done

HERE="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

export HOME="$SANDBOX/home"
mkdir -p "$HOME"
export GIT_CONFIG_GLOBAL="$SANDBOX/gitconfig"
git config --global user.name tester
git config --global user.email tester@example.com
git config --global init.defaultBranch main
unset ATT_DOCS_REPO ATT_DOCS_URL ATT_DOCS_PREFIX ATT_DOCS_PATHS ATT_DOCS_LOCK

UP="$SANDBOX/upstream"
fails=0

check() {
  if [ "$1" = "$2" ]; then echo "ok   $3"; else
    echo "FAIL $3: got [$1], wanted [$2]"; fails=$((fails + 1)); fi
}

# usage: expect_fail <label> <command...>; the command must exit non-zero.
expect_fail() {
  local label="$1"
  shift
  if "$@" > "$SANDBOX/out" 2>&1; then
    echo "FAIL $label: expected a failure"; fails=$((fails + 1))
  else echo "ok   $label"; fi
}

# The upstream carries the scripts under test, as the real repository does.
git init -q "$UP"
mkdir -p "$UP/scripts/consumer" "$UP/plugins/general" "$UP/plugins/voice/skills" "$UP/plugins/other"
cp "$HERE"/overmind-sync.sh "$HERE"/overmind-check.sh "$HERE"/overmind-lock-convert.sh \
  "$HERE"/wrapper-sync.sh.template "$HERE"/wrapper-check.sh.template "$UP/scripts/consumer/"
echo one > "$UP/plugins/general/a.md"
echo one > "$UP/plugins/voice/skills/v.md"
echo one > "$UP/plugins/other/o.md"
git -C "$UP" add -A && git -C "$UP" commit -q -m one && git -C "$UP" tag v1
echo two > "$UP/plugins/general/a.md"
echo new > "$UP/plugins/general/b.md"
git -C "$UP" add -A && git -C "$UP" commit -q -m two && git -C "$UP" tag v2
UP_V1="$(git -C "$UP" rev-parse v1)"
UP_V2="$(git -C "$UP" rev-parse v2)"
UP_V2_TREE="$(git -C "$UP" rev-parse 'v2^{tree}')"

# usage: new_consumer <name>; makes a repository with one commit and enters it.
new_consumer() {
  C="$SANDBOX/$1"
  git init -q "$C"
  cd "$C" || exit 1
  echo hello > README.md
  git add -A && git commit -q -m init
}
sync() { "$HERE/overmind-sync.sh" "$@"; }
check_pin() { "$HERE/overmind-check.sh"; }
lock_value() { sed -n "s/^$1=//p" "$C/.claude/att-docs.lock"; }

export ATT_DOCS_REPO=acme/skills
export ATT_DOCS_URL="$UP"

# First sync, from the upstream's own copy of the script, the way a consumer starts.
new_consumer first
bash "$UP/scripts/consumer/overmind-sync.sh" v1 > /dev/null
check "$(cat .claude/att-docs/plugins/general/a.md)" one "first sync copies the snapshot"
check "$(lock_value tag)" v1 "first sync records the tag"
check "$(lock_value commit)" "$UP_V1" "first sync records the commit"
check "$(lock_value repo)" acme/skills "first sync records the repository"
check "$(lock_value url)" "" "an upstream URL from the environment is not written to the lock"
check "$([ -x .claude/att-docs/scripts/consumer/overmind-sync.sh ] && echo yes)" yes \
  "the vendored sync script stays executable"
check "$(git status --porcelain | grep -c '^[AM]')" "$(git status --porcelain | wc -l)" \
  "first sync stages everything it writes"
printf 'url=%s\n' "$UP" >> .claude/att-docs.lock
git add -A
git commit -q -m vendor
check "$(check_pin | tail -n 1)" "att-docs: .claude/att-docs matches the pin v1" "check passes after a sync"

# The README's first-sync command pipes the script from the tag into bash.
new_consumer piped
git fetch -q --no-tags "$UP" refs/tags/v1
git show FETCH_HEAD:scripts/consumer/overmind-sync.sh | bash -s -- v1 > /dev/null
check "$(sed -n 's/^tag=//p' .claude/att-docs.lock)" v1 "a script piped into bash syncs"
C="$SANDBOX/first"
cd "$C" || exit 1

# Re-sync through the vendored copy with the pin moved, with no environment help.
unset ATT_DOCS_REPO ATT_DOCS_URL
.claude/att-docs/scripts/consumer/overmind-sync.sh v2 > /dev/null
check "$(cat .claude/att-docs/plugins/general/a.md)" two "re-sync moves to the new tag"
check "$(ls .claude/att-docs/plugins/general)" "$(printf 'a.md\nb.md')" "re-sync adds new files"
check "$(lock_value commit)" "$UP_V2" "re-sync records the new commit"
check "$(lock_value tree)" "$UP_V2_TREE" "re-sync records the new tree"
git commit -q -m move
check_pin > /dev/null && echo "ok   check passes after the pin moves" ||
  { echo "FAIL check after the pin moves"; fails=$((fails + 1)); }

# A removed upstream file leaves the vendored copy too.
git -C "$UP" rm -q plugins/general/b.md && git -C "$UP" commit -q -m drop && git -C "$UP" tag v3
UP_V3="$(git -C "$UP" rev-parse v3)"
.claude/att-docs/scripts/consumer/overmind-sync.sh v3 > /dev/null
check "$(ls .claude/att-docs/plugins/general)" a.md "re-sync removes files the tag dropped"
git commit -q -m drop

# The tag defaults to the lock's tag; a moved tag is refused.
.claude/att-docs/scripts/consumer/overmind-sync.sh > /dev/null
check "$(lock_value tag)" v3 "no argument re-syncs the pinned tag"
git -C "$UP" tag -f v3 v1 > /dev/null
expect_fail "a tag moved to another commit is refused" \
  .claude/att-docs/scripts/consumer/overmind-sync.sh v3
git -C "$UP" tag -f v3 "$UP_V3" > /dev/null

# Check failing: a hand edit, an untracked file, and a staged edit.
echo edited >> .claude/att-docs/plugins/general/a.md
expect_fail "check fails on an unstaged hand edit" check_pin
git add -A
expect_fail "check fails on a staged hand edit" check_pin
git reset -q --hard
check_pin > /dev/null && echo "ok   check passes after the edit is discarded" ||
  { echo "FAIL check after discarding the edit"; fails=$((fails + 1)); }
echo stray > .claude/att-docs/stray.md
expect_fail "check fails on an untracked file" check_pin
rm .claude/att-docs/stray.md
expect_fail "sync refuses uncommitted changes under the prefix" bash -c \
  "echo x >> .claude/att-docs/plugins/general/a.md; .claude/att-docs/scripts/consumer/overmind-sync.sh v2"
git checkout -q -- .claude/att-docs

# Missing lock.
new_consumer nolock
expect_fail "check fails with no lock" check_pin
check "$(grep -c 'no .claude/att-docs.lock' "$SANDBOX/out")" 1 "check names the missing lock"
expect_fail "sync with no tag and no lock fails" "$HERE/overmind-sync.sh"
expect_fail "sync with no repository fails" env -u ATT_DOCS_REPO "$HERE/overmind-sync.sh" v1

export ATT_DOCS_REPO=acme/skills
export ATT_DOCS_URL="$UP"

# Per-consumer values: a custom prefix and lock location, all from the environment,
# then read back from the lock alone.
new_consumer custom
ATT_DOCS_REPO=acme/skills ATT_DOCS_URL="$UP" ATT_DOCS_PREFIX=vendor/skills \
  ATT_DOCS_LOCK=vendor/skills.lock sync v1 > /dev/null
check "$(cat vendor/skills/plugins/general/a.md)" one "a custom prefix is honored"
check "$(sed -n 's/^prefix=//p' vendor/skills.lock)" vendor/skills "a custom prefix is recorded"
printf 'url=%s\n' "$UP" >> vendor/skills.lock
git add -A
git commit -q -m vendor
ATT_DOCS_LOCK=vendor/skills.lock check_pin > /dev/null && echo "ok   check reads the prefix from the lock" ||
  { echo "FAIL check with a custom prefix"; fails=$((fails + 1)); }
(unset ATT_DOCS_REPO ATT_DOCS_URL; ATT_DOCS_LOCK=vendor/skills.lock sync v2 > /dev/null)
check "$(cat vendor/skills/plugins/general/a.md)" two "re-sync reads repo, URL and prefix from the lock"
expect_fail "a prefix outside the repository is refused" env ATT_DOCS_PREFIX=../x "$HERE/overmind-sync.sh" v1

# A pruned copy keeps only the listed paths plus the scripts.
new_consumer pruned
ATT_DOCS_PATHS="plugins/general plugins/voice/skills" sync v1 > /dev/null
check "$(ls .claude/att-docs/plugins)" "$(printf 'general\nvoice')" "paths limits the copy"
check "$([ -f .claude/att-docs/scripts/consumer/overmind-check.sh ] && echo yes)" yes \
  "a pruned copy still carries the scripts"
check "$(lock_value paths)" "plugins/general plugins/voice/skills scripts/consumer" "paths is recorded"
git commit -q -m vendor
check_pin > /dev/null && echo "ok   check passes on a pruned copy" ||
  { echo "FAIL check on a pruned copy"; fails=$((fails + 1)); }
check "$([ "$(lock_value copy_tree)" != "$(lock_value tree)" ] && echo differ)" differ \
  "a pruned copy records its own tree"
.claude/att-docs/scripts/consumer/overmind-sync.sh v2 > /dev/null
check "$(cat .claude/att-docs/plugins/general/b.md)" new "a pruned re-sync reads paths from the lock"
git commit -q -m move
echo edited >> .claude/att-docs/plugins/general/a.md
expect_fail "check fails on a hand edit in a pruned copy" check_pin
git checkout -q -- .claude/att-docs

# Prefix guard: .git, a symlinked parent, and path forms that normalize.
new_consumer guard
expect_fail "a prefix of .git is refused" env ATT_DOCS_PREFIX=.git "$HERE/overmind-sync.sh" v1
expect_fail "a prefix under .git is refused" env ATT_DOCS_PREFIX=.git/hooks "$HERE/overmind-sync.sh" v1
expect_fail "a prefix of ./.git/ is refused" env ATT_DOCS_PREFIX=./.git/ "$HERE/overmind-sync.sh" v1
mkdir "$SANDBOX/outside"
ln -s "$SANDBOX/outside" linked
expect_fail "a symlinked parent outside the repository is refused" \
  env ATT_DOCS_PREFIX=linked/vend "$HERE/overmind-sync.sh" v1
check "$(ls "$SANDBOX/outside" | wc -l | tr -d ' ')" 0 "nothing is written through the symlink"
ATT_DOCS_PREFIX=./vend sync v1 > /dev/null
check "$(cat vend/plugins/general/a.md)" one "a leading ./ is normalized"
check "$(sed -n 's/^prefix=//p' .claude/att-docs.lock)" vend "the normalized prefix is recorded"
git add -A && git commit -q -m vend
ATT_DOCS_PREFIX=vend// sync v2 > /dev/null
check "$(cat vend/plugins/general/a.md)" two "repeated trailing slashes are normalized"
git add -A && git commit -q -m vend2

# Prefix guard: a .git component anywhere, and a link inside the repository to .git.
new_consumer gitguard
ln -s .git gl
expect_fail "a link into .git is refused" env ATT_DOCS_PREFIX=gl/hooks "$HERE/overmind-sync.sh" v1
check "$([ -d .git/hooks ] && echo kept)" kept "the git hooks folder survives a link attempt"
mkdir -p nested/.git/objects
expect_fail "a nested .git is refused" env ATT_DOCS_PREFIX=nested/.git "$HERE/overmind-sync.sh" v1
expect_fail "a folder under a nested .git is refused" env ATT_DOCS_PREFIX=nested/.git/objects "$HERE/overmind-sync.sh" v1
expect_fail "a nested .GIT is refused" env ATT_DOCS_PREFIX=nested/.GIT "$HERE/overmind-sync.sh" v1
check "$([ -d nested/.git/objects ] && echo kept)" kept "a nested .git survives"

# The check reads the prefix the way the sync does.
new_consumer normcheck
ATT_DOCS_PREFIX=vendor/om sync v1 > /dev/null
git commit -q -m vendor
ATT_DOCS_PREFIX=./vendor//om/ check_pin > /dev/null && echo "ok   check normalizes the prefix" ||
  { echo "FAIL check with an unnormalized prefix"; fails=$((fails + 1)); }

# Modes come from the tag, even when the consumer ignores file modes.
new_consumer nomode
git config core.fileMode false
ATT_DOCS_PATHS="plugins/general" sync v1 > /dev/null
check "$(git ls-files -s .claude/att-docs/scripts/consumer/overmind-sync.sh | cut -d' ' -f1)" 100755 \
  "a pruned copy keeps the executable mode with core.fileMode off"
check "$([ -x .claude/att-docs/scripts/consumer/overmind-sync.sh ] && echo yes)" yes \
  "a pruned copy is executable on disk"
check "$(stat -c %a .claude/att-docs | grep -c '^700$')" 0 "the vendored folder is not private to its owner"
git commit -q -m vendor
check_pin > /dev/null && echo "ok   check passes with core.fileMode off" ||
  { echo "FAIL check with core.fileMode off"; fails=$((fails + 1)); }

# A JSON lock is refused by the sync as it is by the check.
new_consumer jsonlock
mkdir -p .claude
printf '{"repo":"a/b","tag":"v1","commit":"%s","tree":"%s"}\n' "$UP_V1" "$UP_V2_TREE" > .claude/att-docs.lock
expect_fail "sync refuses a JSON lock" sync v1
check "$(grep -c overmind-lock-convert "$SANDBOX/out")" 1 "sync points at the converter"
check "$([ -d .claude/att-docs ] && echo made)" "" "a refused sync vendors nothing"

# A prefix that git would read as pathspec magic is refused and removes nothing.
new_consumer magic
tracked_before="$(git ls-files | wc -l | tr -d ' ')"
expect_fail "a prefix starting with a colon is refused" env 'ATT_DOCS_PREFIX=:!nothing' "$HERE/overmind-sync.sh" v1
check "$(git ls-files | wc -l | tr -d ' ')" "$tracked_before" "a magic prefix removes no tracked file"
check "$([ -f README.md ] && echo kept)" kept "a magic prefix leaves the working tree alone"

# Untracked files under the folder stop a sync even when status hides them.
new_consumer hidden
sync v1 > /dev/null
git commit -q -m vendor
git config status.showUntrackedFiles no
echo mine > .claude/att-docs/mine.md
expect_fail "sync refuses untracked files that status would hide" sync v2
check "$([ -f .claude/att-docs/mine.md ] && echo kept)" kept "the untracked file is not deleted"

# A failure after the old copy is removed puts the old copy back.
new_consumer restore
sync v1 > /dev/null
git commit -q -m vendor
REAL_GIT="$(command -v git)"
mkdir "$SANDBOX/fakebin"
printf '%s\n' '#!/bin/bash' \
  'if [ "$1" = read-tree ] && [[ "$*" == *--prefix* ]]; then echo "read-tree failed" >&2; exit 1; fi' \
  "exec $REAL_GIT \"\$@\"" > "$SANDBOX/fakebin/git"
chmod +x "$SANDBOX/fakebin/git"
lock_before="$(cat .claude/att-docs.lock)"
PATH="$SANDBOX/fakebin:$PATH" expect_fail "a failed copy-in fails the sync" sync v2
check "$(grep -c 'was restored' "$SANDBOX/out")" 1 "the sync says the old copy was restored"
check "$(cat .claude/att-docs/plugins/general/a.md)" one "the old copy is back"
check "$(git status --porcelain | wc -l | tr -d ' ')" 0 "the index and tree are clean after a restore"
check "$(cat .claude/att-docs.lock)" "$lock_before" "the lock is unchanged after a failed sync"
check_pin > /dev/null && echo "ok   check passes after a restore" ||
  { echo "FAIL check after a restore"; fails=$((fails + 1)); }

# A failed first sync has no old copy: the partial copy is removed and the message says so.
new_consumer firstfail
PATH="$SANDBOX/fakebin:$PATH" expect_fail "a failed first copy-in fails the sync" sync v1
check "$(grep -c 'partial copy of .claude/att-docs was removed' "$SANDBOX/out")" 1 "a first sync failure says the partial copy was removed"
check "$([ -e .claude/att-docs ] && echo left)" "" "no partial copy is left after a failed first sync"

# A failure while staging the lock after the copy landed says what to do.
new_consumer lockfail
mkdir "$SANDBOX/lockbin"
printf '%s\n' '#!/bin/bash' \
  'if [ "$1" = add ] && [[ "$*" == *att-docs.lock* ]]; then echo "add failed" >&2; exit 1; fi' \
  "exec $REAL_GIT \"\$@\"" > "$SANDBOX/lockbin/git"
chmod +x "$SANDBOX/lockbin/git"
PATH="$SANDBOX/lockbin:$PATH" expect_fail "a failed lock stage fails the sync" sync v1
check "$(grep -c 'written but not staged; run: git add -- .claude/att-docs.lock' "$SANDBOX/out")" 1 "a lock stage failure says to stage the lock"
expect_fail "check fails when the lock was never staged" check_pin

# usage: sync_signal <signal> <expected exit>; interrupt a sync blocked inside the swap.
sync_signal() {
  local sig="$1" want="$2" rc
  mkdir -p "$SANDBOX/sigbin"
  printf '%s\n' '#!/bin/bash' \
    'if [ "$1" = read-tree ] && [[ "$*" == *--prefix* ]]; then exec sleep 30; fi' \
    "exec $REAL_GIT \"\$@\"" > "$SANDBOX/sigbin/git"
  chmod +x "$SANDBOX/sigbin/git"
  # A background job starts with SIGINT ignored; reset it so the script's trap can fire.
  PATH="$SANDBOX/sigbin:$PATH" python3 -I -c \
    'import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execv(sys.argv[1], sys.argv[1:])' \
    "$HERE/overmind-sync.sh" v2 > "$SANDBOX/out" 2>&1 &
  local pid=$!
  sleep 2
  kill -"$sig" "$pid"
  pkill -P "$pid" sleep || true
  wait "$pid" && rc=0 || rc=$?
  check "$rc" "$want" "a $sig during the swap exits $want"
  check "$(cat .claude/att-docs/plugins/general/a.md)" one "the old copy is back after a $sig"
  check "$(git status --porcelain -- .claude/att-docs | wc -l | tr -d ' ')" 0 "the index is clean for the prefix after a $sig"
}
new_consumer sigint
sync v1 > /dev/null
git commit -q -m vendor
sync_signal INT 130
new_consumer sigterm
sync v1 > /dev/null
git commit -q -m vendor
sync_signal TERM 143

# A link anywhere in the parent chain is refused, even when it stays inside the repository.
new_consumer inlink
mkdir -p realdir/v
echo mine > realdir/v/notes.txt
ln -s realdir inlink
git add inlink && git commit -q -m link
expect_fail "a symlinked parent inside the repository is refused" env ATT_DOCS_PREFIX=inlink/v "$HERE/overmind-sync.sh" v1
check "$(cat realdir/v/notes.txt)" mine "the untracked file behind the link is kept"

# Refused inputs: a value that git would read as an option or a refspec.
new_consumer inputs
expect_fail "a URL that looks like an option is refused" \
  env "ATT_DOCS_URL=--upload-pack=touch $SANDBOX/injected" "$HERE/overmind-sync.sh" v1
check "$([ -e "$SANDBOX/injected" ] && echo ran)" "" "the injected command did not run"
expect_fail "a URL with a space is refused" env "ATT_DOCS_URL=$UP x" "$HERE/overmind-sync.sh" v1
expect_fail "a tag with a refspec colon is refused" sync "v2:refs/heads/evil"
expect_fail "a tag that starts with a dash is refused" sync "--tags"
expect_fail "a tag with two dots is refused" sync "v1..v2"
expect_fail "a tag with a space is refused" sync "v1 v2"
expect_fail "a repository that is not owner/name is refused" env ATT_DOCS_REPO=../x "$HERE/overmind-sync.sh" v1
expect_fail "a repository with a space is refused" env "ATT_DOCS_REPO=a/b c" "$HERE/overmind-sync.sh" v1
check "$(git branch --list evil | wc -l | tr -d ' ')" 0 "no branch was created from a tag"

# Environment values: an empty variable clears a lock value.
new_consumer clearing
ATT_DOCS_PATHS="plugins/general" sync v1 > /dev/null
git commit -q -m pruned
ATT_DOCS_PATHS="" sync v2 > /dev/null
check "$(ls .claude/att-docs/plugins)" "$(printf 'general\nother\nvoice')" "an empty ATT_DOCS_PATHS gives a full copy"
check "$(lock_value paths)" "" "a full copy records no paths"
git commit -q -m full
printf 'url=%s\n' "/nonexistent" >> .claude/att-docs.lock
ATT_DOCS_URL="$UP" sync v2 > /dev/null
check "$(lock_value url)" /nonexistent "a url already in the lock is kept"
expect_fail "the lock's own url is used when the environment has none" env -u ATT_DOCS_URL "$HERE/overmind-sync.sh" v2

# A failed pruned sync leaves the vendored folder and the index alone.
new_consumer atomic
ATT_DOCS_PATHS="plugins/general" sync v1 > /dev/null
git commit -q -m pruned
before="$(git write-tree)"
expect_fail "a path the tag lacks fails the sync" env ATT_DOCS_PATHS="plugins/general plugins/missing" \
  "$HERE/overmind-sync.sh" v2
check "$(cat .claude/att-docs/plugins/general/a.md)" one "a failed pruned sync keeps the old copy"
check "$(git write-tree)" "$before" "a failed pruned sync leaves the index alone"
check "$(git status --porcelain | wc -l | tr -d ' ')" 0 "a failed pruned sync leaves the tree clean"
# A glob in the path list is never expanded against the consumer tree.
mkdir -p plugins/general && echo local > plugins/general/local.md
expect_fail "a glob path is not expanded" env "ATT_DOCS_PATHS=plugins/*" "$HERE/overmind-sync.sh" v2
rm -r plugins
# Paths that already cover the scripts do not get them added again.
ATT_DOCS_PATHS="plugins/general scripts" sync v2 > /dev/null
check "$(lock_value paths)" "plugins/general scripts" "scripts covers scripts/consumer"

# Files the consuming repository ignores are still vendored and pinned.
new_consumer ignored
echo '*_test.py' > .gitignore
git add -A && git commit -q -m ignore
git -C "$UP" checkout -q -b ign v1
echo t > "$UP/plugins/general/x_test.py"
git -C "$UP" add -A && git -C "$UP" commit -q -m ign && git -C "$UP" tag vign
git -C "$UP" checkout -q main
ATT_DOCS_PATHS="plugins/general" sync vign > /dev/null
check "$(ls .claude/att-docs/plugins/general)" "$(printf 'a.md\nx_test.py')" "an ignored upstream file is vendored"
git commit -q -m vendor
check_pin > /dev/null && echo "ok   check passes with an ignored file in the copy" ||
  { echo "FAIL check with an ignored file"; fails=$((fails + 1)); }
check "$(git ls-files .claude/att-docs | grep -c x_test.py)" 1 "the ignored file is tracked"

# CR line endings in a lock do not break the check.
new_consumer crlf
sync v1 > /dev/null
git commit -q -m vendor
sed -i 's/$/\r/' .claude/att-docs.lock
git add .claude/att-docs.lock
check_pin > /dev/null && echo "ok   check reads a lock with CRLF endings" ||
  { echo "FAIL check with CRLF lock"; fails=$((fails + 1)); }

# The wrapper templates call the vendored scripts.
new_consumer wrapped
sync v1 > /dev/null
mkdir scripts
cp .claude/att-docs/scripts/consumer/wrapper-sync.sh.template scripts/overmind-sync.sh
cp .claude/att-docs/scripts/consumer/wrapper-check.sh.template scripts/overmind-check.sh
chmod +x scripts/*.sh
git add -A && git commit -q -m wrappers
scripts/overmind-sync.sh v2 > /dev/null
check "$(lock_value tag)" v2 "the sync wrapper moves the pin"
git commit -q -m move
scripts/overmind-check.sh > /dev/null && echo "ok   the check wrapper passes" ||
  { echo "FAIL the check wrapper"; fails=$((fails + 1)); }

# JSON lock conversion.
CONV="$HERE/overmind-lock-convert.sh"
SHA_A=62750eeaf29b13244a157d01d121426e558944f0
SHA_B=4537f83fd3ed09179d04fe40273cfcdcfeb8fd7b
cd "$SANDBOX" || exit 1
printf '{\n  "repo": "merph518/Overmind",\n  "tag": "v0.14.2",\n  "commit": "%s",\n  "tree": "%s"\n}\n' \
  "$SHA_A" "$SHA_B" > legacy.lock
want="$(printf 'repo=merph518/Overmind\ntag=v0.14.2\ncommit=%s\ntree=%s' "$SHA_A" "$SHA_B")"
check "$("$CONV" legacy.lock -)" "$want" "convert prints a JSON lock as key=value"
"$CONV" legacy.lock > /dev/null
check "$(cat legacy.lock)" "$want" "convert rewrites the lock in place"
check "$("$CONV" legacy.lock 2>&1; echo "rc=$?")" "$(printf 'legacy.lock is not JSON; nothing to convert\nrc=0')" \
  "convert leaves a key=value lock alone"
check "$(cat legacy.lock)" "$want" "a second convert changes nothing"
printf '{"repo":"a/b","tag":"v1","commit":"%s","tree":"%s","paths":["plugins/general","plugins/voice/skills"]}\n' \
  "$SHA_A" "$SHA_B" > oneline.lock
check "$("$CONV" oneline.lock - | sed -n 's/^paths=//p')" "plugins/general plugins/voice/skills" \
  "convert reads a one-line file and a paths array"
printf '{"repo":"a/b","tag":"v1","commit":"abc","tree":"%s"}\n' "$SHA_B" > bad.lock
expect_fail "convert rejects a short commit" "$CONV" bad.lock -
printf '{"repo":"a/b","commit":"%s","tree":"%s"}\n' "$SHA_A" "$SHA_B" > notag.lock
expect_fail "convert rejects a lock with no tag" "$CONV" notag.lock -
printf '{"repo":"a/b","tag":"v1","commit":"%s","tree":"%s","copy_tree":"nothex"}\n' "$SHA_A" "$SHA_B" > badcopy.lock
expect_fail "convert rejects a bad copy_tree" "$CONV" badcopy.lock -
printf '{"meta":{"tag":"nested"},"repo":"a/b","tag":"v9","commit":"%s","tree":"%s"}\n' "$SHA_A" "$SHA_B" > nested.lock
check "$("$CONV" nested.lock - | sed -n 's/^tag=//p')" v9 "convert ignores a nested tag key"
expect_fail "convert fails on a missing file" "$CONV" nothing.lock -

# A converted lock works with the check: the JSON form is refused first.
new_consumer legacy
sync v1 > /dev/null
git commit -q -m vendor
printf '{"repo":"a/b","tag":"v1","commit":"%s","tree":"%s"}\n' \
  "$(lock_value commit)" "$(lock_value tree)" > .claude/att-docs.lock
expect_fail "check refuses a JSON lock" check_pin
check "$(grep -c overmind-lock-convert "$SANDBOX/out")" 1 "check points at the converter"
"$CONV" > /dev/null
git add .claude/att-docs.lock
check_pin > /dev/null && echo "ok   check passes once the lock is converted" ||
  { echo "FAIL check after conversion"; fails=$((fails + 1)); }

# The remote proof and the base rules. Each case runs the shared check with an explicit
# ATT_DOCS_REMOTE and a file:// source, so no case touches the network.
SRC="file://$UP"
MISSING="file://$SANDBOX/absent"
P=.claude/att-docs
LOCK=.claude/att-docs.lock

# usage: pcheck <case> <exit status> <fragment> [VAR=value ...]; a fragment that starts
# with ! must be absent from the output.
pcheck() {
  local name="$1" want="$2" frag="$3" out rc=0 ok=true
  shift 3
  out="$(env "$@" bash "$HERE/overmind-check.sh" 2>&1)" || rc=$?
  if [ "${frag:0:1}" = '!' ]; then
    [[ "$out" == *"${frag:1}"* ]] && ok=false
  else
    [[ "$out" == *"$frag"* ]] || ok=false
  fi
  if [ "$rc" -eq "$want" ] && [ "$ok" = true ]; then
    echo "ok   $name"
  else
    echo "FAIL $name (exit $rc, wanted $want, fragment '$frag')"
    echo "$out" | sed 's/^/     /'
    fails=$((fails + 1))
  fi
}
branch() { git checkout -q -f -B "$1" main && git clean -fdq; }
commit_all() { git add -A && git commit -q -m x; }
hand_edit() { echo hand >> "$P/plugins/general/a.md" && git add -A -- "$P"; }
set_lock() { sed -i "s#^$1=.*#$1=$2#" "$LOCK" && git add -- "$LOCK"; }
relock() {
  set_lock tree "$(git write-tree --prefix="$P/")"
  if grep -q '^copy_tree=' "$LOCK"; then set_lock copy_tree "$(git write-tree --prefix="$P/")"; fi
}
forge_commit() { set_lock commit "$(git commit-tree "$(git write-tree --prefix="$P/")" -m forged)"; }

new_consumer remote
SEED="$(git rev-parse HEAD)"
env -u ATT_DOCS_URL ATT_DOCS_REPO=acme/skills ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
git commit -q -m vendor
git update-ref refs/remotes/origin/main HEAD
git branch -q -M main
U="ATT_DOCS_URL=$SRC"
M="ATT_DOCS_URL=$MISSING"

branch r1
for mode in off try require; do
  pcheck "remote 1 clean sync passes in $mode" 0 'matches the pin v1' "ATT_DOCS_REMOTE=$mode" "$U"
done

branch r2
sync_v2() { ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v2 > /dev/null; }
sync_v2 && commit_all
pcheck 'remote 2 a sync to v2 passes in require' 0 'matches the pin v2' ATT_DOCS_REMOTE=require "$U"

branch r3
echo more > other.txt && commit_all
pcheck 'remote 3 a change that leaves the pin alone makes no fetch' 0 'matches the pin v1' \
  ATT_DOCS_REMOTE=require "$M"

branch r4
hand_edit
pcheck 'remote 4 a hand edit with the lock unchanged fails' 1 'staged changes but' ATT_DOCS_REMOTE=off

branch r5
hand_edit && relock && commit_all
pcheck 'remote 5 a hand edit with a rewritten tree fails in off' 1 'pinned commit did not' \
  ATT_DOCS_REMOTE=off
pcheck 'remote 5 a hand edit with a rewritten tree fails in require' 1 'pinned commit did not' \
  ATT_DOCS_REMOTE=require "$U"

branch r6
hand_edit && relock && forge_commit && commit_all
pcheck 'remote 6 a forged commit fails in require' 1 'is commit' ATT_DOCS_REMOTE=require "$U"
pcheck 'remote 6 a forged commit fails in try when the tag is reachable' 1 'is commit' \
  ATT_DOCS_REMOTE=try "$U"
pcheck 'remote 6 a forged commit warns in try with the remote unreachable' 0 'warning' \
  ATT_DOCS_REMOTE=try "$M"

branch r7
sync_v2 && commit_all
hand_edit && relock && commit_all
pcheck 'remote 7 a hand edit after a sync to v2 fails' 1 'is commit' \
  ATT_DOCS_REMOTE=require "$U"

branch r8
set_lock tag v2 && commit_all
pcheck 'remote 8 a tag that does not match the commit fails' 1 'is commit' ATT_DOCS_REMOTE=require "$U"

branch r9
set_lock repo other/skills && commit_all
pcheck 'remote 9 a changed repo fails offline' 1 'repo=' ATT_DOCS_REMOTE=off

branch r10
set_lock tag v9 && commit_all
pcheck 'remote 10 a tag absent from the remote fails in require' 1 'is not in' \
  ATT_DOCS_REMOTE=require "$U"
pcheck 'remote 10 a tag absent from the remote fails in try' 1 'is not in' ATT_DOCS_REMOTE=try "$U"
pcheck 'remote 11 an unreachable remote fails in require and names the secret' 1 \
  'OVERMIND_READ_TOKEN' ATT_DOCS_REMOTE=require "$M"
pcheck 'remote 11 an unreachable remote warns in try' 0 'cannot fetch' ATT_DOCS_REMOTE=try "$M"
pcheck 'remote 11 off makes no fetch' 0 '!fetch' ATT_DOCS_REMOTE=off "$M"
pcheck 'remote 11 a bad ATT_DOCS_REMOTE fails' 1 'must be off, try or require' ATT_DOCS_REMOTE=maybe

branch r12
for bad in -x a:b; do
  set_lock tag "$bad" && commit_all
  pcheck "remote 12 the tag '$bad' fails before a fetch" 1 'not a tag name' ATT_DOCS_REMOTE=require "$M"
done
branch r12b
set_lock commit abc && commit_all
pcheck 'remote 12 a short commit fails before a fetch' 1 '40 hex' ATT_DOCS_REMOTE=require "$M"

branch r13
pcheck 'remote 13 a first vendoring passes in require' 0 'matches the pin v1' \
  ATT_DOCS_REMOTE=require "ATT_DOCS_BASE=$SEED" "$U"
set_lock commit "$(git rev-parse 'HEAD^{tree}')" && commit_all
pcheck 'remote 13 a first vendoring is still compared with the tag' 1 'is commit' \
  ATT_DOCS_REMOTE=require "ATT_DOCS_BASE=$SEED" "$U"

branch r14
git update-ref -d refs/remotes/origin/main
pcheck 'remote 14 no origin/main skips the base rules' 0 'base rules skipped' ATT_DOCS_REMOTE=off
pcheck 'remote 14 no origin/main proves the pin against the tag' 0 'matches the pin v1' \
  ATT_DOCS_REMOTE=require "$U"
pcheck 'remote 14 no origin/main with an unreachable remote fails' 1 'OVERMIND_READ_TOKEN' \
  ATT_DOCS_REMOTE=require "$M"
hand_edit
pcheck 'remote 14 no origin/main still checks the tree' 1 'staged changes but' ATT_DOCS_REMOTE=require
git update-ref refs/remotes/origin/main main

branch r15
rm -f "$LOCK"
pcheck 'remote 15 no lock fails' 1 'no .claude/att-docs.lock' ATT_DOCS_REMOTE=off
branch r15b
echo hand >> "$P/plugins/general/a.md"
pcheck 'remote 15 unstaged changes fail' 1 'unstaged changes' ATT_DOCS_REMOTE=off

branch r16
sync_v2 && commit_all
# The only route to the source is the rewrite held in entry 0, so the fetch succeeds only
# if that entry is still in force once the credential header is appended.
pcheck 'remote 16 existing config entries survive the credential header' 0 'matches the pin v2' \
  ATT_DOCS_REMOTE=require ATT_DOCS_URL=https://example.invalid/o.git \
  OVERMIND_READ_TOKEN=dummy GIT_CONFIG_COUNT=1 \
  "GIT_CONFIG_KEY_0=url.$SRC.insteadOf" GIT_CONFIG_VALUE_0=https://example.invalid/o.git

# The URL comes from ATT_DOCS_URL, else the lock's url=; an empty variable clears url=.
branch r17
sync_v2 && printf 'url=%s\n' "$SRC" >> "$LOCK" && commit_all
pcheck 'remote 17 the lock url is used when the environment has none' 0 'matches the pin v2' \
  -u ATT_DOCS_URL "ATT_DOCS_BASE=$SEED" ATT_DOCS_REMOTE=require
pcheck 'remote 17 ATT_DOCS_URL wins over the lock url' 1 'OVERMIND_READ_TOKEN' \
  "ATT_DOCS_BASE=$SEED" ATT_DOCS_REMOTE=require "$M"
branch r17b
printf 'url=%s\n' "$MISSING" >> "$LOCK" && commit_all
pcheck 'remote 17 a lock url that cannot be fetched fails in require' 1 'OVERMIND_READ_TOKEN' \
  -u ATT_DOCS_URL "ATT_DOCS_BASE=$SEED" ATT_DOCS_REMOTE=require
pcheck 'remote 17 an option-like URL is refused' 1 'refusing upstream URL' \
  "ATT_DOCS_BASE=$SEED" ATT_DOCS_REMOTE=require ATT_DOCS_URL=--upload-pack=x

# A pruned copy: the copy is compared with copy_tree=, the remote with the root tree=.
new_consumer prunedremote
SEED="$(git rev-parse HEAD)"
ATT_DOCS_PATHS="plugins/general" ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
git commit -q -m vendor
git update-ref refs/remotes/origin/main HEAD
git branch -q -M main
pcheck 'pruned 1 passes in require' 0 'matches the pin v1' ATT_DOCS_REMOTE=require "$U"
branch p2
pcheck 'pruned 1 passes with no base' 0 'matches the pin v1' ATT_DOCS_REMOTE=require "ATT_DOCS_BASE=$SEED" "$U"
branch p3
hand_edit && relock && forge_commit && commit_all
pcheck 'pruned 2 a forged lock fails in require' 1 'is commit' ATT_DOCS_REMOTE=require "$U"
pcheck 'pruned 2 a forged lock fails in try when the tag is reachable' 1 'is commit' \
  ATT_DOCS_REMOTE=try "$U"
branch p4
hand_edit && relock && commit_all
pcheck 'pruned 3 a rewritten pin without a new commit fails' 1 'pinned commit did not' \
  ATT_DOCS_REMOTE=require "$U"
branch p5
hand_edit
pcheck 'pruned 4 a hand edit with the lock unchanged fails' 1 'staged changes but' ATT_DOCS_REMOTE=off
branch p6
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v2 > /dev/null && commit_all
pcheck 'pruned 5 a pruned sync to v2 passes in require' 0 'matches the pin v2' ATT_DOCS_REMOTE=require "$U"

# The lock's url=, prefix= and copy_tree=, a JSON base lock, and the wrapper's base handling.
branch p7
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v2 > /dev/null && commit_all
hand_edit
set_lock copy_tree "$(git write-tree --prefix="$P/")"
commit_all
pcheck 'pruned 6 a forged copy_tree fails in require' 1 'copy_tree' ATT_DOCS_REMOTE=require "$U"
branch p8
printf 'url=%s\n' "$SRC" >> "$LOCK" && commit_all
pcheck 'lock 1 a changed url= fails' 1 'url=' ATT_DOCS_REMOTE=off
branch p9
mkdir vendor && git mv "$P" vendor/x && echo prefix=vendor/x >> "$LOCK" && commit_all
pcheck 'lock 2 a changed prefix= fails' 1 'prefix=' ATT_DOCS_REMOTE=off
pcheck 'lock 2 a base that holds the new values passes' 0 'matches the pin' \
  ATT_DOCS_REMOTE=off "ATT_DOCS_BASE=$(git rev-parse HEAD)"
branch p10
pcheck 'lock 3 an unchanged lock passes' 0 'matches the pin v1' ATT_DOCS_REMOTE=off

# A tag the remote does not have fails in try and require; an unreachable remote only warns.
new_consumer notag
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
git commit -q -m vendor
git update-ref refs/remotes/origin/main HEAD
git branch -q -M main
branch n1
hand_edit
set_lock tag v9-missing
set_lock commit 1111111111111111111111111111111111111111
set_lock tree "$(git write-tree --prefix="$P/")"
commit_all
for mode in try require; do
  pcheck "missing tag 1 fails in $mode" 1 'is not in acme/skills' ATT_DOCS_REMOTE=$mode "$U"
done
pcheck 'missing tag 1 passes the local part in off' 0 'matches the pin' ATT_DOCS_REMOTE=off
branch n2
pcheck 'missing tag 2 an unreachable remote still warns in try' 0 'warning' ATT_DOCS_REMOTE=try "$M" \
  "ATT_DOCS_BASE=$SEED"

# The --remote flag and unknown arguments.
new_consumer flag
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
git commit -q -m vendor
branch f1
echo more > other.txt && commit_all
git update-ref -d refs/remotes/origin/main
expect_fail "flag: --remote on an unreachable remote fails" env "$M" bash "$HERE/overmind-check.sh" --remote
check "$(grep -c 'OVERMIND_READ_TOKEN' "$SANDBOX/out")" 1 "flag: --remote names the secret"
env ATT_DOCS_REMOTE=off "$U" bash "$HERE/overmind-check.sh" --remote > /dev/null 2>&1 &&
  echo "ok   flag: --remote wins over ATT_DOCS_REMOTE=off with a reachable tag" ||
  { echo "FAIL flag: --remote with a reachable tag"; fails=$((fails + 1)); }
expect_fail "flag: --remote wins over ATT_DOCS_REMOTE=off" env ATT_DOCS_REMOTE=off "$M" bash "$HERE/overmind-check.sh" --remote
rc=0
bash "$HERE/overmind-check.sh" --bogus > "$SANDBOX/out" 2>&1 || rc=$?
check "$rc" 2 "flag: an unknown argument exits 2"
check "$(grep -c "unknown argument '--bogus'" "$SANDBOX/out")" 1 "flag: an unknown argument is named"
cat "$HERE/overmind-check.sh" | env "$M" bash -s -- --remote > "$SANDBOX/out" 2>&1 && rc=0 || rc=$?
check "$rc" 1 "flag: --remote works piped into bash -s"
mkdir -p scripts
cp "$HERE/wrapper-check.sh.template" scripts/overmind-check.sh
chmod +x scripts/overmind-check.sh
git add -A && git commit -q -m wrapper
git checkout -q -f -B main
git update-ref refs/remotes/origin/main HEAD
branch f2
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v2 > /dev/null && commit_all
expect_fail "flag: the wrapper passes --remote through the base path" env "$M" scripts/overmind-check.sh --remote
check "$(grep -c 'OVERMIND_READ_TOKEN' "$SANDBOX/out")" 1 "flag: the wrapper's --remote reached the check"

# The wrapper runs the check from the base commit, so a branch cannot weaken the vendored
# script it runs. With no script in the base, it runs the vendored one.
new_consumer wrapbase
SEED="$(git rev-parse HEAD)"
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
mkdir scripts
cp "$HERE/wrapper-check.sh.template" scripts/overmind-check.sh
chmod +x scripts/overmind-check.sh
git add -A && git commit -q -m vendor
git update-ref refs/remotes/origin/main HEAD
git branch -q -M main
wcheck() { env ATT_DOCS_REMOTE=off "$@" scripts/overmind-check.sh > "$SANDBOX/out" 2>&1; }
S=.claude/att-docs/scripts/consumer/overmind-check.sh
branch w1
printf '#!/usr/bin/env bash\nexit 0\n' > "$S"
hand_edit && relock && commit_all
expect_fail "wrapper: a doctored vendored script does not hide a hand edit" wcheck
check "$(grep -c 'pinned commit did not' "$SANDBOX/out")" 1 "wrapper: the base script reports the edit"
bash "$S" > /dev/null && echo "ok   the doctored vendored script alone would pass" ||
  { echo "FAIL the doctored script should pass on its own"; fails=$((fails + 1)); }
git checkout -q -f -B w2 main
wcheck && echo "ok   wrapper: an untouched branch passes" ||
  { echo "FAIL wrapper on an untouched branch"; cat "$SANDBOX/out"; fails=$((fails + 1)); }
printf '#!/usr/bin/env bash\necho fallback ran\nexit 1\n' > "$S"
git add -A && git commit -q -m x
expect_fail "wrapper: with no script in the base it runs the vendored one" wcheck ATT_DOCS_BASE="$SEED"
check "$(grep -c 'fallback ran' "$SANDBOX/out")" 1 "wrapper: the fallback ran the vendored script"
# The check also runs when piped into bash, as the wrapper does.
git checkout -q -f -B w3 main
git show "main:$S" | bash -s > "$SANDBOX/out" 2>&1 && echo "ok   the check runs piped into bash -s" ||
  { echo "FAIL the check piped into bash -s"; cat "$SANDBOX/out"; fails=$((fails + 1)); }

new_consumer plaincopy
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
git commit -q -m vendor
git update-ref refs/remotes/origin/main HEAD
git branch -q -M main
branch c1
printf 'copy_tree=%s\n' "$(git write-tree --prefix="$P/")" >> "$LOCK" && commit_all
pcheck 'lock 4 a copy_tree= on a lock with no paths= fails in require' 1 'no paths=' \
  ATT_DOCS_REMOTE=require "$U"

new_consumer jsonbase
SEED="$(git rev-parse HEAD)"
mkdir -p .claude
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
printf '{"repo":"acme/skills","tag":"v1","commit":"%s","tree":"%s"}\n' \
  "$(lock_value commit)" "$(lock_value tree)" > "$LOCK"
git add -A && git commit -q -m json
git update-ref refs/remotes/origin/main HEAD
git branch -q -M main
branch j1
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null 2>&1 || true
bash "$HERE/overmind-lock-convert.sh" > /dev/null
git add -A
pcheck 'json 1 converting a JSON lock passes in require' 0 'matches the pin v1' \
  ATT_DOCS_REMOTE=require "$U"

# Wrapper base handling.
new_consumer wrapbase2
SEED="$(git rev-parse HEAD)"
ATT_DOCS_URL="$SRC" bash "$HERE/overmind-sync.sh" v1 > /dev/null
mkdir scripts
cp "$HERE/wrapper-check.sh.template" scripts/overmind-check.sh
chmod +x scripts/overmind-check.sh
git add -A && git commit -q -m vendor
git update-ref refs/remotes/origin/main HEAD
git branch -q -M main
S=.claude/att-docs/scripts/consumer/overmind-check.sh
wcheck() { env ATT_DOCS_REMOTE=off "$@" scripts/overmind-check.sh > "$SANDBOX/out" 2>&1; }
expect_fail "wrapper: a bogus ATT_DOCS_BASE fails" wcheck ATT_DOCS_BASE=0123456789abcdef0123456789abcdef01234567
check "$(grep -c 'not a commit' "$SANDBOX/out")" 1 "wrapper: a bogus base names the problem"
git update-ref -d refs/remotes/origin/main
printf '#!/usr/bin/env bash\necho vendored ran\nexit 1\n' > "$S"
expect_fail "wrapper: with no base at all it runs the vendored script" wcheck
check "$(grep -c 'vendored ran' "$SANDBOX/out")" 1 "wrapper: the vendored script ran with no base"

echo
if [ "$fails" -eq 0 ]; then echo "all passed"; else echo "$fails failed"; exit 1; fi
