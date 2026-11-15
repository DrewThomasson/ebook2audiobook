---
name: build-test-pack
description: Build a test pack workbook for one defect record and its change record by running a phased Build Test Pack procedure, each phase gated before the next, and writing the workbook a workbook standard defines, or one for a suite's whole approved rule set. Use when asked to build, make, or generate a test pack for a defect or a change. Also use to load an approved suite pack into the test management tool's test plan and test lab.
---

# Build Test Pack

Takes a `<issue-term>` number, a `<change-term>` number when the change has
one, and the source documents. `<invocation>` names both; the documents can be
named in the request, attached, or found in the repository.

When the repository names `<pipeline-config>`, the pack is built by the local
pipeline, not by the session: see "Running on the local model" below. The
session then reads none of the inputs and none of what the pipeline writes.

The procedure and the standard are the reference material's, and they live only
in `<reference-dir>`. This skill is how they run in a repository: which of the
procedure's inputs come from where, what each phase writes into the pack file,
and the builder that turns that file into the workbook.

The consuming repository's extension supplies the values below. Where it names
none, ask the user rather than guessing.

| Placeholder | Meaning |
| --- | --- |
| `<issue-term>` | What the repository calls the defect record a pack is built for |
| `<change-term>` | What it calls the change record that fixes it |
| `<invocation>` | An example request that names an issue and its change |
| `<suite-invocation>` | An example request for a suite pack |
| `<suites>` | The suites a suite pack can be built for |
| `<reference-dir>` | The folder that holds the procedure, the standard, and their companions |
| `<procedure>` | The phased Build Test Pack procedure: the phases, their order, the stop conditions |
| `<phase-count>` | How many numbered phases `<procedure>` has |
| `<workbook-standard>` | The workbook standard: name, sheets, columns, objectives, status values |
| `<sheet-count>` | How many sheets `<workbook-standard>` defines |
| `<objective-count>` | How many testing objectives `<workbook-standard>` defines |
| `<intake-procedure>` | The job intake read before Phase 1 |
| `<job-type>` | The job type code and name intake classifies this request as |
| `<understanding-gate>` | Phase 1's procedure: source authority order, the PASS conditions |
| `<rule-intake-procedure>` | Phase 2's procedure |
| `<scope-procedure>` | Phase 3's procedure |
| `<validation-procedure>` | Phase 9's validation checklist |
| `<revalidation-procedure>` | Phase 9's revalidation |
| `<implementation-guide>` | The traceability and reuse rules every phase keeps |
| `<methodology>` | The testing methodology the phases lean on |
| `<methodology-chapters>` | Which `<methodology>` chapter covers which subject |
| `<glossary>` | The reference material's terms |
| `<manifest>` | The reference archive's own list of SHA-256 fingerprints |
| `<manifest-check>` | The test that checks every reference document against `<manifest>` |
| `<shipped-paths>` | The paths that ship beyond the repository and so may not carry reference text |
| `<component-map>` | Where each repository component `<procedure>` expects loaded is found |
| `<baseline-packs>` | Packs kept as the bar a new pack should match or beat, read for shape and depth |
| `<description-source>` | Where the change or defect description comes from |
| `<rule-export>` | The command that exports one document's rules from the master |
| `<folder-export>` | The command that exports a suite folder's rules |
| `<process-docs>` | Where process descriptions live and how one is found |
| `<design-docs>` | Where design and module specifications live |
| `<attached-only>` | Inputs with no copy in the repository, attached by the user |
| `<existing-tests>` | Where existing test plan and test lab assets come from |
| `<existing-automation>` | Where existing automated tests for the same screen live |
| `<test-tool>` | The test management tool that holds the test plan and the test lab |
| `<id-fields>` | The pack fields that name the issue, the change, whether a change applies, and the change description |
| `<pack-file>` | The pack file's name for an issue pack |
| `<suite-pack-file>` | The pack file's name for a suite pack |
| `<case-id>` | The test case ID pattern for an issue pack |
| `<suite-case-id>` | The test case ID pattern for a suite pack |
| `<suite-workbook-name>` | The workbook's name for a suite pack |
| `<rule-code-example>` | How a card file's code is read from a rule's prefix, with an example |
| `<derived-rule-example>` | An example name for a rule the master does not hold |
| `<dashboard-sheet>` | The sheet with the counts and the coverage percentage |
| `<objective-sheet>` | The sheet that relates objectives to cards and sets |
| `<upload-sheet>` | The sheet that is the `<test-tool>` test plan import |
| `<rule-matrix-sheet>` | The sheet that maps every rule to its tests |
| `<coverage-sheet>` | The sheet with each rule's coverage status and gap |
| `<validation-sheet>` | The sheet that carries each sheet's validation status |
| `<cards-sheet>` | The sheet that carries the test card titles |
| `<notes-sheet>` | The sheet that carries tester notes |
| `<confidence-sheet>` | The sheet that carries the confidence assessment |
| `<intake-sheet>` | The sheet that carries job intake |
| `<core-objective>` | The objective that tests the change itself |
| `<break-objective>` | The objective that tries to break the change, run last |
| `<full-coverage-objective>` | The objective whose set runs every card that comes from a requirement |
| `<suite-merge>` | The command that merges a suite pack's card files and narrative |
| `<pack-builder>` | The command that builds the workbook from a pack file |
| `<testpack-command>` | The command that loads a suite pack into `<test-tool>`, dry run by default |
| `<committed-pack>` | Where an approved suite pack file is committed |
| `<pack-source>` | Where `<testpack-command>` reads the pack file from |
| `<upload-script>` | The script that does the load |
| `<rule-upload>` | The command that loads a suite's rules and records their `<test-tool>` ids |
| `<plan-folder>` | The test plan folder a suite's tests go under |
| `<lab-folder>` | The test lab folder a suite's sets go under |
| `<tool-roots>` | The root folders of the two trees, which always exist |
| `<shared-folders>` | The folders the first suite creates and the rest reuse |
| `<name-substitutes>` | Characters `<test-tool>` refuses in a test name, and what replaces each |
| `<ask-user>` | How the session asks the user for a missing input |
| `<follow-up>` | How a gap in the repository's own tooling is filed |
| `<docs-root>` | The documents folder, one folder per suite |
| `<writing-gates>` | The checks text under `<docs-root>` passes before it is committed |
| `<send-file>` | How the finished file is sent to a user following from another device |
| `<extract-skill>` | The skill that extracts a document's rules for the first time |
| `<update-skill>` | The skill that updates a document's rules in the master |
| `<scratchpad>` | A scratch directory outside the repository |
| `<pipeline-config>` | The local pipeline's config file, when packs are built on the local model |
| `<pipeline>` | The local pipeline's command, `node <this skill's folder>/local/build-pack.mjs` |

| Reference | What it governs |
| --- | --- |
| `<procedure>` | the `<phase-count>` phases, their order, the stop conditions |
| `<workbook-standard>` | the workbook: name, `<sheet-count>` sheets, columns, objectives, status values |
| `<intake-procedure>` | the intake read before Phase 1 |
| `<understanding-gate>` | Phase 1, source authority order, the PASS conditions |
| `<rule-intake-procedure>` | Phase 2 |
| `<scope-procedure>` | Phase 3 |
| `<validation-procedure>`, `<revalidation-procedure>` | Phase 9 |
| `<implementation-guide>` | traceability and reuse rules every phase keeps |
| `<methodology>` | the methodology, chapter by chapter as `<methodology-chapters>` gives it |
| `<glossary>` | the reference material's terms |

Read `<procedure>` and `<workbook-standard>` in full before Phase 1. Read each
procedure as its phase starts, and the `<methodology>` chapter a phase leans on
when the phase starts. A methodology too large to read whole is read by chapter
with a line range.

`<manifest>` is the reference archive's own list of SHA-256 fingerprints, and
`<manifest-check>` checks every reference document against it. A failing check
means the copy in the repository is no longer the one that was verified.

## Running on the local model

With `<pipeline-config>` set, the whole pack is built by `<pipeline>` against the
local model the config names, and no part of it passes through the session. The
pipeline runs intake and every phase below as fixed prompts that answer against
a JSON schema, checks each gate in code, and ends with `<pack-builder>`, feeding
any FAIL back to the model a bounded number of times. Its config names the
endpoint, which must be on the loopback interface, the model, the reference
documents and the methodology chapters each phase reads, the input commands
(`<rule-export>`, `<folder-export>`, the description and the document index),
and `<pack-builder>` and `<suite-merge>`, which it runs unchanged.

Three config keys feed the design phases. `reference.operatingManual` names the
operating rules, such as preferring an existing test to a new card; the Phase 6
card calls and the Phase 7 set call read it, and no other phase does.
`methodology.byPhase` lists the chapters each phase reads, keyed by phase number,
and Phase 7 takes its chapters from the key `7`. `inputs.existingTests` is a
pattern filled with the job's values; every file it matches is read whole and
given to the Phase 6 card calls and the Phase 7 set call. When the existing tests
do not fit beside the set information, Phase 7 leaves them out and says so in
`detail.log`. `detail.log` also records, for Phases 6 and 7, which chapters,
whether the operating manual and how many tokens of existing tests each phase was
given.

Each document's rules are checked in two places. Intake checks every document
it resolves, and stops with a code and the document's number when:

| Code | Meaning |
| --- | --- |
| `rule-export-failed` | `<rule-export>` failed for a reason other than the next row, so an outage never passes for a document with no rules |
| `rules-malformed` | the export is not the shape the rule master writes: the top level, `doc`, the prefix, the rule IDs and their uniqueness, the statuses, or an empty rule list; what is wrong goes to `detail.log` only |

A document whose path is outside the repository root, missing, or not a file is
`document-file`: the export is not run, and intake stops with `missing-inputs`.

Phase 2 reads the export again for each Included document whose rules intake
did not just export, so a job resumed after the rules were extracted sees them.
It writes a `stop-doc` status line per failing document, then stops with a
count and the document numbers under the first code that applies:
`document-file` (as above, so a bad path never reads as a document with no
rules), `rule-export-failed`, `rules-malformed` (the last two as above), then:

| Code | Meaning |
| --- | --- |
| `rules-not-extracted` | the document is in the repository and the export's error output matches the config's `noRules` pattern, its own way of saying the document has no rules in the master yet |

An export outage in Phase 2, or a path that no longer resolves, for a document
whose rules intake read keeps those rules and leaves a `warn` status line. So
does a `noRules` answer for a document intake read as `rules-ok` or
`rules-stale`, with the reason `rules-not-extracted`: rules in the master do not
disappear between two phases. A valid rule list from the new export replaces the
held rules.

A document that is only supporting context needs no rules: Phase 2 does not
read it again, and a missing or stale rule set on it never stops the job.

Values the master holds that the current procedure would not write (an older
category, a requirement type that names a category, a blank column, a page the
document cannot place) are warnings in `detail.log`, not a stop. So is `rules-stale`: the document's provenance revision date is later than
the day its rules were last confirmed (the export's `reviewed` or
`last_reviewed` day when it has one, else the newest `created` date on its
rules). A stale export leaves a `warn` status line with the document's number;
the session offers `<update-skill>` for it and does not stop the job. A document
that states no revision date is not checked.

`rule-page-missing` is a warning raised at the end of Phase 2 for each Included
document with live rules whose source page is `N/A`. The status line carries the document
number and a count, the rule IDs go to `detail.log` and to the Job Intake limitation, and the
run goes on.

`retired-rule-missing` is the same kind of warning, raised at the start of Phase 2
for each Included document: its text has struck-through (`~~...~~`) text that
states something, outside code, and no rule citing it is in its rule export. Each
span is one of three. A fragment is part of a sentence (it does not end in `.`,
`!`, `?` or `:`, inside the tildes or just after them, and does not fill its line, list item or table cell), such as
`~~90~~ 120 days` or `~~not~~`; it is a wording or value change and never
warns. A restated sentence is a whole sentence followed in its paragraph by a
live sentence holding two thirds of its significant words (four letters or
more, common words left out); it never warns either. Any other span is a
removal, and a retired rule cites it when the rule's `source_page` is the span's
page (the nearest `page-N` marker above it), a range or list holding that page,
or the heading above the span. A live sentence that says something else beside
a struck one does not cite it. The warning
leaves a `warn` status line with the document's number and a `Job Intake`
limitation saying removed behavior may be missing; the job goes on. The session
offers `<update-skill>` for it.

The rules are derived from the document in Phase 2 only when the job or the
config opts in, with `--allow-derived-rules` or `allowDerivedRules` in the
config, off by default. Use it only when the user chooses to go ahead without
extracted rules; Job Intake then records the limitation. A retired rule stays in
the pack with a summary that starts "Retired:", and Phase 3 classifies it like
any other rule: Direct Change only when the change description concerns that
removal, Not Impacted otherwise. A retired rule's `status` is `Retired` (every
other rule's is `Active`), and it keeps that status whatever its class: there is
no "Superseded / Removal Verification" class. Phase 6 asks for at least one card
for every impacted rule, and for a retired Direct Change rule that card verifies
the behavior is gone.

### The model gate

The local model runs only on the user's yes. Before any command that loads or
calls it, the session asks through `<ask-user>` and waits for the answer. A
request to build, start or resume a job is the reason to ask; the yes is the
answer to the question. One yes covers one named run and nothing after it: a
second slice, a rerun after a stop, and a job queued for another night each get a
question of their own.

The question says:

- what runs, and on which job;
- how long it holds the machine: a job takes an hour or more, and a queue run
  holds it until its jobs end or the cutoff passes;
- which `pause` units stop for it, and which apps `closeApps` closes;
- when it ends.

Behind the gate, because each loads or calls the model, or puts a job in front
of a run that does:

- `<pipeline> run` in every form (an issue, a suite, a resume, a slice) and
  every `step` except `draft` and `build`, with the one exception on the free
  list below: a recording that answers every call;
- any slice or step with `--replay-miss live`;
- `queue add` in every form, and `queue fill`, which put jobs in front of the
  nightly run;
- `queue start`, and `queue run` in every form, which runs the queue's jobs on
  the model whenever it is started;
- starting `build-pack-now@<job-id>.service`, or starting `build-pack.service`
  ahead of its timer;
- enabling `build-pack.timer`, which starts `queue run` every night from then
  on;
- `compare` with `--config`, unless `--no-model` is given;
- a load on the model server, such as the `/load` call that saves the window.

Free of the gate, because none of them loads or calls the model or queues a
job:

- `check`, as the input gates or as the setup check, which reads the server's
  model list and the model's saved options and loads nothing, and
  `queue check`;
- `queue status`, `queue watch`, `queue summary`, `queue remove`,
  `queue cancel` and `queue restore`;
- the `draft` and `build` steps;
- a slice or a step answered from a recording with `--replay-miss fail`, the
  default, which serves every call from the recording or stops: the one case
  where `run` and a gated `step` are free;
- `compare` without `--config`, or with `--no-model`;
- `report`;
- the unit tests in `local/`;
- an unload of the model.

The nightly timer and its fill run jobs no one was asked about that night, and
they run on the user's yes all the same. A job reaches the queue only by the
user's own act: a line or a record they put in a `queue.sources` source, or a
`queue add` they said yes to. That act covers the job's tries in the queue,
the one retry included. Putting a stopped or dropped job back is a new run with
a question of its own. The session queues only what the user said yes to: a
source line is the user's to write, and a session whose other work adds a
record that a `records` source reads tells the user the nightly run will take
it.

A subagent cannot ask. Its brief says the local model is off limits, and it
returns the request to the session, which asks.

### Before a job is run or queued

Before `run` or `queue add`, the session refreshes the source documents, as
"Refreshing the source documents" under "Inputs, and where they come from"
sets out, and then runs the input gates, which make no
model call and print content-free lines only:

```bash
<pipeline> check --config <pipeline-config> --issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] [--resume]
```

Each line reads `<input>  present|missing  <code>`: the issue number, the
description, and each document by number with the reason code for its rules
(`rules-ok`, `rules-derived`, `rules-stale`, `rules-not-extracted`,
`rules-malformed`, `rule-export-failed`, or `document-file` for a document that
is missing, is not a file, or is outside the repository root). The exit code is 0 when every input is present, 1
when a required input is missing or a pause unit fails, and 3 when no `--doc` was given: the model
chooses the documents at intake, so only the candidates are counted and the
line `rules  unchecked  name-documents-with-doc` is printed. Pass the documents
the request names so their rules are checked before the job waits for the
night; a job with unchecked rules is queued only when the user chooses to.
What `check` found wrong with an export is in `<job-id>.check/detail.log` in
the pipeline's output folder, which a later run does not clear.

When `pause.units` is set, the gates also print each pause unit that fails the
setup check, as `pause  <unit>  fail  <code>`, for example
`pause  <unit>  fail  sudoers-refused stop start` when sudoers will not let the
run stop or start it (see "Freeing the machine for a job"). A passing unit
prints nothing, and a failing one makes the exit code 1. The line is about the
host, so the session reports it without asking for a document, and the job can
still be run or queued; the unit is then not stopped, or not started when the
run ends.

With `--resume`, `check` reads the job's checkpoint and checks the documents the
resumed run will use, not the ones `--doc` names. It prints
`checkpoint  present  <phase>` first, then one `document-<n>  present|missing  <code>`
line for each document the checkpoint holds, numbered as the job numbers them.
A document Phase 1 left as context only reads `context-only`, and a checkpoint
at Phase 2 or later reads `documents  present  past-phase2`, since those phases do
not read the rule export again. A document whose rules intake already read stays
`present` when its export now fails or its path no longer resolves, because
Phase 2 keeps those rules and only warns. A checkpoint saved at intake has no
inclusion decision yet, so every document counts as included. With no
checkpoint the job starts over and `--doc` is checked as above.

For every missing input, the session asks the user through `<ask-user>`:

- for each document without usable rules, offer `<extract-skill>`; for
  `rules-stale`, offer `<update-skill>`; for `rules-malformed`, offer
  `<update-skill>` and say the cause is in the check's `detail.log`, for the
  user to read;
- list the `<attached-only>` items, which `check` cannot see, and any rule
  extract to attach, and ask which the user has;
- offer to go ahead with limitations (`--allow-derived-rules` for a document
  with no extracted rules).

The job is run or queued only when the input gates pass (a `pause` line does
not count, see above), or when the user explicitly chooses to go ahead with
limitations, and then on the model gate's yes. The session never reads a
document or a
rule to answer any of this. `queue add` for a job already queued merges
`--allow-derived-rules`, `--doc`, `--now` and `--resume` into its row and says
what it updated.

The session never reads the documents, the rules, the description, the pack
file, the workbook, or the job's `detail.log` and `work` folder. It runs or
queues the job and reports the content-free status lines: phase names, pass or
fail, reason codes, counts and timings. The one exception is the build
supervisor's step, while a job waits on its questions; see "Answering the
model's questions".

Each model call leaves a file in the job's `work/calls` folder, named
`<seq>-<step>-<attempt>.json`: the step, the attempt, whether thinking was on, the seed the
call was sent with, a hash of the whole prompt, a hash of the reply schema, the prompt
itself, the reply as the model wrote it (an object whose fields depend on one another, such as a
reason and its verdict, has them numbered: `01_why`, `02_verdict`), the token counts and the
timings. A call that failed is recorded with its error code and no reply, and a retry is a second file.
A job run again with `--resume` adds to the folder and never replaces a file. The files
hold document and rule text, as `detail.log` does, so they stay on the machine and the
session does not read them. A slice or a step can answer its calls from these files
instead of the model; see "Replaying recorded calls".

```bash
<pipeline> check --config <pipeline-config> --issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] [--resume]
<pipeline> run --config <pipeline-config> --issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] [--resume]
<pipeline> run --config <pipeline-config> --suite <code> [--resume]
<pipeline> queue add --config <pipeline-config> --issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] [--resume]
<pipeline> queue start --config <pipeline-config> --job <job-id> [--cutoff HH:MM]
<pipeline> queue status --config <pipeline-config> [--job <job-id>]
<pipeline> queue watch --config <pipeline-config> --job <job-id>
<pipeline> queue summary --config <pipeline-config>
<pipeline> queue remove --config <pipeline-config> --job <job-id>
<pipeline> queue cancel --config <pipeline-config> --job <job-id>
<pipeline> queue fill --config <pipeline-config>
<pipeline> report --config <pipeline-config> [--period day|week|auto] [--seed <n>]
```

After each phase passes, the job saves its state in its `work` folder. A job run
again with `--resume` starts at the phase that stopped it, with the phases
before it kept as they passed, so a fix made after a failure costs only the
phases left. Without `--resume` a job starts over from intake.

Phase 9 runs as four steps, each saved when it passes: `phase9-checklist`
(issues, coverage rows, assumptions, the fix rounds), `phase9-senior` (the senior review
and the tester notes, a call for each), `phase9-confidence` (each field of the assessment, one call per field,
the assessment steps, and the overall level last), and
`phase9-revalidate` (the rebuild, the revalidation in a call for each group of checks that read the same sheets, its one repair round, and a new
rating when items stay open). The checklist calls, the
first read and each read after a fix round, run with thinking off and an output
budget of `model.maxOutput`. The five single-string confidence fields run the same way,
with thinking off. The assessment steps, the overall level, the senior review and
the revalidation calls think, each through one part of the review. A job resumed in Phase 9 keeps the
steps that passed.

Every call goes out with `model.temperature` (0 by default) and `model.seed` (42 by
default). A `pipeline.json` can set either: the temperature from 0 to 0.2, the seed as a
whole number from 0 to 4294967294. llama.cpp reads -1 and 4294967295 as "pick a random
seed", so neither is accepted. With one slot (`-np 1` in Lemonade's `llamacpp_args`), the
same server, model file and load options give the same reply byte for byte to the same
prompt, whether the server reads it fresh or from its prompt cache. Two runs on the same
inputs then stop at the same gate, and a sandbox comparison shows what a fix changed
rather than what sampling changed. llama.cpp does not promise the same numbers across
batch sizes, so more slots, another server version or other load options can change the
reply; before comparing runs on such a setup, run one slice twice, each on its
own yes at the model gate, and compare the two.

A reasoning call has an output budget of up to `model.reasoningOutput` tokens (40,960 by
default), its thinking and its answer together, which takes well over an hour at local generation speeds, inside a
`model.context` of 128,000 tokens by default, so a call waits up to
`model.timeoutMinutes` (150 by default). The pipeline reads the model server's
context size before every call and budgets the prompt against the smaller of it
and `model.context` (128000 by default; a `pipeline.json` can change it). When
the server's is smaller, the status log gets a `server-window` warning with both
sizes, and a prompt that does not fit the smaller one fails with `too-big`
rather than reaching a server that would drop the start of it. When the size
cannot be read, the log gets a `server-window-unknown` warning once per job;
`model.context` is used until a size has been read, and the last size read stays
in force after that. When the health check fails, the saved window is used as a guess that can
only lower the budget and never fails the job. The window sizes are per slot.
A window with no room left for a prompt fails the job
with `model:window-too-small`. The server's own request time-out must still be at
least `model.timeoutMinutes`, or the server ends the reply early and the call
fails with `no-reply`. Each call streams its reply, so when a call reaches
`model.timeoutMinutes` or its run is stopped, the closed connection also stops
the server generating the reply. Each request to the model server opens a connection of
its own, because Lemonade closes a streamed reply's connection a moment after the reply
ends, and a request sent on it is reset. A thinking reply cut off at its output budget is retried
once with thinking off and an output budget of `model.retryOutput` (8192 by
default); a second cut fails the job as `model:runaway`. A cut with thinking off
is not retried and fails as `model:length`, except in the break-only scenario call
of Phase 6, which ends its pass instead, and in a repair call of the revalidation
round, which leaves its finding open when another call of the round answered (see
Phase 9). Any other failure of a thinking call
(no reply, network, a reply that does not parse) is retried once with thinking
off at `model.maxOutput`.

Each thinking step also has an output budget of its own, so one step cannot run for an hour.
The built-in budgets are `phase1.rules` and `phase3.scope` 20,480, `phase5.objectives`,
`phase9.senior-review`, `phase9.senior-notes`, `phase9.confidence-steps` and
`phase9.revalidation-traceability` 12,288, `phase4.impact`,
`phase9.confidence-overall`, `phase9.revalidation-resolution` and
`phase9.revalidation-readiness` 8,192. The senior review and the revalidation walk make one
call per part or group, each under its own budget. A step with an index or a
repeat, such as `rules-3`, uses its name without it. `model.reasoningOutputByStep` changes
them, for example `{ "phase4.impact": 4096 }`; each value is a whole number from 1024 to
`model.reasoningOutput`, and its keys are the steps listed here. A call takes the first
budget that applies: the config's for its step, or else the smallest of the config's for its
phase, the built-in one for its step and `model.reasoningOutput`, which also caps all of them. A step cut
off at its budget is retried once with thinking off, as above.

The server's thinking budget, described below, ends a step's thinking before the step
reaches its output budget. On a host with that budget set, a step that is still cut wrote
an answer longer than the room its output budget leaves above the thinking budget: raise
the step's output budget with `model.reasoningOutputByStep`.

On a host without the thinking budget, the fallback is this rule: a thinking step cut at
its output budget on two or more recorded runs gets thinking off. A larger output budget
does not help there: the cut call's thinking and answer are lost, and the retry
with thinking off answers anyway, so the thinking attempt adds its run time and nothing to
the pack. Phase 1's understanding call runs with thinking off by this rule: its answer is
about 540 tokens, and with thinking on it spends its whole budget thinking and never reaches
the answer. A step with one recorded cut, such as `phase9.senior-notes`, keeps thinking and is
checked again on the next `repeated-cut` line or report.

`model.reasoningOutputByPhase` lowers the output budget for single phases, for
example `{ "phase9": 16384 }`. Its keys are `phase1`, `phase3`, `phase4`,
`phase5` and `phase9`, and each value is a whole number from 1024 to
`model.reasoningOutput`. In Phase 1 the budget covers the rule reading calls; the
understanding call does not think and uses `model.maxOutput`. In Phase 9 the budget covers
the assessment steps, overall level, senior review
and revalidation calls; the checklist calls do not think and use `model.maxOutput`.
`model.retryOutput` is a whole number from 1024 to
`model.maxOutput`; when `model.maxOutput` is smaller than 8192 it defaults to
`model.maxOutput`. To find the steps that ran out their budget, read the `retry` and
`call-fail` lines in `status.log`: a line whose `reason` is `length` or `runaway`
was cut off, and its `phase` and `step` say where. A server may leave out the
token usage on a cut reply, so do not rely on `outputTokens` matching `maxTokens`.
`queue status --job` counts those lines with their phase and step, and
`queue status` and the report show `model:runaway` and `model:length` for the jobs
that failed this way. Each queue run also records on its row the thinking steps it asked
and the ones cut at their budget, and `queue status --job` and the report name every step
cut on two or more runs of the job in a row, with its budget, as the rule above asks. For
a thinking call, space
for the prompt is budgeted against the larger of `model.reasoningOutput` and
`model.maxOutput`, never against a per-phase or per-step budget.

`status.log` also says more about each call. A `call`, `retry` or `call-fail` line has
`promptMs`, `genMs` and `cachedTokens` when the server returns them, and `reasoningTokens`
and `answerTokens` when it says how the output split. A cut call has both counts when the
split is known (a call with thinking off counts all of its output as answer),
and the last 2,000 characters of its thinking go to `detail.log` under
`<phase> <step> reasoning tail`; the status line never holds them. A `retry` or `call-fail`
line whose `reason` is `network` also has `cause`: the connection's error code, such as
`ECONNRESET` or `ECONNREFUSED`, `timeout` when the call reached `model.timeoutMinutes`, or
`unknown`. A failure replayed from a recording has no `cause`. While a call runs, a
`progress` line gives every `model.progressMinutes` minutes (a whole number from 1 to 1440, 5 by default)
the step, the `reasoningTokens` and `answerTokens` so far, and `elapsedMs`. The counts so far
are the reply's stream chunks, about one per token. On a `fail` line, `ms` and `calls` are
those of the phase that stopped (left out when a failed revalidation stops a job resumed after
that phase passed), and `jobMs` and `jobCalls` are the whole job's.

A server-wide thinking budget is the recommended setting for the model server.
`--reasoning-budget N` in the model's saved `llamacpp_args` holds every thinking
call on the server to N tokens of thinking. When a call reaches N, the server
adds the text given with `--reasoning-budget-message`, ends the thinking, and the
model writes its answer with its thinking kept. Nothing is lost and the prompt is
not read again. Without it, a call that thinks up to its output budget is cut
with no answer and is asked again with thinking off, which reads the whole
prompt a second time. It is a setting of the server, not of the pipeline config,
and the setup check under "Setting up a host" warns when it is missing.

- To set it: Lemonade runs the model with the llama.cpp build it bundles for
  the saved backend, not `/usr/bin/llama-server`, so check that binary's
  `--help` for `--reasoning-budget` and `--reasoning-budget-message` first. If
  both are there, append the two flags to the model's saved `llamacpp_args`,
  using the load command below:

        --reasoning-budget 6000 --reasoning-budget-message "Thinking time is up. Write the answer now from the analysis above."

  Inside the load command's JSON, write each quote around the message as `\"`.
