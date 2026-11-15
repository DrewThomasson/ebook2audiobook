# Overmind

These rules are for the `merph518/Overmind` repository itself. In a vendored copy under
`.claude/att-docs/`, ignore this file.

## Every pull request follows the implement procedure

The procedure in `.claude/skills/implement/SKILL.md` is the standard for every pull request
in this repository, whether or not it starts from an issue and whether or not a session
was asked to implement one. At the start of any change, before editing anything, read that
file and the general skill it builds on, `plugins/general/skills/implement/SKILL.md`, and
follow them. The section "Applies to every pull request" in the first file says which
steps to skip when there is no issue.

Two parts are easy to miss:

- The self review loop runs on every pull request, with a review of every change,
  including the last fix. Section 7 sets the pass limit.
- When the loop ends, add the `Manual Review Needed` label and read it back. A pull request
  reported ready without the label is not ready.

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `merph518/Overmind`, worked with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
