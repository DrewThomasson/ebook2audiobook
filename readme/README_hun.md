# 📚 ebook2audiobook (E2A)
CPU/GPU átalakító e-könyvből hangoskönyvvé fejezetekkel és metaadatokkal<br/>
fejlett TTS-motorok használatával és még sok mással.<br/>
Támogatja a hangklónozást és 1158 nyelvet!
> [!IMPORTANT]
**Ez az eszköz kizárólag DRM-mentes, legálisan beszerzett e-könyvekhez használható.** <br>
A szerzők nem felelősek a szoftver bárminemű visszaéléséért, sem az ebből eredő jogi következményekért. <br>
Használd ezt az eszközt felelősségteljesen, az összes vonatkozó törvénnyel összhangban.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Köszönjük, hogy támogatod az ebook2audiobook fejlesztőit!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Futtatás helyben

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Futtatás távolról
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Grafikus felület (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Kattints a webes GUI képeinek megtekintéséhez</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demók

**Az új alapértelmezett hang demója**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>További demók</summary>

**ASMR hang** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Esős napi hang**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett hang**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David Attenborough hang** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Példa**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Tartalomjegyzék
- [ebook2audiobook](#-ebook2audiobook)
- [Funkciók](#features)
- [Grafikus felület](#gui-interface)
- [Demók](#demos)
- [Támogatott nyelvek](#supported-languages)
- [Minimális követelmények](#hardware-requirements)
- [Használat](#instructions)
  - [Futtatás helyben](#instructions)
    - [A Gradio webes felület indítása](#instructions)
    - [Alapvető headless használat](#basic-usage)
    - [Egyéni XTTS modell használata headless módban](#example-of-custom-model-zip-upload)
    - [A súgóparancs kimenete](#help-command-output)
  - [Futtatás távolról](#run-remotely)
  - [Docker](#docker)
    - [Futtatási lépések](#docker)
  
- [Klónozott hangok](#cloned-voices)
- [Finomhangolt TTS modellek](#fine-tuned-tts-models)
  - [Finomhangolt TTS modellek gyűjteménye](#fine-tuned-tts-collection)
  - [XTTSv2 tanítása](#fine-tune-your-own-xttsv2-model)
- [Támogatott e-könyv formátumok](#supported-ebook-formats)
- [Kimeneti formátumok](#output-and-process-formats)
- [Visszatérés régebbi verzióhoz](#reverting-to-older-versions)
- [Gyakori problémák](#common-issues)
- [Külön köszönet](#special-thanks)
- [Tartalomjegyzék](#table-of-contents)


## Funkciók
- 🔧 **Támogatott TTS-motorok**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Több fájlformátum átalakítása**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Szövegmező** rövid szöveg közvetlen hanggá alakításához
- 🔍 **OCR-beolvasás** képként megjelenő szöveges oldalakat tartalmazó fájlokhoz
- 🔊 **Kiváló minőségű szövegfelolvasás**, a közel valós időtől a szinte valós hangig
- 🗣️ **Opcionális hangklónozás** a saját hangfájlod használatával
- 🌐 **1158 nyelvet támogat** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Erőforrás-barát** — fut **2 GB RAM / 1 GB VRAM (minimum)** mellett
- 🎵 **Hangoskönyv kimeneti formátumok**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML címkék támogatása** — szünetek, megállások, hangváltás és egyebek finom vezérlése ([see below](#sml-tags-available))
- 🧩 **Opcionális egyéni modell** a saját betanított modelled használatával (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Finomhangolt előbeállított modellek**, amelyeket az E2A csapata tanított be<br/>
     <i>(Lépj kapcsolatba velünk, ha további finomhangolt modellekre van szükséged, vagy ha meg szeretnéd osztani a sajátjaidat a hivatalos előbeállítások listáján)</i>


##  Hardverkövetelmények
- 2 GB RAM min., 8 GB ajánlott.
- 1 GB VRAM min., 4 GB ajánlott.
- Engedélyezett virtualizáció, ha Windowson fut (csak Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon CPU)

*<i> A modern TTS-motorok nagyon lassúak CPU-n, ezért használj alacsonyabb minőségű TTS-t, mint a YourTTS, Tacotron2 stb.</i>

## Támogatott nyelvek
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 nyelv és nyelvjárás itt**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Támogatott e-könyv formátumok
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Legjobb eredmények**: `.epub` vagy `.mobi` az automatikus fejezetfelismeréshez

## Kimeneti és feldolgozási formátumok
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- A feldolgozási formátum a lib/conf.py fájlban módosítható

## Elérhető SML címkék
- `[break]` — csend (véletlenszerű tartomány **0.3–0.6 sec.**)
- `[pause]` — csend (véletlenszerű tartomány **1.0–1.6 sec.**)
- `[pause:N]` — fix szünet (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — hangváltás az alapértelmezett vagy a GUI/CLI-ben kiválasztott hangról

**Nézd meg másik repónkat, amely az SML automatikus hozzáadásának szentelt az e-könyvedhez -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Mielőtt telepítési vagy hibajegyet nyitnál, gondosan keress rá a nyitott és lezárt jegyek fülön<br>
hogy biztos legyél benne, hogy a problémád még nem létezik.**

>[!NOTE]
**Az EPUB formátum nem rendelkezik semmilyen szabványos struktúrával arra nézve, hogy mi a fejezet, bekezdés, előszó stb.<br>
Ezért először manuálisan el kell távolítanod minden olyan szöveget, amelyet nem szeretnél hanggá alakítani.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Telepítsd / Futtasd az ebook2audiobookot**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac indító**  
     Kattints duplán a `Mac Ebook2Audiobook Launcher.command` fájlra


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Megjegyzés Windows-felhasználóknak: a scoop telepítésre kerül a hiányzó programok rendszergazdai jogosultságok nélküli telepítéséhez.</i>
   
1. **Nyisd meg a webalkalmazást**: Kattints a terminálban megadott URL-re a webalkalmazás eléréséhez és az e-könyvek átalakításához. `http://localhost:7860/`
2. **Nyilvános linkhez**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Ha a szkriptet leállítják és újra futtatják, frissítened kell a Gradio GUI felületedet<br>
hogy a weboldal újra tudjon csatlakozni az új kapcsolati sockethez.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Az e-könyv fájlod elérési útja
  - **[--voice]**: A hangklónozó fájl elérési útja (opcionális)
  - **[--language]**: Nyelvkód ISO-639-3 formátumban (pl.: ita olaszhoz, eng angolhoz, deu némethez...).<br>
    Az alapértelmezett nyelv az eng, és a --language opcionális a ./lib/lang.py fájlban beállított alapértelmezett nyelvhez.<br>
    A kétbetűs ISO-639-1 kódok is támogatottak.


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
     
- **<custom_model_path>**: A `model_name.zip` fájl elérési útja,
      amelynek (a TTS-motortól függően) tartalmaznia kell az összes kötelező fájlt<br>
      (lásd ./lib/models.py).

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

MEGJEGYZÉS: gradio/gui módban a folyamatban lévő átalakítás megszakításához egyszerűen kattints az e-könyv feltöltési komponens [X] gombjára.
TIPP: ha kicsit több szünet szükséges, adj hozzá '[pause:3]'-at 3 mp-hez stb.

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

## Klónozott hangok
Bármilyen hangfelvételt feltölthet bármelyik támogatott hangformátumban, az ideális időtartam 1-5 mn.
Nem számít, hogy a felvétel zajos háttérrel vagy zenével rendelkezik — az E2A megtisztítja a hangot az Ön számára.

A beépített klónozott hangok listája főként angol nyelven érhető el. Ha más nyelvű hangokra van szüksége ahhoz, hogy hivatalosan
hozzáadva a listához. Vedd fel velünk a kapcsolatot, és az ellenőrzés után hozzáadjuk őket.

## Finomhangolt (fine-tuned) TTS modellek
#### Finomhangold a saját XTTSv2 modelledet

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Tanítóadatok zajszűrése

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Finomhangolt TTS modellek gyűjteménye

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Egyéni XTTSv2 modellhez kötelező egy referencia hangklip a hangról:

## A saját Ebook2Audiobook testreszabásod
Szabadon módosíthatod a libs/conf.py fájlt a kívánt beállítások hozzáadásához vagy eltávolításához. Ha ezt tervezed, egyszerűen készíts
egy másolatot az eredeti conf.py fájlról, hogy minden ebook2audiobook frissítésnél elmenthesd a módosított conf.py fájlodat, és visszatehesd
az eredetit. Ugyanezt a folyamatot kell megtervezned a models.py esetében is. Ha szeretnéd a saját egyéni modelledet
hivatalos finomhangolt ebook2audiobook modellé tenni, lépj kapcsolatba velünk, és hozzáadjuk az előbeállítások listájához.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Gyakori problémák:
- Az NVIDIA/ROCm/XPU/MPS GPU-mat nem érzékeli?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  A CPU lassú (jobb szerver SMP CPU-n), míg a GPU szinte valós idejű átalakítást tud nyújtani.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Nincs azonban zero-shot hangklónozása, és a hangok Siri minőségűek, de CPU-n sokkal gyorsabb).
- „Függőségi problémáim vannak” - Egyszerűen használd a Dockert, teljesen önálló, és van headless módja,
   adj hozzá `--help` paramétert a docker run parancs végéhez további információkért.
- „Levágott hang problémám van!” - KÉRJÜK, NYISS ERRŐL EGY ISSUE-T,
   nem beszélünk minden nyelvet, és szükségünk van a felhasználók tanácsaira a mondatfelosztási logika finomhangolásához.😊

## ***** ÜTEMTERV *****
- Minden funkció nyitva a nyilvános hozzájárulások előtt ⭐
- Bármilyen segítség a támogatott nyelvek valamelyikét beszélő emberektől, hogy segítsenek javítani a modelleket ⭐
- [x] Blokkok/fejezetek előnézete az átalakítás megkezdése előtt
- [ ] Szerkesztés átalakított mondatonként a sebészi pontosságú szövegmódosításhoz
- [x] SML címkék integrációja hanghoz, szünethez, megszakításhoz és további módosításokhoz 
- [x] A -h -help paraméterek információi különböző nyelveken
- [x] OCR-beolvasás PDF / JPG / BMP / PNG / TIFF formátumokhoz
- [x] Notebookok mappa [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] A kínai szövegfelosztás úgy alakítása, hogy ne vágjon szét szavakat, és a szünetek időzítésének javítása [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle notebook
- [x] Google Colab notebook
- [ ] Audiobookshelf integráció
- [ ] [iOS alkalmazás készítése](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Android alkalmazás készítése](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### További opciók
- [x] E-könyv fordítási opció
- [x] Kimeneti formátum választása
- [x] Kötegelt e-könyv mappa
- [x] Átalakítás többszálú feldolgozással
- [x] E-könyv mappa kötegelt átalakítása
- [x] GPU-eszköz észlelése
- [x] Bármilyen referencia hang zajszűrése a feltöltött hangklónozáshoz,
- [x] Egyéni modell feltöltése (egyelőre csak XTTSv2. több kérésre)
- [ ] Európai portugál nyelvi modell hozzáadása legalább xttsv2, fairseq, vits, piper számára (segítség szívesen látott)
- [ ] Szindhi nyelvi modell hozzáadása legalább xttsv2, fairseq, vits, piper számára (segítség szívesen látott)

#### TTS motorok
- [x] XTTSv2
- [x] Bark
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Szárazfölditeknős-félék
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] hal-beszéd (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Szupertonikus (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Stílus-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### A Readme fordítása
- [x] Arab (ara)
- [x] Kínai (zho)
- [x] English (eng)
- [x] Spanyol (Spa)
- [x] Francia (fra)
- [x] Német (deu)
- [x] Olasz (ita)
- [x] Portugál (por)
- [x] Lengyel (pol)
- [x] Török (tur)
- [x] Orosz (orosz)
- [x] Holland (nld)
- [x] Czech (ces)
- [x] Japán (jpn)
- [x] Hindi (hin)
- [x] Bengáli (ben)
- [x] Hungarian (hun)
- [x] Koreai (kor)
- [x] Vietnami (vie)
- [x] Svéd (swe)
- [x] Perzsa (fas)
- [x] Yoruba (yor)
- [x] Szuahéli (swa)
- [x] Indonéz (ind)
- [x] Slovak (slk)
- [x] Horvát (hrv)

#### 🐍 Operációsrendszer-kompatibilitás
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra túlzás modellek tanításához és hasonlókhoz (az összes támogatott Coqui-tts modell és a piper-tts egyetlen egyszerű paranccsal) 
- Az erről szóló információkért: @DrewThomasson jelenleg ennek a fejlesztésén dolgozik, [fejlesztés alatt álló repó itt](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Könnyen használható tanító GUI készítése az összes coqui-tts modellhez ljspeech formátumú tanító receptekben [itt a coqui tts-től](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Python kódnormalizálási információk közreműködőknek
- nincs üres sor a kód között, kivéve a függvények és osztályok között.
- egyszeres idézőjel minden kulcshoz, kivéve a dict() és json esetében. a dict['key'] mindig egyszeres idézőjellel hívandó
- 4 szóköznyi behúzás, egyáltalán nincs tabulátor
- szigorú típusozás minden függvényhez, valamint argumentumaik és visszatérési értékeik deklarációjához
- nincs szóköz az argumentum és a típusozása között, nincs szóköz a függvény, a „->” és a visszatérési érték között

Példa:

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

## Hardveradományt keresünk béta tesztekhez
Bármilyen típusú hardvert elfogadunk a fejlesztésünk teszteléséhez, például:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson ha bármilyen módon segíteni szeretnél! 😃
<!--
## Szükséged van GPU bérlésére a szolgáltatásunk felgyorsításához?
- Egy szavazás nyitva van itt https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Külön köszönet
Minden pénzügyi és kód közreműködő számára minden hozzájárulás és javaslat hozzájárul az E2A minőségének javításához.