---
name: new-branch
description: >-
  Start a working branch of ebook2audiobook-expressive from a freshly fetched origin/main,
  in a worktree of its own. Use whenever new work needs a branch - "start a branch",
  "branch for issue N", "let's work on X" - and before the first edit of any task that
  does not already have one.
---

# New Branch

## Base

Read
[the general skill](../../att-docs/plugins/general/skills/new-branch/SKILL.md)
first and follow it, except where this file overrides it. The general skill is the vendored
copy pinned by `.claude/att-docs.lock`; never edit it here.

## Paths

| Placeholder | Value here |
| --- | --- |
| `<default-branch>` | `main` |
| `<remote>` | `origin` (`merph518/ebook2audiobook-expressive`) |
| `<worktree-script>` | `git fetch origin --prune`, then `git worktree add -b <branch> .claude/worktrees/<slug> origin/main` from the main checkout, then `realpath .claude/worktrees/<slug>` |
| `<enter-worktree-note>` | Give every later shell call the worktree as its working directory, and address every file by its absolute worktree path, because the session's working directory stays the main checkout |
| `<branch-types>` | `fix`, `feat`, `chore`, `docs` |
| `<branch-name-form>` | `<type>/issue-<N>-<slug>` with an issue, `<type>/<slug>` without |
| `<branch-age-note>` | Before the pull request opens and after any sibling merge, `git fetch origin` and merge `origin/main` into the branch when it moved. Never rebase a pushed branch |

## Overrides

None.

## Repository notes

- This repository is a fork of `DrewThomasson/ebook2audiobook`. Branches are cut from the
  fork's `main`, and pull requests target the fork, never the upstream repository.
- `.claude/worktrees/` is ignored by git.
