---
name: repo-writing
description: >-
  Check every write that lands in a repository whose text ships to a separate work side -
  code comments, skip reasons, log strings, shipped Markdown, README text, and text a tool
  posts to the work tracker - against the four rules that govern shipped text: it never
  names this side's tracker, its CI, or any assistant (unless the repository's `<audience>`
  already knows them), it describes how the code works now
  rather than what it used to do, it uses words the tester who owns the repository would
  reach for, in American spelling, and it runs through the humanizer pass in section 4
  before it is committed. Use before committing any comment or document, whenever another
  skill writes prose into the repository, and when asked to clean up, audit, or check
  wording that already landed.
---

# Writing text that ships

Everything under `<shipping-paths>` is copied to `<work-side>`, and text a tool posts to
the work tracker is read by the same people. Unless `<audience>` says otherwise, the work
side has none of this side's tracker, CI, or assistant tooling. A sentence leaning on any of them arrives there as a
dead reference: the reader cannot follow it, and the line spends its space pointing at a
record instead of carrying the fact.

| Placeholder | Meaning |
| --- | --- |
| `<audience>` | Who the shipped text is read by, and what they already know about how the repository is built |
| `<shipping-paths>` | The paths copied to the work side, and the root files that go with them |
| `<work-side>` | Where shipped text is read: the work repository and its tracker |
| `<banned-terms>` | The names of this side's tracker, CI, assistants, and repository, in every form they take, that `<audience>` cannot resolve |
| `<kept-terms>` | Identifiers that look like a citation but stay, because the work side has them too |
| `<voice-words>` | The words the owning tester would not reach for, with the replacement for each |
| `<exempt-paths>` | Paths the rules and the scan leave alone, and the exceptions inside them |
| `<scan-command>` | The entry point that runs `check-repo-text.sh` from this folder with `--config <extension.json>`, over the files a branch changed, tracked and untracked |
| `<verbatim-marker>` | The per-line marker that lets a legitimate quote through the scan |
| `<companion-checks>` | Checks that run beside this one, such as an acronym dictionary scan |
| `<side-records>` | Where provenance goes: the commit message, the pull request body, the tracker |
| `<line-limit>` | The longest source line, in characters |
| `<house-conventions>` | Conventions this side holds itself to that the work team has not agreed |
| `<issue-filing>` | How a gap a review turns up is filed on this side |
| `<review-bans>` | What a review comment on a colleague's work may never name |
| `<payload-guard>` | The send for text a tool carries to the work tracker, and the entry points that run `stamp-payload.sh` and `payload-guard.sh` from this folder with the same config |
| `<rendered-pages>` | Shipped pages rendered word for word from a data file, and that file |
| `<writers>` | The skills that write into the repository and so run this check |

Four rules cover it. All four are checked before the commit rather than in review, and
none of them is a preference. Where the lint configuration ships with the code, nothing in
lint enforces them: a lint rule ships to the work side too, and this boundary is this
side's business.

1. No out-of-band reference. Say the thing, never point at where it was written down.
2. Describe how the code works now. Never contrast it with what it used to do.
3. Write in the tester's vocabulary, American spelling included. A word he would not reach
   for is a tell, whatever else the sentence gets right.
4. The prose-tell pass. Generated-prose habits make a tester's note read like something
   nobody typed.

## 1. What the text may never name

This applies to every string that survives into the repository: a `//` comment, a JSDoc
block, a `test.skip` reason, a `console.log`, an annotation description, a Markdown heading
or paragraph, a table cell, a fenced example.

Never name anything in `<banned-terms>`. The categories a reader without this side's tooling cannot follow are:

- **This side's tracker.** An issue or pull request number, a link to one, a closing
  keyword. A number carries no keyword to give it away, so every form of it counts:
  punctuated rather than spaced, listed, ranged, rounded off, and left blank for later.
- **CI in any form.** A run URL, a job link, or a bare run id, a job, an action, a runner,
  an artifact path or share location, the name of the hosted provider, the workflows this
  side drives the suite with, by name and by their inputs. **A dispatch** is the
  mechanism's word for starting one of them: the work side runs the suite, so write run.
- **Any assistant.** By product name, as an agent or a model, a generated-with line, a
  robot emoji. The skills that write here, by name or as a slash command, this one
  included. Unless `<audience>` knows the tooling, a tester wrote this.
- **This repository itself.** Its name, its URL, its branches, its commits, and the
  tooling that belongs only to this side.

What stays clean is listed in `<kept-terms>`: the work side's own identifiers, qualified so
the reader knows which side is meant, and the inputs the code reads rather than cites.

