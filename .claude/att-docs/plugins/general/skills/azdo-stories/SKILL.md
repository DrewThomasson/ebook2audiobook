---
name: azdo-stories
description: >-
  Migrate named issues to AZDO User Stories, or named User Stories to issues, and follow a
  merged pull request through to its paired story. Every write is a choice the user makes. Use
  when the user asks to pair, migrate, or follow named issues, User Stories, or pull requests -
  "/azdo-stories to-azdo 5016 5017", "pair issues 5016 to 5043 with AZDO stories", "move story
  1234 over here".
---

# AZDO Stories

Moves user stories between issues in this repository's tracker and User Stories on AZDO, for
the ids the user names, in the direction the user names. Once a pull request that closed a
paired issue has merged and reached AZDO, follows it through to the story, for the pull
requests the user names.

The user curates AZDO by hand, so nothing moves unless the user asks for it. A run starts when
the user types `/azdo-stories` or asks a session in words for a migration, a pairing, or a
follow, and the session then starts the skill for the ids that request names. Nothing else
starts it: no skill, loop, schedule, or session dispatches the story operations, changes a
paired item, or records a pair on its own initiative. A change to an issue or a story never
starts a migration.

One change crosses without a run: when a session sees an issue carrying the paired label
close, it closes the paired story without a commit comment and without asking, which is the
user's standing answer. The steps are in `<paired-note>`. Following a merged pull request
through, below, is separate: it is the user's pick each time.

Inside a run, every write is an option the user picks, per `<asking-note>`. No write follows
from the step before it. Writing nothing is always one of the choices, and a dismissed
question writes nothing. The writes are:

- creating a story, or updating a paired one, and which of its fields;
- creating an issue, or updating a paired one;
- recording a pair in the pairs file;
- commenting the story id onto the issue;
- moving a paired story to a closing state, and commenting the AZDO commit onto it, after the
  pull request that closed its issue merged.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments, payload forms, and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing payloads, issue bodies, and comments to a command as files |
| `<tunnel-command>` | The command that dispatches an operation through the tunnel to AZDO: its arguments, how it takes a payload, the ref flag and its default, the apply flag, the largest payload file a dispatch can carry, and the lines it prints before the result |
| `<story-ops>` | The three operations, each with its payload and result: to AZDO (create or update stories, as a batch), to the tracker (read stories), and follow (state change and commit comment on a paired story). It names the batch limit (items per batch and stories per read), the item fields, how a backslash in an area or iteration path is written in a payload, the read-only query that lists open items with their iteration paths, and the follow payload's depth with its default and maximum, its default state, and the states it accepts |
| `<stamp-command>` | The command that stamps a payload for the write operations, and the rule that a changed file is stamped and dry-run again |
| `<pairs-command>` | The command that finds, adds, and removes a pair, the work item type a pair records (User Story), the origin values, where the pairs file lives, how a change to it is committed, and how it keeps the paired label on the issue |
| `<paired-note>` | The note on closing a paired story when its issue closes, and the paired label's name |
| `<area-paths>` | The table from each suite to its AZDO area path, the area to offer for tooling or cross-suite work, and how the suite is read from an issue title or a story area |
| `<iteration-rule>` | How the iteration path is chosen: the sprint name form, how the current month's sprint is read off the open items, which paths are never the default, and when to stop and ask |
| `<text-rules>` | The rules for text written to AZDO: the title, the allowed HTML, what it must not carry, and the prose pass |
| `<issue-conventions>` | The create-issue conventions this repository sets: the title shape, the labels, the body sections, and how the suite is chosen |
| `<issue-labels>` | The repository's note on which labels exist and the read-back after a create |
| `<sync-skill>` | The skill that pushes a branch to AZDO, used when a merge has not reached it |
| `<run-log-note>` | How to read a dispatched run's job log after a timeout, so a dispatched batch is never sent twice |
| `<branch-note>` | The worktree and branch the run works in, kept off the main checkout, and the branch name to use when the run has none |

