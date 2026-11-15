---
name: business-rule-update
description: Update the business rules for one converted document that already has rules, by reading the revised document against a working master of the rules, classifying every rule as unchanged, modified, new, or retired, and staging the result in an import table for review before it is approved into the master. Use when asked to update, refresh, or re-extract the business rules for a document, or to approve or reject a staged import. Also use to load a suite's approved rules and workbooks into the requirements tool.
---

# Business rule update

The business rules the test team keeps in `<rule-tool>` are mirrored into
`<mirror-table>` by `<mirror-skill>`. This skill keeps a working master of them,
`<master-table>`, on the same store, and updates it from the converted
documents one document at a time. Only the upload, below, writes to
`<rule-tool>`, and nothing here writes to `<mirror-table>`.

`<rule-root>` holds rules for `<hand-loaded-suite>` documents only. The other
suites, `<upload-suites>`, keep their specifications under
`<docs-root>/<suite>`, and their rules are codified into the business rule
workbook described in `<workbook-format>`. Such a document's rules start in
the master with `<extract-skill>`, and from then on this skill updates them the
same way it updates a `<hand-loaded-suite>` document's. The upload loads one of
those suites' approved rules into a `<rule-tool>` folder outside `<rule-root>`.

The consuming repository's extension supplies the values below. Where it names
none, ask the user rather than guessing.

| Placeholder | Meaning |
| --- | --- |
| `<rule-tool>` | The requirements tool the test team keeps its business rules in |
| `<rule-root>` | The `<rule-tool>` folder the `<hand-loaded-suite>` rules live under |
| `<mirror-table>` | The store table `<mirror-skill>` copies `<rule-tool>` requirements into |
| `<mirror-skill>` | The skill that refreshes `<mirror-table>` from a `<rule-tool>` folder |
| `<rule-store>` | The database that holds the four tables below |
| `<master-table>` | The working master, one row per rule |
| `<doc-map-table>` | One row per document with rules |
| `<batch-table>` | One row per staged import |
| `<import-table>` | The staged rows of every import |
| `<location-columns>` | The columns that record where an uploaded rule and folder live |
| `<br-command>` | The command that runs every store action: `init`, `map`, `rename`, `docmap`, `export`, `stage`, `workbook`, `review`, `approve`, `reject`, `upload`, `drift` |
| `<stage-source>` | Where `<br-command> stage` reads an import file from |
| `<store-query>` | How a reviewer runs a read-only query on `<rule-store>` |
| `<docs-root>` | Where converted documents live, one folder per suite |
| `<hand-loaded-suite>` | The suite whose rules were seeded from `<rule-root>` and are loaded by hand |
| `<hand-loaded-root>` | The `<docs-root>` folder that holds `<hand-loaded-suite>` documents |
| `<upload-suites>` | The suites whose rules this skill uploads |
| `<rule-id>` | Pattern and example of a rule ID, `<prefix>-<seq>` |
| `<imports-dir>` | The committed folder import files are written to |
| `<check-import>` | The command that checks an import file against its export |
| `<page-tool>` | The script that places a quoted wording on its page |
| `<extract-procedure>` | The first-extraction procedure's section on extracting and placing pages |
| `<extract-skill>` | The skill that extracts a document's rules for the first time |
| `<scan-skill>` | The skill that checks every rule set against its document |
| `<impact-skill>` | The skill that flags a revised document's rules and files drift |
| `<workbook-format>` | The workbook layout, column by column, and the `<rule-tool>` field map |
| `<workbook-name>` | The workbook's file name, and its form inside a list |
| `<update-sheets>` | The sheets an update batch's workbook carries |
| `<extract-sheets>` | The sheets an extract batch's workbook carries |
| `<rules-sheet>` | The sheet that holds the rules themselves |
| `<field-limits>` | The longest value each `<rule-tool>` field takes |
| `<code-page>` | The character set `<rule-tool>` stores text in |
| `<staging-folder>` | The `<rule-tool>` folder uploaded rules wait in for review |
| `<staging-id>` | The id of `<staging-folder>` |
| `<rule-type>` | The requirement type each uploaded rule is created as |
| `<rule-fields>` | The `<rule-tool>` fields each uploaded rule carries |
| `<source-line>` | The provenance line that names a converted document's source |
| `<library-line>` | The provenance line that links the source in the document library |
| `<attachment-source>` | The `<source-line>` form for a source kept as a `<rule-tool>` attachment |
| `<scratchpad>` | A scratch directory outside the repository |

## The tables

