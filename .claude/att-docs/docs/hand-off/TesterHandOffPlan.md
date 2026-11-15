# Tester hand-off on a failed test: plan

Status: **proposed, awaiting review** (issue 3276). Nothing here is built yet.

This plan lives in this repository because it is about the harness on this side:
the `Playwright Debug (on demand)` workflow, the runners, and the session
tooling. The code it leads to ships to the work side like any other code under
`src/`, so the comments and log strings in that code follow the usual
shipped-text rules even though this file does not have to.

## What the RPG Club bot runner does, and what carries over

The bot repo's `scripts/conduct-playwright/run.ts` drives a test plan in a
headed, persistent Chrome profile. When a step fails (a `HandOff` error or any
`TimeoutError`), it prints `Step N is yours`, stops touching the page, polls the
page once a second for up to 15 minutes for a sign the human finished, then
carries on at the next step. It runs locally only, never headless, never in CI.

Three things differ here and shape everything below:

1. **A failed step ends the test body.** A Playwright spec is one `async`
   function. Once an `expect` or a locator action throws, the body has unwound,
   and nothing short of editing every spec can resume it at the next
   `test.step`. The bot runner can carry on because it interprets a plan step by
   step; our specs are code.
2. **Runs happen on runner services, not at a desk.** The six Linux runners are
   system services on the Hyper-V guest with no display. A headed run there
   needs the guest's desktop, reached over remote login, per
   [LinuxRunnerMigration.md](../runners/LinuxRunnerMigration.md). The Windows runner sits on the work laptop.
3. **Accounts are leased.** A test that waits holds its account the whole time,
   and other jobs queue behind it.

So the useful part to carry over is the hold, not the resume: keep the failed
page alive and in front of a person, with a deadline, and fail the test
honestly afterward.

## The recommendation in one paragraph

Add an opt-in **hand-off fixture** to the base `test` in
`src/_base/fixtures/userFixtures.ts`. When
hand-off is on and a test fails, the fixture's teardown takes a screenshot,
logs which test and step failed and why, injects a small banner with two
buttons into the failed page, and waits for a bounded time. Either button,
closing the page, or the deadline ends the wait. The test then **fails as it
would have anyway**, with the tester's verdict recorded as an annotation. Turn
it on with `PW_HAND_OFF=1` locally first; a `hand_off` input on the debug
workflow comes second, once the way to see a runner's browser is settled.
Every other workflow, and every debug dispatch that did not ask for it, is
refused by the gate.

## How it is turned on, and how it stays off everywhere else

Two switches, one gate.

- **Local:** `PW_HAND_OFF=1` in the shell (or `.env`) for an
  `npx playwright test` run started from a desktop terminal, on the work laptop
  or on the Linux guest's desktop.
- **Debug workflow (phase 3):** a boolean input `hand_off`, default `false`.
  The workflow has 22 inputs today and GitHub allows 25, so it fits, with one
  input to spare beside a `hand_off_minutes` input.

The gate is one exported helper (`handOffEnabled()` in a new
`src/_base/global/handOff.ts`), so the config and the fixture read the same
answer. Where the switch is read from depends on where the run is:

| Where | The switch is | What it keeps out |
| --- | --- | --- |
| `TF_BUILD` set | never on | the AZDO pipelines, whatever their variable group says |
| `GITHUB_ACTIONS` set | on only when the dispatch payload at `GITHUB_EVENT_PATH` carries `inputs.hand_off` as the string `"true"` (dispatch inputs arrive as strings); `PW_HAND_OFF` is not read at all | every workflow but the debug one (their payloads carry no such input), and every debug dispatch that did not tick the box: sweeps, folder runs, and every session's scoped rerun go through the debug workflow too, so a stray `PW_HAND_OFF` in a runner's `.env` must count for nothing there. The runner writes the payload file per job, and no `.env` reaches it |
| neither | `PW_HAND_OFF` is `1` | local runs that did not ask for it |

When the switch is set but the gate refuses, the config logs one line naming
the condition that failed (`Hand-off: refused, TF_BUILD is set`) and the run
goes on exactly as it does now. When the gate passes, it logs
`Hand-off: on, wait up to N min per failure` once at startup.

### Retries, workers, and repeats

