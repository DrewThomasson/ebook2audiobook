---
name: manual-spec
description: >-
  Turn one manual row of a suite's manual test plan into an automated spec that runs the
  row's steps and prints the evidence for each step as a block that can be pasted straight
  under the row. Use when asked to automate a manual test case by its id, build a
  manual-equivalent spec, or produce step evidence for a manual row.
---

# Manual Spec

The input is one manual test id. The output is a committed spec named after that id, a
dispatched run, and the run's step blocks handed back for pasting into the actual-result
field. `<spec-skeleton>` names the working example to copy and the outline its shape
follows.

This skill writes evidence into the run log, never into the manual test plan document. The
tester decides what lands there.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing commit messages and pull request bodies to a command as files |
| `<default-branch>` | The branch work never commits to and pull requests merge into |
| `<manual-plan-docs>` | Where the manual test plans, functional specs, test packs, and automation notes live, and how a manual id is searched for in them |
| `<manual-id-rules>` | The shape of a manual id, the spec file name and folder it gets, and the test tag and describe naming that carries the id |
| `<spec-skeleton>` | The working example spec to copy and the reference outline of its shape |
| `<data-lookup>` | The skill or note to run before writing a query, and where finders for test data live |
| `<pick-rules>` | The limits on a data pick: the query shapes that are allowed, the time limit a query has, and what is counted in the spec instead |
| `<discovery-rules>` | The rules for test data discovery: hints, query shape, helper layout, probe paths, and how a pick that walks candidates tightens |
| `<test-accounts>` | The document that lists test accounts, and the note that keeps it current |
| `<step-logger>` | The helper that prints one evidence block, and the delimiter lines that open and close a test id's blocks in the run log |
| `<assertion-style>` | The repository's assertion helpers: the soft assertion, how a skip is written, and where a skip reason is spelled out |
| `<skip-ledger>` | The ledger of parked tests and the rule for moving a row |
| `<static-checks>` | The static-check commands, what each one gates, and the command that lists a spec's tests without running them |
| `<test-dispatch>` | How a test run is sent: the runner, the dispatch command, its defaults, how a run is cancelled |
| `<test-config>` | The project a spec runs under and where it is resolved |
| `<branch-age-note>` | The note on refreshing an old branch before a run or a pull request |
| `<run-watch>` | The ledger and the one watcher that report runs and pull requests, and the log search the evidence is pulled from |
| `<run-log>` | How a run's job log is read, and the command that pulls one test id's blocks out of it |
| `<defect-route>` | Where a rule the run contradicts is sent |
| `<investigation-log>` | The skill or file that records what a run settled that the documents did not predict |
| `<mergeability-note>` | The note on reading and resolving a pull request's mergeable state |

## 1. Read the row

Search `<manual-plan-docs>` for the id. A manual row is several lines, one per step, each
carrying its action, the rules it covers, and its expected result. Collect all of them
before writing anything.

Write out the row's steps and expected results side by side, and keep them where the spec
can be checked against them. The expected result is the acceptance test for the block:
every one of them has a line in its step's block that answers it, in words the tester can
compare. A step naming alternatives is every alternative, not the convenient one: an
action reading "reopen after 60 days or with a changed owner" is two scenarios, and a
retrieval reading "retrieve each person, record, and detail" reads the endpoint the row
names as well as the tables behind it.

For each business rule id in the row, find the rule's own text in the functional spec or
test pack under the same folder, and write down which step it belongs to. A rule whose
text nothing states is asked about through `AskUserQuestion`, per `<asking-note>`, never
guessed. A rule that names a value no documented column carries is reported in the block
as read by hand rather than asserted against a guessed column.

Read the automation notes in `<manual-plan-docs>` for how the application behaves in
practice before deciding what a step can measure.

## 2. Find what already covers it

Search the feature folder and its test plan for an automated row already proving those
rules. A manual row usually widens something already covered: one automated row proved a
set of columns on one record, another proved one date, a third one narrative type, and the
manual row puts all of it on one record and one request.

Name the overlap in the first line of the step 1 block, so the tester reading the evidence
knows what the row adds. Do not re-prove the single case an existing row already holds.

## 3. Source the data

Follow `<data-lookup>` before writing any query. Then look for a finder in the discovery
layer that already reaches the columns the rules name, such as one that finds a record in
the state the row starts from, with a side-effect aspect.

The account comes from `<test-accounts>`: the alias that holds the privilege or role the
row needs, and that can reach the site at all. A run that shows something the document
does not say goes into it, per that note.

- A capability that is missing becomes a named method or a named aspect on the discovery
  class. Raw SQL never lands in a spec.
- Every pick is hinted, and so is any existing finder the spec edits, per
  `<discovery-rules>`. A skip needs the user's answer through `AskUserQuestion`. A pick
  that walks candidates tightens from what the walk rejected, per `<discovery-rules>`.
- Keep a pick inside `<pick-rules>`. A pick that counts how many records carry the data
  can run the driving scan past the query time limit and take the whole test with it.
  Count off the snapshot in the spec instead, where it is free.
