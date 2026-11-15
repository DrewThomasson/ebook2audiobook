---
name: debug-spec
description: >-
  Diagnose and fix a failing or flaky test spec through an issue-first workflow: file a
  tracking issue, fix the root cause on a branch, verify the fix with title-scoped test
  runs, then open a linked pull request and review it. Use when asked to stabilize,
  diagnose, or fix a broken or flaky spec.
---

# Debug Spec

No test runs when a pull request opens. `<pr-checks>` run static checks and nothing else,
so opening one verifies no runtime behavior. The only runtime check is a `<test-dispatch>`
run this session makes itself in section 5, and the fix is green there before the pull
request opens. Never run tests locally; run them only the way `<test-dispatch>` runs them.
Every question this skill puts to the user goes through `AskUserQuestion`,
per `<asking-note>`.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the
rules around it still hold. `<worktree-script>` is the exception; without it, cut the
branch with plain `git` from a freshly fetched `<default-branch>`.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing issue bodies, commit messages, and pull request bodies to a command as files |
| `<default-branch>` | The branch fixes start from and merge into |
| `<branch-types>` | The branch type prefixes the history uses; a fix takes the one for a defect fix |
| `<worktree-script>` | The command or tool that cuts a branch and its worktree from a freshly fetched default branch |
| `<test-config>` | Where a spec's test project is resolved, and the project a failing spec runs under |
| `<test-dispatch>` | How a test run is sent: the runner, the dispatch command, its defaults, and how a run is cancelled |
| `<test-run-rules>` | The mechanics of a run: the ref to test, the title filter and how to anchor it, the runner choice, the retry default, repeat runs, and the flags for a whole-spec run |
| `<run-watch>` | The ledger and the one watcher that report runs and pull requests |
| `<artifact-read>` | How a run's output and a failed test's snapshot are read |
| `<failure-snapshot>` | The per-test file that shows the page at the moment a test failed |
| `<flake-report>` | The command that lists titles that both passed and failed on one commit, within a run or across runs, with the arguments it takes for the project and the commit; or `none` |
| `<baseline-rules>` | How the default branch's recorded results are read, and how a baseline branch is built |
| `<investigation-log>` | The skill or file that records what each red run settled |
| `<fix-cycle-budget>` | How many fix cycles a test gets, what a cycle owes, and what is handed over when the budget runs out |
| `<test-accounts>` | The document that lists test accounts, and the note that keeps it current |
| `<discovery-rules>` | The rules for test data discovery: hints, query shape, helper layout, probe paths, and what a scratch probe is exempt from |
| `<skip-ledger>` | The ledger of parked tests and the rule for moving a row |
| `<sampling-note>` | How a shared edit is verified by a sample of its consumers |
| `<deviation-note>` | The deviation gate: what counts, where the documented behavior is read from, the check for one already recorded, the record's shape, and the narrowing of the assertion |
| `<deviation-records>` | Where a spec-versus-app deviation is recorded and the state a new record starts in |
| `<follow-up-note>` | How findings outside the spec are filed as issues |
| `<static-checks>` | The static-check commands, what each one gates, and the final pass |
| `<writing-rules>` | The gate for comments, skip reasons, and log strings that ship |
| `<repo-constraints>` | The coding constraints every change follows, such as line length and banned APIs |
| `<branch-age-note>` | The note on refreshing an old branch before a run or a pull request |
| `<mergeability-note>` | The note on reading and resolving a pull request's mergeable state |
| `<pr-checks>` | The checks a pull request runs when it opens |
| `<self-review>` | The self review procedure: its loop, minor findings, and settled decisions |
| `<ready-signal>` | The ready signal: its wording, its label, and when it is withheld |

## 1. Establish evidence

- Resolve the target spec and the project it runs under from `<test-config>`.
- Read the errors the user supplied, the failed run's concise log, and its output
  (`<artifact-read>` says how) before editing.
- Report only directly observed failures. Do not invent error text, line numbers,
  retries, or root causes when the output is unavailable.

