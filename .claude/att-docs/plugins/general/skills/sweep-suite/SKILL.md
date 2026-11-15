---
name: sweep-suite
description: >-
  Run a whole test suite spec by spec on one project, as a smoke wave and then a rolling
  wave that keeps a fixed number of dispatches in flight, then triage the red runs against
  a baseline, file the new failures, and write up the result. Use when asked to sweep, run
  the full suite, or check a suite after server updates or a deploy.
---

# Sweep Suite

Takes a suite, and optionally a project, a slot count, and an issue number. A request such
as `/sweep-suite <suite> 4 #<N>` sweeps that suite on its default project, four dispatches
in flight, reporting on that issue. `<suite-defaults>` names the default project for a
suite, the default slot count, and the default number of smoke specs. Every question goes
through `AskUserQuestion`, per `<asking-note>`, and only the suite is worth asking for.
Everything else takes its default.

A sweep runs only when the user asks for one in chat. No other skill invokes this one or
reproduces it by dispatching every spec in a folder, and a session never starts one as the
verification of its own change: shared edits are verified by the sample in
`<sampling-note>`, and the choice to sweep afterwards belongs to the user.

A sweep changes no code. When it runs under an issue, that issue is worked through the
`implement` skill's steps 1 to 3 (read, label, branch), and this skill replaces steps 4 to
7: there is no pull request unless a fix was asked for.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments, state files, and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing issue bodies, comments, and commit messages to a command as files |
| `<default-branch>` | The branch fixes start from and merge into |
| `<in-progress-label>` | The label that claims the sweep issue for a session |
| `<labels-note>` | The repository's note on the label read-back and what a failed edit means |
| `<branch-types>` | The branch type prefixes the history uses; a sweep takes the chore prefix |
| `<worktree-script>` | The command or tool that cuts a branch and its worktree from a freshly fetched default branch |
| `<branch-age-note>` | The note on refreshing an old branch before a run or a pull request |
| `<suite-defaults>` | The suites, each suite's default project, the default slot count, the default smoke count, and where a suite's specs live |
| `<spec-list-rules>` | How the spec list is built: the file pattern, the sort, the setup specs to leave out, how smoke specs are chosen, and the check that a project lists tests for a spec |
| `<sweep-issue-script>` | The command that writes the sweep issue's body from one template and prints its title, and how a round and its sections are named |
| `<sweep-driver>` | The command that runs both waves: its arguments, the environment settings that change workers, retries, parallelism, and extra inputs, its state files, its exit codes, and how a stopped driver is resumed |
| `<run-inputs>` | Workflow inputs a suite needs on every dispatch, how a spec that can never run at an input value is pre-skipped, and which suites change retries |
| `<follow-watch>` | The command that reports each run the driver finishes, and the call that carries its count forward |
| `<overlap-check>` | The command that names the test accounts a sweep shares with runs already in flight, and what each of its exit codes means |
| `<test-accounts>` | The document that lists test accounts, and the note that keeps it current |
| `<sampling-note>` | How a shared edit is verified by a sample of its consumers instead of a sweep |
| `<test-dispatch>` | How a test run is sent: the runner, the dispatch command, its defaults, how a run is cancelled |
| `<test-run-rules>` | The mechanics of a run: the ref to test, the title filter, the retry default, and the run budget settings |
| `<budget-markers>` | How a run that hit its budget shows in its log and tally: the timeout line, the tally wording, the banner that lists the titles that never ran, how the test cut off mid-run is counted and marked, and how a run cancelled by hand reads |
| `<run-watch>` | The ledger and the one watcher that report runs and pull requests, how a tally is read, and the run budget rule with what a split proposal carries |
| `<sweep-report>` | The command that builds the rerun list from the saved run logs and prints the write-up tables, with its checks |
| `<artifact-read>` | How a run's output and a failed test's snapshot are read |
| `<failure-snapshot>` | The per-test file that shows the page at the moment a test failed |
| `<baseline-rules>` | How the default branch's recorded results are read as the "before" picture |
| `<flake-report>` | The command that lists titles that both passed and failed on one commit, or `none` |
| `<signature-report>` | The command that lists error first lines since a date, most frequent first, or `none` |
| `<contention-rules>` | What a wait on a shared resource looks like in a run log, such as a lease timeout, and how the holder is named |
| `<discovery-rules>` | The rules for test data discovery, including what a walk that turns candidates down means |
| `<skip-ledger>` | The ledger of parked tests |
| `<deviation-note>` | The deviation gate: what counts, the record's shape, and where it lands |
| `<deviation-records>` | Where a spec-versus-app deviation is recorded and the state a new record starts in |
| `<issue-labels>` | The area label and kind label every filed issue carries, and how the round's milestone and its cleanup milestone are found |
| `<follow-up-note>` | How findings outside the sweep are filed as issues |
| `<sweep-log>` | The record that holds only the latest sweep of each project: its line shape, the note terms, the check script, and the pull request it lands in, or `none` |
| `<report-document>` | An extra deliverable the issue can ask for, such as a document built from a template, or `none` |
| `<self-review>` | The self review procedure for pull requests opened during a sweep |
| `<ready-signal>` | The ready signal: its wording, its label, and when it is withheld |
| `<pr-checks>` | The checks a pull request runs when it opens |

