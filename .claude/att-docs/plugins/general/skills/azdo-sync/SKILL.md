---
name: azdo-sync
description: >-
  Push a branch to an AZDO feature branch, or bring an AZDO branch's changes back as a branch
  here. Use only when the user asks for a sync. Also use to record or look up which issue
  matches which AZDO work item, to approve or complete an AZDO pull request, to check pipeline
  drift, and to watch a build.
---

# AZDO Sync

Runs only on the user's request. Never pushes to the AZDO default branch, and never pushes this
repository's default branch to a protected AZDO branch. Pulling reads the AZDO default branch
like any other branch.

Files that must not cross, such as a lock file, never cross either way: each repository resolves
its own packages. A push keeps the AZDO branch's copy, a pull lists such a file as left alone
and its branch carries the target's copy, and the link search ignores it when matching pairs.
Never propose carrying it across. `<no-cross-files>` lists them.

Every AZDO branch is readable here as a remote-tracking branch after any tunnel run, and such a
branch is never merged into a branch here. Both rules, and what the copy refuses, are in
`<mirror-note>`.

`<wiki-note>` says how the documents wiki follows AZDO, and what the check in push step 2 and
pull step 4 keeps publishable.

Payloads, commit messages, and pull request bodies are written to the scratchpad with the Write
tool and passed by path, per `<shell-text-note>`.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments, state files, and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing payloads, commit messages, and bodies to a command as files |
| `<tunnel-command>` | The command that dispatches an operation through the tunnel to AZDO: its arguments, payload, ref and runner flags, the apply and detach flags, and the lines it prints before the result |
| `<no-cross-files>` | The files that never cross, and where each shows in a result |
| `<mirror-note>` | The note on how AZDO branches are copied here and what the copy refuses |
| `<wiki-note>` | How the documents wiki follows AZDO, and the check that keeps a merge publishable |
| `<wiki-check>` | The command that runs that check, and how it is run on a pushed branch in a detached worktree |
| `<text-checks>` | The checks run over the files a push carries: the shipped-text scan, the boundary lint with its command, and what a hit names |
| `<commit-message-rules>` | What a pushed commit message, a pull request title, and a description may and may not say |
| `<stamp-command>` | The command that stamps a payload before it is sent |
| `<default-target-branch>` | The AZDO branch a push of this repository's default branch goes to, and its naming |
| `<push-op>` | The operation that pushes: the runner it needs, its payload, dry-run fields (change counts, kept files, scan hits, drift, applyRefuses), `expectedHead`, `acceptDrift`, and its pair record |
| `<pull-op>` | The operation that pulls: its payload, base resolution, dry-run fields (applied, leftAlone, onto, merged flags, conflicts), and the branch it pushes |
| `<link-op>` | The operation that searches for a pair, its depth settings, and its `link`, `closest`, `paths`, and `searched` results |
| `<drift-op>` | The standalone drift read, and the two moments it serves |
| `<pr-ops>` | The operations that create, read, vote on, and complete an AZDO pull request: their payloads, vote values, merge strategies, refusals, bypass field, and the pair a completed merge records |
| `<changes-op>` | The operation that reads the files an AZDO pull request changes, with content |
| `<pairs-command>` | The command that lists, finds, records, adds, and removes branch pairs and work-item pairs, and restores the state branch |
| `<state-branch-note>` | Where the pair records live, why they are not on the default branch, how they are protected and restored, the hidden ref that tracks the branch head and how a read restores the branch from it, and what a branch cleanup must leave out |
| `<new-branch-note>` | How a working branch is cut and stacked on a pulled branch, its branch age check, and which branches take that check differently |
| `<mergeability-note>` | How a conflict in an applied file is settled |
| `<merge-checks>` | The type, declaration, and lint commands run over a merge result |
| `<review-skill>` | The skill that carries review comments across, and its rule for deleting outdated threads |
| `<stories-skill>` | The skill that moves a story either way |
| `<pipeline-drift-op>` | The operation that compares registered build definitions with the committed YAML, its payload, and its result fields |
| `<pipeline-register-note>` | Who regenerates the YAML and registers definitions |
| `<queue-op>` | The operation that queues a build |
| `<build-watch-op>` | The operation that watches a build: its payload, interval and budget settings, its detach output, and its result |
| `<run-log>` | How a dispatched run's job log is read |
| `<catchup-note>` | The ledger and the one watcher a session uses for runs: how a run id is recorded and waited on, and how its tally reads a build watch |

