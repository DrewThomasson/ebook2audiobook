---
name: acronym-guide
description: >-
  Keep a dictionary of what every acronym the shipped Markdown uses stands for,
  render it into one page that ships with the documents, and check that no
  document ships using a short form the dictionary has never seen. Use whenever
  a document in the shipped set is written or edited, before the commit,
  whenever another skill writes a document, and when asked what an acronym
  means or to add one to the dictionary.
---

# The dictionary

The shipped documents reach a reader who holds the application's vocabulary
unevenly: someone who works in one corner of it knows that corner's short forms
cold and has never met another corner's, and nobody holds all of them.

So the repository keeps one dictionary of what its acronyms stand for, and a
check that no document ships using a short form the dictionary has never seen.
The dictionary is the deliverable, and it ships: it is written out into
`<dictionary-page>`, which arrives with everything else and is where the reader
looks a term up.

Every other document is left exactly as its author wrote it. Nothing here
appends a table, a section, or a line to any file but that one.

The check is what makes the dictionary grow. A document that spends a new
acronym stops the run, and the row that answers it is written once and serves
every document after it.

| Placeholder | Meaning |
| --- | --- |
| `<docs-roots>` | The Markdown that ships: folders and single files in scope |
| `<docs-root>` | The main documents folder among them, used in the examples |
| `<excluded-paths>` | Copied dumps under `<docs-roots>` that the scan skips |
| `<local-only-paths>` | Markdown that never leaves this side |
| `<dictionary-page>` | The rendered dictionary page, the one file this writes |
| `<terms-file>` | The tab-separated definitions |
| `<ignore-file>` | The words that look like acronyms and are not |
| `<unknown-file>` | The real acronyms whose expansion nobody has found |
| `<row-width>` | The width a rendered `\| ACRONYM \| Expansion \|` row stays under |
| `<check-command>` | The check, default mode: the entry point that runs `check-acronyms.sh` from this folder with `--config <extension.json>` |
| `<list-command>` | The check in list mode |
| `<verify-command>` | The check that reads every row back against its source |
| `<write-command>` | The command that renders `<dictionary-page>` |
| `<no-source-text>` | What the page prints for a row a person answered |
| `<standard-term-text>` | The fourth column of a row for a universally known term |
| `<lookup-sources>` | The documents searched for an expansion, in order |
| `<first-lookup-source>` | The first of them, where the parenthesis search starts |
| `<answerer>` | Who is asked when no document states an expansion |
| `<ask-method>` | How that question is asked |
| `<wording-pass>` | The check that owns everything else about shipped text |
| `<writers>` | The skills that write into `<docs-roots>` and so run the check |

## 1. What the rule covers

In scope: every `.md` file under `<docs-roots>`.

Out of scope, and the reasons matter:

- Copied dumps under `<excluded-paths>`, such as source bodies and the
  metadata a database reports for a table. The reader is reading the dump, not
  prose. Hand-written files beside the dumps stay in scope.
- Markdown under `<local-only-paths>`, which never leaves this side.
- Tracker text: issue bodies, pull request bodies, and comments pasted into a
  tracker. Those are read in a text box, not a file.
- Memory index files and memory files, which are one-line entries.

`<dictionary-page>` is in scope like any other document, and it holds only
expansions the dictionary already carries, so it covers itself.

A document whose wording is evidence, such as one converted from a source
document, is covered like any other. A wording pass may skip it because its
wording belongs to whoever wrote the source, and this check writes nothing
into it either. A converted functional spec is exactly where the acronyms are
thickest, so it is where the dictionary grows fastest.

## 2. What counts as an acronym

A run of two or more capitals, digits allowed, standing on its own in prose.
`HTTP`, `ISO`, `B2B`, `ABCD`.

What the scan leaves alone, because none of it is an acronym the reader needs
expanded:

- Anything inside a fenced block, at whatever fence depth, or inside backticks.
- Any word touching an underscore or a hyphen. `ORDER_ID` is a column name,
  and `AB-CDE-021` is a coverage id.
- URLs and file paths.
- Table rows. A row holds values read out of the application: names, street
  addresses, place names, status codes. They arrive in capitals and none of
  them wants a definition.
