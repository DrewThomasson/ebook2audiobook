# 📚 eBook2AudioBook

CPU/GPU -Konverter von eBooks zu Hörbüchern mit Kapiteln und Metadaten<br/>Verwenden von Kaliber, FFMPEG, XTTSV2, Fairseq und mehr. Unterstützt Sprachklonen und +1110 Sprachen!

> [!WICHTIG]**Dieses Tool dient zur Verwendung mit nicht-dRM, nur legal erfassten E-Books.**<br>Die Autoren sind nicht für den Missbrauch dieser Software oder die daraus resultierenden rechtlichen Konsequenzen verantwortlich.<br>Verwenden Sie dieses Tool verantwortungsbewusst und gemäß allen geltenden Gesetzen.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Vielen Dank an die Unterstützung eBook2AudioBook -Entwickler!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI -Schnittstelle

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Wir kaufen[Arabisch (Arabisch)](./readme/README_AR.md)
-   Zho[chinesisch](./readme/README_CN.md)
-   a \`a[Englisch](README.md)
-   Swe[Schwedisch (schwedisch)](./readme/README_SWE.md)
-   Fas[Persisch (Persisch)](./readme/README_FA.md)
-   sie[Italienisch (Italienisch)](./readme/README.it.md)

## Inhaltsverzeichnis

-   [eBook2AudioBook](#-ebook2audiobook)
-   [Merkmale](#features)
-   [Docker GUI -Schnittstelle](#docker-gui-interface)
-   [Umarmung der Space Demo](#huggingface-space-demo)
-   [Kostenloser Google Colab](#free-google-colab)
-   [Vorgefertigte Audio-Demos](#demos)
-   [Unterstützte Sprachen](#supported-languages)
-   [Anforderungen](#hardware-requirements)
-   [Installationsanweisungen](#installation-instructions)
-   [Verwendung](#launching-gradio-web-interface)
    -   [Starten Sie die Gradio -Weboberfläche](#launching-gradio-web-interface)
    -   [Grundlegende kopflose Nutzung](#basic--usage)
    -   [Kopflosen benutzerdefinierten XTTS -Modellverbrauch](#example-of-custom-model-zip-upload)
    -   [Mieten Sie eine GPU](#renting-a-gpu)
    -   [HILFE -Befehlsausgabe](#help-command-output)
-   [Fein abgestimmte TTS -Modelle](#fine-tuned-tts-models)
    -   [Für die Sammlung von fein abgestimmten TTS-Modellen](#fine-tuned-tts-collection)
-   [Verwenden von Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker komponieren](#docker-compose)
    -   [Docker Headless Guide](#docker-headless-guide)
    -   [Docker -Containerdatei -Standorte](#docker-container-file-locations)
    -   [Häufige Docker -Probleme](#common-docker-issues)
-   [Unterstützte E -Book -Formate](#supported-ebook-formats)
-   [Ausgabe](#output)
-   [Häufige Probleme](#common-issues)
-   [Besonderer Dank](#special-thanks)
-   [Treten Sie unserem Server bei!](#join-our--server)
-   [Vermächtnis](#legacy-v10)
-   [Inhaltsverzeichnis](#table-of-contents)

## Merkmale

-   📖 Konvertiert eBooks mit Kaliber in ein Textformat.
-   📚 Teilen Sie das eBook in Kapitel für organisierte Audio ein.
-   🎙️ hochwertige Text-zu-Sprache mit[Coqui XTSV2](https://huggingface.co/coqui/XTTS-v2)Und[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(und mehr).
-   🗣️ Optionales Sprachklonen mit Ihrer eigenen Sprachdatei.
-   🌍 unterstützt +1110 Sprachen (standardmäßig Englisch).[Liste der unterstützten Sprachen](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️, der für 4 GB RAM ausgeführt wurde.

## [Umarmung der Space Demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Der Speicherplatz für den Umarmungen läuft auf der kostenlosen CPU -Stufe. Erwarten Sie also sehr langsam oder Zeitüberschreitung lol, einfach keine riesigen Dateien geben, ist alles
-   Am besten, um Platz zu duplizieren oder lokal zu laufen.

## Kostenloser Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Unterstützte Sprachen

-   **Arabisch (ARA)**
-   **Chinesisch (ZH)**
-   **Tschechisch (CES)**
-   **Kroatisch (HRV)**
-   **Niederländisch (NLD)**
-   **Englisch (ENG)**
-   **Französisch (von)**
-   **Deutsch (Deu)**
-   **Hindi (hin)**
-   **Ungarisch (AM)**
-   **Italienisch (ita)**
-   **Japanisch (JPN)**
-   **Koreanisch (Cor)**
-   **Polnisch (pol)**
-   **Portugiesisch (Por)**
-   **Russisch (Rus)**
-   **Spanisch (Spa)**
-   **Türkisch (runde)**
-   **Vietnamesisch (Vie)**
-   [**+1100 Sprachen über Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Hardwareanforderungen

-   4 GB RAM Minimum, 8 GB empfohlen
-   Virtualisierung aktiviert, wenn Sie unter Windows ausgeführt werden (nur Docker)
-   CPU, GPU (empfohlen), MPS (noch nicht optimiert und können langsamer sein als CPU) kompatibel

> [!WICHTIG]**Bevor Sie eine Installations- oder Fehlerprobleme sorgfältig auf die Registerkarte "Geöffnete und geschlossene Probleme" veröffentlichen<br>Um sicherzustellen, dass Ihr Problem nicht bereits vorhanden ist.**

> [!NOTIZ]**Fehlen einer Standardstruktur wie ein Kapitel, Absatz, Vorwort usw.<br>Sie sollten zuerst jeden Text manuell entfernen, den Sie nicht in Audio konvertiert werden möchten.**

### Installationsanweisungen

1.  **Klonrepo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Starten Sie die Gradio -Weboberfläche

1.  **Run eBook2AudioBook**:
    -   **Linux/macos**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Fenster**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Öffnen Sie die Web -App**: Klicken Sie auf die im Terminal bereitgestellte URL, um auf die Web -App zuzugreifen und eBooks zu konvertieren.
3.  **Für öffentliche Link**:`python app.py --share`(Alle Betriebssysteme)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!WICHTIG]**Wenn das Skript gestoppt und wieder ausgeführt wird, müssen Sie Ihre Gradio GUI -Schnittstelle aktualisieren<br>Um die Webseite wieder mit dem neuen Verbindungsbuchsen zu verbinden.**

### Grundnutzung

-   **Linux/macos**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Fenster**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Book]**: Pfad zu Ihrer E -Book -Datei.
-   **[--Stimme]**: Voice Cloning -Dateipfad (optional).
-   **[--Sprache]**: Sprachcode in ISO-639-3 (d. H. ITA für Italienisch, Eng für Englisch, Deu für Deutsch ...).<br>Standardsprache ist Eng und -Sprache ist optional für die Standardsprache in ./lib/lang.py.<br>Die ISO-639-1 2 Buchstabencodes werden ebenfalls unterstützt.

### Beispiel für das Upload des benutzerdefinierten Modells ZIP -Upload

(Muss eine .zip -Datei sein, die die obligatorischen Modelldateien enthält. Beispiel für XTTS: config.json, model.pth, vocab.json und ref.wav)

-   **Linux/macos**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Fenster**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;Custom_model_path>**: Weg zu`model_name.zip`Datei,
        die alle obligatorischen Dateien enthalten müssen (gemäß der TTS -Engine)<br>(siehe ./lib/models.py).

### Eine detaillierte Anleitung mit der Liste aller zu verwendenden Parameter

-   **Linux/macos**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Fenster**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Oder für alle Betriebssysteme**
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

Hinweis: Um eine laufende Konvertierung abzubrechen, klicken Sie im Gradio/GUI -Modus einfach auf die[X]Aus der E -Book -hochladungskomponente.

### Verwenden von Docker

Sie können auch Docker verwenden, um das eBook auf Hörbücherkonverter auszuführen. 
Diese Methode sorgt für die Konsistenz in verschiedenen Umgebungen und vereinfacht das Setup.

#### Ausführen des Docker -Containers

Verwenden Sie den folgenden Befehl, um den Docker -Container auszuführen und die Gradio -Schnittstelle zu starten:

\-Run nur mit CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run mit GPU -Geschwindigkeit (nur NVIDIA -kompatibel)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Bauen des Docker -Containers

-   Sie können das Docker -Bild mit dem Befehl erstellen:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Dieser Befehl startet die Gradio -Schnittstelle auf Port 7860. (Localhost: 7860)

-   Für weitere Optionen fügen Sie den Parameter hinzu`--help`

## Docker -Containerdatei -Standorte

Alle eBook2AudioBooks haben die Basisdire von`/home/user/app/`Zum Beispiel:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker Headless Guide

zuerst für einen Docker -Zug von der neuesten mit

```bash
docker pull athomasson2/ebook2audiobook
```

-   Bevor Sie dies ausführen
    Dies wird verknüpft. Hier können Sie Ihre Eingabedateien für das Docker -Image einstellen, um sie anzuzeigen

```bash
mkdir input-folder && mkdir Audiobooks
```

-   Im folgenden Befehl tauschen Sie aus**Your_input_file.txt**Mit dem Namen Ihrer Eingabedatei

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   Und das sollte es sein!
-   Die Ausgabe -Hörbücher finden Sie im Ordner Hörbücher, der sich ebenfalls befinden wird
    In Ihrem lokalen Dir haben Sie diesen Docker -Befehl in ausgeführt

## Um den Befehl Hilfe für die anderen Parameter dieses Programms zu erhalten, können Sie dies ausführen

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

Und das wird dies ausgeben[HILFE -Befehlsausgabe](#help-command-output)

### Docker komponieren

In diesem Projekt wird Docker Compose verwendet, um lokal auszuführen. Sie können die GPU -Unterstützung aktivieren oder deaktivieren 
durch ein Festlegen`*gpu-enabled`oder`*gpu-disabled`In`docker-compose.yml`

#### Schritte zum Laufen

1.  **Klonen Sie das Repository**(Wenn Sie es noch nicht getan haben):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Stellen Sie den GPU -Support fest (standardmäßig deaktiviert)**Um die GPU -Unterstützung zu aktivieren, ändern Sie`docker-compose.yml`und ändern`*gpu-disabled`Zu`*gpu-enabled`
3.  **Starten Sie den Service:**
    ```bash
    docker-compose up -d
    ```
4.  **Zugriff auf den Service:**Der Service ist unter http&#x3A; // localhost: 7860 erhältlich.

### Docker GUI -Schnittstelle

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Mieten Sie eine GPU

Sie haben nicht die Hardware, um sie auszuführen, oder Sie möchten eine GPU mieten?

#### Sie können den Hugginface -Raum duplizieren und eine GPU für rund 0,40 US -Dollar pro Stunde mieten

[Umarmung der Space Demo](#huggingface-space-demo)

#### Oder Sie können versuchen, das Google Colab kostenlos zu verwenden!

(Seien Sie sich bewusst, dass es sich nach einigem Spiel mit dem Google Colab einteilen.)[Kostenloser Google Colab](#free-google-colab)

## Häufige Docker -Probleme

-   Docker steckt fest, feine Modelle herunterzuladen.
    (Dies geschieht nicht für jeden Computer, aber einige scheinen auf dieses Problem zu stoßen)
    Das Deaktivieren der Fortschrittsleiste scheint das Problem zu beheben.
    Wie diskutiert[Hier in #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Beispiel für das Hinzufügen dieses Fixes in der`docker run`Befehl

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Fein abgestimmte TTS -Modelle

Mit diesem Repo können Sie Ihr eigenes XTTS-Modell leicht optimieren[XTS-Finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Wenn Sie eine GPU problemlos mieten möchten, können Sie dieses Umarmungsfeld auch duplizieren[XTS-Finetune-Webui-Raum](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Ein Raum, mit dem Sie die Trainingsdaten auch einfach entfernen können[Denoise-Hugging-Face-Raum](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Fein abgestimmte TTS -Sammlung

Um unsere Sammlung bereits fein abgestimmter TTS-Modelle zu finden,
besuchen[Dieser umarmende Gesichtslink](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Für ein XTTS -benutzerdefiniertes Modell ist ein Ref -Audioclip der Sprachreferenz obligatorisch:

## Demos

**Regnerische Tagstimme**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Unterstützte E -Book -Formate

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Beste Ergebnisse**:`.epub`oder`.mobi`zur automatischen Kapitelerkennung

## Ausgabe

-   Erstellt a`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Set in ./lib/conf.py) Datei mit Metadaten und Kapiteln.
-   **Beispiel**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Häufige Themen:

-   CPU ist langsam (besser auf der Server -SMP -CPU), während die NVIDIA -GPU fast in Echtzeitumwandlung durchführen kann.[Diskussion darüber](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Für eine schnellere mehrsprachige Generation würde ich meinen anderen vorschlagen[Projekt, das Piper-TTS verwendet](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)stattdessen
    (Es gibt jedoch kein Sprachklonen von Null-Shot-Klonen und ist Siri-Qualitätsstimmen, aber es ist viel schneller bei der CPU).
-   "Ich habe Abhängigkeitsprobleme" - verwenden
     hinzufügen`--help`Parameter am Ende des Befehls Docker Run für weitere Informationen.
-   "Ich bekomme ein abgeschnittenes Audio -Problem!" - Bitte machen Sie ein Problem damit,
     Wir sprechen nicht jede Sprache und müssen von den Benutzern beraten, die Satzspaltung Logik zu beenden. 😊

## Was ich Hilfe brauche! 🙌

## [Die vollständige Liste der Dinge finden Sie hier](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Jede Hilfe von Personen, die eine der unterstützten Sprachen sprechen, um bei den richtigen Satzspaltmethoden zu helfen
-   Potenziell erstellen

## Besonderer Dank

-   **TTS kochen**:[Coqui tts Github](https://github.com/idiap/coqui-ai-TTS)
-   **Kaliber**:[Kaliberwebsite](https://calibre-ebook.com)
-   **Ffmpeg**:[FFMPEG -Website](https://ffmpeg.org)
-   [@Shakenbake15 für eine bessere Kapitelsparenmethode](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Sie können den Code anzeigen[Hier](legacy/v1.0).

## Treten Sie unserem Server bei!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
