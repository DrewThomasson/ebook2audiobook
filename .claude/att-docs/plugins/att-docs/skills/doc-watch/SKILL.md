---
name: doc-watch
description: Compare a SharePoint documentation library with the Markdown documents converted from it, list what changed or is new, keep one tracking issue of documents waiting for conversion, and on an attended run download the approved documents onto a branch. Use when asked whether the specifications changed, to check SharePoint for revised documents, or to refresh the conversion backlog, and from a scheduled task.
---

# Doc Watch

Reads one or more SharePoint document libraries through the user's signed-in
browser, and says which converted documents under `<apps-root>` are out of date
and which in-scope documents were never converted. The site is read, never
edited.

The consuming repository's extension supplies the values below. Where it names
none, ask the user rather than guessing.

| Placeholder | Meaning |
| --- | --- |
| `<library-table>` | Each library: its key, its web, its library title, and the suites it holds |
| `<library-host>` | The SharePoint host the libraries live on |
| `<library-url>` | The default library's `AllItems.aspx` page, opened to start a scan |
| `<signin-hosts>` | The sign-in pages an expired session lands on |
| `<suites>` | The suite names a `<folders-table>` row may carry |
| `<apps-root>` | Where converted documents live, one folder per suite |
| `<todo-root>` | Where downloaded documents wait for conversion, one folder per suite |
| `<docs-root>` | The documentation tree that holds `<apps-root>` and `<todo-root>` |
| `<library-map>` | The table under `<todo-root>` mapping each waiting file to its library path |
| `<downloads>` | The folder the browser saves downloads into |
| `<scan-script>` | `docwatch.py` in this folder, run with `--config <extension>` ahead of its subcommand, or the extension's shim that adds it: it builds the page payload, reads the page report, writes the issue body, places downloads, and writes links |
| `<page-script>` | `page.js` in this folder, the scan that runs inside the SharePoint page |
| `<extension>` | The `extension.json` `<scan-script>` reads: the libraries, the suite codes, the three tables, the source names that never came from a library, and the `convert-docs` extension that names `<todo-root>`, `<apps-root>`, the Future folder and `<library-host>` |
| `<folders-table>` | Every top folder of each library, and the rule for each folder that matters |
| `<ignored-table>` | Documents to pass over: a file name, then `*` or the one Modified time to skip |
| `<sources-table>` | The library folder a converted file came from, for a name found in more than one walked folder |
| `<collisions-table>` | The name a download takes when its name is found in two library folders |
| `<converter>` | The conversion script `convert-docs` runs, and the formats it reads |
| `<expected-not-listed>` | How many converted documents are expected to sit outside every walked folder |
| `<browser-tools>` | The tools that drive the user's browser, and how to load them |
| `<ask-tool>` | How a question reaches the user |
| `<notify-tool>` | How a scheduled run tells the user what it found |
| `<tracking-issue>` | The tracking issue's title and labels, and the commands that find, create, edit, and close it |
| `<migration-check>` | How to tell whether a revision has reached the web app |
| `<new-branch>` | The command that cuts a branch and worktree from a fresh main branch |
| `<download-branch>` | The branch name for a download batch |
| `<links-branch>` | The branch name for a links run |
| `<pr-title>` | The pull request title for a download batch |
| `<wiki-check>` | The `living-wiki` check, its write mode, and the pages it generates for `<todo-root>` |
| `<branch-age-gate>` | The check run on a branch before its push |
| `<text-gate>` | The text checks a commit message and pull request body pass before they ship |

```
/doc-watch             attended: scan, ask, download, branch, pull request, issue
/doc-watch --dry-run   scan and report; nothing is written anywhere
```

The scheduled task runs the scan and the tracking-issue step only. Downloading
needs the user's approval each time, and a schedule cannot give it. The one
standing approval is for the documents `build-test-pack` relies on; see "What
this skill never does".

Every question goes to the user through `<ask-tool>`. Commit messages, the pull
request body, and the issue body are written to a scratch file and passed by
path.

