---
name: doc-impact
description: Review what changed in a repository's converted specification documents against the automation test plans, the manual test cases, and the specs built on them, and file an issue for every plan and test case update the change needs and for every business rule set it leaves due for a refresh, and check uploaded business rule folders for drift from the master. Use after a pull request that changes a converted document merges, from a scheduled document scan as a catch-up, or by hand on an open conversion pull request.
---

# Doc Impact

A converted document is the rule set its test plans were written from. When a
revision lands in `<docs-root>`, the plans, the manual test cases, and the spec
titles written against the old text keep asserting the old rule until someone
notices. This skill is the someone: it reads what the revision changed, finds
what depends on it, decides what each dependent needs, and files the work.

```
/doc-impact <pr>     an open pull request, before it merges
/doc-impact          <main-ref> since the last reviewed commit
```

It files issues and writes nothing else, save the `<rule-tool>` location of each
uploaded business rule that step 6 records. It never edits a plan, a manual test
case, a spec, or a document; `<work-skill>` does that on the issue this files.

The consuming repository's extension supplies the values below. Where it names
none, ask the user rather than guessing. A step whose values the extension
leaves out on purpose, such as a repository with no `<rule-tool>`, is skipped
and the report says so.

| Placeholder | Meaning |
| --- | --- |
| `<impact-script>` | The script behind every step: `changes`, `rules`, `drift`, `record`, `unresolved`, `state`. It ships in this folder as `docimpact.py`, run as `python3 docimpact.py --config <impact-config> <subcommand>`, with its fixture cases in `docimpact_test.py` |
| `<impact-config>` | The `extension.json` that names the roots, the plan and notes names, the ID patterns, `<main-ref>`, and the drift issue's title, marker, and fix commands |
| `<state-file>` | Where `<impact-script>` keeps the reviewed record, outside the repository |
| `<main-ref>` | The remote main branch a bare run reviews |
| `<scratchpad>` | A scratch directory outside the repository for the JSON each step writes |
| `<docs-root>` | Where converted documents live, one folder per suite |
| `<future-folder>` | The folder under a suite that holds revisions the app does not carry yet |
| `<legacy-citations>` | Older path layouts and links a plan may still cite a document by |
| `<tests-root>` | Where a feature's specs and its plan live |
| `<plan-name>` | File name pattern for a plan |
| `<notes-name>` | File name of a suite's automation notes |
| `<rule-id>` | Pattern of a business rule ID |
| `<manual-id>` | Pattern of a manual test case ID |
| `<window-id>` | Pattern of a screen or window code a plan or manual pack may name |
| `<issue-rules>` | The issue conventions: title form, labels, same-name check, acceptance criteria |
| `<plan-labels>` | Labels on a plan update issue |
| `<rule-labels>` | Title slot and labels on a business rule issue |
| `<future-label>` | Label on work that waits for a revision to migrate |
| `<plan-marker>` | Marker line of a plan finding, naming document and blob |
| `<rules-marker>` | Marker line of a business rule refresh issue |
| `<drift-marker>` | Marker line `<impact-script> drift` ends an item's body on |
| `<marker-search>` | How to search every issue, open and closed, for a marker |
| `<watch-skill>` | The scheduled document scan that ends with a bare run |
| `<work-skill>` | What works an issue this files |
| `<rule-store>` | The working master of the business rules |
| `<rule-map-command>` | What reads the document map from `<rule-store>` |
| `<rule-update-skill>` | What refreshes a document's rules in `<rule-store>` |
| `<rule-extract-skill>` | What extracts a document's rules for the first time |
| `<rule-tool>` | Where approved rules are uploaded for test management |
| `<staging-folder>` | The folder in `<rule-tool>` that uploads land in |
| `<rule-upload>` | What uploads approved rules to `<rule-tool>`, and its resend form |
| `<drift-command>` | What reads the uploaded folders from `<rule-tool>` |
| `<hand-loaded>` | Rule folders in `<rule-tool>` loaded by hand, left out of the drift check |
| `<change-record>` | The change request a `future` revision belongs to, and how to read it |
| `<defect-record>` | The record of an app defect, which this skill never writes |
| `<deviation-rule>` | The check a spec that goes red against a changed rule meets |

## When it runs

- **After a merge.** A merged pull request that changed a converted document
  owes this review. Run the bare `/doc-impact` after the merge.
- **The scheduled scan.** `<watch-skill>` ends with the bare `/doc-impact`,
  which catches a conversion that merged some other way.
