# 📚 ebook2audiobook (E2A)
Conversor CPU/GPU de libro electrónico a audiolibro con capítulos y metadatos<br/>
usando motores TTS avanzados y mucho más.<br/>
¡Admite clonación de voz y 1158 idiomas!
> [!IMPORTANT]
**Esta herramienta está destinada a usarse únicamente con libros electrónicos sin DRM y adquiridos legalmente.** <br>
Los autores no se hacen responsables de ningún uso indebido de este software ni de las consecuencias legales que de ello se deriven. <br>
Utiliza esta herramienta de forma responsable y conforme a todas las leyes aplicables.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### ¡Gracias por apoyar a los desarrolladores de ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Ejecución local

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Ejecución remota
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Interfaz gráfica (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Haz clic para ver imágenes de la GUI web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demos

**Demo de la nueva voz por defecto**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Más demos</summary>

**Voz ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Voz de día lluvioso**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Voz Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Voz David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Ejemplo**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Tabla de contenidos
- [ebook2audiobook](#-ebook2audiobook)
- [Características](#features)
- [Interfaz gráfica](#gui-interface)
- [Demos](#demos)
- [Idiomas admitidos](#supported-languages)
- [Requisitos mínimos](#hardware-requirements)
- [Uso](#instructions)
  - [Ejecución local](#instructions)
    - [Lanzar la interfaz web de Gradio](#instructions)
    - [Uso básico sin interfaz (headless)](#basic-usage)
    - [Uso de modelo XTTS personalizado sin interfaz](#example-of-custom-model-zip-upload)
    - [Salida del comando de ayuda](#help-command-output)
  - [Ejecución remota](#run-remotely)
  - [Docker](#docker)
    - [Pasos para ejecutar](#docker)
    - [Problemas habituales con Docker](#common-docker-issues)
  
- [Modelos TTS ajustados](#fine-tuned-tts-models)
  - [Colección de modelos TTS ajustados](#fine-tuned-tts-collection)
  - [Entrenar XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Formatos de libro electrónico admitidos](#supported-ebook-formats)
- [Formatos de salida](#output-and-process-formats)
- [Volver a una versión anterior](#reverting-to-older-versions)
- [Problemas habituales](#common-issues)
- [Agradecimientos especiales](#special-thanks)
- [Tabla de contenidos](#table-of-contents)


## Características
- 🔧 **Motores TTS admitidos**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Convertir múltiples formatos de archivo**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Área de texto** para convertir directamente un texto corto en audio
- 🔍 **Escaneo OCR** para archivos con páginas de texto en forma de imágenes
- 🔊 **Texto a voz de alta calidad**, desde casi en tiempo real hasta una voz casi real
- 🗣️ **Clonación de voz opcional** usando tu propio archivo de voz
- 🌐 **Admite 1158 idiomas** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Apto para recursos limitados** — funciona con **2 GB de RAM / 1 GB de VRAM (mínimo)**
- 🎵 **Formatos de salida del audiolibro**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Etiquetas SML admitidas** — control preciso de cortes, pausas, cambio de voz y mucho más ([see below](#sml-tags-available))
- 🧩 **Modelo personalizado opcional** usando tu propio modelo entrenado (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modelos preajustados y ajustados** entrenados por el equipo de E2A<br/>
     <i>(Contáctanos si necesitas modelos ajustados adicionales, o si quieres compartir los tuyos en la lista oficial de preajustes)</i>


##  Requisitos de hardware
- 2 GB de RAM mín., 8 GB recomendados.
- 1 GB de VRAM mín., 4 GB recomendados.
- Virtualización habilitada si se ejecuta en Windows (solo Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Los motores TTS modernos son muy lentos en CPU, así que usa TTS de menor calidad como YourTTS, Tacotron2, etc.</i>

## Idiomas admitidos
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 idiomas y dialectos aquí**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Formatos de libro electrónico admitidos
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Mejores resultados**: `.epub` o `.mobi` para la detección automática de capítulos

## Formatos de salida y de proceso
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- El formato de proceso se puede cambiar en lib/conf.py

## Etiquetas SML disponibles
- `[break]` — silencio (rango aleatorio **0.3–0.6 sec.**)
- `[pause]` — silencio (rango aleatorio **1.0–1.6 sec.**)
- `[pause:N]` — pausa fija (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — cambiar de voz respecto a la voz por defecto o seleccionada desde la GUI/CLI

**Consulta nuestro otro repositorio dedicado a añadir SML automáticamente en tu libro electrónico -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**Antes de publicar un problema de instalación o un error, busca cuidadosamente en la pestaña de problemas abiertos y cerrados<br>
para asegurarte de que tu problema no exista ya.**

>[!NOTE]
**El formato EPUB carece de cualquier estructura estándar que defina qué es un capítulo, un párrafo, un prefacio, etc.<br>
Por tanto, primero deberías eliminar manualmente cualquier texto que no quieras convertir en audio.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Instalar / Ejecutar ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Lanzador de Mac**  
     Haz doble clic en `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Nota para usuarios de Windows: se instala scoop para instalar los programas que falten sin privilegios de administrador.</i>
   
1. **Abrir la aplicación web**: Haz clic en la URL proporcionada en el terminal para acceder a la aplicación web y convertir libros electrónicos. `http://localhost:7860/`
2. **Para un enlace público**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Si el script se detiene y se vuelve a ejecutar, debes actualizar tu interfaz gráfica de Gradio<br>
para que la página web vuelva a conectarse al nuevo socket de conexión.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Ruta a tu archivo de libro electrónico
  - **[--voice]**: Ruta del archivo de clonación de voz (opcional)
  - **[--language]**: Código de idioma en ISO-639-3 (p. ej.: ita para italiano, eng para inglés, deu para alemán...).<br>
    El idioma por defecto es eng y --language es opcional para el idioma por defecto definido en ./lib/lang.py.<br>
    También se admiten los códigos ISO-639-1 de 2 letras.


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
     
- **<custom_model_path>**: Ruta al archivo `model_name.zip`,
      que debe contener (según el motor TTS) todos los archivos obligatorios<br>
      (consulta ./lib/models.py).

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

NOTA: en modo gradio/gui, para cancelar una conversión en curso, simplemente haz clic en la [X] del componente de subida del libro electrónico.
CONSEJO: si necesita algo más de pausa, añade '[pause:3]' para 3 seg., etc.

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
  
### Problemas habituales con Docker
- ¿Mi GPU NVIDIA no se detecta?? -> [Página wiki de PROBLEMAS DE GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Modelos TTS ajustados (fine-tuned)
#### Ajusta tu propio modelo XTTSv2

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Eliminar ruido de los datos de entrenamiento

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Colección de modelos TTS ajustados

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Para un modelo personalizado XTTSv2 es obligatorio un clip de audio de referencia de la voz:

## Tu propia personalización de Ebook2Audiobook
Eres libre de modificar libs/conf.py para añadir o eliminar los ajustes que desees. Si piensas hacerlo, simplemente haz
una copia del conf.py original para que en cada actualización de ebook2audiobook puedas respaldar tu conf.py modificado y volver a poner
el original. Debes planificar el mismo proceso para models.py. Si deseas convertir tu propio modelo personalizado
en un modelo ajustado oficial de ebook2audiobook, contáctanos y lo añadiremos a la lista de preajustes.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Problemas habituales:
- ¿Mi GPU NVIDIA/ROCm/XPU/MPS no se detecta?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  La CPU es lenta (mejor en una CPU SMP de servidor) mientras que la GPU puede lograr una conversión casi en tiempo real.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Sin embargo, no tiene clonación de voz zero-shot, y las voces son de calidad Siri, pero es mucho más rápido en CPU).
- «Tengo problemas de dependencias» - Simplemente usa Docker, es totalmente autónomo y tiene un modo headless,
   añade el parámetro `--help` al final del comando docker run para más información.
- «¡Tengo un problema de audio truncado!» - POR FAVOR, ABRE UN ISSUE SOBRE ESTO,
   no hablamos todos los idiomas y necesitamos el consejo de los usuarios para ajustar la lógica de división de frases.😊

## ***** HOJA DE RUTA *****
- Todas las características abiertas a contribuciones públicas ⭐
- Cualquier ayuda de personas que hablen alguno de los idiomas admitidos para ayudarnos a mejorar los modelos ⭐
- [x] Previsualizar bloques/capítulos antes de iniciar la conversión
- [ ] Edición por frase convertida para un cambio quirúrgico del texto
- [x] Integración de etiquetas SML para voz, pausa, corte y más cambios 
- [x] Información de los parámetros -h -help en distintos idiomas
- [x] Escaneo OCR para PDF / JPG / BMP / PNG / TIFF
- [x] Carpeta de notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Hacer que la división de texto en chino no parta las palabras y mejorar la sincronización de las pausas [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook de Kaggle
- [x] Notebook de Google Colab
- [ ] [Crear una app para iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Crear una app para Android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Integración con Audiobookshelf

#### Opciones adicionales
- [x] Opción de traducción del libro electrónico
- [x] Opciones de formato de salida
- [x] Carpeta de libros electrónicos por lotes
- [x] Conversión con multiprocesamiento
- [x] Conversión por lotes de una carpeta de libros electrónicos
- [x] Detección del dispositivo GPU
- [x] Eliminar ruido de cualquier audio de referencia para clonación de voz subida,
- [x] Subida de modelo personalizado (solo XTTSv2 por ahora. más bajo petición)
- [ ] Añadir un modelo de idioma portugués europeo para xttsv2, fairseq, vits, piper como mínimo (ayuda bienvenida)
- [ ] Añadir un modelo de idioma sindhi para xttsv2, fairseq, vits, piper como mínimo (ayuda bienvenida)

#### Motores TTS
- [x] XTTSv2
- [x] Corteza
- [x] Fairseq
- [x] JAASKELAINEN
- [x] Tacotron2
- [x] YourTTS
- [x] Tortuga
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
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
- [ ] Estilo-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Traducción del Readme
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

#### 🐍 Compatibilidad de sistemas operativos
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra exagerado para entrenar modelos y demás (todos los modelos Coqui-tts admitidos y piper-tts en un solo comando fácil) 
- Para información sobre esto @DrewThomasson, actualmente está trabajando en su desarrollo, [repositorio en desarrollo aquí](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Crear una GUI de entrenamiento fácil de usar para todos los modelos coqui-tts en las recetas de entrenamiento con formato ljspeech [aquí de coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Información de normalización del código Python para colaboradores
- sin línea en blanco entre el código, salvo entre funciones y clases.
- comilla simple usada para todas las claves salvo para dict() y json. dict['key'] siempre se llama con comilla simple
- indentación de 4 espacios, nada de tabulaciones
- tipado estricto para todas las funciones y la declaración de sus argumentos y valores de retorno
- sin espacio entre el argumento y su tipado, sin espacio entre la función, el «->» y el valor de retorno

Ejemplo:

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

## Se busca donación de hardware para pruebas beta
Aceptamos cualquier tipo de hardware para probar nuestro desarrollo, como:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

¡@DrewThomasson si quieres ayudar en lo que sea! 😃
<!--
## ¿Necesitas alquilar una GPU para potenciar nuestro servicio?
- Hay una encuesta abierta aquí https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Agradecimientos especiales
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 por un mejor método de guardado de capítulos](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
