# 📚 EBOEK2AUDIOBOOK

CPU/GPU pretvarač iz e -knjiga u audioknjige s poglavljima i metapodacima<br/>Korištenje kalibra, ffmpeg, xttsv2, FairSeq i još mnogo toga. Podržava kloniranje glasa i +1110 jezika!

> [!VAŽNO]**Ovaj je alat namijenjen upotrebi s ne-DRM-om, pravno stečenim e-knjigama.**<br>Autori nisu odgovorni za zlouporabu ovog softvera ili bilo kakve pravne posljedice.<br>Koristite ovaj alat odgovorno i u skladu sa svim primjenjivim zakonima.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Zahvaljujući podršci ebook2AudioBook programerima!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI sučelje

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Kupujemo[Arapski (arapski)](./readme/README_AR.md)
-   ZHO[kineski](./readme/README_CN.md)
-   a \`a[engleski](README.md)
-   sne[Švedski (švedski)](./readme/README_SWE.md)
-   fasa[Perzijski (perzijski)](./readme/README_FA.md)
-   ona[Talijanski (talijanski)](./readme/README.it.md)

## Sadržaj

-   [eBook2AudioBook](#-ebook2audiobook)
-   [Značajke](#features)
-   [Docker GUI sučelje](#docker-gui-interface)
-   [Demo zagrljaj prostora](#huggingface-space-demo)
-   [Besplatno Google Colab](#free-google-colab)
-   [Unaprijed napravljeni audio demonstracije](#demos)
-   [Podržani jezici](#supported-languages)
-   [Zahtjevi](#hardware-requirements)
-   [Upute za instalaciju](#installation-instructions)
-   [Uporaba](#launching-gradio-web-interface)
    -   [Launching Gradio Web Interface](#launching-gradio-web-interface)
    -   [Osnovna upotreba bez glave](#basic--usage)
    -   [Upotreba prilagođenih XTTS modela bez glave](#example-of-custom-model-zip-upload)
    -   [Iznajmljivanje GPU -a](#renting-a-gpu)
    -   [Naredba za pomoć](#help-command-output)
-   [Fino podešeni TTS modeli](#fine-tuned-tts-models)
    -   [Za prikupljanje fino podešenih TTS modela](#fine-tuned-tts-collection)
-   [Korištenje Dockera](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [Docker vodič bez glave](#docker-headless-guide)
    -   [Docker Lokacije datoteka spremnika](#docker-container-file-locations)
    -   [Uobičajena izdanja Docker](#common-docker-issues)
-   [Podržani formati e -knjige](#supported-ebook-formats)
-   [Izlaz](#output)
-   [Uobičajena pitanja](#common-issues)
-   [Posebna hvala](#special-thanks)
-   [Pridružite se našem poslužitelju!](#join-our--server)
-   [Nasljeđe](#legacy-v10)
-   [Sadržaj](#table-of-contents)

## Značajke

-   📖 Pretvara e -knjige u tekstni format s kalibrom.
-   📚 dijeli e -knjigu u poglavlja za organizirani zvuk.
-   🎙️ visokokvalitetni tekst u govor s[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)i[Sajam](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) (and more).
-   🗣️ Neobavezno kloniranje glasa s vlastitom glasovnom datotekom.
-   🌍 podržava +1110 jezika (engleski jezik prema zadanim postavkama).[Popis podržanih jezika](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ dizajniran za pokretanje na 4 GB RAM -a.

## [Demo zagrljaj prostora](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Prostor za Huggingface radi na besplatnom nivou CPU -a, pa očekujte vrlo sporo ili vremensko vrijeme hahaha, samo ne dajte mu divovske datoteke su sve
-   Najbolje duplicirati prostor ili trčati lokalno.

## Besplatno Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Podržani jezici

-   **Arapski (ara)**
-   **Kinezi (ZH)**
-   **Češki (CES)**
-   **Hrvat (HRV)**
-   **Nizozemski (NLD)**
-   **Engleski (eng)**
-   **Francuski (od)**
-   **Njemački (DEU)**
-   **Ne (HIN)**
-   **Mađarski (AM)**
-   **Talijanski (ITA)**
-   **Japanski (JPN)**
-   **Korejski (COR)**
-   **Poljski (pol)**
-   **Portugalski (por)**
-   **Ruski (rus)**
-   **Španjolski (spa)**
-   **Turski (okrugli)**
-   **Vijetnamci (vie)**
-   [**+1100 jezika putem FairSeq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Uvjeti hardvera

-   4GB RAM minimum, preporučeno 8 GB
-   Virtualizacija omogućena ako se radi na Windows (samo docker)
-   CPU, GPU (preporučeno), MPS (još nije optimiziran i može biti sporiji od CPU -a) kompatibilan

> [!VAŽNO]**Prije nego što objavite instalaciju ili problem s pogreškama, pažljivo pretražite na kartici otvorenih i zatvorenih problema<br>Da biste bili sigurni da vaš problem već ne postoji.**

> [!BILJEŠKA]**Nedostaje bilo kakve strukture standarda poput onoga što je poglavlje, odlomak, predgovor itd.<br>
> you should first remove manually any text you don't want to be converted in audio.**

### Upute za instalaciju

1.  **Kloni repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Launching Gradio Web Interface

1.  **Pokrenite ebook2AudioBook**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Prozori**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Otvorite web aplikaciju**: Kliknite URL predviđen na terminalu za pristup web aplikaciji i pretvorbu e -knjiga.
3.  **Za javnu vezu**:`python app.py --share`(Sav OS)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!VAŽNO]**Ako je skripta zaustavljena i ponovno pokrenuta, morate osvježiti GUI sučelje Grad GUI<br>da se web stranica ponovno poveže s novom utičnicom za povezivanje.**

### Osnovna upotreba

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Prozori**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Ebook]**: Put do vaše e -knjige.
-   **[--glas]**: Put datoteke za kloniranje glasa (neobavezno).
-   **[--jezik]**: Jezični kod u ISO-639-3 (tj. ITA za talijanski, eng za engleski, deu za njemački ...).<br>Zadani jezik je eng, a -jezik nije obavezan za zadani jezik postavljen u ./lib/lang.py.<br>Podržani su i kodovi slova ISO-639-1 2.

### Primjer prilagođenog prijenosa Zip modela

(Mora biti .zip datoteka koja sadrži obvezne datoteke modela. Primjer za XTTS: config.json, model.pth, vokab.json i ref.wav)

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Prozori**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;pričasni_model_path>**: Put do`model_name.zip`spis,
        koje moraju sadržavati (prema TTS motoru) sve obvezne datoteke<br>(Vidi ./lib/models.py).

### Za detaljan vodič s popisom svih parametara koje treba koristiti

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Prozori**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Ili za sve OS**
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

NAPOMENA: U načinu Gradion/GUI, za otkazivanje trčane konverzije, samo kliknite na[X]iz komponente prijenosa e -knjige.

### Korištenje Dockera

Docker možete koristiti i za pokretanje e -knjige do pretvarača AudioBook -a. 
Ova metoda osigurava dosljednost u različitim okruženjima i pojednostavljuje postavljanje.

#### Trčanje spremnika Docker

Da biste pokrenuli spremnik Docker i pokrenuli sučelje Grada, koristite sljedeću naredbu:

\-Run samo s CPU -om

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-RUN SA GPU SPEEGUUP (samo NVIDIA kompatibilan)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Izgradnja spremnika Docker

-   Docker sliku možete izgraditi s naredbom:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Ova naredba pokrenut će gradivo sučelje na portu 7860. (localhost: 7860)

-   Za više opcija dodajte parametar`--help`

## Docker Lokacije datoteka spremnika

Sve e -knjige2AudioBooks će imati osnovni dir od`/home/user/app/`Na primjer:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker vodič bez glave

Prvo za docker povlačenje najnovijeg sa

```bash
docker pull athomasson2/ebook2audiobook
```

-   Prije nego što to pokrenete, morate stvoriti dir nazvan "Ulazni uređaj" u svom trenutnom dir
    koji će biti povezani, ovdje možete staviti svoje ulazne datoteke za docker sliku da biste vidjeli

```bash
mkdir input-folder && mkdir Audiobooks
```

-   U naredbi ispod zamjene**Your_input_file.txt**s imenom vaše ulazne datoteke

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   I to bi trebalo biti!
-   Izlazne audioknjige naći će se u mapi za audioknjige koja će se također nalaziti
    U svom lokalnom diru pokrenuli ste ovu docker naredbu u

## Da biste dobili naredbu za pomoć za ostale parametre, ovaj program možete pokrenuti ovo

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

I to će ovo iznijeti[Naredba za pomoć](#help-command-output)

### Docker Compose

Ovaj projekt koristi Docker Compose za lokalno pokretanje. Možete omogućiti ili onemogućiti podršku GPU -a 
Postavljajući bilo koji`*gpu-enabled`ili`*gpu-disabled`u`docker-compose.yml`

#### Koraci za trčanje

1.  **Klonirati spremište**(Ako već niste):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Postavite GPU podršku (onemogućeno je prema zadanim postavkama)**Da biste omogućili podršku GPU -a, izmijenite`docker-compose.yml`i promijeniti`*gpu-disabled`do`*gpu-enabled`
3.  **Pokrenite uslugu:**
    ```bash
    docker-compose up -d
    ```
4.  **Pristupite usluzi:**Usluga će biti dostupna na http&#x3A; // localhost: 7860.

### Docker GUI sučelje

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Iznajmljivanje GPU -a

Nemate hardver za pokretanje ili želite unajmiti GPU?

#### Možete duplicirati prostor za Hugginface i unajmiti GPU za oko 0,40 USD na sat

[Demo zagrljaj prostora](#huggingface-space-demo)

#### Ili možete besplatno pokušati koristiti Google Colab!

(Imajte na umu da će se vremenski izbaciti nakon što se malo ne zabrljate s Google Colabom)[Besplatno Google Colab](#free-google-colab)

## Uobičajena izdanja Docker

-   Docker dobiva zaglavljeno preuzimanje fino podešenih modela.
    (To se ne događa za svako računalo, ali čini se da neki nailaze na ovo pitanje)
    Čini se da će traka napretka riješiti problem,
    Kao što je raspravljano[here in #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Primjer dodavanja ovog popravka u`docker run`naredba

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Fino podešeni TTS modeli

Možete precizno prilagoditi vlastiti XTTS model s ovim repo-om[XTTS-FINETUNE-WEBUI](https://github.com/daswer123/xtts-finetune-webui)

Ako želite lako unajmiti GPU, također možete duplicirati ovaj zagrljaj zagrljaja[XTTS-FINETUNE-WEBUI-prostor](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Prostor koji možete koristiti za lako uklanjanje unosa podataka o treningu[Denoise-Huggingface-Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Fino podešena TTS kolekcija

Da bismo pronašli našu kolekciju već fino podešenih TTS modela,
posjetiti[ova veza zagrljaja lica](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Za XTTS prilagođeni model Ref Audio isječak glasovne reference je obavezan:

## Demonstracija

**Kišni dan glas**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough glas**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Podržani formati e -knjige

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Najbolji rezultati**:`.epub`ili`.mobi`Za automatsko otkrivanje poglavlja

## Izlaz

-   Stvara a`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Postavite ./lib/conf.py) Datoteka s metapodacima i poglavljima.
-   **Primjer**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Uobičajena pitanja:

-   CPU je spor (bolji na poslužitelju SMP CPU), dok NVIDIA GPU može imati gotovo pretvorbu u stvarnom vremenu.[Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Za bržu višejezičnu generaciju predložio bih svoje drugo[Projekt koji koristi Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)umjesto toga
    (Ipak, nema bez ikakvih glasova glasova, a je li Siri kvalitetan glasovi, ali na CPU-u je mnogo brži).
-   "Imam problema s ovisnošću" - samo upotrijebite Docker, potpuno se samostalno i ima način bez glave,
     dodati`--help`Parametar na kraju naredbe Docker Run za više informacija.
-   "Dobivam skraćeni audio problem!" - molim vas, napravite ovo pitanje,
     Ne govorimo svaki jezik i trebamo savjet od korisnika da fino prilagode logiku dijeljenja rečenice.😊

## O čemu trebam pomoć! 🙌

## [Potpuni popis stvari možete pronaći ovdje](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Svaka pomoć ljudi koji govore bilo koji od podržanih jezika kako bi pomogli u pravilnim metodama dijeljenja rečenica
-   Potencijalno stvaranje ReadMe vodiča za više jezika (jer jedini jezik koji znam je engleski 😔)

## Posebna hvala

-   **Kuhanje TTS**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Kalibar**:[Web stranica kalibra](https://calibre-ebook.com)
-   **Ffmpeg**:[Web stranica ffmppeg](https://ffmpeg.org)
-   [@shakenbake15 za bolju metodu uštede poglavlja](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Možete pogledati kod[ovdje](legacy/v1.0).

## Pridružite se našem poslužitelju!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
