# ebook2Audiobook

電子ブックから章とメタデータを備えたオーディオブックまでのCPU/GPUコンバーター<br/>Caliber、FFMPEG、XTTSV2、FAIRSEQなどを使用します。音声クローニングと+1110言語をサポートします！

> [！重要!]**このツールは、法的に取得した電子書籍のみで使用されていない非DRMでの使用を目的としています。**<br>著者は、このソフトウェアの誤用や結果として生じる法的結果について責任を負いません。<br>このツールを責任を持って、適用されるすべての法律に従って使用します。

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

ebook2audiobook開発者のサポートに感謝します！<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUIインターフェイス

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   私たちは買う[アラビア語（アラビア語）](./readme/README_AR.md)
-   ZHO[中文 (Chinese)](./readme/README_CN.md)
-   a \`a[英語](README.md)
-   swe[スウェーデン語（スウェーデン語）](./readme/README_SWE.md)
-   fas[ペルシャ語（ペルシャ）](./readme/README_FA.md)
-   彼女[イタリア語（イタリア語）](./readme/README.it.md)

## 目次

-   [ebook2Audiobook](#-ebook2audiobook)
-   [特徴](#features)
-   [Docker GUIインターフェイス](#docker-gui-interface)
-   [ハギングフェイススペースデモ](#huggingface-space-demo)
-   [無料のGoogleコラブ](#free-google-colab)
-   [事前に作られたオーディオデモ](#demos)
-   [サポート言語](#supported-languages)
-   [要件](#hardware-requirements)
-   [インストール手順](#installation-instructions)
-   [使用法](#launching-gradio-web-interface)
    -   [Gradio Webインターフェイスの起動](#launching-gradio-web-interface)
    -   [基本的なヘッドレス使用](#basic--usage)
    -   [ヘッドレスカスタムXTTSモデルの使用](#example-of-custom-model-zip-upload)
    -   [GPUをレンタルします](#renting-a-gpu)
    -   [コマンド出力をヘルプします](#help-command-output)
-   [細かい調整されたTTSモデル](#fine-tuned-tts-models)
    -   [微調整されたTTSモデルの収集用](#fine-tuned-tts-collection)
-   [Dockerを使用します](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Dockerビルド](#building-the-docker-container)
    -   [Dockerは作曲します](#docker-compose)
    -   [Docker Headless Guide](#docker-headless-guide)
    -   [Dockerコンテナファイルの場所](#docker-container-file-locations)
    -   [一般的なDockerの問題](#common-docker-issues)
-   [サポートされている電子書籍形式](#supported-ebook-formats)
-   [出力](#output)
-   [一般的な問題](#common-issues)
-   [特別なありがとう](#special-thanks)
-   [サーバーに参加してください！](#join-our--server)
-   [遺産](#legacy-v10)
-   [目次](#table-of-contents)

## 特徴

-   calibreで電子ブックをテキスト形式に変換します。
-   ebook整理されたオーディオの章に電子書籍を分割します。
-   🎙§高いテキストからスピーチ[Coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)そして[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)（そしてもっと）。
-   opty独自の音声ファイルでクローニングするオプションの音声。
-   buter +1110言語（デフォルトでは英語）をサポートしています。[サポートされている言語のリスト](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   4GB RAMで実行するように設計されています。

## [ハギングフェイススペースデモ](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingfaceスペースは無料のCPU層で実行されているので、非常に遅いまたはタイムアウトlolを期待してください。巨大なファイルを与えないでください
-   スペースを複製するか、地元で実行するのが最適です。

## 無料のGoogleコラブ

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## サポート言語

-   **アラビア語（ara）**
-   **中国人（zh）**
-   **チェコ（CES）**
-   **クロアチア語（HRV）**
-   **オランダ（NLD）**
-   **英語（ENG）**
-   **フランス語（from）**
-   **ドイツ語（deu）**
-   **NOT（hin）**
-   **ハンガリー（AM）**
-   **イタリア語（ita）**
-   **日本人（jpn）**
-   **韓国語（cor）**
-   **ポリッシュ（pol）**
-   **ポルトガル語（POR）**
-   **ロシア語（rus）**
-   **スペイン語（スパ）**
-   **トルコ語（ラウンド）**
-   **ベトナム人（vie）**
-   [**FairSeq経由の+1100言語**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## ハードウェア要件

-   4GB RAM最小、8GBが推奨されます
-   Windowsで実行されている場合、仮想化が有効になります（Dockerのみ）
-   CPU、GPU（推奨）、MPS（まだ最適化されておらず、CPUよりも遅くなる可能性がある）互換性

> [！重要!]**インストールまたはバグの問題を投稿する前に、開いた問題と閉じた問題タブに注意深く検索します<br>あなたの問題がまだ存在していないことを確認するために。**

> [！注記!]**章、段落、序文などのような標準構造が不足しています。<br>まず、オーディオで変換されたくないテキストを手動で削除する必要があります。**

### インストール手順

1.  **クローンリポジトリ**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Gradio Webインターフェイスの起動

1.  **ebook2audiobookを実行します**:
    -   **Linux/macos**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Windows**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Webアプリを開きます**：ターミナルで提供されているURLをクリックして、Webアプリにアクセスして電子ブックを変換します。
3.  **パブリックリンク用**:`python app.py --share`（すべてのOS）`./ebook2audiobook.sh --share`（Linux/macos）`ebook2audiobook.cmd --share`（Windows）

> [！重要!]**スクリプトが停止して再度実行された場合は、Gradio GUIインターフェイスを更新する必要があります<br>Webページを新しい接続ソケットに再接続します。**

### 基本的な使用法

-   **Linux/macos**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--ebook]**：電子書籍ファイルへのパス。
-   **[ -- 声]**：音声クローニングファイルパス（オプション）。
-   **[ -- 言語]**：ISO-639-3の言語コード（つまり、イタリア語のITA、英語のENG、ドイツ語のDeu ...）。<br>デフォルト言語はENGであり、-Languageは、./lib/lang.pyに設定されたデフォルト言語でオプションです。<br>ISO-639-1 2文字のコードもサポートされています。

### カスタムモデルzipアップロードの例

（必須モデルファイルを含む.zipファイルでなければなりません。XTTSの例：config.json、model.pth、vocab.json、ref.wav）

-   **Linux/macos**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**：への道`model_name.zip`ファイル、
        （TTSエンジンに従って）すべての必須ファイルを含める必要があります<br>（./lib/models.pyを参照）。

### 使用するすべてのパラメーターのリストを含む詳細ガイドについては

-   **Linux/macos**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **またはすべてのOSに対して**
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

注：Gradio/GUIモードでは、実行中の変換をキャンセルするには、をクリックするだけです[x]電子ブックアップロードコンポーネントから。

### Dockerを使用します

Dockerを使用して電子書籍をオーディオブックコンバーターに実行することもできます。 
この方法は、さまざまな環境での一貫性を保証し、セットアップを簡素化します。

#### Dockerコンテナを実行します

Dockerコンテナを実行してグラデーションインターフェイスを開始するには、次のコマンドを使用します。

\-CPUのみで実行

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run GPU SpeedUp（nvidia互換のみ）

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Dockerコンテナの構築

-   コマンドでDocker画像を作成できます。

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

このコマンドは、ポート7860のグラデーションインターフェイスを開始します。（LocalHost：7860）

-   その他のオプションについては、パラメーターを追加します`--help`

## Dockerコンテナファイルの場所

すべてのebook2Audiobookには、基本ディレクトがあります`/home/user/app/`例えば：`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker Headless Guide