All four live on `<rule-store>`, and every read and write below goes through
`<br-command>`.

| Table | Holds |
|---|---|
| `<master-table>` | The working master. One row per rule: `rule_id` (`<rule-id>`), `prefix`, `seq`, the nine matrix columns (`path`, `requirement_type`, `rule_category`, `name`, `description`, `source_document`, `source_page`, `rule_summary`, `risk_level`), `status` (`active`, `retired`, `superseded`), the rule's `<rule-tool>` id (null until `<rule-tool>` holds the rule) and folder, and which batch last changed it. An uploaded rule also carries where it lives: whether it sits in `<staging-folder>`, the day it was uploaded, and the day it was promoted, as the upload section below explains. |
| `<doc-map-table>` | One row per document with rules: `doc_path`, `prefix`, the `<rule-tool>` folder, and how the match was made (`folder-name`, `manual`, `extract`). An uploaded document also carries its staging folder's id, whether that folder sits in `<staging-folder>`, and the day it was promoted. `<br-command> docmap` prints every row with its active rules' IDs and anchors; `<impact-skill>` reads it to flag a revised document's rules for this skill. |
| `<batch-table>` | One row per staged import: the document, the prefix, `kind` (`update`, `extract`), `status` (`pending`, `approved`, `rejected`), the Extraction QA counts as `qa`. |
| `<import-table>` | The staged rows: `rule_id`, `classification`, `business_rule_id` for anything not new, the nine columns, `change_summary`, and `review` (`pending`, `approved`, `rejected`). |

`rule_id` is unique among rows not `superseded`. The seed marks a rule
superseded when a later extraction nested under the same folder repeated its
ID, so the older copy stays readable without taking the ID.

## Setting up, once

```bash
<br-command> init
<br-command> map
```

`init` creates the tables and seeds `<master-table>` from `<mirror-table>`
when it is empty; a second `init` creates nothing and seeds nothing. `map`
matches every top-level folder under `<rule-root>` to the document whose file
name equals the folder name, case and punctuation aside, and prints the
folders it could not place. A folder is placed by hand with
`<br-command> map --doc <path> --folder <id>`; nothing is guessed. `map` reads
`<hand-loaded-root>` alone, since `<rule-root>` holds no other suite's rules.
Those documents reach `<doc-map-table>` when their first extraction is
approved.

A document can be renamed after its rules are in the store.
`<br-command> rename` lists every `<doc-map-table>` and `<batch-table>` path
whose file is gone and whose renamed path holds the same document, by its
`<source-line>`, and `--send` moves them. A path it cannot place is printed
for a hand `map`. A document's title, which names its workbook and its
`<rule-tool>` folder, is the page's H1, so a rename leaves the title as it was.

`<br-command> export --doc "<folder>"`, given a folder rather than a file,
prints `{ "folder": ..., "exports": [...] }`: one export per document
`<doc-map-table>` holds under that folder, nested folders included. That is how
`<scan-skill>` reads a suite's rules in one run.

## Updating one document

1. **Export.** `<br-command> export --doc "<path>" > <scratchpad>/export.json`.
   It refuses a document `<doc-map-table>` does not hold; that document is
   extracted for the first time instead, which is `<extract-skill>`.
2. **Read.** Read the whole revised document, every heading, numbered rule,
   paragraph, table, note, and appendix, and the exported rules. Treat every
   statement as a possible rule.
3. **Classify.** Every exported rule with `status` `active` gets exactly one
   row. Compare on behavior, conditions, timing, workflow, and validation, not
   on wording:
   - `unchanged`: the behavior is the same. The row repeats the export's nine
     columns exactly.
   - `modified`: the behavior changed. The row carries the new columns and
     keeps the `rule_id`. A wording change alone is not a modification.
   - `retired`: the document no longer carries the behavior. The row keeps
     the export's columns. The ID is never reused.
   - Struck-through text, `~~like this~~`, is behavior the document removed.
     Struck old text beside live text that changes that behavior is the live
     rule: `modified` when the export holds it, `new` when not, with no retired
     row. Live text that restates the same behavior is `unchanged`.
     When the behavior is gone and the export holds its rule as active, the row is
     `retired`, and its `change_summary` starts "Retired:" and says where the
     struck text sits. When the export holds no such rule, the span is a `new` row
     written as the behavior it described, with a `change_summary` that starts
     "Retired:". A span the export already holds as `retired`, a span that only
     corrects wording, and a span the live text repeats unchanged get no row.
     The rule store reads the "Retired:" marker on a `new` row: approval inserts it
     with `status` `retired`, counted as `new_retired` rather than `new`, and the
     workbook leaves it off the rules sheet, so the removed behavior is never uploaded
     as a live rule. `qa.new` counts these rows. The review states how many such rows
     the batch holds.
   - `new`: behavior the export does not hold. IDs continue from
     `next_seq` in the export, in order, with no gap. One row is one
     independently testable behavior; a compound statement is split.
