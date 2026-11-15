---
name: azdo-review
description: >-
  Mirror the review threads of an AZDO pull request onto the paired pull request in this
  repository as comments, and send the replies written here back to AZDO. Every write is a
  choice the user makes. Starts only when the user types /azdo-review.
disable-model-invocation: true
---

# AZDO Review

Carries a review across the tunnel in both directions: the threads reviewers open on an AZDO
pull request land on the paired pull request here as comments, and a reply written here goes
back onto the AZDO thread. Only the user starts it, by typing `/azdo-review`; the frontmatter
keeps the model from starting it. Nothing stands in for it: no other skill, loop, schedule, or
session mirrors a thread, sends a reply, or records a pair on its own.

Inside a run, every write is an option the user picks through `AskUserQuestion`, per
`<asking-note>`. Writing nothing is always one of the choices. The writes are:

- recording a pair in the pairs file;
- posting mirrored threads as comments on the pull request here;
- sending a reply to an AZDO thread.

Payloads are written to the scratchpad with the Write tool and passed by path, per
`<shell-text-note>`.

Every comment this skill writes, a mirrored thread and a reply alike, follows
`<review-comment-rules>`.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments, state files, and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing payloads and comments to a command as files |
| `<review-comment-rules>` | The rules every written review comment follows: its order and what it quotes |
| `<tunnel-command>` | The command that dispatches an operation through the tunnel to AZDO: its arguments, how it takes a payload, the ref flag and its default, the apply flag, and the lines it prints before the result |
| `<session-branch-command>` | The command that cuts a branch and worktree for a run that has none, and the branch name it takes |
| `<pairs-file>` | The file that records which AZDO pull request mirrors onto which pull request here and what has crossed, where it lives, and why no push carries it to the work side |
| `<mirror-command>` | The command that edits the pairs file and builds the mirror and the reply payloads: its `find`, `pair`, `mirror`, `replies`, and `sent` forms, their arguments, and how it commits |
| `<pr-get-op>` | The operation that reads an AZDO pull request, and that it is a read |
| `<threads-op>` | The operation that reads the threads of an AZDO pull request |
| `<comment-op>` | The operation that writes a comment or a reply: its payloads for a new thread and for a reply, what it refuses, and the result field that proves the write |
| `<delete-op>` | The operation that removes a duplicate comment: its payload and dry run |
| `<text-pass>` | The checks run over the text of a comment that crosses to the work side: the voice pass, the scan, and the rule for text that names this side's tracker, runs, or tooling |
| `<stamp-command>` | The command that stamps a payload before it is sent, if the operation needs one |
| `<apply-group-note>` | The note on how many applies the tunnel runs at once and why a burst queues |
| `<run-log>` | How a dispatched run's job log is read |
| `<sync-skill>` | The skill that merges a colleague's branch into a reference pull request, and that covers the state branch |
| `<report-note>` | Anything else the report names, such as run links |

## Starting a run

`/azdo-review <AZDO pull request id> [github=<pull request number>]`

Ask for a missing id. Tunnel dispatches go through `<tunnel-command>` on its default ref unless
the user names another ref. The pairs file and any commit belong in a worktree on a branch,
never the main checkout: `<session-branch-command>` when the run has no branch of its own.

## The pair

The pairs file, `<pairs-file>`, records which AZDO pull request mirrors onto which pull
request here, and what has crossed so far: per AZDO thread, the AZDO comment ids already posted
here or sent from here, and the ids of the comments here already sent to AZDO. Edit it only
through `<mirror-command>`, which runs locally and dispatches nothing. The file never crosses to
the work side, and the AZDO side holds nothing that points back at it.

1. Find the pair with the `find` form of `<mirror-command>`. A pair found is the one to use.
2. No pair: the user names the pull request here (`github=`), or is asked for it. Confirm both
   with `<pr-get-op>` (a read) and a read of the pull request here, then ask whether to record
   the pair with the `pair` form. Pairing either side with a second partner is refused.

## AZDO to here

1. Read the threads, a read, and keep the result: `<threads-op>` with the AZDO pull request id,
   saved to `<scratchpad>/threads.json`.
2. Dry-run the mirror with the `mirror` form of `<mirror-command>`. It lists, per thread, the
   comments people wrote that the pair has not seen (system comments such as votes and policy
   changes never cross) and the Markdown it would post: the thread's file and line, each
   comment's author, time and text, a line saying how to answer, and a marker on the last line
   holding the ids. Show the user the bodies.
