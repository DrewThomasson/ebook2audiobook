---
name: azdo-build-issue
description: >-
  Draft an issue from a failed AZDO build, carrying its failed tests, failed tasks, a log
  excerpt, and the build link under the create-issue conventions. Filing the issue is a
  choice the user makes. Starts only when the user types /azdo-build-issue.
disable-model-invocation: true
---

# AZDO Build Issue

Turns one failed AZDO build into an issue in this repository's tracker, for the build id the
user names. The build stays as it is: the build read reads the build, its timeline, its
published test results, and the end of each failed task's log, and writes nothing on either
side.

Only the user starts this skill, by typing `/azdo-build-issue`; the frontmatter keeps the
model from starting it. Nothing stands in for it: no watch, ledger tally, loop, or schedule
files an issue for a red build on its own. A build going red is a fact for the report, never
a trigger.

Inside a run, every write is an option the user picks through `AskUserQuestion`, per
`<asking-note>`. Writing nothing is always one of the choices, and a dismissed question
writes nothing. The one write is creating the issue, or appending to an open issue on the
same spec. The build, its results, and AZDO are not touched.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing payloads and issue bodies to a command as files |
| `<tunnel-command>` | The command that dispatches an operation through the tunnel to AZDO: its arguments, how it takes a payload, the ref flag and its default, and the lines it prints before the result |
| `<build-read-op>` | The operation that reads a failed build: its payload, the tail-lines setting with its default and maximum, the result it returns, and what it refuses |
| `<watch-skill>` | The skill that watches a build that is still running |
| `<issue-conventions>` | The create-issue conventions this repository sets: the title shape, the areas, the body sections, and how the area is chosen from the failed tests or the pipeline |
| `<same-spec-search>` | The command that searches open issues for the same spec, and what it searches on for a tooling draft |
| `<append-rule>` | How a build is appended to an open issue: the fetch, the size check, and the edit |
| `<issue-labels>` | The repository's note on which labels exist, which are applied, and the read-back after a create |
| `<create-command>` | The command that creates the issue, with its label flags |

## Starting a run

`/azdo-build-issue <build id> [tail=<lines>]`

Ask for a missing build id. The id is the AZDO build id, the one the run list, the queue, and
the watch report; a build number such as `20260916.1` is not it.

Tunnel dispatches go through `<tunnel-command>` on its default ref unless the user names
another ref. Payloads and the issue body are written to the scratchpad with the Write tool and
passed by path, per `<shell-text-note>`.

## Drafting

1. Read the build with `<build-read-op>`, which also says whether the read needs anything
   beyond its payload. It is a read and writes nothing. The tail-lines
   setting sets how many lines of each failed task's log the body quotes. A build still
   running is refused; watch it first with `<watch-skill>`.
2. Save the result. The stdout opens with the run address lines, so read from the first line
   that starts the result object. The result carries:
   - `title`, `labels`, and `body`: the draft, under `<issue-conventions>`. The area and spec
     come from the failed tests' files when they agree on one area, else from the pipeline's
     definition name, else the tooling area with the definition in the spec slot.
   - `build`: the summary the watch prints, with the build page under `web`.
   - `failedTests`, with each test's file, error, and stack, and `failedTasks`, each with its
     job, its logged error, and its `excerpt`.
   - `specFiles`: the spec files the failed tests belong to.
3. Write `body` to `<scratchpad>/issue-body.md` with the Write tool, and check it against the
   body sections in `<issue-conventions>`. The operation reports only what the build
   recorded, so the body names no root cause; add one only when the user states it.
4. Run the same-spec search, `<same-spec-search>`. A hit is where the build belongs: the
   option is to append it to that issue as a checklist item carrying the build link, not to
   open a second one. A tooling draft searches on the definition name instead.
5. Show the title, the labels, the body, and any same-spec issue found.

## Filing

6. Ask what to write: create the issue as drafted, append to the open issue found in step 4,
   change the draft first, or skip. An area label is used only when it already exists, and a
   label is never created.
7. On a create, run `<create-command>` with the body file, and confirm the labels with a read
   of the issue, per `<issue-labels>`. On an append, edit the open issue's body per
   `<append-rule>`, and report its address.
8. Two builds of the same pipeline do not make two issues. When step 4 found the earlier
   build's issue, the second build is appended there.

## Report

The build id and its page, the title and labels drafted, and what was written: the issue
created with its address, the issue appended to, or nothing. Name anything the draft could
not read: a build with no published test results says so in its body, and a failed task with
no log has no excerpt.