## Libraries

`<library-table>` lists every library. `<extension>` holds the same table for
`<scan-script>`, and `<scan-script> check-config` checks every `<folders-table>`
row against it.
One scan walks every library from the one page, fetching a request digest for
each web. A folder of the default library, the one with no key, is written as
it sits in it, `Process Description`. A folder of any other library starts
with that library's key and a colon, `<Key>:<Folder>`, in `<folders-table>`,
`<sources-table>`, the report, and the summary. SharePoint allows no colon in a
folder name, so the two forms never collide. The key and colon alone is the
library's root: a library whose documents sit in no folder maps its root to a
suite with a `<Key>:` row. The scan lists only the files in a root, and walks
each of its folders through that folder's own row.

## What lives here

| File | Holds |
|---|---|
| `<folders-table>` | every top folder of each library, and the rule for each folder that matters |
| `<ignored-table>` | documents to pass over: a file name, then `*` or the one Modified time to skip |
| `<sources-table>` | the library folder a converted file came from, for a name found in more than one walked folder |
| `<extension>` | the values and table paths `<scan-script>` reads, in the consuming repository |
| `<page-script>` | the scan that runs inside the SharePoint page, shipped in this folder |
| `<scan-script>` | builds the page payload, reads the page report, writes the issue body, places downloads; shipped in this folder |

`<folders-table>` rules, longest matching folder first:

- a suite name from `<suites>`: walked; a converted document is followed, and
  any other document is **new** for that suite
- `track`: walked; converted documents are followed, nothing else is reported
- `skip`: not walked

A top folder of any library that the table does not name comes back as
`UNMAPPED`. Report it and leave it; the table changes only on evidence of where
converted documents live. To gather that evidence, run the scan with
`payload --mode survey`, which walks every top folder and counts the converted
documents found under each folder, by suite.

## How a document is matched

The index is the provenance block every converted file carries (`- Source:`
and `- Converted:`). A document is keyed by its file name without the
extension, lowercased, because `<converter>` converts a `.doc` and its `.pdf`
twin as one document. A trailing `_MMDDYYYY` or `_YYYYMMDD` date is dropped
from the key as well. A document that takes a new dated name at each revision,
such as a contract file `Contract_08252026.yaml`, is followed by a `track` rule
on its folder as one document whatever date it carries.

A changed document in a format no converter reads is left in `<downloads>` by
`place`, which prints `BY HAND`. Update its converted copy by hand, as the
extension describes for that document. A dated revision of a document the
converter does read, such as `Extract File Layouts_20150401.xlsx`, converts to
a file named after the new stem, so move it over the old converted file rather
than keeping both.

- **changed**: the library's Modified time is later than the `Converted` date.
  A document claimed by two converted files (the same source converted into two
  suite folders) is changed for each one whose date is older, and lands in each
  of those suite folders.
- **new**: under a suite folder, not in the index, and not a revision copy
  (a `Revision History` or `Archive` folder, or a `_RevN.N` file name).
- **not listed**: in the index but not found in any walked folder. Some
  sources sit outside every walked folder, so about `<expected-not-listed>` are
  expected. A jump in that number means a folder moved.

### One name in two folders

The library repeats some documents under more than one walked folder, and the
same name can be two different revisions, one in each folder. The key is the
name alone, so the scan holds every file it matches until the walk ends and
then weighs each name found in the home folder of two or more documents. A
home folder is the file's own folder, above any `Revision History`, `Archive`,
or `<name>.doc File` folder. Each name gets one of three states:

- **copy**: every home folder holds the same files at the same sizes. It is
  one document, compared once through the home whose files are newest.
- **resolved**: `<sources-table>` names the folder each converted file came
  from. Only the copies under that folder are compared, and the others are
  passed over.
- **conflict**: different files, and no row in `<sources-table>`. The name is
  **held** and counts as neither changed nor unchanged, because only the copy
  the conversion came from can say whether the conversion is current.

