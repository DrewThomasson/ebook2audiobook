---
name: retest-sir
description: >-
  Retest a raised SIR against the application to decide whether the fix took, and produce
  the report that goes back to the dev team. The outcome is one of two statuses: `Retested`,
  meaning the defect is fixed and the SIR can be closed in ALM, or `Failed Test`, meaning it
  is not fixed and the report carries the evidence of why. Use when asked to retest, recheck,
  or verify a SIR fix, or after a migration lands in the test environment. Finds its work
  from the records whose fix was delivered, and claims the record while the retest runs.
---

# Retest a raised SIR

A raised SIR is a claim the dev team now has to answer. When they say it is fixed, someone
has to go and see. This skill does that, and it ends in one of two statuses:

- **`Retested`**: the defect is fixed. The user reports back that the fix is good and closes
  the SIR in ALM.
- **`Failed Test`**: the defect is not fixed. The user reports back with the evidence of why
  it is not fixed yet.

There is no third status. An application that moved without arriving at the fixed behavior
is `Failed Test`, and the report says what it does now rather than what the record says it
did before.

A retest that never reached the rule reports no status at all. That is not a third one: it
is the skill saying the run did not measure anything, and section 6.4 covers what happens
next. Every status here rests on the rule having been exercised.

The two statuses cost different amounts of work, and the difference is the point of the
skill. `Retested` can be carried by the existing tests going green in the right places.
`Failed Test` goes back to a team that already believes they fixed it, so it owes them the
whole request, the whole response, and what the record reads as afterwards.

| Placeholder | Meaning |
| --- | --- |
| `<records-root>` | The folder that holds one record per SIR, grouped by area |
| `<records-note>` | The note that says how the records, their queues and claims work |
| `<record-states>` | How the records spell the lifecycle states, such as `raised` and `migrated` |
| `<record-name>` | How a record file is named from its number, state and slug |
| `<record-header>` | The record's state, updated-date and SIR-number lines |
| `<record-identifiers>` | The identifiers the application uses to name a record |
| `<impacted-tests>` | The record's list of the tests the defect touches |
| `<alm-read-lines>` | The record lines that say what ALM reads for a status |
| `<queue-command>` | The command that lists the records in the `migrated` state |
| `<find-record-command>` | The command that finds a record by its SIR number in any state |
| `<open-records-command>` | The command that lists the open records for one area |
| `<read-script>` | The script that reads a SIR out of ALM by its number |
| `<claim-script>` | The script that claims and releases a record for one branch |
| `<index-command>` | The command that regenerates the records index |
| `<housekeeping-skill>` | The skill that reads ALM and brings the records in line with it |
| `<dispute-example>` | The case that shows a disputed method costing a retest |
| `<test-dispatch>` | The command that sends a test run, with its ledger and the project option |
| `<parallel-dispatch-rule>` | How several runs for one record stay separate runs |
| `<run-watch>` | The note on linking, watching and budgeting the runs |
| `<branch-age-note>` | The note that checks the branch against the main line |
| `<test-accounts>` | The record of what each test account may do |
| `<accounts-note>` | The note on keeping that record current |
| `<probe-history-command>` | The command that recovers an earlier probe from history |
| `<no-retry-option>` | The dispatch option that runs each test once |
| `<discovery-note>` | The note on hints for lookups in shared code |
| `<precision-note>` | The note on tightening a lookup from what it rejected |
| `<lookup-identifiers>` | The identifiers the dev team looks up first |
| `<fact-example>` | A measurement written as a fact |
| `<conclusion-example>` | The same measurement with a conclusion added |
| `<verdict-sections>` | The dated section each status appends to the record |
| `<migrated-section>` | The dated section a delivered fix appends to the record |
| `<skip-ledger>` | The ledger of parked tests and the rule for keeping it current |
| `<doc-checks>` | The checks a record file passes before the commit |
| `<writing-rules>` | The rules that govern text that lands in the repository |
| `<withdrawal-note>` | The note on recording a withdrawn SIR |
| `<learning-log>` | The investigation log kept across run cycles |
| `<shell-text-note>` | The note on passing text to commands through files |
| `<self-review>` | The note on reviewing the pull request the session opened |
| `<ready-signal>` | The note on the signal that hands the pull request over |
| `<scratchpad>` | The session's scratch directory |