## Push

1. Confirm the source ref (a pushed branch) and the AZDO target branch. Refuse the default
   branch. A push of this repository's default branch goes to `<default-target-branch>` and
   needs no confirmation: the request to update AZDO is the answer to every question in steps
   1 to 7, including the apply and the pull request into the AZDO default branch. No AZDO
   branch name says `sync`.
2. Run `<text-checks>` over the files the branch changed and fix what it reports. The runner
   scans the whole export again; this pass catches problems before a dispatch. Last, run
   `<wiki-check>` and fix what it reports, so the documents reach AZDO as pages the wiki can
   carry.
3. Draft the commit message under `<commit-message-rules>`. It describes the work being pushed,
   read from the changes since the target's last link, and never mentions syncing, pushing, or
   updating AZDO. The pull request title and description follow the same rule. Write the payload
   to the scratchpad with the Write tool, with the target branch and the message. Stamp it with
   `<stamp-command>`, on its own or chained with `&&` before the dry run in the same call.
4. Dry-run `<push-op>` with the source as the ref, on the runner it needs. Show the user the change counts, the kept
   files, the rendered ignore file, the scan hits, `drift`, `driftLoses`, and `applyRefuses`.
   Stop when `applyRefuses` is set.
   The dry run is also the drift check. `drift` reads what the AZDO branch the commit lands on
   holds beyond its last recorded export: the target branch when it is already on the server,
   the AZDO default branch when the push creates it. `drift.dropped` lists AZDO-side edits the
   push would write over, `drift.carried` lists edits the source already holds, and
   `drift.rendered` lists rendered-file changes, which a push always rewrites. `driftLoses` is
   true when either of the first and last is non-empty, and the apply refuses while it holds
   unless the payload carries `acceptDrift`. When it is true, show the user the dropped and
   rendered paths, and bring the edits back with a pull of the same branch before pushing
   again; the pull resolves the same base `drift.base` names, with no `base` in its payload, the
   default branch included. The user can instead say to send
   anyway; then add `"acceptDrift": true` to the payload, restamp, and say so in the AZDO pull
   request description. A `drift` that carries `error` in place of a base did not resolve one
   (`<link-op>` names the fix), and it is a stop, not a pass.
5. Add `"expectedHead": "<targetHead from the dry run>"` (omit it when the branch is new),
   restamp, and apply once the user says yes through `AskUserQuestion`, per `<asking-note>`.
   The apply reads the drift again against the same base, so a branch that moved after the dry
   run is refused there.
6. The apply records its own `link` as the branch's pair: `pair.recorded` true means it is on
   the state branch (see Branch pairs below), and nothing is committed here. `pair.recorded`
   false carries `pair.error`; record it by hand with `<pairs-command>` from the result's
   `link`, and never resend the apply. An error saying the state branch is not on the server
   needs the restore form of `<pairs-command>` before that hand record. Then confirm the pair
   with `<pairs-command>`: the push is not finished until it prints this push's source commit.
7. On request, and always for a push of this repository's default branch, open the AZDO pull
   request with `<pr-ops>`.

A push needs no separate `<drift-op>`. That operation is the standalone read for two other
moments: checking a base the pull could not resolve on its own, and reading the new AZDO default
branch head after a pull request completes. It only reads and needs no stamp.

A timeout in `<tunnel-command>` after the line that names the run means the run was dispatched:
read its job log per `<run-log>`, and never resend an apply.

## Approve and complete

Both run only when the user asks for them by name, each one its own `AskUserQuestion` before the
apply. Neither takes any prose, so the stamp is the only text check.

- The vote operation in `<pr-ops>` casts the token holder's own vote. The dry run shows the vote
  the identity holds now.
