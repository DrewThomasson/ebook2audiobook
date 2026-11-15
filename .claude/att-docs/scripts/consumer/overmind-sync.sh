#!/usr/bin/env bash
# Vendor a tagged snapshot of the skills repository into a consuming repository and
# record the pin in a lock file. Run it from inside the consuming repository.
#
# usage: overmind-sync.sh [<tag>]
#
# The tag defaults to the one the lock file already holds. Every other value comes
# from the environment first, then from the lock file, then from the default. A
# variable that is set but empty clears the lock's value for paths and url.
#
#   value             environment       lock key   default
#   repository        ATT_DOCS_REPO     repo       (required)
#   upstream URL      ATT_DOCS_URL      url        https://github.com/<repo>.git
#   vendored folder   ATT_DOCS_PREFIX   prefix     .claude/att-docs
#   subset of paths   ATT_DOCS_PATHS    paths      (whole snapshot)
#   lock file         ATT_DOCS_LOCK     -          .claude/att-docs.lock
#
# ATT_DOCS_PATHS and paths= hold space-separated paths inside the snapshot. When set,
# only those paths are copied, plus scripts/consumer so the wrapper keeps working
# and .gitattributes when the tag has one (unless a listed path already covers it). The lock then also records copy_tree=, the
# tree of the pruned copy, because tree= always names the whole tag. The
# overmind-check.sh script compares the copy_tree value when it is present and the
# tree value otherwise.
#
# The lock file is plain key=value lines: repo, [url], [prefix], tag, commit, tree,
# [paths], [copy_tree]. A url from ATT_DOCS_URL is used for the fetch but never written
# to the lock, since a committed lock must not carry a credential; only a url= line
# already in the lock is kept. The script stages the copy and the lock; it does not
# commit.
set -euo pipefail

# A prefix is always a literal path, never a pathspec with magic such as ':!'.
export GIT_LITERAL_PATHSPECS=1

STAGE=""
RESTORE=""
LOCKING=""

# Runs on every exit. If the old copy was removed and the new one never landed, put
# the old copy back from the last commit. A failure after the new copy is staged but
# before the lock is staged leaves the new copy with the old lock.
on_exit() {
  local rc=$?
  trap - EXIT
  if [ -n "$STAGE" ]; then rm -rf "$STAGE" || true; fi
  if [ -n "$RESTORE" ] && [ "$rc" -ne 0 ]; then
    local had_old=""
    if git cat-file -e "HEAD:$RESTORE" 2> /dev/null; then had_old=1; fi
    if git reset -q HEAD -- "$RESTORE" && rm -rf -- "$RESTORE" &&
      { [ -z "$had_old" ] || git checkout -q HEAD -- "$RESTORE"; }; then
      if [ -n "$had_old" ]; then
        echo "the sync failed; the previous copy of $RESTORE was restored" >&2
      else
        echo "the sync failed; the partial copy of $RESTORE was removed" >&2
      fi
    else
      local q
      q="$(printf '%q' "$RESTORE")"
      if [ -n "$had_old" ]; then
        echo "the sync failed and the previous copy of $RESTORE could not be restored; run:" >&2
        echo "  git --literal-pathspecs reset -q HEAD -- $q && git --literal-pathspecs checkout HEAD -- $q" >&2
      else
        echo "the sync failed and the partial copy of $RESTORE could not be removed; run:" >&2
        echo "  git --literal-pathspecs reset -q HEAD -- $q && rm -rf -- $q" >&2
      fi
    fi
  elif [ -n "$LOCKING" ] && [ "$rc" -ne 0 ]; then
    echo "the new copy is staged and the lock was written but not staged; run: git add -- $(printf '%q' "$LOCKING")" >&2
    echo "or rerun the sync" >&2
  fi
  exit "$rc"
}
trap on_exit EXIT
# A signal runs the exit trap with a zero status; map each to a failing exit so the
# restore still runs.
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

die() {
  echo "$*" >&2
  exit 1
}