- To confirm it: `curl -s <endpoint>/models/<model name>` shows the saved flags
  in `recipe_options.llamacpp_args`, and the model's entry in
  `all_models_loaded` in `<endpoint>/health` shows the ones the loaded model
  runs with. A thinking call's `reasoningTokens` in `status.log` then stops a
  few tokens past N.
- To size it: the output budget covers a call's thinking and its answer
  together, so the answer gets what the output budget leaves above N. The
  largest answer seen after a call used its whole thinking budget was about
  2,230 tokens, so the setup check wants at least 2,300 tokens of room and
  warns for each thinking step whose output budget is less than 2,300 tokens
  above N. A step's output budget here is the one its calls are sent with,
  after `model.reasoningOutputByStep`, `model.reasoningOutputByPhase` and
  `model.reasoningOutput` are applied. Four steps have the smallest built-in
  budget, 8,192, which leaves 2,192 tokens above an N of 6,000, so the check
  flags them at that setting. The fix for a flagged step is to raise its output
  budget with `model.reasoningOutputByStep`:

        "reasoningOutputByStep": { "phase4.impact": 10240, "phase9.confidence-overall": 10240, "phase9.revalidation-resolution": 10240, "phase9.revalidation-readiness": 10240 }

A quantized KV cache is another opt-in that nothing in the pipeline sets. Check
the bundled binary's `--help` for `--cache-type-k` and `--cache-type-v` first, and
check that `-fa` takes a value there (`on`, `off` or `auto`). If both flags are
there and `-fa` takes a value, append `--cache-type-k q8_0 --cache-type-v q8_0` to
the model's saved `llamacpp_args`, using the load command below. Otherwise skip
this opt-in. A quantized V cache needs flash attention, so
`-fa on` has to be in the args too. The flags roughly halve the attention layers'
cache. The weights and a hybrid model's recurrent state stay the same size, so the
drop in total memory is smaller. The flags add to a smaller `model.context` and do
not replace it. Read `mem_info_gtt_used` under `/sys/class/drm/card*/device/` with
the model loaded before and after the change. Build one pack with the flags and
one without, each on its own yes at the model gate, then run `compare` on the
two packs before keeping the flags, because
a quantized cache can change what the model writes.

A cap on the server's prompt cache is another opt-in setting that nothing in the
pipeline sets. `llama-server` keeps earlier prompts in host memory, up to 8192 MiB
by default, so a new prompt that shares a start with one of them skips re-reading
it. A hybrid model often has to re-read the whole prompt anyway, and then the cache
holds memory without saving time. Check the bundled binary's `--help` for
`--cache-ram` first. If it is there, append `--cache-ram 0` to the model's saved
`llamacpp_args` to turn the cache off, or `--cache-ram N` to cap it at N MiB. The
slot's own context checkpoints are a separate store and stay in use. After the
model loads, the flag shows in the `llamacpp_args` of its entry in `all_models_loaded`
in `<endpoint>/health`. Compare the prompt eval times in the server log before and
after; if they do not move, the cache was not helping.

Lemonade keeps the model's window as a saved recipe option on the user model,
not in `/etc/lemonade` or the systemd unit. In the commands below, `<endpoint>`
is `model.endpoint` (for example `http://localhost:13305/api/v1`) and `<model name>` is
`model.name` in the pipeline config.

- To check the saved window, run `curl -s <endpoint>/models/<model name>` and
  read `recipe_options.ctx_size`. It works whether or not the model is loaded.
  URL-encode the model name when it has characters such as `/` or spaces.
  To see what a loaded model is running with, read `recipe_options.ctx_size` in
  the matching `model_name` entry of `all_models_loaded` in `<endpoint>/health`;
  that list is empty when no model is loaded.