## 1. Pin one ref

A sweep reports on one piece of code, so every spec runs from one branch at one commit.

- Cut the branch with `<worktree-script>`, named `<type>/issue-<N>-<suite>-sweep` (or
  `<type>/<suite>-sweep-<date>` with no issue) with `<type>` the chore prefix from
  `<branch-types>`, and push it unchanged.
- Run `<branch-age-note>` before starting the driver; a branch cut for the sweep the same
  day passes it. Once the driver has started, a resumed session included, the gate is not
  run, since the pin below holds the whole sweep on one commit.
- Nothing is pushed to that branch while the sweep runs. The driver pins the remote head at
  start and stops if it moves.
- If the default branch has to be merged in partway, every spec that ran before the merge
  is dispatched again on the merged ref. Two halves on two refs are not one sweep.

## 2. Build the spec list

A sweep issue comes from `<sweep-issue-script>`, which writes the body from one template,
so every sweep of a round carries the same sections, the suite's dispatch inputs from
step 3, the spec list, and the other sweeps of the round. It prints the title. File a new
issue under the round's milestone with the labels `<issue-labels>` sets, or refresh an open one when the spec list or step 3 changes, with the body in a
scratchpad file per `<shell-text-note>`. A sweep's findings go in the body under Observed
once it has run, so a refresh is for an issue whose sweep has not started.

Build the list per `<spec-list-rules>`, sorted, one per line, in a scratchpad file. Compare
the count against what the issue names and say which specs were added or removed since it
was written.

Put the smoke specs on the first lines. Take small, fast specs from different folders, such
as a welcome page and one form page. They exist to show that sign-in, the project's setup,
and the landing page work before the rest of the suite goes out.

One spec per dispatch, never a folder or the whole suite, so a red run names one file.

List every spec, including one the project is known to exclude. The driver asks the test
runner what the project lists before the first dispatch and leaves out any spec with no
tests on that project. Dispatched, that spec lists zero tests and concludes red. When a
smoke spec is left out, the next spec on the list takes its place.

## 3. Run the driver

`<sweep-driver>` does both waves. Before starting it, run `<overlap-check>`, which reads
which suites sign in as each account from `<test-accounts>` and prints one line per other
branch with runs queued or running: that branch's suites and the accounts they share with
this one. Two jobs that sign in as one account take it in turn, so a sweep started beside
another suite's runs on a shared account spends its runs waiting, and they can time out in
the wait.

- When another sweep driver shares an account, hold this sweep until that branch has
  nothing queued or running. Hold on the watcher, never on a timer: add that branch's
  running runs to the session's ledger, per `<run-watch>`, and run the check again once the
  one watcher reports them finished. When the user wants the sweep now regardless, start it
  with one slot instead of the default, so at most one of its runs waits at a time, and name
  the shared account and the other sweep in the write-up.
- A single dispatch that shares an account is named but does not hold the sweep: it ends
  within its run budget, and a run of this sweep that times out waiting on it is a
  contention call in step 6 and goes into the step 5 rerun.
