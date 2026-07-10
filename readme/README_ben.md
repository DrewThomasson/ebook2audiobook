# 📚 ebook2audiobook (E2A)
অধ্যায় ও মেটাডেটা সহ ই-বুক থেকে অডিওবুকে রূপান্তরকারী CPU/GPU কনভার্টার<br/>
উন্নত TTS ইঞ্জিন ইত্যাদি ব্যবহার করে।<br/>
ভয়েস ক্লোনিং এবং ১১৫৮টি ভাষা সমর্থন করে!
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
- [বৈশিষ্ট্য](#features)
- [গ্রাফিকাল ইন্টারফেস](#gui-interface)
- [ডেমো](#demos)
- [সমর্থিত ভাষা](#supported-languages)
- [ন্যূনতম প্রয়োজনীয়তা](#hardware-requirements)
- [ব্যবহার](#instructions)
  - [স্থানীয়ভাবে চালান](#instructions)
    - [Gradio ওয়েব ইন্টারফেস চালু করা](#instructions)
    - [মৌলিক Headless ব্যবহার](#basic-usage)
    - [Headless কাস্টম XTTS মডেল ব্যবহার](#example-of-custom-model-zip-upload)
    - [সহায়তা কমান্ড আউটপুট](#help-command-output)
  - [দূরবর্তীভাবে চালান](#run-remotely)
  - [Docker](#docker)
    - [চালানোর ধাপ](#docker)
    - [সাধারণ Docker সমস্যা](#common-docker-issues)
  
- [ফাইন-টিউন করা TTS মডেল](#fine-tuned-tts-models)
  - [ফাইন-টিউন করা TTS মডেলের সংগ্রহ](#fine-tuned-tts-collection)
  - [XTTSv2 প্রশিক্ষণ](#fine-tune-your-own-xttsv2-model)
- [সমর্থিত ই-বুক ফরম্যাট](#supported-ebook-formats)
- [আউটপুট ফরম্যাট](#output-and-process-formats)
- [পুরনো সংস্করণে ফিরে যাওয়া](#reverting-to-older-versions)
- [সাধারণ সমস্যা](#common-issues)
- [বিশেষ ধন্যবাদ](#special-thanks)
- [সূচিপত্র](#table-of-contents)


## বৈশিষ্ট্য
- 🔧 **সমর্থিত TTS ইঞ্জিন**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **একাধিক ফাইল ফরম্যাট রূপান্তর করুন**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 সংক্ষিপ্ত টেক্সট সরাসরি অডিওতে রূপান্তর করার জন্য **টেক্সট এরিয়া**
- 🔍 ছবি হিসেবে টেক্সট পৃষ্ঠা সহ ফাইলের জন্য **OCR স্ক্যানিং**
- 🔊 **উচ্চমানের টেক্সট-টু-স্পিচ**, প্রায় রিয়েল-টাইম থেকে প্রায় বাস্তব ভয়েস পর্যন্ত
- 🗣️ আপনার নিজের ভয়েস ফাইল ব্যবহার করে **ঐচ্ছিক ভয়েস ক্লোনিং**
- 🌐 **১১৫৮টি ভাষা সমর্থন করে** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **কম সম্পদ-বান্ধব** — **2 GB RAM / 1 GB VRAM (ন্যূনতম)**-এ চলে
- 🎵 **অডিওবুক আউটপুট ফরম্যাট**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML ট্যাগ সমর্থিত** — বিরতি, থামা, ভয়েস পরিবর্তন ইত্যাদির সূক্ষ্ম নিয়ন্ত্রণ ([see below](#sml-tags-available))
- 🧩 আপনার নিজের প্রশিক্ষিত মডেল ব্যবহার করে **ঐচ্ছিক কাস্টম মডেল** (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ E2A টিম দ্বারা প্রশিক্ষিত **ফাইন-টিউন করা প্রিসেট মডেল**<br/>
     <i>(আপনার অতিরিক্ত ফাইন-টিউন করা মডেলের প্রয়োজন হলে, অথবা অফিসিয়াল প্রিসেট তালিকায় আপনার মডেল শেয়ার করতে চাইলে আমাদের সাথে যোগাযোগ করুন)</i>


##  হার্ডওয়্যার প্রয়োজনীয়তা
- RAM ন্যূনতম 2GB, 8GB প্রস্তাবিত।
- VRAM ন্যূনতম 1GB, 4GB প্রস্তাবিত।
- windows-এ চালানোর সময় ভার্চুয়ালাইজেশন সক্ষম (শুধুমাত্র Docker)।
- CPU, XPU (intel, AMD, ARM)*।
- CUDA, ROCm, JETSON
- MPS (Apple Silicon CPU)

*<i> আধুনিক TTS ইঞ্জিন CPU-তে খুব ধীর, তাই YourTTS, Tacotron2 ইত্যাদির মতো নিম্নমানের TTS ব্যবহার করুন।</i>

## সমর্থিত ভাষা
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+১১৩০টি ভাষা ও উপভাষা এখানে**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


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

**আপনার ই-বুকে স্বয়ংক্রিয়ভাবে SML যোগ করার জন্য নিবেদিত আমাদের অন্য রেপোটি দেখুন -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**ইনস্টলেশন বা বাগ সমস্যা পোস্ট করার আগে, খোলা ও বন্ধ সমস্যার ট্যাবে সাবধানে অনুসন্ধান করুন<br>
এটা নিশ্চিত করতে যে আপনার সমস্যাটি ইতিমধ্যে নেই।**

>[!NOTE]
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
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

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
- NOTE: MPS is not exposed in docker so CPU must be used
  
### সাধারণ Docker সমস্যা
- আমার NVIDIA GPU শনাক্ত হচ্ছে না?? -> [GPU সমস্যা Wiki পৃষ্ঠা](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## ফাইন-টিউন করা (fine-tuned) TTS মডেল
#### আপনার নিজের XTTSv2 মডেল ফাইন-টিউন করুন

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


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
- [ ] সূক্ষ্ম টেক্সট পরিবর্তনের জন্য রূপান্তরিত বাক্য অনুযায়ী সম্পাদনা
- [x] ভয়েস, বিরতি, থামা এবং আরও পরিবর্তনের জন্য SML ট্যাগ ইন্টিগ্রেশন 
- [x] বিভিন্ন ভাষায় -h -help প্যারামিটার তথ্য
- [x] PDF / JPG / BMP / PNG / TIFF-এর জন্য OCR স্ক্যানিং
- [x] Notebooks ফোল্ডার [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] চীনা টেক্সট বিভাজন যাতে শব্দ ভাগ না করে তা নিশ্চিত করা এবং বিরতির সময় উন্নত করা [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle Notebook
- [x] Google Colab Notebook
- [ ] [একটি iOS অ্যাপ তৈরি করা](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [একটি android অ্যাপ তৈরি করা](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Audiobookshelf ইন্টিগ্রেশন

#### অতিরিক্ত বিকল্প
- [x] ই-বুক অনুবাদ বিকল্প
- [x] আউটপুট ফরম্যাট পছন্দ
- [x] ব্যাচ ই-বুক ফোল্ডার
- [x] মাল্টিপ্রসেসিং রূপান্তর
- [x] ব্যাচ ই-বুক ফোল্ডার রূপান্তর
- [x] GPU ডিভাইস শনাক্তকরণ
- [x] আপলোড করা ভয়েস ক্লোনিংয়ের জন্য যেকোনো রেফারেন্স অডিওর শব্দ অপসারণ,
- [x] কাস্টম মডেল আপলোড (আপাতত শুধু XTTSv2। চাহিদা অনুযায়ী আরও)
- [ ] অন্তত xttsv2, fairseq, vits, piper-এর জন্য ইউরোপীয় পর্তুগিজ ভাষা মডেল যোগ করা (সাহায্য স্বাগত)
- [ ] অন্তত xttsv2, fairseq, vits, piper-এর জন্য সিন্ধি ভাষা মডেল যোগ করা (সাহায্য স্বাগত)

#### TTS ইঞ্জিন
- [x] XTTSv2
- [x] বাকল
- [x] ফেয়ারসিক
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] কচ্ছপ
- [x] GlowTTS
- [x] পাইপার
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] ফিশ-স্পিচ (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] চ্যাটারবক্স (https://github.com/resemble-ai/chatterbox)
- [ ] সুপারটোনিক (https://github.com/supertone-inc/supertonic)
- [ ] স্পার্ক-টিটিএস (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] কোকোরো-টিটিএস (https://github.com/hexgrad/kokoro)
- [ ] ওমনিভয়েস (https://github.com/k2-fsa/OmniVoice)
- [ ] জোনোস (https://github.com/Zyphra/Zonos)
- [ ] Style-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] অর্ফিয়াস-টিটিএস (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Readme অনুবাদ
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

#### 🐍 OS সামঞ্জস্যতা
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## মডেল প্রশিক্ষণ ইত্যাদির জন্য অতিরিক্ত ওভারকিল (সমস্ত সমর্থিত Coqui-tts মডেল এবং piper-tts একটি সহজ কমান্ডে) 
- এই সম্পর্কে তথ্যের জন্য @DrewThomasson, তিনি বর্তমানে এর উন্নয়নে কাজ করছেন, [কার্য-চলমান রেপো এখানে](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] ljspeech ফরম্যাট প্রশিক্ষণ রেসিপিতে সমস্ত coqui-tts মডেলের জন্য একটি সহজ-ব্যবহারযোগ্য প্রশিক্ষণ gui তৈরি করুন [coqui tts থেকে এখানে](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


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
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson আপনি যদি যেকোনো উপায়ে সাহায্য করতে চান! 😃
<!--
## আমাদের পরিষেবা বাড়াতে আপনার কি একটি GPU ভাড়া নেওয়ার প্রয়োজন?
- এখানে একটি জরিপ খোলা আছে https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## বিশেষ ধন্যবাদ
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 অধ্যায় সংরক্ষণের আরও ভালো পদ্ধতির জন্য](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
