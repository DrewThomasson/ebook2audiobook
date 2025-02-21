# 📚 eBook2AudiBook

Convertitore CPU/GPU da ebook agli audiolibri con capitoli e metadati<br/>Utilizzando Caliber, FFMPEG, XTTSV2, Fairseq e altro. Supporta la clonazione vocale e +1110 lingue!

> [!IMPORTANT]
**Questo strumento è destinato all'uso solo con e-book non acquisiti legalmente.**<br>Gli autori non sono responsabili per qualsiasi uso improprio di questo software o di conseguenze legali risultanti.<br>Utilizzare questo strumento in modo responsabile e in conformità con tutte le leggi applicabili.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Grazie a Support EBook2Audiobook Developer!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Interfaccia GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

- ara [العربية (Arabic)](./readme/README_AR.md)
- zho [中文 (Chinese)](./readme/README_CN.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
- fas [فارسی (Persian)](./readme/README_FA.md)
- ita [Italiano (Italian)](./readme/README.it.md)

## Sommario

-   [eBook2Audiokook](#-ebook2audiobook)
-   [Caratteristiche](#features)
-   [Interfaccia Docker GUI](#docker-gui-interface)
-   [Demo spaziale Huggingface](#huggingface-space-demo)
-   [Google Colab gratuito](#free-google-colab)
-   [Demos audio prefabbricate](#demos)
-   [Lingue supportate](#supported-languages)
-   [Requisiti](#hardware-requirements)
-   [Istruzioni di installazione](#installation-instructions)
-   [Utilizzo](#launching-gradio-web-interface)
    -   [Avvio dell'interfaccia Web Gradio](#launching-gradio-web-interface)
    -   [Uso di base senza testa](#basic--usage)
    -   [Utilizzo del modello personalizzato senza testa](#example-of-custom-model-zip-upload)
    -   [Affittare una GPU](#renting-a-gpu)
    -   [Aiuta l'output di comandi](#help-command-output)
-   [Modelli TTS sintonizzati fine](#fine-tuned-tts-models)
    -   [Per la raccolta di modelli TTS perfezionati](#fine-tuned-tts-collection)
-   [Usando Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Build Docker](#building-the-docker-container)
    -   [Docker composi](#docker-compose)
    -   [Docker Headless Guide](#docker-headless-guide)
    -   [Posizioni dei file container Docker](#docker-container-file-locations)
    -   [Problemi comuni di Docker](#common-docker-issues)
-   [Formati di ebook supportati](#supported-ebook-formats)
-   [Produzione](#output)
-   [Problemi comuni](#common-issues)
-   [Un ringraziamento speciale](#special-thanks)
-   [Unisciti al nostro server!](#join-our--server)
-   [Eredità](#legacy-v10)
-   [Sommario](#table-of-contents)

## Caratteristiche

-   📖 Converte gli ebook in formato di testo con calibro.
-   📚 divide l'eBook in capitoli per l'audio organizzato.
-   🎙️ Text-to-Speech di alta qualità con[Coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)E[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(e altro).
-   🗣️ Clonazione vocale opzionale con il tuo file vocale.
-   🌍 Supporta +1110 lingue (inglese per impostazione predefinita).[Elenco delle lingue supportate](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ Progettato per funzionare su 4 GB di RAM.

## [Demo spaziale Huggingface](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Lo spazio di HuggingFace è in esecuzione con il livello CPU gratuito, quindi aspettati molto lento o timeout lol, non dargli i file giganti è tutto
-   Meglio duplicare lo spazio o correre localmente.

## Google Colab gratuito

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Lingue supportate

-   **Arabo (ARA)**
-   **Cinese (ZH)**
-   **Ceco (CES)**
-   **Croato (HRV)**
-   **Olandese (NLD)**
-   **English (Eng)**
-   **Francese (da)**
-   **Tedesco (DEU)**
-   **Non (hin)**
-   **Ungherese (am)**
-   **Italiano (Ita)**
-   **Giapponese (jpn)**
-   **Coreano (cor)**
-   **Polish (Pol)**
-   **Portoghese (POR)**
-   **Russia (Rus)**
-   **Spagnolo (spa)**
-   **Turco (round)**
-   **Vietnamese (vie)**
-   [**+1100 lingue tramite Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Requisiti hardware

-   4 GB di RAM minimo, 8 GB consigliato
-   Virtualizzazione abilitata se in esecuzione su Windows (solo docker)
-   CPU, GPU (consigliato), MPS (non ancora ottimizzato e può essere più lento della CPU) compatibile

> [!IMPORTANT]
**Prima di pubblicare una ricerca di emissione di installazione o bug attentamente nella scheda Aperta e chiusa<br>Per essere sicuro che il tuo problema non esista già.**

> [!NOTE]
**In mancanza di una struttura standard come quello che è un capitolo, un paragrafo, una prefazione ecc.<br>Dovresti prima rimuovere manualmente qualsiasi testo che non vuoi essere convertito in audio.**

### Istruzioni di installazione

1.  **Clone Repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Avvio dell'interfaccia Web Gradio

1.  **Esegui eBook2AudiBook**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Finestre**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Apri l'app Web**: Fare clic sull'URL fornito nel terminale per accedere all'app Web e convertire gli eBook.
3.  **Per collegamento pubblico**:`python app.py --share`(Tutto il sistema operativo)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!IMPORTANT]
**Se lo script viene interrotto ed eseguito di nuovo, è necessario aggiornare l'interfaccia GUI di Gradio<br>Per consentire alla pagina Web di riconnettersi al nuovo socket di connessione.**

### Uso di base

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Finestre**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Ebook]**: Percorso per il tuo file ebook.
-   **[--voce]**: Percorso del file di clonazione vocale (facoltativo).
-   **[--lingua]**: Codice di lingua in ISO-639-3 (cioè: Ita per italiano, Eng per l'inglese, Deu per tedesco ...).<br>La lingua predefinita è ENG e -Language è facoltativo per la lingua predefinita impostata in ./lib/lang.py.<br>Sono anche supportati i codici ISO-639-1 2 Lettere.

### Esempio di caricamento zip modello personalizzato

(Deve essere un file .Zip contenente i file modello obbligatori. Esempio per XTT: config.json, model.pth, vocab.json e ref.wav)

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Finestre**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**: Path to`model_name.zip`file,
        che deve contenere (secondo il motore TTS) tutti i file obbligatori<br>(vedi ./lib/models.py).

### Per una guida dettagliata con l'elenco di tutti i parametri da utilizzare

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Finestre**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **O per tutto il sistema operativo**
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

Nota: in modalità Gradio/GUI, per annullare una conversione in esecuzione, fai clic su[X]Dal componente caricamento ebook.

### Usando Docker

Puoi anche usare Docker per eseguire l'eBook su AudioBook Converter. 
Questo metodo garantisce coerenza in diversi ambienti e semplifica la configurazione.

#### Esecuzione del contenitore Docker

Per eseguire il contenitore Docker e avviare l'interfaccia graduale, utilizzare il comando seguente:

\-Run solo con CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run con accelerazione GPU (solo Nvidia compatibile)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Costruire il contenitore Docker

-   Puoi creare l'immagine Docker con il comando:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Questo comando avverrà l'interfaccia di gradio sulla porta 7860. (LocalHost: 7860)

-   Per ulteriori opzioni aggiungi il parametro`--help`

## Posizioni dei file container Docker

Tutti gli eBook2Audibooks avranno la dirmatura di base di`/home/user/app/`Per esempio:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker Headless Guide

Primo per una pista da docker dell'ultimo con

```bash
docker pull athomasson2/ebook2audiobook
```

-   Prima di eseguirlo, è necessario creare un dir denominato "input-finder" nel tuo dir attuale
    che sarà collegato, è qui che puoi mettere i tuoi file di input per l'immagine Docker da vedere

```bash
mkdir input-folder && mkdir Audiobooks
```

-   Nel comando sotto lo scambio**Your_input_file.txt**Con il nome del tuo file di input

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   E questo dovrebbe essere!
-   Gli audiolibri di output saranno trovati nella cartella audiolibro che si troverà anche
    Nella tua direttrice locale hai eseguito questo comando Docker in

## Per ottenere il comando di aiuto per gli altri parametri questo programma è possibile eseguirlo

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

E questo subirà questo[Aiuta l'output di comandi](#help-command-output)

### Docker composi

Questo progetto utilizza Docker Composi per funzionare localmente. È possibile abilitare o disabilitare il supporto GPU 
Impostando nemmeno`*gpu-enabled`O`*gpu-disabled`In`docker-compose.yml`

#### Passi da eseguire

1.  **Clona il repository**(se non l'hai già fatto):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Imposta supporto GPU (disabilitato per impostazione predefinita)**Per abilitare il supporto GPU, modificare`docker-compose.yml`e cambiare`*gpu-disabled`A`*gpu-enabled`
3.  **Avvia il servizio:**
    ```bash
    docker-compose up -d
    ```
4.  **Accedi al servizio:**Il servizio sarà disponibile su http&#x3A; // localhost: 7860.

### Interfaccia Docker GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Affittare una GPU

Non hai l'hardware per eseguirlo o vuoi noleggiare una GPU?

#### Puoi duplicare lo spazio Hugginface e noleggiare una GPU per circa $ 0,40 l'ora

[Demo spaziale Huggingface](#huggingface-space-demo)

#### Oppure puoi provare a utilizzare Google Colab gratuitamente!

(Essere consapevoli che scaterirà dopo un po 'di non scherzare con Google Colab)[Google Colab gratuito](#free-google-colab)

## Problemi comuni di Docker

-   Docker si blocca a scaricare modelli perfetti.
    (Questo non accade per ogni computer, ma alcuni sembrano riscontrare questo problema)
    Disabilitare la barra di avanzamento sembra risolvere il problema,
    come discusso[Qui nel #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Esempio di aggiunta di questa correzione in`docker run`comando

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Modelli TTS sintonizzati fine

Puoi perfezionare facilmente il tuo modello XTTS con questo repository[XTS-FineTune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Se vuoi affittare facilmente una GPU, puoi anche duplicare questo Huggingface[XTTS-FineTune-Webui-Space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Uno spazio che puoi utilizzare per degannare facilmente anche i dati di allenamento[Denaise-Huggingface-Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Collezione TTS sintonizzata fine

Per trovare la nostra collezione di modelli TTS già perfezionati,
visita[Questo collegamento facciale abbracciato](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Per un modello personalizzato XTT Un clip audio REF del riferimento vocale è obbligatorio:

## Demo

**Voce del giorno delle piogge**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Formati di ebook supportati

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **I migliori risultati**:`.epub`O`.mobi`Per il rilevamento automatico di capitoli

## Produzione

-   Crea un`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Imposta nel file ./lib/conf.py) con metadati e capitoli.
-   **Esempio**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Problemi comuni:

-   La CPU è lenta (migliore sulla CPU SPP Server) mentre la GPU NVIDIA può avere una conversione quasi in tempo reale.[Discussione su questo](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Per una generazione multilingue più veloce suggerirei l'altro mio[Progetto che utilizza Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)Invece
    (Tuttavia, non ha una clonazione vocale a zero colpi, ed è voci di qualità Siri, ma è molto più veloce per la CPU).
-   "Sto avendo problemi di dipendenza" - usa solo il docker, è completamente autonomo e ha una modalità senza testa,
     aggiungere`--help`Parametro alla fine del comando Docker Run per ulteriori informazioni.
-   "Sto ottenendo un problema audio troncato!" - Si prega di fare un problema,
     Non parliamo di ogni lingua e abbiamo bisogno di consigli agli utenti di mettere a punto la logica di scissione della frase .😊

## Cosa ho bisogno di aiuto! 🙌

## [L'elenco completo delle cose può essere trovato qui](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Qualsiasi aiuto da parte di persone che parlano di una delle lingue supportate per aiutare con i metodi di divisione delle frasi adeguate
-   Potenzialmente creazione di guide Readme per più lingue (perché l'unica lingua che conosco è l'inglese 😔)

## Un ringraziamento speciale

-   **Cucinare TTS**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Calibro**:[Sito Web calibro](https://calibre-ebook.com)
-   **Ffmpeg**:[Sito Web FFMPEG](https://ffmpeg.org)
-   [@shakenbake15 per un migliore metodo di salvataggio dei capitoli](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Puoi visualizzare il codice[Qui](legacy/v1.0).

## Unisciti al nostro server!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
