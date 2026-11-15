---
name: business-rule-extract
description: >-
  Extract the business rules from one converted specification document that has no rules
  yet, following the first-extraction procedure, into an import file reviewed as a
  workbook, then staged as a batch on the rule store, approved into the working master,
  and the document registered. Use when asked to extract, pull, or write up the business
  rules for a document for the first time, or when a document has no rules yet.
---

# Business rule extraction, first time

A document that already has rules is updated with `<update-skill>`; this skill is
for one that has none. It reads the converted document whole, writes every
atomic rule into an import file, and hands the user a workbook built from that
file to review. Only once the review is complete is the file staged in
`<import-table>`, and approving that batch is what inserts the rules into
`<master-table>` and registers the document in `<doc-map>`, so the next revision
goes through an update. Nothing here writes to `<rule-tool>` or to
`<tool-mirror>`. The reviewed import, staged as one batch, is the deliverable.

The consuming repository's extension supplies the values below. Where it names
none, ask the user rather than guessing.

| Placeholder | Meaning |
| --- | --- |
| `<docs-root>` | Where converted documents live, one folder per suite |
| `<suite>` | The suite folders under `<docs-root>` |
| `<tool-docs>` | The documents whose rules `<rule-tool>` also holds |
| `<workbook-docs>` | The documents whose rules go only into the business rule workbook |
| `<rule-tool>` | The requirements tool that holds rules for `<tool-docs>` |
| `<tool-mirror>` | The store table that mirrors `<rule-tool>`'s requirements |
| `<rule-store>` | The database that holds the master, the map, and the staged imports |
| `<master-table>` | The working master of approved rules on `<rule-store>` |
| `<doc-map>` | The table registering each document with rules and its prefix |
| `<import-table>` | The table a staged batch's rows land in |
| `<tool-id-column>` | The `<master-table>` column holding a rule's `<rule-tool>` id |
| `<extract-match>` | The `<doc-map>` value marking a row registered by an extraction |
| `<update-skill>` | The skill that updates rules for a document that has them |
| `<update-lists>` | Where `<update-skill>` says how its commands take a list |
| `<update-export>` | Where `<update-skill>` says what an export refuses and how Path is built |
| `<workbook-format>` | The document fixing the business rule workbook's layout |
| `<gate-command>` | The command that gates a document and checks a prefix |
| `<page-script>` | The script that places quoted wording on a source page |
| `<import-check>` | The script that checks an import file against the gate export |
| `<preview-script>` | The script that builds the review workbook from an import file |
| `<stage-command>` | The command that stages one or more import files as batches |
| `<workbook-command>` | The command that exports a staged batch's workbook |
| `<review-commands>` | The commands that reject rows, approve a batch, and reject a batch |
| `<store-read>` | How a reviewer reads a staged batch on `<rule-store>` |
| `<staging-source>` | Where `<stage-command>` reads the import file from |
| `<import-file>` | Where an import file is written and how it is named |
| `<id-prefix>` | The fixed opening of every rule prefix |
| `<field-limits>` | The `<rule-tool>` field lengths an import value must fit |
| `<self-review>` | The review the repository runs on its own pull request, if any |
| `<scratchpad>` | A scratch directory outside the repository |

The document is a `<tool-docs>` document or a `<workbook-docs>` document under
`<docs-root>/<suite>`, in a nested folder or not. `<rule-tool>` holds rules for
`<tool-docs>` only; a `<workbook-docs>` document's rules are codified into the
business rule workbook (`<workbook-format>`) and never go to `<rule-tool>`. The
steps below are the same for both.

The tables, `<gate-command>`, `<import-check>`, `<preview-script>`, and the
review and approval commands are `<update-skill>`'s. Read it for what each table
holds.

## 1. Gate

```bash
<gate-command> --doc "<doc path>"
```

A document `<doc-map>` holds is refused, naming its prefix; that document is an
update. Otherwise the result is one JSON object with the document `title`, a
`proposed_prefix`, and `taken_prefixes`, one row per prefix any rule has used in
any status, any the map holds, and any a pending first extraction holds.

## 2. Prefix

The proposal is `<id-prefix>` plus the module letters and the screen number with
a trailing `.0` dropped: `ABC1.2.1 Select Date` gives `<id-prefix>ABC1.2.1`,
`ABC 4.0 - Entry` gives `<id-prefix>ABC4`. A `<workbook-docs>` document whose
module letters are not its suite's gets the suite in front, since the suites
reuse module codes: suite `XYZ`'s `UC1.1 - Login` gives `<id-prefix>XYZ.UC1.1`,
while suite `XYZ`'s `XYZ - 1.0 Home` gives `<id-prefix>XYZ1`. The prefixes
already in use do not all follow that shape, so the proposal is put to the user,
beside the taken list, before any rule is numbered. The user may pick the
proposal or name another. A title that does not open on a module code and a
screen number (`Intake Overview`) gets `proposed_prefix: null`, and the question
asks the user to name the prefix outright. Then:

```bash
<gate-command> --doc "<doc path>" --prefix <prefix> > <scratchpad>/export.json
```

