# GitHub write permissions

Sessions file and comment on GitHub issues with the `gh` command line tool. Each of those commands asks for approval by default, and a session that is voice driven or running unattended has nobody to answer the prompt, so it stalls. The rules below let the routine tracker writes through and keep everything destructive behind a prompt.

The user adds these rules. A session never edits its own permissions, so this page only documents what to add.

## Where the rules go

Put them under `permissions` in the user settings file, `~/.claude/settings.json`, or add them one at a time in the `/permissions` dialog. Rules in the user file apply to every repository. A rule added to a repository's `.claude/settings.json` applies to that repository only.

```json
{
  "permissions": {
    "allow": [
      "Bash(gh issue create *)",
      "Bash(gh issue comment *)",
      "Bash(gh issue edit *)",
      "Bash(gh pr comment *)"
    ],
    "deny": [
      "Bash(gh issue create*-R*)",
      "Bash(gh issue create*--repo*)",
      "Bash(gh issue comment*-R*)",
      "Bash(gh issue comment*--repo*)",
      "Bash(gh issue comment*--delete-last*)",
      "Bash(gh issue edit*-R*)",
      "Bash(gh issue edit*--repo*)",
      "Bash(gh pr comment*-R*)",
      "Bash(gh pr comment*--repo*)",
      "Bash(gh pr comment*--delete-last*)"
    ]
  }
}
```

An existing `Bash(gh issue create:*)` rule means the same as `Bash(gh issue create *)`, so it can stay. Merge these entries into the lists already in the file rather than adding a second `permissions` block.

## What each rule does

| Rule | Effect |
| --- | --- |
| `gh issue create *` | Opens an issue in the current repository without a prompt |
| `gh issue comment *` | Comments on an issue without a prompt |
| `gh issue edit *` | Changes any field of an issue (title, body, labels, assignees, milestone, dependencies) without a prompt |
| `gh pr comment *` | Comments on a pull request without a prompt |
| `-R` and `--repo` deny rules | Refuse the four commands above when they name another repository |
| `--delete-last` deny rules | Refuse the flag that deletes the user's last comment |

A rule matches the command text from its first word. The allow rules match only the named subcommand, so every other `gh` write still asks: `gh issue close`, `gh issue delete`, `gh issue reopen`, `gh pr merge`, `gh pr close`, `gh pr ready`, and anything under `gh repo`. The `gh api` writes the issue tracker page uses to add and remove labels and to link sub-issues also still ask. A rule such as `Bash(gh api repos/*/issues/*/labels:*)` lets the add-label call through, but not the remove-label call, which starts with `gh api -X DELETE`. Each `*` in that rule matches any text, so it also allows other `gh api` calls whose text contains those pieces, including calls on other repositories. It does not restrict which calls run; for a strict limit, use a `PreToolUse` hook.

Deny rules are checked before allow rules, and a more specific allow rule cannot override a deny. In the deny rules the `*` before `-R` or `--repo` stands for any text, so they match the flag right after the subcommand or after other options, and whether it is written `-R x`, `-Rx`, `--repo x`, or `--repo=x`.

The syntax is described in the permission rules documentation: <https://code.claude.com/docs/en/permissions>.

## What the rules do not stop

Pattern rules match the text of the command, so they limit the usual way a command is written and are not a security boundary.

- A full URL names its repository without a flag. `gh issue comment https://github.com/<owner>/<other-repo>/issues/1` matches the allow rule and none of the deny rules.
- `GH_REPO` selects a repository without a flag. When it is exported in the shell or set in the settings `env` block, the rules never see it. Written inline, as in `GH_REPO=<owner>/<repo> gh issue create`, the command does not match an allow rule and prompts.
- A different spelling of the program does not match: `/usr/bin/gh issue create`, `sh -c 'gh issue create ...'`, or `gh -R <owner>/<repo> issue create`. These are not auto-approved, so they prompt, but a deny rule does not catch them either.
- In a fork, `gh` can default to the upstream repository. Check the target with `gh repo view --json nameWithOwner` before the first `gh issue create` of a session, as [the issue tracker page](issue-tracker.md) says.
- A deny rule also fires when `-R` or `--repo` appears anywhere in the command text, such as in a `--body` text that mentions the flag or in a file name like `issue-Review.md`. The command is refused rather than prompted. Put long text in a file passed with `--body-file`, which keeps the flag text out of the command line.
- The rules follow the documented rule syntax. How a given permission mode combines allow and deny rules with its own checks is set by that mode, and these rules were not exercised against every mode.

For enforcement that does not depend on the command text, use a `PreToolUse` hook that inspects the full command, or sandboxing.

## Choices

- `gh issue edit` is included because a session that files an issue also corrects its title and body. It can also rewrite an existing issue, so remove that line from `allow` to keep edits behind a prompt.
- Closing is left out on purpose. Closing an issue is the user's decision, and so are merges and deletes.