3. Ask whether to post them. On a yes, run the same command with its apply flag. Each thread
   becomes one comment on the pull request here, posted as the user, and the pairs file records
   the ids as each one lands. Nothing here is checked for banned terms: a comment on this side
   may name anything.

## Here to AZDO

Only comments cross. The pull request description here never does: it is written for this
side, names this side's runs, links, and process, and the AZDO pull request has its own
description. No operation reads a body here and writes it there, and a reply never quotes one.

A review thread here that no longer applies to the current changeset is deleted, never resolved
and left. GitHub marks such a thread outdated (its `line` reads null) once the lines it sat on
are gone; a thread can also stop applying while its anchor survives, when the user says so.
Either way the comment's text is written to the scratchpad first, then the comment is deleted
through the comments endpoint of the pull request. A resolved thread still exists, and a pass
that reads threads to send them across could pick it up; a deleted one cannot cross by
accident. Run that sweep before any mirror pass, and after every resync of the branch.

### Review comments onto a colleague's pull request

A review written here on a reference pull request (a colleague's branch with the default
branch merged in, see `<sync-skill>`) crosses as one AZDO thread per live review comment, on
the same file and line. Only on the user's word.

1. Read the live comments of the pull request here, keeping those whose `line` is not null.
   Confirm with `<pr-get-op>` that the AZDO source commit still holds the tree the anchors
   were read on.
2. Write one `<comment-op>` payload per comment to the scratchpad, with the pull request id,
   the path, the line, and the text. Run `<text-pass>` over the texts, and stamp each with
   `<stamp-command>`.
3. Dry-run one. Its result names the thread it would open, or `alreadyOn` with the thread that
   already holds that text at that place.
4. Ask once for the set, then apply them one at a time, each dispatch on its own, output
   captured to a file. A payload is sent exactly once. Never wrap the applies in a loop that
   retries on a missing result.
5. After each apply, read what came back before the next one. The result's `threadId` is the
   proof. When the shell prints nothing, or stops after the line that names the run, the
   dispatch may still have run: read that run with its job log per `<run-log>`, or list the
   tunnel runs, or read the threads with `<threads-op>`, and only then decide. A missing result
   is not a missing thread.
6. Record the pairs in a file beside the payloads: comment id here, thread id there. That file
   is what a later pass reads, so nothing is sent twice.

`<comment-op>` refuses a new thread whose text already sits on the same file and line as an open
thread, so a resend after a lost result is caught on the server side too. When a duplicate does
land, `<delete-op>` removes it: dry-run first, which shows the text and whether it is the last
comment in its thread, then apply. `<apply-group-note>` says why a burst of dispatches queues
rather than runs together, and why a script that reads an empty shell as a failure will send
again while the first is still in the queue. That is how two threads land twice.

A reply is a comment on the pull request here whose first line is `azdo thread <thread id>` and
whose remaining lines are the answer. The user writes it on the pull request page, or asks for
it here, in which case the skill posts it as the user once the user approves the text.

1. Collect the replies not yet sent with the `replies` form of `<mirror-command>`. It writes one
   payload per reply (the pull request id, the thread id, and the text) and lists them with the
   comment id here and its author. A reply naming a thread the mirror never posted is skipped
   with a note.
2. Each reply crosses to the work tracker, so `<text-pass>` applies to its text: fix the text on
   the pull request here when it names this tracker, a run, or tooling, and collect again.
   Stamp each payload with `<stamp-command>`.
3. Dry-run each with `<comment-op>`. Show the thread and the text.
4. Ask whether to send, one question per reply. On a yes, rerun the same command with its apply
   flag, one at a time, per `<apply-group-note>`. A timeout after the line that names the run
   means the run was dispatched: read its job log per `<run-log>`, never resend.
5. Record what was sent from the result's `commentId` with the `sent` form of
   `<mirror-command>`, giving the AZDO pull request id, the comment id here, the thread id, and
   the AZDO comment id. This marks the AZDO comment as already on this side, so the next mirror
   does not post the reply back here as new.

## Pairs file

A run that records a pair, posts a mirror, or sends a reply changes the pairs file, and
`<mirror-command>` commits each change itself. There is nothing to commit here and no pull
request to open; `<sync-skill>` covers the state branch.

## Report

The pair, the threads mirrored with the comment ids here, the replies sent with the AZDO comment
ids, anything skipped and why, and the run links, plus `<report-note>`.