- The complete operation in `<pr-ops>` merges an active pull request into its target, with the
  expected source commit read from the pull request read. The dry run reports `applyRefuses`:
  the pull request is not active, its merge status is not `succeeded`, its source head moved past
  the expected commit, or a required reviewer has not approved. Stop on any of them; vote first
  when the last one names the token holder. Branch policies are not in `applyRefuses`; the apply
  fails on one with an error naming a policy override. The bypass field overrides them, recorded
  on the pull request, and goes in the payload only when the user says to override for that pull
  request.

After a completed merge into the AZDO default branch, the apply records the pair for that branch
itself: the commit here the source branch's pair names, with the AZDO merge commit, so the next
pull or drift check needs no link search. The dry run's `mainPairOnApply` and the apply's
`mainPair` say what it wrote or why it skipped: the source branch has no pair, its pair came from
a pull (the commit here sits on a pulled branch that the default branch never merged), no pull
request here merged that commit into the default branch, or the server had not finished the
merge. A skip is reported to the user and recorded by hand with `<pairs-command>` only once its
cause is gone.

## Pull

1. Confirm the AZDO branch. `<pull-op>` resolves its base the way `<drift-op>` does: the pair for
   that branch on the state branch, or else the newest commit of the branch holding any recorded
   pair's export, paired with that pair's commit here. A `base` in the payload overrides both.
   The plan's `baseFrom` and `baseRead` say which it took.
   - Only when the dry run refuses because no commit of the branch holds a recorded export: find
     a pair with `<link-op>` on the AZDO default branch. It reads both histories to `depth` and
     returns `link`, the newest pair holding the same exported files.
   - `link` null: show the user `closest`: its pair, the `paths` where the pair differs (these
     can conflict on pull), and `headPaths`, roughly what the pull brings back. Show the dates
     `searched` reached too. Rerun with a larger `depth` when the oldest commit read is newer
     than the last sync, otherwise ask the user through `AskUserQuestion` whether to base on
     `closest`.
   - Record the pair with `<pairs-command>`, so later pulls find it. It lands on the state
     branch at once; no pull request is needed.
2. Dry-run `<pull-op>`. Show `applied`, `leftAlone`, and `gitignoreChanged`. A change that does
   not apply onto the base pair fails with the paths listed; report them.
   The operation builds the twin first: the base pair's commit here plus the AZDO changes, with
   every path that does not cross, and the ignore file, taken from `onto`, so it holds the AZDO
   head's exported files and differs from `onto` in exported files only; `keptFromOnto` lists
   those paths. It then applies the same changes onto the head of the dispatched ref, reported
   as `onto` and `ontoRef`. The dispatch carries the ref `<pull-op>` requires, and the operation
   refuses any other ref, dry run included.
   - `mergedOntoHead: true`: the branch head is a merge whose first parent is `onto` and whose
     second is `twin`. `changedFromOnto` lists what a pull request against `ontoRef` shows;
     check it matches `applied`.
   - `mergedOntoHead: false`: the branch head is the twin alone, and `ontoConflicts` names the
     paths that did not apply onto `onto`. A pull request from it against the default branch
     reads as reverting every exported file the default branch changed since the base pair, so
     step 5 merges the default branch into its working branch before the pull request opens.
3. Apply once the user says yes through `AskUserQuestion`. The operation pushes a pulled branch
   named for the AZDO branch and a short commit id. The apply records the operation's `link` as
   the branch's pair, marked as from a pull, and reports it as `pair`. The link names the twin
   and not the merge, since only the twin holds exactly the AZDO side's exported files. Keep the
   pulled branch until that pair is superseded: a squash merge here leaves the twin reachable
   only through it.
4. When `applied` lists a file under the documents folder, run `<wiki-check>` on the pushed
   branch first. The AZDO repository takes names its wiki refuses, so a page added there can fail
   it. Name what it reports in the pull request body.
