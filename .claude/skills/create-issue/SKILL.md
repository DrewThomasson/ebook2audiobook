---
name: create-issue
description: >-
  File an issue in ebook2audiobook-expressive under the `[<area>] <unit>: <description>`
  title convention, with the standard body sections, an area label and a kind label. Use
  when asked to file, open, create or write up an issue, when another skill turns up
  follow-up work outside its task, and when existing issues need retitling.
---

# Create Issue

## Base

Read
[the general skill](../../att-docs/plugins/general/skills/create-issue/SKILL.md)
first and follow it, except where this file overrides it. The general skill is the vendored
copy pinned by `.claude/att-docs.lock`; never edit it here.

## Paths

| Placeholder | Value here |
| --- | --- |
| `<title-limit>` | 100 |
| `<areas>` | The area labels below. `general` is the catch-all |
| `<unit-rule>` | The basename of the file the issue is about, such as `gradio.py` or `xtts.py`. With no single file, the module or folder name, such as `tts_engines` or `python_env` |
| `<ownership-rule>` | The general skill's default: one area and one unit per issue |
| `<labels-note>` | A label edit counts only when `gh issue view <n> --json labels` shows it afterward |
| `<label-script>` | `gh issue edit <n> --add-label <label>`, then `gh issue view <n> --json labels --jq '[.labels[].name] \| join(", ")'` |
| `<kind-labels>` | `bug`, `enhancement`, `documentation`. `question`, `duplicate`, `invalid` and `wontfix` are never applied at filing |
| `<body-sections>` | The general skill's default list |
| `<acceptance-rule>` | The run that shows the change: a headless conversion or a Gradio session, per the implement extension's Section 6, or the static check for a change that runs no code |
| `<special-slots>` | None |
| `<deviation-route>` | None. A gap between the README and the app is filed as an issue |
| `<shell-text-note>` | The body is a file written with the file-writing tool, passed with `--body-file` |
| `<asking-note>` | The ask tool (`AskUserQuestion` in Claude Code) |
| `<scratchpad>` | The session's scratch or temp directory, never the worktree |
| `<writing-rules>` | Code comments, UI strings and log lines say how the code works now, with no issue numbers or assistant names. An issue body may name issues, pull requests and runs |

## Areas

| Area | What it covers |
| --- | --- |
| `core` | `app.py`, `lib/core.py`, `lib/conf*.py`, and the ebook parsing and audio assembly pipeline |
| `tts` | `lib/classes/tts_engines/`, its presets, `tts_manager.py`, `tts_registry.py` |
| `gui` | The Gradio interface: `lib/gradio.py`, `lib/header.css`, `lib/header.js` |
| `install` | `ebook2audiobook.command`, `ebook2audiobook.cmd`, `components/`, `Dockerfile`, compose files, `tools/pip_bootstrap/`, `setup.py` |
| `i18n` | `lib/lang/`, `tools/readme_i18n/`, `tools/legends_i18n/`, `SUPPORTED_LANGUAGES.md` |
| `ci` | `.github/workflows/` |
| `tooling` | `.claude/` (outside the vendored `att-docs`), `scripts/`, the rest of `tools/` |
| `general` | Catch-all for work that belongs to no single area |

## Overrides

None.
