# Coding standards

The rules this repository's reviews check changes against. Each line names a rule and
links its source; the source is the authority, not this file.

A documented rule here overrides the code-smell baseline. Anything `scripts/validate.py`
already checks is not a review finding.

Checked by `scripts/validate.py` in CI:

- Python, Node and shell syntax, `SKILL.md` frontmatter, `plugin.json` and
  `marketplace.json` parsing, relative Markdown links:
  [scripts/validate.py](scripts/validate.py).
- Baton tool and argument names in the voice skills and `README.md` exist in the bridge's
  tool list: [scripts/bridge-tools/skill_tools.py](scripts/bridge-tools/skill_tools.py).

Review checks (a reviewer decides):

- Other changed JSON files parse:
  [Section 5, static checks](.claude/skills/implement/SKILL.md#section-5-static-checks).
- Conventional commits and pull request title:
  [Section 7, the pull request](.claude/skills/implement/SKILL.md#section-7-the-pull-request).
- Pull request body order and ready state:
  [Section 7, the pull request](.claude/skills/implement/SKILL.md#section-7-the-pull-request)
  and [Applies to every pull request](.claude/skills/implement/SKILL.md#applies-to-every-pull-request).
- CI runners: [CI runners](.claude/skills/implement/SKILL.md#ci-runners).
- Versions and release files: [Releases](.claude/skills/implement/SKILL.md#releases).
- Shipped text: [Shipped text](.claude/skills/implement/SKILL.md#shipped-text) and
  [repo-writing](plugins/att-docs/skills/repo-writing/SKILL.md).
- README upkeep: [Repository notes](.claude/skills/implement/SKILL.md#repository-notes).
- Session rules: [CLAUDE.md](CLAUDE.md).
