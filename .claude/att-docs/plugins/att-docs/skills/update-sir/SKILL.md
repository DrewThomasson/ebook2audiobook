---
name: update-sir
description: >-
  Change a SIR that is already in ALM, by its number, over the same REST interface the
  read skill uses - set its SIR Status, Build, Severity, Type or owner, add a comment to
  its thread, or correct a Draft's title and description - without opening the desktop
  client. Always dry runs first and sends only after the user confirms. Use when asked to
  update, change, move, comment on, withdraw, or set the status of a SIR in ALM.
---

# Update SIR

Changes one existing SIR in ALM and reads it back. It writes to ALM and to nothing else: the
SIR's record under `<records-root>` follows from ALM on the next `<housekeeping-skill>` sweep,
which is the one place that moves it.

| Placeholder | Meaning |
| --- | --- |
| `<alm-project>` | The ALM domain and project the SIRs live in, and why the project is fixed |
| `<alm-host>` | The ALM server the script must be able to reach |
| `<update-script>` | The command that runs the update script |
| `<read-script>` | The command that runs the read script |
| `<submit-flags>` | The flags that turn a dry run into a send, carrying the version stamp |
| `<field-map>` | Each change the script takes: its flag, the ALM field it sets, and any limit |
| `<status-values>` | The command that prints the `SIR Status` values the project holds |
| `<build-values>` | The command that prints the `Build` values the project holds |
| `<editable-status>` | The status while which a SIR's title and description may change |
| `<settable-statuses>` | The statuses this side sets, and what each one means |
| `<not-settable>` | The fields `--set` refuses because ALM keeps them for itself |
| `<account-env>` | Where the ALM account name comes from, and the blank password |
| `<records-root>` | Where the SIR records live |
| `<records-note>` | The repository's note on how a record is laid out and moved |
| `<housekeeping-skill>` | The skill that brings the records back in line with ALM |
| `<status-map>` | Where the `SIR Status` values are listed and what each one means |
| `<withdrawal-note>` | The repository's note on recording a withdrawn SIR |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing text to a command as a file |
| `<writing-rules>` | The gate for text that ships, and the text it leaves alone |
| `<scratchpad>` | The session's scratch directory for the comment and description files |

The SIRs live in `<alm-project>`, fixed in the shared client for the reason the read skill
gives: another project holds unrelated defects under the same numbers.

ALM is the user's, and so is every message to the dev team. This skill runs only when the
user asks for a change to a SIR. No other skill calls it on its own: the retest skill
produces a status and a comment, and the user decides whether this skill sends them.

## Running it

Every change starts as a dry run, which reads the SIR, checks each value against the
project, prints each field as it is and as it would be, and writes nothing. Run
`<update-script>` with the SIR number and the changes, such as a status and a comment file.
Write the comment or description to a file in `<scratchpad>` first, per `<shell-text-note>`.

The last line of the dry run names the version stamp the SIR was read at. Show the whole dry
run output to the user in a fenced block, then ask whether to send it, per `<asking-note>`,
with **Send it** and **Do not send** as the options. On a yes, run the same command with
`<submit-flags>`, where the stamp is the one the dry run printed.

A yes covers that one send. A second change, or the same one after a refused send, goes
through its own dry run and its own question.

`<field-map>` lists what the script changes: the status, the build, the severity, the type,
the owner, any other editable field by name or label, a comment, and, on a `<editable-status>`
SIR only, the title and the description. A comment is appended to the thread. A description is
formatted the way the raise skill formats a record. A title keeps its area prefix.

A value a lookup field's list does not hold is refused with the list, as is a field ALM marks
read-only. `<status-values>` prints the status list and `<build-values>` the build list. The
script refuses the fields in `<not-settable>` and the three that have a flag of their own.

Exit codes follow the read skill: 2 when the server was never reached, 1 for every refusal.
Both say what was refused and whether anything was sent.

## What a send does

1. Signs in the way the read skill does.
2. Reads the lock. A SIR that someone has open in the ALM client is refused with nothing
   sent. Otherwise the script locks it, and unlocks it on the way out whatever happened in
   between.
3. Reads the SIR again under the lock and compares its version stamp with the stamp the
   send carries. A SIR that moved since the dry run is refused with nothing sent, because
   the dry run the user approved no longer describes what would change. Run the dry run
   again and ask again.
4. One `PUT /defects/<id>` carrying every changed field, as XML, through the shared client's
   `putDefect`.
5. Reads the SIR back and checks that each field holds what was sent and that the thread
   grew. A read that disagrees exits 1 and says which field.

A send that resets partway is not retried: the client retries a write only when nothing
reached the server. Read the SIR with `<read-script>` before sending anything again, since
the first send may have landed.

## Comments

A comment is added to the end of the thread, where ALM puts the newest, headed the way the
ALM client heads one: the user's full name from ALM, their login, and the date as
`M/d/yyyy[M/d/yyyy]:`, with the rule of underscores above it when the thread already holds a
comment. That header is what `<housekeeping-skill>` reads a thread by, so a comment sent here
reads back the same as one typed into the client. The thread is read under the lock and the
comment goes on the end of that copy, so a dev comment posted before the send is kept.

The file holds plain text: no markup, no Markdown. Line breaks are kept. Before it goes to
ALM:

- A retest comment passes the text gate in `<writing-rules>`. A SIR's title and description
  sit outside it, as `<writing-rules>` says.
- A retest comment follows the retest skill's rules for the comment it writes: no date, no
  SIR number, no status name, facts in the order they were measured.
- Every comment is signed by the account named in `<account-env>`, which is the user's, so
  the text reads as theirs.
- ALM keeps text in Windows-1252 and saves any character that code page lacks as `?`, such
  as the arrow 🡪 or the circle ⚫. A comment and a Draft's description are HTML, so the
  script writes such a character there as a numeric entity, which ALM keeps. Any other field
  holding one is refused in the dry run.

## Text stays as submitted

A SIR's short and long descriptions change only while its `SIR Status` is `<editable-status>`.
Once the dev team has it, its text stays as it went in, and anything to add goes on as a
comment. The script refuses a title or description change on any other status.

A `<editable-status>` SIR corrected here still has its record under `<records-root>` holding
the old text, so correct the record in the same pass, per `<records-note>`, so the two read
the same.

## Which statuses this side sets

The `SIR Status` values, and what each one means, are in `<status-map>`. Most of them are
the dev team's to set. The ones this side sets, and only on the user's say-so, are
`<settable-statuses>`. A withdrawal's record side is in `<withdrawal-note>`.

Any other value is set only when the user names it. The dry run says that the record follows
on the next sweep.

## After a send

Run `<housekeeping-skill>`, or tell the user to, so the record catches up with what ALM now
says. This skill never moves it, which keeps a single path from ALM to the records.

Read the SIR back with `<read-script>` and its number when the user wants to see it whole.

## Credentials and limits

The same as the read skill: the account in `<account-env>`, a blank password, and a machine
that can reach `<alm-host>`. Attachments are not handled.
