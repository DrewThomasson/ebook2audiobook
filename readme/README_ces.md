# 📚 ebook2audiobook (E2A)
CPU/GPU převodník z e-knihy na audioknihu s kapitolami a metadaty<br/>
s využitím pokročilých TTS enginů a mnoha dalšího.<br/>
Podporuje klonování hlasu a 1158 jazyků!
> [!IMPORTANT]
**Tento nástroj je určen pouze pro použití s e-knihami bez DRM, získanými legálně.** <br>
Autoři nenesou odpovědnost za jakékoli zneužití tohoto softwaru ani za případné právní následky. <br>
Používejte tento nástroj zodpovědně a v souladu se všemi platnými zákony.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Děkujeme za podporu vývojářů ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Spuštění lokálně

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Spuštění vzdáleně
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Grafické rozhraní (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Klikněte pro zobrazení obrázků webového GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Ukázky

**Ukázka nového výchozího hlasu**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Více ukázek</summary>

**Hlas ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Hlas deštivého dne**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Hlas Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Hlas Davida Attenborougha** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Příklad**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Obsah
- [ebook2audiobook](#-ebook2audiobook)
- [Funkce](#features)
- [Grafické rozhraní](#gui-interface)
- [Ukázky](#demos)
- [Podporované jazyky](#supported-languages)
- [Minimální požadavky](#hardware-requirements)
- [Použití](#instructions)
  - [Spuštění lokálně](#instructions)
    - [Spuštění webového rozhraní Gradio](#instructions)
    - [Základní použití v režimu headless](#basic-usage)
    - [Použití vlastního modelu XTTS v režimu headless](#example-of-custom-model-zip-upload)
    - [Výstup příkazu nápovědy](#help-command-output)
  - [Spuštění vzdáleně](#run-remotely)
  - [Dokovací stanice](#docker)
    - [Kroky ke spuštění](#docker)
  
- [Klonované hlasy](#cloned-voices)
- [Doladěné TTS modely](#fine-tuned-tts-models)
  - [Kolekce doladěných TTS modelů](#fine-tuned-tts-collection)
  - [Trénování XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Podporované formáty e-knih](#supported-ebook-formats)
- [Výstupní formáty](#output-and-process-formats)
- [Návrat ke starší verzi](#reverting-to-older-versions)
- [Časté problémy](#common-issues)
- [Zvláštní poděkování](#special-thanks)
- [Obsah](#table-of-contents)


## Funkce
- 🔧 **Podporované TTS enginy**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Převod více formátů souborů**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Textové pole** pro přímý převod krátkého textu na zvuk
- 🔍 **OCR skenování** pro soubory s textovými stránkami ve formě obrázků
- 🔊 **Vysoce kvalitní převod textu na řeč**, od téměř reálného času po téměř skutečný hlas
- 🗣️ **Volitelné klonování hlasu** pomocí vlastního hlasového souboru
- 🌐 **Podporuje 1158 jazyků** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Vhodné pro omezené zdroje** — běží na **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Výstupní formáty audioknihy**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Podpora SML tagů** — jemné ovládání přerušení, pauz, přepínání hlasu a dalšího ([see below](#sml-tags-available))
- 🧩 **Volitelný vlastní model** pomocí vašeho vlastního natrénovaného modelu (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Doladěné přednastavené modely** natrénované týmem E2A<br/>
     <i>(Kontaktujte nás, pokud potřebujete další doladěné modely, nebo pokud chcete sdílet ty své v oficiálním seznamu předvoleb)</i>


##  Hardwarové požadavky
- 2 GB RAM min., 8 GB doporučeno.
- 1 GB VRAM min., 4 GB doporučeno.
- Povolená virtualizace při spuštění ve Windows (pouze Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Moderní TTS enginy jsou na CPU velmi pomalé, používejte tedy TTS nižší kvality jako YourTTS, Tacotron2 atd.</i>

## Podporované jazyky
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 jazyků a dialektů zde**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Podporované formáty e-knih
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Nejlepší výsledky**: `.epub` nebo `.mobi` pro automatickou detekci kapitol

## Formáty výstupu a zpracování
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Formát zpracování lze změnit v lib/conf.py

## Dostupné SML tagy
- `[break]` — ticho (náhodný rozsah **0.3–0.6 sec.**)
- `[pause]` — ticho (náhodný rozsah **1.0–1.6 sec.**)
- `[pause:N]` — pevná pauza (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — přepnutí hlasu z výchozího nebo vybraného hlasu z GUI/CLI

**Podívejte se na náš další repozitář věnovaný automatickému přidávání SML do vaší e-knihy -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Než nahlásíte problém s instalací nebo chybu, pečlivě prohledejte záložku otevřených a uzavřených issues<br>
abyste se ujistili, že váš problém ještě neexistuje.**

>[!NOTE]
**Formát EPUB postrádá jakoukoli standardní strukturu definující, co je kapitola, odstavec, předmluva atd.<br>
Proto byste měli nejprve ručně odstranit veškerý text, který nechcete převádět na zvuk.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Nainstalujte / Spusťte ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Spouštěč pro Mac**  
     Dvakrát klikněte na `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Poznámka pro uživatele Windows: pro instalaci chybějících programů bez administrátorských oprávnění se instaluje scoop.</i>
   
1. **Otevřete webovou aplikaci**: Klikněte na adresu URL uvedenou v terminálu pro přístup k webové aplikaci a převod e-knih. `http://localhost:7860/`
2. **Pro veřejný odkaz**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Pokud je skript zastaven a znovu spuštěn, musíte obnovit své grafické rozhraní Gradio<br>
aby se webová stránka mohla znovu připojit k novému připojovacímu socketu.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Cesta k souboru vaší e-knihy
  - **[--voice]**: Cesta k souboru pro klonování hlasu (volitelné)
  - **[--language]**: Kód jazyka v ISO-639-3 (např.: ita pro italštinu, eng pro angličtinu, deu pro němčinu...).<br>
    Výchozí jazyk je eng a --language je volitelný pro výchozí jazyk nastavený v ./lib/lang.py.<br>
    Podporovány jsou také dvoupísmenné kódy ISO-639-1.


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
     
- **<custom_model_path>**: Cesta k souboru `model_name.zip`,
      který musí obsahovat (podle TTS enginu) všechny povinné soubory<br>
      (viz ./lib/models.py).

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

POZNÁMKA: v režimu gradio/gui zrušíte probíhající převod jednoduše kliknutím na [X] v komponentě pro nahrání e-knihy.
TIP: pokud je potřeba o něco delší pauza, přidejte '[pause:3]' pro 3 s atd.

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

## Klonované hlasy
Můžete nahrát libovolný hlasový zvuk v kterémkoli z podporovaných zvukových formátů, ideální doba trvání je přibližně 1 až 5 milionů.
Nezáleží na tom, jestli má nahrávka hlučné pozadí nebo přehrává hudbu — E2A vám hlas vyčistí.

Vestavěný seznam klonovaných hlasů je převážně v angličtině. Pokud potřebujete, aby hlasy v jiných jazycích byly oficiálně
přidáno do seznamu, kontaktujte nás a po kontrole je přidáme.

## Doladěné (fine-tuned) TTS modely
#### Dolaďte svůj vlastní model XTTSv2

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Odšumění tréninkových dat

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Kolekce doladěných TTS modelů

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Pro vlastní model XTTSv2 je povinný referenční zvukový klip hlasu:

## Vaše vlastní úprava Ebook2Audiobook
Můžete libovolně upravovat libs/conf.py a přidávat či odebírat nastavení, která chcete. Pokud to plánujete, jednoduše si udělejte
kopii původního conf.py, abyste při každé aktualizaci ebook2audiobook mohli zazálohovat svůj upravený conf.py a vrátit
původní. Stejný postup musíte naplánovat i pro models.py. Pokud chcete ze svého vlastního modelu
udělat oficiální doladěný model ebook2audiobook, kontaktujte nás a my jej přidáme do seznamu předvoleb.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Časté problémy:
- Moje GPU NVIDIA/ROCm/XPU/MPS není detekováno?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU je pomalé (lepší na serverovém SMP CPU), zatímco GPU může mít téměř převod v reálném čase.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Nemá však klonování hlasu zero-shot a hlasy jsou kvality Siri, ale na CPU je mnohem rychlejší).
- „Mám problémy se závislostmi“ - Použijte prostě Docker, je zcela samostatný a má režim headless,
   pro více informací přidejte na konec příkazu docker run parametr `--help`.
- „Mám problém s oříznutým zvukem!“ - PROSÍM, NAHLASTE TO JAKO ISSUE,
   nemluvíme každým jazykem a potřebujeme rady uživatelů, abychom doladili logiku dělení vět.😊

## ***** PLÁN ROZVOJE *****
- Všechny funkce otevřené veřejným příspěvkům ⭐
- Jakákoli pomoc od lidí mluvících některým z podporovaných jazyků, aby nám pomohli vylepšit modely ⭐
- [x] Náhled bloků/kapitol před zahájením převodu
- [ ] Úprava po převedené větě pro chirurgickou změnu textu
- [x] Integrace SML tagů pro hlas, pauzu, přerušení a další změny 
- [x] Informace o parametrech -h -help v různých jazycích
- [x] OCR skenování pro PDF / JPG / BMP / PNG / TIFF
- [x] Složka notebooků [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Zajistit, aby dělení čínského textu nerozdělovalo slova, a zlepšit načasování pauz [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] Integrace s Audiobookshelf
- [ ] [Vytvořit aplikaci pro iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Vytvořit aplikaci pro Android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Další možnosti
- [x] Možnost překladu e-knihy
- [x] Možnosti výstupního formátu
- [x] Dávková složka e-knih
- [x] Převod s multiprocessingem
- [x] Dávkový převod složky e-knih
- [x] Detekce zařízení GPU
- [x] Odšumění libovolného referenčního zvuku pro nahrané klonování hlasu,
- [x] Nahrání vlastního modelu (zatím pouze XTTSv2. více na vyžádání)
- [ ] Přidat jazykový model evropské portugalštiny alespoň pro xttsv2, fairseq, vits, piper (pomoc vítána)
- [ ] Přidat jazykový model sindhštiny alespoň pro xttsv2, fairseq, vits, piper (pomoc vítána)

#### Motory TTS
- [x] XTTSv2
- [x] Bark
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Želvovití
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SOVITS (https://github.com/RVC-Boss/GPT-SoVITS)
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
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Styl-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Překlad souboru Readme
- [x] Arabština (ara)
- [x] Čínština (zho)
- [x] English (eng)
- [x] Španělština (Spa)
- [x] Francouzština (fra)
- [x] Němčina (deu)
- [x] Italština (ita)
- [x] Portugalština (por)
- [x] Polština (pol)
- [x] Turečtina (tur)
- [x] Ruština (rus)
- [x] Holandština (nld)
- [x] Czech (ces)
- [x] Japonština (jpn)
- [x] Hindština (hin)
- [x] Bengálština (ben)
- [x] Maďarština (Hun)
- [x] Korejština (kor)
- [x] Vietnamština (vie)
- [x] Švédština (swe)
- [x] Perština (fas)
- [x] Yoruba (yor)
- [x] Svahilština (swa)
- [x] Indonéština (ind)
- [x] Slovenština (slk)
- [x] Chorvatština (hrv)

#### 🐍 Kompatibilita operačních systémů
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra nadstandard pro trénování modelů a podobně (všechny podporované modely Coqui-tts a piper-tts v jednom snadném příkazu) 
- Pro informace o tomto: @DrewThomasson na tom v současné době pracuje, [repozitář ve vývoji zde](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Vytvořit snadno použitelné tréninkové GUI pro všechny modely coqui-tts v tréninkových receptech ve formátu ljspeech [zde od coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informace o normalizaci kódu Python pro přispěvatele
- žádný prázdný řádek mezi kódem, kromě mezi funkcemi a třídami.
- jednoduché uvozovky použité pro všechny klíče kromě dict() a json. dict['key'] vždy volán s jednoduchými uvozovkami
- odsazení 4 mezery, vůbec žádné tabulátory
- striktní typování pro všechny funkce a deklaraci jejich argumentů a návratových hodnot
- žádná mezera mezi argumentem a jeho typováním, žádná mezera mezi funkcí, „->“ a návratovou hodnotou

Příklad:

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

## Hledáme darování hardwaru pro beta testy
Přijímáme jakýkoli druh hardwaru pro testování našeho vývoje, jako například:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson, pokud chcete jakkoli pomoci! 😃
<!--
## Potřebujete pronajmout GPU pro posílení naší služby?
- Anketa je otevřena zde https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Zvláštní poděkování
Pro všechny finanční a kódové přispěvatele každý příspěvek a návrh pomáhá zlepšit kvalitu E2A.