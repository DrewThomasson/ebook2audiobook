---
name: business-rule-scan
description: >-
  Check every business rule against the converted document it came from, in both directions,
  reading the rules from a rule tool's dump or from a folder export of the working master, and
  say which documents need a rule update run, which rule sets carry duplicates, and which
  folders have no document or no rules. Reads only; writes nothing to the rule store, the rule
  tool, or the documents. Use when asked whether the business rules are current, which rules
  are out of date, or which documents need their rules refreshed, and after a batch of
  converted documents merges.
---

# Business rule scan

`<rule-update-skill>` refreshes the rules for one document. This skill says
which documents need that run. It compares the rules with the converted
documents under `<dump-docs>`, or under one of the `<master-suites>` folders,
and reports; it never stages, approves, or edits.

| Placeholder | Meaning |
| --- | --- |
| `<docs-root>` | The folder that holds the converted documents, one folder per suite |
| `<dump-docs>` | The documents folder whose rules are held in `<rule-tool>` and read from `<rule-dump>` |
| `<master-suites>` | The suites whose rules live only in the working master, and their folders under `<docs-root>` |
| `<rule-tool>` | The requirements tool that holds the rules for `<dump-docs>` |
| `<rule-root>` | The top-level `<rule-tool>` folder whose subfolders each hold one document's rules |
| `<rule-dump>` | The checked-in dump of `<rule-tool>`'s rules, the scan's default rule source |
| `<rule-store>` | The store that holds the working master of the rules |
| `<rule-workbook>` | The workbook the master-only suites' rules are codified into |
| `<id-dedupe>` | What in `<rule-store>` supersedes the older copy of a rule ID used twice |
| `<export-command>` | The command that exports the master's rules for one document or one folder |
| `<map-command>` | The command that places a `<rule-tool>` folder against its document |
| `<scan-command>` | The command that runs the mechanical pass, with the options under section 1 |
| `<scratchpad>` | Where the session writes its working files |
| `<scan-output>` | The JSON report the scan writes, under `<scratchpad>` |
| `<anchor-form>` | How a rule cites the document rule it anchors on |
| `<change-tags>` | The build or change-record tags a document puts on a numbered rule |
| `<revision-suffix>` | The suffix on an older revision kept beside a document |
| `<deleted-marker>` | The text a document puts in place of a numbered rule it removed |
| `<library>` | The source library the converted documents follow |
| `<watch-skill>` | The skill that keeps the converted documents in step with `<library>` |
| `<rule-update-skill>` | The skill that refreshes one document's rules |
| `<rule-extract-skill>` | The skill that runs a document's first extraction |
| `<issue-skill>` | How an issue is filed |

`<path>`, `<folder>`, `<suite>`, and `<suite-folder>` in the commands below are
the arguments of one run: a document, a `<rule-tool>` folder, a suite's name,
and that suite's folder under `<docs-root>`.

The converted documents are the source of truth. They follow `<library>`
through `<watch-skill>` and change as often as it does; the rules in
`<rule-tool>`, and the dump of them, are a snapshot that may already be stale.
A disagreement between a rule and its document is always settled in the rule:
updated, retired, or added to match. The one question to ask before that is
whether `<library>` holds a newer revision than the converted copy, since then
the document comes up to date first and the rules follow it.

## 1. Run the mechanical pass

```bash
<scan-command> --json <scan-output>
```

The rules come from `<rule-dump>` by default. When the working master has
moved past `<rule-tool>` for a document, export it with `<export-command>` and
pass the file; it replaces the dump for that document:

```bash
<export-command> "<path>" > <scratchpad>/export.json
<scan-command> --export <scratchpad>/export.json
```

Each top-level folder under `<rule-root>` is matched to the document whose
file name equals the folder name, case and punctuation aside. One line per
folder comes back, `current` or `review`, with these counts:

| Count | Means |
|---|---|
| `low` | Rules whose quoted wording shares under 60% of its three-word runs with the document. A rule with no quote is scored on its description. |
| `uncited` | Top-level numbered document rules no rule anchors on, `<anchor-form>`. |
| `pastEnd` | Anchors past the document's last numbered rule. |
| `uncovered` | Numbered document rules whose wording the rules cover under 30%. |
| `tagged` | The `uncovered` ones carrying one of the `<change-tags>`, the likeliest to postdate the rules. |
| `dupIds` | Rule IDs used twice. `<id-dedupe>` supersedes the older copy. |
| `sameText` | One description under two or more IDs. `<id-dedupe>` does not catch these. |
| `later` | Commits to the document after the newest rule was created, not counting the commit that added it. |
| `revisions` | `<revision-suffix>` copies beside the document. |
| `restarts` | Numbers the document gives to more than one top-level rule because its numbering restarts per section. A cited number there may belong to another section's rule, so read `uncited` and `pastEnd` for that document by hand. |

A folder reads `review` when any count other than `tagged`, `dupIds`, and
`restarts` is above zero. An export that matches no `<rule-tool>` folder, such
as a `<dump-docs>` document whose first extraction was approved in the master,
is scanned on its own under its title. An export from outside `--docs`, or one
naming a file the checkout lacks, stops the scan with the document's path.

### A master-only suite

`<rule-tool>` holds no rules for the `<master-suites>`. Their rules live in the
working master, `<rule-store>`, and are codified into `<rule-workbook>`, so the
scan reads them from a folder export instead of the dump:

```bash
<export-command> <suite-folder> > <scratchpad>/<suite>-export.json
<scan-command> --docs <suite-folder> \
  --export <scratchpad>/<suite>-export.json --json <scan-output>
```

`--docs` naming a folder other than `<dump-docs>`, with no `--rules`, reads no
dump. Each exported document is one line, named by its title, with the same
counts. A document in a nested folder is named by its path under `--docs`,
`Testing/api testing.docx`, so two files of one name stay apart, and that name
is what `--detail` takes. `later` counts commits after the newest rule entered
the master, which for an extracted rule is the day its batch was approved. An
export from outside the `--docs` folder stops the scan, and so does a folder
export that holds no document. A document with no rules yet is not in the
export, so it gets no line; the coverage of a suite is
`<rule-extract-skill>`'s question, not this scan's.

`--detail "<folder>"` prints the flagged rules and paragraphs for one folder,
`--detail all` for every folder. `no-doc` means no document matched the
folder, and `empty` means a folder with no rules. Rules filed straight under
`<rule-root>`, under another rule, or under a parent the dump lacks come back
together as `no-doc (rules outside a document folder)`.

## 2. Read what it flagged

The counts are where to look, not findings. Read the detail for every
`review` folder and settle each flag against the document:

- **Noise.** A rule that paraphrases the document rather than quoting it, a
  dropdown list the dump flattens into one line, a rule split from a
  compound sentence. `pastEnd` on a short document whose rules count list
  items rather than top-level rules. A numbered rule reading
  `<deleted-marker>`.
- **Changed.** The rule quotes wording or a rule number the document no
  longer carries in that form, or a `later` commit changed the paragraph it
  quotes.
- **Missing.** A numbered rule, most of all a `tagged` one, that no rule
  covers.
- **Duplicate.** A `sameText` set. Retiring the later ID is
  `<rule-update-skill>`'s work, never this skill's.

A folder whose rules quote wording the document lacks in bulk was extracted
from a different revision. Before recommending an update, find out from
`<watch-skill>` which revision is current, since converting the newer revision
may be the real fix.

Each folder then reads `current`, `review` (only questions to put to the
reader), or `stale` (an update is owed).

## 3. Report and file

Report one line per folder with its verdict, then for each `stale` folder the
rules and paragraphs that decided it. Give the `low` rules by ID and the
uncovered paragraphs by number.

File one issue per `stale` document through `<issue-skill>`, unless an open
issue already covers it. The issue names the `<rule-update-skill>` run the
document needs, and the revision question first when there is one. Duplicate
sets across several folders go on one issue. A folder with no document, or a
document with no rules, is reported and left alone: placing a folder is
`<map-command>`, and a first extraction is `<rule-extract-skill>`. Rules
outside a document folder are reported by ID for whoever files them in
`<rule-tool>`; no script moves a rule between folders.

## Limits

- The comparison is on wording, so a rule that keeps its words while the
  behavior around it changes reads as current. Changes like that come up in
  `later` and `tagged`, which is why those two are read in full.
- `<rule-dump>` records when each rule was created, not when it was last
  reviewed, so `later` counts against creation.
