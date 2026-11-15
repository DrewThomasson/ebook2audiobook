# Voice casts

One JSON file per series, or per book that has no series. A cast gives each character a voice file, so
that a `[voice:Alice]...[/voice]` passage is read with Alice's voice in every chapter and every book.
The text names the character; only the cast names the file, so recasting a character is one edit here.

A cast does not find who speaks a line. The `[voice:Name]` tags are written by hand in the blocks editor
or in an `--export_blocks` file, or by a tool that marks up dialogue.

## Which cast a book uses

1. The file given with `--cast <path>`.
2. `casts/<series>.json` when the ebook has a series (calibre or EPUB3 metadata).
3. `casts/<title>.json` otherwise. The title is the ebook's own, or its file name when it has none.

`<series>` and `<title>` are written like the audiobook file names: spaces become `_`, `&` becomes `And`,
and `< > : " / \ | ? * ( )` become `_`. "A Song of Ice & Fire" is `A_Song_of_Ice_And_Fire.json`.
A book with a series reads the series cast only, so every book of the series reads the same file.
The [pronunciation guide](../pronunciations/README.md) of a book is found by the same rule.

The conversion prints the cast it uses and its characters, or that it found none and where it looked.
The GUI shows the same line when the conversion starts and under the book's name in the blocks editor.

## Format

A JSON object with one entry per character:

```json
{
  "Alice": {"voice": "voices/eng/adult/female/AnaFlorence.wav", "aliases": ["Ally", "Miss Liddell"]},
  "Bob": {"voice": "voices/eng/adult/male/AaronDreschner.wav", "note": "gruff, older"}
}
```

| Key | Required | Meaning |
| --- | --- | --- |
| the entry's name | yes | The character's name, as the `[voice:Name]` tags write it. |
| `voice` | yes | The voice file. A path that is not absolute starts at the app folder, as a `--voice` path does. |
| `aliases` | no | Other names that lead to the same voice. |
| `note` | no | Anything worth remembering about the choice. |

An entry with no `voice`, with a voice file that is not there, or whose `aliases` is not a list of names is
left out and named in the line the conversion prints; the other entries still apply. When two entries claim
one name, the first keeps it. A file that is not a JSON object is left out as a whole. The conversion never
stops for a cast.

## How a tag is resolved

- A value that is an existing file is a voice file path, as it is without a cast: `[voice:/path/to/alice.wav]`.
- Any other value is looked up in the cast as a name or an alias, whatever its case or spacing:
  `[voice:alice]`, `[voice:Ally]` and `[voice:Miss  Liddell]` all read with Alice's voice.
- A name the cast does not have, or any name when there is no cast, is reported in one line and the passage
  is read with the voice of its chapter block.
- A value written as a path (it has a `/` or `\`, or ends in an audio extension) that leads to no file stops
  the conversion with an error, as it does without a cast.

The narrator is not a cast entry. The narration is read with `--voice`, the voice chosen in the GUI, or the
voice of a chapter block, and a cast leaves those alone.

## Engines

A cast voice is used exactly as a `[voice:/path]` voice is. Engines that clone from a voice file (XTTS,
Zonos, Chatterbox and the like) speak the passage with it. Engines with speakers of their own (Piper,
MeloTTS, Orpheus, OpenVoice, Phonon and the like) speak with their speaker and convert the result toward
the voice file, so the difference between two characters can come through more weakly: listen to one
exchange before converting a whole book.

## When a voice changes

Each converted sentence remembers the text the engine was given, the voice file of its passage included.
On the next run of a book, a sentence whose voice file would now be another one is converted again and its
chapter is put together again; every other sentence keeps its audio. This covers a character given another
voice file, a name added to or taken out of the cast, and each book of a series on its own next run.
A chapter block that also holds a `[direct]` or `[emotion]` passage is converted again as a whole.

The record holds the path of the voice file, not its sound: a voice file replaced under the same name is
not noticed. Give the new recording another file name.