The debug workflow passes `--retries`, `--workers`, and `--repeat-each` on the
command line every time, and command line flags override the config, so the
config cannot force these. Two checks instead:

- The workflow refuses `hand_off=true` up front, as a named error before
  Playwright starts, unless `retries` is `0`, `workers` is `1`, and
  `repeat_each` is `1`. Folder runs (`whole_suite`) are refused the same way.
- The fixture reads the resolved values from `testInfo.project.retries`,
  `testInfo.config.workers`, and `testInfo.project.repeatEach`, and declines to
  hold when any of them is above the single-run value, with a log line naming
  which one. That covers a local run started with `--retries=1` too.

A retry would restart the worker and re-run the test while the tester is
looking at the first attempt, and would write the test's records into UAT
twice. Several workers or repeats are sweeps and flake hunts, which nobody
watches test by test.

On the session side, `scripts/dispatch.sh` gets no flag for it. Unattended
sessions (`/oversee-development`, `/sweep-suite`, scoped reruns from
`/implement` and `/debug-spec`) dispatch only through that script, so they
cannot send `hand_off=true` without someone editing the script. The skills'
shared docs say the input is for a person watching and never for a session.

## What happens on a failure

With hand-off on, the config also changes these for that run only. The debug
workflow passes neither `--max-failures` nor `--headed`, so those two config
values hold there:

- `retries: 0`, as the default for a plain local run. The checks above catch
  a command line that says otherwise.
- `maxFailures: 1`. Only the first failure is handed off; the run stops after
  it, which also keeps the wait inside one test's worth of budget.
- `headless: false` for a local run. On a runner job, see "Seeing a runner's
  browser" below.

Then, in the hand-off fixture's teardown (it depends on the worker-scoped
`user`, so the failed page is still open when teardown runs):

1. `testInfo.status` is not `expectedStatus` and not `skipped`. Anything else
   returns at once, so a passing test pays nothing.
2. Extend the test's own deadline by the wait cap with
   `testInfo.setTimeout(testInfo.timeout + waitMs)`, since teardown time counts
   against the test timeout. A test that failed by timing out gets a separate
   teardown slot from Playwright; whether the extension reaches that slot is
   open question 3.
3. Take `hand-off-start.png` of every open page and attach it.
4. Log the hand-off line (see "What gets recorded").
5. Show the banner: the failed step and the first line of the error, plus
   **Step works by hand** and **Confirmed broken** buttons. The binding goes on
   the context (`context.exposeBinding`) and the banner script on
   `context.addInitScript`, then is evaluated once into the open pages. Working
   the step by hand means navigating, and a banner evaluated into one page only
   would vanish at the first reload or link, leaving the deadline as the only
   way out. The binding resolves the wait.
6. Wait for the first of: a button, the page closing, or the deadline. Poll
   once a second so a closed page or a crashed browser ends the wait promptly.
7. Take `hand-off-end.png`, add the `hand-off` annotation, log the end line.

### `page.pause()` and the Inspector, against a custom wait

| | `page.pause()` / Inspector | Custom wait (recommended) |
| --- | --- | --- |
| Needs a display | yes, the Inspector is a window | no; the banner rides in the page, so any way of viewing the page works |
| Deadline | none; it waits until Resume | bounded, and logged |
| Tester away from the screen | the run sits until `globalTimeout` kills it and the leases ride out to expiry | the wait times out, the test fails, `maxFailures: 1` ends the run, global teardown frees the leases |
| Records a verdict | no | yes, the button pressed |
| Lets the tester step through locators | yes, its real strength | no; the trace viewer covers it after the fact |

On a runner on the work laptop, where the tester may or may not be watching,
the deadline decides it: the custom wait. `page.pause()` stays the right tool
for a local `--debug` session, which already works without any of this.

## What happens after the tester acts

The test fails, every time. The three options the issue names come out as:

- **Rerun the failed step:** not offered. The body has already unwound, and
  re-driving one step out of context would report a result for a state the
  test never reached on its own. A rerun is a fresh run of the test.
- **Continue to the next step:** not offered, for the same reason. The tester
  is free to continue by hand in the open page, which is the point of the
  hold, but the automation does not pick up again.
- **Fail with the evidence:** always. The verdict goes into the annotation, so
  the report and the results row say which of these it was:
  `hand-off: step works by hand`, which points at the test,
  `hand-off: confirmed broken`, which points at the app, or
  `hand-off: no answer in N min`.

