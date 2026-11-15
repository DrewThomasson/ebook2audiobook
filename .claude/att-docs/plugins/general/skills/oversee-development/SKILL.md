---
name: oversee-development
description: >-
  Work the issues labeled `ready-for-agent` oldest first, or the best next issue of one
  milestone, one issue at a time per session, unattended, opening one review-ready pull
  request per issue and never merging anything. Use when asked to run through the backlog
  or a milestone, work issues while the user is away, or keep implementing issues on a
  loop - "/oversee-development", "/oversee-development milestone <title>", "work the
  backlog", "keep going through the issues".
---

# Oversee Development

Runs the backlog as a conductor. The conductor works each issue through the `/implement`
skill, either itself through the Skill tool or by handing the issue to a subagent that runs
`/implement`. The queue and the ledger hold the state between issues, so a session that is
compacted partway through the backlog carries on from them rather than from the transcript.

Arguments, all optional:

- `/oversee-development` runs until the queue is empty or a stop condition hits
- `/oversee-development 5` runs the next five issues, then reports and stops
- `/oversee-development voice` narrows the queue to issues that carry that label as well as
  `ready-for-agent`; the conductor runs `OVERSEE_FORCE=1 oversee.sh init voice` before
  step 1
- `/oversee-development milestone "<title>"` works one milestone: the conductor runs
  `OVERSEE_FORCE=1 oversee.sh init --milestone "<title>"` before step 1 and the script
  serves the best next issue in it, ranked as step 2 says. It combines with a label and a
  count, and `resume` keeps the milestone.
- `/oversee-development resume` re-reads the ledger and continues, queue as-is

`oversee.sh` below is the script in this skill's folder, the base directory the Skill tool
prints when the skill loads. Run it by that absolute path.

## Persistent implement loop

`/implement --loop` runs this procedure with a persistent marker. The general plugin's
session hooks supply the session identifier and restore the loop instruction on resume
and compaction. Before step 1, run the helper by its absolute path in this skill's
folder, with the project as the working directory and the session ID from the hook:

```bash
python3 <skill-folder>/loop.py --session <session-id> start
```

Pass `CLAUDE_CODE_SESSION_ID=<session-id>` in the environment of each `oversee.sh`
command so the ledger recognizes this session across separate shell invocations.

Pass `--milestone "<title>"` and a label after `start` when the run has a scope. An
active loop's marker fixes its scope; `init` and `refresh` cannot change it. The marker
and queue survive a session restart. On resume, inspect `python3 <skill-folder>/loop.py
--session <session-id> status` and continue the saved queue; do not initialize a new scope.

The Stop hook continues an active loop after a turn. On a user pause request, run
`python3 <skill-folder>/loop.py --session <session-id> pause "<reason>"`; use `resume` to continue.
The hook also pauses on the eighth stop attempt without this session's ledger progress.
When the user ends the loop or step 5 ends the run, run `python3 <skill-folder>/loop.py
--session <session-id> stop "<reason>"` before the final reply.
An interactive restart needs a user prompt to start a turn; the hook restores context on
that turn but cannot start one itself.

An active or paused marker holds its session's in-flight issue even if the process has
exited. Resume that session to continue it. If the session will not return, first verify
that it has stopped, then run `python3 <skill-folder>/loop.py --session <old-session-id>
stop "<reason>"`. Once the recorded process has exited, `oversee.sh next` can offer its
issue as an orphan. A missing process ID cannot establish that the owner exited.

`oversee.sh` needs gh 2.94 or newer, because the queue reads each issue's blockers with
`gh issue list --json blockedBy`. `init`, `refresh`, `next`, `blocked`, and `start` stop with the install
fix when gh is older. `finish`, `swap`, `status`, `adopt`, `withdraw`, `runs`, and `resume` do not read
blockers and run on any gh, so finished work is still recorded.

## What this never does

Never merges, never pushes to `main`, never closes an issue, and never deletes a branch or a
worktree. Every issue ends as an open, non-draft pull request with a self review recorded in
its body and no conflict against `main`, waiting for the user. `gh pr merge` is not part of
this workflow at any point, including when a pull request looks obviously safe and including
when the user is asleep.

## State

Two files under `.claude/oversee/` in the main checkout, driven by `oversee.sh`. They are
gitignored and shared by every worktree, and they are the memory of this skill: the
transcript is not. A session that is compacted, interrupted, or killed resumes from these
files with nothing else.

