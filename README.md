# 📚 ebook2audiobook
CPU/GPU Converter from E-Book to audiobook with chapters and metadata<br/>
using XTTSv2, Piper-TTS, Vits, Fairseq, Tacotron2, YourTTS and much more.<br/>
Supports voice cloning and 1158 languages!
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
  - [Run Locally](#instructions)
    - [Launching Gradio Web Interface](#instructions)
    - [Basic Headless Usage](#basic--usage)
    - [Headless Custom XTTS Model Usage](#example-of-custom-model-zip-upload)
    - [Help command output](#help-command-output)
  - [Run Remotely](#run-remotely)
  - [Docker](#docker)
    - [Steps to Run](#docker)
    - [Common Docker Issues](#common-docker-issues)
  
- [Fine Tuned TTS models](#fine-tuned-tts-models)
  - [Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
  - [Train XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Supported eBook Formats](#supported-ebook-formats)
- [Output Formats](#output-and-process-formats)
- [Updating to Latest Version](#updating-to-latest-version)
- [Revert to older Version](#reverting-to-older-versions)
- [Common Issues](#common-issues)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


## Features
- 📚 **Convert multiple file formats**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`
- 🔍 **OCR scanning** for files with text pages as images
- 🔊 **High-quality text-to-speech** from near realtime to near real voice
- 🗣️ **Optional voice cloning** using your own voice file
- 🌐 **Supports 1158 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Low-resource friendly** — runs on **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Audiobook output formats**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML tags supported** — fine-grained control of breaks, pauses, voice switching and more ([see below](#sml-tags-available))
- 🧩 **Optional custom model** using your own trained model (XTTSv2 only, other on request)
- 🎛️ **Fine-tuned preset models** trained by the E2A Team<br/>
     <i>(Contact us if you need additional fine-tuned models, or if you’d like to share yours to the official preset list)</i>


##  Hardware Requirements
- 2GB RAM min, 8GB recommended.
- 1GB VRAM min, 4GB recommended.
- Virtualization enabled if running on windows (Docker only).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon CPU)

*<i> Modern TTS engines are very slow on CPU, so use lower quality TTS like YourTTS, Tacotron2 etc..</i>

## Supported Languages
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection

## Output and process Formats
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Process format can be changed in lib/conf.py

## SML tags available
- `[break]` — silence (random range **0.3–0.6 sec.**)
- `[pause]` — silence (random range **1.0–1.6 sec.**)
- `[pause:N]` — fixed pause (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — switch voice from default or selected voice from GUI/CLI

> [!IMPORTANT]
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**

>[!NOTE]
**EPUB format lacks any standard structure like what is a chapter, paragraph, preface etc.<br>
So you should first remove manually any text you don't want to be converted in audio.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Install / Run ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command  # Run launch script
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac Launcher**  
     Double click `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Note for Windows users: scoop is installed to install missing programs without administrator privileges.</i>
   
1. **Open the Web App**: Click the URL provided in the terminal to access the web app and convert eBooks. `http://localhost:7860/`
2. **For Public Link**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**If the script is stopped and run again, you need to refresh your gradio GUI interface<br>
to let the web page reconnect to the new connection socket.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
     ```
     
  - **[--ebook]**: Path to your eBook file
  - **[--voice]**: Voice cloning file path (optional)
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
    Default language is eng and --language is optional for default language set in ./lib/lang.py.<br>
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTSv2: config.json, model.pth, vocab.json and ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Note: the ref.wav of your custom model is always the voice selected for the conversion</i>
     
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
      (see ./lib/models.py).

### For Detailed Guide with list of all Parameters to use
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
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
usage: app.py [-h] [--session SESSION] [--share] [--headless] [--ebook EBOOK] [--ebooks_dir EBOOKS_DIR]
              [--language LANGUAGE] [--voice VOICE] [--device {CPU,CUDA,MPS,ROCM,XPU,JETSON}]
              [--tts_engine {XTTSv2,BARK,VITS,FAIRSEQ,TACOTRON2,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}]
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED] [--output_format OUTPUT_FORMAT]
              [--output_channel OUTPUT_CHANNEL] [--temperature TEMPERATURE] [--length_penalty LENGTH_PENALTY]
              [--num_beams NUM_BEAMS] [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--text_temp TEXT_TEMP] [--waveform_temp WAVEFORM_TEMP]
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
  --device {CPU,CUDA,MPS,ROCM,XPU,JETSON}
                        (Optional) Processor unit type for the conversion.
                            Default is set in ./lib/conf.py if not present. Fall back to CPU if CUDA or MPS is not available.
  --tts_engine {XTTSv2,BARK,VITS,FAIRSEQ,TACOTRON2,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}
                        (Optional) Preferred TTS engine (available are: ['XTTSv2', 'BARK', 'VITS', 'FAIRSEQ', 'TACOTRON2', 'YOURTTS', 'xtts', 'bark', 'vits', 'fairseq', 'tacotron', 'yourtts'].
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
                        (Optional) Path to the custom model zip file cntaining mandatory model files.
                            Please refer to ./lib/models.py
  --fine_tuned FINE_TUNED
                        (Optional) Fine tuned model path. Default is builtin model.
  --output_format OUTPUT_FORMAT
                        (Optional) Output audio format. Default is m4b set in ./lib/conf.py
  --output_channel OUTPUT_CHANNEL
                        (Optional) Output audio channel. Default is mono set in ./lib/conf.py
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
                            Default to config.json model.
  --waveform_temp WAVEFORM_TEMP
                        (bark only, optional) Waveform Temperature for the model.
                            Default to config.json model.
  --output_dir OUTPUT_DIR
                        (Optional) Path to the output directory. Default is set in ./lib/conf.py
  --version             Show the version of the script and exit

Example usage:
Windows:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file' --language eng
Linux/Mac:
    Gradio/GUI:
    ./ebook2audiobook.command
    Headless mode:
    ./ebook2audiobook.command --headless --ebook '/path/to/file' --language eng

Docker build image:
    Windows:
    ebook2audiobook.cmd --script_mode build_docker
    Linux/Mac
    ./ebook2audiobook.command --script_mode build_docker
Docker run image:
    Gradio/GUI:
        CPU:
        docker run --rm -it -p 7860:7860 ebook2audiobook:cpu
        CUDA:
        docker run --gpus all --rm -it -p 7860:7860 ebook2audiobook:cu[118/121/128 etc..]
        ROCM:
        docker run --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:rocm[5.5/6.1/6.4 etc..]
        XPU:
        docker run --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:xpu
        JETSON:
        docker run --runtime nvidia  --rm -it -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc...]
    Headless mode:
        CPU:
        docker run --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:cpu --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
        docker run --gpus all --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:cu[118/121/128 etc..] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
        docker run --device=/dev/kfd --device=/dev/dri --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:rocm[5.5/6.1/6.4 etc..] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
        docker run --device=/dev/dri --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:xpu --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
        docker run --runtime nvidia --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc...] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]

Docker Compose (i.e. cuda 12.8:
        Build
            DEVICE_TAG=cu128 docker compose --progress plain --profile gpu up -d --build
        Run Gradio GUI:
            DEVICE_TAG=cu128 docker compose --profile gpu up -d
        Run Headless mode:
            DEVICE_TAG=cu128 docker compose --profile gpu run --rm ebook2audiobook --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]

Podman Compose (i.e. cuda 12.8:
        Build
            DEVICE_TAG=cu128 podman-compose -f podman-compose.yml up -d --build
        Run Gradio GUI:
            DEVICE_TAG=cu128 podman-compose -f podman-compose.yml up -d
        Run Headless mode:
            DEVICE_TAG=cu128 podman-compose -f podman-compose.yml run --rm ebook2audiobook --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]

    * MPS is not exposed in docker so CPU must be used.

SML tags available:
        [break]` — silence (random range **0.3–0.6 sec.**)
        [pause]` — silence (random range **1.0–1.6 sec.**)
        [pause:N]` — fixed pause (**N sec.**)
        [voice:/path/to/voice/file]...[/voice]` — switch voice from default or selected voice from GUI/CLI
```

NOTE: in gradio/gui mode, to cancel a running conversion, just click on the [X] from the ebook upload component.
TIP: if it needs some more pause, add '[pause:3]' for 3 sec. etc.

### Docker
1. **Clone the Repository**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Build the container**
```bash
   # Windows
   ebook2audiobook.cmd --script_mode build_docker

   # Linux/MacOS
   ./ebook2audiobook.command --script_mode build_docker 
```
4. **Run the Container:**
```bash
	# Gradio/GUI:

	# CPU:
		docker run --rm -it -p 7860:7860 ebook2audiobook:cpu
	# CUDA:
		docker run --gpus all --rm -it -p 7860:7860 ebook2audiobook:cu[118/121/128 etc..]
	# ROCM:
		docker run --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:rocm[5.5/6.1/6.4 etc..]
	# XPU:
		docker run --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:xpu
	# JETSON:
		docker run --runtime nvidia  --rm -it -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc...]
	
	# Headless mode examples:
	
	# CPU:
		docker run --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:cpu --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
	# CUDA:
		docker run --gpus all --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:cu[118/121/128 etc..] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
	# ROCM:
		docker run --device=/dev/kfd --device=/dev/dri --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:rocm[5.5/6.1/6.4 etc..] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
	# XPU:
		docker run --device=/dev/dri --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:xpu --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
	# JETSON:
		docker run --runtime nvidia --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc...] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]

    # Docker Compose (example for cuda 12.9)
    docker-compose up -d
    DEVICE_TAG=cu128 docker compose up -d
    # To stop -> docker-compose down

    # Podman Compose (example for cuda 12.8)
    podman compose -f podman-compose.yml up
    DEVICE_TAG=cu128 podman-compose up -d
    # To stop -> podman compose -f podman-compose.yml down
```
- NOTE: MPS is not exposed in docker so CPU must be used
  
### Common Docker Issues
- My NVIDIA GPU isn't being detected?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Fine Tuned TTS models
#### Fine Tune your own XTTSv2 model

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### De-noise training data

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Fine Tuned TTS Collection

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

For an XTTSv2 custom model a ref audio clip of the voice reference is mandatory:

## Your own Ebook2Audiobook customization
You are free to modify libs/conf.py to add or remove the settings you wish. If you plan to do it just make
a copy of the original conf.py so on each ebook2audiobook update you will backup your modified conf.py and put
back the original one. You must plan the same process for models.py. If you wish to make your own custom model
as an official ebook2audiobook fine tuned model so please contact us and we'll add it to the presets list.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Common Issues:
- My NVIDIA/ROCm/XPU/MPS GPU isn't being detected?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU is slow (better on server smp CPU) while GPU can have almost real time conversion.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   For faster multilingual generation I would suggest my other
   [project that uses piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) instead
   (It doesn't have zero-shot voice cloning though, and is Siri quality voices, but it is much faster on cpu).
- "I'm having dependency issues" - Just use the docker, its fully self contained and has a headless mode,
   add `--help` parameter at the end of the docker run command for more information.
- "Im getting a truncated audio issue!" - PLEASE MAKE AN ISSUE OF THIS,
   we don't speak every language and need advise from users to fine tune the sentence splitting logic.😊


## What we need help with! 🙌 
## [Roadmap and Full list of things can be found here](https://github.com/DrewThomasson/ebook2audiobook/issues/32)
- Any help from people speaking any of the supported languages to help us improve the models
  
<!--
## Do you need to rent a GPU to boost service from us?
- A poll is open here https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Special Thanks
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
