# 📚 ebook2audiobook (E2A)
Ayípadà CPU/GPU láti inú ìwé-kàwé ẹ̀rọ sí ìwé-ohùn pẹ̀lú àwọn orí àti metadata<br/>
ní lílo àwọn ẹ̀rọ TTS tó ní ìlọsíwájú àti púpọ̀ síi.<br/>
Ó ń ṣe àtìlẹ́yìn fún ẹ̀dà ohùn àti èdè 1158!
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
- [Àwọn Ẹ̀yà](#features)
- [Wíwo GUI](#gui-interface)
- [Àwọn Àfihàn](#demos)
- [Àwọn Èdè Tí A Ṣe Àtìlẹ́yìn Fún](#supported-languages)
- [Àwọn Ìbéèrè Tó Kéré Jù](#hardware-requirements)
- [Ìlò](#instructions)
  - [Ṣíṣe ní Agbègbè](#instructions)
    - [Ṣíṣí Wíwo Wẹ́ẹ̀bù Gradio](#instructions)
    - [Ìlò Headless Ìpilẹ̀](#basic-usage)
    - [Ìlò Àwòṣe XTTS Àdáni Headless](#example-of-custom-model-zip-upload)
    - [Ìjáde àṣẹ ìrànlọ́wọ́](#help-command-output)
  - [Ṣíṣe ní Òkèèrè](#run-remotely)
  - [Docker](#docker)
    - [Àwọn Ìgbésẹ̀ láti Ṣe](#docker)
  
- [Cloned Voices](#cloned-voices)
- [Àwọn àwòṣe TTS Tí A Ti Ṣàtúnṣe](#fine-tuned-tts-models)
  - [Àkójọ Àwọn Àwòṣe TTS Tí A Ti Ṣàtúnṣe](#fine-tuned-tts-collection)
  - [Dídá XTTSv2 Lẹ́kọ̀ọ́](#fine-tune-your-own-xttsv2-model)
- [Àwọn Ọ̀nà eBook Tí A Ṣe Àtìlẹ́yìn Fún](#supported-ebook-formats)
- [Àwọn Ọ̀nà Ìjáde](#output-and-process-formats)
- [Padà sí Ẹ̀dà àtijọ́](#reverting-to-older-versions)
- [Àwọn Ìṣòro Tó Wọ́pọ̀](#common-issues)
- [Ọpẹ́ Pàtàkì](#special-thanks)
- [Àkójọ Àwọn Àkóónú](#table-of-contents)


## Àwọn Ẹ̀yà
- 🔧 **Àwọn ẹ̀rọ TTS tí a ṣe àtìlẹ́yìn fún**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Yí àwọn ọ̀nà fáìlì púpọ̀ padà**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Agbègbè Ọ̀rọ̀** láti yí ọ̀rọ̀ kúkúrú padà tààrà sí ohùn
- 🔍 **Àyẹ̀wò OCR** fún àwọn fáìlì tó ní àwọn ojú-ìwé ọ̀rọ̀ gẹ́gẹ́ bí àwòrán
- 🔊 **Ọ̀rọ̀-sí-ọ̀rọ̀ olódodo gíga**, láti ó fẹ́rẹ̀ jẹ́ àkókò gidi sí ohùn tó fẹ́rẹ̀ jẹ́ gidi
- 🗣️ **Ẹ̀dà ohùn àṣàyàn** ní lílo fáìlì ohùn tìrẹ
- 🌐 **Ó ń ṣe àtìlẹ́yìn fún èdè 1158** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
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
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 èdè àti èdè-ìbílẹ̀ níbí**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


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

**Wo repo wa míràn tí a yà sọ́tọ̀ fún àfikún SML lọ́nà aládàáṣiṣẹ́ nínú eBook rẹ -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Kí o tó fi ìṣòro ìfìsọ́nà tàbí àṣìṣe sílẹ̀, ṣàwárí dáradára nínú TAB àwọn ìṣòro tó ṣí sílẹ̀ àti èyí tí a ti tì<br>
láti rí i dájú pé ìṣòro rẹ kò tíì sí.**

>[!NOTE]
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
   `python app.py --share` (all OS)

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

## Àwọn Oríṣun àwòrán, Cloned Voices
O lè gbé ohùn ohùn èyíkéyìí sókè nínú èyíkéyìí nínú àwọn fọ́mù ohùn tí a ṣe àtìlẹyìn, iye tí ó dára ni nǹkan bí 1 sí 5 mn.
Kò ṣe pàtàkì bí àkọsílẹ̀ náà bá ní ìpìlẹ̀ ariwo tàbí orin tí ó ń ṣeré lórí rẹ̀ — E2A yóò fọ ohùn náà fún ọ.

Èdè Gẹ̀ẹ́sì ni àtòjọ àwọn ohùn tí wọ́n kọ́ sínú rẹ̀. Tí o bá nílò ohùn ní èdè mìíràn kí ó lè jẹ́ ti ìjọba.
àfikún sí àtòjọ náà, jọ̀wọ́ kàn sí wa a ó sì fi kún un lẹ́yìn àtúnyẹ̀wò.

## Àwọn àwòṣe TTS Tí A Ti Ṣàtúnṣe (fine-tuned)
#### Ṣàtúnṣe àwòṣe XTTSv2 tìrẹ

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


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
   ṣàfikún àléébù `--help` ní òpin àṣẹ docker run fún ìsọfúnni síi.
- "Mo ní ìṣòro ohùn tí a gé kúrú!" - JỌ̀WỌ́ ṢÍ ISSUE NÍPA ÈYÍ,
   a kò sọ gbogbo èdè a sì nílò ìmọ̀ràn láti ọ̀dọ̀ àwọn olùmúlò láti ṣàtúnṣe ọgbọ́n pípín gbólóhùn.😊

## ***** ÈTÒ-ÌLỌSÍWÁJÚ *****
- Gbogbo Àwọn Ẹ̀yà ṣí sílẹ̀ fún Àwọn Ìdáwó àjọ̀dún ⭐
- Ìrànlọ́wọ́ èyíkéyìí láti ọ̀dọ̀ àwọn ènìyàn tó ń sọ èdè èyíkéyìí tí a ṣe àtìlẹ́yìn fún láti ràn wá lọ́wọ́ láti mú àwọn àwòṣe dára síi ⭐
- [x] Àwòkọ́ Àwọn Àkójọpọ̀/Orí kí a tó bẹ̀rẹ̀ ìyípadà
- [ ] Ṣàtúnṣe ní gbólóhùn tí a yí padà fún ìyípadà ọ̀rọ̀ tó pé
- [x] Ìṣọ̀kan àmì SML fún ohùn, ìdúró, ìdáwọ́dúró, àti àwọn ìyípadà síi 
- [x] Ìsọfúnni àléébù -h -help ní àwọn èdè ọ̀tọ̀ọ̀tọ̀
- [x] Àyẹ̀wò OCR fún PDF / JPG / BMP / PNG / TIFF
- [x] Fódà Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Mú kí pípín ọ̀rọ̀ Ṣáínà má pín àwọn ọ̀rọ̀ kí a sì mú àkókò ìdúró dára síi [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] Ìṣọ̀kan Audiobookshelf
- [ ] [Ṣe ohun-èlò IOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Ṣe ohun-èlò android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Àwọn Àṣàyàn Àfikún
- [x] Àṣàyàn Ìtumọ̀ eBook
- [x] Àwọn àṣàyàn ọ̀nà ìjáde
- [x] Fódà eBook ìpapọ̀
- [x] Ìyípadà oníṣíṣẹ́-púpọ̀
- [x] Ìyípadà fódà eBook ìpapọ̀
- [x] Ìdánimọ̀ Ẹ̀rọ GPU
- [x] Yọ ariwo kúrò nínú ohùn ìtọ́kasí èyíkéyìí fún ìgbéga ẹ̀dà ohùn,
- [x] Ìgbéga àwòṣe àdáni (XTTSv2 nìkan fún ìsinsìnyí. púpọ̀ síi lórí ìbéèrè)
- [ ] Ṣàfikún àwòṣe èdè Portuguese Yúróòpù fún ó kéré tán xttsv2, fairseq, vits, piper (a kí ìrànlọ́wọ́ káàbọ̀)
- [ ] Ṣàfikún àwòṣe èdè Sindhi fún ó kéré tán xttsv2, fairseq, vits, piper (a kí ìrànlọ́wọ́ káàbọ̀)

#### Àwọn ẹ̀rọ TTS
- [x] XTTSv2
- [x] Bark
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] ijapa
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fish-speech (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Style-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Ìtumọ̀ Readme
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

#### 🐍 Ìbáramu OS
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Àpọ̀jù Àfikún fún dídá àwọn àwòṣe lẹ́kọ̀ọ́ àti irú rẹ̀ (Gbogbo àwọn àwòṣe Coqui-tts tí a ṣe àtìlẹ́yìn fún àti piper-tts nínú àṣẹ rọrùn kan) 
- Fún ìsọfúnni nípa èyí @DrewThomasson, ó ń ṣiṣẹ́ lórí ìdàgbàsókè rẹ̀ lọ́wọ́lọ́wọ́, [repo tó ń lọ lọ́wọ́ níbí](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Ṣe gui ìdánilẹ́kọ̀ọ́ tó rọrùn láti lò fún gbogbo àwọn àwòṣe coqui-tts nínú àwọn ìlànà ìdánilẹ́kọ̀ọ́ ọ̀nà ljspeech [níbí láti ọ̀dọ̀ coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


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
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson tí o bá fẹ́ ṣe ìrànlọ́wọ́ ní ọ̀nà èyíkéyìí! 😃
<!--
## Ṣé o nílò láti yá GPU láti mú iṣẹ́ wa lágbára?
- Ìdìbò kan ti ṣí síbí https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Ọpẹ́ Pàtàkì
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 fún ọ̀nà tó dára jù láti tọ́jú àwọn orí](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
