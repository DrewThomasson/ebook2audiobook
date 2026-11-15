#!/usr/bin/env bash
# Fail when the vendored copy in a consuming repository differs from the tree its lock
# file pins, so a hand edit to a vendored file cannot land. Works offline. Run it from
# inside the consuming repository.
#
# usage: overmind-check.sh [--remote]
#
# --remote  the same as ATT_DOCS_REMOTE=require, and wins over that variable. Any other
#           argument prints a usage line and exits 2.
#
# Reads the same settings as overmind-sync.sh: ATT_DOCS_LOCK and ATT_DOCS_PREFIX in the
# environment, then prefix= in the lock, then the defaults .claude/att-docs.lock and
# .claude/att-docs. It compares the lock's copy_tree= when present, else tree=.
#
# The lock itself is held to the pinned tag: it cannot change repo=, url= or prefix=,
# cannot change the vendored tree without moving commit=, and a changed pin is compared with the tag in the
# source repository, whose root tree must equal the lock's tree=.
#
# ATT_DOCS_BASE    the commit the lock is compared with; default: merge base with origin/main
# ATT_DOCS_REMOTE  off: no fetch. try (default): a fetch that cannot complete warns and
#                  passes. require: a fetch that cannot complete fails.
# ATT_DOCS_URL     where the source repository is fetched from; else url= in the lock, else
#                  https://github.com/<repo>.git. A variable that is set but empty clears url=.
# OVERMIND_READ_TOKEN  read access to the source repository, sent to the fetch only
#
# The script does not use $0, so it runs when piped into bash -s.
set -euo pipefail

REMOTE_FLAG=""
for arg in "$@"; do
  case "$arg" in
    --remote) REMOTE_FLAG=require ;;
    *)
      echo "att-docs: unknown argument '$arg'"
      echo "usage: overmind-check.sh [--remote]"
      exit 2
      ;;
  esac
done

# The folder is always a literal path, never a pathspec with magic such as ':!'.
export GIT_LITERAL_PATHSPECS=1

cd "$(git rev-parse --show-toplevel)"
LOCK="${ATT_DOCS_LOCK:-.claude/att-docs.lock}"

if [ ! -f "$LOCK" ]; then
  echo "att-docs: no $LOCK"
  exit 1
fi
if grep -q '^[[:space:]]*{' "$LOCK"; then
  echo "att-docs: $LOCK is JSON; convert it with ${ATT_DOCS_PREFIX:-.claude/att-docs}/scripts/consumer/overmind-lock-convert.sh, or pipe that script from the tag into bash -s"
  exit 1
fi

lock_get() { sed -n "s/^$1=//p" "$LOCK" | head -n 1 | tr -d '\r'; }

PREFIX="${ATT_DOCS_PREFIX:-$(lock_get prefix)}"
PREFIX="${PREFIX:-.claude/att-docs}"
PREFIX="$(printf '%s' "$PREFIX" | sed -e 's#//*#/#g' -e 's#/\./#/#g' -e 's#^\(\./\)\{1,\}##' \
  -e 's#/\.$##' -e 's#/$##')"

if ! git diff --quiet -- "$PREFIX"; then
  echo "att-docs: unstaged changes under $PREFIX"
  exit 1
fi
if ! git ls-files --error-unmatch -- "$LOCK" > /dev/null 2>&1 || ! git diff --quiet -- "$LOCK"; then
  echo "att-docs: $LOCK is not staged; run git add on it or rerun overmind-sync.sh"
  exit 1
fi
if ! git diff --cached --quiet -- "$PREFIX" && git diff --cached --quiet -- "$LOCK"; then
  echo "att-docs: $PREFIX has staged changes but $LOCK does not; stage the lock or rerun overmind-sync.sh"
  exit 1
fi
if [ -n "$(git ls-files --others --exclude-standard -- "$PREFIX")" ]; then
  echo "att-docs: untracked files under $PREFIX"
  exit 1
fi

LOCK_TEXT="$(tr -d '\r' < "$LOCK")"
lock_value() { printf '%s\n' "$2" | sed -n "s/^$1=//p" | head -n 1; }

REPO="$(lock_value repo "$LOCK_TEXT")"
TAG="$(lock_value tag "$LOCK_TEXT")"
COMMIT="$(lock_value commit "$LOCK_TEXT")"
ROOT_TREE="$(lock_value tree "$LOCK_TEXT")"
COPY_TREE="$(lock_value copy_tree "$LOCK_TEXT")"
PINNED="${COPY_TREE:-$ROOT_TREE}"
ACTUAL="$(git write-tree --prefix="$PREFIX/" 2>/dev/null || true)"
if [ -z "$PINNED" ] || [ "$PINNED" != "$ACTUAL" ]; then
  echo "att-docs: $PREFIX is tree '${ACTUAL:-missing}', the lock pins '${PINNED:-none}'"
  echo "att-docs: change the pin with overmind-sync.sh <tag>, never by hand"
  exit 1
