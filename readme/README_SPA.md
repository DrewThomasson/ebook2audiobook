📚 eBook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
Convertidor de CPU/GPU de libros electrónicos a audiolibros con capítulos y metadatos <br/>
Usando Calibre, FFMPEG, XTTSV2, Fairseq y más. ¡Apoya la clonación de voz y los idiomas +1110! [!IMPORTANTE]
** Esta herramienta está destinada a usarse solo con libros electrónicos no DRM y legalmente adquiridos. ** <br>
Los autores no son responsables de ningún uso indebido de este software o cualquier consecuencia legal resultante. <br>
Use esta herramienta de manera responsable y de acuerdo con todas las leyes aplicables. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

/ .com/athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [demo_web_gui] (assets/demo_web_gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
Ara [العربية (árabe)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
ZHO [中文 (chino)] (./ Readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
Swe [Svenska (sueco)] (./ Readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
Fas [فارسی (Persian)] (./ Readme/Readme_fa.md)


## Table of Contents
[eBook2audiobook] (#-eBook2audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Características] (#características)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Interfaz GUI Docker] (#Docker-gui-interfaz)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Demo de Space Space] (#Huggingface-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Google Colab gratis] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Demostraciones de audio prefabricadas] (#demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Idiomas compatibles] (#Lenguajes compatibles)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Requisitos] (#requirtos de hardware)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Instrucciones de instalación] (#instalación-instrucciones)
- [Output](#output)
- [Common Issues](#common-issues)
[Uso] (#Interfaz-Web-Interface de lanzamiento-Gradio-Web)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Iniciar interfaz web de Gradio] (#iniciar la interfaz-Web-Web)


[Uso básico sin cabeza] (#Basic-Usage)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Uso del modelo XTTS personalizado sin cabeza] (#Ejemplo de Custom-Modelo-Zip-Spload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Alquilar una GPU] (#alquiler-a-gpu)


[Salida del comando de ayuda] (#ayude-command-output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Modelos TTS ajustados] (#modelos TTS-TTS)


[Para la recolección de modelos TTS ajustados] (#-ajustado-tts-colección)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Running-the-Docker-Container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#edificio-the-docker-contener)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#Docker-Compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Guía sin cabeza Docker] (#Docker-Headless-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Ubicaciones de archivos de contenedores de Docker] (#-locations-continer-archivo-archivo)
- **Portuguese (por)**
- **Russian (rus)**
[Problemas de Docker comunes] (#Common-Docker-Issues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Formatos de libros electrónicos compatibles] (#compatible-ebook-formats)


[Salida] (#salida)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Problemas comunes] (#emisores comunes)


[Agradecimiento especial] (#especial-gracias)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Características
```bash
📖 Convierte los libros electrónicos en formato de texto con calibre. 📚 Divida el libro electrónico en capítulos para audio organizado. 🎙️ Text-to-speech de alta calidad con [Coqui Xttsv2] (https://huggingface.co/coqui/xtts-v2) y [jairseq] (https://github.com/facebookresearch/fairseq/tree/main/ ejemplos/mms) (y más). 🗣️ Clonación de voz opcional con su propio archivo de voz. 🌍 Admite +1110 idiomas (inglés por defecto). [Lista de idiomas compatibles] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥️ diseñado para ejecutar en 4 GB de RAM. [Demo de Space Space] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
/ /eBook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Huggingface Space se ejecuta en nivel de CPU gratuito, así que espere muy lento o tiempo de espera jajaja, simplemente no le das archivos gigantes es todo
   - **Windows**
     ```bash
Lo mejor es duplicar el espacio o ejecutar localmente. Google Colab gratis
     ```
/ Main/cuaderno/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Idiomas compatibles
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** árabe (ara) **

> [!IMPORTANT]
** chino (zho) **
to let the web page reconnect to the new connection socket.**

** checo (ces) **
   - **Linux/MacOS**:
     ```bash
** croata (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** holandés (nld) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Inglés (Eng) **
     ```
     
** French (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Alemán (Deu) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Húngaro (Hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** italiano (ita) **
     ```
   - **Windows**
** japonés (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** coreano (kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Polaco (Pol) **


** portugués (por) **
   - **Linux/MacOS**
     ```bash
** ruso (rus) **
     ```
   - **Windows**
** español (spa) **
     .\ebook2audiobook.cmd --help
     ```
** turco (tur) **
    ```python
     app.py --help
** vietnamita (Vie) **

<a id="help-command-output"></a>
[** +1100 idiomas a través de Fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Requisitos de hardware
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
Mínimo de 4 GB de RAM, 8 GB recomendado
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualización habilitada si se ejecuta en Windows (solo Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (recomendado), MPS (aún no optimizado y puede ser más lento que la CPU) compatible con

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Antes de publicar una búsqueda de instalación o problema de errores cuidadosamente en la pestaña de problemas abiertos y cerrados <br>
Para asegurarse de que su problema aún no exista. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Falta de cualquier estructura de estándares como lo que es un capítulo, párrafo, prefacio, etc. <br>
Primero debe eliminar manualmente cualquier texto que no desee convertirse en audio. **

Instrucciones de instalación

** Repo clon **
  --headless            Run the script in headless mode
Lanzamiento de la interfaz web de Gradio
  --ebooks_dir EBOOKS_DIR
** Ejecutar ebook2audiobook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Abra la aplicación web **: haga clic en la URL proporcionada en el terminal para acceder a la aplicación web y convertir libros electrónicos. ** Para enlace público **:
`python app.py --share` (todo el sistema operativo)
`./EBOOK2AUDIOBOOK.SH --SHARE` (LINUX/MACOS)
`ebook2audiobook.cmd --share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!IMPORTANTE]
** Si el script se detiene y se ejecuta nuevamente, debe actualizar su interfaz GUI de Gradio <br>
para dejar que la página web se vuelva a conectar a la nueva conexión de conexión. **
                        (Optional) Fine tuned model path. Default is builtin model.
Uso básico
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-Ebook] **: ruta a su archivo de libro electrónico. ** [-voz] **: ruta del archivo de clonación de voz (opcional). ** [-Idioma] **: Código de idiomas en ISO-639-3 (es decir: ITA para italiano, Ing para inglés, deu para alemán ...). <br>
El lenguaje predeterminado es ENG y --language es opcional para el lenguaje predeterminado establecido en ./lib/lang.py. <br>
Los códigos de letras ISO-639-1 2 también son compatibles. Ejemplo de carga de polvo de modelo personalizado
  --repetition_penalty REPETITION_PENALTY
(Debe ser un archivo .zip que contenga los archivos de modelo obligatorios. Ejemplo para XTTS: config.json, model.pth, vocab.json y ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <Custom_model_path> **: ruta al archivo `model_name.zip`,
    que debe contener (según el motor TTS) todos los archivos obligatorios <br>
    (Ver ./lib/models.py). Para una guía detallada con la lista de todos los parámetros para usar
  --output_dir OUTPUT_DIR
** Linux/macOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** o para todo el sistema operativo **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "ayuda-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Nota: En modo Gradio/GUI, para cancelar una conversión en ejecución, simplemente haga clic en [x] desde el componente de carga de libro electrónico. Usando Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
También puede usar Docker para ejecutar el libro electrónico a audiolibro convertidor. Este método garantiza la consistencia en los diferentes entornos y simplifica la configuración. Ejecutando el contenedor Docker

Para ejecutar el contenedor Docker e iniciar la interfaz Gradio, use el siguiente comando:

### Using Docker
-Cre solo con CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Construyendo el contenedor Docker

Puede construir la imagen Docker con el comando:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Este comando iniciará la interfaz de Gradio en el puerto 7860. (Localhost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Para obtener más opciones, agregue el parámetro `help`
```


Todos los ebook2audiobooks tendrán el directorio base de `/home/user/app/`
Por ejemplo:
`tmp` =`/home/user/app/tmp`
`Audiobooks` =`/home/user/app/audiobooks`
```
Guía sin cabeza de Docker
- For more options add the parameter `--help`


## Docker container file locations
Antes de ejecutar esto, debe crear un DIR llamado "Foldador de entrada" en su DIR actual
que estará vinculado, aquí es donde puede colocar sus archivos de entrada para que la imagen de Docker vea
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
¡Y eso debería ser todo! Los audiolibros de salida se encontrarán en la carpeta de audiolibros que también se ubicará
En su directorio local ejecutaste este comando Docker en
docker pull athomasson2/ebook2audiobook
Para obtener el comando de ayuda para los otros parámetros que tiene este programa, puede ejecutar esto
- Before you do run this you need to create a dir named "input-folder" in your current dir
y eso generará esto 
[Salida del comando de ayuda] (#ayude-command-output)
mkdir input-folder && mkdir Audiobooks
Docker componer
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Este proyecto utiliza Docker Compose para ejecutar localmente. Puede habilitar o deshabilitar el soporte de GPU 
Estableciendo `*GPU habilitado` o`*GPU-DISABLED` en `docker-composa.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Pasos para correr
    athomasson2/ebook2audiobook \
** Clone el repositorio ** (si aún no lo ha hecho):
```
- And that should be it! 
** Establecer soporte de GPU (deshabilitado por defecto) **
Para habilitar el soporte de GPU, modifique `docker-compose.yml` y cambie`*gpu-disable` a `*GPU-habilitado`


** Inicie el servicio: **

```bash
** Acceda al servicio: **

```
! [demo_web_gui] (assets/demo_web_gui.gif)
[Help command output](#help-command-output)


¿No tienes el hardware para ejecutarlo o quieres alquilar una GPU? Puede duplicar el espacio de Hugginface y alquilar una GPU por alrededor de $ 0.40 por hora
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Demo de Space Space] (#Huggingface-Space-Demo)


[Google Colab gratis] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Problemas de Docker comunes
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker se queda atascado descargando modelos ajustados. (Esto no sucede para cada computadora, pero algunos parecen encontrarse con este problema)
Deshabilitar la barra de progreso parece solucionar el problema,
Como se discutió [aquí en #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Ejemplo de agregar esta solución en el comando 'Docker Run`
3. **Start the service:**
Modelos TTS ajustados
    docker-compose up -d
Puede ajustar su propio modelo XTTS fácilmente con este repositorio
[Xtts-Finetune-Webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[Xtts-Finetune-webui-space] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Un espacio que puede usar para eliminar los datos de capacitación fácilmente también
[Denoise-Huggingface-space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Colección TTS fina
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Para encontrar nuestra colección de modelos TTS ya ajustados,


## Renting a GPU
Población
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Voz del día lluvioso **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** Voz de David Attenborough **


Formatos de libros electrónicos compatibles
- Docker gets stuck downloading Fine-Tuned models.
`.Epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Los mejores resultados **: `.Epub` o` .mobi` para la detección automática de capítulos
    -p 7860:7860 athomasson2/ebook2audiobook
Producción


! [Ejemplo] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Problemas comunes:

La CPU es lenta (mejor en la CPU SMP del servidor), mientras que NVIDIA GPU puede tener una conversión casi en tiempo real. [Discusión sobre esto] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
Para una generación multilingüe más rápida, sugeriría mi otro

(Sin embargo, no tiene clonación de voz de cero disparos, y son voces de calidad de Siri, pero es mucho más rápido en la CPU). "Tengo problemas de dependencia", solo usa el Docker, está completamente contenido y tiene un modo sin cabeza,
 Agregue el parámetro `help` al final del comando Docker Ejecutar para obtener más información. "¡Estoy recibiendo un problema de audio truncado!" - Por favor haz un problema de esto,

### Fine Tuned TTS Collection
Con qué necesito ayuda! 🙌
[La lista completa de cosas se puede encontrar aquí] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potencialmente, creando guías Readme para varios idiomas (porque el único idioma que sé es el inglés 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui tts **: [Coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [Sitio web de FFMPEG] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy V1.0] (Legacy/V1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Puede ver el código [aquí] (Legacy/V1.0). ¡Únete a nuestro servidor! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)