# 📚 eBook2audiobook

Convertidor de CPU/GPU de libros electrónicos a audiolibros con capítulos y metadatos<br/>Usando Calibre, FFMPEG, XTTSV2, Fairseq y más. ¡Apoya la clonación de voz y los idiomas +1110!

> [!IMPORTANTE]**Esta herramienta está destinada a su uso solo con libros electrónicos no DRM, adquiridos legalmente.**<br>Los autores no son responsables de ningún uso indebido de este software o cualquier consecuencia legal resultante.<br>Use esta herramienta de manera responsable y de acuerdo con todas las leyes aplicables.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

¡Gracias a apoyar a los desarrolladores de eBook2audiobook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Interfaz GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   compramos[Árabe (árabe)](./readme/README_AR.md)
-   Zho[Chino](./readme/README_CN.md)
-   A \`A[Inglés](README.md)
-   swe[Sueco (sueco)](./readme/README_SWE.md)
-   fas[Persa (persa)](./readme/README_FA.md)
-   ella[Italiano (Italian)](./readme/README.it.md)

## Tabla de contenido

-   [eBook2audiobook](#-ebook2audiobook)
-   [Características](#features)
-   [Interfaz GUI de Docker](#docker-gui-interface)
-   [Demostración del espacio de Huggingface](#huggingface-space-demo)
-   [Google Colab gratis](#free-google-colab)
-   [Demostraciones de audio prefabricadas](#demos)
-   [Idiomas compatibles](#supported-languages)
-   [Requisitos](#hardware-requirements)
-   [Instrucciones de instalación](#installation-instructions)
-   [Uso](#launching-gradio-web-interface)
    -   [Lanzamiento de la interfaz web de Gradio](#launching-gradio-web-interface)
    -   [Uso básico sin cabeza](#basic--usage)
    -   [Uso del modelo XTTS personalizado sin cabeza](#example-of-custom-model-zip-upload)
    -   [Alquilar una GPU](#renting-a-gpu)
    -   [Ayuda de salida de comando](#help-command-output)
-   [Modelos TTS ajustados](#fine-tuned-tts-models)
    -   [Para la recolección de modelos TTS ajustados](#fine-tuned-tts-collection)
-   [Usando Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker componer](#docker-compose)
    -   [Guía sin cabeza de Docker](#docker-headless-guide)
    -   [Ubicaciones de archivos de contenedor de docker](#docker-container-file-locations)
    -   [Problemas de Docker comunes](#common-docker-issues)
-   [Formatos de libros electrónicos compatibles](#supported-ebook-formats)
-   [Producción](#output)
-   [Problemas comunes](#common-issues)
-   [Agradecimiento especial](#special-thanks)
-   [¡Únete a nuestro servidor!](#join-our--server)
-   [Legado](#legacy-v10)
-   [Tabla de contenido](#table-of-contents)

## Características

-   📖 Convierte los libros electrónicos en formato de texto con calibre.
-   📚 Divida el libro electrónico en capítulos para audio organizado.
-   🎙️ Texto de alta calidad a voz con[Coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)y[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(y más).
-   🗣️ Clonación de voz opcional con su propio archivo de voz.
-   🌍 Admite +1110 idiomas (inglés por defecto).[Lista de idiomas compatibles](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ diseñado para ejecutar en 4 GB de RAM.

## [Demostración del espacio de Huggingface](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingface Space se ejecuta en nivel de CPU gratuito, así que espere muy lento o tiempo de espera jajaja, simplemente no le das archivos gigantes es todo
-   Lo mejor es duplicar el espacio o ejecutar localmente.

## Google Colab gratis

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Idiomas compatibles

-   **Árabe (Ara)**
-   **Chino (zh)**
-   **Checo (CES)**
-   **Croata (HRV)**
-   **Holandés (NLD)**
-   **Inglés (Eng)**
-   **Francés (de)**
-   **Alemán (Deu)**
-   **No (hin)**
-   **Húngaro (AM)**
-   **Italiano (ITA)**
-   **Japonés (JPN)**
-   **Coreano (cor)**
-   **Polaco (Pol)**
-   **Portuguese (por)**
-   **Ruso (Rus)**
-   **Español (spa)**
-   **Turco (ronda)**
-   **Vietnamita (Vie)**
-   [**+1100 idiomas a través de Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Requisitos de hardware

-   Mínimo de 4 GB de RAM, 8 GB recomendado
-   Virtualización habilitada si se ejecuta en Windows (solo Docker)
-   CPU, GPU (recomendado), MPS (aún no optimizado y puede ser más lento que la CPU) compatible con

> [!IMPORTANTE]**Antes de publicar una búsqueda de instalación o error de error cuidadosamente en la pestaña de problemas abiertos y cerrados<br>Para asegurarse de que su problema aún no exista.**

> [!NOTA]**Falta de cualquier estructura de estándares como lo que es un capítulo, párrafo, prefacio, etc.<br>Primero debe eliminar manualmente cualquier texto que no desee convertirse en audio.**

### Instrucciones de instalación

1.  **Repositorio**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Lanzamiento de la interfaz web de Gradio

1.  **Ejecutar ebook2audiobook**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Windows**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Abra la aplicación web**: Haga clic en la URL proporcionada en el terminal para acceder a la aplicación web y convertir libros electrónicos.
3.  **Para enlace público**:`python app.py --share`(Todo el sistema operativo)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!IMPORTANTE]**Si el script se detiene y se ejecuta nuevamente, debe actualizar su interfaz GUI de Gradio<br>Para dejar que la página web se vuelva a conectar a la nueva toma de conexión.**

### Uso básico

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--eBook]**: Ruta a su archivo de libro electrónico.
-   **[--voz]**: Ruta del archivo de clonación de voz (opcional).
-   **[--idioma]**: Código de idiomas en ISO-639-3 (es decir, ITA para italiano, Ing para inglés, deu para alemán ...).<br>El lenguaje predeterminado es ENG y --language es opcional para el lenguaje predeterminado establecido en ./lib/lang.py.<br>Los códigos de letras ISO-639-1 2 también son compatibles.

### Ejemplo de carga de polvo de modelo personalizado

(Debe ser un archivo .zip que contenga los archivos de modelo obligatorios. Ejemplo para XTTS: config.json, model.pth, vocab.json y ref.wav)

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;Untect_model_path>**:`model_name.zip`archivo,
        que debe contener (según el motor TTS) todos los archivos obligatorios<br>(Ver ./lib/models.py).

### Para una guía detallada con la lista de todos los parámetros para usar

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **O para todo el sistema operativo**
    ```python
     app.py --help
    ```

<a id="help-command-output"></a>

```bash
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
              [--headless] [--ebook EBOOK] [--ebooks_dir EBOOKS_DIR]
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
              [--tts_engine {xtts,bark,vits,fairseq,yourtts}]
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
              [--length_penalty LENGTH_PENALTY] [--num_beams NUM_BEAMS]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
              [--version]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

