---
name: new-branch
description: >-
  Start a working branch from a freshly fetched default branch, in a worktree of its own.
  Use whenever new work needs a branch - "start a branch", "branch for issue N", "let's work
  on X" - and before the first edit of any task that does not already have one.
---

# New Branch

Every branch starts from the current default branch on the remote, never from whatever
happens to be checked out. Branching off the previous task's branch silently drags its
commits into the next pull request.

Every branch also gets a worktree of its own. The main checkout is a read-only reference
that concurrent sessions share, and a harness that launches worktrees may refuse
`git checkout -b` and `git switch -c` as a change to shared state, so a branch is never cut
in place.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped.

| Placeholder | Meaning |
| --- | --- |
| `<default-branch>` | The branch every new branch is cut from, such as `main` |
| `<remote>` | The remote that holds it, usually `origin` |
| `<worktree-script>` | The command or tool that fetches the remote, adds a worktree on a new branch cut from `<remote>/<default-branch>`, and prints the worktree's path |
| `<enter-worktree-note>` | How the session starts working inside the worktree, because a `cd` in a shell may not move it |
| `<branch-types>` | The branch type prefixes the history uses |
| `<branch-name-form>` | The branch name form, such as `<type>/issue-<N>-<slug>` with an issue and `<type>/<slug>` without |
| `<branch-age-note>` | The note on refreshing a branch that has fallen behind, and where it is checked |

## 1. Protect existing work

Run `git status` first.

- Clean: continue.
- Uncommitted work that belongs to the current branch: commit it there before leaving.
- Uncommitted work that belongs to the new branch: carry it over with a tagged stash, which
  every worktree shares. Run `git stash push -u -m "<unique-tag>"` here, before section 2,
  and capture its SHA from `git stash list --format='%H %gs'`. Run `git stash apply <sha>`
  inside the new worktree only after section 3 passes (for a stacked branch, after the reset
  in "Overriding the base"). If the apply fails outright, keep the entry and stop. If it
  conflicts, resolve it there and keep the entry until the resolved work is in place. Once
  the work is in place, with or without a conflict, read `git stash list` again, find the
  entry by its tag, and drop it with `git stash drop stash@{<n>}` right away. A SHA is not
  accepted by `git stash drop`, and another session can shift the indexes between a read
  and a drop.

Never use a bare `git stash` or `git stash pop`. The stash stack is shared with the main
checkout and every other worktree, so another session's entry can be popped.

## 2. Branch from the default branch in a new worktree

Run `<worktree-script>` with the branch name in `<branch-name-form>`. It fetches the remote
and cuts the new branch from `<remote>/<default-branch>`. Then start working from the
worktree's path as `<enter-worktree-note>` says. Until the session is in the worktree, its
edits may stay blocked.

`<branch-types>` matches the existing history. Include the issue number when one exists.

## 3. Verify the base

```bash
git log --oneline <remote>/<default-branch>..HEAD
```

It must print nothing. (A stacked branch checks against `<remote>/<parent>` instead, per
"Overriding the base".) Any commit listed means the branch was cut from the wrong base, and
those commits will land in the pull request. Fix it before editing: start a fresh worktree
under a new name, enter it, and move the work over.

## 4. Keep it current

The base is current only on the day the branch is cut. Run `<branch-age-note>` at each point
it says it is checked, stacked branches included.

## Overriding the base

Branch from something other than `<remote>/<default-branch>` only when the user explicitly
asks, or when the work genuinely stacks on an unmerged branch. Say which base was used and
why. `<worktree-script>` always cuts from the default branch, so to stack, run it as usual,
enter the worktree, and before the first edit move the new branch onto its parent with
`git reset --hard <remote>/<parent>`, which loses nothing while the branch holds no commits.
Push the parent first if it exists only locally. The base check in section 3 then runs
against `<remote>/<parent>`.
Open the pull request against that parent (`gh pr create --base <parent>`) so the diff stays
scoped, or against the base the parent merged into once it has. A stacked branch still runs
`<branch-age-note>`, but merges nothing for it until the parent merges.
