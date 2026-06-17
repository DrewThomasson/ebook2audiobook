# 📚 ebook2audiobook (E2A)
CPU/GPU-converter van e-book naar audioboek met hoofdstukken en metadata<br/>
met geavanceerde TTS-engines en nog veel meer.<br/>
Ondersteunt stemklonen en 1158 talen!
> [!IMPORTANT]
**Deze tool is uitsluitend bedoeld voor gebruik met DRM-vrije, legaal verkregen e-books.** <br>
De auteurs zijn niet verantwoordelijk voor enig misbruik van deze software of voor eventuele juridische gevolgen daarvan. <br>
Gebruik deze tool verantwoord en in overeenstemming met alle toepasselijke wetten.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Bedankt voor het steunen van de ontwikkelaars van ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Lokaal uitvoeren

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Op afstand uitvoeren
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Grafische interface (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Klik om afbeeldingen van de web-GUI te zien</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

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

## Inhoudsopgave
- [ebook2audiobook](#-ebook2audiobook)
- [Functies](#features)
- [Grafische interface](#gui-interface)
- [Demo's](#demos)
- [Ondersteunde talen](#supported-languages)
- [Minimale vereisten](#hardware-requirements)
- [Gebruik](#instructions)
  - [Lokaal uitvoeren](#instructions)
    - [De Gradio-webinterface starten](#instructions)
    - [Basisgebruik in headless-modus](#basic-usage)
    - [Gebruik van aangepast XTTS-model in headless-modus](#example-of-custom-model-zip-upload)
    - [Uitvoer van het helpcommando](#help-command-output)
  - [Op afstand uitvoeren](#run-remotely)
  - [Docker](#docker)
    - [Stappen om uit te voeren](#docker)
    - [Veelvoorkomende Docker-problemen](#common-docker-issues)
  
- [Fijnafgestelde TTS-modellen](#fine-tuned-tts-models)
  - [Collectie van fijnafgestelde TTS-modellen](#fine-tuned-tts-collection)
  - [XTTSv2 trainen](#fine-tune-your-own-xttsv2-model)
- [Ondersteunde e-bookformaten](#supported-ebook-formats)
- [Uitvoerformaten](#output-and-process-formats)
- [Terugkeren naar een oudere versie](#reverting-to-older-versions)
- [Veelvoorkomende problemen](#common-issues)
- [Speciale dank](#special-thanks)
- [Inhoudsopgave](#table-of-contents)


## Functies
- 🔧 **Ondersteunde TTS-engines**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Meerdere bestandsformaten converteren**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Tekstvak** om direct een korte tekst naar audio te converteren
- 🔍 **OCR-scanning** voor bestanden met tekstpagina's als afbeeldingen
- 🔊 **Hoogwaardige tekst-naar-spraak**, van bijna realtime tot een bijna echte stem
- 🗣️ **Optioneel stemklonen** met je eigen stembestand
- 🌐 **Ondersteunt 1158 talen** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Geschikt voor beperkte middelen** — draait op **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Uitvoerformaten van het audioboek**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML-tags ondersteund** — nauwkeurige controle over onderbrekingen, pauzes, stemwisselingen en meer ([see below](#sml-tags-available))
- 🧩 **Optioneel aangepast model** met je eigen getrainde model (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Fijnafgestelde presetmodellen** getraind door het E2A-team<br/>
     <i>(Neem contact met ons op als je extra fijnafgestelde modellen nodig hebt, of als je die van jou wilt delen op de officiële presetlijst)</i>


##  Hardwarevereisten
- 2 GB RAM min., 8 GB aanbevolen.
- 1 GB VRAM min., 4 GB aanbevolen.
- Virtualisatie ingeschakeld bij gebruik op Windows (alleen Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon-CPU)

*<i> Moderne TTS-engines zijn erg traag op de CPU, gebruik dus TTS van lagere kwaliteit zoals YourTTS, Tacotron2 enz.</i>

## Ondersteunde talen
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 talen en dialecten hier**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Ondersteunde e-bookformaten
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Beste resultaten**: `.epub` of `.mobi` voor automatische hoofdstukdetectie

## Uitvoer- en verwerkingsformaten
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Het verwerkingsformaat kan worden gewijzigd in lib/conf.py

## Beschikbare SML-tags
- `[break]` — stilte (willekeurig bereik **0.3–0.6 sec.**)
- `[pause]` — stilte (willekeurig bereik **1.0–1.6 sec.**)
- `[pause:N]` — vaste pauze (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — wissel van stem ten opzichte van de standaard- of in de GUI/CLI geselecteerde stem

**Bekijk onze andere repo die gewijd is aan het automatisch toevoegen van SML in je e-book -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**Voordat je een installatie- of bugprobleem plaatst, zoek zorgvuldig in het tabblad met open en gesloten issues<br>
om er zeker van te zijn dat je probleem nog niet bestaat.**

>[!NOTE]
**Het EPUB-formaat heeft geen enkele standaardstructuur die aangeeft wat een hoofdstuk, alinea, voorwoord enz. is.<br>
Daarom moet je eerst handmatig alle tekst verwijderen die je niet naar audio wilt converteren.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook installeren / uitvoeren**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac-launcher**  
     Dubbelklik op `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Opmerking voor Windows-gebruikers: scoop wordt geïnstalleerd om ontbrekende programma's te installeren zonder beheerdersrechten.</i>
   
1. **Open de web-app**: Klik op de URL in de terminal om toegang te krijgen tot de web-app en e-books te converteren. `http://localhost:7860/`
2. **Voor een openbare link**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Als het script wordt gestopt en opnieuw uitgevoerd, moet je je Gradio-GUI-interface vernieuwen<br>
zodat de webpagina opnieuw verbinding kan maken met de nieuwe verbindings-socket.**

### Basic  Usage
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
     
- **<custom_model_path>**: Pad naar het `model_name.zip`-bestand,
      dat (afhankelijk van de TTS-engine) alle verplichte bestanden moet bevatten<br>
      (zie ./lib/models.py).

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

```

OPMERKING: in gradio/gui-modus klik je gewoon op de [X] van de e-book-uploadcomponent om een lopende conversie te annuleren.
TIP: als er wat meer pauze nodig is, voeg dan '[pause:3]' toe voor 3 sec. enz.

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
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --runtime nvidia  --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[51/60/61 etc...]
    Headless mode:
        CPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
Docker Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 docker compose --profile gpu up --no-log-prefix
        Run Headless mode:
               DEVICE_TAG=cu128 docker compose --profile gpu run --rm ebook2audiobook --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
Podman Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile gpu up
        Run Headless mode:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile gpu run --rm ebook2audiobook-gpu --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
```
- NOTE: MPS is not exposed in docker so CPU must be used
  
### Veelvoorkomende Docker-problemen
- Mijn NVIDIA-GPU wordt niet gedetecteerd?? -> [Wikipagina GPU-PROBLEMEN](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Fijnafgestelde (fine-tuned) TTS-modellen
#### Stel je eigen XTTSv2-model fijn af

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Ruis verwijderen uit trainingsdata

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Collectie van fijnafgestelde TTS-modellen

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Voor een aangepast XTTSv2-model is een referentie-audiofragment van de stem verplicht:

## Je eigen Ebook2Audiobook-aanpassing
Je bent vrij om libs/conf.py aan te passen om de gewenste instellingen toe te voegen of te verwijderen. Als je dit van plan bent, maak dan gewoon
een kopie van de originele conf.py, zodat je bij elke ebook2audiobook-update je gewijzigde conf.py kunt back-uppen en de
originele kunt terugzetten. Je moet hetzelfde proces plannen voor models.py. Als je van je eigen aangepaste model
een officieel fijnafgesteld ebook2audiobook-model wilt maken, neem dan contact met ons op en we voegen het toe aan de presetlijst.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Veelvoorkomende problemen:
- Mijn NVIDIA/ROCm/XPU/MPS-GPU wordt niet gedetecteerd?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  De CPU is traag (beter op een server-SMP-CPU), terwijl de GPU een bijna realtime conversie kan bereiken.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Het heeft echter geen zero-shot stemklonen, en de stemmen zijn van Siri-kwaliteit, maar het is veel sneller op de CPU).
- "Ik heb problemen met afhankelijkheden" - Gebruik gewoon Docker, het is volledig zelfstandig en heeft een headless-modus,
   voeg de parameter `--help` toe aan het einde van het docker run-commando voor meer informatie.
- "Ik heb een probleem met afgekapte audio!" - MAAK HIER ALSJEBLIEFT EEN ISSUE VAN,
   we spreken niet elke taal en hebben advies van gebruikers nodig om de logica voor het splitsen van zinnen te verfijnen.😊

## ***** ROADMAP *****
- Alle functies open voor publieke bijdragen ⭐
- Alle hulp van mensen die een van de ondersteunde talen spreken om ons te helpen de modellen te verbeteren ⭐
- [x] Blokken/hoofdstukken bekijken voordat de conversie start
- [ ] Bewerken per geconverteerde zin voor chirurgische tekstwijziging
- [x] SML-tag-integratie voor stem, pauze, onderbreking en meer wijzigingen 
- [x] Info over de parameters -h -help in verschillende talen
- [x] OCR-scanning voor PDF / JPG / BMP / PNG / TIFF
- [x] Notebooks-map [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Ervoor zorgen dat het splitsen van Chinese tekst geen woorden splitst en de timing van pauzes verbeteren [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle-notebook
- [x] Google Colab-notebook
- [ ] [Een iOS-app maken](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Een Android-app maken](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Audiobookshelf-integratie

#### Extra opties
- [x] Optie voor e-bookvertaling
- [x] Keuzes voor uitvoerformaat
- [x] Batch e-bookmap
- [x] Conversie met multiprocessing
- [x] Batchconversie van een e-bookmap
- [x] GPU-apparaatdetectie
- [x] Ruis verwijderen uit elke referentie-audio voor het uploaden van stemklonen,
- [x] Upload van aangepast model (voorlopig alleen XTTSv2. meer op aanvraag)
- [ ] Een Europees-Portugees taalmodel toevoegen voor ten minste xttsv2, fairseq, vits, piper (hulp welkom)
- [ ] Een Sindhi-taalmodel toevoegen voor ten minste xttsv2, fairseq, vits, piper (hulp welkom)

#### TTS-motoren
- [x] XTTSv2
- [x] Blaffen
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Schildpad
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] vis-spraak (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Stijl-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Readme-vertaling
- [ ] Arabic (ara)
- [ ] Chinese (zho)
- [x] English (eng)
- [ ] Spanish (spa)
- [ ] French (fra)
- [ ] German (deu)
- [ ] Italian (ita)
- [ ] Portuguese (por)
- [ ] Polish (pol)
- [ ] Turkish (tur)
- [ ] Russian (rus)
- [ ] Dutch (nld)
- [ ] Czech (ces)
- [ ] Japanese (jpn)
- [ ] Hindi (hin)
- [ ] Bengali (ben)
- [ ] Hungarian (hun)
- [ ] Korean (kor)
- [ ] Vietnamese (vie)
- [ ] Swedish (swe)
- [ ] Persian (fas)
- [ ] Yoruba (yor)
- [ ] Swahili (swa)
- [ ] Indonesian (ind)
- [ ] Slovak (slk)
- [ ] Croatian (hrv)   

#### 🐍 Compatibiliteit met besturingssystemen
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra overkill voor het trainen van modellen en dergelijke (alle ondersteunde Coqui-tts-modellen en piper-tts in één eenvoudige opdracht) 
- Voor informatie hierover: @DrewThomasson werkt momenteel aan de ontwikkeling hiervan, [work-in-progress-repo hier](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Een gebruiksvriendelijke trainings-GUI maken voor alle coqui-tts-modellen in de ljspeech-formaat trainingsrecepten [hier van coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informatie over Python-codenormalisatie voor bijdragers
- geen lege regel tussen de code, behalve tussen functies en klassen.
- enkele aanhalingstekens gebruikt voor alle sleutels behalve voor dict() en json. dict['key'] altijd aangeroepen met enkele aanhalingstekens
- 4 spaties inspringing, helemaal geen tabs
- strikte typering voor alle functies en de declaratie van hun argumenten en retourwaarden
- geen spatie tussen het argument en de typering ervan, geen spatie tussen de functie, de "->" en de retourwaarde

Voorbeeld:

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

## Hardwaredonatie voor bètatests gezocht
We accepteren elk soort hardware om onze ontwikkeling te testen, zoals:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson als je op welke manier dan ook wilt helpen! 😃
<!--
## Moet je een GPU huren om onze service te versnellen?
- Er is hier een peiling geopend https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Speciale dank
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 voor een betere methode om hoofdstukken op te slaan](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
