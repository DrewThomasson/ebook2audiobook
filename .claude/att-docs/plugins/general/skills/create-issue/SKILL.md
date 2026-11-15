---
name: create-issue
description: >-
  File an issue in the current repository's tracker under a required title
  convention, with the standard body sections, an area label, and a kind label.
  Use when asked to file, open, create, or write up an issue, when another skill
  needs an issue title or turns up follow-up work outside its task, and when
  existing issues need retitling to the convention.
---

# Create Issue

Every issue in a repository carries the same title shape. The shape is what makes a
long tracker searchable by area and by unit, so it is a rule, not a preference.

```
[<AREA>] <unit>: <description of issue>
```

Exactly one bracketed area, one space, the unit name, a colon, then the description.
No trailing period. The whole title stays within `<title-limit>` characters.

| Placeholder | Meaning |
| --- | --- |
| `<title-limit>` | The longest title allowed, usually the repository's line limit |
| `<areas>` | The list of area names, where each one comes from, and the catch-all area for work that belongs to no single area |
| `<unit-rule>` | How the unit name is derived: a file basename, a module, a script |
| `<ownership-rule>` | How many areas and units one issue may name, and why |
| `<labels-note>` | The repository's note on applying a label and reading it back |
| `<label-script>` | The command that adds a label and reads it back |
| `<kind-labels>` | The kind labels that exist, and the ones never applied at filing |
| `<body-sections>` | The required body sections, in order, when they differ from the default |
| `<acceptance-rule>` | What an acceptance criterion says in this repository: which run closes an issue |
| `<special-slots>` | Areas or units with a filing rule of their own, such as a slot only one change may hold |
| `<deviation-route>` | Where a gap between documented and observed behavior goes when it is not an issue |
| `<shell-text-note>` | The repository's note on passing a body to a command as a file |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<scratchpad>` | The session's scratch directory for the body file |
| `<writing-rules>` | The gate for text that ships, and what an issue body may say that shipped text may not |

## 1. Area

The area is one of `<areas>`. Each area also exists as a repository label of the same
name, and the issue carries both. The title prefix is what a person reads; the label is
what a list filter and the tracker sidebar use, and a title prefix is not filterable.
Applying one without the other leaves the issue out of half the views it belongs in, so
an issue is not filed until it has both.

Work that belongs to no single area takes the catch-all area from `<areas>`.

`<ownership-rule>` sets the size of one issue. The default is one area and one unit per
issue. Work spanning two is split into two issues, each scoped to its own area or unit,
and the body says which sibling each was split from. They are branched, verified, and
merged separately, so one issue covering both can never be closed cleanly, and a
cross-unit issue claims ground other sessions are standing on. A leftover belongs to
the unit it lives in, so no issue collects the leftovers of several others.

## 2. Unit name

The unit name follows `<unit-rule>`. Keep every segment that identifies the variant,
because the variant is what identifies the failing file. When the unit does not exist
yet, use the planned name from the plan that proposes it, so the issue and the file it
produces line up. When there is no file at all, name the module, workflow, or script the
issue is about.

## 3. Description

State the observed behavior or the requested change. No conventional-commit verb
prefix: `fix`, `feat`, `refactor`, and `chore` belong on the branch name, the commit,
and the labels, and repeating them in the title costs characters the unit name needs.

Sentence case, no trailing period, present tense, specific enough to recognize without
opening the issue. `dropdown is broken` is not a description; `destination dropdown
lists closed stages` is.

## 4. Body

Required sections, in this order, unless `<body-sections>` sets another list. A section
with nothing to put in it says so explicitly rather than being dropped.

The body is not hand-wrapped. A line limit on source is not a rule about an issue body,
which is read in a text box that wraps on its own.

- **Context**: the unit's path, the tests or functions involved, and any identifiers the
  plan gives them.
- **Observed**: what actually happened, with the run link or the output path that shows
  it. Report only what was directly observed. Never invent error text, line numbers,
  retry counts, or a root cause. With no evidence yet, write that the issue is filed from
  a report rather than a run.
- **Expected**: the documented behavior, cited by path and section, or the rule as
  written. For an enhancement, the behavior being asked for.
- **Scope**: the files and helpers a fix is expected to touch, and anything deliberately
  out of scope.
- **Acceptance criteria**: what `<acceptance-rule>` says closes the issue, named
  precisely enough that someone else can run it.

An issue body lives in the tracker, so it may name runs, issues, and pull requests that
`<writing-rules>` bans from shipped text. Text quoted into the body that is destined for
a file is held to the shipped-text rules as if it were already committed.

## 5. Labels