4. **Write the import** to `<imports-dir>/<doc stem>-<date>.json`:

   ```json
   {
     "doc": "<docs-root>/<suite>/<document>.md",
     "prefix": "<prefix>",
     "kind": "update",
     "note": "revision 1.4, 2026-09-30",
     "qa": {
       "pages_reviewed": 12, "existing_loaded": 285, "new": 3, "modified": 7,
       "retired": 1, "unchanged": 277, "duplicate_candidates": 0,
       "manual_review_items": ["<prefix>-104: the table on page 9 reads two ways"],
       "completed": true
     },
     "rows": [
       {
         "rule_id": "<prefix>-018", "classification": "modified", "business_rule_id": 412,
         "path": "<document title>", "requirement_type": "Business Rule",
         "rule_category": "Workflow", "name": "<prefix>-018 - Generate Medical Exam Due Cue",
         "description": "(Rule 12, Page 4) \"...\" Atomic Summary: System displays the Medical Exam cue 120 days before the due date.",
         "source_document": "<document title>", "source_page": "4",
         "rule_summary": "System displays the Medical Exam cue 120 days before the due date.",
         "risk_level": "High",
         "change_summary": "90 days became 120 days"
       }
     ]
   }
   ```

   `description` keeps the `(anchor, Page X) "wording" Atomic Summary: ...`
   form with line breaks replaced by spaces, the most specific anchor the
   document offers, never an invented one. `source_page` is the page `X`
   names, `4`, or a range, `3-5`, for text between two page markers with an
   unmarked page between them; the page is placed the way
   `<extract-procedure>` says, with `<page-tool>`, and a range goes under
   `manual_review_items`. A modified row whose rule predates page references
   gets them in the same row. `name` is `<rule_id> - <title>`.
   `risk_level` is `High`, `Medium`, or `Low`. `change_summary` is empty on an
   unchanged row, and on a `retired` row or a struck-through `new` row it starts
   "Retired:".
5. **Check.** `<check-import> <import> <export>`. It names every problem: a
   missing column, an ID out of sequence or used twice, an `unchanged` row that
   differs from the export, a `modified` row that does not, an active rule left
   unclassified, a new or modified value longer than the `<rule-tool>` field it
   fills (`<field-limits>`), a new or modified `source_page` that is not a page
   number or range, an anchor that does not end with it, a "Retired:" summary on
   a `modified` or `unchanged` row, or a summary that opens like the marker but is
   not exactly "Retired:". Fix the file until
   it prints no problems. The same check runs again when the file is staged.
6. **Second pass.** Read the document once more against the rows: no numbered
   rule, table row, cue, release condition, or calculation skipped. Anything
   found goes into the file before it is staged, and anything that reads two
   ways goes under `manual_review_items`.
7. **Stage.** Put the import file where `<stage-source>` says, then
   `<br-command> stage --file "<import path>"`. A file that is not there yet
   is not staged. The result names the batch id and the counts. Then export the
   pending batch's workbook, per "Exporting the workbook" below, and hand the
   file to the user. Report the batch id, the counts, the
   `manual_review_items`, and the workbook's path. The step ends there: the
   batch stays pending until the user has read the workbook and asks for
   approval.

## Exporting the workbook

The workbook is how the user reviews a batch, so it is exported while the
batch is pending, straight after staging, and handed to the user:

```bash
<br-command> workbook --batch 3 --out <scratchpad>
```

It writes `<out>/<workbook-name>` and prints the file's path last. `--out`
defaults to the current directory. Report that path to the user.

An update batch writes `<update-sheets>`; an extract batch writes
`<extract-sheets>`. `<rules-sheet>` holds every row a reviewer did not reject
and that is not retired, so a pending batch's workbook shows what approval
would give. After a `review` call, export the batch again and hand over the
new file. A rejected batch is refused. `<br-command> workbook --doc "<path>"`
writes the document's active rules from the master as `<rules-sheet>` alone,
with no batch behind it. For a `<hand-loaded-suite>` document, the user uploads
the workbook to `<rule-tool>` by hand once the batch is approved, the `--doc`
workbook when the batch held struck-through rows.