With `--prefix` the gate checks the prefix against every rule, every map row,
and every pending first extraction of another document, and prints the empty
export (`next_seq: 1`, no rules) that `<import-check>` reads. A prefix in use is
refused with the rules or document holding it.

## 3. Extract

Read the whole document: every heading, paragraph, numbered rule, bullet, table
row, note, and cross reference, in the order the document has them. Treat every
statement as a possible rule, including a workflow that implies a system
behavior, and extract: validation, workflow, state transitions, security and
role restrictions, timing, batch, event and cue generation, reporting,
integration, display conditions, save, update and delete behavior, required and
derived fields, navigation, duplicate prevention, release and expiration
conditions.

One row is one independently testable behavior. A compound sentence is split; a
list of values the system shows or accepts stays one rule, the way a grid's
column list is one rule. Write the summary as system behavior: "System displays
the Medical Exam cue 120 days before the due date", never "System handles
medical exams".

Numbering runs from `001` in document order, with no gap. Merge two statements
only when they say the same behavior under the same conditions; when the
conditions differ, they are two rules, and when two parts of the document
disagree, both are extracted and the pair goes under `manual_review_items`.

Every rule cites the page of the source document it was taken from. The
converted file marks where each of the original's pages starts with
`<a id="page-N"></a>*Page N*`, and the provenance block's `Pages:` line gives
the count and names any page the conversion could not mark. Text after the
marker for page 3 and before the one for page 6, with pages 4 and 5 unmarked,
sits somewhere on pages 3 to 5, and is cited as `3-5`; every rule cited with a
range goes under `manual_review_items`, so a person with the source document
can narrow it. The page script places quoted wording for you:

```bash
<page-script> "<doc path>" "<exact wording>"
```

It prints `Page 4` or `Pages 3-5`. When the wording is not found, take the page
from the nearest marker above the text by eye.

A converted file with no page markers at all gives a rule no page to cite.
There, `source_page` is the heading the rule sits under and the description's
anchor ends with that heading, and the import check holds no row of that
document to a page.

Struck-through text, `~~like this~~` in the converted file, is behavior the
document removed. Each struck-through span that states behavior becomes a rule
of its own, written as the behavior it described, with a `change_summary` that
starts "Retired:" and says it was removed and where it sat. It takes the next
number in document order, cites the page of the struck text, and is never
merged into a rule the live text carries. Struck old text beside live text
that changes or restates the same behavior is one rule, the live one, with no
retired row. A
span that only corrects wording, or that the live text repeats unchanged, is not a
retired rule.

A struck-through row is classified `new`, and the rule store reads the "Retired:" marker
on it: approval inserts the row with `status` `retired`, counted as `new_retired`
rather than `new`. The workbook leaves it off the Business Rules sheet, so the removed
behavior is never uploaded as a live rule, and names its rule ID in the Extraction QA
row for struck-through rules approved as retired. The review states how many such rows
the batch holds.

The converted files carry no images, and whatever a screenshot said is not in
the repository copy. A document with a screen print or image section gets that
section named under `manual_review_items` and `screenshots_reviewed: false`, so
a person with the source document knows what is left.

## 4. Write the import

To `<import-file>`:

```json
{
  "doc": "<docs-root>/<suite>/ABC1.2.1-Select-Date.md",
  "prefix": "<prefix>",
  "kind": "extract",
  "note": "first extraction, revised 2007-02-12 per the provenance block",
  "qa": {
    "sections_reviewed": 6, "rules_extracted": 27,
    "by_category": { "Workflow": 7, "Conditional Display": 7 },
    "sections_without_rules": ["Screen Print (if applicable)"],
    "duplicates_merged": 6, "screenshots_reviewed": false,
    "manual_review_items": ["<prefix>-010 and -027 list different tracks"],
    "completed": true
  },
  "rows": [
    {
      "rule_id": "<prefix>-001", "classification": "new",
      "path": "ABC1.2.1 Select Date", "requirement_type": "Business Rule",
      "rule_category": "Workflow", "name": "<prefix>-001 - Date Before Questions",
      "description": "(Brief Description of Process, Page 1) \"...\" Atomic Summary: System requires ...",
      "source_document": "ABC1.2.1 Select Date",
      "source_page": "1",
      "rule_summary": "System requires ...", "risk_level": "High",
      "change_summary": ""
    }
  ]
}
```

Column by column, per the procedure:

- `path` and `source_document` are the document title, the `#` heading of the
  converted file, which is the folder the rules will be created under. A
  `<workbook-docs>` document's title is its file name too, whatever folder the
  file sits in.
- `requirement_type` is `Business Rule`.
- `rule_category` is one of: Validation, Workflow, State Transition, Security,
  Batch, Reporting, Event Generation, Conditional Display, Navigation,
  Integration, Data Integrity, Calculation, Notification, Role Restriction,
  Timing/Temporal. Display content (which columns a grid shows, how a field is
  formatted) is `Data Integrity`, as the rules already in `<rule-tool>` have it.