## 2. Create the tracking issue

Create the issue before branching or editing, unless the user supplied an existing one.
Use the GitHub connector when one is available, and the authenticated `gh` otherwise.

The title, area label, kind label, and body sections follow the `create-issue` skill. Do
not invent a title shape here, and use the defect kind label. The body goes in a
scratchpad file written with the Write tool, per `<shell-text-note>`:

```bash
gh issue create --title "<title per create-issue>" \
  --label "<area label>" --label "<kind label>" --body-file <scratchpad>/issue-body.md
```

The issue includes:

- the target spec and the failing test names, when known
- the observed failure and the evidence URL
- the investigation scope
- the expected stable behavior
- acceptance criteria, including the failing titles passing on a scoped run without
  retries

Use the issue number in the branch name, `<type>/issue-<number>-<short-description>`, with
`<type>` the defect-fix prefix from `<branch-types>`.

## 3. Diagnose and fix

Cut the branch from the current `<default-branch>` with `<worktree-script>`. Preserve
unrelated user changes. Inspect the target spec, its page objects, helpers, and the
relevant setup only.

When the failure turns on the account the spec signs in with, read that account's section
in `<test-accounts>` first, and write what the diagnosis settled back into it in this
pull request, per that note.

Prefer root-cause fixes:

- an observable URL, element, row, or confirmation state
- deterministic selectors
- explicit synchronization on a meaningful state
- isolated test data and cleanup

A fix that adds or touches a discovery lookup follows `<discovery-rules>`. That
conversion is part of the fix, not an unrelated refactor, and a skip needs the user's
answer through `AskUserQuestion`. A skip that parks the test on every run, and a fix that
lifts one, moves its row in `<skip-ledger>`. A scratch probe the investigation takes back
out before the pull request is exempt, per `<discovery-rules>`.

A lookup the run log shows turning candidates down is fixed with the rest of the spec,
per `<discovery-rules>`. A spec that is slow or flaky because its discovery walks is not
fixed by a longer timeout.

Do not add blind waits, timeout increases, retries, or unrelated refactors. Something
worth fixing outside this spec goes on the tracker and the fix carries on, per
`<follow-up-note>`. Add or update focused regression coverage in the target spec when
the behavior can be asserted meaningfully.

Validate before publication. Run the per-fix checks in `<static-checks>`. That note is
the only copy of the commands, and it says what each one gates and which checks wait for
the final pass, including the `<writing-rules>` gate over every comment, skip reason, and
log string the fix added.

Reread the modified lines against `<repo-constraints>`.

## 4. File spec-versus-app deviations

This is a gate, not advice. When a run proves the app does not do what its functional spec
or business rule says, that deviation is recorded before the pull request opens. A
deviation left in a code comment or in the conversation is a deviation nobody reports.

`<deviation-note>` is the gate. Follow it as written; nothing in this section overrides
it.

What this section adds: each deviation gets its own record in `<deviation-records>`,
never an entry on the tracking issue from section 2, and every record written or amended
is listed by path in the pull request body and in the section 7 report.

## 5. Verify with scoped runs

The run rules are the ones the `implement` skill sets in its step 6, "Run the affected
tests yourself", from "Branch age gate" through "The scoped-rerun gate" and "Fix cycles
on a family", plus its "The baseline gate" and "The final full run". Follow them as
written, and link and watch every run per `<run-watch>`. Commit and push the fix first,
since a run tests the pushed ref. The dispatch is one per touched spec, through
`<test-dispatch>`, with the flags `<test-run-rules>` sets:

- Test the branch's pushed ref every time. A run without it executes the default branch,
  matches no tests, and goes red.
- The title filter matches the titles that failed and nothing else.
- Keep the default runner unless `<test-run-rules>` names a reason to change it, and say
  why in the report when it changes.
- One retry is the default. It says whether a red test is flaky (passes on retry) or
  failing (fails twice), and both need a fix. Zero retries go only with a repeat-each run.