A `<hand-loaded-suite>` rule's Path is the `<rule-tool>` folder chain down to
`<rule-root>`, read from `<mirror-table>`, then the rule's own `path`. The
export refuses when the mirror does not hold every folder above `<rule-root>`;
a `<mirror-skill>` run records them. An uploaded suite's Path is the rule's
`path` as the master holds it, since its rules sit outside `<rule-root>`, in
the folder the upload writes. The export also refuses, by rule ID, any value
longer than the `<rule-tool>` field it fills, rather than writing text
`<rule-tool>` would cut. The layout, column by column, is in
`<workbook-format>`.

## Lists

`stage`, `reject`, `approve`, and `workbook --batch` each take a list in one
call, so a set of documents costs one run rather than one per document:

```bash
<br-command> stage --file <dir>/*.json
<br-command> stage --file a.json b.json
<br-command> reject --batch 200,201,202
<br-command> approve --batch 7,9,12
<br-command> workbook --batch 200-244 --out <scratchpad>
```

The result has one line per item, `stage: batch <id> for <doc>` for each file
staged and `<action>: <item> refused: <reason>` for each one refused. An item
is refused on its own problems only; the others still run, the closing line
counts both, and the call exits nonzero when any item was refused. An error
that is not a refusal, such as a lost connection, stops the list at that item
and the lines name it. `approve` and `reject` take batch ids one by one, never
a range: other sessions stage into the same id sequence, so a range can take in
a batch nobody here staged or reviewed. Name each id from its `stage` line. A
`workbook` list only reads, so it takes a range, and it passes over the
rejected batches and the unused ids inside a range with a line each; an id
named outright is still refused. A range can still take in another session's
pending batch, so check the doc named on each workbook line. The action is the
first argument, and `--file` takes every path up to the next option. `--batch`
given more than once adds to the list.

A pattern over `<imports-dir>` takes in every dated import of a doc, and two
files in one list that import the same doc are both refused, so name the
current one. Read the lines for the batch ids before sending a list again: a
staged file already has its batch, and staging it again is refused as pending.
A workbook list writes every workbook it could build and prints each path, and
each file name in a list takes the list form of `<workbook-name>`, ending with
its batch.

## Review and approval

The reviewer reads the batch with `<store-query>`, for example
`SELECT id, rule_id, classification, change_summary FROM <import-table> WHERE batch_id = 3`,
and the pull request shows the import file whole.

```bash
<br-command> review --batch 3 --rows 41,47 --note "page 9 reads the other way"
<br-command> approve --batch 3
<br-command> reject --batch 3
```

`review` rejects the named rows. `approve` applies every row not rejected in
one transaction: a modified row updates the `<master-table>` row in place, a
new row is inserted with no `<rule-tool>` id, as `retired` when its `change_summary`
starts "Retired:" and active otherwise; a retired row sets `status` to
`retired`, an unchanged row changes nothing, and the batch records when it was
decided. `reject` closes the batch with nothing applied. An approval is not
undone; a correction is another import.

Approval happens only when the user asks for it, after reading the batch's
workbook. A question about the workbook, such as where the file is, is not a
request to approve. The skill stages, exports, and reports; the user reads
the workbook and decides.

## Uploading a suite to the rule tool

The upload loads the approved rules of one suite in `<upload-suites>` into
`<rule-tool>`, under `<staging-folder>`:

```
<staging-folder>
  <suite>
    <document title>                         one folder per document with active rules
      <the document's active rules>          <rule-type> requirements
      <workbook-name>                        attachment
      <document title>.url                   attachment
```

Each rule is a `<rule-type>` requirement carrying the fields
`<workbook-format>` maps, `<rule-fields>`. The workbook holds the same bytes
`<br-command> workbook --doc "<path>"` writes. Rules not `active` stay out.

The `.url` file is an Internet shortcut to the source document in the
document library, the link the converted file's provenance block gives on its
`<library-line>`. It is written in the form the shortcuts already under
`<rule-root>` take: UTF-16 with a byte order mark, `[InternetShortcut]` and a
`URL=` line, CRLF line ends. A document whose provenance block has no
`<library-line>` is refused in the dry run, since its folder would carry no
link to the source. The one exception is a source kept as an attachment in
`<rule-tool>`, whose `<source-line>` reads `<attachment-source>`: it has no
place in the library, so its folder carries the workbook alone and the dry run
says so.

