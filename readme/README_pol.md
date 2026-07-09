# 📚 ebook2audiobook (E2A)
Konwerter CPU/GPU z e-booka na audiobook z rozdziałami i metadanymi<br/>
z wykorzystaniem zaawansowanych silników TTS i nie tylko.<br/>
Obsługuje klonowanie głosu i 1158 języków!
> [!IMPORTANT]
**To narzędzie jest przeznaczone wyłącznie do użytku z e-bookami bez DRM, nabytymi legalnie.** <br>
Autorzy nie ponoszą odpowiedzialności za jakiekolwiek niewłaściwe użycie tego oprogramowania ani za wynikające z tego konsekwencje prawne. <br>
Korzystaj z tego narzędzia odpowiedzialnie i zgodnie ze wszystkimi obowiązującymi przepisami.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Dziękujemy za wsparcie twórców ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Uruchamianie lokalne

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Uruchamianie zdalne
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Interfejs graficzny (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Kliknij, aby zobaczyć obrazy interfejsu webowego</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Dema

**Demo nowego domyślnego głosu**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Więcej dem</summary>

**Głos ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Głos deszczowego dnia**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Głos Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Głos Davida Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Przykład**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Spis treści
- [ebook2audiobook](#-ebook2audiobook)
- [Funkcje](#features)
- [Interfejs graficzny](#gui-interface)
- [Dema](#demos)
- [Obsługiwane języki](#supported-languages)
- [Minimalne wymagania](#hardware-requirements)
- [Użycie](#instructions)
  - [Uruchamianie lokalne](#instructions)
    - [Uruchamianie interfejsu webowego Gradio](#instructions)
    - [Podstawowe użycie w trybie headless](#basic-usage)
    - [Użycie własnego modelu XTTS w trybie headless](#example-of-custom-model-zip-upload)
    - [Wynik polecenia pomocy](#help-command-output)
  - [Uruchamianie zdalne](#run-remotely)
  - [Docker](#docker)
    - [Kroki uruchamiania](#docker)
    - [Częste problemy z Dockerem](#common-docker-issues)
  
- [Dostrojone modele TTS](#fine-tuned-tts-models)
  - [Kolekcja dostrojonych modeli TTS](#fine-tuned-tts-collection)
  - [Trenowanie XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Obsługiwane formaty e-booków](#supported-ebook-formats)
- [Formaty wyjściowe](#output-and-process-formats)
- [Powrót do starszej wersji](#reverting-to-older-versions)
- [Częste problemy](#common-issues)
- [Specjalne podziękowania](#special-thanks)
- [Spis treści](#table-of-contents)


## Funkcje
- 🔧 **Obsługiwane silniki TTS**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Konwersja wielu formatów plików**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Pole tekstowe** do bezpośredniej konwersji krótkiego tekstu na audio
- 🔍 **Skanowanie OCR** dla plików ze stronami tekstu w postaci obrazów
- 🔊 **Wysokiej jakości zamiana tekstu na mowę**, od niemal czasu rzeczywistego po niemal naturalny głos
- 🗣️ **Opcjonalne klonowanie głosu** przy użyciu własnego pliku głosowego
- 🌐 **Obsługuje 1158 języków** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Przyjazny dla ograniczonych zasobów** — działa na **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Formaty wyjściowe audiobooka**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Obsługa znaczników SML** — precyzyjna kontrola przerw, pauz, zmiany głosu i nie tylko ([see below](#sml-tags-available))
- 🧩 **Opcjonalny własny model** przy użyciu własnego wytrenowanego modelu (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Dostrojone modele gotowe** wytrenowane przez zespół E2A<br/>
     <i>(Skontaktuj się z nami, jeśli potrzebujesz dodatkowych dostrojonych modeli lub jeśli chcesz udostępnić własne na oficjalnej liście gotowych ustawień)</i>


##  Wymagania sprzętowe
- 2 GB RAM min., 8 GB zalecane.
- 1 GB VRAM min., 4 GB zalecane.
- Włączona wirtualizacja przy uruchamianiu w systemie Windows (tylko Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Nowoczesne silniki TTS są bardzo wolne na CPU, więc używaj TTS o niższej jakości, takich jak YourTTS, Tacotron2 itd.</i>

## Obsługiwane języki
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 języków i dialektów tutaj**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Obsługiwane formaty e-booków
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Najlepsze rezultaty**: `.epub` lub `.mobi` dla automatycznego wykrywania rozdziałów

## Formaty wyjściowe i przetwarzania
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Format przetwarzania można zmienić w lib/conf.py

## Dostępne znaczniki SML
- `[break]` — cisza (losowy zakres **0.3–0.6 sec.**)
- `[pause]` — cisza (losowy zakres **1.0–1.6 sec.**)
- `[pause:N]` — stała pauza (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — przełączenie głosu z domyślnego lub wybranego z GUI/CLI

**Sprawdź nasze inne repozytorium poświęcone automatycznemu dodawaniu SML w Twoim e-booku -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Zanim zgłosisz problem z instalacją lub błąd, przeszukaj dokładnie zakładkę z otwartymi i zamkniętymi zgłoszeniami<br>
aby upewnić się, że Twój problem jeszcze nie istnieje.**

>[!NOTE]
**Format EPUB nie posiada żadnej standardowej struktury określającej, czym jest rozdział, akapit, przedmowa itd.<br>
Dlatego najpierw należy ręcznie usunąć wszelki tekst, którego nie chcesz konwertować na audio.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Zainstaluj / Uruchom ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Launcher dla Maca**  
     Kliknij dwukrotnie `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Uwaga dla użytkowników Windows: scoop jest instalowany w celu zainstalowania brakujących programów bez uprawnień administratora.</i>
   
1. **Otwórz aplikację webową**: Kliknij adres URL podany w terminalu, aby uzyskać dostęp do aplikacji webowej i konwertować e-booki. `http://localhost:7860/`
2. **Aby uzyskać link publiczny**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Jeśli skrypt zostanie zatrzymany i uruchomiony ponownie, musisz odświeżyć swój interfejs graficzny Gradio<br>
aby strona internetowa mogła ponownie połączyć się z nowym gniazdem połączenia.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Ścieżka do pliku e-booka
  - **[--voice]**: Ścieżka pliku do klonowania głosu (opcjonalnie)
  - **[--language]**: Kod języka w ISO-639-3 (np.: ita dla włoskiego, eng dla angielskiego, deu dla niemieckiego...).<br>
    Domyślny język to eng, a --language jest opcjonalny dla języka domyślnego ustawionego w ./lib/lang.py.<br>
    Obsługiwane są również 2-literowe kody ISO-639-1.


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
     
- **<custom_model_path>**: Ścieżka do pliku `model_name.zip`,
      który musi zawierać (zależnie od silnika TTS) wszystkie obowiązkowe pliki<br>
      (zobacz ./lib/models.py).

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

UWAGA: w trybie gradio/gui, aby anulować trwającą konwersję, po prostu kliknij [X] w komponencie przesyłania e-booka.
WSKAZÓWKA: jeśli potrzebna jest dłuższa pauza, dodaj '[pause:3]' dla 3 sek. itd.

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
  
### Częste problemy z Dockerem
- Moja karta NVIDIA nie jest wykrywana?? -> [Strona wiki PROBLEMY Z GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Dostrojone (fine-tuned) modele TTS
#### Dostrój własny model XTTSv2

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Odszumianie danych treningowych

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Kolekcja dostrojonych modeli TTS

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Dla własnego modelu XTTSv2 obowiązkowy jest referencyjny klip audio z głosem:

## Twoja własna personalizacja Ebook2Audiobook
Możesz dowolnie modyfikować libs/conf.py, aby dodać lub usunąć żądane ustawienia. Jeśli planujesz to zrobić, po prostu wykonaj
kopię oryginalnego conf.py, aby przy każdej aktualizacji ebook2audiobook móc zachować swój zmodyfikowany conf.py i przywrócić
oryginalny. Musisz zaplanować ten sam proces dla models.py. Jeśli chcesz, aby Twój własny model
stał się oficjalnym dostrojonym modelem ebook2audiobook, skontaktuj się z nami, a dodamy go do listy gotowych ustawień.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Częste problemy:
- Moja karta GPU NVIDIA/ROCm/XPU/MPS nie jest wykrywana?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU jest wolne (lepsze na serwerowym CPU SMP), podczas gdy GPU może zapewnić konwersję niemal w czasie rzeczywistym.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Nie ma jednak klonowania głosu zero-shot, a głosy są jakości Siri, ale jest znacznie szybsze na CPU).
- „Mam problemy z zależnościami” - Po prostu użyj Dockera, jest w pełni samodzielny i ma tryb headless,
   dodaj parametr `--help` na końcu polecenia docker run, aby uzyskać więcej informacji.
- „Mam problem z przyciętym dźwiękiem!” - PROSIMY O ZGŁOSZENIE TEGO JAKO ISSUE,
   nie mówimy w każdym języku i potrzebujemy porad użytkowników, aby dostroić logikę dzielenia zdań.😊

## ***** PLAN ROZWOJU *****
- Wszystkie funkcje otwarte na publiczne wkłady ⭐
- Wszelka pomoc od osób mówiących w którymkolwiek z obsługiwanych języków, aby pomóc nam ulepszać modele ⭐
- [x] Podgląd bloków/rozdziałów przed rozpoczęciem konwersji
- [ ] Edycja według przekonwertowanego zdania dla chirurgicznej zmiany tekstu
- [x] Integracja znaczników SML dla głosu, pauzy, przerwy i innych zmian 
- [x] Informacje o parametrach -h -help w różnych językach
- [x] Skanowanie OCR dla PDF / JPG / BMP / PNG / TIFF
- [x] Folder notebooków [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Sprawić, by dzielenie tekstu chińskiego nie rozdzielało słów i poprawić synchronizację pauz [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] [Stworzyć aplikację na iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Stworzyć aplikację na Androida](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Integracja z Audiobookshelf

#### Dodatkowe opcje
- [x] Opcja tłumaczenia e-booka
- [x] Wybór formatu wyjściowego
- [x] Wsadowy folder e-booków
- [x] Konwersja wieloprocesowa
- [x] Wsadowa konwersja folderu e-booków
- [x] Wykrywanie urządzenia GPU
- [x] Odszumianie dowolnego referencyjnego audio do przesyłanego klonowania głosu,
- [x] Przesyłanie własnego modelu (na razie tylko XTTSv2. więcej na życzenie)
- [ ] Dodać model języka portugalskiego europejskiego przynajmniej dla xttsv2, fairseq, vits, piper (pomoc mile widziana)
- [ ] Dodać model języka sindhi przynajmniej dla xttsv2, fairseq, vits, piper (pomoc mile widziana)

#### Silniki TTS
- [x] XTTSv2
- [x] Kora
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Żółwie
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] przemowa ryb (https://github.com/fishaudio/fish-speech)
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
- [ ] Strefy (https://github.com/Zyphra/Zonos)
- [ ] Styl-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Tłumaczenie pliku Readme
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

#### 🐍 Zgodność z systemami operacyjnymi
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Dodatkowy przerost dla trenowania modeli i nie tylko (wszystkie obsługiwane modele Coqui-tts oraz piper-tts w jednym prostym poleceniu) 
- Po informacje na ten temat: @DrewThomasson obecnie pracuje nad jego rozwojem, [repozytorium w trakcie prac tutaj](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Stworzyć łatwy w użyciu interfejs treningowy dla wszystkich modeli coqui-tts w przepisach treningowych w formacie ljspeech [tutaj od coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informacje o normalizacji kodu Python dla współtwórców
- brak pustej linii między kodem, z wyjątkiem między funkcjami i klasami.
- pojedynczy cudzysłów używany dla wszystkich kluczy z wyjątkiem dict() i json. dict['key'] zawsze wywoływany z pojedynczym cudzysłowem
- wcięcie 4 spacje, w ogóle bez tabulatorów
- ścisłe typowanie dla wszystkich funkcji oraz deklaracji ich argumentów i wartości zwracanych
- brak spacji między argumentem a jego typem, brak spacji między funkcją, „->” a wartością zwracaną

Przykład:

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

## Poszukiwana darowizna sprzętu na testy beta
Przyjmujemy każdy rodzaj sprzętu do testowania naszego rozwoju, taki jak:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson jeśli chcesz w jakikolwiek sposób pomóc! 😃
<!--
## Czy potrzebujesz wynająć GPU, aby przyspieszyć naszą usługę?
- Ankieta jest otwarta tutaj https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Specjalne podziękowania
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 za lepszą metodę zapisywania rozdziałów](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
