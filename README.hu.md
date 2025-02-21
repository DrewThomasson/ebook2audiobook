# 📚 eBook2audiokönyv

CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>Caliber, FFMPEG, XTTSV2, FairSeQ és még sok más felhasználásával. Támogatja a hangklónozást és a +1110 nyelveket!

> [!FONTOS]**Ezt az eszközt nem DRM, jogilag megvásárolt e-könyvekkel való használatra szánták.**<br>A szerzők nem felelősek a szoftverrel való visszaélés vagy az ebből eredő jogi következményekért.<br>Használja ezt az eszközt felelősségteljesen és az összes alkalmazandó törvénynek megfelelően.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Köszönet az eBook2audiobook fejlesztők támogatásának!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI felület

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Vásárolunk[Arab (arab)](./readme/README_AR.md)
-   Zho[kínai](./readme/README_CN.md)
-   a \`a[angol](README.md)
-   swe[Svéd (svéd)](./readme/README_SWE.md)
-   FAS[Perzsa (perzsa)](./readme/README_FA.md)
-   ő[Olasz (olasz)](./readme/README.it.md)

## Tartalomjegyzék

-   [eBook2audiobook](#-ebook2audiobook)
-   [Jellemzők](#features)
-   [Docker GUI felület](#docker-gui-interface)
-   [Ölelésface űr demonstráció](#huggingface-space-demo)
-   [Ingyenes Google Colab](#free-google-colab)
-   [Előre elkészített audio-demók](#demos)
-   [Támogatott nyelvek](#supported-languages)
-   [Requirements](#hardware-requirements)
-   [Telepítési utasítások](#installation-instructions)
-   [Használat](#launching-gradio-web-interface)
    -   [A Gradio webes felület elindítása](#launching-gradio-web-interface)
    -   [Alapvető fej nélküli használat](#basic--usage)
    -   [Headless Custom XTTS modellfelhasználás](#example-of-custom-model-zip-upload)
    -   [GPU bérelése](#renting-a-gpu)
    -   [Súgó parancs kimenet](#help-command-output)
-   [Finomhangos TTS modellek](#fine-tuned-tts-models)
    -   [A finomhangolt TTS modellek gyűjtésére](#fine-tuned-tts-collection)
-   [Docker használatával](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [Docker fej nélküli útmutató](#docker-headless-guide)
    -   [Docker Container fájl helyek](#docker-container-file-locations)
    -   [Közös Docker -kérdések](#common-docker-issues)
-   [Támogatott e -könyv formátumok](#supported-ebook-formats)
-   [Kibocsátás](#output)
-   [Általános kérdések](#common-issues)
-   [Külön köszönet](#special-thanks)
-   [Csatlakozzon szerverünkhöz!](#join-our--server)
-   [Örökség](#legacy-v10)
-   [Tartalomjegyzék](#table-of-contents)

## Jellemzők

-   📖 konvertálja az e -könyveket szöveges formátumra kaliberrel.
-   📚 Az e -könyvet a szervezett audio fejezetekre osztja.
-   🎙️ Kiváló minőségű szöveg-beszéd[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)és[FairSeq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(és még sok más).
-   🗣️ Opcionális hangklónozás a saját hangfájljával.
-   🌍 támogatja a +1110 nyelveket (alapértelmezés szerint angol).[A támogatott nyelvek listája](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ A 4 GB -os RAM -on történő futtatásra tervezték.

## [Ölelésface űr demonstráció](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   A Hugingface Space ingyenes CPU -szinten fut, tehát várjon nagyon lassú vagy időtúllépést, csak ne adjon neki óriási fájlokat
-   A legjobb, ha a helyet másolják, vagy helyben futtassák.

## Ingyenes Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Támogatott nyelvek

-   **Arab (ARA)**
-   **Kínai (ZH)**
-   **Cseh (CES)**
-   **Horvát (HRV)**
-   **Holland (nld)**
-   **Angol (Eng)**
-   **Francia (**
-   **Német (DEU)**
-   **Nem (hin)**
-   **Hungarian (hun)**
-   **Olasz (ITA)**
-   **Japán (JPN)**
-   **Korean (kor)**
-   **Lengyel (POL)**
-   **Portugál (POR)**
-   **Orosz (or)**
-   **Spanyol (gyógyfürdő)**
-   **Török (kerek)**
-   **Vietnami (vie)**
-   [**+1100 nyelvek a Fairseq -en keresztül**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Hardverkövetelmények

-   4 GB RAM minimum, 8 GB ajánlott
-   A virtualizáció engedélyezve, ha Windows rendszeren fut (csak Docker)
-   CPU, GPU (ajánlott), MPS (még nem optimalizálva és lassabb lehet, mint a CPU) kompatibilis

> [!FONTOS]**A telepítés vagy a hiba kiadásának keresése gondos elküldése előtt a megnyitott és zárt kérdések lapon<br>Annak érdekében, hogy megbizonyosodjon arról, hogy a problémája még nem létezik.**

> [!JEGYZET]**Nincs olyan szabványszerkezet hiánya, mint egy fejezet, bekezdés, előszó stb.<br>Először kézzel kell távolítani minden olyan szöveget, amelyet nem akarja konvertálni audio -ban.**

### Telepítési utasítások

1.  **Klón repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### A Gradio webes felület elindítása

1.  **Futtassa az eBook2audiokookot**:
    -   **Linux/MacOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Ablakok**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Nyissa meg a webalkalmazást**: Kattintson a terminálon található URL -re a webes alkalmazáshoz való hozzáféréshez és az e -könyvek konvertálásához.
3.  **Nyilvános linkre**:`python app.py --share`(All OS)`./ebook2audiobook.sh --share`(Linux/MacOS)`ebook2audiobook.cmd --share`(Windows)

> [!FONTOS]**Ha a szkript leállítja és újra fut, frissítenie kell a Gradio GUI felületét<br>hogy a weboldal újból csatlakozzon az új csatlakozási aljzathoz.**

### Alaphasználat

-   **Linux/MacOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Ablakok**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Ebook]**: Út az e -könyv fájlhoz.
-   **[--hang]**: Hangklónozó fájl elérési útja (opcionális).
-   **[--nyelv]**: Nyelvi kód az ISO-639-3-ban (azaz: ITA az olasz, angol nyelv számára, deu németül ...).<br>Az alapértelmezett nyelv az Eng, és a -nyelv opcionális az alapértelmezett nyelvnél ./lib/lang.py.<br>Az ISO-639-1 2 betűkódok szintén támogatottak.

### Példa az egyéni modell ZIP feltöltésére

(A kötelező modellfájlokat tartalmazó .zip fájlnak kell lennie. Példa az XTT -kre: config.json, modell.pth, cocab.json és ref.wav)

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Ablakok**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**: Út a`model_name.zip`fájl,
        amelynek tartalmaznia kell (a TTS motor szerint) az összes kötelező fájlt<br>(lásd ./lib/models.py).

### A részletes útmutatóért az összes használni kívánt paraméter listájával

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Ablakok**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Vagy az összes operációs rendszerhez**
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

Megjegyzés: Gradio/GUI módban a futó konverzió törléséhez kattintson a[X]az e -könyv feltöltési elemből.

### Docker használatával

A Docker segítségével az e -könyv futtatásához az Audiokönyv -konverterhez is futtathatja. 
Ez a módszer biztosítja a konzisztenciát a különböző környezetekben, és egyszerűsíti a beállítást.

#### A Docker Container futtatása

A Docker Container futtatásához és a Gradio felület elindításához használja a következő parancsot:

\-Az csak CPU -val

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run GPU gyorsulással (csak az NVIDIA kompatibilis)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### A Docker konténer építése

-   Készítheti a Docker -képet a paranccsal:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Ez a parancs elindítja a Gradio felületet a 7860 -as porton. (Localhost: 7860)

-   További lehetőségekért adja hozzá a paramétert`--help`

## Docker Container fájl helyek

Az összes eBook2audiokönyvnek megvan az alapja`/home/user/app/`Például:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker fej nélküli útmutató

Először a legújabb Docker húzáshoz

```bash
docker pull athomasson2/ebook2audiobook
```

-   Mielőtt ezt futtatná, létre kell hoznia egy "bemeneti-molder" nevű DIR-t az aktuális DIR-ben
    Amit összekapcsolnak, itt helyezheti el a Docker -kép bemeneti fájljait

```bash
mkdir input-folder && mkdir Audiobooks
```

-   Az alábbi parancsban cserélje ki**Your_input_file.txt**A bemeneti fájl nevével

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   És ennek kell lennie!
-   A kimeneti hangoskönyvek megtalálhatók az audiokönyv mappájában, amely szintén megtalálható
    A helyi dir -ben beadta ezt a Docker parancsot

## Ahhoz, hogy megkapja a Súgó parancsot a program többi paraméteréhez, ezt futtathatja

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

És ez kimutatja ezt[Súgó parancs kimenet](#help-command-output)

### Docker Compose

Ez a projekt a Docker Compose -t használja a helyi futtatáshoz. Engedélyezheti vagy letilthatja a GPU támogatását 
beállítva`*gpu-enabled`vagy`*gpu-disabled`-ben`docker-compose.yml`

#### A futáshoz szükséges lépések

1.  **Klónozza a tárolóit**(Ha még nem tette meg):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Állítsa be a GPU támogatást (alapértelmezés szerint letiltva)**A GPU támogatás engedélyezéséhez módosítsa`docker-compose.yml`és változás`*gpu-disabled`-hoz`*gpu-enabled`
3.  **Indítsa el a szolgáltatást:**
    ```bash
    docker-compose up -d
    ```
4.  **Hozzáférés a szolgáltatáshoz:**A szolgáltatás a http&#x3A; // localhost: 7860 oldalon lesz elérhető.

### Docker GUI felület

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## GPU bérelése

Nincs a hardver a futtatáshoz, vagy GPU -t szeretne bérelni?

#### Másolhatja a Hugginface helyet, és bérelhet egy GPU -t körülbelül 0,40 dollár óránként

[Ölelésface űr demonstráció](#huggingface-space-demo)

#### Vagy megpróbálhatja ingyenesen használni a Google Colabot!

(Vegye figyelembe, hogy ez egy kicsit, miután nem zavarja a Google Colab -ot)[Ingyenes Google Colab](#free-google-colab)

## Közös Docker -kérdések

-   A Docker elakad a finomhangolt modellek letöltésével.
    (Ez nem történik meg minden számítógépnél, de úgy tűnik, hogy néhányan belefutnak ebbe a kérdésbe)
    Úgy tűnik, hogy a Progress sáv letiltása kijavítja a problémát,
    amint azt tárgyaltuk[Itt a #191 -ben](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Példa erre a javításra a`docker run`parancs

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Finomhangos TTS modellek

Könnyen finomíthatja a saját XTTS modelljét ezzel a repo-val[XTTS-Finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Ha könnyen bérelni szeretne egy GPU -t, akkor ezt az átölelést is megismételheti[XTTS-Finetune-Webui-Space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Egy olyan hely, amelyet felhasználhat az edzési adatok egyszerűségének megkönnyítésére is[denoise-öblítő-tér](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Finom hangolt TTS kollekció

Hogy megtaláljuk a már finoman hangolt TT-modellek gyűjteményét,
látogatás[Ez az átölelő arc link](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Az XTTS egyedi modelljéhez a hanghivatkozás Ref audio klipje kötelező:

## Demók

**Esős ​​napi hang**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Támogatott e -könyv formátumok

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Legjobb eredmény**:`.epub`vagy`.mobi`az automatikus fejezet észleléséhez

## Kibocsátás

-   Létrehoz egy`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Beállítva :/lib/conf.py) fájl metaadatokkal és fejezetekkel.
-   **Példa**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Általános kérdések:

