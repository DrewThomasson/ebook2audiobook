# 📚 ebook2audiobook

CPU/GPU -converter van e -boeken tot audioboeken met hoofdstukken en metadata<br/>met behulp van kaliber, FFMPEG, XTTSV2, Fairseq en meer. Ondersteunt spraakklonen en +1110 talen!

> [!BELANGRIJK]**Deze tool is bedoeld voor gebruik met niet-DRM, alleen wettelijk overgenomen eBooks.**<br>De auteurs zijn niet verantwoordelijk voor misbruik van deze software of resulterende juridische gevolgen.<br>Gebruik deze tool verantwoordelijk en in overeenstemming met alle toepasselijke wetten.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Dankzij ondersteuning Ebook2audiobook -ontwikkelaars!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI -interface

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   We kopen[Arabisch (Arabisch)](./readme/README_AR.md)
-   Zho[Chinese](./readme/README_CN.md)
-   a \`a[Engels](README.md)
-   zweren[Zweeds (Zweeds)](./readme/README_SWE.md)
-   fas[Perzisch (Perzisch)](./readme/README_FA.md)
-   zij[Italiaans (Italiaans)](./readme/README.it.md)

## Inhoudsopgave

-   [ebook2audiobook](#-ebook2audiobook)
-   [Functies](#features)
-   [Docker GUI -interface](#docker-gui-interface)
-   [Knuffelruimte Demo](#huggingface-space-demo)
-   [Gratis Google Colab](#free-google-colab)
-   [Vooraf gemaakte audio-demo's](#demos)
-   [Ondersteunde talen](#supported-languages)
-   [Vereisten](#hardware-requirements)
-   [Installatie -instructies](#installation-instructions)
-   [Gebruik](#launching-gradio-web-interface)
    -   [Gradio Web -interface starten](#launching-gradio-web-interface)
    -   [Basic Headless gebruik](#basic--usage)
    -   [Headless aangepaste XTTS -modelgebruik](#example-of-custom-model-zip-upload)
    -   [Een GPU huren](#renting-a-gpu)
    -   [Help Command -uitvoer](#help-command-output)
-   [Fijn afgestemde TTS -modellen](#fine-tuned-tts-models)
    -   [Voor het verzamelen van verfijnde TTS-modellen](#fine-tuned-tts-collection)
-   [Docker gebruiken](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker componeren](#docker-compose)
    -   [Docker Headless Guide](#docker-headless-guide)
    -   [Docker -containerbestandslocaties](#docker-container-file-locations)
    -   [Veel voorkomende docker -problemen](#common-docker-issues)
-   [Ondersteunde e -boekformaten](#supported-ebook-formats)
-   [Uitvoer](#output)
-   [Veel voorkomende problemen](#common-issues)
-   [Speciale dank](#special-thanks)
-   [Word lid van onze server!](#join-our--server)
-   [Nalatenschap](#legacy-v10)
-   [Inhoudsopgave](#table-of-contents)

## Functies

-   📖 Converteert eBooks naar tekstformaat met kaliber.
-   📚 splitst e -boek in hoofdstukken voor georganiseerde audio.
-   🎙️ hoogwaardige tekst-naar-spraak met[Coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)En[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(en meer).
-   🗣️ Optioneel spraakklonering met uw eigen spraakbestand.
-   🌍 Ondersteunt +1110 talen (standaard Engels).[Lijst met ondersteunde talen](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ Ontworpen om te draaien op 4 GB RAM.

## [Knuffelruimte Demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingface Space draait op gratis CPU -laag, dus verwacht erg langzaam of time -out lol, geef het gewoon geen gigantische bestanden
-   Het beste om ruimte te dupliceren of lokaal te rennen.

## Gratis Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Ondersteunde talen

-   **Arabisch (ARA)**
-   **Chinees (ZH)**
-   **Tsjechisch (CES)**
-   **Kroatisch (HRV)**
-   **Dutch (nld)**
-   **Engels (eng)**
-   **Frans (van)**
-   **Duits (DEU)**
-   **Niet (hin)**
-   **Hungarian (hun)**
-   **Italiaans (ita)**
-   **Japans (JPN)**
-   **Koreaans (Cor)**
-   **Pools (Pol)**
-   **Portugees (Por)**
-   **Russisch (Rus)**
-   **Spaans (spa)**
-   **Turks (rond)**
-   **Vietnamees (VIE)**
-   [**+1100 talen via Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Hardwarevereisten

-   4 GB RAM -minimum, 8 GB aanbevolen
-   Virtualisatie ingeschakeld als het wordt uitgevoerd op Windows (alleen Docker)
-   CPU, GPU (aanbevolen), MPS (nog niet geoptimaliseerd en kan langzamer zijn dan CPU)

> [!BELANGRIJK]**Voordat u een installatie- of bug -uitgave zorgvuldig zoeken naar het tabblad Opende en gesloten problemen<br>Om er zeker van te zijn dat uw probleem nog niet bestaat.**

> [!OPMERKING]**Het ontbreken van een standaardstructuur zoals een hoofdstuk, paragraaf, voorwoord enz.<br>U moet eerst handmatig alle tekst verwijderen die u niet in audio wilt bekeren.**

### Installatie -instructies

1.  **Kloon repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Gradio Web -interface starten

1.  **Voer eBook2audiobook uit**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Ramen**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Open de web -app**: Klik op de URL die in de terminal is geleverd om toegang te krijgen tot de web -app en eBooks te converteren.
3.  **Voor openbare link**:`python app.py --share`(Alle OS)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!BELANGRIJK]**Als het script wordt gestopt en opnieuw wordt uitgevoerd, moet u uw Gradio GUI -interface vernieuwen<br>Om de webpagina opnieuw te laten verbinding maken met de nieuwe verbindingssap.**

### Basisgebruik

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Ramen**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Boek]**: Pad naar je e -boekbestand.
-   **[--stem]**: Spraakkloneringspad (optioneel).
-   **[--taal]**: Taalcode in ISO-639-3 (d.w.z. ITA voor Italiaans, eng voor Engels, Deu voor Duits ...).<br>Standaardtaal is ENG en -Language is optioneel voor standaardtaal ingesteld in ./lib/lang.py.<br>De ISO-639-1 2-letterscodes worden ook ondersteund.

### Voorbeeld van aangepaste model ZIP -upload

(Moet een .zip -bestand zijn met de verplichte modelbestanden. Voorbeeld voor XTTS: config.json, model.pth, vocab.json en ref.wav)

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Ramen**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**: Pad naar`model_name.zip`bestand,
        die (volgens de TTS -engine) alle verplichte bestanden moeten bevatten<br>(Zie ./lib/models.py).

### Voor gedetailleerde gids met een lijst met alle te gebruiken parameters

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Ramen**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Of voor al het os**
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

OPMERKING: Klik in de Gradio/GUI -modus om een ​​lopende conversie te annuleren gewoon op de[X]van de eBook Upload -component.

### Docker gebruiken

U kunt ook Docker gebruiken om het e -boek uit te voeren naar Audiobook Converter. 
Deze methode zorgt voor consistentie in verschillende omgevingen en vereenvoudigt de installatie.

#### De Docker -container uitvoeren

Gebruik de volgende opdracht om de Docker -container uit te voeren en de Gradio -interface te starten:

\-Run alleen met CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run met GPU -versnelling (alleen nvidia compatibel)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Het bouwen van de Docker -container

-   U kunt de Docker -afbeelding bouwen met de opdracht:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Deze opdracht start de Gradio -interface op poort 7860. (LocalHost: 7860)

-   Voeg voor meer opties de parameter toe`--help`

## Docker -containerbestandslocaties

Alle eBook2audiobooks zullen de basis hebben van`/home/user/app/`Bijvoorbeeld:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker Headless Guide

Eerst voor een Docker -pull van de laatste met

```bash
docker pull athomasson2/ebook2audiobook
```

-   Voordat u dit uitvoert, moet u een DIR maken met de naam "Input-Folder" in uw huidige directie
    die wordt gekoppeld, hier kunt u uw invoerbestanden voor de Docker -afbeelding plaatsen om te zien

```bash
mkdir input-folder && mkdir Audiobooks
```

-   In het onderstaande opdracht ruilt uit**Your_input_file.txt**Met de naam van uw invoerbestand

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   En dat zou het moeten zijn!
-   De output -audioboeken zijn te vinden in de map Audiobook die ook zal worden gevonden
    In uw plaatselijke directie U heeft dit Docker -opdracht uitgevoerd

## Om de Help -opdracht te krijgen voor de andere parameters die dit programma heeft, kunt u dit uitvoeren

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

En dat zal dit uitvoeren[Help Command -uitvoer](#help-command-output)

### Docker componeren

Dit project maakt gebruik van Docker Compose om lokaal te worden uitgevoerd. U kunt GPU -ondersteuning inschakelen of uitschakelen 
door beide in te stellen`*gpu-enabled`of`*gpu-disabled`in`docker-compose.yml`

#### Stappen om uit te voeren

1.  **Kloon de repository**(Als je dat nog niet hebt gedaan):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Stel GPU -ondersteuning in (standaard uitgeschakeld)**Om GPU -ondersteuning mogelijk te maken, wijzigen`docker-compose.yml`en veranderen`*gpu-disabled`naar`*gpu-enabled`
3.  **Start de service:**
    ```bash
    docker-compose up -d
    ```
4.  **Toegang tot de service:**De service is beschikbaar op http&#x3A; // localhost: 7860.

### Docker GUI -interface

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Een GPU huren

Heb je niet de hardware om het uit te voeren of wil je een GPU huren?

#### U kunt de Hugginface -ruimte dupliceren en een GPU huren voor ongeveer $ 0,40 per uur

[Knuffelruimte Demo](#huggingface-space-demo)

#### Of u kunt de Google Colab gratis proberen te gebruiken!

(Houd er rekening mee dat het time -out zal zijn na een beetje van je niet knoeien met de Google Colab)[Gratis Google Colab](#free-google-colab)

## Veel voorkomende docker -problemen

-   Docker komt vast te zitten en het downloaden van verfijnde modellen.
    (Dit gebeurt niet voor elke computer, maar sommigen lijken dit probleem tegen te komen)
    Het uitschakelen van de voortgangsbalk lijkt het probleem op te lossen,
    Zoals besproken[Hier in #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Voorbeeld van het toevoegen van deze oplossing in de`docker run`commando

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Fijn afgestemde TTS -modellen

U kunt uw eigen XTTS-model gemakkelijk aanpassen met deze repo[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

Als u eenvoudig een GPU wilt huren, kunt u dit knuffel ook dupliceren[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Een ruimte die u kunt gebruiken om de trainingsgegevens ook gemakkelijk uit te roven[denoise-huggingface-ruimte](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Fijn afgestemde TTS -collectie

Om onze verzameling reeds verfijnde TTS-modellen te vinden,
bezoek[Deze knuffelende gezichtslink](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Voor een XTTS Aangepast model is een ref -audioclip van de spraakreferentie verplicht:

## Demos

**Regenachtige dagstem**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough stem**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Ondersteunde e -boekformaten

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Beste resultaten**:`.epub`of`.mobi`voor automatische hoofdstukdetectie

## Uitvoer

-   Creëert een`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Set in ./lib/conf.py) Bestand met metadata en hoofdstukken.
-   **Voorbeeld**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Veel voorkomende problemen:

-   CPU is traag (beter op Server SMP CPU), terwijl NVIDIA GPU bijna realtime conversie kan hebben.[Discussie hierover](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Voor snellere meertalige generatie zou ik mijn andere voorstellen[Project dat Piper-TT's gebruikt](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)in plaats van
    (Het heeft echter geen nul-shot stem klonen en is Siri-kwaliteitsstemmen, maar het is veel sneller op CPU).
-   "Ik heb afhankelijkheidsproblemen" - gebruik gewoon de Docker, het is volledig op zichzelf staand en heeft een modus zonder headly,
     toevoegen`--help`Parameter aan het einde van de opdracht Docker Run voor meer informatie.
-   "Ik krijg een afgekapt audioprobleem!" - Maak hier een probleem van,
     We spreken niet elke taal en hebben advies van gebruikers nodig om de zinsplitsende logica te afstemmen.

## Waar ik hulp bij nodig heb! 🙌

## [Volledige lijst met dingen is hier te vinden](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Alle hulp van mensen die een van de ondersteunde talen spreken om te helpen bij de juiste methoden voor het splitsen van zinnen
-   Potentieel het creëren van README -gidsen voor meerdere talen (omdat de enige taal die ik ken Engels is 😔 😔 😔)

## Speciale dank

-   **Kookts**:[Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
-   **Kaliber**:[Kaliberwebsite](https://calibre-ebook.com)
-   **Ffmpeg**:[FFMPEG -website](https://ffmpeg.org)
-   [@shakenbake15 voor een betere methode voor het opslaan van hoofdstukken](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

U kunt de code bekijken[hier](legacy/v1.0).

## Word lid van onze server!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
