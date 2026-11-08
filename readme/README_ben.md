# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

অধ্যায় ও মেটাডেটা সহ ই-বুক থেকে অডিওবুকে রূপান্তরকারী CPU/GPU কনভার্টার<br/>
উন্নত TTS ইঞ্জিন ইত্যাদি ব্যবহার করে।<br/>
ভয়েস ক্লোনিং এবং 1696 টি ভাষা সমর্থন করে!
> [!IMPORTANT]
**এই টুলটি কেবল DRM-মুক্ত, বৈধভাবে অর্জিত ই-বুকের সাথে ব্যবহারের জন্য তৈরি করা হয়েছে।** <br>
লেখকগণ এই সফটওয়্যারের কোনো অপব্যবহার বা তা থেকে উদ্ভূত কোনো আইনি পরিণতির জন্য দায়ী নন। <br>
এই টুলটি দায়িত্বের সাথে এবং সমস্ত প্রযোজ্য আইন মেনে ব্যবহার করুন।

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### ebook2audiobook-এর ডেভেলপারদের সমর্থন করার জন্য ধন্যবাদ!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### স্থানীয়ভাবে চালান

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### দূরবর্তীভাবে চালান
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### গ্রাফিকাল ইন্টারফেস (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>ওয়েব GUI-এর ছবি দেখতে ক্লিক করুন</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## ডেমো

**নতুন ডিফল্ট ভয়েসের ডেমো**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>আরও ডেমো</summary>

**ASMR ভয়েস** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**বৃষ্টির দিনের ভয়েস**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**স্কারলেট ভয়েস**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**ডেভিড অ্যাটেনবরো ভয়েস** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**উদাহরণ**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## সূচিপত্র
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


