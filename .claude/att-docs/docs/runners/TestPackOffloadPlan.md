# Test pack offload plan

Which parts of the Build Test Pack process are purely mechanical, and which of
those could run as jobs on the self-hosted runners instead of in the Claude
session, and what else could ease the memory pressure on the model's machine,
MTabletPC.
Issue 272 asks for this plan only.

This is a plan awaiting review. Nothing in it is built: no workflow, no
script, no runner job, and no follow-up issue exists yet. Every row below
describes the code as it stands in `plugins/att-docs/skills/build-test-pack/`.

Runners allowed for any job that comes out of this plan: `tablet-runner-1` to
`-4` (labels `self-hosted`, `Linux`, `X64`, `ci`, `static-checks`, `overmind`),
`pw-linux-runner-1` to `-6` (labels `self-hosted`, `Linux`, `X64`, `playwright`,
`overmind`) and `pw-ci-runner-desktop-1` to `-5` (labels `self-hosted`,
`Windows`, `X64`, `ci`, `overmind`), as `RunnerRegistration.md` lists them. Never
a GitHub-hosted runner, never `pw-windows-runner-1`, never a runner without the
`overmind` label, and never a `runs-on` that names `playwright`.

Three kinds of runner appear in that list, and they are not alike. The four
`tablet-runner-*` units are Linux system services
(`actions.runner.MRF-ORG.tablet-runner-1` to `-4`) on MTabletPC, the machine
that serves the model. They run as `michael`, with `MemoryHigh` and `MemoryMax`
both infinity, and their `_work` folders are under `~/Github/actions-runner-N/`.
The `pw-linux-runner-*` runners are Linux runners on other machines, shared with
the Playwright jobs, so they cannot reach the queue or env file a tablet can. The
`pw-ci-runner-desktop-*` runners are Windows runners on other machines. "The
desktop" is avoided below for MTabletPC, because the name also fits those
runners.

Two short names are used below. `SKILL.md` is
`plugins/att-docs/skills/build-test-pack/SKILL.md`. `local/` is
`plugins/att-docs/skills/build-test-pack/local/`, the local pipeline.

## The constraint that shapes everything

A test pack promised to the supervisor is built on the local model only, on
MTabletPC, and no work content reaches a cloud model. A Claude session
therefore never reads the documents, the rules, the description, the pack, the
workbook, or a job's `detail.log`, `status.log`, journal and `work` folder
(`SKILL.md`, "Before a job is run or queued"). Its view of a job is
`queue status` and the report's lines. The session runs commands and reports
content-free status lines.

That makes moving mechanical work off the session attractive, but a runner is
not the session's safe neighbor by default:

- Work content on a runner sits on that machine's disk, in the job's `_work`
  folder, until something deletes it. The Playwright and Overmind jobs share
  these machines.
- Anything a job prints goes to the Actions log, and anything it uploads goes to
  an artifact. Both live on GitHub, outside the local-only boundary.
- Credentials the jobs need (the rule store, ALM) stay where they are, in
  `~/.config/build-pack/env` on MTabletPC, which a tablet runner can already
  read. Risks rules out Actions secrets for them.
- A tablet runner is on the model's machine, so it can reach the queue file,
  the queue lock, the env file and the loopback model, but whatever it runs
  competes with the model for memory.

So the test for every candidate below has three parts: "is it deterministic",
"can it do the work without work content leaving the machine in a log or an
artifact", and "does it take memory from the model while a job runs". The second
and third decide most rows.

## How a test pack is built today

**Who triggers what.** The user asks the session for a pack. The session
refreshes the source documents (`SKILL.md`, "Refreshing the source documents"),
runs `build-pack.mjs check` for the input gates, asks the user about anything
missing, then either runs `queue add` and leaves the job for the 22:00 timer, or
queues it with `--now` and starts `build-pack-now@<job-id>.service` with
`systemctl --user` (`SKILL.md`, "Starting a job now"). After that it reads one
line at a time with `queue status`. When the job passes it gives the user the
workbook path and, for a suite pack the user has approved, runs the test-tool
loader.

