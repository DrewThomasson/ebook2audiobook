📚ebook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
CPU/GPU转换器从电子书到有声读物的章节和元数据<br/>
使用Caliber，FFMPEG，XTTSV2，FairSeq等。支持语音克隆和+1110语言！ [！重要的]
**该工具旨在与非DRM，仅合法获得的电子书一起使用。** <br>
作者对滥用此软件或任何由此产生的法律后果概不负责。 <br>
负责任地使用此工具，并按照所有适用的法律使用。 [！

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[！ .com/athomasson2）
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


！[demo_web_gui]（资产/demo_web_gui.gif）
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [البر吊（阿拉伯语）]（./ readme/readme_ar.md）
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文（中文）]（./ readme/readme_cn.md）
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
SWE [svenska（瑞典）]（./ readme/readme_swe.md）
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
FAS [فف氨基（波斯）]（./ readme/readme_fa.md）


## Table of Contents
[ebook2audiobook]（＃ -  ebook2audiobook）
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[功能]（＃功能）
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[docker gui界面]（＃docker-gui-interface）
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[huggingface太空演示]（＃huggingface空间demo）
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[免费的Google Colab]（＃自由谷歌舞）
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[预制音频演示]（＃演示）
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[支持语言]（＃支持语言）
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[需求]（＃硬件引用）
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[安装说明]（＃安装 - 指令）
- [Output](#output)
- [Common Issues](#common-issues)
[用法]（＃启动Gradio-Web-Interface）
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[启动Gradio Web界面]（＃启动Gradio-Web-Interface）


[基本无头的用法]（＃BASIC-- USAGE）
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[无头自定义XTTS模型使用]（＃custom-model-zip-upload示例）
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[租用GPU]（＃租用-A-GPU）


[help命令输出]（＃help-command-output）
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[微调TTS型号]（＃微调TTS模型）


[用于收集微调TTS型号]（＃微调TTS收集）
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run]（＃Running-the-Docker-container）
- **Czech (ces)**
- **Croatian (hrv)**
[docker build]（＃building-the-the-docker-container）
- **English (eng)**
- **French (fra)**
[Docker Compose]（＃Docker-Compose）
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide]（＃Docker-Headless指南）
- **Japanese (jpn)**
- **Korean (kor)**
[Docker容器文件位置]（＃docker-container-file-locations）
- **Portuguese (por)**
- **Russian (rus)**
[常见的Docker问题]（＃ponsum-docker-Issues）
- **Turkish (tur)**
- **Vietnamese (vie)**
[支持的电子书格式]（＃支持的ebook-formats）


[输出]（＃输出）
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[常见问题]（＃普通问题）


[特别感谢]（＃特别感谢）
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[遗产]（＃遗留-V10）
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
特征
```bash
📖将电子书转换为具有口径的文本格式。 📚将电子书分为有组织的音频。 🎙️高质量的文本到 -  speech，带有[coqui Xttsv2]（https://huggingface.co/coqui/coqui/xtts-v2）和[fairseq]（https://github.com/facebook.com/facebookereaff示例/mms）（更多）。 🗣️使用您自己的语音文件可选语音克隆。 🌍支持+1110语言（默认为英语）。 [支持语言列表]（https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html）
```

🖥️设计用于在4GB RAM上运行。 [huggingface空间演示]（https://huggingface.co/spaces/drewthomasson/ebook2audiobook）
1. **Run ebook2audiobook**:
[！[拥抱脸]（https://img.shields.io/badge/hugging%20face-spaces-yellow?style=for-the-badge&logo=huggingFace）] /ebook2audiobook）
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Huggingface空间在免费的CPU层上运行，因此期望非常慢或超时，只是不要给它巨型文件就是全部
   - **Windows**
     ```bash
最好复制空间或在本地运行。免费的Google Colab
     ```
[！主/笔记本/colab_ebook2audiobook.ipynb）
3. **For Public Link**:
支持的语言
   `./ebook2audiobook.sh --share` (Linux/MacOS)
**阿拉伯语（ARA）**

> [!IMPORTANT]
**中文（Zho）**
to let the web page reconnect to the new connection socket.**

**捷克（CES）**
   - **Linux/MacOS**:
     ```bash
**克罗地亚（HRV）**
         --voice [path_to_voice_file] --language [language_code]
     ```
**荷兰（NLD）**
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
**英语（英语）**
     ```
     
**法语（fra）**
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
**德语（deu）**
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
**匈牙利（匈奴）**
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
**意大利语（ita）**
     ```
   - **Windows**
**日语（JPN）**
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
**韩语（kor）**
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
**抛光（pol）**


**葡萄牙语（POR）**
   - **Linux/MacOS**
     ```bash
**俄罗斯（rus）**
     ```
   - **Windows**
**西班牙语（水疗）**
     .\ebook2audiobook.cmd --help
     ```
**土耳其语（tur）**
    ```python
     app.py --help
**越南（VIE）**

<a id="help-command-output"></a>
[** +1100语言通过FairSeq **]（https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html）
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
硬件要求
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
最低4GB RAM，建议使用8GB
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
如果在Windows上运行（仅Docker），则启用虚拟化
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU，GPU（推荐），MPS（尚未优化并且可以比CPU慢）兼容

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

**之前，请仔细发布安装或错误问题搜索到打开和已关闭的问题选项卡<br>
为了确保您的问题还不存在。**
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

**缺乏任何标准结构，例如一章，段落，序言等。<br>
您应该首先手动删除您不想在音频中转换的任何文本。**

安装说明

**克隆仓库**
  --headless            Run the script in headless mode
启动Gradio Web界面
  --ebooks_dir EBOOKS_DIR
**运行ebook2audiobook **：
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** linux/macos **

optional parameters:
**视窗**
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
**打开Web应用程序**：单击终端中提供的URL以访问Web应用程序并转换电子书。 **对于公共链接**：
`python app.py -share`（全操作）
`./ebook2audiobook.sh -share`（linux/macos）
`ebook2audiobook.cmd -share`（Windows）
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[！重要的]
**如果脚本停止并再次运行，则需要刷新Gradio GUI界面<br>
让网页重新连接到新的连接套接字。**
                        (Optional) Fine tuned model path. Default is builtin model.
基本用法
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** linux/macos **：
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
**视窗**
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [ - 电子书] **：您的电子书文件的路径。 ** [ - 语音] **：语音克隆文件路径（可选）。 ** [ - 语言] **：ISO-639-3中的语言代码（即：Ita for Italian，英语，英语，deu for German ...）。<br>
默认语言为Eng， - 语言对于设置为./lib/lang.py。<br>的默认语言是可选的。<br>
还支持ISO-639-1 2字母代码。自定义模型邮政编码上传的示例
  --repetition_penalty REPETITION_PENALTY
（必须是包含强制性模型文件的.zip文件。
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** linux/macos **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
**视窗**
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custom_model_path> **：通往`model_name.zip`文件的路径，
    必须包含（根据TTS引擎）所有强制性文件<br>
    （请参阅./lib/models.py）。有关所有参数列表的详细指南
  --output_dir OUTPUT_DIR
** linux/macos **
  --version             Show the version of the script and exit

**视窗**
Windows:
    Gradio/GUI:
**或所有操作系统**
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id =“ help-command-output”> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
注意：在Gradio/GUI模式下，要取消运行转换，只需单击电子书上传组件的[X]。使用Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
您也可以使用Docker运行电子书到Audiobook Converter。此方法可确保在不同环境之间保持一致性并简化设置。运行Docker容器

要运行Docker容器并启动Gradio接口，请使用以下命令：

### Using Docker
 - 仅使用CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
构建Docker容器

您可以使用命令构建Docker映像：
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
此命令将在端口7860上启动Gradio接口。（Localhost：7860）
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
有关更多选项，请添加参数`-help`
```


所有ebook2audiobooks都将拥有`/home/user/app/``
例如：
`tmp` =`/home/user/app/tmp`
`oudiobooks` =`/home/home/user/app/audiobooks`
```
Docker无头指南
- For more options add the parameter `--help`


## Docker container file locations
在运行此操作之前，您需要在当前的DIR中创建一个名为“输入文件”的DIR
将链接到哪个，这是您可以将输入文件放置以供Docker Image查看
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
那应该就是这样！输出有声读物将在Audiobook文件夹中找到，该文件夹也将位于
在您的本地dir中，您运行了此Docker命令
docker pull athomasson2/ebook2audiobook
为了获得其他参数的帮助命令，该程序有您可以运行此
- Before you do run this you need to create a dir named "input-folder" in your current dir
这将输出此 
[help命令输出]（＃help-command-output）
mkdir input-folder && mkdir Audiobooks
Docker组成
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
该项目使用Docker撰写本地运行。您可以启用或禁用GPU支持 
通过设置`*docker-compose.yml`中
    -v $(pwd)/input-folder:/home/user/app/input_folder \
运行步骤
    athomasson2/ebook2audiobook \
**克隆存储库**（如果您还没有）：
```
- And that should be it! 
**设置GPU支持（默认情况下禁用）**
要启用GPU支持，请修改`docker-compose.yml``


**开始服务：**

```bash
**访问服务：**

```
！[demo_web_gui]（资产/demo_web_gui.gif）
[Help command output](#help-command-output)


没有硬件可以运行它，或者您想租用GPU？您可以复制Hugginface空间并以每小时0.40美元的价格租用GPU
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[huggingface太空演示]（＃huggingface空间demo）


[免费的Google Colab]（＃自由谷歌舞）
1. **Clone the Repository** (if you haven't already):
常见的Docker问题
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker被卡住下载微调模型。 （并非每台计算机都会发生这种情况，但有些似乎遇到了这个问题）
禁用进度栏似乎可以解决问题，
如[在＃191]中讨论（https://github.com/drewthomasson/ebook2audiobook/191）
在“ Docker Run”命令中添加此修复程序的示例
3. **Start the service:**
微调TTS型号
    docker-compose up -d
您可以通过此仓库轻松地调整自己的XTTS模型
[XTTS-FINETUNE-WEBUI]（https://github.com/daswer123/xtts-finetune-webui）
  The service will be available at http://localhost:7860.


[XTTS-FINETUNE-WEBUI空间]（https://huggingface.co/spaces/drewthomasson/xtts-finune-webui-gpu）
![demo_web_gui](assets/demo_web_gui.gif)

您也可以轻松地使用训练数据的空间
[denoise-huggingFace-空间]（https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit）
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
微调TTS系列
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
为了找到我们已经微调TTS模型的集合，


## Renting a GPU
演示
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
**雨天的声音**

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
**大卫·阿滕伯勒（David Attenborough）的声音**


支持的电子书格式
- Docker gets stuck downloading Fine-Tuned models.
.epub`，`.pdf`，`.mobi`，`.txt`，`.html`，`.rtf`，`.rtf`，`.chm` .chm`，`.lit` .lit`，
.pdb`，`.fb2`，`.odt`，`.cbr`，`.cbz`，`.prc`，`.lrf`，`.lrf`，`.pml` .pml`，
.snb`，`.cbc`，`.rb`，`.tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
**最佳结果**：`.epub`或`.mobi`自动章节检测
    -p 7860:7860 athomasson2/ebook2audiobook
输出


！[示例]（https://github.com/drewthomasson/voxnovel/blob/DC5197DFF97252FA44C391DC0596902D71278A888/ReadMe_files/eadme_files/example_in_app.jpeg）
You can fine-tune your own xtts model easily with this repo
常见问题：

CPU很慢（在服务器SMP CPU上更好），而NVIDIA GPU几乎可以实时转换。 [讨论]（https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846）
对于更快的多语言一代，我建议我的其他

（但是，它没有零声音克隆，并且是Siri质量的声音，但在CPU上的声音要快得多）。 “我有依赖性问题”  - 只需使用Docker，它的完全自我包含并具有无头模式，
 在Docker Run命令末尾添加` -  help`参数以获取更多信息。 “我会遇到截短的音频问题！” - 请解决这个问题，

### Fine Tuned TTS Collection
我需要帮助！ 🙌
[可以在此处找到的完整列表]（https://github.com/drewthomasson/ebook2audiobook/sissues/32）
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
有可能为多种语言创建README指南（因为我知道的唯一语言是英语😔）
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** coqui tts **：[coqui tts github]（https://github.com/idiap/coququi-ai-tts）
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **：[ffmpeg网站]（https://ffmpeg.org）
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0]（传统/v1.0）
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
您可以查看代码[此处]（Legacy/v1.0）。加入我们的服务器！ [！