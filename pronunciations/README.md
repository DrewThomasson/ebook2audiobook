# Pronunciation guides

One JSON file per series, or per book that has no series. A guide lists the names and places of the
book and how each one is read, so that every engine reads a name the same way each time it occurs.
Guides are committed here and grow book by book.

## Which guide a book uses

1. The file given with `--pronunciations <path>`.
2. `pronunciations/<series>.json` when the ebook has a series (calibre or EPUB3 metadata).
3. `pronunciations/<title>.json` otherwise. The title is the ebook's own, or its file name when it has none.

`<series>` and `<title>` are written like the audiobook file names: spaces become `_`, `&` becomes `And`,
and `< > : " / \ | ? * ( )` become `_`. "A Song of Ice & Fire" is `A_Song_of_Ice_And_Fire.json`.
A book with a series reads the series guide only, so every book of the series reads the same file.

The conversion prints the guide it uses, or that it found none and where it looked. The GUI shows the
same line when the conversion starts and under the book's name in the blocks editor.

## Format

A JSON list of entries:

```json
[
  {"word": "Qyburn", "say": "KWY-burn"},
  {"word": "Hermione", "say": "her-MY-oh-nee", "ipa": "hɜːrˈmaɪ.əni", "note": "author's website"},
  {"word": "Arya", "say": "Arya"},
  {"word": "ser", "say": "sair", "case_sensitive": false}
]
```

| Key | Required | Meaning |
| --- | --- | --- |
| `word` | yes | The name as the book spells it. It can be several words (`King's Landing`). |
| `say` | yes | The text the engine reads instead. `say` equal to `word` means the name is confirmed as written: it is on record and nothing is changed. |
| `case_sensitive` | no | `true` by default, so `Rose` the character is not `rose` the flower. `false` matches any case. |
| `ipa` | no | Kept for engines that read phonemes. No engine uses it yet. |
| `note` | no | Where the pronunciation comes from. |

An entry with no `word` or no `say`, or whose `case_sensitive` is not `true` or `false`, is left out and
named in the line the conversion prints; the other entries still apply. A file that is not a JSON list is
left out as a whole. The conversion never stops for a guide.

## What an entry matches

- Whole words only, the longest entry first: with `King` and `King's Landing` both listed,
  "King's Landing" is read with its own entry.
- The name followed by a plural or possessive `s`: `Qyburn` also matches "Qyburn's" and `Lannister`
  matches "the Lannisters" and "the Lannisters'". The ending is kept: "KWY-burn's".
- Any other form is its own entry: `Valyria` does not match "Valyrian", and `Jones` does not match "Joneses".
- Chapter titles and the book's title are matched like any other sentence that is read.
- A straight and a curly apostrophe are the same character.
- Text inside an SML tag is never changed: a `[voice:...]` path and a `[direct:...]` note stay as written.
  The text between `[direct:...]` and `[/direct]` is read, so it is matched.

## When an entry changes

The guide is applied when a sentence is given to the engine, not when the ebook is parsed. The blocks,
the GUI editor and `--export_blocks` keep the book's spelling.

Each converted sentence remembers the text the engine was given. On the next run of a book, a sentence
whose text would now be different is converted again and its chapter is put together again; every other
sentence keeps its audio. A chapter block that holds a `[voice]`, `[direct]` or `[emotion]` passage is
converted again as a whole instead, because a passage can run over several sentences.
This holds for each book of a series on its own next run.

## Limits

A respelling gives every engine the same text for a name, which removes most of the drift. Engines that
sample (XTTS, Zonos, Maya1) can still vary a little from one conversion to the next. Heavy respellings
(capitals, hyphens) can sound stilted or be spelled out letter by letter on some engines: listen to one
sentence before converting a whole book.
