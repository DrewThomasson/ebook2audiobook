<a id="ebook2audiobook"></a>
# 📚 کتاب الکترونیکی به کتاب صوتی (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

مبدل CPU/GPU از کتاب الکترونیکی به کتاب صوتی همراه با فصل‌ها و فراداده<br/>
با استفاده از موتورهای پیشرفته TTS و موارد دیگر.<br/>
پشتیبانی از شبیه‌سازی صدا و ۱۶۹۶ زبان!
> [!IMPORTANT]
**این ابزار تنها برای استفاده با کتاب‌های الکترونیکی فاقد DRM که به‌صورت قانونی به دست آمده‌اند، در نظر گرفته شده است.** <br>
نویسندگان مسئول هیچ‌گونه سوءاستفاده از این نرم‌افزار یا هرگونه پیامد قانونی ناشی از آن نیستند. <br>
از این ابزار مسئولانه و در چارچوب تمام قوانین قابل اجرا استفاده کنید.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### با تشکر از حمایت توسعه‌دهندگان کتاب‌های صوتی الکترونیکی!
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### اجرا به صورت محلی
[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)Instructions
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### اجرای از راه دور
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### رابط گرافیکی (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>برای دیدن تصاویر رابط گرافیکی وب کلیک کنید</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
## نمونه‌ها

**نمونه صدای پیش‌فرض جدید**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>نمونه‌های بیشتر</summary>

**صدای ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**صدای روز بارانی**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**صدای اسکارلت**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**صدای دیوید اتنبرو** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**نمونه**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

