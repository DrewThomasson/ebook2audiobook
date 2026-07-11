# 📚 ebook2audiobook (E2A)
CPU/GPU-Konverter von E-Book zu Hörbuch mit Kapiteln und Metadaten<br/>
unter Verwendung fortschrittlicher TTS-Engines und vielem mehr.<br/>
Unterstützt Stimmenklonen und 1158 Sprachen!
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
- [Funktionen](#features)
- [GUI-Oberfläche](#gui-interface)
- [Demos](#demos)
- [Unterstützte Sprachen](#supported-languages)
- [Mindestanforderungen](#hardware-requirements)
- [Verwendung](#instructions)
  - [Lokal ausführen](#instructions)
    - [Gradio-Web-Oberfläche starten](#instructions)
    - [Grundlegende Headless-Verwendung](#basic-usage)
    - [Headless-Verwendung eines benutzerdefinierten XTTS-Modells](#example-of-custom-model-zip-upload)
    - [Ausgabe des Hilfebefehls](#help-command-output)
  - [Remote ausführen](#run-remotely)
  - [Docker](#docker)
    - [Schritte zur Ausführung](#docker)
  
- [Geklonte Stimmen](#cloned-voices)
- [Feinabgestimmte TTS-Modelle](#fine-tuned-tts-models)
  - [Sammlung feinabgestimmter TTS-Modelle](#fine-tuned-tts-collection)
  - [XTTSv2 trainieren](#fine-tune-your-own-xttsv2-model)
- [Unterstützte E-Book-Formate](#supported-ebook-formats)
- [Ausgabeformate](#output-and-process-formats)
- [Zu einer älteren Version zurückkehren](#reverting-to-older-versions)
- [Häufige Probleme](#common-issues)
- [Besonderer Dank](#special-thanks)
- [Inhaltsverzeichnis](#table-of-contents)


## Funktionen
- 🔧 **Unterstützte TTS-Engines**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Mehrere Dateiformate konvertieren**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Textbereich** zum direkten Umwandeln eines kurzen Texts in Audio
- 🔍 **OCR-Erkennung** für Dateien mit Textseiten als Bilder
- 🔊 **Hochwertige Sprachausgabe**, von nahezu Echtzeit bis zu nahezu echter Stimme
- 🗣️ **Optionales Stimmenklonen** mit Ihrer eigenen Sprachdatei
- 🌐 **Unterstützt 1158 Sprachen** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
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
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple-Silicon-CPU)

*<i> Moderne TTS-Engines sind auf der CPU sehr langsam, verwenden Sie daher TTS geringerer Qualität wie YourTTS, Tacotron2 usw.</i>

## Unterstützte Sprachen
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 Sprachen und Dialekte hier**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


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

**Sehen Sie sich unser anderes Repo an, das dem automatischen Hinzufügen von SML in Ihrem E-Book gewidmet ist -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Bevor Sie ein Installations- oder Fehlerproblem melden, durchsuchen Sie sorgfältig den Tab mit offenen und geschlossenen Issues<br>
um sicherzustellen, dass Ihr Problem nicht bereits existiert.**

>[!NOTE]
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
   `python app.py --share` (all OS)

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

## Geklonte Stimmen
Sie können jedes Sprachaudio in jedem der unterstützten Audioformate hochladen. Die ideale Dauer beträgt etwa 1 bis 5 Minuten.
Es spielt keine Rolle, ob die Aufnahme einen lauten Hintergrund hat oder Musik darüber abgespielt wird — E2A wird die Stimme für Sie aufräumen.

Die eingebaute Liste der geklonten Stimmen ist hauptsächlich auf Englisch. Wenn Sie Stimmen in anderen Sprachen benötigen, um offiziell
der Liste hinzugefügt, kontaktieren Sie uns bitte und wir werden sie nach der Überprüfung hinzufügen.

## Feinabgestimmte (fine-tuned) TTS-Modelle
#### Stimmen Sie Ihr eigenes XTTSv2-Modell fein ab

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


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
   fügen Sie für weitere Informationen den Parameter `--help` am Ende des docker-run-Befehls hinzu.
- „Ich habe ein Problem mit abgeschnittenem Audio!“ - BITTE ERSTELLEN SIE DAZU EIN ISSUE,
   wir sprechen nicht jede Sprache und benötigen den Rat der Nutzer, um die Logik der Satztrennung zu verfeinern.😊

## ***** ROADMAP *****
- Alle Funktionen offen für öffentliche Beiträge ⭐
- Jede Hilfe von Personen, die eine der unterstützten Sprachen sprechen, um uns bei der Verbesserung der Modelle zu helfen ⭐
- [x] Blöcke/Kapitel vor dem Start der Konvertierung in der Vorschau anzeigen
- [ ] Bearbeitung nach konvertiertem Satz für chirurgisch genaue Textänderungen
- [x] SML-Tag-Integration für Stimme, Pause, Unterbrechung und weitere Änderungen 
- [x] Informationen zu den Parametern -h -help in verschiedenen Sprachen
- [x] OCR-Erkennung für PDF / JPG / BMP / PNG / TIFF
- [x] Notebooks-Ordner [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Die chinesische Textaufteilung so gestalten, dass keine Wörter getrennt werden, und das Pausen-Timing verbessern [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle-Notebook
- [x] Google-Colab-Notebook
- [ ] Audiobookshelf-Integration
- [ ] [Eine iOS-App erstellen](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Eine Android-App erstellen](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Zusätzliche Optionen
- [x] Option zur E-Book-Übersetzung
- [x] Auswahl des Ausgabeformats
- [x] Stapelverarbeitung eines E-Book-Ordners
- [x] Konvertierung mit Multiprocessing
- [x] Stapelkonvertierung eines E-Book-Ordners
- [x] GPU-Geräteerkennung
- [x] Beliebiges Referenz-Audio für das Stimmenklonen beim Upload entrauschen,
- [x] Upload eines benutzerdefinierten Modells (vorerst nur XTTSv2. mehr auf Anfrage)
- [ ] Ein europäisch-portugiesisches Sprachmodell für mindestens xttsv2, fairseq, vits, piper hinzufügen (Hilfe willkommen)
- [ ] Ein Sindhi-Sprachmodell für mindestens xttsv2, fairseq, vits, piper hinzufügen (Hilfe willkommen)

#### TTS-Motoren
- [x] XTTSv2
- [x] Rinde
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Türkis
- [x] GlowTTS
- [x] Pfeffer
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fischsprache (https://github.com/fishaudio/fish-speech)
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
- [ ] Style-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Readme-Übersetzung
- [ ] Arabisch (ara)
- [ ] Chinesisch (zho)
- [x] English (eng)
- [ ] Spanisch (Spa)
- [ ] Französisch (fra)
- [ ] Deutsch (deu)
- [ ] Italienisch (ita)
- [ ] Portugiesisch (por)
- [ ] Polnisch (pol)
- [ ] Türkisch (tur)
- [ ] Russisch (rus)
- [ ] Niederländisch (nld)
- [ ] Tschechisch (ces)
- [ ] Japanisch (jpn)
- [ ] Hindi (hin)
- [ ] Bengalisch (ben)
- [ ] Ungarisch (hun)
- [ ] Koreanisch (kor)
- [ ] Vietnamesisch (Vie)
- [ ] Schwedisch (swe)
- [ ] Persisch (fas)
- [ ] Yoruba (yor)
- [ ] Swahili (swa)
- [ ] Indonesisch (ind)
- [ ] Slowakisch (slk)
- [ ] Kroatisch (hrv)

#### 🐍 Betriebssystem-Kompatibilität
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra-Overkill für das Trainieren von Modellen und Ähnliches (alle unterstützten Coqui-tts-Modelle und piper-tts in einem einzigen einfachen Befehl) 
- Für Informationen dazu: @DrewThomasson arbeitet derzeit an der Entwicklung, [Work-in-Progress-Repo hier](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Eine einfach zu bedienende Trainings-GUI für alle coqui-tts-Modelle im ljspeech-Format erstellen [Trainingsrezepte hier von coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


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
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson, falls Sie auf irgendeine Weise mithelfen möchten! 😃
<!--
## Müssen Sie eine GPU mieten, um unseren Service zu beschleunigen?
- Eine Umfrage ist hier offen https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Besonderer Dank
Für alle Finanz- und Code-Mitwirkenden trägt jeder Beitrag und Vorschlag dazu bei, die Qualität von E2A zu verbessern.