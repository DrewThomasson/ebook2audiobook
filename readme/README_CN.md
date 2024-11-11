# 📚 ebook2audiobook

使用Calibre和Coqui XTTS将电子书转换为包含章节和元数据的有声读物。支持可选的语音克隆和多种语言！

#### 🖥️ Web GUI界面
![demo_web_gui](https://github.com/user-attachments/assets/85af88a7-05dd-4a29-91de-76a14cf5ef06)

<details>
  <summary>点击查看Web GUI的图片</summary>
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/b36c71cf-8e06-484c-a252-934e6b1d0c2f">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/c0dab57a-d2d4-4658-bff9-3842ec90cb40">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/0a99eeac-c521-4b21-8656-e064c1adc528">
</details>

## 🌟 特征

- 📖 使用Calibre将电子书转换为文本格式。
- 📚 将电子书拆分为章节，以获得有组织的音频。
- 🎙️ 使用Coqui XTTS实现高质量的文本到语音转换。
- 🗣️ 可选择使用您自己的语音文件进行语音克隆。
- 🌍 支持多种语言（默认为英语）。
- 🖥️ 基于4GB RAM运行。

## 🛠️ 环境要求

- Python 3.10
- `coqui-tts` Python package
- Calibre (用于电子书转换)
- FFmpeg (用于有声读物创作)
- Optional: 用于语音克隆的自定义语音文件

### 🔧 安装说明

1. **安装 Python 3.x** from [Python.org](https://www.python.org/downloads/).

2. **安装 Calibre**:
   - **Ubuntu**: `sudo apt-get install -y calibre`
   - **macOS**: `brew install calibre`
   - **Windows** (Admin Powershell): `choco install calibre`

3. **安装 FFmpeg**:
   - **Ubuntu**: `sudo apt-get install -y ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows** (Admin Powershell): `choco install ffmpeg`

4. **可选: Install Mecab** (非拉丁语言):
   - **Ubuntu**: `sudo apt-get install -y mecab libmecab-dev mecab-ipadic-utf8`
   - **macOS**: `brew install mecab`, `brew install mecab-ipadic`
   - **Windows**: [mecab-website-to-install-manually](https://taku910.github.io/mecab/#download) (注：日语支持有限)

5. **安装 Python packages**:
   ```bash
   pip install coqui-tts==0.24.2 pydub nltk beautifulsoup4 ebooklib tqdm gradio==4.44.0

   python -m nltk.downloader punkt
   python -m nltk.downloader punkt_tab
   ```

   **For non-Latin languages**:
   ```bash
   pip install mecab mecab-python3 unidic

   python -m unidic download
   ```

## 🌐 支持的语言

- **English (en)**
- **Spanish (es)**
- **French (fr)**
- **German (de)**
- **Italian (it)**
- **Portuguese (pt)**
- **Polish (pl)**
- **Turkish (tr)**
- **Russian (ru)**
- **Dutch (nl)**
- **Czech (cs)**
- **Arabic (ar)**
- **Chinese (zh-cn)**
- **Japanese (ja)**
- **Hungarian (hu)**
- **Korean (ko)**

在无头模式下运行脚本时指定语言代码。
## 🚀 使用

### 🖥️ 启动Gradio Web界面

1. **运行脚本**:
   ```bash
   python app.py
   ```

2. **打开web应用程序**: 点击终端中提供的URL访问web应用程序并转换电子书.
3. **公共链接**: 在末尾添加“--share True”，如下所示：`python app.py--share True`
- **[更多参数]**: 使用`-h`参数，如`python app.py-h`

### 📝 基本的无头用法

```bash
python app.py --headless True --ebook <path_to_ebook_file> --voice [path_to_voice_file] --language [language_code]
```

- **<path_to_ebook_file>**: 电子书文件的路径。
- **[path_to_voice_file]**: 指定转换的语音文件，可选。
- **[language_code]**: 指定转换的语言，可选。
- **[更多参数]**: 使用 `-h` 参数，如 `python app.py -h`

### 🧩 自定义XTTS模型的无头用法

```bash
python app.py --headless True --use_custom_model True --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path> --custom_config <custom_config_path> --custom_vocab <custom_vocab_path>
```

- **<ebook_file_path>**: 电子书文件的路径。
- **<target_voice_file_path>**: 指定转换的语音文件，可选。
- **<language>**: 指定转换的语言，可选。
- **<custom_model_path>**: `model.pth`的路径。
- **<custom_config_path>**: `config.json`的路径。
- **<custom_vocab_path>**: `vocab.json`的路径。
- **[更多参数]**: 使用 `-h` 参数，如 `python app.py -h`

### 🧩 自定义XTTS Fine-Tune 模型的无头用法 🌐

```bash
python app.py --headless True --use_custom_model True --ebook <ebook_file_path> --voice <target_voice_file_path> --language <language> --custom_model_url <custom_model_URL_ZIP_path>
```

- **<ebook_file_path>**: 电子书文件的路径。
- **<target_voice_file_path>**: 指定转换的语音文件，可选。
- **<language>**: 指定转换的语言，可选。
- **<custom_model_URL_ZIP_path>**: 模型文件夹压缩包的URL路径。例如
 [xtts_David_Attenborough_fine_tune](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/tree/main) `https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true`
- **[更多参数]**: 使用 `-h` 参数，如 `python app.py -h`

### 🔍 详细指南，包括所有要使用的参数列表
```bash
python app.py -h
```
- 这将输出以下内容:
```bash
usage: app.py [-h] [--share] [--headless [HEADLESS]] [--ebook EBOOK]
              [--ebooks_dir [EBOOKS_DIR]] [--voice VOICE] [--language LANGUAGE]
              [--device {cpu,gpu}] [--use_custom_model] [--custom_model CUSTOM_MODEL]
              [--custom_config CUSTOM_CONFIG] [--custom_vocab CUSTOM_VOCAB]
              [--custom_model_url CUSTOM_MODEL_URL] [--temperature TEMPERATURE]
              [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --share               Enable a public shareable Gradio link. Defaults to False.
  --headless [HEADLESS]
                        Run in headless mode. Defaults to True if the flag is present without a value, False otherwise.
  --ebook EBOOK         Path to the ebook file for conversion. Required in headless mode.
  --ebooks_dir [EBOOKS_DIR]
                        Path to the directory containing ebooks for batch conversion. Defaults to './ebooks' if 'default' value is provided.
  --voice VOICE         Path to the target voice file for TTS. Optional, uses a default voice if not provided.
  --language LANGUAGE   Language for the audiobook conversion. Options: en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko. Defaults to English (en).
  --device {cpu,gpu}    Type of processor unit for the audiobook conversion. Defaults to cpu.
  --use_custom_model    Use a custom TTS model. Defaults to False. Must be True to use custom models.
  --custom_model CUSTOM_MODEL
                        Path to the custom model file (.pth). Required if using a custom model.
  --custom_config CUSTOM_CONFIG
                        Path to the custom config file (config.json). Required if using a custom model.
  --custom_vocab CUSTOM_VOCAB
                        Path to the custom vocab file (vocab.json). Required if using a custom model.
  --custom_model_url CUSTOM_MODEL_URL
                        URL to download the custom model as a zip file. Optional, but will be used if provided. Examples include David Attenborough's model: 'https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true'. More XTTS fine-tunes can be found on my Hugging Face at 'https://huggingface.co/drewThomasson'.
  --temperature TEMPERATURE
                        Temperature for the model. Defaults to 0.65. Higher temperatures lead to more creative outputs.
  --length_penalty LENGTH_PENALTY
                        A length penalty applied to the autoregressive decoder. Defaults to 1.0. Not applied to custom models.
  --repetition_penalty REPETITION_PENALTY
                        A penalty that prevents the autoregressive decoder from repeating itself. Defaults to 2.0.
  --top_k TOP_K         Top-k sampling. Lower values mean more likely outputs and increased audio generation speed. Defaults to 50.
  --top_p TOP_P         Top-p sampling. Lower values mean more likely outputs and increased audio generation speed. Defaults to 0.8.
  --speed SPEED         Speed factor for the speech generation. Defaults to 1.0.
  --enable_text_splitting
                        Enable splitting text into sentences. Defaults to False.

Example usage:    
Windows:
    headless:
    ./ebook2audiobook.cmd --headless --ebook 'path_to_ebook' --voice 'path_to_voice' --language en --use_custom_model --custom_model 'model.zip' --custom_config config.json --custom_vocab vocab.json
    Graphic Interface:
    ./ebook2audiobook.cmd
Linux/Mac:
    headless:
    ./ebook2audiobook.sh --headless --ebook 'path_to_ebook' --voice 'path_to_voice' --language en --use_custom_model --custom_model 'model.zip' --custom_config config.json --custom_vocab vocab.json
    Graphic Interface:
    ./ebook2audiobook.sh
```

<details>
  <summary>⚠️ 遗留的旧版使用说明</summary>

## 🚀 使用

----> `ebook2audiobookXTTS/legacy/`

### 🖥️ Web界面

1. **运行脚本**:
   ```bash
   python custom_model_ebook2audiobookXTTS_gradio.py
   ```

2. **打开web应用程序**: 单击终端中提供的URL以访问web应用程序并转换电子书。

### 📝 基础用法

```bash
python ebook2audiobook.py <path_to_ebook_file> [path_to_voice_file] [language_code]
```

- **<path_to_ebook_file>**: 电子书文件的路径。
- **[path_to_voice_file]**: 指定转换的语音文件，可选。
- **[language_code]**: 指定转换的语言，可选。

### 🧩 自定义XTTS模型

```bash
python custom_model_ebook2audiobookXTTS.py <ebook_file_path> <target_voice_file_path> <language> <custom_model_path> <custom_config_path> <custom_vocab_path>
```

- **<ebook_file_path>**: 电子书文件的路径。
- **<target_voice_file_path>**: 指定转换的语音文件，可选。
- **<language>**: 指定转换的语言，可选。
- **<custom_model_path>**: `model.pth`的路径。
- **<custom_config_path>**: `config.json`的路径。
- **<custom_vocab_path>**: `vocab.json`的路径。
</details>

### 🐳 使用Docker

您还可以使用Docker运行电子书到有声读物的转换器。这种方法确保了不同环境之间的一致性，并简化了设置。

#### 🚀 运行Docker容器

要运行Docker容器并启动Gradio接口，请使用以下命令：

 -仅使用CPU运行
```powershell
docker run -it --rm -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```
 -使用GPU加速运行（仅限Nvida显卡）
```powershell
docker run -it --rm --gpus all -p 7860:7860 --platform=linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py
```

此命令将启动7860端口上的Gradio接口(localhost:7860)
- 对于更多选项，如以无头模式运行docker或公开gradio链接，请在docker启动命令中的`app.py`后添加`-h`参数
<details>
  <summary><strong>在无头模式下使用docker或使用额外参数修改任何内容的示例+完整指南</strong></summary>

## 在无头模式下使用docker的示例

首先是docker pull的最新版本
```bash
docker pull athomasson2/ebook2audiobookxtts:huggingface
```

- 在运行此命令之前，您需要在当前目录中创建一个名为“input folder”的目录，该目录将被链接，您可以在此处放置docker镜像的输入文件
```bash
mkdir input-folder && mkdir Audiobooks
```

- 运行下面命令需要将 **YOUR_INPUT_FILE.TXT** 替换为您创建的输入文件的名称

```bash
docker run -it --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/Audiobooks:/home/user/app/Audiobooks \
    --platform linux/amd64 \
    athomasson2/ebook2audiobookxtts:huggingface \
    python app.py --headless True --ebook /home/user/app/input_folder/YOUR_INPUT_FILE.TXT
```

- 应该就是这样了！

- 输出Audiobooks将在Audiobook文件夹中找到，该文件夹也位于您运行此docker命令的本地目录中


## 要获取此程序中其他参数的帮助命令，可以运行以下命令

```bash
docker run -it --rm \
    --platform linux/amd64 \
    athomasson2/ebook2audiobookxtts:huggingface \
    python app.py -h

```


这将输出以下内容

```bash
user/app/ebook2audiobookXTTS/input-folder -v $(pwd)/Audiobooks:/home/user/app/ebook2audiobookXTTS/Audiobooks --memory="4g" --network none --platform linux/amd64 athomasson2/ebook2audiobookxtts:huggingface python app.py -h
starting...
usage: app.py [-h] [--share SHARE] [--headless HEADLESS] [--ebook EBOOK] [--voice VOICE]
              [--language LANGUAGE] [--use_custom_model USE_CUSTOM_MODEL]
              [--custom_model CUSTOM_MODEL] [--custom_config CUSTOM_CONFIG]
              [--custom_vocab CUSTOM_VOCAB] [--custom_model_url CUSTOM_MODEL_URL]
              [--temperature TEMPERATURE] [--length_penalty LENGTH_PENALTY]
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting ENABLE_TEXT_SPLITTING]

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the
Gradio interface or run the script in headless mode for direct conversion.

options:
  -h, --help            show this help message and exit
  --share SHARE         Set to True to enable a public shareable Gradio link. Defaults
                        to False.
  --headless HEADLESS   Set to True to run in headless mode without the Gradio
                        interface. Defaults to False.
  --ebook EBOOK         Path to the ebook file for conversion. Required in headless
                        mode.
  --voice VOICE         Path to the target voice file for TTS. Optional, uses a default
                        voice if not provided.
  --language LANGUAGE   Language for the audiobook conversion. Options: en, es, fr, de,
                        it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko. Defaults to
                        English (en).
  --use_custom_model USE_CUSTOM_MODEL
                        Set to True to use a custom TTS model. Defaults to False. Must
                        be True to use custom models, otherwise you'll get an error.
  --custom_model CUSTOM_MODEL
                        Path to the custom model file (.pth). Required if using a custom
                        model.
  --custom_config CUSTOM_CONFIG
                        Path to the custom config file (config.json). Required if using
                        a custom model.
  --custom_vocab CUSTOM_VOCAB
                        Path to the custom vocab file (vocab.json). Required if using a
                        custom model.
  --custom_model_url CUSTOM_MODEL_URL
                        URL to download the custom model as a zip file. Optional, but
                        will be used if provided. Examples include David Attenborough's
                        model: 'https://huggingface.co/drewThomasson/xtts_David_Attenbor
                        ough_fine_tune/resolve/main/Finished_model_files.zip?download=tr
                        ue'. More XTTS fine-tunes can be found on my Hugging Face at
                        'https://huggingface.co/drewThomasson'.
  --temperature TEMPERATURE
                        Temperature for the model. Defaults to 0.65. Higher Tempatures
                        will lead to more creative outputs IE: more Hallucinations.
                        Lower Tempatures will be more monotone outputs IE: less
                        Hallucinations.
  --length_penalty LENGTH_PENALTY
                        A length penalty applied to the autoregressive decoder. Defaults
                        to 1.0. Not applied to custom models.
  --repetition_penalty REPETITION_PENALTY
                        A penalty that prevents the autoregressive decoder from
                        repeating itself. Defaults to 2.0.
  --top_k TOP_K         Top-k sampling. Lower values mean more likely outputs and
                        increased audio generation speed. Defaults to 50.
  --top_p TOP_P         Top-p sampling. Lower values mean more likely outputs and
                        increased audio generation speed. Defaults to 0.8.
  --speed SPEED         Speed factor for the speech generation. IE: How fast the
                        Narrerator will speak. Defaults to 1.0.
  --enable_text_splitting ENABLE_TEXT_SPLITTING
                        Enable splitting text into sentences. Defaults to True.

Example: python script.py --headless --ebook path_to_ebook --voice path_to_voice
--language en --use_custom_model True --custom_model model.pth --custom_config
config.json --custom_vocab vocab.json
```
</details>

#### 🖥️ Docker图形用户界面
![demo_web_gui](https://github.com/user-attachments/assets/85af88a7-05dd-4a29-91de-76a14cf5ef06)

<details>
  <summary>点击查看Web界面的图片</summary>
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/b36c71cf-8e06-484c-a252-934e6b1d0c2f">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/c0dab57a-d2d4-4658-bff9-3842ec90cb40">
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/0a99eeac-c521-4b21-8656-e064c1adc528">
</details>

### 🛠️ 关于自定义XTTS模型

为更好地处理特定声音而构建的模型。查看我的Hugging Face页面 [here](https://huggingface.co/drewThomasson).

要使用自定义模型，请粘贴“Finished_model_files.zip”文件的链接，如下所示：

[David Attenborough fine tuned Finished_model_files.zip](https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true)




更多详细信息请访问 [Dockerfile Hub Page]([https://github.com/DrewThomasson/ebook2audiobookXTTS](https://hub.docker.com/repository/docker/athomasson2/ebook2audiobookxtts/general)).

## 🌐 微调XTTS模型

要查找已经过微调的XTTS型号，请访问[Hugging Face](https://huggingface.co/drewThomasson) 🌐. 模型搜索需要包含“xtts fine tune”的关键字。

## 🎥 Demos

https://github.com/user-attachments/assets/8486603c-38b1-43ce-9639-73757dfb1031

## 🤗 [Huggingface space demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobookXTTS)
- Huggingface空间正在空闲cpu层上运行，所以预计会非常慢或超时，哈哈，只是不要给它大文件
- 最好复制空间或在本地运行。
## 📚 支持的电子书格式

- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`, `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`, `.snb`, `.cbc`, `.rb`, `.tcr`
- **最佳结果**: `.epub` 或者 `.mobi`格式可以进行自动章节检测。

## 📂 输出

- 创建一个包含元数据和章节的“.m4b”文件。
- **例子**: ![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
