# 📚 ebook2audiobook (E2A)
CPU/GPU-omvandlare från e-bok till ljudbok med kapitel och metadata<br/>
med avancerade TTS-motorer och mycket mer.<br/>
Stöder röstkloning och 1158 språk!
> [!IMPORTANT]
**Detta verktyg är endast avsett att användas med DRM-fria, lagligt förvärvade e-böcker.** <br>
Författarna ansvarar inte för något missbruk av denna programvara eller för eventuella rättsliga följder. <br>
Använd detta verktyg ansvarsfullt och i enlighet med alla tillämpliga lagar.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Tack för att du stöder utvecklarna av ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Kör lokalt

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Kör på distans
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Grafiskt gränssnitt (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Klicka för att se bilder på webb-GUI:t</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demos

**Demo av den nya standardrösten**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Fler demos</summary>

**ASMR-röst** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Regnig dag-röst**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett-röst**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David Attenborough-röst** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Exempel**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Innehållsförteckning
- [ebook2audiobook](#-ebook2audiobook)
- [Funktioner](#features)
- [Grafiskt gränssnitt](#gui-interface)
- [Demos](#demos)
- [Språk som stöds](#supported-languages)
- [Minimikrav](#hardware-requirements)
- [Användning](#instructions)
  - [Kör lokalt](#instructions)
    - [Starta Gradio-webbgränssnittet](#instructions)
    - [Grundläggande användning i headless-läge](#basic-usage)
    - [Användning av anpassad XTTS-modell i headless-läge](#example-of-custom-model-zip-upload)
    - [Utdata från hjälpkommandot](#help-command-output)
  - [Kör på distans](#run-remotely)
  - [Docker](#docker)
    - [Steg för att köra](#docker)
  
- [Klonade röster](#cloned-voices)
- [Finjusterade TTS-modeller](#fine-tuned-tts-models)
  - [Samling av finjusterade TTS-modeller](#fine-tuned-tts-collection)
  - [Träna XTTSv2](#fine-tune-your-own-xttsv2-model)
- [E-boksformat som stöds](#supported-ebook-formats)
- [Utdataformat](#output-and-process-formats)
- [Återgå till en äldre version](#reverting-to-older-versions)
- [Vanliga problem](#common-issues)
- [Särskilt tack](#special-thanks)
- [Innehållsförteckning](#table-of-contents)


## Funktioner
- 🔧 **TTS-motorer som stöds**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Konvertera flera filformat**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Textområde** för att direkt konvertera en kort text till ljud
- 🔍 **OCR-skanning** för filer med textsidor som bilder
- 🔊 **Högkvalitativ text-till-tal**, från nära realtid till en nästan verklig röst
- 🗣️ **Valfri röstkloning** med din egen röstfil
- 🌐 **Stöder 1158 språk** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Resurssnål** — körs på **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Utdataformat för ljudbok**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML-taggar stöds** — finkornig kontroll av avbrott, pauser, röstbyte och mer ([see below](#sml-tags-available))
- 🧩 **Valfri anpassad modell** med din egen tränade modell (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Finjusterade förinställda modeller** tränade av E2A-teamet<br/>
     <i>(Kontakta oss om du behöver ytterligare finjusterade modeller, eller om du vill dela dina egna i den officiella förinställningslistan)</i>


##  Hårdvarukrav
- 2 GB RAM min., 8 GB rekommenderas.
- 1 GB VRAM min., 4 GB rekommenderas.
- Virtualisering aktiverad vid körning på Windows (endast Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon-CPU)

*<i> Moderna TTS-motorer är mycket långsamma på CPU, så använd TTS av lägre kvalitet som YourTTS, Tacotron2 osv.</i>

## Språk som stöds
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 språk och dialekter här**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## E-boksformat som stöds
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Bästa resultat**: `.epub` eller `.mobi` för automatisk kapiteldetektering

## Utdata- och bearbetningsformat
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Bearbetningsformatet kan ändras i lib/conf.py

## Tillgängliga SML-taggar
- `[break]` — tystnad (slumpmässigt intervall **0.3–0.6 sec.**)
- `[pause]` — tystnad (slumpmässigt intervall **1.0–1.6 sec.**)
- `[pause:N]` — fast paus (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — byt röst från standard- eller vald röst från GUI/CLI

**Kolla in vårt andra repo som är dedikerat till att lägga till SML automatiskt i din e-bok -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Innan du rapporterar ett installations- eller buggproblem, sök noggrant i fliken med öppna och stängda ärenden<br>
för att vara säker på att ditt problem inte redan finns.**

>[!NOTE]
**EPUB-formatet saknar all standardstruktur för vad som är ett kapitel, ett stycke, ett förord osv.<br>
Du bör därför först manuellt ta bort all text som du inte vill omvandla till ljud.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Installera / Kör ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac-startprogram**  
     Dubbelklicka på `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Notera för Windows-användare: scoop installeras för att installera saknade program utan administratörsbehörighet.</i>
   
1. **Öppna webbappen**: Klicka på URL:en som anges i terminalen för att komma åt webbappen och konvertera e-böcker. `http://localhost:7860/`
2. **För en offentlig länk**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Om skriptet stoppas och körs igen måste du uppdatera ditt Gradio-GUI-gränssnitt<br>
så att webbsidan kan återansluta till den nya anslutningssocketen.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Sökväg till din e-boksfil
  - **[--voice]**: Sökväg till fil för röstkloning (valfritt)
  - **[--language]**: Språkkod i ISO-639-3 (dvs.: ita för italienska, eng för engelska, deu för tyska...).<br>
    Standardspråket är eng och --language är valfritt för standardspråket som anges i ./lib/lang.py.<br>
    De tvåbokstaviga ISO-639-1-koderna stöds också.


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
     
- **<custom_model_path>**: Sökväg till filen `model_name.zip`,
      som måste innehålla (beroende på TTS-motorn) alla obligatoriska filer<br>
      (se ./lib/models.py).

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

NOTERA: i gradio/gui-läget avbryter du en pågående konvertering genom att helt enkelt klicka på [X] i komponenten för e-boksuppladdning.
TIPS: om det behövs lite mer paus, lägg till '[pause:3]' för 3 sek. osv.

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

## Klonade röster
Du kan ladda upp valfritt röstljud i något av de ljudformat som stöds, den ideala varaktigheten är cirka 1 till 5 minuter.
Det spelar ingen roll om inspelningen har en bullrig bakgrund eller musik som spelas över den — E2A kommer att städa upp rösten åt dig.

Den inbyggda klonade röstlistan är huvudsakligen på engelska. Om du behöver röster på andra språk för att vara officiellt
tillagd i listan, vänligen kontakta oss så lägger vi till dem efter granskning.

## Finjusterade (fine-tuned) TTS-modeller
#### Finjustera din egen XTTSv2-modell

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Brusreducera träningsdata

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Samling av finjusterade TTS-modeller

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

För en anpassad XTTSv2-modell är ett referensljudklipp av rösten obligatoriskt:

## Din egen anpassning av Ebook2Audiobook
Du är fri att ändra libs/conf.py för att lägga till eller ta bort de inställningar du vill. Om du planerar att göra det, gör helt enkelt
en kopia av den ursprungliga conf.py så att du vid varje ebook2audiobook-uppdatering kan säkerhetskopiera din ändrade conf.py och lägga
tillbaka originalet. Du måste planera samma process för models.py. Om du vill göra din egen anpassade modell
till en officiell finjusterad ebook2audiobook-modell, kontakta oss så lägger vi till den i förinställningslistan.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Vanliga problem:
- Min NVIDIA/ROCm/XPU/MPS-GPU upptäcks inte?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU:n är långsam (bättre på en server-SMP-CPU) medan GPU:n kan ha nästan realtidskonvertering.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Den har dock inte zero-shot-röstkloning, och rösterna är av Siri-kvalitet, men den är mycket snabbare på CPU).
- "Jag har problem med beroenden" - Använd bara Docker, den är helt fristående och har ett headless-läge,
   lägg till parametern `--help` i slutet av docker run-kommandot för mer information.
- "Jag har ett problem med avklippt ljud!" - VÄNLIGEN SKAPA ETT ÄRENDE OM DETTA,
   vi talar inte alla språk och behöver råd från användare för att finjustera logiken för meningsdelning.😊

## ***** FÄRDPLAN *****
- Alla funktioner öppna för offentliga bidrag ⭐
- All hjälp från personer som talar något av de språk som stöds för att hjälpa oss förbättra modellerna ⭐
- [x] Förhandsgranska block/kapitel innan konverteringen startar
- [ ] Redigering per konverterad mening för kirurgisk textändring
- [x] Integrering av SML-taggar för röst, paus, avbrott och fler ändringar 
- [x] Info om parametrarna -h -help på olika språk
- [x] OCR-skanning för PDF / JPG / BMP / PNG / TIFF
- [x] Notebooks-mapp [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Få kinesisk textdelning att inte dela ord och förbättra pausernas timing [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle-notebook
- [x] Google Colab-notebook
- [ ] Audiobookshelf-integrering
- [ ] [Skapa en iOS-app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Skapa en Android-app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Extra alternativ
- [x] Alternativ för e-boksöversättning
- [x] Val av utdataformat
- [x] Batch-e-boksmapp
- [x] Konvertering med multiprocessing
- [x] Batchkonvertering av en e-boksmapp
- [x] Detektering av GPU-enhet
- [x] Brusreducera valfritt referensljud för uppladdad röstkloning,
- [x] Uppladdning av anpassad modell (endast XTTSv2 för närvarande. mer på begäran)
- [ ] Lägg till en europeisk portugisisk språkmodell för åtminstone xttsv2, fairseq, vits, piper (hjälp välkomnas)
- [ ] Lägg till en sindhi-språkmodell för åtminstone xttsv2, fairseq, vits, piper (hjälp välkomnas)

#### TTS-motorer
- [x] XTTSv2
- [x] Bark
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Landsköldpaddor
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fisk-tal (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chattlåda (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonisk (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zoner (https://github.com/Zyphra/Zonos)
- [ ] Stil-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Readme-översättning
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

#### 🐍 Kompatibilitet med operativsystem
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra overkill för att träna modeller och liknande (alla Coqui-tts-modeller som stöds och piper-tts i ett enkelt kommando) 
- För information om detta: @DrewThomasson arbetar för närvarande med utvecklingen av detta, [pågående repo här](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Skapa ett lättanvänt tränings-GUI för alla coqui-tts-modeller i träningsrecepten i ljspeech-format [här från coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Information om normalisering av Python-kod för bidragsgivare
- ingen tom rad mellan koden, utom mellan funktioner och klasser.
- enkla citattecken används för alla nycklar utom för dict() och json. dict['key'] anropas alltid med enkla citattecken
- 4 mellanslags indrag, inga tabbar alls
- strikt typning för alla funktioner och deklarationen av deras argument och returvärden
- inget mellanslag mellan argumentet och dess typning, inget mellanslag mellan funktionen, "->" och returvärdet

Exempel:

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

## Hårdvarudonation för betatester sökes
Vi tar emot alla typer av hårdvara för att testa vår utveckling, till exempel:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson om du vill hjälpa till på något sätt! 😃
<!--
## Behöver du hyra en GPU för att förstärka vår tjänst?
- En omröstning är öppen här https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Särskilt tack
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 för en bättre metod att spara kapitel](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
