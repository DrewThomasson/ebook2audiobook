# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Ayípadà CPU/GPU láti inú ìwé-kàwé ẹ̀rọ sí ìwé-ohùn pẹ̀lú àwọn orí àti metadata<br/>
ní lílo àwọn ẹ̀rọ TTS tó ní ìlọsíwájú àti púpọ̀ síi.<br/>
Ṣe àtìlẹyìn fún ìsopọ̀ ohùn àti àwọn èdè 1696!
> [!IMPORTANT]
**Ọ̀pá-ìṣẹ́ yìí jẹ́ fún lílo pẹ̀lú àwọn ìwé-kàwé ẹ̀rọ tí kò ní DRM, tí a rí gbà ní ọ̀nà òfin nìkan.** <br>
Àwọn òǹkọ̀wé kò ní jẹ́jọ́ fún ìlòkulò èyíkéyìí ti software yìí tàbí àbájáde òfin èyíkéyìí tí ó bá yọrí sí. <br>
Lo ọ̀pá-ìṣẹ́ yìí pẹ̀lú ojúṣe àti ní ìbámu pẹ̀lú gbogbo àwọn òfin tó wà ní agbára.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### A dúpẹ́ fún àtìlẹ́yìn àwọn olùdàgbàsókè ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Ṣíṣe ní agbègbè

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Ṣíṣe ní Òkèèrè
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Wíwo GUI
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Tẹ̀ láti rí àwọn àwòrán GUI Wẹ́ẹ̀bù</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Àwọn Àfihàn

**Àfihàn Ohùn Àpẹẹrẹ Tuntun**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Àwọn àfihàn síi</summary>