```bash
oversee.sh init [--milestone <title>] [label]     # build the queue, once
oversee.sh refresh [--milestone <title>] [label]  # rebuild it from the live backlog
oversee.sh next                    # refresh, then what to work or why nothing is
oversee.sh blocked                 # list blocked issues and their reasons
oversee.sh start <issue> <branch>
oversee.sh adopt <issue>           # claim an orphaned in-flight issue
oversee.sh withdraw <issue>        # take back this session's own start
oversee.sh runs <issue>            # park this session's issue while its runs go
oversee.sh resume <issue>          # take a parked issue back
oversee.sh finish <issue> <done|stalled|skipped> <pr|-> <note>
oversee.sh swap <issue> <from> <to>  # move a label, read back
oversee.sh status                  # counts and the tail of the ledger
```

The label and the milestone a queue was built for are saved with it. `next` refreshes
the queue with a bare `refresh`, which keeps both, and a `refresh` given only one of them
keeps the other. A forced `init` sets the whole scope: a label or milestone it is not
given comes out empty, so a run that names a scope starts with it. It rewrites the queue,
the filter, and the open list, and leaves the ledger alone.

Repository filters live in `.claude/skills/oversee-development/extension.json`:

```json
{
  "queue": {
    "readyLabel": "ready-for-agent",
    "requireLabels": [],
    "excludeLabels": [],
    "blockedLabels": []
  }
}
```

`readyLabel: null` removes the ready-label requirement. Required labels all have to
match. Excluded and blocked labels add to the built-in exclusions; blocked labels also
appear in the blocker report. The queue reads this file from the main checkout.

`start` tags its ledger row with the session's id and process id, from
`CLAUDE_CODE_SESSION_ID` and `CLAUDE_PID`. That tag is how several conductor sessions share
one queue: each holds its own in-flight issue and passes over the others'.

An issue's area is the word before the colon in its title (`voice: speechctl commands ...`
is area `voice`). Two issues in one area never run together, because they edit the same
folder: `next` defers the second until the first one's pull request is merged or closed.
A title with no such prefix has no area and is never deferred.

`next` prints one of these:

- `NEXT <issue> <area> <title>` work it; in a milestone run the line ends with
  `pick: <reason>`, why this issue ranks first
- `INFLIGHT <issue> ... branch <name> mine` this session's unfinished issue, resume it
  before anything else
- `INFLIGHT <issue> ... branch <name> orphan` an unfinished issue whose session has exited,
  adopt and resume it; a scoped run adopts an orphan only while the run would serve it,
  and a session still resumes its own `mine` issue wherever it sits
- `RUNS <issue> ... branch <name>` this session's issue parked on its runs with
  `oversee.sh runs <issue>`; its area stays held (`issue <n> waiting on its runs`), and
  `next` serves a different issue. Take it back with `oversee.sh resume <issue>`, which
  refuses while another issue of this session is in flight; `start` refuses a parked issue
  and points at `resume`. While an issue is parked and nothing else is workable, `next`
  prints `BLOCKED`, not `EMPTY`, and `blocked` lists the `RUNS` line. A `runs` row whose session has
  exited is served as an `INFLIGHT ... orphan`, and `adopt` claims it
- `ELSEWHERE <issue> ... branch <name>` held by another session or its active or paused
  loop marker; its area stays held. A scoped run prints an orphan it does not adopt the
  same way, and its area stays held while the branch is open
- `DEFER <issue> ... area held by <PR or issue>` skipped this pass, printed for the record
- `DEFER <issue> ... blocked by #<n>` skipped this pass because an open issue blocks it,
  printed for the record; it is served once the blockers close
- `DEFER <issue> ... waits on #<n>` skipped this pass because its body names an open issue
  it depends on, with `(pull request <pr> open)` when that issue is done and its pull
  request is not merged yet; milestone runs only
- `BLOCKED` everything left is deferred behind an unmerged pull request, an issue in flight
  elsewhere, an open blocker, or an open dependency
- `EMPTY` queue exhausted

## 1. Resume before anything else

Always start here, on every invocation, including the first.

A run given a label or a milestone sets the whole scope first, before `status` and `next`,
because `next` rebuilds the queue from the scope saved with it. A part the call does not
name comes out empty, so no scope from an earlier run carries over:

```bash
OVERSEE_FORCE=1 oversee.sh init --milestone "<title>" [label]   # or: init voice
```

A bare run, a count-only run, and a `resume` run skip this call.

```bash
oversee.sh status
oversee.sh next
```

`status` prints a `scope:` line when the run is scoped, `scope: milestone "<title>"` or
`scope: label <label>`, and the label follows the milestone when both are set.
An empty queue under that line means the milestone has no open ready issue, so run `next`
and let it end the run. Never run a bare `init` on a resume: it would drop the milestone.

