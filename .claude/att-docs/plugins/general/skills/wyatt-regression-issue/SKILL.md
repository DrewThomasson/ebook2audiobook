---
name: wyatt-regression-issue
description: >-
  File one full-regression issue per Playwright project of a suite, from the saved template,
  for the run owner on the work side: run every folder locally, rerun only the failures,
  replace the project's sweep log row, list every skipped test in the skipped test
  inventory, and file an issue per failed or flaky spec. Starts only when the user asks for
  it by name.
disable-model-invocation: true
---

# Wyatt Regression Issue

`/wyatt-regression-issue <SUITE> [project ...]`

Files one issue per Playwright project of the suite, or only the projects named. The issues
move to the work-side tracker, where the run owner runs them locally. The body comes from
`<issue-template>`, rendered by `<render-script>`, and is not reworded per run: the user
tuned every line of it.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. This skill does not ship the template or the render script, so the
extension also names the arguments, exit codes, and values file each one uses. The
extension's own frontmatter carries `disable-model-invocation: true` too, so the model cannot
start it unasked.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | How a question is put to the user |
| `<shell-text-note>` | The repository's note on passing values files, issue bodies, and comments to a command as files |
| `<issue-template>` | The saved issue body, with its fill-in keys and the five numbered Expected items |
| `<render-script>` | The command that renders one body from a values file and the template, copies the project's current sweep log row into Observed, and exits 1 on a placeholder left unfilled, an Expected list that is not five items, a list item run onto the line before it, or an em dash |
| `<values-keys>` | The keys of the values file and what each holds, including which are optional, and a worked example the user approved |
| `<suite-config>` | Where the suite's projects are defined, which are setup projects (left out, since they run as a dependency), and which are mobile projects (left out unless named) |
| `<sweep-log>` | The file that holds the latest result per project, and the rules for its columns and its note term. The render script reads the project's row from it, and the template tells the run owner to replace that row |
| `<skip-inventory>` | The file that lists every skipped test, with the columns each row needs |
| `<issue-labels>` | The labels a regression issue carries, and the milestone rule |
| `<issue-title-form>` | The title form for a regression issue |
| `<failure-issue-form>` | The title form and sections for the per-spec failure issues, and where a failure that turns out to be the application not matching its documentation is recorded instead. The template tells the run owner to file them |
| `<handoff-note>` | What the issue body must not mention because the issue moves to another tracker: this tracker's issues, pull requests and runs, pipelines, workflows and runners, local tooling paths, the skip ledger, run budgets, and environment setup |
| `<scratch-dir>` | Where the values files are written |

## What the body leaves out

The template already holds these out. Keep them out of anything filled in, per
`<handoff-note>`:

- No mention of any issue, pull request, or run in this repository's tracker. The issue moves
  to the work-side tracker, and those links point nowhere there.
- No pipelines, workflows, dispatches, runners, or local tooling paths. The run is local.
- No skip ledger beyond `<skip-inventory>`. The work side has none, so the inventory file is
  the record, and the user carries rows into this side's skip ledger by hand.
- No run budget, worker settings, environment setup, primer or notes pointers, report or
  result-folder instructions, or note length rule.
- No exception for skips that depend on the day's data. Every skipped test is listed.
- No em dashes.

## Steps

1. Read the suite's projects from `<suite-config>`. Leave out setup projects, and mobile
   projects unless the user names them.
2. Same-project check. List the suite's open issues:

   ```bash
   gh issue list --state open --label "<suite-label>" --limit 200 --json number,title
   ```

   `<suite-label>` is the suite's label from `<issue-labels>`.

   An open issue whose title names the project and a sweep or regression run is a duplicate.
   Ask the user, per `<asking-note>`, whether to rewrite it, file beside it, or close it and
   file new. Closing one takes a comment naming the new issue (passed per
   `<shell-text-note>`) and `--reason "not planned"`, after the new issue exists.
3. Fill one values file per project in `<scratch-dir>`, with the keys in `<values-keys>`.
   Write the file per `<shell-text-note>`.
4. Render each body with `<render-script>`. Fix what it refuses and render again.
5. File each one with the title in `<issue-title-form>`, the labels in `<issue-labels>`,
   and the rendered body. This skill sets those three itself, and step 2 is its duplicate
   check, so the `create-issue` skill is not run for these issues. Pass the body as a file,
   per `<shell-text-note>`:

   ```bash
   gh issue create --title "<title>" --label <first-label> --label <second-label> \
     --milestone "<milestone>" --body-file <body.md>
   ```

   One `--label` flag per label in `<issue-labels>`, and `--milestone` only when its
   milestone rule calls for one. Use only labels that already exist, and never create one.
   Never apply the label that claims an issue for a session at filing.

6. Read each issue back: the title, every label, the milestone when one was set, and the
   five numbered items under Expected.

## Changing the body later

An edit the user asks for on a filed issue goes into `<issue-template>` first, then every body
is rendered again and pushed with `gh issue edit <n> --body-file` (per `<shell-text-note>`),
so the template and the issues never drift. Removing a sentence that ends a line keeps the
line break after it: the render script's run-on check is there because that join happened
twice. A sentence removed from one section often has a partner elsewhere, usually in Scope
or Acceptance criteria. Search for it and raise it in the same change.

## Report

The issue links, one line each, and any duplicate that was closed or rewritten.
