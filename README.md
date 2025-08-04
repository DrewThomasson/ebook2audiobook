# 📚 ebook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
using XTTSv2, Bark, Vits, Fairseq, YourTTS, Tacotron and more. Supports voice cloning and +1110 languages!
> [!IMPORTANT]
**This tool is intended for use with non-DRM, legally acquired eBooks only.** <br>
The authors are not responsible for any misuse of this software or any resulting legal consequences. <br>
Use this tool responsibly and in accordance with all applicable laws.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Thanks to support ebook2audiobook developers!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Run locally

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#launching-gradio-web-interface)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Run Remotely
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### GUI Interface
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demos

**New Default Voice Demo**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>More Demos</summary>

**ASMR Voice** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Rainy Day Voice**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett Voice**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David Attenborough Voice** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Example**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Table of Contents
- [ebook2audiobook](#-ebook2audiobook)
- [Features](#features)
- [GUI Interface](#gui-interface)
- [Demos](#demos)
- [Supported Languages](#supported-languages)
- [Minimum Requirements](#hardware-requirements)
- [Usage](#launching-gradio-web-interface)
  - [Run Locally](#launching-gradio-web-interface)
    - [Launching Gradio Web Interface](#launching-gradio-web-interface)
    - [Basic Headless Usage](#basic--usage)
    - [Headless Custom XTTS Model Usage](#example-of-custom-model-zip-upload)
    - [Help command output](#help-command-output)
  - [Run Remotely](#run-remotely)  
- [Fine Tuned TTS models](#fine-tuned-tts-models)
  - [Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
  - [Train XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Docker](#docker-gpu-options) 
  - [GPU options](#docker-gpu-options)
  - [Docker Run](#running-the-pre-built-docker-container)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
  - [Docker headless guide](#docker-headless-guide)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
- [Supported eBook Formats](#supported-ebook-formats)
- [Output Formats](#output-formats)
- [Updating to Latest Version](#updating-to-latest-version)
- [Revert to older Version](#reverting-to-older-versions)
- [Common Issues](#common-issues)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


## Features
- 📚 Splits eBook into chapters for organized audio.
- 🎙️ High-quality text-to-speech with [Coqui XTTSv2](https://huggingface.co/coqui/XTTS-v2) and [Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) (and more).
- 🗣️ Optional voice cloning with your own voice file.
- 🎭 **NEW:** Multi-character voice support with automatic voice assignment based on character metadata.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 🖥️ Designed to run on 4GB RAM.


## Supported Languages
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1100 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


##  Hardware Requirements
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
- CPU (intel, AMD, ARM), GPU (Nvidia, AMD*, Intel*) (Recommended), MPS (Apple Silicon CPU)
*available very soon

> [!IMPORTANT]
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
**Lacking of any standards structure like what is a chapter, paragraph, preface etc.<br>
you should first remove manually any text you don't want to be converted in audio.**

### Installation Instructions
1. **Clone repo**
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
```

### Launching Gradio Web Interface  
1. **Run ebook2audiobook**:  
   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.sh  # Run launch script
     ```

   - **Mac Launcher**  
     Double click `Mac Ebook2Audiobook Launcher.command`

  
   - **Windows**  
     ```bash
     ebook2audiobook.cmd  # Run launch script or double click on it
     ```
     
   - **Windows Launcher**  
     Double click `ebook2audiobook.cmd`


   - **Manual Python Install**
     ```bash
     # (for experts only!)
     REQUIRED_PROGRAMS=("calibre" "ffmpeg" "nodejs" "mecab" "espeak-ng" "rust" "sox")
     REQUIRED_PYTHON_VERSION="3.12"
     pip install -r requirements.txt  # Install Python Requirements
     python app.py  # Run Ebook2Audiobook
     ```
   
1. **Open the Web App**: Click the URL provided in the terminal to access the web app and convert eBooks. `http://localhost:7860/`
2. **For Public Link**:
   `python app.py --share` (all OS)
   `./ebook2audiobook.sh --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)

> [!IMPORTANT]
**If the script is stopped and run again, you need to refresh your gradio GUI interface<br>
to let the web page reconnect to the new connection socket.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
         --voice [path_to_voice_file] --language [language_code]
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
         --voice [path_to_voice_file] --language [language_code]
     ```
     
  - **[--ebook]**: Path to your eBook file
  - **[--voice]**: Voice cloning file path (optional)
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
    Default language is eng and --language is optional for default language set in ./lib/lang.py.<br>
    The ISO-639-1 2 letters codes are also supported.

### Multi-Character Voice Usage 🎭
Convert pre-tagged scripts with automatic character voice assignment:
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.sh --headless --script <path_to_script_file> \
         --characters <path_to_characters_json> --language [language_code]
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --script <path_to_script_file> \
         --characters <path_to_characters_json> --language [language_code]
     ```
     
  - **[--script]**: Path to pre-tagged text script with `<CharacterName>: dialogue` format
  - **[--characters]**: Path to character JSON file with voice metadata
  - **[--voice]**: Default voice for narrator and fallback (optional)

**Example script format:**
```text
This is narrator text.

<Alice>: Hello everyone! I'm excited to be here.

<Bob>: Nice to meet you, Alice. Welcome to our story.
```

**Example characters.json:**
```json
[
  {
    "normalized_name": "Alice",
    "inferred_gender": "female", 
    "inferred_age_category": "adult",
    "language": "eng",
    "voice": null
  },
  {
    "normalized_name": "Bob",
    "inferred_gender": "male", 
    "inferred_age_category": "adult", 
    "language": "eng",
    "voice": "CustomMaleVoice"
  }
]
```

📖 **[Complete Multi-Character Guide](MULTI_CHARACTER_GUIDE.md)** | 📁 **[Example Files](examples/)**


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTSv2: config.json, model.pth, vocab.json and ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
     ```
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
      (see ./lib/models.py).


### For Detailed Guide with list of all Parameters to use
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.sh --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Or for all OS**
    ```python
     app.py --help
    ```

<a id="help-command-output"></a>
```bash
usage: app.py [-h] [--session SESSION] [--share] [--headless] [--ebook EBOOK]
              [--ebooks_dir EBOOKS_DIR] [--language LANGUAGE] [--voice VOICE]
              [--device {cpu,gpu,mps}]
              [--tts_engine {XTTSv2,BARK,VITS,FAIRSEQ,TACOTRON2,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}]
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
              [--length_penalty LENGTH_PENALTY] [--num_beams NUM_BEAMS]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K]
              [--top_p TOP_P] [--speed SPEED] [--enable_text_splitting]
              [--text_temp TEXT_TEMP] [--waveform_temp WAVEFORM_TEMP]
              [--output_dir OUTPUT_DIR] [--version]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

**** The following options are for all modes:
  Optional

**** The following option are for gradio/gui mode only:
  Optional

  --share               Enable a public shareable Gradio link.

**** The following options are for --headless mode only:
  --headless            Run the script in headless mode
  --ebook EBOOK         Path to the ebook file for conversion. Cannot be used when --ebooks_dir is present.
  --ebooks_dir EBOOKS_DIR
                        Relative or absolute path of the directory containing the files to convert. 
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
                            in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py

optional parameters:
  --voice VOICE         (Optional) Path to the voice cloning file for TTS engine. 
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
                        (Optional) Pprocessor unit type for the conversion. 
                            Default is set in ./lib/conf.py if not present. Fall back to CPU if GPU not available.
  --tts_engine {XTTSv2,BARK,VITS,FAIRSEQ,TACOTRON2,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}
                        (Optional) Preferred TTS engine (available are: ['XTTSv2', 'BARK', 'VITS', 'FAIRSEQ', 'TACOTRON2', 'YOURTTS', 'xtts', 'bark', 'vits', 'fairseq', 'tacotron', 'yourtts'].
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
                        (Optional) Path to the custom model zip file cntaining mandatory model files. 
                            Please refer to ./lib/models.py
  --fine_tuned FINE_TUNED
                        (Optional) Fine tuned model path. Default is builtin model.
  --output_format OUTPUT_FORMAT
                        (Optional) Output audio format. Default is set in ./lib/conf.py
  --temperature TEMPERATURE
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
  --length_penalty LENGTH_PENALTY
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
  --num_beams NUM_BEAMS
                        (xtts only, optional) Controls how many alternative sequences the model explores. Must be equal or greater than length penalty. 
                            Default to config.json model.
  --repetition_penalty REPETITION_PENALTY
                        (xtts only, optional) A penalty that prevents the autoregressive decoder from repeating itself. 
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
                            Lower values mean more likely outputs and increased audio generation speed. 
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
                            Lower values mean more likely outputs and increased audio generation speed. Default to config.json model.
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
  --enable_text_splitting
                        (xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient. 
                            Default to config.json model.
  --text_temp TEXT_TEMP
                        (bark only, optional) Text Temperature for the model. 
                            Default to 0.85. Higher temperatures lead to more creative outputs.
  --waveform_temp WAVEFORM_TEMP
                        (bark only, optional) Waveform Temperature for the model. 
                            Default to 0.5. Higher temperatures lead to more creative outputs.
  --output_dir OUTPUT_DIR
                        (Optional) Path to the output directory. Default is set in ./lib/conf.py
  --version             Show the version of the script and exit

Example usage:    
Windows:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
Linux/Mac:
    Gradio/GUI:
    ./ebook2audiobook.sh
    Headless mode:
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
    
Tip: to add of silence (1.4 seconds) into your text just use "###" or "[pause]".

```

NOTE: in gradio/gui mode, to cancel a running conversion, just click on the [X] from the ebook upload component.

TIP: if it needs some more pauses, just add '###' or '[pause]' between the words you wish more pause. one [pause] equals to 1.4 seconds

#### Docker GPU Options

Available pre-build tags: `latest` (CUDA 11.8)
#### Edit: IF GPU isn't detected then you'll have to build the image -> [Building the Docker Container](#building-the-docker-container)



#### Running the pre-built Docker Container

 -Run with CPU only
```powershell
docker run --pull always --rm -p 7860:7860 athomasson2/ebook2audiobook
```
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
docker run --pull always --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

This command will start the Gradio interface on port 7860.(localhost:7860)
- For more options add the parameter `--help`


#### Building the Docker Container
- You can build the docker image with the command:
```powershell
docker build -t athomasson2/ebook2audiobook .
```
#### Avalible Docker Build Arguments

`--build-arg TORCH_VERSION=cuda118` Available tags: [cuda121, cuda118, cuda128, rocm, xpu, cpu] 

All CUDA version numbers should work, Ex: CUDA 11.6-> cuda116

`--build-arg SKIP_XTTS_TEST=true` (Saves space by not baking XTTSv2 model into docker image)


## Docker container file locations
All ebook2audiobooks will have the base dir of `/app/`
For example:
`tmp` = `/app/tmp`
`audiobooks` = `/app/audiobooks`


## Docker headless guide

- Before you do run this you need to create a dir named "input-folder" in your current dir
  which will be linked, This is where you can put your input files for the docker image to see
```bash
mkdir input-folder && mkdir Audiobooks
```
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
```bash
docker run --pull always --rm \
    -v $(pwd)/input-folder:/app/input_folder \
    -v $(pwd)/audiobooks:/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```
- The output Audiobooks will be found in the Audiobook folder which will also be located
  in your local dir you ran this docker command in


## To get the help command for the other parameters this program has you can run this 

```bash
docker run --pull always --rm athomasson2/ebook2audiobook --help

```
That will output this 
[Help command output](#help-command-output)


### Docker Compose
This project uses Docker Compose to run locally. You can enable or disable GPU support 
by setting either `*gpu-enabled` or `*gpu-disabled` in `docker-compose.yml`


#### Steps to Run
1. **Clone the Repository** (if you haven't already):
   ```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
   ```
2. **Set GPU Support (disabled by default)**
  To enable GPU support, modify `docker-compose.yml` and change `*gpu-disabled` to `*gpu-enabled`
3. **Start the service:**
    ```bash
    # Docker
    docker-compose up -d # To update add --build

    # Podman
    podman compose -f podman-compose.yml up -d # To update add --build
    ```
4. **Access the service:**
  The service will be available at http://localhost:7860.


## Common Docker Issues

- My NVIDIA GPU isnt being detected?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

- `python: can't open file '/home/user/app/app.py': [Errno 2] No such file or directory` (Just remove all post arguments as I replaced the `CMD` with `ENTRYPOINT` in the [Dockerfile](Dockerfile))
  - Example: `docker run --pull always athomasson2/ebook2audiobook app.py --script_mode full_docker` - > corrected - > `docker run --pull always athomasson2/ebook2audiobook`
  - Arguments can be easily added like this now `docker run --pull always athomasson2/ebook2audiobook --share`

- Docker gets stuck downloading Fine-Tuned models.
  (This does not happen for every computer but some appear to run into this issue)
  Disabling the progress bar appears to fix the issue,
  as discussed [here in #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)
  Example of adding this fix in the `docker run` command
```Dockerfile
docker run --pull always --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```


## Fine Tuned TTS models
#### Fine Tune your own XTTSv2 model

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)





#### De-noise training data

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Fine Tuned TTS Collection

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

For an XTTSv2 custom model a ref audio clip of the voice reference is mandatory:


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


## Output Formats
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.

## Updating to Latest Version
```bash
git pull # Locally/Compose

docker pull athomasson2/ebook2audiobook:latest # For Pre-build docker images
```

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7

athomasson2/ebook2audiobook:VERSION_NUM # For Pre-build docker images -> Example: athomasson2/ebook2audiobook:v25.7.7
```

## Common Issues:
- My NVIDIA GPU isnt being detected?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU is slow (better on server smp CPU) while NVIDIA GPU can have almost real time conversion.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   For faster multilingual generation I would suggest my other
   [project that uses piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) instead
   (It doesn't have zero-shot voice cloning though, and is Siri quality voices, but it is much faster on cpu).
- "I'm having dependency issues" - Just use the docker, its fully self contained and has a headless mode,
   add `--help` parameter at the end of the docker run command for more information.
- "Im getting a truncated audio issue!" - PLEASE MAKE AN ISSUE OF THIS,
   we don't speak every language and need advise from users to fine tune the sentence splitting logic.😊


## What we need help with! 🙌 
## [Full list of things can be found here](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- Any help from people speaking any of the supported languages to help us improve the models

## Do you need to rent a GPU to boost service from us?
- A poll is open here https://github.com/DrewThomasson/ebook2audiobook/discussions/889

## Special Thanks
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