fi

if ! [[ "$REPO" =~ ^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$ ]]; then
  echo "att-docs: repo= in $LOCK is not <owner>/<name>"
  exit 1
fi
if ! [[ "$TAG" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]*$ ]] || [[ "$TAG" == *..* ]]; then
  echo "att-docs: tag= in $LOCK is not a tag name"
  exit 1
fi
if ! [[ "$COMMIT" =~ ^[0-9a-f]{40}$ ]] || ! [[ "$ROOT_TREE" =~ ^[0-9a-f]{40}$ ]] ||
  { [ -n "$COPY_TREE" ] && ! [[ "$COPY_TREE" =~ ^[0-9a-f]{40}$ ]]; }; then
  echo "att-docs: commit=, tree= and copy_tree= in $LOCK must each be 40 hex characters"
  exit 1
fi

# Fetches the pinned tag into a scratch repository and compares its commit and root tree
# with the lock's commit= and tree=. Returns 0 on a match, 1 on a mismatch, 2 when the
# fetch cannot complete. Runs in a subshell, so the credential header and the scratch
# directory stay inside it.
remote_compare() {
  local url n basic got_commit got_tree
  if [ "${ATT_DOCS_URL+x}" = x ]; then url="$ATT_DOCS_URL"; else url="$(lock_value url "$LOCK_TEXT")"; fi
  url="${url:-https://github.com/$REPO.git}"
  case "$url" in
    -* | *[[:space:]]* | *[[:cntrl:]]*)
      echo "att-docs: refusing upstream URL: it must not start with '-' or hold spaces"
      return 1
      ;;
  esac
  # The scratch repository must not inherit the caller's repository selection.
  unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_COMMON_DIR GIT_NAMESPACE
  tmp="$(mktemp -d)"  # not local: the exit trap reads it
  trap 'rm -rf "$tmp"' EXIT
  git init -q --bare "$tmp/src.git"
  if [ -n "${OVERMIND_READ_TOKEN:-}" ]; then
    # The header goes through the environment, never the command line. The count is
    # appended to, because the caller may already hold config entries.
    basic="$(printf 'x-access-token:%s' "$OVERMIND_READ_TOKEN" | base64 | tr -d '\n')"
    n="${GIT_CONFIG_COUNT:-0}"
    export "GIT_CONFIG_KEY_$n=http.https://github.com/.extraheader"
    export "GIT_CONFIG_VALUE_$n=AUTHORIZATION: basic $basic"
    export GIT_CONFIG_COUNT=$((n + 1))
  fi
  if ! GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git -C "$tmp/src.git" -c http.lowSpeedLimit=1000 \
      -c http.lowSpeedTime=30 fetch -q --no-tags --depth=1 -- "$url" "refs/tags/$TAG" \
      < /dev/null 2> /dev/null; then
    # Exit 2 from ls-remote means the remote answered and has no such tag.
    rc=0
    GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git -c http.lowSpeedLimit=1000 \
      -c http.lowSpeedTime=30 ls-remote --exit-code -- "$url" "refs/tags/$TAG" \
      < /dev/null > /dev/null 2>&1 || rc=$?
    if [ "$rc" -eq 2 ]; then
      echo "att-docs: tag $TAG is not in $REPO"
      return 1
    fi
    return 2
  fi
  got_commit="$(git -C "$tmp/src.git" rev-parse 'FETCH_HEAD^{commit}')"
  got_tree="$(git -C "$tmp/src.git" rev-parse 'FETCH_HEAD^{tree}')"
  if [ "$got_commit" != "$COMMIT" ] || [ "$got_tree" != "$ROOT_TREE" ]; then
    echo "att-docs: tag $TAG in $REPO is commit $got_commit, tree $got_tree"
    echo "att-docs: the lock pins commit $COMMIT, tree $ROOT_TREE"
    return 1
  fi
  if [ -n "$COPY_TREE" ]; then
    # A pruned lock: rebuild the copy from the tag and the lock's paths=, as the sync does.
    local paths p covered="" rebuilt
    paths="$(lock_value paths "$LOCK_TEXT")"
    if [ -z "$paths" ]; then
      echo "att-docs: copy_tree= in $LOCK has no paths= to rebuild it from the tag"
      return 1
    fi
    set -f
    for p in $paths; do
      case "$p" in
        -* | /* | *..*) set +f; echo "att-docs: refusing path '$p' in paths="; return 1 ;;
      esac
      case "$p" in scripts | scripts/ | scripts/consumer | scripts/consumer/) covered=1 ;; esac
    done
    if [ -z "$covered" ]; then paths="$paths scripts/consumer"; fi
    case " $paths " in
      *" .gitattributes "*) ;;
      *) if git -C "$tmp/src.git" cat-file -e "FETCH_HEAD:.gitattributes" 2> /dev/null; then paths="$paths .gitattributes"; fi ;;
    esac
    # shellcheck disable=SC2086  # the path list is split on purpose, with globbing off
    rebuilt="$(git -C "$tmp/src.git" ls-tree -r -z FETCH_HEAD -- $paths |
      GIT_INDEX_FILE="$tmp/index" git -C "$tmp/src.git" update-index -z --index-info &&
      GIT_INDEX_FILE="$tmp/index" git -C "$tmp/src.git" write-tree)" || rebuilt=""
    set +f
    if [ "$rebuilt" != "$COPY_TREE" ]; then
      echo "att-docs: the paths= of tag $TAG in $REPO make tree '${rebuilt:-none}', the lock pins copy_tree $COPY_TREE"
      return 1
    fi
  fi
  return 0
}

MODE="${REMOTE_FLAG:-${ATT_DOCS_REMOTE:-try}}"
case "$MODE" in
  off | try | require) ;;
  *)
    echo "att-docs: ATT_DOCS_REMOTE must be off, try or require, not '$MODE'"
    exit 1
    ;;
esac

BASE="${ATT_DOCS_BASE:-}"
if [ -z "$BASE" ]; then
  BASE="$(git merge-base HEAD origin/main 2>/dev/null || true)"
fi
if [ -z "$BASE" ]; then
  echo "att-docs: no origin/main to compare the lock with; base rules skipped"
else
  BASE_LOCK="$(git show "$BASE:$LOCK" 2>/dev/null | tr -d '\r' || true)"
  # A JSON lock has no keys to compare; it counts as no base lock, so converting it passes.
  if printf '%s\n' "$BASE_LOCK" | grep -q '^[[:space:]]*{'; then BASE_LOCK=""; fi
  BASE_TREE="$(git rev-parse "$BASE:$PREFIX" 2>/dev/null || true)"
  if [ -n "$BASE_LOCK" ]; then
    if [ "$(lock_value repo "$BASE_LOCK")" != "$REPO" ]; then
      echo "att-docs: repo= is '$REPO', the base lock has '$(lock_value repo "$BASE_LOCK")'"
      exit 1
    fi
    if [ "$(lock_value url "$BASE_LOCK")" != "$(lock_value url "$LOCK_TEXT")" ]; then
      echo "att-docs: url= is '$(lock_value url "$LOCK_TEXT")', the base lock has '$(lock_value url "$BASE_LOCK")'"
      exit 1
    fi
    base_prefix="$(lock_value prefix "$BASE_LOCK")"
    cur_prefix="$(lock_value prefix "$LOCK_TEXT")"
    if [ "${base_prefix:-.claude/att-docs}" != "${cur_prefix:-.claude/att-docs}" ]; then
      echo "att-docs: prefix= is '$(lock_value prefix "$LOCK_TEXT")', the base lock has '$base_prefix'"
      exit 1
    fi
    if [ "$BASE_TREE" != "$ACTUAL" ] && [ "$(lock_value commit "$BASE_LOCK")" = "$COMMIT" ]; then
      echo "att-docs: the vendored tree changed but the pinned commit did not"
      echo "att-docs: move the pin with overmind-sync.sh <tag>"
      exit 1
    fi
  fi
  if [ -n "$BASE_LOCK" ] && [ "$BASE_LOCK" = "$LOCK_TEXT" ] && [ "$BASE_TREE" = "$ACTUAL" ]; then
    echo "att-docs: $PREFIX matches the pin $TAG"
    exit 0
  fi
fi

# With no base to say the pin is unchanged, the pin is proved against the tag.
if [ "$MODE" != off ]; then
  rc=0
  (remote_compare) || rc=$?
  if [ "$rc" -eq 1 ]; then
    exit 1
  elif [ "$rc" -ne 0 ]; then
    if [ "$MODE" = require ]; then
      echo "att-docs: cannot fetch tag $TAG from $REPO to prove the pin"
      echo "att-docs: load the OVERMIND_READ_TOKEN secret, a credential that reads $REPO"
      exit 1
    fi
    echo "att-docs: warning: cannot fetch tag $TAG from $REPO; pin not proved against it"
  fi
fi
echo "att-docs: $PREFIX matches the pin $TAG"