-   A CPU lassú (jobb az SMP CPU -nál), míg az NVIDIA GPU szinte valós idejű konverzióval rendelkezik.[Beszélgetés erről](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)A gyorsabb többnyelvű generációhoz javasolnám a másikomat[A Piper-TTS-t használó projekt](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)helyette
    (Ennek ellenére nincs nulla lövésű klónozás, és a Siri minőségű hangok, de a CPU-nál sokkal gyorsabb).
-   "Függőségi problémáim vannak" - csak használja a Docker -t, annak teljesen önállóan és fej nélküli módja,
     hozzáad`--help`Paraméter a Docker Run parancs végén további információkért.
-   "Kapok egy csonkított audio problémát!" - Kérjük, tegye fel ezt a kérdést,
     Nem beszélünk minden nyelvet, és tanácsot kell adnunk a felhasználóktól, hogy finomítsák a mondat felosztási logikáját.😊

## Mire szükségem van segítségre! 🙌

## [A dolgok teljes listája itt található](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   A támogatott nyelvek bármelyikét beszélő emberek bármilyen segítsége a megfelelő mondatmegosztási módszerek elősegítése érdekében
-   Potenciálisan létrehozni a Readme útmutatókat több nyelvre (mert az egyetlen nyelv, amelyet tudok az angol 😔)

## Külön köszönet

-   **Főzési TTS**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Kaliber**:[Kaliberű weboldal](https://calibre-ebook.com)
-   **Ffmpeg**:[FFMPEG weboldal](https://ffmpeg.org)
-   [@Shakenbake15 a jobb fejezetmegtakarítási módszerhez](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Megtekintheti a kódot[itt](legacy/v1.0).

## Csatlakozzon szerverünkhöz!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