Only labels that already exist. Never create one. Every label this skill applies is read
back off the issue before the skill reports, per `<labels-note>`: an issue filed without
its area label reaches no per-area view, so it is filed and then invisible.

Every issue carries one area label matching its title prefix. On top of it goes a kind
label from `<kind-labels>`. The catch-all area is an area label only, never a kind.

Never apply the label that claims an issue for a session. It is applied by the
implementing skill when work actually starts, and applying it at filing time makes the
queue lie.

A gap between documented behavior and observed behavior is not filed as an issue when
`<deviation-route>` names another home for it. It goes there, once per deviation.

## 6. Before creating

1. **Same-unit check.** The question is not only whether this exact behavior is filed,
   but whether anything for this unit is. Search open issues by area label and unit name,
   dropping the label and searching again when the labeled search comes back empty for a
   unit you expect to be filed, since issues filed before the labels existed carry the
   prefix alone.

   A hit means this finding is added to that issue as a checklist item under its own
   heading, and that issue's URL is what gets reported. Returning an existing URL is a
   successful run of this skill.

   Fetch the body from inside the repository, check the file is not empty, append the
   item, and edit the issue from the file. An empty fetch edited back wipes the issue
   body and reports success, so the size check before the edit is required, and the first
   lines are read back afterward.

   A cause that reaches several units through shared code gets one issue named for the
   shared code, listing every unit and title it reaches, and each unit's open issue gets a
   line pointing at it. Search closed issues from the last 30 days too: a match closed
   lately is a regression, and the new issue links it.

   Editing the body rather than commenting keeps the work list in one place where the
   implementing skill reads it. A comment is for a question about the issue rather than
   more work under it.

   `<special-slots>` names any area or unit with a rule of its own. Where it says every
   change gets an issue of its own, the same-unit search and the append are replaced by a
   duplicate check over every open issue in that area: one asking for the same change is
   the duplicate and its URL is reported, and one asking for a different change is filed
   beside it, linking the other when the two touch the same file.

2. **Sibling session check.** Another session may already own this unit. Read the open
   pull requests' file lists, not just branch names, before filing. If one owns it, the
   finding still goes onto that unit's issue, and the report says which session holds it.
3. **Confirm the title** with the user whenever the description was inferred rather than
   given, through the tool `<asking-note>` names. A title the user supplied is used as-is
   once it fits the convention.

Write the body to a file in `<scratchpad>` with the file-writing tool, per
`<shell-text-note>`, and file it:

```bash
gh issue create --title "[<AREA>] <unit>: <description>" \
  --label <AREA> --label <kind> --body-file <scratchpad>/issue-body.md
```

The area label and the kind label are two `--label` flags, not one comma string. A caller
that names a milestone adds `--milestone "<title>"` to the same call. Gate: the created
issue is read back, and both labels, and the milestone when one was named, are confirmed
before the URL is reported.

```bash
gh issue view <n> --json labels,milestone \
  --jq '"\([.labels[].name] | join(", ")) | \(.milestone.title // "no milestone")"'
```

Report the issue URL. Do not branch, do not claim the issue, do not edit code. The
branching and implementing skills own everything after the URL exists.

## 7. Retitling existing issues

Issues filed before the convention exist under older shapes. They are retitled in place,
never closed and refiled, because their numbers are referenced from branches, pull
requests, and other issue bodies.

Retitle when asked to clean up the tracker, and whenever an old issue is picked up for
work.

1. List the open issues with their titles and labels.
2. A title already matching `^\[[A-Za-z0-9]+\] \S+: .+` is left alone, but it still gets
   its area label if it is missing one. A converted title and a missing label are the
   same issue half done.
3. Derive the area and unit from the issue body, from the path it names, or from the
   branch that references it. When none identifies them, ask through the tool
   `<asking-note>` names rather than guessing. A wrong area is worse than an unconverted
   title, because it makes the issue unfindable under both shapes.
4. Preserve the description's meaning. Drop the verb prefix and any trailing
   "remaining work" suffix, and keep the words that carry information.
5. Apply one at a time, the label first and then the title, which waits on the label
   landing. Use `<label-script>` so the read-back says the label landed on that issue.
6. Present the full old-to-new mapping to the user before applying it in bulk, and report
   the count changed, the count labeled, and the ones skipped for lack of a unit.

Issue bodies are not rewritten during a retitle pass. The title and the area label
change, nothing else.

## 8. Other skills

The skills that file issues take their titles from this one rather than defining their
own shapes, so a title created by any path through the repository looks the same. The one
exception is a skill that files issues from its own saved template, such as
`wyatt-regression-issue`: it sets its title, labels and body, and runs its own duplicate
check.
