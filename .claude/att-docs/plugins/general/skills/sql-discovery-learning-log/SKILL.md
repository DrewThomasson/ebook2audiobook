---
name: sql-discovery-learning-log
description: >-
  Keep a per-investigation file recording what is settled and what is still open, while
  iterating on test-data discovery or a failing spec across run cycles. Use after diagnosing
  any red run during an implement or debug session, and whenever a multi-run investigation
  produces a fact worth more than one cycle.
---

# SQL Discovery Learning Log

A multi-run investigation produces facts at roughly one per cycle: which join path the
application really uses, what a grid's row metadata carries, which hypothesis a fresh-data
experiment killed. Those facts live only in the conversation until they are written down,
which means a compaction, a crash, or a concurrent session working the same code buys them
again at the cost of another run. This skill makes the write-down part of the diagnosis
loop instead of an afterthought.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<investigations-folder>` | The folder that holds the investigation files, and how it is split: one subfolder per application or suite, and the subfolder for a question that belongs to no single one |
| `<app-tags>` | The names a subfolder can take, where each comes from, and the tag for work about no single application |
| `<folder-page-command>` | The command that writes a new subfolder's folder page, if the repository keeps one |
| `<process-docs>` | The documents that describe the rules the application applies, and the index that finds them by module |
| `<fix-cycle-budget>` | The note on how many fix cycles a test gets and what a spent budget owes |
| `<probe-precision>` | The note on recording why a discovery walk rejected candidates |
| `<test-accounts>` | The document that lists test accounts and the facts about what each sees or holds |
| `<schema-notes>` | Where a settled schema or application rule is also recorded, so a reader of the schema finds it |
| `<tracker-comment-note>` | Where the material that must not ship goes instead: the issue the work is funded by, and what the comment carries |
| `<writing-rules>` | The scan, the humanizer pass, and the checks that govern text that ships, and who the audience is: what an investigation file may name when its readers already know it |
| `<gates>` | The commands that run before the commit on an investigation file |
| `<shared-env-writes>` | How writes into the shared test environment are reported |

## When to update

- After diagnosing any red run, before pushing the fix. The diagnosis is the moment the
  finding is sharpest.
- When an experiment concludes, even mid-cycle: a hypothesis confirmed or killed is a
  finding whether or not the run went green.
- When the fix-cycle budget runs out, per `<fix-cycle-budget>`, so the defect chain handed
  to the user matches what the file says.

Before spending a cycle on a rule the application already documents, grep
`<process-docs>`. A rule read there is a starting hypothesis, not a settled finding: it goes
in the Open section until a run or a query settles it.

Do not wait for the investigation to resolve. The unresolved state is exactly what the next
session needs.

## Why the row that worked worked

A lookup that walked candidates and landed on a usable row has not finished until the file
says what separated that row from the ones it turned down. The row's identifiers are not the
finding; the rule behind them is. Take the rejection reasons the run recorded, per
`<probe-precision>`, and write the rule as a condition a query could hold:

- The condition, once it is settled, goes under `## What is settled` in the words the schema
  uses, with the columns it reads. It then goes into the sweep itself and into
  `<schema-notes>`, because nobody reading a table's page thinks to look under
  `<investigations-folder>`.
- A rejection the database cannot express, where the page is the only arbiter, goes under
  `## Open` as the question it is: which column predicts what the page does. That question
  outlives the cycle that found it, and it stays in the file until a query or a process
  description answers it.

A cycle that closes with "this row works" and no rule buys the next session nothing, because
the next session's run will land on different data.

## Where it lives

One markdown file per investigation, in the subfolder `<investigations-folder>` and
`<app-tags>` name, from the first cycle. The subfolder is taken from the spec whose run
raised the question, so every note about one application sits in one folder. A question about
no single application goes under the tag `<app-tags>` gives for that. A folder that does not
exist yet is created with the first note in it, and `<folder-page-command>` then writes its
folder page.

The slug names the behavior under investigation rather than the ticket that funded it, and
carries no application prefix, because the folder already says which one. Before opening a
file, list the folder for one already covering the behavior. Update that file on later
cycles; never open a second file for the same investigation.

