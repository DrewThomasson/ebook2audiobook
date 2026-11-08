<<<<<<< HEAD
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Convertitore CPU/GPU da e-book ad audiolibro con capitoli e metadati<br/>
utilizzando motori TTS avanzati e molto altro.<br/>
Supporta la clonazione vocale e 1696 lingue!
> [!IMPORTANT]
**Questo strumento è destinato all'uso esclusivamente con e-book privi di DRM e acquisiti legalmente.** <br>
Gli autori non sono responsabili di alcun uso improprio di questo software né di eventuali conseguenze legali. <br>
Utilizza questo strumento in modo responsabile e nel rispetto di tutte le leggi vigenti.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Grazie per il supporto agli sviluppatori di ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Esecuzione locale

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Esecuzione da remoto
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Interfaccia grafica (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Clicca per vedere le immagini della GUI web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demo

**Demo della nuova voce predefinita**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Altre demo</summary>

**Voce ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Voce giorno di pioggia**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Voce Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Voce David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Esempio**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Indice
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


## Funzionalità
- 🔧 ** Motori TTS supportati**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Convertire più formati di file**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Area di testo** per convertire direttamente un breve testo in audio
- 🔍 **Scansione OCR** per file con pagine di testo sotto forma di immagini
- 🔊 **Sintesi vocale di alta qualità**, dal quasi tempo reale a una voce quasi reale
- 🗣️ **Clonazione vocale opzionale** utilizzando il tuo file vocale
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Adatto a risorse limitate** — funziona con **2 GB di RAM / 1 GB di VRAM (minimo)**
- 🎵 **Formati di output dell'audiolibro**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Tag SML supportati** — controllo granulare di interruzioni, pause, cambio voce e altro ([see below](#sml-tags-available))
- 🧩 **Modello personalizzato opzionale** utilizzando il tuo modello addestrato (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modelli preset ottimizzati** addestrati dal team E2A<br/>
     <i>(Contattaci se hai bisogno di modelli ottimizzati aggiuntivi, o se desideri condividere i tuoi nell'elenco ufficiale dei preset)</i>


##  Requisiti hardware
- 2 GB di RAM min., 8 GB consigliati.
- 1 GB di VRAM min., 4 GB consigliati.
- Virtualizzazione abilitata se eseguito su Windows (solo Docker).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> I moderni motori TTS sono molto lenti su CPU, quindi usa TTS di qualità inferiore come YourTTS, Tacotron2 ecc.</i>

## Lingue supportate
| **Arabo (ar)**    | **Cinese (zh)**    | **Inglese (en)**   | **Spagnolo (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **Francese (fr)**    | **Tedesco (de)**     | **Italiano (it)**   | **Portoghese (pt)** |
| **Polacco (pl)**    | **Turco (tr)**    | **Russo (ru)**   | **Olandese (nl)**     |
| **Ceco (cs)**     | **Giapponese (ja)**   | **Hindi (hi)**     | **Bengalese (bn)**   |
| **Ungherese (hu)** | **Coreano (ko)**     | **Vietnamita (vi)**| **Svedese (sv)**   |
| **Persiano (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesiano (id)**|
| **Slovacco (sk)**    | **Croato (hr)**   | **Tamil (ta)**     | **Danese (da)**    |
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Formati di e-book supportati
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Risultati migliori**: `.epub` o `.mobi` per il rilevamento automatico dei capitoli

## Formati di output e di elaborazione
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Il formato di elaborazione può essere modificato in lib/conf.py

## Tag SML disponibili
- `[break]` — silenzio (intervallo casuale **0.3–0.6 sec.**)
- `[pause]` — silenzio (intervallo casuale **1.0–1.6 sec.**)
- `[pause:N]` — pausa fissa (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — cambiare voce rispetto alla voce predefinita o selezionata da GUI/CLI
- `[emotion:sadness]...[/emotion]` — Solo zoni: emozione per un passaggio (felicità, tristezza, disgusto, paura, sorpresa, rabbia, altro, neutro) o un mix come `[emotion:sadness=0.7,neutral=0.3]`; altri motori lo ignorano

**Dai un'occhiata al nostro altro repo dedicato all'aggiunta automatica di SML nel tuo e-book -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Prima di pubblicare un problema di installazione o un bug, cerca attentamente nella scheda dei problemi aperti e chiusi<br>
per essere sicuro che il tuo problema non esista già.**

Note
**Il formato EPUB è privo di qualsiasi struttura standard che definisca cosa sia un capitolo, un paragrafo, una prefazione, ecc.<br>
Quindi dovresti prima rimuovere manualmente qualsiasi testo che non vuoi convertire in audio.**


### Istruzioni
1. **Clona repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Installa / Esegui ebook2audiobook**:

   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Nota per gli utenti MacOS: homebrew è installato per installare i programmi mancanti.</i>
     
   - **Launcher per Mac**  
     Fai doppio clic su `Mac Ebook2Audiobook Launcher.command`


   - Vetrine
     ```bash
     ebook2audiobook.cmd
     ```
     oppure
     Doppio clic `ebook2audiobook.cmd`

     <i>Nota per gli utenti Windows: scoop viene installato per installare i programmi mancanti senza privilegi di amministratore.</i>
   
1. **Apri la Web App**: Clicca sull'URL fornito nel terminale per accedere alla web app e convertire gli e-book. `http://localhost:7860/`
2. **Per un link pubblico**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Se lo script viene interrotto e rieseguito, devi aggiornare la tua interfaccia grafica Gradio<br>
per consentire alla pagina web di riconnettersi al nuovo socket di connessione.**

### Uso di Base
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - VETRINE
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Percorso del tuo file e-book
  - **[--voice]**: Percorso del file per la clonazione vocale (opzionale)
  - **[--language]**: Codice della lingua in ISO-639-3 (es.: ita per italiano, eng per inglese, deu per tedesco...).<br>
    La lingua predefinita è eng e --language è opzionale per la lingua predefinita impostata in ./lib/lang.py.<br>
    Sono supportati anche i codici ISO-639-1 a 2 lettere.


###  Esempio di caricamento zip modello personalizzato
  (deve essere un file .zip contenente i file di modello obbligatori. Esempio per XTTSv2: config.json, model.pth, vocab.json e ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - VETRINE
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Nota: l'ref.wav del tuo modello personalizzato è sempre la voce selezionata per la conversione</i>
     
- **<custom_model_path>**: Percorso del file `model_name.zip`,
      che deve contenere (a seconda del motore TTS) tutti i file obbligatori<br>
      (vedi ./lib/models.py).

### Per Guida Dettagliata con elenco di tutti i Parametri da utilizzare
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - VETRINE
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **O per tutti i sistemi operativi**
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

NOTA: in modalità gradio/gui, per annullare una conversione in corso, basta cliccare sulla [X] del componente di caricamento dell'e-book.
SUGGERIMENTO: se serve qualche pausa in più, aggiungi '[pause:3]' per 3 sec., ecc.

### Docker
1. Clona il repository:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Costruisci il container**
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
4. **Eseguire il container:**
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
- NOTA: MPS non è esposto nel docker, quindi è necessario utilizzare la CPU
- NOTA: il volume denominato `e2a_venvs` mantiene i motori TTS installati nel proprio venv (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM ecc.)
  attraverso i percorsi dei container, in modo che non vengano reinstallati ogni volta. Per resettarli: `docker volume rm e2a_venvs`

## Utensili
Strumenti autonomi, eseguiti con il Python di e2a (`python_env`, creato dal primo lancio di e2a).

<a id="preload-models"></a>
### Modelli di precarico per installazioni offline: `tools/preload_models.py`
Scarica ogni modello utilizzato da e2a (motori TTS e loro perfezionamenti, conversione vocale, stanza, pyannote, demucs,
interludi musicali, pacchetti argos-translate, dati tesseract, jieba e le voci) in un'unica cartella
esattamente come , cioè una chiavetta USB. Sulla macchina offline, copiare quella cartella nella cartella ⟦1 di e2a⟧ `./models` `./models`
e la⟧ cartella ⟦0 scritta accanto in ⟦1 di e2a⟧. `voices` `./voices`
Ogni lavoro finito viene registrato in `<models_dir>/.e2a_downloads.json`: una ripetizione salta ciò che viene fatto e inizia
nuovamente ciò che è stato tagliato (ctrl-c, crash, tasto scollegato) dopo aver rimosso i suoi file parziali.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - VETRINE
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` elenca i lavori e il loro stato (fatto, interrotto, da fare) senza scaricare nulla.

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
### Traduci ebook da e2a: `translate_ebook.sh`/`translate_ebook.cmd`
Traduce file EPUB/AZW3, un'intera cartella (`-r` per le sue sottocartelle) o un elenco di percorsi (`@list.txt`)
in ebook tradotti, offline, con il plugin di calibro Argos Translate spedito in
`tools/argostranslate-calibre-plugin.zip`. Indipendente dalla conversione dell'audiolibro: scrive solo ebook.
Ha bisogno di calibro (già richiesto da e2a) e funziona su pacchetti `python_env` e argos-translate di e2a:
una combinazione linguistica e2a già utilizzata non viene scaricata di nuovo, una mancante viene scaricata al primo utilizzo.
Il plugin viene installato al primo utilizzo nel profilo di calibro di e2a (`./run`), il tuo calibro non viene toccato.
`--to fra,ara,spa` si traduce in più lingue contemporaneamente, un ebook per lingua e `--to all` in ogni
lingua raggiunta dalla fonte (`--from`, altrimenti la lingua di ogni libro; quelli installati solo con `--no_download`).
`--list --from eng` elenca le lingue in cui l'inglese viene tradotto (installato, scaricabile o in inglese per
un'altra fonte).
Gli altri formati di⟧ lettura ⟦0 del calibro (PDF, DOCX, mobi, txt, ...) vengono convertiti in EPUB una volta, prima del `ebook-convert`
prima lingua e tradotto come EPUB: `--from` è necessario quando non hanno una lingua, come spesso fanno PDF e txt.
Senza `-o` o `--output_dir`, ogni traduzione viene salvata accanto al suo libro come `<name>.<lang>.<ext>`,
e un libro la cui traduzione esiste già viene saltato (`--overwrite` per tradurlo di nuovo).
I launcher nella cartella di e2a eseguono `tools/translate_ebook.py` con `python_env`, nulla da attivare,
da qualsiasi cartella (i percorsi relativi vengono presi da dove viene avviato):
   - **Linux/MacOS**
     ```bash
     ./translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - VETRINE
     ```bash
     translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - O direttamente con Python⟧ di ⟦0: `./python_env/bin/python tools/translate_ebook.py ...` `python_env`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Avviato con qualsiasi altro Python,
     lo script ricomincia da ⟦⟧zero. `python_env`
   - **Docker**: eseguirlo all'interno del container e2a, ad es. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     con percorsi visti dal container.
   - **Velocità**: argostranslate viene eseguito in base alle proprie impostazioni predefinite (CTranslate2 sceglie i thread e il tipo di calcolo più veloce,
     int8 sulla CPU), non sul thread 1 di e2a in float32. Impostare `ARGOS_INTRA_THREADS` o `ARGOS_COMPUTE_TYPE` per sovrascriverli.

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

## Voci clonate
È possibile caricare qualsiasi audio vocale in uno qualsiasi dei formati audio supportati, la durata ideale è di circa 1-5 minuti.
Non importa se la registrazione ha uno sfondo rumoroso o se la musica viene riprodotta su di essa: E2A ripulirà la voce per te.

L'elenco delle voci clonate integrate è principalmente in inglese. Se hai bisogno che le voci in altre lingue siano ufficialmente
aggiunto all'elenco, ti preghiamo di contattarci e li aggiungeremo dopo averlo esaminato.

## Modelli TTS ottimizzati (fine-tuned)
#### Ottimizza il tuo modello TTS

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Rimuovere il rumore dai dati di addestramento

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Collezione di modelli TTS ottimizzati

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Per un modello personalizzato XTTSv2 è obbligatorio un clip audio di riferimento della voce:

## La tua personalizzazione di Ebook2Audiobook
Sei libero di modificare libs/conf.py per aggiungere o rimuovere le impostazioni che desideri. Se intendi farlo, crea semplicemente
una copia del conf.py originale così che, a ogni aggiornamento di ebook2audiobook, tu possa salvare il tuo conf.py modificato e ripristinare
quello originale. Devi pianificare lo stesso processo per models.py. Se desideri rendere il tuo modello personalizzato
un modello ottimizzato ufficiale di ebook2audiobook, contattaci e lo aggiungeremo all'elenco dei preset.

## Ripristino delle versioni precedenti
I rilasci possono essere trovati -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Problemi comuni:
- La mia GPU NVIDIA/ROCm/XPU/MPS non viene rilevata?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  La CPU è lenta (meglio su una CPU SMP da server) mentre la GPU può ottenere una conversione quasi in tempo reale.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Non ha però la clonazione vocale zero-shot, e le voci sono di qualità Siri, ma è molto più veloce su CPU).
- «Ho problemi di dipendenze» - Usa semplicemente Docker, è completamente autonomo e ha una modalità headless,
   aggiungi il parametro  alla fine del comando docker run per maggiori informazioni. `--help`
- «Ho un problema di audio troncato!» - PER FAVORE APRI UN ISSUE A RIGUARDO,
   non parliamo tutte le lingue e abbiamo bisogno dei consigli degli utenti per perfezionare la logica di divisione delle frasi.😊

## Roadmap
- Tutte le funzionalità aperte ai contributi pubblici ⭐
- Qualsiasi aiuto da parte di persone che parlano una delle lingue supportate per aiutarci a migliorare i modelli ⭐
- [x] Anteprima di blocchi/capitoli prima di avviare la conversione
- [x] Modifica per frase convertita per un cambiamento chirurgico del testo
- [x] Genera intro, interludi e finali musicali; modifica interludi e finali
- [x] Integrazione dei tag SML per voce, pausa, interruzione e altre modifiche
- [x] Informazioni sui parametri -h -help in diverse lingue
- [x] Scansione OCR per PDF / JPG / BMP / PNG / TIFF
- [x] Cartella dei notebook [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Fare in modo che la divisione del testo cinese non spezzi le parole e migliorare la sincronizzazione delle pause [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compone
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [x] Integrazione con Audiobookshelf
- [x] Opzione di traduzione dell'e-book
- [x] Scelte del formato di output
- [x] Conversione con multiprocessing
- [x] Conversione in batch di una cartella di e-book
- [x] Rilevamento del dispositivo GPU
- [x] Denoise any background reference audio for voice cloning upload
- [x] Caricamento del modello personalizzato perfezionato
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Richieste degli utenti
- [ ] Aggiungere un modello linguistico portoghese europeo almeno per xttsv2, fairseq, vits, piper (aiuto benvenuto)
- [ ] Aggiungere un modello linguistico sindhi almeno per xttsv2, fairseq, vits, piper (aiuto benvenuto)

#### Motori TTS
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Fish-speech / Fish Audio (https://github.com/fishaudio/fish-speech)[cite: 1]
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
- [x] Indice-tts / Indice TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Confucio 4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Puntini TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Locale / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Tasca TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Fonone al Gradio (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotrone2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Tartaruga (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zoni (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Corteccia (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Traduzione del Readme
- [x] Arabo (ara)
- [x] Cinese (zho)
- [x] Inglese (ENG)
- [x] Spagnolo (spa)
- [x] Francese (fra)
- [x] Tedesco (deu)
- [x] Italiano (ita)
- [x] Portoghese (POR)
- [x] Polacco (pol)
- [x] Turco (tur)
- [x] Russo (rus)
- [x] Olandese (nld)
- [x] Ceco (ces)
- [x] Giapponese (jpn)
- [x] Hindi (hin)
- [x] Bengalese (ben)
- [x] Ungherese (hun)
- [x] Coreano (kor)
- [x] Vietnamita (vie)
- [x] Svedese (swe)
- [x] Persiano (fas)
- [x] Yoruba (yor)
- [x] Swahili (swa)
- [x] Indonesiano (ind)
- [x] Slovacco (slk)
- [x] Croato (hrv)

#### Compatibilità del sistema operativo
- [x] 🪟 Windows x86
- [x] Finestre 🪟 ARM
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

## Extra esagerato per addestrare modelli e simili (tutti i modelli Coqui-tts supportati e piper-tts in un unico semplice comando) 
- Per informazioni su questo @ DrewThomasson, sta attualmente lavorando allo sviluppo di questo, [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Crea una guida di formazione facile da usare per tutti i modelli coqui-tts nel [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) Completed at [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## Informazioni sulla normalizzazione del codice Python per i contributori
- nessuna riga vuota tra il codice, tranne tra funzioni e classi.
- apice singolo usato per tutte le chiavi tranne che per dict() e json. dict['key'] sempre richiamato con apice singolo
- indentazione di 4 spazi, nessuna tabulazione
- tipizzazione rigorosa per tutte le funzioni e per la dichiarazione dei loro argomenti e valori di ritorno
- nessuno spazio tra l'argomento e la sua tipizzazione, nessuno spazio tra la funzione, il «->» e il valore di ritorno

Esempio:

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

## Cercasi donazione di hardware per i beta test
Accettiamo qualsiasi tipo di hardware per testare il nostro sviluppo, come:
- Nvidia Supporting cuda >= 11,8
- Schede intel XPU
- Schede ROCm AMD che supportano ROCm >=5,7

@DrewThomasson se vuoi dare una mano in qualsiasi modo! 😃
<!--
## Hai bisogno di noleggiare una GPU per potenziare il nostro servizio?
- È aperto un sondaggio qui https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Crediti
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- A deep learning toolkit for Text-to-Speech, battle-tested in research and production.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Motore di sintesi vocale neurale veloce e locale.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- codice di inferenza ggml per Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) - Un motore di inferenza C++ all-in-one e puro per modelli audio, alimentato da ggml.

## Ringraziamenti speciali
=======
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Convertitore CPU/GPU da e-book ad audiolibro con capitoli e metadati<br/>
utilizzando motori TTS avanzati e molto altro.<br/>
Supporta la clonazione vocale e 1696 lingue!
> [!IMPORTANT]
**Questo strumento è destinato all'uso esclusivamente con e-book privi di DRM e acquisiti legalmente.** <br>
Gli autori non sono responsabili di alcun uso improprio di questo software né di eventuali conseguenze legali. <br>
Utilizza questo strumento in modo responsabile e nel rispetto di tutte le leggi vigenti.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Grazie per il supporto agli sviluppatori di ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Esecuzione locale

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Esecuzione da remoto
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Interfaccia grafica (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Clicca per vedere le immagini della GUI web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demo

**Demo della nuova voce predefinita**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Altre demo</summary>

**Voce ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Voce giorno di pioggia**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Voce Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Voce David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Esempio**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Indice
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


## Funzionalità
- 🔧 ** Motori TTS supportati**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Convertire più formati di file**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Area di testo** per convertire direttamente un breve testo in audio
- 🔍 **Scansione OCR** per file con pagine di testo sotto forma di immagini
- 🔊 **Sintesi vocale di alta qualità**, dal quasi tempo reale a una voce quasi reale
- 🗣️ **Clonazione vocale opzionale** utilizzando il tuo file vocale
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Adatto a risorse limitate** — funziona con **2 GB di RAM / 1 GB di VRAM (minimo)**
- 🎵 **Formati di output dell'audiolibro**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Tag SML supportati** — controllo granulare di interruzioni, pause, cambio voce e altro ([see below](#sml-tags-available))
- 🧩 **Modello personalizzato opzionale** utilizzando il tuo modello addestrato (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modelli preset ottimizzati** addestrati dal team E2A<br/>
     <i>(Contattaci se hai bisogno di modelli ottimizzati aggiuntivi, o se desideri condividere i tuoi nell'elenco ufficiale dei preset)</i>


##  Requisiti hardware
- 2 GB di RAM min., 8 GB consigliati.
- 1 GB di VRAM min., 4 GB consigliati.
- Virtualizzazione abilitata se eseguito su Windows (solo Docker).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> I moderni motori TTS sono molto lenti su CPU, quindi usa TTS di qualità inferiore come YourTTS, Tacotron2 ecc.</i>

## Lingue supportate
| **Arabo (ar)**    | **Cinese (zh)**    | **Inglese (en)**   | **Spagnolo (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **Francese (fr)**    | **Tedesco (de)**     | **Italiano (it)**   | **Portoghese (pt)** |
| **Polacco (pl)**    | **Turco (tr)**    | **Russo (ru)**   | **Olandese (nl)**     |
| **Ceco (cs)**     | **Giapponese (ja)**   | **Hindi (hi)**     | **Bengalese (bn)**   |
| **Ungherese (hu)** | **Coreano (ko)**     | **Vietnamita (vi)**| **Svedese (sv)**   |
| **Persiano (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesiano (id)**|
| **Slovacco (sk)**    | **Croato (hr)**   | **Tamil (ta)**     | **Danese (da)**    |
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Formati di e-book supportati
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Risultati migliori**: `.epub` o `.mobi` per il rilevamento automatico dei capitoli

## Formati di output e di elaborazione
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Il formato di elaborazione può essere modificato in lib/conf.py

## Tag SML disponibili
- `[break]` — silenzio (intervallo casuale **0.3–0.6 sec.**)
- `[pause]` — silenzio (intervallo casuale **1.0–1.6 sec.**)
- `[pause:N]` — pausa fissa (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — cambiare voce rispetto alla voce predefinita o selezionata da GUI/CLI
- `[emotion:sadness]...[/emotion]` — Solo zoni: emozione per un passaggio (felicità, tristezza, disgusto, paura, sorpresa, rabbia, altro, neutro) o un mix come `[emotion:sadness=0.7,neutral=0.3]`; altri motori lo ignorano

**Dai un'occhiata al nostro altro repo dedicato all'aggiunta automatica di SML nel tuo e-book -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Prima di pubblicare un problema di installazione o un bug, cerca attentamente nella scheda dei problemi aperti e chiusi<br>
per essere sicuro che il tuo problema non esista già.**

Note
**Il formato EPUB è privo di qualsiasi struttura standard che definisca cosa sia un capitolo, un paragrafo, una prefazione, ecc.<br>
Quindi dovresti prima rimuovere manualmente qualsiasi testo che non vuoi convertire in audio.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Installa / Esegui ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Launcher per Mac**  
     Fai doppio clic su `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Nota per gli utenti Windows: scoop viene installato per installare i programmi mancanti senza privilegi di amministratore.</i>
   
1. **Apri la Web App**: Clicca sull'URL fornito nel terminale per accedere alla web app e convertire gli e-book. `http://localhost:7860/`
2. **Per un link pubblico**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Se lo script viene interrotto e rieseguito, devi aggiornare la tua interfaccia grafica Gradio<br>
per consentire alla pagina web di riconnettersi al nuovo socket di connessione.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Percorso del tuo file e-book
  - **[--voice]**: Percorso del file per la clonazione vocale (opzionale)
  - **[--language]**: Codice della lingua in ISO-639-3 (es.: ita per italiano, eng per inglese, deu per tedesco...).<br>
    La lingua predefinita è eng e --language è opzionale per la lingua predefinita impostata in ./lib/lang.py.<br>
    Sono supportati anche i codici ISO-639-1 a 2 lettere.


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
     
- **<custom_model_path>**: Percorso del file `model_name.zip`,
      che deve contenere (a seconda del motore TTS) tutti i file obbligatori<br>
      (vedi ./lib/models.py).

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

NOTA: in modalità gradio/gui, per annullare una conversione in corso, basta cliccare sulla [X] del componente di caricamento dell'e-book.
SUGGERIMENTO: se serve qualche pausa in più, aggiungi '[pause:3]' per 3 sec., ecc.

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

## Utensili
Strumenti autonomi, eseguiti con il Python di e2a (`python_env`, creato dal primo lancio di e2a).

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

## Voci clonate
È possibile caricare qualsiasi audio vocale in uno qualsiasi dei formati audio supportati, la durata ideale è di circa 1-5 minuti.
Non importa se la registrazione ha uno sfondo rumoroso o se la musica viene riprodotta su di essa: E2A ripulirà la voce per te.

L'elenco delle voci clonate integrate è principalmente in inglese. Se hai bisogno che le voci in altre lingue siano ufficialmente
aggiunto all'elenco, ti preghiamo di contattarci e li aggiungeremo dopo averlo esaminato.

## Modelli TTS ottimizzati (fine-tuned)
#### Ottimizza il tuo modello TTS

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Rimuovere il rumore dai dati di addestramento

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Collezione di modelli TTS ottimizzati

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Per un modello personalizzato XTTSv2 è obbligatorio un clip audio di riferimento della voce:

## La tua personalizzazione di Ebook2Audiobook
Sei libero di modificare libs/conf.py per aggiungere o rimuovere le impostazioni che desideri. Se intendi farlo, crea semplicemente
una copia del conf.py originale così che, a ogni aggiornamento di ebook2audiobook, tu possa salvare il tuo conf.py modificato e ripristinare
quello originale. Devi pianificare lo stesso processo per models.py. Se desideri rendere il tuo modello personalizzato
un modello ottimizzato ufficiale di ebook2audiobook, contattaci e lo aggiungeremo all'elenco dei preset.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Problemi comuni:
- La mia GPU NVIDIA/ROCm/XPU/MPS non viene rilevata?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  La CPU è lenta (meglio su una CPU SMP da server) mentre la GPU può ottenere una conversione quasi in tempo reale.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Non ha però la clonazione vocale zero-shot, e le voci sono di qualità Siri, ma è molto più veloce su CPU).
- «Ho problemi di dipendenze» - Usa semplicemente Docker, è completamente autonomo e ha una modalità headless,
   aggiungi il parametro  alla fine del comando docker run per maggiori informazioni. `--help`
- «Ho un problema di audio troncato!» - PER FAVORE APRI UN ISSUE A RIGUARDO,
   non parliamo tutte le lingue e abbiamo bisogno dei consigli degli utenti per perfezionare la logica di divisione delle frasi.😊

## Roadmap
- Tutte le funzionalità aperte ai contributi pubblici ⭐
- Qualsiasi aiuto da parte di persone che parlano una delle lingue supportate per aiutarci a migliorare i modelli ⭐
- [x] Anteprima di blocchi/capitoli prima di avviare la conversione
- [x] Modifica per frase convertita per un cambiamento chirurgico del testo
- [x] Genera intro, interludi e finali musicali; modifica interludi e finali
- [x] Integrazione dei tag SML per voce, pausa, interruzione e altre modifiche
- [x] Informazioni sui parametri -h -help in diverse lingue
- [x] Scansione OCR per PDF / JPG / BMP / PNG / TIFF
- [x] Cartella dei notebook [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Fare in modo che la divisione del testo cinese non spezzi le parole e migliorare la sincronizzazione delle pause [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compone
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [x] Integrazione con Audiobookshelf
- [x] Opzione di traduzione dell'e-book
- [x] Scelte del formato di output
- [x] Conversione con multiprocessing
- [x] Conversione in batch di una cartella di e-book
- [x] Rilevamento del dispositivo GPU
- [x] Denoise any background reference audio for voice cloning upload
- [x] Caricamento del modello personalizzato perfezionato
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Richieste degli utenti
- [ ] Aggiungere un modello linguistico portoghese europeo almeno per xttsv2, fairseq, vits, piper (aiuto benvenuto)
- [ ] Aggiungere un modello linguistico sindhi almeno per xttsv2, fairseq, vits, piper (aiuto benvenuto)

#### Motori TTS
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Fish-speech / Fish Audio (https://github.com/fishaudio/fish-speech)[cite: 1]
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
- [x] Indice-tts / Indice TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Confucio 4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Puntini TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Locale / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Tasca TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Fonone al Gradio (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotrone2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Tartaruga (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zoni (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Corteccia (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Traduzione del Readme
- [x] Arabo (ara)
- [x] Cinese (zho)
- [x] Inglese (ENG)
- [x] Spagnolo (spa)
- [x] Francese (fra)
- [x] Tedesco (deu)
- [x] Italiano (ita)
- [x] Portoghese (POR)
- [x] Polacco (pol)
- [x] Turco (tur)
- [x] Russo (rus)
- [x] Olandese (nld)
- [x] Ceco (ces)
- [x] Giapponese (jpn)
- [x] Hindi (hin)
- [x] Bengalese (ben)
- [x] Ungherese (hun)
- [x] Coreano (kor)
- [x] Vietnamita (vie)
- [x] Svedese (swe)
- [x] Persiano (fas)
- [x] Yoruba (yor)
- [x] Swahili (swa)
- [x] Indonesiano (ind)
- [x] Slovacco (slk)
- [x] Croato (hrv)

#### Compatibilità del sistema operativo
- [x] 🪟 Windows x86
- [x] Finestre 🪟 ARM
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

## Extra esagerato per addestrare modelli e simili (tutti i modelli Coqui-tts supportati e piper-tts in un unico semplice comando) 
- Per informazioni su questo @ DrewThomasson, sta attualmente lavorando allo sviluppo di questo, [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Crea una guida di formazione facile da usare per tutti i modelli coqui-tts nel [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) Completed at [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## Informazioni sulla normalizzazione del codice Python per i contributori
- nessuna riga vuota tra il codice, tranne tra funzioni e classi.
- apice singolo usato per tutte le chiavi tranne che per dict() e json. dict['key'] sempre richiamato con apice singolo
- indentazione di 4 spazi, nessuna tabulazione
- tipizzazione rigorosa per tutte le funzioni e per la dichiarazione dei loro argomenti e valori di ritorno
- nessuno spazio tra l'argomento e la sua tipizzazione, nessuno spazio tra la funzione, il «->» e il valore di ritorno

Esempio:

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

## Cercasi donazione di hardware per i beta test
Accettiamo qualsiasi tipo di hardware per testare il nostro sviluppo, come:
- Nvidia Supporting cuda >= 11,8
- Schede intel XPU
- Schede ROCm AMD che supportano ROCm >=5,7

@DrewThomasson se vuoi dare una mano in qualsiasi modo! 😃
<!--
## Hai bisogno di noleggiare una GPU per potenziare il nostro servizio?
- È aperto un sondaggio qui https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Crediti
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- A deep learning toolkit for Text-to-Speech, battle-tested in research and production.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Motore di sintesi vocale neurale veloce e locale.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- codice di inferenza ggml per Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) - Un motore di inferenza C++ all-in-one e puro per modelli audio, alimentato da ggml.

## Ringraziamenti speciali
>>>>>>> b9c7b9f1ac1b8217f97de7a9192b7291ec770fcd
A tutti i contributori finanziari e di codice, ogni contributo e suggerimento aiuta a migliorare la qualità di E2A.