- A suite whose sign-in takes no shared account has nothing to share; the check says so.
- A check that could not answer is not a pass. A failed read is run again; a suite missing
  from the accounts document gets its accounts added there, per `<test-accounts>`, before
  the sweep starts, since the check cannot hold apart accounts it does not know.

Run the driver as a background command, from the sweep worktree, on the branch's pushed head
with nothing uncommitted, then start `<follow-watch>` as a second background call, and end
the turn.

### Follow each finished run

The driver exits only once every run in its list has finished, so on its own the session
hears nothing between the start and the end, however many runs finish or fail in between.
`<follow-watch>` closes that gap. It reads the driver's own output file, makes no remote
calls, exits as soon as another run finishes, and exits when the driver is gone, so a driver
that died or stalled is noticed rather than waited on.

Each exit is the session's cue: post the new results, note a red run for triage, then start
the watch again with the call its last line names, which carries the count forward so no run
is reported twice. Keep one follow watch per driver state directory. It is not a second
watcher on the ledger: the driver's watcher stays the only one, and the follow watch only
reads what that watcher writes. The driver's output can trail the remote by a few runs when
the API is slow; the run list on the branch is the authority when the two disagree.

- **Smoke wave.** The smoke specs run alone, no more than the slot count at a time. If
  none passes a single test, the driver stops before the rolling wave. That is one shared
  cause (sign-in, setup, the landing page): read one `<failure-snapshot>`, fix or report it,
  and start the driver again. Rerunning it unchanged teaches nothing. Every start empties
  the state directory's ledger and output file, so the red smoke rows of the stopped driver
  do not count toward the new one. Start the follow watch again with no count after each
  start.
- **Rolling wave.** The rest go out with the slot count in flight at all times. When one
  finishes, the next dispatches. The default is small because many runs at once on a shared
  runner pool measure contention rather than the specs, and several long runs at once fill
  the runner's disk with traces.
- **Dispatch settings.** Every dispatch goes through `<test-dispatch>`, on the branch's
  pushed ref, with the workers and retries `<test-run-rules>` sets, and is recorded on the
  ledger. A sweep the user asks to run with other workers or retries sets them through
  `<sweep-driver>`'s settings, and the driver logs them. `<run-inputs>` names the inputs a
  suite needs on every dispatch, the step 5 rerun driver included.
- **What the driver does with each outcome** follows `<sweep-driver>`'s exit codes: a
  dispatch that sent nothing goes back on the end of the list and is tried again after a
  pause, up to a limit, then is recorded as unsent; a refused dispatch is recorded as unsent
  with the refusal; an accepted dispatch with no run found waits and holds a slot until the
  branch's run list shows its run, and a line still without one after the wait the driver
  sets (three minutes in the repository this skill came from) goes back on the end of the
  list so the slot is not lost; a sent dispatch the ledger refused waits and is retried
  every pass.
- The driver keeps exactly one watcher on the ledger, which satisfies the one-watcher rule in
  `<run-watch>`.
- Before it reports, the driver checks every list line for a run in the ledger, and looks on
  the branch for any line that has none. It reports complete only when every list line has a
  run, prints the ledger (label, job link, tally), one line per spec it left out, with the
  reason, and one per spec a pre-skip rule closed, with what it needs. It reports incomplete
  when a line has no run, naming each such line with the reason. Those specs never ran: once
  the connection holds, start the driver again on the same list and state directory with its
  resume setting, so it sends only those lines and the sweep keeps one ledger. It refuses to
  start before dispatching anything when the list step fails, or when the test runner reports
  load errors: a spec that cannot load would otherwise read as one with no tests.

Read the driver's dispatch log a minute after starting and post the first waiting lines.
Post each later batch when the follow watch exits. One state directory holds the whole sweep,
the resend of unsent lines included. Only the step 5 reruns get a directory of their own.

The scratchpad does not outlive the session, and a driver can stop partway: a restart, a
cancelled background call, a dropped connection. Take the sweep up again with the same
branch, project, list and slots, with the resume setting at the time the first driver
started (its pinned line in the dispatch log, or the issue's first run link when the
scratchpad is gone). A stopped driver can leave its watcher running on the ledger, and the
driver refuses to start beside it, printing its process id: stop that one process by id,
never with a pattern kill, which takes down every session's watcher.

