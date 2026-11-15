<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

CPU/GPU-converter van e-book naar audioboek met hoofdstukken en metadata<br/>
met geavanceerde TTS-engines en nog veel meer.<br/>
Ondersteunt stemklonen en 1696 talen!
> [!IMPORTANT]
**Deze tool is uitsluitend bedoeld voor gebruik met DRM-vrije, legaal verkregen e-books.** <br>
De auteurs zijn niet verantwoordelijk voor enig misbruik van deze software of voor eventuele juridische gevolgen daarvan. <br>
Gebruik deze tool verantwoord en in overeenstemming met alle toepasselijke wetten.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Bedankt voor het steunen van de ontwikkelaars van ebook2audiobook!
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### Lokaal uitvoeren
[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)Instructies
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### Op afstand uitvoeren
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### Grafische interface (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Klik om afbeeldingen van de web-GUI te zien</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
## Demo's

**Demo van de nieuwe standaardstem**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Meer demo's</summary>

**ASMR-stem** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Regenachtige-dag-stem**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett-stem**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David Attenborough-stem** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Voorbeeld**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

<a id="table-of-contents"></a>
## Inhoudsopgave
- [ebook2audiobook](#ebook2audiobook)
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
- [Contributing](#contributing)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


<a id="features"></a>
## Functies
- 🔧 **Ondersteunde TTS-motoren**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Meerdere bestandsformaten converteren**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Tekstvak** om direct een korte tekst naar audio te converteren
- 🔍 **OCR-scanning** voor bestanden met tekstpagina's als afbeeldingen
- 🔊 **Hoogwaardige tekst-naar-spraak**, van bijna realtime tot een bijna echte stem
- 🗣️ **Optioneel stemklonen** met je eigen stembestand
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Geschikt voor beperkte middelen** — draait op **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Uitvoerformaten van het audioboek**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML-tags ondersteund** — nauwkeurige controle over onderbrekingen, pauzes, stemwisselingen en meer ([see below](#sml-tags-available))
- 🧩 **Optioneel aangepast model** met je eigen getrainde model (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Fijnafgestelde presetmodellen** getraind door het E2A-team<br/>
     <i>(Neem contact met ons op als je extra fijnafgestelde modellen nodig hebt, of als je die van jou wilt delen op de officiële presetlijst)</i>


<a id="hardware-requirements"></a>
##  Hardwarevereisten
- 2 GB RAM min., 8 GB aanbevolen.
- 1 GB VRAM min., 4 GB aanbevolen.
- Virtualisatie ingeschakeld bij gebruik op Windows (alleen Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon-CPU)

*<i> Moderne TTS-engines zijn erg traag op de CPU, gebruik dus TTS van lagere kwaliteit zoals YourTTS, Tacotron2 enz.</i>

<a id="supported-languages"></a>
## Ondersteunde talen
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## Ondersteunde e-bookformaten
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Beste resultaten**: `.epub` of `.mobi` voor automatische hoofdstukdetectie

<a id="output-and-process-formats"></a>
## Uitvoer- en verwerkingsformaten
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Het verwerkingsformaat kan worden gewijzigd in lib/conf.py

## Beschikbare SML-tags
- `[break]` — stilte (willekeurig bereik **0.3–0.6 sec.**)
- `[pause]` — stilte (willekeurig bereik **1.0–1.6 sec.**)
- `[pause:N]` — vaste pauze (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — wissel van stem ten opzichte van de standaard- of in de GUI/CLI geselecteerde stem
- `[emotion:sadness]...[/emotion]` — Alleen Zonos: emotie voor een passage (geluk, verdriet, walging, angst, verrassing, woede, andere, neutraal) of een mix zoals `[emotion:sadness=0.7,neutral=0.3]`; andere motoren negeren het

**Bekijk onze andere repo die gewijd is aan het automatisch toevoegen van SML in je e-book -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Voordat je een installatie- of bugprobleem plaatst, zoek zorgvuldig in het tabblad met open en gesloten issues<br>
om er zeker van te zijn dat je probleem nog niet bestaat.**

Opmerking
**Het EPUB-formaat heeft geen enkele standaardstructuur die aangeeft wat een hoofdstuk, alinea, voorwoord enz. is.<br>
Daarom moet je eerst handmatig alle tekst verwijderen die je niet naar audio wilt converteren.**


<a id="instructions"></a>
### Instructies
1. **Repository klonen**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook installeren / uitvoeren**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Opmerking voor MacOS-gebruikers: homebrew wordt geïnstalleerd om ontbrekende programma's te installeren.</i>
     
   - **Mac-launcher**  
     Dubbelklik op `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     of
     Dubbelklik op `ebook2audiobook.cmd`

     <i>Opmerking voor Windows-gebruikers: scoop wordt geïnstalleerd om ontbrekende programma's te installeren zonder beheerdersrechten.</i>
   
1. **Open de web-app**: Klik op de URL in de terminal om toegang te krijgen tot de web-app en e-books te converteren. `http://localhost:7860/`
2. **Voor een openbare link**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (alle besturingssystemen, slechts eenmaal geïnstalleerd en met de Python van de map python_env)

> [!IMPORTANT]
**Als het script wordt gestopt en opnieuw uitgevoerd, moet je je Gradio-GUI-interface vernieuwen<br>
zodat de webpagina opnieuw verbinding kan maken met de nieuwe verbindings-socket.**

<a id="basic-usage"></a>
### Basisgebruik
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Pad naar je e-bookbestand
  - **[--voice]**: Bestandspad voor stemklonen (optioneel)
  - **[--language]**: Taalcode in ISO-639-3 (bijv.: ita voor Italiaans, eng voor Engels, deu voor Duits...).<br>
    De standaardtaal is eng en --language is optioneel voor de standaardtaal die is ingesteld in ./lib/lang.py.<br>
    De 2-letterige ISO-639-1-codes worden ook ondersteund.


<a id="example-of-custom-model-zip-upload"></a>
###  Voorbeeld van het uploaden van een aangepast model als zip
  (moet een .zip-bestand zijn met de verplichte modelbestanden. Voorbeeld voor XTTSv2: config.json, model.pth, vocab.json en ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Opmerking: de ref.wav van je aangepaste model is altijd de stem die voor de conversie wordt gekozen</i>
     
- **<custom_model_path>**: Pad naar het `model_name.zip`-bestand,
      dat (afhankelijk van de TTS-engine) alle verplichte bestanden moet bevatten<br>
      (zie ./lib/models.py).

### Uitgebreide handleiding met een lijst van alle beschikbare parameters
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Of voor alle besturingssystemen**
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

OPMERKING: in gradio/gui-modus klik je gewoon op de [X] van de e-book-uploadcomponent om een lopende conversie te annuleren.
TIP: als er wat meer pauze nodig is, voeg dan '[pause:3]' toe voor 3 sec. enz.

<a id="docker"></a>
### Docker
1. **De repository klonen**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **De container bouwen**
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
4. **De container starten:**
```bash
Docker run image:
    Gradio/GUI:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc...]
    Headless mode:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
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
- OPMERKING: MPS is niet beschikbaar in Docker, dus moet de CPU worden gebruikt
- OPMERKING: het benoemde volume `e2a_venvs` bewaart de TTS-engines die in hun eigen venv zijn geïnstalleerd (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM enz.)
  tussen containerruns, zodat ze niet elke keer opnieuw worden geïnstalleerd. Om ze te resetten: `docker volume rm e2a_venvs`

<a id="tools"></a>
## Hulpmiddelen
Zelfstandige hulpmiddelen, uitgevoerd met de eigen Python van e2a (`python_env`, aangemaakt bij de eerste start van e2a).

<a id="preload-models"></a>
### Modellen vooraf laden voor offline installaties: `tools/preload_models.py`
Downloadt elk model dat e2a gebruikt (TTS-engines en hun fine-tunes, stemconversie, stanza, pyannote, demucs,
muzikale intermezzo's, argos-translate-pakketten, tesseract-data, jieba en de stemmen) naar één map die
precies zo is opgebouwd als `./models`, bijvoorbeeld een USB-stick. Kopieer op de offline machine die map naar `./models` van e2a
en de map `voices` die ernaast is geschreven naar `./voices` van e2a.
Elke voltooide taak wordt vastgelegd in `<models_dir>/.e2a_downloads.json`: een nieuwe run slaat over wat klaar is en start
opnieuw wat werd onderbroken (ctrl-c, crash, losgekoppelde stick) nadat de gedeeltelijke bestanden zijn verwijderd.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` toont de taken en hun status (klaar, onderbroken, nog te doen) zonder iets te downloaden.

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
### Ebooks vertalen buiten e2a: `tools/translate_ebook.sh` / `tools/translate_ebook.cmd`
Vertaalt EPUB/AZW3-bestanden, een hele map (`-r` voor de submappen) of een lijst met paden (`@list.txt`)
naar vertaalde ebooks, offline, met de Argos Translate-plugin voor calibre die wordt meegeleverd in
`tools/argostranslate-calibre-plugin.zip`. Los van de audioboekconversie: het schrijft alleen ebooks.
Het vereist calibre (al nodig voor e2a) en draait op de `python_env` en argos-translate-pakketten van e2a:
een taalpaar dat e2a al gebruikt wordt niet opnieuw gedownload, een ontbrekend paar wordt bij het eerste gebruik gedownload.
De plugin wordt bij het eerste gebruik geïnstalleerd in het eigen calibre-profiel van e2a (`./run`), jouw calibre blijft onaangeroerd.
`--to fra,ara,spa` vertaalt in één keer naar meerdere talen, één ebook per taal, en `--to all` naar elke
taal die de brontaal bereikt (`--from`, anders de eigen taal van elk boek; met `--no_download` alleen geïnstalleerde taalparen).
`--list --from eng` toont de talen waarnaar Engels vertaalt (geïnstalleerd, downloadbaar, of via het Engels voor
een andere brontaal).
Andere formaten die `ebook-convert` van calibre leest (PDF, DOCX, MOBI, TXT, ...) worden één keer naar EPUB omgezet, vóór de
eerste taal, en als EPUB vertaald: `--from` is nodig wanneer ze geen taal vermelden, zoals vaak bij PDF en TXT.
Zonder `-o` of `--output_dir` wordt elke vertaling naast het boek opgeslagen als `<name>.<lang>.<ext>`,
en een boek waarvan de vertaling al bestaat wordt overgeslagen (`--overwrite` om het opnieuw te vertalen).
De launchers in de map `tools/` voeren `tools/translate_ebook.py` uit met `python_env`, niets te activeren,
vanuit elke map (relatieve paden gelden vanaf de plek waar het wordt gestart):
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Of rechtstreeks met de Python van `python_env`: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Wordt het met een andere Python gestart,
     dan herstart het script zichzelf met die van `python_env`.
   - **Docker**: voer het uit in de e2a-container, bijv. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     met paden zoals de container ze ziet.
   - **Snelheid**: argostranslate draait op zijn eigen standaardinstellingen (CTranslate2 kiest de threads en het snelste rekentype,
     int8 op CPU), niet op de enkele thread in float32 van e2a. Stel `ARGOS_INTRA_THREADS` of `ARGOS_COMPUTE_TYPE` in om ze te overschrijven.

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

<a id="cloned-voices"></a>
## Gekloonde stemmen
U kunt spraakaudio uploaden in elk van de ondersteunde audioformaten, de ideale duur is ongeveer 1 tot 5 mn.
Het maakt niet uit of de opname een lawaaierige achtergrond heeft of dat er muziek overheen wordt afgespeeld — E2A zal de stem voor u opruimen.

De ingebouwde lijst met gekloonde stemmen is voornamelijk in het Engels. Als u wilt dat stemmen in andere talen officieel worden
toegevoegd aan de lijst, neem dan contact met ons op en we zullen ze na beoordeling toevoegen.

<a id="fine-tuned-tts-models"></a>
## Fijnafgestelde (fine-tuned) TTS-modellen
<a id="fine-tune-your-own-tts-model"></a>
#### Verfijn je eigen TTS-model

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Ruis verwijderen uit trainingsdata

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### Collectie van fijnafgestelde TTS-modellen

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Voor een aangepast XTTSv2-model is een referentie-audiofragment van de stem verplicht:

## Je eigen Ebook2Audiobook-aanpassing
Je bent vrij om libs/conf.py aan te passen om de gewenste instellingen toe te voegen of te verwijderen. Als je dit van plan bent, maak dan gewoon
een kopie van de originele conf.py, zodat je bij elke ebook2audiobook-update je gewijzigde conf.py kunt back-uppen en de
originele kunt terugzetten. Je moet hetzelfde proces plannen voor models.py. Als je van je eigen aangepaste model
een officieel fijnafgesteld ebook2audiobook-model wilt maken, neem dan contact met ons op en we voegen het toe aan de presetlijst.

<a id="reverting-to-older-versions"></a>
## Terugkeren naar oudere versies
Releases zijn te vinden -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## Veelvoorkomende problemen:
- Mijn NVIDIA/ROCm/XPU/MPS-GPU wordt niet gedetecteerd?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  De CPU is traag (beter op een server-SMP-CPU), terwijl de GPU een bijna realtime conversie kan bereiken.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Het heeft echter geen zero-shot stemklonen, en de stemmen zijn van Siri-kwaliteit, maar het is veel sneller op de CPU).
- "Ik heb problemen met afhankelijkheden" - Gebruik gewoon Docker, het is volledig zelfstandig en heeft een headless-modus,
   voeg de parameter  toe aan het einde van het docker run-commando voor meer informatie. `--help`
- "Ik heb een probleem met afgekapte audio!" - MAAK HIER ALSJEBLIEFT EEN ISSUE VAN,
   we spreken niet elke taal en hebben advies van gebruikers nodig om de logica voor het splitsen van zinnen te verfijnen.😊

## Wegenkaart
- Alle functies open voor publieke bijdragen ⭐
- Alle hulp van mensen die een van de ondersteunde talen spreken om ons te helpen de modellen te verbeteren ⭐
- [x] Blokken/hoofdstukken bekijken voordat de conversie start
- [x] Bewerken per geconverteerde zin voor chirurgische tekstwijziging
- [x] Genereer muziekintro's, intermezzo's en eindes; bewerk intermezzo's en eindes
- [x] SML-tag-integratie voor stem, pauze, onderbreking en meer wijzigingen
- [x] Info over de parameters -h -help in verschillende talen
- [x] OCR-scanning voor PDF / JPG / BMP / PNG / TIFF
- [x] Notebooks-map [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Ervoor zorgen dat het splitsen van Chinese tekst geen woorden splitst en de timing van pauzes verbeteren [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker opstellen
- [x] Podman componeren
- [x] Kaggle-notebook
- [x] Google Colab-notebook
- [x] Audiobookshelf-integratie
- [x] Optie voor e-bookvertaling
- [x] Keuzes voor uitvoerformaat
- [x] Conversie met multiprocessing
- [x] Batchconversie van een e-bookmap
- [x] GPU-apparaatdetectie
- [x] Denoise elke achtergrondreferentie-audio voor het uploaden van stemklonen
- [x] Aangepaste verfijnde modelupload

#### Verzoeken van gbruikers
- [ ] Een Europees-Portugees taalmodel toevoegen voor ten minste xttsv2, fairseq, vits, piper (hulp welkom)
- [ ] Een Sindhi-taalmodel toevoegen voor ten minste xttsv2, fairseq, vits, piper (hulp welkom)

#### TTS-motoren
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Vis-spraak / Vis-audio (https://github.com/fishaudio/fish-speech)[cite: 1]
- [x] Higgs Audio TTS (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] Maya1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1]
- [x] F5-TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1]
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1]
- [x] Voxtral TTS (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] Chatterbox (https://github.com/resemble-ai/chatterbox)[cite: 1]
- [x] CosyVoice / CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1]
- [x] Index-tts / Index TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Confucius4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Dots TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Mos TTS Lokaal / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Pocket TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Schildpad (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Schors (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Readme-vertaling
- [x] Arabisch (ara)
- [x] Chinees (zho)
- [x] Engels (ENG)
- [x] Spaans (spa)
- [x] Frans (fra)
- [x] Duits (deu)
- [x] Italiaans (ita)
- [x] Portugees (por)
- [x] Pools (pol)
- [x] Turks (tur)
- [x] Russisch (rus)
- [x] Nederlands (nld)
- [x] Tsjechisch (ces)
- [x] Japans (jpn)
- [x] Hindi (hin)
- [x] Bengaals (ben)
- [x] Hongaars (hun)
- [x] Koreaans (kor)
- [x] Vietnamees (Vie)
- [x] Zweeds (swe)
- [x] Perzisch (fas)
- [x] Yoruba (yor)
- [x] Swahili (swa)
- [x] Indonesisch (ind)
- [x] Slowaaks (slk)
- [x] Kroatisch (hrv)

#### Compatibiliteit met OS
- [x] 🪟 Windows x86
- [x] 🪟 Armramen
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

<a id="contributing"></a>
## Bijdragen
Lees [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md): Python-code-normalisatieregels voordat u een probleem of een pull-verzoek opent,
vertakkings- en pull-aanvraagworkflow, GUI-legenda's en README-vertalingen, het toevoegen van een TTS-engine, testen.

## Hardwaredonatie voor bètatests gezocht
We accepteren elk soort hardware om onze ontwikkeling te testen, zoals:
- Nvidia ondersteunende cuda >= 11,8
- XPU INTEL-kaarten
- ROCm AMD-kaarten die ROCm ondersteunen >=5,7

@DrewThomasson als je op welke manier dan ook wilt helpen! 😃
<!--
## Moet je een GPU huren om onze service te versnellen?
- Er is hier een peiling geopend https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Dankwoord
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- A deep learning toolkit for Text-to-Speech, battle-tested in research and production.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Snelle en lokale neurale tekst-naar-spraak-engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml inferentiecode voor Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- Een alles-in-één, pure C++ inferentie-engine voor audiomodellen, aangedreven door ggml.

<a id="special-thanks"></a>
## Speciale dank
Aan alle financiële en code-bijdragers helpt elke bijdrage en suggestie om de kwaliteit van E2A te verbeteren.