## Starting a run

`/azdo-stories to-azdo <issue>... [area=<path>] [iteration=<path>]`

`/azdo-stories to-github <story id>...`

`/azdo-stories follow <pull request>... [state=<state>]`

Ask for a missing direction or id list. The area path comes from the issue's suite, per
`<area-paths>`, unless the run names one. The iteration path is not asked for: an issue to
story run uses the sprint for the current month and year, per `<iteration-rule>`, unless the
run names `iteration=<path>`. The run asks only when that lookup finds no single path.

Tunnel dispatches go through `<tunnel-command>` on its default ref unless the user names
another ref. The run works in the worktree and branch `<branch-note>` names.

## Issue to User Story

1. Read each issue with `gh issue view <N> --json number,title,body,labels,state`, and look up
   its pair with `<pairs-command>`.
2. For a paired issue, read the story with the to-tracker read in `<story-ops>`, which needs
   no stamp. Keep its `rev`.
3. Draft the AZDO text under `<text-rules>`:
   - The title is the issue title, less anything naming this tracker, a run, or tooling.
     Existing stories match their issues by exact title, so change nothing else.
   - The description and acceptance criteria are plain HTML. They carry no issue or pull
     request numbers, no links to this tracker or its runs, and no skill or tool names. They
     are written in a plain tester voice.
   - Run the prose pass over the text.
4. Show the drafts. For a paired story, show each drafted field beside its current value.
5. Ask what to write, one question per item:
   - Unpaired: create the story as drafted, change the draft, or skip. Show the area path the
     suite gives it and the resolved iteration path. A parent id, tags, board column, rank, or
     state goes in only when the user names it.
   - Paired: which fields to update (title, description, acceptance criteria), or none. A
     paired issue never gets a second story.
6. Only after every item's question from step 5 has an answer, write one batch payload per
   `<shell-text-note>`: one item per issue the user chose to write, each holding only the
   fields the user picked. Skipped issues are left out. The item fields are in `<story-ops>`,
   and the batch carries nothing beside `items`. For an update item, the operation sends only
   the named fields whose values differ, and the item carries the rev kept in step 2; a stale
   rev is never raised by hand. A batch stays within the item limit in `<story-ops>`, and the
   payload file stays under the size `<tunnel-command>` names; split a larger run into several
   batches. Stamp the
   file once with `<stamp-command>`, then dry-run it once. The plan's `items` carries one
   entry per item, by `index` in the order written, with its own `applyRefuses`, `sameTitle`,
   and for an update `changes` and `unchanged`. Show each one.
   - A batch that names one story twice, or gives two items one title, is refused before the
     dry-run sends anything. Fix the file and restamp.
   - `sameTitle` lists another story with an item's title, which also sets that item's
     `applyRefuses`. Ask per item whether to pair the issue with an unpaired story from that
     list (no AZDO write, and the item leaves the batch), write anyway (the duplicate-title
     flag on that item), or skip it (the item leaves the batch).
   - The dry-run does not check that an area exists: a path that does not exist is refused
     at apply, while the rest of the batch still goes out.
   - Any other `applyRefuses`: that item leaves the batch; say why. A stale rev means the story
     changed since it was read: read it again and redraft it for a later batch.
   - An edit to the file after its stamp needs a new stamp and a new dry-run, since the stamp
     holds the payload's exact bytes.
7. Ask whether to apply the batch as the last dry-run showed it, listing its items. On a yes,
   rerun the same command with the apply flag: one dispatch for the whole batch. Items go out
   in order. An item the server refuses is recorded in the result with its `error`, the rest
   still go out, and the run ends red when any item was refused. The result's `items` hold
   each item's `result` or `error`, with `sent` and `refused` counts. Never resend the batch:
   the items that went out are already on AZDO. Redraft a refused item into a new batch of its
   own. A timeout after the run line means the run was dispatched: read its job log per
   `<run-log-note>`, never resend. Read back every story the batch created or updated in one
   call with the to-tracker read.