## বৈশিষ্ট্য
- 🔧 **TTS ইঞ্জিন সমর্থিত**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **একাধিক ফাইল ফরম্যাট রূপান্তর করুন**: , , , , , , , , , , , , , , , , , , , , , , `.epub` `.mobi` `.azw3` `.fb2` `.lrf` `.rb` `.snb` `.tcr` `.pdf` `.txt` `.rtf` `.doc` `.docx` `.html` `.odt` `.azw` `.tiff` `.tif` `.png` `.jpg` `.jpeg` `.bmp` `.zip`
- 💻 সংক্ষিপ্ত টেক্সট সরাসরি অডিওতে রূপান্তর করার জন্য **টেক্সট এরিয়া**
- 🔍 ছবি হিসেবে টেক্সট পৃষ্ঠা সহ ফাইলের জন্য **OCR স্ক্যানিং**
- 🔊 **উচ্চমানের টেক্সট-টু-স্পিচ**, প্রায় রিয়েল-টাইম থেকে প্রায় বাস্তব ভয়েস পর্যন্ত
- 🗣️ আপনার নিজের ভয়েস ফাইল ব্যবহার করে **ঐচ্ছিক ভয়েস ক্লোনিং**
- 🌐 ** 1696 টি ভাষা সমর্থন করে ** () [supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
- 💻 **কম সম্পদ-বান্ধব** — **2 GB RAM / 1 GB VRAM (ন্যূনতম)**-এ চলে
- 🎵 **অডিওবুক আউটপুট ফরম্যাট**: mono or stereo , , , , , , , , , `aac` `flac` `mp3` `m4b` `m4a` `mp4` `mov` `ogg` `wav` `webm`
- 🧠 **SML ট্যাগ সমর্থিত** — বিরতি, থামা, ভয়েস পরিবর্তন ইত্যাদির সূক্ষ্ম নিয়ন্ত্রণ () [see below](#sml-tags-available)
- 🧩 আপনার নিজের প্রশিক্ষিত মডেল ব্যবহার করে **ঐচ্ছিক কাস্টম মডেল** (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ E2A টিম দ্বারা প্রশিক্ষিত **ফাইন-টিউন করা প্রিসেট মডেল** <br/>
     (আপনার অতিরিক্ত ফাইন-টিউন করা মডেলের প্রয়োজন হলে, অথবা অফিসিয়াল প্রিসেট তালিকায় আপনার মডেল শেয়ার করতে চাইলে আমাদের সাথে যোগাযোগ করুন) <i> </i>


##  হার্ডওয়্যার প্রয়োজনীয়তা
- RAM ন্যূনতম 2GB, 8GB প্রস্তাবিত।
- VRAM ন্যূনতম 1GB, 4GB প্রস্তাবিত।
- windows-এ চালানোর সময় ভার্চুয়ালাইজেশন সক্ষম (শুধুমাত্র Docker)।
- CPU, XPU (intel, AMD, ARM)*।
- CUDA, ROCM, JETSON
- এমপিএস (অ্যাপল সিলিকন সিপিইউ)

*<i> আধুনিক TTS ইঞ্জিন CPU-তে খুব ধীর, তাই YourTTS, Tacotron2 ইত্যাদির মতো নিম্নমানের TTS ব্যবহার করুন।</i>

## সমর্থিত ভাষা
| **আরবি (ar)**    | **চীনা (zh)**    | **ইংরেজি (en)**   | **স্প্যানিশ (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **ফরাসি (fr)**    | **জার্মান (de)**     | **ইতালীয় (it)**   | * **পর্তুগীজ (pt)** |
| **পোলিশ (pl)**    | **তুর্কি (tr)**    | **রাশিয়ান (ru)**   | * **ডাচ (nl)**     |
| **চেক (cs)**     | **জাপানি (ja)**   | **হিন্দি (hi)**     | **বাংলা (bn)**   |
| **হাঙ্গেরীয় (hu)** | **কোরিয়ান (ko)**     | **ভিয়েতনামী (vi)**| **সুইডিশ (sv)**   |
| **Persian (fa)**   | ** *Yoruba (yo)**     | **Swahili (sw)** * **ইন্দোনেশিয়ান (id)**|
| **স্লোভাক (sk)**    | **ক্রোয়েশিয়ান (hr)**   | **তামিল (ta)**     | **ডেনিশ (da)**    |
- [**+1130 languages and dialects here**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## সমর্থিত ই-বুক ফরম্যাট
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **সেরা ফলাফল**: স্বয়ংক্রিয় অধ্যায় শনাক্তকরণের জন্য `.epub` বা `.mobi`

## আউটপুট ও প্রক্রিয়াকরণ ফরম্যাট
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- প্রক্রিয়াকরণ ফরম্যাট lib/conf.py-তে পরিবর্তন করা যায়

## উপলব্ধ SML ট্যাগ
- `[break]` — নীরবতা (এলোমেলো পরিসর **0.3–0.6 sec.**)
- `[pause]` — নীরবতা (এলোমেলো পরিসর **1.0–1.6 sec.**)
- `[pause:N]` — নির্দিষ্ট বিরতি (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — ডিফল্ট বা GUI/CLI থেকে নির্বাচিত ভয়েস থেকে ভয়েস পরিবর্তন করুন
- `[emotion:sadness]...[/emotion]` — Zonos only: emotion for a passage (happiness, sadness, disgust, fear, surprise, anger, other, neutral) or a mix like `[emotion:sadness=0.7,neutral=0.3]`; other engines ignore it

**আপনার ই-বুকে স্বয়ংক্রিয়ভাবে SML যোগ করার জন্য নিবেদিত আমাদের অন্য রেপোটি দেখুন -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**ইনস্টলেশন বা বাগ সমস্যা পোস্ট করার আগে, খোলা ও বন্ধ সমস্যার ট্যাবে সাবধানে অনুসন্ধান করুন<br>
এটা নিশ্চিত করতে যে আপনার সমস্যাটি ইতিমধ্যে নেই।**

দ্রষ্টব্য
**EPUB ফরম্যাটে অধ্যায়, অনুচ্ছেদ, ভূমিকা ইত্যাদি কী তা সংজ্ঞায়িত করার কোনো মানক কাঠামো নেই।<br>
তাই আপনাকে প্রথমে ম্যানুয়ালি সেই সমস্ত টেক্সট সরিয়ে ফেলতে হবে যা আপনি অডিওতে রূপান্তর করতে চান না।**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook ইনস্টল / চালান**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac লঞ্চার**  
     `Mac Ebook2Audiobook Launcher.command`-এ ডাবল ক্লিক করুন


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Windows ব্যবহারকারীদের জন্য নোট: প্রশাসক অনুমতি ছাড়াই অনুপস্থিত প্রোগ্রাম ইনস্টল করতে scoop ইনস্টল করা হয়।</i>
   
1. **ওয়েব অ্যাপ খুলুন**: ওয়েব অ্যাপে প্রবেশ করতে এবং ই-বুক রূপান্তর করতে টার্মিনালে প্রদত্ত URL-এ ক্লিক করুন। `http://localhost:7860/`
2. **পাবলিক লিঙ্কের জন্য**:
   `./ebook2audiobook.command --share` (লিনাক্স/ম্যাকওএস)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (সব ওএস)

> [!IMPORTANT]
**যদি স্ক্রিপ্ট বন্ধ করে আবার চালানো হয়, তাহলে আপনাকে আপনার Gradio GUI ইন্টারফেস রিফ্রেশ করতে হবে<br>
যাতে ওয়েব পৃষ্ঠাটি নতুন কানেকশন সকেটে পুনরায় সংযুক্ত হতে পারে।**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: আপনার ই-বুক ফাইলের পথ
  - **[--voice]**: ভয়েস ক্লোনিং ফাইল পথ (ঐচ্ছিক)
  - **[--language]**: ISO-639-3-তে ভাষা কোড (অর্থাৎ: ইতালীয়র জন্য ita, ইংরেজির জন্য eng, জার্মানের জন্য deu...)।<br>
    ডিফল্ট ভাষা হল eng এবং ./lib/lang.py-তে সেট করা ডিফল্ট ভাষার জন্য --language ঐচ্ছিক।<br>
    ২ অক্ষরের ISO-639-1 কোডও সমর্থিত।


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
     
- **<custom_model_path>**: `model_name.zip` ফাইলের পথ,
      যাতে (tts ইঞ্জিন অনুযায়ী) সমস্ত বাধ্যতামূলক ফাইল থাকতে হবে<br>
      (দেখুন ./lib/models.py)।

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

নোট: gradio/gui মোডে, চলমান রূপান্তর বাতিল করতে, কেবল ই-বুক আপলোড উপাদানের [X]-এ ক্লিক করুন।
টিপ: যদি একটু বেশি বিরতির প্রয়োজন হয়, তাহলে ৩ সেকেন্ডের জন্য '[pause:3]' যোগ করুন ইত্যাদি।

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

## টুলস
স্বতন্ত্র সরঞ্জাম, e2a এর নিজস্ব পাইথন দিয়ে চালান (`python_env`, e2a এর প্রথম লঞ্চ দ্বারা তৈরি) ।

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

## ক্লোনড ভয়েসেস
আপনি সমর্থিত যে কোনও অডিও ফর্ম্যাটে যে কোনও ভয়েস অডিও আপলোড করতে পারেন, আদর্শ সময়কাল প্রায় 1 থেকে 5 মিলিয়ন ।
রেকর্ডিংয়ে শোরগোলের পটভূমি বা মিউজিক বাজছে কিনা তা বিবেচ্য নয় — E2A আপনার জন্য ভয়েস পরিষ্কার করবে ।

বিল্ট-ইন ক্লোনড ভয়েস লিস্ট মূলত ইংরেজিতে । আপনার যদি অন্য ভাষায় কণ্ঠের প্রয়োজন হয় তবে আনুষ্ঠানিকভাবে
তালিকায় যোগ করা হয়েছে, অনুগ্রহ করে আমাদের সাথে যোগাযোগ করুন এবং পর্যালোচনার পরে আমরা সেগুলি যোগ করব ।

## ফাইন-টিউন করা (fine-tuned) TTS মডেল
#### আপনার নিজস্ব টিটিএস মডেলটি সুর করুন

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### প্রশিক্ষণ ডেটার শব্দ অপসারণ

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### ফাইন-টিউন করা TTS মডেলের সংগ্রহ

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

কাস্টম XTTSv2 মডেলের জন্য, ভয়েসের একটি রেফারেন্স অডিও ক্লিপ বাধ্যতামূলক:

## আপনার নিজের Ebook2Audiobook কাস্টমাইজেশন
আপনি যে সেটিংস চান তা যোগ বা অপসারণ করতে libs/conf.py অবাধে পরিবর্তন করতে পারেন। আপনি যদি এটি করার পরিকল্পনা করেন, তাহলে কেবল
মূল conf.py-এর একটি কপি তৈরি করুন যাতে প্রতিটি ebook2audiobook আপডেটে আপনি আপনার পরিবর্তিত conf.py ব্যাকআপ করতে এবং মূলটি
ফিরিয়ে রাখতে পারেন। আপনাকে models.py-এর জন্যও একই প্রক্রিয়া পরিকল্পনা করতে হবে। আপনি যদি আপনার নিজের কাস্টম মডেলকে
একটি অফিসিয়াল ফাইন-টিউন করা ebook2audiobook মডেল বানাতে চান, তাহলে অনুগ্রহ করে আমাদের সাথে যোগাযোগ করুন এবং আমরা এটি প্রিসেট তালিকায় যোগ করব।

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## সাধারণ সমস্যা:
- আমার NVIDIA/ROCm/XPU/MPS GPU শনাক্ত হচ্ছে না?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU ধীর (সার্ভার smp CPU-তে ভালো) যখন GPU প্রায় রিয়েল-টাইম রূপান্তর করতে পারে।
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (তবে এতে zero-shot ভয়েস ক্লোনিং নেই, এবং এগুলি Siri মানের ভয়েস, কিন্তু cpu-তে অনেক দ্রুত)।
- "আমার নির্ভরতা সংক্রান্ত সমস্যা হচ্ছে" - কেবল docker ব্যবহার করুন, এটি সম্পূর্ণ স্বয়ংসম্পূর্ণ এবং এর headless মোড আছে,
   আরও তথ্যের জন্য docker run কমান্ডের শেষে `--help` প্যারামিটার যোগ করুন।
- "আমার কাটা অডিওর সমস্যা হচ্ছে!" - অনুগ্রহ করে এই বিষয়ে একটি ISSUE তৈরি করুন,
   আমরা প্রতিটি ভাষা বলি না এবং বাক্য বিভাজন যুক্তি ফাইন-টিউন করতে ব্যবহারকারীদের পরামর্শ প্রয়োজন।😊

## ***** রোডম্যাপ *****
- সমস্ত বৈশিষ্ট্য সর্বজনীন অবদানের জন্য উন্মুক্ত ⭐
- মডেল উন্নত করতে আমাদের সাহায্য করার জন্য যেকোনো সমর্থিত ভাষায় কথা বলা লোকদের কাছ থেকে যেকোনো সাহায্য ⭐
- [x] রূপান্তর শুরু করার আগে ব্লক/অধ্যায় প্রিভিউ
- [x] সূক্ষ্ম টেক্সট পরিবর্তনের জন্য রূপান্তরিত বাক্য অনুযায়ী সম্পাদনা
- [x] মিউজিক ইন্ট্রো, ইন্টারলুড এবং এন্ডিং জেনারেট করুন; ইন্টারলুড এবং এন্ডিং এডিট করুন
- [x] ভয়েস, বিরতি, থামা এবং আরও পরিবর্তনের জন্য SML ট্যাগ ইন্টিগ্রেশন
- [x] বিভিন্ন ভাষায় -h -help প্যারামিটার তথ্য
- [x] PDF / JPG / BMP / PNG / TIFF-এর জন্য OCR স্ক্যানিং
- [x] Notebooks ফোল্ডার [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] চীনা টেক্সট বিভাজন যাতে শব্দ ভাগ না করে তা নিশ্চিত করা এবং বিরতির সময় উন্নত করা [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] ডকার রচনা
- [x] পডম্যান রচনা
- [x] Kaggle নোটবুক
- [x] Google Colab নোটবুক
- [x] Audiobookshelf ইন্টিগ্রেশন
- [x] ই-বুক অনুবাদ বিকল্প
- [x] আউটপুট ফরম্যাট পছন্দ
- [x] মাল্টিপ্রসেসিং রূপান্তর
- [x] ব্যাচ ই-বুক ফোল্ডার রূপান্তর
- [x] GPU ডিভাইস শনাক্তকরণ
- [x] ভয়েস ক্লোনিং আপলোডের জন্য কোনও ব্যাকগ্রাউন্ড রেফারেন্স অডিওকে অস্বীকার করুন
- [x] কাস্টম সূক্ষ্ম সুরযুক্ত মডেল আপলোড
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### ব্যবহারকারীর অনুরোধ
- [ ] অন্তত xttsv2, fairseq, vits, piper-এর জন্য ইউরোপীয় পর্তুগিজ ভাষা মডেল যোগ করা (সাহায্য স্বাগত)
- [ ] অন্তত xttsv2, fairseq, vits, piper-এর জন্য সিন্ধি ভাষা মডেল যোগ করা (সাহায্য স্বাগত)

#### TTS ইঞ্জিন
- [x] ড্রামা বক্স (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed অডিও / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] ফিশ-স্পিচ / ফিশ অডিও (https://github.com/fishaudio/fish-speech)[cite: 1]
- [x] হিগস অডিও টিটিএস (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] মায়া 1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] ওমনিভয়েস (https://github.com/k2-fsa/OmniVoice)[cite: 1]
- [x] F5-TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1]
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1]
- [x] ভক্সট্রাল টিটিএস (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] চ্যাটারবক্স (https://github.com/resemble-ai/chatterbox)[cite: 1]
- [x] CosyVoice / CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1]
- [x] Index-tts / Index TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] কনফুসিয়াস 4 টিটিএস (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] বিন্দু TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] কোকোরো-টিটিএস (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] মস টিটিএস স্থানীয় / ন্যানো (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] নিউটিটিএস / নিউটিএস (https://github.com/neuphonic/neutts)[cite: 1]
- [x] পকেট টিটিএস (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] গ্র্যাডিয়াম ফোনন (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] সুপারটনিক (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] পাইপার (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] ফেয়ারসিক (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] কচ্ছপ (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] জোনোস (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] বার্ক (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] অর্ফিয়াস-টিটিএস (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] স্পার্ক-টিটিএস (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Readme অনুবাদ
- [x] আরবি (ara)
- [x] চীনা (zho)
- [x] ইংরেজি (eng)
- [x] স্প্যানিশ (SPA)
- [x] ফ্রেঞ্চ (FRA)
- [x] জার্মান (deu)
- [x] ইতালীয় (ita)
- [x] পর্তুগীজ (por)
- [x] পোলিশ (পোল)
- [x] তুর্কি (tur)
- [x] রাশিয়ান (rus)
- [x] ডাচ (এনএলডি)
- [x] চেক (সিইএস)
- [x] জাপানি (jpn)
- [x] হিন্দি (hin)
- [x] বাংলা (ben)
- [x] হাঙ্গেরিয়ান (হান)
- [x] কোরিয়ান (কোর)
- [x] ভিয়েতনামী (vie)
- [x] সুইডিশ (SWE)
- [x] ফার্সি (FAS)
- [x] Yoruba (yor)
- [x] সোয়াহিলি (সোয়া)
- [x] ইন্দোনেশীয় (ind)
- [x] স্লোভাক (slk)
- [x] ক্রোয়েশীয় (hrv)

#### 💻 ওএস কম্প্যাটিবিলিটি
- [x] 🪟 উইন্ডোজ x86
- [x] 🪟 আর্ম উইন্ডোজ
- [x] 🍎 ম্যাক ইন্টেল x86
- [x] 🍎 অ্যাপল সিলিকন ম্যাক
- [x] 🐧 লিনাক্স x86
- [x] 🐧 আর্ম লিনাক্স

**********

## মডেল প্রশিক্ষণ ইত্যাদির জন্য অতিরিক্ত ওভারকিল (সমস্ত সমর্থিত Coqui-tts মডেল এবং piper-tts একটি সহজ কমান্ডে) 
- @ DrewThomasson সম্পর্কে তথ্যের জন্য, তিনি বর্তমানে এটির উন্নয়নে কাজ করছেন, [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [x] Make a easy to use training gui for all coqui-tts models in the [ljspeech format training recipes](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech) Completed at [Universal TTS Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)


## অবদানকারীদের জন্য Python কোড স্বাভাবিকীকরণ তথ্য
- ফাংশন এবং ক্লাসের মধ্যে ছাড়া, কোডের মধ্যে কোনো খালি লাইন নেই।
- dict() এবং json ছাড়া সমস্ত কী-এর জন্য একক উদ্ধৃতি ব্যবহৃত হয়। dict['key'] সর্বদা একক উদ্ধৃতি দিয়ে কল করা হয়
- ৪ স্পেস ইন্ডেন্টেশন, একদমই কোনো ট্যাব নয়
- সমস্ত ফাংশন এবং তাদের আর্গুমেন্ট ও রিটার্ন মান ঘোষণার জন্য কঠোর টাইপিং
- আর্গুমেন্ট এবং তার টাইপিংয়ের মধ্যে কোনো স্পেস নেই, ফাংশন, "->" এবং রিটার্ন মানের মধ্যে কোনো স্পেস নেই

উদাহরণ:

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

## বিটা পরীক্ষার জন্য হার্ডওয়্যার দান খোঁজা হচ্ছে
আমরা আমাদের উন্নয়ন পরীক্ষা করার জন্য যেকোনো ধরনের হার্ডওয়্যার গ্রহণ করি যেমন:
- Nvidia সাপোর্টিং কুদা >= 11.8
- XPU ইন্টেল কার্ড
- ROCm AMD কার্ড সমর্থন করে ROCm >=5.7

@DrewThomasson আপনি যদি যেকোনো উপায়ে সাহায্য করতে চান! 😃
<!--
## আমাদের পরিষেবা বাড়াতে আপনার কি একটি GPU ভাড়া নেওয়ার প্রয়োজন?
- এখানে একটি জরিপ খোলা আছে https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## ক্রেডিট
-  - টেক্সট-টু-স্পীচের জন্য একটি গভীর শেখার টুলকিট, গবেষণা এবং উত্পাদনে যুদ্ধ-পরীক্ষিত । [Coqui-tts](https://github.com/idiap/coqui-ai-TTS)
-  - দ্রুত এবং স্থানীয় নিউরাল টেক্সট-টু-স্পিচ ইঞ্জিন । [Piper-tts](https://github.com/OHF-Voice/piper1-gpl)
-  -- Zonos2 এর জন্য ggml ইনফারেন্স কোড । [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp)
-  - ggml দ্বারা চালিত অডিও মডেলের জন্য একটি অল-ইন-ওয়ান, খাঁটি C++ ইনফারেন্স ইঞ্জিন । [Audio.cpp](https://github.com/0xShug0/audio.cpp)

## বিশেষ ধন্যবাদ
সমস্ত আর্থিক এবং কোড অবদানকারীদের জন্য, প্রতিটি অবদান এবং পরামর্শ E2A এর গুণমান উন্নত করতে সহায়তা করে ।