The resumed driver lists the branch's runs once, adds the latest run of each list line on
the pinned head to the ledger, skipping cancelled and skipped runs, tallies those again, and
dispatches only the lines with none. When any line had a run it skips the smoke wave. A run
on another head is not part of this sweep, so a branch that moved since the first driver
gets a fresh sweep, per step 1. On a long sweep, still write the dispatched run links to the
issue as they accumulate, so the start time and the runs can be found from the issue.

## 4. Record the runs

Once the driver exits, whichever way, post one comment on the issue with every spec, its job
link, and its tally, taken from the ledger. Write the body to the scratchpad and pass the
file, per `<shell-text-note>`.

Read each tally, not just the conclusion, as `<run-watch>` describes: a missing reporter
summary, a gap between tests and buckets, or a hit run budget are findings too. A red run
with zero failed tests is an artifact storage quota, not a spec failure.

A run that hit the budget shows it as `<budget-markers>` describes: the timeout line at the
end of its log, a tally that reads as timed out, and the titles it never reached listed under
the never-ran banner. The test that was running when the budget hit is not under that
banner, and the summary counts it as skipped: it is cut off, not failed, unless the stopped attempt was the retry of one that
failed, which the summary counts as failed. With several workers there is one per worker.
A run cancelled by hand is read the same way. Sort each run into one of two cases, per the
budget rule in `<run-watch>`:

- **Budget hit with failures**: any failed or flaky test. The failures may be what spent the
  time, so the spec is not called too large yet. Step 5 reruns its failed titles together
  with the titles that never ran and the cut-off ones.
- **Budget hit, no failures**: every test that ran passed or skipped. The spec is too large
  for one file, and step 7 files a split proposal for it. Its never-ran titles are not rerun;
  they are named in the proposal. The one exception is a run whose log shows the time going
  into discovery walks that ended in skips: candidate after candidate turned down on a
  timeout. Each new file would walk again, so a split buys nothing. That is a finding for the
  lookup, per `<discovery-rules>`, filed in step 7 with those lines, and the proposal waits
  for a run after the walk is fixed.

Never raise the run budget to get either kind through.

## 5. Rerun only what failed

Collect the failed and flaky titles from every red run, grouped by spec. For each spec with
any, dispatch once more with a title filter matching only those titles, one worker, the
default retries. Never rerun a whole spec for a few titles. Say how many titles failed and
how many the filter selects before each dispatch; the two numbers match.

`<sweep-report>` builds the list from the saved run logs, run from the sweep's worktree so
the count reads the code the sweep ran. It writes one line per spec, the spec and a filter of
its titles, and checks each title count against what the test runner lists for that filter on
the project. A count that does not match is fixed before any dispatch. A run that hit the
budget with no failures, and a red run that names no failed title, are printed rather than
listed, for step 4 and step 7.

The reruns go through the driver as well, with a fresh state directory and no smoke wave.
Follow it with `<follow-watch>`, as in step 3.

A test that passes on the rerun is flaky, one that fails twice is failing. Both count as red
in the write-up.

For a budget hit with failures, the filter also takes the titles under that run's never-ran
banner and its cut-off title (per `<budget-markers>`), which the script adds, and the count it prints includes them. A
rerun that hits the budget again with no failures makes the spec a budget hit with no
failures, and it goes to step 7 as one. A rerun that hits it again with failures is not
rerun a third time: its reds go to step 6 like any other, and the budget hit is named with
them.

## 6. Triage against a baseline

For each red test, read its `<failure-snapshot>` through `<artifact-read>` before calling
what caused it.

Then place it against the "before" picture. The recorded results come first, per
`<baseline-rules>`: every run is recorded there, default branch runs included, so the
question "was this red before" usually has its answer with no dispatch. Ask for every red
title before reading any older run log, and use `<flake-report>` and `<signature-report>`
where they exist:

- The baseline shows each matching title's last runs on the default branch. Only rows that
  started before the server change the sweep checks are the before picture; a default branch
  run after it met the same change, and its red is new like the sweep's. Rows all green means
  the title passed before and is new red here. Red, or red then green on retry, means it was
  failing or flaking before the sweep, and the rows are the baseline the write-up names.
