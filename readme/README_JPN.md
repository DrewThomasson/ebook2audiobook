ebook2Audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
cpu/gpuコンバーターは、電子書籍から章とメタデータを備えたオーディオブックまで<br/>
Caliber、FFMPEG、XTTSV2、FAIRSEQなどを使用します。音声クローニングと+1110言語をサポートします！ [！重要]
**このツールは、法的に取得した電子書籍のみで使用することを目的としています。** <br>
著者は、このソフトウェアの誤用や結果として生じる法的結果について責任を負いません。 <br>
このツールを責任を持って、適用されるすべての法律に従って使用します。 [！[discord]（https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6）]（https://discord.gg/63tv3f65k6））

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[！[ko-fi]（https://img.shields.io/badge/ko  -  fi-f16061?style=for-the-badge&logo=ko-fi&logocolor = white）]（https：// ko-fi .com/athomasson2）
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


！[demo_web_gui]（assets/demo_web_gui.gif）
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العربية（アラビア語）]（./ readme/readme_ar.md）
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
Zho [中文（中国）]（./ readme/readme_cn.md）
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
swe [svenska（swedish）]（./ readme/readme_swe.md）
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فار慈愛（ペルシャ）]（./ readme/readme_fa.md）


## Table of Contents
[ebook2audiobook]（＃-ebook2audiobook）
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[機能]（＃機能）
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker GUIインターフェイス]（＃docker-gui-interface）
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Huggingface Space Demo]（＃Huggingface-Space-demo）
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[無料のGoogle Colab]（＃free-google-colab）
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[事前に作られたオーディオデモ]（＃デモ）
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[サポート言語]（＃サポートされた言語）
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[要件]（＃ハードウェア要求）
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[インストール手順]（＃インストール - インストラクション）
- [Output](#output)
- [Common Issues](#common-issues)
[使用]（＃launch-gradio-web-interface）
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Gradio Webインターフェイスの起動]（＃Gradio-Web-Interface）


[基本的なヘッドレス使用]（＃Basic-- USAGE）
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[ヘッドレスカスタムXTTSモデルの使用]（＃of-of-custom-model-zip-upload）
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[GPUのレンタル]（＃RENTING-A-GPU）


[ヘルプコマンド出力]（＃ヘルプコマンド出力）
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[微調整されたTTSモデル]（＃微調整されたTTS-Models）


[微調整されたTTSモデルのコレクションの場合]（＃微調整されたTTTSコレクション）
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[docker run]（＃ranun-the-docker-container）
- **Czech (ces)**
- **Croatian (hrv)**
[docker build]（＃building-the-docker-container）
- **English (eng)**
- **French (fra)**
[Docker Compose]（＃docker-compose）
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide]（＃docker-headless-guide）
- **Japanese (jpn)**
- **Korean (kor)**
[dockerコンテナファイルの場所]（＃docker-container-file-locations）
- **Portuguese (por)**
- **Russian (rus)**
[一般的なDockerの問題]（＃Common-Docker-Issues）
- **Turkish (tur)**
- **Vietnamese (vie)**
[サポートされている電子ブック形式]（＃サポートebook-formats）


[出力]（＃出力）
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[一般的な問題]（＃Common-Issues）


[特別なありがとう]（＃特典）
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[レガシー]（＃レガシー-V10）
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
特徴
```bash
calibreで電子ブックをテキスト形式に変換します。 ebook整理されたオーディオの章に電子書籍を分割します。 [coqui xttsv2]（https://huggingface.co/coqui/xtts-v2）および[fairseq]（https://github.com/facebookresearch/fairseq/tree/main/例/mms）（その他）。 opty独自の音声ファイルでクローニングするオプションの音声。 buter +1110言語（デフォルトでは英語）をサポートしています。 [サポートされている言語のリスト]（https://dl.fbaipbublicfiles.com/mms/tts/all-tts-languages.html）
```

