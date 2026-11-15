#!/usr/bin/env bash
# PreToolUse guard for one repository rule that a session cannot be trusted to
# hold in its head for the length of a long task: the main checkout is shared
# by concurrent sessions, so it stays read-only. Edits and branch-changing git
# belong in a worktree under .claude/worktrees/<name>, which is exempt; a harness
# with a worktree tool may create it, and `git worktree add` always can.
# `git pull --ff-only` of main is allowed.
# Wire up via .claude/settings.json, or, for a session that loads project
# extensions from .omp/settings.json, through scripts/omp-guard-hook.mjs.
# Exit 2 blocks the tool call and returns stderr to the model.

HERE="$(dirname "$0")"
. "$HERE/lib/session-paths.sh"
. "$HERE/lib/hook-tool.sh"

payload=$(cat)

# Each tool is read as a file edit, judged by the paths it writes, or as a shell
# command, judged by its text (lib/hook-tool.sh says which tools are which). A
# terminal tab opened in another directory is judged from there.
hook_tool "$payload"
kind="$HOOK_KIND"
cmd="$HOOK_CMD"
cwd="$HOOK_CWD"

# The command with its heredoc bodies taken out, since grep reads each line as
# the start of a command and a body line such as `git stash` is only text.
# lib/heredoc.py follows quotes, comments, and substitutions to find where each
# body starts, and the whole command is read where it cannot run.
lines="$cmd"
case "$cmd" in
  *"<<"*) lines=$(python3 "$HERE/lib/heredoc.py" <<<"$cmd" 2>/dev/null) || lines="$cmd" ;;
esac

# Only the writing tools are checked. A relative path is resolved against the
# session's cwd before matching, since the same file arrives as a relative path
# from the repository root and as an absolute path from anywhere else. A leading
# `~` is the home directory. A move writes both its ends: the source goes away
# and the destination appears.
targets=()
root=""
if [ "$kind" = edit ]; then
  while IFS= read -r path; do
    [ -n "$path" ] && targets+=("$(hook_path "$cwd" "$path")")
  done < <(jq -r '.tool_input | (.file_path, .notebook_path, .path, .outputPath,
    .source, .destination) // empty' <<<"$payload")
  root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)"
fi

# A guard that cannot tell where the checkout is cannot tell what to block, so
# it stands down rather than blocking every session it is wired into.
MAIN="$(session_main_checkout "$HERE")" || exit 0
# The cwd and every target are resolved, so the checkout they are matched
# against is too.
real_main="$(resolve "$MAIN")"
WORKTREES="$real_main/.claude/worktrees"

deny() {
  echo "Blocked: $1" >&2
  echo "The main checkout is read-only; other sessions share it." >&2
  echo "Work in a worktree instead: git worktree add -b <branch> \\" >&2
  echo "  $MAIN/.claude/worktrees/<name> origin/main" >&2
  echo "Then address its files by absolute path and give each shell call" >&2
  echo "that worktree as its working directory. Where the harness supports it, an" >&2
  echo "operator can rebind the session: /move <path>, or a launch with --cwd <path>." >&2
  exit 2
}

# The edit tools are judged by where the write lands, whatever the session's
# cwd: a scratchpad or other file outside the repository passes, and a file in
# the checkout is blocked even from a worktree session. The resolved target
# follows a `..` that climbs out of a worktree, and a link a worktree shares
# with the checkout, such as node_modules, to the checkout itself.
if [ "$kind" = edit ]; then
  for target in "${targets[@]}"; do
    case "$target" in
      "$WORKTREES"/*) ;;
      "$real_main" | "$real_main"/*)
        case "$cwd" in
          "$WORKTREES"/*)
            echo "Blocked: file edit in the main checkout" >&2
            echo "The main checkout is read-only; other sessions share it." >&2
            echo "This session is already in a worktree: edit the same" >&2
            echo "path under ${root:-$cwd} instead." >&2
            exit 2
            ;;
        esac
        deny "file edit in the main checkout"
        ;;
    esac
  done
  exit 0
fi

# A shell command is judged by where each of its branch-mutating git commands
# acts, after any `cd` before it and any `git -C`, whatever directory the
# command starts in. lib/git-targets.py prints one directory per such command.
# Where python3 cannot run, a bare git verb on any line is judged from the
# starting directory.
if [ "$kind" = shell ] && [ -n "$cwd" ] && grep -qw git <<<"$lines"; then
  verbs='checkout|switch|restore|stash|reset|merge|rebase|pull'
  if ! acted=$(python3 "$HERE/lib/git-targets.py" "$cwd" <<<"$lines" 2>/dev/null); then
    acted=""
    if grep -qE "(^|[;&|] *)git +(-c +[^ ]+ +)*($verbs)( |$)" <<<"$lines"; then
      acted="$cwd"
    fi
  fi
  while IFS= read -r target; do
    case "$target" in
      "$WORKTREES"/*) ;;
      "$real_main" | "$real_main"/*)
        deny "branch-mutating git in the main checkout"
        ;;
    esac
  done <<<"$acted"
fi

exit 0
