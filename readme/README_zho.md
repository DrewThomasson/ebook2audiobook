# 📚 ebook2audiobook (E2A)
将电子书转换为带有章节和元数据的有声书的 CPU/GPU 转换器<br/>
使用先进的 TTS 引擎等。<br/>
支持语音克隆和 1158 种语言！
> [!IMPORTANT]
**本工具仅供与合法获取的无 DRM 电子书一起使用。** <br>
作者对本软件的任何滥用或由此产生的任何法律后果概不负责。 <br>
请负责任地使用本工具，并遵守所有适用的法律。

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### 感谢您支持 ebook2audiobook 的开发者！
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### 本地运行

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### 远程运行
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### 图形界面（GUI）
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>点击查看 Web GUI 图像</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## 演示

**新默认语音演示**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>更多演示</summary>

**ASMR 语音** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**雨天语音**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**斯嘉丽语音**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**大卫·阿滕伯勒语音** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**示例**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## 目录
- [ebook2audiobook](#-ebook2audiobook)
- [功能](#features)
- [图形界面](#gui-interface)
- [演示](#demos)
- [支持的语言](#supported-languages)
- [最低要求](#hardware-requirements)
- [用法](#instructions)
  - [本地运行](#instructions)
    - [启动 Gradio Web 界面](#instructions)
    - [基本 Headless 用法](#basic-usage)
    - [Headless 自定义 XTTS 模型用法](#example-of-custom-model-zip-upload)
    - [帮助命令输出](#help-command-output)
  - [远程运行](#run-remotely)
  - [Docker](#docker)
    - [运行步骤](#docker)
    - [常见的 Docker 问题](#common-docker-issues)
  
- [微调 TTS 模型](#fine-tuned-tts-models)
  - [微调 TTS 模型集合](#fine-tuned-tts-collection)
  - [训练 XTTSv2](#fine-tune-your-own-xttsv2-model)
- [支持的电子书格式](#supported-ebook-formats)
- [输出格式](#output-and-process-formats)
- [还原到较旧版本](#reverting-to-older-versions)
- [常见问题](#common-issues)
- [特别鸣谢](#special-thanks)
- [目录](#table-of-contents)


## 功能
- 🔧 **支持的 TTS 引擎**： `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **转换多种文件格式**： `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 用于直接将短文本转换为音频的**文本区域**
- 🔍 针对文本页面为图像的文件的 **OCR 扫描**
- 🔊 **高质量文本转语音**，从接近实时到接近真实的语音
- 🗣️ 使用您自己的语音文件进行**可选的语音克隆**
- 🌐 **支持 1158 种语言** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **低资源友好** — 可在 **2 GB RAM / 1 GB VRAM（最低）** 上运行
- 🎵 **有声书输出格式**： mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **支持 SML 标签** — 对中断、停顿、语音切换等进行精细控制 ([see below](#sml-tags-available))
- 🧩 使用您自己训练的模型的**可选自定义模型** (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ 由 E2A 团队训练的**微调预设模型**<br/>
     <i>（如果您需要额外的微调模型，或者如果您想在官方预设列表中分享您自己的模型，请联系我们）</i>


##  硬件要求
- RAM 最低 2GB，推荐 8GB。
- VRAM 最低 1GB，推荐 4GB。
- 在 windows 上运行时启用虚拟化（仅限 Docker）。
- CPU、XPU（intel、AMD、ARM）*。
- CUDA、ROCm、JETSON
- MPS（Apple Silicon CPU）

*<i> 现代 TTS 引擎在 CPU 上非常慢，因此请使用质量较低的 TTS，如 YourTTS、Tacotron2 等。</i>

## 支持的语言
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**此处有 +1130 种语言和方言**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## 支持的电子书格式
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **最佳效果**：使用 `.epub` 或 `.mobi` 进行自动章节检测

## 输出和处理格式
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- 处理格式可在 lib/conf.py 中更改

## 可用的 SML 标签
- `[break]` — 静音（随机范围 **0.3–0.6 sec.**）
- `[pause]` — 静音（随机范围 **1.0–1.6 sec.**）
- `[pause:N]` — 固定停顿（**N sec.**）
- `[voice:/path/to/voice/file]...[/voice]` — 从默认语音或从 GUI/CLI 选择的语音切换语音

**请查看我们另一个专门用于在电子书中自动添加 SML 的仓库 -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**在发布安装或错误问题之前，请仔细搜索打开和已关闭问题的标签页<br>
以确保您的问题尚不存在。**

>[!NOTE]
**EPUB 格式缺乏任何定义什么是章节、段落、前言等的标准结构。<br>
因此，您应该首先手动删除任何不想转换为音频的文本。**


### 说明 
1. **克隆仓库**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **安装 / 运行 ebook2audiobook**：

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>macOS 用户注意：将安装 homebrew 以安装缺失的程序。</i>
     
   - **Mac 启动器**  
     双击 `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     或
     双击 `ebook2audiobook.cmd`

     <i>Windows 用户注意：将安装 scoop 以在没有管理员权限的情况下安装缺失的程序。</i>
   
1. **打开 Web 应用**：点击终端中提供的 URL，以访问 Web 应用并转换电子书。 `http://localhost:7860/`
2. **获取公共链接**：
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**如果脚本被停止并再次运行，您需要刷新您的 Gradio GUI 界面<br>
以便网页能够重新连接到新的连接套接字。**

### 基本用法
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**：电子书文件的路径
  - **[--voice]**：语音克隆文件路径（可选）
  - **[--language]**：ISO-639-3 格式的语言代码（即：意大利语为 ita，英语为 eng，德语为 deu...）。<br>
    默认语言为 eng，对于 ./lib/lang.py 中设置的默认语言，--language 是可选的。<br>
    也支持 2 个字母的 ISO-639-1 代码。


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
     <i>注意：您的自定义模型的 ref.wav 始终是为转换所选择的语音</i>
     
- **<custom_model_path>**：`model_name.zip` 文件的路径，
      该文件必须（根据 tts 引擎）包含所有必需文件<br>
      （参见 ./lib/models.py）。

### 有关包含所有可用参数列表的详细指南
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

注意：在 gradio/gui 模式下，要取消正在进行的转换，只需点击电子书上传组件的 [X] 即可。
提示：如果需要稍长的停顿，请添加 '[pause:3]' 表示 3 秒等。

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
- 注意：MPS 未在 docker 中公开，因此必须使用 CPU
  
### 常见的 Docker 问题
- 未检测到我的 NVIDIA GPU？？ -> [GPU 问题 Wiki 页面](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## 微调（fine-tuned）TTS 模型
#### 微调您自己的 XTTSv2 模型

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### 训练数据降噪

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### 微调 TTS 模型集合

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

对于自定义 XTTSv2 模型，必须提供语音的参考音频片段：

## 您自己的 Ebook2Audiobook 自定义
您可以自由修改 libs/conf.py 以添加或删除您想要的设置。如果您打算这样做，只需制作
原始 conf.py 的副本，这样在每次更新 ebook2audiobook 时，您可以备份修改后的 conf.py 并恢复
原始文件。您必须为 models.py 计划相同的流程。如果您想将自己的自定义模型
变成官方微调的 ebook2audiobook 模型，请联系我们，我们会将其添加到预设列表中。

## 还原到较旧版本
可以在 -> [此处](https://github.com/DrewThomasson/ebook2audiobook/releases) 找到发行版
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## 常见问题：
- 未检测到我的 NVIDIA/ROCm/XPU/MPS GPU？？ -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU 很慢（在服务器 SMP CPU 上更好），而 GPU 可以实现接近实时的转换。
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   （不过它没有 zero-shot 语音克隆，是 Siri 质量的语音，但在 cpu 上快得多）。
- “我遇到依赖项问题” - 只需使用 docker，它完全独立并具有 headless 模式，
   在 docker run 命令末尾添加 `--help` 参数以获取更多信息。
- “我遇到音频被截断的问题！” - 请就此创建一个 ISSUE，
   我们不会说每种语言，需要用户的建议来微调句子拆分逻辑。😊

## ***** 路线图 *****
- 所有功能均向公众贡献开放 ⭐
- 来自任何说支持语言的人的任何帮助，以帮助我们改进模型 ⭐
- [x] 在开始转换之前预览块/章节
- [ ] 按转换后的句子进行编辑，以进行精准的文本更改
- [x] 用于语音、停顿、中断及更多更改的 SML 标签集成 
- [x] 不同语言的 -h -help 参数信息
- [x] 针对 PDF / JPG / BMP / PNG / TIFF 的 OCR 扫描
- [x] Notebooks 文件夹 [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] 使中文文本拆分不拆分单词并改善停顿时间 [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle Notebook
- [x] Google Colab Notebook
- [ ] [制作 iOS 应用](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [制作 android 应用](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Audiobookshelf 集成

#### 额外选项
- [x] 电子书翻译选项
- [x] 输出格式选择
- [x] 批量电子书文件夹
- [x] 多进程转换
- [x] 批量电子书文件夹转换
- [x] GPU 设备检测
- [x] 为上传的语音克隆对任何参考音频进行降噪，
- [x] 自定义模型上传（目前仅 XTTSv2。更多应需求提供）
- [ ] 至少为 xttsv2、fairseq、vits、piper 添加欧洲葡萄牙语语言模型（欢迎帮助）
- [ ] 至少为 xttsv2、fairseq、vits、piper 添加信德语语言模型（欢迎帮助）

#### TTS 引擎
- [x] XTTSv2
- [x] Bark
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Tortoise
- [x] GlowTTS
- [x] Piper-TTS
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] Kokoro-TTS
- [ ] Orpheus-TTS
- [ ] Zonos
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Style-TTS2
- [ ] GPT-SoVITS
- [ ] F5-TTS (https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/38#issuecomment-2453224267)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] Speedy-Speech
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Align-TTS
- [ ] Delightful-TTS
- [ ] Spark-TTS

#### Readme 翻译
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

#### 🐍 操作系统兼容性
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## 用于训练模型等的额外杀手锏（所有支持的 Coqui-tts 模型和 piper-tts 通过一条简单命令） 
- 有关此信息 @DrewThomasson，他目前正在进行其开发，[正在进行中的仓库在此处](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] 为 ljspeech 格式训练配方中的所有 coqui-tts 模型创建一个易于使用的训练 gui [此处来自 coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## 面向贡献者的 Python 代码规范化信息
- 代码之间没有空行，函数和类之间除外。
- 除 dict() 和 json 外，所有键均使用单引号。dict['key'] 始终用单引号调用
- 4 个空格缩进，完全不使用制表符
- 对所有函数及其参数和返回值声明进行严格类型标注
- 参数与其类型标注之间无空格，函数、“->”和返回值之间无空格

示例：

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

## 征求用于测试版测试的硬件捐赠
我们接受任何类型的硬件来测试我们的开发，例如：
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson 如果您想以任何方式提供帮助！ 😃
<!--
## 您需要租用 GPU 来增强我们的服务吗？
- 此处已开放投票 https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## 特别鸣谢
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 提供了更好的章节保存方法](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
