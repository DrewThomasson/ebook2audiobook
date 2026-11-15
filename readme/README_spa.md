<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Convertidor de CPU/GPU de libro electrónico a audiolibro con capítulos y metadatos<br/>
usando motores TTS avanzados y mucho más.<br/>
¡Admite la clonación de voz y 1696 idiomas!
> Importante
**Esta herramienta está diseñada para su uso con libros electrónicos adquiridos legalmente que no sean de DRM.** <br>
Los autores no son responsables de ningún uso indebido de este software ni de las consecuencias legales resultantes. <br>
Utilice esta herramienta de manera responsable y de acuerdo con todas las leyes aplicables.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### ¡Gracias por apoyar a los desarrolladores de ebook2audiobook!
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### Ejecutar localmente
0. Instrucciones [![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### Ejecutar de forma remota
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### g id="i1"Interfaz GUI/g
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Haga clic para ver imágenes de Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
## Demos

**Nueva demostración de voz predeterminada**

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Más Demos</summary>

**ASMR Voice**

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Voz de día lluvioso**

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett Voice**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Voz de David Attenborough**

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Ejemplo**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

<a id="table-of-contents"></a>
## Tabla de Contenidos
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
## Rasgos
- 🔧 **Motores TTS compatibles**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Convertir múltiples formatos de archivo**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **TextArea** para convertir directamente un texto corto en audio
- 🔍 **Escaneo OCR** para archivos con páginas de texto como imágenes
- 🔊 **Texto a voz de alta calidad** de voz casi en tiempo real a voz casi real
- 🗣️ **Clonación de voz opcional** con tu propio archivo de voz
- 🌐 **Admite 1696 idiomas** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Apto para personas con pocos recursos**: funciona con **2 GB de RAM / 1 GB de VRAM (mínimo)**
- 🎵 **Formatos de salida de audiolibros**: mono o estéreo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Etiquetas SML compatibles**: control detallado de descansos, pausas, conmutación de voz y más ([see below](#sml-tags-available))
- 🧩 **Modelo personalizado opcional** utilizando su propio modelo capacitado (XTTSv2, VITS, FAIRSEQ, PIPER, otros a pedido)
- 🎛️ **Modelos preestablecidos ajustados** entrenados por el equipo E2A<br/>
     <i>(Póngase en contacto con nosotros si necesita modelos adicionales ajustados o si desea compartir los suyos con la lista preestablecida oficial)</i>


<a id="hardware-requirements"></a>
##  Requisitos de hardware
- 2 GB RAM mín., se recomiendan 8 GB.
- VRAM mínima de 1 GB, se recomiendan 4 GB.
- Virtualización habilitada si se ejecuta en Windows (solo Docker).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon CPU)

*<i> Los motores TTS modernos son muy lentos en la CPU, así que use TTS de menor calidad como YourTTS, Tacotron2, etc.</i>

<a id="supported-languages"></a>
## Idiomas admitidos
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## Formatos de libros electrónicos compatibles
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Mejores resultados**: `.epub` o `.mobi` para la detección automática de capítulos

<a id="output-and-process-formats"></a>
## Formatos de salida y proceso
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- El formato del proceso se puede cambiar en lib/conf.py

## Etiquetas SML disponibles
- `[break]` — silencio (rango aleatorio **0,3-0,6 seg.**)
- `[pause]` — silencio (rango aleatorio **1.0–1.6 seg.**)
- `[pause:N]` — pausa fija (**N seg.**)
- `[voice:/path/to/voice/file]...[/voice]` — cambiar voz desde la predeterminada o la voz seleccionada desde GUI/CLI
- `[emotion:sadness]...[/emotion]` — Solo zonos: emoción por un pasaje (felicidad, tristeza, disgusto, miedo, sorpresa, enojo, otro, neutro) o una mezcla como `[emotion:sadness=0.7,neutral=0.3]`; otros motores lo ignoran

**Consulta nuestro otro repositorio dedicado a añadir SML automáticamente en tu libro electrónico -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> Importante
**Antes de publicar una instalación o un problema de error, busque cuidadosamente en la PESTAÑA de problemas abiertos y cerrados<br>
para asegurarte de que tu problema no exista ya.**

Nota
**El formato EPUB carece de una estructura estándar como lo que es un capítulo, párrafo, prefacio, etc.<br>
Por lo tanto, primero debes eliminar manualmente cualquier texto que no quieras que se convierta en audio.**


<a id="instructions"></a>
### Instrucciones
1. **Clonar el repositorio**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Instalar / ejecutar ebook2audiobook**:

   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Nota para usuarios de MacOS: se instala homebrew para instalar los programas que faltan.</i>
     
   - **Lanzador de Mac**
     Doble clic `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     o
     Haga doble clic en `ebook2audiobook.cmd`

     <i>Nota para usuarios de Windows: se instala scoop para instalar los programas que faltan sin privilegios de administrador.</i>
   
1. **Abra la aplicación web**: haga clic en la URL proporcionada en el terminal para acceder a la aplicación web y convertir libros electrónicos. `http://localhost:7860/`
2. **Para Enlace Público**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (todos los sistemas operativos, solo una vez instalado y con el Python de su carpeta python_env)

> Importante
**Si el script se detiene y se ejecuta de nuevo, debe actualizar la interfaz GUI de gradio<br>
para permitir que la página web se vuelva a conectar al nuevo socket de conexión.**

<a id="basic-usage"></a>
### Uso básico
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Ruta a su archivo de libro electrónico
  - **[--voice]**: Ruta del archivo de clonación de voz (opcional)
  - **[--language]**: Código de idioma en ISO-639-3 (es decir: ita para italiano, eng para inglés, deu para alemán...).<br>
    El idioma predeterminado es eng y --language es opcional para el idioma predeterminado establecido en ./lib/lang.py.<br>
    También se admiten los códigos ISO-639-1 de 2 letras.


<a id="example-of-custom-model-zip-upload"></a>
###  Ejemplo de carga de un modelo personalizado en zip
  (debe ser un archivo .zip que contenga los archivos obligatorios del modelo. Ejemplo para XTTSv2: config.json, model.pth, vocab.json y ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Nota: el ref.wav de su modelo personalizado es siempre la voz seleccionada para la conversión</i>
     
- **<custom_model_path>**: ruta al archivo `model_name.zip`,
      que debe contener (según el motor tts) todos los ficheros obligatorios<br>
      (ver ./lib/models.py).

### Guía detallada con la lista de todos los parámetros disponibles
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **O para todos los sistemas operativos**
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

NOTA: en el modo gradio/gui, para cancelar una conversión en ejecución, simplemente haga clic en la [X] del componente de carga de libros electrónicos.
CONSEJO: si necesita una pausa más, añada '[pause:3]' durante 3 segundos, etc.

<a id="docker"></a>
### Docker
1. **Clonar el repositorio**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Construir el contenedor**
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
4. **Ejecutar el contenedor:**
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
- NOTA: MPS no está expuesto en Docker, por lo que se debe usar la CPU
- NOTA: el volumen con nombre `e2a_venvs` conserva los motores TTS instalados en su propio venv (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM, etc.)
  entre ejecuciones del contenedor, para que no se reinstalen cada vez. Para restablecerlos: `docker volume rm e2a_venvs`

<a id="tools"></a>
## Herramientas
Herramientas independientes, ejecutadas con el Python propio de e2a (`python_env`, creado en el primer arranque de e2a).

<a id="preload-models"></a>
### Precargar modelos para instalaciones sin conexión: `tools/preload_models.py`
Descarga todos los modelos que usa e2a (motores TTS y sus fine-tunes, conversión de voz, stanza, pyannote, demucs,
interludios musicales, paquetes de argos-translate, datos de tesseract, jieba y las voces) en una sola carpeta organizada
exactamente como `./models`, por ejemplo una memoria USB. En la máquina sin conexión, copie esa carpeta en `./models` de e2a
y la carpeta `voices` escrita a su lado en `./voices` de e2a.
Cada tarea terminada se registra en `<models_dir>/.e2a_downloads.json`: una nueva ejecución omite lo que ya está hecho y vuelve a empezar
lo que se interrumpió (ctrl-c, fallo, memoria desconectada) tras eliminar sus archivos parciales.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` lista las tareas y su estado (hecha, interrumpida, pendiente) sin descargar nada.

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
### Traducir ebooks fuera de e2a: `tools/translate_ebook.sh` / `tools/translate_ebook.cmd`
Traduce archivos EPUB/AZW3, una carpeta completa (`-r` para sus subcarpetas) o una lista de rutas (`@list.txt`)
a ebooks traducidos, sin conexión, con el plugin de calibre Argos Translate incluido en
`tools/argostranslate-calibre-plugin.zip`. Independiente de la conversión a audiolibro: solo escribe ebooks.
Necesita calibre (ya requerido por e2a) y funciona con el `python_env` y los paquetes argos-translate de e2a:
un par de idiomas que e2a ya usa no se vuelve a descargar, uno que falta se descarga en el primer uso.
El plugin se instala en el primer uso en el perfil de calibre propio de e2a (`./run`), su calibre queda intacto.
`--to fra,ara,spa` traduce a varios idiomas a la vez, un ebook por idioma, y `--to all` a todos los
idiomas que alcanza el origen (`--from`, si no el idioma de cada libro; solo los pares instalados con `--no_download`).
`--list --from eng` lista los idiomas a los que traduce el inglés (instalados, descargables o a través del inglés para
otro origen).
Los demás formatos que lee `ebook-convert` de calibre (PDF, DOCX, MOBI, TXT, ...) se convierten a EPUB una sola vez, antes del
primer idioma, y se traducen como EPUB: `--from` es necesario cuando no indican idioma, como suele pasar con PDF y TXT.
Sin `-o` ni `--output_dir`, cada traducción se guarda junto a su libro como `<name>.<lang>.<ext>`,
y se omite un libro cuya traducción ya existe (`--overwrite` para volver a traducirlo).
Los lanzadores de la carpeta `tools/` ejecutan `tools/translate_ebook.py` con `python_env`, sin nada que activar,
desde cualquier carpeta (las rutas relativas se toman desde donde se inicia):
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - O directamente con el Python de `python_env`: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Si se inicia con cualquier otro Python,
     el script se vuelve a iniciar con el de `python_env`.
   - **Docker**: ejecútelo dentro del contenedor e2a, p. ej. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     con las rutas vistas desde el contenedor.
   - **Velocidad**: argostranslate usa sus propios valores por defecto (CTranslate2 elige los hilos y el tipo de cálculo más rápido,
     int8 en CPU), no el hilo único en float32 de e2a. Defina `ARGOS_INTRA_THREADS` o `ARGOS_COMPUTE_TYPE` para cambiarlos.

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
## Voces clonadas
Puedes subir cualquier audio de voz en cualquiera de los formatos de audio admitidos, la duración ideal es de alrededor de 1 a 5 minutos.
No importa si la grabación tiene un fondo ruidoso o si se reproduce música sobre ella: E2A limpiará la voz por ti.

La lista de voces clonadas incorporada está principalmente en inglés. Si necesitas voces en otros idiomas para ser oficialmente
añadidos a la lista, ponte en contacto con nosotros y los añadiremos después de revisarlos.

<a id="fine-tuned-tts-models"></a>
## Modelos TTS afinados
<a id="fine-tune-your-own-tts-model"></a>
#### Ajusta tu propio modelo TTS

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Datos de entrenamiento de ruido

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### Colección TTS de ajuste fino

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Para un modelo personalizado XTTSv2, es obligatorio un clip de audio de referencia de la referencia de voz:

## Tu propia personalización de Ebook2Audiobook
Puede modificar libs/conf.py para añadir o eliminar la configuración que desee. Si planeas hacerlo, haz
una copia del conf.py original, por lo que en cada actualización de ebook2audiobook hará una copia de seguridad de su conf.py modificado y pondrá
volver a la original. Debe planificar el mismo proceso para models.py. Si desea hacer su propio modelo personalizado
como un modelo oficial de ebook2audiobook, así que póngase en contacto con nosotros y lo añadiremos a la lista de preajustes.

<a id="reverting-to-older-versions"></a>
## Volver a versiones anteriores
Las versiones publicadas están disponibles -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## Probleme frecvente:
- Mi GPU NVIDIA/ROCm/XPU/MPS no se está detectando?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  La CPU es lenta (mejor en la CPU smp del servidor), mientras que la GPU puede tener una conversión casi en tiempo real.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Sin embargo, no tiene clonación de voz de disparo cero, y tiene voces de calidad Siri, pero es mucho más rápido en la CPU).
- "Tengo problemas de dependencias" - Simplemente use Docker, es totalmente autónomo y tiene un modo headless,
   añada el parámetro `--help` al final del comando docker run para obtener más información.
- "¡Tengo un problema de audio truncado!" - POR FAVOR, HAGA UN PROBLEMA con ESTO,
   no hablamos todos los idiomas y necesitamos consejos de los usuarios para afinar la lógica de división de oraciones.😊

## Hoja de ruta
- Todas las funciones están abiertas al público Contribuciones ⭐
- Cualquier ayuda de personas que hablen cualquiera de los idiomas admitidos para ayudarnos a mejorar los modelos ⭐
- [x] Vista previa de bloques/capítulos antes de iniciar la conversión
- [x] Editar por oración convertida para cambio de texto quirúrgico
- [x] Generar introducciones, interludios y finales de música; editar interludios y finales
- [x] Integración de etiquetas SML para voz, pausa, descanso y más cambios
- [x] -h -help información de parámetros en diferentes idiomas
- [x] Escaneo OCR para PDF / JPG / BMP / PNG / TIFF
- [x] Carpeta de blocs de notas [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Hacer que la división del texto chino no divida las palabras y mejorar el tiempo de pausa [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker- Compose
- [x] Podman componer
- [x] Cuaderno Kaggle
- [x] Cuaderno de Google Colab
- [x] Integración de estantes de audiolibros
- [x] Opción de traducción de libros electrónicos
- [x] Opciones de formato de salida
- [x] Conversión multiprocesamiento
- [x] Conversión de carpetas de libros electrónicos por lotes
- [x] Detección del dispositivo
- [x] Denoise cualquier audio de referencia de fondo para la carga de clonación de voz
- [x] Carga de modelo personalizada y ajustada

#### Peticiones de usuario
- [ ] Añade el modelo de idioma portugués europeo para xttsv2, fairseq, vits, piper al menos (ayuda bienvenida)
- [ ] Añadir el modelo de lenguaje sindhi para xttsv2, fairseq, vits, piper al menos (ayuda bienvenida)

#### Motores TTS
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Discurso de pez/Audio de pez (https://github.com/fishaudio/fish-speech)[cite: 1]
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
- [x] Confucio4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Puntos TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Bolsillo TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradio Fonón (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertónica (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1)
- [x] Tortuga (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Corteza (https://github.com/suno-ai/bark)[cite: 1)
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1)
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] MCS https://github.com/SesameAILabs/csm)

#### Readme Translation
- [x] Árabe (ara)
- [x] Chino (zho)
- [x] English (ENG)
- [x] Español IV (Esp)
- [x] Francés (fra)
- [x] Alemán (deu)
- [x] Italiano I (ita)
- [x] Portugués (por)
- [x] Polaco (pol)
- [x] Turco (tur)
- [x] Russian (rus)
- [x] Holandés (nld)
- [x] Czech (ces)
- [x] Japonés (jpn)
- [x] Hindi (hin)
- [x] Bengalí (ben)
- [x] Húngaro (HUN)
- [x] Coreano (kor)
- [x] Vietnamita (vie)
- [x] Swedish (swe)
- [x] Persa (fas)
- [x] Yoruba (yor)
- [x] Swahili (swa)
- [x] Indonesio (ind)
- [x] Eslovaco (slk)
- [x] Croata (hrv)

#### Compatibilidad con sistemas operativos
- [x] 🪟 Windows x86
- [x] 🪟 ARM WINDOWS
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

<a id="contributing"></a>
## Contribuir 
Antes de abrir un problema o una solicitud de extracción, lea [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md): Reglas de normalización de código Python,
flujo de trabajo de solicitud de ramificación y extracción, leyendas de GUI y traducciones README, añadiendo un motor TTS, pruebas.

## Se busca donación de hardware para pruebas beta
Aceptamos cualquier tipo de hardware para probar nuestro desarrollo como:
- Nvidia soportando cuda >= 11.8
- Tarjetas XPU Intel
- Tarjetas ROCm AMD compatibles con ROCm >=5,7

¡@ DrewThomasson si quieres ayudar! 😃
<!--
## ¿Necesitas alquilar una GPU para mejorar nuestro servicio?
- Una encuesta está abierta aquí https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Créditos
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- Un kit de herramientas de aprendizaje profundo para texto a voz, probado en batalla en investigación y producción.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Motor de conversión de texto a voz neuronal rápido y local.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml código de inferencia para Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- Un motor de inferencia todo en uno, puro C++ para modelos de audio, alimentado por ggml.

<a id="special-thanks"></a>
## Agradecimientos especiales
Para todos los contribuyentes financieros y de código, cada contribución y sugerencia ayuda a mejorar la calidad de E2A.