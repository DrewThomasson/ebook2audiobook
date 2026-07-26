# E2A-SML

Turn an ebook into speaker-attributed SML for multi-voice audiobook generation with [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook).

E2A-SML uses [BookNLP](https://github.com/DrewThomasson/booknlp) to find characters, attribute dialogue, estimate speaker traits, and assign compatible voices. Use the web interface to review assignments or the CLI for automated processing.

```text
Book → character and dialogue analysis → voice assignment → SML + voice map
```

## Quick start

Docker is the easiest option because it includes BookNLP, spaCy, Calibre, and Gradio.

From `components/E2A-SML`:

```bash
docker compose up --build
```

Open <http://localhost:7861>, upload a book, review the detected speakers, and download the generated SML files.

The Compose configuration mounts the repository at `/ebook2audiobook`, so the app can use its voice library. Generated files persist in `components/E2A-SML/output`.

## What you get

| File | Purpose |
|---|---|
| `{book_id}.sml.txt` | Book text containing `[voice:CharacterName]` tags |
| `{book_id}.sml.json` | Maps the character names to voice files |
| `{book_id}.deprecated.sml.txt` | Legacy output with voice paths embedded in the tags |

Example:

```text
[voice:Narrator]
It was a bright cold day in April.
[/voice]
[voice:Winston]
"Freedom is the freedom to say that two plus two make four."
[/voice]
```

The matching JSON voice map looks like:

```json
{
  "macros": {
    "voices": {
      "Narrator": "/path/to/narrator_voice.wav",
      "Winston": "/path/to/male_voice.wav"
    }
  }
}
```

## Features

- Character detection and coreference resolution
- Dialogue attribution
- Gender and age-category estimates
- Automatic or manual voice assignment
- SML output compatible with ebook2audiobook
- Gradio web interface and headless CLI
- Docker support
- `.txt`, `.epub`, `.mobi`, `.pdf`, `.html`, `.fb2`, `.azw`, and `.azw3` input

Non-text formats require [Calibre](https://calibre-ebook.com/download) when running locally.

## Local installation

First install ebook2audiobook so its Python environment and voice library are available.

macOS or Linux:

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
./ebook2audiobook.command
conda activate ./python_env
cd components/E2A-SML
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Windows:

```bat
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
ebook2audiobook.cmd
conda activate .\python_env
cd components\E2A-SML
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Launch the web interface:

```bash
python cli.py --gui
```

Then open <http://localhost:7861> if it does not open automatically.

## CLI examples

Run these commands from `components/E2A-SML`.

```bash
# Analyze a book and write to output/
python cli.py mybook.txt

# Choose another output directory
python cli.py mybook.txt --output-dir ./my-output

# Process an EPUB (Calibre required)
python cli.py mybook.epub

# Prefer accuracy over speed
python cli.py mybook.txt --model big

# Reuse an existing BookNLP analysis
python cli.py \
  --booknlp-dir ./existing-output \
  --book-id mybook \
  --output-dir ./sml-output
```

For every option:

```bash
python cli.py --help
```

## Docker CLI

From `components/E2A-SML`:

```bash
docker build -t e2a-sml .

docker run --rm \
  -v "$(pwd)/../..:/ebook2audiobook" \
  -v "$(pwd)/output:/app/output" \
  -v "/absolute/path/to/mybook.txt:/app/mybook.txt:ro" \
  e2a-sml python cli.py /app/mybook.txt --output-dir /app/output
```

## How voice assignment works

When an ebook2audiobook installation is available, E2A-SML matches inferred speaker traits to directories such as:

| Speaker | Voice directory |
|---|---|
| Adult woman | `voices/eng/adult/female/` |
| Adult man | `voices/eng/adult/male/` |
| Teen girl | `voices/eng/teen/female/` |
| Teen boy | `voices/eng/teen/male/` |
| Child girl | `voices/eng/child/female/` |
| Child boy | `voices/eng/child/male/` |
| Elder woman | `voices/eng/elder/female/` |
| Elder man | `voices/eng/elder/male/` |

BookNLP’s attribution and trait estimates are predictions. The web interface lets you review and correct voice assignments before generating the final files.

## CLI reference

```text
usage: cli.py [-h] [-o OUTPUT_DIR] [--model {small,big}] [--e2a-path E2A_PATH]
              [--voices-dir VOICES_DIR] [--language LANGUAGE]
              [--booknlp-dir BOOKNLP_DIR] [--book-id BOOK_ID]
              [--gui] [--host HOST] [--port PORT] [--share]
              [input_file]

Options:
  input_file              Input book (.txt, .epub, .mobi, .pdf, and others)
  -o, --output-dir        Output directory (default: output/)
  --model {small,big}     BookNLP model (default: small)
  --e2a-path              ebook2audiobook repository path
  --voices-dir            Custom voice directory
  --language              Voice-selection language code (default: eng)
  --booknlp-dir           Existing BookNLP output directory
  --book-id               ID used to load existing BookNLP output
  --gui                   Launch the web interface
  --host                  Interface host (default: 127.0.0.1)
  --port                  Interface port (default: 7861)
  --share                 Create a public Gradio share link
```

## Requirements

For Docker:

- Docker with Docker Compose
- A local ebook2audiobook checkout for voice-library access

For local use:

- Python 3.10+
- Packages in `requirements.txt`
- The `en_core_web_sm` spaCy model
- Calibre for non-text ebook conversion
- ebook2audiobook for its voice library

## License

MIT
