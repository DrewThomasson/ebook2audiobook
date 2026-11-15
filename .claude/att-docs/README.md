# Overmind

The base for my Claude Code skills, at
[merph518/Overmind](https://github.com/merph518/Overmind). Every skill I use lives
here once, in general form, and works without any particular repository. Each
repository I work in extends the skills it needs with a thin layer of its own: its
paths, its naming rules, its gates, its tracker. The skill itself is never edited in
the repository that uses it.

This repository is private and for my own use.

## The idea

- **One copy of each skill.** A fix or an improvement lands here and reaches every
  repository on its next pin move.
- **Repositories extend, never fork.** A repository keeps only what is true of that
  repository. Everything else defers to the general skill.
- **Stable by default.** A repository pins one release of this repository, so a
  change here never changes a repository's behavior until I move its pin.

## Skills

| Group | Skill | Purpose |
| --- | --- | --- |
| `att-docs` | `test-plan-from-doc` | Turn a functional spec document into a structured test coverage plan |
| `att-docs` | `living-wiki` | Keep a documents folder publishable as a code wiki |
| `att-docs` | `convert-docs` | Convert source documents into wiki-quality Markdown with provenance |
| `att-docs` | `doc-watch` | Compare a document library with the converted set and download what changed |
| `att-docs` | `doc-impact` | Find the test plans and rules a document revision affects, and file the issues |
| `att-docs` | `repo-writing` | Check shipped text against the wording rules and run the humanizer pass |
| `att-docs` | `acronym-guide` | Keep a dictionary of the acronyms the shipped Markdown uses and gate on undefined ones |
| `att-docs` | `business-rule-extract` | Extract the business rules from a document that has none yet |
| `att-docs` | `business-rule-scan` | Check every business rule against the document it came from |
| `att-docs` | `business-rule-update` | Update a document's rules and stage the result for review |
| `att-docs` | `alm-mirror` | Copy an ALM requirements folder into a database table |
| `att-docs` | `build-test-pack` | Build a test pack workbook for a change from its documents and rules, on the local model when the repository configures it |
| `att-docs` | `validate-sir` | Reproduce a suspected defect and write the SIR text for the dev team or the design team |
| `att-docs` | `manual-validation-walkthrough` | Walk the user through reproducing a validated SIR by hand and record what the check found |
| `att-docs` | `raise-sir` | File one verified SIR record into ALM without opening the desktop client |
| `att-docs` | `read-sir` | Read one SIR back out of ALM by number: status, owner, description, comments |
| `att-docs` | `update-sir` | Change a SIR already in ALM: status, fields, comments, or a Draft's text |
| `att-docs` | `retest-sir` | Retest a raised SIR against the application and report Retested or Failed Test |
| `att-docs` | `skip-ledger` | Keep the ledger of every parked test and check that no skip lands or lifts without its row |
| `general` | `implement` | Take an issue to a reviewed pull request, or run the backlog with `--loop` |
| `general` | `create-issue` | File an issue under the repository's title convention with an area label and a kind label, and retitle old ones |
| `general` | `oversee-development` | Work the issues labeled `ready-for-agent` oldest first, or the best next issue of one milestone ranked by dependents, priority and tracker order, skipping any with an open blocker or dependency, one `implement` run at a time, and never merge |
| `general` | `debug-spec` | Diagnose and fix a failing or flaky spec issue-first, verify it with title-scoped runs, then open a linked pull request |
| `general` | `manual-spec` | Turn one manual test row into an automated spec that prints each step's evidence as a block ready to paste under the row |
| `general` | `new-branch` | Start a working branch from a freshly fetched default branch, in a worktree of its own, and check that the base is clean |
| `general` | `wyatt-regression-issue` | File one full-regression issue per Playwright project of a suite from a saved template, for the run owner on the work side to run locally |
| `general` | `wyatt-review-phase-1` | Review a junior engineer's pull request and leave mentoring comments with proven fixes, without touching their code |
| `general` | `sweep-suite` | Run a whole suite spec by spec in a smoke wave and a rolling wave, triage the red runs against a baseline, file the new failures, and write up the result |
| `general` | `sql-lookup` | Confirm real table and column names in the checked-in schema reference before writing SQL, then run the confirmed read-only query on a runner and read the rows back |
| `general` | `sql-discovery-learning-log` | Keep one file per investigation that records what is settled and what is still open while test-data discovery or a failing spec is worked across run cycles |
| `general` | `azdo-build-issue` | Draft an issue from a failed AZDO build with its failed tests, failed tasks, a log excerpt and the build link, and file it or append it to an open issue only when the user chooses |
| `general` | `azdo-digest` | Read a digest of what needs a look on AZDO: pull requests waiting on you, unanswered review threads, failed builds and changed User Stories, writing nothing and safe to run on a loop |
| `general` | `azdo-review` | Mirror the review threads of an AZDO pull request onto the paired pull request as comments and send replies back to AZDO, each write only when the user chooses |
| `general` | `azdo-sync` | Push a branch to an AZDO feature branch or bring an AZDO branch back, approve and complete AZDO pull requests, keep branch and work-item pairs, check pipeline drift and watch a build, only when the user asks |
| `general` | `day-recap` | Recap the day across the configured repositories: what merged, what is still open, what needs you |
| `general` | `wyatt-review-phase-2` | Fix every finding on a junior engineer's pull request on a pushed fix branch, one commit per fix, and write a wiki page that teaches what was wrong and why |
| `general` | `azdo-stories` | Migrate named issues to AZDO User Stories, or named User Stories to issues, and follow a merged pull request through to its paired story, with every write the user's choice |
| `voice` | `voice-bridge-hooks` | Session hooks that read replies aloud, announce held stops, and relay voice requests |
| `voice` | `voice-request` | Answer a request the user spoke on their phone and Baton relayed |

## Layout

```
CLAUDE.md                         standing rules for sessions working in this repository
CODING_STANDARDS.md               pointers to the rules a code review checks changes against
.claude-plugin/marketplace.json   marketplace entry, for a machine that installs a plugin
plugins/<group>/
  .claude-plugin/plugin.json
  skills/<name>/SKILL.md          the general skill, plus any scripts it runs
  shared/                         helpers and notes that more than one skill uses
docs/<subject>/                   documents that have no place in the AZDO repository
scripts/                          repository scripts, their tests, and the session guard
scripts/consumer/                 the consumer sync, check, lock converter and wrapper
                                  templates; they ship in every snapshot
scripts/pin/                      opens the pin-move pull requests in the consumers
.gitattributes                    line-ending rules, vendored with every snapshot
package.json                      dependencies the shared scripts import
```

The guard in `scripts/guard-main-checkout.sh`, wired up in `.claude/settings.json`,
refuses file edits and the git verbs checkout, switch, restore, stash, reset, merge,
rebase and pull in the shared main checkout, so a session works in a worktree. A
harness with a worktree tool can make it; `git worktree add -b <branch>
.claude/worktrees/<name> origin/main` always can. Other commands, such as commit, are
not blocked. A `git pull --ff-only` of main is allowed.

A session that loads project extensions from `.omp/settings.json` gets the same guard
through `scripts/omp-guard-hook.mjs`. It judges the `write`, `edit`, `ast_edit`, `lsp` and
`bash` tools by the path each call names, resolved the way the harness resolves it, and
hands the call to `guard-main-checkout.sh`. The harness reads `.omp/settings.json` only
from the directory the session starts in, so a session started in a subdirectory is not
guarded. An `edit` call that names no file is refused. The `eval` tool runs unguarded
there, and so do files a `bash` command writes by redirection or other means. The guard
allows an edit under any directory in `.claude/worktrees/`, so another session's
worktree is not protected.

Worktrees pile up under `.claude/worktrees/`. `scripts/worktree-cleanup.sh` lists each
one with its branch, the state of its pull request, the count of uncommitted paths, and
the count of commits that have not been pushed. A worktree is marked `remove` when its
pull request merged, nothing in it is uncommitted, and every commit is at or below the
head the pull request merged. Every other worktree is marked `keep` with the reason. That
includes a worktree whose pull request state could not be read.

`scripts/worktree-cleanup.sh --remove` asks about each worktree marked `remove`. It reads
the answers from standard input, so an empty input removes nothing. After a yes it checks
the worktree again. It then removes the worktree with `git worktree remove` without
`--force`. It never removes the worktree it runs from, and it leaves the branch in place.

`docs/` holds the documents about the harness on the repository side: the runners and
their registration under `docs/runners/`, and the tester hand-off plan under
`docs/hand-off/`. A consuming repository reads them from its vendored copy, at
`.claude/att-docs/docs/<subject>/`. `docs/agents/` holds this repository's issue tracker,
triage label and domain docs settings, which the engineering skills read from the
repository root, and the permission rules that let sessions file and comment on GitHub
issues without a prompt.

Skills are grouped into plugins by subject. `att-docs` holds the documentation
skills, `general` holds the workflow skills that serve any repository (implementing
issues), and `voice` holds the hooks that feed Baton and the skill that answers a relayed
request. All three install at user scope; `voice` is still its own group because its
subject is different. Further groups sit beside them and
follow the same layout and the same extension contract. A group's `hooks/hooks.json`
registers hooks when the plugin is installed.

A skill links to a shared file with a relative path, `../../shared/<file>`. The link
resolves the same way from a vendored copy and from a plugin cache.
`${CLAUDE_SKILL_DIR}` is not substituted when a file is only read, so a link never
uses it.

The ALM helpers in `shared/` (`alm-client.mjs`, `alm-text.mjs`, `alm-stub.mjs`) are
configured by the caller: `configure({ base, domain, project, usernameEnvs })` runs
before any call.

## Requirements

The scripts need `python3`, `bash`, and Node with this repository's `package.json`
dependencies installed. `convert-docs` also needs `pandoc`.

## Tests

Run everything with one command:

```sh
npm ci && bash scripts/test-all.sh
```

It finds and runs every `*.test.mjs` (with `node --test`), `*_test.py` (with
`python3`) and `*_test.sh` (with `bash`) file, keeps going after a failure, prints one
line per file and a summary, and exits non-zero if anything failed. It then runs
`scripts/validate.py`, which checks that every `plugin.json` and `marketplace.json`
parses, every `SKILL.md` has a `name` and a `description`, relative Markdown links
resolve, and every Python, JavaScript and shell file passes a syntax check. Pass
`--tests-only` or `--checks-only` to run just one half.

The same step runs `scripts/bridge-tools/skill_tools.py`, which compares the Baton tool
and argument names in `README.md` and the two voice skills with `bridge-tools.json`, the
tool list taken from Baton's definitions. A skill names a tool in a code span, and the
arguments it takes in call form, as in `send(anyway)` or `read_pull_request(repo)`. The
check fails on a tool or an argument that is not in the list, and on another Markdown file
that names a Baton tool without being added to `SCANNED` in the script. It warns about
an argument of a covered tool that no call form names. After a Baton release changes its
tools, run `bash scripts/bridge-tools/refresh.sh` from a fetched Code Conductor checkout
(`~/Code/Code-Conductor`, or pass its path), commit the new `bridge-tools.json`, and fix
what the check then reports.

The `test-all` check in `.github/workflows/ci.yml` runs this same command on every pull
request and on each push to `main`. `shellcheck` also runs when it is installed, but
its findings are advisory and never fail the run. The runners need `node`, `python3`,
`jq` and `bash`.

The same job runs `scripts/bridge-tools/drift.sh`, which compares `bridge-tools.json` with
Baton's tool list at the main branch of the Code-Conductor repository. It clones that
branch with a token that can read it, rebuilds the list with `refresh.sh` into a scratch
file, and prints a warning that names each tool and argument that was added or removed. A
difference never fails the job: it means `bridge-tools.json` is behind, so refresh it as
above. A missing token, a failed clone, or a rebuild that fails prints a notice and skips
the comparison. The script needs `gh`, `git`, `node`, `python3` and `timeout`. To run it
by hand, use `GH_TOKEN=$(gh auth token) bash scripts/bridge-tools/drift.sh`.

`.github/workflows/pack-compare.yml` is run by hand and compares two staged test packs on a
desktop runner. `docs/runners/RunnerRegistration.md` says how to stage the files.

## How a repository uses it

1. **Install by vendoring.** The repository is copied into the consuming
   repository at `.claude/att-docs/`. Scripts are called by a path in the tree,
   which keeps CI jobs and `node` module resolution working, and no token or
   submodule initialization is needed on a runner. The sync script in
   `scripts/consumer/` does the copy: it fetches a tag, removes the old copy, and
   reads the tag's tree under the prefix. A repository that needs only part of it
   lists the paths to keep; the copy then holds those paths plus `scripts/consumer`
   and `.gitattributes`.
2. **Pin by tag and tree.** `.claude/att-docs.lock` is a plain `key=value` file
   that records the repository (`merph518/Overmind`), the tag, the commit SHA, and
   the root tree SHA of the snapshot. A pruned copy also records `paths=` and
   `copy_tree=`, the tree of what was copied. The check script compares the tree of
   `.claude/att-docs` with the recorded one, so a hand edit, a stray file, or a
   staged change to a vendored file fails offline. Moving the pin is one pull
   request that reruns the sync script.
3. **Extend by a same-name skill.** `.claude/skills/<name>/SKILL.md` in the
   consuming repository has the skill's name and a description that carries that
   repository's trigger words. Skill discovery reads only `.claude/skills`, so the
   vendored copy is never registered and the two cannot collide. A machine that
   also has the plugin installed at user level can disable it in the project
   settings so a second copy at a different version is not loaded.

The repository name is read from the lock, so a move or rename of this repository
changes one line there. A lock that still names an earlier location needs that line
updated before its next sync.

### Sync and check scripts

`scripts/consumer/` holds the scripts and wrapper templates every consuming repository
uses, so it ships in every vendored snapshot:

- `overmind-sync.sh [<tag>]` vendors a tag and writes the lock. With no tag it
  re-syncs the one in the lock, and it refuses when that tag now points at another
  commit. It stages the copy and the lock but does not commit.
- `overmind-check.sh [--remote]` fails when the vendored copy differs from the pinned tree, and
  holds the lock to the pinned tag (below).
- `overmind-lock-convert.sh` rewrites a JSON lock as `key=value`.
- `wrapper-sync.sh.template` and `wrapper-check.sh.template` are the wrappers below.

Nothing about a consuming repository is built into the scripts. Each value comes
from the environment, then from the lock, then from the default:

| Value | Environment | Lock key | Default |
| --- | --- | --- | --- |
| Repository | `ATT_DOCS_REPO` | `repo` | none; required on the first sync |
| Upstream URL | `ATT_DOCS_URL` | `url` | `https://github.com/<repo>.git` |
| Vendored folder | `ATT_DOCS_PREFIX` | `prefix` | `.claude/att-docs` |
| Paths to keep | `ATT_DOCS_PATHS` | `paths` | the whole snapshot |
| Lock file | `ATT_DOCS_LOCK` | none | `.claude/att-docs.lock` |

A variable that is set but empty clears the lock's value for the URL and for the
paths, so a wrapper that exports an empty `ATT_DOCS_URL` or `ATT_DOCS_PATHS` as a
default drops what the lock holds. Export only the values the repository needs.

A consuming repository keeps a thin wrapper in its own `scripts/` so people and
automated jobs keep one stable command. Copy the templates and make them executable:

```
cp .claude/att-docs/scripts/consumer/wrapper-sync.sh.template scripts/overmind-sync.sh
cp .claude/att-docs/scripts/consumer/wrapper-check.sh.template scripts/overmind-check.sh
chmod +x scripts/overmind-sync.sh scripts/overmind-check.sh
```

The check wrapper runs `overmind-check.sh` from the base commit when the base has
it, so a branch cannot weaken the check by editing the vendored script; when the base
has no such script, it runs the vendored copy.
With no `ATT_DOCS_BASE` and no `origin/main`, it runs the vendored copy and the base rules
are skipped.
A consuming repository that has its own `scripts/overmind-check_test.sh`, or any test
that runs its own copy of the sync in a scratch repository, deletes that test and its CI
step when it adopts the wrappers: the wrapper needs the vendored scripts, and the cases
live in `scripts/consumer/overmind-consumer_test.sh`.
The sync wrapper is a short `exec` of the vendored script at the default
`.claude/att-docs`. A repository with another `prefix` edits both wrappers to
point at its own folder. A setting the lock does not hold is exported in the
wrapper before the `exec`. The sync replaces the vendored copy it lives in, so it
keeps all of its work inside one function and exits right after it; bash has read
the whole script before the copy is touched, and replacing itself while running is
safe. A sync that fails before the new copy is ready, such as a path the tag lacks,
leaves the existing vendored folder and the index as they were. A failure after the
old copy is removed, up to the point the new copy is read in, restores the old copy
from the last commit (or removes the partial copy on a first sync) and says so; if
that fails, the sync prints the command to run. A failure while staging
the lock leaves the new lock written but not staged; the sync says so and prints the
`git add` to run, and the check fails until the lock is staged or the sync is rerun.
An interrupt or termination signal during the swap restores the old copy the same way.
A parent folder that is a symbolic link is refused. A sync refuses uncommitted or untracked
files under the folder, but removes ignored files there along with the old copy.
The folder is always read as a literal path, and a name that starts with `:` is
refused. The scripts need LF line endings, so the repository's `.gitattributes`
sets `eol=lf` for `*.sh`, `*.py`, `*.mjs`, `*.template` and the extensionless
`speechctl`; a consumer that uses `core.autocrlf` gets those rules for the vendored
folder from the snapshot's `.gitattributes`, which every sync vendors as
`<prefix>/.gitattributes`, pruned copies included. The sync refuses a
tag, URL, repository, or prefix that git or the filesystem could misread (an
option, a refspec, `.git`, a folder that resolves outside the repository). A URL
given in `ATT_DOCS_URL` is used for the fetch and never written to the lock; only a
`url=` line already in the lock is kept.

The check also holds the lock to the pinned tag. It compares the vendored folder
with `copy_tree=` when the lock has one, else with `tree=`, and then compares the lock
with the lock at the base commit: `repo=`, `url=` and `prefix=` must be unchanged, and the
vendored tree cannot change unless `commit=` moves. When the lock and the vendored tree equal the
base's, the check passes with no fetch. Otherwise it fetches `refs/tags/<tag>` at depth
1 into a scratch repository and requires the tag's commit to equal `commit=` and the
tag's root tree to equal `tree=`; a pruned lock is compared with its root `tree=` there,
and its `copy_tree=` must equal the tree rebuilt from the tag and the lock's `paths=`
(a `copy_tree=` with no `paths=` fails). A base lock in JSON form counts as
no base lock, so a pull request that converts it passes the base rules. `--remote` is the same as
`ATT_DOCS_REMOTE=require` and wins over the variable; any other argument exits 2. The
wrapper passes its arguments through. These settings control the check:

| Setting | Meaning |
| --- | --- |
| `ATT_DOCS_BASE` | The commit the lock is compared with. Default: the merge base of `HEAD` and `origin/main`. With no base at all, the base rules are skipped and the pin is proved against the tag; a CI checkout must fetch `origin/main` (full history, or enough to hold the merge base) for the base rules to apply. |
| `ATT_DOCS_REMOTE` | `off` makes no fetch. `try` (default) warns and passes when the remote cannot be reached. `require` fails when it cannot. A tag the remote does not have fails in both. |
| `ATT_DOCS_URL` | Where the tag is fetched from. Else `url=` in the lock, else `https://github.com/<repo>.git`; a set but empty value clears `url=`. |
| `OVERMIND_READ_TOKEN` | A credential that reads the source repository. It reaches the fetch only through the environment, never the command line. |

A mismatch between the tag and the lock fails in every mode that fetches.

Moving `url=` or `prefix=` is a deliberate change: the check fails in the pull request
that makes it, unless `ATT_DOCS_BASE` names a commit that already holds the new values.
The check script that runs is the one at the base commit, so a change to the script
itself takes effect one pull request later. The wrapper stops with an error when
`ATT_DOCS_BASE` is set but is not a commit in the repository.

A repository whose vendored copy does not hold `scripts/consumer` yet has no script
to call, so it runs the script straight from the tag, from inside the consuming
repository. These two commands work for a repository with no lock yet or a
`key=value` lock; a repository with a JSON lock converts it first (below):

```
git fetch --no-tags https://github.com/merph518/Overmind.git refs/tags/<tag>
git show FETCH_HEAD:scripts/consumer/overmind-sync.sh | ATT_DOCS_REPO=merph518/Overmind bash -s -- <tag>
```

Run the script from the tag being synced: it is the one that writes `copy_tree=`
for a pruned lock and keeps `scripts/consumer` in the copy.

A JSON lock is refused. Both the sync and the check name the
converter; the sync does not read it. Convert it once, in place, with
`.claude/att-docs/scripts/consumer/overmind-lock-convert.sh`, or without a vendored
copy by piping `scripts/consumer/overmind-lock-convert.sh` from the fetched tag into
`bash -s`. The converter checks the SHAs and leaves a `key=value` lock alone, so
rerunning it is safe. The sync then works from the converted lock.

The cases for the three scripts are in `scripts/consumer/overmind-consumer_test.sh`.
They run against a local repository in place of the network.

A machine installs all three plugins at user scope, so every session on it has the
skills, including a session in this repository. The marketplace is pinned to a release
tag with `#<tag>` after the repository name. This pins it the way `att-docs.lock` pins a
vendored copy:

```
claude plugin marketplace add merph518/Overmind#<tag>
claude plugin install att-docs@att-docs --scope user
claude plugin install general@att-docs --scope user
claude plugin install voice@att-docs --scope user
```

The pin moves by hand. To move it, remove the marketplace (which uninstalls its
plugins), add it again with the new tag, and install the three plugins again:

```
claude plugin marketplace remove att-docs
claude plugin marketplace add merph518/Overmind#<new tag>
claude plugin install att-docs@att-docs --scope user
claude plugin install general@att-docs --scope user
claude plugin install voice@att-docs --scope user
```

Adding the marketplace again without removing it keeps the old tag, and
`claude plugin marketplace update` stays on the tag it was added with.

A plugin stays at the version it was installed or last updated at. A release does not reach a
machine until someone runs the commands above, so the `voice` plugin's `SessionStart` hook,
`hooks/plugin_version_check.py`, checks for one when a session starts. It compares the
version each `att-docs` plugin is installed at for the session's project with the newest
version in the marketplace clone's `plugin.json` files. It also compares it with the newest
`v*` release tag on the clone's origin. The tag lookup runs at most every six hours, never
prompts for a credential, and gives up after three seconds.

A plugin that is behind gets a message to the user and to the session. The message holds the
commands for a pinned or an unpinned marketplace, in the scope the plugin is installed in. A
new session after the update lists the new skills. A plugin that the project turns off in
`enabledPlugins`, a version that cannot be read and a lookup that fails produce no message.
The hook exists only in a `voice` plugin that already holds it, so the first update to a
release with the hook is by hand.

A repository that vendors this one should turn the `att-docs` and `general` plugins off
in its own `.claude/settings.json`, so their skills don't load a second time, possibly at a
different version from the vendored copy. Add this block:

```json
{
  "enabledPlugins": {
    "att-docs@att-docs": false,
    "general@att-docs": false
  }
}
```

A project setting overrides the user setting. `voice` stays on, because its hooks are
what give the repository's sessions the reply relay and spoken replies. A repository
that also extends a `voice` skill loads both: the plugin's copy carries the `voice:`
prefix, and the extension keeps the plain name.

See [Install and manage plugins](https://code.claude.com/docs/en/discover-plugins)
for the install scopes and the `#ref` form.

The `voice` plugin registers the voice hooks, which feed Baton (the voice bridge service in
`merph518/Code-Conductor`). Installed at user scope, it gives a
session in any repository the reply relay, spoken replies and attention announcements,
with no hook entries in the repository. A repository adds its own values with an extension file at
`.claude/skills/voice-bridge-hooks/extension.json`. See the `voice-bridge-hooks`
skill's Wiring section. A session can also be read in a voice of its own: the speech widget
saves the choice as `<session id>.voice` in the hook's state folder, and the hook speaks that
session's lines in it, falling back to the global voice when the name is not installed.

Every `send` through Baton reaches a session as `Voice request: `, then a fixed
header, then the phone voice chat's wording of what the user said. The header is a claim, not
proof: it says Baton posted the message from the user's phone, explains why Claude
Code labels it as from another session, and says the message is not the user's confirmation,
approves no permission prompt and grants no escalation. A consumer needs the `voice` plugin
installed and kept current with `claude plugin update voice@att-docs` after a version bump.
`update_bridge` updates a Baton run from a checkout, along with the hooks it vendors (a
packaged Baton is updated with apt), but the skill loads from the plugin install. Do not also copy `voice-request` into `.claude/skills/`. A vendored copy under
`.claude/att-docs/` is not loaded as a skill.

The `general` plugin registers repo hooks for pull request testing, merge-watch
reminders, stray-file checks, tests and formatting on edit, and persistent implement
loops. Hook settings live in `.claude/skills/repo-hooks/extension.json`. The loop and
stray-file hooks are enabled by default; the others require a section in that file.
A repository that vendors this one registers `plugins/general/hooks/run.sh` in its own
settings. See the `repo-hooks` skill.

`/implement --loop` uses the `oversee-development` queue. Its optional
`.claude/skills/oversee-development/extension.json` sets `queue.readyLabel`,
`queue.requireLabels`, `queue.excludeLabels`, and `queue.blockedLabels`; see the skill
for their defaults and the loop's stop and resume commands. Loop state is shared by
worktrees in the main checkout. An interactive restart requires a prompt before the
session can resume work.

`implement` ships `claims.py`, which keeps sessions that work one repository at the same
time out of each other's files. `claims.py check <path>...` reports a file that another
live session has claimed or that another open pull request changes, `claim` records a
claim, `release` drops it, and `sync` reports the files that both the default branch and
the current branch changed, so another branch's merge is brought in before the pull
request opens. Claims are files in the main checkout's git directory, shared by
worktrees and held while the claiming process runs, or for twelve hours when no process
is named. The `implement` skill's `<claim-script>` placeholder names the command; a
repository that leaves it out skips the claim checks.

Baton, the voice bridge server, is in `merph518/Code-Conductor` under `baton/`. The extension
file at `.claude/skills/voice-bridge-hooks/extension.json` also names Baton's repository
values: `inProgressLabel`, `mainBranch`, `reviewLabel` and `startRequest` (with `<N>` for
the issue number). A field left out keeps its default, and the repository the file sits in is
the one Baton lists sessions under. A packaged Baton reports its version from `update_bridge`
and is updated with apt; a Baton run from a Code Conductor checkout fast-forwards that
checkout and restarts, and fast-forwards the served repository's checkout too when it is
clean and on its main branch, since that repository's scripts and tool module are what Baton
runs for it.

A repository adds tools of its own with `"bridge": { "module": "<path>" }` in the same file.
Baton imports that module, relative to the repository, and calls its
`register(core)`, which returns `{ tools: [{ definition, call(args, context) }] }`. `core`
holds `repoRoot()`, the extension file's `extension` fields, and a `helpers` object with
Baton's own `runFile`, `runGh`, `runGit`, `spawnCaptured`, `ghJson`, `takeReadBack` and
`readBackRefusal`, among others. `context` has the call's `paths`, `config`, `pages`, `now`,
`gh`, `git` and `tracker`, plus any option the caller passes. A repository with no module is
offered none of them.

## Extension contract

An extension `SKILL.md` has these parts, in this order.

1. Frontmatter with the same `name` as the general skill, and a `description`
   written for the consuming repository.
2. **Base.** One line: read the general skill at
   `.claude/att-docs/plugins/<group>/skills/<name>/SKILL.md` first and follow it,
   except where the extension overrides it.
3. **Paths.** The values the general skill leaves as placeholders: roots, lists,
   output locations, identifiers.
4. **Overrides.** Each override names the general skill's section it replaces and
   says what applies instead. A rule the extension does not name is the general
   skill's rule.
5. **Added gates.** Checks the repository runs before a commit, such as its own text
   scan or review steps.
6. **Repository notes.** Links to notes that stay in the consuming repository.

### Script config

A skill that runs a script takes its inputs from an `extension.json` beside the
extension, passed with `--config <path>`:

```json
{ "base": "<name>", "docsRoot": "docs", "dataDir": "...", "suites": [] }
```

A path in the config is relative to the git toplevel of the config file's folder.
Scripts read data only. A rule that needs judgment lives in the extension's prose,
not in the config. `--config` comes before a Python subcommand, and a missing config
exits 64.

Scripts that ship here:

- `convert-docs`: converter, page markers, credential scan, word list
- `doc-watch`: `docwatch.py`, `page.js`
- `doc-impact`: `docimpact.py`
- `repo-writing`: text scan, payload guard. Its shell scripts read their config
  through `config-read.py`, so they need only `python3`.
- `acronym-guide`: scan, dictionary writer, term verifier
- `living-wiki`: `wiki.mjs`
- `voice-bridge-hooks`: the hook scripts
- `repo-hooks`: the gate, reminder, test and format hooks, in `plugins/general/hooks/`

### Shims

A repository keeps its existing entry points when other tooling calls them. Each
becomes a short shim that calls the vendored script with `--config`, so callers do
not change. A Python shim hands over with `os.execv`, a Bash shim with `exec bash`,
and a Node shim splices `--config` into `process.argv` and imports the script, so
the exit code and the script's own paths stay right.

## What lives where

| Belongs here | Stays in the repository |
| --- | --- |
| Skill procedure, written in general terms | Document and test layout, suite list |
| Helpers that name no repository path, tool, tracker, or hook | Tracker, CI, and review conventions |
| Scripts, taking their inputs from `--config` | Data files (dictionaries, banned terms, page maps) |
| Notes every repository needs | Notes about that repository's own tooling |

A helper that mixes the two is split. The general part takes the
repository-specific part, such as where to find credentials, as an argument from the
caller.

## Adding a skill

1. Write it in general form here, with every repository-specific value as a
   placeholder in a table at the top.
2. Move any script it runs here and make it read its inputs from `--config`.
3. Add it to the table under [Skills](#skills).
4. Merge the release pull request, then move one repository's pin to the tag it creates.
5. In that repository, replace the local skill with an extension that follows the
   contract above, and confirm a dry run behaves as it did before.

## Releases

A release is a tag, `vMAJOR.MINOR.PATCH`. A repository pins one tag.

Nobody tags by hand. The release workflow (`.github/workflows/release.yml`) runs
release-please on every push to `main`. release-please keeps one release pull request
open that collects the commits merged since the last tag, with the changelog and the
next version. Merging that pull request is the release: the workflow tags the merge
and publishes the GitHub release with its changelog.

A tag cut by hand, which only happens while the workflow is off, leaves the manifest
behind it. A `chore:` pull request then sets `.release-please-manifest.json` and the
three `plugin.json` versions to that tag, and release-please counts commits from there.

The version comes from the commit subjects on `main`, written as conventional commits.
While the version is below 1.0:

- `fix:` and `feat:` bump the patch version.
- A breaking change to the extension contract (`feat!:`, or a `BREAKING CHANGE:` footer)
  bumps the minor version. A consumer moving its pin across a minor version checks its
  extension.
- Other types, such as `chore:`, `docs:` and `test:`, are left out of the changelog and
  bump nothing on their own.

A squash merge makes the pull request title the commit, so the title is what counts.
With a merge commit, each commit on the branch counts, and a subject that is not a
conventional commit is left out.

`.release-please-manifest.json` holds the current version. Each release also writes it
into the three `plugin.json` files, so every plugin carries the repository's version.

The workflow's token comes from the automation GitHub App, described under
[Automation GitHub App](#automation-github-app).

## Pin pull requests

A pin only moves when a consumer merges a pull request, so a consumer stays on its tag
until someone decides otherwise. The pull requests are opened for you.

When release-please tags a release, the release workflow calls
`.github/workflows/pin-consumers.yml` with that tag. It opens one pull request in each
repository listed in `.github/consumers.json`. Each consumer is its own job with its own
token, so one failing does not stop the others, and the run fails if any job did. The run
summary has one line per consumer.

For each consumer, `scripts/pin/overmind-pin.sh`:

1. Clones the default branch and reads the pinned tag from the lock. A consumer already on
   the tag, or on a newer one, is left alone.
2. Runs `overmind-sync.sh` and `overmind-check.sh` from `main` in this repository, which
   also serves the tag, so a rerun for an old tag uses today's scripts. No consumer
   wrapper runs, so a consumer needs no copy of the scripts. A sync or check that fails
   stops that consumer before anything is pushed, and its output is kept: it is in the
   job log, and the run summary line for that consumer ends with it.
3. Reads `CHANGELOG.md` at the tag and writes the pull request body. A changelog that
   cannot be read, or that has no section for the tag, fails that consumer; the body
   never says there are no entries because the file was missing.
4. Commits the move to the branch `overmind/pin-vX.Y.Z` as
   `chore: Move the Overmind pin to vX.Y.Z`, with the author and committer
   `overmind-automation[bot]` whatever identity the runner has configured, and pushes it.
   The push is never forced. The branch is looked up by its exact name, so a branch that
   only ends in it is not mistaken for it. If the branch exists already, the move goes on
   top of whatever it holds, so commits a person added are kept, and a rerun that finds
   nothing to change pushes nothing.
5. Opens a pull request with the same title unless one is already open for the branch. A
   rerun never opens a second one and never edits an open one.

The body is read outside this repository, by people who cannot see its tracker, its
builds or its assistants, so it names both versions, lists the entries after the pinned
tag, and, when the minor version moved, says the extension contract changed. It links
nothing, including the release. Trailing issue and commit references are removed from the
entries. An entry that still names the tracker, a build, an assistant, a link, or this
repository is left out whole, and the body says how many entries were left out, so the
list does not pass for complete. The test is a list of words in `scripts/pin/pin_notes.py`
and leans toward leaving an entry out; the full text is in the changelog.

Nothing merges these pull requests, and nothing closes the ones for older tags. When a
consumer is several releases behind, its open pull requests show it; merge the newest and
close the rest by hand.

To repeat a missed or failed run, run the workflow from `main`; it reads the consumer list
from `main`, not from the tag. The tag must be `vMAJOR.MINOR.PATCH`, and the consumer, if
given, must be listed in `.github/consumers.json`:

```bash
gh workflow run pin-consumers.yml -f tag=v0.32.0
gh workflow run pin-consumers.yml -f tag=v0.32.0 -f consumer=Gnome-Widgets
```

The jobs read this private repository with the workflow's own token. The App token for
each job is narrowed to that one consumer, with Contents and Pull requests write, and
starts the consumer's checks (see [Automation GitHub App](#automation-github-app)).

To add a consumer, list it in `.github/consumers.json` once its lock file is in the
standard `key=value` format. `AI-Health-Coach` is not listed until its lock is migrated.

The runners reuse their workspace, so the checkout the jobs read Overmind from can be a
partial clone, which a sparse checkout by this workflow's plan job or by another
workflow leaves behind. A partial clone cannot serve the file contents it lacks, so a
consumer whose history needs one fails in the sync with `bad pack header`. Before the
pin step, the job runs `scripts/pin/overmind-complete-clone.sh`, which drops the partial
clone mark and fetches every object with the workflow's token. A full checkout is left
as it is, and a fetch that fails or is interrupted keeps the mark so the next run tries
again.

The cases are in `scripts/pin/overmind-pin_test.sh`,
`scripts/pin/overmind-complete-clone_test.sh` and `scripts/pin/pin_notes_test.py`.

## Automation GitHub App

A pull request opened with a workflow's own token starts no checks, and that token
cannot reach any other repository. Workflows that open pull requests here, or in a
repository that pins Overmind, use a token from a GitHub App instead.

The App is `overmind-automation`, a private App owned by merph518. It has no webhook.
Its permissions are:

| Permission | Level | Why |
| --- | --- | --- |
| Contents | Read and write | Create branches and commit files |
| Pull requests | Read and write | Open and update pull requests |
| Metadata | Read | Required of every App |

It has no Workflows permission, because a vendored tree holds no workflow files.

It is installed with All repositories access, so a repository that starts pinning
Overmind is covered without an installation change. Add it to `.github/consumers.json`,
which lists the repositories that pin Overmind.

The repository variable `AUTOMATION_APP_CLIENT_ID` and the secret
`AUTOMATION_APP_PRIVATE_KEY` hold its client ID and private key. A workflow mints a
short-lived token with `actions/create-github-app-token`, narrowed to the repositories
and permissions that job needs, and never uses the key for anything else.

Node actions check certificates against a list bundled with Node, which lacks the root
of a TLS-inspecting proxy. `release.yml` and `consumer-pr-check.yml` set
`NODE_OPTIONS=--use-system-ca` so their actions read the operating system's store
instead.

To prove the App can open a pull request in a consumer, run the consumer pull request
check:

```bash
gh workflow run consumer-pr-check.yml -f repository=Gnome-Widgets -f keep=true
```

It opens a draft pull request with a one-line file, and `keep=true` leaves it open so
you can watch the consumer's checks start. Without `keep` it closes the pull request
and deletes the branch. The repository must be listed in `.github/consumers.json`.

## License

Overmind is released under the MIT License. See [LICENSE](LICENSE). A vendored copy keeps the LICENSE file.
