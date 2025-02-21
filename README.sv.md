# 📚 Ebook2AudioBook

CPU/GPU -omvandlare från e -böcker till ljudböcker med kapitel och metadata<br/>Använda kaliber, ffmpeg, xTTSV2, Fairseq och mer. Stöder röstkloning och +1110 språk!

> [!VIKTIG]**Detta verktyg är avsett för användning med icke-DRM, endast lagligt förvärvade e-böcker.**<br>Författarna ansvarar inte för missbruk av denna programvara eller några resulterande rättsliga konsekvenser.<br>Använd detta verktyg ansvarsfullt och i enlighet med alla tillämpliga lagar.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Tack vare Support Ebook2AudioBook -utvecklare!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI -gränssnitt

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Vi köper[Arabiska (arabiska)](./readme/README_AR.md)
-   Zho[Kinesisk](./readme/README_CN.md)
-   a \`a[Engelska](README.md)
-   svärm[Svenska (Swedish)](./readme/README_SWE.md)
-   fas[Persisk (persisk)](./readme/README_FA.md)
-   hon[Italiensk (italiensk)](./readme/README.it.md)

## Innehållsförteckning

-   [ebook2audiobok](#-ebook2audiobook)
-   [Drag](#features)
-   [Docker Gui -gränssnitt](#docker-gui-interface)
-   [Huggingface Space Demo](#huggingface-space-demo)
-   [Gratis Google Colab](#free-google-colab)
-   [Förgjorda ljuddemos](#demos)
-   [Stödsspråk](#supported-languages)
-   [Krav](#hardware-requirements)
-   [Installationsinstruktioner](#installation-instructions)
-   [Användande](#launching-gradio-web-interface)
    -   [Lansering av gradio webbgränssnitt](#launching-gradio-web-interface)
    -   [Grundlös användning](#basic--usage)
    -   [Huvudlös anpassad XTTS -modellanvändning](#example-of-custom-model-zip-upload)
    -   [Hyra en GPU](#renting-a-gpu)
    -   [Hjälpkommandoutdata](#help-command-output)
-   [Fin anpassade TTS -modeller](#fine-tuned-tts-models)
    -   [För insamling av finjusterade TTS-modeller](#fine-tuned-tts-collection)
-   [Använda Docker](#using-docker)
    -   [Dockning](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker komponerar](#docker-compose)
    -   [Docker huvudlös guide](#docker-headless-guide)
    -   [Docker Container filplatser](#docker-container-file-locations)
    -   [Gemensamma dockningsfrågor](#common-docker-issues)
-   [Stödda e -bokformat](#supported-ebook-formats)
-   [Produktion](#output)
-   [Gemensamma frågor](#common-issues)
-   [Särskilt tack](#special-thanks)
-   [Gå med i vår server!](#join-our--server)
-   [Arv](#legacy-v10)
-   [Innehållsförteckning](#table-of-contents)

## Drag

-   📖 Konverterar e -böcker till textformat med kaliber.
-   📚 Delar upp e -boken i kapitel för organiserat ljud.
-   🎙 Högkvalitativ text-till-tal med[Coqui xtTSV2](https://huggingface.co/coqui/XTTS-v2)och[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(och mer).
-   🗣 Valfri röstkloning med din egen röstfil.
-   🌍 Stöder +1110 språk (engelska som standard).[Lista över stödda språk](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥 Utformad för att köra på 4 GB RAM.

## [Huggingface Space Demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingface Space körs på gratis CPU -nivå så förvänta dig mycket långsam eller timeout lol, bara ge det jättefiler är allt
-   Bäst att duplicera utrymme eller springa lokalt.

## Gratis Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Stödsspråk

-   **Arabiska (ARA)**
-   **Kinesiska (ZH)**
-   **Tjeckien (CES)**
-   **Kroatiska (HRV)**
-   **Holländska (NLD)**
-   **Engelska (Eng)**
-   **Franska (från)**
-   **Tyska (DEU)**
-   **Inte (hin)**
-   **Ungerska (AM)**
-   **Italiensk (ita)**
-   **Japanska (JPN)**
-   **Koreanska (COR)**
-   **Polska (pol)**
-   **Portugisiska (por)**
-   **Ryska (RUS)**
-   **Spanska (spa)**
-   **Turkish (tur)**
-   **Vietnamesiska (VIE)**
-   [**+1100 språk via Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Hårdvarukrav

-   4 GB RAM -minimum, 8 GB rekommenderas
-   Virtualisering aktiverad om det körs på Windows (endast Docker)
-   CPU, GPU (rekommenderas), MPS (ännu inte optimerad och kan vara långsammare än CPU) kompatibel

> [!VIKTIG]**Innan för att publicera en installation eller buggproblem söker du noggrant till fliken Öppnade och stängda utgåvor<br>För att vara säker på att ditt problem inte finns redan.**

> [!NOTERA]**Brist på någon standardstruktur som vad som är ett kapitel, stycke, förord ​​etc.<br>Du bör först ta bort manuellt all text som du inte vill konverteras i ljud.**

### Installationsinstruktioner

1.  **Klonrepo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Lansering av gradio webbgränssnitt

1.  **Kör ebook2audiobok**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Fönster**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Öppna webbappen**: Klicka på URL: n som anges i terminalen för att komma åt webbappen och konvertera e -böcker.
3.  **För offentlig länk**:`python app.py --share`(Alla operativsystem)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!VIKTIG]**Om skriptet stoppas och körs igen måste du uppdatera ditt Gradio GUI -gränssnitt<br>För att låta webbsidan återansluta till det nya anslutningsuttaget.**

### Grundläggande användning

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Fönster**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--bok]**: Sökväg till din e -bokfil.
-   **[--röst]**: Röstkloningfilväg (valfritt).
-   **[--språk]**: Språkkod i ISO-639-3 (dvs. ITA för italienska, Eng för engelska, deu för tyska ...).<br>Standardspråket är Eng och -språk är valfritt för standardspråk som är inställt i ./lib/lang.py.<br>ISO-639-1 2 bokstäver koder stöds också.

### Exempel på anpassad zip -uppladdning

(Måste vara en .zip -fil som innehåller obligatoriska modellfiler. Exempel för Xtts: config.json, Model.PTH, VoCab.json och Ref.Wav)

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Fönster**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;anpassad_model_path>**: Väg till`model_name.zip`fil,
        som måste innehålla (enligt TTS -motorn) alla obligatoriska filer<br>(Se ./lib/models.py).

### För detaljerad guide med lista över alla parametrar att använda

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Fönster**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Eller för allt operativsystem**
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

Obs: I Gradio/GUI -läge, för att avbryta en löpande konvertering, klicka bara på[X]Från eBook -uppladdningskomponenten.

### Använda Docker

Du kan också använda Docker för att köra e -boken till Audiobook Converter. 
Denna metod säkerställer konsistens mellan olika miljöer och förenklar installationen.

#### Kör dockningsbehållaren

För att köra Docker -behållaren och starta Gradio -gränssnittet använder du följande kommando:

\-Run med endast CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run med GPU Speedup (endast NVIDIA -kompatibel))

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Bygga dockningsbehållaren

-   Du kan bygga dockningsbilden med kommandot:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Detta kommando startar Gradio -gränssnittet på port 7860. (Localhost: 7860)

-   För fler alternativ lägg till parametern`--help`

## Docker Container filplatser

Alla eBook2AudioBooks kommer att ha basen -dir av`/home/user/app/`Till exempel:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker huvudlös guide

först för en dockare drag av det senaste med

```bash
docker pull athomasson2/ebook2audiobook
```

-   Innan du kör detta måste du skapa en dir med namnet "input-folder" i din nuvarande dir
    som kommer att länkas, det är här du kan lägga dina inmatningsfiler för Docker -bilden för att se

```bash
mkdir input-folder && mkdir Audiobooks
```

-   I kommandot nedan byt ut**Your_input_file.txt**Med namnet på din inmatningsfil

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   Och det borde vara det!
-   Output Audiobooks finns i Audiobook -mappen som också kommer att finnas
    I din lokala dir körde du detta Docker -kommando i

## För att få hjälpkommandot för de andra parametrarna som detta program har kan du köra detta

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

Och det kommer att mata ut detta[Hjälpkommandoutdata](#help-command-output)

### Docker komponerar

Detta projekt använder Docker Compose för att köras lokalt. Du kan aktivera eller inaktivera GPU -stöd 
genom att ställa in endera`*gpu-enabled`eller`*gpu-disabled`i`docker-compose.yml`

#### Steg att springa

1.  **Klona förvaret**(Om du inte redan har gjort det):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Ställ in GPU -support (inaktiverat som standard)**För att aktivera GPU -stöd, ändra`docker-compose.yml`och förändring`*gpu-disabled`till`*gpu-enabled`
3.  **Starta tjänsten:**
    ```bash
    docker-compose up -d
    ```
4.  **Åtkomst till tjänsten:**Tjänsten kommer att finnas tillgänglig på http&#x3A; // localhost: 7860.

### Docker Gui -gränssnitt

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Hyra en GPU

Har du inte hårdvaran för att köra den eller vill du hyra en GPU?

#### Du kan duplicera Hugginface -utrymmet och hyra en GPU för cirka $ 0,40 per timme

[Huggingface Space Demo](#huggingface-space-demo)

#### Eller så kan du försöka använda Google Colab gratis!

(Var medveten om att det kommer att avgå efter lite av att du inte rör sig med Google Colab)[Gratis Google Colab](#free-google-colab)

## Gemensamma dockningsfrågor

-   Docker fastnar nedladdning av finjusterade modeller.
    (Detta händer inte för varje dator men vissa verkar stöta på det här problemet)
    Inaktivering av framstegsfältet verkar lösa problemet,
    Som diskuterats[Här i #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Exempel på att lägga till denna fix i`docker run`kommando

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Fin anpassade TTS -modeller

Du kan enkelt finjustera din egen XTTS-modell med denna repo[XttTs-Finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Om du enkelt vill hyra en GPU kan du också duplicera det här kramytan[XTTS-FINETUNE-WEBUI-SPACE](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Ett utrymme du kan använda för att avbryta utbildningsdata lätt också[denre-kramplatsen](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Finjusterad TTS -samling

För att hitta vår samling av redan finjusterade TTS-modeller,
besök[Denna kramande ansiktslänk](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)För en XTTS -anpassad modell är ett REF -ljudklipp av röstreferensen obligatorisk:

## Demos

**Regny Day Voice**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Stödda e -bokformat

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Bästa resultat**:`.epub`eller`.mobi`för automatisk kapitelupptäckt

## Produktion

-   Skapar en`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Ställ in ./lib/conf.py) -filen med metadata och kapitel.
-   **Exempel**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Vanliga frågor:

-   CPU är långsam (bättre på server SMP CPU) medan NVIDIA GPU kan ha nästan realtidskonvertering.[Diskussion om detta](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)För snabbare flerspråkig generation skulle jag föreslå min andra[projekt som använder Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)i stället
    (Det har dock inte noll-skott-röstkloning och är Siri-kvalitetsröster, men det är mycket snabbare på CPU).
-   "Jag har beroendeproblem" - använd bara dockaren, det är helt fristående och har ett huvudlöst läge,
     tillägga`--help`Parameter i slutet av Docker Run -kommandot för mer information.
-   "Jag får ett trunkerat ljudproblem!" - Vänligen göra en fråga om detta,
     Vi talar inte alla språk och behöver råd från användare att finjustera meningen som delar Logic.😊

## Vad jag behöver hjälp med! 🙌

## [Fullständig lista över saker kan hittas här](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   All hjälp från personer som talar något av de stödda språken för att hjälpa till med korrekt meningsdelningsmetoder
-   Potentiellt skapa Readme Guides för flera språk (eftersom det enda språket jag känner är engelska 😔)

## Särskilt tack

-   **Matlagning**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Kaliber**:[Kaliberwebbplats](https://calibre-ebook.com)
-   **Ffmpeg**:[FFMPEG -webbplats](https://ffmpeg.org)
-   [@ShakenBake15 för bättre kapitelbesparingsmetod](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Du kan se koden[här](legacy/v1.0).

## Gå med i vår server!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
