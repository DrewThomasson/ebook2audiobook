📚 eBook2audiokönyv
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
CPU/GPU konverter az e -könyvekről audiokönyvekbe fejezetekkel és metaadatokkal <br/>
Caliber, FFMPEG, XTTSV2, FairSeQ és még sok más felhasználásával. Támogatja a hangklónozást és a +1110 nyelveket! [!FONTOS]
** Ezt az eszközt nem DRM, jogilag megszerzett e-könyvekkel való használatra szánják. ** <br>
A szerzők nem felelősek a szoftverrel való visszaélés vagy az ebből eredő jogi következményekért. <br>
Használja ezt az eszközt felelősségteljesen és az összes alkalmazandó törvénynek megfelelően. [!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! .com/Athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


!
![demo_web_gui](assets/demo_web_gui.gif)

<details>
Ara [العرب (arab)] (./ README/README_AR.MD)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文 (kínai)] (./ README/README_CN.MD)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
Swe [svenska (svéd)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فاری (perzsa)] (./ Readme/readme_fa.md)


## Table of Contents
[eBook2audiobook] (#-Ebook2audiOBook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Jellemzők] (#Jellemzők)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker GUI interfész] (#docker-gui-interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Hugingface Space Demo] (#Huggingface-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Ingyenes Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Előre elkészített audio demók] (#demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Támogatott nyelvek] (#támogatott nyelvek)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Követelmények] (#hardver-igények)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Telepítési utasítások] (#Telepítés-beavatkozások)
- [Output](#output)
- [Common Issues](#common-issues)
[Használat] (#elindítás-gradio-web-interfész)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[A Gradio webes interfész indítása] (#indítás-gradio-web-interfész)


[Alapvető fej nélküli használat] (#alap- felhasználás)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Headless Custom XTTS modellfelhasználás] (#Az óvodai-modell-zip-Upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[GPU bérlése] (#Renting-A-GPU)


[Súgóparancs kimenet] (#súgó-command-output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Finomhangos TTS modellek] (#Finomhangos-TTS-modellek)


[A finomhangolt TTS modellek gyűjtéséhez] (#Finomhangos-TTS-gyűjtés)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#futó-the-docker-tartály)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Docker-Container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#Docker-Compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide] (#Docker fej nélküli út)
- **Japanese (jpn)**
- **Korean (kor)**
[Docker Container File helyek] (#Docker-Container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Közös Docker-kérdések] (#Common-Docker-kiadások)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Támogatott e-könyv formátumok] (#támogatott-eBook-formátumok)


[Kimenet] (#kimenet)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Általános kérdések] (#COMLED-MEGÁLLAPÍTÁS)


[Különleges köszönet] (#Különleges köszönet)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Jellemzők
```bash
📖 konvertálja az e -könyveket szöveges formátumra kaliberrel. 📚 Az e -könyvet a szervezett audio fejezetekre osztja. 🎙️ Kiváló minőségű szöveg-speech a [coqui xttsv2] (https://huggingface.co/coqui/xtts-v2) és a [Fairseq] (https://github.com/facebookresearch/fairseq/tree/main/main/ Példák/MMS) (és még sok más). 🗣️ Opcionális hangklónozás a saját hangfájljával. 🌍 támogatja a +1110 nyelveket (alapértelmezés szerint angol). [A támogatott nyelvek listája] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-Languages.html)
```

🖥️ A 4 GB -os RAM -on történő futtatásra tervezték. [Huggingface Space Demo] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! /eBook2audiokook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
A Hugingface Space ingyenes CPU -szinten fut, tehát várjon nagyon lassú vagy időtúllépést, csak ne adjon neki óriási fájlokat
   - **Windows**
     ```bash
A legjobb, ha a helyet másolják, vagy helyben futtassák. Ingyenes Google Colab
     ```
[! Main/notebooks/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Támogatott nyelvek
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arab (ARA) **

> [!IMPORTANT]
** Kínai (zho) **
to let the web page reconnect to the new connection socket.**

** Cseh (CES) **
   - **Linux/MacOS**:
     ```bash
** Horvát (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Holland (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Angol (Eng) **
     ```
     
** francia (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Német (DEU) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** magyar (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** olasz (ita) **
     ```
   - **Windows**
** Japán (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Koreai (KOR) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Lengyel (POL) **


** Portugál (por) **
   - **Linux/MacOS**
     ```bash
** Orosz (orosz) **
     ```
   - **Windows**
** Spanyol (gyógyfürdő) **
     .\ebook2audiobook.cmd --help
     ```
** Török (TUR) **
    ```python
     app.py --help
** vietnami (vie) **

<a id="help-command-output"></a>
[** +1100 nyelvek a FairSeq-en keresztül **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-Languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Hardverkövetelmények
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4 GB RAM minimum, 8 GB ajánlott
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
A virtualizáció engedélyezve, ha Windows rendszeren fut (csak Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (ajánlott), MPS (még nem optimalizálva és lassabb lehet, mint a CPU) kompatibilis

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** A telepítési vagy hibakibocsátás -keresést gondosan küldje el a megnyitott és zárt problémák fülre <br>
hogy megbizonyosodjunk arról, hogy a problémája még nem létezik. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Nincs olyan szabványszerkezet hiánya, mint egy fejezet, bekezdés, előszó stb. <br>
Először kézzel kell távolítani minden olyan szöveget, amelyet nem akarja konvertálni a hangban. **

Telepítési utasítások

** klón repo **
  --headless            Run the script in headless mode
A Gradio webes felület elindítása
  --ebooks_dir EBOOKS_DIR
** Futtassa az eBook2audiokookot **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macos **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Nyissa meg a webalkalmazást **: Kattintson a terminálon található URL -re a webalkalmazáshoz való hozzáféréshez és az e -könyvek konvertálásához. ** A nyilvános linkhez **:
`python app.py - -chare` (All OS)
`.
`eBook2audiobook.cmd --szare (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!FONTOS]
** Ha a szkript le van állítva, és újra futtatja, akkor frissítenie kell a Gradio GUI felületét <br>
hogy a weboldal újból csatlakozzon az új csatlakozási aljzathoz. **
                        (Optional) Fine tuned model path. Default is builtin model.
Alaphasználat
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-eBook] **: elérési út az e-könyv fájlhoz. ** [-hang] **: Hangklónozó fájl elérési útja (opcionális). ** [-Nyelv] **: Nyelvi kód az ISO-639-3-ban (azaz: ITA olaszul, angolul, deu németül ...). <br>
Az alapértelmezett nyelv az Eng, és a -nyelv opcionális az alapértelmezett nyelv számára ./lib/lang.py. <br>
Az ISO-639-1 2 betűkódok szintén támogatottak. Példa az egyéni modell ZIP feltöltésére
  --repetition_penalty REPETITION_PENALTY
(A kötelező modellfájlokat tartalmazó .zip fájlnak kell lennie. Példa az XTT -kre: config.json, modell.pth, cocab.json és ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macos **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custom_model_path> **: elérési út a `modell_name.zip` fájlhoz,
    amelynek tartalmaznia kell (a TTS motor szerint) az összes kötelező fájlt <br>
    (lásd ./lib/models.py). A részletes útmutatóért az összes használni kívánt paraméter listájával
  --output_dir OUTPUT_DIR
** Linux/macos **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** vagy az összes OS esetében **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "súgó-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Megjegyzés: Gradio/GUI módban a futó konverzió törléséhez kattintson az [x] -re az e -könyv feltöltési elemre. Docker használatával
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
A Docker segítségével az e -könyv futtatásához az Audiokönyv -konverterhez is futtathatja. Ez a módszer biztosítja a konzisztenciát a különböző környezetekben, és egyszerűsíti a beállítást. A Docker Container futtatása

A Docker Container futtatásához és a Gradio felület elindításához használja a következő parancsot:

### Using Docker
-Az csak CPU -val
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
A Docker konténer építése

Készítheti a Docker -képet a paranccsal:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Ez a parancs elindítja a Gradio felületet a 7860 -as porton. (Localhost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
További lehetőségekért adja hozzá a `--help 'paramétert
```


Az összes eBook2audiokönyvnek megvan a „/home/user/app/” alapja.
Például:
`tmp` =`/home/user/app/tmp`
`Audiokönyvek`/Home/User/APP/Audiokönyvek "
```
Docker fej nélküli útmutató
- For more options add the parameter `--help`


## Docker container file locations
Mielőtt ezt futtatná, létre kell hoznia egy "bemeneti-molder" nevű DIR-t az aktuális DIR-ben
Amit összekapcsolnak, itt helyezheti el a Docker -kép bemeneti fájljait
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
És ennek kell lennie! A kimeneti hangoskönyvek megtalálhatók az audiokönyv mappájában, amely szintén megtalálható
A helyi dir -ben beadta ezt a Docker parancsot
docker pull athomasson2/ebook2audiobook
Ahhoz, hogy megkapja a Súgó parancsot a program többi paraméteréhez, ezt futtathatja
- Before you do run this you need to create a dir named "input-folder" in your current dir
És ez kimutatja ezt 
[Súgóparancs kimenet] (#súgó-command-output)
mkdir input-folder && mkdir Audiobooks
Docker Compose
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Ez a projekt a Docker Compose -t használja a helyi futtatáshoz. Engedélyezheti vagy letilthatja a GPU támogatását 
A `*gpu-kompatibilis" vagy a „*gpu-fogyatékos” beállításával a `docker-compose.yml`-ben beállítva
    -v $(pwd)/input-folder:/home/user/app/input_folder \
A futáshoz szükséges lépések
    athomasson2/ebook2audiobook \
** klónozza a lerakatot ** (ha még nem tette meg):
```
- And that should be it! 
** Állítsa be a GPU támogatást (alapértelmezés szerint letiltva) **
A GPU támogatás engedélyezéséhez módosítsa a „docker-compose.yml” -et, és változtassa meg a „*gpu-fogyatékos” -t `*GPU-engedélyezőként”


** Indítsa el a szolgáltatást: **

```bash
** Hozzáférés a szolgáltatáshoz: **

```
!
[Help command output](#help-command-output)


Nincs a hardver a futtatáshoz, vagy GPU -t szeretne bérelni? Másolhatja a Hugginface helyet, és bérelhet egy GPU -t körülbelül 0,40 dollár óránként
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Hugingface Space Demo] (#Huggingface-Space-Demo)


[Ingyenes Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Közös Docker -kérdések
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
A Docker elakad a finomhangolt modellek letöltésével. (Ez nem történik meg minden számítógépnél, de úgy tűnik, hogy néhányan belefutnak ebbe a kérdésbe)
Úgy tűnik, hogy a Progress sáv letiltása kijavítja a problémát,
amint azt a [itt a #191 -ben] tárgyaltuk (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Példa erre a javításra a `Docker Run` parancshoz
3. **Start the service:**
Finomhangos TTS modellek
    docker-compose up -d
Könnyen finomíthatja a saját XTTS modelljét ezzel a repo-val
[XTTS-finetune-webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-finetune-webui-space] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Egy olyan hely, amelyet felhasználhat az edzési adatok egyszerűségének megkönnyítésére is
[Denoise-huggingface-space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Finom hangolt TTS kollekció
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Hogy megtaláljuk a már finoman hangolt TT-modellek gyűjteményét,


## Renting a GPU
Demók
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Esős nap hangja **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough hang **


Támogatott e -könyv formátumok
- Docker gets stuck downloading Fine-Tuned models.
`.Epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.Chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** A legjobb eredmények **: `.Epub` vagy` .mobi` az automatikus fejezet észleléséhez
    -p 7860:7860 athomasson2/ebook2audiobook
Kibocsátás


!
You can fine-tune your own xtts model easily with this repo
Általános kérdések:

A CPU lassú (jobb az SMP CPU -nál), míg az NVIDIA GPU szinte valós idejű konverzióval rendelkezik. [Beszélgetés erről] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
A gyorsabb többnyelvű generációhoz javasolnám a másikomat

(Ennek ellenére nincs nulla lövésű klónozás, és a Siri minőségű hangok, de a CPU-nál sokkal gyorsabb). "Függőségi problémáim vannak" - csak használja a Docker -t, annak teljesen önállóan és fej nélküli módja,
 Adja hozzá a `--help` paramétert a Docker Run parancs végén további információkért. "Kapok egy csonkított audio problémát!" - Kérjük, tegye fel ezt a kérdést,

### Fine Tuned TTS Collection
Mire szükségem van segítségre! 🙌
[A dolgok teljes listája itt található] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potenciálisan létrehozni a Readme útmutatókat több nyelvre (mivel az egyetlen nyelv, amelyet tudok, az angol 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui tts **: [Coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** FFMPEG **: [FFMPEG weboldal] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Megtekintheti a [itt] kódot (Legacy/v1.0). Csatlakozzon szerverünkhöz! [!