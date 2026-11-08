<<<<<<< HEAD
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

CPU/GPU-Konverter von E-Book zu Hörbuch mit Kapiteln und Metadaten<br/>
unter Verwendung fortschrittlicher TTS-Engines und vielem mehr.<br/>
Unterstützt Sprachklonen und 1696 Sprachen!
> [!IMPORTANT]
**Dieses Tool ist ausschließlich für die Verwendung mit DRM-freien, legal erworbenen E-Books bestimmt.** <br>
Die Autoren übernehmen keine Verantwortung für jeglichen Missbrauch dieser Software oder daraus resultierende rechtliche Folgen. <br>
Verwenden Sie dieses Tool verantwortungsvoll und in Übereinstimmung mit allen geltenden Gesetzen.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Danke, dass Sie die Entwickler von ebook2audiobook unterstützen!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Lokal ausführen

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Remote ausführen
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### GUI-Oberfläche
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Zum Anzeigen von Bildern der Web-GUI klicken</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demos

**Demo der neuen Standardstimme**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Weitere Demos</summary>

**ASMR-Stimme** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Regentag-Stimme**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett-Stimme**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David-Attenborough-Stimme** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Beispiel**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Inhaltsverzeichnis
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


## Funktionen
- 🔧 ** Unterstützte TTS Engines **: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Mehrere Dateiformate konvertieren**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Textbereich** zum direkten Umwandeln eines kurzen Texts in Audio
- 🔍 **OCR-Erkennung** für Dateien mit Textseiten als Bilder
- 🔊 **Hochwertige Sprachausgabe**, von nahezu Echtzeit bis zu nahezu echter Stimme
- 🗣️ **Optionales Stimmenklonen** mit Ihrer eigenen Sprachdatei
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Ressourcenschonend** — läuft mit **2 GB RAM / 1 GB VRAM (Minimum)**
- 🎵 **Hörbuch-Ausgabeformate**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML-Tags unterstützt** — feingranulare Steuerung von Unterbrechungen, Pausen, Stimmwechsel und mehr ([see below](#sml-tags-available))
- 🧩 **Optionales benutzerdefiniertes Modell** mit Ihrem eigenen trainierten Modell (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Feinabgestimmte Preset-Modelle**, trainiert vom E2A-Team<br/>
     <i>(Kontaktieren Sie uns, wenn Sie zusätzliche feinabgestimmte Modelle benötigen oder Ihre eigenen zur offiziellen Preset-Liste beitragen möchten)</i>


##  Hardware-Anforderungen
- 2 GB RAM min., 8 GB empfohlen.
- 1 GB VRAM min., 4 GB empfohlen.
- Virtualisierung aktiviert, falls unter Windows ausgeführt (nur Docker).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple-Silicon-CPU)

*<i> Moderne TTS-Engines sind auf der CPU sehr langsam, verwenden Sie daher TTS geringerer Qualität wie YourTTS, Tacotron2 usw.</i>

## Unterstützte Sprachen
| **Arabisch (ar)**    | **Chinesisch (zh)**    | **Englisch (en)**   | **Spanisch (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **Französisch (fr)**    | **Deutsch (de)**     | **Italienisch (it)**   | **Portugiesisch (pt)** |
| **Polnisch (pl)**    | **Türkisch (tr)**    | **Russisch (ru)**   | **Niederländisch (nl)**     |
| **Tschechisch (cs)**     | **Japanisch (ja)**   | **Hindi (hi)**     | **Bengalisch (bn)**   |
| **Ungarisch (hu)** | **Koreanisch (ko)**     | **Vietnamesisch (vi)**| **Schwedisch (sv)**   |
| **Persisch (fa)**   | **Yoruba (yo)**     | **Suaheli (sw)**   | **Indonesisch (id)**|
| **Slowakisch (sk)**    | **Kroatisch (hr)**   | **Tamilisch (ta)**     | **Dänisch (da)**    |
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Unterstützte E-Book-Formate
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Beste Ergebnisse**: `.epub` oder `.mobi` für die automatische Kapitelerkennung

## Ausgabe- und Verarbeitungsformate
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Das Verarbeitungsformat kann in lib/conf.py geändert werden

## Verfügbare SML-Tags
- `[break]` — Stille (zufälliger Bereich **0.3–0.6 sec.**)
- `[pause]` — Stille (zufälliger Bereich **1.0–1.6 sec.**)
- `[pause:N]` — feste Pause (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — Stimme von der Standard- oder in der GUI/CLI ausgewählten Stimme wechseln
- `[emotion:sadness]...[/emotion]` — Nur Zonos: Emotion für eine Passage (Glück, Traurigkeit, Ekel, Angst, Überraschung, Wut, andere, neutral) oder eine Mischung wie `[emotion:sadness=0.7,neutral=0.3]`; andere Motoren ignorieren es

**Sehen Sie sich unser anderes Repo an, das dem automatischen Hinzufügen von SML in Ihrem E-Book gewidmet ist -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Bevor Sie ein Installations- oder Fehlerproblem melden, durchsuchen Sie sorgfältig den Tab mit offenen und geschlossenen Issues<br>
um sicherzustellen, dass Ihr Problem nicht bereits existiert.**

 HINWEIS
**Dem EPUB-Format fehlt jegliche Standardstruktur, die festlegt, was ein Kapitel, ein Absatz, ein Vorwort usw. ist.<br>
Daher sollten Sie zunächst manuell jeglichen Text entfernen, den Sie nicht in Audio umwandeln möchten.**


### Anleitung
1. ** Repo klonen **
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook installieren / ausführen**:

   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Hinweis für MacOS-Benutzer: homebrew ist installiert, um fehlende Programme zu installieren.</i>
     
   - **Mac-Launcher**  
     Doppelklicken Sie auf `Mac Ebook2Audiobook Launcher.command`


   - FENSTER
     ```bash
     ebook2audiobook.cmd
     ```
     oder
     Doppelklick `ebook2audiobook.cmd`

     <i>Hinweis für Windows-Nutzer: scoop wird installiert, um fehlende Programme ohne Administratorrechte zu installieren.</i>
   
1. **Web-App öffnen**: Klicken Sie auf die im Terminal angegebene URL, um auf die Web-App zuzugreifen und E-Books zu konvertieren. `http://localhost:7860/`
2. **Für einen öffentlichen Link**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (alle Betriebssysteme)

> [!IMPORTANT]
**Wenn das Skript gestoppt und erneut ausgeführt wird, müssen Sie Ihre Gradio-GUI-Oberfläche aktualisieren<br>
damit sich die Webseite mit dem neuen Verbindungs-Socket verbinden kann.**

### Grundlagen
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - FENSTER
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Pfad zu Ihrer E-Book-Datei
  - **[--voice]**: Pfad zur Datei für das Stimmenklonen (optional)
  - **[--language]**: Sprachcode in ISO-639-3 (d. h.: ita für Italienisch, eng für Englisch, deu für Deutsch...).<br>
    Die Standardsprache ist eng und --language ist optional für die in ./lib/lang.py festgelegte Standardsprache.<br>
    Die zweistelligen ISO-639-1-Codes werden ebenfalls unterstützt.


###  Beispiel für benutzerdefiniertes Modell Zip-Upload
  (muss eine .zip-Datei sein, die die obligatorischen Modelldateien enthält. Beispiel für XTTSv2: config.json, model.pth, vocab.json und ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - FENSTER
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Hinweis: Die ref.wav Ihres benutzerdefinierten Modells ist immer die für die Konvertierung ausgewählte Stimme</i>
     
- **<custom_model_path>**: Pfad zur Datei `model_name.zip`,
      die (je nach TTS-Engine) alle erforderlichen Dateien enthalten muss<br>
      (siehe ./lib/models.py).

### Für eine detaillierte Anleitung mit einer Liste aller zu verwendenden Parameter
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - FENSTER
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Oder für alle Betriebssysteme**
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

HINWEIS: Um im gradio/gui-Modus eine laufende Konvertierung abzubrechen, klicken Sie einfach auf das [X] der E-Book-Upload-Komponente.
TIPP: Wenn etwas mehr Pause nötig ist, fügen Sie '[pause:3]' für 3 Sek. usw. hinzu.

### Docker
1. ** Das Repository klonen **:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Baue den Container**
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
4. **Führen Sie den Container aus:**
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
- HINWEIS: MPS ist in Docker nicht exponiert, daher muss eine CPU verwendet werden
- HINWEIS: Der genannte Band `e2a_venvs` hält die TTS-Motoren in ihrem eigenen Venv installiert (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM usw.)
  über Containerläufe hinweg, so dass sie nicht jedes Mal neu installiert werden. So setzen Sie sie zurück: `docker volume rm e2a_venvs`

## Werkzeuge
Eigenständige Tools, die mit e2as eigenem Python ausgeführt werden (`python_env`, erstellt durch den ersten Start von e2a).

<a id="preload-models"></a>
### Vorlademodelle für Offline-Installationen: `tools/preload_models.py`
Lädt jedes Modell herunter, das e2a verwendet (TTS-Engines und deren Feinabstimmung, Sprachkonvertierung, Strophe, Pyannote, Demucs,
musikeinlagen, Argos-Übersetzungspakete, Tesseraktdaten, Jieba und die Stimmen) in einem Ordner angeordnet
genau wie `./models`, also ein USB-Stick. Kopieren Sie diesen Ordner auf dem Offline-Computer in e2as `./models`
und den daneben geschriebenen⟧ Ordner ⟦0 in e2a's ⟦⟧1. `voices` `./voices`
Jeder abgeschlossene Job wird in ⟦0 aufgezeichnet⟧: Eine Wiederholung überspringt, was getan wird, und startet `<models_dir>/.e2a_downloads.json`
wieder, was nach dem Entfernen seiner Teildateien abgeschnitten wurde (Strg-C, Crash, Unplugged Key).
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - FENSTER
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` listet die Jobs und ihren Status (erledigt, unterbrochen, ToDo) auf, ohne etwas herunterzuladen.

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
### E-Books aus e2a übersetzen: `translate_ebook.sh`/`translate_ebook.cmd`
Übersetzt EPUB/AZW3-Dateien, einen ganzen Ordner (`-r` für seine Unterordner) oder eine Liste von Pfaden (`@list.txt`)
in übersetzte E-Books, offline, mit dem Argos Translate-Kaliber-Plugin, das im
`tools/argostranslate-calibre-plugin.zip`. Unabhängig von der Hörbuchkonvertierung: Es schreibt nur E-Books.
Es benötigt Kaliber (bereits von e2a benötigt) und läuft auf ⟦e2as 0-⟧ und argos-translate-Paketen: `python_env`
ein bereits verwendetes Sprachpaar e2a wird nicht erneut heruntergeladen, ein fehlendes wird bei der ersten Verwendung heruntergeladen.
Das Plugin wird bei der ersten Verwendung in das e2a-eigene Kaliberprofil (`./run`) installiert, Ihr Kaliber bleibt unberührt.
`--to fra,ara,spa` übersetzt in mehrere Sprachen gleichzeitig, ein E-Book pro Sprache und `--to all` in jede
sprache, die die Quelle erreicht (`--from`, sonst die eigene Sprache jedes Buches; installierte nur mit `--no_download`).
`--list --from eng` listet die Sprachen auf, in die Englisch übersetzt (installiert, herunterladbar oder über Englisch für
eine andere Quelle).
Andere Formate, die das Kaliber `ebook-convert` liest (PDF, DOCX, MOBI, TXT, ...), werden einmal in EPUB konvertiert, bevor die
muttersprache und⟧ wird als EPUB: ⟦0 übersetzt, wenn sie keine Sprache tragen, wie es PDF und TXT oft tun. `--from`
Ohne `-o` oder `--output_dir` wird jede Übersetzung neben ihrem Buch als ⟦2 gespeichert⟧, `<name>.<lang>.<ext>`
und ein Buch, dessen Übersetzung bereits vorhanden ist, wird übersprungen (`--overwrite`, um es erneut zu übersetzen).
Die Trägerraketen im Ordner von e2a laufen `tools/translate_ebook.py` mit `python_env`, nichts zu aktivieren,
aus einem beliebigen Ordner (relative Pfade werden vom Startort übernommen):
   - **Linux/MacOS**
     ```bash
     ./translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - FENSTER
     ```bash
     translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Oder direkt mit `python_env`'s Python: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Begonnen mit jedem anderen Python,
     beginnt sich das Skript erneut mit ⟦⟧0. `python_env`
   - **Docker**: innerhalb des e2a-Containers ausführen, z.B. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     mit Pfaden vom Container aus gesehen.
   - **Geschwindigkeit**: argostranslate läuft auf eigenen Standardeinstellungen (CTranslate2 wählt die Threads und den schnellsten Berechnungstyp aus,
     int8 auf der CPU), nicht auf dem 1-Thread von e2a in float32. Setzen Sie `ARGOS_INTRA_THREADS` oder `ARGOS_COMPUTE_TYPE`, um sie zu überschreiben.

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

## Geklonte Stimmen
Sie können jedes Sprachaudio in jedem der unterstützten Audioformate hochladen. Die ideale Dauer beträgt etwa 1 bis 5 Minuten.
Es spielt keine Rolle, ob die Aufnahme einen lauten Hintergrund hat oder Musik darüber abgespielt wird — E2A wird die Stimme für Sie aufräumen.

Die eingebaute Liste der geklonten Stimmen ist hauptsächlich auf Englisch. Wenn Sie Stimmen in anderen Sprachen benötigen, um offiziell
der Liste hinzugefügt, kontaktieren Sie uns bitte und wir werden sie nach der Überprüfung hinzufügen.

## Feinabgestimmte (fine-tuned) TTS-Modelle
#### Feinabstimmung Ihres eigenen TTS-Modells

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Trainingsdaten entrauschen

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Sammlung feinabgestimmter TTS-Modelle

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Für ein benutzerdefiniertes XTTSv2-Modell ist ein Referenz-Audioclip der Stimme zwingend erforderlich:

## Ihre eigene Ebook2Audiobook-Anpassung
Es steht Ihnen frei, libs/conf.py zu ändern, um die gewünschten Einstellungen hinzuzufügen oder zu entfernen. Falls Sie dies vorhaben, erstellen Sie einfach
eine Kopie der ursprünglichen conf.py, damit Sie bei jedem ebook2audiobook-Update Ihre geänderte conf.py sichern und
die Originaldatei wiederherstellen können. Sie müssen denselben Vorgang für models.py einplanen. Wenn Sie Ihr eigenes benutzerdefiniertes Modell
zu einem offiziellen, feinabgestimmten ebook2audiobook-Modell machen möchten, kontaktieren Sie uns bitte, und wir fügen es der Preset-Liste hinzu.

## Zurücksetzen auf ältere Versionen
Freigaben sind zu finden -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Häufige Probleme:
- Meine NVIDIA-/ROCm-/XPU-/MPS-GPU wird nicht erkannt?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  Die CPU ist langsam (besser auf einer Server-SMP-CPU), während die GPU eine nahezu Echtzeit-Konvertierung erreichen kann.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Es hat allerdings kein Zero-Shot-Stimmenklonen und bietet Stimmen in Siri-Qualität, ist aber auf der CPU deutlich schneller).
- „Ich habe Abhängigkeitsprobleme“ - Verwenden Sie einfach Docker, es ist vollständig eigenständig und hat einen Headless-Modus,
   fügen Sie für weitere Informationen den Parameter  am Ende des docker-run-Befehls hinzu. `--help`
- „Ich habe ein Problem mit abgeschnittenem Audio!“ - BITTE ERSTELLEN SIE DAZU EIN ISSUE,
   wir sprechen nicht jede Sprache und benötigen den Rat der Nutzer, um die Logik der Satztrennung zu verfeinern.😊

## Fahrplan
- Alle Funktionen offen für öffentliche Beiträge ⭐
- Jede Hilfe von Personen, die eine der unterstützten Sprachen sprechen, um uns bei der Verbesserung der Modelle zu helfen ⭐
- [x] Blöcke/Kapitel vor dem Start der Konvertierung in der Vorschau anzeigen
- [x] Bearbeitung nach konvertiertem Satz für chirurgisch genaue Textänderungen
- [x] Musik-Intros, -Zwischenspiele und -Enden generieren; Zwischenspiele und -Enden bearbeiten
- [x] SML-Tag-Integration für Stimme, Pause, Unterbrechung und weitere Änderungen
- [x] Informationen zu den Parametern -h -help in verschiedenen Sprachen
- [x] OCR-Erkennung für PDF / JPG / BMP / PNG / TIFF
- [x] Notebooks-Ordner [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Die chinesische Textaufteilung so gestalten, dass keine Wörter getrennt werden, und das Pausen-Timing verbessern [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker komponieren
- [x] Podman komponieren
- [x] Kaggle-Notebook
- [x] Google-Colab-Notebook
- [x] Audiobookshelf-Integration
- [x] Option zur E-Book-Übersetzung
- [x] Auswahl des Ausgabeformats
- [x] Konvertierung mit Multiprocessing
- [x] Stapelkonvertierung eines E-Book-Ordners
- [x] GPU-Geräteerkennung
- [x] Hintergrundreferenzaudio für das Hochladen von Sprachklonen entrauschen
- [x] Benutzerdefinierter, fein abgestimmter Modell-Upload
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Benutzer Anfragen
- [ ] Ein europäisch-portugiesisches Sprachmodell für mindestens xttsv2, fairseq, vits, piper hinzufügen (Hilfe willkommen)
- [ ] Ein Sindhi-Sprachmodell für mindestens xttsv2, fairseq, vits, piper hinzufügen (Hilfe willkommen)

#### TTS-Motoren
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Fisch-Sprache / Fisch-Audio (https://github.com/fishaudio/fish-speech)[cite: 1]
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
- [x] Konfuzius4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Dots TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Elster TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
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
- [x] Schildkröte (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Rinde (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Readme-Übersetzung
- [x] Arabisch (ara)
- [x] Chinesisch (zho)
- [x]            Englisch (eng)
- [x] Spanisch (Spa)
- [x] Französisch (fra)
- [x] Deutsch (deu)
- [x] Italienisch (ita)
- [x] Portugiesisch (por)
- [x] Polnisch (pol)
- [x] Türkisch (tur)
- [x] Russisch (rus)
- [x] Niederländisch (nld)
- [x] Tschechisch (ces)
- [x] Japanisch (jpn)
- [x] Hindi (hin)
- [x] Bengalisch (ben)
- [x] Ungarisch (hun)
- [x] Koreanisch (kor)
- [x] Vietnamesisch (Vie)
- [x] Schwedisch (swe)
- [x] Persisch (fas)
- [x] Yoruba (yor)
- [x] Swahili (swa)
- [x] Indonesisch (ind)
- [x] Slowakisch (slk)
- [x] Kroatisch (hrv)

#### Betriebssystem Kompatibilität
- [x] 🪟 Windows x86
- [x] 🪟 Arm-Fenster
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] Linux on IA-32 (for Intel x86)
- [x] 🐧 ARM LINUX

**********

## Extra-Overkill für das Trainieren von Modellen und Ähnliches (alle unterstützten Coqui-tts-Modelle und piper-tts in einem einzigen einfachen Befehl) 
- Zur Information darüber @DrewThomasson, er arbeitet derzeit an der Entwicklung dieses, [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Make a easy to use training gui for all coqui-tts models in the [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) Completed at [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## Informationen zur Python-Code-Normalisierung für Mitwirkende
- keine Leerzeile zwischen dem Code, außer zwischen Funktionen und Klassen.
- einfaches Anführungszeichen für alle Schlüssel, außer bei dict() und json. dict['key'] wird immer mit einfachem Anführungszeichen aufgerufen
- 4 Leerzeichen Einrückung, überhaupt kein Tab
- strikte Typisierung für alle Funktionen sowie die Deklaration ihrer Argumente und Rückgabewerte
- kein Leerzeichen zwischen dem Argument und seiner Typisierung, kein Leerzeichen zwischen der Funktion, dem „->“ und dem Rückgabewert

Beispiel:

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

## Hardware-Spende für Beta-Tests gesucht
Wir nehmen jede Art von Hardware an, um unsere Entwicklung zu testen, wie zum Beispiel:
- Nvidia unterstützt Cuda >= 11,8
- XPU-Intel-Karten
- ROCm AMD-Karten, die ROCm >=5,7 unterstützen

@DrewThomasson, falls Sie auf irgendeine Weise mithelfen möchten! 😃
<!--
## Müssen Sie eine GPU mieten, um unseren Service zu beschleunigen?
- Eine Umfrage ist hier offen https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Credits
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- Ein Deep-Learning-Toolkit für Text-to-Speech, kampferprobt in Forschung und Produktion.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Schnelle und lokale neuronale Text-zu-Sprache-Engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml-Inferenzcode für Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- Eine All-in-One, reine C++ Inferenz-Engine für Audiomodelle, angetrieben von ggml.

## Besonderer Dank
=======
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

CPU/GPU-Konverter von E-Book zu Hörbuch mit Kapiteln und Metadaten<br/>
unter Verwendung fortschrittlicher TTS-Engines und vielem mehr.<br/>
Unterstützt Sprachklonen und 1696 Sprachen!
> [!IMPORTANT]
**Dieses Tool ist ausschließlich für die Verwendung mit DRM-freien, legal erworbenen E-Books bestimmt.** <br>
Die Autoren übernehmen keine Verantwortung für jeglichen Missbrauch dieser Software oder daraus resultierende rechtliche Folgen. <br>
Verwenden Sie dieses Tool verantwortungsvoll und in Übereinstimmung mit allen geltenden Gesetzen.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Danke, dass Sie die Entwickler von ebook2audiobook unterstützen!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Lokal ausführen

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Remote ausführen
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### GUI-Oberfläche
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Zum Anzeigen von Bildern der Web-GUI klicken</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demos

**Demo der neuen Standardstimme**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Weitere Demos</summary>

**ASMR-Stimme** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Regentag-Stimme**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett-Stimme**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David-Attenborough-Stimme** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Beispiel**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Inhaltsverzeichnis
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


## Funktionen
- 🔧 ** Unterstützte TTS Engines **: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Mehrere Dateiformate konvertieren**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Textbereich** zum direkten Umwandeln eines kurzen Texts in Audio
- 🔍 **OCR-Erkennung** für Dateien mit Textseiten als Bilder
- 🔊 **Hochwertige Sprachausgabe**, von nahezu Echtzeit bis zu nahezu echter Stimme
- 🗣️ **Optionales Stimmenklonen** mit Ihrer eigenen Sprachdatei
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Ressourcenschonend** — läuft mit **2 GB RAM / 1 GB VRAM (Minimum)**
- 🎵 **Hörbuch-Ausgabeformate**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML-Tags unterstützt** — feingranulare Steuerung von Unterbrechungen, Pausen, Stimmwechsel und mehr ([see below](#sml-tags-available))
- 🧩 **Optionales benutzerdefiniertes Modell** mit Ihrem eigenen trainierten Modell (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Feinabgestimmte Preset-Modelle**, trainiert vom E2A-Team<br/>
     <i>(Kontaktieren Sie uns, wenn Sie zusätzliche feinabgestimmte Modelle benötigen oder Ihre eigenen zur offiziellen Preset-Liste beitragen möchten)</i>


##  Hardware-Anforderungen
- 2 GB RAM min., 8 GB empfohlen.
- 1 GB VRAM min., 4 GB empfohlen.
- Virtualisierung aktiviert, falls unter Windows ausgeführt (nur Docker).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple-Silicon-CPU)

*<i> Moderne TTS-Engines sind auf der CPU sehr langsam, verwenden Sie daher TTS geringerer Qualität wie YourTTS, Tacotron2 usw.</i>

## Unterstützte Sprachen
| **Arabisch (ar)**    | **Chinesisch (zh)**    | **Englisch (en)**   | **Spanisch (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **Französisch (fr)**    | **Deutsch (de)**     | **Italienisch (it)**   | **Portugiesisch (pt)** |
| **Polnisch (pl)**    | **Türkisch (tr)**    | **Russisch (ru)**   | **Niederländisch (nl)**     |
| **Tschechisch (cs)**     | **Japanisch (ja)**   | **Hindi (hi)**     | **Bengalisch (bn)**   |
| **Ungarisch (hu)** | **Koreanisch (ko)**     | **Vietnamesisch (vi)**| **Schwedisch (sv)**   |
| **Persisch (fa)**   | **Yoruba (yo)**     | **Suaheli (sw)**   | **Indonesisch (id)**|
| **Slowakisch (sk)**    | **Kroatisch (hr)**   | **Tamilisch (ta)**     | **Dänisch (da)**    |
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Unterstützte E-Book-Formate
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Beste Ergebnisse**: `.epub` oder `.mobi` für die automatische Kapitelerkennung

## Ausgabe- und Verarbeitungsformate
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Das Verarbeitungsformat kann in lib/conf.py geändert werden

## Verfügbare SML-Tags
- `[break]` — Stille (zufälliger Bereich **0.3–0.6 sec.**)
- `[pause]` — Stille (zufälliger Bereich **1.0–1.6 sec.**)
- `[pause:N]` — feste Pause (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — Stimme von der Standard- oder in der GUI/CLI ausgewählten Stimme wechseln
- `[emotion:sadness]...[/emotion]` — Nur Zonos: Emotion für eine Passage (Glück, Traurigkeit, Ekel, Angst, Überraschung, Wut, andere, neutral) oder eine Mischung wie `[emotion:sadness=0.7,neutral=0.3]`; andere Motoren ignorieren es

**Sehen Sie sich unser anderes Repo an, das dem automatischen Hinzufügen von SML in Ihrem E-Book gewidmet ist -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Bevor Sie ein Installations- oder Fehlerproblem melden, durchsuchen Sie sorgfältig den Tab mit offenen und geschlossenen Issues<br>
um sicherzustellen, dass Ihr Problem nicht bereits existiert.**

 HINWEIS
**Dem EPUB-Format fehlt jegliche Standardstruktur, die festlegt, was ein Kapitel, ein Absatz, ein Vorwort usw. ist.<br>
Daher sollten Sie zunächst manuell jeglichen Text entfernen, den Sie nicht in Audio umwandeln möchten.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook installieren / ausführen**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac-Launcher**  
     Doppelklicken Sie auf `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Hinweis für Windows-Nutzer: scoop wird installiert, um fehlende Programme ohne Administratorrechte zu installieren.</i>
   
1. **Web-App öffnen**: Klicken Sie auf die im Terminal angegebene URL, um auf die Web-App zuzugreifen und E-Books zu konvertieren. `http://localhost:7860/`
2. **Für einen öffentlichen Link**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (alle Betriebssysteme)

> [!IMPORTANT]
**Wenn das Skript gestoppt und erneut ausgeführt wird, müssen Sie Ihre Gradio-GUI-Oberfläche aktualisieren<br>
damit sich die Webseite mit dem neuen Verbindungs-Socket verbinden kann.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Pfad zu Ihrer E-Book-Datei
  - **[--voice]**: Pfad zur Datei für das Stimmenklonen (optional)
  - **[--language]**: Sprachcode in ISO-639-3 (d. h.: ita für Italienisch, eng für Englisch, deu für Deutsch...).<br>
    Die Standardsprache ist eng und --language ist optional für die in ./lib/lang.py festgelegte Standardsprache.<br>
    Die zweistelligen ISO-639-1-Codes werden ebenfalls unterstützt.


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
     
- **<custom_model_path>**: Pfad zur Datei `model_name.zip`,
      die (je nach TTS-Engine) alle erforderlichen Dateien enthalten muss<br>
      (siehe ./lib/models.py).

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

HINWEIS: Um im gradio/gui-Modus eine laufende Konvertierung abzubrechen, klicken Sie einfach auf das [X] der E-Book-Upload-Komponente.
TIPP: Wenn etwas mehr Pause nötig ist, fügen Sie '[pause:3]' für 3 Sek. usw. hinzu.

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

## Werkzeuge
Eigenständige Tools, die mit e2as eigenem Python ausgeführt werden (`python_env`, erstellt durch den ersten Start von e2a).

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

## Geklonte Stimmen
Sie können jedes Sprachaudio in jedem der unterstützten Audioformate hochladen. Die ideale Dauer beträgt etwa 1 bis 5 Minuten.
Es spielt keine Rolle, ob die Aufnahme einen lauten Hintergrund hat oder Musik darüber abgespielt wird — E2A wird die Stimme für Sie aufräumen.

Die eingebaute Liste der geklonten Stimmen ist hauptsächlich auf Englisch. Wenn Sie Stimmen in anderen Sprachen benötigen, um offiziell
der Liste hinzugefügt, kontaktieren Sie uns bitte und wir werden sie nach der Überprüfung hinzufügen.

## Feinabgestimmte (fine-tuned) TTS-Modelle
#### Feinabstimmung Ihres eigenen TTS-Modells

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Trainingsdaten entrauschen

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Sammlung feinabgestimmter TTS-Modelle

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Für ein benutzerdefiniertes XTTSv2-Modell ist ein Referenz-Audioclip der Stimme zwingend erforderlich:

## Ihre eigene Ebook2Audiobook-Anpassung
Es steht Ihnen frei, libs/conf.py zu ändern, um die gewünschten Einstellungen hinzuzufügen oder zu entfernen. Falls Sie dies vorhaben, erstellen Sie einfach
eine Kopie der ursprünglichen conf.py, damit Sie bei jedem ebook2audiobook-Update Ihre geänderte conf.py sichern und
die Originaldatei wiederherstellen können. Sie müssen denselben Vorgang für models.py einplanen. Wenn Sie Ihr eigenes benutzerdefiniertes Modell
zu einem offiziellen, feinabgestimmten ebook2audiobook-Modell machen möchten, kontaktieren Sie uns bitte, und wir fügen es der Preset-Liste hinzu.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Häufige Probleme:
- Meine NVIDIA-/ROCm-/XPU-/MPS-GPU wird nicht erkannt?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  Die CPU ist langsam (besser auf einer Server-SMP-CPU), während die GPU eine nahezu Echtzeit-Konvertierung erreichen kann.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Es hat allerdings kein Zero-Shot-Stimmenklonen und bietet Stimmen in Siri-Qualität, ist aber auf der CPU deutlich schneller).
- „Ich habe Abhängigkeitsprobleme“ - Verwenden Sie einfach Docker, es ist vollständig eigenständig und hat einen Headless-Modus,
   fügen Sie für weitere Informationen den Parameter  am Ende des docker-run-Befehls hinzu. `--help`
- „Ich habe ein Problem mit abgeschnittenem Audio!“ - BITTE ERSTELLEN SIE DAZU EIN ISSUE,
   wir sprechen nicht jede Sprache und benötigen den Rat der Nutzer, um die Logik der Satztrennung zu verfeinern.😊

## Fahrplan
- Alle Funktionen offen für öffentliche Beiträge ⭐
- Jede Hilfe von Personen, die eine der unterstützten Sprachen sprechen, um uns bei der Verbesserung der Modelle zu helfen ⭐
- [x] Blöcke/Kapitel vor dem Start der Konvertierung in der Vorschau anzeigen
- [x] Bearbeitung nach konvertiertem Satz für chirurgisch genaue Textänderungen
- [x] Musik-Intros, -Zwischenspiele und -Enden generieren; Zwischenspiele und -Enden bearbeiten
- [x] SML-Tag-Integration für Stimme, Pause, Unterbrechung und weitere Änderungen
- [x] Informationen zu den Parametern -h -help in verschiedenen Sprachen
- [x] OCR-Erkennung für PDF / JPG / BMP / PNG / TIFF
- [x] Notebooks-Ordner [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Die chinesische Textaufteilung so gestalten, dass keine Wörter getrennt werden, und das Pausen-Timing verbessern [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker komponieren
- [x] Podman komponieren
- [x] Kaggle-Notebook
- [x] Google-Colab-Notebook
- [x] Audiobookshelf-Integration
- [x] Option zur E-Book-Übersetzung
- [x] Auswahl des Ausgabeformats
- [x] Konvertierung mit Multiprocessing
- [x] Stapelkonvertierung eines E-Book-Ordners
- [x] GPU-Geräteerkennung
- [x] Hintergrundreferenzaudio für das Hochladen von Sprachklonen entrauschen
- [x] Benutzerdefinierter, fein abgestimmter Modell-Upload
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Benutzer Anfragen
- [ ] Ein europäisch-portugiesisches Sprachmodell für mindestens xttsv2, fairseq, vits, piper hinzufügen (Hilfe willkommen)
- [ ] Ein Sindhi-Sprachmodell für mindestens xttsv2, fairseq, vits, piper hinzufügen (Hilfe willkommen)

#### TTS-Motoren
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Fisch-Sprache / Fisch-Audio (https://github.com/fishaudio/fish-speech)[cite: 1]
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
- [x] Konfuzius4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Dots TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Elster TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
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
- [x] Schildkröte (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Rinde (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Readme-Übersetzung
- [x] Arabisch (ara)
- [x] Chinesisch (zho)
- [x]            Englisch (eng)
- [x] Spanisch (Spa)
- [x] Französisch (fra)
- [x] Deutsch (deu)
- [x] Italienisch (ita)
- [x] Portugiesisch (por)
- [x] Polnisch (pol)
- [x] Türkisch (tur)
- [x] Russisch (rus)
- [x] Niederländisch (nld)
- [x] Tschechisch (ces)
- [x] Japanisch (jpn)
- [x] Hindi (hin)
- [x] Bengalisch (ben)
- [x] Ungarisch (hun)
- [x] Koreanisch (kor)
- [x] Vietnamesisch (Vie)
- [x] Schwedisch (swe)
- [x] Persisch (fas)
- [x] Yoruba (yor)
- [x] Swahili (swa)
- [x] Indonesisch (ind)
- [x] Slowakisch (slk)
- [x] Kroatisch (hrv)

#### Betriebssystem Kompatibilität
- [x] 🪟 Windows x86
- [x] 🪟 Arm-Fenster
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] Linux on IA-32 (for Intel x86)
- [x] 🐧 ARM LINUX

**********

## Extra-Overkill für das Trainieren von Modellen und Ähnliches (alle unterstützten Coqui-tts-Modelle und piper-tts in einem einzigen einfachen Befehl) 
- Zur Information darüber @DrewThomasson, er arbeitet derzeit an der Entwicklung dieses, [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Make a easy to use training gui for all coqui-tts models in the [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) Completed at [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## Informationen zur Python-Code-Normalisierung für Mitwirkende
- keine Leerzeile zwischen dem Code, außer zwischen Funktionen und Klassen.
- einfaches Anführungszeichen für alle Schlüssel, außer bei dict() und json. dict['key'] wird immer mit einfachem Anführungszeichen aufgerufen
- 4 Leerzeichen Einrückung, überhaupt kein Tab
- strikte Typisierung für alle Funktionen sowie die Deklaration ihrer Argumente und Rückgabewerte
- kein Leerzeichen zwischen dem Argument und seiner Typisierung, kein Leerzeichen zwischen der Funktion, dem „->“ und dem Rückgabewert

Beispiel:

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

## Hardware-Spende für Beta-Tests gesucht
Wir nehmen jede Art von Hardware an, um unsere Entwicklung zu testen, wie zum Beispiel:
- Nvidia unterstützt Cuda >= 11,8
- XPU-Intel-Karten
- ROCm AMD-Karten, die ROCm >=5,7 unterstützen

@DrewThomasson, falls Sie auf irgendeine Weise mithelfen möchten! 😃
<!--
## Müssen Sie eine GPU mieten, um unseren Service zu beschleunigen?
- Eine Umfrage ist hier offen https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Credits
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- Ein Deep-Learning-Toolkit für Text-to-Speech, kampferprobt in Forschung und Produktion.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Schnelle und lokale neuronale Text-zu-Sprache-Engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml-Inferenzcode für Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- Eine All-in-One, reine C++ Inferenz-Engine für Audiomodelle, angetrieben von ggml.

## Besonderer Dank
>>>>>>> b9c7b9f1ac1b8217f97de7a9192b7291ec770fcd
Für alle Finanz- und Code-Mitwirkenden trägt jeder Beitrag und Vorschlag dazu bei, die Qualität von E2A zu verbessern.