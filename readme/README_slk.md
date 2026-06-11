# 📚 ebook2audiobook (E2A)
CPU/GPU prevodník z e-knihy na audioknihu s kapitolami a metadátami<br/>
s využitím pokročilých TTS enginov a mnohého ďalšieho.<br/>
Podporuje klonovanie hlasu a 1158 jazykov!
> [!IMPORTANT]
**Tento nástroj je určený len na použitie s e-knihami bez DRM, získanými legálne.** <br>
Autori nenesú zodpovednosť za akékoľvek zneužitie tohto softvéru ani za prípadné právne následky. <br>
Používajte tento nástroj zodpovedne a v súlade so všetkými platnými zákonmi.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Ďakujeme za podporu vývojárov ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Spustenie lokálne

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Spustenie vzdialene
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Grafické rozhranie (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Kliknite pre zobrazenie obrázkov webového GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Ukážky

**Ukážka nového predvoleného hlasu**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Viac ukážok</summary>

**Hlas ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Hlas daždivého dňa**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Hlas Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Hlas Davida Attenborougha** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Príklad**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Obsah
- [ebook2audiobook](#-ebook2audiobook)
- [Funkcie](#features)
- [Grafické rozhranie](#gui-interface)
- [Ukážky](#demos)
- [Podporované jazyky](#supported-languages)
- [Minimálne požiadavky](#hardware-requirements)
- [Použitie](#instructions)
  - [Spustenie lokálne](#instructions)
    - [Spustenie webového rozhrania Gradio](#instructions)
    - [Základné použitie v režime headless](#basic-usage)
    - [Použitie vlastného modelu XTTS v režime headless](#example-of-custom-model-zip-upload)
    - [Výstup príkazu pomocníka](#help-command-output)
  - [Spustenie vzdialene](#run-remotely)
  - [Docker](#docker)
    - [Kroky na spustenie](#docker)
    - [Časté problémy s Dockerom](#common-docker-issues)
  
- [Doladené TTS modely](#fine-tuned-tts-models)
  - [Kolekcia doladených TTS modelov](#fine-tuned-tts-collection)
  - [Trénovanie XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Podporované formáty e-kníh](#supported-ebook-formats)
- [Výstupné formáty](#output-and-process-formats)
- [Návrat k staršej verzii](#reverting-to-older-versions)
- [Časté problémy](#common-issues)
- [Osobitné poďakovanie](#special-thanks)
- [Obsah](#table-of-contents)


## Funkcie
- 🔧 **Podporované TTS enginy**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Prevod viacerých formátov súborov**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Textové pole** na priamy prevod krátkeho textu na zvuk
- 🔍 **OCR skenovanie** pre súbory s textovými stránkami vo forme obrázkov
- 🔊 **Vysokokvalitný prevod textu na reč**, od takmer reálneho času po takmer skutočný hlas
- 🗣️ **Voliteľné klonovanie hlasu** pomocou vlastného hlasového súboru
- 🌐 **Podporuje 1158 jazykov** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Vhodné pre obmedzené zdroje** — beží na **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Výstupné formáty audioknihy**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Podpora SML tagov** — jemné ovládanie prerušení, páuz, prepínania hlasu a ďalšieho ([see below](#sml-tags-available))
- 🧩 **Voliteľný vlastný model** pomocou vášho vlastného natrénovaného modelu (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Doladené prednastavené modely** natrénované tímom E2A<br/>
     <i>(Kontaktujte nás, ak potrebujete ďalšie doladené modely, alebo ak chcete zdieľať tie svoje v oficiálnom zozname predvolieb)</i>


##  Hardvérové požiadavky
- 2 GB RAM min., 8 GB odporúčané.
- 1 GB VRAM min., 4 GB odporúčané.
- Povolená virtualizácia pri spustení vo Windows (iba Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Moderné TTS enginy sú na CPU veľmi pomalé, používajte teda TTS nižšej kvality ako YourTTS, Tacotron2 atď.</i>

## Podporované jazyky
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 jazykov a dialektov tu**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Podporované formáty e-kníh
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Najlepšie výsledky**: `.epub` alebo `.mobi` pre automatickú detekciu kapitol

## Formáty výstupu a spracovania
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Formát spracovania je možné zmeniť v lib/conf.py

## Dostupné SML tagy
- `[break]` — ticho (náhodný rozsah **0.3–0.6 sec.**)
- `[pause]` — ticho (náhodný rozsah **1.0–1.6 sec.**)
- `[pause:N]` — pevná pauza (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — prepnutie hlasu z predvoleného alebo vybraného hlasu z GUI/CLI

**Pozrite si náš ďalší repozitár venovaný automatickému pridávaniu SML do vašej e-knihy -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**Skôr než nahlásite problém s inštaláciou alebo chybu, dôkladne prehľadajte záložku otvorených a uzavretých issues<br>
aby ste sa uistili, že váš problém ešte neexistuje.**

>[!NOTE]
**Formát EPUB postráda akúkoľvek štandardnú štruktúru definujúcu, čo je kapitola, odsek, predslov atď.<br>
Preto by ste mali najprv ručne odstrániť všetok text, ktorý nechcete prevádzať na zvuk.**


### Pokyny 
1. **Naklonujte repozitár**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Nainštalujte / Spustite ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Poznámka pre používateľov macOS: na inštaláciu chýbajúcich programov sa inštaluje homebrew.</i>
     
   - **Spúšťač pre Mac**  
     Dvakrát kliknite na `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     alebo
     Dvakrát kliknite na `ebook2audiobook.cmd`

     <i>Poznámka pre používateľov Windows: na inštaláciu chýbajúcich programov bez administrátorských oprávnení sa inštaluje scoop.</i>
   
1. **Otvorte webovú aplikáciu**: Kliknite na adresu URL uvedenú v termináli pre prístup k webovej aplikácii a prevod e-kníh. `http://localhost:7860/`
2. **Pre verejný odkaz**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Ak je skript zastavený a znovu spustený, musíte obnoviť svoje grafické rozhranie Gradio<br>
aby sa webová stránka mohla znovu pripojiť k novému pripojovaciemu socketu.**

### Základné použitie
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Cesta k súboru vašej e-knihy
  - **[--voice]**: Cesta k súboru pre klonovanie hlasu (voliteľné)
  - **[--language]**: Kód jazyka v ISO-639-3 (napr.: ita pre taliančinu, eng pre angličtinu, deu pre nemčinu...).<br>
    Predvolený jazyk je eng a --language je voliteľný pre predvolený jazyk nastavený v ./lib/lang.py.<br>
    Podporované sú aj dvojpísmenové kódy ISO-639-1.


###  Príklad nahrania vlastného modelu ako zip
  (musí to byť súbor .zip obsahujúci povinné súbory modelu. Príklad pre XTTSv2: config.json, model.pth, vocab.json a ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Poznámka: ref.wav vášho vlastného modelu je vždy hlas vybraný na prevod</i>
     
- **<custom_model_path>**: Cesta k súboru `model_name.zip`,
      ktorý musí obsahovať (podľa TTS enginu) všetky povinné súbory<br>
      (pozri ./lib/models.py).

### Pre podrobného sprievodcu so zoznamom všetkých parametrov na použitie
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Alebo pre všetky operačné systémy**
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

POZNÁMKA: v režime gradio/gui zrušíte prebiehajúci prevod jednoducho kliknutím na [X] v komponente na nahranie e-knihy.
TIP: ak je potrebná o niečo dlhšia pauza, pridajte '[pause:3]' pre 3 s atď.

### Docker
1. **Naklonujte repozitár**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Zostavte kontajner**
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
4. **Spustite kontajner:**
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
- POZNÁMKA: MPS nie je v Dockeri dostupné, preto je nutné použiť CPU
  
### Časté problémy s Dockerom
- Moje GPU NVIDIA nie je detekované?? -> [Wiki stránka PROBLÉMY S GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Doladené (fine-tuned) TTS modely
#### Doláďte svoj vlastný model XTTSv2

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Odšumenie tréningových dát

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Kolekcia doladených TTS modelov

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Pre vlastný model XTTSv2 je povinný referenčný zvukový klip hlasu:

## Vaša vlastná úprava Ebook2Audiobook
Môžete ľubovoľne upravovať libs/conf.py a pridávať či odstraňovať nastavenia, ktoré chcete. Ak to plánujete, jednoducho si urobte
kópiu pôvodného conf.py, aby ste pri každej aktualizácii ebook2audiobook mohli zálohovať svoj upravený conf.py a vrátiť
pôvodný. Rovnaký postup musíte naplánovať aj pre models.py. Ak chcete zo svojho vlastného modelu
urobiť oficiálny doladený model ebook2audiobook, kontaktujte nás a my ho pridáme do zoznamu predvolieb.

## Návrat k starším verziám
Vydania nájdete -> [tu](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Časté problémy:
- Moje GPU NVIDIA/ROCm/XPU/MPS nie je detekované?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU je pomalé (lepšie na serverovom SMP CPU), zatiaľ čo GPU môže mať takmer prevod v reálnom čase.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Nemá však klonovanie hlasu zero-shot a hlasy sú kvality Siri, ale na CPU je oveľa rýchlejšie).
- „Mám problémy so závislosťami“ - Použite jednoducho Docker, je úplne samostatný a má režim headless,
   pre viac informácií pridajte na koniec príkazu docker run parameter `--help`.
- „Mám problém s oREZaným zvukom!“ - PROSÍM, NAHLÁSTE TO AKO ISSUE,
   nehovoríme každým jazykom a potrebujeme rady používateľov, aby sme doladili logiku delenia viet.😊

## ***** PLÁN ROZVOJA *****
- Všetky funkcie otvorené verejným príspevkom ⭐
- Akákoľvek pomoc od ľudí hovoriacich niektorým z podporovaných jazykov, aby nám pomohli vylepšiť modely ⭐
- [x] Náhľad blokov/kapitol pred začatím prevodu
- [ ] Úprava po prevedenej vete pre chirurgickú zmenu textu
- [x] Integrácia SML tagov pre hlas, pauzu, prerušenie a ďalšie zmeny 
- [x] Informácie o parametroch -h -help v rôznych jazykoch
- [x] OCR skenovanie pre PDF / JPG / BMP / PNG / TIFF
- [x] Priečinok notebookov [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Zabezpečiť, aby delenie čínskeho textu nerozdeľovalo slová, a zlepšiť načasovanie páuz [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] [Vytvoriť aplikáciu pre iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Vytvoriť aplikáciu pre Android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Integrácia s Audiobookshelf

#### Ďalšie možnosti
- [x] Možnosť prekladu e-knihy
- [x] Možnosti výstupného formátu
- [x] Dávkový priečinok e-kníh
- [x] Prevod s multiprocessingom
- [x] Dávkový prevod priečinka e-kníh
- [x] Detekcia zariadenia GPU
- [x] Odšumenie ľubovoľného referenčného zvuku pre nahrané klonovanie hlasu,
- [x] Nahranie vlastného modelu (zatiaľ iba XTTSv2. viac na vyžiadanie)
- [ ] Pridať jazykový model európskej portugalčiny aspoň pre xttsv2, fairseq, vits, piper (pomoc vítaná)
- [ ] Pridať jazykový model sindhčiny aspoň pre xttsv2, fairseq, vits, piper (pomoc vítaná)

#### TTS enginy
- [x] XTTSv2
- [x] Bark
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Tortoise
- [x] GlowTTS
- [x] Piper-TTS
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] Kokoro-TTS
- [ ] Orpheus-TTS
- [ ] Zonos
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Style-TTS2
- [ ] GPT-SoVITS
- [ ] F5-TTS (https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/38#issuecomment-2453224267)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] Speedy-Speech
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Align-TTS
- [ ] Delightful-TTS
- [ ] Spark-TTS

#### Preklad súboru Readme
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

#### 🐍 Kompatibilita operačných systémov
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra nadštandard na trénovanie modelov a podobne (všetky podporované modely Coqui-tts a piper-tts v jednom jednoduchom príkaze) 
- Pre informácie o tomto: @DrewThomasson na tom v súčasnosti pracuje, [repozitár vo vývoji tu](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Vytvoriť ľahko použiteľné tréningové GUI pre všetky modely coqui-tts v tréningových receptoch vo formáte ljspeech [tu od coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informácie o normalizácii kódu Python pre prispievateľov
- žiadny prázdny riadok medzi kódom, okrem medzi funkciami a triedami.
- jednoduché úvodzovky použité pre všetky kľúče okrem dict() a json. dict['key'] vždy volaný s jednoduchými úvodzovkami
- odsadenie 4 medzery, vôbec žiadne tabulátory
- striktné typovanie pre všetky funkcie a deklaráciu ich argumentov a návratových hodnôt
- žiadna medzera medzi argumentom a jeho typovaním, žiadna medzera medzi funkciou, „->“ a návratovou hodnotou

Príklad:

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

## Hľadáme darovanie hardvéru na beta testy
Prijímame akýkoľvek druh hardvéru na testovanie nášho vývoja, ako napríklad:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson, ak chcete akokoľvek pomôcť! 😃
<!--
## Potrebujete si prenajať GPU na posilnenie našej služby?
- Anketa je otvorená tu https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Osobitné poďakovanie
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 za lepšiu metódu ukladania kapitol](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