- **Before a merge, by hand.** `/doc-impact <pr>` reviews an open pull request,
  so a conversion can be checked against the plans before it lands. A pull
  request review marks each document it covered with the blob it read, and the
  post-merge run passes over any document whose blob still matches.

## The reviewed record

The reviewed record lives at `<state-file>`, outside the repository. It holds
the last reviewed `<main-ref>` commit and every document blob a review covered.
The issues this skill files are the second record: each item carries a marker
naming the document and blob, so a lost state file costs a repeated read, never
a duplicate issue.

## 1. Read what changed

Any checkout of the repository will do, however stale: the script fetches,
then reads the documents, the plans, and the spec paths from git at the
revision under review, never from the working tree. A pull request review reads
the pull request's head, so a plan the pull request adds is in the index.

```bash
<impact-script> changes --pr <pr> > <scratchpad>/changes.json
<impact-script> changes --since-watermark > <scratchpad>/changes.json
```

`first_run: true` means no review has run on this machine yet. Nothing is
reviewed; record the result (step 7) so the next run starts from here, and say
so in the report.

Each entry in `documents` is one converted document:

| Field | Holds |
|---|---|
| `status` | `A` added, `M` changed, `R` renamed, `D` removed |
| `key` | what the record and the issue marker name: the blob reviewed, or `removed-<blob>` for a removal |
| `kind` | `added` or `removed` for a whole document; `content`, `layout`, or `unchanged` for a changed one |
| `hunks` | for `content`: each change as its `section`, every section it runs through (`sections`), the units `removed`, and the units `added` |
| `predecessor` | for a new numbered document, the one it reissues under a new number, when the titles match once the numbers are dropped; for a new `future` document, the suite folder's copy |
| `future` | the document sits in `<future-folder>`: a revision the app does not carry yet |
| `current` | for a `future` document, the suite folder's copy, the version the app follows |
| `dependents` | everything the change reaches, each marked with a `kind` below |

A unit is a heading, a table row, a list item, or a paragraph with its
whitespace collapsed. `layout` means the words are the same and only the
paragraph breaks moved; `unchanged` means only the provenance block moved.
Neither files anything. `reviewed_before` lists the documents an earlier review
already covered at the same blob.

A new document with a `predecessor` is reviewed as a revision: its `kind` is
`content`, its hunks are the difference from the document it reissues, and it
inherits that document's dependents. The plans that covered the old document
cover the new one.

A new `future` document is reviewed the same way against the suite folder's
copy, so its hunks are what the app will change once the work migrates. A later
revision of a `future` document is reviewed against its earlier `future` text,
and reaches the suite folder copy's dependents through `current`. Plans cite the
suite folder's copy, and a citation that names a document with a `future` copy
resolves to the suite folder's copy.

## 2. Find everything that depends on each change

The plans are the `<plan-name>` files under `<tests-root>`, beside the specs they
plan for, and `<impact-script>` indexes them with the documents.

| `kind` | Reached through |
|---|---|
| `plan` | the plan cites the document by path, including `<legacy-citations>` |
| `title` | the plan names the document by its title in prose |
| `number` | the plan names a reissued document's old number; `lines` gives where |
| `window` | a plan, a `<notes-name>`, or a manual test pack names a `<window-id>` the change touches |
| `manual` | a manual `<manual-id>` row cites a `<rule-id>` rule this document is the source of |
| `plan-rule` | a plan row cites one of those `<rule-id>` rules or `<manual-id>` ids |

`plan` and `title` entries carry the plan's specs. A plan row that needs a
change names its matrix ID, and the spec's test titles carry the same ID, so
grep the specs for it to find the test that asserts the rule.

`number` and `window` are the weaker links: a number can be a count and a
window can be named in passing. Read the line before counting either as a
dependent.

A new document that nothing depends on is a coverage gap. Place it with the
spec folder whose feature it describes: the folder whose plan cites a sibling
document from the same library folder, or whose page the document specifies.
One the evidence cannot place goes in the report as unplaced, with what was
checked.

## 3. Decide what each dependent needs

Read each hunk against each dependent and decide, one line per dependent:

- **new row**: the change adds a rule no row covers
- **changed expectation**: a row asserts the old text of a changed rule
- **retired row**: a row asserts a rule the change removed
- **nothing**: the dependent does not touch the changed section

