---
name: oversee-development
description: >-
  Work the ebook2audiobook-expressive issues labeled `ready-for-agent` oldest first, or the
  best next issue of one milestone, one at a time, by running the implement skill on each,
  opening one review-ready pull request per issue and never merging. Use when asked to run
  through the backlog or a milestone, work issues while the user is away, or keep
  implementing issues on a loop - "/oversee-development", "work the backlog", "keep going
  through the issues".
---

# Oversee Development

## Base

Read
[the general skill](../../att-docs/plugins/general/skills/oversee-development/SKILL.md)
first and follow it, except where this file overrides it. The general skill is the vendored
copy pinned by `.claude/att-docs.lock`; never edit it here.

The general skill has no placeholder table, so this file only says where its pieces are here
and what differs.

## Paths

| Piece | Value here |
| --- | --- |
| `oversee.sh` | `.claude/att-docs/plugins/general/skills/oversee-development/oversee.sh`, run by its absolute path from the main checkout |
| `loop.py` | Beside `oversee.sh`. The general plugin is turned off in this repository's `.claude/settings.json`, so its Stop hook does not continue an `/implement --loop` run; the conductor continues the loop itself until a stop condition |
| State | `.claude/oversee/` in the main checkout, ignored by git |
| Queue filters | [extension.json](extension.json): the default `ready-for-agent` gate and no extra filters |
| Implement skill | [the implement extension](../implement/SKILL.md) |
| Labels | `ready-for-agent`, `In Progress`, `Manual Review Needed`, `Blocked` and `Already Done` exist on the repository |
| Areas | Titles follow [/create-issue](../create-issue/SKILL.md) and open with a bracketed area such as `[tts]`, not a word and a colon, so `oversee.sh` reads no area and defers no issue for sharing one |

## Overrides

### Sharing files

With no area read from the title, `next` may serve two issues that edit the same file. The
implement extension's claim check reads open pull requests' file lists before claiming; when
it finds one holding the issue's file, record
`oversee.sh finish <N> skipped - "waits on PR #<n>"`, and the queue serves the issue again once
that pull request closes.

### Machine load

A runtime check downloads TTS models and runs inference on this machine. Between issues,
make sure the last issue left no Gradio server or conversion running (`pgrep -af app.py`),
and stop only the processes this session started.
