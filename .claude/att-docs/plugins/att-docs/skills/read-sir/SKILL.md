---
name: read-sir
description: >-
  Read one SIR's record back out of ALM by its number - status, state, owner,
  description and the dev team's comments - without opening the desktop client. Use when
  asked to read, look up, check, or pull a SIR, "what does ALM say about that SIR", "has the
  dev team answered on that SIR yet", "pull the dev comments for that SIR", and from the SIR
  skills when a record's current state in ALM is the question.
---

# Read SIR

Reads a single SIR out of ALM over its REST interface and prints it. Read only: nothing in
this skill writes to ALM, and nothing in it touches `<records-root>`. Changing a SIR that is
already in ALM is the update skill, over the same session.

| Placeholder | Meaning |
| --- | --- |
| `<alm-project>` | The ALM server, domain and project the SIRs live in |
| `<read-script>` | The command that reads one SIR and prints it |
| `<label-cache>` | The file beside the script that maps ALM field names to the project's labels |
| `<account-env>` | Where the ALM account name comes from, and what to set for the password |
| `<records-root>` | The folder that holds the repository's SIR records |
| `<record-states>` | The states a SIR record can hold, apart from ALM's status fields |
| `<project-lists>` | The values the project lists allow, bar `SIR Status`, which is mapped |
| `<housekeeping-skill>` | The skill that brings the records back in line with what ALM says |

The SIRs live in the server, domain and project `<alm-project>` names. All three are fixed
in the script. Another project in the same domain can hold unrelated defects under the same
numbers, so a lookup that picks the wrong project returns a believable wrong record rather
than nothing at all. That is why the project is not an argument.

## Running it

```bash
<read-script> <number>
```

A read that cannot reach the server at all exits 2 and says so in one line, with the address
and the reason the connection gave. Every other refusal exits 1: a username the server would
not take, a number this project does not hold. The two are separate codes because
`<housekeeping-skill>` branches on them, carrying on without ALM in the first case and
reporting a wrong number in the second.

`--json` prints the same fields as JSON with the HTML stripped. `--raw` prints ALM's own
response untouched, for working out what a field is called. `--refresh-labels` rewrites the
cached field labels described below. `--status-values` prints what `SIR Status`,
`Bug Status`, `Test Status` and `Type` are allowed to hold, straight off the project, and
takes no SIR number. Those are project lists rather than free text, so that output is the
whole set a status can be, which is what `<housekeeping-skill>` maps. Run it when a status
turns up that its map does not name.

The script's output goes back to the reader whole, in a fenced block, exactly as it printed.
A SIR is read to be read: the status line, the long description and the whole comments thread
all carry weight, and which part matters is the reader's call. Anything worth adding, such as
what a dev comment means for a retest, goes after the block, never in place of it.

## Credentials

`<account-env>` says where the account name comes from and what to set for the password.
With the username missing, the script names every place it looked and stops.

If `authenticate` ever answers 401, the pivot is an API key from the `API Key` link on the
server's `/qcbin/` page, posted to `/qcbin/rest/oauth2/login` as `{clientId, secret}`.
`login()` is one function so that swap stays in one place.

## What it does

1. `POST /qcbin/authentication-point/authenticate` with Basic credentials, and checks for an
   `LWSSO_COOKIE_KEY` cookie. A 200 without that cookie means the sign-in bounced, so the
   script stops rather than reading on.
2. `POST /qcbin/rest/site-session`, which answers 201 and sets `QCSession`. Without this step
   every read comes back as an authentication failure even though the user is already signed
   in.
3. `GET /qcbin/rest/domains/{domain}/projects/{project}/defects/{id}`, with the domain and
   project from `<alm-project>`.
4. The field labels, out of `<label-cache>` beside the script, so the output reads
   `SIR Status: Retested` rather than `user-06`. The file is committed and the run does not
   call ALM for it. `--refresh-labels` fetches
   `.../customization/entities/defect/fields` and rewrites it, which is what to run when a
   heading comes out as a bare field name.
5. `DELETE /qcbin/rest/site-session` and a logout, so the read does not hold an ALM license
   until it times out.

## Fields

A SIR's state is a project customization, not a built-in ALM field, so the interesting values
arrive under names like `user-06`. The output carries the project's own labels only, so the
state reads `SIR Status`, and the release and the origin read `Build` and `Type`.
`Bug Status` is ALM's own workflow field and is a different thing from the state the
`<records-root>` records keep, which is `<record-states>`: on a SIR whose `SIR Status` read
`Retested`, `Bug Status` still read `New`.

`<label-cache>` is where the two sets of names meet, for anyone who needs to know which
customization a heading came from.

`Long Description` and `Comments` come back as HTML fragments. The script strips the markup
and keeps the line breaks. `Comments` holds the whole thread, each entry headed with the
author's name, their ALM id and the date, which is the back and forth the retest skill needs.
Both print on every read, and a SIR with nothing in one of them says `(none)` rather than
dropping the heading.

## Reading the result

The record under `<records-root>` is what this repository tracks, and ALM is the side that
moves. When the two disagree, ALM is current and the record is behind, so hand the
difference to `<housekeeping-skill>` rather than editing the record from here.

The dev team's answer lives in `Comments`. The retest skill treats that thread as outranking the
record file, so read it before deciding whether a retest is due.

`<housekeeping-skill>` is the other end of that handoff, and it is the one that takes a
difference and does something about it. It calls this script, with `--json` and nothing else,
over every SIR the repository still tracks by number, reads `SIR Status` as the field that
says where each one is, and moves the record from it. A second script of its own calls this
one the same way, reading upward past the highest number any record carries to record the
SIRs ALM holds that no record does. Its map says what each `SIR Status` value means on this
side, so a value this script prints that looks unfamiliar is looked up there rather than
guessed at here.

`SIR Status` is the field to read. `Bug Status` is ALM's own workflow field and answers a
different question: it sat at `New` on every tracked SIR the first sweep read, including ones
ALM had already closed. `Build` is filled in from the start, so it names the build a SIR
belongs to rather than the one a fix rides.

## The project lists

`--status-values` prints the four project lists off the project. `SIR Status` is the one
`<housekeeping-skill>` maps, so the record state each of its values leads to lives in that
skill's map rather than being repeated here. `<project-lists>` writes out the sets of the
other three, so a value can be recognized without spending a call. They are read but never
acted on:

- `Bug Status` is ALM's own workflow field. It does not track `SIR Status`, and a rule written
  on it fires on nothing: on the first sweep it read `New` on every SIR in the set, closed
  ones included.
- `Test Status` is which stage of the dev team's own testing a SIR is at. It is not this
  repository's retest, which is recorded under `<records-root>`.
- `SIR Type` is what kind of ticket it is, set when it is filed.

A value one of those three prints that is not in `<project-lists>` means the list changed.
Report it and add it there, rather than reading it as a value the lists already hold.

## Limits

The call has to come from a machine that can reach the server `<alm-project>` names.

A browser cannot stand in for the script: browser tooling's data guard can replace
cookie-shaped values in a response, and the comments thread is one of the fields it blanks.

Reading through a browser session can also fail on `/qcbin/ui/` and on any
`?login-form-required=y` URL when the server redirects to a port zero plain-http address that
resolves to nothing. The REST calls above go direct and are not affected.