Wording that restates a rule without changing what it requires is `nothing`:
a reordered sentence, a fixed typo, a renamed label that no row quotes. A
changed number, list member, condition, message, or role is a rule change even
when the sentence around it reads the same. When a hunk could be read either
way, file it and say which reading was taken.

Read the whole document for an `added` one, and the plan's own `Documentation
Reviewed` and coverage sections for every dependent. A decision written from the
hunk alone misses the row two sections away that quotes the same rule.

A document change is a change to what the app should do. It is never evidence
that the app does something else, so this skill writes no `<defect-record>`. A
spec that goes red later because the app still follows the old rule meets
`<deviation-rule>` in the run that finds it.

A `future` document says what the app will do, not what it does. Its findings
plan the rows the revision needs once it migrates, and every row that asserts
the suite folder copy's rule keeps asserting it until then. Before filing, read
the `<change-record>` the revision belongs to, and name it in the finding.

## 4. File the work

One issue per spec folder, through `<issue-rules>`: the title convention,
`<plan-labels>`, and the same-spec check that appends to that folder's open
issue instead of opening a second one. A folder whose plan does not exist yet
takes its planned spec name from the `test-plan-from-doc` naming.

Each finding in the body carries:

- the document path and section, and the changed text quoted, removed and added
- the plan rows, `<manual-id>` ids, and spec titles it reaches, and what each
  one needs
- the `<plan-marker>` line naming the document and the first 12 characters of
  the key, where a removal's key keeps its `removed-` prefix

Search for the marker with `<marker-search>` before filing, so a review that
repeats because the state file was lost adds nothing twice.

A pull request review files its issues the same way, and says in each item that
the document is not on the main branch yet. The acceptance criteria of each
issue are the `<issue-rules>` ones for the spec it names. The marker search also
finds the business rule issues step 5 files for the same blob; those carry the
`<rules-marker>` and do not count as a plan item already filed.

An issue whose findings all come from `future` documents also carries the
`<future-label>` label. A spec folder with findings of both kinds gets two
issues, one per kind, so the migrated work is not held behind the work that
waits on a migration.

## 5. Flag the business rules for refresh

The converted documents are the source of truth for the business rules, and
`<rule-store>` is the working master of them. A revision leaves a document's
rules on the old wording until someone runs `<rule-update-skill>` on it, so the
review says which rule sets now need that run.

Skip this step when `changes.json` lists no document at all. Otherwise read the
document map from the store, which names every document with rules whatever
its suite, with `<rule-map-command>` into `<scratchpad>/rule-map.json`, then:

```bash
<impact-script> rules <scratchpad>/changes.json <scratchpad>/rule-map.json \
  > <scratchpad>/rule-refresh.json