- To set it, load the model with the window saved:

        curl -sS --fail-with-body -X POST <endpoint>/load -H 'content-type: application/json' \
          -d '{"model_name":"<model name>","ctx_size":<model.context>,"llamacpp_backend":"<saved backend>","llamacpp_args":"<saved args>","save_options":true}'

  Take the backend and args from the model's saved `recipe_options`, carrying
  over every key it has, including any `--cache-ram`, `--reasoning-budget`,
  `--reasoning-budget-message`, `--cache-type-k`, `--cache-type-v` or `-fa` flag
  in the args, and leaving out
  one that is not saved, because saving may replace the stored options. A
  rejected load prints the server's error and exits non-zero. The load reloads
  the model, so do it when no build is running, on the model gate's yes.

A job takes an hour or more, so a request made during the day is queued.
`local/systemd/` holds a user timer that starts `queue run` at 22:00; the queue
runs one job at a time, puts a failed job back for a later run and moves on,
takes no new job past the cutoff (07:00 by default), takes none at all when the
timer only fires after the cutoff, and leaves a morning summary with one line
per job. "Running unattended" below covers how the queue fills, what a failure
does, and the daily report.
`queue run` given `--cutoff` runs whenever it is started. A stopped job's
status line names the phase and the gate; what the gate found is in the job's
own folder, for the user to read.

### Starting a job now, without reading it

When the user asks for a job to start now rather than at 22:00, the session
asks at the model gate, then
queues it and starts a unit for that one job, detached, and never sees what the
job reads or writes:

```bash
<pipeline> queue add --config <pipeline-config> --issue <n> [--change <m>] --now
systemctl --user start --no-block build-pack-now@<job-id>.service
```

`build-pack-now@.service` in `local/systemd/` is installed beside
`build-pack.service` and mirrors it: the same `EnvironmentFile`, and the same
`Nice=10`, so a daytime job does not take the machine at full priority. The unit
runs `/usr/bin/node`. The script and config paths come from
`~/.config/build-pack/env`, and so does everything else the job needs from its
environment: the unit gets the user manager's `PATH`, not the session's, so the
env file has to carry a full `PATH=` line (systemd does not expand `$PATH`
there) for a `<rule-export>` command that lives outside the system folders, and
any token that command reads, one `NAME=value` per line. Its instance name is
the job ID, and it runs `queue start --job <job-id>`, which runs that job's row
first and then any other row added with `--now`, until the configured
`queue.cutoff`. A row queued without `--now` is waiting for the nightly run and
stays queued; `queue add --now` for a job already waiting for tonight marks that
row to start now. `--no-block` returns at once; without it `systemctl` waits for
the whole run. The unit's output goes to the user's journal and the
job's own folder, never to the session.

The nightly timer is left as it is. The queue is held by one process at a time:
while it is held, a 22:00 `queue run` waits, polling every 30 seconds, and
works the night's queue as soon as the holder finishes; it gives up only when
the cutoff passes. A oneshot unit stays activating for its whole run, so a
second start of the same instance merges into it at any point while it runs. A
job already running under the nightly service is not refused by systemd, but
`queue start` finds the queue held and the row `running`, says `<job-id> is
already running`, and takes nothing. `queue add` prints `queued`, `marked to
start now` for a row it set to start now, `<job-id> is already queued; updated
<fields>` when it merged options into a waiting row, `already running`, or
`already queued`. A row
marked `running` whose process is gone counts as a failed try, `interrupted`,
for the next run that takes the queue. A run that works every queued row takes
the job again at once; a `queue start` run works only rows marked `--now`, so it
leaves the job for the night. The lock and the duplicate-ID check in
`queue add` are what stop a job from starting twice. The lock records the
holder's PID and start time, so a lock file left by a crash, or one whose PID
another process has since taken, is not a holder.

If another `queue run` or `queue start` already holds the queue, `queue start`
waits a couple of seconds, tries once more, and then takes nothing, says so, and
exits. The job stays `queued`. A `queue run` that holds the queue works every
queued row, oldest first, and takes this one when it is due and has not failed in
that run. A `queue start` works only rows marked `--now`, so it takes this one
only if it was queued with `--now`. Either way the row stays `queued`: that is
not a failed start. If the holder was a nightly run, wait for it; if it was a
start-now run and the row is not marked, start it again when the run ends, on
the same yes since the job never ran, or let
tonight's run take it.

The session reads the outcome with one command, which prints only the row's
status, whether a live process holds the queue, and the last status line the
job wrote (phase, event, reason code, counts, timings). Under those it prints
the phase now running and how long it has run, or the phase and reason code a
stopped job ended with (and, for a gate stop, the count and numbers of the documents
it names), the time each finished phase took, the count of `retry`
and `call-fail` lines by reason, and a `cut` line for every `length` or
`runaway` hit with its phase and step. Then a `last-check` line and a `last-repair` line
show the last `check` and `repair` line the job wrote. Last comes a `repeated-cut` line, such as
`repeated-cut step=phase9.senior-notes budget=12288 runs=2`, for each thinking step cut at its
output budget on two or more of the job's queue runs in a row. Without `--job` it lists every row in
the queue with its status, phase, reason code and last update, so a job that
stopped or can resume shows even when its ID is not remembered:

```bash
<pipeline> queue status --config <pipeline-config> [--job <job-id>]
```

A unit needs a moment to take the queue and mark the row `running`, so the
session repeats the command every few seconds for up to a minute before it
decides anything. `running` with the queue `held` is a start. `queued` with the
queue `held` is the case above. `queued` with the queue `free` after the minute
means the unit did not start; `systemctl --user is-active
build-pack-now@<job-id>.service` and the exit code in `systemctl --user show -p
Result build-pack-now@<job-id>.service` say why, and the session reports that
without opening the journal. `running` with the queue `free` is a row left by a
dead process: report it, and the next run marks it `interrupted`. `failed`
with the queue `free` is a job that stopped in its first phase and has already
released the queue; the status line names the phase and the reason code, and
the session reports them. `stopped` with the queue `free` is a job
that `queue cancel` ended; the status line names the phase it stopped in, and
`queue add --resume` carries on from there. `failed` or `passed` is final, whether the queue
shows `held` or `free`; the queue may be held by another job's run. `not queued`
means no row has that job ID, so the `--job` value or the `queue add` is wrong.
A lock file is not evidence of a live process; `queue status` checks the
process. The status line shown is the current attempt's; a resumed job shows
nothing until it writes its first line.

Later checks use the same command, and only it. They never read the journal,
`status.log` or anything else in the job's folder directly. Resume a stopped job
the same way, with `--resume` on the `queue add` and a new yes at the model
gate. A session that stays with the
job to answer its questions runs `queue watch` instead, which prints the same
lines and keeps the job's heartbeat fresh; the next section is the one exception
to these rules.

### Answering the model's questions

Three gates stop a job on questions a person has to settle: Phase 1's
`source-conflict`, Phase 2's `rule-conflict` and Phase 3's `needs-user-review`. When
a session is watching the job, the job asks it, the build supervisor, instead of
stopping, and waits with the model still loaded.

A session that watches a running job is the build supervisor. It checks the job
with `queue watch`, every few minutes and at least once every
`supervisor.staleMinutes`:

```bash
<pipeline> queue watch --config <pipeline-config> --job <job-id>
```

Each check writes a heartbeat beside the queue file, `<queue file>.watch-<job-id>`,
holding the time. A job waits at a question gate only when that heartbeat is newer
than `supervisor.staleMinutes`; a sandbox job, `<source>~<label>`, also takes its
source job's heartbeat. With no fresh heartbeat, as on a nightly run with no session
attached, the gate stops the job at once with its usual reason, and the model is not
left loaded through a wait nobody will answer.

At the gate the job writes `work/questions-<phase>.json`, with the job ID, the phase,
the time the wait ends, and the questions, each with an ID (`Q1`, `Q2`, and so on). It
then waits up to `supervisor.waitMinutes` for `work/answers-<phase>.json`, checking
for it and for the heartbeat every 15 seconds. `queue watch` shows the wait as
`waiting phase=<phase> questions=<n> left=<minutes>` while the job's run holds the
queue. A sandbox's wait shows until the time it ends, since a slice replayed with no
live model holds no queue and the sandbox's log does not say whether its slice held one. When
`supervisor.notifyUrl` is set, the job posts that line, with its job ID in front, to
the URL once, such as an ntfy topic, so the user sees it too. The line names no
document, rule or question. A failed post is a `warn notify-failed` status line
and never stops the job.

When the supervisor sees `waiting`, it answers:

1. It reads `work/questions-<phase>.json` and the sources below, and nothing else in
   the job's folder. It writes only `work/answers-<phase>.json`. It never edits the
   pipeline's code, config, prompts, checkpoints, or any other file in the job's
   folder, and it never fixes the build while the job runs.
2. It answers from four sources only:
   - the documentation: the converted documents and the process descriptions;
   - the build's inputs: the change record and the `--doc` documents;
   - the approved business rules, through `<rule-export>`;
   - the issue's own record in the tracker, its fields and comments, from
     `<description-source>`.
   No outside knowledge, and nothing about how the application behaves that a
   source does not state.
3. It answers every question as well as those sources allow. Each answer cites
   what it rests on: a document path and section, a rule ID, a tracker field or
   comment with its date, or an input name. Each carries a confidence: `settled`
   when a source states it, `best reading` when the sources point to it without
   stating it. When no source bears on a question, the answer says so, with
   `best reading` and no citations, and the pack carries it as an assumption
   instead of stopping.
4. It writes the file whole: to a temporary name in the same folder, then renamed
   into place, so the job never reads half of it.

The answers file holds one object:

```json
{ "answers": [
  { "id": "Q1", "answer": "<a full sentence>", "confidence": "settled",
    "citations": ["<document path>, <section>", "<rule ID>"] }
] }
```

Every row has exactly these four fields. An ID the questions file does not hold, an
ID given twice, a blank answer, another confidence, or a `settled` answer with no
citation fails the schema: the job writes an `answers-rejected` status line with
the reason code, keeps waiting, and reads the file again when it changes. A question
the file leaves out is one the supervisor declined.

Once a file passes, the job writes an `answers` status line with counts only:
`answered`, `declined`, `settled` and `bestReading`. With every question answered
the phase carries on from where it stopped, and nothing before it runs again; its
`pass` line counts the answers as `supervised`. Each answer becomes an assumption
in the pack, its why reading "Answered by the build supervisor (`<confidence>`)
from `<citations>`" and its clarification naming the question for the change owner
to confirm, and a line under Job Intake's assumptions to proceed. Phase 1 gives the
understanding call the answers to the conflicts its rule batches found. The later
phases read the rules as written, and the rules keep the impact Phase 3 classified
them with, so each assumption's impact says what the answer did not change. A
question declined, the wait running out (`wait-over reason=timeout`), or the
heartbeat going stale during the wait (`wait-over reason=supervisor-gone`) stops
the job with the gate's usual reason, so a person can still take it over.

What the supervisor tells the user stays content-free like every other report:
the phase, how many questions it answered and declined, and the confidence of
each, never the questions, the answers or what the sources say.

The `supervisor` block in the pipeline config sets the wait:

```json
"supervisor": { "waitMinutes": 30, "staleMinutes": 15, "notifyUrl": null }
```

`waitMinutes` (default 30) is how long a gate waits; 0 turns the wait off, and every
gate stops at once. `staleMinutes` (default 15) is how old a
heartbeat may be. `notifyUrl` (default none) is an http or https URL that receives
the waiting line. A job waiting holds the queue, the paused units and the model
for up to `waitMinutes`, so a wait can run past the cutoff.

### Freeing the machine for a job

A job needs the machine's memory and GPU for the model server. The optional
`pause` block in the pipeline config names systemd units to stop while a job
runs and start again afterward:

```json
"pause": {
  "units": ["<unit-pattern>"],
  "scope": "system",
  "busyProcess": "<worker process name>",
  "pollSeconds": 5,
  "maxWaitMinutes": 60
}
```

`units` takes unit names or patterns, as `systemctl list-units` does. Only
units that are active when a job is about to start are stopped, and only those, plus
any a dead run left stopped, are started again. `scope` is `system` (the default) or `user`. With no `units`,
nothing is stopped and no command runs.

The stop comes when the first job is about to start, so a run with an empty
queue leaves the units alone. If `busyProcess` is set, a unit with a process of
that name inside its cgroup is busy: the run polls every `pollSeconds` and
stops it once the worker has finished, and never stops it while it works. The
first job waits for a busy unit at most `maxWaitMinutes` (60 by default; 0 means
no wait), and never past the cutoff. A unit still busy then is left running,
logged as `pause: left running <unit>`, and not started later. The job starts
anyway unless the cutoff has passed, in which case no job starts and the stopped
units start again. Before each later job the run looks again and stops any unit
whose worker has finished. The
units stopped are listed in a `.paused` file beside the queue file as each one
stops. The units start again when the run ends, however it ends, and also when
the process gets SIGTERM, SIGINT or SIGHUP. If a run dies before it can do
that, the next run that takes the queue finds the file and starts those units
at its end, even when it has no job to run. A stop or start that fails is
logged as `pause: stop failed <unit>` or `pause: start failed <unit>` and the
run carries on; a unit that would not stop is not started later. A `run`
outside the queue stops and starts the units the same way, but holds no queue
lock, so it leaves a dead run's `.paused` file for the next queue run.

A unit that was taken down by hand before the job, and was therefore not
running when the run began, is not started when the run ends unless the job
marks it. `queue add` and `queue start` take `--restore <unit>`, which can be
repeated, and `--restore-paused`:

```bash
<pipeline> queue add --config <pipeline-config> --issue <n> --restore <unit> --restore <unit>
<pipeline> queue start --config <pipeline-config> --job <job-id> --restore-paused
```

Each `--restore` unit must match a `pause.units` entry, or the command stops
with `--restore <unit> is not on pause.units`. Patterns match the way `systemctl list-units` reads them, with `*`, `?` and
`[...]`. `--restore-paused` marks every
`pause.units` match that systemd lists and that is not active when the
command runs, and the command prints the units it marked. A unit systemd has
not loaded does not show up there; name it with `--restore`.

With scope `system`, the run starts a marked unit through `sudo -n`, so the
command reads `sudo -n -l` once and does not mark a unit that sudoers will not
let it start. It prints `restore  <unit>  refused  sudoers-refused start; not
marked` for each, marks the others, and still exits 0. Start a refused unit by
hand when the run ends, or add its sudoers rule first.

The marks ride on the job's row until the run takes the job, then move into the
`.paused` file, which holds `{"stopped": [...], "restore": [...], "failedStart": [...]}`.
`failedStart` names the units of the other two lists whose last start failed,
and the file leaves it out when it is empty. A file that
is a bare list of unit names counts as the stopped units. The marked units start
when the run ends through a normal finish, a failure, the cutoff, a signal or
`queue cancel`, and on a running job `--restore` writes to the file directly. A
run that reaches the cutoff before it takes the job leaves the marks on the row
for the next run. `queue status` lists the units waiting as
`restore pending <units>`, and a unit whose start failed apart from those, as
`restore start-failed <units>`, with the next step: start it by hand with
`sudo systemctl start` (`systemctl --user start` for scope `user`), then remove
its name from the `.paused` file. To try the start again and clear the record:

```bash
<pipeline> queue restore --config <pipeline-config>
```

It exits 0 when every unit started, and 1 when one did not start or the queue is
running, since the running run restores its own units. A unit that does not start
stays recorded for the next run or `queue restore`, which fails again until the
cause is fixed, such as a missing sudoers rule for scope `system`. To drop the record of a unit
that can never start, such as a masked or misnamed one, or one started by hand,
remove its name from the `.paused` file beside the queue file.

### Stopping a job

When the machine is needed before a job ends, stop it with the queue's own
command instead of stopping the unit:

```bash
<pipeline> queue cancel --config <pipeline-config> --job <job-id>
```

The command signals the process that holds the queue, whether the nightly unit
or a `build-pack-now@` unit started it, and waits for it to end, for up to
150 seconds. The run ends the model call in flight, which stops the model
server generating its reply, keeps the job's checkpoint,
marks the row `stopped` with the phase it stopped in, starts the paused units
again, unloads the model the way a finished run does, and frees the queue. A
stop is not a failed try, so it never counts toward dropping the job. The
rows still waiting stay queued for the next run, and a nightly run does not
take the stopped row. When the command ends it prints `cancelled <job-id>`
and the same lines `queue status --job` prints, which show the row `stopped`,
its phase, and the queue `free`.

Resume the job when the machine is free again and the model gate has a new
yes; it starts at the phase it
stopped in, with the phases before it kept:

```bash
<pipeline> queue add --config <pipeline-config> --issue <n> --resume --now
```

