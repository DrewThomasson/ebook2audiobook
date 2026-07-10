# 📚 ebook2audiobook (E2A)
Kibadilishaji cha CPU/GPU kutoka E-Kitabu hadi kitabu cha sauti chenye sura na metadata<br/>
kwa kutumia injini za hali ya juu za TTS na mengi zaidi.<br/>
Kinaunga mkono unakili wa sauti na lugha 1158!
> [!IMPORTANT]
**Zana hii imekusudiwa kutumika tu na vitabu pepe visivyo na DRM, vilivyopatikana kihalali.** <br>
Waandishi hawawajibikii matumizi mabaya yoyote ya programu hii au matokeo yoyote ya kisheria yanayotokana nayo. <br>
Tumia zana hii kwa uwajibikaji na kwa kufuata sheria zote zinazotumika.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Asante kwa kuwaunga mkono wasanidi wa ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Endesha kwa ndani

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Endesha kwa Mbali
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Kiolesura cha GUI
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Bofya ili kuona picha za GUI ya Wavuti</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Onyesho

**Onyesho la Sauti Mpya ya Chaguo-msingi**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Maonyesho Zaidi</summary>

**Sauti ya ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Sauti ya Siku ya Mvua**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Sauti ya Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Sauti ya David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Mfano**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Jedwali la Yaliyomo
- [ebook2audiobook](#-ebook2audiobook)
- [Vipengele](#features)
- [Kiolesura cha GUI](#gui-interface)
- [Onyesho](#demos)
- [Lugha Zinazoungwa Mkono](#supported-languages)
- [Mahitaji ya Chini](#hardware-requirements)
- [Matumizi](#instructions)
  - [Endesha kwa Ndani](#instructions)
    - [Kuzindua Kiolesura cha Wavuti cha Gradio](#instructions)
    - [Matumizi ya Msingi ya Headless](#basic-usage)
    - [Matumizi ya Modeli Maalum ya XTTS ya Headless](#example-of-custom-model-zip-upload)
    - [Matokeo ya amri ya usaidizi](#help-command-output)
  - [Endesha kwa Mbali](#run-remotely)
  - [Docker](#docker)
    - [Hatua za Kuendesha](#docker)
  
- [Sauti Zilizopambwa](#cloned-voices)
- [Modeli za TTS Zilizoboreshwa](#fine-tuned-tts-models)
  - [Mkusanyiko wa Modeli za TTS Zilizoboreshwa](#fine-tuned-tts-collection)
  - [Funza XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Miundo ya eBook Inayoungwa Mkono](#supported-ebook-formats)
- [Miundo ya Matokeo](#output-and-process-formats)
- [Rudi kwa Toleo la zamani](#reverting-to-older-versions)
- [Matatizo ya Kawaida](#common-issues)
- [Shukrani za Pekee](#special-thanks)
- [Jedwali la Yaliyomo](#table-of-contents)


## Vipengele
- 🔧 **Injini za TTS zinazoungwa mkono**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Badilisha miundo mingi ya faili**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Eneo la Maandishi** ili kubadilisha moja kwa moja maandishi mafupi kuwa sauti
- 🔍 **Uchanganuzi wa OCR** kwa faili zenye kurasa za maandishi kama picha
- 🔊 **Maandishi-kwa-usemi ya ubora wa juu**, kutoka karibu wakati halisi hadi sauti karibu halisi
- 🗣️ **Unakili wa sauti wa hiari** kwa kutumia faili yako mwenyewe ya sauti
- 🌐 **Inaunga mkono lugha 1158** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Rafiki kwa rasilimali ndogo** — inaendeshwa kwa **2 GB RAM / 1 GB VRAM (kima cha chini)**
- 🎵 **Miundo ya matokeo ya kitabu cha sauti**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Lebo za SML zinaungwa mkono** — udhibiti wa kina wa mapumziko, vituo, ubadilishaji wa sauti na zaidi ([see below](#sml-tags-available))
- 🧩 **Modeli maalum ya hiari** kwa kutumia modeli yako uliyofunza mwenyewe (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modeli za mipangilio iliyowekwa awali zilizoboreshwa** zilizofunzwa na Timu ya E2A<br/>
     <i>(Wasiliana nasi ikiwa unahitaji modeli za ziada zilizoboreshwa, au ikiwa ungependa kushiriki zako kwenye orodha rasmi ya mipangilio iliyowekwa awali)</i>


##  Mahitaji ya Maunzi
- RAM 2GB chini, 8GB inapendekezwa.
- VRAM 1GB chini, 4GB inapendekezwa.
- Uboreshaji umewezeshwa ikiwa unaendeshwa kwenye windows (Docker pekee).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU ya Apple Silicon)

*<i> Injini za kisasa za TTS ni polepole sana kwenye CPU, kwa hivyo tumia TTS za ubora wa chini kama YourTTS, Tacotron2 n.k.</i>

## Lugha Zinazoungwa Mkono
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 lugha na lahaja hapa**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Miundo ya eBook Inayoungwa Mkono
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Matokeo bora**: `.epub` au `.mobi` kwa utambuzi wa sura kiotomatiki

## Miundo ya Matokeo na uchakataji
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Muundo wa uchakataji unaweza kubadilishwa katika lib/conf.py

## Lebo za SML zinazopatikana
- `[break]` — ukimya (anuwai nasibu **0.3–0.6 sec.**)
- `[pause]` — ukimya (anuwai nasibu **1.0–1.6 sec.**)
- `[pause:N]` — pumziko maalum (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — badilisha sauti kutoka kwa sauti ya chaguo-msingi au iliyochaguliwa kutoka GUI/CLI

**Angalia repo yetu nyingine iliyojikita katika kuongeza SML kiotomatiki katika eBook yako -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Kabla ya kutuma tatizo la usakinishaji au hitilafu, tafuta kwa makini katika KICHUPO cha matatizo yaliyofunguliwa na yaliyofungwa<br>
ili kuhakikisha tatizo lako halipo tayari.**

>[!NOTE]
**Muundo wa EPUB hauna muundo wowote wa kawaida kama vile sura ni nini, aya, dibaji n.k.<br>
Kwa hivyo unapaswa kwanza kuondoa kwa mkono maandishi yoyote ambayo hutaki kubadilishwa kuwa sauti.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Sakinisha / Endesha ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Kizinduzi cha Mac**  
     Bofya mara mbili `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Kumbuka kwa watumiaji wa Windows: scoop husakinishwa ili kusakinisha programu zinazokosekana bila ruhusa za msimamizi.</i>
   
1. **Fungua Programu ya Wavuti**: Bofya URL iliyotolewa kwenye terminal ili kufikia programu ya wavuti na kubadilisha eBooks. `http://localhost:7860/`
2. **Kwa Kiungo cha Umma**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Ikiwa hati itasimamishwa na kuendeshwa tena, unahitaji kuonyesha upya kiolesura chako cha GUI cha gradio<br>
ili kuruhusu ukurasa wa wavuti uunganishe upya kwa soketi mpya ya muunganisho.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Njia ya faili yako ya eBook
  - **[--voice]**: Njia ya faili ya unakili wa sauti (hiari)
  - **[--language]**: Msimbo wa lugha katika ISO-639-3 (yaani: ita kwa Kiitaliano, eng kwa Kiingereza, deu kwa Kijerumani...).<br>
    Lugha ya chaguo-msingi ni eng na --language ni hiari kwa lugha ya chaguo-msingi iliyowekwa katika ./lib/lang.py.<br>
    Misimbo ya herufi 2 ya ISO-639-1 pia inaungwa mkono.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTSv2: config.json, model.pth, vocab.json and ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Note: the ref.wav of your custom model is always the voice selected for the conversion</i>
     
- **<custom_model_path>**: Njia ya faili ya `model_name.zip`,
      ambayo lazima iwe na (kulingana na injini ya tts) faili zote za lazima<br>
      (angalia ./lib/models.py).

### For Detailed Guide with list of all Parameters to use
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Or for all OS**
    ```python
     app.py --help
    ```

<a id="help-command-output"></a>
```bash
usage: app.py [-h] [--session SESSION] [--share] [--headless] [--ebook EBOOK] [--ebooks_dir EBOOKS_DIR]
              [--language LANGUAGE] [--voice VOICE] [--voice_map VOICE_MAP] [--device {CPU,CUDA,MPS,ROCM,XPU,JETSON}]
              [--tts_engine {XTTS,BARK,VITS,FAIRSEQ,TACOTRON,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}]
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED] [--output_format OUTPUT_FORMAT]
              [--output_channel OUTPUT_CHANNEL] [--temperature TEMPERATURE] [--length_penalty LENGTH_PENALTY]
              [--num_beams NUM_BEAMS] [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--text_temp TEXT_TEMP] [--waveform_temp WAVEFORM_TEMP]
              [--output_dir OUTPUT_DIR] [--version]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --session SESSION     Session to resume the conversion in case of interruption, crash,
                            or reuse of custom models and custom cloning voices.

**** The following option is for gradio/gui mode only:
  --share               (Optional) Enable a public shareable Gradio link.

**** The following options are for --headless mode only:
  --headless            Run the script in headless mode
  --ebook EBOOK         Path to the ebook file for conversion. Cannot be used when --ebooks_dir is present.
  --ebooks_dir EBOOKS_DIR
                        Relative or absolute path of the directory containing the files to convert.
                            Cannot be used when --ebook is present.
  --text TEXT           Raw text for conversion. Cannot be used when --ebook or --ebooks_dir is present.
  --language LANGUAGE   Language of the e-book. Default language is set
                            in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py

optional parameters:
  --translate ISO3      (Optional) Translate ebook to a target language (ISO 639-3 code, e.g. eng, fra, deu) before TTS synthesis.
                            Uses argostranslate. The target language becomes the effective TTS language for the run.
                            A copy of the source ebook is made with the _<iso3> suffix so translated and non-translated
                            outputs stay isolated (independent process folder, audio chunks, and final file).
  --voice VOICE         (Optional) Path to the voice cloning file for TTS engine.
                            Uses the default voice if not present.
  --voice_map VOICE_MAP
                        (Optional, --ebooks_dir only) Path to a JSON file mapping ebook path -> voice path.
                            Each entry overrides --voice for that specific ebook. Missing/null entries fall back to --voice.
                            Keys may be absolute paths or basenames. Example:
                            {"book1.epub": "/voices/eng/adult/female/alice.wav", "/abs/path/book2.epub": null}
  --device {CPU,CUDA,MPS,ROCM,XPU,JETSON}
                        (Optional) Processor unit type for the conversion.
                            Default is set in ./lib/conf.py if not present. Fall back to CPU if CUDA or MPS is not available.
  --tts_engine {XTTS,BARK,VITS,FAIRSEQ,TACOTRON,YOURTTS,xtts,bark,vits,fairseq,tacotron,yourtts}
                        (Optional) Preferred TTS engine (available are: ['XTTS', 'BARK', 'VITS', 'FAIRSEQ', 'TACOTRON', 'YOURTTS', 'xtts', 'bark', 'vits', 'fairseq', 'tacotron', 'yourtts'].
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
                        (Optional) Path to the custom model zip file cntaining mandatory model files.
                            Please refer to ./lib/models.py
  --fine_tuned FINE_TUNED
                        (Optional) Fine tuned model path. Default is builtin model.
  --output_format OUTPUT_FORMAT
                        (Optional) Output audio format. Default is m4b set in ./lib/conf.py
  --output_channel OUTPUT_CHANNEL
                        (Optional) Output audio channel. Default is mono set in ./lib/conf.py
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
                            Lower values mean more likely outputs and increased audio generation speed. Default to config.json model.
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation.
                            Default to config.json model.
  --enable_text_splitting
                        (xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient.
                            Default to config.json model.
  --text_temp TEXT_TEMP
                        (bark only, optional) Text Temperature for the model.
                            Default to config.json model.
  --waveform_temp WAVEFORM_TEMP
                        (bark only, optional) Waveform Temperature for the model.
                            Default to config.json model.
  --output_dir OUTPUT_DIR
                        (Optional) Path to the output directory. Default is set in ./lib/conf.py
  --version             Show the version of the script and exit

Example usage:
Windows:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file' --language eng
Linux/Mac:
    Gradio/GUI:
    ./ebook2audiobook.command
    Headless mode:
    ./ebook2audiobook.command --headless --ebook '/path/to/file' --language eng

SML tags available:
	[break] — silence (random range **0.3–0.6 sec.**)
	[pause] — silence (random range **1.0–1.6 sec.**)
	[pause:N] — fixed pause (**N sec.**)
	[voice:/path/to/voice/file]...[/voice] — switch voice from default or selected voice from GUI/CLI

```

KUMBUKA: katika hali ya gradio/gui, ili kughairi ubadilishaji unaoendelea, bonyeza tu [X] kutoka kwa kipengele cha upakiaji wa eBook.
KIDOKEZO: ikiwa inahitaji pumziko zaidi, ongeza '[pause:3]' kwa sekunde 3 n.k.

### Docker
1. **Clone the Repository**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Build the container**
```bash
    Windows:
        Docker:
            ebook2audiobook.cmd --script_mode build_docker
        Docker Compose:
            ebook2audiobook.cmd --script_mode build_docker --docker_mode compose
        Podman Compose:
            ebook2audiobook.cmd --script_mode build_docker --docker_mode podman
    Linux/Mac
        Docker:
            ./ebook2audiobook.command --script_mode build_docker
        Docker Compose
            ./ebook2audiobook.command --script_mode build_docker --docker_mode compose
        Podman Compose:
            ./ebook2audiobook.command --script_mode build_docker --docker_mode podman
```
4. **Run the Container:**
```bash
Docker run image:
    Gradio/GUI:
        CPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" --runtime nvidia  --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[51/60/61 etc...]
    Headless mode:
        CPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
Docker Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 docker compose --profile gpu up --no-log-prefix
        Run Headless mode:
               DEVICE_TAG=cu128 docker compose --profile gpu run --rm ebook2audiobook --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
Podman Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile gpu up
        Run Headless mode:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile gpu run --rm ebook2audiobook-gpu --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
```
- NOTE: MPS is not exposed in docker so CPU must be used

## Sauti Zilizopambwa
Unaweza kupakia sauti yoyote ya sauti katika muundo wowote wa sauti unaotumika, muda unaofaa ni karibu 1 hadi 5 mn.
Haijalishi ikiwa rekodi ina mandharinyuma ya kelele au muziki unaocheza juu yake — E2A itakusafishia sauti.

Orodha ya sauti zilizojengwa ndani ni hasa kwa Kiingereza. Ikiwa unahitaji sauti katika lugha zingine kuwa rasmi
imeongezwa kwenye orodha, tafadhali wasiliana nasi na tutayaweka baada ya kutathminiwa.

## Modeli za TTS Zilizoboreshwa (fine-tuned)
#### Boresha modeli yako mwenyewe ya XTTSv2

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Ondoa kelele kwenye data ya mafunzo

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Mkusanyiko wa Modeli za TTS Zilizoboreshwa

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Kwa modeli maalum ya XTTSv2, klipu ya sauti ya marejeleo ya sauti ni ya lazima:

## Ubinafsishaji wako mwenyewe wa Ebook2Audiobook
Uko huru kurekebisha libs/conf.py ili kuongeza au kuondoa mipangilio unayotaka. Ikiwa unapanga kufanya hivyo, fanya tu
nakala ya conf.py asili ili kila sasisho la ebook2audiobook utahifadhi conf.py yako iliyorekebishwa na kuweka
tena ile asili. Lazima upange mchakato huo huo kwa models.py. Ikiwa unataka kuifanya modeli yako maalum
kuwa modeli rasmi iliyoboreshwa ya ebook2audiobook, tafadhali wasiliana nasi na tutaiongeza kwenye orodha ya mipangilio iliyowekwa awali.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Matatizo ya Kawaida:
- GPU yangu ya NVIDIA/ROCm/XPU/MPS haitambuliki?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU ni polepole (bora kwenye CPU smp ya seva) huku GPU ikiweza kuwa na ubadilishaji wa karibu wakati halisi.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Hata hivyo haina unakili wa sauti wa zero-shot, na ni sauti za ubora wa Siri, lakini ni haraka zaidi kwenye cpu).
- "Nina matatizo ya utegemezi" - Tumia tu docker, imejitosheleza kabisa na ina hali ya headless,
   ongeza kigezo `--help` mwishoni mwa amri ya docker run kwa maelezo zaidi.
- "Ninapata tatizo la sauti iliyokatwa!" - TAFADHALI FUNGUA ISSUE KUHUSU HILI,
   hatuzungumzi kila lugha na tunahitaji ushauri kutoka kwa watumiaji ili kuboresha mantiki ya kugawanya sentensi.😊

## ***** RAMANI YA BARABARA *****
- Vipengele vyote vimefunguliwa kwa Michango ya umma ⭐
- Msaada wowote kutoka kwa watu wanaozungumza lugha yoyote inayoungwa mkono ili kutusaidia kuboresha modeli ⭐
- [x] Hakiki Vizuizi/Sura kabla ya kuanza ubadilishaji
- [ ] Hariri kwa sentensi iliyobadilishwa kwa mabadiliko ya maandishi ya kina
- [x] Ujumuishaji wa lebo za SML kwa sauti, pumziko, mapumziko, na mabadiliko zaidi 
- [x] Taarifa za vigezo -h -help katika lugha tofauti
- [x] Uchanganuzi wa OCR kwa PDF / JPG / BMP / PNG / TIFF
- [x] Folda ya Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Kufanya ugawanyaji wa maandishi ya Kichina usigawanye maneno na kuboresha muda wa mapumziko [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Daftari la Kaggle
- [x] Daftari la Google Colab
- [ ] Ujumuishaji wa Audiobookshelf
- [ ] [Tengeneza programu ya IOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Tengeneza programu ya android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Chaguo za Ziada
- [x] Chaguo la Tafsiri ya eBook
- [x] Chaguo za muundo wa matokeo
- [x] Folda ya eBook ya kundi
- [x] Ubadilishaji wa uchakataji-nyingi
- [x] Ubadilishaji wa folda ya eBook ya kundi
- [x] Utambuzi wa Kifaa cha GPU
- [x] Ondoa kelele kwenye sauti yoyote ya marejeleo kwa upakiaji wa unakili wa sauti,
- [x] Upakiaji wa modeli maalum (XTTSv2 pekee kwa sasa. zaidi kwa ombi)
- [ ] Ongeza modeli ya lugha ya Kireno cha Ulaya kwa angalau xttsv2, fairseq, vits, piper (msaada unakaribishwa)
- [ ] Ongeza modeli ya lugha ya Kisindhi kwa angalau xttsv2, fairseq, vits, piper (msaada unakaribishwa)

#### Injini za TTS
- [x] XTTSv2
- [x] ngano
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Usipoteze muda wan
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] msemo wa samaki (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] sanduku la mazungumzo (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Kanda (https://github.com/Zyphra/Zonos)
- [ ] Mtindo-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Tafsiri ya Readme
- [ ] Arabic (ara)
- [ ] Chinese (zho)
- [x] English (eng)
- [ ] Spanish (spa)
- [ ] French (fra)
- [ ] German (deu)
- [ ] Italian (ita)
- [ ] Portuguese (por)
- [ ] Polish (pol)
- [ ] Turkish (tur)
- [ ] Russian (rus)
- [ ] Dutch (nld)
- [ ] Czech (ces)
- [ ] Japanese (jpn)
- [ ] Hindi (hin)
- [ ] Bengali (ben)
- [ ] Hungarian (hun)
- [ ] Korean (kor)
- [ ] Vietnamese (vie)
- [ ] Swedish (swe)
- [ ] Persian (fas)
- [ ] Yoruba (yor)
- [ ] Swahili (swa)
- [ ] Indonesian (ind)
- [ ] Slovak (slk)
- [ ] Croatian (hrv)   

#### 🐍 Uoanifu wa OS
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Ziada ya Kupita Kiasi kwa kufunza modeli na mengineyo (Modeli zote za Coqui-tts zinazoungwa mkono na piper-tts katika amri moja rahisi) 
- Kwa maelezo kuhusu hili @DrewThomasson, kwa sasa anafanyia kazi maendeleo ya hili, [repo inayoendelea hapa](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Tengeneza gui ya mafunzo rahisi kutumia kwa modeli zote za coqui-tts katika maagizo ya mafunzo ya muundo wa ljspeech [hapa kutoka coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Maelezo ya usanifishaji wa Msimbo wa Python kwa wachangiaji
- hakuna mstari tupu kati ya msimbo, isipokuwa kati ya kazi na madarasa.
- nukuu moja inatumika kwa funguo zote isipokuwa kwa dict() na json. dict['key'] huitwa kila wakati kwa nukuu moja
- mwingizo wa nafasi 4, sio tab hata kidogo
- uchapaji mkali kwa kazi zote na tamko la hoja zake na thamani za kurudi
- hakuna nafasi kati ya hoja na uchapaji wake, hakuna nafasi kati ya kazi, "->" na thamani ya kurudi

Mfano:

```python
import json
from typing import Optional

def get_user(user_id:int, users:list[dict])->Optional[dict]:
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def summarize(user:dict)->str:
    return f"User {user['name']} is {'active' if user['is_active'] else 'inactive'}."

def to_json(user:dict)->str:
    return json.dumps({"id": user['id'], "name": user['name'], "email": user['email']})

users:list = [
    dict(id=1, name="alice", email="alice@example.com", role="admin", is_active=True),
    dict(id=2, name="bob", email="bob@example.com", role="editor", is_active=False),
    dict(id=3, name="carol", email="carol@example.com", role="viewer", is_active=True),
]
config = {
    "max_users": 100,
    "default_role": "viewer",
    "allow_signup": True,
}
roles = ['admin', 'editor', 'viewer']
found = get_user(1, users)
if found:
    print(summarize(found))
    print(found['email'])
    print(to_json(found))
if config['default_role'] in roles:
    print(config['default_role'])
```

## Mchango wa maunzi kwa majaribio ya beta unahitajika
Tunakubali aina yoyote ya maunzi ili kujaribu maendeleo yetu kama vile:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson ikiwa unataka kusaidia kwa namna yoyote ile! 😃
<!--
## Je, unahitaji kukodisha GPU ili kuongeza huduma kutoka kwetu?
- Kura ya maoni imefunguliwa hapa https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Shukrani za Pekee
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 kwa njia bora ya kuhifadhi sura](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
