---
name: implement
description: >-
  Implement a GitHub issue of ebook2audiobook-expressive end to end: read it, label it
  `In Progress`, branch from origin/main in its own worktree, do the work, run it, open a
  linked pull request, review that pull request itself, then hand it to the user. Use when
  asked to implement, work on, pick up, or start an issue by number - "/implement 12",
  "work issue 12", "start on #12".
---

# Implement

## Base

Read
[the general skill](../../att-docs/plugins/general/skills/implement/SKILL.md)
first and follow it, except where this file overrides it. The general skill is the vendored
copy pinned by `.claude/att-docs.lock`; never edit it here.

The general skill is written for a repository with a dispatched test suite. This one has no
test suite and no CI that runs on the fork, so the overrides below replace its test steps
with a static check and a run of the app. Where the general skill says "dispatch", "spec" or
"run", read "run the app per Section 6 below".

## This project

- A fork of `DrewThomasson/ebook2audiobook`: a Python app that converts ebooks to
  audiobooks through many TTS engines, with a Gradio web interface (`lib/gradio.py`) and a
  headless command line (`app.py --headless`). `README.md` documents every option.
- Pull requests target the fork (`merph518/ebook2audiobook-expressive`), never upstream.
  `gh pr create` names `--repo merph518/ebook2audiobook-expressive` so it cannot default to
  the parent.
- The upstream workflows in `.github/workflows/` run on upstream's self-hosted runners and
  do not run on the fork. A pull request here has no check job.

## Paths

| Placeholder | Value here |
| --- | --- |
| `<asking-note>` | Every question goes through the ask tool (`AskUserQuestion` in Claude Code), never in reply text alone |
| `<in-progress-label>` | `In Progress` |
| `<ready-label>` | `Manual Review Needed` |
| `<preflight>` | `gh auth status` succeeds and `git fetch origin` reaches the fork |
| `<label-script>` | `gh issue edit <N> --add-label "<label>"` (or `--remove-label`; `gh pr edit` for a pull request), then `gh issue view <N> --json labels --jq '[.labels[].name] \| join(", ")'` |
| `<labels-note>` | A label edit counts only when the read-back shows it |
| `<area-label-rule>` | The area and kind labels of [/create-issue](../create-issue/SKILL.md). An issue missing its area label gets it per that skill's section 7 before work starts |
| `<reference-docs>` | `README.md`, `CONTRIBUTING.md`, and the code |
| `<ownership-unit>` | The files the issue's diff changes |
| `<ownership-rules>` | Override 2 below |
| `<claim-script>` | None. Override 2 reads the board instead |
| `<main-checkout>` | `~/Code/ebook2audiobook-expressive` |
| `<worktree-script>` | [/new-branch](../new-branch/SKILL.md) |
| `<edit-guard>` | None. Every shell call takes the worktree as its working directory, and every file is addressed by its absolute worktree path |
| `<dependency-setup>` | Override 4 below |
| `<shell-text-note>` | Commit messages, pull request bodies and scripts are files in the session's scratch directory, written with the file-writing tool and passed with `-F` or `--body-file` |
| `<branch-types>` | `fix`, `feat`, `chore`, `docs` |
| `<default-branch>` | `main` |
| `<follow-up-note>` | [/create-issue](../create-issue/SKILL.md) |
| `<writing-rules>` | Comments, UI strings and log lines say how the code works now and why, never its history, an issue number or an assistant name. Match the surrounding code's style; do not reformat code the change does not touch |
| `<repo-constraints>` | The launchers (`ebook2audiobook.command`, `ebook2audiobook.cmd`) and `Dockerfile` stay in step: a new dependency lands in `requirements.txt` and every launcher that installs it. A new option lands in `lib/conf.py`, the headless parser in `app.py`, the Gradio interface when it is user-facing, and the README's usage block |
| `<static-checks>` | Override 3 below |
| `<pr-checks>` | None. No workflow runs on the fork |
| `<mergeability-note>` | `gh pr view <pr> --json mergeable,mergeStateStatus`. A conflict is resolved by merging `origin/main` into the branch, never a rebase or force-push, then the static checks again |
| `<branch-age-note>` | The note in [/new-branch](../new-branch/SKILL.md) |
| `<run-watch>` | None. The wait for a merge is the user saying so, or `gh pr view <pr> --json state` |
| `<self-review>` | Override 6 below |
| `<ready-signal>` | Override 7 below |
| `<instructions-file>` | `CLAUDE.md` when it exists |
| `<post-merge-checks>` | None |
| `<merge-cleanup>` | Override 8 below |
| `<sampling-note>`, `<discovery-rules>`, `<schema-source>`, `<project-exclusion>`, `<test-accounts>`, `<test-dispatch>`, `<test-run-rules>`, `<shared-env>`, `<baseline-rules>`, `<artifact-read>`, `<failure-snapshot>`, `<deviation-note>`, `<deviation-records>`, `<fix-cycle-budget>`, `<investigation-log>`, `<skip-ledger>`, `<pairing>` | None: they belong to a test runner and a second tracker this repository does not have |

## Overrides

1. **What does not apply.** The first two non-negotiable gates (dispatched test runs and
   deviation records), Section 6 except "Failures already on the default branch get fixed",
   Section 8, and every rule that names a dispatch, a spec, a baseline, a deviation record, a
   skip ledger, an investigation log, a shared test environment or test accounts are void.
   The gate in their place: no pull request opens before the Section 6 run below is done,
   except for a change to documentation, `.claude/` or `scripts/` alone, which owes no run and
   says so in the pull request.