4GB RAMで実行するように設計されています。 [Huggingface Space Demo]（https://huggingface.co/spaces/drewthomasson/ebook2audiobook）
1. **Run ebook2audiobook**:
[！[顔をハグ]（https://img.shields.io/badge/hugging%20face-spaces-yellow?style = for-the-logo=huggingface）]（https://huggingface.co/spaces/drewthomasson /ebook2audiobook）
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Huggingfaceスペースは無料のCPU層で実行されているので、非常に遅いまたはタイムアウトlolを期待してください。
   - **Windows**
     ```bash
スペースを複製するか、地元で実行するのが最適です。無料のGoogleコラブ
     ```
[！[無料Google Colab]（https://colab.research.google.com/assets/colab-badge.svg）] [https://colab.research.google.com/github/drewthomasson/ebook2audiobook/blob/メイン/ノートブック/colab_ebook2audiobook.ipynb）
3. **For Public Link**:
サポート言語
   `./ebook2audiobook.sh --share` (Linux/MacOS)
**アラビア語（ara）**

> [!IMPORTANT]
**中国語（ZHO）**
to let the web page reconnect to the new connection socket.**

**チェコ（CES）**
   - **Linux/MacOS**:
     ```bash
**クロアチア語（HRV）**
         --voice [path_to_voice_file] --language [language_code]
     ```
**ダッチ（NLD）**
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
**英語（ENG）**
     ```
     
**フランス語（fra）**
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
**ドイツ語（deu）**
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
**ハンガリー（フン）**
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
**イタリア語（ita）**
     ```
   - **Windows**
**日本（jpn）**
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
**韓国（kor）**
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
**ポリッシュ（pol）**


**ポルトガル語（por）**
   - **Linux/MacOS**
     ```bash
**ロシア語（rus）**
     ```
   - **Windows**
**スペイン語（スパ）**
     .\ebook2audiobook.cmd --help
     ```
**トルコ（TUR）**
    ```python
     app.py --help
**ベトナム人（vie）**

<a id="help-command-output"></a>
[** +1100 FairSeqを介した言語**]（https://dl.fbaipbublicfiles.com/mms/tts/all-tts-languages.html）
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
ハードウェア要件
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4GB RAM最小、8GBが推奨されます
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Windowsで実行されている場合、仮想化が有効になります（Dockerのみ）
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU、GPU（推奨）、MPS（まだ最適化されておらず、CPUよりも遅くなる可能性がある）互換性

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

**インストールまたはバグの問題を投稿する前に、開いた問題と閉じた問題タブ<br>に注意深く検索します
あなたの問題がまだ存在していないことを確認するために。**
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

**章、段落、序文などのような標準構造の欠如<br>
まず、オーディオで変換されたくないテキストを手動で削除する必要があります。**

インストール手順

**クローンrepo **
  --headless            Run the script in headless mode
Gradio Webインターフェイスの起動
  --ebooks_dir EBOOKS_DIR
** ebook2audiobookを実行**：
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** linux/macos **

optional parameters:
** windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Webアプリを開く**：端末に提供されているURLをクリックして、Webアプリにアクセスして電子ブックを変換します。 **パブリックリンクの場合**：
`python app.py-- share`（すべてのos）
`./ebook2audiobook.sh -share`（linux/macos）
`ebook2audiobook.cmd -share`（windows）
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[！重要]
**スクリプトが停止して再度実行された場合、Gragio GUIインターフェイスを更新する必要があります<br>
Webページを新しい接続ソケットに再接続します。**
                        (Optional) Fine tuned model path. Default is builtin model.
基本的な使用法
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** linux/macos **：
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [ - 電子ブック] **：電子書籍ファイルへのパス。 ** [ - 音声] **：音声クローニングファイルパス（オプション）。 ** [ - 言語] **：ISO-639-3の言語コード（つまり、イタリア語のITA、英語のENG、ドイツ語のdeu ...）。<br>
デフォルトの言語はENGであり、 - 言語はデフォルト言語で設定されたデフォルト言語ではオプションです。/lib/lang.py。<br>
ISO-639-1 2文字のコードもサポートされています。カスタムモデルzipアップロードの例
  --repetition_penalty REPETITION_PENALTY
（必須モデルファイルを含む.zipファイルでなければなりません。XTTSの例：config.json、model.pth、vocab.json、ref.wav）
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** linux/macos **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <Custom_model_path> **： `model_name.zip`ファイルへのパス
    （TTSエンジンに従って）すべての必須ファイルを含む必要があります<br>
    （./lib/models.pyを参照）。使用するすべてのパラメーターのリストを含む詳細ガイドについては
  --output_dir OUTPUT_DIR
** linux/macos **
  --version             Show the version of the script and exit

** windows **
Windows:
    Gradio/GUI:
**またはすべてのos **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "help-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
注：Gradio/GUIモードでは、実行中の変換をキャンセルするには、電子ブックアップロードコンポーネントから[x]をクリックしてください。 Dockerを使用します
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Dockerを使用して電子書籍をオーディオブックコンバーターに実行することもできます。この方法は、さまざまな環境での一貫性を保証し、セットアップを簡素化します。 Dockerコンテナを実行します

Dockerコンテナを実行してグラデーションインターフェイスを開始するには、次のコマンドを使用します。

### Using Docker
-CPUのみで実行
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Dockerコンテナの構築

コマンドでDocker画像を作成できます。
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
このコマンドは、ポート7860のグラデーションインターフェイスを開始します。（LocalHost：7860）
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
その他のオプションについては、パラメーター `-help`を追加します
```


すべてのebook2Audiobookには、 `/home/user/app/`のベースディレクトルがあります
例えば：
`tmp` =`/home/user/app/tmp`
`audiobooks` =`/home/user/app/audiobooks`
```
Docker Headless Guide
- For more options add the parameter `--help`


## Docker container file locations
これを実行する前に、現在のdirに「入力倍率」という名前の監督を作成する必要があります
これがリンクされます、これはDocker画像の入力ファイルを配置して表示できる場所です
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
そして、それはそれであるべきです！出力オーディオブックは、オーディオブックフォルダーにあります。
あなたの地元の監督であなたはこのDockerコマンドを実行しました
docker pull athomasson2/ebook2audiobook
他のパラメーターのヘルプコマンドを取得するには、このプログラムがこれを実行できます
- Before you do run this you need to create a dir named "input-folder" in your current dir
そして、それはこれを出力します 
[ヘルプコマンド出力]（＃ヘルプコマンド出力）
mkdir input-folder && mkdir Audiobooks
Dockerは作曲します
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
このプロジェクトでは、Docker Composeがローカルで実行されます。 GPUサポートを有効または無効にすることができます 
`docker-compose.yml`に`*gpu-exabled`または `*gpu-disabled`を設定します
    -v $(pwd)/input-folder:/home/user/app/input_folder \
実行する手順
    athomasson2/ebook2audiobook \
**リポジトリをクローン**（まだお持ちでない場合）：
```
- And that should be it! 
** GPUサポートを設定します（デフォルトで無効）**
GPUサポートを有効にするには、 `docker-compose.yml`を変更し、`*gpu-disabled`に `*gpu-enabled`に変更します


**サービスを開始：**

```bash
**サービスへのアクセス：**

```
！[demo_web_gui]（assets/demo_web_gui.gif）
[Help command output](#help-command-output)


ハードウェアを実行するハードウェアを持っていないか、GPUをレンタルしたいですか？ Hugginfaceスペースを複製し、1時間あたり約0.40ドルでGPUをレンタルできます
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Huggingface Space Demo]（＃Huggingface-Space-demo）


[無料のGoogle Colab]（＃free-google-colab）
1. **Clone the Repository** (if you haven't already):
一般的なDockerの問題
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Dockerは、微調整されたモデルをダウンロードしています。 （これはすべてのコンピューターでは発生しませんが、一部はこの問題に遭遇しているように見えます）
進行状況バーを無効にすると、問題が修正されるように見えます。
説明したように[＃191]（https://github.com/drewthomasson/ebook2audiobook/issues/191）
`docker run`コマンドにこの修正を追加する例
3. **Start the service:**
細かい調整されたTTSモデル
    docker-compose up -d
このレポで簡単に独自のXTTSモデルを微調整できます
[xtts-finetune-webui]（https://github.com/daswer123/xtts-finetune-webui）
  The service will be available at http://localhost:7860.


[xtts-finetune-webui-space]（https://huggingface.co/spaces/drewthomasson/xts-finetune-webui-gpu）
![demo_web_gui](assets/demo_web_gui.gif)

トレーニングデータを簡単に除去するために使用できるスペースも
[denoise-huggingface-space]（https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit）
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
細かい調整されたTTSコレクション
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
すでに微調整されたTTSモデルのコレクションを見つけるには、


## Renting a GPU
デモ
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
**雨の日の声**

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
**デビッドアッテンボローの声**


サポートされている電子書籍形式
- Docker gets stuck downloading Fine-Tuned models.
`.epub`、` .pdf`、 `.mobi`、` .txt`、 `.html`、` .rtf`、 `.chm`、` .lit`、
`.pdb`、` .fb2`、 `.odt`、` .cbr`、 `.cbz`、` .prc`、 `.lrf`、` .pml`、
`.snb`、` .cbc`、 `.rb`、` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
**最良の結果**： `.epub`または` .mobi`自動章検出用
    -p 7860:7860 athomasson2/ebook2audiobook
出力


！[例]（https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a8888/readme_files/example_in_app.jpegpegpegpeg）
You can fine-tune your own xtts model easily with this repo
一般的な問題：

CPUは遅い（サーバーSMP CPUでより良い）一方、NVIDIA GPUはほぼリアルタイムの変換を行うことができます。 [これについての議論]（https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846）
より速い多言語の世代のために、私は私の他の世代を提案します

（ただし、ゼロショット音声クローンはありませんが、Siriの品質の声ですが、CPUでははるかに高速です）。 「私は依存関係の問題を抱えています」 -  Dockerを使用してください。完全に自己閉じ込められ、ヘッドレスモードがあります。
 詳細については、docker runコマンドの最後に `-help`パラメーターを追加します。 「私は切り捨てられたオーディオの問題を抱えています！」 - これの問題をお願いします、

### Fine Tuned TTS Collection
私が助けが必要なこと！ 🙌
[物事の完全なリストはこちらにあります]（https://github.com/drewthomasson/ebook2audiobook/issues/32）
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
潜在的に複数の言語用のReadMeガイドを作成する可能性があります（私が知っている唯一の言語は英語です😔）
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** coqui tts **：[coqui tts github]（https://github.com/idiap/coqui-ai-tts）
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **：[ffmpeg webサイト]（https://ffmpeg.org）
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[レガシーv1.0]（レガシー/v1.0）
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
コード[こちら]（レガシー/v1.0）を表示できます。サーバーに参加してください！ [！[discord]（https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6）]（https://discord.gg/63tv3f65k6））