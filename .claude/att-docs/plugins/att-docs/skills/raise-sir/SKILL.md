---
name: raise-sir
description: >-
  File one SIR from its record into ALM, over the REST interface, without opening the
  desktop client. Moves the record to raised and regenerates the SIR index. Use when asked
  to raise, file, submit, or open a SIR, once a record that has been checked by hand still
  reads as not raised.
---

# Raise SIR

Creates one defect in ALM from a SIR record under `<records-root>` and writes the number it
gets back onto that record. The SIRs live in `<alm-project>`, fixed in the shared client,
because a neighboring project in the same domain holds unrelated defects under the same
numbers.

A SIR goes in as `New`, which is where the dev team's triage picks it up. `Draft` holds one
back instead, out of that queue, for a record that wants more research before anyone reads
it; its author moves it on in the ALM client. The script takes neither as a default, so the
choice is always made rather than assumed.

| Placeholder | Meaning |
| --- | --- |
| `<alm-project>` | The ALM domain and project SIRs live in, and why the client fixes them |
| `<records-root>` | The folder that holds the SIR records, one subfolder per application |
| `<records-note>` | The note on the record lifecycle: the queues and the index |
| `<record-states>` | The record states and file names: raisable, awaiting hand check, raised |
| `<raise-gate>` | What a record must show to be taken: file name, markers, title block |
| `<validate-skill>` | The skill that validates a defect and leaves a record awaiting hand check |
| `<hand-check-skill>` | The skill that takes the user through the hand check and records it |
| `<housekeeping-skill>` | The skill that reads ALM back into the records and impacted tests |
| `<raise-script>` | The command that runs the raise script |
| `<create-statuses>` | The statuses a SIR may be created with, and the other status values |
| `<asking-note>` | The note on how a question is put to the user |
| `<build-values>` | The command that lists the project's Build values, and how many |
| `<no-build-value>` | The Build value for a SIR that rides no release because no build is cut |
| `<non-build-value>` | The Build value for a SIR about tooling or a document |
| `<type-severity-defaults>` | The default Type and Severity, their flags, and the Type values |
| `<field-map>` | The ALM field names behind the fields the script sends, and the required set |
| `<record-format>` | How the record holds its title and long description, and who finds them |
| `<renderer-note>` | What the renderer emits for each kind of line in the long description |
| `<writing-rules>` | The note on how shipped text and record text are written and laid out |
| `<raised-form>` | Every change a create makes to the record, its file name, and the index lines |
| `<record-test>` | The command that checks the record rewrite against the index's record checks |
| `<index-command>` | The command that regenerates the SIR index |
| `<account-env>` | Where the ALM account is read from, and what it takes to sign in |
| `<read-script>` | The command that reads a SIR back out of ALM by its number |

## 1. Before raising anything

The record has to be a raisable record, or an awaiting-hand-check one under the unverified
flag, that still reads as not raised, as `<record-states>` and `<raise-gate>` name them. The
script refuses any other file name, and a record that carries a number already.

`<validate-skill>` leaves an awaiting-hand-check record, and those records are the user's
queue for reproducing the SIR by hand and reading its text before ALM sees it, per
`<records-note>`. `<hand-check-skill>` takes the user through that check, writes the
record's hand-check line, and moves it to the raisable state, and the script refuses an
awaiting-hand-check record. When the user vetted the SIR some other way and says so, the
unverified flag files an awaiting-hand-check record anyway, and the report says no hand
check is recorded.
Only the user starts a raise. This skill never raises a SIR the user has not asked for by
name, including from a loop or an unattended run.

A record's text sits outside the `<writing-rules>` scan, per its section 4.1, and once it
has gone to the dev team it stays as submitted.

## 2. Asking which status

Ask which of the two a SIR goes in as, per `<asking-note>`, and recommend `New`:

- **New**, the recommendation. The SIR is ready for the dev team to triage, which is true
  of any record that has been through `<validate-skill>` and the user's hand vet.
- **Draft**. Something about the record is still open, and it should sit where nobody picks
  it up until that is settled.

The answer goes to the status flag. The script refuses a run without one rather than
picking, and takes no other value: `<create-statuses>` names the statuses a SIR may start
with, and the other values of the status list are where a SIR gets to later, through the dev
team and `<housekeeping-skill>`, not where one starts.

## 3. Asking which build

`Build` is required on a create and the project holds many values, so the script takes it as
an argument rather than choosing. Ask the user which one, per `<asking-note>`, and suggest
the one that fits rather than offering a bare list:

- No build is being cut for the application, so the SIR is not riding a release:
  `<no-build-value>`.
- The SIR is about tooling or a document rather than the application: `<non-build-value>`.
- A build is in flight and the SIR belongs to it: that build's own value.

Read the values off the project rather than from this page, which is a copy and goes
stale, with `<build-values>`.

`Type` and `Severity` take the defaults in `<type-severity-defaults>`. Both flags are
checked against the project's own lists before anything is sent, so a value the list does
not hold is named here rather than refused by ALM with a message that says neither the field
nor the value.

## 4. Running it

The dry run is the default and writes nothing, on either side:

