📚 EBOEK2AUDIOBOOK
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
CPU/GPU pretvarač iz e -knjiga u audioknjige s poglavljima i metapodacima <br/>
Korištenje kalibra, ffmpeg, xttsv2, FairSeq i još mnogo toga. Podržava kloniranje glasa i +1110 jezika! [!VAŽNO]
** Ovaj je alat namijenjen upotrebi s ne-DRM-om, samo zakonski stečenim e-knjigama. ** <br>
Autori nisu odgovorni za zlouporabu ovog softvera ili bilo kakve pravne posljedice. <br>
Koristite ovaj alat odgovorno i u skladu sa svim primjenjivim zakonima. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko-fi-f16061?style=for-tfor-badge&logo=ko-fi&logocolor=white)] .com/athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_web_Gui] (imovina/demo_Web_GUI.GIF)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العربية (arapski)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
ZHO [中文 (kineski)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
SWE [Svenska (Švedska)] (./ ReadMe/ReadMe_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
FAS [فارسی (perzijski)] (./ readme/readme_fa.md)


## Table of Contents
[EBOEK2AUDIOBOOK] (#-EBOEK2AUDIOBOOK)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Značajke] (#značajke)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker GUI sučelje] (#docker-gui-sučelje)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Demo za Huggingface Space] (#Huggingface-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Besplatno Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Unaprijed napravljeni audio demonstracije] (#demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Podržani jezici] (#podržani jezici)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Zahtjevi] (#Hardver-Requirements)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Upute za instalaciju] (#instalacije-instrukcije)
- [Output](#output)
- [Common Issues](#common-issues)
[Upotreba] (#lansiranje-gradio-web-sučelje)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Pokretanje Gradijskog web sučelja] (#Pokretanje-Gradio-Web-sučelje)


[Osnovna upotreba bez glave] (#osnovna-korisnost)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Upotreba prilagođenog XTTS modela] (#Primjer-of-Custom-Model-Zip-upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Iznajmljivanje GPU-a] (#iznajmljivanje-A-GPU)


[Naredba za pomoć] (#HELP-COMMAND-I-Output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Fine podešeni TTS modeli] (#fino podešeni-tts-modeli)


[Za prikupljanje fino podešenih TTS modela] (#fino podešeno-tts-collection)
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
[Docker vodič bez glave] (#Docker-Headless-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Lokacije datoteka docker spremnika] (#Docker-Container-File-Locacije)
- **Portuguese (por)**
- **Russian (rus)**
[Uobičajena izdanja Docker-a] (#Common-Docker-tetivi)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Podržani formati e-knjige] (#podržani-ebook-formati)


[Izlaz] (#izlaz)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Uobičajena pitanja] (#uobičajena pitanja)


[Posebna zahvala] (#Posebna hvala)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-v10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Značajke
```bash
📖 Pretvara e -knjige u tekstni format s kalibrom. 📚 dijeli e -knjigu u poglavlja za organizirani zvuk. 🎙️ Visokokvalitetni tekst-to-spor s [Coqui XTTSV2] (https://huggingface.co/coqui/xtts-v2) i [Fairseq] (https://github.com/facebookresearch/fairseq/tree/Main/main/main/ Primjeri/MMS) (i više). 🗣️ Neobavezno kloniranje glasa s vlastitom glasovnom datotekom. 🌍 podržava +1110 jezika (engleski jezik prema zadanim postavkama). [Popis podržanih jezika] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥️ dizajniran za pokretanje na 4 GB RAM -a. [Demo zagrljaj prostora] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [[Zagrljaj lice] (https://img.shields.io/badge/hugging%20face-spaces-yellow?style=for-tfor-badge&logo=huggingface)] (https://huggingface.co/spaces/drewthomasson /eBook2AudioBook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Prostor za Huggingface radi na besplatnom nivou CPU -a, pa očekujte vrlo sporo ili vremensko vrijeme hahaha, samo ne dajte mu divovske datoteke su sve
   - **Windows**
     ```bash
Najbolje duplicirati prostor ili trčati lokalno. Besplatno Google Colab
     ```
[! [Besplatno Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)] (https://colab.research.google.com/github/drewthomasson/ebook2audiobook/blob/blob/blob/blob/blob/blob/blob/blob/blob Main/Notebooks/colab_ebook2audioBook.ipynb)
3. **For Public Link**:
Podržani jezici
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** arapski (ara) **

> [!IMPORTANT]
** Kinezi (ZHO) **
to let the web page reconnect to the new connection socket.**

** Češki (CES) **
   - **Linux/MacOS**:
     ```bash
** Hrvatska (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Nizozemci (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** engleski (eng) **
     ```
     
** francuski (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** njemački (deu) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Mađarski (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** talijanski (ita) **
     ```
   - **Windows**
** japanski (jpn) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Korejski (Kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** poljski (pol) **


** portugalski (por) **
   - **Linux/MacOS**
     ```bash
** Ruski (rus) **
     ```
   - **Windows**
** španjolski (spa) **
     .\ebook2audiobook.cmd --help
     ```
** turski (tur) **
    ```python
     app.py --help
** Vijetnamci (vie) **

<a id="help-command-output"></a>
[** +1100 Jezici putem FairSeq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Uvjeti hardvera
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4GB RAM minimum, preporučeno 8 GB
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualizacija omogućena ako se radi na Windows (samo docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (preporučeno), MPS (još nije optimiziran i može biti sporiji od CPU -a) kompatibilan

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Prije nego što se pažljivo objavi instalacijski ili pogrešan problem potražite na kartici otvorenih i zatvorenih problema <br>
Da biste bili sigurni da vaš problem već ne postoji. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Nedostaje bilo kakve strukture standarda poput onoga što je poglavlje, odlomak, predgovor itd. <br>
Prvo biste trebali ručno ukloniti bilo koji tekst koji ne želite da vas pretvore u zvuk. **

Upute za instalaciju

** klon repo **
  --headless            Run the script in headless mode
Pokretanje gradičnog web sučelja
  --ebooks_dir EBOOKS_DIR
** Pokrenite eBook2AudioBook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Otvorite web aplikaciju **: Kliknite URL navedeni na terminalu za pristup web aplikaciji i pretvoriti e -knjige. ** Za javnu vezu **:
`python app.py --share` (sav OS)
`./ebook2AudioBook.sh --share` (Linux/MacOS)
`eBook2AudioBook.cmd --share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!VAŽNO]
** Ako je skripta zaustavljena i pokrenuta, morate osvježiti svoje sučelje GUI GUI <br>
da se web stranica ponovno poveže s novom utičnicom za vezu. **
                        (Optional) Fine tuned model path. Default is builtin model.
Osnovna upotreba
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-Ebook] **: Put do vaše e-knjige. ** [-glas] **: Put datoteke za kloniranje glasa (neobavezno). ** [-Jezik] **: Jezični kod u ISO-639-3 (tj.: ITA za talijanski, eng za engleski, deu za njemački ...). <br>
Zadani jezik je eng i -jezik nije obavezan za zadani jezik postavljen u ./lib/lang.py. <br>
Podržani su i kodovi slova ISO-639-1 2. Primjer prilagođenog prijenosa Zip modela
  --repetition_penalty REPETITION_PENALTY
(Mora biti .zip datoteka koja sadrži obvezne datoteke modela. Primjer za XTTS: config.json, model.pth, vokab.json i ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <Custom_Model_Path> **: Put do `model_name.zip` datoteku,
    koje moraju sadržavati (prema TTS motoru) sve obvezne datoteke <br>
    (Vidi ./lib/models.py). Za detaljan vodič s popisom svih parametara koje treba koristiti
  --output_dir OUTPUT_DIR
** Linux/macOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** ili za sve OS **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "Pomoć-zapovjednici"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
NAPOMENA: U načinu Grade/GUI, za otkazivanje konverzije u pokretanju, samo kliknite na [X] iz komponente za prijenos e -knjige. Korištenje Dockera
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Docker možete koristiti i za pokretanje e -knjige do pretvarača AudioBook -a. Ova metoda osigurava dosljednost u različitim okruženjima i pojednostavljuje postavljanje. Trčanje spremnika Docker

Da biste pokrenuli spremnik Docker i pokrenuli sučelje Grada, koristite sljedeću naredbu:

### Using Docker
-Run samo s CPU -om
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Izgradnja spremnika Docker

Docker sliku možete izgraditi s naredbom:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Ova naredba pokrenut će gradivo sučelje na portu 7860. (localhost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Za više opcija dodajte parametar `-Help`
```


Sve eBook2AudioBooks imat će osnovni dio `/home/user/app/`
Na primjer:
`tmp` =`/home/user/app/tmp`
`Audiobooks` =`/home/korisnik/App/AudioBooks`
```
Docker vodič bez glave
- For more options add the parameter `--help`


## Docker container file locations
Prije nego što to pokrenete, morate stvoriti dir nazvan "Ulazni uređaj" u svom trenutnom dir
koji će biti povezani, ovdje možete staviti svoje ulazne datoteke za docker sliku da biste vidjeli
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
I to bi trebalo biti! Izlazne audioknjige naći će se u mapi za audioknjige koja će se također nalaziti
U svom lokalnom diru pokrenuli ste ovu docker naredbu u
docker pull athomasson2/ebook2audiobook
Da biste dobili naredbu za pomoć za ostale parametre, ovaj program možete pokrenuti ovo
- Before you do run this you need to create a dir named "input-folder" in your current dir
I to će ovo iznijeti 
[Naredba za pomoć] (#HELP-COMMAND-I-Output)
mkdir input-folder && mkdir Audiobooks
Docker Compose
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Ovaj projekt koristi Docker Compose za lokalno pokretanje. Možete omogućiti ili onemogućiti podršku GPU -a 
Postavljanjem ili `*GPU-omogućenog` `*GPU-Desabled` u` docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Koraci za trčanje
    athomasson2/ebook2audiobook \
** Klonirajte spremište ** (ako već niste):
```
- And that should be it! 
** Postavite GPU podršku (onemogućeno prema zadanim postavkama) **
Da biste omogućili podršku GPU-a, modificirajte `docker-compose.yml` i promijenite`*GPU-Desabled` u `*GPU-omogućeno`


** Pokrenite uslugu: **

```bash
** Pristup usluzi: **

```
! [Demo_web_Gui] (imovina/demo_Web_GUI.GIF)
[Help command output](#help-command-output)


Nemate hardver za pokretanje ili želite unajmiti GPU? Možete duplicirati prostor za Hugginface i unajmiti GPU za oko 0,40 USD na sat
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Demo za Huggingface Space] (#Huggingface-Space-Demo)


[Besplatno Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Uobičajena izdanja Docker
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker dobiva zaglavljeno preuzimanje fino podešenih modela. (To se ne događa za svako računalo, ali čini se da neki nailaze na ovo pitanje)
Čini se da će traka napretka riješiti problem,
Kao što je rečeno [ovdje u #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Primjer dodavanja ovog popravka u naredbi `Docker Run`
3. **Start the service:**
Fino podešeni TTS modeli
    docker-compose up -d
Možete precizno prilagoditi vlastiti XTTS model s ovim repo-om
[XTTS-FINETUNE-WEBUI] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-FINETUNE-WEBUI-SPACE] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webu-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Prostor koji možete koristiti za lako uklanjanje unosa podataka o treningu
[Denoise-Huggingface Space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Fino podešena TTS kolekcija
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Da bismo pronašli našu kolekciju već fino podešenih TTS modela,


## Renting a GPU
Demonstracija
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** kišni dan glas **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough glas **


Podržani formati e -knjige
- Docker gets stuck downloading Fine-Tuned models.
`.EPUB`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Najbolji rezultati **: `.EPUB` ili` .Mobi` za automatsko otkrivanje poglavlja
    -p 7860:7860 athomasson2/ebook2audiobook
Izlaz


! [Primjer] (https://github.com/drewthomasson/voxnovel/blob/dc5197ff97252fa44c391dc0596902d71278a88/readme_files/example.jpeg)
You can fine-tune your own xtts model easily with this repo
Uobičajena pitanja:

CPU je spor (bolji na poslužitelju SMP CPU), dok NVIDIA GPU može imati gotovo pretvorbu u stvarnom vremenu. [Rasprava o tome] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
Za bržu višejezičnu generaciju predložio bih svoje drugo

(Ipak, nema bez ikakvih glasova glasova, a je li Siri kvalitetan glasovi, ali na CPU-u je mnogo brži). "Imam problema s ovisnošću" - samo upotrijebite Docker, potpuno se samostalno i ima način bez glave,
 Dodajte parametar `-Help` na kraju naredbe Docker Run za više informacija. "Dobivam skraćeni audio problem!" - molim vas, napravite ovo pitanje,

### Fine Tuned TTS Collection
O čemu trebam pomoć! 🙌
[Potpuni popis stvari možete pronaći ovdje] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potencijalno stvaranje ReadMe vodiča za više jezika (jer je jedini jezik za koji znam da je engleski 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** coqui tts **: [coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** FFMPEG **: [FFMPEG Web stranica] (https://ffmppeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Možete pogledati kôd [ovdje] (Legacy/v1.0). Pridružite se našem poslužitelju! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)