5. Open the pull request from a working branch stacked on the pulled branch, cut per
   `<new-branch-note>`, so the pulled branch stays as the operation pushed it whatever a later
   branch age gate merges. Before the push, run the branch age check from `<new-branch-note>`.
   When the check prints anything, or the pull reported `mergedOntoHead: false`, which needs the
   merge whatever the check says, merge the default branch into it. A conflicted file outside
   `applied` takes the default branch's side, since the branch holds an older copy of it; paths
   that do not cross already match and do not conflict; one in `applied` is settled per
   `<mergeability-note>`. After a merge, run `<wiki-check>` again on the working branch, since the
   merge can bring in pages the pull did not touch, and name its result in the pull request body
   in place of step 4's. Push the working branch, open the pull request from it against the
   default branch, and link it. Targeting the default branch, it is not a stacked branch for the
   gate. When `gitignoreChanged` is true, say the ignore-file change needs a hand merge.

## Merge main into a colleague's branch

The tunnel has no merge operation. When a colleague's AZDO pull request conflicts with the
default branch, the route is a pull, a merge here, and a push back, and the branch is theirs the
whole way: the merge brings the default branch in and settles conflicts, and it changes nothing
else. A lint error or a type error in the result is left as it is and goes into the review as a
comment. Most of what differs from the default branch in their files is not their edit at all:
the branch was cut from an older default branch, so a method added since, a rewrite that vetting
made, a rule that landed later, all read as removals on their side and are nothing they did. The
push lands one commit authored by the token holder on their branch, so anything beyond the merge
in that commit reads as an edit to their work made without asking.

1. Pull the branch here per steps 1 to 4 of the Pull section, which leave the merge and the pull
   request to the steps below, with the link search first only when the pull cannot resolve a
   base. When `gitignoreChanged` is true, say the ignore-file change needs a hand merge. A
   `closest` pair is fine when the paths it differs on are outside the colleague's files.
2. Read the changed files with `<changes-op>`, so the colleague's own files are known. When the
   pull reported `mergedOntoHead: true`, the operation already merged the default branch with no
   conflict: branch a working branch from the pulled branch, check `changedFromOnto` against the
   changed files, and go to step 4. Otherwise merge the default branch into that branch on a
   working branch here.
3. Settle each conflict, and only the conflicts:
   - A file outside the colleague's changed files takes the default branch's side. The branch
     holds an older copy of it, and the default branch has whatever vetting or fixes happened
     since.
   - A file in the changed files is rebuilt as the default branch's version plus the diff
     `<changes-op>` reports with content (merge base to source), with a three-way file merge.
     That reapplies exactly what the colleague changed and nothing the branch merely inherited. A
     hunk that still conflicts is the one place the merge decides, and it decides for the default
     branch when the colleague's side is a copy-paste or doubling artifact, and for the colleague
     otherwise. Their diff is the reported change, never the raw difference from the default
     branch.
   - A file that the default branch no longer holds but the branch still does, and the reverse, is
     settled the same way: outside the changed files, the default branch wins.
4. Run `<merge-checks>` over the result, and read the output without acting on it. A failure is
   reported in the review with what caused it: a stale base (their file misses something the
   default branch added since, which is the common case and not their doing) or an edit of
   theirs. Neither is fixed in the merge. Nothing here restores a method, wraps an assertion, or
   renames a title.
5. Push the working branch here and open a pull request against the default branch, not for
   merging, as the reference copy the review is written on. It skips the branch age gate, per
   `<new-branch-note>`: the pull request is never merged, and the push in step 6 carries one merge
   and nothing else. The pull's apply already recorded its pair. Its description stays here: only
   review comments ever cross to the AZDO pull request, through `<review-skill>`, and only when
   the user starts that.
6. Push the working branch onto the colleague's AZDO branch with `<push-op>`, dry run first, with
   `expectedHead` set to the pulled head, and only after the user says yes through
   `AskUserQuestion`. The drift check bases on the pair the pull recorded, and the push's apply
   records its own pair over it.

A branch the colleague or the user cleans up after the push comes back through the same pull,
based on the last recorded pair, and merges onto the same working branch, so the review's
comments keep their anchors. After the merge, a comment whose lines are gone (marked outdated) or
that the user says no longer applies is deleted, not resolved, per `<review-skill>`, so nothing
stale can cross later.