## What this skill does not do

It does not validate a new defect. `/validate-sir` proves a defect and writes the SIR; this
skill only re-measures one that is already raised.

It does not close a SIR. ALM is the user's, and so is the message to the dev team. This
skill produces the status and the evidence.

It does not widen scope. A retest measures the record's own defect. Anything else the run
turns up is reported to the user and filed on its own, per section 7.

It does not move a record to `migrated`, and it does not write the `<alm-read-lines>` lines
that say `SIR Awaiting Migration`, `SIR Migrated`, or `LD Update Complete`. Those say what
the dev or design team reported, and `<housekeeping-skill>` records them from what ALM says.
This skill reads them and never writes them.

## 1. Find the work from the records

A SIR is ready to retest when the team that owns the fix says it has landed. ALM says so
first, and `<housekeeping-skill>` carries it onto the record by moving it to `migrated`.
That move is the trigger, and the queue is a file listing, per `<records-note>` (the
queues):

```bash
<queue-command>
```

A `migrated` record is a dev SIR whose fix reached the test environment, and it is the only
state this skill takes work from (the states are spelled as `<record-states>` names them). A
`likely-valid`, `valid`, `raised`, or `failed-test`
record is waiting on someone else, so it is not retested yet: say which state it is in and
stop. A second fix reaches the retest the same way the first did, when the sweep moves the
`failed-test` record back to `migrated`.

A SIR the design team answered with a document has nothing to measure, so
`<housekeeping-skill>` reconverts the revised document instead. A No Code Change answer ends
the SIR; any other LD update leaves it open, and it can still go on to a fix that reaches
this skill later.

The record's name carries the SIR number, per `<record-name>`, which is the handle for
everything below.

Read what the dev team answered before anything else. The answer is in ALM, in the SIR's
`Comments` field, and the record's own `<alm-read-lines>` lines and `<migrated-section>`
section carry what the sweep already copied across:

```bash
<read-script> <number> --json
```

The record's state says a fix migrated. The comments say what the dev team actually
answered. A team that disputes how the SIR was measured says so there, and a retest that
repeats the disputed method measures nothing. This has already cost one full retest:
`<dispute-example>`.

A comment naming a different record, column, sequence, or acting user than the record file
names outranks the record file. The record is what was measured before the fix. The comment
is what the team says the rule reads.

Claim the record before any of the retest is spent. A retest costs runner time and permanent
test-environment writes, and several sessions work at once. Gate: none of the retest runs
until the claim holds.

```bash
<claim-script> claim <record> <branch>
```

A refusal names the branch that holds it: another session has the retest, so stop and report
who has it rather than repeating the probe. The claim holds across the move section 8 makes,
and it is released when the pull request opens or the session stops without one, per
`<records-note>` (claiming a record).

## 1.1 Load the record, not the endpoint documentation

The `raised` or `migrated` record under `<records-root>` is the retest script. It already
holds the records, the acting logons, the payload that was accepted or refused, the
controls, and the quoted rule. Re-deriving any of that from the endpoint documentation
reintroduces the traps the original probe already stepped around.

One thing outranks it, and only one: a dev team comment in ALM saying the SIR measured the
wrong thing. Then the record's method is what is under test, not what to repeat. Run their
method, and run the record's alongside it so the two answers sit next to each other.

An invocation that names a SIR number rather than a record finds it across every state
rather than `raised` and `migrated`, so a record in the wrong state is caught by the refusal
below instead of coming back as no such file:

```bash
<find-record-command>
```

Read the whole file, then write the retest checklist out to the user before spending a
runner:

- the records, by the identifiers the application uses (`<record-identifiers>`)
- the acting logon or role for each
- the payload, field by field
- the expected refusal or acceptance, quoted from the rule
- the controls, positive and negative
- the read that proves the effect, by the call that answers it
- the impacted tests the record lists (`<impacted-tests>`)
- what the dev team said in ALM, and which item above it contradicts