**Ohùn ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Ohùn Ọjọ́ Òjò**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Ohùn Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Ohùn David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Àpẹẹrẹ**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Àkójọ Àwọn Àkóónú
- [ebook2audiobook](#-ebook2audiobook)
- [Features](#features)
- [GUI Interface](#gui-interface)
- [Demos](#demos)
- [Supported Languages](#supported-languages)
- [Minimum Requirements](#hardware-requirements)
- [Usage](#instructions)
  - [Run Locally](#instructions)
    - [Launching Gradio Web Interface](#instructions)
    - [Basic Headless Usage](#basic-usage)
    - [Headless Custom XTTS Model Usage](#example-of-custom-model-zip-upload)
    - [Help command output](#help-command-output)
  - [Run Remotely](#run-remotely)
  - [Docker](#docker)
    - [Steps to Run](#docker)
- [Tools](#tools)
  - [Preload models for offline installs](#preload-models)
  - [Translate ebooks out of e2a](#translate-ebooks)

- [Cloned Voices](#cloned-voices)
- [Fine Tuned TTS models](#fine-tuned-tts-models)
  - [Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
  - [Train TTS Model](#fine-tune-your-own-tts-model)
- [Supported eBook Formats](#supported-ebook-formats)
- [Output Formats](#output-and-process-formats)
- [Revert to older Version](#reverting-to-older-versions)
- [Common Issues](#common-issues)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


## Àwọn Ẹ̀yà
- 🔧 **TTS Engines ni atilẹyin**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Yí àwọn ọ̀nà fáìlì púpọ̀ padà**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Agbègbè Ọ̀rọ̀** láti yí ọ̀rọ̀ kúkúrú padà tààrà sí ohùn
- 🔍 **Àyẹ̀wò OCR** fún àwọn fáìlì tó ní àwọn ojú-ìwé ọ̀rọ̀ gẹ́gẹ́ bí àwòrán
- 🔊 **Ọ̀rọ̀-sí-ọ̀rọ̀ olódodo gíga**, láti ó fẹ́rẹ̀ jẹ́ àkókò gidi sí ohùn tó fẹ́rẹ̀ jẹ́ gidi
- 🗣️ **Ẹ̀dà ohùn àṣàyàn** ní lílo fáìlì ohùn tìrẹ
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Ọ̀rẹ́ àwọn ohun-àmúṣe kékeré** — ó ń ṣiṣẹ́ lórí **2 GB RAM / 1 GB VRAM (tó kéré jù)**
- 🎵 **Àwọn ọ̀nà ìjáde ìwé-ohùn**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **A ṣe àtìlẹ́yìn fún àwọn àmì SML** — ìṣàkóso tó pé fún àwọn ìdáwọ́dúró, ìdúró, ìyípadà ohùn àti púpọ̀ síi ([see below](#sml-tags-available))
- 🧩 **Àwòṣe àdáni àṣàyàn** ní lílo àwòṣe tí o dá lẹ́kọ̀ọ́ fúnra rẹ (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Àwọn àwòṣe preset tí a ti ṣàtúnṣe** tí Ẹgbẹ́ E2A dá lẹ́kọ̀ọ́<br/>
     <i>(Kàn sí wa tí o bá nílò àwọn àwòṣe àfikún tí a ti ṣàtúnṣe, tàbí tí o bá fẹ́ pín tìrẹ sí àkójọ preset oníṣẹ́-aṣẹ)</i>


##  Àwọn Ìbéèrè Ohun-èlò
- RAM 2GB tó kéré jù, 8GB ní ìṣedéédéé.
- VRAM 1GB tó kéré jù, 4GB ní ìṣedéédéé.
- A ṣe àfikún Virtualization tí a bá ń ṣe lórí windows (Docker nìkan).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Àwọn ẹ̀rọ TTS òde-òní lọ́ra gan-an lórí CPU, nítorí náà lo TTS olódodo kékeré bíi YourTTS, Tacotron2 àti bẹ́ẹ̀ bẹ́ẹ̀ lọ.</i>

## Àwọn Èdè Tí A Ṣe Àtìlẹ́yìn Fún
Èdè Lárúbáwá (ar) **Èdè Ṣáínà (zh)** * Èdè Gẹ̀ẹ́sì (en)* * Èdè Sípáníìṣì (es) **Èdè Sípáníìṣì (es)** Èdè Sípáníìṣì (es) **Èdè Sípáníìṣì (es)** Èdè Sípán
|:------------------:|:------------------:|:------------------:|:------------------:|
Èdè Faransé (fr)** Èdè Jẹ́mánì (de)* ** Èdè Ítálì (it)**Èdè Potogí (pt)**.
**Polish (pl)** * **Turkish (tr)** **Russian (ru)** **Dutch (nl)**.
**Czech (cs)** **Japanese (ja)** **Hindi (hi)** **Bengali (bn)**
**Hungarian (hu)** **Korean (ko)** **Vietnamese (vi)** **Swedish (sv)**.
Èdè Páṣíà (fa)* **Èdè Yorùbá (yo)** *Èdè Swahili (sw)** Èdè Indonéṣíà (id)**.
**Slovak (sk)** ***Croatian (hr)* **Tamil (ta)** *Danish (da)**.
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Àwọn Ọ̀nà eBook Tí A Ṣe Àtìlẹ́yìn Fún
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Àbájáde tó dára jù**: `.epub` tàbí `.mobi` fún ìdánimọ̀ orí lọ́nà aládàáṣiṣẹ́

## Àwọn Ọ̀nà Ìjáde àti ìṣíṣẹ́
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- A lè yí ọ̀nà ìṣíṣẹ́ padà nínú lib/conf.py

## Àwọn àmì SML tó wà
- `[break]` — ìdákẹ́jẹ́ẹ́ (àyè àìròtẹ́lẹ̀ **0.3–0.6 sec.**)
- `[pause]` — ìdákẹ́jẹ́ẹ́ (àyè àìròtẹ́lẹ̀ **1.0–1.6 sec.**)
- `[pause:N]` — ìdúró tí a gbé kalẹ̀ (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — yí ohùn padà láti ohùn àpẹẹrẹ tàbí èyí tí a yàn láti GUI/CLI
- `[emotion:sadness]...[/emotion]` — Zonos nìkan: ìmọ̀lára fún ìrìn-àjò kan (ìdùnnú, ìbànújẹ́, ìkórìíra, ìbẹ̀rù, ìyanu, ìbínú, òmíràn, àìdáa) tàbí ìdàpọ̀ bíi `[emotion:sadness=0.7,neutral=0.3]`; àwọn ẹ̀rọ mìíràn ṣàìgbọràn sí i

**Wo repo wa míràn tí a yà sọ́tọ̀ fún àfikún SML lọ́nà aládàáṣiṣẹ́ nínú eBook rẹ -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Kí o tó fi ìṣòro ìfìsọ́nà tàbí àṣìṣe sílẹ̀, ṣàwárí dáradára nínú TAB àwọn ìṣòro tó ṣí sílẹ̀ àti èyí tí a ti tì<br>
láti rí i dájú pé ìṣòro rẹ kò tíì sí.**

Àkíyèsi
**Ọ̀nà EPUB kò ní ètò àpapọ̀ èyíkéyìí bíi ohun tí orí jẹ́, ìpínrọ̀, ọ̀rọ̀-ìṣáájú àti bẹ́ẹ̀ bẹ́ẹ̀ lọ.<br>
Nítorí náà o gbọ́dọ̀ kọ́kọ́ yọ ọ̀rọ̀ èyíkéyìí tí o kò fẹ́ yí padà sí ohùn pẹ̀lú ọwọ́.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Fi sori ẹrọ / Ṣe ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Olùṣíṣẹ́ Mac**  
     Tẹ̀ ní ẹ̀ẹ̀mejì `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Àkíyèsí fún àwọn olùmúlò Windows: a fi scoop sori ẹrọ láti fi àwọn ètò tó nù sori ẹrọ láìsí àwọn ẹ̀tọ́ alábòójútó.</i>
   
1. **Ṣí Ohun-èlò Wẹ́ẹ̀bù**: Tẹ̀ URL tí a pèsè nínú terminal láti wọlé sí ohun-èlò wẹ́ẹ̀bù àti yí àwọn eBook padà. `http://localhost:7860/`
2. **Fún Ọ̀nà Àjọ̀dún**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (gbogbo OS)

> [!IMPORTANT]
**Tí a bá dúró kọ̀ǹpútà-ìtọ́ni tí a sì tún ṣe é, o nílò láti tún wíwo GUI gradio rẹ ṣe<br>
láti gba ojú-ìwé wẹ́ẹ̀bù láàyè láti tún sopọ̀ mọ́ socket ìsopọ̀ tuntun.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Ọ̀nà sí fáìlì eBook rẹ
  - **[--voice]**: Ọ̀nà fáìlì ẹ̀dà ohùn (àṣàyàn)
  - **[--language]**: Àmì èdè ní ISO-639-3 (ìyẹn: ita fún Ítálì, eng fún Gẹ̀ẹ́sì, deu fún Jámánì...).<br>
    Èdè àpẹẹrẹ ni eng àti --language jẹ́ àṣàyàn fún èdè àpẹẹrẹ tí a gbé kalẹ̀ nínú ./lib/lang.py.<br>
    Àwọn àmì ISO-639-1 oníléta 2 náà ni a ṣe àtìlẹ́yìn fún.


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
     
- **<custom_model_path>**: Ọ̀nà sí fáìlì `model_name.zip`,
      èyí tó gbọ́dọ̀ ní (gẹ́gẹ́ bí ẹ̀rọ tts) gbogbo àwọn fáìlì pàtàkì<br>
      (wo ./lib/models.py).

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
  --abs_url ABS_URL     Audiobookshelf server URL (e.g. http://localhost:13378).
  --abs_api_token ABS_API_TOKEN
                        Audiobookshelf API token.
  --abs_library ABS_LIBRARY
                        Audiobookshelf library ID.
  --enable_interlude    Add MusicGen music before the first chapter, between chapters, and at the end of the audiobook. Settings are in ./lib/conf_interlude.py
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
	[emotion:sadness]...[/emotion] — Zonos only: emotion for a passage (happiness, sadness, disgust, fear, surprise, anger, other, neutral) or a mix like [emotion:sadness=0.7,neutral=0.3]; other engines ignore it

```

ÀKÍYÈSÍ: ní ìpò gradio/gui, láti fagilé ìyípadà tó ń lọ lọ́wọ́, kàn tẹ̀ [X] láti inú ẹ̀yà ìgbéga eBook.
ÌMỌ̀RÀN: tí ó bá nílò ìdúró díẹ̀ síi, ṣàfikún '[pause:3]' fún ìṣẹ́jú-àáyá 3 àti bẹ́ẹ̀ bẹ́ẹ̀ lọ.

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
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc...]
    Headless mode:
        CPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
Docker Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 docker compose --profile cuda up --no-log-prefix
        Run Headless mode:
               DEVICE_TAG=cu128 docker compose --profile cuda run --rm ebook2audiobook-cuda --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
Podman Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile cuda up
        Run Headless mode:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile cuda run --rm ebook2audiobook-cuda --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
```
- NOTE: MPS is not exposed in docker so CPU must be used
- NOTE: the named volume `e2a_venvs` keeps the TTS engines installed in their own venv (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM etc.)
  across container runs, so they are not reinstalled each time. To reset them: `docker volume rm e2a_venvs`

## Àwọn irin iṣẹ́
Àwọn irinṣẹ́ tí ó dúró ṣánṣán, sáré pẹ̀lú Python ti e2a fúnra rẹ̀ (`python_env`, tí a ṣẹ̀dá nípa ìfilọ̀ àkọ́kọ́ ti e2a).

<a id="preload-models"></a>
### Preload models for offline installs: `tools/preload_models.py`
Downloads every model e2a uses (TTS engines and their fine-tunes, voice conversion, stanza, pyannote, demucs,
music interludes, argos-translate packages, tesseract data, jieba, and the voices) into one folder laid out
exactly like `./models`, i.e. a USB key. On the offline machine, copy that folder into e2a's `./models`
and the `voices` folder written beside it into e2a's `./voices`.
Every finished job is recorded in `<models_dir>/.e2a_downloads.json`: a rerun skips what is done and starts
again what was cut (ctrl-c, crash, unplugged key) after removing its partial files.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` lists the jobs and their state (done, interrupted, todo) without downloading anything.

```bash
usage: preload_models.py [-h] [--only ONLY] [--skip SKIP] [--languages LANGUAGES]
                         [--audiocpp_packages AUDIOCPP_PACKAGES] [--refresh] [--dry_run]
                         models_dir

Download every model e2a uses into one folder laid out exactly like ./models (i.e. a USB key for offline
installs).

positional arguments:
  models_dir            Target folder, i.e. /media/user/KEY/models or E:\models

options:
  -h, --help            show this help message and exit
  --only ONLY           Comma list of categories: common,xtts,bark,tortoise,vits,fairseq,glowtts,tacotron,yo
                        urtts,piper,zonos,audiocpp,audiocpp_server,gptsovits,f5tts,omnivoice,orpheus,sparktt
                        s,chattts,csm,openvoice,melotts,phonon,stanza,pyannote,demucs,interlude,argos,tessda
                        ta,jieba,voices
  --skip SKIP           Comma list of categories to leave out
  --languages LANGUAGES
                        Comma list of e2a ISO-639-3 codes (eng,fra,ita...): single-language models and fine-
                        tunes for these only, multilingual models only for engines speaking one of them
  --audiocpp_packages AUDIOCPP_PACKAGES
                        audiocpp_server category: auto (the packages this machine runs, GPU and CPU), all
                        (every platform, for a key used elsewhere), or a comma list of audiocpp_packages
                        keys from lib/conf_models.py
  --refresh             Run every job again, even those already marked done (files already there are still
                        not downloaded twice)
  --dry_run             List every download job with its state (done, interrupted, todo) and exit
```

<a id="translate-ebooks"></a>
### Translate ebooks out of e2a: `translate_ebook.sh` / `translate_ebook.cmd`
Translates EPUB/AZW3 files, a whole folder (`-r` for its subfolders) or a list of paths (`@list.txt`)
into translated ebooks, offline, with the Argos Translate calibre plugin shipped in
`tools/argostranslate-calibre-plugin.zip`. Independent of the audiobook conversion: it only writes ebooks.
It needs calibre (already required by e2a) and runs on e2a's `python_env` and argos-translate packages:
a language pair e2a already uses is not downloaded again, a missing one is downloaded on first use.
The plugin is installed on first use into e2a's own calibre profile (`./run`), your calibre is left untouched.
`--to fra,ara,spa` translates into several languages at once, one ebook per language, and `--to all` into every
language the source reaches (`--from`, else each book's own language; installed ones only with `--no_download`).
`--list --from eng` lists the languages English translates into (installed, downloadable, or through English for
another source).
Other formats calibre's `ebook-convert` reads (PDF, DOCX, MOBI, TXT, ...) are converted to EPUB once, before the
first language, and translated as EPUB: `--from` is needed when they carry no language, as PDF and TXT often do.
Without `-o` or `--output_dir`, each translation is saved beside its book as `<name>.<lang>.<ext>`,
and a book whose translation already exists is skipped (`--overwrite` to translate it again).
The launchers in e2a's folder run `tools/translate_ebook.py` with `python_env`, nothing to activate,
from any folder (relative paths are taken from where it is started):
   - **Linux/MacOS**
     ```bash
     ./translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Or directly with `python_env`'s Python: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Started with any other Python,
     the script starts itself again with `python_env`'s.
   - **Docker**: run it inside the e2a container, e.g. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     with paths seen from the container.
   - **Speed**: argostranslate runs on its own defaults (CTranslate2 picks the threads and the fastest compute type,
     int8 on CPU), not on e2a's 1 thread in float32. Set `ARGOS_INTRA_THREADS` or `ARGOS_COMPUTE_TYPE` to override them.

```bash
usage: translate_ebook.py [-h] [-t LANG[,LANG...]] [-f LANG] [-r] [-o OUTPUT] [--output_dir OUTPUT_DIR]
                          [--overwrite] [-m {replace,bilingual}] [--device {cpu,cuda,auto}]
                          [--batch_size BATCH_SIZE] [--no_cache] [--no_download] [--allow_changes] [--list]
                          [books ...]

Translate ebooks offline, out of e2a, with the Argos Translate calibre plugin
(tools/argostranslate-calibre-plugin.zip). EPUB/AZW3 are translated as they are, the other formats
calibre's ebook-convert reads (PDF, DOCX, MOBI, ...) are converted to EPUB once, before the first
language, and their translations saved as EPUB. It runs on e2a's python_env and argos-translate packages
(models/argos-translate): a language pair e2a already uses is not downloaded again, a missing one is
downloaded on first use (direct or through English). The plugin is installed into e2a's own calibre
profile (run/) on first use, your calibre setup is left untouched.
Translated paths are printed on stdout, progress and logs on stderr.

positional arguments:
  books                 Ebook files (EPUB, AZW3, or PDF, DOCX, MOBI... converted to EPUB first) or folders
                        to translate; @list.txt reads paths from a file, one per line

options:
  -h, --help            show this help message and exit
  -t, --to LANG[,LANG...]
                        Target language(s), ISO-639-1 or ISO-639-3 codes, comma separated for several (fr,
                        fra or fra,ara,spa): one translated ebook per language. all: every language the
                        source reaches (see --list --from), installed ones only with --no_download
  -f, --from LANG       Source language, ISO-639-1 or ISO-639-3 code (default: read from each book)
  -r, --recursive       Also look for books in the subfolders of the given folders
  -o, --output OUTPUT   Output file, single input only, same extension as the input, .epub for a converted
                        one (default: <name>.<lang>.<ext> next to the input)
  --output_dir OUTPUT_DIR
                        Write the translations into this folder (subfolders are mirrored with -r) instead of
                        next to each book
  --overwrite           Translate again even if the output file already exists (skipped otherwise)
  -m, --mode {replace,bilingual}
                        replace: the translation replaces the text. bilingual: each paragraph is followed by
                        its translation, saved as <name>.<lang>.bilingual.<ext> (default: replace)
  --device {cpu,cuda,auto}
                        Device argostranslate runs on (default: cpu)
  --batch_size BATCH_SIZE
                        Segments sent to the translation worker per request (default: 16)
  --no_cache            Neither read nor write the translation cache (run/argos_translate/cache.sqlite), the
                        one that makes a second run of the same book near instant
  --no_download         Never download a missing argos-translate package, fail instead
  --allow_changes       Only when argostranslate is missing from python_env: install it even if packages
                        already there would change version
  --list                List the installed and the downloadable language pairs, then exit. With --from
                        and/or --to: only their pairs, plus the targets a source reaches through English

examples:
  translate_ebook.py book.epub --to fr
  translate_ebook.py book.epub --to fra,ara,spa
  translate_ebook.py book.azw3 --from en --to deu -o /path/to/book_deu.azw3
  translate_ebook.py /path/to/books -r --to es,it --output_dir /path/to/books_translated
  translate_ebook.py book.epub --from eng --to all
  translate_ebook.py @books.txt --to ita --mode bilingual
  translate_ebook.py --list
  translate_ebook.py --list --from eng
```

## Àwọn Oríṣun àwòrán, Cloned Voices
O lè gbé ohùn ohùn èyíkéyìí sókè nínú èyíkéyìí nínú àwọn fọ́mù ohùn tí a ṣe àtìlẹyìn, iye tí ó dára ni nǹkan bí 1 sí 5 mn.
Kò ṣe pàtàkì bí àkọsílẹ̀ náà bá ní ìpìlẹ̀ ariwo tàbí orin tí ó ń ṣeré lórí rẹ̀ — E2A yóò fọ ohùn náà fún ọ.

Èdè Gẹ̀ẹ́sì ni àtòjọ àwọn ohùn tí wọ́n kọ́ sínú rẹ̀. Tí o bá nílò ohùn ní èdè mìíràn kí ó lè jẹ́ ti ìjọba.
àfikún sí àtòjọ náà, jọ̀wọ́ kàn sí wa a ó sì fi kún un lẹ́yìn àtúnyẹ̀wò.

## Àwọn àwòṣe TTS Tí A Ti Ṣàtúnṣe (fine-tuned)
#### Tún àwòṣe TTS tìrẹ ṣe dáadáa

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Yíyọ ariwo kúrò nínú dátà ìdánilẹ́kọ̀ọ́

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Àkójọ Àwọn Àwòṣe TTS Tí A Ti Ṣàtúnṣe

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Fún àwòṣe àdáni XTTSv2, klipu ohùn ìtọ́kasí ti ohùn jẹ́ pàtàkì:

## Ìbáamu Ebook2Audiobook tìrẹ
O ní òmìnira láti ṣàtúnṣe libs/conf.py láti ṣàfikún tàbí yọ àwọn ètò tí o fẹ́ kúrò. Tí o bá ń gbèrò láti ṣe é, kàn ṣe
ẹ̀dà conf.py ìpilẹ̀ kí o lè, ní gbogbo ìmúdójúìwọ̀n ebook2audiobook, gba conf.py tí o ṣàtúnṣe pamọ́ kí o sì tún
ìpilẹ̀ padà. O gbọ́dọ̀ gbèrò ìṣẹ̀lẹ̀ kan náà fún models.py. Tí o bá fẹ́ sọ àwòṣe àdáni tìrẹ
di àwòṣe ebook2audiobook oníṣẹ́-aṣẹ tí a ti ṣàtúnṣe, jọ̀wọ́ kàn sí wa a ó sì fi kún àkójọ preset.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Àwọn Ìṣòro Tó Wọ́pọ̀:
- A kò rí GPU NVIDIA/ROCm/XPU/MPS mi?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU lọ́ra (ó dára jù lórí CPU smp sáfà) nígbà tí GPU lè ní ìyípadà tó fẹ́rẹ̀ jẹ́ àkókò gidi.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Bí ó tilẹ̀ jẹ́ pé kò ní ẹ̀dà ohùn zero-shot, tí ó sì jẹ́ àwọn ohùn olódodo Siri, ṣùgbọ́n ó yára púpọ̀ síi lórí cpu).
- "Mo ní àwọn ìṣòro ìgbẹ́kẹ̀lé" - Kàn lo docker, ó dúró lóró fúnra rẹ̀ pátápátá ó sì ní ìpò headless,
   ṣàfikún àléébù  ní òpin àṣẹ docker run fún ìsọfúnni síi. `--help`
- "Mo ní ìṣòro ohùn tí a gé kúrú!" - JỌ̀WỌ́ ṢÍ ISSUE NÍPA ÈYÍ,
   a kò sọ gbogbo èdè a sì nílò ìmọ̀ràn láti ọ̀dọ̀ àwọn olùmúlò láti ṣàtúnṣe ọgbọ́n pípín gbólóhùn.😊

## ***** ÈTÒ-ÌLỌSÍWÁJÚ *****
- Gbogbo Àwọn Ẹ̀yà ṣí sílẹ̀ fún Àwọn Ìdáwó àjọ̀dún ⭐
- Ìrànlọ́wọ́ èyíkéyìí láti ọ̀dọ̀ àwọn ènìyàn tó ń sọ èdè èyíkéyìí tí a ṣe àtìlẹ́yìn fún láti ràn wá lọ́wọ́ láti mú àwọn àwòṣe dára síi ⭐
- [x] Àwòkọ́ Àwọn Àkójọpọ̀/Orí kí a tó bẹ̀rẹ̀ ìyípadà
- [x] Ṣàtúnṣe ní gbólóhùn tí a yí padà fún ìyípadà ọ̀rọ̀ tó pé
- [x] Ṣẹda orin intros, interludes, àti ìparí; ṣatunkọ interludes àti ìparí
- [x] Ìṣọ̀kan àmì SML fún ohùn, ìdúró, ìdáwọ́dúró, àti àwọn ìyípadà síi
- [x] Ìsọfúnni àléébù -h -help ní àwọn èdè ọ̀tọ̀ọ̀tọ̀
- [x] Àyẹ̀wò OCR fún PDF / JPG / BMP / PNG / TIFF
- [x] Fódà Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Mú kí pípín ọ̀rọ̀ Ṣáínà má pín àwọn ọ̀rọ̀ kí a sì mú àkókò ìdúró dára síi [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Àkọsílẹ Docker
- [x] Docker compose
- [x] Podman kọ
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [x] Ìṣọ̀kan Audiobookshelf
- [x] Àṣàyàn Ìtumọ̀ eBook
- [x] Àwọn àṣàyàn ọ̀nà ìjáde
- [x] Ìyípadà oníṣíṣẹ́-púpọ̀
- [x] Ìyípadà fódà eBook ìpapọ̀
- [x] Ìdánimọ̀ Ẹ̀rọ GPU
- [x] Yọ eyikeyi ohun afetigbọ itọkasi abẹlẹ fun gbigbasilẹ ohun afetigbọ
- [x] Awoṣe aṣa ti o dara-tuned gbe soke
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Àwọn ìbéèrè oníṣe
- [ ] Ṣàfikún àwòṣe èdè Portuguese Yúróòpù fún ó kéré tán xttsv2, fairseq, vits, piper (a kí ìrànlọ́wọ́ káàbọ̀)
- [ ] Ṣàfikún àwòṣe èdè Sindhi fún ó kéré tán xttsv2, fairseq, vits, piper (a kí ìrànlọ́wọ́ káàbọ̀)

#### Àwọn ẹ̀rọ TTS
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1)
- [x] FireRed Audio / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1)
- [x] Eja-ọrọ / Eja Audio (https://github.com/fishaudio/fish-speech)[cite: 1)
- [x] Higgs Audio TTS (https://github.com/higgs-audio/higgs-audio)[cite: 1)
- [x] Maya1 (https://github.com/maya-ai/maya1)[cite: 1)
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1)
- [x] F5-TTS (https://github.com/swivid/f5-tts)[cite: 1)
- [x] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1)
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1)
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1)
- [x] Voxtral TTS (https://github.com/voxtral/voxtral-tts)[cite: 1)
- [x] Chatterbox (https://github.com/resemble-ai/chatterbox)[cite: 1)
- [x] CosyVoice / CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1)
- [x] Atọka-tts / Atọka TTS2 (https://github.com/index-tts/index-tts)[cite: 1)
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1)
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1)
- [x] Confucius4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1)
- [x] Dots TTS (https://github.com/dot-audio/dots-tts)[cite: 1)
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1)
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1)
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1)
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1)
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1)
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1)
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1)
- [x] Pocket TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1)
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1)
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1)
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1)
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1)
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1)
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1)
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1)
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1)
- [x] Tortoise (https://github.com/neonbjb/tortoise-tts)[cite: 1)
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1)
- [x] Bark (https://github.com/suno-ai/bark)[cite: 1)
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1)
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Ìtumọ̀ Readme
- [x] Lárúbáwá (Lárúbáwá)
- [x] Chinese (zho)
- [x] Èdè Gẹ̀ẹ́sì (eng)
- [x] Èdè Sípáníìṣì (SPA)
- [x] Faranse (fra)
- [x] Jẹmánì (DEU)
- [x] Itali (ita)
- [x] Èdè Potogí (por)
- [x] Pólándì (pol)
- [x] Tọki (TUR)
- [x] Rọ́ṣíà (Rọ́ṣíà)
- [x] Dutch (nld)
- [x] Czech (ces)
- [x] Japanese (jpn)
- [x] Hindi (hin)
- [x] Èdè Bengali (BEN)
- [x] Hungarian (hun)
- [x] Kòréà (kor)
- [x] Vietnamese (VIVE)
- [x] Swedish (swe)
- [x] Persian (FAS)
- [x] Yorùbá (yor)
- [x] Swahili (swa)
- [x] Indonesian (IND)
- [x] Slovak (slk)
- [x] Croatian (hrv)

#### Ibamu 💻 OS
- [x] 🪟 Windows x86
- [x] 🪟 ARM Windows
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM Linux

**********

## Àpọ̀jù Àfikún fún dídá àwọn àwòṣe lẹ́kọ̀ọ́ àti irú rẹ̀ (Gbogbo àwọn àwòṣe Coqui-tts tí a ṣe àtìlẹ́yìn fún àti piper-tts nínú àṣẹ rọrùn kan) 
- Fún àlàyé nípa èyí @ DrewThomasson, ó ń ṣiṣẹ́ lórí ìdàgbàsókè èyí, [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Make a easy to use training gui for all coqui-tts models in the [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) Completed at [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## Ìsọfúnni ìṣàkóso Kóòdù Python fún àwọn olùdáwó
- kò sí ìlà òfìfo láàrin kóòdù, àyàfi láàrin àwọn iṣẹ́ àti àwọn kíláàsì.
- àmì-ọ̀rọ̀ kan ṣoṣo ni a lò fún gbogbo àwọn kọ́kọ́rọ́ àyàfi fún dict() àti json. dict['key'] ni a máa ń pè pẹ̀lú àmì-ọ̀rọ̀ kan ṣoṣo nígbà gbogbo
- àyè-ìbẹ̀rẹ̀ àwọn àlàfo 4, kì í ṣe tab rárá
- ìtẹ̀wé tó le fún gbogbo àwọn iṣẹ́ àti ìkéde àwọn àríyànjiyàn àti àwọn iye ìpadàbọ̀ wọn
- kò sí àlàfo láàrin àríyànjiyàn àti ìtẹ̀wé rẹ̀, kò sí àlàfo láàrin iṣẹ́, "->" àti iye ìpadàbọ̀

Àpẹẹrẹ:

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

## A ń wá ẹ̀bùn ohun-èlò fún àwọn ìdánwò beta
A gba irú ohun-èlò èyíkéyìí láti dán ìdàgbàsókè wa wò bíi:
- Nvidia ṣe àtìlẹyìn cuda >= 11.8
- Àwọn káàdì XPU intel
- Àwọn káàdì ROCm AMD tí ó ń ṣètìlẹ́yìn fún ROCm >=5.7

@DrewThomasson tí o bá fẹ́ ṣe ìrànlọ́wọ́ ní ọ̀nà èyíkéyìí! 😃
<!--
## Ṣé o nílò láti yá GPU láti mú iṣẹ́ wa lágbára?
- Ìdìbò kan ti ṣí síbí https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Awọn kirediti
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- Ohun èlò ìkẹ́kọ̀ọ́ tó jinlẹ̀ fún Text-to-Speech, tí a dán wò nínú ìwádìí àti ìṣẹ̀dá.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Fast and local neural text-to-speech engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml kóódù ìfihàn fún Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) - Ẹrọ ìfihàn C++ tí ó mọ́ fún àwọn àwòṣe ohùn, tí ggml ń lò.

## Ọpẹ́ Pàtàkì
Fún gbogbo àwọn olùpínlẹ̀ owó àti kóódù, ìfowópamọ́ àti àbá kọ̀ọ̀kan ń ṣe ìrànlọ́wọ́ láti mú kí E2A dára sí i.