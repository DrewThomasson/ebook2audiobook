---
name: wyatt-review-phase-1
description: >-
  Review a junior engineer's pull request at high effort and leave mentoring review comments
  on it, never touching their code. Each comment says what the finding is, what goes wrong as
  the code stands, and walks them through the fix step by step with code blocks, in a kind
  teaching voice that explains the deeper machinery rather than assuming they know it. Every
  fix is first made and proven in a throwaway branch, which is deleted afterward. Starts only
  when the user asks for it by name.
disable-model-invocation: true
---

# Wyatt Review, Phase 1

`/wyatt-review-phase-1 <pull request number>`

The author is a junior engineer. Their pull requests reach this repository as reference
copies of work done on the work side. A review here is teaching: they should finish each
comment knowing what is wrong, why it matters on a real run, and exactly what to type to fix
it. The method is in `<mentoring-notes>`; this skill adds the rules for leaving their code
alone.

Ask for the number when it is missing. Confirm it and say which pull request is being
reviewed before starting, per the first section of `<mentoring-notes>`. That step also reads
the head commit every finding is checked against.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. The extension's own frontmatter carries `disable-model-invocation:
true` too, so the model cannot start it unasked.

| Placeholder | Meaning |
| --- | --- |
| `<mentoring-notes>` | The shared note that holds the review method: confirming the pull request, finding and verifying findings, the comment shape and voice, the background to explain, checking a comment, and posting a review. Its comment shape numbers the parts, with the proven fix steps as part 5 and how to tell the fix worked as part 6 |
| `<phase-2-skill>` | The second-round skill, if the repository has one, and the command that starts it |
| `<proving-branch-form>` | The proving branch's name form, its suffix rule when a name is taken, and the worktree folder |
| `<proving-worktree-note>` | How the proving worktree is cut from the author's head commit (never with the script that prunes branches), including the command that fetches the pull request's head from the remote and leaves it in `FETCH_HEAD`, and how dependencies are linked in |
| `<static-checks>` | The command that runs the repository's static checks, and the type and lint commands |
| `<fix-rules>` | The rules a real fix follows: lint rules, shared helpers, and the assertion rules that stop a fix from weakening a test |
| `<run-dispatch>` | The command that dispatches the affected specs on a branch, the options that narrow it to the rows a fix touches, and where the failure context is read |
| `<run-rules>` | The repository's rules for runs and reruns |
| `<asking-note>` | How a question is put to the user |
| `<sync-route>` | The route that carries approved comments to the work side, and the ask that triggers it |
| `<ready-hook-note>` | Any hook that fires after a review and asks for a ready label or ledger row, which does not apply to the author's pull request |

## Hands off their code

This skill leaves review comments on their pull request and changes nothing they own. Every
fix it describes is first made and proven in a throwaway branch (section 3), and that code is
then thrown away: the author gets the walkthrough and makes the fix themselves, which is how
they learn it. When the user wants the second round, the user starts `<phase-2-skill>`.

- No edits, commits, or pushes to their branch: not whitespace, not a tag, not a lint fix,
  not a red static check. Red checks become findings, or a summary line when their branch is
  only behind the default branch.
- The proving branch is never pushed to their branch, never opened as a pull request, and
  never shown to them as code to merge.
- No automatic fix mode of the code review skill, no self-review fix loop, no ready label,
  and no entry in any pull request ledger the repository keeps (`<ready-hook-note>`).
- The comments land on the pull request in this repository only. Nothing crosses to the work
  side from this skill. The user reads and approves them first, then asks for them to be
  sent, and `<sync-route>` carries them over only on that ask.
- `<ready-hook-note>` is for the session's own pull requests; on theirs, ignore it.

## 1. Cut the proving branch

Cut it from their head commit in a worktree outside the checkout, per
`<proving-worktree-note>`. Section 2 settles claims about types and lint in it, and section 3
makes its fixes there.

`<proof>` is the branch name from `<proving-branch-form>`, with its suffix when that name is
taken, and `<dir>` is the worktree folder from `<proving-branch-form>` with the same suffix. A
suffix is free when the remote has no such branch, no local branch has the name, and
the worktree folder does not exist:

```bash
git ls-remote origin refs/heads/<proof>
git branch --list <proof>
```

Fetch the pull request's head as `<proving-worktree-note>` says, then:

```bash
git worktree add -b <proof> <dir> FETCH_HEAD
```

## 2. Find the findings

Run the review and verify each finding, per "Finding and verifying findings" in
`<mentoring-notes>`. Run the type and lint commands from `<static-checks>` in the proving
worktree before any commit lands there, so the checks read the author's code as it stands, and run
the full static checks there once too: its result at their head is the baseline section 3
compares each draft against.

## 3. Prove every fix before it is described

A fix written from a first guess is not a fix. Each one goes through as many drafts as it
takes, the way any change here does, and only the version that passes becomes the steps in
the comment.

The fixes stack on one branch in the order the comments will be posted, so each fix is proven
on top of the ones before it. The comments build on each other the same way: the summary tells
the author to apply the comments in order, and a comment whose fix leans on an earlier one names
that comment in a sentence.

For each finding, in the proving worktree:

1. Make the fix and commit it, under `<fix-rules>`. A fix that only works by weakening an
   assertion is not a fix to teach. A redraft is a new commit on top, never an amend, since
   the branch may already be pushed.
2. Run the static checks. A red result means another draft, except for a check that was
   already red in section 2's baseline for a reason that is not their edit: that is their
   branch being behind the default branch, and it stays the one summary line "Hands off their
   code" describes.
3. When the fix changes what a test does at run time, push the branch and dispatch the
   affected specs on it with `<run-dispatch>`, under `<run-rules>`. Read each failed test's
   failure context before the next draft, and rerun only the failed titles. Keep drafting
   until the tests the fix touches pass, then record the counts.
4. A finding whose fix cannot be made to pass, or that needs the user's call, goes to the
   user per `<asking-note>` before any comment describes it.

The comment's steps and code blocks are copied from the fix's whole diff on the branch, every
draft of it together, not retyped, so what the author is told to write is what passed.

## 4. Write one comment per finding

Follow "The comment shape", its voice rules, and "Background to explain, never assume" in
`<mentoring-notes>`.

Part 5 carries the proven fix for them to type. Part 6 keeps its sentence on how they can tell
it worked, then says how the fix was proven: the static checks, or the run's counts (never a
link to the run). When one suggestion block replaces exactly the anchored lines, add it at the
end of the comment; it shows the lines for them to copy.

## 5. Check every comment

Per "Checking a comment" in `<mentoring-notes>`: the text scan, the humanizer pass, and a
fresh scan after any edit.

## 6. Post the review

Per "Posting a review" in `<mentoring-notes>`.

## 7. Throw the proving code away

Once the review is posted and every run dispatched on the branch has finished:

```bash
git push origin --delete <proof>
git worktree remove --force <dir>
git branch -D <proof>
```

The first line applies only when the branch was pushed. The branch never reaches the author,
and no later round builds on it.

## 8. Report back

Tell the user the review is posted, how many findings went up, and the bold line of each, most
serious first, with how each fix was proven (static checks only, or a run and its counts).
Name any finding dropped in verification and why, and any red check set aside as a
branch-behind note. Say that the proving branch is deleted. Name the findings that sit in the
summary body: they stay in this repository and cannot cross by `<sync-route>`. Say that the
comments are in this repository only and wait for the user's approval; nothing goes to the
work side until the user asks for it.