The one exception to the title filter is a failure that depends on test order: a title
that fails in the full run and passes alone, because an earlier test leaves the state it
trips on. A scoped rerun cannot reproduce it, so once a filtered run has shown the title
green alone, redispatch the whole spec without the filter, pass the reason
`<test-run-rules>` asks for, and say in the report why a full run was needed.

A fix that edits a shared fixture, page object, or helper is verified on this spec plus a
sample of one to three other consumers, never on every consumer, per `<sampling-note>`.
This skill never starts a suite or folder sweep; the unrun consumers go in the pull
request body and the report as the user's call.

For a failure, read the run's output before editing, per `<artifact-read>`.
`<failure-snapshot>` holds the page's state at the moment of failure: which controls
existed, what a message said, whether the form had rendered. Diagnose from it, fix on the
same branch, push, and dispatch again scoped to the titles still failing. After each
diagnosis, update the record per `<investigation-log>` so findings survive the session.
The dispatch budget for one test is in `<fix-cycle-budget>`: when it runs out, hand over
the defect chain that note describes instead of guessing at another cycle.

Read the shape of the failing set before rerunning anything. When every test in the run
ends on the same per-test timeout, or every one fails on the same first assertion, one
cause is holding the whole file: a landing wait, a hook, a select that never populates.
That run has already said so. Do not rerun it, and do not raise the per-test timeout or
the run budget, because nothing ran slowly; the page never reached the state the first
assertion waits on. Read one test's `<failure-snapshot>`, fix the shared cause, then run
one representative title under the filter. The rest of the file follows it.

For an intermittent failure, meaning a failing set that changes between attempts, read the
recorded results before dispatching anything. When `<flake-report>` names a command, run
it for the failing project and the red run's commit, with the arguments it takes. It lists
the titles that both passed and failed on that commit. A title that failed and
then passed on retry shows there with no new dispatch, and that is the proof it flakes.
Hunt it with a repeat-each dispatch of the failing titles under the filter, with zero
retries, only when the fix needs it reproduced under new diagnostics. Never rerun a
finished run to find out. Treat retry or flaky evidence as failure even when the final
conclusion is green.

A failure that may predate the branch goes through the baseline gate in the `implement`
skill's step 6, which asks the recorded results per `<baseline-rules>` before any
dispatch against the default branch.

Once the scoped runs are green, one full-spec dispatch without the filter confirms the
whole file, as the `implement` skill's step 6 sets out. It carries the reason
`<test-run-rules>` asks for: after a red whole run, the titles now green under the filter;
after a green whole run, that this is the final run. If the fix changed nothing a spec loads, no dispatch runs; say so in the report.

## 6. Open the issue-linked pull request

Only publish once section 5 is green and the static validation is complete. The commit
message and the pull request body go through scratchpad files, per `<shell-text-note>`.

1. Stage only the intended files, by name.
2. Commit the root-cause fix.
3. Run `<branch-age-note>` and follow it. When it fires, its merge reruns the static
   validation and pushes the branch.
4. Push the issue branch, if step 3 did not.
5. Open a non-draft pull request with `Closes #<issue-number>`.
6. Explain the observed cause, the fix, the impact, and the validation: each spec,
   project, run link, and result from section 5.
7. Read the pull request's mergeable state and resolve any conflict without being asked,
   per `<mergeability-note>`, before reporting the pull request at all.
8. Review the pull request yourself, per `<self-review>`, with `<pr-checks>` running
   beside the review. Fixes it makes owe a scoped section 5 dispatch when they touch
   spec-loaded code.

## 7. Complete

Update the issue with the pull request URL and the final validation result. Do not merge.
Report:

- the issue and pull request URLs
- the root cause and the fix
- the static checks
- the exact runtime result, project, failures, and reruns
- the deviation records written or amended, by path
- how many self review passes ran, and what they found and fixed
- anything not verified

End the report with the ready signal from `<ready-signal>` once the self review loop ends,
on a pass with no real bug or after the last allowed pass's fixes, per `<self-review>`.