Resolve a conflict by reading the converted file's `Revised` and `Version`
lines against the files the summary lists, then adding one `<sources-table>`
row per converted file that claims the name: the path under `<apps-root>`, a
tab, and the library folder (or a parent of it) the matching file sits in. A
root row, `<Key>:`, names the files at the root only, never a folder under it,
so a file in `<Key>:<Folder>` takes that folder in its row. When the name is
converted twice, every converted file needs its own row. `<scan-script>` stops
on a row whose file has no provenance block, whose folder is not walked, or
that leaves out one of the name's converted files.

The library's search index leaves documents out, and filtered list queries
trip its 5,000 item view threshold, so the scan walks each folder through
`RenderListDataAsStream` instead.

### A revision the web app does not carry yet

A revised specification can describe work the dev team has not built, so a
revision is not proof that the web app should behave the new way. The version
the web app follows stays in `<apps-root>/<SUITE>/`, and a revision that is not
migrated converts into `<apps-root>/<SUITE>/Future/` beside it, under the same
file name. Step 6 decides which revisions those are.

Once a name has a Future copy, the watch follows it through that copy alone. A
later revision is compared with the Future copy's `Converted` date, `place`
puts it in `<todo-root>/<SUITE>/Future/` without being told, and the suite
folder's copy is never reported as changed.

When the work reaches the web app, promote the revision: on a branch of its
own, `git mv` the Future copy over the suite folder's copy, open a pull
request, and run `doc-impact` on it. The promotion is a revision of the copy
the plans cite, so that review files the plan updates the revision now needs.

## 1. Open the library

Load `<browser-tools>`. If the browser is not connected, report that the
browser must be running with its automation connected, and stop.

Open a new tab at `<library-url>`.

The page needs the user's SSO session. The library can load and then redirect,
so wait a few seconds after the navigation, then ask the page where it is,
comparing inside the page and returning only the result:

```js
await new Promise((r) => setTimeout(r, 4000));
location.host === '<library-host>'
```

`true` means the session is live; `false` means the tab is on a sign-in page
(`<signin-hosts>`). Nothing is ever typed into a sign-in form.

More than one browser can be connected, one per machine the user has signed in
to the automation from, and the default one is not always the machine the user
signed in to SharePoint on. So when the tab lands on a sign-in page, list the
connected browsers before reporting anything. Keep that tab open. For each
other browser, most recently connected first: select it, open the library in a
new tab, and run the same check. Scan in the first browser where it returns
`true` and name that browser in the report. Then close the original tab and
every other tab opened this way, except the one that is scanning.

When no other browser returns `true`, close the tabs opened in the other
browsers and select the default browser and the original tab again. A
scheduled run does not wait for anyone: close the tab, report that the session
has expired, and stop. The session does not last overnight, and the user signs
in by hand, so an expired session on a scheduled run means that sign-in did
not happen that day. Step 5 sends the notification, which names the site to
sign in to.

An attended run, `--dry-run` included, waits for the user instead. Tell the
user that sign-in is needed, which browser holds the tab, that the tab stays
open, and that the run waits about 30 seconds for them to sign in to
`<library-host>` by hand in that same tab. Then check that tab every few
seconds for about 30 seconds in total. Make each check its own browser call,
so each wait stays well under the browser call's time limit, and a sign-in
that navigates the page ends only that one short check:

```js
await new Promise((r) => setTimeout(r, 3000));
location.host === '<library-host>'
```

A check that fails because the page was navigating is repeated on the same tab
within the 30 seconds. A `true` can come from a page on `<library-host>` that
the sign-in passes through on its way to the library, so when a check returns
`true`, open `<library-url>` in that same tab again and run the first check in
this step, the one with the 4-second wait, once on that tab. The 30 seconds
keep counting, and nothing else in this step starts over. When that check
returns `true`, carry on to step 2 in that tab without asking the user
anything. When it returns `false`, go on checking until the 30 seconds are up.
When the 30 seconds pass without a library page, or the tab or browser is
gone, close the tab if it is still open, report that the session has expired,
name the site to sign in to, tell the user to start the run again after
signing in, and stop.

