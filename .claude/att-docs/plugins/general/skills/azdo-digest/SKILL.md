---
name: azdo-digest
description: >-
  Read a digest of what needs a look on AZDO: the pull requests waiting on you, the review
  threads you have not answered, the builds that did not succeed, and the User Stories that
  changed since the last digest. Reads only, writes nothing on either side, and runs on a
  loop when asked - "/azdo-digest", "what is waiting on me in AZDO", "/loop 30m /azdo-digest".
---

# AZDO Digest

One read of the server, reported as a short block. The digest read writes nothing on either
side, so it runs the same whatever mode the tunnel is in, needs nothing beyond its payload, and
may be started by the model or a loop as well as by the user. Anything the digest turns up is
acted on through the skill that owns the write: a reply goes through `<review-skill>`, a
failed build through `<build-issue-skill>`, a story through `<stories-skill>`. This skill
never writes.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<shell-text-note>` | The repository's note on passing payloads to a command as files |
| `<tunnel-command>` | The command that dispatches an operation through the tunnel to AZDO: its arguments, how it takes a payload, the ref flag and its default, and the lines it prints before the result |
| `<digest-op>` | The operation that reads the digest: its payload, the default window, the `since`, `until`, and `top` settings with their limits, and the result fields |
| `<review-skill>` | The skill that replies to review threads and votes |
| `<build-issue-skill>` | The skill that drafts an issue from a failed build |
| `<stories-skill>` | The skill that reads and changes User Stories |
| `<loop-interval>` | The shortest interval a loop of this skill may use, and why |

## Starting a run

`/azdo-digest [since=<ISO date and time>]`

Tunnel dispatches go through `<tunnel-command>` on its default ref unless the user names
another ref. Payloads are written to the scratchpad with the Write tool and passed by path,
per `<shell-text-note>`.

1. Pick the window. The first digest of a session reads the default window of `<digest-op>`
   unless the user gives `since`. Every later digest passes the `until` the previous one
   reported as its `since`, so nothing is read twice and nothing falls between two digests.
   Keep that stamp in the session: write it to `<scratchpad>/azdo-digest-until` after each
   read.
2. Read with `<digest-op>`, with a payload carrying the `since` stamp, or an empty payload for
   the default window. The stdout opens with the run address lines, so read from the first line
   that starts the result object.
3. Print `lines` from the result as the report, verbatim. The rest of the result carries what
   the lines summarize:
   - `pullsWaitingOnMe`: active pull requests where the token's identity is a reviewer with no
     vote, or the author with a reviewer waiting or rejecting, or the author of a pull request
     the server marks as in conflict. A draft waits on nobody. `morePulls` is true when the
     active list filled its page; raise `top` and read again, within the limit `<digest-op>`
     gives.
   - `unansweredThreads`: open threads on the identity's own or assigned pull requests whose
     last written comment is someone else's. Votes and pushes are system comments and never
     count as an answer.
   - `failedBuilds`: builds that finished in the window with any result but succeeded, each
     with its page under `web`.
   - `changedStories`: every User Story whose change date falls in the window, whatever state
     it moved to.
4. Save `until` from the result as the next `since`.

## On a loop

`/loop 30m /azdo-digest` reads every half hour and reports each time, when `<loop-interval>`
allows an interval that short; otherwise the loop uses the floor. Each tick is one job on
the shared runner pool, a few minutes of it, so the interval stays at or above
`<loop-interval>`; a loop that finds the pool busy waits for its run rather than dispatching a
second one. The loop reads and reports only. A pull request waiting, a thread unanswered, or
a build red is a line in the report, never a trigger: the user picks up the owning skill.

## Report

The `lines` block, then the run link. When a section is empty the block says so with a zero;
a digest with four zeros is still reported, so silence is never read as a read that did not
happen.
