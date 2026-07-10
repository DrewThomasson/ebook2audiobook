# 📚 ebook2audiobook (E2A)
전자책을 챕터 및 메타데이터가 포함된 오디오북으로 변환하는 CPU/GPU 변환기<br/>
고급 TTS 엔진 등을 사용합니다.<br/>
음성 복제와 1158개 언어를 지원합니다!
> [!IMPORTANT]
**이 도구는 DRM이 없고 합법적으로 취득한 전자책에만 사용하도록 만들어졌습니다.** <br>
저작자는 이 소프트웨어의 어떠한 오용이나 그로 인한 법적 결과에 대해 책임지지 않습니다. <br>
이 도구를 책임감 있게, 그리고 적용 가능한 모든 법률을 준수하여 사용하십시오.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### ebook2audiobook 개발자를 지원해 주셔서 감사합니다!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### 로컬에서 실행

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### 원격으로 실행
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### 그래픽 인터페이스(GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>웹 GUI 이미지를 보려면 클릭하세요</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## 데모

**새로운 기본 음성 데모**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>추가 데모</summary>

**ASMR 음성** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**비 오는 날 음성**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**스칼렛 음성**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**데이비드 애튼버러 음성** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**예시**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## 목차
- [ebook2audiobook](#-ebook2audiobook)
- [기능](#features)
- [그래픽 인터페이스](#gui-interface)
- [데모](#demos)
- [지원 언어](#supported-languages)
- [최소 요구 사항](#hardware-requirements)
- [사용법](#instructions)
  - [로컬에서 실행](#instructions)
    - [Gradio 웹 인터페이스 실행](#instructions)
    - [기본 Headless 사용법](#basic-usage)
    - [Headless 커스텀 XTTS 모델 사용법](#example-of-custom-model-zip-upload)
    - [도움말 명령 출력](#help-command-output)
  - [원격으로 실행](#run-remotely)
  - [Docker](#docker)
    - [실행 단계](#docker)
  
- [Cloned Voices](#cloned-voices)
- [미세 조정된 TTS 모델](#fine-tuned-tts-models)
  - [미세 조정된 TTS 모델 모음](#fine-tuned-tts-collection)
  - [XTTSv2 학습](#fine-tune-your-own-xttsv2-model)
- [지원되는 전자책 형식](#supported-ebook-formats)
- [출력 형식](#output-and-process-formats)
- [이전 버전으로 되돌리기](#reverting-to-older-versions)
- [일반적인 문제](#common-issues)
- [특별히 감사드립니다](#special-thanks)
- [목차](#table-of-contents)


## 기능
- 🔧 **지원되는 TTS 엔진**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **여러 파일 형식 변환**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 짧은 텍스트를 직접 오디오로 변환하는 **텍스트 영역**
- 🔍 이미지로 된 텍스트 페이지가 있는 파일을 위한 **OCR 스캔**
- 🔊 **고품질 텍스트 음성 변환**, 거의 실시간부터 거의 실제 음성까지
- 🗣️ 자신의 음성 파일을 사용한 **선택적 음성 복제**
- 🌐 **1158개 언어 지원** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **저사양 친화적** — **2 GB RAM / 1 GB VRAM(최소)**에서 실행
- 🎵 **오디오북 출력 형식**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML 태그 지원** — 중단, 멈춤, 음성 전환 등의 세밀한 제어 ([see below](#sml-tags-available))
- 🧩 자신이 학습한 모델을 사용한 **선택적 커스텀 모델** (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ E2A 팀이 학습한 **미세 조정된 프리셋 모델**<br/>
     <i>(추가 미세 조정된 모델이 필요하거나, 공식 프리셋 목록에 자신의 모델을 공유하고 싶으시면 저희에게 연락하세요)</i>


##  하드웨어 요구 사항
- RAM 2GB 최소, 8GB 권장.
- VRAM 1GB 최소, 4GB 권장.
- Windows에서 실행하는 경우 가상화 활성화(Docker 전용).
- CPU, XPU(intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS(Apple Silicon CPU)

*<i> 최신 TTS 엔진은 CPU에서 매우 느리므로 YourTTS, Tacotron2 등 더 낮은 품질의 TTS를 사용하세요.</i>

## 지원 언어
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130개 언어 및 방언은 여기에서**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## 지원되는 전자책 형식
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **최상의 결과**: 자동 챕터 감지에는 `.epub` 또는 `.mobi`

## 출력 및 처리 형식
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- 처리 형식은 lib/conf.py에서 변경할 수 있습니다

## 사용 가능한 SML 태그
- `[break]` — 무음(무작위 범위 **0.3–0.6 sec.**)
- `[pause]` — 무음(무작위 범위 **1.0–1.6 sec.**)
- `[pause:N]` — 고정 멈춤(**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — 기본 음성 또는 GUI/CLI에서 선택한 음성에서 음성 전환

**전자책에 SML을 자동으로 추가하는 데 전념하는 다른 저장소를 확인하세요 -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**설치 또는 버그 문제를 게시하기 전에, 열린 문제와 닫힌 문제 탭을 주의 깊게 검색하여<br>
귀하의 문제가 아직 존재하지 않는지 확인하십시오.**

>[!NOTE]
**EPUB 형식에는 챕터, 단락, 서문 등이 무엇인지 정의하는 어떠한 표준 구조도 없습니다.<br>
따라서 먼저 오디오로 변환하고 싶지 않은 텍스트를 수동으로 제거해야 합니다.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook 설치 / 실행**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac 런처**  
     `Mac Ebook2Audiobook Launcher.command`를 더블 클릭하세요


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Windows 사용자 참고: 관리자 권한 없이 누락된 프로그램을 설치하기 위해 scoop이 설치됩니다.</i>
   
1. **웹 앱 열기**: 터미널에 제공된 URL을 클릭하여 웹 앱에 접속하고 전자책을 변환하세요. `http://localhost:7860/`
2. **공개 링크의 경우**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**스크립트를 중지하고 다시 실행하면 Gradio GUI 인터페이스를 새로 고쳐야 합니다<br>
웹 페이지가 새로운 연결 소켓에 다시 연결될 수 있도록 하기 위해서입니다.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: 전자책 파일의 경로
  - **[--voice]**: 음성 복제 파일 경로(선택 사항)
  - **[--language]**: ISO-639-3 형식의 언어 코드(예: 이탈리아어는 ita, 영어는 eng, 독일어는 deu...).<br>
    기본 언어는 eng이며, ./lib/lang.py에 설정된 기본 언어의 경우 --language는 선택 사항입니다.<br>
    2글자 ISO-639-1 코드도 지원됩니다.


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
     
- **<custom_model_path>**: `model_name.zip` 파일의 경로,
      이 파일은 (tts 엔진에 따라) 모든 필수 파일을 포함해야 합니다<br>
      (./lib/models.py 참조).

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

참고: gradio/gui 모드에서 진행 중인 변환을 취소하려면 전자책 업로드 구성 요소의 [X]를 클릭하기만 하면 됩니다.
팁: 좀 더 긴 멈춤이 필요하면 3초의 경우 '[pause:3]'을 추가하는 등.

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

## 복제된 음성
지원되는 오디오 형식으로 모든 음성 오디오를 업로드할 수 있으며, 이상적인 지속 시간은 약 1 ~ 5분입니다.
녹음에 시끄러운 배경이 있거나 음악이 재생되는지 여부는 중요하지 않습니다. E2A가 음성을 정리합니다.

내장된 복제된 음성 목록은 주로 영어로 되어 있습니다. 공식적으로 사용하려면 다른 언어로 된 목소리가 필요한 경우
목록에 추가되었습니다. 문의해 주시면 검토 후 추가해 드리겠습니다.

## 미세 조정된(fine-tuned) TTS 모델
#### 자신만의 XTTSv2 모델을 미세 조정하세요

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### 학습 데이터의 노이즈 제거

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### 미세 조정된 TTS 모델 모음

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

커스텀 XTTSv2 모델의 경우 음성의 참조 오디오 클립이 필수입니다:

## 자신만의 Ebook2Audiobook 사용자 정의
원하는 설정을 추가하거나 제거하기 위해 libs/conf.py를 자유롭게 수정할 수 있습니다. 이를 계획하고 있다면, 단순히
원본 conf.py의 복사본을 만들어 두면 ebook2audiobook을 업데이트할 때마다 수정된 conf.py를 백업하고 원본을
다시 되돌릴 수 있습니다. models.py에 대해서도 동일한 과정을 계획해야 합니다. 자신만의 커스텀 모델을
공식 미세 조정된 ebook2audiobook 모델로 만들고 싶다면, 저희에게 연락해 주시면 프리셋 목록에 추가하겠습니다.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## 일반적인 문제:
- 내 NVIDIA/ROCm/XPU/MPS GPU가 감지되지 않나요?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU는 느립니다(서버 SMP CPU에서 더 좋음) 반면 GPU는 거의 실시간 변환이 가능합니다.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (하지만 zero-shot 음성 복제는 없으며 Siri 품질의 음성이지만 cpu에서 훨씬 빠릅니다).
- "종속성 문제가 있습니다" - 그냥 docker를 사용하세요, 완전히 독립적이며 headless 모드가 있습니다,
   자세한 정보는 docker run 명령 끝에 `--help` 매개변수를 추가하세요.
- "오디오가 잘리는 문제가 있습니다!" - 이에 대해 ISSUE를 작성해 주세요,
   저희는 모든 언어를 구사하지 못하며 문장 분할 로직을 미세 조정하기 위해 사용자의 조언이 필요합니다.😊

## ***** 로드맵 *****
- 모든 기능이 공개 기여에 열려 있습니다 ⭐
- 모델 개선을 돕기 위해 지원 언어 중 하나를 구사하는 사람들의 모든 도움 ⭐
- [x] 변환을 시작하기 전에 블록/챕터 미리 보기
- [ ] 정밀한 텍스트 변경을 위해 변환된 문장 단위로 편집
- [x] 음성, 멈춤, 중단 및 추가 변경을 위한 SML 태그 통합 
- [x] 다양한 언어로 된 -h -help 매개변수 정보
- [x] PDF / JPG / BMP / PNG / TIFF용 OCR 스캔
- [x] 노트북 폴더 [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] 중국어 텍스트 분할이 단어를 분리하지 않도록 하고 멈춤 타이밍 개선 [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle 노트북
- [x] Google Colab 노트북
- [ ] Audiobookshelf 통합
- [ ] [iOS 앱 만들기](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [android 앱 만들기](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### 추가 옵션
- [x] 전자책 번역 옵션
- [x] 출력 형식 선택
- [x] 일괄 전자책 폴더
- [x] 멀티프로세싱 변환
- [x] 일괄 전자책 폴더 변환
- [x] GPU 장치 감지
- [x] 업로드된 음성 복제를 위해 모든 참조 오디오의 노이즈 제거,
- [x] 커스텀 모델 업로드(현재로서는 XTTSv2만. 요청 시 추가)
- [ ] 최소한 xttsv2, fairseq, vits, piper용 유럽 포르투갈어 언어 모델 추가(도움 환영)
- [ ] 최소한 xttsv2, fairseq, vits, piper용 신디어 언어 모델 추가(도움 환영)

#### TTS 엔진
- [x] XTTSv2
- [x] 나무껍질
- [x] 페어섹
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] 땅거북과
- [x] GlowTTS
- [x] 바람등칡속
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fish-speech (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] 초음파 (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] 스타일-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Readme 번역
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

#### 🐍 OS 호환성
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## 모델 학습 등을 위한 추가적인 오버킬(지원되는 모든 Coqui-tts 모델과 piper-tts를 하나의 쉬운 명령으로) 
- 이에 관한 정보는 @DrewThomasson, 그가 현재 이것의 개발을 진행하고 있습니다, [작업 중인 저장소는 여기](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] ljspeech 형식의 학습 레시피에서 모든 coqui-tts 모델을 위한 사용하기 쉬운 학습 gui 만들기 [coqui tts에서 여기](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## 기여자를 위한 Python 코드 정규화 정보
- 함수와 클래스 사이를 제외하고 코드 사이에 빈 줄 없음.
- dict()와 json을 제외한 모든 키에 작은따옴표 사용. dict['key']는 항상 작은따옴표로 호출
- 4칸 들여쓰기, 탭은 전혀 사용 안 함
- 모든 함수와 그 인수 및 반환 값 선언에 대한 엄격한 타이핑
- 인수와 그 타이핑 사이에 공백 없음, 함수, "->", 반환 값 사이에 공백 없음

예시:

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

## 베타 테스트를 위한 하드웨어 기부를 찾습니다
다음과 같이 개발 테스트를 위한 모든 종류의 하드웨어를 받습니다:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson 어떤 식으로든 돕고 싶으시다면! 😃
<!--
## 저희 서비스를 강화하기 위해 GPU를 대여해야 하나요?
- 설문조사가 여기에서 열려 있습니다 https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## 특별히 감사드립니다
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 더 나은 챕터 저장 방법에 대해](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