## 2. Scan

Write the payload into the scratchpad and read it back:

```bash
python3 <scan-script> payload --cached > <scratchpad>/page.js
```

Pass the file's whole text to the page as script on that tab. It returns
`started`, or reports the index instead:

- `index stale`: the page holds another version of the index. Regenerate
  without `--cached` and pass that text. The page keeps the full index, so
  later runs send the cached, shorter version again until a conversion changes
  the index.
- `index corrupt`: the pasted index does not match its checksum. Pass the full
  payload again, copied exactly.

Poll until the scan finishes. Each poll waits well under the browser call's own
time limit:

```js
for (let i = 0; i < 10 && !DW.done; i++) await new Promise((r) => setTimeout(r, 3000));
({ done: DW.done, folders: DW.folders, files: DW.files })
```

Then read the page's text. The page body is replaced by the report, one
URI-encoded record per line between `DOCWATCH-BEGIN` and `DOCWATCH-END`. Copy
those lines exactly into `<scratchpad>/report.txt` and classify them:

```bash
python3 <scan-script> compare <scratchpad>/report.txt > <scratchpad>/result.json
python3 <scan-script> summary <scratchpad>/result.json
```

`SESSION expired` in the summary means the scan never ran; report it and stop.
An `ERROR` line names the folder that failed; report it, and treat that
folder's documents as unknown rather than unchanged.

Close the tab when the run is done.

## 3. Report the scan

Give the summary: unchanged, changed, new, passed over in a format no converter
reads, not listed, conflicts, names found in two or more folders, unmapped
folders, errors, and one line per changed or new document with its suite,
Modified date, size, and the converted file it replaces. Name every `HELD`
entry with both paths: it stays out of the changed list until a
`<sources-table>` row settles it.

The scan reports a new document only in a format `convert-docs` turns into
Markdown, reading that list out of `<converter>` itself. Diagrams, project
plans and images under a walked folder are counted by format on the "no
converter reads" line instead, so nothing that cannot become Markdown reaches
`<todo-root>`.

`--dry-run` stops here. It wrote only scratchpad files.

## 4. Update the tracking issue

One open issue, `<tracking-issue>`, holds every document waiting in
`<todo-root>`. Find it by its title and label, and write its body:

```bash
python3 <scan-script> issue-body --result <scratchpad>/result.json \
  > <scratchpad>/tracking-body.md
```

The body is regenerated from `<todo-root>` plus the pending downloads, never
appended to. `issue-body` also flags a document waiting under the wrong suite
folder, and one that was already converted after it was added.

- No open issue and nothing waiting: nothing to do.
- No open issue and something waiting: create it with the title and labels
  `<tracking-issue>` names and the body file, then read its number from the
  output.
- An open issue: replace the body, but only once the body file is non-empty and
  the issue's title is the tracking title. Read the first lines of the body
  back afterward.

After step 7, `issue-body --repo <download worktree>` lists that branch's
`<todo-root>`, so the issue describes the files before the branch merges.

- An open issue and the body says `Nothing is waiting.` after a conversion:
  close it.

Never file a second tracking issue. Two open issues with that title is a
finding; report both numbers and edit neither.

## 5. Scheduled run: review, notify, and stop

A scheduled run then runs the bare `doc-impact`, which reviews every converted
document that reached the main branch since its last run against the test
plans and files the updates they need. It catches a conversion whose merge
never triggered the review. It reads git and the repository, not SharePoint,
so it runs even when step 1 stopped on an expired session.

A scheduled run ends here. When anything is changed or new, send one
notification through `<notify-tool>` naming the counts and the tracking issue
URL, and say that `/doc-watch` downloads them. When `doc-impact` filed or
extended any issue, the same notification names how many and links them.
Nothing else is written: the tracking issue, the `doc-impact` issues, and the
`doc-impact` record outside the repository are the whole of what a scheduled
run changes, with anything more the extension names.

