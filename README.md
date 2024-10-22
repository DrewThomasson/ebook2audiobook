# 📚 ebook2audiobook

Convert eBooks to audiobooks with chapters and metadata using Calibre and Coqui XTTS. Supports optional voice cloning and multiple languages!


#### 🖥️ Web GUI Interface
![demo_web_gui](https://github.com/user-attachments/assets/85af88a7-05dd-4a29-91de-76a14cf5ef06)

<details>
  <summary>Click to see images of Web GUI</summary>
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/b36c71cf-8e06-484c-a252-934e6b1d0c2f">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/c0dab57a-d2d4-4658-bff9-3842ec90cb40">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/0a99eeac-c521-4b21-8656-e064c1adc528">
</details>

## README.md
- en [English](README.md)
- zh_CN [简体中文](readme/README_CN.md)


## 🌟 Features

- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
- 🎙️ High-quality text-to-speech with Coqui XTTS.
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports multiple languages (English by default).
- 🖥️ Designed to run on 4GB RAM.

## 🤗 [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobookXTTS)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just don't give it giant files is all
- Best to duplicate space or run locally.

## Free Google Colab [![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobookXTTS/blob/main/Notebooks/colab_ebook2audiobookxtts.ipynb)


## 🛠️ Requirements

- Python 3.10
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
   pip install coqui-tts==0.24.2 pydub nltk beautifulsoup4 ebooklib tqdm gradio==4.44.0
   
   python -m nltk.downloader punkt
   python -m nltk.downloader punkt_tab
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

Specify the language code when running the script in headless mode.
## 🚀 Usage

### 🖥️ Launching Gradio Web Interface

1. **Run the Script**:
   ```bash
   python app.py
   ```

2. **Open the Web App**: Click the URL provided in the terminal to access the web app and convert eBooks.
3. **For Public Link**: Add `--share True` to the end of it like this: `python app.py --share True`
- **[For More Parameters]**: use the `-h` parameter like this `python app.py -h`

### 📝 Basic Headless Usage

```bash
python app.py --headless True --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
```

- **<path_to_ebook_file>**: Path to your eBook file.
- **[path_to_voice_file]**: Optional for voice cloning.
- **[language_code]**: Optional to specify language.
- **[For More Parameters]**: use the `-h` parameter like this `python app.py -h`

### 🧩 Headless Custom XTTS Model Usage

```bash
python app.py --headless True --use_custom_model True --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
```

- **<ebook_file_path>**: Path to your eBook file.
- **<target_voice_file_path>**: Optional for voice cloning.
- **<language>**: Optional to specify language.
- **<custom_model_path>**: Path to `model.pth`.
- **<custom_config_path>**: Path to `config.json`.
- **<custom_vocab_path>**: Path to `vocab.json`.
- **[For More Parameters]**: use the `-h` parameter like this `python app.py -h`


### 🧩 Headless Custom XTTS Model Usage With Zip link to XTTS Fine-Tune Model 🌐

```bash
python app.py --headless True --use_custom_model True --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model_url <custom_model_URL_ZIP_path>
```

- **<ebook_file_path>**: Path to your eBook file.
- **<target_voice_file_path>**: Optional for voice cloning.
- **<language>**: Optional to specify language.
- **<custom_model_URL_ZIP_path>**: URL Path to zip of Model folder. For Example this for the [xtts_David_Attenborough_fine_tune](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/tree/main) `https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true`
- For a custom model a ref audio clip of the voice will also be needed:
[ref audio clip of David Attenborough](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/blob/main/ref.wav)
- **[For More Parameters]**: use the `-h` parameter like this `python app.py -h`

### 🔍 For Detailed Guide with list of all Parameters to use
```bash
python app.py -h
```
- This will output the following:
```bash
usage: app.py [-h] [--share SHARE] [--headless HEADLESS] [--ebook EBOOK] [--voice VOICE]
              [--language LANGUAGE] [--use_custom_model USE_CUSTOM_MODEL]
              [--custom_model CUSTOM_MODEL] [--custom_config CUSTOM_CONFIG]
              [--custom_vocab CUSTOM_VOCAB] [--custom_model_url CUSTOM_MODEL_URL]
              [--temperature TEMPERATURE] [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting ENABLE_TEXT_SPLITTING]

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
  --temperature TEMPERATURE
                        Temperature for the model. Defaults to 0.65. Higher Tempatures
                        will lead to more creative outputs IE: more Hallucinations.
                        Lower Tempatures will be more monotone outputs IE: less
                        Hallucinations.
  --length_penalty LENGTH_PENALTY
                        A length penalty applied to the autoregressive decoder. Defaults
                        to 1.0. Not applied to custom models.
  --repetition_penalty REPETITION_PENALTY
                        A penalty that prevents the autoregressive decoder from
                        repeating itself. Defaults to 2.0.
  --top_k TOP_K         Top-k sampling. Lower values mean more likely outputs and
                        increased audio generation speed. Defaults to 50.
  --top_p TOP_P         Top-p sampling. Lower values mean more likely outputs and
                        increased audio generation speed. Defaults to 0.8.
  --speed SPEED         Speed factor for the speech generation. IE: How fast the
                        Narrerator will speak. Defaults to 1.0.
  --enable_text_splitting ENABLE_TEXT_SPLITTING
                        Enable splitting text into sentences. Defaults to True.

Example: python script.py --headless --ebook path_to_ebook --voice path_to_voice
--language en --use_custom_model True --custom_model model.pth --custom_config
config.json --custom_vocab vocab.json
```


<details>
  <summary>⚠️ Legacy-Depricated Old Use Instructions</summary>
   
## 🚀 Usage

## Legacy files have been moved to `ebook2audiobookXTTS/legacy/`

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
</details>

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
docker pull athomasson2/ebook2audiobookxtts:huggingface
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
    athomasson2/ebook2audiobookxtts:huggingface \
    python app.py --headless True --ebook /home/user/app/input_folder/YOUR_INPUT_FILE.TXT
```

- And that should be it! 

- The output Audiobooks will be found in the Audiobook folder which will also be located in your local dir you ran this docker command in


## To get the help command for the other parameters this program has you can run this 

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobookxtts:huggingface \
    python app.py -h

```


and that will output this 

```bash
user/app/ebook2audiobookXTTS/input-folder -v $(pwd)/Audiobooks:/home/user/app/ebook2audiobookXTTS/Audiobooks --memory="4g" --network none --platform linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py -h
starting...
usage: app.py [-h] [--share SHARE] [--headless HEADLESS] [--ebook EBOOK] [--voice VOICE]
              [--language LANGUAGE] [--use_custom_model USE_CUSTOM_MODEL]
              [--custom_model CUSTOM_MODEL] [--custom_config CUSTOM_CONFIG]
              [--custom_vocab CUSTOM_VOCAB] [--custom_model_url CUSTOM_MODEL_URL]
              [--temperature TEMPERATURE] [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting ENABLE_TEXT_SPLITTING]

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
  --temperature TEMPERATURE
                        Temperature for the model. Defaults to 0.65. Higher Tempatures
                        will lead to more creative outputs IE: more Hallucinations.
                        Lower Tempatures will be more monotone outputs IE: less
                        Hallucinations.
  --length_penalty LENGTH_PENALTY
                        A length penalty applied to the autoregressive decoder. Defaults
                        to 1.0. Not applied to custom models.
  --repetition_penalty REPETITION_PENALTY
                        A penalty that prevents the autoregressive decoder from
                        repeating itself. Defaults to 2.0.
  --top_k TOP_K         Top-k sampling. Lower values mean more likely outputs and
                        increased audio generation speed. Defaults to 50.
  --top_p TOP_P         Top-p sampling. Lower values mean more likely outputs and
                        increased audio generation speed. Defaults to 0.8.
  --speed SPEED         Speed factor for the speech generation. IE: How fast the
                        Narrerator will speak. Defaults to 1.0.
  --enable_text_splitting ENABLE_TEXT_SPLITTING
                        Enable splitting text into sentences. Defaults to True.

Example: python script.py --headless --ebook path_to_ebook --voice path_to_voice
--language en --use_custom_model True --custom_model model.pth --custom_config
config.json --custom_vocab vocab.json
```
</details>

#### 🖥️ Docker GUI 
![demo_web_gui](https://github.com/user-attachments/assets/85af88a7-05dd-4a29-91de-76a14cf5ef06)

<details>
  <summary>Click to see images of Web GUI</summary>
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/b36c71cf-8e06-484c-a252-934e6b1d0c2f">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/c0dab57a-d2d4-4658-bff9-3842ec90cb40">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/0a99eeac-c521-4b21-8656-e064c1adc528">
</details>
### 🛠️ For Custom Xtts Models

Models built to be better at a specific voice. Check out my Hugging Face page [here](https://huggingface.co/drewThomasson).

To use a custom model, paste the link of the `Finished_model_files.zip` file like this:

[David Attenborough fine tuned Finished_model_files.zip](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true)

For a custom model a ref audio clip of the voice will also be needed:
[ref audio clip of David Attenborough](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/blob/main/ref.wav)



More details can be found at the [Dockerfile Hub Page]([https://github.com/DrewThomasson/ebook2audiobookXTTS](https://hub.docker.com/repository/docker/athomasson2/ebook2audiobookxtts/general)).

## 🌐 Fine Tuned Xtts models

To find already fine-tuned XTTS models, visit [this Hugging Face link](https://huggingface.co/drewThomasson) 🌐. Search for models that include "xtts fine tune" in their names.

## 🎥 Demos

Rainy day voice

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

David Attenborough voice

https://github.com/user-attachments/assets/47c846a7-9e51-4eb9-844a-7460402a20a8


## 🤗 [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobookXTTS)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just don't give it giant files is all
- Best to duplicate space or run locally.

## Free Google Colab [![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobookXTTS/blob/main/Notebooks/colab_ebook2audiobookxtts.ipynb)



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

## What I need help with! 🙌 
## [Full list of things can be found here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/32)
- Any help from people speaking any of the supported langues to help with proper sentence splitting methods
- Potentially creating readme Guides for Multiple languages(Becuase the only language I know is English 😔)

## 🙏 Special Thanks

- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/coqui-ai/TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)

- [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/8) 