A pass the automation did not earn cannot come out of this, because nothing in
the fixture ever changes the test's status.

## Fitting the budget, timeouts, and leases

- **Run budget.** `DEFAULT_RUN_BUDGET_MS` is 20 minutes, applied as
  `globalTimeout`. With hand-off on and `maxFailures: 1` there is at most one
  wait per run, so the config raises `globalTimeout` by exactly the wait cap and
  logs the sum (`run budget 20 min + 10 min hand-off`). The 20 minutes the tests
  get is unchanged.
- **Wait cap.** A new `HAND_OFF_WAIT_MS` in `waits.ts`, default 10 minutes,
  overridable through `PW_HAND_OFF_MINUTES` and capped at 15. A job queued on
  the same account gives up after `LEASE_ACQUIRE_TIMEOUT_MS` (10 minutes). A
  job that queued while the failed test was still running waits for the rest of
  that test plus the hold, so any hold can push it past that limit. Ten minutes
  only keeps the hold alone from exceeding it, and a hand-off run is best
  started when no other job needs the account.
- **Test timeouts.** Specs set their own (`test.setTimeout`, `test.slow`). The
  fixture extends whatever the test ended up with by the cap, rather than
  touching any constant, so no spec changes.
- **Job timeout.** The debug workflow's `timeout_minutes` defaults to 60, which
  already covers 20 plus 15.
- **Leases.** The lease heartbeat runs every 15 seconds in the worker process,
  so a waiting test keeps its account, which is what it needs for the tester
  to look at a signed-in page. The cost is that another job wanting that account
  waits. The start log line names the leased account so whoever holds the
  queue knows why. Fixture teardown does not release leases; global teardown,
  the worker's `beforeExit`, and the reporter on an interrupted run do. With
  `maxFailures: 1` the run ends right after the wait, so those free the account
  the usual way and nothing new is needed.

## Seeing a runner's browser

The repo settles this part least of all, so it is phased last. Open
questions 1 and 2 are about it; question 3 is about the hold itself and is
settled earlier, in phase 2.

- **Local run, phase 2:** headed on the desktop where the terminal is. Works
  today on the work laptop and on the Linux guest's desktop.
- **Linux runner job, phase 3:** the runner service has no display. The two
  candidates:
  - Chromium remote debugging. Launch with `--remote-debugging-port` on the
    guest's loopback address, and have the tester forward it from the laptop
    with `ssh -L`, the same way the guest is already driven. Then
    `chrome://inspect` in Chrome on the laptop shows the screencast, and the
    banner can be clicked through it. Loopback plus a tunnel avoids relying on
    `--remote-debugging-address`, which Chromium honors only in some headless
    modes, and opens no port on the guest's firewall. This is headless and
    chromium-only, and whether the port coexists with Playwright's own pipe
    connection is the first thing phase 3 proves (open question 2).
  - Xvfb plus a VNC server, installed with apt on the guest. The tester connects
    with a VNC client. This covers every engine, at the cost of two more
    services to keep running.
  Recommendation: remote debugging first, since most debugging dispatches are
  `*.chromium` and it adds no service. The workflow then refuses `hand_off` on a
  non-chromium project, and on `runner=Windows` until the open question below is
  answered.

## What gets recorded

- **Log lines**, three in all, through `console.log` so the run log carries
  them, in the order they appear:
  - `Hand-off: failed step "<step title>"` (from the reporter, see below)
  - `Hand-off: <title path> failed at <file:line>: <first error line>.`
    `Waiting up to 10 min (account test4).` (from the fixture)
  - `Hand-off: ended after 3m12s, tester says step works by hand.`
- **Screenshots** `hand-off-start.png` and `hand-off-end.png`, attached to the
  test, so they land in `test-results` and on the share with everything else.
- **Trace.** `retain-on-failure` already keeps it. The open question below asks
  whether a trace stopped at test end includes the teardown wait.
- **Annotation** `hand-off` with the verdict and wait time. `CustomReporter`
  copies it into the results row so `catchup.py results` can show it.