**** The following option are for gradio/gui mode only:
  Optional

  --share               Enable a public shareable Gradio link.

**** The following options are for --headless mode only:
  --headless            Run the script in headless mode
  --ebook EBOOK         Path to the ebook file for conversion. Cannot be used when --ebooks_dir is present.
  --ebooks_dir EBOOKS_DIR
                        Relative or absolute path of the directory containing the files to convert. 
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
                            in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py

optional parameters:
  --voice VOICE         (Optional) Path to the voice cloning file for TTS engine. 
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
                        (Optional) Pprocessor unit type for the conversion. 
                            Default is set in ./lib/conf.py if not present. Fall back to CPU if GPU not available.
  --tts_engine {xtts,bark,vits,fairseq,yourtts}
                        (Optional) Preferred TTS engine (available are: ['xtts', 'bark', 'vits', 'fairseq', 'yourtts'].
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
                        (Optional) Path to the custom model zip file cntaining mandatory model files. 
                            Please refer to ./lib/models.py
  --fine_tuned FINE_TUNED
                        (Optional) Fine tuned model path. Default is builtin model.
  --output_format OUTPUT_FORMAT
                        (Optional) Output audio format. Default is set in ./lib/conf.py
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
                            Lower values mean more likely outputs and increased audio generation speed. Default to 0.85
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
  --enable_text_splitting
                        (xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient. 
                            Default to config.json model.
  --output_dir OUTPUT_DIR
                        (Optional) Path to the output directory. Default is set in ./lib/conf.py
  --version             Show the version of the script and exit

Example usage:    
Windows:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
Linux/Mac:
    Gradio/GUI:
    ./ebook2audiobook.sh
    Headless mode:
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
```

Nota: en modo Gradio/GUI, para cancelar una conversión en ejecución, simplemente haga clic en el[incógnita]Desde el componente de carga electrónica.

### Usando Docker

También puede usar Docker para ejecutar el libro electrónico a audiolibro convertidor. 
Este método garantiza la consistencia en los diferentes entornos y simplifica la configuración.

#### Ejecutando el contenedor Docker

Para ejecutar el contenedor Docker e iniciar la interfaz Gradio, use el siguiente comando:

\-Cre solo con CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Rungue con GPU Speedup (solo compatible con NVIDIA)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Construyendo el contenedor Docker

-   Puede construir la imagen Docker con el comando:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Este comando iniciará la interfaz de Gradio en el puerto 7860. (Localhost: 7860)

-   Para más opciones, agregue el parámetro`--help`

## Ubicaciones de archivos de contenedor de docker

Todos los eBook2audiobooks tendrán el directorio base de`/home/user/app/`Por ejemplo:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Guía sin cabeza de Docker

Primero para un Docker tirón de lo último con

```bash
docker pull athomasson2/ebook2audiobook
```

-   Antes de ejecutar esto, debe crear un DIR llamado "Foldador de entrada" en su DIR actual
    que estará vinculado, aquí es donde puede colocar sus archivos de entrada para que la imagen de Docker vea

```bash
mkdir input-folder && mkdir Audiobooks
```

-   En el comando a continuación intercambio**You_input_file.txt**con el nombre de su archivo de entrada

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   ¡Y eso debería ser todo!
-   Los audiolibros de salida se encontrarán en la carpeta de audiolibros que también se ubicará
    En su directorio local ejecutaste este comando Docker en

## Para obtener el comando de ayuda para los otros parámetros que tiene este programa, puede ejecutar esto

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

y eso generará esto[Ayuda de salida de comando](#help-command-output)

### Docker componer

Este proyecto utiliza Docker Compose para ejecutar localmente. Puede habilitar o deshabilitar el soporte de GPU 
Configurando`*gpu-enabled`o`*gpu-disabled`en`docker-compose.yml`

#### Pasos para correr

1.  **Clonar el repositorio**(Si aún no lo has hecho):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Establecer soporte de GPU (deshabilitado por defecto)**Para habilitar el soporte de GPU, modifique`docker-compose.yml`y cambiar`*gpu-disabled`a`*gpu-enabled`
3.  **Inicie el servicio:**
    ```bash
    docker-compose up -d
    ```
4.  **Acceda al servicio:**El servicio estará disponible en http&#x3A; // localhost: 7860.

### Interfaz GUI de Docker

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Alquilar una GPU

¿No tienes el hardware para ejecutarlo o quieres alquilar una GPU?

#### Puede duplicar el espacio de Hugginface y alquilar una GPU por alrededor de $ 0.40 por hora

[Demostración del espacio de Huggingface](#huggingface-space-demo)

#### ¡O puede intentar usar Google Colab de forma gratuita!

(Tenga en cuenta que pasará tiempo después de un poco de no jugar con Google Colab)[Google Colab gratis](#free-google-colab)

## Problemas de Docker comunes

-   Docker se queda atascado descargando modelos ajustados.
    (Esto no sucede para cada computadora, pero algunos parecen encontrarse con este problema)
    Deshabilitar la barra de progreso parece solucionar el problema,
    Como se discutió[aquí en #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Ejemplo de agregar esta solución en el`docker run`dominio

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Modelos TTS ajustados

Puede ajustar su propio modelo XTTS fácilmente con este repositorio[Xtts-Finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Si desea alquilar una GPU fácilmente, también puede duplicar esta cara de abrazo[Xtts-Finetune-Webui-Space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Un espacio que puede usar para eliminar los datos de capacitación fácilmente también[Denoise-Huggingface-Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Colección TTS fina

Para encontrar nuestra colección de modelos TTS ya ajustados,
visita[este enlace de la cara abrazando](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Para un modelo personalizado XTTS, es obligatorio un clip de audio de referencia de la referencia de voz:

## Población

**Voz del día lluvioso**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**Voz de David Attenborough**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Formatos de libros electrónicos compatibles

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Mejores resultados**:`.epub`o`.mobi`para detección automática de capítulos

## Producción

-   Crea un`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Establecer el archivo ./lib/conf.py) con metadatos y capítulos.
-   **Ejemplo**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Problemas comunes:

-   La CPU es lenta (mejor en la CPU SMP del servidor), mientras que NVIDIA GPU puede tener una conversión casi en tiempo real.[Discusión sobre esto](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Para una generación multilingüe más rápida, sugeriría mi otro[Proyecto que usa Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)en cambio
    (Sin embargo, no tiene clonación de voz de cero disparos, y son voces de calidad de Siri, pero es mucho más rápido en la CPU).
-   "Tengo problemas de dependencia", solo usa el Docker, está completamente contenido y tiene un modo sin cabeza,
     agregar`--help`Parámetro al final del comando Docker Ejecutar para obtener más información.
-   "¡Estoy recibiendo un problema de audio truncado!" - Por favor haz un problema de esto,
     No hablamos todos los idiomas y necesitamos asesorar a los usuarios para ajustar la lógica de división de oraciones.

## Con qué necesito ayuda! 🙌

## [Lista completa de cosas se puede encontrar aquí](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Cualquier ayuda de personas que hablen cualquiera de los idiomas apoyados para ayudar con los métodos de división de oraciones adecuados
-   Potencialmente, creando guías Readme para varios idiomas (porque el único idioma que conozco es el inglés 😔)

## Agradecimiento especial

-   **Cocinar TTS**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Calibre**:[Calibre Website](https://calibre-ebook.com)
-   **Ffmpeg**:[Sitio web de FFMPEG](https://ffmpeg.org)
-   [@shakenbake15 for better chapter saving method](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Puedes ver el código[aquí](legacy/v1.0).

## ¡Únete a nuestro servidor!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
