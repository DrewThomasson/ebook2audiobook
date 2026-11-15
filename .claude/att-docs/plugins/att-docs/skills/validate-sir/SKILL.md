---
name: validate-sir
description: >-
  Validate a suspected application or documentation defect is reproducible, then
  produce the finished SIR text to hand to the dev team or the design team.
  Claims the SIR record while the probe runs and moves it from `possible` to
  `likely-valid` (awaiting the user's hand check) or `invalid` once the outcome
  is settled, or to `invalid` keeping its number when a submitted SIR is taken
  back by its author. Use when asked to validate, write, draft, or prepare a
  SIR, and after a run or a manual probe surfaces a gap between a functional
  spec and observed application behavior. Also keeps the record for each one,
  so use it when told a SIR was raised in ALM with its number.
---

# Validate a SIR

A SIR is a defect report read by people who did not watch the run. It has to
carry everything they need to see the defect themselves, in their environment,
without asking a follow-up question.

This skill has two halves and they are ordered. First prove the defect
reproduces. Only then write it up. A SIR that turns out not to reproduce costs
more credibility than the defect costs to leave unfiled, so the validation half
is not optional and its outcome may be "no SIR".

The consuming repository's extension supplies the values below. Where it names
none, ask the user rather than guessing.

| Placeholder | Meaning |
| --- | --- |
| `<records-root>` | The directory that holds one record file per suspected defect |
| `<records-note>` | The note saying a SIR's life is kept in its record and nowhere else |
| `<record-states>` | The record states, in lifecycle order, and how a state shows in a file name |
| `<queue-command>` | The command that lists the `possible` records waiting to be validated |
| `<claim-script>` | The command that claims a record for a branch and releases it again |
| `<index-command>` | The command that regenerates the records index |
| `<rule-sources>` | The documents that carry the intended behavior, and where each one lives |
| `<automation-notes>` | The notes on how the application actually behaves, one per suite |
| `<test-accounts>` | The accounts a probe signs in as, and the note on adding a fact to them |
| `<probe-print>` | The statements a probe uses to print a call's request and response whole |
| `<test-dispatch>` | The command that sends a probe run, and what it records |
| `<branch-age-note>` | The note on checking the branch is current before a run or a pull request |
| `<run-watch>` | The note on waiting for a run and naming the runs in flight |
| `<discovery-note>` | The note on hinting shared discovery, and what it exempts |
| `<precision-note>` | The note on tightening a probe from what its walk rejected |
| `<identifiers>` | The identifiers the dev team can look up in the application |
| `<control-note>` | The note that records the positive control rule |
| `<schema-lookup>` | The skill that looks up and reads the stored data to confirm an effect |
| `<env-fields>` | The environment header fields the SIR carries, each one word |
| `<learning-log>` | The skill that logs what the gate established for the next probe |
| `<asking-note>` | The note on how a question is put to the user |
| `<writing-rules>` | The gate for text that ships, and what it skips |
| `<record-checks>` | The checks a record file passes before the commit |
| `<decode-note>` | The note on values an interface decodes on read and takes as codes on write |
| `<hand-check-skill>` | The skill that walks the user through a hand check of a record |
| `<housekeeping-skill>` | The skill that brings the records in line with what ALM holds |
| `<deviation-note>` | The note on where a further deviation goes when a run finds one |
| `<intent-docs>` | The documents that carry intended behavior, never changed to match a defect |
| `<plan-doc>` | The coverage plan whose rows say what the application is supposed to do |
| `<mergeability-note>` | The note on reading a pull request's mergeable state and resolving it |
| `<shell-text-note>` | The note on passing commit and pull request text to a command as a file |
| `<scratchpad>` | The session's scratch directory for those files |
| `<self-review>` | The note on how the session reviews its own pull request |
| `<ready-signal>` | The note that sets the wording of the last line of the run |
| `<raise-steps>` | The steps that move a record to `raised`, and where the Author comes from |
| `<skip-ledger>` | The ledger of parked tests, and how a record's number lands in it |
| `<withdrawal-note>` | The note on withdrawing a raised SIR |

## Claim the record before validating

A SIR's life is kept in its record under `<records-root>` and nowhere else, per
`<records-note>`. No tracker issue is opened, labeled, or closed for one. Most
SIRs start from a `possible` record that a spec run's deviation gate wrote, and
the queue is a listing:

`<queue-command>`

Validating one costs runner time and permanent writes in the test environment,
and several sessions work the same records at once, so the record is
claimed before any of that is spent. Gate: none of the validation runs until
the claim holds.

`<claim-script>`, with `claim`, the record, and the branch.

A refusal names the branch holding it: another session is validating it, so stop
and report who holds it rather than repeating the probe.

When the suspected defect has no record yet, because it came out of a
conversation or a manual probe, write the `possible` record at claim time and
claim that path. Section 5 says what goes in it and how it moves between states.
The claim keys on the suite and the slug, so it holds across the renames the
outcome makes, and it is released when the pull request opens, not when the SIR
text is emitted.

## 1. One SIR per possible record

One `possible` record gets one SIR. Both teams read it, so it does not get split
by who fixes it. If the probe turns up a code problem and a doc problem in the
same record, they go in the same report, and the reader works out which half is
theirs from the evidence.

Work out which team acts first anyway, because it decides what evidence to
gather:

- **Dev** when the app does not do what the spec says. The fix is a code change.
  Evidence is the spec quote next to what the app did.
- **Design** when the app looks right and the doc is wrong, missing, or says two
  things at once. Design owns the documents in `<rule-sources>`, so the fix is a
  doc change. Evidence is what the app did next to the passage that fails to
  describe it.

Say which one it is in the line above the SIR. It stays out of the SIR body.

If no document carries the rule at all, the SIR is about the missing rule, not
about the behavior. Never write a SIR against a rule you believe but cannot
quote.

Before deciding no document carries it, search every source in `<rule-sources>`,
not only the suite's own doc. A rule quoted from any of them is as quotable as
one from the suite doc.

## 2. Validation gate

Every item below is answered before any SIR text is written. Answer them out
loud to the user as a checklist so a gap is visible rather than assumed.

The probe signs in as an account chosen from `<test-accounts>`, so a defect is
not mistaken for a privilege the account lacks. A probe that shows an account
fact the document does not carry adds it in the same pull request, per
`<test-accounts>`.

### 2.0 Write the probe to capture the report

The probe runs once. What it failed to print is a second run, a second set of
permanent writes, and a wait, so what the report needs is decided before the
probe is written rather than after it comes back.

A reproduction step that rests on a call carries that call's request object and
its response object, so every call the report will name prints both, whole and
pretty, with `<probe-print>`.

The `request` and `response` markers are what makes the pair findable in
a run's output, and the indentation is what makes it paste into ALM as JSON
rather than as one long line.

Print the body the client sends, not the object the probe built. A fixture that
fills a field in when the caller names none leaves the two different, and an
evidence block missing a field the endpoint received is a reproduction that does
not reproduce. Name that field in the probe so both copies agree.

A shared helper that prints a one-line summary of a call, such as status,
success, and the joined errors, is for reading a run, and it is not evidence. A
probe that leaves only summary lines cannot produce a report, whatever it
proved.

Everything the gate below asks for is a call, so everything below prints its two
objects:

- the failing call, on each record 2.2 names
- the read-back 2.5 asks for, which is a step in the report
- the positive control from 2.3 and the negative control from 2.4, whose objects
  go to the record file rather than to the report

One thing never goes to the run output whole: a field carrying Base64 or an
embedded document body. It buries the log and can cost the run its output
entirely. Replace that value with `<...>` before printing and keep the key.

### 2.1 Cite the requirement exactly

**No SIR ships without a quoted passage.** Every claim about what the app
should do is backed by documentation text quoted verbatim in the SIR body, not
summarized, not paraphrased, and not replaced by a section reference the reader
has to go look up. The quote is the whole basis for calling the behavior a
defect rather than a preference, so a SIR without one is an opinion.

Record the document name, its revision or version, and the section or page
alongside the quote. A document file name with no revision is not a citation,
because the reader cannot confirm the rule is still current and the defect dies
in triage.

Quote enough to stand alone. If the rule only makes sense with the sentence
before it, or with the field definition it sits under, include both. A quote
that the reader must reconstruct context for is the same problem as no quote.

When a SIR rests on more than one rule, quote each one and label which step of
the reproduction it governs. When the same passage governs the whole
reproduction, quote it once and say so explicitly.

Name the document once. Rules drawn from the same document belong under a single
citation line carrying the name and the revision, with each further passage
introduced by its section alone. Repeating the document name and revision above
every quote reads as two documents to a reader skimming for the source, and
costs a line each time it appears:

```
<doc name>, <revision>.

<section>:
"<quote>"

<section>, rows 3, 8, and 9:
"<quote>"
```

A second document gets its own citation line, name and revision included, so the
reader can see where one source ends and the next begins.

Quote a numbered constraint row under its own number, written the way a list is
written, and put the row's message on the line below the rule it belongs to. The
constraints tables run the two columns together, and a reader who cannot tell
the rule from the message it returns cannot check either one:

```
3. <the rule, verbatim>
   <the message it returns, verbatim>
```

The text stays verbatim. The number, its period, and the line break are
formatting the table already implied.

A doc problem gets quoted too. There the quote is the passage that is wrong,
incomplete, or says two things at once, copied out next to what the app did.
When the rule is missing altogether, quote the nearest passage that should have
carried it and say it does not, naming the document and section you searched.

Read `<automation-notes>` for the same page or endpoint before concluding the
behavior is undocumented. A known quirk recorded there is not a new SIR.

### 2.2 Reproduce on independent data

One observation is an anecdote. Run the reproduction at least twice against data
that shares nothing: a different record of the same kind each time. If the
defect only appears on one record, the SIR is about that record's state, not
about the code path, and the write-up has to say so.

A probe that picks its data by query does not hint that pick. It is a
temporary probe, which `<discovery-note>` exempts, so each independent record
comes from a fresh query that excludes the records already picked. Shared
discovery the probe edits is still hinted.

A probe that walks candidates to reach a reproducible record tightens from what
the walk rejected, per `<precision-note>`. A probe that has to retry is a probe
still deciding what it is looking for, and a SIR built on one is harder to hand
over than the walk was to run.

Record the identifiers the dev team can look up in the application, which are
`<identifiers>`. For a UI defect it is the record the run navigated to.
Keep the link to the run for the user, who needs it to find the output again; it
does not go in the SIR. Say it while the run is still going, not only
afterwards: a session waiting on a probe run names the tests it is waiting on
and links the run, one line per run in flight, so the user can follow it without
asking.

Run `<branch-age-note>` once before the first run of a probe set, every run
section 2 sends from 2.2 through 2.5, and not between them, so the evidence and
its controls come from one tree. Send every probe run with `<test-dispatch>`.
Wait on it per `<run-watch>`.

### 2.3 Run a positive control

Show the same call or the same control accepting a value that is supposed to
work. Without it the reader cannot tell a broken validation rule from an
endpoint that validates nothing, and those are different fixes.

A probe that only produces the failing call proves nothing. The same rule is in
`<control-note>`.

The control is what lets the gate pass, not something the SIR carries. Its
result goes to the user alongside the SIR text and into the record file's
`What was measured`.

### 2.4 Run a negative control

Show a value that is invalid for an unrelated reason being rejected. That is
what narrows the defect from "no validation here" to "this specific rule is
missing", which is the sentence the dev team acts on. It is recorded the same
way the positive control is, outside the SIR.

### 2.5 Prove the effect, not just the response

An API answering with success proves acceptance. It does not prove the bad
value persisted. Read it back: a follow-up GET, a read of the stored data
through `<schema-lookup>`, or a UI screenshot of the record.

The two outcomes are different defects with different fixes.

- Value stored: validation is missing. Data is now wrong.
- Value silently dropped: validation is missing and the caller is told a change
  succeeded that did not happen.

Say which one the evidence shows. If the read-back was not possible, say that
in the SIR rather than letting the reader assume it was checked.

### 2.6 Record the environment

Environment name, API version, app build or deploy date, and the acting user
and logon. A defect reproduced under one worker's security profile and
not another's is a different defect.

Gather all of it, then put only what the reader needs in the SIR. The header
carries `<env-fields>`, each one word:

- The environment field, the environment name alone. Everyone reading it works
  the same handful of environments and the rest of the string is noise.
- The client level the call went in as.
- The logon the call acted as.

The endpoint and its version belong in the `Reproduction` step that names the
call. Keep a build or deploy date out unless the defect turns on it, and say so
when it was never available.

No date goes in the SIR body. ALM stamps its own, and a second date in the text
is one more thing to keep true. The date the probe ran belongs in the record
file's `Updated` line.

### 2.7 Name the class, not the examples

Three inputs rejected by the same missing check are one defect, so write it as
one reproduction that walks the inputs and one statement of the rule that is
missing. The record gets one SIR either way, so a second unrelated
failure found along the way is reported to the user and written as its own
`possible` record instead of being bolted onto this report.

Then name the neighbors that were **not** tested. Untested neighbors are
usually:

- the same rule on the sibling field
- the same code in a mixed payload alongside a valid one
- the same code arriving through the other verb that writes the field

They stay out of the SIR, which reports what was measured. Report them to the
user alongside the SIR text and log them through `<learning-log>`, so the next
probe of the same endpoint starts where this one stopped.

### 2.8 Outcome

If 2.1 cannot produce a verbatim quote, stop. Say which documents were searched
and came back empty, and ask the user for the document, per `<asking-note>`. A
SIR is never written around a remembered rule.

If any of 2.2 through 2.5 fails, stop. Report to the user what reproduced, what
did not, and what would be needed to close the gap. Do not write SIR text for
an unproven defect and do not soften it into a "possible" SIR to get past this
step. `possible` is a record state for a queue of things still to probe, not a
confidence level inside a filed SIR.

## 3. SIR text

The SIR text is pasted into ALM, which is a plain text field with no formatting
of any kind. Nothing is marked up. No `**`, no `#`, no backtick fences, and
no HTML tags: every one of them arrives as the literal characters and tells the
reader the SIR was written somewhere else and pasted in.

Structure comes from three things a plain text field does keep, and nothing
else:

- A heading is its own line in capitals, with a blank line above and below it:
  `REQUIREMENT`, `EXPECTED`, `ACTUAL`, `REPRODUCTION`. Capitals are what a
  reader scans in a wall of plain text.
- A label is its own line ending in a colon, in sentence case: `Environment:`,
  `Request:`, `Response:`. A one-word value sits on the same line after it.
- A blank line separates every block. A numbered step is its own line, and the
  evidence hanging under it is separated from the next step by a blank line.

The defect title carries no label and no capitals beyond the ones the sentence
already carries. It is the ALM summary, which is its own field, so it is handed
over on its own rather than as the first line of the description.

Evidence keeps its own line breaks and its indentation, which the field
preserves. A JSON object that lost its alignment is no longer a copy of what
went over the wire, so nothing is re-flowed to fit.

Emit the SIR as two fenced blocks, one per ALM field. The title goes in the
first, under a `Title:` line. Everything from the header fields down goes in the
second, under a `Long description:` line. The fences are not part of the SIR:
they are the containers that get the text through the Markdown surfaces this
skill writes to, and they are what make the copy button hand over exactly the
bytes ALM receives.

Two blocks rather than one because ALM takes the summary and the description in
separate fields. A single block makes the user cut the first line out of what
they pasted, every time, and a title that arrives at the top of the description
is a title nobody notices is wrong. Nothing above the first fence but a one-line
note of what to do with the pair. Section 4 writes both blocks into the
`likely-valid` record and repeats them in the chat report.

A SIR is read by someone triaging a queue. Length costs it attention, so every
line either helps them find the record, judge the outcome, or fix the code. Cut
everything else. The target is under a page per SIR, and evidence blocks are
what the page is spent on.

Write it tight:

- One sentence per field. `Expected` and `Actual` are one line each, never a
  paragraph, and `Actual` names only what differs from `Expected`.
- Never restate a fact the reader already has. The header carries the
  environment, so no step repeats it, and `Actual` carries the behavior, so no
  later line narrates it again.
- Cut every sentence explaining why the evidence counts as evidence. The
  measurements carry themselves.
- No sentence about what the reader would conclude, what the report shows, or
  how the steps relate to each other. State the facts and stop.
- Drop a step that adds no new fact. Two records proving the same behavior are
  one step naming both records, not two.
- Untested neighbors are reported to the user, never inside the SIR.

A SIR reports a potential defect. It does not ask the team a question, request a
decision, propose which of two fixes to apply, or address the reader at all. No
"please", no "should this be", no "the answer decides whether". The team owns
what happens next and does not need a tester's framing of their options.

There is no `Impact` field. A SIR carries the requirement, the behavior, and
the records, and the team reads the consequences off those faster
than a tester can guess at them. What a defect costs depends on who calls the
endpoint and what they do with the answer, which is knowledge the SIR's reader
has and its writer does not.

Where two behaviors conflict, that conflict is a fact and gets its own step,
stated the way every other measurement is: what this endpoint
does, what the other one does, and the source that says so. A reader who sees
both facts asks the question on their own, and it is theirs to answer.

    Yes: <Endpoint A> answers the same situation with success and an empty
         error list (SIR <number>, closed remain as is <date>).
    No:  Please settle which answer a spent key is supposed to get, because the
         two endpoints cannot both be right.

The SIR text and the record file sit outside `<writing-rules>`, which skips
them. Any comment this validation leaves in a test still goes through
`<writing-rules>` before the commit. Once the record carries an ALM number its
paste block is a copy of what the dev team holds, so nothing in it changes after
the hand-off.

The record file also passes `<record-checks>`, which check that the acronym
dictionary knows what its short forms stand for, and that its page name and
links are ones the documentation can carry. The acronym
scan stops on any acronym its dictionary does not hold. Add the row with the
document that states the expansion, and never write one nobody can source. The
record file itself is not written to, and neither is the SIR text handed to the
dev team, which is fenced and skipped.

A SIR is technical reference prose, so the neutral voice is correct and any
personality guidance in `<writing-rules>` does not apply. The patterns that do
bite a SIR are the ones that pad it: significance-inflation ("this
demonstrates", "underscores"), `-ing` tails bolted onto a finding, hedging and
weasel attributions where a measured value belongs, rule-of-three lists padded
to three, negative parallelism ("not X, but Y"), and elegant variation, which
in a defect report is a correctness bug rather than a style one: the field is
called the same thing every time it appears or the reader thinks there are two
fields.

Verbatim quotes, response bodies, payloads, identifiers, and error strings are
evidence, not prose. The humanizer pass never touches them.

### What never appears in a SIR

The SIR body sits outside the `<writing-rules>` scan, so this list is applied by
hand. The reason for it: the SIR body describes the application
and the document that governs it, and naming how the observation was made hands
the reader a place to look that they cannot reach and a reason to discount the
report.

Out of the SIR entirely, including the `Reproduction` steps:

- The code host in any form: a repository name, a URL, an issue or pull request
  number, a branch, a commit.
- The automation that ran the probe, in any form: a run URL, a job link, a run
  or job ID, a workflow name, a runner, an artifact path or share location.
- AI in any form: an assistant, an agent, a model, a generated-with line, a
  robot emoji. A tester wrote this.

The reproduction is written so a person can follow it by hand. "Open the record
and click Save" is a step. "Rerun the spec with a grep on the test ID" is not.

A request or response body that carries a test's own value stays as it is. It
is what the endpoint was sent and what it answered, and the reader never has to
fetch anything to read it.

Say the link to the run and the record path to the user in the line above the
SIR, alongside the destination. They need both. The SIR does not.

### Voice

A tester typed this at the end of a long day, not a technical writer. It should
read that way, or the reader wonders who really wrote it.

- Short words. "sends" over "transmits", "shows" over "demonstrates", "lets"
  over "permits", "runs" over "executes", "same" over "identical".
- Say the actor. "The server accepts the update", not "the update is accepted".
- One idea per sentence. When a sentence has a comma in the middle holding two
  clauses together, it is usually two sentences.
- No stock report phrases: "it should be noted", "as expected", "the following",
  "in order to", "this indicates that".
- No lecturing connectives: "thus", "therefore", "hence", "accordingly", "as
  such", "consequently". Write "so" and "which means", or start a new sentence
  and let the order of the facts carry the link. A conclusion that needs
  "therefore" to hold usually needs another measurement instead.
- No sentences that grade the finding. Nothing "critical", "concerning",
  "significant", or "worth noting". No severity rating either: the reader rates
  it from the evidence. State what was measured and stop.
- Plain contractions are fine. Sounding stiff is a tell of its own.
- American spelling everywhere: behavior, canceled, license (the noun and the
  verb), gray. Never behaviour, cancelled, licence, honour, colour, or analyse.
  The one exception is a verbatim quote or a field name that already spells it
  another way. Copy those exactly.

Inside the fences, the SIR reads like this. The indentation below is this
document's, not the SIR's: every line starts at the left margin except the ones
inside a JSON object. The rule above the header fields is where the first fence
closes and the second opens.

    Title:

    <verb-less statement of the defect, one line>

    ---

    Long description:

    <one header line per field in the env-fields list, each value one word>

    REQUIREMENT

    <doc name>, rev <version>.

    <section or page>:
    <verbatim quote, enough of it to stand without the surrounding page. a quote
    of one line sits in quotation marks on the line below the section. a quote
    of several lines keeps its own line breaks and starts at the left margin>

    <repeat the section heading and quote for each additional rule from the same
    document, naming the step it governs. the document is named once, above.
    one line of context per quote at most, and only where the quote cannot be
    read without it>

    EXPECTED

    <what the app should do, stated as one observable outcome>

    ACTUAL

    <what it does, stated as the same kind of observable outcome>

    REPRODUCTION

    1. <setup, including how the test record was obtained>

    2. <the call, naming the endpoint and version, or the click, naming the page>

    Request:
    <the whole request body, exactly as it was sent>

    Response:
    <the whole response body, exactly as it came back>

    3. <the next step. a step that rests on no call is its line and nothing else>

    4. <the read-back or the second call, where the reproduction runs on>

    Request:
    <the whole request body, exactly as it was sent>

    Response:
    <the whole response body, exactly as it came back>

The last step is the end of the SIR. Nothing follows it: no controls block, no
closing sentence naming the rule, no summary of what the steps add up to. The
controls were run and they are what let this SIR be written, but they live in
the record file and in what goes to the user. A reader triaging the queue needs
the requirement, the behavior, and the records, and stops there.

One reproduction path, walked once. The reader follows it from the first line to
the last and sees the defect, so the numbers run unbroken and every step is
something they do next rather than a variation set beside the others. A second
record proving the same behavior is named inside a step, never given a path of
its own.

Take as many steps as the walk takes. A reproduction is as long as the shortest
honest path to the defect, so nothing is folded together to hit a count and
nothing is padded out to reach one.

The destination stays out of the SIR body. Classify it in section 1, act on it
while gathering evidence, and tell the user which team the SIR goes to in the
line above the SIR.

A step carries no field labels. Its number and its sentence, then `Request:` and
the request object, then `Response:` and the response object. Those two words
are the only labels: they say which direction each block runs, which a reader
scanning a queue should not have to work out from the contents. Nothing is
aligned into columns either. Hand-aligned labels come apart in a proportional
font, and the field the SIR lands in is not guaranteed to be monospaced.

Do not wrap the lines. The source-code line limit does not apply here: this is
prose going into a text box that wraps on its own. Hand-wrapped lines re-wrap
into a ragged mess there, and a reader who copies a quote back out gets line
breaks in the middle of it. Write each field, sentence,
and quote on one line however long it runs. The only breaks are the ones that
mean something: between fields, between steps, and between a quote and the text
around it.

### The evidence blocks

Evidence hangs off the step it belongs to, under the sentence that says what the
reader is doing. A step that calls the endpoint carries the two JSON objects and
nothing else: the request body as it was sent on the lines under `Request:`,
then the response body as it came back on the lines under `Response:`, each one
pasted whole with the line breaks and indentation it already has. Those two
words are the whole labelling. No `Input`, `Record`, or `Data` labels, no field
labels inside the objects, no prose restating what they already say, and no
lines lifted out of a run log. The reader can read JSON.

Not every step has evidence, and a step without it is not weaker for that. Setup
and observation steps are sentences on their own, and only a step that actually
went over the wire carries a request and a response.

A response that is not JSON is still evidence, and still labelled. An empty body
says what arrived, in parentheses on the line under `Response:`:

    Response:
    (HTTP 500, no response body)

Both objects go in whole. A trimmed response is a response the reader has to
trust rather than check, and the fields a tester thinks are noise are often the
ones that identify the record: the record identifiers all arrive that way.
Never paraphrase a field either. A field shown as null is the evidence.

The one thing that comes out is a field whose value is a wall of Base64 or an
embedded document body. Replace that value with `<...>` and leave the key, so
the reader sees the field was there without losing the page to it.

A read-back is a step of its own, labelled the same way: the follow-up GET under
`Request:`, and what it answered under `Response:`. That
keeps every piece of evidence in the same form and gives 2.5 somewhere to land.
When no read-back was possible, one sentence under the last step says so.

Where a read echoes values decoded and a write takes codes, as `<decode-note>`
describes, translate one side when a SIR compares a value sent against a value
read back, and say which side was translated, or the comparison reads as a
second defect that does not exist.

## 4. Handoff

The SIR text goes to the user, who submits it. This skill never submits one.

Settle the record once the outcome is known, whether that outcome is SIR text or
a dismissal. The outcome is the record's move, per section 5, and nothing else
carries it: no issue is commented, labeled, or closed for a SIR, per
`<records-note>`.

- A defect that cleared 2.1 through 2.5 moves from `possible` to
  `likely-valid`, never straight to `valid`. The
  record gains the whole SIR in the two fences of section 3, so what the user
  copies out is the plain text ALM receives, one field at a time, and nothing
  has to be cleaned up by hand.
- A defect the gate disproved moves from `possible` to `invalid`. Its `Outcome`
  says in one or two sentences what was probed, on what records, and why it did
  not reproduce. Nothing reached ALM, so there is no number to record, no fix to
  wait for, and no later skill that picks it up.

The same two fences go into the chat report the skill ends with, so the user can
copy the SIR from either. The destination team, the link to the run, and the
untested neighbors are said to the user in chat and stay out of the record, and
the rules in section 3 about what never appears in a SIR apply to the record the
same way.

A SIR that is rewritten after the dev team answers replaces the text in the
record rather than joining it, so the record carries one copy and the user
cannot paste a stale title into ALM.

`likely-valid` is the user's queue. The gate clearing is not the last word on a
SIR: the user reproduces it by hand and reads the SIR text before anything
reaches ALM, and this skill never skips that step or marks it done on the
user's behalf. Only the hand check makes a record `valid`.

Everything downstream of `likely-valid` belongs to another skill or to the
user. The user vets the SIR by hand through `<hand-check-skill>`,
which writes the record's `Verified:` line and moves it to `valid`, or sends
the record back to `possible` or on to `invalid` when the hand check does not
reproduce it. `raise-sir` then files the `valid` SIR and moves the record to
`raised`, and refuses a `likely-valid` one unless the user says it was vetted
another way. A SIR the user enters in ALM by
hand instead is picked up by `<housekeeping-skill>`, from the number the user
gives in chat or from a new ALM number whose Short Description matches the
record's title. `<housekeeping-skill>` thereafter moves the record on whatever
ALM currently reads, and `retest-sir` moves it to `retested` or `failed-test` off
its own measurement. This skill never makes any of those moves.

A stop before the gate finished is neither outcome. A missing document at 2.1,
or a probe blocked before it ran, leaves the record `possible` and releases the
claim, because nothing was proved either way and the next session picks it up
where this one stopped.

If the probe or the spec run behind it turned up a further deviation, it gets its
own `possible` record under `<records-root>` in the same pull request, one
record per deviation, per `<deviation-note>`. It is never filed as an issue.

Take the probe back out of the codebase before the pull request. A probe spec, a
scratch test case, an instrumentation log line, a loosened assertion, a
test narrowed to run alone, and a temporary fixture or SQL file are all built to answer one
question, and the answer now lives in the record file and the SIR. Diff the
branch against the main branch and confirm what remains is the record file and
any test change that is a real fix. Nothing written to measure the defect ships.

A probe worth keeping is a probe worth writing as a test on its own terms, with
a matrix ID and a title, not left behind because it happened to run.

The coverage plan is off limits. A `<plan-doc>` row says what the application is
supposed to do, which is the rule the SIR is written against, so a validated
defect never edits one. Rewriting a row from "rejected" to "accepted" turns the
coverage matrix into a description of the broken behavior, and the next reader
has nothing left to compare the application to. The row stays as the
documentation says, whatever the endpoint answered, for the whole life of the
defect, including after the SIR is raised and while it sits unfixed.

That holds for every document that carries the intended behavior, which are
`<intent-docs>`, and a plan row drawn from them. A doc changes when the design is
wrong, which is a design SIR with its own evidence, never as a side effect of
measuring what the code does.

What the defect does change is the test code, which reports what the endpoint
answers today. Say in the pull request that the assertion and its plan row now
disagree, and name the SIR that closes the gap.

Move the record to its outcome state in the same pass, per section 5, regenerate
the index in the same commit, and commit both on a branch with a pull request,
running `<branch-age-note>` before the pull request is created: the probe set
behind the record can run across days. The pull request body lists the path of
every record the branch wrote or moved, and carries the provenance the record
leaves out: the run ids, the job links, and the cost of the probe. Release the
claim as soon as the pull request opens:

`<claim-script>`, with `release`, the record, and the branch.

Read that pull request's mergeable state as soon as it exists and resolve any
conflict without being asked, per `<mergeability-note>`. Merging it means the
record landed, not that the defect was reported: a `likely-valid` record waits on
the user's hand check and then entry in ALM. Commit messages and the pull request
body go through files in `<scratchpad>`, per `<shell-text-note>`.

Log what the validation gate established through `<learning-log>`, especially a
control result or an untested neighbor. The next investigation of the same
endpoint starts from it.

Before the handoff, the session reviews its own pull request, per
`<self-review>`.

The last line of the whole run is the pull request handoff, in the wording
`<ready-signal>` sets. It goes below everything else, including the untested
neighbors and the links to runs. A run that opened no pull request, a stop
mid-gate that left an existing record as it stood, says nothing in its place.

## 5. The SIR record under `<records-root>`

Every suspected defect gets one Markdown file under `<records-root>`, filed in a
directory named for the suite and carrying its state in the file name:

```
<records-root>/<SUITE>/<state>-<short-slug>.md
<records-root>/<SUITE>/SIR_<number>_<state>-<short-slug>.md
```

A record whose `SIR:` line starts with an ALM number, `SIR: <number>` or
`SIR: <number>, withdrawn`, takes the second form, with that number after `SIR_`.
A record still reading `SIR: not raised` takes the first.

The suite directory is the same abbreviation the suite label and the test tree
use, uppercase. One endpoint or page tends to produce several SIRs over its
life, and grouping them by suite keeps a reader who works one application out of
every other application's queue.

The slug names the behavior, the way an investigation write-up does:
`<behavior-slug>`, not a tracker number. A tracker number in a file
name tells a reader scanning the directory nothing about what the file holds,
and a record never names a tracker issue at all, per the shipping rule below.
The ALM number in the `SIR_<number>_` prefix is the SIR's own identifier in ALM,
and it never changes once ALM gives it.

The states, per `<record-states>`, are `possible`, `likely-valid`, `valid`,
`invalid`, `raised`, `migrated`, and then one of `retested` or `failed-test`, in
that order. A state change renames the file and never copies it, so one defect
is one file for its whole life and a listing of a suite's directory reads as
that suite's queue. Only the `<state>` part changes; the number and the slug
stay. A move is a `git mv` from the old name to the new one:

```bash
git mv <records-root>/<SUITE>/possible-<slug>.md \
  <records-root>/<SUITE>/likely-valid-<slug>.md
git mv <records-root>/<SUITE>/likely-valid-<slug>.md \
  <records-root>/<SUITE>/valid-<slug>.md
git mv <records-root>/<SUITE>/valid-<slug>.md \
  <records-root>/<SUITE>/SIR_<number>_raised-<slug>.md
git mv <records-root>/<SUITE>/SIR_<number>_raised-<slug>.md \
  <records-root>/<SUITE>/SIR_<number>_migrated-<slug>.md
```

- **possible**: written when the record is claimed, before the probe spends a
  runner, or by the deviation gate when a spec run finds the app and the doc
  disagreeing, per `<deviation-note>`. It holds the suspected defect, the rule it
  appears to break, and what the probe is going to measure.
- **likely-valid**: the gate cleared 2.1 through 2.5. The file now carries the
  finished SIR text, the same text the chat report hands the user, and waits on
  the user's hand check. This is as far as this skill moves a record.
- **valid**: the user reproduced it by hand. `<hand-check-skill>` adds a
  `Verified:` line under `Updated:` and a `## Manual verification, <date>`
  section, and renames the file from `likely-valid-` to `valid-`. The record
  waits on entry in ALM.
- **invalid**: the gate disproved it, or a raised SIR was later withdrawn. The
  file keeps what was probed and why it did not reproduce, because the next
  person to suspect the same thing reads this instead of re-running it.
- **raised**: only when the SIR is in ALM with a number. This skill never moves
  a file to `raised` on its own: `raise-sir` moves one there when it files the
  SIR, and `<housekeeping-skill>` moves a `likely-valid` or `valid` record there
  when the user gives the number in chat or ALM holds a SIR whose Short
  Description matches the record's title.
- **migrated**: the fix reached the test environment, which ALM reports as
  `Migrated` and `<housekeeping-skill>` records, and nothing has measured it yet.
  `retest-sir` moves a `raised` record here when it claims the record, and the
  user may move one by hand when the retest is done manually. The record
  gains a `## Migrated, <date>` section saying what the team reports changed.
- **retested**: the fix was measured and the defect is gone. `retest-sir` owns
  this state and only reaches it on measurement, never on the dev team saying
  the fix is in.
- **failed-test**: the fix was measured and the defect is still there. The
  record stays live, and its `Impacted tests` list stays current.

A defect that stops mid-gate stays `possible`, and its claim is released so the
next session can pick it up.

`raised` and `migrated` are not terminal. A raised SIR is answered by a fix,
the fix reaching the test environment makes it `migrated`, and the migrated
fix is answered by `retest-sir`, which lands the record on one of the two
states above.

`<records-root>` ships to a separate work repository that knows nothing about
this one, so the record file is held to the same rule as an investigation
write-up. It never names a tracker issue, a run, a workflow, a runner, an
artifact path, or any assistant. It may name the spec file and the test title,
which are the application's own vocabulary for the reproduction.

Provenance still has to live somewhere, and that somewhere is the pull request
body and the commit message that land the record: the run ids, the job links,
and the cost of the probe, per `<records-note>`. Both stay on this side. The
record file keeps the finding, and the pull request keeps where the finding came
from.

Every branch that writes, renames, or moves a record regenerates the index in
the same commit, so the index never disagrees with the files:

`<index-command>`

```markdown
# <defect title, the same one-liner the SIR uses>

State: <possible | likely-valid | valid | invalid | raised | migrated | retested | failed-test>
SIR: <ALM number, or "not raised">
Team: <dev | design>
Updated: <date>

## Suspected defect

<what the app appears to do wrong, one paragraph>

## Requirement

<doc name>, rev <version>.

<section>:
"<verbatim quote>"

## What was measured

<records, controls, and read-back results, identified the way the application
identifies them: `<identifiers>`, and the acting logon. in `possible` state this
is the plan instead, saying what the probe will measure>

## Outcome

<the gate result in a sentence. from `likely-valid` on, the finished SIR text follows,
in the same two blocks the chat report carries and nothing but them:>

````markdown
Title:

```
<the defect title, the ALM summary field on its own>
```

Long description:

```
<the rest of the SIR, the same plain text that went into the chat report and
into ALM, copied without reformatting any of it>
```
````

## Impacted tests

<only in `raised` state, see below>
```

### Moving a record to `raised`

The user says the SIR was raised and gives the number. Only then:

1. Set `SIR:` to the ALM number and `State:` to `raised`, and add an `Author:`
   line under `SIR:` holding ALM's `Detected By`, read back out of ALM through
   `read-sir`, per `<raise-steps>`. A numbered record without it fails the index
   check, per `<housekeeping-skill>`.
2. Rename the file from `valid-<slug>.md`, or `likely-valid-<slug>.md` when the
   user raised it without the hand check, to `SIR_<number>_raised-<slug>.md`.
3. Fill in `Impacted tests`.

`Impacted tests` lists every spec file and test that the defect touches, one per
line, with the file path and the test title or matrix ID, and one clause on how
the defect shows up there. Search the codebase for it rather than recalling it:
the endpoint or page name, the matrix IDs the record's own `What was measured`
names, and any test already skipped or soft-asserted around the behavior. The
tests already parked are in `<skip-ledger>`, with what each one waits on, so
search the ledger's reason and unskip entries for the page or rule; a parked
test the record now explains gets this SIR's number, per `<skip-ledger>`.

```markdown
## Impacted tests

- <test file>, <matrix ID>: <how the defect shows up in this test>.
- <test file>, <matrix ID>: <how the defect shows up in this test>.
```

An empty list is a sentence saying no test covers the behavior yet, not a blank
heading. That sentence is the argument for writing one.

### Withdrawing a raised SIR

`<withdrawal-note>` carries the withdrawal: who may withdraw a SIR, the record's
move to `invalid` keeping its ALM number, and taking the number back out of the
code. Follow it as written, except that no issue is labeled or closed for it, per
`<records-note>`.