The step title is the awkward part: the worker has no public API for the step
that was running. The plan's answer is the error location (`file:line`) from
`testInfo.errors[0]`, which every failure has, with the step title added by the
reporter, which sees `onStepEnd` with the error. That event arrives as the step
fails, before fixture teardown starts, so the reporter's line comes just ahead
of the fixture's.

## Files a build would touch

| File | Change |
| --- | --- |
| `playwright.config.ts` | read the gate; when on: `retries` 0, `maxFailures` 1, `globalTimeout` plus the cap, `headless` false locally, the startup log line |
| `src/_base/global/waits.ts` | `HAND_OFF_WAIT_MS`, its env override and cap |
| `src/_base/global/handOff.ts` (new) | `handOffEnabled()` gate and its refusal reasons, shared by config and fixture |
| `src/_base/fixtures/handOff.ts` (new) | the teardown hold: resolved retries, workers, and repeat check, screenshots, context-level banner, wait loop, annotation |
| `src/_base/fixtures/userFixtures.ts` | register the auto fixture |
| `src/_base/fixtures/CustomReporter.ts` | step title on the hand-off line; annotation into the results row |
| `.github/workflows/playwright-debug-on-demand.yml` | phase 3: `hand_off` and `hand_off_minutes` inputs, refusal for non-chromium, Windows, retries, workers, repeats, and folder runs; the loopback debugging port |
| `.claude/skills/_shared/*` | one line: `hand_off` is for a person watching, never a session |
| `eslint-local-rules/` | possibly a rule refusing `page.pause()` in committed specs, so the hand-off stays the only hold |

Nothing under `pipelines/` changes; the `TF_BUILD` condition keeps the AZDO
pipelines out without touching their YAML.

## Follow-up issues

To be filed once the plan is approved, each with the usual criteria: the named
specs green through `Playwright Debug (on demand)` with `workers=1` and
`retries=1`, plus a run without the option that matches the previous run's
results and log line for line apart from timings.

1. **[Tooling] gate and config.** `handOffEnabled()`, the refusal log lines,
   `HAND_OFF_WAIT_MS`, and the config changes, with unit tests in
   `_unit-tests` for every row of the gate table, including a runner job whose
   `.env` sets `PW_HAND_OFF` and whose payload does not. No fixture yet, so a
   run with the switch set behaves as now apart from retries, maxFailures, and
   budget.
2. **[Tooling] the hand-off fixture, local only.** The teardown hold, the
   resolved retries, workers, and repeat check, the context-level banner,
   screenshots, annotation, reporter line. Proven by hand on one local headed
   run of a spec forced to fail, with one navigation during the wait, and by
   one dispatch without the option.
3. **[Tooling] debug workflow input.** The inputs, the up-front refusal of
   `retries`, `workers`, `repeat_each`, and `whole_suite` values above the
   single-run ones, and the runner viewing method chosen from the open
   questions, chromium on Linux first.

## Open questions

1. **Is the Windows runner a service or an interactive `run.cmd`?** Nothing in
   the repo says. As a service it runs in session 0 and cannot show a window on
   the laptop's desktop, which rules out headed there.
2. **Does a remote debugging port work beside Playwright's own connection?**
   Playwright drives Chromium over a pipe and adds its own launch flags. Adding
   `--remote-debugging-port` through `launchOptions.args` has to be proven to
   leave the pipe working and to show the page in `chrome://inspect` through
   the SSH tunnel. If it does not, Xvfb plus VNC is the fallback.
3. **Does the retained trace cover the teardown wait, and does the extended
   timeout reach a timed-out test's teardown?** If tracing stops before
   fixture teardown, the trace shows the failure but not what the tester did
   afterward, and the end screenshot is the only record of that. If the
   extension does not reach the separate teardown slot a timed-out test gets,
   timeouts (the most common failure) need the hold moved to a worker-scoped
   fixture or a reporter-driven pause instead. Phase 2 settles both on its
   first local run.
4. **Is ten minutes the right default?** It is set by the lease acquire limit,
   not by how long a tester needs. Fifteen, as the bot repo uses, would push a
   queued job past its acquire limit.
5. **Is resuming worth a `test.step` wrapper later?** Each suite extends the
   base `test` again, so wrapping `step` once in the base does not reach the
   suites' `test` objects. Resuming at the next step would mean wrapping `step`
   in each suite fixture and catching inside it, which changes what a failed
   step means for every spec. This plan leaves that out.