- The words in `<ignore-file>`: capitalized ordinary English, SQL keywords,
  the place names the documents shout, and the one-offs a document brings. A
  definition in `<terms-file>` outranks this list, so a word that is both
  ordinary English and an acronym counts as defined once the dictionary says
  what it stands for.

## 3. The dictionary

Three files carry the vocabulary. `<terms-file>` holds the definitions,
`<ignore-file>` the words that look like acronyms and are not, and
`<unknown-file>` the acronyms whose expansion nobody has found. Every short
form a document uses lands in one of the three.

`<terms-file>` holds the definitions. Four tab-separated columns:

    ACRONYM   Expansion   scope glob   where the expansion was confirmed

`scope` defaults to `*`. The longest matching glob wins, so an acronym can mean
one thing under one folder and something else everywhere else. Two definitions
of equal reach for the same path is an error rather than a silent pick: narrow
one of them.

The expansion is short enough that `| ACRONYM | Expansion |` stays under
`<row-width>` characters. The loader refuses a row that does not.

The fourth column is what the rest of it rests on. Every expansion is confirmed
against a file in the repository, and the column names that file. The one
other form it takes is a person's answer, for a term the repository uses and
never spells out.

That form is provenance for this side, and it stops here. `<dictionary-page>`
renders such a row as `<no-source-text>`, because the reader is being told
whether there is a file to open, and naming whoever answered on this side
answers a question they did not ask.

An expansion nobody can source is asked about, never guessed. A wrong one is
worse than a missing one: it stands in the dictionary, and the next person
reads it as settled. Leaving an acronym undefined costs a question; a plausible
expansion nobody checked costs more.

When the question comes back unanswered, the word goes in `<unknown-file>`.
That list is for a real acronym whose words nobody has found: one the
documents only ever gloss, or one that is the name of a product. The check
reports these and does not fail on them, so a document using one still lands.

`<ignore-file>` is not the place for those. It says there is nothing to
expand, and a real acronym parked there is a question nobody gets asked again.
A word leaves `<unknown-file>` in one direction only, into `<terms-file>`, once
a document states the expansion or `<answerer>` does.

The check that proves a row rather than trusting it:

```bash
<verify-command>
```

It opens each row's cited file and looks for the acronym and the expansion
sitting together: a glossary heading, a table row, or the parenthesis a
document opens the first time it uses the short form. The expansion turning up
somewhere else in that file does not pass. A file can name a category one way
on page 3 and use a different code on page 9, and a row built on that reads as
sourced when nobody checked. Run it whenever rows are added, and read the rows
it lists as answered by a person: those are the ones no file can confirm.

A row whose fourth column names a file that does not exist fails the check, so
deleting or renaming a cited document has to be followed by repointing its rows.
A fourth column counts as a file when it ends in `.md`, or holds a slash and no
whitespace and is not a URL.

A universally known technical term has no file to cite, so a row for one says
`<standard-term-text>` in its fourth column. Such a row is there only because
`<answerer>` asked for it by name. The rest of that family sits in
`<ignore-file>`, which is where one belongs unless someone asks for the row.

## 4. The document that ships

`<dictionary-page>` is the dictionary rendered for the reader. It is generated
whole from `<terms-file>` and `<unknown-file>`:

```bash
<write-command>
```

Three tables. The acronyms that mean one thing everywhere, with the file that
states each expansion; the handful that read differently under one folder,
with the paths that narrows to; and the short forms nobody has found the words
for, listed so the reader knows the term is a short form rather than a code.

A source under `<docs-roots>` is written as a link, because that file ships
too. A path outside it, such as source code or a schema dump, is written as
text: it names where the expansion was confirmed, and the reader has no such
file to open. A row a person answered for renders as `<no-source-text>`, so no
name ships, and a row for a universally known term says so.

Editing the page by hand is undone by the next run. The row in `<terms-file>`
is what a reader who disagrees with an expansion is arguing with, so a
correction goes there and the page is regenerated.

Every run of the check compares the page on disk against what the dictionary
renders and exits 3 when it is behind, so a row added without regenerating
stops the commit rather than shipping a page that omits it.