- The flake report lists the titles that both passed and failed on the pinned commit, so a
  flaky title is told apart from one the step 5 rerun turned green by chance.
- The signature report lists the error first lines since the sweep started, most frequent
  first, which groups the reds by cause before each one is read.

A title with no baseline rows, or one whose rows all started after the change, has no before
picture in them. Only those titles go through the reads below.

Before calling any red new, check whether the default branch has fixed it since the pin:

```bash
git fetch origin
git log --oneline <pinned sha>..origin/<default-branch> -- <the red spec's folder> <its page objects> <shared code it loads>
```

The shared paths are there because a fix to a helper the spec loads lands outside its folder.
A commit there that touches the failing spec or what it loads is read against the failure
snapshot. When it fixes that failure, the red is **fixed on the default branch**, named with
the commit, and is not filed as new.

The reads for titles the recorded results have no rows for:

1. An earlier run of the same spec on the same project.
2. The suite's other sweep issues on other projects. A failure that already showed there
   before the change being checked is probably not new.
3. Open issues for the suite that already cover a known red or skipped test.
4. `<skip-ledger>`. A test it lists is parked on purpose, with its reason and what it waits
   on, so it is known rather than a new skip. A test it lists as waiting on a defect report
   that is now shown fixed is worth naming in the write-up.

A red whose error `<contention-rules>` recognizes is contention rather than a spec failure.
So is a flaky title whose failed attempt spent its time in the wait the rules name. The
holder the message names is the job that kept the resource. Such a title gets no baseline
read and no issue of its own: once that holder has finished, it goes into the step 5 rerun,
and the write-up names the resource, the holder, and how many titles waited on it.

Each red test gets one call: **new** (red now, green or absent before), **known** (matches
the baseline or an open issue, with the link), **fixed on the default branch** (a commit after
the pin fixes it, named), or **contention** (above, with the resource and its holder). For
each new one, say whether the server change or the spec caused it, from the failure snapshot.

Name the baseline behind every "before" number. Where none exists, say so; never fill one in.

A red test that turns on an account (an inactivity lockout, an unregistered user, a missing
privilege) is checked against `<test-accounts>`. What the sweep showed that the document does
not say goes into it, per that note, in the write-up's pull request.

## 7. File the new failures

Group the new reds by cause before filing any of them. One cause that reaches several spec
folders is one finding, and filing it per folder turns it into several issues worked one at a
time. Group them by failure signature across every folder the sweep reached, from the
signature report step 6 read, or from this call when step 6 did not make it. Reds that share
a first line, or whose failure snapshots show the same stall, message or missing control, are
one group. The shared code the group runs through (a page object, a fixture, a date helper)
is usually what names it.

Then search for the cause before filing it, open and recently closed issues both, since a
cause fixed last week that is red again is a regression of that issue rather than a new one:

```bash
gh issue list --state open --label "<area label>" --search "<error text or helper>" \
  --json number,title,url
gh issue list --state closed --label "<area label>" \
  --search "<error text or helper> closed:>=<30 days ago>" --json number,title,closedAt,url
```

- An open match already holds the cause: the group's folders, titles and job links are
  appended to it, and nothing new is filed.
- A closed match is linked from what gets filed, saying it was closed and is red again.
- One group in one spec folder: through the `create-issue` skill, appending to the folder's
  open issue when there is one, with the job links and the error.
- One group across several folders: one issue through the `create-issue` skill, named for the
  shared code the cause runs through, whose body lists every folder and test title it reaches
  with their job links. Each of those folders' open issues gets one line pointing at it, so
  the folder's session knows its reds are covered there. A folder with no open issue gets
  none; the cross-folder issue already names it.
- A deviation from documented behavior gets its own record per `<deviation-note>` in
  `<deviation-records>`, never an issue. The records land on a branch of their own, like the
  pull requests below, never the sweep branch.