<a id="table-of-contents"></a>
## فهرست مطالب
- [ebook2audiobook](#ebook2audiobook)
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
  - ] [Preload models for offline installs](#preload-models)
  - ] [Translate ebooks out of e2a](#translate-ebooks)

- [Cloned Voices](#cloned-voices)
- [Fine Tuned TTS models](#fine-tuned-tts-models) 
  - [Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
  - [Train TTS Model](#fine-tune-your-own-tts-model)
- [Supported eBook Formats](#supported-ebook-formats)
- [Output Formats](#output-and-process-formats)
- [Revert to older Version](#reverting-to-older-versions)
- [Common Issues](#common-issues)
- [Contributing](#contributing)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


<a id="features"></a>
## ویژگی‌ها
- 🔧 **موتورهای TTS پشتیبانی شده**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **تبدیل چندین قالب فایل**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **ناحیه متن** برای تبدیل مستقیم یک متن کوتاه به صدا
- 🔍 **اسکن OCR** برای فایل‌هایی با صفحات متنی به‌صورت تصویر
- 🔊 **تبدیل متن به گفتار باکیفیت**، از تقریباً بلادرنگ تا صدایی تقریباً واقعی
- 🗣️ **شبیه‌سازی صدای اختیاری** با استفاده از فایل صوتی خودتان
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **سازگار با منابع کم** — روی **2 GB RAM / 1 GB VRAM (حداقل)** اجرا می‌شود
- 🎵 **قالب‌های خروجی کتاب صوتی**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **برچسب‌های SML پشتیبانی می‌شوند** — کنترل دقیق وقفه‌ها، مکث‌ها، تعویض صدا و موارد بیشتر ([see below](#sml-tags-available))
- 🧩 **مدل سفارشی اختیاری** با استفاده از مدل آموزش‌دیده خودتان (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **مدل‌های پیش‌تنظیم تنظیم‌دقیق‌شده** که توسط تیم E2A آموزش دیده‌اند<br/>
     <i>(اگر به مدل‌های تنظیم‌دقیق‌شده بیشتری نیاز دارید، یا اگر می‌خواهید مدل‌های خود را در فهرست پیش‌تنظیم رسمی به اشتراک بگذارید، با ما تماس بگیرید)</i>


<a id="hardware-requirements"></a>
##  نیازمندی‌های سخت‌افزاری
- ۲ گیگابایت RAM حداقل، ۸ گیگابایت توصیه‌شده.
- ۱ گیگابایت VRAM حداقل، ۴ گیگابایت توصیه‌شده.
- مجازی‌سازی هنگام اجرا روی windows فعال باشد (فقط Docker).
- CPU، XPU (intel، AMD، ARM)*.
- CUDA، ROCm، JETSON
- MPS (پردازنده Apple Silicon)

*<i> موتورهای مدرن TTS روی CPU بسیار کند هستند، بنابراین از TTS با کیفیت پایین‌تر مانند YourTTS، Tacotron2 و غیره استفاده کنید.</i>

<a id="supported-languages"></a>
## زبان‌های پشتیبانی‌شده
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## قالب‌های کتاب الکترونیکی پشتیبانی‌شده
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **بهترین نتایج**: `.epub` یا `.mobi` برای تشخیص خودکار فصل‌ها

<a id="output-and-process-formats"></a>
## قالب‌های خروجی و پردازش
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- قالب پردازش را می‌توان در lib/conf.py تغییر داد

## برچسب‌های SML موجود
- `[break]` — سکوت (بازه تصادفی **0.3–0.6 sec.**)
- `[pause]` — سکوت (بازه تصادفی **1.0–1.6 sec.**)
- `[pause:N]` — مکث ثابت (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — تعویض صدا از صدای پیش‌فرض یا انتخاب‌شده از GUI/CLI
- `[emotion:sadness]...[/emotion]` — فقط Zonos: احساسی برای یک متن (شادی، غم، انزجار، ترس، تعجب، خشم، سایر، خنثی) یا ترکیبی مانند `[emotion:sadness=0.7,neutral=0.3]`؛ موتورهای دیگر آن را نادیده می‌گیرند

**مخزن دیگر ما را که به افزودن خودکار SML در کتاب الکترونیکی شما اختصاص دارد، بررسی کنید -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**پیش از ارسال مشکل نصب یا باگ، با دقت در زبانه مسائل باز و بسته جستجو کنید<br>
تا مطمئن شوید مشکل شما از قبل وجود ندارد.**

یادداشت
**قالب EPUB فاقد هرگونه ساختار استاندارد برای تعریف اینکه فصل، پاراگراف، مقدمه و غیره چیست، می‌باشد.<br>
بنابراین ابتدا باید هر متنی را که نمی‌خواهید به صدا تبدیل شود، به‌صورت دستی حذف کنید.**


<a id="instructions"></a>
### دستورالعمل‌ها
1. **کلون کردن مخزن**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook را نصب / اجرا کنید**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>توجه برای کاربران MacOS: برای نصب برنامه‌های ناموجود، homebrew نصب می‌شود.</i>
     
   - **راه‌انداز Mac**  
     روی `Mac Ebook2Audiobook Launcher.command` دوبار کلیک کنید


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     یا
     روی `ebook2audiobook.cmd` دوبار کلیک کنید

     <i>توجه برای کاربران Windows: scoop برای نصب برنامه‌های ناموجود بدون امتیازات مدیر نصب می‌شود.</i>
   
1. **برنامه وب را باز کنید**: برای دسترسی به برنامه وب و تبدیل کتاب‌های الکترونیکی، روی URL ارائه‌شده در ترمینال کلیک کنید. `http://localhost:7860/`
2. **برای پیوند عمومی**:
   `./ebook2audiobook.command --share` (لینوکس/مک او اس)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (همه سیستم‌عامل‌ها، فقط یک بار نصب شده و با پایتون موجود در پوشه python_env آن)

> [!IMPORTANT]
**اگر اسکریپت متوقف و دوباره اجرا شود، باید رابط گرافیکی Gradio خود را تازه‌سازی کنید<br>
تا صفحه وب بتواند دوباره به سوکت اتصال جدید متصل شود.**

<a id="basic-usage"></a>
### استفاده پایه
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: مسیر فایل کتاب الکترونیکی شما
  - **[--voice]**: مسیر فایل شبیه‌سازی صدا (اختیاری)
  - **[--language]**: کد زبان به‌صورت ISO-639-3 (یعنی: ita برای ایتالیایی، eng برای انگلیسی، deu برای آلمانی...).<br>
    زبان پیش‌فرض eng است و --language برای زبان پیش‌فرض تنظیم‌شده در ./lib/lang.py اختیاری است.<br>
    کدهای دوحرفی ISO-639-1 نیز پشتیبانی می‌شوند.


<a id="example-of-custom-model-zip-upload"></a>
###  نمونه بارگذاری مدل سفارشی به صورت Zip
  (باید یک فایل .zip شامل فایل‌های الزامی مدل باشد. نمونه برای XTTSv2: config.json، model.pth، vocab.json و ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>توجه: ref.wav مدل سفارشی شما همیشه صدایی است که برای تبدیل انتخاب می‌شود</i>
     
- **<custom_model_path>**: مسیر فایل `model_name.zip`،
      که باید (بسته به موتور tts) شامل تمام فایل‌های اجباری باشد<br>
      (به ./lib/models.py مراجعه کنید).

### راهنمای کامل با فهرست همه پارامترهای قابل استفاده
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **یا برای همه سیستم‌عامل‌ها**
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

توجه: در حالت gradio/gui، برای لغو یک تبدیل در حال اجرا، کافی است روی [X] مؤلفه بارگذاری کتاب الکترونیکی کلیک کنید.
نکته: اگر به مکث کمی بیشتر نیاز است، برای ۳ ثانیه '[pause:3]' و غیره را اضافه کنید.

<a id="docker"></a>
### Docker
1. **کلون کردن مخزن**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **ساخت کانتینر**
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
4. **اجرای کانتینر:**
```bash
Docker run image:
    Gradio/GUI:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc...]
    Headless mode:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
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
- توجه: MPS در Docker در دسترس نیست، بنابراین باید از CPU استفاده شود
- توجه: volume نام‌دار `e2a_venvs` موتورهای TTS نصب‌شده در venv مخصوص هر کدام (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM و غیره) را
  بین اجراهای کانتینر حفظ می‌کند، بنابراین هر بار دوباره نصب نمی‌شوند. برای بازنشانی آن‌ها: `docker volume rm e2a_venvs`

<a id="tools"></a>
## ابزارها
ابزارهای مستقلی که با پایتون خود e2a اجرا می‌شوند (`python_env`، که در اولین اجرای e2a ساخته می‌شود).

<a id="preload-models"></a>
### پیش‌بارگیری مدل‌ها برای نصب آفلاین: `tools/preload_models.py`
همه مدل‌هایی را که e2a استفاده می‌کند (موتورهای TTS و نسخه‌های fine-tune آن‌ها، تبدیل صدا، stanza، pyannote، demucs،
میان‌پرده‌های موسیقی، بسته‌های argos-translate، داده‌های tesseract، jieba و صداها) در یک پوشه دانلود می‌کند که ساختار آن
دقیقاً مانند `./models` است، مثلاً یک فلش USB. در دستگاه آفلاین، آن پوشه را در `./models` مربوط به e2a کپی کنید
و پوشه `voices` را که کنار آن نوشته شده در `./voices` مربوط به e2a.
هر کار تمام‌شده در `<models_dir>/.e2a_downloads.json` ثبت می‌شود: اجرای دوباره کارهای انجام‌شده را رد می‌کند و
کارهای قطع‌شده (ctrl-c، خرابی، جدا شدن فلش) را پس از حذف فایل‌های ناقص‌شان از نو شروع می‌کند.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` کارها و وضعیت آن‌ها (انجام‌شده، قطع‌شده، در انتظار) را بدون دانلود چیزی فهرست می‌کند.

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
### ترجمه کتاب‌های الکترونیکی خارج از e2a: `tools/translate_ebook.sh` / `tools/translate_ebook.cmd`
فایل‌های EPUB/AZW3، یک پوشه کامل (`-r` برای زیرپوشه‌هایش) یا فهرستی از مسیرها (`@list.txt`) را
به صورت آفلاین به کتاب‌های الکترونیکی ترجمه‌شده تبدیل می‌کند، با افزونه calibre به نام Argos Translate که در این فایل همراه است:
`tools/argostranslate-calibre-plugin.zip`. مستقل از تبدیل کتاب صوتی است: فقط کتاب الکترونیکی می‌نویسد.
به calibre نیاز دارد (که e2a از قبل لازم دارد) و روی `python_env` و بسته‌های argos-translate خود e2a اجرا می‌شود:
جفت زبانی که e2a از قبل استفاده می‌کند دوباره دانلود نمی‌شود، جفت ناموجود در اولین استفاده دانلود می‌شود.
افزونه در اولین استفاده در پروفایل calibre مخصوص e2a (`./run`) نصب می‌شود و calibre شما دست‌نخورده می‌ماند.
`--to fra,ara,spa` همزمان به چند زبان ترجمه می‌کند، برای هر زبان یک کتاب، و `--to all` به همه
زبان‌هایی که از زبان مبدأ قابل دسترسی‌اند (`--from`، وگرنه زبان خود هر کتاب؛ با `--no_download` فقط جفت‌زبان‌های نصب‌شده).
`--list --from eng` زبان‌هایی را که انگلیسی به آن‌ها ترجمه می‌شود فهرست می‌کند (نصب‌شده، قابل دانلود، یا از طریق انگلیسی برای
یک زبان مبدأ دیگر).
سایر قالب‌هایی که `ebook-convert` در calibre می‌خواند (PDF، DOCX، MOBI، TXT، ...) یک بار پیش از
نخستین زبان به EPUB تبدیل و به صورت EPUB ترجمه می‌شوند: وقتی زبانی مشخص نکرده باشند، که در PDF و TXT رایج است، `--from` لازم است.
بدون `-o` یا `--output_dir`، هر ترجمه کنار کتاب خود با نام `<name>.<lang>.<ext>` ذخیره می‌شود،
و کتابی که ترجمه‌اش از قبل وجود دارد رد می‌شود (`--overwrite` برای ترجمه دوباره).
اجراکننده‌های پوشه `tools/` فایل `tools/translate_ebook.py` را با `python_env` اجرا می‌کنند، بدون نیاز به فعال‌سازی،
از هر پوشه‌ای (مسیرهای نسبی از محل اجرا محاسبه می‌شوند):
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - یا مستقیماً با پایتون `python_env`: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). اگر با پایتون دیگری اجرا شود،
     اسکریپت خودش را دوباره با پایتون `python_env` اجرا می‌کند.
   - **Docker**: آن را داخل کانتینر e2a اجرا کنید، مثلاً `docker exec -it <container> python3 tools/translate_ebook.py ...`
     با مسیرهایی که از داخل کانتینر دیده می‌شوند.
   - **سرعت**: argostranslate با پیش‌فرض‌های خودش اجرا می‌شود (CTranslate2 تعداد رشته‌ها و سریع‌ترین نوع محاسبه را انتخاب می‌کند،
     int8 روی CPU)، نه با یک رشته float32 مانند e2a. برای تغییر آن‌ها `ARGOS_INTRA_THREADS` یا `ARGOS_COMPUTE_TYPE` را تنظیم کنید.

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

<a id="cloned-voices"></a>
## صداهای کلون‌شده
شما می‌توانید هر فایل صوتی را با هر یک از فرمت‌های صوتی پشتیبانی‌شده آپلود کنید، مدت زمان ایده‌آل حدود ۱ تا ۵ دقیقه است.
فرقی نمی‌کند که صدای ضبط شده نویز پس‌زمینه داشته باشد یا موسیقی در حال پخش باشد - E2A صدا را برای شما واضح‌تر می‌کند.

لیست صداهای کلون شده داخلی عمدتاً به زبان انگلیسی است. اگر به صداهایی به زبان‌های دیگر نیاز دارید تا رسماً ...
به لیست اضافه شد، لطفا با ما تماس بگیرید تا پس از بررسی، آنها را اضافه کنیم.

<a id="fine-tuned-tts-models"></a>
## مدل‌های TTS تنظیم‌دقیق‌شده (fine-tuned)
<a id="fine-tune-your-own-tts-model"></a>
#### مدل TTS خودتان را به طور دقیق تنظیم کنید

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### حذف نویز از داده‌های آموزشی

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### مجموعه مدل‌های TTS تنظیم‌دقیق‌شده

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

برای مدل سفارشی XTTSv2، یک کلیپ صوتی مرجع از صدا اجباری است:

## سفارشی‌سازی شخصی شما برای Ebook2Audiobook
شما آزادید libs/conf.py را برای افزودن یا حذف تنظیمات دلخواه خود تغییر دهید. اگر قصد این کار را دارید، کافی است یک
نسخه از conf.py اصلی تهیه کنید تا در هر به‌روزرسانی ebook2audiobook بتوانید از conf.py تغییریافته خود نسخه پشتیبان بگیرید و
نسخه اصلی را بازگردانید. باید همین روند را برای models.py نیز برنامه‌ریزی کنید. اگر می‌خواهید مدل سفارشی خود را
به یک مدل رسمی تنظیم‌دقیق‌شده ebook2audiobook تبدیل کنید، لطفاً با ما تماس بگیرید تا آن را به فهرست پیش‌تنظیم‌ها اضافه کنیم.

<a id="reverting-to-older-versions"></a>
## بازگشت به نسخه‌های قدیمی‌تر
نسخه‌ها را می‌توانید اینجا پیدا کنید -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## مشکلات رایج:
- پردازنده گرافیکی NVIDIA/ROCm/XPU/MPS من شناسایی نمی‌شود؟؟ -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU کند است (روی CPU سرور SMP بهتر است) در حالی که GPU می‌تواند تبدیل تقریباً بلادرنگ داشته باشد.
   ] [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (با این حال شبیه‌سازی صدای zero-shot ندارد، و صداها با کیفیت Siri هستند، اما روی cpu بسیار سریع‌تر است).
- «مشکلاتی با وابستگی‌ها دارم» - کافی است از docker استفاده کنید، کاملاً مستقل است و حالت بدون رابط دارد،
   برای اطلاعات بیشتر پارامتر  را به انتهای دستور docker run اضافه کنید. `--help`
- «مشکل قطع شدن صدا دارم!» - لطفاً یک ISSUE در این مورد ایجاد کنید،
   ما به همه زبان‌ها صحبت نمی‌کنیم و برای تنظیم دقیق منطق تقسیم جمله به توصیه کاربران نیاز داریم.😊

## ***** نقشه راه *****
- تمام ویژگی‌ها برای مشارکت‌های عمومی باز هستند ⭐
- هرگونه کمک از افرادی که به یکی از زبان‌های پشتیبانی‌شده صحبت می‌کنند تا به ما در بهبود مدل‌ها کمک کنند ⭐
- [x] پیش‌نمایش بلوک‌ها/فصل‌ها پیش از شروع تبدیل
- [x] ویرایش به‌ازای هر جمله تبدیل‌شده برای تغییر دقیق متن
- [x] تولید مقدمه، میان‌پرده و پایان موسیقی؛ ویرایش میان‌پرده‌ها و پایان‌ها
- [x] یکپارچه‌سازی برچسب‌های SML برای صدا، مکث، وقفه و تغییرات بیشتر
- [x] اطلاعات پارامتر -h -help به زبان‌های مختلف
- [x] اسکن OCR برای PDF / JPG / BMP / PNG / TIFF
- [x] پوشه Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] اطمینان از اینکه تقسیم متن چینی کلمات را تقسیم نکند و بهبود زمان‌بندی مکث‌ها [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] داکرفایل
- [x] آهنگسازی داکر
- [x] پودمن آهنگسازی
- [x] دفترچه Kaggle
- [x] دفترچه Google Colab
- [x] یکپارچه‌سازی Audiobookshelf
- [x] گزینه ترجمه کتاب الکترونیکی
- [x] انتخاب‌های قالب خروجی
- [x] تبدیل چندپردازشی
- [x] تبدیل دسته‌ای پوشه کتاب الکترونیکی
- [x] تشخیص دستگاه GPU
- [x] حذف نویز هرگونه صدای مرجع پس‌زمینه برای آپلود شبیه‌سازی صدا
- [x] آپلود مدل سفارشی و تنظیم‌شده

#### درخواست های کاربر
- [ ] افزودن مدل زبانی پرتغالی اروپایی حداقل برای xttsv2، fairseq، vits، piper (از کمک استقبال می‌شود)
- [ ] افزودن مدل زبانی سندی حداقل برای xttsv2، fairseq، vits، piper (از کمک استقبال می‌شود)

#### موتورهای TTS
- [x] DramaBox ( 1] https://github.com/dramabox-ai/dramabox)[cite:
- [x] FireRed Audio / FireRedTTS3 ( 1] https://github.com/FireRedTeam/FireRedTTS)[cite:
- [x] گفتار ماهی / صدای ماهی ( 1) https://github.com/fishaudio/fish-speech)[cite:
- [x] صدای هیگز TTS ( 1) https://github.com/higgs-audio/higgs-audio)[cite:
- [x] Maya1 ( 1] https://github.com/maya-ai/maya1)[cite:
- [x] OmniVoice ( 1] https://github.com/k2-fsa/OmniVoice)[cite:
- [x] F5-TTS ( 1) https://github.com/swivid/f5-tts)[cite:
- [x] Qwen3-TTS ( 1) https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite:
- [x] VibeVoice ( 1] https://github.com/vibevoice-community/VibeVoice)[cite:
- [x] VoxCPM2 ( 1) https://github.com/voxcpm/voxcpm)[cite:
- [x] Voxtral TTS ( 1] https://github.com/voxtral/voxtral-tts)[cite:
- [x] چت باکس ( 1) https://github.com/resemble-ai/chatterbox)[cite:
- [x] CosyVoice / CosyVoice3 ( 1) https://github.com/FunAudioLLM/CosyVoice)[cite:
- [x] فهرست-tts / فهرست TTS2 ( 1) https://github.com/index-tts/index-tts)[cite:
- [x] XTTSv2 ( 1) https://github.com/coqui-ai/XTTS)[cite:
- [x] صدای نسیم ( 1) https://github.com/FreedomIntelligence/Breeze-TTS)[cite:
- [x] Confucius4 TTS ( 1) https://github.com/confucius-tts/confucius4)[cite:
- [x] نقطه‌ها TTS ( 1) https://github.com/dot-audio/dots-tts)[cite:
- [x] GPT-SoVITS ( 1) https://github.com/RVC-Boss/GPT-SoVITS)[cite:
- [x] Kokoro-TTS ( 1] https://github.com/hexgrad/kokoro)[cite:
- [x] KugelAudio ( 1] https://github.com/kugel-audio/kugelaudio)[cite:
- [x] TTS زاغی ( 1) https://github.com/magpie-tts/magpie-tts)[cite:
- [x] MioTTS ( 1] https://github.com/mio-tts/miotts)[cite:
- [x] Moss TTS محلی / نانو ( 1) https://github.com/OpenBMB/MossTTS)[cite:
- [x] NewTTS / NeuTTS ( 1) https://github.com/neuphonic/neutts)[cite:
- [x] Pocket TTS ( 1] https://github.com/pocket-tts/pocket-tts)[cite:
- [x] گرادیوم فونون ( 1) https://github.com/gradium-ai/xn-ptts)[cite:
- [x] Supertonic ( 1] https://github.com/supertone-inc/supertonic)[cite:
- [x] Irodori TTS ( 1] https://github.com/irodori-tts/irodori-tts)[cite:
- [x] Piper ( 1] https://github.com/rhasspy/piper)[cite:
- [x] VITS ( 1] https://github.com/jaywalnut330/vits)[cite:
- [x] Fairseq ( 1] https://github.com/facebookresearch/fairseq)[cite:
- [x] GlowTTS ( 1) https://github.com/jaywalnut330/glow-tts)[cite:
- [x] Tacotron2 ( 1] https://github.com/NVIDIA/Tacotron2)[cite:
- [x] Tortoise ( 1] https://github.com/neonbjb/tortoise-tts)[cite:
- [x] Zonos ( 1] https://github.com/Zyphra/Zonos)[cite:
- [x] Bark ( 1] https://github.com/suno-ai/bark)[cite:
- [x] YourTTS ( 1] https://github.com/Edresson/YourTTS)[cite:
- [x] اورفئوس-TTS ( https://github.com/canopyai/Orpheus-TTS)
- [x] اوپن ویس ( https://github.com/myshell-ai/OpenVoice)
- [x] چتTTS ( https://github.com/2noise/ChatTTS)
- [x] جرقه-TTS ( https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS ( https://github.com/myshell-ai/MeloTTS)
- [x] CSM ( https://github.com/SesameAILabs/csm)

#### ترجمه Readme
- [x] عربی (عربی)
- [x] چینی (ژو)
- [x] انگلیسی (eng)
- [x] اسپانیایی (اسپا)
- [x] فرانسوی (fra)
- [x] آلمانی (deu)
- [x] ایتالیایی (ita)
- [x] پرتغالی (por)
- [x] لهستانی (pol)
- [x] ترکی (تور)
- [x] روسی (روسی)
- [x] هلندی (nld)
- [x] چک (ces)
- [x] ژاپنی (ژاپنی)
- [x] هندی (هین)
- [x] بنگالی (بن)
- [x] مجارستانی (هون)
- [x] کره‌ای (کور)
- [x] ویتنامی (vie)
- [x] سوئدی (swe)
- [x] فارسی (fas)
- [x] یوروبا (یور)
- [x] سواحیلی (swa)
- [x] اندونزیایی (indonesia)
- [x] اسلواکی (slk)
- [x] کرواتی (hrv)

#### سازگاری با سیستم عامل
- [x] 🪟 ویندوز x86
- [x] 🪟 ویندوز آرم
- [x] 🍎 مک اینتل x86
- [x] 🍎 مک اپل سیلیکون
- [x] 🐧 لینوکس x86
- [x] 🐧 آرم لینوکس

**********

<a id="contributing"></a>
## مشارکت
قبل از باز کردن یک مشکل یا درخواست pull، [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md) را بخوانید: قوانین نرمال‌سازی کد پایتون،
گردش کار درخواست انشعاب و pull، راهنمای رابط کاربری گرافیکی و ترجمه‌های README، اضافه کردن موتور TTS، آزمایش.

## اهدای سخت‌افزار برای آزمایش‌های بتا مورد نیاز است
ما هر نوع سخت‌افزاری را برای آزمایش توسعه خود می‌پذیریم، مانند:
- انویدیا از کودا = 11.8 پشتیبانی می‌کند
- کارت‌های اینتل XPU
- کارت‌های گرافیک ROCm AMD که از ROCm =5.7 پشتیبانی می‌کنند

@DrewThomasson اگر می‌خواهید به هر شکلی کمک کنید! 😃
<!--
## آیا برای تقویت خدمات ما به اجاره یک GPU نیاز دارید؟
- یک نظرسنجی در اینجا باز است https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## قیمت
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS)] -- یک جعبه ابزار یادگیری عمیق برای تبدیل متن به گفتار، که در تحقیقات و تولید، آزمایش خود را پس داده است.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl)] -- موتور تبدیل متن به گفتار عصبی سریع و محلی.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- کد استنتاج ggml برای Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp)] -- یک موتور استنتاج کاملاً یکپارچه C++ برای مدل‌های صوتی، با پشتیبانی ggml.

<a id="special-thanks"></a>
## تشکر ویژه
به اطلاع همه مشارکت‌کنندگان مالی و کدنویسی می‌رساند که هر مشارکت و پیشنهادی به بهبود کیفیت E2A کمک می‌کند.