Every item on that list is covered by the retest. A retest that skips the controls cannot
tell a fix from a rule that stopped running everywhere.

The checklist also names the precondition: the state the record has to be in for the rule to
be reachable at all, and the read that proves it is in that state. A wait rule needs a
record inside the wait. A role rule needs a caller without the role. Write down which
column, field, or flag carries it and how the run confirms it, before the run. Everything
after this depends on the precondition holding, and an unproven one turns every later result
into a result about nothing.

Refuse to proceed when the record's state is not `raised` or `migrated`. A `possible`,
`likely-valid`, or `valid` record has never been submitted, so there is no fix to retest and
the work belongs in `/validate-sir`. Say so and stop.

A `migrated` record is ready as it stands, because the sweep already moved it. A `raised`
record is retested only when ALM's `SIR Status` reads `Migrated` on the read above and the
sweep has not caught up yet. Then it moves to `migrated` once the claim holds. Rename it to
the `migrated` name, set the state to `migrated` and the updated date to today
(`<record-header>`), and append what ALM says changed, in the team's words
(`<migrated-section>`). A `raised` record whose ALM status reads anything else is waiting on
the dev team: say what ALM reads, release the claim, and stop.

A record already `migrated` keeps its section. A second fix after a failed retest appends a
new `<migrated-section>` section to the `failed-test` record and renames it back to
`migrated`; `<housekeeping-skill>` makes that move from ALM, the same as the first.

An invocation that names a SIR number rather than a record still reads ALM and claims the
record as section 1 says, with the same refusal on the state.

## 2. Tier 1: run what already exists

The impacted tests were written against this defect. Run them first, unchanged, on the
projects the record names. This costs one dispatch and it is often the whole answer.

Run `<branch-age-note>` once before the retest's first run, and not again before its
verdict, so every tier's evidence comes from one tree. Every dispatch goes through
`<test-dispatch>`, which refuses a run without a branch, sends it at once, and adds it to the
session's ledger. The full command line, with its branch, spec and ledger arguments, is the
value of `<test-dispatch>`.

Where the record names more than one spec or more than one project, dispatch them together,
one call each, with the project option naming any project other than the spec's own default.
`<parallel-dispatch-rule>`, and every one of them goes into the session's one ledger.

### Link the runs you are waiting on

A session waiting on tests says what it is waiting on, before it starts the watcher and
before it ends the turn. One line per run in flight:

```
waiting: <spec or grep, and project> - <job link>
```

The link line, the catch-up script that records and tallies each run, the one-watcher rule
and its floor, and the run budget are in `<run-watch>`. Read it before starting the watcher
and follow it as written.

Read the record's `<impacted-tests>` list for what to run and where. A test that the defect
made unreachable usually carries a tag or a project filter that has to come off for the
retest, and that removal is temporary until the status is known.

Interpreting Tier 1:

- **Green where the record says the rule should fire, and green on the controls**: candidate
  `Retested`. Go to section 5.
- **Red, with the record's own message**: `Failed Test`, and the evidence is already in
  hand. Go to section 4 for the report, and to section 3 only if the report needs the calls
  printed whole.
- **Red with a different message, or green for a reason the record does not predict**:
  nothing is decided yet. Go to section 3.

That third case is the one that costs people a wrong report. See section 6.

## 3. Tier 2: the probe

Only when Tier 1 left the question open, or when a `Failed Test` report needs the calls
printed whole.

Check the account the record names against `<test-accounts>` before the probe signs in: a
privilege taken away since the SIR was raised reads as the defect coming back. What the
probe shows about the account goes into the document, per `<accounts-note>`.

Recover the original probe from history rather than writing a new one. The record names the
spec and the test title, and the probe that produced the original evidence is usually still
in the log even when it was taken back out:

```bash
<probe-history-command>
```

Build the retest probe on these rules:

**Use the record's own records.** Not a fresh discovery sweep. A discovery-picked substitute
adds a second variable, and it can land on a record that answers a different rule first,
which says nothing either way. A probe pinned to those identifiers makes no pick, so it has
nothing to hint. A lookup the retest probe runs to find something is a temporary probe's
pick and is not hinted either, per `<discovery-note>` (what it does not reach). One it
touches in shared code is hinted. Either kind is tightened from what it rejected, per
`<precision-note>`.

**Use the record's own payload.** The original probe chose its field for a reason, usually
that the field is optional and carries no cross-field rule, so a stored write is
distinguishable from a discarded one. A re-derived payload walks back into whatever the
original avoided.

**Print both halves of every call.** Method, path, and the request body whole. Status and
the response body whole. Do this for every call in the sequence, not only the decisive one:
the read that lists the record, the read that issues any key, the write, the read that
follows it, the restore, and the final read.

**Dispatch with retries off (`<no-retry-option>`).** Each call appears exactly once in the
log, so the report can quote it without the reader wondering which attempt they are looking
at. This is the one case that overrides the default retry count.

**Log the identifiers the dev team looks up.** `<lookup-identifiers>`. A report that names
only a bare record id makes them run a query before they can start.

**Restore what the probe wrote.** Put every value back on a fresh key and read it back at
the stored value. Say in the output what was written and what it was put back to. Permanent
test-environment writes are the cost of a retest and the skill accounts for them out loud.

## 4. `Failed Test`

The comment goes onto a SIR the dev team already believes they fixed, so it carries the
measurement rather than an assertion about it. It is a comment on a record they are looking
at, not a second SIR, so it is four lines and two JSON objects.

The whole thing:

```
SIR failed testing. <one or two sentences: the record, its state, what the endpoint did instead.>

Request:
<the request body, whole, exactly as it was sent>

Response:
<the response body, whole, exactly as it came back>
```

Before writing it, check that the retest earned the status. `Failed Test` means the rule did
not fire where it should have, which is only distinguishable from the rule never being
reachable if something in the run shows it firing. A case where the rule is supposed to fire
and did, or a documented refusal on the same record from a neighboring rule, is what
separates "still broken" from "never asked." Without one, the outcome is section 6.4, not
this section.

The first line is always `SIR failed testing.` What follows it is the record by the
identifier the application uses, the state it was put in, what the endpoint answered, and
what the record reads as afterwards. Facts in the order they were measured, nothing between
them.

No date is written anywhere in the comment, and that includes the relative ones: `today`,
`same day as`, `yesterday`. ALM stamps the comment with the date it was posted, and a second
date in the body is one more thing to keep true. Say the condition the record was in
instead, in the application's own terms. Dates inside a request or a response body are
evidence and stay exactly as they came over the wire.

Nothing is explained. The team wrote the endpoint and has the SIR open, so the comment never
quotes the rule back at them, never says what should have happened instead, and never draws
the conclusion the values already carry. `<fact-example>` is the fact. `<conclusion-example>`
is the tester telling them what their own field means.

Never write the SIR number. ALM shows the reader which record they are on, and a number
typed into the body is a second copy to keep true. Never call the comment a retest, and never
name the status it reached: `Retested` and `Failed Test` are the tester's own words for the
pipeline, and the first line already says what happened.

Nothing else goes in. No environment header, no requirement quote, no `REPRODUCTION` steps,
no `CASE` headings, no controls, no closing line naming the rule. The SIR carries all of that
already and the reader has it open. The controls ran and they are what let the comment be
written, but they live in the record file and in what goes to the user.

The comment is plain text: no asterisks, no fences, no HTML. It goes inside one fence in
chat so the copy hands over exactly those bytes.

Everything `/validate-sir` section 3 says about what never appears in a SIR applies to this
comment unchanged: no repository, no run URL, no job link, no workflow, no runner, no
artifact path, no assistant. The dev team cannot reach any of it and naming it hands them a
reason to discount the report.

Run the comment through `<writing-rules>` before handing it over, the same as any line that
lands in the repository. The sentences around the two JSON objects are the team's own
writing, so they carry this side's vocabulary and American spelling, per `<writing-rules>`.
The request and the response are
evidence and the pass never touches them.

