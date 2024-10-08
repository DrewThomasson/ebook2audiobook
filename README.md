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
   - **Windows**: [mecab-website-to-install-manually](https://taku910.github.io/mecab/#download) (Note: Japanese support is limited)

5. **Install Python packages**:
   ```bash
   pip install tts==0.21.3 pydub nltk beautifulsoup4 ebooklib tqdm
   
   python -m nltk.downloader punkt
   ```

   **For non-Latin languages**:
   ```bash
   pip install mecab mecab-python3 unidic
   
   python -m unidic download
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

 -Run with CPU only
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```
 -Run with GPU Speedup (Nvida graphics cards only)
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```

This command will start the Gradio interface on port 7860.(localhost:7860)
- For more options like running the docker in headless mode or making the gradio link public add the `-h` parameter after the `app.py` in the docker launch command
<details>
  <summary><strong>Example of using docker in headless mode or modifying anything with the extra parameters + Full guide</strong></summary>
   
## Example of using docker in headless mode

first for a docker pull of the latest with
```bash 
docker pull registry.hf.space/drewthomasson-ebook2audiobookxtts:latest
```

- Before you do run this you need to create a dir named "input-folder" in your current dir which will be linked, This is where you can put your input files for the docker image to see
```bash
mkdir input-folder && mkdir Audiobooks
```

- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/Audiobooks:/home/user/app/Audiobooks \
    --platform linux/amd64 \
    registry.hf.space/drewthomasson-ebook2audiobookxtts:latest \
    python app.py --headless True --ebook /home/user/app/input_folder/YOUR_INPUT_FILE.TXT
```

- And that should be it! 

- The output Audiobooks will be found in the Audiobook folder which will also be located in your local dir you ran this docker command in


## To get the help command for the other parameters this program has you can run this 

```bash
docker run -it --rm \
    --platform linux/amd64 \
    registry.hf.space/drewthomasson-ebook2audiobookxtts:latest \
    python app.py -h

```


and that will output this 

```bash
user/app/ebook2audiobookXTTS/input-folder -v $(pwd)/Audiobooks:/home/user/app/ebook2audiobookXTTS/Audiobooks --memory="4g" --network none --platform linux/amd64 registry.hf.space/drewthomasson-ebook2audiobookxtts:latest python app.py -h
starting...
usage: app.py [-h] [--share SHARE] [--headless HEADLESS] [--ebook EBOOK] [--voice VOICE]
              [--language LANGUAGE] [--use_custom_model USE_CUSTOM_MODEL]
              [--custom_model CUSTOM_MODEL] [--custom_config CUSTOM_CONFIG]
              [--custom_vocab CUSTOM_VOCAB] [--custom_model_url CUSTOM_MODEL_URL]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the
Gradio interface or run the script in headless mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --share SHARE         Set to True to enable a public shareable Gradio link. Defaults
                        to False.
  --headless HEADLESS   Set to True to run in headless mode without the Gradio
                        interface. Defaults to False.
  --ebook EBOOK         Path to the ebook file for conversion. Required in headless
                        mode.
  --voice VOICE         Path to the target voice file for TTS. Optional, uses a default
                        voice if not provided.
  --language LANGUAGE   Language for the audiobook conversion. Options: en, es, fr, de,
                        it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko. Defaults to
                        English (en).
  --use_custom_model USE_CUSTOM_MODEL
                        Set to True to use a custom TTS model. Defaults to False. Must
                        be True to use custom models, otherwise you'll get an error.
  --custom_model CUSTOM_MODEL
                        Path to the custom model file (.pth). Required if using a custom
                        model.
  --custom_config CUSTOM_CONFIG
                        Path to the custom config file (config.json). Required if using
                        a custom model.
  --custom_vocab CUSTOM_VOCAB
                        Path to the custom vocab file (vocab.json). Required if using a
                        custom model.
  --custom_model_url CUSTOM_MODEL_URL
                        URL to download the custom model as a zip file. Optional, but
                        will be used if provided. Examples include David Attenborough's
                        model: 'https://huggingface.co/drewThomasson/xtts_David_Attenbor
                        ough_fine_tune/resolve/main/Finished_model_files.zip?download=tr
                        ue'. More XTTS fine-tunes can be found on my Hugging Face at
                        'https://huggingface.co/drewThomasson'.

Example: python script.py --headless --ebook path_to_ebook --voice path_to_voice
--language en --use_custom_model True --custom_model model.pth --custom_config
config.json --custom_vocab vocab.json
```
</details>

#### 🖥️ Docker GUI 

<img width="1401" alt="Screenshot 2024-08-25 at 10 08 40 AM" src="https://github.com/user-attachments/assets/78cfd33e-cd46-41cc-8128-3820160a5e40">
<img width="1406" alt="Screenshot 2024-08-25 at 10 08 51 AM" src="https://github.com/user-attachments/assets/dbfad9f6-e6e5-4cad-b248-adb76c5434f3">

### 🛠️ For Custom Xtts Models

Models built to be better at a specific voice. Check out my Hugging Face page [here](https://huggingface.co/drewThomasson).

To use a custom model, paste the link of the `Finished_model_files.zip` file like this:

[David Attenborough fine tuned Finished_model_files.zip](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true)




More details can be found at the [Dockerfile Hub Page]([https://github.com/DrewThomasson/ebook2audiobookXTTS](https://hub.docker.com/repository/docker/athomasson2/ebook2audiobookxtts/general)).

## 🌐 Fine Tuned Xtts models

To find already fine-tuned XTTS models, visit [this Hugging Face link](https://huggingface.co/drewThomasson) 🌐. Search for models that include "xtts fine tune" in their names.

## 🎥 Demos

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

## 🤗 [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobookXTTS)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just don't give it giant files is all
- Best to duplicate space or run locally.
## 📚 Supported eBook Formats

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection

## 📂 Output

- Creates an `.m4b` file with metadata and chapters.
- **Example Output**: ![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## 🛠️ Common Issues:
- "It's slow!" - On CPU only this is very slow, and you can only get speedups though a NVIDIA GPU. [Discussion about this](https://github.com/DrewThomasson/ebook2audiobookXTTS/discussions/19#discussioncomment-10879846) For faster multilingual generation I would suggest my other [project that uses piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) instead(It doesn't have zero-shot voice cloning though, and is siri quality voices, but it is much faster on cpu.)
- "I'm having dependency issues" - Just use the docker, its fully self contained and has a headless mode, add `-h` parameter after the `app.py` in the docker run command for more information.
- "Im getting a truncated audio issue!" - PLEASE MAKE AN ISSUE OF THIS, I don't speak every language and I need advise from each person to fine tune my sentense splitting function on any other languages.😊
- "The loading bar is stuck at 30% in the web gui!" - The web gui loading bar is extreamly basic as its just split between the three loading steps, refer to the terminal and what sentense it's on for a more accurate gauge on where is it progress wise.

## 🙏 Special Thanks

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/coqui-ai/TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