A link from one note to another in the same folder is the bare file name; a note in another
folder is reached by a relative link through the parent folder, and the rest of the
documents folder by a relative link up to its top.

This is repository text from the first line, so it is written to ship from the first line.
Nothing about the investigation as an activity goes in it. See "What never goes in the file"
below for where that material lives instead.

Memory holds none of this. An investigation file is not mirrored into a memory entry, and no
memory index line points at one. What stays in memory is the environment fact that outlives
every investigation: identity behavior, caching, per-account limits, a tool that lies about
its exit code.

A settled fact about one account, which account sees what or what it holds, also goes into
`<test-accounts>` once settled. The investigation file keeps the evidence; the document keeps
the fact.

## The two shapes

While questions are open:

```markdown
# <The behavior under investigation>

## Question

<What opened the investigation, in one or two sentences.>

## What is settled

<Each fact stated plainly enough to act on, with the observation that
establishes it. What renders, what a query returns, which account sees what.>

## What this rules out

<Explanations that looked right and are not, with the observation that kills
each one. Omit while empty.>

## Open

<What the next cycle should settle, stated as a question.>
```

Once the last question closes, the file becomes the write-up. `## What is settled` gives way
to `## Answer` carrying the rule, and `## Evidence` carrying what establishes it. Add
`## Sources` for the functional spec paths and sections, package and procedure names, and
column names that already answer part of it. Drop `## Open`, or keep the questions that
genuinely outlived the investigation.

A file that never had an open phase, because one query settled it, is written in the closed
shape directly.

## What never goes in the file

The documents folder ships to a separate work repository that knows nothing about this one,
so the rules that govern a code comment govern this file from its first draft, per
`<writing-rules>`. None of the following may appear, at any stage. The three marked with an
asterisk are the one exception: they may appear when the audience `<writing-rules>` names
already knows them.

- Tracker numbers of this repository's tracker, a branch name, or a pull request.* The work
  side's own identifiers are fine.
- Run identifiers, run URLs, and job links, whether bare numbers or links.
- A hosted CI provider, its workflows, its actions, or its runners.*
- Any assistant, agent, or skill, this one included.*
- The suite's own economics: how many cycles a question took, what it cost.
- The investigation told as a story. A reader wants the rule and what establishes it, not the
  order in which they were found. "The grid renders 12 rows disjoint from the worker's 72
  stages" is a finding. "I first believed the header settled it and lost four cycles" is not.

That material is real and still has to live somewhere. It goes where `<tracker-comment-note>`
says, where the run identifiers, the cycle count, and the permanent writes made into the
shared environment belong together, and where the next person reading the issue will find
them. Post it as part of the same diagnosis step that updates the file.

Writes into the shared environment are the one item worth posting even when nothing else
happened, per `<shared-env-writes>`, because an investigation's write cost is otherwise
invisible until someone trips over the records.

## The gates

Run `<gates>` before the commit, on the file as it stands, open or closed. They cover the
shipped-text scan, the short-form check, and the check on the documents folder as a whole.
The humanizer pass in `<writing-rules>` is not one of the `<gates>` commands; run it on the
same file before the commit.

An investigation file is a wiki page when the repository publishes one, so a slug that breaks
the page-name rules fails it, and so does a relative link to a file outside the documents
folder. Name a spec or a helper as code text rather than linking it.

An investigation file is dense with short forms: stage types, business function codes, column
names quoted out of the schema. Add a dictionary row for anything the check stops on. A SQL
identifier quoted in prose reads as an undefined short form until it is wrapped in backticks,
which is the right fix rather than a dictionary row.

Beyond the scan: no em dashes, the application's and the database's real vocabulary rather
than a paraphrase, and full paragraphs rather than hand-wrapped lines.

## On resolution

Distilling still happens, it just no longer means moving the file:

- Facts a reader of the code needs move into comments beside the mechanism.
- Facts about the schema or the application's rules are added to `<schema-notes>` as well,
  because someone reading a table's page will not think to look under
  `<investigations-folder>`.
- The file itself is rewritten into the closed shape and stays where it is.
