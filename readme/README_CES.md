📚 Ebook2audiObook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
Převodník CPU/GPU z e -knih na audioknihy s kapitolami a metadatami <br/>
Použití ráže, FFMPEG, XTTSV2, FAIRSEQ a další. Podporuje hlasové klonování a +1110 jazyků! [! Důležité]
** Tento nástroj je určen k použití pouze s EN-DRM, pouze legálně získanými e-knihami. ** <br>
Autoři neodpovídají za zneužití tohoto softwaru ani žádné výsledné právní důsledky. <br>
Tento nástroj použijte zodpovědně a v souladu se všemi platnými zákony. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko-fi-f16061?Style=Fothe-the-badge&logo=ko-fi&logolor=white)] (https: // ko-fi .com/Athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_web_gui] (Aktiva/demo_web_gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العربية (arabština)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
Zho [中文 (čínština)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
SWE [Svenska (švédská)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
FAS [فارسی (Persian)] (./ ReadMe/Readme_fa.md)


## Table of Contents
[Ebook2audiObook] (#-Ebook2audiObook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Funkce] (#funkce)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Rozhraní GUI Docker]] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Demo Huggingface Space] (#objímající povrch-mezera-demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Zdarma Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Pre-Made Audio Demos] (#Demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Podporované jazyky] (#podporované jazyky)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Požadavky] (#hardware-požadované)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Instalační pokyny] (#Instalační instrukce)
- [Output](#output)
- [Common Issues](#common-issues)
[Použití] (#Spuštění-gradio-web-rozhraní)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Spuštění webového rozhraní Gradio] (#Spuštění-gradio-interface)


[Základní bezhlavé použití] (#Basic-Usage)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Použití modelu bez hlav XTTS] (#Příklad-Of-Custom-Model-Zip-Upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Pronájem GPU] (#pronájem a-gpu)


[Výstup příkazu nápovědy] (#nápověda-command-output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Jemně vyladěné modely TTS] (#jemně doladěné-tts-modely)


[Pro sběr jemně doladěných modelů TTS] (#jemně tuned-TTS-Collection)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#běh-the-docker-Container)
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
[Umístění souborů kontejneru Docker] (#Docker-Container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Obyčejné problémy Docker] (#Common-Docker-Issues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Podporované formáty e-knih] (#podporované-ebook-formáty)


[Výstup] (#výstup)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Obyčejné problémy] (#Common-Places)


[Zvláštní poděkování] (#Special-Tanks)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Funkce
```bash
📖 Převádí e -knihy do textového formátu s Caliber. 📚 Rozdělí ebook do kapitol pro organizovaný zvuk. 🎙 Vysoce kvalitní text-to-řeč s [coqui xttsv2] (https://huggingface.co/coqui/xtts-v2) a [fairSeq] (https://github.com/facebookresearch/fairseq/tree/main/ Příklady/MMS) (a další). 🗣 Volitelné klonování hlasu s vlastním hlasovým souborem. 🌍 Podporuje jazyky +1110 (ve výchozím nastavení angličtina). [Seznam podporovaných jazyků] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥 Navrženo pro běh na 4 GB RAM. [Demo Huggingface Space] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [Objímající tvář] (https://img.shields.io/badge/hugging%20facespaces-wellow?Style=Fothe-the-badge&logo=huggingface)] (https://huggingface.co/spaces/drewthomasson /ebook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Objímání prostoru probíhá na volné úrovni CPU, takže očekávejte velmi pomalý nebo časový limit lol, prostě to nedávejte obří soubory, je všechno
   - **Windows**
     ```bash
Nejlepší je duplikovat prostor nebo běžet lokálně. Zdarma Google Colab
     ```
[! [Zdarma Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)] (https://colab.research.google.com/github/drewthomasson/ebook2audiook/blob/ Hlavní/notebooky/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Podporované jazyky
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arabština (ara) **

> [!IMPORTANT]
** Číňan (Zho) **
to let the web page reconnect to the new connection socket.**

** Czech (CES) **
   - **Linux/MacOS**:
     ```bash
** Croatian (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Holanďan (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Angličtina (Eng) **
     ```
     
** Francouzština (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Němci (DEU) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Maďarský (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** ITALIAN (ITA) **
     ```
   - **Windows**
** Japonština (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Korean (KOR) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Polská (pol) **


** Portugalština (por) **
   - **Linux/MacOS**
     ```bash
** Russian (RUS) **
     ```
   - **Windows**
** Španělština (lázně) **
     .\ebook2audiobook.cmd --help
     ```
** Turecké (tur) **
    ```python
     app.py --help
** Vietnamci (vie) **

<a id="help-command-output"></a>
[** +1100 jazyky prostřednictvím FairSeq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Hardwarové požadavky
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4 GB RAM minimálně, doporučeno 8 GB
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualizace je povolena, pokud běží na Windows (pouze Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (doporučeno), MPS (dosud není optimalizován a může být pomalejší než CPU) kompatibilní

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Předtím, než na kartu Otevřené a uzavřené problémy pečlivě zveřejníte instalaci nebo vydání chyby, <br>
Ujistěte se, že váš problém již neexistuje. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Chybějící strukturu standardů, jako je to, co je kapitola, odstavec, předmluva atd. <br>
Nejprve byste měli odstranit ručně jakýkoli text, který nechcete být převedeni ve zvuku. **

Instalační pokyny

** Clone Repo **
  --headless            Run the script in headless mode
Spuštění webového rozhraní Gradio
  --ebooks_dir EBOOKS_DIR
** Spusťte ebook2audiobook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/MacOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Otevřete webovou aplikaci **: Kliknutím na adresu URL poskytnuté v terminálu získáte přístup k webové aplikaci a převeďte elektronické knihy. ** Pro veřejný odkaz **:
`Python App.py -Share` (všechny os)
`./ebook2audiobook.sh -Share` (Linux/MacOS)
`eBook2audiObook.cmd - -Share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[! Důležité]
** Pokud je skript zastaven a znovu spuštěn, musíte obnovit rozhraní Gradio GUI <br>
Aby se webová stránka znovu připojila k nové zásuvce připojení. **
                        (Optional) Fine tuned model path. Default is builtin model.
Základní použití
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/MacOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-eBook] **: Cesta do souboru elektronické knihy. ** [-hlas] **: Path cloningové cesty hlasového klonování (volitelné). ** [-jazyk] **: Kód jazyka v ISO-639-3 (tj.: ITA pro italštinu, Eng pro angličtinu, deu pro němčinu ...). <br>
Výchozí jazyk je Eng a -jazyk je volitelný pro výchozí jazyk nastavený ./lib/lang.py. <br>
Kódy ISO-639-1 2 jsou také podporovány. Příklad vlastního modelu nahrávání zip
  --repetition_penalty REPETITION_PENALTY
(Musí to být soubor .zip obsahující povinné soubory modelu.
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/MacOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custom_model_path> **: cesta k `souboru model_name.zip`,
    které musí obsahovat (podle motoru TTS) všechny povinné soubory <br>
    (viz ./lib/models.py). Pro podrobný průvodce se seznamem všech parametrů
  --output_dir OUTPUT_DIR
** Linux/MacOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** nebo pro všechny os **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "help-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
POZNÁMKA: V režimu Gradio/GUI zrušit převod běžícího převodu stačí kliknout na [x] ze komponenty ebook upload. Pomocí Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Můžete také použít Docker ke spuštění ebook do převodníku Audioknic. Tato metoda zajišťuje konzistenci v různých prostředích a zjednodušuje nastavení. Spuštění kontejneru Docker

Chcete -li spustit kontejner Docker a spusťte rozhraní Gradio, použijte následující příkaz:

### Using Docker
-Cun pouze s CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Budování kontejneru Docker

Obrázek Docker můžete vytvořit s příkazem:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Tento příkaz spustí rozhraní Gradio na portu 7860. (LocalHost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Další možnosti přidejte parametr `-Help`
```


Všechny eBook2audiObooks budou mít základní dir `/home/uživatel/app/`
Například:
`tmp` =`/home/user/app/tmp`
`Audioknics` =`/home/user/app/audiokooks`
```
Docker bezhlavý průvodce
- For more options add the parameter `--help`


## Docker container file locations
Než to spustíte, musíte vytvořit dir s názvem „vstupní forma“ ve svém aktuálním dir
který bude propojen, zde můžete dát své vstupní soubory pro obrázek Dockera vidět
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
A to by mělo být! Výstupní zvukové knihy budou nalezeny ve složce audioknic, která bude také umístěna
Ve vašem místním dir jste spustili tento příkaz Docker
docker pull athomasson2/ebook2audiobook
Chcete -li získat příkaz nápovědy pro další parametry, tento program, můžete to spustit
- Before you do run this you need to create a dir named "input-folder" in your current dir
a to bude vystupovat 
[Výstup příkazu nápovědy] (#nápověda-command-output)
mkdir input-folder && mkdir Audiobooks
Docker Compose
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Tento projekt používá Compose Docker ke spuštění lokálně. Podpora GPU můžete povolit nebo deaktivovat 
Nastavením buď `*GPU-ENABLED 'nebo`*GPU-disabled` v `Docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Kroky ke spuštění
    athomasson2/ebook2audiobook \
** Klonejte úložiště ** (pokud jste dosud neučinili):
```
- And that should be it! 
** Nastavení podpory GPU (ve výchozím nastavení deaktivováno) **
Chcete-li povolit podporu GPU, upravte `docker-compose.yml` a změňte`*gpu-disabled` na `*gpu-enabled```


** Začněte službu: **

```bash
** Přístup ke službě: **

```
! [Demo_web_gui] (Aktiva/demo_web_gui.gif)
[Help command output](#help-command-output)


Nemáte hardware k jeho spuštění nebo si chcete pronajmout GPU? Můžete duplikovat prostor Hugginface a pronajmout si GPU za přibližně 0,40 $ za hodinu
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Demo Huggingface Space] (#objímající povrch-mezera-demo)


[Zdarma Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Běžné problémy Docker
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker uvízne stahování jemně doladěných modelů. (To se nestane pro každý počítač, ale zdá se, že někteří se do tohoto problému narazí)
Zdá se, že deaktivace lišty pro pokrok vyřeší problém,
Jak je uvedeno [zde v #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Příklad přidání této opravy do příkazu „Docker Run“
3. **Start the service:**
Jemně vyladěné modely TTS
    docker-compose up -d
S tímto repo si můžete snadno vyladit svůj vlastní model XTTS
[xtts-finetune-webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[xtts-finetune-webui-pace] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Prostor, který můžete použít k snadno zrušení dat tréninku
[Denoise-Huggingface-Space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Jemně vyladěná kolekce TTS
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Chcete-li najít naši sbírku již jemně vyladěných modelů TTS,


## Renting a GPU
Demos
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** hlas deštivého dne **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** Hlas David Attenborough **


Podporované formáty ebook
- Docker gets stuck downloading Fine-Tuned models.
"
"
`.Snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Nejlepší výsledky **: `.epub` nebo` .mobi` pro automatickou detekci kapitol
    -p 7860:7860 athomasson2/ebook2audiobook
Výstup


! [Příklad] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Běžné problémy:

CPU je pomalý (lepší na serveru SMP CPU), zatímco GPU NVIDIA může mít převod téměř v reálném čase. [Diskuse o tom] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#DiscussionComment-10879846)
Pro rychlejší vícejazyčné generace bych navrhl své druhé

(Nicméně nemá klonování hlasu nulového výstřelu a je to hlasy kvality Siri, ale na CPU je to mnohem rychlejší). „Mám problémy s závislostí“ - stačí používat Docker, jeho plně obsažený a má bezhlavý režim,
 Přidat `-HELP` Parametr na konci příkazu Docker Run pro více informací. "Dostanu zkrácený zvukový problém!" - prosím, udělejte to problém,

### Fine Tuned TTS Collection
S čím potřebuji pomoc! 🙌
[Úplný seznam věcí naleznete zde] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potenciálně vytvářet průvodce README pro více jazyků (protože jediný jazyk, který znám, je angličtina 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui TTS **: [Coqui TTS GitHub] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** FFMPEG **: [FFMPEG Web] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy V1.0] (Legacy/V1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Můžete zobrazit kód [zde] (Legacy/V1.0). Připojte se k našemu serveru! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)