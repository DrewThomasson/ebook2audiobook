---
name: alm-mirror
description: >-
  Copy an ALM requirements folder, with everything under it, into a table in a SQL database,
  so the business rules or other requirements held there can be queried with SQL. Use when
  asked to mirror, refresh, sync, or reload the business rules or requirements from ALM into
  the database.
---

# ALM Mirror

Copies one requirements folder of `<alm-project>`, with everything under it, into `<table>`
in `<store>`. Nothing is written to ALM.

| Placeholder | Meaning |
| --- | --- |
| `<alm-project>` | The ALM server, domain and project the requirements live in |
| `<default-root>` | The requirements folder mirrored by default, its path and requirement id |
| `<rule-type>` | The requirement type the business rules carry, and its type id |
| `<rule-owner>` | The owner the business rule requirements are assigned to |
| `<other-roots>` | Other folders worth mirroring, with their requirement ids |
| `<store>` | The SQL database the copy writes to |
| `<table>` | The table in `<store>` that holds the copy |
| `<rule-fields>` | The requirement fields that hold the business rule, and their columns |
| `<mirror-script>` | The script that reads ALM and writes `<table>` |
| `<account-env>` | The environment variables that name the ALM account and the store connection |
| `<run-host>` | The machines that reach `<store>`, where the copy runs |
| `<run-command>` | The command that runs `<mirror-script>` on `<run-host>` for a root |
| `<log-lines>` | The lines the run's log ends with |

## 1. What it copies

The business rules live in the Requirements module as requirements of type `<rule-type>`,
under `<default-root>`, owned by `<rule-owner>`. The script takes the root as a requirement
id and mirrors `<default-root>` when none is given. Any folder in `<other-roots>` is mirrored
the same way by passing its id as the root.

## 2. The table

One row per requirement, keyed on `req_id`, folders included, so the tree can be rebuilt
from `parent_folder` or filtered on `req_path`. One column per requirement field ALM defines,
named after the field label in snake case, with the ALM field name in the column comment. A
field ALM adds later becomes a new column on the next run. The business rule fields are the
ones `<rule-fields>` lists.

Each run inserts or updates every row under the root and deletes the rows under it that ALM
no longer holds. Rows under other roots stay. `mirrored_at` is when the row was last written.

Each run also writes the folders above the root, up to requirement 0 at the top of the tree,
and logs them. Walking `parent_folder` up through them gives each rule its full folder path.

## 3. Running it

The copy runs on `<run-host>`, the machines that reach `<store>`, with the account and the
connection named in `<account-env>`:

```bash
<run-command>
```

The job log ends with `<log-lines>`: the root folder with its requirement count, and the rows
written and the rows ALM no longer holds deleted. Querying the rows afterward goes through
`<run-host>` too.
