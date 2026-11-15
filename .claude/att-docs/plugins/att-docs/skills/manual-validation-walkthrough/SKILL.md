---
name: manual-validation-walkthrough
description: >-
  Walk the user through reproducing a validated SIR by hand, one step at a time, asking
  what they saw at each step, then write what the hand check found into the SIR's record:
  a dated verification section, a verified line and a move to the verified state, corrected
  SIR text when the details differed, or a move to invalid or back to possible when it did
  not reproduce. Use when asked to check, vet, verify, or reproduce a SIR by hand, "walk me
  through verifying that SIR", "what's left to verify", and before a SIR is raised, since
  the raise refuses a record the user has not checked.
---

# Manual validation walkthrough

`<validate-skill>` proves a defect with a probe and leaves a record awaiting the hand check,
holding the SIR text. Only this check makes the record verified. Before that text reaches
ALM, the tester reproduces it by hand, because the dev team reads the SIR as a set of steps
a person follows, and a step only a probe could follow is one they cannot. This skill is that
hand check. It reads the steps out of the record, asks the user what they saw at each one,
and writes the answers back into the record.

The user does the clicking. This skill runs nothing against the application, dispatches no
test, and never files anything in ALM. It never records an observation the user did not give,
and never fills a gap with what the probe saw: a step the user skipped is recorded as skipped.

The record is the tracker, per `<records-note>`. No issue is opened or touched.

| Placeholder | Meaning |
| --- | --- |
| `<validate-skill>` | The skill that validates a defect and writes the SIR text |
| `<raise-skill>` | The skill that files a verified record into ALM |
| `<retest-skill>` | The skill that rechecks a fix for a SIR already in ALM |
| `<records-root>` | The folder that holds the SIR records, one subfolder per application |
| `<records-note>` | The note on record states, file names, queues and the index |
| `<record-states>` | The record states and file names: not yet probed, awaiting the hand check, verified, invalid, and the numbered ones |
| `<unchecked-list>` | The command that lists the records awaiting the hand check |
| `<verified-form>` | The verified line a record carries, the section a check appends, its heading and its layout, and the file name each outcome moves the record to |
| `<text-layout>` | Where the SIR text sits in a record and the order of its parts: environment, logon, requirement quote, expected, actual, numbered steps |
| `<text-voice>` | The voice the SIR text is written in, set by the validate skill |
| `<worktree-rule>` | How a session gets its own worktree and branch for a record change, and the branch name |
| `<claim-script>` | The command that claims a record for a branch and releases it again, and what its exit codes mean |
| `<record-checks>` | The checks a record change runs before it is committed: the acronym gate, the index regeneration, the wiki check |
| `<test-accounts>` | The note on the logons the tests use and where a logon fact is recorded |
| `<asking-note>` | The note on how a question is put to the user |
| `<branch-age-note>` | The note on refreshing an old branch before a pull request |
| `<shell-text-note>` | The note on passing commit messages and bodies to a command as files |
| `<run-watch>`, `<self-review>`, `<ready-signal>` | The notes on waiting for a pull request, reviewing it, and reporting it ready |
| `<writing-rules>` | The note on text that ships, and whether record text is inside it |

## 1. Pick the record

The argument is a record path, or a word or two of its title. With neither, list the records
nobody has checked by hand yet, with `<unchecked-list>`, which reads them from under `<records-root>`.

Show the list in the turn text, one line each with the application and the record's title,
then ask which one through the tool `<asking-note>` names. Offer up to four, the oldest
`Updated:` first, and the user names any other in a free-text answer.

A verified record was checked before, and its verified line says when. Say so, and ask
whether to check it again before going on: a second check appends a second dated section and
moves the date on the line.

A record in any other state is not this skill's, per `<record-states>`. One not yet probed
goes to `<validate-skill>`, and a numbered one is already in ALM, where a recheck of a fix is
`<retest-skill>`.

## 2. Branch and claim

The check ends in a record change, which lands through a pull request, so work in a worktree
per `<worktree-rule>`, and claim the record so no other session probes or rewrites it while
the user is checking it:

```bash
<claim-script> claim <record> <branch>
```

A refusal names who holds it. Tell the user and stop: the session holding it may be
rewriting the steps the user is about to follow.

## 3. Read the steps out of the record

The SIR text sits where `<text-layout>` says. It carries the environment, the worker logon,
the requirement quote, the expected behavior, the actual behavior, and numbered reproduction
steps. Read all of it before asking anything.

Put the context in the turn text once, before the first question, so the user has it on
screen while they work: the environment, the logon, the requirement quote, and expected
against actual. The steps come one at a time after that.

A record whose SIR text has no numbered steps, or no actual behavior, cannot be walked. Say
which part is missing and send it back to `<validate-skill>`, which owns the text. Nothing is
written here.

## 4. Walk it

Every question goes through the tool `<asking-note>` names, one call per step, so the user
answers in the order they work. A free-text answer is where the specifics go, and the question
says so: the record ids they used, the exact message, what rendered instead.