`INFLIGHT` means a previous session never recorded the issue as finished. For a `mine` row,
first check with `ListAgents` whether a subagent of this session is still working the issue.
If one is, wait for its report and handle it as step 3 does, rather than resuming the issue a
second time. For an `orphan` row, run `oversee.sh adopt <issue>` first, so no third session
adopts it too. Do not restart the issue: find out how far it got, with two cheap calls and no
file reading.

```bash
gh pr list --head <branch> --state all --json number,state
git ls-remote origin "refs/heads/<branch>"
```

- A pull request exists: `finish <issue> done <pr> "resumed"`, move on.
- Branch pushed, no pull request: finish it with `/implement`, resuming from the existing
  branch rather than cutting a new one.
- No branch at all: `finish <issue> skipped - "session died before branching"`, swap the
  `In Progress` label off with `oversee.sh swap`, and let the queue serve it again later.

## 2. Build the queue

When `status` reports zero queued entries and the run was given no label or milestone:

```bash
oversee.sh init
```

A run given a label or milestone has built its queue with `init` in step 1 already.

`next` rebuilds the queue from the live backlog on every call, through `refresh`, so an
issue filed since the last call is in the queue it serves from. A failed backlog or pull
request read stops selection. The rebuild keeps every open issue the ledger already
names, whatever its labels: an issue in flight or waiting on an open pull request still
holds its area though `In Progress` would drop it.

A `skipped` issue is served again once the reason it was skipped is gone:

- a note starting `not workable at start:` names a label, a blocker, a closed state, or a
  milestone, so the issue comes back once the live backlog lists it without an excluded
  label; it is then served only if it carries `ready-for-agent`, has no open blocker, and,
  in a milestone run, is in the milestone, like any other issue
- any other note comes back once every issue or pull request number it names is closed
- a note that names no other issue or pull request stays skipped, since nothing `next` can
  read says the reason is gone

`done` and `stalled` rows and in-flight rows are never served again. When `next` prints
`BLOCKED` or `EMPTY`, that is the stop in step 5.

Outside a milestone run this reads issue numbers, titles, labels, and blockers. Nothing
else. An issue's body is read by `/implement` when that issue comes up, never all of them
at once.

By default the queue holds issues labeled `ready-for-agent`. A repository may change
that label or add filters in its extension file. `/oversee-development <label>` also
requires the named label. The queue drops issues labeled `In Progress`, `Blocked`,
`Tracker`, `Already Done`, `DO NOT MERGE`, `question`, `wontfix`, `duplicate`,
`needs-triage`, `needs-info`, `ready-for-human`, or `invalid`, and outside a milestone
run orders what is left oldest issue first. An issue with an open pull request is deferred.

An issue with an open blocker is not served. A blocker is another issue that GitHub's issue
dependencies list as blocking it, and it counts until that issue is closed. Outside a
milestone run, a `Blocked by:` line in an issue body is not read. `next` prints a `DEFER`
line naming the blockers and serves the issue once they have all closed. The `Blocked`
label is separate: it marks an issue waiting on something it cannot get for itself, such
as another issue or pull request, a person, or a service. A person or the `implement`
skill removes it.

### A milestone run

`oversee.sh init --milestone "<title>"` keeps the issues whose milestone title is exactly
`<title>`, on top of the `ready-for-agent` gate and the excluded labels. In this mode the
script reads every open issue's body, parses it, and writes the queue already sorted, so
the conductor never sees a body. Each `NEXT` line ends with the reason the issue ranks
first.

Issues rank by, in order:

1. How many open issues in the milestone depend on it, directly or through others, by a
   dependency in their body or an open native blocker on GitHub. A dependency is always
   ahead of what waits on it.
2. Stated priority: `critical` or `P0`, `high` or `P1`, `medium` or `P2`, `low` or `P3`.
   An issue with no priority statement ranks as `medium`.
3. Its position in the milestone's tracker, when there is one.
4. Issue number, lowest first.

The script reads these lines in an issue's body, in any case, and skips fenced code blocks:

- A dependency: the phrase `Depends on` or `Blocked by`, anywhere in a line, with an
  optional colon or bold, followed by a leading run of references: `#<n>`, then more joined
  to it by commas, `and`, or `&`. Only that run counts, so `Depends on #5 but see #12`
  waits on 5 alone.
- A dependency under a heading named `Depends on` or `Blocked by`: a line that starts, after
  an optional list marker or checkbox, with `#<n>`. More references joined to it by commas,
  `and`, or `&` count. Other prose in the section does not.
- A priority: a line `Priority: <word>`, or the first line under a `Priority` heading. The
  first statement wins, and an unknown word is ignored.

