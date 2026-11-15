# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: follow `plugins/general/skills/create-issue/SKILL.md`: its title format, an area label and a kind label, the body passed as a file with `--body-file`, and a read-back of the labels after filing. `gh issue create` is the mechanism. Overmind's values for that template:
  - Title: `[Tooling] <unit>: <description>`. The unit is the skill, script or hook name, as in `[Tooling] build-test-pack: ...`.
  - Area label: `Tooling`.
  - Kind label: one of `bug`, `enhancement`, `documentation`. A wayfinder map or ticket that is not a bug takes `enhancement`.
  - Labels are added with `gh api repos/<owner>/<repo>/issues/<n>/labels -f "labels[]=<label>"`, and the response is the read-back.
  - Never add `In Progress` at filing.
- **Read an issue**: `gh issue view <number> --json number,title,body,labels,comments`.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Make an issue a sub-issue of a parent**: `gh api --method POST repos/<owner>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>` (database id, as in **Blocking** below). The flags `gh issue create --parent <parent> ...` and `gh issue edit <parent> --add-sub-issue <child>` need `gh` 2.94+ and fail on older versions. Without sub-issues, put `Part of #<parent>` at the top of the child body.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). The flags `gh issue create --blocked-by <n>,<n> ...` and `gh issue edit <child> --add-blocked-by <blocker>` need `gh` 2.94+ and fail on older versions. Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed. An issue labeled `Blocked` is also blocked here. The implement skill (`.claude/skills/implement/SKILL.md`) adds that label, or you add it by hand, with a comment naming what the issue waits on. Remove it, as in **Apply / remove labels**, once that settles. Native dependencies are the machine-checked blocker.
- **Count open blockers**: `gh api repos/<owner>/<repo>/issues/<n> --jq .issue_dependencies_summary.blocked_by` (open blockers only; 0 means startable). `gh issue view <n> --json blockedBy` needs `gh` 2.94+; it also lists closed blockers, so filter it: `--jq '[.blockedBy.nodes[] | select(.state == "OPEN")] | length'`.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: add with `gh api repos/<owner>/<repo>/issues/<n>/labels -f "labels[]=<label>"`; the response is the read-back. Remove with `gh api -X DELETE repos/<owner>/<repo>/issues/<n>/labels/<url-encoded label>` (for example `.../labels/In%20Progress`). `gh issue edit` can fail on the Projects (classic) deprecation.
- **Close**: post the explanation with `gh issue comment <number> --body "..."`, then `gh issue close <number>`. On an already-closed issue, `gh issue close --comment` drops the comment and still exits 0.

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

File issues only into the user's own repo. Never file into `mattpocock/skills` (the repo these skills come from) unless the user owns it. In a fork, `gh` can default to the upstream parent, so before the first `gh issue create` of a session, check the target with `gh repo view --json nameWithOwner` and confirm it with the user if it is not their repo.

The `gh` writes that run without a prompt, and the ones that still ask, are listed in [GitHub write permissions](gh-write-permissions.md).

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number>`, then `gh pr view <number> --comments` (off a TTY, `--comments` prints only the comments, not the body), and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`.
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue as described in **Create an issue** under Conventions.

## When a skill says "fetch the relevant ticket"

Read it as in **Read an issue** above.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labeled `Tracker`, holding a body with Destination, Notes, Decisions so far, Not yet specified, and Out of scope. Create it as in **Create an issue**, with the `Tracker` label added. The map and its children also carry the area and kind labels from **Create an issue**.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (see **Make an issue a sub-issue of a parent**). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. The `wayfinder:*` labels do not exist and are not created. Record the type (`research`/`prototype`/`grilling`/`task`) in the first line of the child body, for example `Type: research`. Read the type from this line, since no type label exists. Once claimed, the ticket carries the `In Progress` label.
- **Blocking**: see **Blocking** under Conventions.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (see **Count open blockers**, or an open issue in the `Blocked by` line), an `In Progress` label, or a `Blocked` label; first in map order wins.
- **Claim**: add the `In Progress` label with `gh api repos/<owner>/<repo>/issues/<n>/labels -f "labels[]=In Progress"` as the session's first write, and read the response back to confirm the label is on the issue.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then remove the `In Progress` label, then append a context pointer (gist + link) to the map's Decisions-so-far.