**What runs under systemd, without the session.** `build-pack.timer` starts
`queue run` at 22:00, and `build-pack-report.timer` writes the report at 07:30
(`local/systemd/`). `queue run` fills the queue from `queue.sources`, takes the
queue lock, stops the configured units to free the GPU, runs one job at a time
through `runJob`, retries a failed job once, and leaves a morning summary
(`build-pack.mjs`: `drainQueue`, `fillQueue`, `drainJobs`, `settleRow`;
`pause.mjs`: `createPauser`). All of that is code on MTabletPC. The queue file,
the lock, the paused-units file, the job folders and the status logs are local
files on that machine, and the queue lock is per host (`SKILL.md`, "Maintainer
runbook").

**Where the model is called.** One place within a job: `phases.mjs: ask`, which
calls `model.mjs: modelClient().json`. The endpoint must be a loopback address
(`model.mjs: localEndpoint`, enforced again in `config.mjs: loadConfig`), so the
model client can only run on the machine that serves the model. Every other
module under `local/` is plain code. `compare.mjs` calls the model only when
`--model` is given, and then calls `client.json` itself, not through `ask`.

**What is inside a job.** `run.mjs: runJob` runs 14 steps in order (`PHASES`):
intake, phases 1 to 8, the four Phase 9 steps, Phase 10, then the repository's
own builder command (`config.builder.command`) for the final workbook. Most
phases are a model call with code before and after it. Section "Mixed steps"
lists which.

**Where the data lives.** In the consuming (work) repository and on MTabletPC:
the converted documents, the rule export command (`inputs.ruleExport`, which
reads the rule store), the description files, the reference material, the
builder, the job output folder (`config.output`, default
`~/.local/share/build-pack`). The SharePoint library is reached through the
user's signed-in browser (`doc-watch`). ALM and the rule store are reached by
commands the work repository supplies. This repository (Overmind) holds the
skill and the pipeline code, not any of that content.

## Step table

Classes in the Recommendation column:

- **Already off the session.** Runs without the session today (systemd or
  inside the pipeline). A runner would add nothing, or only a second place that
  can fall out of step.
- **Offload now.** Mechanical, the session only triggers or watches it, and a
  runner can do it without work content in a log or artifact.
- **Offload after a split.** Mechanical half is tangled with a model call or with
  a session-only input; see "Mixed steps".
- **Keep in the session.** Needs the user, the user's browser, or judgment.
- **Stays with the model.** A model call; local model only, on MTabletPC.

"Runner fit" assumes the runner is one of the allowed machines above. A
`tablet-runner-*` is on MTabletPC as `michael`, so it can reach the queue, the
lock, the env file and the loopback model, but it takes memory from the model
while it works. A `pw-ci-runner-desktop-*` runner is another machine and reaches
none of those. Where a row can only run on MTabletPC, it says so. Whether the
work repository's documents and tools are on MTabletPC is open question 2.

### Before a job is queued

| # | Step | Where | Mechanical or AI | Inputs, outputs, dependencies | Runner fit | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Find the documents a job relies on | `SKILL.md`, "Refreshing the source documents" step 1 | Mechanical on the local pipeline: the list is the request's `--doc` values. In a session build it is judgment (read the issue thread). | In: the request. Out: a list of file names. No network. | Trivial, but it is the user's request text, not a data step. | Keep in the session. |
| 2 | Library lookup: is the converted copy older than the library copy | `SKILL.md` step 2; `doc-watch` `docwatch.py` `payload --mode lookup` and `lookup`, `page.js` | Mechanical comparison of two timestamps, to the minute | In: each copy's `Source` and `Converted` lines. Reads SharePoint through the user's signed-in browser. Out: stale, missing, held, not_found, ignored. | Blocked: the lookup runs inside a browser page signed in as the user (`doc-watch` "Reads ... through the user's signed-in browser"). A runner has no such session, and `SKILL.md` step 5 already stops the job when the library cannot be reached. Effort L, and it needs a service-account path to SharePoint that does not exist. | Keep in the session. |
| 3 | Download a stale document and place it | `SKILL.md` step 3; `doc-watch` download handler, `place --keep-resaved` | Mechanical, but starts with a browser download | In: the library URL. Out: a file in `<todo-root>`. | Blocked by the same sign-in as row 2. | Keep in the session. |
| 4 | Convert the new copy | `SKILL.md` step 3; `convert-docs` `convert.sh`, `stamp.py`, `pages.py`, `flatten-tables.lua`, `drop-images.lua` | Mechanical (Pandoc plus filters and a stamp). A conversion that needs a hand merge stops for the user. | In: a source document. Out: Markdown with a provenance block. Needs Pandoc and the converter's dependencies. | Possible on a Linux runner if Pandoc is installed, but the input is work content and the output lands in the work repository, which an Overmind job cannot check out (open question 2). Effort M. | Offload after a split: the clean path is mechanical, the hand-merge case is not. See "Mixed steps", S1. |
| 5 | Keep a record: branch and pull request of refreshed documents | `SKILL.md` step 4 | Mechanical git and `gh` work, with a text gate on the commit message | In: converted files, `library.tsv` row. Out: a branch and a pull request in the work repository. | Depends on row 4 and on reaching the work repository. | Keep in the session until row 4 moves. |
| 6 | Input gates, `check` | `build-pack.mjs: checkJob`; `phases.mjs: documentRules`, `runCommand`; `rules.mjs: shapeProblems`, `rulesStale`, `revisedDate`; `SKILL.md`, "Before a job is run or queued" | Mechanical, no model call, prints content-free lines (`<input>  present|missing  <code>`) and writes `<job-id>.check/detail.log` | In: issue number, description files, each `--doc` file, the rule export command (reads the rule store). Out: exit code 0, 1 or 3, plus content-free lines. | A tablet runner on MTabletPC runs as `michael`, so it can read the env file's credentials and the queue, if the work repository is checked out there; a Windows runner cannot. `detail.log` has to stay on the machine. The code is plain Node, but the work repository is not on GitHub (open question 2). Effort M. | Offload after a split, and only if a tablet runner can reach the inputs. See "Mixed steps", S2. The session's part today is already one command. |
| 7 | Ask the user about each missing input; offer extract, update, or go ahead with limitations | `SKILL.md`, "Before a job is run or queued" | Judgment and a question to the user | In: the `check` lines. Out: the user's decision. | Not applicable. | Keep in the session. |
| 8 | `queue add`, `queue remove`, `queue fill` | `build-pack.mjs: addJob`, `removeJob`, `fillQueue`, `jobFromLine`; `sources.mjs: sourceLines` | Mechanical | In: job fields; for `fill`, the folder, records glob or command in `queue.sources`. Out: edits to the queue file under the queue lock. | The queue file and lock are local to the host and take a PID and start time (`lockQueue`, `holderAlive`). Only a tablet runner is on that host, and it runs as the same user, so it could reach both. A Windows runner would split the queue in two. | Already off the session, in the sense that it is a single command. Leave on MTabletPC. |
| 9 | Start a job now | `SKILL.md`, "Starting a job now"; `local/systemd/build-pack-now@.service` | Mechanical: `systemctl --user start --no-block` | In: job id. Needs the user manager on MTabletPC. | A Windows runner cannot. A tablet runner runs as `michael` on that host, but a system service does not necessarily have the user manager's environment; that was not checked. | Keep in the session (it is one command). |
| 10 | Read the outcome | `build-pack.mjs: jobStatus`, `queue status`, `queue summary`; `status.mjs: statusFields` | Mechanical and already content-safe: `statusFields` refuses any value that is not a short code | In: queue file, `status.log`. Out: the status line, the phase detail lines, and the queue listing. | Same host constraint as row 8. | Already off the session apart from the polling; leave. |

### Inside a job (`run.mjs: runJob`)

Every row here runs on MTabletPC under the queue today. The runner question is
whether any piece could run separately from the model call that surrounds it,
which only matters if a runner could receive the pack file. See open question 3.

| # | Step | Where | Mechanical or AI | Inputs, outputs, dependencies | Runner fit | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | Intake, code half: resolve description, documents, rule exports, readiness | `phases.mjs: intake`, `documentRules`, `splitText`; gates `missing-inputs`, `document-key-shared`, `rules-malformed`, `rule-export-failed` | Mechanical | Same inputs as row 6 | Same as row 6 | Already off the session. Part of the split in S2. |
| 12 | Intake, inventory call | `phases.mjs: intake` (`ask` step `inventory-N`) | AI, no reasoning; also picks the documents when `--doc` was not given | In: description, candidate list. Out: received, missing, assumptions, documents. | Local model only. | Stays with the model. |
| 13 | Phase 1 understanding gate | `phases.mjs: phase1`, `documentViews`, `digestDocument` | AI (reasoning); code after it checks module abbreviations, inclusion decisions, `source-conflict`, `low-confidence` | In: description, rules, documents. Out: summary, inclusions, modules. | Local model only. | Stays with the model. The checks after it are a few lines; leave with it. |
| 14 | Phase 2 rule intake, normal path | `phases.mjs: phase2`, `refreshRules`, `warnUnretired`; `rules.mjs: uncitedStruck`, `rulesStale` | Mechanical when every Included document has exported rules: it re-reads the exports, warns on struck-through text no rule cites, copies the rules into the pack, checks for duplicate ids and blanks. No model call. | In: rule exports, document text. Out: `pack.rules`, `warn` status lines, a `Job Intake` limitation. | Same as row 6. It runs in the middle of a job, so moving it only helps if the job is cut up (S3). | Already off the session. Candidate for a split only if jobs are ever cut at phase boundaries. |
| 15 | Phase 2 derived rules | `phases.mjs: phase2` (`ask` step `derive-dN-M`) | AI; only when the job opts in (`--allow-derived-rules` or `allowDerivedRules`) | In: document text. Out: derived rules named by source and statement. | Local model only. | Stays with the model. |
| 16 | Phase 3 scope, issue pack | `phases.mjs: phase3` (`ask` step `scope-N`) | AI (reasoning) | In: description, summary, rules. Out: impact and rationale per rule. | Local model only. | Stays with the model. |
| 17 | Phase 3 scope, suite pack | `phases.mjs: phase3`, the `job.suite` branch | Mechanical: every rule becomes `Regression` with a fixed rationale | In: the pack's rules. Out: impact. | Trivial code, but no reason to move it. | Already off the session. |
| 18 | Phase 4 impact and risk | `phases.mjs: phase4` (`ask` steps `impact`, `risk-N`) | AI. After the calls, code raises any Direct Change rule below the top risk level and logs each to `detail.log`. | | Local model only. | Stays with the model. |
| 19 | Phase 5 objectives | `phases.mjs: phase5` | AI; for a suite pack code then forces the core objective to Not Applicable | | Local model only. | Stays with the model. |
| 20 | Phase 6 design | `phases.mjs: phase6`, `designDocument`, `scenarioInventory`, `designBatch`, `verifyDocument`, `verifyCards` | AI throughout. Around the calls, code removes duplicate scenarios and cards (`scenarioKey`), tidies cards (`tidyCard`), compares a card's Expected Result with its last step (`resultsAgree`, `expectedProblems`), and assigns sets (`setsOf`). | | Local model only. | Stays with the model. The code around it has no use apart from it. |
| 21 | Phase 7 sets | `phases.mjs: phase7`, `setSummary` (one `ask` for set scopes) | Mixed. One short model call for scope text; the rest is code: Full Coverage applicability, dropping cards with no set, test case id numbering (`TC-<abbr>-<issue>-NNN`), set numbering. | | Local model only for the call; the rest needs the pack in memory. | Stays with the model (the code is not worth cutting out). |
| 22 | Suite merge | `phases.mjs: mergeSuite`; the repository's `<suite-merge>` module | Mechanical (numbers ids, builds the regression and full coverage sets) | In: folder export, card files, narrative. Out: a merged pack. | Needs the pack, so same as row 14. | Already off the session. |
| 23 | Reconcile | `phases.mjs: reconcile` | Mechanical: aligns coverage rows with cards, fills blank Covered rows with the "Not reviewed" wording, sets confidence from the overall level | | In memory. | Already off the session. |
| 24 | Pack self-checks | `pack-checks.mjs: checkPack`, `derivedSheets`; `consistency.mjs`; `phases.mjs: expectedProblems` | Mechanical, no model | In: the pack. Out: failed sheets or `detail.log` warnings. | Pure functions of the pack. Could run anywhere that has the pack. | Already off the session. |
| 25 | Workbook build | `phases.mjs: phase8` calling `builder.buildPack`; `run.mjs: runJob` final `spawnSync(config.builder.command)` (`SKILL.md` Phase 8) | Mechanical; the builder is the work repository's | In: the pack file. Out: the `.xlsx`, one validation line per sheet. | Pure given the pack, but the pack is the product and holds the work content. | Already off the session. |
| 26 | Phase 8 repair | `phases.mjs: repair`, `verifyCards` | AI | | Local model only. | Stays with the model. |
| 27 | Phase 9 checklist, fixes, confidence, senior review, revalidation | `phases.mjs: phase9Checklist`, `phase9Fix`, `phase9Confidence`, `phase9SeniorReview`, `revalidate` | AI. The checklist calls run with thinking off; the confidence, senior review and revalidation calls think. Code in between: `fixable`, `fixGroups`, `fieldProblem`, `unknownIds`, `reviewViews`. | | Local model only. | Stays with the model. |
| 28 | Phase 10 improvement notes | `phases.mjs: phase10` | AI | | Local model only. | Stays with the model. |
| 29 | Checkpoint, resume, status lines, content-free logging | `run.mjs: runJob` checkpoint; `status.mjs: jobLogs`, `statusFields` | Mechanical | Local files in the job folder. | Local only. | Already off the session. |
| 30 | Free the GPU: stop and restart units | `pause.mjs: createPauser`; `SKILL.md`, "Freeing the machine for a job" | Mechanical; `sudo -n systemctl` on MTabletPC for system scope, `systemctl --user` for user scope | In: unit names, `/proc`. | Cannot move: it exists to free the machine the model runs on. | Already off the session. |

### After a job

| # | Step | Where | Mechanical or AI | Inputs, outputs, dependencies | Runner fit | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 31 | Morning report and queue summary | `report.mjs: writeReports`; `build-pack.mjs: summaryLines`; `build-pack-report.timer` | Mechanical; reads only the queue file and `status.log`. Holds job ids, reason codes, counts, confidence ratings and run times, so `SKILL.md` says a file "can be opened or sent anywhere". | In: queue file, `status.log`. Out: `daily-<date>.md`, weekly on Monday. | The one output in the whole process that is safe to leave the machine. Only a tablet runner has the queue file. | Already off the session. See S4 for publishing it. |
| 32 | Spot-check list | `report.mjs: spotChecks` (`maxPriority`, `sample`, `seededRandom`) | Mechanical | | Same as row 31. | Already off the session. |
| 33 | Give the user the workbook | `SKILL.md`, "Where the workbook lands"; `<send-file>` | Mechanical (copy or send a file) | In: the `.xlsx`. | The workbook is the work content. | Keep in the session as a path report; the session must not read the file. |
| 34 | Compare a pack with a reference pack | `build-pack.mjs: compareCommand`; `compare.mjs: runCompare`, `compare`, `formatChecks`, `truthOf`; `truth.mjs`; `floor.mjs`; `consistency.mjs`; `xlsx.mjs: readXlsx`; `SKILL.md`, "Comparing a pack with a reference pack" | Mechanical without `--model`: no job config, no model, dependency-free zip reader. With `--model` it asks the local model two questions per card, so that mode is AI. | In: reference `.xlsx`, pack `.xlsx`, rule export or workbook, converted document. Out: `compare.json`, `compare.md`. Both outputs quote work content (card names, rule text, document lines). | The best fit in terms of code: one command, no machine state. The blockers are the inputs (the reference pack is a baseline pack, which is work content) and the output (`compare.md` is work content, so it cannot be an artifact or appear in a log). Effort S if inputs can be reached, since the Node code needs nothing installed. | Offload now, but only as a job whose inputs sit on the runner's own disk and whose output stays there, printing the exit code and the counts the console already limits itself to ("The console prints only counts and the output names"). See Job B. |
| 35 | Load a suite pack into the test tool, dry run | `<testpack-command> --doc <committed-pack>`; `<upload-script>` (`SKILL.md`, "Loading a suite pack into the test tool") | Mechanical. Everything is looked up before anything is written, and "a repeat dry run plans no writes". | In: the committed suite pack file, the test tool (ALM) over the network, requirement ids from the rule master. Out: a plan of folders, tests and sets to create. | Needs the ALM account and a route to ALM from the runner. The Linux guest in `LinuxRunnerMigration.md` shows that route can be built on a work-side runner, but none of the allowed `overmind` runners is documented as having one (open question 4). The plan output names tests and rules, so it is work content in a log. | Offload after a split: the lookup and plan are mechanical; the send is an approval step. See Job C. |
| 36 | Load a suite pack, send | `<testpack-command> --doc <committed-pack> --send` | Mechanical, but writes to ALM and `SKILL.md` says "a send only when the user asks for one" | As row 35, plus write access. | As row 35. | Keep in the session as a user-approved step. Do not schedule it. |
| 37 | Upload a suite's rules and record their test-tool ids | `<rule-upload>` (`SKILL.md`, "Loading a suite pack ..."; `business-rule-update` upload) | Mechanical, writes to ALM; the loader refuses to run until it is done | | As row 36. | Keep in the session. |
| 38 | Phase 10 follow-up filing | `SKILL.md`, Phase 10, `<follow-up>` | Judgment on what to file | | | Keep in the session. |

### Neighbors that feed the process

| # | Step | Where | Mechanical or AI | Inputs, outputs, dependencies | Runner fit | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 39 | Mirror ALM requirements into the store | `alm-mirror` `SKILL.md` ("Running it"), `<mirror-script>`, `<run-command>` | Mechanical; inserts, updates and deletes rows, no content leaves the store | In: ALM account and store connection from environment variables. Out: log lines ending with a root and a row count. | `alm-mirror` itself says it "runs on `<run-host>`, the machines that reach `<store>`". Only a runner on such a machine can do it. Log lines carry counts, not content. | Offload after a check: a runner is a fit only if one of the allowed runners is a `<run-host>` (open question 4). It does not run during a pack build, so it is a freshness job, not a pack step. |
| 40 | Tests of the pipeline's own code | `local/*.test.mjs`; `scripts/test-all.sh`; `.github/workflows/ci.yml` job `test-all` on `[self-hosted, overmind, Linux]` | Mechanical, uses fixtures only (`local/fixtures/`) | | Runs on every pull request and on pushes to main, on the tablet runners or the Linux Playwright runners, the Linux runners with the `overmind` label. `release.yml` (release-please, which runs only when `AUTOMATION_APP_CLIENT_ID` is set) runs on any `overmind` runner, the CI desktops included. No work content involved. A run on a tablet takes memory from the model if it lands during a job, so the tablets stay offline while a test pack build runs. | Already off the session, and already on a runner. |

## Mixed steps and the splits they need

**S1. Conversion with a hand merge (row 4).** `convert.sh` runs without help on
the clean path; `SKILL.md` says "A conversion that needs a hand merge stops for
the user." A runner job could convert and report only `converted`, `needs-merge`
or an error code per file, leaving the merge to the session on MTabletPC. The
split is the exit code convention, not new logic. This only helps if the source
document and the work repository are on the runner (open question 2).

**S2. `check` and the intake half of a job (rows 6 and 11).** The gate and
intake's first half are the same function, `documentRules`. Today `check` is run
once by the session before the job is queued. A job that came from
`queue.sources` skips it altogether (`SKILL.md`, "Running unattended": "Jobs queued
this way skip the `check` gates"), so a job with no usable rules is only found
at 22:00, fails at intake, retries once and is dropped. The mechanical half is
useful for exactly those jobs: run `checkJob` over every waiting row in the queue
a few hours before the nightly run, and write the content-free lines where the
report can show them. Nothing in `checkJob` needs a model. What it needs is the
rule export command and the document files, which sit with MTabletPC. Because
`checkJob(config, job)` is an exported function already used by the CLI, the
split is a small new subcommand over existing code (effort S), but where it runs
is a separate question from whether it is mechanical (see Job A).

The benefit is limited to rows that name their documents. `checkJob` checks
rules only when the job has `docs` (`--doc`). Without them it prints
`rules  unchecked  name-documents-with-doc` and `check` exits 3. A suite row
cannot be checked at all, because `check` throws "check takes an issue job" for
one. A row from `queue.sources` with no `--doc` would therefore come out as
unchecked, and the pass would close the gap only for rows with `--doc`.

**S3. Phase boundaries as job boundaries (rows 14, 22 to 25).** Phase 2's normal
path, the suite merge, `reconcile`, `checkPack` and the builder are code that
runs between model calls, with their state in memory and in
`work/checkpoint.json`. The checkpoint already lets a job resume at a phase, so
a cut between phases is possible. The only reason to cut there would be to run
the code half on a runner while MTabletPC's GPU is idle. But the checkpoint is
the whole job state (the pack, the documents, the rules), so a runner receiving
it receives the work content. No cut is recommended: the code halves are fast
next to a model call that can think for over an hour (`SKILL.md`, "Running on
the local model"), so the gain is small and the exposure is large.

**S4. Report publication (row 31).** The report is safe to leave the machine,
but today it is read from MTabletPC's `reports/` folder. A runner could
publish it, for example as a comment on a tracking issue, if MTabletPC pushed
the file somewhere the runner can read. That adds a transport and gains nothing
over `report.dir` on a share. Listed only to say it was considered.

**S5. Test-tool loader (rows 35 and 36).** Dry run and send are the same command
with one flag. The dry run can be a job with no side effects; the send stays
behind the user. The output of the dry run names tests and rules, so it needs a
quiet mode that prints counts only, and that mode does not exist as described in
`SKILL.md`. Whether `<upload-script>` can be made to print counts only is open
question 5.

## Proposed first runner jobs

These are proposals for review. Each is a workflow in this repository on
`runs-on: [self-hosted, overmind, ...]`, never naming `playwright`. All three
depend on the answers to open questions 1 and 2, and none should be built before
those are answered. A job that needs nothing from MTabletPC should prefer the
Windows `pw-ci-runner-desktop-*` runners. A job that does need it runs on a
tablet runner, while no queue run is active (the nightly run, a `--now` job, a
`queue run --cutoff` run, or a direct `run`) or with the runners paused (suggestion 4 below).

### Job A. Queue gate check

- **What it does.** Runs `checkJob` for every waiting row in the queue and
  writes the content-free lines (`document-1  present  rules-ok`, and so on) to a
  file the morning report can read.
- **Covers.** Rows 6, 8 (read only) and S2.
- **Trigger.** A schedule a few hours before 22:00, and `workflow_dispatch` for a
  single job id.
- **Runner labels.** The queue file, the env file and the rule export are on
  MTabletPC, so this needs a `tablet-runner-*` (`Linux`). They run there as
  `michael` and can reach those files. The Windows set cannot. The schedule is a
  few hours before 22:00, but a `--now` job can run at any hour, so the job
  skips itself while the queue lock is held (`<queue file>.lock`, read by
  `lockHeld` in `build-pack.mjs`), or relies on the runner pause (suggestion 4).
  `lockHeld` does not see a direct `build-pack.mjs run` (`SKILL.md` shows the
  session running a job that way): `dispatch` calls the model and pauses the
  units for it but takes no queue lock. Only the runner pause keeps the job
  clear of a direct `run`.
  It does not also skip on a `running` row: a dead run leaves its row `running`
  until the next run that takes the queue (a nightly run or a `queue start`)
  marks it `interrupted` (`drainQueue`), which would
  block the job all day. Where the lock is free but a row is `running`, the job
  reports that stale row instead of skipping. Whether the work repository's
  documents are on MTabletPC is open question 2.
- **Reads.** Queue file, description files, document files, the rule export
  command and its credentials.
- **Writes.** One status file of content-free lines. Nothing else.
- **Must not log or upload.** Rule export output, document names (the status
  lines name documents by number only), `<job-id>.check/detail.log`, any path
  under the work repository's documents folder. No artifact upload. Set
  `ACTIONS_STEP_DEBUG` off and run with `set +x`. Do not move the rule-export
  token into an Actions secret: masking hides a secret only in logs and does not
  stop a branch pull request's workflow from reading it (see Risks, "Secrets on
  runners").
- **Recommendation.** Run the same subcommand from a second user timer on
  MTabletPC. It needs no secret on a runner and leaves no log on GitHub, and it
  does not widen who can run code beside the credentials (see Risks). No
  Actions-secret setup can fence these credentials on the current plan, so the
  timer is the recommendation, not only the cheaper option. The timer version
  also skips while the queue lock is held. It has the same gap for a direct
  `run`, which only the runner pause covers. A runner job is an option only if
  the user accepts the exposure (open question 1) and the credentials stay in
  the env file.

### Job B. Pack comparison

- **What it does.** Runs `build-pack.mjs compare` (no `--model`) over a reference
  pack, a built pack, a rule export and a converted document, and prints the exit
  code and the console's counts.
- **Covers.** Row 34.
- **Trigger.** `workflow_dispatch` with paths as inputs. Not scheduled.
- **Runner labels.** It needs only Node, because `xlsx.mjs` reads the workbook
  itself, and nothing from MTabletPC's queue or model (`compare` without
  `--model` never calls `client.json`). So prefer a Windows
  `pw-ci-runner-desktop-*` runner if Node is installed there, which the runner
  document does not say. Failing that, a tablet runner while no queue run is
  active, skipping itself while the queue lock is held, as Job A does
  (`lockHeld`), or relying on suggestion 4. As in Job A, `lockHeld` does not
  see a direct `run`, so only the runner pause (suggestion 4) keeps the job
  clear of one.
- **Reads.** The four inputs, from the runner's own disk.
- **Writes.** `compare.json` and `compare.md` in a folder under the runner's
  temp folder, deleted at the end of the job. The inputs are staged in one folder
  with fixed file names, and the cleanup step deletes only those names, because
  deleting the paths a person typed could remove the baseline pack itself.
- **Must not log or upload.** `compare.md` and `compare.json` (they quote cards,
  rule text and document lines). No `actions/upload-artifact`. A final cleanup
  step removes the inputs and outputs.
- **Built.** `.github/workflows/pack-compare.yml` and `.github/scripts/pack-compare.mjs`,
  described in `RunnerRegistration.md`, "Pack comparison on the desktop runners".
- **Honest caveat.** The inputs are a baseline pack, used as the reference, and
  a built pack, so they would have to be copied onto the runner first. That copy
  is the exposure. If the answer to open question 2 is that no runner can hold
  them, this job is not worth building and `compare` stays a desktop command.

### Job C. Suite pack loader dry run

- **What it does.** Runs `<testpack-command> --doc <committed-pack>` with no
  `--send`, and reports whether the plan is empty (a repeat plan writes nothing,
  per `SKILL.md`).
- **Covers.** Row 35.
- **Trigger.** `workflow_dispatch` after a user-approved suite pack is committed.
  The send is never a job.
- **Runner labels.** The job needs MTabletPC for its credentials. The plan
  keeps the ALM credentials in `~/.config/build-pack/env` on MTabletPC and out
  of Actions secrets, so a Windows runner cannot get them. It could run only on
  a tablet runner that reaches ALM (none is documented; open question 4), under
  the same exposure and memory limits as Job A. Otherwise it stays a local
  command or a user timer, like Job A.
- **Reads.** The committed pack file, ALM (read only), the rule master's recorded
  test-tool ids.
- **Writes.** Nothing.
- **Must not log or upload.** The plan itself. Print only "plan is empty" or
  "plan has N changes" (needs the quiet mode in open question 5). The ALM
  credentials have the same exposure as Job A's: masking hides a secret only in
  logs and does not stop a branch pull request's workflow from reading it, and
  no secrets fence exists on the current plan. Keep them where they are, not in
  Actions secrets.

Not proposed as runner jobs: the Claude-triggered refresh (rows 2 and 3, blocked
by the browser sign-in), anything that calls the model, the queue itself, the GPU
pause, and any step that writes to ALM.

## Memory on the model's machine

The user asked for this section alongside the offload plan: what else, beyond
trimming the context window (issue 273), would ease the low-memory trouble
during the overnight build of October 29. It is a list of suggestions,
nothing here is changed on the machine yet, and each one wants a measured build
before it is kept.

### What the machine showed that night

These come from system logs and counters only (`sar`, the `lemond` journal,
`/proc` and the `amdgpu` sysfs counters), never from the job's own output.

- MTabletPC has about 57 GiB visible to the system and 20 GiB of swap. The
  model, `Qwen3.8-27B-Q8_0`, runs in `llama-server` under Lemonade
  (`lemonade-server.service`, process `lemond`) with `--ctx-size 153600 -np 1
  -fa on --no-mmap -ngl 99 --context-shift --keep 16 --jinja` and no
  `--cache-ram` or cache-type flags, so the defaults apply.
- The four Actions runner units, the model server and `build-pack.timer` all run
  on this machine. The runner units have no memory limit.
- From 10 PM to past midnight memory sat at 81 to 85 percent used, with as
  little as 4.6 GiB available (10 PM). Swap held about 14 GiB, 68 percent,
  the whole night.
- That swap was cold. Swap-out was 0 from 10:20 PM on, and swap-in stayed
  under 45 pages a second. Swap-out peaked from 9:00 to 9:20 PM (1,382, 1,079 and
  618 pages a second), when the runners ran CI `test-all` 3 times and a scan job
  once while the build was going.
- The GPU's GTT pool held 38,374,531,072 bytes the next morning, about 36 GiB of
  a 48 GiB pool: the weights, the KV cache, the hybrid model's recurrent state and
  the compute buffers.
- `llama-server`'s prompt cache, a host-memory store of earlier prompts, ranged
  from 5,681 to 8,186 MiB against its default 8 GiB limit. The same log shows it
  buying little. The log's `sim` (the share of the new prompt matched against the
  cache) was 0.43 to 0.67 where an entry matched (0.46 for both long replies).
  `f_keep` (the share of the matched cached prompt kept) was often about a
  quarter. The server forced a full prompt re-read 7 times after 9 PM, which the
  log puts down to likely SWA or hybrid/recurrent memory, and this model is a
  hybrid. Separately, 11 calls restored the slot's own context checkpoints, each
  149.6 MiB. Those checkpoints are not part of the `--cache-ram` store.
- Desktop apps were open beside the build: Chrome, Chromium, Spotify, Discord,
  the Claude desktop app and several Claude Code sessions, about 6 GiB between
  them. That figure adds each app's peak, so it overstates what they held at
  once.
- One reasoning reply ran from 10:12:55 PM to 11:57:31 PM, about 104 minutes,
  and stopped at exactly 40,960 tokens, the `reasoningOutput` in
  `local/config.mjs`. The next reply, from 11:57 PM to 12:38:51 AM, stopped at
  16,384, the `maxOutput`. That second reply is `ask`'s retry with thinking off
  (`phases.mjs`), so both attempts failed as `length` (`model.mjs: json`). No
  model call followed. The model was unloaded at 7:08 AM, so about 6.5 hours sat
  idle. Speeds held all night: 6.6 to 7.1 tokens a second for generation, 178 to
  214 for the prompt.
- No OOM kill shows in the kernel log and `systemd-oomd` took no action. The
  cost that night was time, not a crash or a slowdown. If the user saw a
  different symptom, such as a job that failed, that is not in these logs and the
  suggestions should be weighed against it.

### Suggestions, roughly in order of payoff for effort

1. **Cap the runaway replies.** The night above spent about 2.5 hours on two
   replies that both failed as `length`, and then sat idle for 6.5 more. `ask`
   gives a reasoning call `reasoningOutput` (40,960) tokens. On any `ModelError`
   it retries once with thinking off and `maxOutput` (16,384), whatever the
   error code. After a `length` failure that retry can cost up to another 40
   minutes at 7 tokens a second. Two changes would cut this: stop on a `length`
   failure sooner, instead of retrying the same prompt, and set a lower
   `reasoningOutput` for the phases whose real replies are short, so a thinking
   call ends on its own well before 40,960. A reasoning budget set on the server
   caps every thinking call with no code change; a lower limit for only some
   phases needs a code change. It is unconfirmed whether Lemonade launches
   `/usr/bin/llama-server`, which supports `--reasoning-budget`, or a bundled
   binary.

   Which phase hit the cap does not need new logging. In `phases.mjs: ask`, a
   `call` line is written only after a successful reply. A first attempt that the
   model fails writes a `retry` event (reason, output tokens, phase, step). (`ask`
   also throws `too-big` before any call, without logging.) A failed second
   attempt writes nothing in `ask`, because the error is thrown upward. The
   final failure shows in `queue status` and in the report. The Claude session
   does not read `status.log` (`SKILL.md`: later checks use `queue status` "and
   only it"), so the user reads these, not the session. The phases to lower can
   be chosen from them.
2. **Shrink or turn off the prompt cache.** Add `--cache-ram 0`, or a small
   figure such as 1024, to the llama.cpp arguments for the model in Lemonade's
   per-model settings, then restart `lemonade-server.service`. On the evidence
   above the cache holds 5.5 to 8 GiB of host memory and the model re-reads the
   full prompt anyway. `--cache-ram 0` should leave the slot's own context
   checkpoints alone, which are what the 11 restores used. Check prompt eval
   times before and after; if they do not move, the cache was not helping.
3. **Quantize the KV cache.** Add `--cache-type-k q8_0 --cache-type-v q8_0`
   (flash attention is already on, which these need). This halves only the
   attention layers' KV cache. The hybrid model's recurrent state is not
   affected, so the saving is smaller than half of the whole. It stacks with issue
   273's smaller window rather than replacing it. Compare one pack's output
   against a pack built without it before keeping it.

   Status (issue 287): the opt-in and the measurement steps are in the
   `build-test-pack` `SKILL.md`. The saved arguments on the machine are not
   changed. Still to fill in after the measured build: GTT before and after
   (idle and at peak), and the `compare` result.
4. **Pause the Actions runner units while a job runs.** The work repository's
   pipeline config lists the four runner units with `"scope": "system"` and
   `"busyProcess": "Runner.Worker"`. `pause.mjs` stops them when the first job is
   about to start and starts them after. A runner that is running a CI job is
   waited for, polling every `pollSeconds`, and is stopped when the worker
   finishes. The wait ends at the earlier of `pause.maxWaitMinutes` (60 by
   default) and the queue cutoff, so steady CI load cannot hold off the build
   past either. A runner still busy then is left running and logged as
   `pause: left running <unit>`, and the run checks again before each later job.
   The runners start again when the run ends, and a run that died is cleaned up
   by the next one.

   What remains is the sudoers file on MTabletPC, which `RunnerRegistration.md`
   ("Stopping the tablet runners for a test pack build") gives. Until it exists,
   every stop logs `pause: stop failed` and the build runs beside CI.

   The cost is that runs of `ci.yml` `test-all` and `release.yml` (both run only
   on the four tablet runners) wait until the queue run ends: when no job is
   left, or once the job running at the 07:00 cutoff finishes. A daytime `--now`
   job pauses them too. A gentler addition is a `MemoryHigh` limit on the four
   runner units, so a runner left running at the timeout is throttled and cannot
   take memory the model needs; `RunnerRegistration.md` has the command.
5. **Stop the desktop apps for the night with a separate pre-run step.** The
   pause list cannot do this. `pause` takes a single `scope`, `system` or
   `user` (`config.mjs`, `pause.mjs`), so apps under the user manager and the
   runners cannot share one list. Chrome, Spotify, Discord and the Claude
   desktop app also run as transient `app-*.scope` units, which `systemctl start`
   cannot restart. So the apps get closed by a step that runs before the job and
   does not try to bring them back, and `pause.units` stays for system units.
   Claude Code sessions left open overnight are the ones to close by hand. This
   frees memory without touching the model. The `closeApps` config block does
   this: it stops the listed user scopes before the pause, leaves the desktop app
   open while Claude Code sessions run inside it (they run in its scope), and
   skips a `--now` job unless `onNow` is set.
6. **Check free memory between phases.** `run.mjs: runJob` already writes a
   checkpoint after each phase. A check of `MemAvailable` and swap use before
   each model call could wait, or stop at the checkpoint and let `resume`
   carry on later, instead of running on into heavy swapping. The checkpoints
   are per phase, so stopping in the middle of a phase loses that phase's
   finished calls. The thresholds would be config values, set from a measured
   run. Given that the swap that night was cold, this is worth less than it
   looks.
   Done: the check runs at each phase boundary (`local/meminfo.mjs`) with
   defaults set from the measured night, and the `SKILL.md` section "Checking
   free memory between phases" describes it.
7. **Protect the model process.** `lemonade-server.service` has
   `OOMScoreAdjust=0` and `ManagedOOMPreference=none` now, and `llama-server`
   inherits both as its child. Setting `OOMScoreAdjust=-500` and
   `ManagedOOMPreference=avoid` in a drop-in, and putting the desktop apps in a
   slice with a `MemoryHigh` limit, means that if memory does run out the kernel
   and `systemd-oomd` take an app rather than the model in the middle of a job.
   Done: `local/oom/oom-setup.sh` installs the drop-in and the app limit, and
   `local/oom/README.md` says where each file lives and how to check it.
8. **Use a smaller quantization of the same model.** A `Q6_K` build of the model
   is about a quarter smaller than `Q8_0`, a saving of about 6 GiB at this size,
   with a small loss in quality. That is less than the prompt cache's 8 GiB at
   its peak, and it is the change most likely to change the packs, so it comes
   late and only with a side-by-side comparison of packs from both, using
   `compare` (Job B above).
9. **Move swap to zram.** The 14 GiB in swap is on disk, but those pages were
   cold that night, so the payoff is small. A zram swap device, from the
   `zram-tools` or `systemd-zram-generator` apt package, compresses pages in
   memory. Its store takes RAM from the same pool the GPU's GTT draws on, so
   on this machine it trades one pressure for another. Lowering
   `vm.swappiness` from 60 would keep the build's working pages in memory and
   push idle desktop apps out first. Try the other items before this one.

The BIOS memory split between system and GPU is left alone here: the GTT pool
already reaches 48 GiB, so a larger carve-out would only move memory from one
side to the other.

## Risks and open questions

**Risks to design around.**

- **Existing exposure on MTabletPC.** This predates the plan and the plan does
  not widen it, but it decides where jobs should run. The tablet runners run as
  `michael`. Any workflow from any private repository in the organization can
  use them (`RunnerRegistration.md`), and so can a branch pull request in this
  repository that edits a workflow and is not from a fork. Such a workflow runs
  as `michael`, beside the work content, the `~/.config/build-pack/env`
  credentials and the loopback model. The plan's jobs should therefore prefer the
  Windows `pw-ci-runner-desktop-*` runners for anything that does not need
  MTabletPC, and stay clear of an active queue run when it does.
- **Memory taken from the model.** Anything on a tablet runner competes with the
  model for memory, which the swap-out peak at 9 PM showed. Jobs from this plan
  that run there should stay clear of an active queue run, or the runners should
  be paused or given a `MemoryHigh` (suggestion 4).
- **Work content in Actions logs.** A step that echoes a path, a rule id or a
  card name puts work content on GitHub. The pipeline's own habit (`status.log`
  holds codes and counts only, and `statusFields` throws on any other value) is
  the model to copy. Any new script a workflow calls would need the same guard,
  and the workflow itself would have to avoid printing the command line with
  work paths in it.
- **Work content in artifacts.** Never call `actions/upload-artifact` with
  anything but the report, which is content-free by construction.
- **Work content left on a runner.** `RunnerRegistration.md` says each job
  replaces the `_work` checkout, but nothing says files a job copies into
  `_work` outside its checkout are removed, so they should be assumed to stay
  until a job removes them. These runners also serve `Playwright-Testing`,
  which is a separate project. A job that holds work
  content ends with a cleanup step that runs on failure too (`if: always()`).
- **Secrets on runners.** The rule export and ALM need credentials. Today they
  live in `~/.config/build-pack/env` on MTabletPC, which any process on a tablet
  runner can read already (first risk above). Moving them into Actions secrets
  widens who can read them: any workflow in this repository that a pull
  request changes could read one. Masking hides a secret only in logs and does
  not stop a workflow from reading it. The fork refusal in `ci.yml` helps with
  forks only. Limiting a job to `workflow_dispatch` on `main` does not protect
  repository secrets, because any branch pull request in the same repository can
  add a workflow that reads them. The usual fence, environment secrets with a
  deployment rule that allows `main` only, is not available here. GitHub's
  "Managing environments for deployment" documentation says environments,
  environment secrets and deployment branch rules in private or internal
  repositories need GitHub Pro, Team or Enterprise. The organization is on the
  free plan (`RunnerRegistration.md`) and Overmind is private. So no Actions
  secret setup protects these credentials from a branch pull request's
  workflow, and the second user timer on MTabletPC is the recommendation for
  Job A, with the credentials staying in the env file.
- **Two copies of the queue.** The queue lock is per host (`SKILL.md`, "Move the
  timer to another host": two hosts with the timer on build the same jobs
  twice). Any offloaded step that writes the queue file from a second machine
  breaks that. Offloaded steps should be read-only against the queue.
- **Shared runner pool.** Every private repository in the organization can use
  every runner (`RunnerRegistration.md`). A long job here takes a runner from
  the Playwright work that also draws on the `ci` runners.

**Open questions for the user.**

1. **Should the plan's jobs run on the tablet runners at all?** They are on
   MTabletPC as `michael`, so they reach the queue, the lock, the env file and
   the loopback model. The cost is memory taken from the model and the exposure
   in Risks. If yes, restrict them to times when no queue run is active, or
   pause the runners during one (suggestion 4). The recommendation for Job A is
   a second user timer either way, because no secrets fence exists on the free
   plan. A runner job for Job A is only an option if you accept the exposure.
   Job C needs the ALM credentials on MTabletPC, so it follows the same answer.
   If no, Job B goes to a Windows runner where it can, and Job C stays a local
   command or a user timer.
2. **Can a runner job reach the work repository?** The documents, the rule
   export command, the builder and the committed suite packs belong to the work
   repository, which this plan understands to be on the work side and not on
   GitHub. An Overmind workflow can check out Overmind only. Is the work
   repository checked out on MTabletPC, where a tablet runner could read it? If
   not, only row 40 (already running) and fixture-based tests qualify.
3. **Is cutting a job at phase boundaries ever wanted?** S3 recommends not. Say
   so if there is a reason to want the code halves off MTabletPC, such as the
   GPU being needed for something else mid-run.
4. **Does any tablet runner reach ALM, and does any run on a `<run-host>` for
   `alm-mirror`?** `LinuxRunnerMigration.md` documents a work-laptop guest with
   its own route and certificate setup, but it describes `pw-linux-runner`, a
   `playwright` runner, which this plan may not use. Whether `tablet-runner-*`
   can reach ALM is not documented in either runner document. A Windows runner
   is out for Job C, because it cannot get the credentials.
5. **Can `<upload-script>` print counts only?** `SKILL.md` describes the dry run
   as a plan, and does not say how much it prints. If the plan names tests and
   rules, Job C needs a quiet flag in the work repository's script first.
6. **Is the 22:00 gap worth closing?** S2 and Job A exist because queue-sourced
   jobs skip `check`. If a dropped job a day is not a problem in practice, none
   of this is needed and the `check` gate stays a one-command session step.
7. **Not reviewed in this plan.** `business-rule-scan`, `doc-impact` and
   `business-rule-extract`/`update` were read only far enough to see where
   `build-test-pack` calls into them (the rule export, the extract and update
   offers, the rule upload). Each may hold more mechanical steps. If this plan is
   accepted, they need their own pass.