A scheduled run that stopped on an expired session in step 1 also sends one
notification: the scan did not run, sign in to `<library-host>`, then start the
task again.

## 6. Attended run: ask, then download

Before asking, check each changed document against `<migration-check>`. A
revision is not migrated when its change has not reached the test environment,
or when the web app does not show what the revision adds. A document already
followed through its Future copy needs no check.

Ask once for the whole batch. The question lists every file with its suite,
file name, size, and library folder, and says the files land in `<downloads>`
and then move into `<todo-root>/<SUITE>/`. It names each revision the check
found not migrated, with the change it waits on, and says that one lands in
`<todo-root>/<SUITE>/Future/` instead; a revision the evidence leaves open is
named as open, for the user to settle in the answer. Options: download all, or
download none. A user who wants part of the batch says which through the
free-text answer; record the rest in `<ignored-table>` only when they say to.

For each approved file, navigate the tab to the download handler of the web
that holds it. The server-relative path is the `url` field of the result,
encoded, and the web is the one the `url` starts with:

```
https://<library-host><web>/_layouts/15/download.aspx?SourceUrl=<encoded url>
```

The handler serves the file as an attachment, and the browser saves it under
`<downloads>` with its library name. Check each one with `ls -l`; its size
matches the listing.

Cut the branch first (step 7), then place the batch into that worktree. The
first call lists, the second moves:

```bash
python3 <scan-script> place <scratchpad>/result.json \
  --repo <download worktree> --future "<library file name>"
python3 <scan-script> place <scratchpad>/result.json \
  --repo <download worktree> --future "<library file name>" --apply
```

Pass `--future` once per revision the answer left not migrated, naming it as
the result does, and leave it out when there are none. `place` stops on a name
that is not in the batch. The tracking issue marks those rows as not migrated.

No name under `<docs-root>` holds a space, so `place` writes each document
under its library name with each run of spaces, and any hyphens touching it,
as one hyphen: `ACT 4.0 - Activity Entry.docx` waits as
`ACT-4.0-Activity-Entry.docx`. The library name stays at the end of its
`<library-map>` path, and `<converter>` hands it to the Source line, which is
still the name the watch keys on.

With `--apply`, `place` also writes each placed document's server-relative
library path into `<library-map>`, replacing any earlier row for the same
folder and file name and dropping the rows whose file is in neither its folder
nor `_done`. A Future row names its folder as `<SUITE>/Future`. `<converter>`
reads it to give each converted file a `SharePoint` line linking back to its
library document, so the table is committed with the downloads.

`place` drops a changed document whose own last-saved date is no later than
its conversion: the site's Modified time moved without an edit. The drop is
recorded in `<ignored-table>` against that Modified time, so the next edit
reports it again. Formats without embedded properties (`.doc`, `.xls`) are
always kept. `--keep-resaved` keeps those documents too, for a batch downloaded
on purpose to be converted again, such as every source in the library after the
converter gains a feature. `compare --all` reads a `links` report as if every
found document had changed, which gives `place` the whole converted set. A name
found in two library folders needs a download of its own per folder, saved
under the name `<collisions-table>` gives it.

## 7. Attended run: branch, commit, pull request

Cut the branch with `<new-branch>`, named `<download-branch>`.

Place the files there (step 6), enter the worktree, and run `<wiki-check>`. The
downloads are not wiki pages, but their folders are: `<todo-root>` and each
suite folder in it get a generated page. The check reports those pages as
behind until its write mode writes them, so write them, then check again.

Stage `<todo-root>` and the pages the write touched, and nothing else. A drop
recorded in `<ignored-table>` lands in the checkout the script ran from; commit
it there on its own branch. Commit with the message file:

```bash
git commit -F <scratchpad>/commit-msg.txt
```

Run `<branch-age-gate>` on the `<download-branch>` branch before its push. That
branch was cut from the main branch earlier in the same run, so it passes
unless the run sat for a day between the cut and this step. When it fires, its
merge pushes the branch, and the push below is skipped.