**Setup**, before step 1: can the user reach the environment and sign in as the logon the SIR
names?

- As the SIR says. Go on.
- A different environment or logon. They name it in a free-text answer. Go on, and record the one they
  used: a defect that reproduces under a different account is still a finding, and a SIR
  naming an account that no longer works is a difference to correct.
- Cannot get in. Stop, per section 6.

The logon the user signed in with, and whether it got in, is an account fact. A logon that no
longer works, or one that turns out to hold a privilege the SIR assumed it lacked, is
recorded in the pull request that writes the record, per `<test-accounts>`.

**Each reproduction step**, quoted in full in the question:

- Did it as written. Go on.
- Did it, something differed. Ask what, in a free-text answer, if they have not said.
- Could not do this step. Ask why in a free-text answer, then ask whether to go on or stop. A step that
  cannot be done is usually the finding, not an obstacle.

**The observation**, after the last step, with expected and actual quoted:

- Saw the actual behavior. The defect reproduced.
- Saw the actual behavior with differences. Ask what differed.
- Saw the expected behavior. The defect did not reproduce.
- Saw something else. Ask what.

Then one last question: the record ids the user worked on, if they have not given them, and
anything else worth writing down. Record ids are the application's own identifiers and the
logon. Never write a person's name, an address, or any other client detail from the screen
into the record: it ships.

Keep the user's words. Correct spelling, turn shorthand into a sentence, and nothing more.
Their observation is the evidence, and a paraphrase that sharpens it claims something they
did not see.

## 5. The outcomes

The observation decides which one.

**Reproduced as written.** The record gains the section in section 7 and the verified line,
and moves to the verified state, with the file renamed by `git mv`, per `<verified-form>`. A
recheck of a record already verified keeps its name. The SIR is ready for `<raise-skill>`.

**Reproduced with differences.** The defect is there, and the SIR text says something about
it the user did not see: another message, an extra step, a field that moved. The dev team
follows the text, so the text is corrected before it reaches them:

1. Draft the corrected title and long description from the user's answers, changing only the
   parts the differences touch, in the voice `<text-voice>` sets.
2. Show the changed lines against the current ones in the turn text, and ask whether to
   apply them, apply them with the user's edits in a free-text answer, or leave the text as it stands.
3. Applied, the text is rewritten in place. Left, the section in section 7 says the text and
   the hand check disagree, and on which point.

Either way the record gains the section and a verified line that says it was with
differences, and moves to the verified state the same way.

**Did not reproduce.** The probe saw the defect and the user did not, so either the
application changed since the probe, or the steps leave out something the probe did. Which
one is the user's call, asked every time:

- **Dismiss it.** The record moves to invalid: its state, a sentence saying the hand check did
  not reproduce it, and a `git mv` to the invalid file name. What the probe measured stays,
  because the measurements stand whatever the hand check found.
- **Send it back for another probe.** The record moves to not yet probed, with the same
  sentence and a `git mv` to that file name. `<validate-skill>` picks it up from that queue
  and starts from what both checks saw.

Neither move writes a verified line, and a recheck of a verified record deletes the one it
carried, since the index check refuses a verified line on the record a later probe would make
of it. Both keep the SIR text in the record, under a sentence saying it was not raised.

## 6. Stopping part way

The user cannot get in, cannot finish, or asks to stop. The record gains the section in
section 7 up to the last step answered, saying where the check stopped and why, and no
verified line. The state does not move. The next walkthrough on the record starts from the
top and appends its own section.

## 7. The section

Appended at the end of the record, with `Updated:` set to today, in the layout
`<verified-form>` gives. It carries a dated heading, a line saying where the user checked and
as which logon, and on which record ids, then one line per step, numbered as the SIR numbers
them, each saying what the user did and saw, then a closing line.

The closing line is the outcome in one sentence: reproduced as written, reproduced with
differences and what they were, did not reproduce and where the record went, or stopped and
why.

The section refers only to the check itself, never to a tracker issue, a test run, a workflow, or the
tool that helped write it.

## 8. Land it

The record is Markdown, so the checks in `<record-checks>` apply, and the index follows the
record, and the wiki check runs last, over the record and the index as they will be
committed. Whether the record sits inside the `<writing-rules>` scan is set there.

Commit the record and the index, run `<branch-age-note>`, push, and open the pull request
non-draft, with the commit message and body in scratchpad files, per `<shell-text-note>`. The
body says which record, the outcome, and any SIR text change. Nothing here changes code a spec
loads, so no test run is owed, and the body says so. Release the claim once the pull request
is open:

```bash
<claim-script> release <record> <branch>
```

Then follow the pull request through the watch, the self review, and the ready signal the
same as any other, per `<run-watch>`, `<self-review>` and `<ready-signal>`.

## 9. Report

Say which record, the outcome, and where the record now sits. For a verified record, the next
step is `<raise-skill>`, which the user starts when they are ready: it asks for the status and
the build itself. For a record sent back, the next step is `<validate-skill>` on that record,
and for a dismissed one there is none.
