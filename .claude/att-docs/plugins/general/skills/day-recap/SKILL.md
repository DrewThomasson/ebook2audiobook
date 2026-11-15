---
name: day-recap
description: >-
  Give an end-of-day recap across the configured repositories: what merged today, what is
  still open, and what needs the user, on screen or read aloud. Use when asked for an
  end-of-day recap, what happened today, or to wrap up the day - "/day-recap", "recap my
  day", "what got done today".
---

# Day Recap

Reads GitHub for each configured repository and reports today, by US Eastern date. It reads
only: it never labels, comments, merges, or closes anything.

| Placeholder | Meaning |
| --- | --- |
| `<recap-script>` | `recap.py` in this skill's folder, run by its absolute path |
| `<recap-config>` | The repository's `extension.json`, which lists `repos` and may set `reviewLabel` (default `Manual Review Needed`) and `inProgressLabel` (default `In Progress`) |

## Run it

```bash
python3 <recap-script> --config <recap-config> --format text
python3 <recap-script> --repo owner/name --repo owner/other --format spoken
```

- `--config` takes the extension's `extension.json`. A missing or unreadable config exits 64,
  and so does a run with no repositories.
- `--repo` repeats, and replaces the config's `repos` when given, so the script runs with no
  config at all.
- Each GitHub listing is capped at 100 rows. A section that fills the cap says so in the
  text output, and the spoken form says the repository has more than the recap could list.
- `--date YYYY-MM-DD` recaps another Eastern day. `--format` is `text` (default), `spoken`, or
  `json`.

## What it reports, per repository

1. Merged today: pull request number, title, and merge time.
2. Still open: pull requests carrying the review label, issues carrying the in-progress
   label, and workflow runs that failed today. A repository with no Actions counts as having
   no failed runs.
3. Needs the user: open pull requests with the review label that GitHub reports as
   mergeable and not draft.

Sessions waiting on a question or prompt are not included. The voice bridge's session list
(`speechctl sessions --json`) records only whether a session is busy, not whether it is
waiting on the user, so there is no reliable source for it. When the user asks about
sessions, use the voice bridge's own tools instead.

## How to say it

For `--format spoken`, which is made for voice, read the output as is. It is a few short
sentences of counts, such as "Three pull requests merged in Overmind. Two pull requests
wait on your review." Do not read out lists of numbers or titles; offer the on-screen form for those.
Say times in 12-hour US Eastern, like "3:30 PM", never 24-hour or UTC.

For the on-screen form, show the `text` output with its headed sections as is.
