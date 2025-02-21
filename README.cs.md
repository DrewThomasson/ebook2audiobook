# 📚 Ebook2audiObook

Převodník CPU/GPU z e -knih na audioknihy s kapitolami a metadatami<br/>Použití ráže, FFMPEG, XTTSV2, FAIRSEQ a další. Podporuje hlasové klonování a +1110 jazyků!

> [! Důležité]**Tento nástroj je určen k použití pouze s EN-DRM, legálně získanými e-knihami.**<br>Autoři neodpovídají za zneužití tohoto softwaru ani žádné výsledné právní důsledky.<br>Tento nástroj použijte zodpovědně a v souladu se všemi platnými zákony.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Díky podpoře vývojářů Ebook2audiObook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Rozhraní GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Kupujeme[Arabština (arabština)](./readme/README_AR.md)
-   Zho[čínština](./readme/README_CN.md)
-   \`a[angličtina](README.md)
-   Swe[Švédština (švédská)](./readme/README_SWE.md)
-   FAS[Peršan (Peršan)](./readme/README_FA.md)
-   ona[Ital (Ital)](./readme/README.it.md)

## Obsah

-   [Ebook2audiObook](#-ebook2audiobook)
-   [Funkce](#features)
-   [Rozhraní GUI Docker GUI](#docker-gui-interface)
-   [Demo objímání prostoru](#huggingface-space-demo)
-   [Zdarma Google Colab](#free-google-colab)
-   [Předem vytvořená zvuková ukázka](#demos)
-   [Podporované jazyky](#supported-languages)
-   [Požadavky](#hardware-requirements)
-   [Instalační pokyny](#installation-instructions)
-   [Používání](#launching-gradio-web-interface)
    -   [Spuštění webového rozhraní Gradio](#launching-gradio-web-interface)
    -   [Základní bezhlavé použití](#basic--usage)
    -   [Použití modelu bez hlavy](#example-of-custom-model-zip-upload)
    -   [Pronájem GPU](#renting-a-gpu)
    -   [Nápověda výstup příkazu](#help-command-output)
-   [Jemně vyladěné modely TTS](#fine-tuned-tts-models)
    -   [Pro sběr jemně vyladěných modelů TTS](#fine-tuned-tts-collection)
-   [Pomocí Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [Docker bezhlavý průvodce](#docker-headless-guide)
    -   [Umístění souborů kontejneru Docker](#docker-container-file-locations)
    -   [Běžné problémy Docker](#common-docker-issues)
-   [Podporované formáty ebook](#supported-ebook-formats)
-   [Výstup](#output)
-   [Běžné problémy](#common-issues)
-   [Zvláštní poděkování](#special-thanks)
-   [Připojte se k našemu serveru!](#join-our--server)
-   [Dědictví](#legacy-v10)
-   [Obsah](#table-of-contents)

## Funkce

-   📖 Převádí e -knihy do textového formátu s Caliber.
-   📚 Rozdělí ebook do kapitol pro organizovaný zvuk.
-   🎙 Vysoce kvalitní text na řeč[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)a[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(a další).
-   🗣 Volitelné klonování hlasu s vlastním hlasovým souborem.
-   🌍 Podporuje jazyky +1110 (ve výchozím nastavení angličtina).[Seznam podporovaných jazyků](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥 Navrženo pro běh na 4 GB RAM.

## [Demo objímání prostoru](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Objímání prostoru probíhá na volné úrovni CPU, takže očekávejte velmi pomalý nebo časový limit lol, prostě to nedávejte obří soubory, je všechno
-   Nejlepší je duplikovat prostor nebo běžet lokálně.

## Zdarma Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Podporované jazyky

-   **Arabština (ara)**
-   **Číňan (ZH)**
-   **Čech (CES)**
-   **Chorvaté (HRV)**
-   **Holanďan (NLD)**
-   **Angličtina (Eng)**
-   **Francouzština (od)**
-   **Němec (DEU)**
-   **Ne (hin)**
-   **Maďarština (AM)**
-   **Ital (ITA)**
-   **Japonec (JPN)**
-   **Korean (Cor)**
-   **Polský (pol)**
-   **Portugalština (por)**
-   **Rus (RUS)**
-   **Španělština (lázně)**
-   **Turečtina (kolo)**
-   **Vietnamci (vie)**
-   [**+1100 jazyků přes FairSeq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Hardwarové požadavky

-   4 GB RAM minimálně, doporučeno 8 GB
-   Virtualizace je povolena, pokud běží na Windows (pouze Docker)
-   CPU, GPU (doporučeno), MPS (dosud není optimalizován a může být pomalejší než CPU) kompatibilní

> [! Důležité]**Předtím, než na kartě Otevřené a uzavřené problémy pečlivě zveřejníte vyhledávání instalace nebo chyby<br>Chcete -li se ujistit, že váš problém již neexistuje.**

> [!POZNÁMKA]**Chybí jakoukoli strukturu standardů, jako je kapitola, odstavec, předmluva atd.<br>Nejprve byste měli odstranit ručně jakýkoli text, který nechcete být převedeni do zvuku.**

### Instalační pokyny

1.  **Klon repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Spuštění webového rozhraní Gradio

1.  **Spusťte ebook2audiobook**:
    -   **Linux/MacOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Okna**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Otevřete webovou aplikaci**: Kliknutím na adresu URL poskytnuté v terminálu pro přístup k webové aplikaci a převedení e -knih.
3.  **Pro veřejný odkaz**:`python app.py --share`(Všechny os)`./ebook2audiobook.sh --share`(Linux/MacOS)`ebook2audiobook.cmd --share`(Windows)

> [! Důležité]**Pokud je skript zastaven a znovu spuštěn, musíte obnovit své rozhraní Gradio GUI<br>Aby se webová stránka znovu připojila k nové zásuvce připojení.**

### Základní použití

-   **Linux/MacOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Okna**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Ebook]**: Cesta do souboru elektronické knihy.
-   **[--hlas]**: Cesta souboru pro klonování hlasové (volitelné).
-   **[--jazyk]**: Jazykový kód v ISO-639-3 (tj.: ITA pro italštinu, Eng pro angličtinu, DEU pro němčinu ...).<br>Výchozí jazyk je Eng a -jazyk je volitelný pro výchozí jazyk nastavený ./lib/lang.py.<br>Kódy ISO-639-1 2 jsou také podporovány.

### Příklad vlastního modelu nahrávání zip

(Musí to být soubor .zip obsahující povinné soubory modelu.

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Okna**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**: Cesta k`model_name.zip`soubor,
        které musí obsahovat (podle motoru TTS) všechny povinné soubory<br>(viz ./lib/models.py).

### Pro podrobný průvodce se seznamem všech parametrů

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Okna**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Nebo pro všechny OS**
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

NOTE: in gradio/gui mode, to cancel a running conversion, just click on the [X]z komponenty ebook nahrát komponentu.

### Pomocí Docker

Můžete také použít Docker ke spuštění ebook do převodníku Audioknic. 
Tato metoda zajišťuje konzistenci v různých prostředích a zjednodušuje nastavení.

#### Spuštění kontejneru Docker

Chcete -li spustit kontejner Docker a spusťte rozhraní Gradio, použijte následující příkaz:

\-Cun pouze s CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run s GPU Speedup (pouze kompatibilní NVIDIA)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Budování kontejneru Docker

-   Obrázek Docker můžete vytvořit s příkazem:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Tento příkaz spustí rozhraní Gradio na portu 7860. (LocalHost: 7860)

-   Další možnosti přidejte parametr`--help`

## Umístění souborů kontejneru Docker

Všechny ebook2audiobooky budou mít základní dir`/home/user/app/`Například:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker bezhlavý průvodce

nejprve za tah nejnovějších s ukotvením

```bash
docker pull athomasson2/ebook2audiobook
```

-   Než to spustíte, musíte vytvořit dir s názvem „vstupní forma“ ve svém aktuálním dir
    který bude propojen, zde můžete dát své vstupní soubory pro obrázek Dockera vidět

```bash
mkdir input-folder && mkdir Audiobooks
```

-   V příkazu níže swap**Your_input_file.txt**s názvem vašeho vstupního souboru

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   A to by mělo být!
-   Výstupní zvukové knihy budou nalezeny ve složce audioknic, která bude také umístěna
    Ve vašem místním dir jste spustili tento příkaz Docker

## Chcete -li získat příkaz nápovědy pro další parametry, tento program, můžete to spustit

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

a to bude vystupovat[Nápověda výstup příkazu](#help-command-output)

### Docker Compose

Tento projekt používá Compose Docker ke spuštění lokálně. Podpora GPU můžete povolit nebo deaktivovat 
Nastavením buď`*gpu-enabled`nebo`*gpu-disabled`v`docker-compose.yml`

#### Kroky ke spuštění

1.  **Klonovat úložiště**(pokud jste to ještě neučinili):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Nastavit podporu GPU (ve výchozím nastavení deaktivováno)**Chcete -li povolit podporu GPU, upravte`docker-compose.yml`a změnit se`*gpu-disabled`na`*gpu-enabled`
3.  **Spusťte službu:**
    ```bash
    docker-compose up -d
    ```
4.  **Přístup ke službě:**Služba bude k dispozici na adrese http&#x3A; // localhost: 7860.

### Rozhraní GUI Docker GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Pronájem GPU

Nemáte hardware k jeho spuštění nebo si chcete pronajmout GPU?

#### Můžete duplikovat prostor Hugginface a pronajmout si GPU za přibližně 0,40 $ za hodinu

[Demo objímání prostoru](#huggingface-space-demo)

#### Nebo můžete zkusit používat Google Colab zdarma!

(Uvědomte si, že to bude vyčarovat po trochu, že si nebudete moci pohrávat s Google Colab)[Zdarma Google Colab](#free-google-colab)

## Běžné problémy Docker

-   Docker gets stuck downloading Fine-Tuned models.
    (This does not happen for every computer but some appear to run into this issue)
    Disabling the progress bar appears to fix the issue,
    as discussed [Tady v #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Příklad přidání této opravy do`docker run`příkaz

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Jemně vyladěné modely TTS

S tímto repo si můžete snadno vyladit svůj vlastní model XTTS[Xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

Pokud si chcete snadno pronajmout GPU, můžete také duplikovat tento objímání[Xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Prostor, který můžete použít k snadno zrušení dat tréninku[Denoise objasňování prostoru](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Jemně vyladěná kolekce TTS

Chcete-li najít naši sbírku již jemně vyladěných modelů TTS,
návštěva[tento objímající obličej](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)U vlastního modelu XTTS je povinný zvukový klip ref hlasového odkazu:

## Demos

**Deštivý den hlas**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Podporované formáty ebook

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Nejlepší výsledky**:`.epub`nebo`.mobi`Pro automatickou detekci kapitol

## Výstup

-   Vytváří a`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(nastavit soubor ./lib/conf.py) s metadatami a kapitolami.
-   **Příklad**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Běžné problémy:

-   CPU je pomalý (lepší na serveru SMP CPU), zatímco GPU NVIDIA může mít převod téměř v reálném čase.[Diskuse o tom](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Pro rychlejší vícejazyčné generace bych navrhl své druhé[Projekt, který používá Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)místo toho
    (Nicméně nemá klonování hlasu nulového výstřelu a je to hlasy kvality Siri, ale na CPU je to mnohem rychlejší).
-   „Mám problémy s závislostí“ - stačí používat Docker, jeho plně obsažený a má bezhlavý režim,
     přidat`--help`Parametr na konci příkazu Docker Run pro více informací.
-   "Dostanu zkrácený zvukový problém!" - prosím, udělejte to problém,
     Neřekneme každý jazyk a potřebujeme radit od uživatelů, abychom doladili logiku rozdělení věty.😊

## S čím potřebuji pomoc! 🙌

## [Úplný seznam věcí naleznete zde](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Jakákoli pomoc od lidí, kteří mluví některým z podporovaných jazyků, aby pomohli se správnými metodami rozdělení věty
-   Potenciálně vytvářet průvodce README pro více jazyků (protože jediným jazykem, který znám, je angličtina 😔)

## Zvláštní poděkování

-   **Vaření TTS**:[Coqui tts gitHub](https://github.com/idiap/coqui-ai-TTS)
-   **Ráže**:[Web kalibru](https://calibre-ebook.com)
-   **Ffmpeg**:[FFMPEG Web](https://ffmpeg.org)
-   [@ShakenBake15 pro metodu lepší ukládání kapitol](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy V1.0](legacy/v1.0)

Kód si můžete prohlédnout[zde](legacy/v1.0).

## Připojte se k našemu serveru!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
