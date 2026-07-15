# 📚 ebook2audiobook (E2A)
CPU/GPU pretvarač iz e-knjige u audioknjigu s poglavljima i metapodacima<br/>
uz napredne TTS pogone i još mnogo toga.<br/>
Podržava kloniranje glasa i 1158 jezika!
> [!IMPORTANT]
**Ovaj alat namijenjen je isključivo za upotrebu s e-knjigama bez DRM-a, legalno nabavljenima.** <br>
Autori nisu odgovorni ni za kakvu zlouporabu ovog softvera niti za eventualne pravne posljedice. <br>
Koristite ovaj alat odgovorno i u skladu sa svim primjenjivim zakonima.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Hvala što podržavate razvojne programere ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Pokretanje lokalno

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Pokretanje na daljinu
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Grafičko sučelje (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Kliknite za prikaz slika web GUI-ja</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demoi

**Demo novog zadanog glasa**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Više demoa</summary>

**ASMR glas** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Glas kišnog dana**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett glas**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Glas Davida Attenborougha** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Primjer**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Sadržaj
- [ebook2audiobook](#-ebook2audiobook)
- [Značajke](#features)
- [Grafičko sučelje](#gui-interface)
- [Demoi](#demos)
- [Podržani jezici](#supported-languages)
- [Minimalni zahtjevi](#hardware-requirements)
- [Upotreba](#instructions)
  - [Pokretanje lokalno](#instructions)
    - [Pokretanje Gradio web sučelja](#instructions)
    - [Osnovna upotreba u headless načinu](#basic-usage)
    - [Upotreba prilagođenog XTTS modela u headless načinu](#example-of-custom-model-zip-upload)
    - [Izlaz naredbe za pomoć](#help-command-output)
  - [Pokretanje na daljinu](#run-remotely)
  - [Docker](#docker)
    - [Koraci za pokretanje](#docker)
  
- [Klonirani glasovi](#cloned-voices)
- [Fino podešeni TTS modeli](#fine-tuned-tts-models)
  - [Zbirka fino podešenih TTS modela](#fine-tuned-tts-collection)
  - [Treniranje XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Podržani formati e-knjiga](#supported-ebook-formats)
- [Izlazni formati](#output-and-process-formats)
- [Vraćanje na stariju verziju](#reverting-to-older-versions)
- [Česti problemi](#common-issues)
- [Posebna zahvala](#special-thanks)
- [Sadržaj](#table-of-contents)


## Značajke
- 🔧 **Podržani TTS pogoni**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Pretvaranje više formata datoteka**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Tekstno polje** za izravno pretvaranje kratkog teksta u zvuk
- 🔍 **OCR skeniranje** za datoteke s tekstualnim stranicama u obliku slika
- 🔊 **Visokokvalitetno pretvaranje teksta u govor**, od gotovo stvarnog vremena do gotovo stvarnog glasa
- 🗣️ **Neobavezno kloniranje glasa** pomoću vlastite glasovne datoteke
- 🌐 **Podržava 1158 jezika** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Prikladno za ograničene resurse** — radi na **2 GB RAM-a / 1 GB VRAM-a (minimum)**
- 🎵 **Izlazni formati audioknjige**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Podržane SML oznake** — precizna kontrola prekida, pauza, promjene glasa i više ([see below](#sml-tags-available))
- 🧩 **Neobavezni prilagođeni model** pomoću vašeg vlastitog istreniranog modela (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Fino podešeni unaprijed postavljeni modeli** istrenirani od strane E2A tima<br/>
     <i>(Kontaktirajte nas ako trebate dodatne fino podešene modele ili ako želite podijeliti svoje na službenom popisu unaprijed postavljenih)</i>


##  Hardverski zahtjevi
- 2 GB RAM-a min., 8 GB preporučeno.
- 1 GB VRAM-a min., 4 GB preporučeno.
- Omogućena virtualizacija pri pokretanju na Windowsima (samo Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Moderni TTS pogoni vrlo su spori na CPU-u, pa koristite TTS niže kvalitete poput YourTTS, Tacotron2 itd.</i>

## Podržani jezici
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 jezika i dijalekata ovdje**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Podržani formati e-knjiga
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Najbolji rezultati**: `.epub` ili `.mobi` za automatsko otkrivanje poglavlja

## Formati izlaza i obrade
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Format obrade može se promijeniti u lib/conf.py

## Dostupne SML oznake
- `[break]` — tišina (nasumični raspon **0.3–0.6 sec.**)
- `[pause]` — tišina (nasumični raspon **1.0–1.6 sec.**)
- `[pause:N]` — fiksna pauza (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — prebacivanje glasa sa zadanog ili odabranog glasa iz GUI/CLI

**Pogledajte naš drugi repozitorij posvećen automatskom dodavanju SML-a u vašu e-knjigu -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Prije nego što prijavite problem s instalacijom ili pogrešku, pažljivo pretražite karticu otvorenih i zatvorenih problema<br>
kako biste bili sigurni da vaš problem već ne postoji.**

>[!NOTE]
**Format EPUB nema nikakvu standardnu strukturu koja definira što je poglavlje, odlomak, predgovor itd.<br>
Stoga biste prvo trebali ručno ukloniti sav tekst koji ne želite pretvoriti u zvuk.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Instalirajte / Pokrenite ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Pokretač za Mac**  
     Dvaput kliknite na `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Napomena za korisnike Windowsa: scoop se instalira radi instalacije programa koji nedostaju bez administratorskih ovlasti.</i>
   
1. **Otvorite web aplikaciju**: Kliknite na URL naveden u terminalu za pristup web aplikaciji i pretvaranje e-knjiga. `http://localhost:7860/`
2. **Za javnu poveznicu**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Ako se skripta zaustavi i ponovno pokrene, morate osvježiti svoje Gradio GUI sučelje<br>
kako bi se web stranica ponovno povezala s novim utičnicom veze.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Putanja do vaše datoteke e-knjige
  - **[--voice]**: Putanja datoteke za kloniranje glasa (neobavezno)
  - **[--language]**: Kod jezika u ISO-639-3 (npr.: ita za talijanski, eng za engleski, deu za njemački...).<br>
    Zadani jezik je eng, a --language je neobavezan za zadani jezik postavljen u ./lib/lang.py.<br>
    Podržani su i dvoslovni ISO-639-1 kodovi.


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
     
- **<custom_model_path>**: Putanja do datoteke `model_name.zip`,
      koja mora sadržavati (ovisno o TTS pogonu) sve obavezne datoteke<br>
      (vidi ./lib/models.py).

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

NAPOMENA: u gradio/gui načinu rada, za otkazivanje pretvaranja u tijeku jednostavno kliknite na [X] na komponenti za učitavanje e-knjige.
SAVJET: ako je potrebna malo dulja pauza, dodajte '[pause:3]' za 3 sek. itd.

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

## Klonirani glasovi
Možete prenijeti bilo koji glasovni zvuk u bilo kojem od podržanih audio formata, idealno trajanje je oko 1 do 5 milijuna.
Nije važno ima li snimka bučnu pozadinu ili se nad njom reproducira glazba — E2A će očistiti glas za vas.

Ugrađeni popis kloniranih glasova uglavnom je na engleskom jeziku. Ako želite da glasovi na drugim jezicima budu službeno
dodano na popis, obratite nam se i dodat ćemo ih nakon pregleda.

## Fino podešeni (fine-tuned) TTS modeli
#### Fino podesite vlastiti XTTSv2 model

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Uklanjanje šuma iz podataka za treniranje

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Zbirka fino podešenih TTS modela

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Za prilagođeni XTTSv2 model obavezan je referentni audioisječak glasa:

## Vaša vlastita prilagodba Ebook2Audiobook
Slobodni ste mijenjati libs/conf.py kako biste dodali ili uklonili željene postavke. Ako to planirate, jednostavno napravite
kopiju izvornog conf.py kako biste pri svakom ažuriranju ebook2audiobook mogli sigurnosno pohraniti svoj izmijenjeni conf.py i vratiti
izvorni. Isti postupak morate planirati i za models.py. Ako želite od svog vlastitog prilagođenog modela
napraviti službeni fino podešeni ebook2audiobook model, kontaktirajte nas i dodat ćemo ga na popis unaprijed postavljenih.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Česti problemi:
- Moj NVIDIA/ROCm/XPU/MPS GPU nije otkriven?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU je spor (bolje na serverskom SMP CPU-u) dok GPU može imati gotovo pretvaranje u stvarnom vremenu.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Međutim, nema zero-shot kloniranje glasa, a glasovi su Siri kvalitete, ali je puno brži na CPU-u).
- „Imam problema s ovisnostima“ - Jednostavno koristite Docker, potpuno je samostalan i ima headless način,
   dodajte parametar `--help` na kraj naredbe docker run za više informacija.
- „Imam problem s odrezanim zvukom!“ - MOLIMO OTVORITE ISSUE O TOME,
   ne govorimo svaki jezik i trebamo savjete korisnika kako bismo fino podesili logiku dijeljenja rečenica.😊

## ***** PLAN RAZVOJA *****
- Sve značajke otvorene za javne doprinose ⭐
- Bilo kakva pomoć od ljudi koji govore neki od podržanih jezika kako bi nam pomogli poboljšati modele ⭐
- [x] Pregled blokova/poglavlja prije početka pretvaranja
- [ ] Uređivanje po pretvorenoj rečenici za kiruršku izmjenu teksta
- [x] Integracija SML oznaka za glas, pauzu, prekid i druge promjene 
- [x] Informacije o parametrima -h -help na različitim jezicima
- [x] OCR skeniranje za PDF / JPG / BMP / PNG / TIFF
- [x] Mapa bilježnica [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Učiniti da dijeljenje kineskog teksta ne razdvaja riječi i poboljšati vremensko usklađivanje pauza [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle bilježnica
- [x] Google Colab bilježnica
- [ ] Integracija s Audiobookshelf
- [ ] [Napraviti iOS aplikaciju](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Napraviti Android aplikaciju](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Dodatne opcije
- [x] Opcija prijevoda e-knjige
- [x] Izbori izlaznog formata
- [x] Skupna mapa e-knjiga
- [x] Pretvaranje s višeprocesnom obradom
- [x] Skupno pretvaranje mape e-knjiga
- [x] Otkrivanje GPU uređaja
- [x] Uklanjanje šuma iz bilo kojeg referentnog zvuka za učitano kloniranje glasa,
- [x] Učitavanje prilagođenog modela (zasad samo XTTSv2. više na zahtjev)
- [ ] Dodati jezični model europskog portugalskog barem za xttsv2, fairseq, vits, piper (pomoć dobrodošla)
- [ ] Dodati jezični model sindhi barem za xttsv2, fairseq, vits, piper (pomoć dobrodošla)

#### TTS motori
- [x] XTTSv2
- [x] Lavež
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Kornjača
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] riblji govor (https://github.com/fishaudio/fish-speech)
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
- [ ] Stil-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orfej-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Prijevod datoteke Readme
- [x] Arapski (ara)
- [x] Kineski (zho)
- [x] English (eng)
- [x] Španjolski (spa)
- [x] Francuski (fra)
- [x] Njemački (deu)
- [x] Talijanski (ita)
- [x] Portugalski (por)
- [x] Poljski (pol)
- [x] Turski (tur)
- [x] Ruski (rus)
- [x] Nizozemski (nld)
- [x] Češki (ces)
- [x] Japanski (jpn)
- [x] Hindski (hin)
- [x] Bengalski (ben)
- [x] Mađarski (hun)
- [x] Korejski (kor)
- [x] Vijetnamski (vie)
- [x] Švedski (swe)
- [x] Perzijski (fas)
- [x] Yoruba (yor)
- [x] Svahili (sva)
- [x] Indonezijski (ind)
- [x] Slovački (slk)
- [x] Croatian (hrv)

#### 🐍 Kompatibilnost operacijskih sustava
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Dodatni overkill za treniranje modela i slično (svi podržani Coqui-tts modeli i piper-tts u jednoj jednostavnoj naredbi) 
- Za informacije o tome: @DrewThomasson trenutno radi na razvoju ovoga, [repozitorij u izradi ovdje](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Napraviti jednostavan GUI za treniranje svih coqui-tts modela u receptima za treniranje u ljspeech formatu [ovdje od coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informacije o normalizaciji Python koda za suradnike
- nema praznog retka između koda, osim između funkcija i klasa.
- jednostruki navodnik korišten za sve ključeve osim za dict() i json. dict['key'] uvijek pozvan s jednostrukim navodnikom
- uvlaka od 4 razmaka, nikakvi tabulatori
- strogo tipiziranje za sve funkcije i deklaraciju njihovih argumenata i povratnih vrijednosti
- nema razmaka između argumenta i njegovog tipiziranja, nema razmaka između funkcije, „->“ i povratne vrijednosti

Primjer:

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

## Tražimo donaciju hardvera za beta testiranje
Prihvaćamo bilo koju vrstu hardvera za testiranje našeg razvoja, kao što su:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson ako želite pomoći na bilo koji način! 😃
<!--
## Trebate li unajmiti GPU za pojačanje naše usluge?
- Anketa je otvorena ovdje https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Posebna zahvala
Svim financijskim i kodnim suradnicima, svaki doprinos i prijedlog pomaže u poboljšanju kvalitete E2A.