8. After a create, ask which records to make, allowing any mix or none:
   - record the pair with `<pairs-command>`, with the origin set to the issue;
   - comment the story id onto the issue with `gh issue comment`, per `<shell-text-note>`.

   Both stay on this side. Nothing on the story points back.

## User Story to issue

1. Read the stories with the to-tracker read in `<story-ops>` (within its limit per call),
   and look up each pair with `<pairs-command>`.
2. For a paired story, show the issue. Updating its title or body is an option, never a
   default.
3. Draft the issue under `<issue-conventions>`: the title shape, the suite and kind labels, and
   the body sections. The suite is the row in `<area-paths>` whose area the story's area is or
   sits under. A story whose area matches no row takes the suite its work belongs to. A story
   coming from AZDO does not make it a tooling issue: the tooling label in
   `<issue-conventions>` covers issues about the tunnel itself. The body cites the story as
   `AZDO User Story <id>: <url>` and carries the description, acceptance criteria, and
   comments from the `text` fields of the result. A `type` other than `User Story` is named in
   the draft.
4. Show the drafts and ask, per story: create the issue, change the draft, or skip.
5. Create it with `gh issue create` and read the labels back, per `<issue-labels>`.
6. Ask whether to record the pair with `<pairs-command>`, with the origin set to the work item.

## Follow a merged pull request through

A merged pull request is followed through when the user names it, or when a session's
after-merge steps find a closed issue carrying the paired label and the user picks a close or
a resolve, per `<paired-note>`. A merge alone changes no story. The story's board column moves
with its state, so the state change is one offer and the comment is another.

1. Read each pull request:
   `gh pr view <N> --json number,state,mergeCommit,closingIssuesReferences`. A pull request
   that is not merged stops here. Each closed issue is looked up with `<pairs-command>`; an
   unpaired issue is reported and skipped, since there is no story to follow.
2. Write the payload per `<shell-text-note>`, one file per story: the issue and the full merge
   commit id. The state is the default in `<story-ops>` unless the user named another of the
   states it accepts. The operation writes, so the payload is stamped with
   `<stamp-command>` before the dry-run with the follow operation in `<story-ops>`.
3. Read the plan. `carriedBy` lists the recorded pushes whose source holds the merge, and
   `commit` is the AZDO commit the comment names, with its page. `stateChange` and `comment`
   say what apply would write; each is null when the story already holds it. `story.rev` is
   the rev to send.
   - `applyRefuses` naming no recorded push: the merge has not reached AZDO, or the push that
     carried it was never recorded as a branch pair. Push it through `<sync-skill>` first, or
     raise `depth` when the push is older than the history read.
   - `applyRefuses` saying the story already holds both: nothing to write; report it.
4. Show the plan and ask, per story: apply the state change and the comment, the comment alone,
   change the state, or skip. The comment alone is the state set to the story's current state,
   which the operation takes only when that state is one of the states `<story-ops>` lists; a
   story in any other state gets the comment with a state change or nothing. Confirm the
   story is the one the issue means: the pairs file is the only record, and a pair recorded wrong writes to the
   wrong story.
5. Add the expected rev from `story.rev`, restamp, and apply, one call per story and one apply
   at a time. A stale rev refuses the write: dry-run again for the new rev.

A story the run moved is reported with its state, the comment id, and the AZDO commit it names.

## Pairs file

A recorded pair changes the pairs file, and `<pairs-command>` commits it itself, so there is
nothing to commit here and no pull request to open. Adding a pair also puts the paired label on
the issue and reads it back, and removing one takes it off; a label that did not land exits
non-zero, per `<paired-note>`.

## Report

For each id: the pair, and what each write did (created, the fields updated, recorded,
commented, or skipped), with the run links. Name any item that stopped on `applyRefuses`, and
why.
