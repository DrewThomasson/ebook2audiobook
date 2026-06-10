# 📚 ebook2audiobook (E2A)
電子書籍から章とメタデータ付きのオーディオブックへのCPU/GPUコンバーター<br/>
高度なTTSエンジンなどを使用。<br/>
音声クローンと1158言語に対応！
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
- [機能](#features)
- [グラフィカルインターフェース](#gui-interface)
- [デモ](#demos)
- [対応言語](#supported-languages)
- [最小要件](#hardware-requirements)
- [使い方](#instructions)
  - [ローカルで実行](#instructions)
    - [Gradio Webインターフェースの起動](#instructions)
    - [基本的なHeadlessの使い方](#basic-usage)
    - [HeadlessでのカスタムXTTSモデルの使い方](#example-of-custom-model-zip-upload)
    - [ヘルプコマンドの出力](#help-command-output)
  - [リモートで実行](#run-remotely)
  - [Docker](#docker)
    - [実行手順](#docker)
    - [よくあるDockerの問題](#common-docker-issues)
  
- [ファインチューニング済みTTSモデル](#fine-tuned-tts-models)
  - [ファインチューニング済みTTSモデルのコレクション](#fine-tuned-tts-collection)
  - [XTTSv2の学習](#fine-tune-your-own-xttsv2-model)
- [対応する電子書籍形式](#supported-ebook-formats)
- [出力形式](#output-and-process-formats)
- [古いバージョンに戻す](#reverting-to-older-versions)
- [よくある問題](#common-issues)
- [特別な感謝](#special-thanks)
- [目次](#table-of-contents)


## 機能
- 🔧 **対応TTSエンジン**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **複数のファイル形式を変換**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 短いテキストを直接音声に変換する**テキストエリア**
- 🔍 画像としてのテキストページを含むファイル向けの**OCRスキャン**
- 🔊 **高品質なテキスト読み上げ**、ほぼリアルタイムからほぼ本物の音声まで
- 🗣️ 独自の音声ファイルを使用した**任意の音声クローン**
- 🌐 **1158言語に対応** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **低リソースに優しい** — **2 GB RAM / 1 GB VRAM（最小）**で動作
- 🎵 **オーディオブックの出力形式**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SMLタグ対応** — 中断、一時停止、音声切り替えなどのきめ細かな制御 ([see below](#sml-tags-available))
- 🧩 独自の学習済みモデルを使用した**任意のカスタムモデル** (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ E2Aチームによって学習された**ファインチューニング済みプリセットモデル**<br/>
     <i>（追加のファインチューニング済みモデルが必要な場合、または公式プリセットリストにご自身のものを共有したい場合はご連絡ください）</i>


##  ハードウェア要件
- RAM 2GB以上、8GB推奨。
- VRAM 1GB以上、4GB推奨。
- Windowsで実行する場合は仮想化を有効化（Dockerのみ）。
- CPU、XPU（intel、AMD、ARM）*。
- CUDA、ROCm、JETSON
- MPS（Apple Silicon CPU）

*<i> 最新のTTSエンジンはCPUで非常に遅いため、YourTTS、Tacotron2などの低品質のTTSを使用してください。</i>

## 対応言語
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130の言語と方言はこちら**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


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

**電子書籍にSMLを自動的に追加することに特化した別のリポジトリをご覧ください -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**インストールやバグの問題を投稿する前に、未解決および解決済みの課題タブを注意深く検索してください<br>
あなたの問題がまだ存在しないことを確認するためです。**

>[!NOTE]
**EPUB形式には、章、段落、序文などが何であるかを定義する標準的な構造がありません。<br>
そのため、まず音声に変換したくないテキストを手動で削除する必要があります。**


### 手順 
1. **リポジトリをクローン**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobookをインストール／実行**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>macOSユーザーへの注意: 不足しているプログラムをインストールするためにhomebrewがインストールされます。</i>
     
   - **Macランチャー**  
     `Mac Ebook2Audiobook Launcher.command`をダブルクリック


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     または
     `ebook2audiobook.cmd`をダブルクリック

     <i>Windowsユーザーへの注意: 管理者権限なしで不足しているプログラムをインストールするためにscoopがインストールされます。</i>
   
1. **Webアプリを開く**: ターミナルに表示されるURLをクリックして、Webアプリにアクセスし電子書籍を変換します。 `http://localhost:7860/`
2. **公開リンクの場合**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**スクリプトを停止して再実行した場合、Gradio GUIインターフェースを更新する必要があります<br>
Webページが新しい接続ソケットに再接続できるようにするためです。**

### 基本的な使い方
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


###  カスタムモデルZipアップロードの例
  （必須のモデルファイルを含む.zipファイルである必要があります。XTTSv2の例: config.json、model.pth、vocab.json、ref.wav）
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>注意: カスタムモデルのref.wavは常に変換用に選択された音声です</i>
     
- **<custom_model_path>**: `model_name.zip`ファイルへのパス、
      これは（ttsエンジンに応じて）すべての必須ファイルを含む必要があります<br>
      （./lib/models.pyを参照）。

### 使用するすべてのパラメータのリストを含む詳細なガイドはこちら
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **またはすべてのOS向け**
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

注意: gradio/guiモードでは、実行中の変換をキャンセルするには、電子書籍アップロードコンポーネントの[X]をクリックするだけです。
ヒント: もう少し長い間を入れたい場合は、3秒の場合'[pause:3]'を追加するなど。

### Docker
1. **リポジトリをクローン**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **コンテナをビルド**
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
4. **コンテナを実行:**
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
- 注意: MPSはDockerで公開されていないため、CPUを使用する必要があります
  
### よくあるDockerの問題
- NVIDIA GPUが検出されない？？ -> [GPUの問題に関するWikiページ](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## ファインチューニング済み（fine-tuned）TTSモデル
#### 独自のXTTSv2モデルをファインチューニング

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


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

## 古いバージョンに戻す
リリースは -> [こちら](https://github.com/DrewThomasson/ebook2audiobook/releases) で見つけられます
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
- [ ] 外科的なテキスト変更のために変換された文ごとに編集
- [x] 音声、一時停止、中断、その他の変更のためのSMLタグ統合 
- [x] さまざまな言語での-h -helpパラメータ情報
- [x] PDF / JPG / BMP / PNG / TIFF向けのOCRスキャン
- [x] ノートブックフォルダ [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] 中国語のテキスト分割が単語を分割しないようにし、一時停止のタイミングを改善する [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggleノートブック
- [x] Google Colabノートブック
- [ ] [iOSアプリを作成](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [androidアプリを作成](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Audiobookshelf統合

#### 追加オプション
- [x] 電子書籍翻訳オプション
- [x] 出力形式の選択
- [x] バッチ電子書籍フォルダ
- [x] マルチプロセス変換
- [x] バッチ電子書籍フォルダ変換
- [x] GPUデバイス検出
- [x] アップロードされた音声クローン用に任意の参照オーディオをノイズ除去、
- [x] カスタムモデルのアップロード（今のところXTTSv2のみ。ご要望に応じて追加）
- [ ] 少なくともxttsv2、fairseq、vits、piper向けにヨーロッパポルトガル語の言語モデルを追加（支援歓迎）
- [ ] 少なくともxttsv2、fairseq、vits、piper向けにシンド語の言語モデルを追加（支援歓迎）

#### TTSエンジン
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

#### Readmeの翻訳
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

#### 🐍 OS互換性
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## モデルの学習などのための追加のオーバーキル（対応するすべてのCoqui-ttsモデルとpiper-ttsを1つの簡単なコマンドで） 
- これに関する情報は@DrewThomasson、彼は現在この開発に取り組んでいます、[作業中のリポジトリはこちら](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] ljspeech形式の学習レシピですべてのcoqui-ttsモデル向けに使いやすい学習用guiを作成する [coqui ttsからこちら](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


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
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson どんな形でも手伝いたい方は！ 😃
<!--
## 当サービスを強化するためにGPUをレンタルする必要がありますか？
- アンケートはこちらで公開されています https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## 特別な感謝
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 より良い章保存方法のために](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
