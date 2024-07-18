# 📚 ebook2audiobook

Convert eBooks to audiobooks with chapters and metadata using Calibre and Coqui XTTS. Supports optional voice cloning and multiple languages!

## 🌟 Features

- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
- 🎙️ High-quality text-to-speech with Coqui XTTS.
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports multiple languages (English by default).
- 🖥️ Designed to run on 4GB RAM.

## 🛠️ Requirements

- Python 3.x
- `coqui-tts` Python package
- Calibre (for eBook conversion)
- FFmpeg (for audiobook creation)
- Optional: Custom voice file for voice cloning

### 🔧 Installation Instructions

1. **Install Python 3.x** from [Python.org](https://www.python.org/downloads/).

2. **Install Calibre**:
   - **Ubuntu**: `sudo apt-get install -y calibre`
   - **macOS**: `brew install calibre`
   - **Windows** (Admin Powershell): `choco install calibre`

3. **Install FFmpeg**:
   - **Ubuntu**: `sudo apt-get install -y ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows** (Admin Powershell): `choco install ffmpeg`

4. **Optional: Install Mecab** (for non-Latin languages):
   - **Ubuntu**: `sudo apt-get install -y mecab libmecab-dev mecab-ipadic-utf8`
   - **macOS**: `brew install mecab`, `brew install mecab-ipadic`
   - **Windows** (Admin Powershell): `choco install mecab` (Note: Japanese support is limited)

5. **Install Python packages**:
   ```bash
   pip install tts==0.21.3 pydub nltk beautifulsoup4 ebooklib tqdm
   ```

   **For non-Latin languages**:
   ```bash
   python -m unidic download
   pip install mecab mecab-python3 unidic
   ```

## 🌐 Supported Languages

- **English (en)**
- **Spanish (es)**
- **French (fr)**
- **German (de)**
- **Italian (it)**
- **Portuguese (pt)**
- **Polish (pl)**
- **Turkish (tr)**
- **Russian (ru)**
- **Dutch (nl)**
- **Czech (cs)**
- **Arabic (ar)**
- **Chinese (zh-cn)**
- **Japanese (ja)**
- **Hungarian (hu)**
- **Korean (ko)**

Specify the language code when running the script.

## 🚀 Usage

### 🖥️ Gradio Web Interface

1. **Run the Script**:
   ```bash
   python custom_model_ebook2audiobookXTTS_gradio.py
   ```

2. **Open the Web App**: Click the URL provided in the terminal to access the web app and convert eBooks.

### 📝 Basic Usage

```bash
python ebook2audiobook.py <path_to_ebook_file> [path_to_voice_file] [language_code]
```

- **<path_to_ebook_file>**: Path to your eBook file.
- **[path_to_voice_file]**: Optional for voice cloning.
- **[language_code]**: Optional to specify language.

### 🧩 Custom XTTS Model

```bash
python custom_model_ebook2audiobookXTTS.py <ebook_file_path> <target_voice_file_path> <language> <custom_model_path> <custom_config_path> <custom_vocab_path>
```

- **<ebook_file_path>**: Path to your eBook file.
- **<target_voice_file_path>**: Optional for voice cloning.
- **<language>**: Optional to specify language.
- **<custom_model_path>**: Path to `model.pth`.
- **<custom_config_path>**: Path to `config.json`.
- **<custom_vocab_path>**: Path to `vocab.json`.

### 🐳 Using Docker

You can also use Docker to run the eBook to Audiobook converter. This method ensures consistency across different environments and simplifies setup.

#### 🚀 Running the Docker Container

To run the Docker container and start the Gradio interface, use the following command:

```powershell
docker run -it --rm -p 7860:7860 athomasson2/ebook2audiobookxtts:latest
```

This command will start the Gradio interface on port 7860.

More details can be found at the [Dockerfile Hub Page](https://github.com/DrewThomasson/ebook2audiobookXTTS).

## 🎥 Demos

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

## 📚 Supported eBook Formats

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection

## 📂 Output

- Creates an `.m4b` file with metadata and chapters.
- **Example Output**: ![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## 🙏 Special Thanks

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/coqui-ai/TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
