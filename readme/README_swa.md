# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Kibadilishaji cha CPU/GPU kutoka E-Kitabu hadi kitabu cha sauti chenye sura na metadata<br/>
kwa kutumia injini za hali ya juu za TTS na mengi zaidi.<br/>
Inasaidia kupiga picha za sauti na lugha 1696!
> [!IMPORTANT]
**Zana hii imekusudiwa kutumika tu na vitabu pepe visivyo na DRM, vilivyopatikana kihalali.** <br>
Waandishi hawawajibikii matumizi mabaya yoyote ya programu hii au matokeo yoyote ya kisheria yanayotokana nayo. <br>
Tumia zana hii kwa uwajibikaji na kwa kufuata sheria zote zinazotumika.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Asante kwa kuwaunga mkono wasanidi wa ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Endesha kwa ndani

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Endesha kwa Mbali
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Kiolesura cha GUI
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Bofya ili kuona picha za GUI ya Wavuti</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Onyesho

**Onyesho la Sauti Mpya ya Chaguo-msingi**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Maonyesho Zaidi</summary>

**Sauti ya ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Sauti ya Siku ya Mvua**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Sauti ya Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Sauti ya David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Mfano**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Jedwali la Yaliyomo
- [ebook2audiobook](#-ebook2audiobook)
- [Features](#features)
- [GUI Interface](#gui-interface)
- [Demos](#demos)
- [Supported Languages](#supported-languages)
- [Minimum Requirements](#hardware-requirements)
- [Usage](#instructions)
  - [Run Locally](#instructions)
    - [Launching Gradio Web Interface](#instructions)
    - [Basic Headless Usage](#basic-usage)
    - [Headless Custom XTTS Model Usage](#example-of-custom-model-zip-upload)
    - [Help command output](#help-command-output)
  - [Run Remotely](#run-remotely)
  - [Docker](#docker)
    - [Steps to Run](#docker)
- [Tools](#tools)
  - [Preload models for offline installs](#preload-models)
  - [Translate ebooks out of e2a](#translate-ebooks)

- [Cloned Voices](#cloned-voices)
- [Fine Tuned TTS models](#fine-tuned-tts-models)
  - [Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
  - [Train TTS Model](#fine-tune-your-own-tts-model)
- [Supported eBook Formats](#supported-ebook-formats)
- [Output Formats](#output-and-process-formats)
- [Revert to older Version](#reverting-to-older-versions)
- [Common Issues](#common-issues)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


## Vipengele
- 🔧 ** Injini za TTS zinatumika **: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Badilisha miundo mingi ya faili**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Eneo la Maandishi** ili kubadilisha moja kwa moja maandishi mafupi kuwa sauti
- 🔍 **Uchanganuzi wa OCR** kwa faili zenye kurasa za maandishi kama picha
- 🔊 **Maandishi-kwa-usemi ya ubora wa juu**, kutoka karibu wakati halisi hadi sauti karibu halisi
- 🗣️ **Unakili wa sauti wa hiari** kwa kutumia faili yako mwenyewe ya sauti
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Rafiki kwa rasilimali ndogo** — inaendeshwa kwa **2 GB RAM / 1 GB VRAM (kima cha chini)**
- 🎵 **Miundo ya matokeo ya kitabu cha sauti**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Lebo za SML zinaungwa mkono** — udhibiti wa kina wa mapumziko, vituo, ubadilishaji wa sauti na zaidi ([see below](#sml-tags-available))
- 🧩 **Modeli maalum ya hiari** kwa kutumia modeli yako uliyofunza mwenyewe (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modeli za mipangilio iliyowekwa awali zilizoboreshwa** zilizofunzwa na Timu ya E2A<br/>
     <i>(Wasiliana nasi ikiwa unahitaji modeli za ziada zilizoboreshwa, au ikiwa ungependa kushiriki zako kwenye orodha rasmi ya mipangilio iliyowekwa awali)</i>


##  Mahitaji ya Maunzi
- RAM 2GB chini, 8GB inapendekezwa.
- VRAM 1GB chini, 4GB inapendekezwa.
- Uboreshaji umewezeshwa ikiwa unaendeshwa kwenye windows (Docker pekee).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, Rocm, JETSON
- MPS (CPU ya Apple Silicon)

*<i> Injini za kisasa za TTS ni polepole sana kwenye CPU, kwa hivyo tumia TTS za ubora wa chini kama YourTTS, Tacotron2 n.k.</i>

## Lugha Zinazoungwa Mkono
| **Kiarabu (ar)**    | **Kichina (zh)**    | **Kiingereza (sw)**   | **Kihispania (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **Kifaransa (fr)**    | **Kijerumani (de)**     | **Kiitaliano (it)**   | **Kireno (pt)** |
| **Kipolishi (pl)**    | **Kituruki (tr)**    | **Kirusi (ru)**   | **Kiholanzi (nl)**     |
| **Cheki (cs)**     | **Kijapani (ja)**   | **Kihindi (hi)**     | **Kibengali (bn)**   |
| **Hungarian (hu)** | **Kikorea (ko)**     | **Kivietinamu (vi)**| **Kiswidi (sv)**   |
| **Kiajemi (fa)**   | **Yoruba (yo)**     | **Kiswahili (sw)**   | **Kiindonesia (id)**|
| **Kislovakia (sk)**    | **Kikroeshia (hr)**   | **Kitamil (ta)**     | **Kidenmaki (da)**    |
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Miundo ya eBook Inayoungwa Mkono
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Matokeo bora**: `.epub` au `.mobi` kwa utambuzi wa sura kiotomatiki

## Miundo ya Matokeo na uchakataji
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Muundo wa uchakataji unaweza kubadilishwa katika lib/conf.py

## Lebo za SML zinazopatikana
- `[break]` — ukimya (anuwai nasibu **0.3–0.6 sec.**)
- `[pause]` — ukimya (anuwai nasibu **1.0–1.6 sec.**)
- `[pause:N]` — pumziko maalum (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — badilisha sauti kutoka kwa sauti ya chaguo-msingi au iliyochaguliwa kutoka GUI/CLI
- `[emotion:sadness]...[/emotion]` — Kanda pekee: hisia kwa ajili ya kifungu (furaha, huzuni, chukizo, hofu, mshangao, hasira, nyingine, kutokuwamo) au mchanganyiko kama `[emotion:sadness=0.7,neutral=0.3]`; injini nyingine hupuuza

**Angalia repo yetu nyingine iliyojikita katika kuongeza SML kiotomatiki katika eBook yako -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Kabla ya kutuma tatizo la usakinishaji au hitilafu, tafuta kwa makini katika KICHUPO cha matatizo yaliyofunguliwa na yaliyofungwa<br>
ili kuhakikisha tatizo lako halipo tayari.**

Kidokezo
**Muundo wa EPUB hauna muundo wowote wa kawaida kama vile sura ni nini, aya, dibaji n.k.<br>
Kwa hivyo unapaswa kwanza kuondoa kwa mkono maandishi yoyote ambayo hutaki kubadilishwa kuwa sauti.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Sakinisha / Endesha ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Kizinduzi cha Mac**  
     Bofya mara mbili `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Kumbuka kwa watumiaji wa Windows: scoop husakinishwa ili kusakinisha programu zinazokosekana bila ruhusa za msimamizi.</i>
   
1. **Fungua Programu ya Wavuti**: Bofya URL iliyotolewa kwenye terminal ili kufikia programu ya wavuti na kubadilisha eBooks. `http://localhost:7860/`
2. **Kwa Kiungo cha Umma**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (OS zote)

> [!IMPORTANT]
**Ikiwa hati itasimamishwa na kuendeshwa tena, unahitaji kuonyesha upya kiolesura chako cha GUI cha gradio<br>
ili kuruhusu ukurasa wa wavuti uunganishe upya kwa soketi mpya ya muunganisho.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Njia ya faili yako ya eBook
  - **[--voice]**: Njia ya faili ya unakili wa sauti (hiari)
  - **[--language]**: Msimbo wa lugha katika ISO-639-3 (yaani: ita kwa Kiitaliano, eng kwa Kiingereza, deu kwa Kijerumani...).<br>
    Lugha ya chaguo-msingi ni eng na --language ni hiari kwa lugha ya chaguo-msingi iliyowekwa katika ./lib/lang.py.<br>
    Misimbo ya herufi 2 ya ISO-639-1 pia inaungwa mkono.


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
     
- **<custom_model_path>**: Njia ya faili ya `model_name.zip`,
      ambayo lazima iwe na (kulingana na injini ya tts) faili zote za lazima<br>
      (angalia ./lib/models.py).

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
              [--language LANGUAGE] [--voice VOICE] [--voice_map VOICE_MAP] [--device {CPU,CUDA,MPS,ROCM,XPU,JETSON}]
              [--tts_engine {XTTS,BARK,VITS,FAIRSEQ,TACOTRON,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}]
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

**** The following option is for gradio/gui mode only:
  --share               (Optional) Enable a public shareable Gradio link.

**** The following options are for --headless mode only:
  --headless            Run the script in headless mode
  --ebook EBOOK         Path to the ebook file for conversion. Cannot be used when --ebooks_dir is present.
  --ebooks_dir EBOOKS_DIR
                        Relative or absolute path of the directory containing the files to convert.
                            Cannot be used when --ebook is present.
  --text TEXT           Raw text for conversion. Cannot be used when --ebook or --ebooks_dir is present.
  --language LANGUAGE   Language of the e-book. Default language is set
                            in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py

optional parameters:
  --translate ISO3      (Optional) Translate ebook to a target language (ISO 639-3 code, e.g. eng, fra, deu) before TTS synthesis.
                            Uses argostranslate. The target language becomes the effective TTS language for the run.
                            A copy of the source ebook is made with the _<iso3> suffix so translated and non-translated
                            outputs stay isolated (independent process folder, audio chunks, and final file).
  --voice VOICE         (Optional) Path to the voice cloning file for TTS engine.
                            Uses the default voice if not present.
  --voice_map VOICE_MAP
                        (Optional, --ebooks_dir only) Path to a JSON file mapping ebook path -> voice path.
                            Each entry overrides --voice for that specific ebook. Missing/null entries fall back to --voice.
                            Keys may be absolute paths or basenames. Example:
                            {"book1.epub": "/voices/eng/adult/female/alice.wav", "/abs/path/book2.epub": null}
  --device {CPU,CUDA,MPS,ROCM,XPU,JETSON}
                        (Optional) Processor unit type for the conversion.
                            Default is set in ./lib/conf.py if not present. Fall back to CPU if CUDA or MPS is not available.
  --tts_engine {XTTS,BARK,VITS,FAIRSEQ,TACOTRON,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}
                        (Optional) Preferred TTS engine (available are: ['XTTS', 'BARK', 'VITS', 'FAIRSEQ', 'TACOTRON', 'YOURTTS', 'xtts', 'bark', 'vits', 'fairseq', 'tacotron', 'yourtts'].
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
  --abs_url ABS_URL     Audiobookshelf server URL (e.g. http://localhost:13378).
  --abs_api_token ABS_API_TOKEN
                        Audiobookshelf API token.
  --abs_library ABS_LIBRARY
                        Audiobookshelf library ID.
  --enable_interlude    Add MusicGen music before the first chapter, between chapters, and at the end of the audiobook. Settings are in ./lib/conf_interlude.py
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

SML tags available:
	[break] — silence (random range **0.3–0.6 sec.**)
	[pause] — silence (random range **1.0–1.6 sec.**)
	[pause:N] — fixed pause (**N sec.**)
	[voice:/path/to/voice/file]...[/voice] — switch voice from default or selected voice from GUI/CLI
	[emotion:sadness]...[/emotion] — Zonos only: emotion for a passage (happiness, sadness, disgust, fear, surprise, anger, other, neutral) or a mix like [emotion:sadness=0.7,neutral=0.3]; other engines ignore it

```

KUMBUKA: katika hali ya gradio/gui, ili kughairi ubadilishaji unaoendelea, bonyeza tu [X] kutoka kwa kipengele cha upakiaji wa eBook.
KIDOKEZO: ikiwa inahitaji pumziko zaidi, ongeza '[pause:3]' kwa sekunde 3 n.k.

### Docker
1. **Clone the Repository**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Build the container**
```bash
    Windows:
        Docker:
            ebook2audiobook.cmd --script_mode build_docker
        Docker Compose:
            ebook2audiobook.cmd --script_mode build_docker --docker_mode compose
        Podman Compose:
            ebook2audiobook.cmd --script_mode build_docker --docker_mode podman
    Linux/Mac
        Docker:
            ./ebook2audiobook.command --script_mode build_docker
        Docker Compose
            ./ebook2audiobook.command --script_mode build_docker --docker_mode compose
        Podman Compose:
            ./ebook2audiobook.command --script_mode build_docker --docker_mode podman
```
4. **Run the Container:**
```bash
Docker run image:
    Gradio/GUI:
        CPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc...]
    Headless mode:
        CPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
Docker Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 docker compose --profile cuda up --no-log-prefix
        Run Headless mode:
               DEVICE_TAG=cu128 docker compose --profile cuda run --rm ebook2audiobook-cuda --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
Podman Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile cuda up
        Run Headless mode:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile cuda run --rm ebook2audiobook-cuda --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
```
- NOTE: MPS is not exposed in docker so CPU must be used
- NOTE: the named volume `e2a_venvs` keeps the TTS engines installed in their own venv (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM etc.)
  across container runs, so they are not reinstalled each time. To reset them: `docker volume rm e2a_venvs`

## Zana
Zana za kujitegemea, zinaendeshwa na Python ya e2a (`python_env`, iliyoundwa na uzinduzi wa kwanza wa e2a).

<a id="preload-models"></a>
### Preload models for offline installs: `tools/preload_models.py`
Downloads every model e2a uses (TTS engines and their fine-tunes, voice conversion, stanza, pyannote, demucs,
music interludes, argos-translate packages, tesseract data, jieba, and the voices) into one folder laid out
exactly like `./models`, i.e. a USB key. On the offline machine, copy that folder into e2a's `./models`
and the `voices` folder written beside it into e2a's `./voices`.
Every finished job is recorded in `<models_dir>/.e2a_downloads.json`: a rerun skips what is done and starts
again what was cut (ctrl-c, crash, unplugged key) after removing its partial files.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` lists the jobs and their state (done, interrupted, todo) without downloading anything.

```bash
usage: preload_models.py [-h] [--only ONLY] [--skip SKIP] [--languages LANGUAGES]
                         [--audiocpp_packages AUDIOCPP_PACKAGES] [--refresh] [--dry_run]
                         models_dir

Download every model e2a uses into one folder laid out exactly like ./models (i.e. a USB key for offline
installs).

positional arguments:
  models_dir            Target folder, i.e. /media/user/KEY/models or E:\models

options:
  -h, --help            show this help message and exit
  --only ONLY           Comma list of categories: common,xtts,bark,tortoise,vits,fairseq,glowtts,tacotron,yo
                        urtts,piper,zonos,audiocpp,audiocpp_server,gptsovits,f5tts,omnivoice,orpheus,sparktt
                        s,chattts,csm,openvoice,melotts,phonon,stanza,pyannote,demucs,interlude,argos,tessda
                        ta,jieba,voices
  --skip SKIP           Comma list of categories to leave out
  --languages LANGUAGES
                        Comma list of e2a ISO-639-3 codes (eng,fra,ita...): single-language models and fine-
                        tunes for these only, multilingual models only for engines speaking one of them
  --audiocpp_packages AUDIOCPP_PACKAGES
                        audiocpp_server category: auto (the packages this machine runs, GPU and CPU), all
                        (every platform, for a key used elsewhere), or a comma list of audiocpp_packages
                        keys from lib/conf_models.py
  --refresh             Run every job again, even those already marked done (files already there are still
                        not downloaded twice)
  --dry_run             List every download job with its state (done, interrupted, todo) and exit
```

<a id="translate-ebooks"></a>
### Translate ebooks out of e2a: `translate_ebook.sh` / `translate_ebook.cmd`
Translates EPUB/AZW3 files, a whole folder (`-r` for its subfolders) or a list of paths (`@list.txt`)
into translated ebooks, offline, with the Argos Translate calibre plugin shipped in
`tools/argostranslate-calibre-plugin.zip`. Independent of the audiobook conversion: it only writes ebooks.
It needs calibre (already required by e2a) and runs on e2a's `python_env` and argos-translate packages:
a language pair e2a already uses is not downloaded again, a missing one is downloaded on first use.
The plugin is installed on first use into e2a's own calibre profile (`./run`), your calibre is left untouched.
`--to fra,ara,spa` translates into several languages at once, one ebook per language, and `--to all` into every
language the source reaches (`--from`, else each book's own language; installed ones only with `--no_download`).
`--list --from eng` lists the languages English translates into (installed, downloadable, or through English for
another source).
Other formats calibre's `ebook-convert` reads (PDF, DOCX, MOBI, TXT, ...) are converted to EPUB once, before the
first language, and translated as EPUB: `--from` is needed when they carry no language, as PDF and TXT often do.
Without `-o` or `--output_dir`, each translation is saved beside its book as `<name>.<lang>.<ext>`,
and a book whose translation already exists is skipped (`--overwrite` to translate it again).
The launchers in e2a's folder run `tools/translate_ebook.py` with `python_env`, nothing to activate,
from any folder (relative paths are taken from where it is started):
   - **Linux/MacOS**
     ```bash
     ./translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Or directly with `python_env`'s Python: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Started with any other Python,
     the script starts itself again with `python_env`'s.
   - **Docker**: run it inside the e2a container, e.g. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     with paths seen from the container.
   - **Speed**: argostranslate runs on its own defaults (CTranslate2 picks the threads and the fastest compute type,
     int8 on CPU), not on e2a's 1 thread in float32. Set `ARGOS_INTRA_THREADS` or `ARGOS_COMPUTE_TYPE` to override them.

```bash
usage: translate_ebook.py [-h] [-t LANG[,LANG...]] [-f LANG] [-r] [-o OUTPUT] [--output_dir OUTPUT_DIR]
                          [--overwrite] [-m {replace,bilingual}] [--device {cpu,cuda,auto}]
                          [--batch_size BATCH_SIZE] [--no_cache] [--no_download] [--allow_changes] [--list]
                          [books ...]

Translate ebooks offline, out of e2a, with the Argos Translate calibre plugin
(tools/argostranslate-calibre-plugin.zip). EPUB/AZW3 are translated as they are, the other formats
calibre's ebook-convert reads (PDF, DOCX, MOBI, ...) are converted to EPUB once, before the first
language, and their translations saved as EPUB. It runs on e2a's python_env and argos-translate packages
(models/argos-translate): a language pair e2a already uses is not downloaded again, a missing one is
downloaded on first use (direct or through English). The plugin is installed into e2a's own calibre
profile (run/) on first use, your calibre setup is left untouched.
Translated paths are printed on stdout, progress and logs on stderr.

positional arguments:
  books                 Ebook files (EPUB, AZW3, or PDF, DOCX, MOBI... converted to EPUB first) or folders
                        to translate; @list.txt reads paths from a file, one per line

options:
  -h, --help            show this help message and exit
  -t, --to LANG[,LANG...]
                        Target language(s), ISO-639-1 or ISO-639-3 codes, comma separated for several (fr,
                        fra or fra,ara,spa): one translated ebook per language. all: every language the
                        source reaches (see --list --from), installed ones only with --no_download
  -f, --from LANG       Source language, ISO-639-1 or ISO-639-3 code (default: read from each book)
  -r, --recursive       Also look for books in the subfolders of the given folders
  -o, --output OUTPUT   Output file, single input only, same extension as the input, .epub for a converted
                        one (default: <name>.<lang>.<ext> next to the input)
  --output_dir OUTPUT_DIR
                        Write the translations into this folder (subfolders are mirrored with -r) instead of
                        next to each book
  --overwrite           Translate again even if the output file already exists (skipped otherwise)
  -m, --mode {replace,bilingual}
                        replace: the translation replaces the text. bilingual: each paragraph is followed by
                        its translation, saved as <name>.<lang>.bilingual.<ext> (default: replace)
  --device {cpu,cuda,auto}
                        Device argostranslate runs on (default: cpu)
  --batch_size BATCH_SIZE
                        Segments sent to the translation worker per request (default: 16)
  --no_cache            Neither read nor write the translation cache (run/argos_translate/cache.sqlite), the
                        one that makes a second run of the same book near instant
  --no_download         Never download a missing argos-translate package, fail instead
  --allow_changes       Only when argostranslate is missing from python_env: install it even if packages
                        already there would change version
  --list                List the installed and the downloadable language pairs, then exit. With --from
                        and/or --to: only their pairs, plus the targets a source reaches through English

examples:
  translate_ebook.py book.epub --to fr
  translate_ebook.py book.epub --to fra,ara,spa
  translate_ebook.py book.azw3 --from en --to deu -o /path/to/book_deu.azw3
  translate_ebook.py /path/to/books -r --to es,it --output_dir /path/to/books_translated
  translate_ebook.py book.epub --from eng --to all
  translate_ebook.py @books.txt --to ita --mode bilingual
  translate_ebook.py --list
  translate_ebook.py --list --from eng
```

## Sauti Zilizopambwa
Unaweza kupakia sauti yoyote ya sauti katika muundo wowote wa sauti unaotumika, muda unaofaa ni karibu 1 hadi 5 mn.
Haijalishi ikiwa rekodi ina mandharinyuma ya kelele au muziki unaocheza juu yake — E2A itakusafishia sauti.

Orodha ya sauti zilizojengwa ndani ni hasa kwa Kiingereza. Ikiwa unahitaji sauti katika lugha zingine kuwa rasmi
imeongezwa kwenye orodha, tafadhali wasiliana nasi na tutayaweka baada ya kutathminiwa.

## Modeli za TTS Zilizoboreshwa (fine-tuned)
#### Fanya vizuri modeli yako ya TTS

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Ondoa kelele kwenye data ya mafunzo

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Mkusanyiko wa Modeli za TTS Zilizoboreshwa

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Kwa modeli maalum ya XTTSv2, klipu ya sauti ya marejeleo ya sauti ni ya lazima:

## Ubinafsishaji wako mwenyewe wa Ebook2Audiobook
Uko huru kurekebisha libs/conf.py ili kuongeza au kuondoa mipangilio unayotaka. Ikiwa unapanga kufanya hivyo, fanya tu
nakala ya conf.py asili ili kila sasisho la ebook2audiobook utahifadhi conf.py yako iliyorekebishwa na kuweka
tena ile asili. Lazima upange mchakato huo huo kwa models.py. Ikiwa unataka kuifanya modeli yako maalum
kuwa modeli rasmi iliyoboreshwa ya ebook2audiobook, tafadhali wasiliana nasi na tutaiongeza kwenye orodha ya mipangilio iliyowekwa awali.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Matatizo ya Kawaida:
- GPU yangu ya NVIDIA/ROCm/XPU/MPS haitambuliki?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU ni polepole (bora kwenye CPU smp ya seva) huku GPU ikiweza kuwa na ubadilishaji wa karibu wakati halisi.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Hata hivyo haina unakili wa sauti wa zero-shot, na ni sauti za ubora wa Siri, lakini ni haraka zaidi kwenye cpu).
- "Nina matatizo ya utegemezi" - Tumia tu docker, imejitosheleza kabisa na ina hali ya headless,
   ongeza kigezo  mwishoni mwa amri ya docker run kwa maelezo zaidi. `--help`
- "Ninapata tatizo la sauti iliyokatwa!" - TAFADHALI FUNGUA ISSUE KUHUSU HILI,
   hatuzungumzi kila lugha na tunahitaji ushauri kutoka kwa watumiaji ili kuboresha mantiki ya kugawanya sentensi.😊

## ***** RAMANI YA BARABARA *****
- Vipengele vyote vimefunguliwa kwa Michango ya umma ⭐
- Msaada wowote kutoka kwa watu wanaozungumza lugha yoyote inayoungwa mkono ili kutusaidia kuboresha modeli ⭐
- [x] Hakiki Vizuizi/Sura kabla ya kuanza ubadilishaji
- [x] Hariri kwa sentensi iliyobadilishwa kwa mabadiliko ya maandishi ya kina
- [x] Tengeneza intros za muziki, maingiliano, na miisho; hariri miingiliano na miisho
- [x] Ujumuishaji wa lebo za SML kwa sauti, pumziko, mapumziko, na mabadiliko zaidi
- [x] Taarifa za vigezo -h -help katika lugha tofauti
- [x] Uchanganuzi wa OCR kwa PDF / JPG / BMP / PNG / TIFF
- [x] Folda ya Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Kufanya ugawanyaji wa maandishi ya Kichina usigawanye maneno na kuboresha muda wa mapumziko [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Mtunzi wa kizingiti
- [x] Mtunzi wa Podman
- [x] Daftari la Kaggle
- [x] Daftari la Google Colab
- [x] Ujumuishaji wa Audiobookshelf
- [x] Chaguo la Tafsiri ya eBook
- [x] Chaguo za muundo wa matokeo
- [x] Ubadilishaji wa uchakataji-nyingi
- [x] Ubadilishaji wa folda ya eBook ya kundi
- [x] Utambuzi wa Kifaa cha GPU
- [x] Zuia sauti yoyote ya kumbukumbu ya mandharinyuma kwa ajili ya upakiaji wa sauti
- [x] Upakiaji wa modeli mahususi iliyotengenezwa vizuri
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Maombi ya Mtumiaji
- [ ] Ongeza modeli ya lugha ya Kireno cha Ulaya kwa angalau xttsv2, fairseq, vits, piper (msaada unakaribishwa)
- [ ] Ongeza modeli ya lugha ya Kisindhi kwa angalau xttsv2, fairseq, vits, piper (msaada unakaribishwa)

#### Injini za TTS
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1)
- [x] Kuzungumza kwa Samaki/Sauti ya Samaki (https://github.com/fishaudio/fish-speech)[cite: 1)
- [x] Higgs Audio TTS (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] Maya1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1)
- [x] F5-TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1)
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1)
- [x] TTS za sauti (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] Chatterbox (https://github.com/resemble-ai/chatterbox)[cite: 1)
- [x] CosyVoice / CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1)
- [x] Index-tts / Index TTS2 (https://github.com/index-tts/index-tts)[cite: 1)
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Confucius4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1)
- [x] TTS ya Nukta (https://github.com/dot-audio/dots-tts)[cite: 1)
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1)
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1)
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1)
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1)
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1)
- [x] Pocket TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1)
- [x] TTS ya Irodori (https://github.com/irodori-tts/irodori-tts)[cite: 1)
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Kobe (https://github.com/neonbjb/tortoise-tts)[cite: 1)
- [x] Kanda (https://github.com/Zyphra/Zonos)[cite: 1)
- [x] Gome (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Tafsiri ya Readme
- [x] Kiarabu (ara)
- [x] Kichina (zho)
- [x] Kiingereza (Eng)
- [x] Kihispania (spa)
- [x] Kifaransa (fra)
- [x] Kijerumani (deu)
- [x] Kiitaliano (ita)
- [x] Kireno (por)
- [x] Kipolandi (pol)
- [x] Kituruki (tur)
- [x] Kirusi (rus)
- [x] Kiholanzi (nld)
- [x] Kicheki (ces)
- [x] Kijapani (jpn)
- [x] Kihindi (hin)
- [x] Kibengali (ben)
- [x] Kihungaria (hun)
- [x] Kikorea (kor)
- [x] Kivietinamu (vie)
- [x] Kiswidi (swe)
- [x] Kiajemi (fas)
- [x] Kiyoruba (yor)
- [x] Kiswahili (swa)
- [x] Kiindonesia (ind)
- [x] Kislovakia (slk)
- [x] Kikroeshia (hrv)

#### Utangamano wa 💻 OS
- [x] 🪟 Windows x86
- [x] Windows 🪟 YA MKONO
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

## Ziada ya Kupita Kiasi kwa kufunza modeli na mengineyo (Modeli zote za Coqui-tts zinazoungwa mkono na piper-tts katika amri moja rahisi) 
- Kwa taarifa kuhusu hii @ DrewThomasson, kwa sasa anafanyia kazi maendeleo ya hii, [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Make a easy to use training gui for all coqui-tts models in the [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) Completed at [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## Maelezo ya usanifishaji wa Msimbo wa Python kwa wachangiaji
- hakuna mstari tupu kati ya msimbo, isipokuwa kati ya kazi na madarasa.
- nukuu moja inatumika kwa funguo zote isipokuwa kwa dict() na json. dict['key'] huitwa kila wakati kwa nukuu moja
- mwingizo wa nafasi 4, sio tab hata kidogo
- uchapaji mkali kwa kazi zote na tamko la hoja zake na thamani za kurudi
- hakuna nafasi kati ya hoja na uchapaji wake, hakuna nafasi kati ya kazi, "->" na thamani ya kurudi

Mfano:

```python
import json
from typing import Optional

def get_user(user_id:int, users:list[dict])->Optional[dict]:
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def summarize(user:dict)->str:
    return f"User {user['name']} is {'active' if user['is_active'] else 'inactive'}."

def to_json(user:dict)->str:
    return json.dumps({"id": user['id'], "name": user['name'], "email": user['email']})

users:list = [
    dict(id=1, name="alice", email="alice@example.com", role="admin", is_active=True),
    dict(id=2, name="bob", email="bob@example.com", role="editor", is_active=False),
    dict(id=3, name="carol", email="carol@example.com", role="viewer", is_active=True),
]
config = {
    "max_users": 100,
    "default_role": "viewer",
    "allow_signup": True,
}
roles = ['admin', 'editor', 'viewer']
found = get_user(1, users)
if found:
    print(summarize(found))
    print(found['email'])
    print(to_json(found))
if config['default_role'] in roles:
    print(config['default_role'])
```

## Mchango wa maunzi kwa majaribio ya beta unahitajika
Tunakubali aina yoyote ya maunzi ili kujaribu maendeleo yetu kama vile:
- Nvidia kusaidia cuda >= 11.8
- Kadi za intel za XPU
- Kadi za AMD za Rocm zinazounga mkono Rocm >=5.7

@DrewThomasson ikiwa unataka kusaidia kwa namna yoyote ile! 😃
<!--
## Je, unahitaji kukodisha GPU ili kuongeza huduma kutoka kwetu?
- Kura ya maoni imefunguliwa hapa https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Credits
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- Zana ya kujifunza kwa kina kwa ajili ya Maandishi-kwa-maongezi, iliyojaribiwa katika utafiti na uzalishaji.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Fast and local neural text-to-speech engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml inference code for Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- Injini safi ya makadirio ya C++ kwa modeli za sauti, inayoendeshwa na ggml.

## Shukrani za Pekee
Kwa wachangiaji wote wa kifedha na msimbo, kila mchango na pendekezo husaidia kuboresha ubora wa E2A.