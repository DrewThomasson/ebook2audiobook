---
name: narrate-chapter
description: >-
  Direct the reading of an ebook chapter by chapter: export its chapter blocks, read a whole
  chapter, write reading directions (`[direct:...]`, `[pause:N]`, `[voice:...]`) into its
  text, record every name in the pronunciation guide, then convert the marked-up chapter with
  Maya1 or Zonos. Use when asked to narrate, direct or mark up a chapter or a book -
  "/narrate-chapter book.epub 3", "make chapter 3 more expressive".
---

# Narrate Chapter

`/narrate-chapter <ebook> [chapters] [--engine maya1|zonos]`

The session is the reader: it reads a whole chapter, decides how each passage is read, and
writes that into the chapter's text as SML tags. The app speaks the words; the tags are never
spoken. The engine defaults to `maya1`, which reads English only; a book in another language
uses `zonos`. `<code>` below is the book's language (`ebook-meta <ebook>` shows it). `chapters`
are block indexes from step 1, counted from 0; with none given, ask which after listing them.
A first pass on a book is one chapter.

Every question to the user goes through the ask tool. The session never says how audio
sounds: it names the files and the user listens.

`B` below is `.claude/skills/narrate-chapter/blocks.py`, and `W` is the working folder
`tmp/narrate/<ebook file name without extension>/`, which git ignores.

## 0. Where to work

The pronunciation guide is committed, so work on a branch in a worktree per
[/new-branch](../new-branch/SKILL.md), named `chore/narrate-<book>`, with a slug of two or
three characters: the app fails to start from a long path. Link `python_env` and `models`
into it as [/implement](../implement/SKILL.md) override 4 says. Run every command below from
the worktree. A session already on a branch of its own for this book stays on it.

## 1. Export the blocks

```bash
mkdir -p W
./ebook2audiobook.command --headless --ebook <ebook> --language <code> --tts_engine <engine> --export_blocks W/original.json
cp W/original.json W/marked.json
python3 B list W/marked.json
```

One block is one chapter. `original.json` is never edited: it is what step 4 checks
`marked.json` against. Each export starts a new conversion session and gives the blocks new
ids, so a book already exported keeps its `W` files, and a later chapter is marked in the same
`marked.json`. From then on `<indexes>` in steps 4 and 6 is every chapter marked so far: the
session has one audiobook file, and each conversion rebuilds it from the chapters kept.
Chapters already converted keep their audio, except the last one converted, which redoes its
last sentence, and a chapter with a name whose guide entry changed. To keep an earlier
pass's file as it was, copy it elsewhere before converting.

Done when `list` shows the blocks and the chapters to work on are chosen.

## 2. Read the chapter, then mark it up

`python3 B show W/marked.json <index>` prints one chapter. Read all of it before writing a
tag: who speaks, what each scene is doing, where the tension rises and falls, how it ends.
Then read the keyword table of the chosen engine under `TTS_SML['direct']` in
`lib/conf_models.py`, and the comment above it.

Edit the block's `"text"` in `W/marked.json`. Only tags are added; every word, space and
existing tag stays as it is.

- `[direct:<how to read it>]passage[/direct]` around a passage whose delivery differs from
  plain narration: a line of dialogue by its speaker's mood, rising tension, humor, an ending
  that slows. A direction is under ten words and describes delivery ("whispering, frightened",
  "dry, amused", "slow, solemn"). It is never text to be spoken.
- Build each direction on a word the engine's table maps. Zonos reads nothing but those
  keywords and adds up every entry the direction hits. Maya1 uses one delivery token, that of
  the first entry in table order the direction hits, so give it one table word; the rest of
  the direction reaches it only as a tone description, which changes little on its own.
- Keep a passage short: a line of dialogue with its "she said", a few sentences, a paragraph.
  A `[direct]` passage does not go inside another one.
- Open and close a passage, and place a pause, between sentences. The engine renders the text
  on each side of a tag as a request of its own, so a tag inside a sentence breaks its flow.
  `check` prints a note for each tag that falls inside one; move it unless the text has no
  sentence end near where the delivery changes.