The replacement is always the same move. Write the fact the reference stood in for:

    No:  see the issue, and the run that reproduced it
    Yes: the grid lists a different stage than SQL names as current

    No:  skipped, waiting on the workflow fix
    Yes: the save answers with the general status message, so the row 13 message this
         asserts never arrives

Provenance still has to live somewhere, and that somewhere is off to the side: issue and
run identifiers go in `<side-records>`. Those are not repository text and this skill does
not touch them.

### A reader who knows how it is built

The categories above are what a reader who knows none of this side's tooling cannot
follow. `<audience>` says who actually reads the text, and `<banned-terms>` is drawn for
that reader. A repository shared with someone who knows how the work is developed, such as
a supervisor who knows which assistant and which skill set build it, leaves those names
out of its table, and its text may name them. A link to the skill set, a line saying the
assistant writes and tests the code on synthetic data, and an assistant attribution are
all clean there.

Where the extension names no `<audience>`, the table holds as written and the reader is
taken to be the work side. On an interactive run, ask the user who reads the repository
before cutting a name that is already in the text. A run with nobody to ask leaves the
name, reports the hit, and stops short of the commit. A name that reaches the work side
cannot be taken back; a trimmed sentence costs one more commit.

An assistant attribution here means a credit line in the repository's own text. Commit
messages and pull request bodies are `<side-records>`, and text a tool posts to the work
tracker (section 6.1) keeps the full table whatever `<audience>` says.

### The boundary is never the subject

Whatever `<audience>` and `<banned-terms>` allow, shipped text says what this repository
does and how. It never talks about the split it sits on, or about other repositories:

- no "this side", "the work side", or "the other side"
- no "consuming repository", and no sentence on what a repository other than this one
  holds, reads, or assumes
- no line on what this repository may do that another may not, or the reverse

Those words belong to the skills and their config. The reader of a README has one
repository in front of them, and a sentence about the arrangement around it tells them
nothing about the code.

    No:  nothing in the pipeline assumes one consuming repository
    Yes: a config file says where every input lives

## 2. What the text may never narrate

A comment, a skip reason, or a document line says how things work now. It never contrasts
that with a previous state, explains a change or a removal, or argues why one approach beat
the one it replaced. The diff and the commit message carry that, and the work side has
neither.

    No:  the locator no longer matches cellIndex, so this reads the header row
    Yes: the header row carries the column name; cellIndex numbers shift per app

"Previously" and "no longer" are ordinary words in the business rules these files quote, so
the test is what the sentence is about. A rule about the application keeping data the user
entered earlier is clean. A sentence about a helper, a test, a locator, or a constant
having changed is not.

"Predates" reads the same way. A record older than a business function, a date of birth
before 1850: clean, about the data. A measurement that predates a rule the branch later
tightened is not, and a line scan cannot see that one when it wraps across lines. Say what
the measurement ran on and drop the comparison:

    No:  that sampling predates the stage-code conditions
    Yes: that sampling ran without the stage-code conditions

## 3. Words the tester would not reach for

The reader knows who owns these files. A word that is not in that
person's vocabulary reads as though nobody typed the line, and it does that even when the
sentence is accurate and carries no dead reference.

The words that come up often enough to name are in `<voice-words>`, each with what to say
instead. The list is short because it holds only what has actually landed. A word that gets
caught the same way later belongs in it, added to the scan and to the list together.

### American spelling

The same rule, one step down. The reader writes behavior, labeled, license, gray, so
behaviour, labelled, licence and grey read as though someone else typed the line. A scan
carries the families rather than a word list:

- **-our for -or**: behaviour, colour, honour, neighbour, favour, labour.
- **-re for -er**: centre, centred, theatre, fibre, calibre.
- **-ce for -se on a noun**: licence, defence, offence, pretence. `practise` goes with
  them.
- **-ise, -isation, -yse**: organise, authorisation, normalised, analyse.
- **A doubled consonant before a suffix**: labelled, travelling, modelled, signalling.
  `cancelled` and `cancelling` are left alone, and `cancellation` is spelled that way on
  both sides.
- **A single one where American doubles it**: enrolment, fulfil, fulfilment, instalment,
  skilful.
- **On their own**: catalogue, programme as a noun, grey, storey, sceptical, judgement,
  ageing, draught, whilst, amongst.

A word the application spells the other way is the application's, not ours. A test quoting
it says what the screen says, and the word stays out of the scan.

The families are spelled out by their endings rather than closed off with a wildcard, so a
camel-case identifier opening on one of them stays clean: `authorIsWorker` is a method, not
an authorisation.