Exit codes: 0 the job stopped, 1 the job is not running (the line says what
status the row has), 4 the queue was still held after the wait. A row left
`running` by a run that was killed has no process to signal; `queue cancel` marks it
`stopped`, starts the units that run paused, and unloads the model. The units
ask for the same clean end when they are stopped with `systemctl`: both unit
files send the stop signal to the node process alone and allow it three
minutes. A stop that way marks the row `stopped` too. Send the signal a second
time, or let the three minutes pass, and the process starts the units, unloads
the model and exits at once, leaving the row `running` for the next run to
settle. The process cannot act on the signal while it waits on a builder
command, so a builder that runs past the three minutes ends the same way.

### Rerunning part of a job

After each phase passes, the job keeps the state it passed with in
`work/checkpoints/<phase>.json`, beside `work/checkpoint.json`, which holds the
latest. A job whose folder has no `checkpoints` folder cannot be sliced past
intake. To try a change to one phase against a real job's state, run a slice of
that job in a sandbox, behind the model gate unless a recording answers every
call:

```bash
<pipeline> run --config <pipeline-config> --job <job-id> --from <phase> [--until <phase>] [--as <label>] [--pause] [--model replay:<source> [--replay-miss fail|live]]
```

- The sandbox is a copy of the job's folder named `<job-id>~<label>`; the label
  defaults to the time, `YYYYMMDDTHHMMSS`. The job's folder, its queue row and
  its workbook are only read. The copy holds the job's logs and `work` folder,
  without the pack file, the workbook, the call records or the snapshots from
  `--from` on. The sandbox's `work/calls` holds the calls its own run made.
- The slice loads the snapshot of the phase before `--from`, runs `--from`
  through `--until` (`--from` alone by default) with the current code and
  config, and stops. It writes no pack and no workbook, and it does not unload
  the model, so a slice run again meets a loaded model. `--from intake` needs no
  snapshot and starts over in the sandbox. The job's documents come from the
  snapshot, and its other options from its queue row. A job started by hand has
  no row, so only its issue, change or suite, taken from its ID, reach a slice
  from intake or Phase 2; `--doc`, `--description-file` and `--allow-derived-rules`
  do not.
- It holds the queue while it runs, so the nightly run waits for it and a run
  already holding the queue makes the command exit 1. It stops no unit unless
  `--pause` is given. A run answered from a recording holds neither, as
  "Replaying recorded calls" says.
- The sandbox's snapshots are its own, so a slice of the sandbox, `--job
  <job-id>~<label>`, carries on from where the first slice ended.
- When the slice passes, the command prints `sandbox <id>` and how the sandbox's
  pack at `--until` differs from the job's snapshot of the same phase, as
  counts: cards in each and how many were added or removed, the coverage
  statuses that changed, the confidence level, and the open revalidation
  items. The card IDs and the open items go to the sandbox's `detail.log`.
- `queue status --job <job-id>~<label>` reads the sandbox's log like a job's.

Exit codes: 0 the slice passed, 1 it stopped or the queue is running, 2 bad
arguments, a job with no folder, no snapshot for the phase before `--from` (the
message names the snapshot), a replay source with no recorded calls, or a setup
error such as an unreadable config.

### Trying one step

A slice runs whole phases. To try one part of Phase 9, or the builder alone, run
a step on a snapshot of the job:

```bash
<pipeline> step --config <pipeline-config> --job <job-id> --at <phase|sandbox> <step> [--as <label>] [--pause] [--model replay:<source> [--replay-miss fail|live]]
```

`--at` is a phase, read from the job's snapshot of it, or a sandbox of the job
that an earlier step ran in. The sandbox is made as for a slice, and its state
goes in `work/step.json`, which the next step starts from. The job's own folder,
queue row and workbook are only read.

| Step | What it runs | Model |
| --- | --- | --- |
| `draft` | The Draft workbook: the builder command on the pack, writing it to `work/review` | no |
| `build` | The Phase 8 build on the pack in memory, with no repair and no Draft workbook (`draft` writes that), with the review sheets left out of the failures until the confidence assessment | no |
| `checklist` | The checklist reads and the fix rounds | yes |
| `walk [--check <names>]` | One revalidation walk, a call for each group of checks that read the same sheets, or the named checks only, comma-separated, each an exact name or the start of one | yes |
| `repair --finding <n>` | One repair round for finding `<n>` of the last walk, counted from 0 as the walk prints them: one repair call, or one for each part of a finding that names more cards than one reply holds | yes |
| `confidence [--field <name>]` | One confidence field (`coverage`, `remainingRisks`, `assumptions`, `regressionScope`, `breakItScope`, `manualReview`), or the overall level when no field is named | yes |

- Every step except `draft` and `build` sits behind the model gate, unless a
  recording answers every call.
- A step that asks the model holds the queue and stops no unit unless `--pause`
  is given, as a slice does. `draft` and `build` take neither, and neither does a
  step answered from a recording.
- `draft` and `build` print the builder's sheet results, one `PASS` or `FAIL`
  line for each sheet. `build` also prints `DEFERRED` for a review sheet that
  fails before the confidence assessment has run.
- Every step then prints the status lines it wrote. The step's own line holds its
  duration, model calls and tokens, and counts such as the sheets that failed.
- `checklist` adds to the pack's assumptions, so start it from a snapshot before
  Phase 9 has run. `repair` needs the verdicts of a walk: a sandbox a `walk`
  step ran in has them, and so does a snapshot of the revalidation or after it.
  A snapshot whose state holds none reads them from the job's
  `work/phase9-revalidation.json`. A `walk` of some checks before all seven have
  a verdict leaves the pack's revalidation result as it was.
- A step that stops leaves `work/step.json` as it was, writes the pack as far
  as it got to `work/partial-pack.json`, and logs a `fail` line.
- Give `--as` when scripting steps: the default label is a time stamp with one
  second of resolution.

Exit codes: 0 the step ran and its build passed, 1 it stopped, its build failed
a sheet, or the queue is running, 2 bad arguments, a job with no folder, no
snapshot or step state at `--at`, or a replay source with no recorded calls.

### Replaying recorded calls

A slice or a step can answer every model call from the calls a job recorded in
`work/calls`, so a change to the code around the model is tried against a real
job with no model server:

```bash
<pipeline> run --config <pipeline-config> --job <job-id> --from <phase> --model replay:<source> [--replay-miss fail|live]
<pipeline> step --config <pipeline-config> --job <job-id> --at <phase|sandbox> <step> --model replay:<source> [--replay-miss fail|live]
```

- `<source>` is the ID of a job or sandbox in the output folder, or the path of a
  folder of call records: a job folder, its `work/calls`, or a folder of the
  files themselves, such as a recording kept as a regression fixture. The
  flags belong to `run --job` and `step`; no other command takes them.
- Each call is answered from the recorded call for the same step and attempt, in
  the order the calls were made. The reply, the token counts and the timings are
  the recorded ones, so while the code around the model is unchanged the replay
  builds the same pack as the run it came from. A recorded failure is raised
  again as the same error, so the retry that followed it replays too. The replay
  records its own calls in the sandbox, so a sandbox can be replayed in turn.
  The seed is not compared: a replayed call notes the recorded call's seed, or none
  when the record holds no seed, and a call sent to the live model notes the
  config's.
  When the next recorded call holds another prompt but a later one for the
  same step and attempt holds this one, the calls ahead of it are skipped, so a
  slice or a step replayed from a whole job passes over the calls of the phases
  it does not run.
- A call is a miss when its prompt hash is not the recorded one
  (`prompt-changed`), when its reply schema is not (`schema-changed`), when it
  asks with thinking on and the recorded call had it off, or the reverse
  (`thinking-changed`), or when
  the recording has no call left for it (`no-record`). A miss writes a
  content-free `replay-miss` line to `status.log` with the step, the reason and
  how many prompt lines differ, and the differing lines to `detail.log`: the
  system and the user text apart, at most 20 lines on each side of the change.
  When the run ends the command prints `replay  served <n>  live <n>  missed
  <n>` and a line for each miss, such as `replay: prompt changed for <step>`.
- By default a miss stops the run. The job fails with the reason
  `replay:prompt-changed`, `replay:schema-changed`, `replay:thinking-changed` or `replay:no-record`, and no
  phase retries it. With `--replay-miss live`, which sits behind the model
  gate, the call goes to the model server
  the config names, and every other call still comes from the recording, so the
  steps whose prompts did not change cost nothing. A miss always uses up its
  recorded call, and the recorded retry of a call that failed, so one changed
  prompt does not shift the answers of the calls after it. A miss under
  `--replay-miss live` does not change the exit code.
- A run that cannot ask the live model, the default, holds no queue and stops no
  unit, so it runs while the queue does, and `--pause` is refused. With
  `--replay-miss live` it holds the queue as a slice does.
- Replay an uninterrupted run or a sandbox. A job resumed after a stop holds the
  interrupted run's calls first, error records included, and a replay repeats the
  interruption.
- Prompts are split to fit the model window, which a replay cannot read from a
  server: it uses `model.context`. A recording made on a server whose window was
  smaller than `model.context` misses where the batches split differently. Set
  `model.context` in the replay's config to the window the `server-window` line
  in the source's `status.log` names.

### Closing desktop apps before a run

`pause` takes one scope, and desktop apps run as transient `app-*.scope` user
units that `systemctl start` cannot bring back, so they have a separate block.
`pause.units` stays for system units. The optional `closeApps` block names the
apps to close when the first job is about to start:

```json
"closeApps": {
  "scopes": ["app-com.google.Chrome-*.scope", "snap.spotify.spotify-*.scope"],
  "onNow": false,
  "keepIfRunning": ["<process name>"]
}
```

`scopes` takes patterns, as `systemctl --user list-units` does. Each must start
with `app-` or `snap.`, end in `.scope`, and have a literal part before its first
wildcard, so a pattern never matches a service or a system unit. Scope names
carry a process ID that changes on every launch, so use a wildcard for it. With no
`scopes`, nothing is closed (the default). Each active scope is stopped with
`systemctl --user stop`, which sends the apps SIGTERM and ends them if they stay
past the scope's stop timeout. Nothing starts them again. An app with unsaved
work loses it, so close the ones you care about by hand first.

The close comes when the first job is about to start, before the pause, so a
run with an empty queue closes nothing. It runs for a `queue run`, including one
with `--cutoff`, and not for `run`. A job started with `queue start --job`, such
as `build-pack-now@.service`, leaves the apps open unless `onNow` is `true`, so a
daytime job does not close what you are working in.

A scope is also left open when it holds the build itself, or holds a process
named in `keepIfRunning`, a list of process names of up to 15 characters (the
kernel's limit). Its default holds the process name of a long-running session.
Sessions started from a desktop app run inside its scope, so closing that scope
would end them. The app's helper scope, such as `app-gnome-<app>-<pid>.scope`
beside `app-<app>-<pid>.scope`, stays open with it. Each scope left open is
logged as `close: left open <scope>`, followed by `close: <name> processes open
<n>` for each kept name, which counts the processes with that name, terminal
sessions included. A session whose process has another name is not counted or
kept. Those sessions are never closed for you: end them by hand before
leaving for the night, or set `keepIfRunning` to `[]` to close the app and its
sessions anyway. A stop that fails is logged as `close: stop failed <scope>` and
the run carries on.

### Checking free memory between phases

Before each phase starts, a job reads `MemAvailable` and swap use from
`/proc/meminfo`. When free memory is under the floor, or swap use is over the
ceiling while free memory is under twice the floor, the job waits and polls. If memory is still low when the wait ends, it
stops at the last checkpoint, so `queue add --resume` carries on later, with no
finished phase lost. The optional `memory` block sets the limits; these are the
defaults:

```json
"memory": {
  "enabled": true,
  "minAvailableMiB": 3072,
  "maxSwapPercent": 85,
  "pollSeconds": 30,
  "waitMinutes": 20
}
```

The defaults come from one measured night: available memory fell to 4.6 GiB and
swap held at about 68% the whole night, cold, with steady speeds. Both limits
sit just past that healthy run, so it would not have tripped them. Swapped pages
stay in swap after the pressure ends, so swap use over the ceiling counts only
while free memory is also under twice the floor. Measure again after changing
the swap setup (`local/memory/README.md`). `maxSwapPercent: 100` turns the swap
test off, `waitMinutes: 0` stops at once, and `enabled: false` turns the check
off. The numbers cover the host's own memory, not the graphics memory pool.

If memory does run out, `local/oom/README.md` sets up the kernel and `systemd-oomd` to prefer
ending a desktop app over the model.

The status log carries a `wait` line with the reason `memory-low`, then either
`memory-ok` (with `polls` and `waitedMs`) or the job's `fail` line with the reason
`memory:low`. All carry numbers only. If `/proc/meminfo` cannot be read, one
`warn` line with `meminfo-unreadable` is written and the job carries on. A
`memory:low` stop does not count as one of a job's tries, so it waits for the
next night. After 3 such stops in a row (a failure of any other kind resets the
count) the job is dropped from the queue like one that failed twice, and the
report shows it as `MEMORY`, needing a person; `queue add` puts it back. The
queue run takes no further job after a memory stop, since the next would meet
the same memory. A job stopped this way before its
first phase passes has no checkpoint, so a resumed run starts over from intake.
It keeps the earlier `status.log` and adds to it, so the `wait` and `fail` lines
stay as evidence the host ran short. The rest of the job folder is cleared, and
a start over after any other stop begins with an empty log.

With scope `system`, the commands run as `sudo -n /usr/bin/systemctl`, so the
user running the queue needs a sudoers rule that needs no password. List each
unit and each verb on its own, for example:

```
<user> ALL=(root) NOPASSWD: /usr/bin/systemctl stop <unit>.service, /usr/bin/systemctl start <unit>.service
```

sudo matches the arguments exactly, so name each unit in full as
`systemctl list-units` prints it, `.service` included. Write the rule with
`sudo visudo -f /etc/sudoers.d/<file>` so a syntax error cannot lock out sudo,
and check it with `check --config <pipeline.json>` (see "Setting up a host"),
which reads `sudo -n -l` and passes a unit only when both commands sit under
`NOPASSWD:`. `sudo -n -l /usr/bin/systemctl stop <unit>.service` alone also
succeeds for a command that still asks for a password, so it proves nothing.

`queue add` and `queue start` read the same listing before they mark a unit for
`--restore`, and the input gate in "Before a job is run or queued" prints a
pause unit that fails it.

A `*` in a sudoers argument also matches spaces, so a pattern there can allow
more than the unit it was meant for. Listing the units is safer. With scope
`user`, no sudo is involved.

### Releasing the model

When a queue run ends, the local model is unloaded so its memory is free
without stopping the model server by hand. The optional `release` block names
the command and how long to wait for it:

```json
"release": {
  "command": ["lemonade", "unload"],
  "timeoutSeconds": 60
}
```

The values above are the defaults, and `lemonade unload` needs no sudo. An
empty `command` turns the step off.

The unload runs once, when the run ends, after the paused units start again.
A normal finish, a failed job, the cutoff and a SIGTERM, SIGINT or SIGHUP all
end the same way, and the model is not reloaded between the jobs of one run. A
run that started no job, such as one that found the queue held or empty,
unloads nothing, and neither does a `run` outside the queue. A run stopped
during a model call has already closed that call, so the server is not busy
generating its reply and the unload does not wait for it.

The outcome is logged as `release: ok` or `release: failed` and as one
`phase=release` line in the status log of the last job that ran, with the
event `pass` or `fail`, a reason code (`exit-<n>`, `signal`, `spawn-error` or `timeout`)
and the time it took. The command's own output is never read. A failed unload
does not change any job's result. `queue status` shows the line for the job
that ran last, after that job's own last line while its row still runs and
alone once the row has finished.

### Setting up a host

Install these in order, then run the setup check as the last step:

1. The repository, the model server and the pipeline config.
2. The env file at `~/.config/build-pack/env`, with `BUILD_PACK_SCRIPT` and
   `BUILD_PACK_CONFIG` and a full `PATH=` line.
3. Every file in `local/systemd/`, copied to `~/.config/systemd/user/`, which
   includes `build-pack-now@.service`, then `systemctl --user daemon-reload` and
   `systemctl --user enable --now build-pack.timer build-pack-check.timer build-pack-report.timer`,
   with `build-pack.timer` behind the model gate.
4. For a `system` pause scope, the sudoers rule from "Freeing the machine for a
   job".
5. The server's thinking budget: `--reasoning-budget` and
   `--reasoning-budget-message` in the model's saved `llamacpp_args`, set,
   confirmed and sized as the model settings above describe.
6. The setup check:

```
node build-pack.mjs check --config <pipeline.json>
```

Each line reads `<area>  <name>  pass|fail|warn  <code>` and names units, variables,
config fields and thinking steps only. No value from the env file is printed. A
`warn` line is advice: it does not fail the check. The check covers:

- each unit in `local/systemd/`: installed, loaded, and for a timer, enabled. A
  missing unit fails with the file to copy and where
- the env file: present, `BUILD_PACK_SCRIPT` and `BUILD_PACK_CONFIG` set and
  naming files that exist, and a `PATH` line
- each `pause.units` entry: found in the scope, and for scope `system`, a
  sudoers rule that lets the queue user stop and start it without a password
- the model server: answers at `model.endpoint` and lists `model.name`
- the thinking budget, once the model is listed, on a line whose area is
  `thinking-budget` and whose name is `model.name`: `pass  set <N>` when the
  model's saved `llamacpp_args` hold `--reasoning-budget N` with N above zero,
  `warn  not-set` when they do not, and `warn  not-read` when the server does
  not give the saved options. With the budget set, each thinking step whose
  output budget is less than 2,300 tokens above N gets a line of its own, named
  for the step, and is fixed by raising that step's budget with
  `model.reasoningOutputByStep`:

        thinking-budget  phase4.impact  warn  answer-room 2192; output budget 8192, needs 8300

- the `release` command: found on the env file's `PATH`. It is looked up and
  never run, since running it would unload a model another job may be using

The exit code is 0 when every check passes and 1 when any fails, 2 for a config
that does not load; a `warn` line does not change it. `check` with `--issue` is
the input gate described under
"Before a job is run or queued", which adds the pause units that fail this
check, and with neither `--issue` nor `--suite` it is this check.
`build-pack-check.service` runs it after the queue check each day,
so a host that drifts shows as a failed unit; on a day the queue check itself
exits 1, the setup check is skipped.

### Running unattended

A week of nightly runs needs no one at the keyboard. The queue fills itself,
a failed job tries once more, and a report tells the maintainer what to look at.
The session does not read the report's sources any more than it reads a job's
folder; it passes on the report's lines.
A session that runs one of this section's commands for the maintainer asks at
the model gate first, like any other.

**The queue fills itself.** The config's `queue.sources` lists where new jobs
are named. Each night, after `queue run` takes the queue and before it takes a
job, every source is read and each job it names that the queue has not seen is
queued. A source is one of:

```json
"queue": {
  "sources": [
    { "type": "folder", "path": "<folder>" },
    { "type": "records", "glob": "<records-glob>", "pattern": "<file-name-regex>" },
    { "type": "command", "command": ["<program>", "<argument>"] }
  ]
}
```

- `folder`: every file in the folder is a list of jobs, one per line. The
  maintainer drops a list there.
- `records`: one job per record file, such as the SIR records in the
  repository's documents folder. The first group of `pattern` (case-insensitive,
  matched against the file name) is the issue number and an optional second
  group is the change number. A file name the pattern does not read is counted
  as an unreadable line and skipped. Without a `pattern`, a name that starts
  with `SIR` or `ISSUE`, an optional `-`, `_` or space, and the issue number is
  read; a change is read only when `change` or `CR` follows, then a number that
  starts with a digit, as in `SIR-9415-change-7001.md` or `ISSUE_9415_CR7001.md`.
  `SIR-9415-credit-limit.md` is issue 9415 with no change. A name where `change`
  or `CR` stands alone after the issue number but no valid change number follows,
  such as `SIR-9415-CR-CHG7001.md` or `SIR-9415-CR-7001,7002.md`, is counted as an
  unreadable line and not queued, so the issue is never queued without the change
  it names. So is a title that begins with one of those words, such as
  `SIR-9415-change-password.md` or `SIR-9415-CR-screen.md`; the pattern cannot
  tell it from a bad change number. Rename the file or add the job by hand.
- `command`: a program that prints job lines, such as one that lists the build's
  SIR/CR from the requirements tool. It runs in the repository root, and a
  non-zero exit reads as an unreadable source.

A job line is `<issue>`, `<issue> <change>`, `suite <code>`, or the full
`queue add` form, such as `--issue 9415 --doc <path>`. Blank lines and lines
that start with `#` are skipped, and a line that is not a job is counted and
skipped. Jobs queued this way are not checked when they are queued, so the
pre-check below is what catches a bad one before the night. A job whose
documents have no usable rules otherwise stops with a gate reason code (for
example `gate:rules-not-extracted`) and waits for a person, as "A failed job
tries once more" below sets out; the report shows it. A job already in the queue file in any state (waiting, passed, failed
or removed) is never queued again, so a list can stay in the folder after its
jobs have run. `queue fill` does the same read by hand and prints which jobs it
queued, how many it already knew, and which sources it could not read. A source
that lists every record in the repository queues every one of them the first
time, so point a `records` source at the open ones.

