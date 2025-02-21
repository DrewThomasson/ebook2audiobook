# 📚 Ebook2audiobook

CPU/GPU Converter kutoka eBooks hadi Audiobooks na Sura na Metadata<br/>Kutumia caliber, FFMPEG, XTTSV2, FairSeq na zaidi. Inasaidia sauti ya kupiga sauti na +1110 lugha!

> [Muhimu!]**Chombo hiki kimekusudiwa kutumiwa na zisizo za DRM, zilizopatikana kisheria tu.**<br>Waandishi hawawajibiki kwa matumizi mabaya ya programu hii au athari zozote za kisheria.<br>Tumia zana hii kwa uwajibikaji na kulingana na sheria zote zinazotumika.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Shukrani kwa kuunga mkono watengenezaji wa eBook2audiobook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Maingiliano ya GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Tunanunua[Kiarabu (Kiarabu)](./readme/README_AR.md)
-   Zho[Kichina](./readme/README_CN.md)
-   a \`a[Kiingereza](README.md)
-   swe[Kiswidi (Kiswidi)](./readme/README_SWE.md)
-   fas[Kiajemi (Kiajemi)](./readme/README_FA.md)
-   Yeye[Kiitaliano (Kiitaliano)](./readme/README.it.md)

## Jedwali la yaliyomo

-   [eBook2Audiobook](#-ebook2audiobook)
-   [Vipengee](#features)
-   [Docker GUI interface](#docker-gui-interface)
-   [Kukumbatia nafasi ya nafasi](#huggingface-space-demo)
-   [Bure Google Colab](#free-google-colab)
-   [Demos za sauti zilizotengenezwa mapema](#demos)
-   [Lugha zilizoungwa mkono](#supported-languages)
-   [Mahitaji](#hardware-requirements)
-   [Maagizo ya Ufungaji](#installation-instructions)
-   [Matumizi](#launching-gradio-web-interface)
    -   [Kuzindua interface ya Wavuti ya Gradio](#launching-gradio-web-interface)
    -   [Matumizi ya msingi isiyo na kichwa](#basic--usage)
    -   [Matumizi ya mfano wa XTTS ya kichwa](#example-of-custom-model-zip-upload)
    -   [Kukodisha GPU](#renting-a-gpu)
    -   [Msaada wa amri](#help-command-output)
-   [Mfano mzuri wa TTS](#fine-tuned-tts-models)
    -   [Kwa ukusanyaji wa mifano nzuri ya TTS](#fine-tuned-tts-collection)
-   [Kutumia Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker kujenga](#building-the-docker-container)
    -   [Docker kutunga](#docker-compose)
    -   [Mwongozo usio na kichwa wa Docker](#docker-headless-guide)
    -   [Maeneo ya faili ya Docker](#docker-container-file-locations)
    -   [Maswala ya kawaida ya Docker](#common-docker-issues)
-   [Fomati za ebook zilizoungwa mkono](#supported-ebook-formats)
-   [Pato](#output)
-   [Maswala ya kawaida](#common-issues)
-   [Shukrani maalum](#special-thanks)
-   [Jiunge na seva yetu!](#join-our--server)
-   [Urithi](#legacy-v10)
-   [Jedwali la yaliyomo](#table-of-contents)

## Vipengee

-   📖 Inabadilisha eBooks kuwa muundo wa maandishi na caliber.
-   📚 Splits ebook katika sura za sauti zilizopangwa.
-   🎙️ maandishi ya hali ya juu-kwa-hotuba na[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)na[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(na zaidi).
-   Sauti ya hiari ya sauti na faili yako mwenyewe ya sauti.
-   🌍 Inasaidia +1110 Lugha (Kiingereza kwa chaguo -msingi).[Orodha ya lugha zilizoungwa mkono](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ Iliyoundwa ili kukimbia kwenye RAM ya 4GB.

## [Kukumbatia nafasi ya nafasi](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Nafasi ya kukumbatiana inaendelea kwenye tier ya bure ya CPU kwa hivyo tarajia polepole sana au wakati wa muda, usipe faili kubwa ni zote
-   Bora kurudia nafasi au kukimbia ndani.

## Bure Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Lugha zilizoungwa mkono

-   **Kiarabu (Ara)**
-   **Kichina (ZH)**
-   **Kicheki (CES)**
-   **Kikroeshia (HRV)**
-   **Uholanzi (NLD)**
-   **Kiingereza (Eng)**
-   **Mfaransa (kutoka)**
-   **Kijerumani (Deu)**
-   **Sio (Hin)**
-   **Kihungari (AM)**
-   **Kiitaliano (Ita)**
-   **Kijapani (JPN)**
-   **Kikorea (Cor)**
-   **Kipolishi (Pol)**
-   **Kireno (por)**
-   **Kirusi (Rus)**
-   **Kihispania (spa)**
-   **Kituruki (pande zote)**
-   **Kivietinamu (vie)**
-   [**+1100 lugha kupitia FairSeq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Mahitaji ya vifaa

-   Kiwango cha chini cha RAM cha 4GB, 8GB ilipendekezwa
-   Virtualization imewezeshwa ikiwa inaendesha kwenye Windows (Docker tu)
-   CPU, GPU (ilipendekezwa), Wabunge (bado haijaboreshwa na inaweza kuwa polepole kuliko CPU) inayoendana

> [Muhimu!]**Kabla ya kutuma utaftaji au toleo la mdudu kwa uangalifu kwa kichupo kilichofunguliwa na kilichofungwa<br>Ili kuhakikisha kuwa suala lako halipo tayari.**

> [Kumbuka!]**Ukosefu wa muundo wowote wa viwango kama nini sura, aya, utangulizi nk.<br>Unapaswa kwanza kuondoa maandishi yoyote ambayo hautaki kubadilishwa kwa sauti.**

### Maagizo ya Ufungaji

1.  **Clone repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Kuzindua interface ya Wavuti ya Gradio

1.  **Run eBook2Audiobook**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Windows**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Fungua programu ya wavuti**: Bonyeza URL iliyotolewa kwenye terminal kufikia programu ya wavuti na ubadilishe eBooks.
3.  **Kwa kiungo cha umma**:`python app.py --share`(OS yote)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [Muhimu!]**Ikiwa maandishi yamesimamishwa na kukimbia tena, unahitaji kuburudisha kigeuzi chako cha Gradio GUI<br>Kuruhusu ukurasa wa wavuti kuungana tena na tundu mpya la unganisho.**

### Matumizi ya kimsingi

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[—Ebook--]**Njia ya faili yako ya ebook.
-   **[--sauti]**: Njia ya faili ya kuweka sauti (hiari).
-   **[--lugha]**: Nambari ya lugha katika ISO-639-3 (i.e.: ITA kwa Italia, Eng kwa Kiingereza, Deu kwa Kijerumani ...).<br>Lugha chaguo -msingi ni ENG na -lugha ni hiari kwa lugha chaguo -msingi iliyowekwa ./lib/lang.py.<br>Nambari za herufi za ISO-639-1 2 pia zinasaidiwa.

### Mfano wa upakiaji wa mfano wa Zip

.

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**Njia ya`model_name.zip`faili,
        ambayo lazima iwe na (kulingana na injini ya TTS) faili zote za lazima<br>(Tazama ./lib/models.py).

### Kwa mwongozo wa kina na orodha ya vigezo vyote vya kutumia

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Au kwa OS yote**
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

Kumbuka: Katika hali ya Gradio/GUI, kufuta ubadilishaji unaoendesha, bonyeza tu kwenye[X]Kutoka kwa sehemu ya kupakia ebook.

### Kutumia Docker

Unaweza pia kutumia Docker kuendesha eBook kwa kibadilishaji cha sauti. 
Njia hii inahakikisha uthabiti katika mazingira tofauti na kurahisisha usanidi.

#### Kuendesha chombo cha Docker

Ili kuendesha chombo cha Docker na anza interface ya Gradio, tumia amri ifuatayo:

\-Run na CPU tu

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run na kasi ya GPU (NVIDIA inalingana tu)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Kuunda chombo cha Docker

-   Unaweza kujenga picha ya Docker na amri:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Amri hii itaanza interface ya Gradio kwenye bandari 7860. (Localhost: 7860)

-   Kwa chaguzi zaidi ongeza parameta`--help`

## Maeneo ya faili ya Docker

EBOOK2AUDIADIOBOOKS itakuwa na msingi wa`/home/user/app/`Kwa mfano:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Mwongozo usio na kichwa wa Docker

Kwanza kwa docker ya hivi karibuni na

```bash
docker pull athomasson2/ebook2audiobook
```

-   Kabla ya kuendesha hii unahitaji kuunda dir inayoitwa "pembejeo-folder" kwenye dir yako ya sasa
    ambayo itaunganishwa, hapa ndipo unaweza kuweka faili zako za pembejeo kwa picha ya Docker ili kuona

```bash
mkdir input-folder && mkdir Audiobooks
```

-   Katika amri hapa chini ubadilishe**Yako_input_file.txt**na jina la faili yako ya pembejeo

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   Na hiyo inapaswa kuwa hivyo!
-   Vitabu vya pato vitapatikana kwenye folda ya AudioBook ambayo pia itapatikana
    Katika dir yako ya karibu uliendesha amri hii ya kizimbani katika

## Ili kupata amri ya msaada kwa vigezo vingine programu hii inaweza kuendesha hii

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

Na hiyo itatoa hii[Msaada wa amri](#help-command-output)

### Docker kutunga

Mradi huu hutumia Docker kutunga kuendesha ndani. Unaweza kuwezesha au kulemaza msaada wa GPU 
kwa kuweka ama`*gpu-enabled`au`*gpu-disabled`katika`docker-compose.yml`

#### Hatua za kukimbia

1.  **Clone hazina**(Ikiwa haujawahi):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Weka msaada wa GPU (walemavu kwa chaguo -msingi)**Ili kuwezesha msaada wa GPU, kurekebisha`docker-compose.yml`na mabadiliko`*gpu-disabled`kwa`*gpu-enabled`
3.  **Anza huduma:**
    ```bash
    docker-compose up -d
    ```
4.  **Fikia Huduma:**Huduma hiyo itapatikana katika http&#x3A; // localhost: 7860.

### Docker GUI interface

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Kukodisha GPU

Je! Hauna vifaa vya kuiendesha au unataka kukodisha GPU?

#### Unaweza kurudia nafasi ya hugginface na kukodisha GPU kwa karibu $ 0.40 kwa saa

[Kukumbatia nafasi ya nafasi](#huggingface-space-demo)

#### Au unaweza kujaribu kutumia google colab bure!

(Fahamu kuwa itatoka baada ya kukosa shida yako na colab ya google)[Bure Google Colab](#free-google-colab)

## Maswala ya kawaida ya Docker

-   Docker hukwama kupakua mifano laini-iliyowekwa.
    (Hii haifanyiki kwa kila kompyuta lakini wengine wanaonekana kuingia kwenye suala hili)
    Kulemaza bar ya maendeleo inaonekana kurekebisha suala,
    kama ilivyojadiliwa[Hapa katika #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Mfano wa kuongeza fix hii katika`docker run`amri

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Mfano mzuri wa TTS

Unaweza kurekebisha mfano wako mwenyewe wa XTTS kwa urahisi na repo hii[Xtts-finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Ikiwa unataka kukodisha GPU kwa urahisi unaweza pia nakala hii ya kukumbatiana[Xtts-finetune-Webui-nafasi](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Nafasi unayoweza kutumia de-kelele data ya mafunzo kwa urahisi pia[Nafasi ya Denoise-Huggingface](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Mkusanyiko mzuri wa TTS

Ili kupata mkusanyiko wetu wa mifano tayari ya TTS,
Ziara[Kiunga hiki cha uso wa kukumbatia](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Kwa mfano wa kawaida wa XTTS kipande cha sauti cha rejea cha sauti ni lazima:

## Demos

**Sauti ya siku ya mvua**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**Sauti ya David Attenborough**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Fomati za ebook zilizoungwa mkono

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Matokeo bora**:`.epub`au`.mobi`Kwa ugunduzi wa sura moja kwa moja

## Pato

-   Inaunda a`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(kuweka katika ./lib/conf.py) faili na metadata na sura.
-   **Mfano**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Maswala ya kawaida:

-   CPU ni polepole (bora kwenye Server SMP CPU) wakati Nvidia GPU inaweza kuwa na ubadilishaji wa wakati halisi.[Majadiliano juu ya hii](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Kwa kizazi cha lugha nyingi ningependekeza nyingine yangu[Mradi ambao hutumia Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)badala yake
    (Haina sauti ya sauti-sifuri, na ni sauti za ubora wa Siri, lakini ni haraka sana kwenye CPU).
-   "Nina maswala ya utegemezi" - tumia tu kizimbani, kilichomo kikamilifu na ina hali isiyo na kichwa,
     ADD`--help`Parameta mwishoni mwa amri ya kukimbia ya Docker kwa habari zaidi.
-   "Ninapata suala la sauti lililopunguzwa!" - Tafadhali fanya suala la hii,
     Hatuzungumzi kila lugha na tunahitaji ushauri kutoka kwa watumiaji ili kuweka laini ya kugawanyika kwa sentensi.😊

## Ninachohitaji msaada na! 🙌

## [Orodha kamili ya mambo yanaweza kupatikana hapa](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Msaada wowote kutoka kwa watu wanaozungumza lugha yoyote inayoungwa mkono ili kusaidia na njia sahihi za kugawanya sentensi
-   Uwezekano wa kuunda miongozo ya kusoma kwa lugha nyingi (kwa sababu lugha pekee ninayojua ni Kiingereza 😔)

## Shukrani maalum

-   **Kupika TTS**:[Coqui tts GitHub](https://github.com/idiap/coqui-ai-TTS)
-   **Caliber**:[Tovuti ya caliber](https://calibre-ebook.com)
-   **Ffmpeg**:[Tovuti ya FFMPEG](https://ffmpeg.org)
-   [@ShakenBake15 kwa njia bora ya kuokoa sura](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Urithi v1.0](legacy/v1.0)

Unaweza kutazama nambari[Hapa](legacy/v1.0).

## Jiunge na seva yetu!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