## 5. `Retested`

The defect is fixed. Keep the evidence short: which tests ran, on which projects, and what
the application answered where the record said it would answer wrongly.

Before calling it, confirm the controls ran. A rule that stopped running everywhere passes
the same tests as a rule that was fixed, and the two are opposite outcomes. If the retest
did not include a case where the rule is supposed to fire and it did fire, it has not earned
`Retested`.

Confirm the precondition too. A refusal proves the fix only if the record was in the state
the rule governs, and the same reasoning runs in reverse: a rule that now refuses everything
refuses an unreachable record as readily as a reachable one.

## 6. The two traps

Both of them end with a run that looks decisive and is not. The first turns an unrelated
refusal into `Retested`. The second turns an unreached rule into `Failed Test`.

### 6.1 A refusal that is not the record's refusal

A defect that used to be accepted and is now refused looks fixed. It is not fixed until the
refusal is the one the rule specifies.

Any message that is not the record's expected message means one variable is still loose.
Widen it before concluding anything:

- **Is the refusal about the caller or about the record?** Run the same call against records
  under different parents, agencies, or offices. A message that follows the caller across
  all of them is not the record's rule firing.
- **Is it a rule that runs earlier?** A payload can trip a requirement rule before it reaches
  the rule under test. Change the field to one with no cross-field rule and try again.
- **Does it reproduce on a record with nothing wrong with it?** If a clean record draws the
  same refusal, the endpoint is refusing everything and the defect is untested.

An application that is refusing every call is a new defect on top of the old one. It is
`Failed Test` for this SIR, because this SIR's defect is unmeasured, and it is a separate
report for the new behavior. Say both to the user.

### 6.2 An acceptance where the rule was never reachable

The mirror case, and the more comfortable one, because an acceptance is what the record
predicts. A rule that never saw a record in the state it governs accepts the call for the
same reason a fixed rule would refuse it: it was not asked. Both look like the defect
reproducing.

So an acceptance is evidence only once the precondition is proven:

- **Which stored value carries the condition?** Name the column or the field, and say who
  says so. The record's own reproduction steps are a claim about this, not proof of it, and
  the dev team's comment in ALM outranks them.
- **Did a read confirm the value after it was written?** A write that silently did nothing,
  or wrote a column the rule does not read, leaves the record outside the rule's reach while
  the run reports success.
- **Does the rule fire anywhere in this run?** If nothing in the run shows the rule refusing
  a call it should refuse, the run cannot tell an unenforced rule from an unreached one.
- **Do the controls control the right variable?** A positive control on the same unproven
  precondition is not a control. Two records that both sit outside the rule's reach agree
  with each other and say nothing.

### 6.3 Which trap is in play

The trap follows the answer, not the defect. A refusal invites 6.1, an acceptance invites
6.2, and either can appear on a SIR of either kind.

### 6.4 When the rule was not exercised

Neither status applies. `Retested` and `Failed Test` both describe a rule that ran; a rule
that was never reached has no verdict, and giving it one reports a measurement that did not
happen.

So the record stays `migrated`, and nothing goes to ALM. Tell the user what was measured,
which precondition went unproven, and what the run that settles it has to write instead.
Then run that one. The retest is not finished, and saying so costs a dispatch, while a wrong
verdict costs the dev team a round trip and the SIR its credibility.

## 7. Side findings

A retest run reruns tests that have nothing to do with the SIR under test, and it will
sometimes trip over an unrelated change. A test that fails on a message string, or one that
starts passing where the record says it should not, is the application moving underneath a
different record.

So after the retest, check the other records for the same endpoint or page:

```bash
<open-records-command>
```

For each, ask whether this run contradicted it. Report what it found to the user. A
contradicted record is its own retest, run through this skill again, not folded into the
current one.

## 8. Write the verdict

A verdict is written only when the rule was exercised. A run that stopped at section 6.4
writes nothing here: no heading, no rename. It goes back to section 2 with the setup the dev
team named.