A reference written `owner/repo#<n>` is skipped even when it names this repository. A
reference to the issue itself, to a closed issue, or to a `Tracker` issue is not a
dependency either. Dependencies are read only from the forms above: other wordings such as
`requires #<n>` or `after #<n>`, and a reference in other prose, are not read. An open
dependency outside the milestone still holds the dependent.

A tracker is an open `Tracker` issue in the milestone. The `#<n>` that opens a task item
(`- [ ] #<n>`, `- [x] #<n>`) or a numbered item (`1. #<n>`) in its body gives an order, and
several trackers are read in tracker-number order. That order ranks and never holds an
issue back.

A dependent waits until its dependency issue closes, which happens when the user merges the
pull request. While that pull request is open, `next` prints `DEFER` with `waits on` and
serves another issue, so a chain of dependent issues ends at `BLOCKED` until the user
merges.

An issue the ledger names stays in the queue when it leaves the milestone, so work in
flight is never dropped, and it is never served again. When `init` or `next` prints
`no open issue in milestone "<title>"` on stderr, the title is misspelled or the milestone
is done. Titles match whole and are case sensitive.
`gh api repos/{owner}/{repo}/milestones --jq '.[].title'` lists them. A finished milestone
ends as `EMPTY`.

## 3. The loop, one issue at a time per session

One issue worked at a time within a session, finished before the next. That keeps each pull
request reviewable. Other conductor sessions may work the same queue alongside, each with its
own one issue; `next` keeps them apart by passing over every issue in flight elsewhere and
deferring any issue in the same area.

For each `NEXT`:

```bash
oversee.sh start <issue> <type>/issue-<issue>-<short-description>
```

`start` reads the issue's state, labels, blockers, and in a milestone run its milestone
again, since the queue is a snapshot, and it writes the pick reason into the ledger row
itself. When the issue has closed, picked up an excluded label, lost `ready-for-agent`,
left the milestone, or gained an open blocker since, it records the issue as `skipped` and
exits non-zero: run `next` again rather than starting the issue. It also exits non-zero,
writing nothing, when another live session already started the issue: two sessions can read
the same `NEXT`, and the ledger lock lets only the first `start` through. Run `next` again
then too.

A session that started an issue and cannot work it after all, before any label or branch,
takes the start back with `oversee.sh withdraw <issue>`. That puts the issue back the way it
was before the start, so the queue serves it again, where `finish ... skipped` would record
a verdict on the issue.

`next` reads titles, so it cannot see two issues in different areas that edit one file.
`/implement` checks that with its claim script in its first step, before it labels the
issue. When the check defers the issue because an open pull request or another session's
claim holds files of the issue's own unit, record the deferral:
`oversee.sh finish <issue> skipped - "waits on PR #<n>"`. The queue serves the issue again
once that pull request closes. A claim line ending `issue=<N>` names the holder's issue:
write `waits on #<N>` in the note, and the queue serves the issue again once that issue
closes. A claim that names no issue gives the queue nothing to read, so that deferral stays
skipped: say so in the final report. A subagent that defers an issue has labeled nothing;
it reports the outcome `deferred` with the file and the holder, and runs none of these
commands.

Then run `/implement <issue>` on the branch `start` recorded, in this session with the Skill
tool or in a subagent. Run it in this session when the user is watching and may want to step
in, since a subagent's work does not show in the session; use a subagent to keep the
conductor's context small over a long queue. Follow that skill exactly, including its self
review of the pull request before the handoff. The self review runs at most three passes,
and only a real bug sends it round again: an unattended run that keeps reviewing past that
spends the time the next issue needed. When the work the issue asks for is already on main,
cut no branch and take the Already done path below.

A subagent loads `/implement`, not this skill, so the conductor writes these rules into the
prompt it gives the subagent, along with the issue number and the branch. The subagent gets
no transcript and reads the issue body itself. It runs none of the `oversee.sh` commands,
label swaps or issue comments that steps 3 and 4 give the conductor; the labels `/implement`
sets itself stay with the subagent. Where `/implement` would ask the user a question, the
subagent stops and puts the question in its report instead. Its report gives the pull
request number, the outcome (`done`, `stalled`, `deferred`, or `already-done`), and any such question.
It sends the report once `/implement` reaches its ready signal and does not wait for the
merge. The conductor waits for that report before it runs `finish` or `next`, and never has two
subagents working issues at once. To answer a question, the conductor asks it with
`AskUserQuestion` and sends the answer to the same subagent with `SendMessage`; when that
subagent can no longer be reached, a new subagent resumes `/implement` from the pushed
branch with the question and answer in its prompt.