## 5. Adding a definition

The check defines nothing. An acronym it has never seen stops the run:

    <docs-root>/guide/Notes.md:12: UNKNOWN: XYZ

A definition comes out of the documentation in the repository. Not from
general knowledge, not from what the letters obviously suggest, and not from a
sibling acronym that looks similar. Search `<lookup-sources>`, in order.

Two searches find most of them. The documents mostly introduce an acronym in
parentheses after the words, and a stage or status code is usually defined in
a list of its siblings, so search for the parenthesized short form in the
first source, then for the words it seems to stand for across `<docs-roots>`:

```bash
grep -rn "(XYZ)" <first-lookup-source>
grep -rniE "words it seems to stand for" <docs-root>
```

A term that appears in the documents many times and is never expanded is not a
term to infer. Say where it appears, say what the surrounding text implies,
and ask `<answerer>` with `<ask-method>`.

Found it: add the row with the path that states it, then run
`<verify-command>` and watch that row pass. A citation is not a confirmation,
and the difference only shows up when something reads the file back.

Not found: leave the acronym undefined and ask `<answerer>` with
`<ask-method>`. An undefined acronym stops the document that uses it, which is
the rule working rather than failing. The row goes in when a source turns up,
not when a reading of the letters sounds right.

Copy the wording the document uses. A document writing `Mgmt. Review Board`
has not said `Management Review Board`, and finishing the word is inference:
either find the file that spells it out, or use what the document says.

Not every capitalized word is an acronym. A status code, a place name, or a
shouted heading goes into `<ignore-file>` instead, with the same care: a real
acronym parked there is a definition nobody will be asked for again.

`<ignore-file>` is grouped: each group sits under the comment that says what
its words are. A new word goes into its group by hand, in alphabetical order
within that group. Never sort the whole file; a sort pulls every comment line
into the words and interleaves the group headers.

## 6. Running it

```bash
<check-command>
```

With no arguments it covers the files the branch changed under `<docs-roots>`,
including uncommitted ones. Named paths cover exactly those:

```bash
<check-command> <docs-root>/guide/Notes.md
```

Four modes and three exit codes:

| Mode | What it does |
| --- | --- |
| default (`<check-command>`) | reports the acronyms no dictionary row covers |
| list (`<list-command>`) | prints every acronym each file uses, marking the undefined |
| verify (`<verify-command>`) | reads every dictionary row back against the file it cites |
| write (`<write-command>`) | renders the dictionary into `<dictionary-page>` |

Exit 0 is clean, 2 is an acronym with no definition and none of the three
lists accounting for it, 3 is `<dictionary-page>` sitting behind the
dictionary. A word on `<unknown-file>` prints as `PENDING` and passes.

`<dictionary-page>` is the only file under `<docs-roots>` any of this writes,
and it is written from the dictionary rather than edited, so a run can be
repeated as often as it is useful and the only thing a person changes is
`<terms-file>` or `<ignore-file>`.

The scripts ship in this folder: `check-acronyms.sh` runs the modes above,
`acronyms.py` finds the acronyms, `verify-terms.py` reads the rows back, and
`write-acronyms.py` renders the page. Each takes `--config <file>` first, a JSON
file naming `<terms-file>`, `<ignore-file>`, `<unknown-file>`,
`<dictionary-page>`, the paths covered and skipped, and the page's opening
text. A path in it is relative to the git toplevel of the config's folder, and
`config.py` lists every key. A missing config exits 64.

## 7. Where it sits in a commit

Run it after the writing is finished and before the commit, alongside
`<wording-pass>`, which is the check that owns everything else about shipped
text. Order matters only in that the wording pass comes first, since rewording
a paragraph can change which acronyms a file uses.

The check before the commit is one question: does `<check-command>` exit 0
over the files the branch changed? A branch that added a row commits the
regenerated `<dictionary-page>` alongside it.

## 8. Which skills run it

Every skill that writes a file under `<docs-roots>` runs it before its commit.
The extension lists them in `<writers>`. A skill that writes only tracker
text, such as an issue body, does not: that text is not a file.
