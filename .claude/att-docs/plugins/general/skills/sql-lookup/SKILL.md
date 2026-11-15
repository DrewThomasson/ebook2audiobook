---
name: sql-lookup
description: >-
  Look up real table, column and procedure names in the checked-in schema reference before
  writing any SQL, then, when a fact about the data is the question, run the confirmed
  read-only query on a runner and read the rows back. Use whenever a task requires writing
  or editing a SQL query, not just when asked to check a schema, and before adding a
  diagnostic column or log line to a shared query only to learn something about the data.
---

# SQL Lookup

Never write SQL against guessed table or column names, even when flagged as a guess. The
repository keeps a checked-in schema reference, and names are always confirmed there first.

## Placeholders

The repository's extension fills these in. A placeholder the extension leaves out is not
applicable in that repository, and only the part that depends on it is skipped: the rules
around it still hold. Where a placeholder names a command, the extension also names its
arguments and exit codes, since this skill does not ship the helpers.

| Placeholder | Meaning |
| --- | --- |
| `<asking-note>` | The repository's note on how a question is put to the user |
| `<shell-text-note>` | The repository's note on passing queries and other text to a command as files |
| `<schema-reference>` | The folders that hold the schema reference, one per database, with each database's owner or account and what the folder does and does not hold |
| `<schema-layout>` | How a reference folder is organized: the object type folders, its index files, and what each object's page lists |
| `<schema-generation>` | How a missing reference folder is produced, and the command that does it |
| `<process-docs>` | The documents that describe the rules an application applies over the tables, and the index that finds them by module |
| `<database-accounts>` | The logons the lookup can use, which reference folder each reads, the default, any database the lookup cannot reach, and which suites reach a database of their own |
| `<discovery-hints>` | The note on hint confirm queries for queries that pick test data |
| `<probe-precision>` | The note on confirming a condition added because a discovery walk rejected candidates |
| `<lookup-command>` | The command that runs a confirmed query on a runner: its arguments, how it picks the ref and the account, its detach option and what that prints, and its local checks, if it has any |
| `<lookup-limits>` | What the runner accepts: the statements allowed, the columns that may appear in the query and in the result, the row cap, the call timeout, the session's read-only settings, where the runner gets its connection settings, and the wording of a refusal |
| `<run-watch>` | The ledger and the one watcher that report runs, and how a detached run is recorded |
| `<run-log>` | How a finished run's job log is read to get the rows |

## 1. Find the object type folder

Pick the reference folder for the database the query runs against, per `<schema-reference>`.
A query written for a suite that reaches a database of its own is confirmed against that
suite's folder, not against the default one. A table can sit in one database under an
account with its own grants; confirm it in the folder `<database-accounts>` ties to that
account and run it with that account.

A folder that is not there yet is produced per `<schema-generation>` rather than guessed
around. Start from the folder's index when the object type is unsure, per `<schema-layout>`.

## 2. Look up the specific object

Each object has its own page, laid out per `<schema-layout>`. The page must list the
object's columns with their data types, and its primary and foreign key constraints with the
columns they cover. Without those, step 3 cannot confirm a type or a join.

Find a page with a targeted `grep -rl "<name>" "<type folder>"` when the exact name or
casing is unknown, rather than opening files one by one.

## 3. Confirm before writing SQL

- Reference only column names that appear in that object's column list, with the exact data
  type for any literal comparison or cast.
- Join only on columns a foreign key or primary key row confirms. Never infer a join column
  from a naming convention.
- When the object is not found under the database's folder, say so and ask the user with
  `AskUserQuestion`, per `<asking-note>`, rather than guessing or inventing a schema. An
  object type the reference does not hold, such as a package or a trigger, is asked about
  the same way.
- Do not read whole large pages when a targeted `grep` or section read answers the question.

A query that picks test data also gets a hint confirm query built from the same confirmed
columns, per `<discovery-hints>`, and the columns that query pins are confirmed the same
way.

A condition added because a walk rejected candidates is confirmed here before it goes in the
query, per `<probe-precision>`. A condition on a guessed column is the same guess the walk
was making, moved somewhere it is harder to see.

## 4. When the schema page does not say what a column means

The reference names objects; it does not always explain them. The documents in
`<process-docs>` carry the rules the application applies over those tables: what a code
decodes to, which business function gates a read, when a row is written, and which stage a
process considers open. Grep there for the meaning, then confirm every name it mentions
against the reference before it reaches a query.

## 5. Run the confirmed query on a runner

When the database is reachable only from the runners and the question is a fact about the
data (why a case drops out of a report, which rows a stage holds, what a code is set to),
run the query through `<lookup-command>` instead of adding a diagnostic column or a log line
to a shared query and dispatching a spec to read it. That route costs a code change, a push
and a spec dispatch, and it leaves the diagnostic behind in shared code.

Confirm every name through steps 1 to 3 first. Then write the query to a file in the
scratchpad and pass the path, per `<shell-text-note>`. A database `<database-accounts>`
says the lookup cannot reach is a schema reference only; its queries are not run.

The command dispatches the run, waits, and prints the rows with a header. A long wait goes
through the ledger instead: the detach option prints the run id, which is recorded per
`<run-watch>`, and the rows are read afterwards per `<run-log>`.

`<lookup-limits>` says what the runner accepts. Check the query against it before sending:

- The statements the limits allow, and nothing else.
- Only the columns the limits allow, wherever they appear in the text and in the result,
  including a table or column alias spelled like a refused one. Pick another alias.
- No more rows than the cap, within the call timeout. When the limits refuse a query over
  the cap rather than cut it short, bound the driving scan the way discovery queries do.
- The session's read-only settings, as the limits describe them.

When the command has a local check, it runs against the same reference before it dispatches,
so most refusals come back at once and send nothing. Errors from the database and anything
the limits say is settled only on the runner are not caught there. A refusal on the runner
fails the run and prints the line that says why. Rewrite the query rather
than looking for a way around the check: the rows land in the run log, which is why personal
data and free-text columns never reach it.

The lookup runs no test data discovery methods and writes nothing. A query that proves a
discovery condition still lands on the discovery helper, per `<probe-precision>`.
