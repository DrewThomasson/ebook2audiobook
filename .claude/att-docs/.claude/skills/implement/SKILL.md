---
name: implement
description: >-
  Implement a GitHub issue in Overmind end to end: read it, label it `In Progress`,
  work it in an isolated worktree, run the affected test files locally, open a linked
  pull request, review that pull request itself, then hand it to the user. Use when
  asked to implement, work on, pick up, or start an Overmind issue by number.
---

# Implement

## Applies to every pull request

This procedure is the standard for every pull request here, including documentation,
script and skill changes that start from no issue and sessions that were never asked to
implement one. `CLAUDE.md` at the root says so for every session.

A change with no issue skips the steps that need one: reading and claiming it, `issue-<N>`
in the branch name, `(#<N>)` in the title, `Closes #<N>`, the `Blocked` label on the
issue, and closing it after the merge. Name the branch `<type>/<slug>`, and treat the
folders from the `<ownership-unit>` row that hold the files the change touches as the
ownership unit when reading the board. The worktree (Section 3), the non-draft pull
request, the self review loop, and the `Manual Review Needed` label (Section 7) hold for
every pull request.

In this repository `/implement` is this full pull-request procedure: it builds code
changes with the `tdd` skill (see Test seams) and reviews every change with the
`code-review` skill (Section 7, Self review).

