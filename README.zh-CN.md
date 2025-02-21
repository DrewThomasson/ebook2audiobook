# 📚ebook2audiobook

CPU/GPU的转换器从电子书到有声读物的章节和元数据<br/>使用Caliber，FFMPEG，XTTSV2，FairSeq等。支持语音克隆和+1110语言！

> [！重要的!]**该工具旨在与非DRM（合法获得的电子书）一起使用。**<br>作者对滥用此软件或任何由此产生的法律后果概不负责。<br>负责任地使用此工具，并按照所有适用的法律使用。

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

感谢支持ebook2audiobook开发人员！<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI接口

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   我们买[阿拉伯语（阿拉伯语）](./readme/README_AR.md)
-   zho[中文 (Chinese)](./readme/README_CN.md)
-   一个[英语](README.md)
-   SWE[瑞典（瑞典）](./readme/README_SWE.md)
-   fas[波斯（波斯）](./readme/README_FA.md)
-   她[意大利语（意大利语）](./readme/README.it.md)

## 目录

-   [ebook2audiobook](#-ebook2audiobook)
-   [特征](#features)
-   [Docker GUI界面](#docker-gui-interface)
-   [拥抱面太空演示](#huggingface-space-demo)
-   [免费的Google Colab](#free-google-colab)
-   [预制音频演示](#demos)
-   [支持的语言](#supported-languages)
-   [要求](#hardware-requirements)
-   [安装说明](#installation-instructions)
-   [用法](#launching-gradio-web-interface)
    -   [启动Gradio Web界面](#launching-gradio-web-interface)
    -   [基本无头的用法](#basic--usage)
    -   [无头自定义XTTS模型使用](#example-of-custom-model-zip-upload)
    -   [租用GPU](#renting-a-gpu)
    -   [帮助命令输出](#help-command-output)
-   [微调TTS型号](#fine-tuned-tts-models)
    -   [用于收集微调TTS型号](#fine-tuned-tts-collection)
-   [使用Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker组成](#docker-compose)
    -   [Docker无头指南](#docker-headless-guide)
    -   [Docker容器文件位置](#docker-container-file-locations)
    -   [常见的Docker问题](#common-docker-issues)
-   [支持的电子书格式](#supported-ebook-formats)
-   [输出](#output)
-   [常见问题](#common-issues)
-   [特别感谢](#special-thanks)
-   [加入我们的服务器！](#join-our--server)
-   [遗产](#legacy-v10)
-   [目录](#table-of-contents)

## 特征

-   📖将电子书转换为具有口径的文本格式。
-   📚将电子书分为有组织的音频。
-   🎙️高质量的文字到语音[coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)和[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)（以及更多）。
-   🗣️使用您自己的语音文件可选语音克隆。
-   🌍支持+1110语言（默认为英语）。[支持语言列表](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️设计用于在4GB RAM上运行。

## [拥抱面太空演示](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingface空间在免费的CPU层上运行，因此期望非常慢或超时，只是不要给它巨型文件就是全部
-   最好复制空间或在本地运行。

## 免费的Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## 支持的语言

-   **阿拉伯语（ARA）**
-   **中文（ZH）**
-   **捷克（CES）**
-   **克罗地亚（HRV）**
-   **荷兰（NLD）**
-   **英语（英语）**
-   **法语（来自）**
-   **德国（DEU）**
-   **不（hin）**
-   **匈牙利人（上午）**
-   **意大利语（ita）**
-   **日语（JPN）**
-   **韩语（COR）**
-   **抛光（波兰）**
-   **葡萄牙语（POR）**
-   **俄罗斯（RUS）**
-   **西班牙语（水疗）**
-   **土耳其语（圆形）**
-   **越南语（VIE）**
-   [**+1100语言通过Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## 硬件要求

-   最低4GB RAM，建议使用8GB
-   如果在Windows上运行（仅Docker），则启用虚拟化
-   CPU，GPU（推荐），MPS（尚未优化并且可以比CPU慢）兼容

> [！重要的!]**在将安装或错误问题发布到已打开和封闭的问题选项卡之前<br>为了确保您的问题还不存在。**

> [！笔记!]**缺乏任何标准结构，例如一章，段落，序言等。<br>您应该首先手动删除不想在音频中转换的任何文本。**

### 安装说明

1.  **克隆回购**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### 启动Gradio Web界面

1.  **运行ebook2audiobook**:
    -   **Linux/MacOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **视窗**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **打开Web应用程序**：单击终端中提供的URL以访问Web应用程序并转换电子书。
3.  **用于公共链接**:`python app.py --share`（所有操作系统）`./ebook2audiobook.sh --share`（Linux/MacOS）`ebook2audiobook.cmd --share`（视窗）

> [！重要的!]**如果脚本停止并再次运行，则需要刷新Gradio GUI接口<br>让网页重新连接到新的连接套接字。**

### 基本用法

-   **Linux/MacOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **视窗**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[ -- 书]**：通往电子书文件的路径。
-   **[ -- 嗓音]**：语音克隆文件路径（可选）。
-   **[ -- 语言]**：ISO-639-3中的语言代码（即：Ita for Italian，Eng for English，Deu，德语...）。<br>默认语言为Eng， - 语言对于设置在./lib/lang.py中的默认语言是可选的。<br>还支持ISO-639-1 2字母代码。

### 自定义模型邮政编码上传的示例

（必须是包含强制性模型文件的.zip文件。

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **视窗**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**：通往`model_name.zip`文件，
        必须包含（根据TTS引擎）所有强制性文件<br>（请参阅./lib/models.py）。

### 有关所有参数列表的详细指南

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **视窗**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **或所有操作系统**
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

注意：在Gradio/GUI模式下，要取消运行转换，只需单击[x]从电子书上传组件。

### 使用Docker

您也可以使用Docker运行电子书到Audiobook Converter。 
此方法可确保在不同环境之间保持一致性并简化设置。

#### 运行Docker容器

要运行Docker容器并启动Gradio接口，请使用以下命令：

 \- 仅使用CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

 \- 与GPU加速相关（仅兼容NVIDIA）

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### 构建Docker容器

-   您可以使用命令构建Docker映像：

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

此命令将在端口7860上启动Gradio接口。（Localhost：7860）

-   有关更多选项添加参数`--help`

## Docker容器文件位置

所有ebook2audiobooks都将拥有`/home/user/app/`例如：`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker无头指南

首先是最新的码头工具

```bash
docker pull athomasson2/ebook2audiobook
```

-   在运行此操作之前，您需要在当前的DIR中创建一个名为“输入文件”的DIR
    将链接到哪个，这是您可以将输入文件放置以供Docker Image查看

```bash
mkdir input-folder && mkdir Audiobooks
```

-   在下面的命令中交换**your_input_file.txt**带有输入文件的名称

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   那应该就是这样！
-   输出有声读物将在Audiobook文件夹中找到，该文件夹也将位于
    在您的本地dir中，您运行了此Docker命令

## 为了获得其他参数的帮助命令，该程序有您可以运行此

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

这将输出此[帮助命令输出](#help-command-output)

### Docker组成

该项目使用Docker撰写本地运行。您可以启用或禁用GPU支持 
通过设置`*gpu-enabled`或者`*gpu-disabled`在`docker-compose.yml`

#### 运行步骤

1.  **克隆存储库**（如果您还没有）：
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **设置GPU支持（默认情况下禁用）**要启用GPU支持，请修改`docker-compose.yml`并改变`*gpu-disabled`到`*gpu-enabled`
3.  **开始服务：**
    ```bash
    docker-compose up -d
    ```
4.  **访问服务：**该服务将在http：// localhost：7860提供。

### Docker GUI界面

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## 租用GPU

没有硬件可以运行它，或者您想租用GPU？

#### 您可以复制Hugginface空间并以每小时0.40美元的价格租用GPU

[拥抱面太空演示](#huggingface-space-demo)

#### 或者，您可以尝试免费使用Google Colab！

（请注意，在您没有与Google Colab搞砸的一点点之后，它将超时）[免费的Google Colab](#free-google-colab)

## 常见的Docker问题

-   Docker被卡住下载微调模型。
    （并非每台计算机都会发生这种情况，但有些似乎遇到了这个问题）
    禁用进度栏似乎可以解决问题，
    如所讨论的[在＃191中](https://github.com/DrewThomasson/ebook2audiobook/issues/191)在`docker run`命令

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## 微调TTS型号

您可以通过此仓库轻松地调整自己的XTTS模型[XTTS-FINETUNE-WEBUI](https://github.com/daswer123/xtts-finetune-webui)

如果您想轻松租用GPU，也可以复制此拥抱面[XTTS-FINETUNE-WEBUI空间](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

您也可以轻松地使用训练数据的空间[DeNoise-HuggingFace空间](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### 微调TTS系列

为了找到我们已经微调TTS模型的集合，
访问[这个拥抱的脸链接](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)对于XTTS自定义模型，语音参考的参考音频剪辑是必须的：

## 演示

**下雨天的声音**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**大卫·阿滕伯勒（David Attenborough）的声音**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## 支持的电子书格式

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **最好的结果**:`.epub`或者`.mobi`用于自动章节检测

## 输出

-   创建一个`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`（在./lib/conf.py中设置）带有元数据和章节的文件。
-   **例子**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## 常见问题：

-   CPU很慢（在服务器SMP CPU上更好），而NVIDIA GPU几乎可以实时转换。[讨论这一点](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)对于更快的多语言一代，我建议我的其他[使用Piper-TTS的项目](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)反而
    （但是，它没有零声音克隆，并且是Siri质量的声音，但在CPU上的声音要快得多）。
-   “我有依赖性问题”  - 只需使用Docker，它的完全自我包含并具有无头模式，
     添加`--help`Docker Run命令末尾的参数以获取更多信息。
-   “我会遇到截短的音频问题！” - 请解决这个问题，
     我们不会说每种语言，也需要从用户提供建议以微调句子分裂逻辑。

## 我需要帮助！ 🙌

## [可以在这里找到的完整列表](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   人们讲任何受支持的语言的人的任何帮助，以帮助适当的句子分裂方法
-   有可能为多种语言创建README指南（因为我知道的唯一语言是英语😔）

## 特别感谢

-   **烹饪TTS**:[coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **口径**:[口径网站](https://calibre-ebook.com)
-   **ffmpeg**:[FFMPEG网站](https://ffmpeg.org)
-   [@shakenbake15用于更好的章节保存方法](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [传统v1.0](legacy/v1.0)

您可以查看代码[这里](legacy/v1.0).

## 加入我们的服务器！

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
