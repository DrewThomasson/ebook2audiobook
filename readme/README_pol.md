<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Konwerter CPU/GPU z e-booka na audiobook z rozdziałami i metadanymi<br/>
z wykorzystaniem zaawansowanych silników TTS i nie tylko.<br/>
Obsługuje klonowanie głosu i 1696 języków!
> [!IMPORTANT]
**To narzędzie jest przeznaczone wyłącznie do użytku z e-bookami bez DRM, nabytymi legalnie.** <br>
Autorzy nie ponoszą odpowiedzialności za jakiekolwiek niewłaściwe użycie tego oprogramowania ani za wynikające z tego konsekwencje prawne. <br>
Korzystaj z tego narzędzia odpowiedzialnie i zgodnie ze wszystkimi obowiązującymi przepisami.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Dziękujemy za wsparcie twórców ebook2audiobook!
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### Uruchamianie lokalne
[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)redakcyjne
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### Uruchamianie zdalne
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### Interfejs graficzny (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Kliknij, aby zobaczyć obrazy interfejsu webowego</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
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

<a id="table-of-contents"></a>
## Spis treści
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
## Funkcje
- 🔧 **Obsługiwane silniki TTS**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Konwersja wielu formatów plików**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Pole tekstowe** do bezpośredniej konwersji krótkiego tekstu na audio
- 🔍 **Skanowanie OCR** dla plików ze stronami tekstu w postaci obrazów
- 🔊 **Wysokiej jakości zamiana tekstu na mowę**, od niemal czasu rzeczywistego po niemal naturalny głos
- 🗣️ **Opcjonalne klonowanie głosu** przy użyciu własnego pliku głosowego
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Przyjazny dla ograniczonych zasobów** — działa na **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Formaty wyjściowe audiobooka**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Obsługa znaczników SML** — precyzyjna kontrola przerw, pauz, zmiany głosu i nie tylko ([see below](#sml-tags-available))
- 🧩 **Opcjonalny własny model** przy użyciu własnego wytrenowanego modelu (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Dostrojone modele gotowe** wytrenowane przez zespół E2A<br/>
     <i>(Skontaktuj się z nami, jeśli potrzebujesz dodatkowych dostrojonych modeli lub jeśli chcesz udostępnić własne na oficjalnej liście gotowych ustawień)</i>


<a id="hardware-requirements"></a>
##  Wymagania sprzętowe
- 2 GB RAM min., 8 GB zalecane.
- 1 GB VRAM min., 4 GB zalecane.
- Włączona wirtualizacja przy uruchamianiu w systemie Windows (tylko Docker).
- CPU, XPU (Intel, AMD, ARM)*.
- Cuda, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Nowoczesne silniki TTS są bardzo wolne na CPU, więc używaj TTS o niższej jakości, takich jak YourTTS, Tacotron2 itd.</i>

<a id="supported-languages"></a>
## Obsługiwane języki
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## Obsługiwane formaty e-booków
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Najlepsze rezultaty**: `.epub` lub `.mobi` dla automatycznego wykrywania rozdziałów

<a id="output-and-process-formats"></a>
## Formaty wyjściowe i przetwarzania
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Format przetwarzania można zmienić w lib/conf.py

## Dostępne znaczniki SML
- `[break]` — cisza (losowy zakres **0.3–0.6 sec.**)
- `[pause]` — cisza (losowy zakres **1.0–1.6 sec.**)
- `[pause:N]` — stała pauza (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — przełączenie głosu z domyślnego lub wybranego z GUI/CLI
- `[emotion:sadness]...[/emotion]` — Tylko strefy: emocje związane z przejściem (szczęście, smutek, wstręt, strach, zaskoczenie, złość, inne, neutralne) lub mieszanka jak `[emotion:sadness=0.7,neutral=0.3]`; inne silniki ignorują je

**Sprawdź nasze inne repozytorium poświęcone automatycznemu dodawaniu SML w Twoim e-booku -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Zanim zgłosisz problem z instalacją lub błąd, przeszukaj dokładnie zakładkę z otwartymi i zamkniętymi zgłoszeniami<br>
aby upewnić się, że Twój problem jeszcze nie istnieje.**

Uwaga
**Format EPUB nie posiada żadnej standardowej struktury określającej, czym jest rozdział, akapit, przedmowa itd.<br>
Dlatego najpierw należy ręcznie usunąć wszelki tekst, którego nie chcesz konwertować na audio.**


<a id="instructions"></a>
### Instrukcje
1. **Klonuj repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Zainstaluj / Uruchom ebook2audiobook**:

   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Uwaga dla użytkowników systemu MacOS: homebrew jest instalowany w celu zainstalowania brakujących programów.</i>
     
   - **Launcher dla Maca**  
     Kliknij dwukrotnie `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     lub
     Kliknij dwukrotnie `ebook2audiobook.cmd`

     <i>Uwaga dla użytkowników Windows: scoop jest instalowany w celu zainstalowania brakujących programów bez uprawnień administratora.</i>
   
1. **Otwórz aplikację webową**: Kliknij adres URL podany w terminalu, aby uzyskać dostęp do aplikacji webowej i konwertować e-booki. `http://localhost:7860/`
2. **Aby uzyskać link publiczny**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (wszystkie systemy operacyjne, tylko po zainstalowaniu i z Pythonem z folderu python_env)

> [!IMPORTANT]
**Jeśli skrypt zostanie zatrzymany i uruchomiony ponownie, musisz odświeżyć swój interfejs graficzny Gradio<br>
aby strona internetowa mogła ponownie połączyć się z nowym gniazdem połączenia.**

<a id="basic-usage"></a>
### Operacje podstawowe
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


<a id="example-of-custom-model-zip-upload"></a>
###  Przykład przesyłania niestandardowego modelu w pliku ZIP
  (musi być plikiem .zip zawierającym obowiązkowe pliki modeli. Przykład dla XTTSv2: config.json, model.pth, vocab.json i ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Uwaga: ref.wav Twojego modelu niestandardowego jest zawsze głosem wybranym do konwersji</i>
     
- **<custom_model_path>**: Ścieżka do pliku `model_name.zip`,
      który musi zawierać (zależnie od silnika TTS) wszystkie obowiązkowe pliki<br>
      (zobacz ./lib/models.py).

### Szczegółowy przewodnik z listą wszystkich parametrów do użycia
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Lub dla wszystkich systemów operacyjnych**
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

UWAGA: w trybie gradio/gui, aby anulować trwającą konwersję, po prostu kliknij [X] w komponencie przesyłania e-booka.
WSKAZÓWKA: jeśli potrzebna jest dłuższa pauza, dodaj '[pause:3]' dla 3 sek. itd.

<a id="docker"></a>
### Docker
1. **Sklonuj repozytorium**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Zbuduj kontener**
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
4. **Uruchom kontener:**
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
- UWAGA: MPS nie jest udostępniany w Dockerze, więc należy użyć CPU
- UWAGA: nazwany wolumin `e2a_venvs` przechowuje silniki TTS zainstalowane we własnym venv (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM itp.)
  między kolejnymi uruchomieniami kontenera, więc nie są za każdym razem instalowane ponownie. Aby je zresetować: `docker volume rm e2a_venvs`

<a id="tools"></a>
## Narzędzia
Samodzielne narzędzia, uruchamiane za pomocą własnego Pythona e2a (`python_env`, stworzone przez pierwsze uruchomienie e2a).

<a id="preload-models"></a>
### Wstępne ładowanie modeli do instalacji offline: `tools/preload_models.py`
Pobiera każdy model używany przez e2a (silniki TTS i ich dostrojone wersje, konwersja głosu, stanza, pyannote, demucs,
interludia muzyczne, pakiety argos-translate, dane tesseract, jieba i głosy) do jednego folderu o układzie
dokładnie takim jak `./models`, np. na pamięci USB. Na komputerze offline skopiuj ten folder do `./models` e2a
a folder `voices` zapisany obok niego do `./voices` e2a.
Każde ukończone zadanie jest rejestrowane w `<models_dir>/.e2a_downloads.json`: ponowne uruchomienie pomija to, co zostało zrobione, i uruchamia
ponownie to, co zostało przerwane (ctrl-c, awaria, odłączony nośnik), po usunięciu jego częściowych plików.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` wymienia zadania i ich stan (wykonane, przerwane, do zrobienia) bez pobierania czegokolwiek.

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
### Przetłumacz ebooki z e2a: `tools/translate_ebook.sh`/`tools/translate_ebook.cmd`
Tłumaczy pliki EPUB/AZW3, cały folder (`-r` dla jego podfolderów) lub listę ścieżek (`@list.txt`)
na przetłumaczone e-booki, offline, z wtyczką Argos Translate calibre dostarczoną w
`tools/argostranslate-calibre-plugin.zip`. Niezależnie od konwersji audiobooka: zapisuje tylko ebooki.
Wymaga programu calibre (już wymaganego przez e2a) i działa na `python_env` oraz pakietach argos-translate e2a:
para językowa, której e2a już używa, nie jest ponownie pobierana, brakująca jest pobierana przy pierwszym użyciu.
Wtyczka jest instalowana przy pierwszym użyciu we własnym profilu calibre e2a (`./run`), Twój calibre pozostaje nietknięty.
`--to fra,ara,spa` tłumaczy na kilka języków jednocześnie, po jednym ebooku na język, a `--to all` na każdy
język osiągalny ze źródła (`--from`, w przeciwnym razie język każdej książki; tylko zainstalowane z `--no_download`).
`--list --from eng` wymienia języki, na które tłumaczy się z angielskiego (zainstalowane, do pobrania lub przez angielski dla
innego źródła).
Inne formaty odczytywane przez `ebook-convert` z calibre (PDF, DOCX, MOBI, TXT, ...) są raz konwertowane do EPUB, przed
pierwszym językiem, i tłumaczone jako EPUB: `--from` jest potrzebny, gdy nie mają określonego języka, co często zdarza się w PDF i TXT.
Bez `-o` lub `--output_dir` każde tłumaczenie jest zapisywane obok swojej książki jako `<name>.<lang>.<ext>`,
a książka, której tłumaczenie już istnieje, jest pomijana (`--overwrite`, aby przetłumaczyć ją ponownie).
Skrypty uruchamiające w folderze `tools/` uruchamiają `tools/translate_ebook.py` z `python_env`, nic do aktywowania,
z dowolnego folderu (ścieżki względne są pobierane z miejsca, w którym są uruchamiane):
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Lub bezpośrednio za pomocą Pythona z `python_env`: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Uruchamiany z dowolnym innym Pythonem,
     skrypt uruchamia się ponownie z tym z `python_env`.
   - **Docker**: uruchom go wewnątrz kontenera e2a, np. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     ze ścieżkami widocznymi z kontenera.
   - **Prędkość**: argostranslate działa zgodnie z własnymi ustawieniami domyślnymi (CTranslate2 wybiera wątki i najszybszy typ obliczeniowy,
     int8 na CPU), a nie na 1 wątku e2a w float32. Ustaw `ARGOS_INTRA_THREADS` lub `ARGOS_COMPUTE_TYPE`, aby je zastąpić.

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
## Sklonowane głosy
Możesz przesłać dowolny dźwięk głosowy w dowolnym obsługiwanym formacie audio, idealny czas trwania to około 1 do 5 min.
Nie ma znaczenia, czy nagranie ma głośne tło, czy odtwarzana jest nad nim muzyka — E2A wyczyści głos za Ciebie.

Wbudowana lista sklonowanych głosów jest głównie w języku angielskim. Jeśli chcesz, aby głosy w innych językach były oficjalnie
dodane do listy, skontaktuj się z nami, a my dodamy je po sprawdzeniu.

<a id="fine-tuned-tts-models"></a>
## Dostrojone (fine-tuned) modele TTS
<a id="fine-tune-your-own-tts-model"></a>
#### Precyzyjne dostrojenie własnego modelu TTS

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Odszumianie danych treningowych

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### Kolekcja dostrojonych modeli TTS

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Dla własnego modelu XTTSv2 obowiązkowy jest referencyjny klip audio z głosem:

## Twoja własna personalizacja Ebook2Audiobook
Możesz dowolnie modyfikować libs/conf.py, aby dodać lub usunąć żądane ustawienia. Jeśli planujesz to zrobić, po prostu wykonaj
kopię oryginalnego conf.py, aby przy każdej aktualizacji ebook2audiobook móc zachować swój zmodyfikowany conf.py i przywrócić
oryginalny. Musisz zaplanować ten sam proces dla models.py. Jeśli chcesz, aby Twój własny model
stał się oficjalnym dostrojonym modelem ebook2audiobook, skontaktuj się z nami, a dodamy go do listy gotowych ustawień.

<a id="reverting-to-older-versions"></a>
## Powrót do starszych wersji
Wydania można znaleźć -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## Częste problemy:
- Moja karta GPU NVIDIA/ROCm/XPU/MPS nie jest wykrywana?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU jest wolne (lepsze na serwerowym CPU SMP), podczas gdy GPU może zapewnić konwersję niemal w czasie rzeczywistym.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Nie ma jednak klonowania głosu zero-shot, a głosy są jakości Siri, ale jest znacznie szybsze na CPU).
- „Mam problemy z zależnościami” - Po prostu użyj Dockera, jest w pełni samodzielny i ma tryb headless,
   dodaj parametr  na końcu polecenia docker run, aby uzyskać więcej informacji. `--help`
- „Mam problem z przyciętym dźwiękiem!” - PROSIMY O ZGŁOSZENIE TEGO JAKO ISSUE,
   nie mówimy w każdym języku i potrzebujemy porad użytkowników, aby dostroić logikę dzielenia zdań.😊

## ***** PLAN ROZWOJU *****
- Wszystkie funkcje otwarte na publiczne wkłady ⭐
- Wszelka pomoc od osób mówiących w którymkolwiek z obsługiwanych języków, aby pomóc nam ulepszać modele ⭐
- [x] Podgląd bloków/rozdziałów przed rozpoczęciem konwersji
- [x] Edycja według przekonwertowanego zdania dla chirurgicznej zmiany tekstu
- [x] Generuj muzyczne intro, interludia i zakończenia; edytuj interludia i zakończenia
- [x] Integracja znaczników SML dla głosu, pauzy, przerwy i innych zmian
- [x] Informacje o parametrach -h -help w różnych językach
- [x] Skanowanie OCR dla PDF / JPG / BMP / PNG / TIFF
- [x] Folder notebooków [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Sprawić, by dzielenie tekstu chińskiego nie rozdzielało słów i poprawić synchronizację pauz [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker Compose
- [x] Podman komponuje
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [x] Integracja z Audiobookshelf
- [x] Opcja tłumaczenia e-booka
- [x] Wybór formatu wyjściowego
- [x] Konwersja wieloprocesowa
- [x] Wsadowa konwersja folderu e-booków
- [x] Wykrywanie urządzenia GPU
- [x] Usuń szumy z dowolnego dźwięku referencyjnego w tle do przesyłania klonowania głosu
- [x] Niestandardowe, dopracowane przesyłanie modelu

#### Prośby użytkowników
- [ ] Dodać model języka portugalskiego europejskiego przynajmniej dla xttsv2, fairseq, vits, piper (pomoc mile widziana)
- [ ] Dodać model języka sindhi przynajmniej dla xttsv2, fairseq, vits, piper (pomoc mile widziana)

#### Silniki TTS
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
- [x] Indeks-tts / Indeks TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Confucius4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Kropki TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Sroka TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Kieszeń TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Żółw (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Strefy (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Kora (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Tłumaczenie pliku Readme
- [x] Arabski (ara)
- [x] Chiński (zho)
- [x] Angielski (ENG)
- [x] Hiszpański (spa)
- [x] Francuski (fra)
- [x] Niemiecki (deu)
- [x] Włoski (ita)
- [x] Portugalski (por)
- [x] Polski (pol)
- [x] Turecki (tur)
- [x] Rosyjski (Rus)
- [x] Holenderski (nld)
- [x] Czeski (ces)
- [x] Japoński (jpn)
- [x] Hindi (hin)
- [x] Bengalski (ben)
- [x] Węgierski (hun)
- [x] Koreański (kor)
- [x] Wietnamski (Vie)
- [x] Szwedzki (Swe)
- [x] Perski (fas)
- [x] Joruba (yor)
- [x] Suahili (swa)
- [x] Indonezyjski (ind)
- [x] Słowacki (slk)
- [x] Chorwacki (hrv)

#### Zgodność z systemem operacyjnym
- [x] 🪟 Windows x86
- [x] 🪟 ARM Windows
- [x] 🍎 Mac Intel x86
- [x] Apple silicon
- [x] 🐧 Linux x86
- [x] 🐧 UZBRÓJ LINUXA

**********

<a id="contributing"></a>
## Współpraca
Przed otwarciem zgłoszenia lub pull requesta przeczytaj [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md): Zasady normalizacji kodu Python,
przepływ pracy z odgałęzieniami i pull requestami, legendy GUI i tłumaczenia README, dodawanie silnika TTS, testowanie.

## Poszukiwana darowizna sprzętu na testy beta
Przyjmujemy każdy rodzaj sprzętu do testowania naszego rozwoju, taki jak:
- Nvidia wspiera cuda >= 11,8
- Karty wywiadowcze XPU
- Karty ROCm AMD obsługujące ROCm >=5,7

@DrewThomasson jeśli chcesz w jakikolwiek sposób pomóc! 😃
<!--
## Czy potrzebujesz wynająć GPU, aby przyspieszyć naszą usługę?
- Ankieta jest otwarta tutaj https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Twórcy
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) - Zestaw narzędzi do głębokiego uczenia się do zamiany tekstu na mowę, sprawdzony w badaniach i produkcji.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) - Szybki i lokalny neuronowy silnik przekształcania tekstu na mowę.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- kod wnioskowania ggml dla Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) - Uniwersalny, czysty silnik wnioskowania C++ dla modeli audio, zasilany przez ggml.

<a id="special-thanks"></a>
## Specjalne podziękowania
Dla wszystkich współtwórców finansowych i kodowych każdy wkład i sugestia pomaga poprawić jakość E2A.