- `name` is `<rule_id> - <short title>`.
- `description` is `(<anchor>, <heading>, Page <N>) "<exact wording>" Atomic
  Summary: <behavior>`, with line breaks replaced by spaces, and `Pages 3-5`
  in place of `Page <N>` for a range. The anchor is the most
  specific the document offers, in this order: numbered rule, requirement ID,
  table name, table row, section, subsection, bullet, unanchored text. Never
  an invented one. Error messages and conditions are kept word for word.
- `source_page` is the page the rule was taken from, `4`, or the range, `3-5`,
  the same reference the description's anchor ends with, or the heading for a
  file with no page markers.
- `rule_summary` is the one-sentence system behavior.
- `risk_level`: `High` for workflow that changes data or state, security, role
  restriction, batch, integration, timing, and legal rules; `Medium` for
  validation, conditional logic, reporting, and calculation; `Low` for display
  and informational rules.
- `classification` is `new` on every row, `change_summary` is empty except on a
  retired rule, where it starts "Retired:", and no row carries a
  `business_rule_id`.

`qa` holds the Extraction QA counts: sections reviewed, rules extracted, the
count by category, sections with no rule, duplicates merged, whether
screenshots were reviewed, the items a person should read, and whether the
extraction is complete.

## 5. Check

```bash
<import-check> <import> <scratchpad>/export.json
```

It names every problem: a column missing, an ID out of sequence or used twice,
a row not classified `new`, a category outside the list, a `path` or
`source_document` that is not the title, a value longer than the `<rule-tool>`
field it fills (`<field-limits>`), a `source_page` that is not a page number or
range, or a description anchor that does not end with that page. Fix the file
until it prints no problems. The same check runs again when the file is staged.

## 6. Second pass

Read the document once more against the rows: no numbered rule, table row,
bullet, cue, release condition, timing rule, or derived field skipped, and the
appendix and requirements table covered. Anything found goes into the file
before it is reviewed, and anything that reads two ways goes under
`manual_review_items`.

## 7. Review before staging

Nothing is staged while the rows can still change. A batch is a fixed copy of
the file, so every fix made after staging leaves the batch stale and means a
reject and a restage. The rows change during `<self-review>`, and again when the
user reads the workbook, so both come first.

Commit and push the import file, so the pull request shows it whole. Then
build the review workbook from the file itself, with the gate export from step
2:

```bash
<preview-script> "<import path>" <scratchpad>/export.json <scratchpad>/workbooks
```

It runs `<import-check>` first and writes nothing for a file with problems.
Otherwise it prints the path of a workbook with the `Business Rules` and
`Extraction QA` sheets that `<workbook-command>` writes once the file is staged,
in the layout `<workbook-format>` fixes. The one difference is Path on a
`<tool-docs>` document: the preview leaves out the `<rule-tool>` folder chain
the store adds in front, and says so.

Hand the workbook to the user and report the row count, the
`manual_review_items`, and the workbook's path. A row the user wants changed
or dropped is changed or dropped in the import file, renumbering from the
first gap so the IDs run without one. A renumbered rule's `name` and every
rule ID `manual_review_items` names move with it; the check catches a stale
`name`, but nothing checks the review items. Then the check and the preview
run again. Each round is a commit on the branch and a fresh workbook. The step
ends when the user says the review is complete. A question about the workbook,
such as where the file is, does not complete it.

For a run over many documents, each document is reviewed the same way, and
the whole set is staged together only once every workbook in it is accepted.

## 8. Stage

Once the user has said the review is complete, and with the reviewed file
pushed:

```bash
<stage-command> --file "<import path>"
```

The file is read from `<staging-source>`, so an uncommitted file is not there. A
run of several documents stages them in one call with `--file` followed by each
file or by a pattern, and the result has one line per file; `<workbook-command>`
with the ids from those lines then exports them all, per `<update-lists>`. The
result names the batch id and the row count. Export the batch's workbook, per
"Export the workbook" below, as the record of what was staged, and report the
batch id beside it. The batch stays pending until the user asks for approval.

## Export the workbook

```bash
<workbook-command> <id> --out <scratchpad>
```

The staged batch's workbook carries the same sheets as the review workbook,
with Path in full for a `<tool-docs>` document. `Business Rules` leaves out the
rows a reviewer rejected with the row review command, so after a row review
export the batch again and hand over the new file. `<update-export>` says what
the export refuses and how it builds Path. For a `<tool-docs>` document, the
user uploads the workbook to `<rule-tool>` by hand once the batch is approved, the
`--doc` workbook when the batch held struck-through rows.

## Review, approval, and what approval does

The rows are reviewed in the import file before staging, per step 7. After
staging, the reviewer can still read the batch with `<store-read>`, and
`<review-commands>` are `<update-skill>`'s and work the same way here. A row
rejected with the row review command stays in the import file, so a change found
after staging is better made in the file and restaged than rejected row by row.
Approving an extract batch inserts every row not rejected into `<master-table>`
with no `<tool-id-column>`, and adds the document, its prefix, and
`<extract-match>` to `<doc-map>`. A rejected batch registers nothing, so the
document can be extracted again.

Approval happens only when the user asks for it. An approval cannot be undone;
a correction is another import.
