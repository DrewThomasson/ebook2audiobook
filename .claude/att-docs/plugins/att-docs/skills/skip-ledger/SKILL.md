---
name: skip-ledger
description: >-
  Keep the ledger of every parked test, each test that is switched off on some or all of
  its projects, with the day it was parked, why, and what it needs to run again, and check that no skip lands
  or lifts without its row. Use whenever a change adds, moves, rewords, or removes a skip,
  an expected-failure marker, an engine exclusion, or a disabled spec, before the commit;
  whenever a SIR a parked test waits on changes state; and when asked what is skipped or
  why, "what tests are parked", "why is that test skipped", "what is waiting on that SIR".
---

# The ledger

A parked test is easy to forget. Its skip reason prints in a report nobody reads twice, and
the day the SIR it waits on is fixed passes with the test still parked. So the repository
keeps one ledger of every parked test: when it was parked, why, and what has to change
before it runs again.

The ledger is `<ledger-file>`. It ships as `<ledger-doc>`, which is rendered from it whole,
so the reader on the work side sees the same list. A check holds the ledger to the code in
both directions, so it cannot drift: a new skip with no row fails, and a row whose test runs
again fails.

| Placeholder | Meaning |
| --- | --- |
| `<ledger-file>` | The file that holds the rows, and the repository's note on its header |
| `<ledger-doc>` | The rendered page the ledger ships as, and what generates it |
| `<check-command>` | The gate, its list mode, and its write mode |
| `<parked-kinds>` | The kinds of parked test the scan finds on its own, and what the code holds for each |
| `<guard-rule>` | Which conditional skips the scan leaves out, the `guard` kind for one that fires on every run, and how a guard row's key is written |
| `<key-rules>` | How a row's key is formed, the keys that are not titles, and how the page counts parked tests |
| `<scan-scope>` | The folders the gate reads, and what is not parked by design |
| `<since-command>` | The command that finds the commit which added a skip, following renames and reformats |
| `<plan-rule>` | The test plans the gate holds the ledger to, the status that conflicts with a parked test, the status a parked row's plan cell takes, and how a spec that parks every id it quotes is read |
| `<exit-codes>` | What each exit status of the gate means |
| `<static-checks-note>` | Where the gate runs on every pull request |
| `<sir-refs>` | How a SIR number is written in a row |
| `<writing-rules>`, `<acronym-gate>` | The gates the rendered page goes through |

## 1. What counts as parked

A test is parked when it does not run on any data. A test excluded from the projects of one
engine is parked too, though it still runs on the others. The scan finds these on its own, per
`<parked-kinds>`: a skip with a title whose body never runs, a known-failing marker, an
expected-failure marker, a spec file excluded from every project, and a test excluded from
the projects of one engine.

A conditional skip, one that fires when the data a test needs is missing that day or when the
run is on a project the test does not belong to, is a guard, and the scan leaves it out, per
`<guard-rule>`. Those skips are the test working, and they number in the hundreds; listing
them would bury the handful that matter.

A guard that fires on every run anyway is parked in all but name, and goes in by hand as kind
`guard`. The scan cannot tell it apart from a guard that fires sometimes, so the row is what
says it.

What is not parked by design is in `<scan-scope>`.

## 2. A row

Seven tab-separated columns. The header of `<ledger-file>` repeats this.

| Column | Holds |
| --- | --- |
| file | the path from the repository root |
| key | the coverage matrix id the title carries, or the whole title when it carries none |
| kind | one of the kinds in `<parked-kinds>`, or `guard` |
| since | the day the skip went in |
| reason | why the test is parked, in a sentence |
| unskip | what has to be true before it runs again |
| refs | SIR numbers and repository paths, or `-` |

How a key is formed, which keys are not titles, a guard row's key, and how the page counts
parked tests are in `<key-rules>`. The check refuses a key it cannot count rather than
letting the count miss or invent a test.

**since** is the commit that added the skip, not the last one to touch the line. Blame lands
on renames and reformats, so trace past them with `<since-command>`. A test that was commented
out before it was skipped dates from the skip.

**reason** says what the app or the data does, in the words the person debugging it would
use. It is not the skip reason string copied over: that string is often a placeholder or
empty, and the ledger is where the real reason is written down once.

**unskip** is concrete. "The SIR is fixed" is concrete. "Needs work" is not. When nothing
will ever bring the test back, say so and say what should happen instead: retire the row,
delete the dead branch.

**refs** names SIRs as `<sir-refs>` says, and never names a tracker number, a pull request,
or a run. The doc ships to a repository where none of those exist. The scan in
`<writing-rules>` reads the rendered page whenever the ledger changes and refuses one there,
while letting through what that skill keeps, such as a rule's own message number.

## 3. The check

Run `<check-command>`: the gate, a list mode that prints what the scan finds, and a write mode
that renders `<ledger-doc>`.

The gate reads all of `<scan-scope>`, not the branch's diff, because a skip lifted in one file
can leave a row stale anywhere. Its exit statuses are in `<exit-codes>`. In every repository
it fails in these cases:

- a parked test has no row;
- a row names a test that is no longer parked;
- two parked tests in one file share a key, since one row cannot tell them apart;
- a guard row's key names text the file no longer holds, since the guard it describes is gone;
- a test plan marks the row's matrix id as done, per `<plan-rule>`, since the plan then counts
  a test that never runs as covered. An engine-excluded test still runs on the other engines,
  so its plan row may read done;
- the rendered page is behind the ledger, which is a separate status so a stale page can be
  told from a disagreement.

The static checks run it on every pull request, per `<static-checks-note>`. A red run there
means a skip was added, moved, renamed, or lifted without its row.

## 4. Keeping it current

Run the gate before every commit that touches a skip, an engine exclusion, or a disabled
spec. Then:

- **A test parked:** add the row. `since` is today. When a test plan marks its matrix id done,
  set that status cell to the parked status and the row's reason, per `<plan-rule>`. An
  engine-excluded test still runs on the other engines, so its plan cell stays as it is.
- **A test unparked:** drop the row. The check will say so if you forget.
- **A title or matrix id renamed:** rename the key. `since` does not change.
- **A test moved to another file:** change `file`. `since` does not change.
- **A SIR the row waits on changes state:** update `unskip`. When the SIR is fixed and
  migrated, the test is ready to run again, and `unskip` says so until someone runs it.
- **A guard starts firing on every run:** add a `guard` row. Drop it when the guard starts
  passing.

Then run the write mode, and commit the ledger and the rendered page together. The page goes
through `<writing-rules>` and `<acronym-gate>` like any other shipped document.

## 5. Answering questions from it

"What is parked in this suite", "what is waiting on that SIR", "why is that test a known
failure": read `<ledger-file>`, or `<ledger-doc>` for the rendered view. Search `refs` and
`unskip` for a SIR number. When the answer and the code disagree, run the gate; the code is
right and the row is what needs fixing.
