<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

CPU/GPU pretvarač iz e-knjige u audioknjigu s poglavljima i metapodacima<br/>
uz napredne TTS pogone i još mnogo toga.<br/>
Podržava kloniranje glasa i 1696 jezika!
> VAŽNO
**Ovaj alat namijenjen je isključivo za upotrebu s e-knjigama bez DRM-a, legalno nabavljenima.** <br>
Autori nisu odgovorni ni za kakvu zlouporabu ovog softvera niti za eventualne pravne posljedice. <br>
Koristite ovaj alat odgovorno i u skladu sa svim primjenjivim zakonima.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Zahvaljujući podršci za programere ebook2audiobook!
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### Pokreni lokalno
[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)Upute
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### Pokretanje na daljinu
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### Grafičko sučelje (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Kliknite za prikaz slika web GUI-ja</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
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

<a id="table-of-contents"></a>
## Sadržaj
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
## Značajke
- 🔧 **Podržani TTS motori**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Pretvaranje više formata datoteka**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Tekstno polje** za izravno pretvaranje kratkog teksta u zvuk
- 🔍 **OCR skeniranje** za datoteke s tekstualnim stranicama u obliku slika
- 🔊 **Visokokvalitetno pretvaranje teksta u govor**, od gotovo stvarnog vremena do gotovo stvarnog glasa
- 🗣️ **Neobavezno kloniranje glasa** pomoću vlastite glasovne datoteke
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Prikladno za ograničene resurse** — radi na **2 GB RAM-a / 1 GB VRAM-a (minimum)**
- 🎵 **Izlazni formati audioknjige**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Podržane SML oznake** — precizna kontrola prekida, pauza, promjene glasa i više ([see below](#sml-tags-available))
- 🧩 **Neobavezni prilagođeni model** pomoću vašeg vlastitog istreniranog modela (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Fino podešeni unaprijed postavljeni modeli** istrenirani od strane E2A tima<br/>
     <i>(Kontaktirajte nas ako trebate dodatne fino podešene modele ili ako želite podijeliti svoje na službenom popisu unaprijed postavljenih)</i>


<a id="hardware-requirements"></a>
##  Hardverski zahtjevi
- 2 GB RAM-a min., 8 GB preporučeno.
- 1 GB VRAM-a min., 4 GB preporučeno.
- Omogućena virtualizacija pri pokretanju na Windowsima (samo Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Moderni TTS pogoni vrlo su spori na CPU-u, pa koristite TTS niže kvalitete poput YourTTS, Tacotron2 itd.</i>

<a id="supported-languages"></a>
## Podržani jezici
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## Podržani formati e-knjiga
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Najbolji rezultati**: `.epub` ili `.mobi` za automatsko otkrivanje poglavlja

<a id="output-and-process-formats"></a>
## Formati izlaza i obrade
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Format obrade može se promijeniti u lib/conf.py

## Dostupne SML oznake
- `[break]` — tišina (nasumični raspon **0.3–0.6 sec.**)
- `[pause]` — tišina (nasumični raspon **1.0–1.6 sec.**)
- `[pause:N]` — fiksna pauza (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — prebacivanje glasa sa zadanog ili odabranog glasa iz GUI/CLI
- `[emotion:sadness]...[/emotion]` — Zonos samo: emocija za prolaz (sreća, tuga, gađenje, strah, iznenađenje, ljutnja, drugo, neutralno) ili mješavina poput `[emotion:sadness=0.7,neutral=0.3]`; ostali motori to ignoriraju

**Pogledajte naš drugi repozitorij posvećen automatskom dodavanju SML-a u vašu e-knjigu -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Prije nego što prijavite problem s instalacijom ili pogrešku, pažljivo pretražite karticu otvorenih i zatvorenih problema<br>
kako biste bili sigurni da vaš problem već ne postoji.**

>[!NOTE]
**Format EPUB nema nikakvu standardnu strukturu koja definira što je poglavlje, odlomak, predgovor itd.<br>
Stoga biste prvo trebali ručno ukloniti sav tekst koji ne želite pretvoriti u zvuk.**


<a id="instructions"></a>
### Upute
1. **Klonirajte repozitorij**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Instalirajte / Pokrenite ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Napomena za korisnike MacOS-a: homebrew se instalira radi instalacije programa koji nedostaju.</i>
     
   - **Pokretač za Mac**  
     Dvaput kliknite na `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     ili
     Dvaput kliknite `ebook2audiobook.cmd`

     <i>Napomena za korisnike Windowsa: scoop se instalira radi instalacije programa koji nedostaju bez administratorskih ovlasti.</i>
   
1. **Otvorite web aplikaciju**: Kliknite na URL naveden u terminalu za pristup web aplikaciji i pretvaranje e-knjiga. `http://localhost:7860/`
2. **Za javnu poveznicu**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (svi operativni sustavi, samo nakon instalacije i s Pythonom iz mape python_env)

> [!IMPORTANT]
**Ako se skripta zaustavi i ponovno pokrene, morate osvježiti svoje Gradio GUI sučelje<br>
kako bi se web stranica ponovno povezala s novim utičnicom veze.**

<a id="basic-usage"></a>
### Osnovna upotreba
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


<a id="example-of-custom-model-zip-upload"></a>
###  Primjer prijenosa prilagođenog modela u zipu
  (mora biti .zip datoteka koja sadrži obavezne datoteke modela. Primjer za XTTSv2: config.json, model.pth, vocab.json i ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Napomena: ref.wav vašeg prilagođenog modela uvijek je glas odabran za pretvorbu</i>
     
- **<custom_model_path>**: Putanja do datoteke `model_name.zip`,
      koja mora sadržavati (ovisno o TTS pogonu) sve obavezne datoteke<br>
      (vidi ./lib/models.py).

### Detaljan vodič s popisom svih dostupnih parametara
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Ili za sve OS-ove**
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

NAPOMENA: u gradio/gui načinu rada, za otkazivanje pretvaranja u tijeku jednostavno kliknite na [X] na komponenti za učitavanje e-knjige.
SAVJET: ako je potrebna malo dulja pauza, dodajte '[pause:3]' za 3 sek. itd.

<a id="docker"></a>
### Docker
1. **Klonirajte repozitorij**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Izgradite kontejner**
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
4. **Pokrenite kontejner:**
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
- NAPOMENA: MPS nije dostupan u Dockeru pa se mora koristiti CPU
- NAPOMENA: imenovani volumen `e2a_venvs` čuva TTS pogone instalirane u vlastitim venv okruženjima (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM itd.)
  između pokretanja kontejnera, pa se ne instaliraju iznova svaki put. Za njihovo resetiranje: `docker volume rm e2a_venvs`

<a id="tools"></a>
## Alati
Samostalni alati koji se pokreću vlastitim Pythonom e2a (`python_env`, stvoren pri prvom pokretanju e2a).

<a id="preload-models"></a>
### Prethodno preuzimanje modela za izvanmrežne instalacije: `tools/preload_models.py`
Preuzima svaki model koji e2a koristi (TTS pogone i njihove fino podešene verzije, pretvorbu glasa, stanza, pyannote, demucs,
glazbene međuigre, argos-translate pakete, tesseract podatke, jieba i glasove) u jednu mapu organiziranu
točno kao `./models`, npr. na USB stick. Na izvanmrežnom računalu kopirajte tu mapu u `./models` od e2a,
a mapu `voices` zapisanu pokraj nje u `./voices` od e2a.
Svaki dovršeni posao bilježi se u `<models_dir>/.e2a_downloads.json`: ponovno pokretanje preskače dovršeno i iznova pokreće
prekinuto (ctrl-c, rušenje, isključen stick) nakon uklanjanja njegovih djelomičnih datoteka.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` ispisuje poslove i njihovo stanje (dovršeno, prekinuto, na čekanju) bez preuzimanja ičega.

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
### Prevođenje e-knjiga izvan e2a: `tools/translate_ebook.sh` / `tools/translate_ebook.cmd`
Prevodi EPUB/AZW3 datoteke, cijelu mapu (`-r` za njezine podmape) ili popis putanja (`@list.txt`)
u prevedene e-knjige, izvanmrežno, pomoću calibre dodatka Argos Translate isporučenog u
`tools/argostranslate-calibre-plugin.zip`. Neovisno o pretvorbi u audioknjigu: zapisuje samo e-knjige.
Zahtijeva calibre (koji e2a već traži) i radi na `python_env` i argos-translate paketima iz e2a:
jezični par koji e2a već koristi ne preuzima se ponovno, onaj koji nedostaje preuzima se pri prvoj upotrebi.
Dodatak se pri prvoj upotrebi instalira u vlastiti calibre profil e2a (`./run`), vaš calibre ostaje netaknut.
`--to fra,ara,spa` prevodi na više jezika odjednom, jedna e-knjiga po jeziku, a `--to all` na svaki
jezik dostupan iz izvora (`--from`, inače vlastiti jezik svake knjige; uz `--no_download` samo instalirani jezični parovi).
`--list --from eng` ispisuje jezike na koje se prevodi s engleskog (instalirane, dostupne za preuzimanje ili preko engleskog za
drugi izvorni jezik).
Ostali formati koje čita calibreov `ebook-convert` (PDF, DOCX, MOBI, TXT, ...) jednom se pretvaraju u EPUB, prije
prvog jezika, i prevode kao EPUB: `--from` je potreban kada ne navode jezik, što je kod PDF-a i TXT-a često.
Bez `-o` ili `--output_dir` svaki se prijevod sprema pokraj svoje knjige kao `<name>.<lang>.<ext>`,
a knjiga čiji prijevod već postoji preskače se (`--overwrite` za ponovno prevođenje).
Pokretači u mapi `tools/` pokreću `tools/translate_ebook.py` s `python_env`, ništa ne treba aktivirati,
iz bilo koje mape (relativne putanje uzimaju se od mjesta pokretanja):
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Ili izravno s Pythonom iz `python_env`: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Ako se pokrene bilo kojim drugim Pythonom,
     skripta se sama ponovno pokreće s onim iz `python_env`.
   - **Docker**: pokrenite ga unutar e2a kontejnera, npr. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     s putanjama kako ih vidi kontejner.
   - **Brzina**: argostranslate radi na vlastitim zadanim postavkama (CTranslate2 bira niti i najbrži tip izračuna,
     int8 na CPU-u), a ne na jednoj niti e2a u float32. Postavite `ARGOS_INTRA_THREADS` ili `ARGOS_COMPUTE_TYPE` da ih nadjačate.

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
## Klonirani glasovi
Možete prenijeti bilo koji glasovni zvuk u bilo kojem od podržanih audio formata, idealno trajanje je oko 1 do 5 milijuna.
Nije važno ima li snimka bučnu pozadinu ili se nad njom reproducira glazba — E2A će očistiti glas za vas.

Ugrađeni popis kloniranih glasova uglavnom je na engleskom jeziku. Ako želite da glasovi na drugim jezicima budu službeno
dodano na popis, obratite nam se i dodat ćemo ih nakon pregleda.

<a id="fine-tuned-tts-models"></a>
## Fino podešeni (fine-tuned) TTS modeli
<a id="fine-tune-your-own-tts-model"></a>
#### Fino ugađanje vlastitog TTS modela

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Uklanjanje šuma iz podataka za treniranje

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### Zbirka fino podešenih TTS modela

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Za prilagođeni XTTSv2 model obavezan je referentni audioisječak glasa:

## Vaša vlastita prilagodba Ebook2Audiobook
Slobodni ste mijenjati libs/conf.py kako biste dodali ili uklonili željene postavke. Ako to planirate, jednostavno napravite
kopiju izvornog conf.py kako biste pri svakom ažuriranju ebook2audiobook mogli sigurnosno pohraniti svoj izmijenjeni conf.py i vratiti
izvorni. Isti postupak morate planirati i za models.py. Ako želite od svog vlastitog prilagođenog modela
napraviti službeni fino podešeni ebook2audiobook model, kontaktirajte nas i dodat ćemo ga na popis unaprijed postavljenih.

<a id="reverting-to-older-versions"></a>
## Vraćanje na starije verzije
Izdanja se mogu pronaći -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
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
- [x] Uređivanje po pretvorenoj rečenici za kiruršku izmjenu teksta
- [x] Generiranje glazbenih uvoda, interludija i završetaka; uređivanje interludija i završetaka
- [x] Integracija SML oznaka za glas, pauzu, prekid i druge promjene
- [x] Informacije o parametrima -h -help na različitim jezicima
- [x] OCR skeniranje za PDF / JPG / BMP / PNG / TIFF
- [x] Mapa bilježnica [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Učiniti da dijeljenje kineskog teksta ne razdvaja riječi i poboljšati vremensko usklađivanje pauza [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Datoteka Docker
- [x] Docker Compose
- [x] Podman Compose
- [x] Kaggle bilježnica
- [x] Google Colab bilježnica
- [x] Integracija s Audiobookshelf
- [x] Opcija prijevoda e-knjige
- [x] Izbori izlaznog formata
- [x] Pretvaranje s višeprocesnom obradom
- [x] Skupno pretvaranje mape e-knjiga
- [x] Otkrivanje GPU uređaja
- [x] Denoizirati bilo koji pozadinski referentni zvuk za prijenos glasovnog kloniranja
- [x] Prijenos prilagođenog precizno podešenog modela

#### Korisnički zahtjevi
- [ ] Dodati jezični model europskog portugalskog barem za xttsv2, fairseq, vits, piper (pomoć dobrodošla)
- [ ] Dodati jezični model sindhi barem za xttsv2, fairseq, vits, piper (pomoć dobrodošla)

#### TTS motori
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
- [x] Index-tts / Index TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Konfucije4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Točke TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Pocket TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonik (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Kornjača (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Kora (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orfej-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

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

#### Kompatibilnost s 💻 operativnim sustavima
- [x] 🪟 Windows x86
- [x] 🪟 AKTIVIRAJ PROZORE
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

<a id="contributing"></a>
## Doprinos
Prije otvaranja izdanja ili zahtjeva za povlačenje, pročitajte [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md): Pravila normalizacije Python koda,
tijek rada zahtjeva za grananje i povlačenje, legende grafičkog sučelja i prijevodi README, dodavanje TTS motora, testiranje.

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

## Credits
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- Alat za duboko učenje za pretvaranje teksta u govor, testiran u istraživanju i proizvodnji.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Fast and local neural text-to-speech engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml zaključni kod za Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- Višenamjenski, čisti C++ mehanizam za zaključivanje za audio modele, koji pokreće ggml.

<a id="special-thanks"></a>
## Posebna zahvala
Svim financijskim i kodnim suradnicima, svaki doprinos i prijedlog pomaže u poboljšanju kvalitete E2A.