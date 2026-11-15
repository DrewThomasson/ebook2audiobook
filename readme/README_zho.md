<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

CPU/GPU转换器从电子书转换为带有章节和元数据的有声读物<br/>
使用高级TTS引擎等等。<br/>
支持语音克隆和1696种语言！
> 重要
**此工具仅适用于非DRM、合法获得的电子书。** <br>
作者对本软件的任何滥用或由此产生的任何法律后果概不负责。<br>
请负责任地使用此工具，并遵守所有适用法律。

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### 感谢支持ebook2audiobook开发者！
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### 本地运行
说明 [![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### 远程运行
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### GUI界面
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>单击以查看Web GUI的图像</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
## 演示

**新建默认语音演示**

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>更多演示</summary>

**ASMR语音**

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**雨天之声**

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett Voice**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David Attenborough之声**

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**示例**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

<a id="table-of-contents"></a>
## 目录
- [ebook2audiobook](#ebook2audiobook)
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
- [Contributing](#contributing)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


<a id="features"></a>
## 特点
- 🔧 **支持的TTS引擎** ： `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **转换多种文件格式** ： `.epub`、`.mobi`、`.azw3`、`.fb2`、`.lrf`、`.rb`、`.snb`、`.tcr`、`.pdf`、`.txt`、`.rtf`、`.doc`、`.docx`、`.html`、`.odt`、`.azw`、`.tiff`、`.tif`、`.png`、`.jpg`、`.jpeg`、`.bmp`、 `.zip`
- 💻 **TextArea**直接转换音频中的短文本
- 🔍 **OCR扫描**用于将文本页面作为图像的文件
- 🔊 **高质量的文本转语音**从近乎实时到近乎真实的语音
- 🗣️ **可选语音克隆**使用您自己的语音文件
- 🌐 **支持1696种语言** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **低资源友好** —运行于**2 GB RAM/1 GB VRAM （最低）**
- 🎵 **有声读物输出格式** ：单声道或立体声 `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **支持SML标签** —精细控制中断、暂停、语音切换等([see below](#sml-tags-available))
- 🧩 **可选的自定义模型**使用您自己的训练模型（ XTTSv2、VITS、FAIRSEQ、PIPER等）
- 🎛️ **由 E2A 团队训练的微调预设模型**<br/>
     <i> （如果您需要其他微调模型，或者您想将您的模型分享到官方预设列表，请联系我们）</i>


<a id="hardware-requirements"></a>
##  硬件要求：
- 最少2GB内存，建议8GB。
- 最少1GB VRAM ，建议4GB。
- 如果在Windows上运行，则虚拟化已启用（仅限Docker ）。
- CPU、XPU （英特尔、AMD、ARM ） *。
- CUDA、ROCm、JETSON
- MPS （苹果硅CPU ）

*<i>现代TTS引擎在CPU上非常慢，因此请使用较低质量的TTS ，如YourTTS、Tacotron2等。</i>

<a id="supported-languages"></a>
## 支持的语言
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## 支持的电子书格式
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **最佳结果** ： `.epub` 或者 `.mobi` 用于自动章节检测

<a id="output-and-process-formats"></a>
## 输出和过程格式
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- 过程格式可以在lib/conf.py中更改

## SML标签可用
- `[break]` —静音（随机范围**0.3–0.6秒** ）
- `[pause]` —静音（随机范围**1.0–1.6秒** ）
- `[pause:N]` —固定暂停（ **N秒** ）
- `[voice:/path/to/voice/file]...[/voice]` —从GUI/CLI从默认或所选语音切换语音
- `[emotion:sadness]...[/emotion]` — 仅限 Zonos：为一段文字指定情绪（幸福、悲伤、厌恶、恐惧、惊讶、愤怒、其他、中性），或像 `[emotion:sadness=0.7,neutral=0.3]` 这样的混合；其他引擎会忽略它

**查看我们的另一个专门用于在您的电子书中自动添加SML的存储库- > [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> 重要
**在发布安装或错误问题之前，请仔细搜索已打开和已关闭的问题选项卡<br>
以确保您的问题不存在。**

注
**EPUB格式缺少任何标准结构，如章节、段落、前言等。<br>
因此，您应该首先手动删除任何不想在音频中转换的文本。**


<a id="instructions"></a>
### 使用说明
1. **克隆仓库**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **安装/运行ebook2audiobook** ：

   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
     <i>MacOS 用户注意：会安装 homebrew 来安装缺失的程序。</i>
     
   - **Mac启动器**
     双击 `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     或
     双击 `ebook2audiobook.cmd`

     <i>Windows 用户注意：会安装 scoop，以便在无需管理员权限的情况下安装缺失的程序。</i>
   
1. **打开Web应用程序** ：单击终端中提供的URL以访问Web应用程序并转换电子书。`http://localhost:7860/`
2. **对于公开链接** ：
   `./ebook2audiobook.command --share` （ Linux/MacOS ）
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share`（所有操作系统，仅安装一次，并使用其 python_env 文件夹中的 Python）

> 重要
**如果脚本停止并再次运行，则需要刷新gradio GUI界面<br>
让网页重新连接到新的连接套接字。**

<a id="basic-usage"></a>
### 基本用法
   - **Linux/MacOS** ：
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]** ：电子书文件的路径
  - **[--voice]** ：语音克隆文件路径（可选）
  - **[--language]** ： ISO-639-3中的语言代码（即： ita代表意大利语， eng代表英语， deu代表德语... ）。<br>
    默认语言为eng ，对于./lib/lang.py中设置的默认语言， --language是可选的。<br>
    还支持ISO-639-1 2字母代码。


<a id="example-of-custom-model-zip-upload"></a>
###  自定义模型 Zip 上传示例
  （必须是包含必需模型文件的 .zip 文件。XTTSv2 示例：config.json、model.pth、vocab.json 和 ref.wav）
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>注意：自定义模型中的 ref.wav 始终是转换所使用的声音</i>
     
- **<custom_model_path>**：`model_name.zip` 文件的路径，
      该文件必须包含（取决于 TTS 引擎）所有必需文件<br>
      （参见./lib/models.py ）。

### 详细指南及所有可用参数列表
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **或适用于所有操作系统**
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

注意：在gradio/gui模式下，要取消正在运行的转化，只需单击电子书上传组件中的[X]即可。
提示：如果需要更长的停顿，请添加 '[pause:3]' 表示 3 秒，以此类推。

<a id="docker"></a>
### Docker
1. **克隆仓库**：
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **构建容器**
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
4. **运行容器：**
```bash
Docker run image:
    Gradio/GUI:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc...]
    Headless mode:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
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
- 注意：MPS 未在 Docker 中开放，因此必须使用 CPU
- 注意：命名卷 `e2a_venvs` 会将 TTS 引擎保留在各自的 venv 中（GPT-SoVITS、Zonos、OmniVoice、F5-TTS、Orpheus、Spark-TTS、ChatTTS、OpenVoice、MeloTTS、CSM 等），
  在多次运行容器之间保持不变，因此不会每次都重新安装。如需重置：`docker volume rm e2a_venvs`

<a id="tools"></a>
## 工具
独立工具，使用 e2a 自带的 Python 运行（`python_env`，在首次启动 e2a 时创建）。

<a id="preload-models"></a>
### 为离线安装预加载模型：`tools/preload_models.py`
将 e2a 使用的所有模型（TTS 引擎及其微调模型、语音转换、stanza、pyannote、demucs、
音乐间奏、argos-translate 语言包、tesseract 数据、jieba 以及声音）下载到一个文件夹中，其结构
与 `./models` 完全相同，例如 U 盘。在离线机器上，将该文件夹复制到 e2a 的 `./models`，
并将写在其旁边的 `voices` 文件夹复制到 e2a 的 `./voices`。
每个完成的任务都会记录在 `<models_dir>/.e2a_downloads.json` 中：再次运行时会跳过已完成的任务，
并在删除部分文件后重新开始被中断的任务（ctrl-c、崩溃、U 盘被拔出）。
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` 列出所有任务及其状态（已完成、已中断、待处理），不下载任何内容。

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
### 在 e2a 之外翻译电子书：`tools/translate_ebook.sh` / `tools/translate_ebook.cmd`
将 EPUB/AZW3 文件、整个文件夹（`-r` 包含其子文件夹）或路径列表（`@list.txt`）
离线翻译为电子书，使用的是随附于以下位置的 Argos Translate calibre 插件：
`tools/argostranslate-calibre-plugin.zip`。独立于有声书转换：它只输出电子书。
它需要 calibre（e2a 本身已需要），并使用 e2a 的 `python_env` 和 argos-translate 语言包运行：
e2a 已使用的语言对不会重复下载，缺失的语言对会在首次使用时下载。
插件会在首次使用时安装到 e2a 自己的 calibre 配置目录（`./run`）中，不会改动你的 calibre。
`--to fra,ara,spa` 一次翻译成多种语言，每种语言一本电子书；`--to all` 则翻译成源语言
可达的所有语言（`--from`，否则为每本书自身的语言；使用 `--no_download` 时仅限已安装的语言对）。
`--list --from eng` 列出英语可以翻译成的语言（已安装、可下载，或对于其他源语言
经由英语中转）。
calibre 的 `ebook-convert` 可读取的其他格式（PDF、DOCX、MOBI、TXT 等）会在翻译第一种语言之前
先转换为 EPUB（仅一次），再按 EPUB 翻译：当文件未标明语言时（PDF 和 TXT 常常如此）需要 `--from`。
未指定 `-o` 或 `--output_dir` 时，每个译本都会以 `<name>.<lang>.<ext>` 保存在原书旁边，
已有译本的书会被跳过（使用 `--overwrite` 重新翻译）。
`tools/` 文件夹中的启动脚本会用 `python_env` 运行 `tools/translate_ebook.py`，无需激活任何环境，
可在任意文件夹中运行（相对路径以启动位置为准）：
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - 或直接使用 `python_env` 的 Python：`./python_env/bin/python tools/translate_ebook.py ...`
     （Windows：`python_env\Scripts\python.exe tools\translate_ebook.py ...`）。如果用其他 Python 启动，
     脚本会自动改用 `python_env` 的 Python 重新启动。
   - **Docker**：在 e2a 容器内运行，例如 `docker exec -it <container> python3 tools/translate_ebook.py ...`
     路径需使用容器内可见的路径。
   - **速度**：argostranslate 使用其自身的默认设置（由 CTranslate2 选择线程数和最快的计算类型，
     CPU 上为 int8），而不是 e2a 的单线程 float32。可设置 `ARGOS_INTRA_THREADS` 或 `ARGOS_COMPUTE_TYPE` 进行覆盖。

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

<a id="cloned-voices"></a>
## 克隆的声音
您可以上传任何支持的音频格式的任何语音音频，理想的持续时间约为1至5分钟。
无论录音的背景是嘈杂的还是播放的音乐， E2A都会为您清理声音。

内置克隆语音列表主要为英文。如果您需要其他语言的声音才能正式
添加到列表中，请联系我们，我们将在审核后添加它们。

<a id="fine-tuned-tts-models"></a>
## 微调TTS型号
<a id="fine-tune-your-own-tts-model"></a>
#### 微调您自己的TTS模型

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### 去噪训练数据

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### 微调TTS系列

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

对于XTTSv2自定义模型，语音参考的REF音频剪辑是必需的：

## 您自己的Ebook2Audiobook定制
您可以自由修改libs/conf.py以添加或删除您想要的设置。如果您打算这样做，只需
原始conf.py的副本，因此在每次ebook2audiobook更新时，您将备份修改后的conf.py并
回到原来的。您必须为models.py规划相同的流程。如果您想制作自己的自定义模型
作为官方ebook2audiobook微调模型，因此请联系我们，我们会将其添加到预设列表中。

<a id="reverting-to-older-versions"></a>
## 回退到旧版本
发布版本可在此找到 -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## 共同问题：
- 未检测到我的NVIDIA/ROCm/XPU/MPS GPU ？ - > [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU速度慢（在服务器smp CPU上更好） ，而GPU几乎可以实现实时转换。
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   （虽然它没有零拍声音克隆，并且是Siri质量的声音，但在CPU上要快得多）。
- "我有依赖问题" -只需使用docker ，它完全自包含并且具有无头模式，
   在docker run命令末尾添加`--help`参数以获取更多信息。
- “我收到了截断的音频问题！" -请提出这个问题，
   我们不会说所有的语言，需要用户的建议来微调句子分割逻辑。😊

## 路线图
- 所有功能均向公众开放 ⭐
- 使用任何支持语言的人员提供的任何帮助，以帮助我们改进模型 ⭐
- [x] 在开始转换之前预览模块/章节
- [x] 按为手术文本更改转换的句子编辑
- [x] 生成音乐插曲、插曲和结尾；编辑插曲和结尾
- [x] SML标记语音、暂停、中断和更多更改的集成
- [x] -h -help不同语言的参数信息
- [x] PDF/JPG/BMP/PNG/TIFF的OCR扫描
- [x] 笔记本文件夹[Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] 使中文文本拆分不拆分单词，提高暂停时间[Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker撰写
- [x] Podman撰写
- [x] Kaggle笔记本
- [x] Google Colab笔记本
- [x] 有声书架集成
- [x] 电子书翻译选项
- [x] 输出格式选择
- [x] 多处理转换
- [x] 批量电子书文件夹转换
- [x] 设备检测
- [x] 对语音克隆上传的任何背景参考音频进行降噪
- [x] 自定义微调模型上传

#### 用户请求
- [ ] 至少为xttsv2、fairseq、vits、piper添加欧洲葡萄牙语语言模型（帮助欢迎）
- [ ] 至少为xttsv2、fairseq、vits、piper添加信德语语言模型（欢迎使用）

#### TTS引擎
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio/FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] 鱼语/鱼声(https://github.com/fishaudio/fish-speech)[cite: 1]
- [x] Higgs Audio TTS (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] Maya1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1]
- [x] F5-TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1]
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1]
- [x] Voxtral TTS (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] Chatterbox (https://github.com/resemble-ai/chatterbox)[cite: 1]
- [x] CosyVoice/CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1]
- [x] Index-tts/Index TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] 孔子4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] 点TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] 喜鹊TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] MOSS TTS Local/Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS/NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Pocket TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] 声子级(https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] 乌龟(https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] BARK (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM https://github.com/SesameAILabs/csm)

#### 自述文件翻译
- [x] 阿拉伯语(ara)
- [x] Chinese (zho)
- [x] English (eng)
- [x] Spanish (spa)
- [x] French (fra)
- [x] 德语(deu)
- [x] Italian (ita)
- [x] Portuguese (por)
- [x] Polish (pol)
- [x] 土耳其语(TUR)
- [x] Russian (rus)
- [x] Dutch (nld)
- [x] 捷克语（ ces ）
- [x] Japanese (jpn)
- [x] Hindi (hin)
- [x] Bengali (ben)
- [x] 匈牙利语(HUN)
- [x] Korean (kor)
- [x] 越南语（ VIE ）
- [x] Swedish (swe)
- [x] 波斯语(fas)
- [x] 约鲁巴语（ yor ）
- [x] 斯瓦希里语(swa)
- [x] 印尼语（印尼）
- [x] Slovak (slk)
- [x] 克罗地亚语(hrv)

#### 💻 操作系统兼容性
- [x] 🪟 Windows x86
- [x] 🪟 ARM窗口
- [x] 🍎 Mac英特尔x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM Linux

**********

<a id="contributing"></a>
## 贡献
在打开问题或拉取请求之前，请阅读[CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md) ： Python代码规范化规则，
分支和拉取请求工作流程， GUI图例和自述文件翻译，添加TTS引擎，测试。

## 想要为Beta测试捐赠硬件
我们接受任何类型的硬件来测试我们的开发，例如：
- Nvidia支持CUDA > = 11.8
- XPU英特尔卡
- 支持ROCm的ROCm AMD卡> = 5.7

如果您想帮忙，请@ DrewThomasson ！ 😃
<!--
## 您是否需要租用GPU来提升我们的服务？
- 此处打开了一项民意调查https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## 信用
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) --用于文本转语音的深度学习工具包，在研究和生产中经过实战测试。
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) --快速和本地神经文本转语音引擎。
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- Zonos2的ggml推理代码。
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) --音频模型的一体化、纯C + +推理引擎，由ggml提供支持。

<a id="special-thanks"></a>
## 特别鸣谢
对于所有财务和代码贡献者，每项贡献和建议都有助于提高E2A的质量。