- `[emphasis]word[/emphasis]` in the export marks an italic word, or a few, inside a sentence,
  and stays where it is. It is the one tag that sits inside a sentence without breaking its
  flow: the engine takes it out and reads the words with the rest of the sentence. None is
  added by hand, since no engine turns it into stress.
- Plain narration gets no tag. A chapter where every sentence is directed has no plain
  reading left to differ from.
- `[pause:2]` at a scene break; `N` is seconds. The export may already carry a `[pause]` or
  `[break]` at paragraph breaks, and those stay; the added pause goes beside the one at the
  scene break.
- The export drops double quotation marks, so dialogue is found by its "she said" and by
  sense. When who speaks is unclear, read that part of the ebook itself.
- `[voice:<path to voice file>]passage[/voice]` around a character's lines only when the user
  gave a voice file for that character. `[voice:...]` tags already in the text, such as those
  written by E2A-SML, stay where they are.

Done when every scene of the chapter has been considered and the edits are saved.

## 3. Pronunciation guide

The guide is the file named in "Which guide a book uses" of
[pronunciations/README.md](../../../pronunciations/README.md); `ebook-meta <ebook>` shows the
title and the series. That README also holds the entry format and what an entry matches.

Go through the chapter for every character name and place name, the ordinary ones included,
and look each one up in the guide.

- A name already in the guide: leave its entry as it is. A change to an existing entry is
  made only after the user agrees to it.
- A name missing from the guide gets an entry before the chapter is converted.
  - The book gives the pronunciation (a glossary, an author's note, a character spelling it
    out): use it, and say where it is in the entry's `note`.
  - An ordinary name: `say` equal to `word`. The name is on record and the text is not
    changed.
  - A name the engine is known to read wrong, or an invented name nothing in the book
    settles: propose a respelling, as light as will do, and put it in the list for step 5.
    Heavy respellings (capitals, hyphens) can be read stilted or letter by letter.

Done when every name of the chapter has an entry.

## 4. Check

```bash
python3 B only W/marked.json <indexes>
python3 B check W/original.json W/marked.json --only <indexes>
```

`only` sets every other block to be skipped, so only the chosen chapters are converted.
`check` fails unless `marked.json` is `original.json` with tags added and nothing else, the
tags are well formed, and the blocks outside the chosen chapters are untouched. Fix what it
names and run it again. It prints the tags added to each chapter.

Done when `check` prints `OK`.

## 5. Approval

Ask once, in one form:

- the directions of each chapter as `check` printed them, or the marked-up chapter itself when
  it is short, to approve or edit;
- the proposed respellings from step 3, each to confirm or correct;
- on the first chapter of a book, whether to also render the chapter unmarked for a
  side-by-side listen (preselected yes).

Apply the user's edits, then run step 4 again. Done when the user has approved and `check`
prints `OK`.

## 6. Convert

```bash
./ebook2audiobook.command --headless --ebook <ebook> --language <code> \
  --import_blocks W/marked.json --tts_engine <engine> --pronunciations <guide>
```

Add the options the user converts with, such as `--fine_tuned`, `--device` or `--voice`. The
conversion runs in the session that exported the file, and its audiobook lands in
`audiobooks/cli/cli-<session>/`, where `<session>` is the `"session"` of the blocks file.

For the unmarked render, export again to `W/plain.json` with the same command as step 1,
which starts a second session, run `python3 B only W/plain.json <indexes>`, and convert it
with the same options.

Read the console output of each conversion:

- the `Pronunciation guide:` line names the guide from step 3 and its entry count, or says
  there is none at that path when no chapter so far has had a name;
- each direction prints one `[direct:...] on <engine>:` line with what the engine made of it.
  A direction the engine mapped to nothing is reworded on a table keyword and the chapter
  converted again, or reported as it is.

Done when each conversion exits 0 and its audiobook file exists.

## 7. Commit and report

Commit the guide file alone (`git add pronunciations/<name>.json`), with a message naming the
book and the chapters, and push the branch. The guide grows chapter by chapter on this
branch; open the pull request when the user says the book, or this pass, is done.

Report:

- the path of the marked audiobook, and of the unmarked one when it was rendered;
- the chapters converted and how many directions each carries;
- the names added to the guide, with the respellings the user confirmed;
- any direction the engine mapped to nothing.
