# 📚 SML Book Dialog Extractor

Uses [BookNLP](https://github.com/DrewThomasson/booknlp) to analyze books, extract character dialog, and generate **SML-formatted output** for multi-speaker audiobook generation with [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook).

## ✨ Features

- **Automatic character detection** — identifies characters, their gender, and age category
- **Dialog attribution** — determines who speaks each line of dialog
- **SML output** — generates `[voice:]...[/voice]` tagged text compatible with ebook2audiobook
- **Voice auto-assignment** — matches characters to appropriate voices from the ebook2audiobook voice library based on gender and age
- **Web GUI** — Gradio-based web interface for easy voice assignment and preview
- **Headless CLI** — full command-line interface for batch/automated processing
- **Docker support** — fully containerized with all dependencies pre-installed
- **Multiple formats** — supports .txt, .epub, .mobi, .pdf, .html, .fb2, .azw, .azw3 (non-txt requires [Calibre](https://calibre-ebook.com/download))

## 🐳 Docker (Recommended)

The easiest way to run the tool — all dependencies (BookNLP, spaCy, Calibre, Gradio) are pre-installed.

### Quick Start with Docker Compose

```bash
# 1. Clone this repo
git clone https://github.com/DrewThomasson/E2A-SML.git
cd E2A-SML

# 2. Start the container (it automatically mounts the parent ebook2audiobook folder)

# 3. Build and run
docker compose up --build
```

Open http://localhost:7860 in your browser. The ebook2audiobook path is pre-filled as `/ebook2audiobook`.

### Docker CLI

```bash
# Build the image
docker build -t sml-extractor .

# Run the web GUI (mount your ebook2audiobook folder)
docker run -p 7860:7860 -v $(pwd)/../..:/ebook2audiobook sml-extractor

# Run headless mode
docker run -v $(pwd)/../..:/ebook2audiobook -v ./output:/app/output \
  -v ./mybook.txt:/app/mybook.txt \
  sml-extractor python cli.py /app/mybook.txt -o /app/output
```

## 🚀 Local Installation

### Installation

```bash
git clone https://github.com/DrewThomasson/E2A-SML.git
cd E2A-SML
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Web GUI

```bash
python cli.py --gui
```

Opens a browser-based interface where you can:
1. Upload a book file
2. View detected characters with their gender/age
3. Assign voices (auto or manual)
4. Generate and download SML output

### Command Line (Headless)

```bash
# Basic - analyze a book and generate SML output
python cli.py mybook.txt

# With custom output directory
python cli.py mybook.txt -o output/

# Process an epub (requires Calibre)
python cli.py mybook.epub

# Use the more accurate (but slower) BookNLP model
python cli.py mybook.txt --model big

# Use pre-existing BookNLP output
python cli.py --booknlp-dir existing_output/ --book-id mybook -o sml_output/
```

## 📖 How It Works

### Pipeline

```
Input Book → [BookNLP Analysis] → Character Detection → Dialog Attribution
                                                            ↓
                                              Voice Assignment (auto/manual)
                                                            ↓
                                              SML Output + Characters JSON
```

### Step 1: BookNLP Analysis

BookNLP processes the book text and produces:
- **Entity detection** — identifies characters, locations, organizations
- **Coreference resolution** — clusters references (e.g., "Tom", "Tom Sawyer", "Mr. Sawyer" → same person)
- **Quote attribution** — determines who speaks each quoted passage
- **Gender inference** — infers character gender from pronoun usage
- **Age inference** — estimates age category from context clues

### Step 2: SML Generation

The tool converts BookNLP's tagged output into SML format:

**BookNLP format** (`book.txt`):
```
[Narrator] It was a bright cold day in April, and the clocks were striking thirteen. [/]
[Winston] "Freedom is the freedom to say that two plus two make four." [/]
[OBrien] "How many fingers am I holding up, Winston?" [/]
```

**SML output** (for ebook2audiobook):
```
[voice:/path/to/narrator_voice.wav]
It was a bright cold day in April, and the clocks were striking thirteen.
[/voice]
[voice:/path/to/winston_voice.wav]
"Freedom is the freedom to say that two plus two make four."
[/voice]
[voice:/path/to/obrien_voice.wav]
"How many fingers am I holding up, Winston?"
[/voice]
```

### Step 3: Voice Assignment

When given the path to an ebook2audiobook installation, voices are automatically matched:

| Character Property | Voice Directory |
|---|---|
| adult + female | `voices/eng/adult/female/` |
| adult + male | `voices/eng/adult/male/` |
| teen + female | `voices/eng/teen/female/` |
| teen + male | `voices/eng/teen/male/` |
| child + female | `voices/eng/child/female/` |
| child + male | `voices/eng/child/male/` |
| elder + female | `voices/eng/elder/female/` |
| elder + male | `voices/eng/elder/male/` |

## 📁 Output Files

| File | Description |
|---|---|
| `{book_id}.sml.txt` | SML-tagged text with `[voice:]...[/voice]` tags |
| `{book_id}.characters.json` | Character metadata with voice assignments |

### characters.json format

```json
{
  "characters": [
    {
      "normalized_name": "Narrator",
      "inferred_gender": "unknown",
      "inferred_age_category": "unknown",
      "tts_engine": "XTTSv2",
      "language": "eng",
      "voice": "/path/to/voice.wav"
    },
    {
      "normalized_name": "Winston",
      "inferred_gender": "male",
      "inferred_age_category": "adult",
      "tts_engine": "XTTSv2",
      "language": "eng",
      "voice": "/path/to/male_voice.wav"
    }
  ]
}
```

## 🖥️ CLI Reference

```
usage: cli.py [-h] [-o OUTPUT_DIR] [--model {small,big}] [--e2a-path E2A_PATH]
              [--voices-dir VOICES_DIR] [--language LANGUAGE]
              [--booknlp-dir BOOKNLP_DIR] [--book-id BOOK_ID]
              [--gui] [--host HOST] [--port PORT] [--share]
              [input_file]

Options:
  input_file              Input book file (.txt, .epub, .mobi, .pdf, etc.)
  -o, --output-dir        Output directory (default: output/)
  --model {small,big}     BookNLP model size (default: small)
  --e2a-path              Path to ebook2audiobook repo (auto-detected by default)
  --voices-dir            Path to custom voice files directory
  --language              Language code for voice selection (default: eng)
  --booknlp-dir           Use existing BookNLP output directory
  --book-id               Book ID for loading existing BookNLP output
  --gui                   Launch web GUI
  --host                  Web GUI host (default: 127.0.0.1)
  --port                  Web GUI port (default: 7860)
  --share                 Create public Gradio share link
```

## 🔧 Requirements

### Docker (recommended)
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook) cloned locally (for the voice library)

### Local installation
- Python 3.10+
- [BookNLP-plus](https://github.com/DrewThomasson/booknlp) (installed via requirements.txt)
- [Calibre](https://calibre-ebook.com/download) (optional, for non-txt ebook formats)
- [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook) (required, for voice library)

## 📄 License

MIT
