# this is a sample for running on kaggle and it may not be updated frequently

# ebook2audiobook kaggle eddition
Generates an audiobook with chapters and ebook metadata using Calibre and Xtts from Coqui tts, and with optional voice cloning, and supports multiple languages

# import this notebook to kaggle
https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/kaggle-ebook2audiobook-demo.ipynb

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

Install Mecab for (Non Latin-based Languages tts support)(Optional):
- Ubuntu: `sudo apt-get install -y mecab libmecab-dev mecab-ipadic-utf8`
- macOS: `brew install mecab`, `brew install mecab-ipadic`
- Windows(Powershell in Administrator mode no support for mecab-ipadic easy install so no Japanese for windows :/): `choco install mecab ` 

Install Python packages:
```bash
pip install tts pydub nltk beautifulsoup4 ebooklib tqdm
```
(For non Latin-based Languages tts support)(Optional)  
`python -m unidic download`
```bash
pip install mecab mecab-python3 unidic
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
If you have any trouble getting it to run in Windows then it should run fine in WSL2

Basic Usage: ALL PARAMETERS ARE MANDATORY WHEN CALLED THE SCRIPT

```bash
python ebook2audiobook.py <path_to_ebook_file> [path_to_voice_file] [language_code]
```
Replace <path_to_ebook_file> with the path to your eBook file.
include <path_to_voice_file> for voice cloning.
include <language_code> to specify the language


## Demo



https://github.com/DrewThomasson/ebook2audiobookXTTS/assets/126999465/bccd7240-f967-4d27-a87d-445034db7d21



### Supported ebook File Types: 
.epub, .pdf, .mobi, .txt, .html, .rtf, .chm, .lit, .pdb, .fb2, .odt, .cbr, .cbz, .prc, .lrf, .pml, .snb, .cbc, .rb, and .tcr,
(Best results are from using epub or mobi for auto chapter detection)

### outputs as a m4b with all book metadata and chapters, example output file in an audiobook player app
![Example_of_output_in_audiobook_program](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

A special thanks to the creaters of:


-Coqui TTS

-https://github.com/coqui-ai/TTS


-Calibre

-https://calibre-ebook.com