最初に最新のドッカープルの場合

```bash
docker pull athomasson2/ebook2audiobook
```

-   これを実行する前に、現在のdirに「入力倍率」という名前の監督を作成する必要があります
    これがリンクされます、これはDocker画像の入力ファイルを配置して表示できる場所です

```bash
mkdir input-folder && mkdir Audiobooks
```

-   下のコマンドでは、スワップアウトします**your_input_file.txt**入力ファイルの名前

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   そして、それはそれであるべきです！
-   出力オーディオブックは、オーディオブックフォルダーにあります。
    あなたの地元の監督であなたはこのDockerコマンドを実行しました

## 他のパラメーターのヘルプコマンドを取得するには、このプログラムがこれを実行できます

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

そして、それはこれを出力します[コマンド出力をヘルプします](#help-command-output)

### Dockerは作曲します

このプロジェクトでは、Docker Composeがローカルで実行されます。 GPUサポートを有効または無効にすることができます 
どちらかを設定します`*gpu-enabled`または`*gpu-disabled`で`docker-compose.yml`

#### 実行する手順

1.  **リポジトリをクローンします**（まだ行っていない場合）：
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **GPUサポートを設定します（デフォルトで無効）**GPUサポートを有効にするには、変更します`docker-compose.yml`そして変化します`*gpu-disabled`に`*gpu-enabled`
3.  **サービスを開始します：**
    ```bash
    docker-compose up -d
    ```
4.  **サービスへのアクセス：**このサービスは、http：// localhost：7860で入手できます。

### Docker GUIインターフェイス

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## GPUをレンタルします

ハードウェアを実行するハードウェアを持っていないか、GPUをレンタルしたいですか？

#### Hugginfaceスペースを複製し、1時間あたり約0.40ドルでGPUをレンタルできます

[ハギングフェイススペースデモ](#huggingface-space-demo)

#### または、Google Colabを無料で使用してみてください！

(Be aware it will time out after a bit of your not messing with the google colab)
[無料のGoogleコラブ](#free-google-colab)

## 一般的なDockerの問題

-   Dockerは、微調整されたモデルをダウンロードしています。
    （これはすべてのコンピューターでは発生しませんが、一部はこの問題に遭遇しているように見えます）
    進行状況バーを無効にすると、問題が修正されるように見えます。
    説明したように[＃191で](https://github.com/DrewThomasson/ebook2audiobook/issues/191)この修正を追加する例`docker run`指示

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## 細かい調整されたTTSモデル

このレポで簡単に独自のXTTSモデルを微調整できます[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

GPUを簡単にレンタルしたい場合は、このHuggingfaceを複製することもできます[xtts-finetune-webuiスペース](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

トレーニングデータを簡単に除去するために使用できるスペースも[Denoise-Huggingfaceスペース](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### 細かい調整されたTTSコレクション

すでに微調整されたTTSモデルのコレクションを見つけるには、
訪問[この抱きしめる顔のリンク](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)XTTSカスタムモデルの場合、音声参照のオーディオクリップは必須です。

## デモ

**雨の日の声**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**デビッド・アッテンボローの声**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## サポートされている電子書籍形式

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **最良の結果**:`.epub`または`.mobi`自動章検出用

## 出力

-   aを作成します`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`（./lib/conf.pyに設定）メタデータと章を備えたファイル。
-   **例**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## 一般的な問題：

-   CPUは遅い（サーバーSMP CPUでより良い）一方、NVIDIA GPUはほぼリアルタイムの変換を行うことができます。[これについての議論](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)より速い多言語の世代のために、私は私の他の世代を提案します[Piper-TTSを使用するプロジェクト](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)その代わり
    （ただし、ゼロショットの音声クローンはありませんが、Siriの品質の声ですが、CPUでははるかに高速です）。
-   「私は依存関係の問題を抱えています」 -  Dockerを使用してください。完全に自己閉じ込められ、ヘッドレスモードがあります。
     追加`--help`詳細については、docker runコマンドの最後のパラメーター。
-   「私は切り捨てられたオーディオの問題を抱えています！」 - これの問題をお願いします、
     私たちはすべての言語を話しているわけではなく、ロジックを分割する文を微調整するようにユーザーからアドバイスする必要があります。

## 私が助けが必要なこと！ 🙌

## [物事の完全なリストはここにあります](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   適切な文の分割方法を支援するために、サポートされている言語のいずれかを話す人々の助け
-   潜在的に複数の言語用のReadMeガイドを作成する可能性があります（私が知っている唯一の言語は英語です😔）

## 特別なありがとう

-   **TTSの調理**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **口径**:[口径のウェブサイト](https://calibre-ebook.com)
-   **ffmpeg**:[FFMPEG Webサイト](https://ffmpeg.org)
-   [より良い章保存方法については、 @shakenbake15](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [レガシーv1.0](legacy/v1.0)

コードを表示できます[ここ](legacy/v1.0).

## サーバーに参加してください！

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