# usage: replace_copy <prefix> <tree-ish>; swaps the folder for the tree's contents.
replace_copy() {
  RESTORE="$1"
  git rm -r -q --ignore-unmatch -- "$1"
  rm -rf "$1"
  git read-tree --prefix="$1/" -u "$2"
  RESTORE=""
}

main() {
  local tag="${1:-}"
  local root
  root="$(git rev-parse --show-toplevel)"
  cd "$root"

  local lock="${ATT_DOCS_LOCK:-.claude/att-docs.lock}"
  lock_get() {
    if [ -f "$lock" ]; then sed -n "s/^$1=//p" "$lock" | head -n 1 | tr -d '\r'; fi
  }

  if [ -f "$lock" ] && grep -q '^[[:space:]]*{' "$lock"; then
    die "att-docs: $lock is JSON; convert it with ${ATT_DOCS_PREFIX:-.claude/att-docs}/scripts/consumer/overmind-lock-convert.sh, or pipe that script from the tag into bash -s"
  fi

  local repo="${ATT_DOCS_REPO:-$(lock_get repo)}"
  local lock_url url paths prefix
  lock_url="$(lock_get url)"
  if [ "${ATT_DOCS_URL+x}" = x ]; then
    url="$ATT_DOCS_URL"
    if [ -z "$url" ]; then lock_url=""; fi
  else
    url="$lock_url"
  fi
  if [ "${ATT_DOCS_PATHS+x}" = x ]; then paths="$ATT_DOCS_PATHS"; else paths="$(lock_get paths)"; fi
  prefix="${ATT_DOCS_PREFIX:-$(lock_get prefix)}"
  prefix="${prefix:-.claude/att-docs}"
  tag="${tag:-$(lock_get tag)}"

  if [ -z "$tag" ]; then
    die "usage: overmind-sync.sh [<tag>]"
  fi
  if [ -z "$repo" ]; then
    die "no repository: set ATT_DOCS_REPO=<owner>/<name> or add repo= to $lock"
  fi
  if ! printf '%s' "$repo" | grep -Eq '^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$'; then
    die "refusing repository '$repo': expected <owner>/<name>"
  fi
  case "$repo" in ./* | ../* | */. | */..) die "refusing repository '$repo': expected <owner>/<name>" ;; esac
  case "$tag" in
    -* | *:* | *..* | *[[:space:]]* | *[[:cntrl:]]*) die "refusing tag '$tag'" ;;
  esac
  case "$url" in
    -* | *[[:space:]]* | *[[:cntrl:]]*) die "refusing upstream URL: it must not start with '-' or hold spaces" ;;
  esac

  # Normalize ./, repeated and trailing slashes before the guard looks at the folder.
  prefix="$(printf '%s' "$prefix" | sed -e 's#//*#/#g' -e 's#/\./#/#g' -e 's#^\(\./\)\{1,\}##' \
    -e 's#/\.$##' -e 's#/$##')"
  case "$prefix" in
    "" | :* | /* | . | .. | ../* | */.. | */../* | .[Gg][Ii][Tt] | .[Gg][Ii][Tt]/* | */.[Gg][Ii][Tt] | */.[Gg][Ii][Tt]/*)
      die "refusing to vendor into '$prefix': use a folder inside the repository, outside any .git"
      ;;
  esac
  local ancestor real_root real_parent git_dir
  ancestor="$(dirname "$prefix")"
  while [ ! -d "$ancestor" ]; do ancestor="$(dirname "$ancestor")"; done
  real_root="$(pwd -P)"
  real_parent="$(cd -P "$ancestor" && pwd)"
  case "$real_parent/" in
    "$real_root"/*) ;;
    *) die "refusing to vendor into '$prefix': its parent folder resolves outside the repository" ;;
  esac
  # A link anywhere in the parent chain would hide the folder from the status guard.
  if [ "$ancestor" = . ]; then
    [ "$real_parent" = "$real_root" ] || die "refusing to vendor into '$prefix': its parent folder is a link"
  elif [ "$real_parent" != "$real_root/$ancestor" ]; then
    die "refusing to vendor into '$prefix': a parent folder is a symbolic link"
  fi
  # A link inside the repository can still lead into the repository's own git folders.
  for git_dir in "$(git rev-parse --git-dir)" "$(git rev-parse --git-common-dir)"; do
    git_dir="$(cd -P "$git_dir" && pwd)"
    case "$real_parent/" in
      "$git_dir"/*) die "refusing to vendor into '$prefix': its parent folder resolves into the git folder" ;;
    esac
  done
  if [ -L "$prefix" ]; then
    die "refusing to vendor into '$prefix': it is a symbolic link"
  fi

  if [ -n "$(git status --porcelain --untracked-files=all -- "$prefix")" ]; then
    die "uncommitted changes under $prefix; commit or discard them first"
  fi

  local pinned_tag pinned_commit
  pinned_tag="$(lock_get tag)"
  pinned_commit="$(lock_get commit)"

  git fetch --quiet --no-tags -- "${url:-https://github.com/$repo.git}" "refs/tags/$tag"
  local commit tree
  commit="$(git rev-parse 'FETCH_HEAD^{commit}')"
  tree="$(git rev-parse 'FETCH_HEAD^{tree}')"

  if [ "$tag" = "$pinned_tag" ] && [ -n "$pinned_commit" ] && [ "$commit" != "$pinned_commit" ]; then
    die "tag $tag now points at $commit, not the pinned $pinned_commit"
  fi

  local copy_tree=""
  if [ -z "$paths" ]; then
    replace_copy "$prefix" FETCH_HEAD
  else
    # Build the pruned tree from the tag's objects in a temporary index first, so a
    # path the tag lacks leaves the existing vendored folder and the index untouched,
    # and file modes come from the tag rather than from the filesystem.
    local p covered=""
    set -f
    for p in $paths; do
      case "$p" in -* | /* | *..*) die "refusing path '$p'" ;; esac
      case "$p" in scripts | scripts/ | scripts/consumer | scripts/consumer/) covered=1 ;; esac
    done
    if [ -z "$covered" ]; then paths="$paths scripts/consumer"; fi
    # The snapshot's line-ending rules travel with every copy that has them.
    case " $paths " in
      *" .gitattributes "*) ;;
      *) if git cat-file -e "FETCH_HEAD:.gitattributes" 2> /dev/null; then paths="$paths .gitattributes"; fi ;;
    esac
    for p in $paths; do
      git cat-file -e "FETCH_HEAD:$p" 2> /dev/null || { set +f; die "path '$p' is not in $tag"; }
    done
    STAGE="$(mktemp -d)"
    # shellcheck disable=SC2086  # the path list is split on purpose, with globbing off
    git ls-tree -r -z FETCH_HEAD -- $paths | GIT_INDEX_FILE="$STAGE/index" git update-index -z --index-info
    set +f
    copy_tree="$(GIT_INDEX_FILE="$STAGE/index" git write-tree)"
    for p in $paths; do
      git cat-file -e "$copy_tree:${p%/}" 2> /dev/null || die "path '$p' did not make it into the copy"
    done
    replace_copy "$prefix" "$copy_tree"
  fi

  LOCKING="$lock"
  mkdir -p "$(dirname "$lock")"
  {
    printf 'repo=%s\n' "$repo"
    if [ -n "$lock_url" ]; then printf 'url=%s\n' "$lock_url"; fi
    if [ "$prefix" != ".claude/att-docs" ]; then printf 'prefix=%s\n' "$prefix"; fi
    printf 'tag=%s\ncommit=%s\ntree=%s\n' "$tag" "$commit" "$tree"
    if [ -n "$paths" ]; then printf 'paths=%s\n' "$paths"; fi
    if [ -n "$copy_tree" ]; then printf 'copy_tree=%s\n' "$copy_tree"; fi
  } > "$lock"
  git add -- "$lock"
  echo "vendored $repo $tag ($commit) into $prefix"
}

# The vendored copy this file lives in is replaced while it runs. All the work stays
# inside main and the shell exits right after it, so bash has read the whole script
# before the copy is touched and never reads past this point.
main "$@"
exit $?