Append a dated section to the record file rather than editing what it already says. The
original measurement is what the SIR was raised on and it stays readable.

The heading is the status the retest reached, then the date. `Retested` or `Failed Test`,
spelled the way ALM's `SIR Status` spells it, never the word `Retest`. A record that fails
twice carries one such heading per attempt, and the headings read as the history of what the
fix did. The sections are `<verdict-sections>`:

- under `Failed Test`: what was run, what the application answered, quoted, and what part of
  the rule is still unenforced
- under `Retested`: what was run, what the application answered, quoted

Then move the record to its status by renaming it (`<record-name>`).

- **`retested`**: the defect is fixed. The record is history. Update `<impacted-tests>` to
  say the tests it lists are back to asserting the documented behavior, and say which
  assertions have to change if any still work around the defect. A test the retest switches
  back on loses its row in the skip ledger, and a row that cites the SIR but stays parked
  has its unskip entry updated, per `<skip-ledger>`.
- **`failed-test`**: the defect is live. `<impacted-tests>` has to be current, because those
  tests are still working around it, and the reason a test is tagged or skipped may have
  changed even when the defect did not.

Set the updated date to the retest date (`<record-header>`). Leave the SIR number alone.

- **`Retested`**: the SIR's life on this side ends here. The user closes it in ALM.
- **`Failed Test`**: the SIR is live in ALM again, answered with the evidence from section 4,
  and the `failed-test` record carries the retest history. It holds until the dev team
  answers again in ALM, which `<housekeeping-skill>` records and carries back to `migrated`,
  the same path the first fix took.

The rename is the whole of the status change: the file name and the state line are what the
queues and the index read, per `<records-note>`. Regenerate the index in the same commit as
the rename:

```bash
<index-command>
```

A retest that stopped before it measured anything is neither status. The record stays
`migrated` and the index is untouched. Release the claim, so the next session picks it up
where this one stopped:

```bash
<claim-script> release <record> <branch>
```

A record only moves to `retested` on measurement, never on the dev team saying it is fixed.
Their claim is what starts the retest, not what ends it.

The same holds the other way. A dev team that argues the SIR is invalid rather than fixed
has given a position, not a verdict, and a SIR is withdrawn only by the person who authored
it in ALM (`<withdrawal-note>`). Never record the dev team as having withdrawn or closed
one. When the author says they withdrew it, the record moves to `invalid` under
`/validate-sir` section 5, keeping the ALM number.

Run `<writing-rules>` over any spec comment the retest changed. The record file sits outside
it, per `<writing-rules>` section 4.1. The record's paste block is not reworded here: the
SIR carries an ALM number by the time a retest runs, so that text is a copy of what the dev
team holds.

Then run `<doc-checks>` over the record file, which confirm the dictionary holds the short
forms the retest added and that the published docs can carry the record name and its links.

## 9. Handoff

Give the user, in chat:

- the status, in the first line
- the paste-able report from section 4 or 5
- the record's path and the state it is now in
- what the probe wrote to the test environment and what it was put back to
- any side finding from section 7
- the job links, which they need and the record does not

Then land the branch: the record file at its new state and the regenerated index, plus any
test change the retest earned. Release the claim once the pull request opens, per
`<records-note>` (claiming a record). Take the probe back out before the pull request, per
`/validate-sir` section 4, and then run `<branch-age-note>`, so the gate reads the head that
gets opened. A probe worth keeping is worth writing as a test with its own ID and a title.
Commit messages and the pull request body go through `<scratchpad>` files, per
`<shell-text-note>`. Once it is open, the session reviews the pull request itself, with its
static checks job running beside the review, per `<self-review>`, before the ready signal
from `<ready-signal>` goes out.

A test the defect made unreachable, whose filter came off in section 2, goes back on when the
status is `Failed Test`. The record's `<impacted-tests>` says why it is filtered, and that
reason still holds.

Log what the retest established through `<learning-log>`: the status, the records, and the
trap in section 6 if the retest hit one. The next retest of the same endpoint starts from it.
