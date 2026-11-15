---
name: voice-bridge-hooks
description: The speech and voice tunnel hooks, run from the voice plugin with this repository's extension.json, which announce what a session needs, read replies aloud in speech mode, and feed the voice bridge the phone follows. Use when changing those hooks or their values, or working out why a session spoke, stayed quiet, or never reached the phone - "why did the stop not speak", "the ready announcement is wrong", "the phone missed that reply".
---

# Voice bridge hooks

## Base

Read
[the general skill](../../att-docs/plugins/voice/skills/voice-bridge-hooks/SKILL.md)
first and follow it, except where this file overrides it. The general skill is
the vendored copy pinned by `.claude/att-docs.lock`; never edit it here.

## Paths

| Placeholder | Value here |
| --- | --- |
| `<config>` | [extension.json](extension.json): the review label and its announcement, the ready line, the In Progress label, the start request and the spoken terms |
| `<hook-settings>` | The `voice` plugin's `hooks/hooks.json`, installed at user scope; this repository's `.claude/settings.json` registers none of them |
| `<entry-points>` | The plugin's own scripts. This repository keeps no shims |
| `<review-label>` | `Manual Review Needed` |
| `<ready-line>` | `PULL REQUEST <N> IS READY FOR YOUR REVIEW` |
| `<ledger-module>` | None. This repository keeps no run ledger, so `ledgerModule` and `scriptsDir` are left out of `extension.json` and a blocked session is not reported as waiting |
| `<bridge>` | Baton, the voice bridge in `merph518/Code-Conductor`, run with `--config` naming this repository's `extension.json` |

## Overrides

None.