## 4. The prose-tell pass

This section is the `humanizer` pass that the repository's instructions and the other
skills name. It is a checklist, not a separate skill: read every comment, skip reason, log
string, and document you wrote against the tells below, before the commit, and rewrite each
sentence that carries one.

The tells that bite:

- Significance inflation: "serves as a testament to", "plays a crucial role",
  "underscores", "this demonstrates".
- A trailing participle bolted on to sound reflective: "...thereby ensuring correctness".
- Hedging and vague attribution where a measured value belongs.
- Rule-of-three padding, and lists stretched to three when two was the honest count.
- Negative parallelism: "not X, but Y".
- Elegant variation. In a defect report or a comment this is a correctness bug rather than
  a style one: name the field the same way every time it appears or the reader thinks there
  are two fields.
- Copula avoidance: "serves as", "stands as", "functions as" where "is" says it.
- Filler: "in order to", "it is important to note that", "it is worth mentioning".
- Promotional words: "seamless", "robust", "powerful", "comprehensive".
- A closing line that sums up or reassures instead of adding a fact.
- Conversation left in the text: "I hope this helps", "let me know", "as requested".

Verbatim quotes, response bodies, payloads, identifiers, and error strings are evidence.
The pass never touches them.

A companion check in `<companion-checks>` that writes nothing into a document leaves the
pass the whole file to work on. Reword first: what the paragraphs say decides which short
forms a dictionary check is asked to cover.

Technical reference prose is the target voice. The pass takes tells out; it does not add
personality or opinion.

## 4.1 What sits outside these rules

Everything under `<exempt-paths>` sits outside this skill: the rules above do not apply to
it and the scan skips it, apart from the exceptions `<exempt-paths>` names, which the rules
cover. Text that work on an exempt record posts back somewhere else, such as a comment, is
not the record, so it stays under the rules.

## 4.2 Review comments a colleague reads

A review comment on a colleague's pull request is read by one person, in their own editor,
next to their own code. The four rules hold, and the voice is different from a code comment
or a defect report: it talks to the author.

- Casual and gentle. It reads like a note left on a desk, not a finding in a report. No
  severity labels, no bold headers, no "Bug." at the front.
- Lead with a question where one fits. "What happens here if the account didn't start with
  every privilege ticked?" lets the author find the answer, and lands softer than the same
  fact stated flat.
