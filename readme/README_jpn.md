# ebook 📚 2 audiobook (E 2 A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

電子書籍から章とメタデータ付きのオーディオブックへのCPU/GPUコンバーター<br/>
高度なTTSエンジンなどを使用。<br/>
音声クローニングと1696言語をサポート！
> [!IMPORTANT]
**このツールは、DRMフリーで合法的に取得された電子書籍でのみ使用することを目的としています。** <br>
作者は、このソフトウェアのいかなる誤用、またはそれに起因する法的結果について責任を負いません。 <br>
このツールは責任を持って、適用されるすべての法律に従って使用してください。

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### ebook2audiobookの開発者を支援していただきありがとうございます！
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### ローカルで実行

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### リモートで実行
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### グラフィカルインターフェース（GUI）
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>WebのGUI画像を見るにはクリック</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## デモ

**新しいデフォルト音声のデモ**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>その他のデモ</summary>

**ASMR音声** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**雨の日の音声**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**スカーレットの音声**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**デイヴィッド・アッテンボローの音声** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**例**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## 目次
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


## 機能
- 🔧 **サポートされているTTSエンジン**： `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **複数のファイル形式を変換**: , , , , , , , , , , , , , , , , , , , , , , `.epub` `.mobi` `.azw3` `.fb2` `.lrf` `.rb` `.snb` `.tcr` `.pdf` `.txt` `.rtf` `.doc` `.docx` `.html` `.odt` `.azw` `.tiff` `.tif` `.png` `.jpg` `.jpeg` `.bmp` `.zip`
- 💻 短いテキストを直接音声に変換する**テキストエリア**
- 🔍 画像としてのテキストページを含むファイル向けの**OCRスキャン**
- 🔊 **高品質なテキスト読み上げ**、ほぼリアルタイムからほぼ本物の音声まで
- 🗣️ 独自の音声ファイルを使用した**任意の音声クローン**
- 🌐 ** 1696言語をサポート** () [supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 💻 **低リソースに優しい** — **2 GB RAM / 1 GB VRAM（最小）**で動作
- 🎵 **オーディオブックの出力形式**: mono or stereo , , , , , , , , , `aac` `flac` `mp3` `m4b` `m4a` `mp4` `mov` `ogg` `wav` `webm`
- 🧠 **SMLタグ対応** — 中断、一時停止、音声切り替えなどのきめ細かな制御 () [see below](#sml-tags-available)
- 🧩 独自の学習済みモデルを使用した**任意のカスタムモデル** (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ E2Aチームによって学習された**ファインチューニング済みプリセットモデル** <br/>
     （追加のファインチューニング済みモデルが必要な場合、または公式プリセットリストにご自身のものを共有したい場合はご連絡ください） <i> </i>


##  ハードウェア要件
- RAM 2GB以上、8GB推奨。
- VRAM 1GB以上、4GB推奨。
- Windowsで実行する場合は仮想化を有効化（Dockerのみ）。
- CPU、XPU（intel、AMD、ARM）*。
- CUDA、ROCm、JETSON
- MPS（Apple Silicon CPU）

*<i> 最新のTTSエンジンはCPUで非常に遅いため、YourTTS、Tacotron2などの低品質のTTSを使用してください。</i>

## 対応言語
| **アラビア語(ar )**|**中国語(zh )**|**英語(en )**|**スペイン語(es )**|
|:------------------:|:------------------:|:------------------:|:------------------:|
| **フランス語(fr )** | **ドイツ語(de )** | **イタリア語(it )** | **ポルトガル語(pt )** |
| **ポーランド語(pl )**|**トルコ語(tr )**|**ロシア語(ru )**|**オランダ語(nl )**|
| **チェコ語(cs )**|**日本語(ja )**|**ヒンディー語(hi )**|**ベンガル語(bn )**|
| **ハンガリー語(hu )**|**韓国語(ko )**|**ベトナム語(vi )**|**スウェーデン語(sv )**|
| **ペルシャ語(fa )** | **ヨルバ語(yo )** | **スワヒリ語(sw )** | **インドネシア語(id )** |
| **スロバキア語(sk )**|**クロアチア語(hr )**|**タミル語(ta )**|**デンマーク語(da )**|
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## 対応する電子書籍形式
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **最良の結果**: 自動章検出には`.epub`または`.mobi`

## 出力および処理形式
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- 処理形式はlib/conf.pyで変更できます

## 利用可能なSMLタグ
- `[break]` — 無音（ランダム範囲 **0.3–0.6 sec.**）
- `[pause]` — 無音（ランダム範囲 **1.0–1.6 sec.**）
- `[pause:N]` — 固定の一時停止（**N sec.**）
- `[voice:/path/to/voice/file]...[/voice]` — デフォルトまたはGUI/CLIで選択した音声から音声を切り替え
- `[emotion:sadness]...[/emotion]` — Zonos only: emotion for a passage (happiness, sadness, disgust, fear, surprise, anger, other, neutral) or a mix like `[emotion:sadness=0.7,neutral=0.3]`; other engines ignore it

**電子書籍にSMLを自動的に追加することに特化した別のリポジトリをご覧ください -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**インストールやバグの問題を投稿する前に、未解決および解決済みの課題タブを注意深く検索してください<br>
あなたの問題がまだ存在しないことを確認するためです。**

注
**EPUB形式には、章、段落、序文などが何であるかを定義する標準的な構造がありません。<br>
そのため、まず音声に変換したくないテキストを手動で削除する必要があります。**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobookをインストール／実行**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Macランチャー**  
     `Mac Ebook2Audiobook Launcher.command`をダブルクリック


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Windowsユーザーへの注意: 管理者権限なしで不足しているプログラムをインストールするためにscoopがインストールされます。</i>
   
1. **Webアプリを開く**: ターミナルに表示されるURLをクリックして、Webアプリにアクセスし電子書籍を変換します。 `http://localhost:7860/`
2. **公開リンクの場合**:
   `./ebook2audiobook.command --share` （ Linux/MacOS ）
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` （すべてのOS ）

> [!IMPORTANT]
**スクリプトを停止して再実行した場合、Gradio GUIインターフェースを更新する必要があります<br>
Webページが新しい接続ソケットに再接続できるようにするためです。**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: 電子書籍ファイルへのパス
  - **[--voice]**: 音声クローンファイルのパス（任意）
  - **[--language]**: ISO-639-3形式の言語コード（例: イタリア語はita、英語はeng、ドイツ語はdeu...）。<br>
    デフォルト言語はengで、--languageは./lib/lang.pyで設定されたデフォルト言語の場合は任意です。<br>
    2文字のISO-639-1コードも対応しています。


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
     
- **<custom_model_path>**: `model_name.zip`ファイルへのパス、
      これは（ttsエンジンに応じて）すべての必須ファイルを含む必要があります<br>
      （./lib/models.pyを参照）。

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

注意: gradio/guiモードでは、実行中の変換をキャンセルするには、電子書籍アップロードコンポーネントの[X]をクリックするだけです。
ヒント: もう少し長い間を入れたい場合は、3秒の場合'[pause:3]'を追加するなど。

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

## ツール
Standalone tools, run with e2a's own Python (`python_env`, created by the first launch of e2a).

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

## クローン音声
サポートされているオーディオフォーマットのいずれかで任意のボイスオーディオをアップロードできます。理想的な長さは約1〜5分です。
録音にノイズの多い背景や音楽が再生されているかどうかは関係ありません。E 2 Aが音声をクリーンアップします。

内蔵されているクローン音声リストは、主に英語です。他の言語での音声が正式に必要な場合
リストに追加されました。お問い合わせください。審査後に追加させていただきます。

## ファインチューニング済み（fine-tuned）TTSモデル
#### 独自のTTSモデルを微調整する

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### 学習データのノイズ除去

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### ファインチューニング済みTTSモデルのコレクション

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

カスタムXTTSv2モデルには、音声の参照オーディオクリップが必須です:

## 独自のEbook2Audiobookカスタマイズ
libs/conf.pyを自由に変更して、必要な設定を追加または削除できます。これを計画している場合は、単に
オリジナルのconf.pyのコピーを作成しておけば、ebook2audiobookを更新するたびに変更したconf.pyをバックアップし、
オリジナルを元に戻すことができます。models.pyについても同じ手順を計画する必要があります。独自のカスタムモデルを
公式のファインチューニング済みebook2audiobookモデルにしたい場合は、ご連絡いただければプリセットリストに追加します。

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## よくある問題:
- NVIDIA/ROCm/XPU/MPS GPUが検出されない？？ -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPUは遅い（サーバーのSMP CPUの方が良い）一方、GPUはほぼリアルタイムの変換が可能です。
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   （ただし、zero-shotの音声クローンはなく、Siri品質の音声ですが、cpuでははるかに高速です）。
- 「依存関係の問題があります」 - 単にdockerを使ってください、完全に自己完結型でheadlessモードがあります、
   詳細についてはdocker runコマンドの末尾に`--help`パラメータを追加してください。
- 「音声が途切れる問題があります！」 - これについてISSUEを作成してください、
   私たちはすべての言語を話せるわけではなく、文の分割ロジックを微調整するためにユーザーのアドバイスが必要です。😊

## ***** ロードマップ *****
- すべての機能が公開された貢献に開かれています ⭐
- モデルの改善に役立つよう、対応言語のいずれかを話す人々からのあらゆる支援 ⭐
- [x] 変換を開始する前にブロック／章をプレビュー
- [x] 外科的なテキスト変更のために変換された文ごとに編集
- [x] 音楽のイントロ、インタールーデス、エンディングを生成し、インタールーデスとエンディングを編集
- [x] 音声、一時停止、中断、その他の変更のためのSMLタグ統合
- [x] さまざまな言語での-h -helpパラメータ情報
- [x] PDF / JPG / BMP / PNG / TIFF向けのOCRスキャン
- [x] ノートブックフォルダ [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] 中国語のテキスト分割が単語を分割しないようにし、一時停止のタイミングを改善する [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker作成
- [x] ポッドマン作曲
- [x] Kaggleノートブック
- [x] Google Colabノートブック
- [x] Audiobookshelf統合
- [x] 電子書籍翻訳オプション
- [x] 出力形式の選択
- [x] マルチプロセス変換
- [x] バッチ電子書籍フォルダ変換
- [x] GPUデバイス検出
- [x] 音声クローンアップロードのバックグラウンドリファレンス音声をノイズ除去する
- [x] カスタム微調整されたモデルのアップロード
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### ユーザーリクエスト
- [ ] 少なくともxttsv2、fairseq、vits、piper向けにヨーロッパポルトガル語の言語モデルを追加（支援歓迎）
- [ ] 少なくともxttsv2、fairseq、vits、piper向けにシンド語の言語モデルを追加（支援歓迎）

#### TTSエンジン
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed Audio/FireRedTTS 3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Fish-speech / Fish Audio (https://github.com/fishaudio/fish-speech)[cite: 1]
- [x] Higgs Audio TTS (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] Maya 1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1]
- [x] F 5 - TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen 3 - TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1]
- [x] VoxCPM 2 (https://github.com/voxcpm/voxcpm)[cite: 1]
- [x] Voxtral TTS (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] Chatterbox (https://github.com/resemble-ai/chatterbox)[cite: 1]
- [x] CosyVoice/CosyVoice 3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1]
- [x] Index - tts/Index TTS 2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv 2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] 孔子4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] ドットTTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT - SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro - TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS/NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] ポケットTTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] いろどりTTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron 2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] カメ(https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] BARK (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus - TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark - TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Readmeの翻訳
- [x] アラビア語(ara)
- [x] 中国語(zho)
- [x] 英語（ ENGLISH ）
- [x] スペイン語（スパ）
- [x] フランス語(fra)
- [x] ドイツ語(DEU)
- [x] イタリア語(ita)
- [x] ポルトガル語（ポーランド）
- [x] ポーランド語(pol)
- [x] トルコ語(TUR)
- [x] ロシア語(rus)
- [x] オランダ語(nld)
- [x] チェコ語(ces)
- [x] 日本語(jpn)
- [x] ヒンディー語(HIN)
- [x] ベンガル語（ベン）
- [x] ハンガリー語(HUN)
- [x] 韓国語(kor)
- [x] ベトナム語(VIE)
- [x] スウェーデン語(スウェーデン)
- [x] ペルシャ語(fas)
- [x] ヨルバ語(yor)
- [x] スワヒリ語(swa)
- [x] インドネシア語（インド）
- [x] スロバキア語(SLK)
- [x] クロアチア語(hrv)

#### 💻 OSの互換性
- [x] 🪟 Windows x 86
- [x] ウィンドウを🪟アーム
- [x] 🍎 Mac Intel x 86
- [x] 🍎 Apple Silicon Mac
- [x] Linux x86
- [x] 🐧 ARM Linux

**********

## モデルの学習などのための追加のオーバーキル（対応するすべてのCoqui-ttsモデルとpiper-ttsを1つの簡単なコマンドで）
- この@ DrewThomassonに関する情報については、彼は現在これの開発に取り組んでいます、 [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Make a easy to use training gui for all coqui-tts models in the  Completed at [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## 貢献者向けPythonコード正規化情報
- 関数とクラスの間を除いて、コード間に空行なし。
- dict()とjsonを除くすべてのキーに単一引用符を使用。dict['key']は常に単一引用符で呼び出す
- 4スペースのインデント、タブはまったく使わない
- すべての関数とその引数および戻り値の宣言に対する厳密な型付け
- 引数とその型付けの間にスペースなし、関数、「->」、戻り値の間にスペースなし

例:

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

## ベータテスト用のハードウェア寄付を募集
開発のテストのために、以下のようなあらゆる種類のハードウェアを受け付けています:
- CUDAをサポートするNVIDIA >= 11.8
- XPUインテルカード
- ROCmをサポートするROCm AMDカード>= 5.7

@DrewThomasson どんな形でも手伝いたい方は！ 😃
<!--
## 当サービスを強化するためにGPUをレンタルする必要がありますか？
- アンケートはこちらで公開されています https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## クレジット
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- A deep learning toolkit for Text-to-Speech, battle-tested in research and production.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Fast and local neural text-to-speech engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- ggml inference code for Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- An all-in-one, pure C++ inference engine for audio models, powered by ggml.

## 特別な感謝
すべての財務およびコード貢献者にとって、それぞれの貢献と提案はE 2 Aの品質を向上させるのに役立ちます。