Exception to the non-draft rule above and the general skill's non-draft rule: a pull
request opened by the `implement-spec` skill (a user-scope skill that builds a whole
spec's issues on one integration branch) may stay a draft while its issues land. Its own
step 8 does not mark it ready: once its `code-review` pass ends, it goes through the
Section 7 self review loop, checks and the `Manual Review Needed` label, and Section 7
marks it ready. Its body has one `Closes #<N>` line per issue it closes.

## Harness substitutes

This procedure names tools that belong to one harness. When the harness lacks one, use
the substitute, and record each substitution in the pull request body under Judgment
calls, naming the tool missing and the substitute used:

| Tool named here | Substitute when it is absent |
| --- | --- |
| `EnterWorktree` | The Git fallback under Overrides, Section 3: a worktree at `.claude/worktrees/<name>` from `origin/main`. `.claude/worktrees/` is the one folder inside the main checkout that the main-checkout guard exempts |
| `AskUserQuestion` | The harness's own ask tool, with the same rule: never ask only in reply text |
| The Skill tool | Read the skill by its path under `.claude/skills/` or `plugins/*/skills/`, or by its `skill://<name>` URL, and follow it |
| `session_title.py` | Skip the session title and status when the script is absent; the rename never gates the work |
| `ListAgents` | Decide whether another session holds a unit or a pull request from the sources Section 3 lists: the issue's `In Progress` label, the open pull requests and their files, the oversee ledger and the file claims |

## Base

Read [the general skill](../../../plugins/general/skills/implement/SKILL.md), which lives in this repository rather than in a vendored copy, first and follow it, except where this file overrides it.

## Paths

**Every question to the user goes through the `AskUserQuestion` tool, or its substitute under
Harness substitutes. Never ask only in reply text: the user does not see it there.**

| Placeholder | Value here |
| --- | --- |
| `<asking-note>` | Every question goes through the `AskUserQuestion` tool, never only in reply text, because the user will not see it there. Without that tool, the harness's own ask tool, under Harness substitutes |
| `<in-progress-label>` | `In Progress` |
| `<ready-label>` | `Manual Review Needed` |
| `<preflight>` | In the main checkout: `node --version`, `python3 --version`, `gh --version` and `gh auth status` must succeed, and a change whose tests import `dotenv` also needs `node -e "require.resolve('dotenv')"` to succeed. On a failure, label the issue `Blocked` and comment with the failed command and its exact fix: `apt install nodejs` or `apt install python3` for a missing tool, GitHub's official apt repository with its signing key for a missing `gh`, `gh auth login` for authentication, `npm install` in the main checkout for `dotenv` |
| `<label-script>` | None. Under Overrides, Labels |
| `<labels-note>` | Under Overrides, Labels |
| `<area-label-rule>` | A title starting `[Tooling]` carries the `Tooling` label; add it when missing, under the same gate |
| `<reference-docs>` | `README.md` and `docs/` |
| `<ownership-unit>` | The folder the issue names: `plugins/<group>/skills/<name>/`, `plugins/<group>/hooks/`, or a root file |
| `<ownership-rules>` | Under Overrides, Section 3 |
| `<claim-script>` | `python3 plugins/general/skills/implement/claims.py`, under Overrides, Section 3 |
| `<main-checkout>` | `~/Code/Overmind`, read-only |
| `<worktree-script>` | `EnterWorktree` when available; otherwise the Git fallback under Overrides, Section 3, which cuts the worktree at `.claude/worktrees/<name>` from `origin/main` (see Harness substitutes) |
| `<edit-guard>` | The harness worktree guard when available; isolation is required without it, under Overrides, Section 3. The main-checkout guard exempts only `.claude/worktrees/`, so a fallback worktree goes there |
| `<dependency-setup>` | `package.json` needs only `dotenv`. There is no lockfile, so run `npm install` in the worktree when a test imports it. `node_modules` is gitignored |
| `<shell-text-note>` | Under Overrides, Section 3 |
| `<branch-types>` | `feat`, `fix`, `chore`, `docs`, `ci` |
| `<default-branch>` | `main`. Never merge, except a pin-only pull request under Added gates, Post-merge pin; never push to `main`, never force-push |
| `<follow-up-note>` | `gh issue create` in `merph518/Overmind`. When a write is refused, put the text in the pull request body under `Follow-ups` |
| `<sampling-note>` | Not applicable here, because nothing is dispatched; Section 6 below runs every affected test file |
| `<writing-rules>` | `repo-writing`, under Added gates |
| `<repo-constraints>` | None beyond the writing rules and the README rule under Repository notes |
| `<static-checks>` | Local checks, under Overrides, Section 5 |
| `<pr-checks>` | The `test-all` job in `.github/workflows/ci.yml` runs every test and the static checks on a pull request and again on each push to its branch. The ready signal waits for it, under Overrides, Section 7, Ready signal. This replaces the general skill's wording that a pull request check runs static checks only: the local runs in Section 6 still go green before the pull request opens |
| `<test-dispatch>` | Not applicable here, because nothing is dispatched. Tests run locally, under Overrides, Section 6 |
| `<branch-age-note>` | Before opening the pull request and before marking it ready, merge `origin/main` into the branch when it is behind, and as soon as `<claim-script> sync` prints a file. Never rebase, and never force-push |
| `<run-watch>` | No run watcher, because nothing is dispatched. After the ready signal, wait for the merge with a background command that has no command substitution: `until gh pr view <n> --json state --jq .state | grep -qvx OPEN; do sleep 120; done; gh pr view <n> --json state --jq .state`. When working under `oversee-development`, record the opened pull request on its ledger with `bash plugins/general/skills/oversee-development/oversee.sh finish <N> done <pr> "<note>"`, where `<pr>` is the pull request number. Outside it, only that wait |
| `<fix-cycle-budget>` | Three cycles on one failure, then record it on the issue and stop |
| `<mergeability-note>` | Under Overrides, Section 7 |
| `<self-review>` | Under Overrides, Section 7 |
| `<ready-signal>` | Under Overrides, Section 7, Ready signal. A pull request reported ready carries `Manual Review Needed`, read back |
| `<instructions-file>` | `CLAUDE.md` at the root, for the rule that every pull request follows this procedure. `README.md` for the layout and the extension contract |
| `<post-merge-checks>` | The post-merge pin, under Added gates. It runs after the merge, not before the pull request is ready |
| `<pairing>` | None |
| `<merge-cleanup>` | Nothing runs automatically. Removing the worktree after the merge, with `git worktree remove` from the main checkout, is the user's |

Every placeholder this table does not list is not applicable here, because there is no
app under test, runner dispatch, baseline, shared test environment, test account, schema
source, test data discovery, skip ledger or deviation record. Overrides, Section 6 says
what runs instead.

## Overrides

### Plan and review

Each change goes through these steps, in order:

| Step | Produces |
| --- | --- |
| Planning and design advice, before any code is written | The approach, the files to change, the test seams, the risks, and the edge cases, acceptance checks, and open questions of the general skill's step 4 |
| Writing the code and its tests | The change, built from the plan |
| Reviewing every change, including the last fix | A list of real findings, or none |
| Fixing review findings | A fix that is itself reviewed |

Before coding, spawn an agent with the issue or task and the files it touches, and ask it
for the plan and design advice: the approach, the files to change, the test seams, the
risks, and the general skill's step 4 list of edge cases, acceptance checks, and open
questions. The session posts that list as the general skill's step 4 says, puts the
answers to its open questions in it, and passes it in full to every agent that builds
from it and to every review agent. Build from that plan and record in the pull request
body, under Judgment calls, any place the code departed from it. A fix for a review
finding is reviewed like any other change.

### Models

A step that asks for a model the harness will not let the session choose (a subagent
call that rejects a per-call model, for example) still runs, on the best model the
harness offers. Do not skip the step, and do not withhold the ready signal for this
reason alone. Record each such step in the pull request body twice: under Judgment calls
and under Self review, naming the step, the model wanted and the model used.

### Test seams

The plan names the test seams. This overrides the `tdd` skill's step of confirming
seams with the user: when the code is built with `tdd`, the seams the plan names count as
confirmed, so an unattended run does not stop to ask. A seam the plan did not name is
asked through `AskUserQuestion` (or, in a subagent, returned in its report).

### Section 2, labels

There is no label script. Add a label with the response as the read-back; it lists the
issue's labels:

```bash
gh api repos/merph518/Overmind/issues/<N>/labels -f "labels[]=In Progress"
```

Remove one the same way:

```bash
gh api -X DELETE repos/merph518/Overmind/issues/<N>/labels/In%20Progress
```

A label that does not exist is never created. If the add is refused for that reason,
stop and tell the user.

### Section 3, ownership and the worktree

The unit is the folder the issue names. Before branching, read the open issues labeled
`In Progress`, each open pull request's files, and the oversee ledger:

```bash
gh issue list --state open --label "In Progress" --json number,title,url
gh pr list --state open --json number,headRefName,body
gh pr view <n> --json files
bash plugins/general/skills/oversee-development/oversee.sh status
```

Another session holding the unit, or an open pull request already closing the issue (a
branch name containing `issue-<N>-`, or `Closes #<N>` in its body), means defer and pick the next
issue. An issue labeled `Tracker` is not worked itself; work its open child issues. An `In Progress`
label with no open pull request and no session holding it is stale: ask through
`AskUserQuestion` before taking the issue over.

Claims: the board above sees only open pull requests, so claim files before editing them,
per the general skill's "Claim shared files". Claims live in the main checkout's git
directory, so every worktree shares them. `claims.py` takes the session from
`CLAUDE_CODE_SESSION_ID`, then `PI_SESSION_ID`; a session with neither passes
`--session <id>` to every call. Pass `--pid <pid of the session>` too when it is known;
without a pid a claim goes stale after twelve hours, so release it when the work ends or
stops without a pull request. The files most often wanted by two sessions are `CLAUDE.md`,
`README.md` and the two implement `SKILL.md` files: claim one of them right before its
first edit and edit it in one pass.

An issue that cannot be worked now, because it waits on another issue, on something
only the user can do, or on code that is leaving this repository, gets the `Blocked`
label, added the same way as `In Progress`, and this session's `In Progress` comes off
it with the delete command above. The report names what blocks it, and so does
a comment on the issue when the harness allows one. In a loop over issues, read each
`Blocked` issue's comment again before stopping: when what it waited on has settled,
remove the label and take the issue up. `Blocked` here also covers an issue waiting on
another issue or pull request in this repository.

When `EnterWorktree` is available, fetch `origin/main`, then use the tool to create
`.claude/worktrees/<name>` from `origin/main`. Rename the branch in the worktree:
`git branch -m <type>/issue-<N>-<slug>`.

When `EnterWorktree` is unavailable, after the label read-back and ownership checks,
run these commands from the main checkout:

```bash
git fetch origin main
git worktree add -b <type>/issue-<N>-<slug> ~/Code/Overmind/.claude/worktrees/<name> origin/main
```

Keep the path under `.claude/worktrees/`: the main-checkout guard exempts only that
folder, so a worktree elsewhere inside the main checkout has its writes refused. Run the
second command only if the fetch succeeds. Use a new worktree name and branch; if creation
fails, stop rather than reuse either. For a change without an issue, use `<type>/<slug>` as
the branch name.
Run the base verification in the general skill's step 3, Cut the branch, before editing.
All subsequent file operations and commands target that worktree; the main checkout's
files and checked-out branch stay untouched.

The harness worktree guard, when available, blocks a write outside the worktree. It also
refuses `git -C`, `cd` into the main checkout, and complex shell constructs. Keep shell
commands simple, use absolute worktree paths, and put scripts and long text (commit
messages, pull request bodies) in files in the session's scratchpad directory.

A session that loads extensions from `.omp/settings.json` runs `guard-main-checkout.sh`
through `scripts/omp-guard-hook.mjs`, and nothing else: the outright refusal of `git -C`,
of a `cd` into the main checkout and of complex shell constructs above belongs to the
other harness. The guard follows `cd` and `git -C` only to find where a branch-changing
git verb acts. Such a session has no tool that moves it into the worktree: pass the
worktree as the `cwd` of every shell call and name its files by absolute path. The
operator's `/move <path>` or a launch with `--cwd <path>` rebinds the session itself.

### Section 5, static checks

These run locally before every commit, so a push does not wait on CI to find what a local
check would have shown:

- `python3 scripts/validate.py` checks the plugin and marketplace JSON, `SKILL.md`
  frontmatter, relative Markdown links, and the syntax of every `.py`, `.mjs`, `.js` and
  `.sh` file in the tree.
- Every other changed JSON file parses: `python3 -m json.tool <file>`. `validate.py`
  parses JSON only in the plugin and marketplace files.

The final pass in step 7 runs both, with `json.tool` on every JSON file the branch changed.

### Section 6, running the affected tests

There is no app under test, no test runner dispatch, no shared environment, no test
accounts, no schema source, no data discovery, no skip ledger, no deviation records, no
failure snapshot and no baseline. The dispatch, baseline, deviation gate and artifact
reading parts of step 6 do not apply, and neither does the deviation gate in step 7.
Wherever steps 6 and 7 wait on a green dispatch, they wait on these local runs instead.

Runtime verification is running the affected test files locally in the worktree:

- `node --test <file>.test.mjs`
- `python3 <file>_test.py`
- `bash <file>_test.sh` (this includes each hooks folder's `run_test.sh`)
- Find every test of a folder with `git ls-files <folder>`. Pass test files by name:
  running a directory fails.

Every test file next to a changed file, and every test file that imports a changed
shared module, must pass. A change with no test gets one when the code is executable.
A diff with no executable code (Markdown, JSON data) runs no test; the report says so.

### Section 7, the pull request

- Every commit subject on the branch is a conventional commit, `<type>: <summary>`.
  Pull requests here land as merge commits, so release-please reads each branch commit
  from `main`. The title follows the same form, and is the one commit release-please
  reads if the pull request is squash merged. Mark a breaking change to the extension
  contract with `!`.
- The body has, in order: `Closes #<N>` (one line per issue closed), Why, What changes,
  Verification (the static checks and each test file run with its result), Judgment
  calls, Pre-existing failures fixed, Overlap, Self review, Settled decisions, then the
  attribution lines the session gives.
  Tool substitutions (see Harness substitutes) are recorded in one place, Judgment calls.
  The `pr` skill may be loaded when a body is written; this section's order wins. The
  `pr` skill's Summary section goes under What changes and its before/after Evidence
  under Verification; its Merge Danger section (Door and Blast Radius) goes under
  Judgment calls.
- Never merge the pull request, never push to `main`, and never force-push. The user
  merges. The one exception is a pin-only bump pull request, under Added gates, Post-merge
  pin.
- `gh pr edit` fails on a Projects classic deprecation. Edit a body with
  `gh api -X PATCH repos/merph518/Overmind/pulls/<n> -F "body=@<file>"`.
- Mergeability: `gh pr view <n> --json mergeable,mergeStateStatus`. Resolve a conflict by
  merging `origin/main` into the branch, never by rebase plus force-push.
- Self review: every change is reviewed, including the final fix (see Plan and review
  above). Spawn a review agent on the diff, and run the `code-review` skill with
  `origin/<default-branch>` as its fixed point. Fix real findings and review again, for at
  most three passes. The fixes from the last pass still get a review before the pull
  request is marked ready; this replaces the general skill's rule that the third pass's
  fixes get no fourth review. If that review finds another real bug, fix it, have a review
  agent review that fix, and say in the report that the loop ran past three passes. A
  fifth pass that still finds a real bug stops the work and asks through `AskUserQuestion`.
  The body's Self review section names the model used for each pass, and for the
  review of the last fix, with the fallback from Models where a model could not be chosen.
- Ready signal: never leave the pull request in draft. When the loop ends, mark it ready
  with `gh pr ready <n>`. The label is added only when every check on the pull request has
  passed on the current head. A read right after a push or a merge of `origin/main` can
  still show the previous commit's result, so first confirm the pull request's head is the
  commit pushed. Write the local commit to a file in the scratchpad, then compare it with
  the pull request's head every ten seconds for two minutes, in a background command that
  has no command substitution:

  ```bash
  git rev-parse HEAD > <scratchpad>/head.txt
  for i in {1..12}; do gh pr view <n> --json headRefOid --jq .headRefOid | grep -qxFf <scratchpad>/head.txt && { echo matched; break; }; sleep 10; done
  ```

  If it never prints `matched`, check that the push landed (`git status -sb`) and push it,
  or ask through `AskUserQuestion`.

  Then wait while any check is pending, or while none is reported yet, with a background
  command that has no command substitution and stops after thirty minutes:

  ```bash
  for i in {1..30}; do gh pr checks <n> 2>&1 | grep -Eq 'pending|no checks reported' || break; sleep 60; done; gh pr checks <n>
  ```

  If the thirty minutes pass with a check still pending or none reported (a conflict, a
  skipped run, or offline runners keep a run from starting), stop waiting and ask through
  `AskUserQuestion`. Merging `origin/main` into the branch, or any push, starts the checks
  again, so the head check and the wait repeat after it.

  A check that fails is a real failure to fix, then the fix is reviewed and pushed
  like any other fix; the label stays off until the rerun passes. This holds for a docs-only
  branch too, because `test-all` runs the whole suite on every pull request: a failure
  already on `main` is fixed here, and the body's Verification reports the CI result. A
  check that reads `cancel` (a newer push cancels the older run, and a run past its timeout
  reads the same) is not a pass: when the head is current, rerun it once with
  `gh run rerun <run-id>`, and ask through `AskUserQuestion` if it cancels again. Once
  every check reads `pass` on the current head, add the label through the issues endpoint
  and read it back:

  ```bash
  gh api repos/merph518/Overmind/issues/<n>/labels -f "labels[]=Manual Review Needed"
  gh pr view <n> --json labels --jq '[.labels[].name]'
  ```

  A report that calls a pull request ready without the label reading back is wrong; fix
  the label first. A label on this session's own pull request whose checks are pending or
  red is wrong too: remove it. A commit pushed after the label is a new change: remove the label with
  `gh api -X DELETE repos/merph518/Overmind/issues/<n>/labels/Manual%20Review%20Needed`
  (a 404 means it was not on yet) and add it again only once the review of that commit
  is clean and its checks have passed.
- Ready check: at the start of every pass of a loop over issues, and before any final
  report, list the open pull requests that are not drafts and lack the label:

  ```bash
  gh pr list --state open --limit 200 --json number,isDraft,labels --jq '[.[] | select(.isDraft | not) | select(any(.labels[]; .name == "Manual Review Needed") | not) | .number]'
  ```

  Label this session's own pull request on that list once its review is clean and its
  checks have passed. Report another session's only when its body already has a
  `Self review` section and no session holds it (`ListAgents`, the issue's `In Progress`
  label); one still in review is not yet ready. Before any final report, also read
  `gh pr checks` for each of this session's own labeled pull requests, since a later
  "Update branch" merge or push can turn one red, and remove the label from one that is
  not passing. In a loop over issues, the wait runs in the background while the loop works
  the next issue; the next pass's ready check picks the pull request up when its checks
  finish.

## Added gates

### Shipped text

Skill and README text is vendored into work-side repositories. Before each commit, read
[repo-writing](../../../plugins/att-docs/skills/repo-writing/SKILL.md) and apply it to
what the diff adds. Shipped text never names this side's tracker issue numbers,
assistants or sessions (including in code comments), describes how things work now, and
uses plain American English. Overmind has no config for its scan scripts, so they are
not run here. Commit messages and the pull request body are exempt.

### CI runners

All CI in this repository, now and in the future, runs only on the owner's self-hosted
runners that carry the label `overmind`: `tablet-runner-1` to `tablet-runner-4` and
`pw-linux-runner-1` to `pw-linux-runner-6` (Linux), and `pw-ci-runner-desktop-1` to
`pw-ci-runner-desktop-5` (Windows). A job's `runs-on` includes `self-hosted` and
`overmind` and never names `playwright`. Add `Linux` for a job that needs a POSIX shell
(it lands on a tablet or a Linux Playwright runner) and `Windows` for one that needs the
desktops. Never use a GitHub-hosted runner (`ubuntu-latest`, `windows-latest`,
`macos-latest` or any other), and never target `pw-windows-runner-1`, which carries
`playwright` but not `overmind`. Before adding or editing a workflow,
confirm the names and labels with
`gh api orgs/merph518/actions/runners --jq '.runners[] | "\(.name) \(.status) \([.labels[].name] | join(","))"'`,
and before opening the pull request run `grep -rn runs-on .github/workflows` and check
every line against this rule. Only one session edits the workflows at a time: read the
open pull requests' files first, per Section 3.

### Post-merge pin

A pull request that changes functionality ends with a pin cut and a pin-bump pull
request in every repository that pins Overmind. The step runs after the merge, from the
wait in `<run-watch>`, for a pull request with or without an issue, and the work is not
done until it finishes or is skipped.

- **Skip** a pull request whose diff is only documentation (`README.md`, `docs/`, other
  Markdown that no skill reads) or only tests. A change to a `SKILL.md`, a script, a
  hook, a workflow, or a `plugin.json` changes functionality. Say in the
  final report that the step was skipped and why.
- **Cut the pin.** A pin is a release tag, and this session never tags. First read the
  newest tag with `git ls-remote --tags --sort=-v:refname origin 'v*'`, taking the first
  line that does not end in `^{}` and never using `gh release view`, because a tag can
  exist without a GitHub release. Keep it as the tag from before the merge. Then read
  the release workflow's run on the merge commit
  (`gh run list --workflow release.yml --commit <merge sha> --json conclusion,status,url`),
  waiting until that run appears and has finished or shows `skipped`. A `cancelled` run
  is reported to the user with its link: stop there, open no bump pull request, and take
  neither branch below. For any other result, take the branch that fits:
  - The workflow ran. Look for the open release pull request with
    `gh pr list --state open --head release-please--branches--main --json number,title`.
    When it lists this pull request in its changelog, ask the user through
    `AskUserQuestion` to merge it, because this skill merges only pin-only bump pull
    requests. When there is none, or it does not list this pull request, because the change merged as a type
    release-please ignores (it reads only `feat`, `fix` and `perf`), report that no pin
    was cut and why, and open no bump pull request. A failed run is reported the same
    way, with the run's link.
  - The workflow is skipped. The tag is cut by hand, an exception to the README's rule
    that holds only while the workflow is off, and any release pull request left open is
    ignored: ask the user through `AskUserQuestion` to cut it. When the workflow runs
    again, resync the manifest to that tag, under Releases below.

  After the user was asked to merge the release pull request or to cut the tag, open no
  bump pull request until the newest tag is above the one from before the merge.
- **Update the installed plugins.** Once the newest tag is above the one from before the
  merge, bring this machine's installed plugins to it, so the next new session lists the
  new skills. The update changes Claude Code's plugin folder through the `claude` command,
  not by editing files, which is the one exception to the rule below that this session
  writes only inside its worktree. Read
  `~/.claude/plugins/known_marketplaces.json` first.
  - When the `att-docs` source has a `ref`, the marketplace is pinned and an update stays on
    that tag. Run nothing, and report the README's remove, add and install commands to the
    user, because removing the marketplace uninstalls the plugins this session runs from.
  - Otherwise run `claude plugin marketplace update att-docs`, then
    `claude plugin update <name>@att-docs --scope user` for `att-docs`, `general` and
    `voice`. Add the same update with `--scope project` or `--scope local` for each plugin
    that `~/.claude/plugins/installed_plugins.json` lists for the main checkout's path: from
    a worktree the command reaches the main checkout's entry, and no command reaches a
    worktree's own entry. A session in another repository with its own entries gets the
    commands from the `voice` plugin's `SessionStart` hook, which reports an installed
    plugin that is behind.
  - The update applies to sessions started afterward. Report what ran and its result.
- **Find every repository that pins Overmind.** List the owner's repositories with
  `gh repo list merph518 --no-archived --limit 100 --json name --jq '.[].name'` (raise the
  limit when it returns 100 names) and keep each one whose lock names Overmind:
  `gh api repos/merph518/<name>/contents/.claude/att-docs.lock -H "Accept: application/vnd.github.raw"`
  has a `repo=` line naming `merph518/Overmind` or an earlier location of it. A 404 means
  the repository does not pin Overmind. Read the list fresh each time. Compare the
  result with `.github/consumers.json` and report drift both ways to the user: a repository
  that pins Overmind but is missing from the file, so it can be added, and a listed
  repository that no longer pins Overmind, so it can be removed.
- **Open one pin-bump pull request per repository.** This session cannot write outside
  its own worktree, so each bump is handed to a session started in that repository, or to
  the user. That session runs `scripts/overmind-sync.sh <new tag>`, then
  `scripts/overmind-check.sh`, a `chore:` commit, and a pull request titled
  `chore: Move the Overmind pin to <new tag>` that names the Overmind pull request. When
  the new tag crosses a minor version, it checks its extension first, per the README's
  Releases section. Nothing pushes to a repository's `main`.
  - A bump whose diff is only the lock, `.claude/att-docs.lock`, and the vendored files
    under `.claude/att-docs/` is a pin-only pull request. It skips the self review loop,
    the review and the ready label, because the code it brings in was reviewed in
    this repository, and it merges by the next step without a confirm. The handoff says
    so, because that repository's own rules otherwise call for the full procedure.
  - A bump with any other change, such as an extension edit for a new minor version,
    runs that repository's own implement procedure in full, with its review loop and
    ready label, and is never merged by this step.
- **Close the pin pull requests it supersedes.** Once a repository's bump pull request is
  open, run `close_superseded_pins.py` from this skill's folder in the Overmind checkout
  (add `--dry-run` first to see the list). It only calls `gh`, so it works for a repository
  whose bump was handed to another session once that session reports its pull request number:

  ```bash
  python3 .claude/skills/implement/close_superseded_pins.py <owner/repo> <new tag> <new pull request number>
  ```

  It requires the new pull request to be open with the new tag in its title. It then closes
  each other open pin pull request in that repository that targets an earlier version, with
  a comment naming the new pull request, and deletes its branch. It never closes the new
  pull request, a pin pull request for the same or a newer version, or a pull request whose
  title is not a pin bump, so a repository ends with one open pin pull request, the newest.
  A pull request it could not close, or whose branch it could not delete, is reported with
  the reason.
- **Merge each pin-only pull request once its checks pass.** This is the one exception to
  the rule that a session never merges. Once a repository's bump pull request is open,
  run `merge_pin_pr.py` from this skill's folder in the Overmind checkout, in the
  background, one per repository:

  ```bash
  python3 .claude/skills/implement/merge_pin_pr.py <owner/repo> <pull request number>
  ```

  It reads the pull request again and acts only on a pin-only one: an open, non-draft pull
  request from a branch in the same repository into its default branch, with a pin title,
  whose changed files, and the files any rename moved from, are the lock and vendored
  files alone, with the lock changed, not removed or renamed, and naming the same
  repository as before, the title's tag, and the commit that tag points to. Any other
  pull request is left as it is (exit 2, verdict `review`). It waits up to an hour for the
  checks and for any branch rule blocking the merge to clear, giving each new head commit
  five minutes for its checks to start, and merges that commit when every check has
  passed, or when none has started, with the repository's allowed merge method, deleting
  the branch. A failing check, a wait still unfinished at the deadline, a conflict, a
  branch behind its base, a hundred checks or more, a pull request or lock it cannot read,
  or a refused merge leaves the pull request open with a comment saying why and the
  `Manual Review Needed` label, so it shows as waiting on the user (exit 1, verdict
  `flagged`). `--dry-run` judges the pull request
  as it stands, without waiting, and writes nothing.
- **Finish each merged pin.** For each pull request merged, run that repository's
  post-merge steps in a session there: the session that opened the bump when it is still
  running, or a session started for those steps alone, closed when they finish.
- **Report** one line per tag, not per repository: the tag, how many repositories it
  merged in, and each pull request left waiting on the user with its reason, such as
  `v1.4.0 pinned in 6 repositories; Gnome-Widgets #12 waits on you, a check failed`.
  A repository whose sync or check fails is named on that line with the failing command,
  and the others still go ahead.

### Releases

release-please reads conventional commits on `main`. Never bump a version, and never
edit `.release-please-manifest.json`, `CHANGELOG.md`, or a `plugin.json` version by hand.
The one exception is a resync: when a tag was cut by hand and the manifest is behind it,
a `chore:` pull request sets the manifest and the three `plugin.json` versions to that
tag. It changes no other version.

## Repository notes

- A change that alters the layout or the extension contract updates `README.md` in the
  same pull request.
- Follow-ups that need a write the harness refuses go in the pull request body under
  `Follow-ups`.