```bash
<raise-script> <record> --build "<build>" --status <status>
```

It prints the required fields and the long description exactly as ALM will store it. Read
that output back to the user and get a yes before adding `--submit`, which is the call that
files it.

A run that cannot reach the server exits 2 and says so in one line. Every other refusal
exits 1: a record already carrying a number, a record that is not in a state the script
raises, an awaiting-hand-check record without the unverified flag, a raisable record with no
hand-check line, a missing title block, a build the project does not hold, a short
description ALM already has.

## 5. What it sends

The project requires several fields on a create. The script fills all of them, and the
three that are not free text are checked against the project's lists first:

| Field | Where it comes from |
| --- | --- |
| Application | The folder under `<records-root>` named for the application. |
| Build | The build flag, which the user picks. |
| SIR Status | The status flag, which the user picks. |
| Type | The type flag, with the default in `<type-severity-defaults>`. |
| SIR Author | The signed-in user. |
| Creation Date | The day it is raised. |
| Short Description | The application in brackets and the title block, 255 characters at most. |

`<field-map>` gives the ALM field name behind each row.

`Long Description` and `Severity` are not on the required list but are always sent. The long
description comes out of the record's long description block, and the severity is the
default in `<type-severity-defaults>` unless the severity flag names another of the
project's values: a SIR reaches the dev team carrying one either way, so it is set here
rather than left for the author to fill in afterwards.

## 6. The record's two blocks

A record carries its ALM text in two fenced blocks, one for the title and one for the long
description, as `<record-format>` describes. Both are plain text, because the record
is scanned as plain text before it is raised, and the record module is the only place that
knows how to find them.

ALM stores `Long Description` as HTML, in the shape its own client writes: the whole value
wrapped in `<html><body>`, then one `<div>` per line holding a `<font>` and a `<span>`, with
an empty `<div>` for a blank line. The client reads formatting only inside that span, so a
fragment built any other way renders its line breaks and drops its bold.

**The description goes on in a second call.** A create takes the text of a description and
drops the markup in it, leaving one run-on paragraph, so the script creates the SIR and then
sets the description with an update, which takes the document whole. The value has to arrive
as a whole document, wrapper included: ALM will put a wrapper around a bare fragment, and the
field then holds the same markup but the client shows it as text rather than reading it. Read
back over REST the two are indistinguishable, so this is not something a read can check; it
is only visible in the client.

A run says so when the second call fails, because the SIR then holds the create's
unformatted copy and the description has to go on by hand.

`<renderer-note>` is the whole formatting contract: what each kind of record line reaches
ALM as. Every line is escaped first, so text holding an angle bracket arrives as that text.

The short description goes out prefixed with the application in square brackets, such as
`[<APP>]`, and the record's sentence after it. The prefix comes from the folder the record is
filed under, so the record holds the sentence alone and cannot disagree with its own
application. The 255 characters ALM takes cover the prefix.

ALM keeps text in Windows-1252 and saves any character that code page lacks as `?`, such as
an arrow or a filled circle drawn in a source document. The long description is HTML, so the
script writes such a character there as a numeric entity, which ALM keeps. The short
description, the Build, or any other field holding one is refused in the dry run.

How the text itself is laid out, which is what decides where the lines fall, is in section
4.1 of `<writing-rules>`: the application and environment and the logon on the first two
lines, and a control's values inline on the step that names them rather than one to a line.

## 7. Raising the same SIR twice

A create that half succeeded leaves the record still reading as not raised, and a second run
would file the same SIR again. Before it posts anything the script asks ALM whether it
already holds that exact short description, and stops with the numbers it found if it does.

## 8. What a create leaves behind

On a create that lands, the record moves to raised in every place it is read, as
`<raised-form>` lists. The state line and the file-name prefix move together, so a record
cannot be raised by one reading and not the other.

The script then GETs the new SIR from ALM and writes the things the index needs from every
numbered record, as `<raised-form>` names them. When that GET fails, the author line holds
the signed-in username and the status sentence quotes the status the run sent, and the run
says so. `<housekeeping-skill>` rewrites both from ALM on its next pass.

The record keeps its own line endings, so a CRLF record stays CRLF on every line.
`<record-test>` checks the rewrite against the index's own record checks.

The file name is the pairing of SIR and record: its raised prefix and the number are how
`<housekeeping-skill>` finds which record a SIR number belongs to, since ALM holds nothing
that points back to the records.

Then the script regenerates the SIR index, so the index goes into the same commit as the
renamed record, per `<records-note>`. A regeneration that fails stops the run with the SIR
raised and the record moved, and says to run it by hand with `<index-command>`.

A dry run touches neither the record nor the index.

Filling in the record's impacted tests is `<housekeeping-skill>`'s side of it.

## 9. Credentials

The account comes from `<account-env>`. Nothing else is set for the script to sign in.

## 10. Reading it back

The read skill is the other end: once a SIR is raised, its number reads back with
`<read-script> <number>`.

A SIR raised as a draft comes back with `SIR Status: Draft` and `Bug Status: New`.
`Bug Status` is ALM's own workflow field and sits at `New` on everything, so `SIR Status` is
the one that says where a SIR actually is.