- Explain the mechanism before the fix. A line saying what the code does that the author
  did not expect ("`.locator('td').nth(1)` picks the second cell of the flattened list, not
  column 2 of each row") teaches; a line saying "wrong locator" does not.
- Point at the pattern already in the codebase, by file and name, so the author has
  something to copy. When the author built the right tool themselves and did not use it,
  say so: "you already wrote `getCheckboxState()`, that gives you a true round trip."
- Give the author a way to check: "try adding a bad-length username on row 3 and see if it
  catches it."
- Own what is ours. A change that came from our side, or a note that is not about their
  work at all, is said as such and taken off their plate.
- Lint stays behind the curtain. The rules exist to guide the author, so a comment never
  explains how a rule works, what it misses, or that one is being widened. Say what the
  code should look like; the rule that will enforce it is our business. A gap a review
  turns up (a rule that should have caught the line and did not) is filed through
  `<issue-filing>`, with the file and line as evidence, and never mentioned in the comment.
- No real person's name. A test that acts as a named account, or reads and writes a named
  worker's row, is discussed as "the impersonated worker", or "the fixture account", never
  by the name the code holds. The code line under the comment already shows the name; the
  comment does not repeat it, and it never lands in the review summary either.
- A convention in `<house-conventions>` is a preference in the review, not a rule. None of
  them has been agreed with the team, so a comment says "I would like to start keeping
  titles under 100" and never "we keep titles under 100". The practical reason the
  convention exists still goes in, so the author can weigh it.
- A TODO is expected. A comment naming pending work and who holds it is a normal marker,
  and no review asks for it to go.
- A parked test is the author's call. `test.fixme` or `test.skip` on a case means the
  author knows it is not running, and a comment spelling out what that leaves uncovered
  tells them nothing. The only thing to ask for on a parked test is what any test gets
  asked for under `<house-conventions>`.

The author knows one repository. Never name anything in `<review-bans>`. A change that
crossed from this side is "my push" or "a change I made", and a check that would have
caught something is "a check I have now", with no machinery behind it.

Run the prose pass of section 4 over the comments before they are posted, with the reader
in mind: a review is one of the few places where a leading question, an aside, and a "worth
knowing" beat a plain statement. Then write every comment body and the summary to scratch
files and run `<scan-command>` over them, the same gate as a file that ships: the reader
takes these for hand-typed, and one British spelling says otherwise. A hit is fixed before
the post, and an edit to a posted comment goes through the scan again.

## 5. How the text reads once it is clean

- States the fact, then stops. No windup, no summary of what was just read.
- Explains why, not what. The code already says what.
- Uses the application's and the database's real vocabulary, not a paraphrase.
- Describes how things work now. Never contrasts current behavior with what the code used
  to do, and never explains a change or a removal. The diff and the commit message carry
  that.
- Short words, the actor named, one idea per sentence.
- American spelling: behavior, labeled, license, gray. Section 3 has the families, and the
  scan reads them.
- No em dashes anywhere.
- Lines under `<line-limit>` characters in source: the code, the comments in it, and the
  skip reasons and log strings it carries. Markdown is prose and wraps where the reader's
  window puts it, so a shipped Markdown document is not hand-wrapped.
- Prose written for a text box that wraps on its own is not hand-wrapped: a pull request
  body, an issue comment, a tracker comment, a defect description. Hand-wrapped lines
  re-wrap ragged there, and a reader copying a quote back out takes the breaks with it.

## 6. The check before the commit

Answer these out loud, per changed file. A skipped answer is a failure, not a silent pass.

1. Did the mechanical scan come back empty?
2. Does no sentence talk about the boundary or about another repository?
3. Did the `humanizer` pass in section 4 run over every sentence you wrote?
4. Does every comment describe current behavior rather than a change?
5. Does every sentence use a word the tester would use, spelled the American way?
6. Are the identifiers that got cut recorded somewhere off to the side, in
   `<side-records>`?
7. Did every check in `<companion-checks>` come back empty?

The scan is `<scan-command>`, run over the files the branch changed, tracked and
untracked. It lives outside `<shipping-paths>`, because the check is about the boundary
rather than about the application: it runs on the way in, and the work side does not
inherit it.

The scan ships in this folder as `check-repo-text.sh` and takes `--config <file>`, a JSON
file naming the banned-terms table, the paths that ship, the paths and exemptions it
skips, the verbatim marker, and the voice words. A path in it is relative to the git
toplevel of the config's folder, and the script's header lists every key. `terms.sh`
beside it reads the table, for the scan and for the stamp and guard in section 6.1.

A hit on a file the branch did not touch is backlog, not this branch's work. Report it and
leave it; a document already carrying a dead reference is a separate cleanup with its own
scope.

A legitimate quote that trips the scan is rare, and the fix is to say so rather than to
reword the evidence. Mark that one line and only that line with `<verbatim-marker>`.
Report the marker to the user with the reason. A marker used to get a commit through is
this check failing quietly.

## 6.1 Text a tool carries to the work tracker

A tool that writes straight onto the work tracker (a work item description, a comment, a
commit message, a pull request body) carries text read by the same people as the
repository, so every rule in this skill applies to it, and `<payload-guard>` applies on
top. Before a write is sent:

1. Write the payload to a file, run the prose pass of section 4 over its text, and answer
   questions 2 through 4 of section 6 for it.
2. Run the stamp `<payload-guard>` names over that file.
3. Send exactly that file, a dry run first, and the real send once the dry run printed what
   it would send. An edit after the stamp needs a new stamp.

A read that sends only ids and options carries no text and needs no stamp.

The stamp and the guard ship in this folder as `stamp-payload.sh` and `payload-guard.sh`,
reading the `payloadGuard` keys of the scan's config: the tunnel script, the stamp
command and folder, the list of ops that only read, and the lint a tree send passes. The
guard runs as a hook ahead of every shell command and reads the call from the hook payload
on stdin; the header of each script lists its keys.

## 7. Which skills go through here

Each check in `<companion-checks>` runs beside this one. This skill decides what the words
may say; a dictionary check says what the short forms in them stand for. A skill that
writes a document runs both, and neither one writes into the document.

A page in `<rendered-pages>` is rendered word for word from its data file, so the text in
that file is held to this skill as if it were written into the page. A wording fix goes to
the data row, then the page is rendered again, never edited by hand.

Every skill in `<writers>` runs this check before its commit. A skill whose records sit
under `<exempt-paths>` still runs it over the text it posts anywhere else.

An issue body on this side's tracker is the exception, and only partly. It lives on this
side, so it may name runs, issues, and pull requests. The humanizer pass still applies to
it, and any text the issue carries that is destined for a file, a defect body, or a comment
quoted into the issue is held to section 1 the same as if it were already committed.