```

The map is the same whichever revision is under review. A run that cannot read
the map leaves the review unfinished: report it and do not record (step 7), so
the next run reads these documents again.

Each item in `rule-refresh.json` is one document the map holds:

| Field | Holds |
|---|---|
| `doc`, `map_doc` | the path reviewed, and the path the map names when a rename or a reissue moved it |
| `key` | the blob read, as in step 1 |
| `prefix`, `rules` | the rule ID prefix and how many active rules it holds |
| `kind` | `content`, `removed`, or `layout`/`unchanged` for a rename the map has not followed |
| `changed` | the rules whose anchor sits in the changed text: a numbered rule whose text changed, a requirement number a changed unit quotes, or the section a hunk landed in; every rule for a removal |
| `restarts` | the document numbers its rules again per section, so a numbered match may be another section's rule |
| `future` | the document is a `future` revision, read against the rules of the suite folder's copy |

A document the map does not hold gets no item. Its first extraction is a
choice made through `<rule-extract-skill>`, not something a revision files.
A `layout` or `unchanged` revision gets none either, unless the map still
names the old path.

File one issue per item through `<issue-rules>`, with `<rule-labels>` and the
prefix in the name slot. The same-name check appends a later revision of that
document to the open issue rather than opening a second one. The body names the
document, the blob, the prefix and rule count, the `changed` rule IDs with their
anchors and the hunks that reached them, and the `<rule-update-skill>` call that
does the work. An empty `changed` says the anchors could not place the change,
so the update reads the whole document. Say so, and say when `restarts` is true.
Its marker line is `<rules-marker>`, naming the document, the first 12
characters of the key, and the prefix. Search for it with `<marker-search>`
before filing.

The issue asks for the update; it never stages, approves, or writes to
`<rule-tool>`. An import always waits for review in `<rule-update-skill>`.

A `future` item is not a refresh of the master, which stays on the suite
folder copy's rules until the revision is promoted. Its issue carries the
`<future-label>` label and asks for the revised rules as an entry of their own
under `<staging-folder>` in `<rule-tool>`, named for the suite and the feature,
beside the master's rules rather than over them. The title names the `future`
document, so the same-name check keeps it apart from the suite copy's refresh
issue.

## 6. Check the uploaded rule folders for drift

`<rule-upload>` loads a suite's approved rules into `<rule-tool>`, under
`<staging-folder>`. After that, an edit or a deletion made by hand in
`<rule-tool>` goes unnoticed until the next upload, so every run compares those
folders with the master, whatever step 1 found. `<hand-loaded>` are left out of
the comparison.

Read the uploaded folders with `<drift-command>` into
`<scratchpad>/rule-drift.json`, then:

```bash
<impact-script> drift <scratchpad>/rule-drift.json > <scratchpad>/rule-drift-review.json
```

The drift read never writes to `<rule-tool>` or to a rule's content. It records
where each uploaded rule and document folder now lives, and only where that
changed, so a clean comparison writes nothing. A run that cannot read
`<rule-tool>` leaves the review unfinished, the same as an unread map in step 5.

`rule-drift-review.json` holds:

| Field | Holds |
|---|---|
| `items` | one issue per document folder that differs from the master: `doc`, `prefix`, `title`, `fingerprint`, and the `body` to file |
| `clean` | how many document folders matched |
| `waiting` | per document folder, the approved rules still in `<staging-folder>`, grouped by the day each was uploaded |
| `promoted` | the rules a reviewer moved out of `<staging-folder>` since the last run, with the folder each went to |
| `folders_promoted` | the document folders moved out of `<staging-folder>` since the last run |
| `recorded`, `notes` | how many locations the run recorded, and the documents it left out |

A rule moved out of `<staging-folder>` with its content matching the master is
promoted, which is how the folder is meant to be used. It is listed, never
filed. A rule moved somewhere else inside `<staging-folder>`, deleted from
`<rule-tool>`, or changed in any field is drift, and so is a promoted rule whose
content changed.

File each item through `<issue-rules>`, with `<rule-labels>`, under the item's
`title`. The body is the item's `body` as written. It names each differing rule
and field with the `<rule-tool>` value against the master value, the attachment
hashes, and which way the fix probably goes: resend from the master with the
resend form of `<rule-upload>`, or take a `<rule-tool>` edit a reviewer meant
into the master through `<rule-update-skill>`. It ends on the `<drift-marker>`
line, naming the document, the prefix, and the fingerprint. Search issue bodies
and comments for it with `<marker-search>` before filing.

A hit means this exact drift is already on an issue, so nothing is added. With
no hit, the same-name check finds the document folder's open issue and the body
goes on it as a comment, so a later run extends that issue rather than filing a
second one. With no open issue of that name, file one.

The step never fixes the drift: it does not resend, stage, approve, or move a
rule in `<rule-tool>`.

## 7. Record the review

Once every document is filed, placed, or judged `nothing`, record it:

```bash
<impact-script> record <scratchpad>/changes.json
```

A review of the main branch moves the watermark to the head it read. A pull
request review marks each document's blob and leaves the watermark alone.
Record only a finished review: a document left half-read is picked up again by
the next run only while it stays unrecorded.

## 8. Report

- the range reviewed, and whether it was a first run
- documents by `kind`, with `reviewed_before` counted separately
- each issue filed or extended, with its URL and the documents behind it
- the coverage gaps, placed and unplaced
- the citations that resolved to nothing, from `<impact-script> unresolved`,
  each with the closest current name as a hint for whoever fixes the plan
- each business rule refresh issue filed or extended, with the prefix, or that
  no revised document is in the rule map
- each drift issue filed or extended, with the prefix, or that every uploaded
  document folder matched the master
- the rules still waiting in `<staging-folder>`, per document folder, with the
  day each was uploaded, and the rules and folders promoted since the last run
- the watermark, from `<impact-script> state`

## What this skill never does

- Edit a plan, a manual test case, a spec, or a document.
- Write a `<defect-record>`.
- Stage, approve, or update business rules, or write to `<rule-tool>`. The
  drift check records where a rule lives, never what it says.
- Move a rule out of `<staging-folder>`, or resend one to fix drift.
- Move the watermark past a range it did not finish reviewing.