`<rule-tool>` keeps text in `<code-page>` and saves any character that code
page lacks as `?`. The description is HTML, so the upload writes such a
character there as a numeric entity, which `<rule-tool>` keeps. A plain text
field holding one is refused in the dry run.

```bash
<br-command> upload --doc <docs-root>/<suite> --folder <staging-id>
<br-command> upload --doc <docs-root>/<suite> --folder <staging-id> --send
```

Without `--send` the run is a dry run: it reads `<rule-tool>` and the master,
prints what a send would create, update, record and attach, and writes
nothing. Without `--folder` it lists the folders named for temp or test and
stops. Run the dry run first and read it; a send writes into `<rule-tool>`, so
it waits for the user to ask for it.

A send looks up everything before it writes, so a second send writes nothing.
A document folder is the one the master records while `<rule-tool>` still
holds it, and otherwise the folder of the document's name under the suite
folder. Rules are found by the `<rule-tool>` id the master holds or by the rule
ID their name opens with, and the workbook and the shortcut by file name and
SHA-256. A rule the master changed since the last send is updated in the
fields that differ, a field the master cleared included, and an attachment
whose bytes changed is replaced. Each created rule's id and folder go into
`<master-table>`'s `<location-columns>` as `<rule-tool>` answers, with the rule
marked as in staging and the day it was uploaded, and each document folder
goes into `<doc-map-table>`. A rule whose `<rule-tool>` id names a requirement
in another folder under `<staging-folder>` is reported and left there.

### The staging folder is staging

`<staging-folder>` is where approved rules wait for review, not where they
stay. A reviewer moves them to their permanent place in `<rule-tool>`, one rule
at a time or a whole document folder at once. Moving is a person's step in
`<rule-tool>`; the tooling never does it. The tooling expects the move and
follows it:

- A rule or document folder found anywhere outside `<staging-folder>` is
  promoted. Its folder column follows it to its new folder, its staging flag
  turns false, and its promoted day holds the day a drift run first found it
  there. The same columns on `<doc-map-table>` record a promoted document
  folder.
- The upload updates a promoted rule where it now lives and names it as
  promoted in the plan. A promoted document folder keeps the workbook and the
  shortcut, and no folder of the same name is made again under
  `<staging-folder>`.
- A new rule always goes to `<staging-folder>` for review. When its document
  folder was promoted, the upload makes a folder of the document's name under
  the suite folder for it, and only then.
- A rule moved to another folder inside `<staging-folder>`, or deleted from
  `<rule-tool>`, is not promoted. The upload leaves the first where it is and
  creates the second again, and the drift check reports both.

Nothing sets a deadline for the move. The drift check lists, per document
folder, the rules still waiting in `<staging-folder>` with the day each was
uploaded.

### Checking the rule tool against the master

```bash
<br-command> drift
```

The drift action reads every suite the master has uploaded, or the one
`--doc` names, and compares `<rule-tool>` with the master. It reports, as one
JSON line, each rule never uploaded or no longer in `<rule-tool>`, each field
whose `<rule-tool>` value differs (both values), each rule moved inside
`<staging-folder>`, the workbook and shortcut whose SHA-256 differs or which is
missing, and any requirement or attachment in the document's folders that no
active rule or file accounts for. It also lists what waits in
`<staging-folder>` and what was promoted since the last run. It never writes to
`<rule-tool>` or to a rule's content. Its one write is where each rule and
document folder lives, and only where that changed, so a second clean run
writes nothing. A run on a store whose rows predate `<location-columns>` reads
the staging folder from the `<staging-folder>`, suite, document layout and the
upload day from each requirement's creation date in `<rule-tool>`.
`<impact-skill>` runs it and files what it finds.

The upload never deletes: a requirement no active rule names, a retired rule,
or an attachment other than the workbook and the shortcut is reported and left
where it is. The run then reads every document folder back and fails unless it
holds one requirement for each rule it placed there, the workbook and the
shortcut each with a matching SHA-256, and nothing else beyond what it reported
and left in place.

To read the result into `<mirror-table>`, run `<mirror-skill>` with the
`<staging-id>` as its root.

## What stays out

The comparison of `<master-table>` against `<mirror-table>` is a later step;
the drift action compares the uploaded folders with `<rule-tool>` itself.
`<hand-loaded-suite>` rules are not uploaded: the user uploads their workbooks
to `<rule-root>` by hand, and the upload refuses a `<hand-loaded-suite>`
document. `<mirror-skill>` keeps rewriting `<mirror-table>` from `<rule-tool>`
and never touches these tables.