Push the branch and open a pull request titled `<pr-title>`, with the body from
`<scratchpad>/pr-body.md`.

The downloaded files are the application's documents and go through no text
scan. The commit message and pull request body go through `<text-gate>`. The
body lists each file with its suite, Modified date, and the converted file it
replaces, links the tracking issue, and says `/convert-docs` is the next step.

Then rerun step 4 from the new worktree, so the issue lists what the branch
holds.

## 8. Link converted files to the library

A converted file links to its library document through the `SharePoint` line
in its provenance block. A file converted from a doc-watch download gets the
line from `<library-map>`. Any other converted file gets it from the links
scan, run when asked, "link the converted docs to SharePoint", and when the
`link` count below shows files without one.

The links scan is the step 2 scan with one more record: a `FOUND` row naming
the library folder and file behind every converted document the comparison
settled on. A name held as a conflict gets no row until `<sources-table>`
settles it, and neither does one found only under a Revision History or
Archive folder. The report runs to one row per converted document, too long to
copy out of the page, so the page saves it to the downloads folder as
`docwatch-links.txt`. That is a download, so ask before running it, naming the
file and where it lands.

```bash
python3 <scan-script> payload --mode links > <scratchpad>/page.js
```

Open the library as in step 1, pass the payload, and poll as in step 2. The
page saves the file only when the walk finished; a stale index or an expired
session shows on the page as in step 2 and saves nothing. Clear any earlier
`docwatch-links.txt` out of `<downloads>` before the run, since the browser
names a second copy `docwatch-links (1).txt`. Then, from a worktree of its own
(`<new-branch>`, named `<links-branch>`), count what would change, then write
it:

```bash
python3 <scan-script> link <downloads>/docwatch-links.txt
python3 <scan-script> link <downloads>/docwatch-links.txt --apply
```

`link` puts one `SharePoint` line per found source right under the `Source`
lines and replaces any already there, so a rerun after the library moves a
document corrects the link. It prints a `NOT FOUND` line for each converted
file with no library row, such as a held name. Commit the changed files, run
`<branch-age-gate>`, push the branch when the gate did not, and open a pull
request listing the counts.

## Looking up named documents, for a test pack

`build-test-pack` asks whether the documents a pack relies on are current. The
day-level scan cannot answer that for a document edited on the day it was
converted, so a lookup compares to the minute. Open the library as in step 1,
then run the page for the named files:

```bash
python3 <scan-script> --config <extension> payload --mode lookup --name "<library file name>" [--name ...]
```

The page reports a `LOOKUP` row, with the Modified time, for every current copy of
each name, indexed or not. Save the report and classify it:

```bash
python3 <scan-script> --config <extension> lookup <report> --name "<library file name>" [--name ...]
```

Each `--name` is the library file name, which is the name on the converted copy's
`Source` line, never the hyphenated converted name. The result lists `changed` (a
converted copy modified at or after its `Converted` minute; a copy stamped with a
date alone is changed when the library copy was modified that day or later), `new`
(no converted copy), `current`, `not_found`, `held` (a name in two folders holding
different files that `<sources-table>` does not settle), `no_suite` (a new document
in a folder that names no suite, which needs one chosen), and `ignored` (passed
over by `<ignored-table>`). `readable` is false, with the cause in `session`,
`errors`, or `index`, when the walk did not finish: that is an unreachable library,
never documents not found. `changed` and `new` are in the shape `place` reads, so
the download, `place --keep-resaved`, and conversion steps of step 6 apply
unchanged.

## What this skill never does

- Sign in, or type into any form on the site.
- Edit, upload, check out, or delete anything on SharePoint.
- Download without the user's approval for that batch. The one exception is
  `build-test-pack`: a document it relies on that is missing or stale is
  downloaded and converted without asking, so the pack is built from the
  current text. It goes on a `<download-branch>` branch with its
  `library.tsv` row, and a pull request opens for the usual review. Every
  other download still asks first.
- Run `convert-docs`. Conversion stays a separate step the user starts, except
  for the `build-test-pack` documents above.