**The queue is checked at 18:00.** `queue check` changes nothing in the
queue. It runs the `check` input gates, with no model call, on every waiting
issue row and on every job the sources would queue tonight, and writes the
lines to `precheck.txt` in the pipeline output folder: a `checked <local time>`
line, a `sources` line with the counts `queue fill` would print, then one line
per input, `<job-id>  <input>  present|missing  <code>`, with the codes
`check` prints. The sources are read, not filled, so a source line fixed after
the check still counts at the nightly fill. A suite row reads
`<job-id>  suite  refused`, since `check` takes issue jobs only. A row queued
without `--doc` reads `rules  unchecked` when the document index has
candidates, and `documents  missing  no-candidates` when it has none. A row
still marked running while no run holds the queue reads `running  stale-row`
and is checked too: the nightly run counts it as a failed try, `interrupted`,
and takes it again. On its last try that settle drops it instead, so it reads
`running  stale-row-dropped` and is not checked. A row whose check throws reads
`check  failed  <error name>`, and a queue file that does not parse ends the
lines with `precheck  failed  <error name>`. A row queued with `--resume`,
including one waiting for its second try, is checked against its checkpoint as
`check --resume` does, so a resumed job that Phase 2 would stop shows up here
instead of after Phase 1 has run.

A run that holds the queue is waited for, up to an hour; after that the file
reads `queue  held  precheck-skipped`, and a run that takes the queue mid-check
stops it before the next row with `queue  held  precheck-stopped`; a rule
export already going finishes first. While the check runs the file
reads `precheck  running`, and the final `checked` time is when the queue
was read, after any wait. A check stopped part way never leaves the last
day's lines standing. The exit code is like `check`'s: 1 when an input is
missing, a source could not be read, a check or the pre-check failed, or the
queue stayed held, and 3 when some rows' rules went unchecked; the unit fails
on 1 only.
`local/systemd/build-pack-check.timer` starts it at 18:00, four hours before
the nightly run at the default `queue.start`, so a job with a missing input can
be fixed or removed with `queue remove` first; a host with an earlier
`queue.start` moves the timer to match. A check the machine slept through is
not made up.

**A failed job tries once more.** The first time a job fails, its row goes back
to waiting with the failure kept (phase and reason code). A job that failed
during the night is not retaken that night; the next nightly run takes it and
resumes from the phase that stopped it. A job that failed in the daytime, such as
one started on request, is taken by that evening's run. A job that fails a
second time stays `failed`, is never taken again, and is flagged in the report
with both reasons. A model failure during the night window, such as `model:runaway`, waits
for the next night like any other failure. A run that died mid-job counts as a failed try with the
reason `interrupted` and no wait. A run that works every queued row takes it at
once; a `queue start` run works only rows marked `--now`, so it leaves the row
for the night. `queue start --job <job-id>` on a job waiting for its retry runs
it without waiting, and so does a `--now` row under a `queue start`. `queue add
--now` only marks the row; the start comes from `queue start`. A stop for low
memory (`memory:low`) is kept in the row's failures but is not counted as a try, until the third
in a row drops the job. `queue add` on a dropped job is how a person puts it back.

A stop that a second try on the same checkpoint cannot change is not retried:
`gate:rules-not-extracted`, `gate:rules-malformed`, `gate:document-file`,
`gate:duplicate-rule-wording`, `gate:rule-conflict` and `gate:needs-user-review`. The
row is marked `stopped`, keeps its checkpoint, and no run takes it. `queue status --job` prints its phase, reason and, for a
Phase 2 stop, `documents=<count> numbers=<n n>` (`document=<n>` for an intake
stop), which name the documents by number. Once the documents or their rules are
fixed, `queue add --issue <n> --resume` (or `--suite <code> --resume`) puts the job back in the queue as a new
row with no failures, and the pre-check reads its checkpoint. A stop on
`gate:needs-user-review` is the exception: the checkpoint keeps the old change record, so add
the job again without `--resume` once the record holds the answer to each question in
`work/phase3-review.json`. A `gate:builder-fail` stop in a Phase 9 step (`phase9-checklist`,
`phase9-senior`, `phase9-confidence` or `phase9-revalidate`) is not retried either, and its
row is marked `stopped`: the review's repairs could not make the builder accept the pack,
and a resume would build the same pack from the same checkpoint. Its `fail` line names the
failed sheets; once what they name is fixed, `queue add --resume` puts the job back. The
same reason at `phase8` is retried like any other failure. A stop on
`gate:rule-export-failed` is an outage and is retried like any other failure.
`gate:source-conflict`, `gate:rule-conflict` and `gate:needs-user-review` first wait
for the build supervisor when one is watching; see "Answering the model's questions".

**The report.** `report` reads the queue file and each job's `status.log`, and
writes `daily-<date>.md`; on the configured weekday (`report.weeklyDay`, 1 for
Monday) it writes `weekly-<date>.md`, the same layout over seven days with a
count for each day. The files go in the output folder's `reports/` folder, or in
`report.dir`. Like the status lines, they hold job IDs, reason codes, counts,
confidence ratings and run times, and nothing a document or the model said, so
a file can be opened or sent anywhere. Each has:

- a summary: jobs passed, jobs waiting to retry, jobs dropped, jobs dropped
  for repeated low-memory stops, jobs held on a gate a retry cannot change
  (`HELD`), and the queue's depth;
- a table with each job's result (PASS, PASS WITH LIMITATIONS, RETRY, DROPPED,
  MEMORY or HELD), the phase and reason code of the gate that stopped it, the sheet
  counts (pass, limited, fail), the confidence rating and the run time;
- the jobs that keep failing, with every reason code and whether each retries or
  has been dropped;
- the steps cut at their output budget: for each job that finished in the period,
  every thinking step its queue runs cut on two or more runs in a row, with the step's
  budget and how many runs cut it;
- a spot-check list: packs rated Low confidence first, then PASS WITH
  LIMITATIONS, up to `report.maxPriority` (6), then `report.sample` (2) more
  chosen at random from the other passed packs. `--seed <n>` or `report.seed`
  makes the random choice repeatable.

`local/systemd/build-pack-report.timer` writes the report at 07:30 each morning,
half an hour after the queue's default cutoff.

**Maintainer runbook.** Every command below is `<pipeline> <command> --config
<pipeline-config>`, run on the host that holds the timer.

- Add a job. Put its number on a line in a file in the source folder, or run
  `queue add --issue <n> [--change <m>]`. To run a dropped job again, run
  `queue add` for it. Anyone who can write to the source folder can name the
  documents the model will read (`--doc` on a line), so keep that folder
  writable only by people trusted with the repository's documents.
- Remove a job. Run `queue remove --job <job-id>`, and take its line out of the
  source so it is not a surprise later; the job stays out of the queue either
  way. A job that is running cannot be removed; remove it after it finishes.
  `queue remove` and `queue fill` take the queue's lock, so while a run holds the
  queue they say so and exit; run them again when it ends.
- Read the report. Open the newest file in the reports folder. Start with
  "Jobs that keep failing": a DROPPED job needs a person, and its reason code and
  phase say where to look. A RETRY job needs nothing yet. Then open the
  workbooks in the spot-check list and judge them. Packs with Low confidence or
  limitations come first because they are where the model was least sure. A
  queue depth that grows night over night means the jobs take longer than the
  night allows. A step under "Steps cut at their output budget" is handled by the
  rules under the model settings above: on a host with the server's thinking
  budget, more room for its answer, and on a host without it, its thinking
  turned off in `local/phases.mjs`.
- Restart the model server. Find its unit name: the port in the config's
  `model.endpoint` says which service listens, and `systemctl --user list-units
  --type=service` (or `systemctl list-units --type=service` for a system unit)
  shows it. Check that it is up with `systemctl --user status <model-server-unit>`,
  then restart it with `systemctl --user restart <model-server-unit>`. Do it
  while no job is running (`queue status --job <job-id>` shows `held` while one
  is). A restart during a job makes the call in flight fail, and the job takes
  an ordinary failed try (`model:network`, `model:http` or `model:no-reply`),
  so it is retried like any other failure; only a pipeline process that died
  itself leaves an `interrupted` row. After a restart, the server's request
  time-out must still be at least `model.timeoutMinutes`, and its context size
  should still match what you want, because the pipeline uses the smaller of
  that and `model.context`, so a larger `model.context` is not honored.
  Lemonade keeps the window as a saved recipe option on
  the model, so read `recipe_options.ctx_size` from
  `<endpoint>/models/<model name>` (`<endpoint>` and `<model name>` as defined
  above) to confirm it; `/health` shows nothing until the model is loaded.
- Move the timer to another host. On the new host install the repository, the
  model server, the pipeline config and the env file at
  `~/.config/build-pack/env`, then copy `build-pack.service`, `build-pack.timer`,
  `build-pack-check.service`, `build-pack-check.timer`,
  `build-pack-now@.service`, `build-pack-report.service` and
  `build-pack-report.timer` to
  `~/.config/systemd/user/` and run `systemctl --user daemon-reload` and
  `systemctl --user enable --now build-pack.timer build-pack-check.timer build-pack-report.timer`. Run
  `loginctl enable-linger <user>` on the new host as well, or user timers stop
  when that user logs out and the night's run never starts. Copy the queue file
  (`queue.file`) and the pipeline's output folder (the jobs' status logs and the
  reports) from the old host so the queue and its history carry over, and run
  `queue status` for a waiting job to check it is read, and
  `check --config <pipeline.json>` to confirm the host is ready. Then
  `systemctl --user disable --now build-pack.timer build-pack-check.timer build-pack-report.timer` on
  the old host. Two hosts with the timer on would build the same jobs twice,
  since the queue lock is per host.

## Where the reference material may go

Nothing from `<reference-dir>` leaves that folder, and nothing under
`<shipped-paths>` may carry its text. The workbook holds the session's own
analysis of this change, never passages copied from the reference documents: no
procedure text, no methodology wording in a card or a note.

## What the procedure's repository components are

`<procedure>` names repository components it expects to have loaded.
`<component-map>` says where each one is in the repository, so none of them is
missing. Read `<baseline-packs>` for shape and depth; a new pack should match or
beat them. Do not copy their cards into it.

## Inputs, and where they come from

| `<procedure>` input | Source |
| --- | --- |
| `<issue-term>` number, `<change-term>` number | the request |
| `<change-term>` or `<issue-term>` description | `<description-source>` |
| Business rule matrix | the business rule master, through `<rule-export>`, one call per process description; `check` reports whether each document's rules are usable before a job runs |
| Process description | `<process-docs>` |
| Design or module specification | `<design-docs>` |
| `<attached-only>` | attached by the user; there is no copy in the repository |
| Existing `<test-tool>` test plan and test lab assets | `<existing-tests>` |
| Existing automation | `<existing-automation>` |

### Refreshing the source documents

Before a job is checked, run, or queued, the session makes sure every document
the pack relies on is current. A candidate document that intake picks later
is checked the same way before Phase 1 passes, in a session build. A pack built from a stale converted copy gets its
rules, its conflicts, and its scope from text the change has already replaced.

1. **Find the documents.** In a session build, every document the
   `<issue-term>`, the `<change-term>`, or their thread comments name or point
   to, plus the candidate documents intake picks. For a job on the local
   pipeline the session reads none of those, so the documents are the ones the
   request names with `--doc`; a document the model picks at intake is not
   covered, and the user is told so.
2. **Check each against the library** with `doc-watch`'s lookup
   (`payload --mode lookup --name <file>`, then `lookup`), which reports each
   named document's Modified time to the minute. Each `<file>` is the library
   file name from the converted copy's `Source` line; a document with no
   converted copy is named as the request or the description gives it. A result
   with `readable` false is the unreachable case in step 5. A document that comes
   back `held`, `no_suite`, or `not_found` goes to the user through `<ask-user>`
   rather than being guessed at; one that comes back `ignored` is left as it is. A document is **missing** when
   no converted copy exists. It is **stale** when the library copy was modified
   at or after the converted copy's `Converted` minute, compared to the minute and
   not by day. A converted copy whose `Converted` line holds only a date has no
   time to compare, so a library copy modified on that day or later is stale. In
   a session build a document is also stale when the `<change-term>` says it was
   updated after the converted copy's `Revised` date.