2. **Section 2 and 3, reading the board.** Replaces `<ownership-rules>` and "Find out what
   other sessions own":

   ```bash
   git fetch origin --prune
   gh issue list --state open --label "In Progress" --json number,title
   gh pr list --state open --json number,headRefName,files \
     --jq '.[]|"#\(.number) \(.headRefName): \([.files[].path]|join(", "))"'
   git branch -r --list "origin/*issue-<N>-*"
   ```

   - The issue already carries `In Progress`, or has a branch or an open pull request that is
     not this session's: another session holds it. Leave the label alone, report who holds
     it, and stop.
   - An open pull request changes a file this issue needs: proceed, name that pull request in
     this one's body, and merge `origin/main` in once it lands. When both change the same
     function, defer and report it.
   - Nothing overlaps: say in one line what was checked, and go on.

   The label is created with `gh label create "In Progress" --force --color FBCA04` when it
   is missing, then added and read back.

3. **Section 5, static checks.** Replaces `<static-checks>`. In the worktree:

   ```bash
   git diff --name-only origin/main...HEAD -- '*.py' | xargs -r python3 -m py_compile
   git diff --name-only origin/main...HEAD -- '*.sh' '*.command' | xargs -r bash -n
   git diff --check origin/main...HEAD
   ```

   A change under `.claude/` or `scripts/overmind-*` also runs `scripts/overmind-check.sh`.
   Each gates the commit, and the final pass reruns the list on the branch head.

4. **Dependencies.** Replaces `<dependency-setup>`. The launcher builds `python_env/` and
   downloads models into `models/` on its first run in a checkout, which takes a long time and
   several gigabytes. When the main checkout already has `python_env/` and `models/`, link
   them into the worktree (`ln -s <main-checkout>/python_env python_env`, the same for
   `models`) before the first run. Never delete or rebuild the main checkout's copies. Software
   outside the launcher is installed with apt only, and the user runs any `sudo`.

5. **Section 6, run it.** Replaces the rest of the section. A change that touches `app.py`,
   `lib/`, `components/` or a launcher is run from the worktree:

   - Headless: `./ebook2audiobook.command --headless --ebook tools/workflow-testing/test1.txt
     --language eng`, plus the options the change touches, such as `--tts_engine` or
     `--device cpu`. Confirm the run exits 0, the audiobook lands under `audiobooks/cli/`, and
     its length is plausible (`ffprobe`). Listen-worthy changes (voice, prosody, expressiveness)
     name the output file in the report for the user to hear; the session never claims how
     audio sounds.
   - Gradio: a change to `lib/gradio.py` or the interface also starts
     `./ebook2audiobook.command` and drives `http://127.0.0.1:7860` in a browser: the changed
     control, one conversion through it, and the console for errors.
   - A launcher change is run on Linux only; the report says `ebook2audiobook.cmd` and macOS
     were not run.
   - Stop every server and conversion this session started before the report.

   A failure is read from the console output before editing. Two fix attempts that do not turn
   it green are put to the user through `<asking-note>`.

6. **Section 7, self review.** Replaces `<self-review>`: read the whole diff at the branch head
   with fresh eyes (a reviewer subagent when the harness has one), fix every finding that
   holds, rerun the static checks, and rerun Section 6 when the fix touches code it covers.
   Repeat until a pass finds nothing, up to three passes; a third pass with findings stops and
   reports them. Declined findings and their reasons go under `Self review` in the body.

7. **Section 9, the ready signal.** Replaces `<ready-signal>`: only when every commit is
   pushed, the static checks pass, Section 6 is done and the self review ended clean, add
   `Manual Review Needed` to the pull request, read it back, and end the report with
   `PULL REQUEST <pr> IS READY FOR YOUR REVIEW`, where `<pr>` is the pull request number.
   The voice hooks read that line ([extension.json](../voice-bridge-hooks/extension.json)), so
   keep its wording.

8. **Section 10, after the merge.** Remove `In Progress` from the issue and read it back. Then,
   with `git status --short` empty in the worktree, `git switch --detach origin/main` there,
   `git branch -D <branch>` and `git push origin --delete <branch>`. Leave the worktree in
   place. A pull request closed without merging: report it, remove the label, leave the
   branch.

## Added gates

- **Pull request body.** `Closes #<N>`, what changed and why, what Section 6 ran and what it
  did not, `Judgment calls` (each decision the issue left open, what was chosen over what, and
  why), `Pre-existing failures fixed`, any overlapping open pull request, and `Self review`.
  An empty section says "none". Title: `<summary> (#<N>)`.
- **Push, then create.** `git push -u origin HEAD` before
  `gh pr create --repo merph518/ebook2audiobook-expressive --base main`. Every later commit is
  pushed before the next review pass or the ready signal. Never push `main`, never merge.

## Repository notes

- [/create-issue](../create-issue/SKILL.md), [/new-branch](../new-branch/SKILL.md) and
  [/oversee-development](../oversee-development/SKILL.md).
- The vendored base is `.claude/att-docs/`, pinned by `.claude/att-docs.lock`. Move the pin
  with `scripts/overmind-sync.sh <tag>` and check it with `scripts/overmind-check.sh`.
