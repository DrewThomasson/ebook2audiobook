📚 eBook2AudioBook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
CPU/GPU -Konverter von eBooks zu Hörbüchern mit Kapiteln und Metadaten <br/>
Verwenden von Kaliber, FFMPEG, XTTSV2, Fairseq und mehr. Unterstützt Sprachklonen und +1110 Sprachen! [!WICHTIG]
** Dieses Tool dient zur Verwendung mit nicht-dRM, nur legal erfassten E-Books. ** <br>
Die Autoren sind nicht für den Missbrauch dieser Software oder die daraus resultierenden rechtlichen Konsequenzen verantwortlich. <br>
Verwenden Sie dieses Tool verantwortungsbewusst und gemäß allen geltenden Gesetzen. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)]] (https://discord.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko-fi-f16061?style=for-the-badge&logo=ko-fi&logocolor=white)] (https: // ko-fi .com/athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_Web_Gui] (Assets/Demo_Web_Gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العرب sehr (Arabisch)] (./ Readme/Readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文 (chinesisch)] (./ Readme/Readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
Swe [Svenska (schwedisch)] (./ Readme/Readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فارسی (persisch)] (./ Readme/Readme_fa.md)


## Table of Contents
[eBook2AudioBook] (#-eBook2AudioBook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Funktionen] (#Funktionen)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker GUI-Schnittstelle] (#Docker-Gui-Schnittstelle)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Huggingface Space Demo] (#Huggingface-Raum-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Kostenloser Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Vorgefertigte Audio-Demos] (#Demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Unterstützte Sprachen] (#unterstützte Sprachen)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Anforderungen] (#Hardware-Requirements)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Installationsanweisungen] (#Installationsinstruktionen)
- [Output](#output)
- [Common Issues](#common-issues)
[Nutzung] (#Startgradio-Web-Schnittstelle)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Start der Gradio-Weboberfläche] (#Startgradio-Web-Schnittstelle)


[Grundlegender Kopfloser Nutzung] (#grundlegend-usage)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Headless Custom XTTS-Modellverwendung] (#BEISPUCH-VON KOSTOM-MODEL-ZIP-UPAD)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Mieten Sie eine GPU] (#mieten-a-gpu)


[HILFE-Befehlsausgabe] (#Help-Command-Output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Feinabstimmige TTS-Modelle] (#feine abgestimmte TTS-Modelle)


[Für die Sammlung von fein abgestimmten TTS-Modellen] (#feine abgestimmte TTS-Sammlung)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Running-the-Docker-Container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Building-the-Docker-Container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#Docker-Compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide] (#Docker-Headless-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[DOCKER-Containerdatei-Standorte] (#Docker-Container-Datei-Lokationen)
- **Portuguese (por)**
- **Russian (rus)**
[Common Docker-Probleme] (#Common-Docker-Ausgaben)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Unterstützte E-Book-Formate] (#unterstützte-ebook-Formate)


[Ausgabe] (#Ausgabe)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Gemeinsame Probleme] (#Common-Ausgaben)


[Besonderer Dank] (#Sonderdanker)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Merkmale
```bash
📖 Konvertiert eBooks mit Kaliber in ein Textformat. 📚 Teilen Sie das eBook in Kapitel für organisierte Audio ein. 🎙️ hochwertige Text-zu-Speech mit [Coqui Xttsv2] (https://huggingface.co/coqui/xtts-v2) und [fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ Beispiele/mm) (und mehr). 🗣️ Optionales Sprachklonen mit Ihrer eigenen Sprachdatei. 🌍 unterstützt +1110 Sprachen (standardmäßig Englisch). [Liste der unterstützten Sprachen] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥️, der für 4 GB RAM ausgeführt wurde. [Huggingface Space Demo] (https://huggingface.co/spaces/drewthomasson/ebook2AudioBook)
1. **Run ebook2audiobook**:
[! [Umarmtes Gesicht] (https://img.shields.io/badge/hugging%20facespaces-yellow?style=for-he-badge&logo=huggingface)]] (https://huggingface.co/spaces/drewthomasson /eBook2AudioBook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Der Speicherplatz für den Umarmungen läuft auf der kostenlosen CPU -Stufe. Erwarten Sie also sehr langsam oder Zeitüberschreitung lol, einfach keine riesigen Dateien geben, ist alles
   - **Windows**
     ```bash
Am besten, um Platz zu duplizieren oder lokal zu laufen. Kostenloser Google Colab
     ```
[! Free Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)]] (https://colab.research.google.com/github/drewthomasson/ebebook2audiobook/bob/ main/Notebooks/colab_ebook2audioBook.ipynb)
3. **For Public Link**:
Unterstützte Sprachen
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arabisch (Ara) **

> [!IMPORTANT]
** Chinesisch (Zho) **
to let the web page reconnect to the new connection socket.**

** Tschechisch (CES) **
   - **Linux/MacOS**:
     ```bash
** Kroatisch (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Dutch (nld) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Englisch (Eng) **
     ```
     
** Französisch (Fra) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Deutsch (Deu) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** ungarisch (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** Italienisch (ita) **
     ```
   - **Windows**
** Japanisch (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Koreanisch (Kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Polnisch (pol) **


** Portugiesisch (por) **
   - **Linux/MacOS**
     ```bash
** Russisch (Rus) **
     ```
   - **Windows**
** Spanisch (Spa) **
     .\ebook2audiobook.cmd --help
     ```
** Türkisch (tur) **
    ```python
     app.py --help
** vietnamesisch (Vie) **

<a id="help-command-output"></a>
[** +1100 Sprachen über Fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Hardwareanforderungen
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4 GB RAM Minimum, 8 GB empfohlen
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualisierung aktiviert, wenn Sie unter Windows ausgeführt werden (nur Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (empfohlen), MPS (noch nicht optimiert und können langsamer sein als CPU) kompatibel

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Vor dem Posten einer Installations- oder Fehlerprobleme sorgfältig auf die Registerkarte "Geöffnete und geschlossene Probleme" <br>
Um sicherzugehen, dass Ihr Problem nicht bereits vorhanden ist. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Mangels einer Standardstruktur wie ein Kapitel, Absatz, Vorwort usw. <br>
Sie sollten zuerst jeden Text manuell entfernen, den Sie nicht in Audio konvertiert werden möchten. **

Installationsanweisungen

** Clone Repo **
  --headless            Run the script in headless mode
Starten Sie die Gradio -Weboberfläche
  --ebooks_dir EBOOKS_DIR
** Run eBook2AudioBook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Öffnen Sie die Web -App **: Klicken Sie auf die im Terminal bereitgestellte URL, um auf die Web -App zuzugreifen und eBooks zu konvertieren. ** Für öffentliche Link **:
`python app.py -Share` (All OS)
`./BOOK2AUDIOBOOK.SH --SHARE` (Linux/macOS)
`eBook2AudioBook.cmd -Share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!WICHTIG]
** Wenn das Skript gestoppt wird und erneut ausgeführt wird, müssen Sie Ihre Gradio -GUI -Schnittstelle <br> aktualisieren. <br>
Um die Webseite wieder mit dem neuen Verbindungsbuchsen zu verbinden. **
                        (Optional) Fine tuned model path. Default is builtin model.
Grundnutzung
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-eBook] **: Pfad zu Ihrer E-Book-Datei. ** [-Voice] **: Voice Cloning-Dateipfad (optional). ** [-Sprache] **: Sprachcode in ISO-639-3 (d. H. ITA für Italienisch, Eng für Englisch, DEU für Deutsch ...). <br>
Standardsprache ist Eng und -Sprache ist optional für die Standardsprache in ./lib/lang.py. <br>
Die ISO-639-1 2 Buchstabencodes werden ebenfalls unterstützt. Beispiel für das Upload des benutzerdefinierten Modells ZIP -Upload
  --repetition_penalty REPETITION_PENALTY
(Muss eine .zip -Datei sein, die die obligatorischen Modelldateien enthält. Beispiel für XTTS: config.json, model.pth, vocab.json und ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custom_model_path> **: Pfad zu `model_name.zip` Datei,
    die alle obligatorischen Dateien enthalten (gemäß der TTS -Engine) <br>
    (siehe ./lib/models.py). Eine detaillierte Anleitung mit der Liste aller zu verwendenden Parameter
  --output_dir OUTPUT_DIR
** Linux/macOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** oder für alle Betriebssysteme **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "help-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
HINWEIS: Im Gradio/GUI -Modus, um eine laufende Konvertierung abzubrechen, klicken Sie einfach auf die [X] aus der E -Book -Upload -Komponente. Verwenden von Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Sie können auch Docker verwenden, um das eBook auf Hörbücherkonverter auszuführen. Diese Methode sorgt für die Konsistenz in verschiedenen Umgebungen und vereinfacht das Setup. Ausführen des Docker -Containers

Verwenden Sie den folgenden Befehl, um den Docker -Container auszuführen und die Gradio -Schnittstelle zu starten:

### Using Docker
-Run nur mit CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Bauen des Docker -Containers

Sie können das Docker -Bild mit dem Befehl erstellen:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Dieser Befehl startet die Gradio -Schnittstelle auf Port 7860. (Localhost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Für weitere Optionen fügen Sie den Parameter `-HELP` hinzu
```


Alle eBook2AudioBooks haben die Basis -Dire von `/home/user/app/`
Zum Beispiel:
`tmp` =`/home/user/app/tmp`
`audioBooks` =`/home/user/app/audioBooks`
```
Docker Headless Guide
- For more options add the parameter `--help`


## Docker container file locations
Bevor Sie dies ausführen
Dies wird verknüpft. Hier können Sie Ihre Eingabedateien für das Docker -Image einstellen, um sie anzuzeigen
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
Und das sollte es sein! Die Ausgabe -Hörbücher finden Sie im Ordner Hörbücher, der sich ebenfalls befinden wird
In Ihrem lokalen Dir haben Sie diesen Docker -Befehl in ausgeführt
docker pull athomasson2/ebook2audiobook
Um den Befehl Hilfe für die anderen Parameter dieses Programms zu erhalten, können Sie dies ausführen
- Before you do run this you need to create a dir named "input-folder" in your current dir
Und das wird dies ausgeben 
[HILFE-Befehlsausgabe] (#Help-Command-Output)
mkdir input-folder && mkdir Audiobooks
Docker komponieren
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
In diesem Projekt wird Docker Compose verwendet, um lokal auszuführen. Sie können die GPU -Unterstützung aktivieren oder deaktivieren 
Durch Einstellen von `*gpu-fähigen" oder `*gpu-desinders in` docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Schritte zum Laufen
    athomasson2/ebook2audiobook \
** Klonen Sie das Repository ** (wenn Sie es noch nicht getan haben):
```
- And that should be it! 
** Setzen Sie den GPU -Support (standardmäßig deaktiviert) **
Um die Unterstützung von GPU zu aktivieren, ändern Sie `docker-compose.yml` und ändern


** Starten Sie den Service: **

```bash
** Greifen Sie auf den Service zu: **

```
! [Demo_Web_Gui] (Assets/Demo_Web_Gui.gif)
[Help command output](#help-command-output)


Sie haben nicht die Hardware, um sie auszuführen, oder Sie möchten eine GPU mieten? Sie können den Hugginface -Raum duplizieren und eine GPU für rund 0,40 US -Dollar pro Stunde mieten
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Huggingface Space Demo] (#Huggingface-Raum-Demo)


[Kostenloser Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Häufige Docker -Probleme
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker steckt fest, feine Modelle herunterzuladen. (Dies geschieht nicht für jeden Computer, aber einige scheinen auf dieses Problem zu stoßen)
Das Deaktivieren der Fortschrittsleiste scheint das Problem zu beheben.
Wie erläutert [hier in #191] (https://github.com/drewthomasson/ebook2audioBook/issues/191)
Beispiel für das Hinzufügen dieses Fixes im Befehl "Docker Run"
3. **Start the service:**
Fein abgestimmte TTS -Modelle
    docker-compose up -d
Mit diesem Repo können Sie Ihr eigenes XTTS-Modell leicht optimieren
[XTTS-Fintune-Webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-Finetune-webui-space] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Ein Raum, mit dem Sie die Trainingsdaten auch einfach entfernen können
[Denoise-Huggingface-Space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Fein abgestimmte TTS -Sammlung
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Um unsere Sammlung bereits fein abgestimmter TTS-Modelle zu finden,


## Renting a GPU
Demos
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Regeny Day Voice **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough Voice **


Unterstützte E -Book -Formate
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Beste Ergebnisse **: `.epub` oder` .mobi` Für die automatische Kapitelerkennung
    -p 7860:7860 athomasson2/ebook2audiobook
Ausgabe


! [Beispiel] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg))
You can fine-tune your own xtts model easily with this repo
Häufige Themen:

CPU ist langsam (besser auf der Server -SMP -CPU), während die NVIDIA -GPU fast in Echtzeitumwandlung durchführen kann. [Diskussion darüber] (https://github.com/drewthomasson/ebook2audioBook/discussions/19#discussionComent-10879846)
Für eine schnellere mehrsprachige Generation würde ich meinen anderen vorschlagen

(Es gibt jedoch kein Sprachklonen von Null-Shot-Klonen und ist Siri-Qualitätsstimmen, aber es ist viel schneller bei der CPU). "Ich habe Abhängigkeitsprobleme" - verwenden
 Fügen Sie am Ende des Docker Run-Befehls "-Help" Parameter hinzu, um weitere Informationen zu erhalten. "Ich bekomme ein abgeschnittenes Audio -Problem!" - Bitte machen Sie ein Problem damit,

### Fine Tuned TTS Collection
Was ich Hilfe brauche! 🙌
[Die vollständige Liste der Dinge finden Sie hier] (https://github.com/drewthomasson/ebook2audioBook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potenziell erstellen
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui tts **: [Coqui tts Github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [ffmpeg Website] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/V1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Sie können den Code [hier] (Legacy/v1.0) anzeigen. Treten Sie unserem Server bei! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)]] (https://discord.gg/63tv3f65k6)