3. **Download, convert, and use the new copy, without asking.** For each missing
   or stale document, download it through `doc-watch`'s download handler, place
   it with `place --keep-resaved` so a same-day edit is not dropped as a re-save,
   convert it with `convert-docs`, and run the job on the new conversion. This
   is a standing approval for the download and the conversion only: a run on
   the local model still waits at the model gate, and `doc-watch`'s other
   downloads still ask first. A conversion that needs a hand merge stops for
   the user.
4. **Keep a record.** Put each refreshed document on a `<download-branch>`
   branch with its `library.tsv` row, and open a pull request for it, so the
   repository copy catches up through the usual review. Name every refreshed
   document in the pack's intake notes.
5. **When the library cannot be reached**, such as on an overnight run with no
   signed-in browser, the job does not build from a copy that might be stale
   without saying so. This skill stops: the session does not run or queue the
   job, and reports which documents need refreshing. In an attended session
   the user may choose to go ahead anyway; Job Intake then lists each document
   under `<intake-sheet>` limitations as built without a check against the
   library. The local pipeline has no such flag, so a job on it waits until the
   documents are refreshed.

The session reads the library's listing and each copy's provenance block for
the check, never a document's content.

### A suite pack

`<suite-invocation>` builds one pack for a suite's whole approved rule set
rather than for an issue. The suites are `<suites>`. There is no issue or
change, so the pack sets `suite` to the suite's code and `suiteInput` to what it
used in their place, and the change description in `<id-fields>` describes the
rule set. The rules come from one folder export, `<folder-export>`, and the
sources are that folder's documents. The builder then names the workbook
`<suite-workbook-name>`, test case IDs read `<suite-case-id>`, and
`<dashboard-sheet>` shows the suite and its input where an issue pack shows the
issue and the change.