## Branch pairs

`<state-branch-note>` says where the pair records live and how they are protected: the branch
holds only those files, takes one fast-forward commit per write, and is never merged, forced, or
pushed to AZDO. Every read and write fetches it; a write that finds the branch moved reads it
again and tries once more. The copies on the default branch are never read: a missing branch
fails every read and write, naming the restore form of `<pairs-command>`. Never edit the copies on
the default branch, and never open a pull request to change a pair.

The branch is never deleted, and a cleanup of every remote branch but the default one lists its
branches by name and leaves this one out. When a run reports the branch and its hidden ref
missing, the restore form puts the branch back at the head the activity log says it was deleted
at; then rerun the operation. Restoring from the default branch's copies starts the branch over,
which drops every pair since they were made, so it is only for a branch that never existed. A
deletion that went unnoticed leaves later syncs basing on old pairs, so after a restore read the
list of branch pairs against the AZDO branches the pushes made.

- Push, pull, and complete applies write their own pairs, each marked with how it was recorded.
- `<pairs-command>` prints every branch pair, prints one, and records one by hand. That is for a
  pair the link search found, or an apply whose `pair` reports `recorded: false`.

## Work item pairs

The work-item pair record says which issue here matches which AZDO work item. It lives with the other
pair records and is edited only through `<pairs-command>`, which runs locally and dispatches
nothing. Moving a story either way is `<stories-skill>`, which runs only when the user asks for
it; this skill never creates, updates, or pairs a story on its own.

- Find by issue or by work item before creating a work item for an issue or an issue for a work
  item. A pair found means no second item is created. The existing item changes only when the user
  picks that change.
- Add a pair once a create has applied and the user chooses to record it, naming the side the
  pair started from. Adding the same pair again changes nothing; pairing either side with a
  different partner is refused, so removing the pair comes first when one was recorded wrong.
- Add and remove commit to the state branch themselves; there is nothing to commit here. Comment
  the work item id onto the issue when the user asks for it.
- Listing prints every pair. The pull request create operation takes the work item ids for its
  work items field from here.

## Pipeline drift

`<pipeline-drift-op>` compares the build definitions registered on the server with the committed
YAML. It reads both and writes nothing, so it runs in either mode and needs no stamp.

The result lists `missing` (a generated YAML with no definition of its name), `extra` (a
definition in a suite's folder, or carrying its name prefix, that no YAML names), and `drifted` (a
definition whose YAML path, folder, repository, queue, or status differ from what registering
writes, or that holds definition-level variables, variable groups, or trigger overrides the YAML
does not own). `clean` is true when all three are empty. A definition that matches on every
checked field is not listed.

The tree side is the user's, per `<pipeline-register-note>`. Report the result and stop; never run
the generator or the register apply on this skill's own initiative.

## Build watch

`<build-watch-op>` sits on one AZDO build until it completes and reports its result, the tasks
that failed, and the tests that failed. It reads and writes nothing on the server, so it runs in
either mode and needs no stamp. The tunnel run ends when the build does and concludes the way the
build did, so the session waits on it through its ledger like any other run, per
`<catchup-note>`:

1. Queue the build with `<queue-op>` (an apply, stamped like any write) and take the `id` from its
   result. A build already queued or finished is watched by its id from the run list.
2. Dispatch the watch detached, so the shell comes back once the run exists. It prints the run
   link and, on its last line, the run id.
3. Record that run id in the ledger and wait on it with the one watcher the session runs.

The ledger's tally reads the watch the way it reads a test run: overall result, test count, passed
and failed counts, and runtime, then one line per failed test title and one line per failed task
with its job, its result, and the error the task logged. A build the watch could not see finish
inside its budget prints a timeout line, which the tally reports as having hit the run budget.

The watch's interval setting (ten seconds or more, thirty by default) sets how often the build is
read, and its budget setting (at most 120 minutes, sixty by default) how long the watch stays on
it. The result block carries the same summary as JSON, with the failed tasks' log ids for the log
read.
