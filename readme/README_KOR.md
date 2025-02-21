📚 ebook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
전자 책에서 챕터와 메타 데이터가있는 오디오 북에 이르기까지 CPU/GPU 변환기 <br/>
Caliber, FFMPEG, XTTSV2, FairSeQ 등 사용. 음성 클로닝 및 +1110 언어를 지원합니다! [!중요한]
**이 도구는 DRM이 아닌 법적으로 취득한 eBook 만 사용하기위한 것입니다. ** <br>
저자는이 소프트웨어의 오용 또는 그 결과 법적 결과에 대해 책임을지지 않습니다. <br>
이 도구를 책임감 있고 모든 해당 법률에 따라 사용하십시오. [!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! .com/athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [demo_web_gui] (자산/demo_web_gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العررر들도 (아랍어)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文 (중국어)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
SWE [Svenska (Swedish)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
FAS [ر ارسی (페르시아어)] (./ readme/readme_fa.md)


## Table of Contents
[ebook2audiobook] (#-EBook2audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[기능] (#기능)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker Gui 인터페이스] (#docker-gui-interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Huggingface Space Demo] (#Huggingface-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[무료 Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[사전 제작 오디오 데모] (#데모)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[지원되는 언어] (#지원 언어)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[요구 사항] (#하드웨어보고)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[설치 지침] (#설치-통과)
- [Output](#output)
- [Common Issues](#common-issues)
[사용] (##런칭 -gradio-web-interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Gradio Web Interface 시작] (##런칭 -gradio-web-interface)


[기본 헤드리스 사용법] (#BASIC- 사용자)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Headless Custom XTTS 모델 사용] (#CUSTOM-MODEL-ZIP-UPLOAD의 예)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[GPU 임대] (#Renting-A-GPU)


[도움말 명령 출력] (#Help-Command Output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[미세 조정 된 TTS 모델] (#미세 조정 된 TTS- 모델)


[미세 조정 된 TTS 모델 수집] (#미세 조정 TTS- 수집)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Running-the-Docker Container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Building-the-Docker Container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#docker-compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide] (#Docker-Headless-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Docker Container 파일 위치] (#Docker-Container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[일반적인 도커 문제] (#Common-Docker-Issues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[지원되는 eBook 형식] (#supported-ebook-formats)


[출력] (#출력)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[일반적인 문제] (#Common-Issues)


[특별 감사] (#스페셜 감사)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[레거시] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
특징
```bash
📖 eBook을 구경으로 텍스트 형식으로 변환합니다. 📚 eBook을 정리 된 오디오를 위해 챕터로 나눕니다. [coqui xttsv2] (https://huggingface.co/coqui/xtts-v2) 및 [fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ 예/mms) (및 기타). 자신의 음성 파일로 선택적인 음성 복제. 🌍 +1110 언어를 지원합니다 (기본적으로 영어). [지원되는 언어 목록] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

4GB RAM에서 실행하도록 설계되었습니다. [huggingface space demo] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! /ebook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Huggingface Space는 무료 CPU 계층에서 실행되므로 매우 느리거나 시간 초과를 기대하십시오. 거대한 파일을주지 마십시오.
   - **Windows**
     ```bash
공간을 복제하거나 로컬로 실행하는 것이 가장 좋습니다. 무료 Google Colab
     ```
[! 메인/노트북/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
지원되는 언어
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** 아랍어 (ARA) **

> [!IMPORTANT]
** 중국어 (Zho) **
to let the web page reconnect to the new connection socket.**

** 체코 (CES) **
   - **Linux/MacOS**:
     ```bash
** 크로아티아 (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** 네덜란드어 (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** 영어 (ENG) **
     ```
     
** 프랑스어 (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** 독일어 (DEU) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** 헝가리 (Hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** 이탈리아 (ITA) **
     ```
   - **Windows**
** 일본어 (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** 한국 (Kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** 폴란드 (pol) **


** 포르투갈어 (POR) **
   - **Linux/MacOS**
     ```bash
** 러시아어 (RUS) **
     ```
   - **Windows**
** 스페인어 (스파) **
     .\ebook2audiobook.cmd --help
     ```
** 터키 (TUR) **
    ```python
     app.py --help
** 베트남 (Vie) **

<a id="help-command-output"></a>
[** +1100 fairseq를 통한 언어 **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
하드웨어 요구 사항
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4GB RAM 최소값, 8GB 권장
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Windows에서 실행중인 가상화 활성화 (Docker 만 해당)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (권장), MPS (아직 최적화되지 않고 CPU보다 느리게 될 수 있음) 호환

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** 설치 또는 버그 문제를 게시하기 전에 열린 및 폐쇄 된 문제 탭 <br>
당신의 문제가 아직 존재하지 않는지 확인하려면 **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** 장, 단락, 서문 등과 같은 표준 구조가 부족합니다. <br>
먼저 오디오에서 변환하고 싶지 않은 텍스트를 수동으로 제거해야합니다. **

설치 지침

** 복제 레포 **
  --headless            Run the script in headless mode
Gradio 웹 인터페이스 시작
  --ebooks_dir EBOOKS_DIR
** ebook2audiobook 실행 ** :
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/MacOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** 웹 앱 열기 ** : 터미널에 제공된 URL을 클릭하여 웹 앱에 액세스하고 전자 책을 변환합니다. ** 공개 링크의 경우 ** :
`Python app.py -쉐어`(모든 OS)
`./ebook2audiobook.sh ---- 래 (Linux/MacOS)
`ebook2audiobook.cmd -쉐어`(Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!중요한]
** 스크립트가 중지되고 다시 실행되면 Gradio GUI 인터페이스를 새로 고치는 것이 필요합니다 <br>
웹 페이지가 새로운 연결 소켓에 다시 연결하도록하려면. **
                        (Optional) Fine tuned model path. Default is builtin model.
기본 사용
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/MacOS ** :
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-eBook] ** : eBook 파일로가는 경로. ** [-음성] ** : 음성 복제 파일 경로 (선택 사항). ** [-언어] ** : ISO-639-3의 언어 코드 (예 : Ita, Eng의 영어, 영어, 독일어 ...). <br>
기본 언어는 ENG이고 -언어는 ./lib/lang.py에 설정된 기본 언어에 대한 선택 사항입니다. <br>
ISO-639-1 2 문자 코드도 지원됩니다. 사용자 정의 모델 zip 업로드의 예
  --repetition_penalty REPETITION_PENALTY
(필수 모델 파일을 포함하는 .zip 파일이어야합니다.
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/MacOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custion_model_path> ** :`model_name.zip` 파일로가는 경로,
    TTS 엔진에 따라 모든 필수 파일을 포함해야합니다. <br>
    (./lib/models.py 참조). 사용할 모든 매개 변수 목록이있는 자세한 안내서
  --output_dir OUTPUT_DIR
** Linux/MacOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** 또는 모든 OS **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "Help-Command Output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
참고 : Gradio/GUI 모드에서 실행중인 변환을 취소하려면 EBOOK 업로드 구성 요소에서 [X]를 클릭하십시오. Docker 사용
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Docker를 사용하여 eBook을 오디오 북 컨버터로 실행할 수도 있습니다. 이 방법은 다양한 환경에서 일관성을 보장하고 설정을 단순화합니다. Docker 컨테이너를 실행합니다

Docker 컨테이너를 실행하고 Gradio 인터페이스를 시작하려면 다음 명령을 사용하십시오.

### Using Docker
-CPU 와만 런
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
도커 컨테이너 제작

명령으로 docker 이미지를 빌드 할 수 있습니다.
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
이 명령은 포트 7860에서 Gradio 인터페이스를 시작합니다. (LocalHost : 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
더 많은 옵션을 보려면 매개 변수`-help`를 추가하십시오
```


모든 ebook2audiobooks는`/home/user/app/`의 기본 dir를 갖습니다
예를 들어:
`tmp` =`/home/user/app/tmp`
`Audiobooks` =`/home/user/app/audiobooks '
```
도커 헤드리스 가이드
- For more options add the parameter `--help`


## Docker container file locations
이것을 실행하기 전에 현재 DIR에서 "Input-Folder"라는 Dir를 만들어야합니다.
링크 될 것입니다. 이것은 Docker 이미지에 대한 입력 파일을 넣을 수있는 곳입니다.
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
그리고 그게되어야합니다! 출력 오디오 북은 오디오 북 폴더에도 있습니다.
당신의 지역 dir에서 당신은이 docker 명령을
docker pull athomasson2/ebook2audiobook
다른 매개 변수에 대한 도움말 명령을 얻으려면이 프로그램이이를 실행할 수 있습니다.
- Before you do run this you need to create a dir named "input-folder" in your current dir
그리고 그것은 이것을 출력 할 것입니다 
[도움말 명령 출력] (#Help-Command Output)
mkdir input-folder && mkdir Audiobooks
Docker Compose
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
이 프로젝트는 Docker Compose를 사용하여 로컬로 실행합니다. GPU 지원을 활성화 또는 비활성화 할 수 있습니다 
`docker-compose.yml`에서`*gpu-enabled` 또는`*gpu-disabled`를 설정함으로써
    -v $(pwd)/input-folder:/home/user/app/input_folder \
실행 단계
    athomasson2/ebook2audiobook \
** 저장소를 복제하십시오 ** (아직하지 않은 경우) :
```
- And that should be it! 
** GPU 지원 설정 (기본적으로 비활성화) **
GPU 지원을 활성화하려면`docker-compose.yml`을 수정하고`*gpu-disabled`를`*gpu-enabled`로 변경하십시오.


** 서비스 시작 : **

```bash
** 서비스 액세스 : **

```
! [demo_web_gui] (자산/demo_web_gui.gif)
[Help command output](#help-command-output)


그것을 실행할 하드웨어가 없거나 GPU를 빌려고 싶습니까? Hugginface 공간을 복제하고 GPU를 시간당 약 $ 0.40에 대여 할 수 있습니다.
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Huggingface Space Demo] (#Huggingface-Space-Demo)


[무료 Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
일반적인 도커 문제
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker는 미세 조정 모델을 다운로드합니다. (이것은 모든 컴퓨터에서 발생하는 것은 아니지만 일부는이 문제에 실행되는 것 같습니다)
진행률 표시 줄을 비활성화하는 것은 문제를 해결하는 것으로 보입니다.
논의 된 바와 같이 [ #191에서] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
`docker run '명령 에이 수정 사항을 추가하는 예
3. **Start the service:**
미세 조정 된 TTS 모델
    docker-compose up -d
이 repo로 자신의 XTTS 모델을 쉽게 미세 조정할 수 있습니다.
[XTTS-Finetune-webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-Finetune-webui-space] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

훈련 데이터를 쉽게 제거하는 데 사용할 수있는 공간
[Denoise-Huggingface-Space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
미세 조정 된 TTS 컬렉션
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
이미 미세 조정 된 TTS 모델 컬렉션을 찾으려면


## Renting a GPU
시민
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** 비오는 날 목소리 **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough Voice **


지원되는 eBook 형식
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,
`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,
`.snb`,`.cbc`,`.rb`,`.tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** 최상의 결과 ** :`.epub` 또는`.mobi`는 자동 챕터 감지를위한
    -p 7860:7860 athomasson2/ebook2audiobook
산출


! [예] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
You can fine-tune your own xtts model easily with this repo
일반적인 문제 :

CPU는 느리지 않으며 (서버 SMP CPU에서는 더 좋습니다) NVIDIA GPU는 거의 실시간 변환을 가질 수 있습니다. [이것에 대한 토론] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
더 빠른 다국어 생성을 위해 다른 사람을 제안 할 것입니다

(하지만 샷 음성 복제는 없으며 Siri 품질의 음성이지만 CPU에서는 훨씬 빠릅니다). "나는 종속성 문제가있다" - Docker를 사용하여 완전히 자체적으로 포함되어 있으며 헤드리스 모드가 있습니다.
 자세한 내용은 Docker Run 명령의 끝에`-help` 매개 변수를 추가하십시오. "나는 잘린 오디오 문제를 받고있다!" -이 문제를 제발하십시오.

### Fine Tuned TTS Collection
도움이 필요한 것! 🙌
[전체 목록은 여기에서 찾을 수 있습니다] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
잠재적으로 여러 언어에 대한 readme 안내서를 만들 수 있습니다 (내가 아는 유일한 언어는 영어 😔 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** coqui tts ** : [coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg ** : [ffmpeg 웹 사이트] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[레거시 v1.0] (레거시/v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
코드 [여기] (레거시/v1.0)을 볼 수 있습니다. 서버에 가입하십시오! [!