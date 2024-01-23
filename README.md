# ebook2audiobook
Generates an audiobook with chapters and ebook metadata using Calibre and Xtts from Coqui tts, and with optional voice cloning, and supports multiple languages

## Features

- Converts eBooks to text format using Calibre's `ebook-convert` tool.
- Splits the eBook into chapters for structured audio conversion.
- Uses XTTS from Coqui TTS for high-quality text-to-speech conversion.
- Optional voice cloning feature using a provided voice file.
- Supports different languages for text-to-speech conversion, with English as the default.

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

Install FFmpeg:
- Ubuntu: `sudo apt-get install -y ffmpeg`
- macOS: `brew install ffmpeg`

Install Python packages:
```bash
pip install tts pydub nltk beautifulsoup4
```
Usage

Navigate to the script's directory in the terminal and execute one of the following commands:

Basic Usage:
```bash
Copy code
python ebook_to_audiobook.py <path_to_ebook_file>
```
Replace <path_to_ebook_file> with the path to your eBook file.

With Voice Cloning(Optional):
```bash
python ebook_to_audiobook.py <path_to_ebook_file> <path_to_voice_file>
```
Replace <path_to_ebook_file> with the path to your eBook file.

Replace <path_to_voice_file> with the path to the voice file for cloning.

With Language Specification(Optional):
```bash
python ebook_to_audiobook.py <path_to_ebook_file> [path_to_voice_file] [language_code]
```
Replace <path_to_ebook_file> with the path to your eBook file.
Optionally, include <path_to_voice_file> for voice cloning.
Optionally, include <language_code> to specify the language (default is "en" for English).