- Draw fullest first. Write the strict pick, the one asking for every value the row lists,
  and fall back to a looser one when the environment holds nothing for it. Then read
  several candidates and measure the one carrying the most of the list, so a record
  missing a quarter of the row is not what the run reports.
- Add a reporting-only aspect for each piece the pick cannot require, so the step 1 block
  can say whether the environment holds it at all. A pool reading zero and a pool the
  strict pick simply missed look identical otherwise.
- A pool too thin to draw from is written rather than hunted: put the subject into the
  state the row names, then restore the columns afterwards.
- Every prepared subject gets a marker comment naming the test id, so a row written by
  automation is identifiable later.

## 4. Write the spec

- The file name, folder, test tags, and describe names follow `<manual-id-rules>`: the
  file carries the full manual id and sits beside the specs that cover the same endpoint
  or page, one describe covers a step group, and each test title carries the full id as
  its tag.
- A discovery test that walks every pool and reports what the environment holds, which
  is what says whether the row's premise is reachable at all.
- A scenario test that loops the conditions the row names, the control included, drawing a
  fresh subject per condition.
- Readings are collected into arrays and printed at the end with `<step-logger>`, one call
  per manual step. The discovery layer logs a line per query, so anything logged inline
  lands in the middle of the evidence.

### What to assert

Assert what the application does. What the environment could fill is the draw's to
report.

- A rule with nothing to clear on the drawn subject is named in the block and the run
  stays green: an endpoint cannot clear a column nothing ever set, and a premise assertion
  on it turns a data gap into a red run. Assert the premise only where it decides whether
  the reading means anything at all, such as at least one subject carrying the data the
  rule acts on.
- Assert only what a rule promises. A rule that says a value is no longer set is a
  negative assertion on the old value, not an exact cleared value: one reopen empties a
  flag and writes a default to another, and an exact assertion goes red on correct
  behavior. A reading another rule can legitimately move, such as an identifier under a
  duplicate rule, is logged with a comment saying why it is not asserted.
- Use the soft assertion from `<assertion-style>` for the per-condition outcomes so one
  dispatch retires every condition instead of stopping at the first.
- A skip is for an environment that handed the row nothing: no subject, no worker, no
  pool. A subject that was drawn and refused every request is the endpoint answering, so
  that fails rather than skipping. Keep the two apart with a count of what was drawn
  beside the count of what was measured.
- Every skip reason is written out in words, per `<assertion-style>`.
- A row the spec cannot run at all, or a skip that fires on every run, goes in the skip
  ledger, per `<skip-ledger>`.

### What the blocks read like

The blocks are pasted into the actual-result field of the manual row, so they are plain
text for a person, not a log line for a machine.

- Sentences. No pipe-separated fields, no `field=value`, no markup of any kind.
- Name a value the way the tester reads it on the window: `card sent 2007-08-20`, never
  `cardSent=2007-08-20`.
- The subject id is a header line above the readings it belongs to, written once, rather
  than repeated inside every sentence.
- One blank line between lines, so a block stays legible after a paste.
- A count that reached the query's row cap is reported as at least that many. A flat
  number reads as a census the query never took.
- A payload is reported by its length. Printing an encoded narrative fills the whole run
  log and truncates the evidence.

## 5. Gates

The commands, and what each one is a gate on, are in `<static-checks>`, the command that
lists the spec's tests included. Run the whole list over the branch, with the spec path
this row wrote.

Commit on a branch, never on `<default-branch>`. Commit messages and the pull request body
go through scratchpad files, per `<shell-text-note>`.

## 6. Dispatch

Before every dispatch that is not a scoped rerun of a failure, run `<branch-age-note>` and
follow it. Send the run through `<test-dispatch>`: one dispatch for the new spec, scoped to
the row's id, and always on the branch's pushed ref, since a run without it executes the
default branch and matches no tests. `<test-dispatch>` is the only way a run goes out. Its
defaults, and the project the spec runs under (`<test-config>`), are set there.

### Link the runs you are waiting on

The link line, the script that records and tallies each run, the one-watcher rule and its
floor, and the run budget are in `<run-watch>`. Read it before starting the watcher.

What this step adds: pushing the branch is what makes the run execute the branch, and the
run being watched is the dispatch that carries the row's evidence blocks, so the log
search in that note is what those blocks are pulled from.

Expect several cycles. The first run is what says which pools the environment can fill,
which premise assertions were really data gaps, and which query is too slow. Read the
whole block set each time, not only the failure: a green run whose evidence reports a rule
with nothing to clear is a draw to tighten, not a row to hand back.

## 7. Hand the evidence back

Pull the blocks out of the run's job log with the command in `<run-log>`, with the leading
timestamp stripped, between the delimiter lines `<step-logger>` names for the id.

Report one block per manual step, in step order, as plain text ready to paste. Then:

- A rule the run contradicts goes to `<defect-route>`.
- A behavior the documents did not predict goes to `<investigation-log>`, so the next row
  starts from it.
- Run `<branch-age-note>`, then open a pull request, read its mergeable state, and resolve
  any conflict before linking it, per `<mergeability-note>`.
- Link the pull request for review.