When `/implement` hands the pull request off, the issue ends in one of these:

- `done`: an open pull request, self reviewed
- `stalled`: the work cannot be finished, see step 4
- `deferred`: another pull request or session holds the issue's files, recorded as `skipped`
  above
- `already-done`: the work is on main already, see below

A point where `/implement` asks the user a question is a pause rather than an end, and is
never recorded with `finish`. Ask with `AskUserQuestion`, carry on with `/implement` on the
answer, and record the issue only once it ends `done`, `stalled`, `deferred`, or `already-done`.

Record it in one ledger line, a note under 120 characters, and move on:

```bash
oversee.sh finish <issue> <status> <pr|-> "<note>"
```

A `done` issue with a pull request number is ready for the user. Put the
`Manual Review Needed` label on that pull request before running `next`, through the issues
endpoint (`gh pr edit` fails here on the classic projects lookup). The output is the
read-back, and the label is on when its name comes back:

```bash
gh api -X POST repos/{owner}/{repo}/issues/<pr>/labels \
  -f "labels[]=Manual Review Needed" --jq '[.[].name] | join(", ")'
```

When the user leaves feedback on one of the open pull requests, take the label off that pull
request at once, before starting the requested work. Do the work, and put the label back only
when it is ready again.

### Already done

An `already-done` issue has its work on main already. The conductor never closes it. It
labels the issue `Already Done` and says where the work went. Write a comment to
`$CLAUDE_JOB_DIR/tmp/done-<N>.md` (or the session scratchpad) naming the commits or pull
request that delivered it, with one line on what each delivers. Then:

```bash
oversee.sh swap <N> "In Progress" "Already Done"
gh issue comment <N> --body-file <path>/done-<N>.md
oversee.sh finish <N> done <pr|-> "already done: <note>"
```

The read-back is the gate: `Already Done` is one of the labels the queue drops, so an issue
that never got it would be served again.

Once an issue is recorded, do not go back to its branch or diff. The pull request body
carries the detail, and the user reads it at review time.

## 4. Park, do not block

An issue that cannot be finished, because what it needs is outside its scope or outside the
repository, ends `stalled` and the queue keeps moving. Write a one-line note on where it
stuck, plus the branch name, to a file with the Write tool, then:

```bash
oversee.sh swap <N> "In Progress" Blocked
gh issue comment <N> --body-file <path>/stalled-<N>.md
oversee.sh finish <N> stalled - "<note>"
```

The read-back is the gate: a park that dropped `In Progress` but never landed `Blocked` puts
the issue back in the queue it just stalled out of, and one that kept `In Progress` holds
the area against every other session.

A stalled issue may still have an open pull request, if `/implement` landed part of the work
and left the rest. That is a normal outcome, and the pull request number goes in the ledger
row either way.

## 5. Stop conditions

Stop starting issues and write the final report when any of these is true:

- `next` prints `EMPTY` or `BLOCKED`, which it does only after reading the live backlog
- the `/oversee-development <n>` limit is reached
- three issues stall in a row, which means something systemic rather than three hard issues:
  a service is down or a credential expired
- `gh` stops authenticating

`BLOCKED` is not an error. It means every remaining issue is in an area an unmerged pull
request from this run already changed, is in flight in another session, waits on an open
blocker, or waits on an open dependency named in its body. The next move belongs to the
user: review and merge, close the blocker or dependency, or both,
then run `/oversee-development resume`.

`EMPTY` with open issues left usually means none carries `ready-for-agent`. Label the ones
that are ready for unattended work, then run `/oversee-development` again.

## 6. Report

Run `oversee.sh blocked` and include each blocked issue and its reason, including
deferred issues. Recheck a blocker that may have cleared before ending the loop.
For a persistent implement loop, turn off its marker before the final reply.

One block at the end, short enough to read on a phone:

```
worked <n> issues, <d> done, <s> stalled
open for review: #112 (issue 110), #113 (issue 108), ...
stalled: issue 109, needs a credential the session does not hold
blocked: 4 issues behind open PRs in voice
```

Then `oversee.sh status` is the durable version of the same thing, and it survives this
session ending.

## Token discipline

**The queue reads titles, never bodies, outside a milestone run.** An issue's body is read
when that issue comes up and not before. In a milestone run only the script reads the
bodies, and it prints issue numbers and fixed words, never a body.

**Record an issue in the ledger before running `next`**, so a compaction between issues
loses nothing the next one needs.

**Nothing carries past an issue that the ledger cannot hold.** If a fact matters past the
current issue, it goes in the ledger note, the pull request body, an issue comment, or a
memory file.