A suite pack has no change under test. Phase 3 classes every rule `Regression`,
`<core-objective>` is Not Applicable, and `<rule-matrix-sheet>` has to reach
every active rule, covered or with the reason it is not. The suite's rule count
runs to hundreds, so Phase 6 can fan out to subagents, one group of documents
each, writing one card file per document, `<code>.json` after the code its rule
prefix carries (`<rule-code-example>`), holding `cards`, `uncovered`, `reuse`
and `assumptions`. The session writes the rest of the pack, plus `suite`,
`modules` (each code's module name and abbreviation, in run order) and
`sourceAuthority` (what the suite's documents are), into a narrative file, and
merges:

```bash
<suite-merge> --export <scratchpad>/export.json \
  --cards <scratchpad>/cards --narrative <scratchpad>/narrative.json \
  --out <scratchpad>/<suite-pack-file>
```

The merge numbers the IDs, adds every requirement card to the regression and
full coverage sets, builds one set per objective in run order, and decides
applicability from those sets, so none of it can disagree with the cards.

A process description with no rules in the master has none to export: run
`<extract-skill>` for it first, or, when the user chooses to go ahead without,
derive the rules in Phase 2 from the document itself and record that in Job
Intake as a limitation. Never invent a rule ID: a
rule the master does not hold is named by its source and statement, and that
name goes in the rule's `id`, which is how the cards refer to it, for example
`<derived-rule-example>`. A source with no page numbers, such as a sign-off
document, gives `N/A` as `sourcePage`.

## The pack file

Every phase writes its output into one JSON file in the scratchpad,
`<scratchpad>/<pack-file>`, and the builder reads only that file. Its fields, by
the phase that fills them:

| Field | Phase | Shape |
| --- | --- | --- |
| `<id-fields>` | intake | the change-applies field is false when the change has no `<change-term>` |
| `suite`, `suiteInput` | intake | a suite pack only, in place of the issue and change numbers |
| `sourceDocuments` | 1 | `{ name, inclusion, authority, reason, informationObtained, directImpact }`; `informationObtained` is what the source gave the build and `directImpact` is true when that information directly affects the change; inclusion is `Included`, `Supporting Context Only` or `Excluded` |
| `intake` | intake, 1 | `{ received, missing, authority, contextOnly, secondaryRequests, decisionsRequired, assumptionsToProceed, readiness }`; readiness `READY` or `READY WITH ASSUMPTIONS` builds; `INSUFFICIENT INPUTS` and `USER DECISION REQUIRED` stop |
| `rules` | 2, 3 | `{ id, name, module, sourceDocument, sourcePage, summary, risk, impact, rationale, status }`; impact is `Direct Change`, `Indirect Impact`, `Regression` or `Not Impacted`; status is `Active` or `Retired`, and the builder writes it in the Impact Analysis Status column; `module` is the abbreviation, such as `INV`, for a document the config key `moduleAbbreviations` names (a document code or module name mapped to its abbreviation) |
| `executiveSummary` | 4 | `{ scope, modules, sourceDocuments, strategy, execution, risks, confidence }` |
| `impacts` | 4 | `{ windows, businessFunctions, upstream, downstream, data, security, batch, notices, reports, interfaces }`, each a list of short lines; an area the change does not reach is `[]` |
| `objectives` | 5 | `{ objective, applicable, reason }` for each of `<workbook-standard>`'s `<objective-count>` |
| `testCards` | 6 | `{ id, title, module, sourceDocument, mission, focus[], expected, rules[], objectives[], derivation, kind, steps[] }`; `focus[]` lists the tester's actions in order, one item per step, and the builder writes it as numbered steps; derivation is `Requirement` or `Quality`; `kind` is the kind of the scenario the card was written for, one of the scenario kinds, `decision` for a card a Phase 9 repair adds, and `null` for a card with no scenario; each step is `{ description, expected, rules[] }`; a card holds no scenario ID or `breakIt` flag |
| `testSets` | 7 | `{ number, name, objective, scope, ruleSummary[], cards[] }` |
| `coverage` | 9 | `{ ruleId, status, strength, gap, recommendation }`, only where a rule is not plainly Covered |
| `assumptions` | 9 | `{ assumption, why, impact, clarification }` |
| `seniorReview` | 9 | `{ missed, businessBehavior, upstreamDownstream, obviousFirst, qualityDerived }` |
| `testerNotes` | 9 | `{ testData, execution, regressionTargets, breakIt, screenshots, sqlValidation, knownRisks, cautions }` |
| `confidence` | 9 | `{ overall, coverage, remainingRisks, assumptions, regressionScope, breakItScope, manualReview }`; overall is `High`, `Medium` or `Low` |
| `limitations` | any | `{ "<sheet name>": "<why it is not complete>" }` |
| `revalidation` | 9 | `{ passed, remaining[] }`, set only when revalidation fails; the builder shows `<validation-sheet>` as FAIL with `remaining`, and still writes the workbook |
| `improvementNotes` | 10 | `{ gap, impact, recommendation, component }` |

The builder works out the rest: the `<dashboard-sheet>` counts and coverage
percentage, the `<objective-sheet>`'s related cards and sets, both Markdown
columns, every `<upload-sheet>` row, the `<rule-matrix-sheet>`, the derived
columns of the `<coverage-sheet>`, the assumption IDs, and
`<validation-sheet>`. Do not type those into the pack; a hand-typed count is one
that drifts from the cards.

The builder also lays each sheet out as the reference pack (one of
`<baseline-packs>`) does: a title row, a subtitle row and the headers in row 4,
under the sheet and header names in `<workbook-standard>`. The
`<dashboard-sheet>` labels its rule count "Number of Impacted Business Rules",
because the count leaves out Not Impacted rules. Two choices differ from the
reference on purpose, and the comparison records them as deliberate: the ALM
Upload Test Name is the card ID alone, so a "/" in a title never reaches the ALM
import, and every step that checks something carries an observable Expected
Result, where the reference writes one on the final step.

## The phases

`<procedure>` governs. What follows is how each phase runs and what it leaves in
the pack. After each phase, check its outputs against the procedure, record the
phase as passed in the running summary, and only then start the next.
`<procedure>` asks for one phase per response unless the user wants a condensed
run; in a session working on its own, run the phases in order in one pass, but
never merge two phases' work, and stop at the first gate that fails.

**Job Intake.** In a session build, the source documents were refreshed first,
as "Refreshing the source documents" above sets out; name each refreshed
document in the intake notes. Classify the request (`<job-type>`), inventory every input
against the table above, and set `intake.readiness`. What intake records as
missing is what it did not receive, not the procedure's list of preferred
inputs: a converted document whose provenance path is in a CAMP Designs folder counts
as the CAMP document, and its revision date counts as the updated design. The
change description in `<id-fields>` holds only the record's ALM short and long
descriptions. The four required inputs
are the `<issue-term>` number, the `<change-term>` number when the change has
one, the description, and either rules in the master or a source document to
derive them from. One missing is found here and stops the run at Phase 1, the
gate `<procedure>` names for it, before any summary is written: ask only for
what is missing, through `<ask-user>`. The builder refuses a pack missing one
the same way, printing `STOP at Phase 1` and the missing inputs.

Readiness is one of `READY`, `READY WITH ASSUMPTIONS`, `INSUFFICIENT INPUTS`
(a required input is missing) and `USER DECISION REQUIRED` (the user must
choose before the build can start). The primary job is Build Test Pack; any
other request in the record goes in `secondaryRequests` and does not change the
build. Candidate documents are chosen from an outline of each one (title,
section headings and source line), in as many calls as the index needs. In the
local pipeline, a decision stops the run as `gate:user-decision-required` and
its text is kept in the job's `work` folder.

**Phase 1, Project Understanding Gate.** Write the Project Understanding Summary
in the conversation: change, purpose, modules, existing and new behavior, rules
identified, in and out of scope, missing information, confidence. Rank every
source by the gate's authority order and give each an inclusion decision with a
reason, the information obtained from it, and whether that information directly
affects the change; drop what cannot be justified. Give the confidence a brief
reason, written before the rating. Two included sources that conflict stop the
workflow: name the conflict and ask. Missing information the change cannot be
understood or scoped without stops it as well: list it as blocking missing
information and ask only for that. Low confidence stops it too. No test design
starts before this gate passes.

In the local pipeline, blocking missing information stops the run as
`gate:missing-information`, and its text is kept in the job's `work` folder.
When the rules do not fit in one call with the documents, they are read in
batches, and each batch can report conflicts and blocking missing information.
The rule batches think; the understanding call that writes the summary runs with
thinking off, at `model.maxOutput`. Conflicts alone, with no blocking missing
information, wait for the build supervisor before they stop the run as
`gate:source-conflict`; the understanding call reads the answers to the conflicts
the rule batches found.

**Phase 2, Business Rule / Requirement Intake.** Build `rules` from the included
sources only. Rule IDs come from the master export exactly as held; source page
is the rule's `source_page`. Each rule carries its `requirement_type` from the export, or
the config's default when the export gives none. Merge duplicate wording, never unrelated
rules. These stop here, each with the findings in the job's `work` folder:

| Code | Meaning |
| --- | --- |
| `duplicate-rule-wording` | two live rules of one document say the same thing in the same words (a short statement counts only when the names match too); `phase2-duplicates.json` holds the pairs, and the master has to retire one. Rules derived for a document the master holds none for are not checked. The job waits for a person |
| `rule-conflict` | two live rules require different behavior for the same thing, as a model call reads them in batches (an exception is not a conflict, and a pair split across two batches is not compared); `phase2-conflicts.json` holds the pairs. A suite job skips this call. The job waits for the build supervisor's answers when one is watching, and otherwise for a person |
| `untraceable-rule` | a rule has no name or no summary |

A rule with no source page warns and never stops the run.

**Phase 3, Change Scope Analysis.** The `<change-term>` description is the
lens. Set each rule's `impact` and `rationale`. A process description's full
baseline is not the change: rules the change does not touch are `Not Impacted`
or left out, and the count left out is said in the summary. Note ambiguities as
assumptions. The four classes are Direct Change, Indirect Impact, Regression and Not Impacted.
The phase ends with a downstream result: `READY`, `READY WITH ASSUMPTIONS` when it added
assumptions, or `NEEDS USER REVIEW` when a question only the user can settle is left.
A question the scope call raises goes to a second call, with thinking off, that reads it
against the `<change-term>` description alone, quotes the sentence that bears on it, and
answers it, settles it with an assumption, or keeps it. An answer becomes an assumption
whose why quotes that sentence, when the sentence is found in the description with only the
words compared and is at least three words long; otherwise the answer is an ordinary assumption. A found sentence
shows the quote is real, not that it decides the question, so read these assumptions with
the pack. The run keeps a question the call rules kept, one whose answer is missing or under
three words, and one whose assumption talks about how the pipeline ran. The status line counts
the questions `raised`, `answered` and `assumed`, and `review` counts the ones kept. A kept
question waits for the build supervisor when one is watching, and otherwise stops the run
with `needs-user-review` before the impact analysis;
`work/phase3-review.json` lists each one as `question`, the `quote` the second call gave,
and `verbatim`, which is false when that quote is empty, under three words, or not in the description. Put
the answer in the `<change-term>` record and add the job again without `--resume`, so the
record is read again.

**Phase 4, Impact Analysis.** Modules, windows, business functions, upstream and
downstream effects, data, security and roles, batch, notices, reports and
interfaces. This fills `executiveSummary`, `impacts` and the risk on each rule. The
scenario and card calls of Phase 6 and the checklist and senior review of Phase 9 read
`impacts`, cut to fit the model's window. When the pack holds no `impacts`, those calls
go without it. Every Direct
Change, Indirect Impact and Regression rule is rated from the impact analysis,
with the master's `risk_level` as its starting value; a Not Impacted rule keeps
the master's, or is rated when the master gave none. A suite pack has no change
to rate against, so it keeps the approved risks and rates only a rule with none.
Code then raises any Direct Change rule below the first configured risk level,
High by default, to that level and lists each one it raised in detail.log.

**Phase 5, Testing Objective Selection.** Decide all `<objective-count>`
objectives, each with a reason. None is left out. The model decides each one
from the change and the `<methodology>` chapter on testing objectives. A
repository can add evidence rules under `objectiveEvidence` in its config; with
none, the model's answer stands. Each rule is
`{ id, objective, claim, terms, reason }`: `objective` is a pattern for the
objective names it makes applicable, `claim` finishes the sentence "is
applicable when ...", `terms` is a list of patterns that a quote must all match,
and `reason` is the objective's reason when the evidence holds. Patterns are
matched without regard to case against the quote with its whitespace squashed
and lower-cased. A rule whose `objective` matches no objective is logged and left
out. Phase 5 sees the ALM description fields plus the lines of the impacted rules
that hold every term of at least one rule, as many as fit, and detail.log says how
many did not. For each rule the reply says whether the change meets its claim
and, when it does, quotes the sentence that says so. Code accepts a rule's answer
only when the quote appears word for word (whitespace and case aside) in the ALM
descriptions or in a Direct Change or Indirect Impact rule (read as its name and
summary) and matches every term; then each matching objective that is not
applicable becomes applicable, with the rule's reason. Otherwise the model's own
answer stands, and detail.log says the evidence was rejected. Evidence never
turns an applicable objective off, and a suite pack uses none. Assumptions
that cite a rule ID the pack does not hold, or a count of rules or cards it does
not have, are dropped before the build.

**Phase 6, Reusable Test Design.** One card per business decision, per the
`<methodology>` chapters on decisions and on test cards. Test case IDs are
`<case-id>`. Focus lists the tester's actions in order, one item per step and matching
the steps; the expected result is observable business behavior, and every step
that checks something has one (a setup step may leave it blank). Mark quality-derived cards. A card an existing `<test-tool>` asset or
manual test already covers is reused by name in `<notes-sheet>` rather than
written again.

Design scenarios first, then cards. For each Included document, list the
distinct scenarios its impacted rules call for before any card is written. A
scenario is one population, one action and its expected outcome, and names the
rules it checks. In a reply, a scenario's rule list holds at most as many items as the call
has rules, and its population, action and outcome are at most 674 characters each. The
list has to include, wherever the document supports them:

- a control, a population the change must not affect: the same action with no
  blocking condition, the plain save, and the adjacent paths the screen keeps,
  such as Reset and the buttons enabling again after a change;
- isolation, where another record's state must not leak into this one, and in a
  stage with several children or records the check applies to the selected one
  only;
- a combined scenario, where conditions overlap;
- persistence, closing and reopening the record;
- negative, a record or user the rule excludes, which must not get the behavior;
- role, another role or population for whom the outcome differs or must stay the same;
- state-change, a record that moves to another state over time, so the outcome
  follows the new state;
- manual-batch, the same change made by hand and by a batch or automatic process;
- navigation, leaving mid-task (back, cancel, timeout) and returning;
- re-entry, processing the same record again;
- in an issue pack with a `<break-objective>` set, a break scenario, which tries
  to break the change with bad input, a wrong order, a boundary or a repeated
  action.

Where the document gives them, a population names the stage under test, how the
tester reaches it, and the test data (which record, which child, with what
values), and step 1 of each card opens the stage through that entry path. Never
invent a path or data the document does not give.

Every other scenario is a plain decision. The kinds the document does not
support are recorded in one assumption per document, which names them and gives
each kind's reason. Rules too many for one call are taken in batches, each shown
the scenarios listed so far, and a reply holds at most one scenario per 150
tokens of the output budget; an assumption says when a reply reached that many.
Two scenarios with the same kind, rules, population and action are one; the
second is dropped and counted.

Write the cards in batches of scenarios (`cardScenariosPerCall` in the config,
four by default). Each call is shown the scenarios still open, meaning those
with no card, reuse entry or skip yet, the rules they name, and the cards
written so far. Each card names the one open scenario it covers. A scenario is
settled only by a card, or by a `skipped` entry that says an existing test
covers it (`reused`, naming the test) or that no card can (`gap`, with the
reason); a rule gap reported for one scenario never settles another. A card
whose scenario repeats an earlier card's kind, rules, population and action is
dropped and counted. A scenario still open after its batch is asked for once
more; if it is still open, an assumption names it, and any of its rules with no
card get a `Missing` coverage row. A rule only an existing test covers gets a
`Missing` row whose gap names that test and says to confirm and reuse it.

A scenario's kind decides which scenarios, and which cards written for them, are the same (same kind, rules, population and action), which kinds the document's assumption on empty kinds names, and which cards are break cards. A Phase 6 card holds its scenario's ID and a `breakIt` flag, which is true when the scenario is a break scenario and not every rule it names is retired; in an issue pack with a `<break-objective>` set, the flag puts the card in that set. Before the cards are checked, a card that only answers a message or resets joins the card that raises the message, and a card that repeats another is dropped. A card the flag puts in the `<break-objective>` set is joined to, or dropped as a repeat of, only another such card, so a break card and a plain card that read alike both stay, each in its own sets. Where no `<break-objective>` set is in play, a flagged card is treated like any other.

Phase 7 copies each issue-pack card's scenario kind onto the card in the pack's `testCards` as `kind`, and a suite's cards reach `<suite-merge>` with it; the scenario ID and the `breakIt` flag go no further. A card carries only its own scenario's kind: a card another card was joined to, or dropped into as a repeat, keeps its own kind and does not take the kind of the card folded into it or dropped. A scenario code adds for a rule no scenario names is a `decision`, so its card is too; the cards of the break pass are `break`. A card a Phase 9 repair adds has no scenario and is a `decision` too, since it exists to give a rule a card. A card with no scenario otherwise has the kind `null`; Phase 6 leaves none, so the job goes on if one turns up. A `break` card is outside the `<break-objective>` set when every rule its scenario names is retired, in a suite pack, and in an issue pack with no such set. Whether a sheet of the workbook shows the kind is up to the builder. A reviewer sees the break cards in the `<break-objective>` set, and the kinds with no scenario in the document's assumption on empty kinds.

A retired rule Phase 3 classified Direct Change is marked in the scenario and
card prompts as removed: its card verifies the behavior is gone, and the
Expected Result, final step included, says it is absent (for a removed warning,
that the warning and its Yes and No buttons do not appear); the Expected Result
check reads such a rule as removed and passes a card that states the absence.
When no scenario names and no card cites
an impacted rule, retired or not, once its document's cards are written, code
adds a scenario for it and asks for the card, twice at most, in batches of at most the
cards-per-call setting; a rule still without a card reads
`Missing` and the `<coverage-sheet>` limitation names it.

Then check each card's Expected Result: one call per batch of up to eight
cards is shown each card, with its steps, and the rules it cites with their
source wording (the summary, and the master's description when it adds to
it), and answers `follows` or `does not follow` for every card with a reason.
The prompt gives a default for conflicting rules: a rule that blocks an action
outranks one that allows it, so the action stays blocked, unless a cited rule
says it is an exception to the block or overrides it; Reset restores the saved
value, never the edited one. A card that follows its rules but whose final step
words the result differently (see Phase 8 for what counts as agreeing) is kept,
and code copies the card's Expected Result into that final step; only a card
that does not follow is redone. A call too big for its room is split, and a card
too big alone is asked again with rule summaries only; if that is still too
big, the card is kept and an assumption says it was not checked. Each card is
shown with its derivation. A Quality card tests behavior beyond the stated
rules, so it is judged on whether its Expected Result contradicts a cited rule,
not on whether a rule states it; a Requirement card must follow. A Quality card
that is redone stays a Quality card. When no Quality card is left once Phase 7
has dropped the cards no set takes, code adds the assumption "No card in this pack is quality-derived." with
the reason.

A card that fails is designed again once through a card call for its scenario
alone, told the reason and the Expected Result that failed, and checked again.
If it still fails, or the redesign returns no card, the card is removed. When
the redesign answers with a `skipped` entry for the scenario, the scenario is
settled with that skip and its reason; otherwise it is settled as removed. An
assumption names the card and gives the reason, and each of its rules no other
card covers gets a `Missing` coverage row whose gap gives the reason (a rule an
existing test covers keeps its row naming that test). This runs before the
objective passes below, so a removed card never counts toward an objective, and
before Phase 7, so no set holds it. The Phase 6 status line adds `redesigned`
and `removed`, as numbers.

An applicable objective that no card serves gets one targeted pass. Cards that
pass adds are checked the same way. For an ordinary objective, the model is
shown the cards written and names those that serve it; the objective is added to
them, no card is written, and the objective is marked not applicable if none is
named. For `<break-objective>`, a break-only inventory adds new break scenarios,
each with one card; the objective is marked not applicable if there are none.
The break-only reply may list no scenario, which ends the pass with no card call.
The break-only call lists one kind of scenario, so the schema allows it one kind's
share of the scenarios a full reply holds: `model.maxOutput` divided by 150 tokens
and by the number of scenario kinds (12), which is 9 by default. Its output budget is
twice the tokens of those scenarios, 2700 by default, because a scenario takes 190 to
230 tokens in the replies seen. A reply cut off at that budget does not fail the
job and is not retried; any other failure of the call is retried once at the same
budget. A cut stops the pass, the status log gets a `warn` line with the
reason `break-pass-cut` after the call's `call-fail` line, and the document gets an
assumption that the break scenario list was cut off. Break scenarios an earlier
batch of rules listed are kept, and the objective is marked not applicable when
none was listed.
Once that inventory lists a break scenario, break leaves the document's
assumption on empty kinds, even when an existing test covers the scenario and no
card is written. `<full-coverage-objective>` needs no pass, since it holds every
requirement card; Phase 6 marks it not applicable when no requirement-derived
card exists.

**Phase 7, Test Lab / Execution Design.** Group cards into test sets, one
objective per set, in the order they should run: `<core-objective>` first,
`<break-objective>` last. The local pipeline's set call reads the Phase 7
methodology chapters, the cards in each set and the existing tests, and writes each
set's scope. A regression set's scope gives the execution grouping: which cards run
together, in what order, and which existing tests run again beside them. The
`<break-objective>` set's scope says what it tries to break and what it leaves out.
A scope gives no count of cards or rules: each set's rule summary is counted in code,
and counted again whenever a repair changes a card of an issue pack.
In an issue pack, the `<full-coverage-objective>` set
holds every card that comes from a requirement, and the pack marks that
objective applicable whenever one exists and a card lands in the set, even if
Phase 5 did not. The
`<break-objective>` set holds only cards written for break scenarios (`breakIt`,
set by the pipeline from the scenario's kind, never by the model). A card can
sit in more than one set. The config key `exclusiveSets` set to `true` keeps a
BREAK IT card in the `<break-objective>` set alone. A card left with no set,
because none of its objectives is applicable, is left out and an assumption
names it. The config keys `fullCoverageObjective` and `breakItObjective` name
the two sets; without them the pipeline uses the builder's objectives named
`Full Coverage Required Run` and `BREAK IT`. A Build name the user has not
supplied stays the literal `<Build Name>` and is recorded as a limitation.

**Phase 8, Workbook generation.** Run the builder:

```bash
<pack-builder> <scratchpad>/<pack-file> --out <scratchpad>
```

It prints one line per worksheet with its validation status and writes the
workbook only when no sheet is FAIL, except the `revalidation` FAIL on `<validation-sheet>` that Phase 9 sets. A FAIL names the defect: a card naming a
rule the pack does not hold, a repeated rule or test case ID, a test case ID off
the pattern, an objective with no true-or-false decision or one that disagrees
with the test sets, a rule marked covered that no card covers or marked
otherwise when a card does, a rule with no coverage and no gap, a rule taken
from a source that is not Included, a risk, derivation, inclusion or objective
off its list, or a sheet with blank fields. It also fails a rule marked Covered
that only quality-derived cards cover, a module abbreviation two modules share,
test sets out of run order, an executive summary confidence that disagrees with
the overall one, missing intake inputs with no `<intake-sheet>` limitation, and
a Direct Change rule no card covers unless a `<coverage-sheet>` limitation names
its rule ID. A design step that names no rules traces the card's rules no other
step names. Before each build the pipeline also compares every card's Expected
Result with its final step's expected result, and reports a mismatch as a failed
`Test Card Expected Results` sheet beside the builder's own. The repair call
sees the card in full but for its kind, and the problem tells it to keep the card's Expected
Result and change the final step's expected result to say the same. A repair
that changes a card's Expected Result is checked against the rules again with
the same verification call; if the card does not follow, the change is undone,
the final step included, and an assumption says so. The repair never removes an
existing card at this phase. The two agree when they are equal once case and
punctuation are set aside, or when one holds the other as whole words and the
longer side adds no negation (`no`, `not`, `never`, `cannot`, `without`, `none`,
`nothing`, `n't`) and no condition (`unless`, `until`, `only`, `except`); a
blank on either side is a mismatch. The check lives in the pipeline, not in the
builder, so it runs the same whichever builder is configured. Card design asks
for the same words in both places. Every repair call is given the design rules the pack is
built by, each stated only when it holds for the pack: the `<full-coverage-objective>`
set holds only requirement-derived cards, so a quality-derived card is rightly absent
from it; the `<break-objective>` set holds only cards written for break scenarios,
which stay out of the `<core-objective>` set, or out of every other set with
`exclusiveSets`; an objective no test card serves reads Not Applicable with a reason that
says so, which is how the pack records an applicable objective left untested, whether or
not the workbook shows a limitation for it, and no repair changes its row; and a
retired rule keeps its `Retired` status, may be a Direct Change, and as a Direct Change has
a card that verifies the behavior is gone. A set rule, or the clause of it the pack's sets
do not follow, is left out. Code then puts each corrected card
back through the set rules of Phase 7, whatever objectives the reply names: the card's
objectives become the sets those rules give it, each set takes or loses the card, and
every set's rule summary is counted again. A card the `<break-objective>` set held is
still a break card. A set never loses its last card this way: the card stays in it
and keeps that objective, even where a design rule would take it out. A suite pack's
sets stay as the suite merge wrote them, and its corrected card keeps the objectives it
had. The pipeline also checks the pack against
itself on every build, for whichever builder is configured. Four problems fail
the sheet beside the builder's own and go to the repair call: a Covered row with
a blank Gap or Recommendation; a card that cites a rule the Rule-to-Test Matrix
does not list; an Objective Matrix row that lists a card its test sets do not
hold; and a High-risk Not Impacted rule with no regression card and no reason in
its Coverage Matrix gap (text the pipeline wrote because the review gave none
is not a reason). A problem the builder already failed for the same card or rule
is not reported twice. Three more are only written to `detail.log` as a warning
line, because the builder lays those cells out itself and a repair cannot change
them: a Dashboard count that differs from its sheet (the label belongs to the
builder, and only a label that says impacted is read as leaving out Not
Impacted rules), a Rule-to-Test set column that leaves out a set one of its
cards is in, and a confidence level that differs across the Executive Summary,
Dashboard and Confidence Assessment. Before the builder runs, code settles what
it can: the summary's confidence is set to the overall one, and a Covered row
the review left blank reads "Not reviewed; coverage rests on the card mapping"
with the card IDs, and "Confirm in review that the cards exercise this rule."
A High-risk Not Impacted rule is never filled that way. `<validation-sheet>` itself reads PASS WITH
LIMITATIONS when any sheet does. Fix the pack and run it again. A sheet that
cannot be completed gets a `limitations` entry saying why, and validates PASS
WITH LIMITATIONS. The
`<upload-sheet>` test name is the test case ID alone, as `<workbook-standard>`
gives it; the title travels in `<cards-sheet>`.

In the local pipeline the build above runs in memory, and once it passes, Phase 8
ends by writing the Draft workbook to the job's `work/review` folder with the builder
command. Until Phase 9 rates the pack, the draft stands in for what the review writes:
its review fields read `Pending review.`, the overall confidence and the Executive
Summary confidence read `Low`, and `<confidence-sheet>` has the limitation `Pending
review.`, so the draft never claims more than the pack supports. Once the pack is
rated, the draft carries the real rating. The stand-ins live only in the draft and
never reach the finished pack. Each sheet the builder command prints as FAIL goes to
the same repair call with the indented lines under it, `<validation-sheet>` only when
no other sheet failed, and the pack is built again. A status line with the event
`draft` says whether the workbook was written and how many sheets failed. When the
last try still leaves no Draft workbook, or the command writes none and names no
failed sheet, the job stops with `gate:builder-fail`, and the command's output is in
`detail.log`. Phase 8 does not pass without a Draft workbook on disk. A refused draft
puts `failedSheets` on the `draft` line and on the stop's `fail` line: the names of the sheets
the builder failed, joined with `+`. Both also carry `problem`, the first line of the notes of
the first failed sheet whose first note line leaves anything (the sheet's `populated:` line is
skipped).
Only plain words stay in it (a short fixed list such as `has`, `no`, `row`, `card`, `covered`);
each quoted span, every other word, a capitalized word that does not start a sentence (unless
it is a sheet or status word such as `Coverage` or `Missing`), and the rest of a line after a
quote that never closes becomes `_`; each word that holds a digit or has a `-` or `.` between
letters becomes `ID`; text after `said:` and punctuation are dropped. The line is cut at a
word to 80 characters, and the builder's own text stays in `detail.log`.

**Phase 9, Quality Review.** Write the Draft workbook again from the pack as it
stands, read it back as text (every card, step and Expected Result, and the other
sheets), and run `<validation-procedure>` against that text, in parts when it is
longer than one call holds. Every review call writes the draft again first, because
the review's fix rounds change the pack. A workbook read in parts opens each part with
an index of the rules that part shows and the cards that cite them, and each part
judges a rule's coverage from that index. A draft the builder refuses stops the job
with `gate:builder-fail`; no review call reads a summary in place of a refused
draft. The queue does not retry a `gate:builder-fail` stop in a Phase 9 step, because a
resume would build the same pack from the same checkpoint; see "Running unattended".
The senior review and the confidence calls read the pack summary whenever
the workbook needs more than one part. List issues and fixes, each issue under the
section of `<validation-procedure>` it falls under. Every checklist call, the read after
a fix round included, is given the design rules the repair calls are given, as facts about
the pack: it lists no issue because the pack follows one, and gives no fix that would
break one. A fix names the card, rule or sheet
to change and what to change it to; one that is blank, a placeholder such as
N/A, or names no card, rule or sheet of the pack is not applied. Each other one goes
through the Phase 8 repair, which returns corrected cards, coverage rows, limitations
and, for a finding about assumptions, assumptions. Only this fix section lets the repair
add cards; the repair of a Phase 8 builder failure takes none. Here it also accepts `newCards`,
at most 3, each covering only a rule a finding names; the card is numbered and added to
its test sets by code, with the kind `decision`. A new card's Expected Result is checked against its rules like a
repaired card's, and a card that does not follow is dropped and clears nothing. When the
pack holds a retired rule, the call is told that a new card for behavior that still
happens cites the active rules its Expected Result exercises, never retired rules alone,
and the check of a new card that cites only retired rules is told the card can verify
nothing but that their behavior is gone. A kept
new card replaces a Missing or Not Applicable coverage row for each rule it covers, even
when the reply returns such a row. A suite pack refuses new cards, since its cards come
from the suite files. When a finding asks for a new card and a rule it names is still
without one, `status.log` gets a `repair-not-applied` event with the reason `no-card`,
or `new-card-refused-suite` for a suite pack, and a revalidation item that remains ends
with "(repair produced no card)" ("(a suite pack takes no new card)" for a suite pack).
Each finding of a fix round also gets a `repair` line: its number (counted from 1, so
`--finding 0` is finding 1), what it asked for
(`asked`: `new-card`, `card`, `coverage`, `assumption` or `sheet`), what the repair returned
for it (`cards`, `newCards`, `coverageRows`, `limitations`, `assumptions`) and the `result`:
`applied`, `undone` when the checks reverted all of it (a corrected card's Expected Result
and last step put back, a new card dropped), or `empty` when nothing came back for it.
A repair line from the revalidation also names the `check`, and one for a finding split
across calls names its `part` of how many `parts`, a line for each part. When the rebuild or the
second walk after a revalidation repair stops on a gate and the pack goes back to what it was,
a `repair-undone` line with the gate's reason follows the repair lines.
Every corrected card comes back in full, so no repair call of a fix round is given more
cards than fit half of `model.maxOutput` at 2,500 tokens a card, and at least one: 3 cards at the default
16,384. In a checklist round, findings share a call while the cards they name fit the
prompt and stay within that count. In the revalidation round, and in the `repair` step,
every finding gets a call of its own. A finding that names more cards than one call
takes is split across calls, each told which of the cards it corrects; only the first
may add cards or assumptions. The calls of a round are the steps `repair-review-<round>-g<n>`
and `repair-revalidation-g<n>`, where `<n>` counts the calls of the round from 1, so it is
the finding's number only when no finding before it was split or shared a call; the
`repair` step counts its calls from 1 whatever its finding's number. Before
each call a `repair-call` line gives the first `finding` the call holds, how many
`findings`, how many `cards` it was given, and its `part` of how many `parts`. A reply
that still reaches the output budget is cut, and it changes nothing. In a checklist
round the cut stops the job as `model:length`. In the revalidation round the finding
stays open: a `repair-cut` line repeats the call's `finding`, `cards`, `part` and `parts`,
with, when the cut reply's text is known, `replyChars`, the length of the cut reply in characters, and `wholeCards`, the cards
it had finished, so a long reply can be told from one that ran away. The other findings'
repairs stand. A finding with no call that answered is left out of the fixes the second
walk is told were attempted. The revalidation item of a finding with a cut call ends with
"(a repair reply was cut off at its output budget)" when it remains. When no repair call of the round answered, the cut
stops the job as `model:length`.
A coverage row changes only for a rule
a finding names (every rule when it names the Coverage Matrix), and a limitation only for
a sheet it names; a row whose status contradicts the cards is not kept. Every other row
and limitation stays as the pack had it. The pack is rebuilt, and the checklist
reads the rebuilt workbook again, for at most two rounds. When the rules came
from document text because the rule export held none, checklist item OPS-009 runs
limited for those documents' rules and an assumption names them. Write the
`seniorReview` and `testerNotes` from the finished workbook, then the `confidence` fields
with the senior review in view. The coverage field is counted from the Coverage Matrix, not
asked of the model, and counted again on every build once it is written, so it follows a
repair that changes the matrix. Each other field is a call of its own that sees the fields already written
and the cards with the rules they cite, and is asked for no count of cards, rules or coverage
statuses. One call gives a verdict and its evidence for each of
the assessment steps (rules, decisions, coverage, regression, quality-derived, BREAK IT,
professional review, residual risk), and the overall level is rated last, with a reason at
every level that follows the level in the Executive Summary's confidence. A field that is
under 60 characters, names no card or rule ID (the manual review field, and the assumptions field of a pack with no assumptions, may name none), repeats another field's text, or cites an ID
of an ID family the pack uses that the workbook does not hold, is asked for once more with
what was wrong; a second refusal stops the job with `gate:review-field-unsupported`. When
the revalidation leaves items open, the overall level is rated again with them in view, from the assessment steps with the coverage step counted again. Then run `<revalidation-procedure>` over the
rebuilt workbook, review sheets and `<validation-sheet>` included, with one verdict for each
of its seven checks. Every walk call is given the design rules the repair calls are given, as
facts about the pack: it fails no check because the pack follows one, and gives no fix that
would break one. A failed check whose fix names a card, rule or sheet gets one repair
round, with a repair call for each such check, and one more revalidation; a repair the
builder cannot build is undone and the first
verdicts stand. The senior review, the tester notes, the written confidence fields, the
assumptions and each set's scope are not written again after the repair round. A round in
which a repair call answered adds a note to the end of the manual review field of
`<confidence-sheet>`, once: the senior review, the tester notes, the written fields of the
assessment, each set's scope and the assumptions the pack already held were written before
the last corrections to the pack, and what they say of a card, a rule or a count is to be
checked against the test cards and the Coverage Matrix. Writing that field again with the
`confidence` step keeps the note. The second walk is told that this text and the checklist
findings listed as still open were written before the repair round: none of it is evidence
that a finding is still open, the walk judges the state of the pack from the cards, the rule
and coverage matrices, the objectives and test sets, and `<upload-sheet>` as the workbook
shows them, and a gap an assumption or a limitation documents is still documented. A `walk`
step over a pack that carries the note is told so too. Each walk of the checks writes a `check` line for every check: `walk`
(`revalidation`, or `revalidation-again` after the repair round), `check`, `verdict`,
`thinking` (true when every call that judged the check ran with thinking on) and
`fixGiven`. A failed check of the second walk also carries `repeat`: true when the first
walk failed that check too, false when the failure is new. The overall level is held to the pack's confidence ceiling, the highest level
the builder accepts for the pack as it stands. The builder module may export
`confidenceCeiling(pack)`, which returns `{ level, reasons }`: the level, and in sentences
what holds the pack there. The rating call is told that level and those reasons and is
offered only the levels at or under it. A level above the ceiling is lowered to it in code,
with no further call: when a reply gives one, and before every build of the pack, so a
rating made before a repair added to what the pack leaves open, or held by a checkpoint,
never reaches the builder above its ceiling. A lowered rating's reason ends with "The rating
was lowered to what the pack supports", followed by the builder's reasons when it gives
any, and a rating lowered to
Low takes that reason as its `<confidence-sheet>` limitation. A builder module without the
export sets no ceiling: the call is offered every level and its rating stands. Each rating
of the overall level writes a `confidence` line: `overall`, `asked`
(the level the call gave), `cappedBy` (`confidence-ceiling` when code lowered the reply to the ceiling,
`untested-objectives` when an applicable objective with no test card held the level below
the highest, else `none`) and the counts it was
rated from: `stepsWeak`, `stepsPartial`, `openItems`, `checklistIssues` and `untested`. A
rating lowered before a build writes a `confidence-lowered` line: `asked` (the level the
pack had), `overall` (the level applied) and the `reason` `confidence-ceiling`. The Draft
workbook is written from a copy of the pack, and a rating lowered only on that copy writes
no line.
Fill `seniorReview`, `testerNotes`, `confidence` and `coverage` before
the final build. `<procedure>` stops on Low confidence at the Project Understanding Gate,
before anything is built. A Low rating here is allowed, but only with a
`limitations` entry for `<confidence-sheet>` saying what holds it down, and
`executiveSummary.confidence` has to match it. If revalidation does not pass,
`revalidation` holds what remains, `<validation-sheet>` reads FAIL with those
items, and the job stops with `gate:revalidation-failed`. Phase 10 and the
final build still run, so the workbook is written with the FAIL for the
reviewer; the report lists the job as failed. The queue does not retry such a
job, because a resume would skip every phase and build the same pack again; fix
the cause and queue it again, without `--resume`.

**Phase 10, Repository Improvement Notes.** Record what the reference material,
this skill, or the repository's sources lacked during the run in
`improvementNotes`, and say them in the report. `<workbook-standard>` gives them
no worksheet, so the builder leaves them out of the workbook. A gap in the
repository's own tooling is filed through `<follow-up>`.

## Where the workbook lands

The scratchpad, or a path the user names. It goes under `<docs-root>/<suite>`
only when the user asks for that, and then `<writing-gates>` apply to it. Send
the finished file to the user with `<send-file>` when the session is followed
from another device, and give its path either way.

## Loading a suite pack into the test tool

A suite pack the user has approved goes into `<test-tool>` through
`<testpack-command>`, a dry run first and a send only when the user asks for
one:

```bash
<testpack-command> --doc <committed-pack>
<testpack-command> --doc <committed-pack> --send
```

The pack file is read from `<pack-source>`. `<upload-script>` does the work:

- Each test card becomes a manual test in the test plan under `<plan-folder>`,
  named for its test case ID and title, with one design step per pack step and
  a coverage link to each rule requirement the card names. `<test-tool>`
  refuses some characters in a test name, and `<name-substitutes>` gives what
  the name carries in their place.
- Each test set becomes a set in the test lab under `<lab-folder>`, holding an
  instance of every card it names, in the pack's order.
- The requirement ids come from the master, which records them when
  `<rule-upload>` loads the suite's rules. A rule the master holds no
  `<test-tool>` id for refuses the whole run, so the rules go up first.
- Every folder on either path that `<test-tool>` lacks is created,
  `<tool-roots>` aside. The first suite to run creates `<shared-folders>` and
  the rest reuse it.
- Everything is looked up before anything is written, so a repeat dry run plans
  no writes. What `<test-tool>` holds that the pack does not name is reported
  and left in place. The send ends by planning again and fails if anything is
  still missing.

Moving the tests and sets out of the staging folders is the reviewer's job in
`<test-tool>`. Test runs and results stay out.

## Comparing a pack with a reference pack

`<pipeline> compare` scores a built pack against a reference pack (usually one
of `<baseline-packs>`), the rule export and the converted document. The
reference is a baseline to compare against, not a source of truth: the document
and the approved rules decide what is right, so a pack is never scored by how
much it looks like the reference. Without a job config it calls no model; with
`--config` it runs the model pass, which sits behind the model gate, and
scores the format against the config's
workbook standard:

```bash
<pipeline> compare --reference <xlsx> --pack <xlsx> --rules <export> --doc <md> \
  [--out <dir>] [--standard <md>] [--config <pipeline-config> [--no-model]]
```

- `--rules` is a rule export (`{ doc, prefix, rules }` or a folder export's
  `{ exports }`) or a Business Rules workbook with the export's nine columns.
- `--doc` is the converted document. Text written `~~like this~~` is read as
  retired; the page anchors place each line.
- `--standard` is the workbook standard the format is scored against. With
  `--config` and no `--standard`, the config's own workbook standard is used.
- `--config` names the pipeline config, which supplies the model endpoint. It
  turns the model pass on, and `--no-model` turns it off again. `--model` is
  still accepted and needs `--config`.
- `--out` is where `compare.json` (the scorecard) and `compare.md` (the report)
  are written. It defaults to the pack's folder, and an earlier `compare.json`
  or `compare.md` there is overwritten.

The report has four parts, and the reference is checked for truth and quality
the same way as the pack:

- **Format**: the score is the share of the workbook standard's worksheets and
  listed columns the pack holds. With no standard to score against, the score
  falls back to the layout checks and the report says so. The layout checks
  (the sheet inventory and order, the title, subtitle and header rows, the
  header names, the test case ID shape, and the ALM step style: step names,
  where Expected Result and rule references sit) are listed as how alike the
  two layouts are, never as part of the score. A check the pack
  fails on purpose is listed apart as a deliberate difference with its reason:
  the Test Name that is the card ID alone, and an Expected Result on every
  checking step rather than the final step only. `format.differences` counts the
  failed checks that are not deliberate, and a pack that matches the reference's
  format has none.
- **Truth**: each rule row is matched to an approved rule by ID when its
  wording agrees with that rule, else by the words it shares with the rule's
  summary, name or quoted text (a Dice share of at least 0.4). A row whose ID
  names a rule it does not read like, while another rule reads at least 0.1
  more like it, is renumbered: it is matched to that rule, and its risk and page
  are held to that rule's. A row whose ID no rule's wording confirms keeps the
  ID, is listed as unconfirmed, and has no risk or page difference reported.
  A row of several statements is also split at commas, semicolons
  and "and", each statement is matched to its best rule, and the row maps to
  every rule a statement picked. A row that says clearly more than another rule
  does is also mapped to that rule when it holds all that rule's less common
  words. A row that matches no rule must match struck-through text
  (a retired rule) or it is not in the source. An approved rule whose quoted
  text sits mostly in struck-through text, and less in live text, counts as
  retired by the document even when the export says active; the pack must
  record each one. A rule row that is not marked retired but uses wording found
  only in struck-through text (a word used more than once there and never in
  live text) is reported as untrue, with the document line; a negation such as
  "no warning" or "without the retired prompt" excuses the words in its own
  clause, and so does a removal right after the word ("Warning Removal",
  "warning suppressed"). Also reported: rule IDs a card cites that no Impact Analysis row,
  matrix or approved rule holds; risk and page that differ from the approved
  rule; and each card's Expected Result against the Expected Result of its last
  ALM step, flagged when one expects the change to go through and the other
  expects it stopped, or when they share almost no words.
- **Floor**: each reference card is matched to the pack cards that test the
  same scenario. A card's scenario is the controls it presses (names found in
  the document and the rules: capitalized terms after "select" or "click", and
  the names listed before "buttons"), the verbs its steps open with (search,
  export, save and the like), the words it uses, what it rules out ("no
  substantiated ... allegation"), and whether it involves another one of the
  same thing. A word counts for more the fewer cards use it, and only words the
  document and rules use count toward a match. Two cards can stand for each
  other unless one rules out something the other runs on, or only one involves
  another one. The rules the two cards cite count as much as the wording: cards
  that cite the same rules and read alike match, and citing different rules
  never lowers a score. A reference card that no compatible pack card shares an
  action with is listed as unmatched, or as a reference error when its own text
  uses retired wording. A card matched by several pack cards is covered when
  the cards that do the same thing hold, together, at least half of its
  features, and one of them does every action the reference card does. Cards
  that only share an action fill in a part and never make it covered; it is
  partly covered, and the report names the pack cards combined. Pack cards with the
  same actions and the same wording as the first card of a group, or the same
  cited rules as any card in it, are counted as repeats. The report gives the sets and
  cards per set, and whether the Full Coverage set holds every
  requirement-derived card.
- **Quality**: checks on each workbook alone, whatever the reference does: cells
  that hold only punctuation, a program value such as `undefined` or a JSON
  fragment; Assumptions and Workbook Validation notes written in the
  pipeline's words ("project understanding", "this run", gap text filled in
  because the review gave none); Objective Matrix rows marked Not Applicable
  for a reason that says the objective could be designed; Coverage Matrix rows
  rated Strong whose Gap / Concern says they were not reviewed; impacted rules
  no card cites; Workbook Validation rows that are not PASS; and cards that
  cite only rules the document retired.

The scorecard's `gate` says whether it is complete: the format was scored
against a standard and the model pass ran with every question answered. A gate
that scores a pack must refuse a scorecard whose `gate.complete` is false.

Consistency checks that need no source also run on both workbooks: Dashboard
counts against the sheets, the confidence level on the Dashboard, Executive
Summary and Confidence Assessment, matrix rows citing a card the pack lacks or
the row's sets do not hold, and Objective Matrix rows listing a card their set
lacks. A check whose column is missing is reported as not checked, with the
column named, not as zero problems.

With `--config`, the report adds the questions the word checks cannot settle:
whether each card's Expected Result follows from the rules it cites, and
whether an unmatched reference card is the same scenario as the nearest pack
card. `--no-model`, or no `--config`, skips them: the report says they were not
run, no model is called, and `gate.complete` is false.

**Limits.** The thresholds were set against one reference and pack pair and
have not been checked on others: 0.4 Dice for matching a rule row to a rule,
half of a rule's words in struck text for a retired rule, 0.1 Dice between the
rule an ID names and a better-reading rule for a renumbered row, 0.7 for a clause of a
merged row matching a rule, 0.95 and 0.5 for the extra rules a merged row
covers, 0.3 for a pack card testing a reference card's scenario, 0.7 for two
cards being the same test by wording alone, half of a card's features for
covered rather than partly covered, and 0.1 Dice between an Expected Result and
its last step. Two cards that differ only by one more kind of case (a child with
two allegation types against one) can still be counted as repeats. Treat a
count from the report as a guide to read the lists behind it, not as a grade.

The console prints only counts and the output names. Exit codes: 0 the
comparison was written, 1 it failed while running, 2 bad arguments or an input
that could not be read.

## What stays out

- An issue pack is not uploaded to `<test-tool>`. Its `<upload-sheet>` is the
  test plan import the user loads by hand.
- The business rule master is read, never changed. A rule found missing from it
  is an `<update-skill>` or `<extract-skill>` job, filed or run separately.
- `<baseline-packs>` are not edited.

## Report

Say which phases passed, where any stopped and what it needs, the workbook path,
the `<validation-sheet>` result per sheet that is not PASS, the assumptions, and
the improvement notes.
