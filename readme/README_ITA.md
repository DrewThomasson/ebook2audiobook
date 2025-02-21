📚 eBook2AudiBook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
Convertitore CPU/GPU da ebook agli audiolibri con capitoli e metadati <br/>
Utilizzando Caliber, FFMPEG, XTTSV2, Fairseq e altro. Supporta la clonazione vocale e +1110 lingue! [!IMPORTANTE]
** Questo strumento è destinato all'uso solo con e-book non acquisiti legalmente. ** <br>
Gli autori non sono responsabili per qualsiasi uso improprio di questo software o di conseguenze legali risultanti. <br>
Utilizzare questo strumento in modo responsabile e in conformità con tutte le leggi applicabili. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko-fi-f16061?style=For-the-badge&logo=ko-fi &logocolor=White)] (https: // ko-fi .com/Athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_Web_GUI] (Asset/Demo_Web_Gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العربية (arabo)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文 (cinese)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
swe [svenska (svedese)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
Fas [فارسی (persiano)] (./ readme/readme_fa.md)


## Table of Contents
[eBook2AudioBook] (#-eBook2AudioBook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Caratteristiche] (#Funzionalità)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker GUI Interface] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[HuggingFace Space Demo] (#HuggingFace-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[GRATUITO Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Demos audio pre-realizzato] (#demo)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Lingue supportate] (#Languages ​​supportate)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Requisiti] (#Requisiti hardware)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Istruzioni per l'installazione] (#Installation-Instructions)
- [Output](#output)
- [Common Issues](#common-issues)
[Utilizzo] (#lancio-graddio-web-interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Avviamento di Gradio Web Interface] (#lancio-gradi-web-interfaccia)


[Utilizzo di base senza testa] (#BASIC-USAGE)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Utilizzo del modello di XTS personalizzato senza Headless] (#Esempio di Modello-Zip-Zip-Upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Affitto una GPU] (#Renting-a-GPU)


[Output del comando di aiuto] (#help-comand-output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Modelli TTS sintonizzati fine] (#modelli Fine-Tuned-TTS)


[Per la raccolta di modelli TTS sintonizzati] (#Collezione Fine-Tuned-TTS)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Running-the-Docker-Container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Building-the-Docker-container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#Docker-Opse)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide] (#Docker-Headless Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Posizioni di file container Docker] (#Docker-Container-file-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Common Docker Issues] (#Common-Docker-Essues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Formati di eBook supportati] (#supportati-ebook-formatori)


[Output] (#output)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Problemi comuni] (#Common Insues)


[Ringraziamento speciale] (#Special-grazie)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Caratteristiche
```bash
📖 Converte gli ebook in formato di testo con calibro. 📚 divide l'eBook in capitoli per l'audio organizzato. 🎙️ Text-to-speech di alta qualità con [Coqui XTTSV2] (https://huggingface.co/coqui/xtts-v2) e [Fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ Esempi/mms) (e altro). 🗣️ Clonazione vocale opzionale con il tuo file vocale. 🌍 Supporta +1110 lingue (inglese per impostazione predefinita). [Elenco delle lingue supportate] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥️ Progettato per funzionare su 4 GB di RAM. [HuggingFace Space Demo] (https://huggingface.co/spaces/drewthomasson/ebook2audiolibook)
1. **Run ebook2audiobook**:
[! [Abbraccio faccia] (https://img.shields.io/badge/hugging%20Face-Spaces-yellove?style=FOR-The-badge&logo=huggingFace)] (https://huggingface.co/spaces/drewthomasson /eBook2AudiBook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Lo spazio di HuggingFace è in esecuzione con il livello CPU gratuito, quindi aspettati molto lento o timeout lol, non dargli i file giganti è tutto
   - **Windows**
     ```bash
Meglio duplicare lo spazio o correre localmente. Google Colab gratuito
     ```
[! [GRATUITO Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)] (https://colab.research.google.com/github/Drewthomasson/ebook2umoBook/Blob/ main/notebooks/colab_ebook2audiolibook.ipynb)
3. **For Public Link**:
Lingue supportate
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arabo (Ara) **

> [!IMPORTANT]
** cinese (zho) **
to let the web page reconnect to the new connection socket.**

** ceco (CES) **
   - **Linux/MacOS**:
     ```bash
** Croato (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** olandese (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** English (ENG) **
     ```
     
** francese (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** tedesco (DEU) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Ungherese (Hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** italiano (ita) **
     ```
   - **Windows**
** giapponese (jpn) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** coreano (kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** polacco (pol) **


** Portoghese (por) **
   - **Linux/MacOS**
     ```bash
** russo (rus) **
     ```
   - **Windows**
** spagnolo (spa) **
     .\ebook2audiobook.cmd --help
     ```
** Turkish (Tur) **
    ```python
     app.py --help
** vietnamita (Vie) **

<a id="help-command-output"></a>
[;
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Requisiti hardware
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4 GB di RAM minimo, 8 GB consigliato
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualizzazione abilitata se in esecuzione su Windows (solo docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (consigliato), MPS (non ancora ottimizzato e può essere più lento della CPU) compatibile

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Prima di pubblicare un'installazione o un emissione di bug Ricerca attentamente nella scheda Aperta e chiusa <br>
Per essere sicuro che il tuo problema non esiste già. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** carente di qualsiasi struttura standard come quello che è un capitolo, paragrafo, prefazione ecc. <br>
Dovresti prima rimuovere manualmente qualsiasi testo che non vuoi essere convertito in audio. **

Istruzioni di installazione

** Clone Repo **
  --headless            Run the script in headless mode
Avvio dell'interfaccia Web Gradio
  --ebooks_dir EBOOKS_DIR
** Esegui eBook2AuDioBook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macos **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Apri l'app Web **: fai clic sull'URL fornito nel terminale per accedere all'app Web e convertire gli eBook. ** per link pubblico **:
`Python app.py --share` (All OS)
`./EBook2Audiolibook.sh --share` (Linux/MacOS)
`eBook2Audiolibook.cmd --share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!IMPORTANTE]
** Se lo script viene arrestato ed eseguito di nuovo, è necessario aggiornare l'interfaccia GUI Gradio <br>
Per consentire alla pagina Web di riconnettersi al nuovo socket di connessione. **
                        (Optional) Fine tuned model path. Default is builtin model.
Uso di base
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/macos **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-eBook] **: percorso al tuo file ebook. ** [-Voice] **: percorso del file di clonazione vocale (facoltativo). ** [-lingua] **: codice linguistico in ISO-639-3 (cioè: ita per italiano, eng per inglese, deu per tedesco ...). <br>
La lingua predefinita è ENG e -Language è facoltativo per la lingua predefinita impostata in ./lib/lang.py. <br>
Sono anche supportati i codici ISO-639-1 2 Lettere. Esempio di caricamento zip modello personalizzato
  --repetition_penalty REPETITION_PENALTY
(Deve essere un file .Zip contenente i file modello obbligatori. Esempio per XTT: config.json, model.pth, vocab.json e ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macos **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custom_model_path> **: percorso del file `model_name.zip`,
    che deve contenere (secondo il motore TTS) tutti i file obbligatori <br>
    (vedi ./lib/models.py). Per una guida dettagliata con l'elenco di tutti i parametri da utilizzare
  --output_dir OUTPUT_DIR
** Linux/macos **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** O per tutto il sistema operativo **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "help-comand output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Nota: in modalità Gradio/GUI, per annullare una conversione in esecuzione, fai clic sul [x] dal componente di caricamento ebook. Usando Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Puoi anche usare Docker per eseguire l'eBook su AudioBook Converter. Questo metodo garantisce coerenza in diversi ambienti e semplifica la configurazione. Esecuzione del contenitore Docker

Per eseguire il contenitore Docker e avviare l'interfaccia graduale, utilizzare il comando seguente:

### Using Docker
-Run solo con CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Costruire il contenitore Docker

Puoi creare l'immagine Docker con il comando:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Questo comando avverrà l'interfaccia di gradio sulla porta 7860. (LocalHost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Per ulteriori opzioni aggiungi il parametro `--help`
```


Tutti gli eBook2AudiBooks avranno la direttrice di base di `/home/utente/app/`
Per esempio:
`tmp` =`/home/utente/app/tmp`
`audiolibs` =`/home/utente/app/audiolibs`
```
Docker Headless Guide
- For more options add the parameter `--help`


## Docker container file locations
Prima di eseguirlo, è necessario creare un dir denominato "input-finder" nel tuo dir attuale
che sarà collegato, è qui che puoi mettere i tuoi file di input per l'immagine Docker da vedere
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
E questo dovrebbe essere! Gli audiolibri di output saranno trovati nella cartella audiolibro che si troverà anche
Nella tua direttrice locale hai eseguito questo comando Docker in
docker pull athomasson2/ebook2audiobook
Per ottenere il comando di aiuto per gli altri parametri questo programma è possibile eseguirlo
- Before you do run this you need to create a dir named "input-folder" in your current dir
E questo subirà questo 
[Output del comando di aiuto] (#help-comand-output)
mkdir input-folder && mkdir Audiobooks
Docker composi
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Questo progetto utilizza Docker Composi per funzionare localmente. È possibile abilitare o disabilitare il supporto GPU 
Impostando `*GPU-abilita` o`*Disabled `in` Docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Passi da eseguire
    athomasson2/ebook2audiobook \
** Clona il repository ** (se non l'hai già fatto):
```
- And that should be it! 
** Imposta il supporto GPU (disabilitato per impostazione predefinita) **
Per abilitare il supporto GPU, modificare `Docker-compose.yml` e modificare`*Disabled `a`*abilitato GPU`


** Avvia il servizio: **

```bash
** Accedi al servizio: **

```
! [Demo_Web_GUI] (Asset/Demo_Web_Gui.gif)
[Help command output](#help-command-output)


Non hai l'hardware per eseguirlo o vuoi noleggiare una GPU? Puoi duplicare lo spazio Hugginface e noleggiare una GPU per circa $ 0,40 l'ora
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[HuggingFace Space Demo] (#HuggingFace-Space-Demo)


[GRATUITO Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Problemi comuni di Docker
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker si blocca a scaricare modelli perfetti. (Questo non accade per ogni computer, ma alcuni sembrano riscontrare questo problema)
Disabilitare la barra di avanzamento sembra risolvere il problema,
Come discusso [qui in #191] (https://github.com/drewthomasson/eBook2audiolibook/issues/191)
Esempio di aggiunta di questa correzione nel comando `Docker run`
3. **Start the service:**
Modelli TTS sintonizzati fine
    docker-compose up -d
Puoi perfezionare facilmente il tuo modello XTTS con questo repository
[XTTS-Finetune-Webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-FineTUNEWEBUI-SPACE] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Uno spazio che puoi utilizzare per degannare facilmente anche i dati di allenamento
[denoise huggingface-space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Collezione TTS sintonizzata fine
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Per trovare la nostra collezione di modelli TTS già perfezionati,


## Renting a GPU
Demo
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Voce del giorno di pioggia **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough Voice **


Formati di ebook supportati
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** migliori risultati **: `.epub` o` .mobi` per il rilevamento automatico di capitoli
    -p 7860:7860 athomasson2/ebook2audiobook
Produzione


! [Esempio] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Problemi comuni:

La CPU è lenta (migliore sulla CPU SPP Server) mentre la GPU NVIDIA può avere una conversione quasi in tempo reale. [Discussione su questo] (https://github.com/drewthomasson/ebook2audiobbook/discussions/19#discussioncomment-10879846)
Per una generazione multilingue più veloce suggerirei l'altro mio

(Tuttavia, non ha una clonazione vocale a zero colpi, ed è voci di qualità Siri, ma è molto più veloce per la CPU). "Sto avendo problemi di dipendenza" - usa solo il docker, è completamente autonomo e ha una modalità senza testa,
 Aggiungi il parametro `--help` alla fine del comando Docker Run per ulteriori informazioni. "Sto ottenendo un problema audio troncato!" - Si prega di fare un problema,

### Fine Tuned TTS Collection
Cosa ho bisogno di aiuto! 🙌
[L'elenco completo delle cose è disponibile qui] (https://github.com/drewthomasson/ebook2audiolibook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potenzialmente creazione di guide di readme per più lingue (perché l'unica lingua che conosco è l'inglese 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui ts **: [Coqui tts github] (https://github.com/idiap/coqui-ai-ts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [sito Web di ffmpeg] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
È possibile visualizzare il codice [qui] (Legacy/v1.0). Unisciti al nostro server! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)