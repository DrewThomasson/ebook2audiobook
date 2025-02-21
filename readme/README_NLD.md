📚 ebook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
CPU/GPU -converter van e -boeken tot audioboeken met hoofdstukken en metadata <br/>
met behulp van kaliber, FFMPEG, XTTSV2, Fairseq en meer. Ondersteunt spraakklonen en +1110 talen! [!BELANGRIJK]
** Deze tool is bedoeld voor gebruik met niet-DRM, alleen wettelijk verworven eBooks. ** <br>
De auteurs zijn niet verantwoordelijk voor misbruik van deze software of resulterende juridische gevolgen. <br>
Gebruik deze tool verantwoordelijk en in overeenstemming met alle toepasselijke wetten. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko--fi-f16061?style=for-the-badge&logo=ko-fi&logocolor=white)] (https: // ko-fi .com/Athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_web_gui] (Assets/demo_web_gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ARA [العربية (Arabisch)] (./ README/README_AR.MD)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
Zho [中文 (Chinees)] (./ README/README_CN.MD)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
Swe [Svenska (Zweeds)] (./ README/README_SWE.MD)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فارسی (Perzisch)] (./ README/README_FA.MD)


## Table of Contents
[Ebook2audiobook] (#-Ebook2audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Functies] (#Functies)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker GUI-interface] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Huggingface Space Demo] (#Huggingface-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Gratis Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Pre-gemaakte audio-demo's] (#Demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Ondersteunde talen] (#Ondersteunde talen)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Vereisten] (#Hardware-vereiste)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Installatie-instructies] (#Installatie-instructies)
- [Output](#output)
- [Common Issues](#common-issues)
[Gebruik] (#Launching-Gradio-Web-Interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Launching Gradio Web Interface] (#Launching-Gradio-Web-Interface)


[Basic Headless Usage] (#Basic-usage)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Headless Custom XTTS-modelgebruik] (#Voorbeeld-van-Custom-Model-Zip-Upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Een GPU huren] (#Renting-a-GPU)


[Help-opdrachtuitvoer] (#Help-command-output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Fine Tuned TTS-modellen] (#Fine-Tuned-TTS-modellen)


[Voor het verzamelen van verfijnde TTS-modellen] (#Fine-Tuned-TTS-verzameling)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Running-the-Docker-Container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Building-the-Docker-Container)
- **English (eng)**
- **French (fra)**
[Docker compose] (#docker-compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide] (#Docker-Headless-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Docker Container File Locations] (#Docker-Container-file-locaties)
- **Portuguese (por)**
- **Russian (rus)**
[Common Docker-problemen] (#Common-Docker-Issues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Ondersteunde eBook-formaten] (#Ondersteunde-book-formaten)


[Output] (#Output)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Gemeenschappelijke problemen] (#Common-Issues)


[Special Thank] (#Special-Thanks)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Functies
```bash
📖 Converteert eBooks naar tekstformaat met kaliber. 📚 splitst e -boek in hoofdstukken voor georganiseerde audio. 🎙️ hoge kwaliteit tekst-naar-speech met [coqui xttSv2] (https://huggingface.co/coqui/ults-v2) en [fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ Voorbeelden/mms) (en meer). 🗣️ Optioneel spraakklonering met uw eigen spraakbestand. 🌍 Ondersteunt +1110 talen (standaard Engels). [Lijst met ondersteunde talen] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥️ Ontworpen om te draaien op 4 GB RAM. [Huggingface Space Demo] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [Hugging Face] (https://img.shields.io/badge/hugging%20face-spaces-yellow?style=for-the-badge&logo=huggingface)] (https://huggingface.co/spaces/drewthomasson /eBook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Huggingface Space draait op gratis CPU -laag, dus verwacht erg langzaam of time -out lol, geef het gewoon geen gigantische bestanden
   - **Windows**
     ```bash
Het beste om ruimte te dupliceren of lokaal te rennen. Gratis Google Colab
     ```
[! [Gratis Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)] (https://colab.research.google.com/github/drewthomasson/iebook2audiobook/Blob/ main/notebooks/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Ondersteunde talen
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arabisch (ara) **

> [!IMPORTANT]
** Chinees (Zho) **
to let the web page reconnect to the new connection socket.**

** Tsjech (CES) **
   - **Linux/MacOS**:
     ```bash
** Kroatisch (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Nederlands (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Engels (eng) **
     ```
     
** Frans (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Duits (DEU) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Hongaars (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** Italiaans (ita) **
     ```
   - **Windows**
** Japans (jpn) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Koreaans (KOR) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Pools (pol) **


** Portugees (por) **
   - **Linux/MacOS**
     ```bash
** Russisch (rus) **
     ```
   - **Windows**
** Spaans (spa) **
     .\ebook2audiobook.cmd --help
     ```
** Turks (tur) **
    ```python
     app.py --help
** Vietnamees (vie) **

<a id="help-command-output"></a>
[** +1100 talen via Fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Hardwarevereisten
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4 GB RAM -minimum, 8 GB aanbevolen
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualisatie ingeschakeld als het wordt uitgevoerd op Windows (alleen Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (aanbevolen), MPS (nog niet geoptimaliseerd en kan langzamer zijn dan CPU)

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Voordat u een installatie- of bug -uitgave zorgvuldig zoeken naar het tabblad Opende en gesloten problemen
Om er zeker van te zijn dat uw probleem nog niet bestaat. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Bij gebrek aan een standaardstructuur zoals een hoofdstuk, paragraaf, voorwoord enz. <br>
U moet eerst handmatig alle tekst verwijderen die u niet in audio wilt converteren. **

Installatie -instructies

** kloon repo **
  --headless            Run the script in headless mode
Gradio Web -interface starten
  --ebooks_dir EBOOKS_DIR
** Voer eBook2audiobook ** uit:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Open de web -app **: klik op de URL die in de terminal is geleverd om toegang te krijgen tot de web -app en eBooks te converteren. ** voor openbare link **:
`python app.py -share` (alle os)
`./ebook2audiobook.sh --- share` (Linux/MacOS)
`eBook2audiobook.cmd --- share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!BELANGRIJK]
** Als het script wordt gestopt en opnieuw wordt uitgevoerd, moet u uw Gradio GUI -interface vernieuwen <br>
Om de webpagina opnieuw te laten verbinding maken met de nieuwe verbindingsaansluiting. **
                        (Optional) Fine tuned model path. Default is builtin model.
Basisgebruik
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-Ebook] **: pad naar uw e-boekbestand. ** [-Voice] **: spraakkloneringspad (optioneel). ** [-Language] **: Taalcode in ISO-639-3 (d.w.z. ITA voor Italiaans, eng voor Engels, Deu voor Duits ...). <br>
Standaardtaal is ENG en -Language is optioneel voor standaardtaal ingesteld in ./lib/lang.py. <br>
De ISO-639-1 2-letterscodes worden ook ondersteund. Voorbeeld van aangepaste model ZIP -upload
  --repetition_penalty REPETITION_PENALTY
(Moet een .zip -bestand zijn met de verplichte modelbestanden. Voorbeeld voor XTTS: config.json, model.pth, vocab.json en ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custom_model_path> **: pad naar `model_name.zip` bestand,
    die alle verplichte bestanden moet bevatten (volgens de TTS -engine) <br>
    (Zie ./lib/models.py). Voor gedetailleerde gids met een lijst met alle te gebruiken parameters
  --output_dir OUTPUT_DIR
** Linux/macOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** of voor alle os **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "help-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Opmerking: klik in de Gradio/GUI -modus om een ​​lopende conversie te annuleren, gewoon op de [X] van de Ebook Upload -component. Docker gebruiken
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
U kunt ook Docker gebruiken om het e -boek uit te voeren naar Audiobook Converter. Deze methode zorgt voor consistentie in verschillende omgevingen en vereenvoudigt de installatie. De Docker -container uitvoeren

Gebruik de volgende opdracht om de Docker -container uit te voeren en de Gradio -interface te starten:

### Using Docker
-Run alleen met CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Het bouwen van de Docker -container

U kunt de Docker -afbeelding bouwen met de opdracht:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Deze opdracht start de Gradio -interface op poort 7860. (LocalHost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Voeg voor meer opties de parameter `--help` toe
```


Alle eBook2audiobooks hebben de basisdicht van `/home/user/app/`
Bijvoorbeeld:
`tmp` =`/home/user/app/tmp`
`audiobooks` =`/home/user/app/audiobooks`
```
Docker Headless Guide
- For more options add the parameter `--help`


## Docker container file locations
Voordat u dit uitvoert, moet u een DIR maken met de naam "Input-Folder" in uw huidige directie
die wordt gekoppeld, hier kunt u uw invoerbestanden voor de Docker -afbeelding plaatsen om te zien
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
En dat zou het moeten zijn! De output -audioboeken zijn te vinden in de map Audiobook die ook zal worden gevonden
In uw plaatselijke directie U heeft dit Docker -opdracht uitgevoerd
docker pull athomasson2/ebook2audiobook
Om de Help -opdracht te krijgen voor de andere parameters die dit programma heeft, kunt u dit uitvoeren
- Before you do run this you need to create a dir named "input-folder" in your current dir
En dat zal dit uitvoeren 
[Help-opdrachtuitvoer] (#Help-command-output)
mkdir input-folder && mkdir Audiobooks
Docker componeren
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Dit project maakt gebruik van Docker Compose om lokaal te worden uitgevoerd. U kunt GPU -ondersteuning inschakelen of uitschakelen 
Door ofwel `*gpu-enabled` of`*gpu-disabled` in `docker-compose.yml` in te stellen
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Stappen om uit te voeren
    athomasson2/ebook2audiobook \
** Kloon de repository ** (als u dat nog niet hebt gedaan):
```
- And that should be it! 
** Stel GPU -ondersteuning in (standaard uitgeschakeld) **
Om GPU-ondersteuning in te schakelen, wijzigt u `docker-compose.yml` en verandert u`*gpu-disabled` in `*gpu-enabled`


** Start de service: **

```bash
** Toegang tot de service: **

```
! [Demo_web_gui] (Assets/demo_web_gui.gif)
[Help command output](#help-command-output)


Heb je niet de hardware om het uit te voeren of wil je een GPU huren? U kunt de Hugginface -ruimte dupliceren en een GPU huren voor ongeveer $ 0,40 per uur
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Huggingface Space Demo] (#Huggingface-Space-Demo)


[Gratis Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Veel voorkomende docker -problemen
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker komt vast te zitten en het downloaden van verfijnde modellen. (Dit gebeurt niet voor elke computer, maar sommigen lijken dit probleem tegen te komen)
Het uitschakelen van de voortgangsbalk lijkt het probleem op te lossen,
Zoals besproken [hier in #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Voorbeeld van het toevoegen van deze fix in de opdracht `docker run`
3. **Start the service:**
Fijn afgestemde TTS -modellen
    docker-compose up -d
U kunt uw eigen XTTS-model gemakkelijk aanpassen met deze repo
[XTTS-FINETUNE-WEBUI] (https://github.com/daswer123/alts-finetune-webui)
  The service will be available at http://localhost:7860.


[xtts-Finetune-Webui-Space] (https://huggingface.co/spaces/drewthomasson/alts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Een ruimte die u kunt gebruiken om de trainingsgegevens ook gemakkelijk uit te roven
[denoise-huggingface-space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Fijn afgestemde TTS -collectie
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Om onze verzameling reeds verfijnde TTS-modellen te vinden,


## Renting a GPU
Demos
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Regenachtige dagstem **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough Voice **


Ondersteunde e -boekformaten
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Beste resultaten **: `.epub` of` .mobi` voor automatische hoofdstukdetectie
    -p 7860:7860 athomasson2/ebook2audiobook
Uitvoer


! [Voorbeeld] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Veel voorkomende problemen:

CPU is traag (beter op Server SMP CPU), terwijl NVIDIA GPU bijna realtime conversie kan hebben. [Discussie hierover] (https://github.com/drewthomasson/ebook2audiobook/Discussions/19#discussComment-10879846)
Voor snellere meertalige generatie zou ik mijn andere voorstellen

(Het heeft echter geen nul-shot stem klonen en is Siri-kwaliteitsstemmen, maar het is veel sneller op CPU). "Ik heb afhankelijkheidsproblemen" - gebruik gewoon de Docker, het is volledig op zichzelf staand en heeft een modus zonder headly,
 Voeg de parameter `--help` toe aan het einde van de opdracht Docker Run voor meer informatie. "Ik krijg een afgekapt audioprobleem!" - Maak hier een probleem van,

### Fine Tuned TTS Collection
Waar ik hulp bij nodig heb! 🙌
[Volledige lijst met dingen is hier te vinden] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potentieel het creëren van README -gidsen voor meerdere talen (omdat de enige taal die ik ken is Engels 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui TTS **: [Coqui TTS GitHub] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [ffmpeg website] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/V1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
U kunt de code [hier] (Legacy/V1.0) bekijken. Word lid van onze server! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg.gg/63tv3f65k6)