# 📚 ebook2audiobook (E2A)
Convertitore CPU/GPU da e-book ad audiolibro con capitoli e metadati<br/>
utilizzando motori TTS avanzati e molto altro.<br/>
Supporta la clonazione vocale e 1158 lingue!
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
- [Funzionalità](#features)
- [Interfaccia grafica](#gui-interface)
- [Demo](#demos)
- [Lingue supportate](#supported-languages)
- [Requisiti minimi](#hardware-requirements)
- [Utilizzo](#instructions)
  - [Esecuzione locale](#instructions)
    - [Avvio dell'interfaccia web Gradio](#instructions)
    - [Utilizzo di base in modalità headless](#basic-usage)
    - [Utilizzo di un modello XTTS personalizzato in modalità headless](#example-of-custom-model-zip-upload)
    - [Output del comando di aiuto](#help-command-output)
  - [Esecuzione da remoto](#run-remotely)
  - [Docker](#docker)
    - [Passaggi per l'esecuzione](#docker)
  
- [Cloned Voices](#cloned-voices)
- [Modelli TTS ottimizzati](#fine-tuned-tts-models)
  - [Collezione di modelli TTS ottimizzati](#fine-tuned-tts-collection)
  - [Addestrare XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Formati di e-book supportati](#supported-ebook-formats)
- [Formati di output](#output-and-process-formats)
- [Tornare a una versione precedente](#reverting-to-older-versions)
- [Problemi comuni](#common-issues)
- [Ringraziamenti speciali](#special-thanks)
- [Indice](#table-of-contents)


## Funzionalità
- 🔧 **Motori TTS supportati**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Convertire più formati di file**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Area di testo** per convertire direttamente un breve testo in audio
- 🔍 **Scansione OCR** per file con pagine di testo sotto forma di immagini
- 🔊 **Sintesi vocale di alta qualità**, dal quasi tempo reale a una voce quasi reale
- 🗣️ **Clonazione vocale opzionale** utilizzando il tuo file vocale
- 🌐 **Supporta 1158 lingue** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
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
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> I moderni motori TTS sono molto lenti su CPU, quindi usa TTS di qualità inferiore come YourTTS, Tacotron2 ecc.</i>

## Lingue supportate
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 lingue e dialetti qui**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


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

**Dai un'occhiata al nostro altro repo dedicato all'aggiunta automatica di SML nel tuo e-book -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Prima di pubblicare un problema di installazione o un bug, cerca attentamente nella scheda dei problemi aperti e chiusi<br>
per essere sicuro che il tuo problema non esista già.**

>[!NOTE]
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

## Voci clonate
È possibile caricare qualsiasi audio vocale in uno qualsiasi dei formati audio supportati, la durata ideale è di circa 1-5 minuti.
Non importa se la registrazione ha uno sfondo rumoroso o se la musica viene riprodotta su di essa: E2A ripulirà la voce per te.

L'elenco delle voci clonate integrate è principalmente in inglese. Se hai bisogno che le voci in altre lingue siano ufficialmente
aggiunto all'elenco, ti preghiamo di contattarci e li aggiungeremo dopo averlo esaminato.

## Modelli TTS ottimizzati (fine-tuned)
#### Ottimizza il tuo modello XTTSv2

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


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
   aggiungi il parametro `--help` alla fine del comando docker run per maggiori informazioni.
- «Ho un problema di audio troncato!» - PER FAVORE APRI UN ISSUE A RIGUARDO,
   non parliamo tutte le lingue e abbiamo bisogno dei consigli degli utenti per perfezionare la logica di divisione delle frasi.😊

## ***** ROADMAP *****
- Tutte le funzionalità aperte ai contributi pubblici ⭐
- Qualsiasi aiuto da parte di persone che parlano una delle lingue supportate per aiutarci a migliorare i modelli ⭐
- [x] Anteprima di blocchi/capitoli prima di avviare la conversione
- [ ] Modifica per frase convertita per un cambiamento chirurgico del testo
- [x] Integrazione dei tag SML per voce, pausa, interruzione e altre modifiche 
- [x] Informazioni sui parametri -h -help in diverse lingue
- [x] Scansione OCR per PDF / JPG / BMP / PNG / TIFF
- [x] Cartella dei notebook [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Fare in modo che la divisione del testo cinese non spezzi le parole e migliorare la sincronizzazione delle pause [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] Integrazione con Audiobookshelf
- [ ] [Creare un'app per iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Creare un'app per Android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Opzioni aggiuntive
- [x] Opzione di traduzione dell'e-book
- [x] Scelte del formato di output
- [x] Cartella di e-book in batch
- [x] Conversione con multiprocessing
- [x] Conversione in batch di una cartella di e-book
- [x] Rilevamento del dispositivo GPU
- [x] Rimuovere il rumore da qualsiasi audio di riferimento per la clonazione vocale caricata,
- [x] Caricamento di modello personalizzato (solo XTTSv2 per ora. altri su richiesta)
- [ ] Aggiungere un modello linguistico portoghese europeo almeno per xttsv2, fairseq, vits, piper (aiuto benvenuto)
- [ ] Aggiungere un modello linguistico sindhi almeno per xttsv2, fairseq, vits, piper (aiuto benvenuto)

#### Motori TTS
- [x] XTTSv2
- [x] Corteccia
- [x] Fairseq
- [x] VITS
- [x] Tacotrone2
- [x] YourTTS
- [x] Testuggine
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fish-speech (https://github.com/fishaudio/fish-speech)
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
- [ ] Zoni (https://github.com/Zyphra/Zonos)
- [ ] Style-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Traduzione del Readme
- [ ] Arabo (ara)
- [ ] Cinese (zho)
- [x] English (eng)
- [ ] Spagnolo (spa)
- [ ] Francese (fra)
- [ ] Tedesco (deu)
- [ ] Italiano (ita)
- [ ] Portoghese (POR)
- [ ] Polacco (pol)
- [ ] Turco (tur)
- [ ] Russo (rus)
- [ ] Olandese (nld)
- [ ] Ceco (ces)
- [ ] Giapponese (jpn)
- [ ] Hindi (hin)
- [ ] Bengalese (ben)
- [ ] Ungherese (hun)
- [ ] Coreano (kor)
- [ ] Vietnamita (vie)
- [ ] Svedese (swe)
- [ ] Persiano (fas)
- [ ] Yoruba (yor)
- [ ] Swahili (swa)
- [ ] Indonesiano (ind)
- [ ] Slovacco (slk)
- [ ] Croato (hrv)

#### 🐍 Compatibilità con i sistemi operativi
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra esagerato per addestrare modelli e simili (tutti i modelli Coqui-tts supportati e piper-tts in un unico semplice comando) 
- Per informazioni a riguardo @DrewThomasson, attualmente sta lavorando al suo sviluppo, [repo work-in-progress qui](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Creare una GUI di addestramento facile da usare per tutti i modelli coqui-tts nelle ricette di addestramento in formato ljspeech [qui da coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


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
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson se vuoi dare una mano in qualsiasi modo! 😃
<!--
## Hai bisogno di noleggiare una GPU per potenziare il nostro servizio?
- È aperto un sondaggio qui https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Ringraziamenti speciali
A tutti i contributori finanziari e di codice, ogni contributo e suggerimento aiuta a migliorare la qualità di E2A.