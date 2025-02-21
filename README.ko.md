# 📚 ebook2audiobook

전자 책에서 챕터 및 메타 데이터가있는 오디오 북에 이르기까지 CPU/GPU 변환기<br/>Caliber, FFMPEG, XTTSV2, FairSeQ 등 사용. 음성 클로닝 및 +1110 언어를 지원합니다!

> [!중요한]**이 도구는 DRM이 아닌 법적으로 획득 한 eBook 만 사용하기위한 것입니다.**<br>저자는이 소프트웨어의 오용 또는 그 결과 법적 결과에 대해 책임을지지 않습니다.<br>이 도구를 책임감 있고 모든 해당 법률에 따라 사용하십시오.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

ebook2audiobook 개발자 지원에 감사드립니다!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI 인터페이스

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   우리는 구매합니다[아랍어 (아랍어)](./readme/README_AR.md)
-   Zho[중국인](./readme/README_CN.md)
-   A\`a[영어](README.md)
-   SWE[스웨덴어 (스웨덴어)](./readme/README_SWE.md)
-   fas[페르시아어 (페르시아어)](./readme/README_FA.md)
-   그녀[이탈리아어 (이탈리아어)](./readme/README.it.md)

## 목차

-   [ebook2audiobook](#-ebook2audiobook)
-   [특징](#features)
-   [Docker Gui 인터페이스](#docker-gui-interface)
-   [포옹 페이스 스페이스 데모](#huggingface-space-demo)
-   [무료 Google Colab](#free-google-colab)
-   [사전 제작 된 오디오 데모](#demos)
-   [지원되는 언어](#supported-languages)
-   [요구 사항](#hardware-requirements)
-   [설치 지침](#installation-instructions)
-   [용법](#launching-gradio-web-interface)
    -   [Gradio 웹 인터페이스 시작](#launching-gradio-web-interface)
    -   [기본적인 헤드리스 사용](#basic--usage)
    -   [헤드리스 사용자 정의 XTTS 모델 사용](#example-of-custom-model-zip-upload)
    -   [GPU 임대](#renting-a-gpu)
    -   [명령 출력을 도와줍니다](#help-command-output)
-   [미세 조정 된 TTS 모델](#fine-tuned-tts-models)
    -   [미세 조정 된 TTS 모델 수집 용](#fine-tuned-tts-collection)
-   [Docker 사용](#using-docker)
    -   [도커 런](#running-the-docker-container)
    -   [도커 빌드](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [도커 헤드리스 가이드](#docker-headless-guide)
    -   [도커 컨테이너 파일 위치](#docker-container-file-locations)
    -   [일반적인 도커 문제](#common-docker-issues)
-   [지원되는 eBook 형식](#supported-ebook-formats)
-   [산출](#output)
-   [일반적인 문제](#common-issues)
-   [특별한 감사](#special-thanks)
-   [서버에 가입하십시오!](#join-our--server)
-   [유산](#legacy-v10)
-   [목차](#table-of-contents)

## 특징

-   📖 eBook을 구경으로 텍스트 형식으로 변환합니다.
-   📚 eBook을 정리 된 오디오를 위해 챕터로 나눕니다.
-   🎙️ 고품질 텍스트 음성[coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)그리고[페어 세크](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(더 많은).
-   자신의 음성 파일로 선택적인 음성 복제.
-   🌍 ++1110 언어를 지원합니다 (기본적으로 영어).[지원되는 언어 목록](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   4GB RAM에서 실행하도록 설계되었습니다.

## [포옹 페이스 스페이스 데모](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingface Space는 무료 CPU 계층에서 실행되므로 매우 느리거나 시간 초과를 기대하십시오. 거대한 파일을주지 마십시오.
-   공간을 복제하거나 로컬로 실행하는 것이 가장 좋습니다.

## 무료 Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## 지원되는 언어

-   **아랍어 (ARA)**
-   **중국어 (ZH)**
-   **체코 (CES)**
-   **크로아티아 (HRV)**
-   **네덜란드어 (NLD)**
-   **영어 (Eng)**
-   **프랑스어 (From)**
-   **독일어 (DEU)**
-   **아님 (Hin)**
-   **헝가리어 (AM)**
-   **이탈리아 (ITA)**
-   **일본어 (JPN)**
-   **한국 (COR)**
-   **광택 (pol)**
-   **포르투갈어 (POR)**
-   **러시아어 (RUS)**
-   **스페인어 (스파)**
-   **터키어 (라운드)**
-   **베트남 (Vie)**
-   [**FairSeq를 통한 +1100 언어**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## 하드웨어 요구 사항

-   4GB RAM 최소값, 8GB 권장
-   Windows에서 실행중인 가상화 활성화 (Docker 만 해당)
-   CPU, GPU (권장), MPS (아직 최적화되지 않고 CPU보다 느리게 될 수 있음) 호환

> [!중요한]**설치 또는 버그 문제를 게시하기 전에 열린 및 폐쇄 된 문제 탭에 신중하게 검색<br>귀하의 문제가 아직 존재하지 않는지 확인하십시오.**

> [!메모]**장, 단락, 서문 등과 같은 표준 구조가 부족합니다.<br>먼저 오디오에서 변환하고 싶지 않은 텍스트를 수동으로 제거해야합니다.**

### 설치 지침

1.  **복제 레포**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Gradio 웹 인터페이스 시작

1.  **ebook2audiobook를 실행하십시오**:
    -   **Linux/MacOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **창**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **웹 앱을 엽니 다**: 터미널에 제공된 URL을 클릭하여 웹 앱에 액세스하고 eBook을 변환합니다.
3.  **공개 링크 용**:`python app.py --share`(모든 OS)`./ebook2audiobook.sh --share`(Linux/MacOS)`ebook2audiobook.cmd --share`(창)

> [!중요한]**스크립트가 중지되고 다시 실행되면 Gradio GUI 인터페이스를 새로 고침해야합니다.<br>웹 페이지가 새 연결 소켓에 다시 연결되도록합니다.**

### 기본 사용

-   **Linux/MacOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **창**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--ebook]**: eBook 파일로가는 경로.
-   **[--목소리]**: 음성 복제 파일 경로 (선택 사항).
-   **[--언어]**: ISO-639-3의 언어 코드 (즉, 이탈리아의 경우 ITA, 영어, 독일어 용 DEU ...).<br>기본 언어는 ENG이고 -언어는 ./lib/lang.py로 설정된 기본 언어의 경우 선택 사항입니다.<br>ISO-639-1 2 문자 코드도 지원됩니다.

### 사용자 정의 모델 zip 업로드의 예

(필수 모델 파일을 포함하는 .zip 파일이어야합니다.

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **창**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custion_model_path>**: 경로`model_name.zip`파일,
        TTS 엔진에 따라 모든 필수 파일을 포함해야합니다.<br>(./lib/models.py 참조).

### 사용할 모든 매개 변수 목록이있는 자세한 안내서

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **창**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **또는 모든 OS에 대해**
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

참고 : Gradio/GUI 모드에서 실행중인 변환을 취소하려면 클릭하십시오.[엑스]eBook 업로드 구성 요소에서

### Docker 사용

Docker를 사용하여 eBook을 오디오 북 컨버터로 실행할 수도 있습니다. 
이 방법은 다양한 환경에서 일관성을 보장하고 설정을 단순화합니다.

#### Docker 컨테이너를 실행합니다

Docker 컨테이너를 실행하고 Gradio 인터페이스를 시작하려면 다음 명령을 사용하십시오.

\-CPU 와만 런

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-GPU 속도를 가진 런 (nvidia 호환 가능)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### 도커 컨테이너 제작

-   명령으로 docker 이미지를 빌드 할 수 있습니다.

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

이 명령은 포트 7860에서 Gradio 인터페이스를 시작합니다. (LocalHost : 7860)

-   더 많은 옵션을 위해 매개 변수를 추가하십시오`--help`

## 도커 컨테이너 파일 위치

모든 ebook2audiobooks는 기본 dir를 갖습니다`/home/user/app/`예를 들어:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## 도커 헤드리스 가이드

먼저 최신의 도커 당기기

```bash
docker pull athomasson2/ebook2audiobook
```

-   이것을 실행하기 전에 현재 DIR에서 "Input-Folder"라는 Dir를 만들어야합니다.
    링크 될 것입니다. 이것은 Docker 이미지에 대한 입력 파일을 넣을 수있는 곳입니다.

```bash
mkdir input-folder && mkdir Audiobooks
```

-   아래 명령에서 스왑 아웃**your_input_file.txt**입력 파일의 이름으로

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   그리고 그게되어야합니다!
-   출력 오디오 북은 오디오 북 폴더에도 있습니다.
    당신의 지역 dir에서 당신은이 docker 명령을

## 다른 매개 변수에 대한 도움말 명령을 얻으려면이 프로그램이이를 실행할 수 있습니다.

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

그리고 그것은 이것을 출력 할 것입니다[명령 출력을 도와줍니다](#help-command-output)

### Docker Compose

이 프로젝트는 Docker Compose를 사용하여 로컬로 실행합니다. GPU 지원을 활성화 또는 비활성화 할 수 있습니다 
중 하나를 설정하여`*gpu-enabled`또는`*gpu-disabled`~에`docker-compose.yml`

#### 실행하기위한 단계

1.  **저장소를 복제하십시오**(아직하지 않은 경우) :
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **GPU 지원 설정 (기본적으로 비활성화)**GPU 지원을 활성화하려면 수정하십시오`docker-compose.yml`그리고 변화`*gpu-disabled`에게`*gpu-enabled`
3.  **서비스 시작 :**
    ```bash
    docker-compose up -d
    ```
4.  **서비스 액세스 :**이 서비스는 http : // localhost : 7860에서 제공됩니다.

### Docker Gui 인터페이스

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## GPU 임대

그것을 실행할 하드웨어가 없거나 GPU를 빌려고 싶습니까?

#### Hugginface 공간을 복제하고 GPU를 시간당 약 $ 0.40에 대여 할 수 있습니다.

[포옹 페이스 스페이스 데모](#huggingface-space-demo)

#### 또는 Google Colab을 무료로 사용해보십시오!

(Google Colab을 엉망으로 만들지 않은 후 시간이 걸릴 것입니다.)[무료 Google Colab](#free-google-colab)

## 일반적인 도커 문제

-   Docker는 미세 조정 모델을 다운로드합니다.
    (이것은 모든 컴퓨터에서 발생하는 것은 아니지만 일부는이 문제에 실행되는 것 같습니다)
    진행률 표시 줄을 비활성화하는 것은 문제를 해결하는 것으로 보입니다.
    논의 된대로[여기 #191에서](https://github.com/DrewThomasson/ebook2audiobook/issues/191)이 수정 사항을 추가하는 예`docker run`명령

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## 미세 조정 된 TTS 모델

이 repo로 자신의 XTTS 모델을 쉽게 미세 조정할 수 있습니다.[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

GPU를 쉽게 빌리려면이 huggingface를 복제 할 수도 있습니다.[xtts-finetune-webui 공간](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

훈련 데이터를 쉽게 제거하는 데 사용할 수있는 공간[Denoise Huggingface 공간](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### 미세 조정 된 TTS 컬렉션

이미 미세 조정 된 TTS 모델 컬렉션을 찾으려면
방문하다[이 포옹 얼굴 링크](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:

## 시민

**비오는 날 목소리**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## 지원되는 eBook 형식

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **최상의 결과**:`.epub`또는`.mobi`자동 챕터 감지

## 산출

-   a`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`메타 데이터 및 챕터가있는 파일 (.lib/conf.py로 설정) 파일.
-   **예**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## 일반적인 문제 :

-   CPU는 느리지 않으며 (서버 SMP CPU에서는 더 좋습니다) NVIDIA GPU는 거의 실시간 변환을 가질 수 있습니다.[이것에 대한 토론](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)더 빠른 다국어 생성을 위해 다른 사람을 제안 할 것입니다[Piper-Tts를 사용하는 프로젝트](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)대신에
    (하지만 샷 음성 복제는 없으며 Siri 품질의 음성이지만 CPU에서는 훨씬 빠릅니다).
-   "나는 종속성 문제가있다" - Docker를 사용하여 완전히 자체적으로 포함되어 있으며 헤드리스 모드가 있습니다.
     추가하다`--help`자세한 내용은 Docker Run 명령의 끝에있는 매개 변수입니다.
-   "나는 잘린 오디오 문제를 받고있다!" -이 문제를 제발하십시오.
     우리는 모든 언어를 말하지 않고 문장 분할 논리를 미세 조정하기 위해 사용자의 조언이 필요합니다.

## 도움이 필요한 것! 🙌

## [전체 목록은 여기에서 찾을 수 있습니다](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   적절한 문장 분할 방법을 돕기 위해 지원되는 언어를 사용하는 사람들의 도움
-   잠재적으로 여러 언어에 대한 readme 안내서를 만들 수 있습니다 (내가 아는 유일한 언어는 영어이기 때문에)

## 특별한 감사

-   **요리 TT**:[coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **구경**:[캘리버 웹 사이트](https://calibre-ebook.com)
-   **ffmpeg**:[FFMPEG 웹 사이트](https://ffmpeg.org)
-   [더 나은 장 저장 방법을위한 @shakenbake15](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [레거시 v1.0](legacy/v1.0)

코드를 볼 수 있습니다[여기](legacy/v1.0).

## 서버에 가입하십시오!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
