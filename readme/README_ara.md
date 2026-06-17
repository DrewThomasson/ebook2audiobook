# 📚 ebook2audiobook (E2A)
محوّل CPU/GPU من الكتاب الإلكتروني إلى كتاب صوتي مع الفصول والبيانات الوصفية<br/>
باستخدام محركات TTS المتقدمة وغير ذلك الكثير.<br/>
يدعم استنساخ الصوت و1158 لغة!
> [!IMPORTANT]
**هذه الأداة مخصصة للاستخدام فقط مع الكتب الإلكترونية الخالية من DRM والتي تم الحصول عليها بشكل قانوني.** <br>
المؤلفون غير مسؤولين عن أي سوء استخدام لهذا البرنامج أو أي عواقب قانونية تنتج عنه. <br>
استخدم هذه الأداة بمسؤولية وبما يتوافق مع جميع القوانين المعمول بها.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### شكرًا لدعمك لمطوّري ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### التشغيل محليًا

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### التشغيل عن بُعد
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### الواجهة الرسومية (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>انقر لرؤية صور واجهة الويب الرسومية</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## عروض توضيحية

**عرض توضيحي للصوت الافتراضي الجديد**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>المزيد من العروض التوضيحية</summary>

**صوت ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**صوت يوم ممطر**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**صوت سكارليت**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**صوت ديفيد أتينبورو** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**مثال**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## جدول المحتويات
- [ebook2audiobook](#-ebook2audiobook)
- [الميزات](#features)
- [الواجهة الرسومية](#gui-interface)
- [عروض توضيحية](#demos)
- [اللغات المدعومة](#supported-languages)
- [الحد الأدنى من المتطلبات](#hardware-requirements)
- [الاستخدام](#instructions)
  - [التشغيل محليًا](#instructions)
    - [تشغيل واجهة الويب Gradio](#instructions)
    - [الاستخدام الأساسي بدون واجهة](#basic-usage)
    - [استخدام نموذج XTTS مخصص بدون واجهة](#example-of-custom-model-zip-upload)
    - [مخرجات أمر المساعدة](#help-command-output)
  - [التشغيل عن بُعد](#run-remotely)
  - [Docker](#docker)
    - [خطوات التشغيل](#docker)
    - [مشكلات Docker الشائعة](#common-docker-issues)
  
- [نماذج TTS المضبوطة بدقة](#fine-tuned-tts-models)
  - [مجموعة نماذج TTS المضبوطة بدقة](#fine-tuned-tts-collection)
  - [تدريب XTTSv2](#fine-tune-your-own-xttsv2-model)
- [صيغ الكتب الإلكترونية المدعومة](#supported-ebook-formats)
- [صيغ الإخراج](#output-and-process-formats)
- [العودة إلى إصدار أقدم](#reverting-to-older-versions)
- [المشكلات الشائعة](#common-issues)
- [شكر خاص](#special-thanks)
- [جدول المحتويات](#table-of-contents)


## الميزات
- 🔧 **محركات TTS المدعومة**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **تحويل صيغ ملفات متعددة**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **منطقة نص** لتحويل نص قصير مباشرةً إلى صوت
- 🔍 **مسح OCR** للملفات التي تحتوي على صفحات نصية كصور
- 🔊 **تحويل نص إلى كلام عالي الجودة**، من شبه الوقت الفعلي إلى صوت شبه حقيقي
- 🗣️ **استنساخ صوت اختياري** باستخدام ملف صوتك الخاص
- 🌐 **يدعم 1158 لغة** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **صديق للموارد المنخفضة** — يعمل على **2 GB RAM / 1 GB VRAM (الحد الأدنى)**
- 🎵 **صيغ إخراج الكتاب الصوتي**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **وسوم SML مدعومة** — تحكم دقيق في الفواصل والتوقفات وتبديل الصوت والمزيد ([see below](#sml-tags-available))
- 🧩 **نموذج مخصص اختياري** باستخدام نموذجك المدرّب الخاص (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **نماذج مُعدّة مسبقًا ومضبوطة بدقة** دُرّبت بواسطة فريق E2A<br/>
     <i>(تواصل معنا إذا كنت بحاجة إلى نماذج إضافية مضبوطة بدقة، أو إذا كنت ترغب في مشاركة نماذجك في قائمة الإعدادات المسبقة الرسمية)</i>


##  متطلبات العتاد
- 2 جيجابايت RAM كحد أدنى، 8 جيجابايت موصى به.
- 1 جيجابايت VRAM كحد أدنى، 4 جيجابايت موصى به.
- المحاكاة الافتراضية مُفعّلة عند التشغيل على windows (Docker فقط).
- CPU، XPU (intel، AMD، ARM)*.
- CUDA، ROCm، JETSON
- MPS (معالج Apple Silicon)

*<i> محركات TTS الحديثة بطيئة جدًا على CPU، لذا استخدم TTS أقل جودة مثل YourTTS وTacotron2 وما إلى ذلك.</i>

## اللغات المدعومة
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 لغة ولهجة هنا**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## صيغ الكتب الإلكترونية المدعومة
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **أفضل النتائج**: `.epub` أو `.mobi` للكشف التلقائي عن الفصول

## صيغ الإخراج والمعالجة
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- يمكن تغيير صيغة المعالجة في lib/conf.py

## وسوم SML المتاحة
- `[break]` — صمت (نطاق عشوائي **0.3–0.6 sec.**)
- `[pause]` — صمت (نطاق عشوائي **1.0–1.6 sec.**)
- `[pause:N]` — توقف ثابت (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — تبديل الصوت من الصوت الافتراضي أو المحدد من GUI/CLI

**اطّلع على مستودعنا الآخر المخصص لإضافة SML تلقائيًا في كتابك الإلكتروني -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**قبل نشر مشكلة تثبيت أو خطأ، ابحث بعناية في علامة تبويب المشكلات المفتوحة والمغلقة<br>
للتأكد من أن مشكلتك غير موجودة بالفعل.**

>[!NOTE]
**تفتقر صيغة EPUB إلى أي بنية معيارية لما هو الفصل أو الفقرة أو المقدمة وما إلى ذلك.<br>
لذا يجب عليك أولًا أن تزيل يدويًا أي نص لا ترغب في تحويله إلى صوت.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ثبّت / شغّل ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **مشغّل Mac**  
     انقر نقرًا مزدوجًا على `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>ملاحظة لمستخدمي Windows: يتم تثبيت scoop لتثبيت البرامج المفقودة دون امتيازات المسؤول.</i>
   
1. **افتح تطبيق الويب**: انقر على الرابط المتوفر في الطرفية للوصول إلى تطبيق الويب وتحويل الكتب الإلكترونية. `http://localhost:7860/`
2. **للحصول على رابط عام**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**إذا تم إيقاف السكربت وتشغيله مرة أخرى، فستحتاج إلى تحديث واجهة Gradio الرسومية<br>
للسماح لصفحة الويب بإعادة الاتصال بمقبس الاتصال الجديد.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: مسار ملف كتابك الإلكتروني
  - **[--voice]**: مسار ملف استنساخ الصوت (اختياري)
  - **[--language]**: رمز اللغة بصيغة ISO-639-3 (أي: ita للإيطالية، eng للإنجليزية، deu للألمانية...).<br>
    اللغة الافتراضية هي eng و--language اختياري للغة الافتراضية المحددة في ./lib/lang.py.<br>
    كما يتم دعم رموز ISO-639-1 المكونة من حرفين.


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
     
- **<custom_model_path>**: مسار ملف `model_name.zip`،
      الذي يجب أن يحتوي (وفقًا لمحرك tts) على جميع الملفات الإلزامية<br>
      (انظر ./lib/models.py).

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

ملاحظة: في وضع gradio/gui، لإلغاء تحويل قيد التشغيل، ما عليك سوى النقر على [X] في مكوّن رفع الكتاب الإلكتروني.
نصيحة: إذا كانت هناك حاجة إلى توقف أطول قليلًا، أضف '[pause:3]' لمدة 3 ثوانٍ وما إلى ذلك.

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
  
### مشكلات Docker الشائعة
- لا يتم اكتشاف بطاقة NVIDIA الرسومية لدي؟؟ -> [صفحة Wiki لمشكلات GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## نماذج TTS المضبوطة بدقة (fine-tuned)
#### اضبط نموذج XTTSv2 الخاص بك بدقة

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### إزالة الضوضاء من بيانات التدريب

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### مجموعة نماذج TTS المضبوطة بدقة

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

بالنسبة إلى نموذج XTTSv2 المخصص، يكون مقطع صوتي مرجعي للصوت إلزاميًا:

## تخصيصك الخاص لـ Ebook2Audiobook
أنت حر في تعديل libs/conf.py لإضافة أو إزالة الإعدادات التي تريدها. إذا كنت تخطط للقيام بذلك، فما عليك سوى إنشاء
نسخة من conf.py الأصلي بحيث يمكنك في كل تحديث لـ ebook2audiobook عمل نسخة احتياطية من conf.py المعدّل وإعادة
وضع الأصلي. يجب عليك التخطيط للعملية نفسها بالنسبة لـ models.py. إذا كنت ترغب في جعل نموذجك المخصص
نموذج ebook2audiobook رسميًا مضبوطًا بدقة، فيرجى الاتصال بنا وسنضيفه إلى قائمة الإعدادات المسبقة.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## المشكلات الشائعة:
- لا يتم اكتشاف بطاقة NVIDIA/ROCm/XPU/MPS الرسومية لدي؟؟ -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  المعالج بطيء (أفضل على معالج خادم SMP) بينما يمكن لبطاقة GPU إجراء تحويل شبه فوري.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (لكنه لا يحتوي على استنساخ صوت zero-shot، وهي أصوات بجودة Siri، لكنه أسرع بكثير على cpu).
- "أواجه مشكلات في التبعيات" - ما عليك سوى استخدام docker، فهو مكتفٍ ذاتيًا تمامًا وله وضع بدون واجهة،
   أضف المعامل `--help` في نهاية أمر docker run للمزيد من المعلومات.
- "أواجه مشكلة في انقطاع الصوت!" - يرجى إنشاء ISSUE حول هذا،
   نحن لا نتحدث كل لغة ونحتاج إلى نصيحة من المستخدمين لضبط منطق تقسيم الجمل بدقة.😊

## ***** خارطة الطريق *****
- جميع الميزات مفتوحة للمساهمات العامة ⭐
- أي مساعدة من أشخاص يتحدثون أيًا من اللغات المدعومة لمساعدتنا في تحسين النماذج ⭐
- [x] معاينة الكتل/الفصول قبل بدء التحويل
- [ ] التحرير لكل جملة محوّلة لتغيير نصي دقيق
- [x] دمج وسوم SML للصوت والتوقف والفاصل والمزيد من التغييرات 
- [x] معلومات معاملات -h -help بلغات مختلفة
- [x] مسح OCR لملفات PDF / JPG / BMP / PNG / TIFF
- [x] مجلد Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] جعل تقسيم النص الصيني لا يقسم الكلمات وتحسين توقيت الفواصل [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] دفتر Kaggle
- [x] دفتر Google Colab
- [ ] [إنشاء تطبيق iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [إنشاء تطبيق android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] دمج Audiobookshelf

#### خيارات إضافية
- [x] خيار ترجمة الكتاب الإلكتروني
- [x] خيارات صيغة الإخراج
- [x] مجلد كتب إلكترونية دفعي
- [x] تحويل متعدد المعالجة
- [x] تحويل مجلد كتب إلكترونية دفعي
- [x] اكتشاف جهاز GPU
- [x] إزالة الضوضاء من أي صوت مرجعي لرفع استنساخ الصوت،
- [x] رفع نموذج مخصص (XTTSv2 فقط حاليًا. المزيد عند الطلب)
- [ ] إضافة نموذج لغة البرتغالية الأوروبية على الأقل لـ xttsv2 وfairseq وvits وpiper (المساعدة مرحب بها)
- [ ] إضافة نموذج لغة السندية على الأقل لـ xttsv2 وfairseq وvits وpiper (المساعدة مرحب بها)

#### محركات TTS
- [x] XTTSv2
- [x] ﺡﺎﺒﻧ
- [x] فيرسيك
- [x] فيتس
- [x] تاكوترون 2
- [x] YourTTS
- [x] لون السلحفاة
- [x] GlowTTS
- [x] الفلفل الأسود
- [ ] GPT - SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] كلام السمكة (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5 - TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Spark - TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index - tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro - TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] زونوس (https://github.com/Zyphra/Zonos)
- [ ] Style - TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus - TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3 - TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### ترجمة Readme
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

#### 🐍 توافق نظام التشغيل
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## مبالغة إضافية لتدريب النماذج وما شابه (جميع نماذج Coqui-tts المدعومة وpiper-tts في أمر واحد سهل) 
- للمعلومات حول هذا @DrewThomasson، يعمل حاليًا على تطويره، [المستودع قيد العمل هنا](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] إنشاء واجهة تدريب سهلة الاستخدام لجميع نماذج coqui-tts في وصفات التدريب بصيغة ljspeech [هنا من coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## معلومات تسوية كود Python للمساهمين
- لا سطر فارغ بين الكود، باستثناء بين الدوال والفئات.
- تُستخدم علامات الاقتباس المفردة لجميع المفاتيح باستثناء dict() وjson. يتم استدعاء dict['key'] دائمًا بعلامات اقتباس مفردة
- مسافة بادئة من 4 مسافات، دون أي علامات جدولة على الإطلاق
- كتابة صارمة للأنواع لجميع الدوال وإعلان وسائطها وقيم إرجاعها
- لا مسافة بين الوسيط وكتابة نوعه، لا مسافة بين الدالة و"->" وقيمة الإرجاع

مثال:

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

## مطلوب تبرع بالعتاد لاختبارات بيتا
نقبل أي نوع من العتاد لاختبار تطويرنا مثل:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson إذا كنت ترغب في المساعدة بأي شكل من الأشكال! 😃
<!--
## هل تحتاج إلى استئجار GPU لتعزيز خدمتنا؟
- استطلاع رأي مفتوح هنا https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## شكر خاص
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 لطريقة أفضل لحفظ الفصول](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
