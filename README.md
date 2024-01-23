# ebook2audiobook
Generates an audiobook with chapters and ebook metadata using Calibre and Xtts from Coqui tts, and with optional voice cloning, and supports multiple languages

## Features

- Converts eBooks to text format using Calibre's `ebook-convert` tool.
- Splits the eBook into chapters for structured audio conversion.
- Uses XTTS from Coqui TTS for high-quality text-to-speech conversion.
- Optional voice cloning feature using a provided voice file.
- Supports different languages for text-to-speech conversion, with English as the default.
- Confirmed to run on only 4 gb ram

## Requirements

- Python 3.x
- `coqui-tts` Python package
- Calibre (for eBook conversion)
- FFmpeg (for audiobook file creation)
- Optional: Custom voice file for voice cloning

### Installation Instructions for Dependencies

Install Python 3.x from [Python.org](https://www.python.org/downloads/).

Install Calibre:
- Ubuntu: `sudo apt-get install -y calibre`
- macOS: `brew install calibre`
- Windows(Powershell in Administrator mode): `choco install calibre` 

Install FFmpeg:
- Ubuntu: `sudo apt-get install -y ffmpeg`
- macOS: `brew install ffmpeg`
- Windows(Powershell in Administrator mode): `choco install ffmpeg` 

Install Python packages:
```bash
pip install tts pydub nltk beautifulsoup4 ebooklib
```

### Supported Languages

The script supports the following languages for text-to-speech conversion:

English (en),
Spanish (es),
French (fr),
German (de),
Italian (it),
Portuguese (pt),
Polish (pl),
Turkish (tr),
Russian (ru),
Dutch (nl),
Czech (cs),
Arabic (ar),
Chinese (zh-cn),
Japanese (ja),
Hungarian (hu),
Korean (ko)

Specify the language code when running the script to use these languages.

### Usage

Navigate to the script's directory in the terminal and execute one of the following commands:

Basic Usage:
```bash
python ebook2audiobook.py <path_to_ebook_file>
```
Replace <path_to_ebook_file> with the path to your eBook file.

With Voice Cloning(Optional):
```bash
python ebook2audiobook.py <path_to_ebook_file> <path_to_voice_file>
```
Replace <path_to_ebook_file> with the path to your eBook file.

Replace <path_to_voice_file> with the path to the voice file for cloning.

With Language Specification(Optional):
```bash
python ebook2audiobook.py <path_to_ebook_file> [path_to_voice_file] [language_code]
```
Replace <path_to_ebook_file> with the path to your eBook file.
Optionally, include <path_to_voice_file> for voice cloning.
Optionally, include <language_code> to specify the language (default is "en" for English).