- A spec whose run hit the budget with no failures, from step 4 or after its step 5 rerun,
  gets one issue of its own through the `create-issue` skill proposing the split, never a line
  on a data or skip issue. Search for an open split proposal on the spec first and append the
  sweep's job link to it when there is one. The body carries what the budget rule in
  `<run-watch>` asks of a split proposal, plus the run's runtime, the titles it never ran, and
  the titles it cut off, which the rerun list names for the spec. A budget hit step 4 traced
  to a discovery walk is filed instead through the `create-issue` skill against the spec,
  appending to the folder's open issue when there is one, with the walk's lines.
- A sweep does not fix specs. Fixes happen in those issues. Findings outside the sweep go
  per `<follow-up-note>`.

Every issue a sweep files carries the labels `<issue-labels>` sets, and goes into the cleanup
milestone of the sweep's round, which `<issue-labels>` says how to find. The round is the
sweep issue's own milestone. An open issue a finding is appended to takes the milestone too
when it has none, and keeps the one it has otherwise. With no sweep milestone on the sweep
issue, or no open cleanup milestone to match it, the issues are filed with no milestone, and
step 9 names them for the user rather than a milestone being created.

## 8. Write it up

The counts come from the run logs, through `<sweep-report>`, never from a hand tally. Leave
out the rerun directory when step 5 was skipped. It prints the totals table against the
project's current `<sweep-log>` line, the by-folder table, the excluded and pre-skipped
specs, and the project's new log line with its note term, ready for the cause after the
colon. A failed title that passed or went flaky on its rerun counts as flaky, and a never-ran
or cut-off title takes what its rerun reported. When the sweep cannot have a line, it prints
why instead and fails.

The write-up carries:

- A totals table, before, after and change: spec files, tests, passed, failed, flaky,
  skipped, and the pass rate with and without skips.
- A by-folder table with the same columns.
- New failures first, each with its job link, test case ID (when the repository keeps one), error, and the call on its cause.
- A shorter section for known failures, each with its issue link.
- Skips as findings, with the reason each one gave.
- Every run that hit the budget, named with its step 4 case: with failures, and what its rerun
  showed; no failures, with the split proposal's link; or a discovery walk, with the link to
  the issue that holds the walk's lines.
- The specs the project excludes, listed as excluded on that project rather than as red runs,
  and left out of the spec file count. One whose reason says the file does not exist is a
  wrong line in the spec list, not an exclusion.
- The pre-skipped specs, each with what it needs, in a section of their own apart from the
  runtime skips, and left out of the spec file count and the log counts like the excluded
  ones.

When the sweep completed, every spec dispatched and every run tallied, write its line to
`<sweep-log>`, which holds only the latest sweep of each project, following the line shape,
note terms, and rules it sets. A sweep that was cancelled, cut off, or left specs unsent gets
no line, and neither does one missing any count, and the project's earlier line stays. The
log carries the counts and nothing that names the issue or its runs. It lands through a pull
request of its own, as the next section describes, never on the sweep branch.

When the issue asks for `<report-document>`, build it as that note says.

## Pull requests opened during a sweep

A sweep often turns up a fix worth making on the side: the driver, a skill, a shared script.
Each one goes on its own branch from `<default-branch>`, never the sweep branch, whose head
the driver pins. It runs `<branch-age-note>` before the pull request opens, since a sweep can
outlast a day of the default branch. Once it is open, the session reviews it, with
`<pr-checks>` running beside the review, per `<self-review>`, then sends the ready signal in
the turn that review ends, per `<ready-signal>`, even though the sweep is still going.

Record it in a ledger of its own, not the driver's, per `<run-watch>`: the driver counts every
open row in its ledger as a slot, so a pull request row there would hold a dispatch back. Keep
one watcher on that ledger in the background. On the merge, run the after-merge steps.

## 9. Close out

Report the issue link, the counts, the new failures with their issue links, and any spec that
never produced a tally. Read back the milestone and labels of every issue step 7 filed or
appended to, and fix any that lack the labels or the cleanup milestone `<issue-labels>`
requires before reporting:

```bash
gh issue view <n> --json number,milestone,labels \
  --jq '"\(.number) \(.milestone.title // "no milestone") [\([.labels[].name] | join(", "))]"'
```

The report lists each one with that line. Remove `<in-progress-label>` only once the write-up has
been sent and the issue's acceptance criteria are checked, with the read-back
`<labels-note>` requires.
