# 📚 ebook2audiobook (E2A)
مبدل CPU/GPU از کتاب الکترونیکی به کتاب صوتی همراه با فصل‌ها و فراداده<br/>
با استفاده از موتورهای پیشرفته TTS و موارد دیگر.<br/>
از شبیه‌سازی صدا و ۱۱۵۸ زبان پشتیبانی می‌کند!
> [!IMPORTANT]
**این ابزار تنها برای استفاده با کتاب‌های الکترونیکی فاقد DRM که به‌صورت قانونی به دست آمده‌اند، در نظر گرفته شده است.** <br>
نویسندگان مسئول هیچ‌گونه سوءاستفاده از این نرم‌افزار یا هرگونه پیامد قانونی ناشی از آن نیستند. <br>
از این ابزار مسئولانه و در چارچوب تمام قوانین قابل اجرا استفاده کنید.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### از پشتیبانی شما از توسعه‌دهندگان ebook2audiobook سپاسگزاریم!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### اجرای محلی

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### اجرای از راه دور
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### رابط گرافیکی (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>برای دیدن تصاویر رابط گرافیکی وب کلیک کنید</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

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

## فهرست مطالب
- [ebook2audiobook](#-ebook2audiobook)
- [ویژگی‌ها](#features)
- [رابط گرافیکی](#gui-interface)
- [نمونه‌ها](#demos)
- [زبان‌های پشتیبانی‌شده](#supported-languages)
- [حداقل نیازمندی‌ها](#hardware-requirements)
- [استفاده](#instructions)
  - [اجرای محلی](#instructions)
    - [راه‌اندازی رابط وب Gradio](#instructions)
    - [استفاده پایه بدون رابط](#basic-usage)
    - [استفاده از مدل سفارشی XTTS بدون رابط](#example-of-custom-model-zip-upload)
    - [خروجی دستور راهنما](#help-command-output)
  - [اجرای از راه دور](#run-remotely)
  - [Docker](#docker)
    - [مراحل اجرا](#docker)
    - [مشکلات رایج Docker](#common-docker-issues)
  
- [مدل‌های TTS تنظیم‌دقیق‌شده](#fine-tuned-tts-models)
  - [مجموعه مدل‌های TTS تنظیم‌دقیق‌شده](#fine-tuned-tts-collection)
  - [آموزش XTTSv2](#fine-tune-your-own-xttsv2-model)
- [قالب‌های کتاب الکترونیکی پشتیبانی‌شده](#supported-ebook-formats)
- [قالب‌های خروجی](#output-and-process-formats)
- [بازگشت به نسخه قدیمی‌تر](#reverting-to-older-versions)
- [مشکلات رایج](#common-issues)
- [تشکر ویژه](#special-thanks)
- [فهرست مطالب](#table-of-contents)


## ویژگی‌ها
- 🔧 **موتورهای TTS پشتیبانی‌شده**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **تبدیل چندین قالب فایل**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **ناحیه متن** برای تبدیل مستقیم یک متن کوتاه به صدا
- 🔍 **اسکن OCR** برای فایل‌هایی با صفحات متنی به‌صورت تصویر
- 🔊 **تبدیل متن به گفتار باکیفیت**، از تقریباً بلادرنگ تا صدایی تقریباً واقعی
- 🗣️ **شبیه‌سازی صدای اختیاری** با استفاده از فایل صوتی خودتان
- 🌐 **از ۱۱۵۸ زبان پشتیبانی می‌کند** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **سازگار با منابع کم** — روی **2 GB RAM / 1 GB VRAM (حداقل)** اجرا می‌شود
- 🎵 **قالب‌های خروجی کتاب صوتی**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **برچسب‌های SML پشتیبانی می‌شوند** — کنترل دقیق وقفه‌ها، مکث‌ها، تعویض صدا و موارد بیشتر ([see below](#sml-tags-available))
- 🧩 **مدل سفارشی اختیاری** با استفاده از مدل آموزش‌دیده خودتان (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **مدل‌های پیش‌تنظیم تنظیم‌دقیق‌شده** که توسط تیم E2A آموزش دیده‌اند<br/>
     <i>(اگر به مدل‌های تنظیم‌دقیق‌شده بیشتری نیاز دارید، یا اگر می‌خواهید مدل‌های خود را در فهرست پیش‌تنظیم رسمی به اشتراک بگذارید، با ما تماس بگیرید)</i>


##  نیازمندی‌های سخت‌افزاری
- ۲ گیگابایت RAM حداقل، ۸ گیگابایت توصیه‌شده.
- ۱ گیگابایت VRAM حداقل، ۴ گیگابایت توصیه‌شده.
- مجازی‌سازی هنگام اجرا روی windows فعال باشد (فقط Docker).
- CPU، XPU (intel، AMD، ARM)*.
- CUDA، ROCm، JETSON
- MPS (پردازنده Apple Silicon)

*<i> موتورهای مدرن TTS روی CPU بسیار کند هستند، بنابراین از TTS با کیفیت پایین‌تر مانند YourTTS، Tacotron2 و غیره استفاده کنید.</i>

## زبان‌های پشتیبانی‌شده
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+۱۱۳۰ زبان و گویش در اینجا**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## قالب‌های کتاب الکترونیکی پشتیبانی‌شده
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **بهترین نتایج**: `.epub` یا `.mobi` برای تشخیص خودکار فصل‌ها

## قالب‌های خروجی و پردازش
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- قالب پردازش را می‌توان در lib/conf.py تغییر داد

## برچسب‌های SML موجود
- `[break]` — سکوت (بازه تصادفی **0.3–0.6 sec.**)
- `[pause]` — سکوت (بازه تصادفی **1.0–1.6 sec.**)
- `[pause:N]` — مکث ثابت (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — تعویض صدا از صدای پیش‌فرض یا انتخاب‌شده از GUI/CLI

**مخزن دیگر ما را که به افزودن خودکار SML در کتاب الکترونیکی شما اختصاص دارد، بررسی کنید -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**پیش از ارسال مشکل نصب یا باگ، با دقت در زبانه مسائل باز و بسته جستجو کنید<br>
تا مطمئن شوید مشکل شما از قبل وجود ندارد.**

>[!NOTE]
**قالب EPUB فاقد هرگونه ساختار استاندارد برای تعریف اینکه فصل، پاراگراف، مقدمه و غیره چیست، می‌باشد.<br>
بنابراین ابتدا باید هر متنی را که نمی‌خواهید به صدا تبدیل شود، به‌صورت دستی حذف کنید.**


### دستورالعمل‌ها 
1. **مخزن را کلون کنید**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook را نصب / اجرا کنید**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>توجه برای کاربران macOS: homebrew برای نصب برنامه‌های ناموجود نصب می‌شود.</i>
     
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
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**اگر اسکریپت متوقف و دوباره اجرا شود، باید رابط گرافیکی Gradio خود را تازه‌سازی کنید<br>
تا صفحه وب بتواند دوباره به سوکت اتصال جدید متصل شود.**

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


###  نمونه بارگذاری مدل سفارشی به‌صورت Zip
  (باید یک فایل .zip باشد که شامل فایل‌های اجباری مدل است. نمونه برای XTTSv2: config.json، model.pth، vocab.json و ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>توجه: ref.wav مدل سفارشی شما همیشه صدای انتخاب‌شده برای تبدیل است</i>
     
- **<custom_model_path>**: مسیر فایل `model_name.zip`،
      که باید (بسته به موتور tts) شامل تمام فایل‌های اجباری باشد<br>
      (به ./lib/models.py مراجعه کنید).

### برای راهنمای مفصل همراه با فهرستی از تمام پارامترهای قابل استفاده
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **یا برای تمام سیستم‌عامل‌ها**
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

توجه: در حالت gradio/gui، برای لغو یک تبدیل در حال اجرا، کافی است روی [X] مؤلفه بارگذاری کتاب الکترونیکی کلیک کنید.
نکته: اگر به مکث کمی بیشتر نیاز است، برای ۳ ثانیه '[pause:3]' و غیره را اضافه کنید.

### Docker
1. **مخزن را کلون کنید**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **کانتینر را بسازید**
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
4. **کانتینر را اجرا کنید:**
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
- توجه: MPS در docker در دسترس نیست بنابراین باید از CPU استفاده شود
  
### مشکلات رایج Docker
- پردازنده گرافیکی NVIDIA من شناسایی نمی‌شود؟؟ -> [صفحه ویکی مشکلات GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## مدل‌های TTS تنظیم‌دقیق‌شده (fine-tuned)
#### مدل XTTSv2 خود را تنظیم دقیق کنید

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### حذف نویز از داده‌های آموزشی

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### مجموعه مدل‌های TTS تنظیم‌دقیق‌شده

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

برای مدل سفارشی XTTSv2، یک کلیپ صوتی مرجع از صدا اجباری است:

## سفارشی‌سازی شخصی شما برای Ebook2Audiobook
شما آزادید libs/conf.py را برای افزودن یا حذف تنظیمات دلخواه خود تغییر دهید. اگر قصد این کار را دارید، کافی است یک
نسخه از conf.py اصلی تهیه کنید تا در هر به‌روزرسانی ebook2audiobook بتوانید از conf.py تغییریافته خود نسخه پشتیبان بگیرید و
نسخه اصلی را بازگردانید. باید همین روند را برای models.py نیز برنامه‌ریزی کنید. اگر می‌خواهید مدل سفارشی خود را
به یک مدل رسمی تنظیم‌دقیق‌شده ebook2audiobook تبدیل کنید، لطفاً با ما تماس بگیرید تا آن را به فهرست پیش‌تنظیم‌ها اضافه کنیم.

## بازگشت به نسخه‌های قدیمی‌تر
نسخه‌ها را می‌توان -> [اینجا](https://github.com/DrewThomasson/ebook2audiobook/releases) یافت
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## مشکلات رایج:
- پردازنده گرافیکی NVIDIA/ROCm/XPU/MPS من شناسایی نمی‌شود؟؟ -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU کند است (روی CPU سرور SMP بهتر است) در حالی که GPU می‌تواند تبدیل تقریباً بلادرنگ داشته باشد.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (با این حال شبیه‌سازی صدای zero-shot ندارد، و صداها با کیفیت Siri هستند، اما روی cpu بسیار سریع‌تر است).
- «مشکلاتی با وابستگی‌ها دارم» - کافی است از docker استفاده کنید، کاملاً مستقل است و حالت بدون رابط دارد،
   برای اطلاعات بیشتر پارامتر `--help` را به انتهای دستور docker run اضافه کنید.
- «مشکل قطع شدن صدا دارم!» - لطفاً یک ISSUE در این مورد ایجاد کنید،
   ما به همه زبان‌ها صحبت نمی‌کنیم و برای تنظیم دقیق منطق تقسیم جمله به توصیه کاربران نیاز داریم.😊

## ***** نقشه راه *****
- تمام ویژگی‌ها برای مشارکت‌های عمومی باز هستند ⭐
- هرگونه کمک از افرادی که به یکی از زبان‌های پشتیبانی‌شده صحبت می‌کنند تا به ما در بهبود مدل‌ها کمک کنند ⭐
- [x] پیش‌نمایش بلوک‌ها/فصل‌ها پیش از شروع تبدیل
- [ ] ویرایش به‌ازای هر جمله تبدیل‌شده برای تغییر دقیق متن
- [x] یکپارچه‌سازی برچسب‌های SML برای صدا، مکث، وقفه و تغییرات بیشتر 
- [x] اطلاعات پارامتر -h -help به زبان‌های مختلف
- [x] اسکن OCR برای PDF / JPG / BMP / PNG / TIFF
- [x] پوشه Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] اطمینان از اینکه تقسیم متن چینی کلمات را تقسیم نکند و بهبود زمان‌بندی مکث‌ها [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] دفترچه Kaggle
- [x] دفترچه Google Colab
- [ ] [ساخت یک اپلیکیشن iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [ساخت یک اپلیکیشن android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] یکپارچه‌سازی Audiobookshelf

#### گزینه‌های اضافی
- [x] گزینه ترجمه کتاب الکترونیکی
- [x] انتخاب‌های قالب خروجی
- [x] پوشه دسته‌ای کتاب الکترونیکی
- [x] تبدیل چندپردازشی
- [x] تبدیل دسته‌ای پوشه کتاب الکترونیکی
- [x] تشخیص دستگاه GPU
- [x] حذف نویز از هر صدای مرجع برای بارگذاری شبیه‌سازی صدا،
- [x] بارگذاری مدل سفارشی (فعلاً فقط XTTSv2. موارد بیشتر بنا به درخواست)
- [ ] افزودن مدل زبانی پرتغالی اروپایی حداقل برای xttsv2، fairseq، vits، piper (از کمک استقبال می‌شود)
- [ ] افزودن مدل زبانی سندی حداقل برای xttsv2، fairseq، vits، piper (از کمک استقبال می‌شود)

#### موتورهای TTS
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

#### ترجمه Readme
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

#### 🐍 سازگاری سیستم‌عامل
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## افراط اضافی برای آموزش مدل‌ها و موارد مشابه (تمام مدل‌های پشتیبانی‌شده Coqui-tts و piper-tts در یک دستور ساده) 
- برای اطلاعات در این مورد @DrewThomasson، او در حال حاضر روی توسعه این مورد کار می‌کند، [مخزن در حال انجام در اینجا](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] ساخت یک رابط گرافیکی آموزشی آسان برای استفاده برای تمام مدل‌های coqui-tts در دستورالعمل‌های آموزشی قالب ljspeech [اینجا از coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## اطلاعات نرمال‌سازی کد Python برای مشارکت‌کنندگان
- بدون خط خالی بین کد، به‌جز بین توابع و کلاس‌ها.
- از نقل‌قول تکی برای تمام کلیدها به‌جز dict() و json استفاده می‌شود. dict['key'] همیشه با نقل‌قول تکی فراخوانی می‌شود
- تورفتگی ۴ فاصله، بدون هیچ تب
- تایپ‌گذاری سختگیرانه برای تمام توابع و اعلان آرگومان‌ها و مقادیر بازگشتی آن‌ها
- بدون فاصله بین آرگومان و تایپ‌گذاری آن، بدون فاصله بین تابع، «->» و مقدار بازگشتی

نمونه:

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

## به اهدای سخت‌افزار برای آزمایش‌های بتا نیازمندیم
ما هر نوع سخت‌افزاری را برای آزمایش توسعه خود می‌پذیریم مانند:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson اگر می‌خواهید به هر شکلی کمک کنید! 😃
<!--
## آیا برای تقویت خدمات ما به اجاره یک GPU نیاز دارید؟
- یک نظرسنجی در اینجا باز است https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## تشکر ویژه
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 برای روش بهتر ذخیره فصل‌ها](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
