# 📚 eBook2AudiObook

محول وحدة المعالجة المركزية/GPU من الكتب الإلكترونية إلى الكتب الصوتية مع الفصول والبيانات الوصفية<br/>باستخدام العيار ، FFMPEG ، XTTSV2 ، FAIRSEQ والمزيد. يدعم الاستنساخ الصوتي و +1110 لغات!

> [!مهم]**هذه الأداة مخصصة للاستخدام مع الكتب الإلكترونية المكتسبة قانونًا فقط.**<br>المؤلفون ليسوا مسؤولين عن أي سوء استخدام لهذا البرنامج أو أي عواقب قانونية ناتجة.<br>استخدم هذه الأداة بمسؤولية ووفقًا لجميع القوانين المعمول بها.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

بفضل دعم مطوري ebook2audiobook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### واجهة واجهة المستخدم الرسومية

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   نشتري[العربية (Arabic)](./readme/README_AR.md)
-   تشو[الصينية](./readme/README_CN.md)
-   أ[إنجليزي](README.md)
-   سو[السويدية (السويدية)](./readme/README_SWE.md)
-   Fas[الفارسية (الفارسية)](./readme/README_FA.md)
-   هي[إيطالي (إيطالي)](./readme/README.it.md)

## جدول المحتويات

-   [eBook2AudiObook](#-ebook2audiobook)
-   [سمات](#features)
-   [واجهة Docker واجهة المستخدم الرسومية](#docker-gui-interface)
-   [عانق الفضاء العرض التوضيحي](#huggingface-space-demo)
-   [جوجل كولاب مجاني](#free-google-colab)
-   [عروض صوتية مسبقة الصنع](#demos)
-   [اللغات المدعومة](#supported-languages)
-   [متطلبات](#hardware-requirements)
-   [تعليمات التثبيت](#installation-instructions)
-   [الاستخدام](#launching-gradio-web-interface)
    -   [إطلاق واجهة ويب Gradio](#launching-gradio-web-interface)
    -   [الاستخدام الأساسي مقطوعة الرأس](#basic--usage)
    -   [استخدام نموذج XTTS مخصص مخصص](#example-of-custom-model-zip-upload)
    -   [استئجار وحدة معالجة الرسومات](#renting-a-gpu)
    -   [مساعدة الإخراج أمر](#help-command-output)
-   [نماذج TTS ذات ضبطها](#fine-tuned-tts-models)
    -   [لجمع نماذج TTS التي تم ضبطها](#fine-tuned-tts-collection)
-   [باستخدام Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [بناء Docker](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [دليل Docker Headless](#docker-headless-guide)
    -   [مواقع ملفات حاوية Docker](#docker-container-file-locations)
    -   [قضايا العرف المشتركة](#common-docker-issues)
-   [تدعم تنسيقات الكتاب الاليكتروني](#supported-ebook-formats)
-   [الإخراج](#output)
-   [القضايا المشتركة](#common-issues)
-   [شكر خاص](#special-thanks)
-   [انضم إلى الخادم الخاص بنا!](#join-our--server)
-   [إرث](#legacy-v10)
-   [جدول المحتويات](#table-of-contents)

## سمات

-   📖 يحول الكتب الإلكترونية إلى تنسيق النص مع العيار.
-   📚 ينقسم الكتاب الإلكتروني إلى فصول للصوت المنظم.
-   🎙 من نص إلى كلام عالي الجودة مع[Coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)و[فيرسيك](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(وأكثر).
-   🗣 استنساخ الصوت الاختياري مع ملف الصوت الخاص بك.
-   🌍 يدعم +1110 لغات (اللغة الإنجليزية بشكل افتراضي).[قائمة اللغات المدعومة](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥 مصمم لتشغيل على ذاكرة الوصول العشوائي 4 جيجابايت.

## [عانق الفضاء العرض التوضيحي](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   يتم تشغيل مساحة العناق على المستوى المجاني للوحدة المعالجة المركزية ، لذا توقع بطيئًا جدًا أو مهلة LOL ، فقط لا تعطيها ملفات عملاقة
-   من الأفضل تكرار المساحة أو الركض محليًا.

## جوجل كولاب مجاني

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## اللغات المدعومة

-   **اللغة العربية (ARA)**
-   **الصينية (ZH)**
-   **التشيكية (CES)**
-   **الكرواتية (HRV)**
-   **الهولندي (NLD)**
-   **اللغة الإنجليزية (المهندس)**
-   **الفرنسية (من)**
-   **الألمانية (ديو)**
-   **لا (هين)**
-   **الهنغاري (صباحا)**
-   **إيطالي (إيتا)**
-   **اليابانية (JPN)**
-   **الكورية (COR)**
-   **البولندية (بول)**
-   **البرتغالي (بور)**
-   **الروسي (روس)**
-   **الإسبانية (سبا)**
-   **التركية (جولة)**
-   **الفيتناميين (VIE)**
-   [**+1100 لغات عبر فيرسيك**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## متطلبات الأجهزة

-   4 جيجابايت ذاكرة الوصول العشوائي الحد الأدنى ، موصى بها 8 جيجابايت
-   تم تمكين المحاكاة الافتراضية في حالة تشغيل Windows (Docker فقط)
-   وحدة المعالجة المركزية ، GPU (الموصى بها) ، نواب (لم يتم تحسينها بعد ويمكن أن تكون أبطأ من وحدة المعالجة المركزية) متوافقة

> [!مهم]**قبل نشر علامة تثبيت أو علة بحث بعناية في علامة التبويب المشكلات المفتوحة والمغلقة<br>للتأكد من أن مشكلتك غير موجودة بالفعل.**

> [!ملحوظة]**عدم وجود أي بنية المعايير مثل ما هو الفصل ، الفقرة ، المقدمة وما إلى ذلك.<br>يجب عليك أولاً إزالة أي نص لا تريد تحويله في الصوت يدويًا.**

### تعليمات التثبيت

1.  **استنساخ repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### إطلاق واجهة ويب Gradio

1.  **تشغيل eBook2AudiObook**:
    -   **Linux/Macos**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **النوافذ**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **افتح تطبيق الويب**: انقر فوق عنوان URL المتوفر في المحطة للوصول إلى تطبيق الويب وتحويل الكتب الإلكترونية.
3.  **للرابط العام**:`python app.py --share`(كل OS)`./ebook2audiobook.sh --share`(Linux/MacOS)`ebook2audiobook.cmd --share`(Windows)

> [!مهم]**إذا تم إيقاف البرنامج النصي وتشغيله مرة أخرى ، فأنت بحاجة إلى تحديث واجهة Gradio GUI الخاصة بك<br>للسماح لصفحة الويب بإعادة الاتصال بمقبس الاتصال الجديد.**

### الاستخدام الأساسي

-   **Linux/Macos**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **النوافذ**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--ebook]**: مسار إلى ملف الكتاب الإلكتروني الخاص بك.
-   **[--صوت]**: مسار ملف الاستنساخ الصوتي (اختياري).
-   **[--لغة]**: رمز اللغة في ISO-639-3 (على سبيل المثال: ITA للإيطالية ، المهندس للغة الإنجليزية ، DEU للألمانية ...).<br>اللغة الافتراضية هي المهندس و -اللغة اختيارية للغة الافتراضية المحددة في ./lib/lang.py.<br>كما يتم دعم رموز الرسائل ISO-639-1 2.

### مثال على تحميل zip model model

(يجب أن يكون ملف .zip يحتوي على ملفات النماذج الإلزامية. مثال لـ XTTS: config.json ، model.pth ، vocab.json و ref.wav)

-   **Linux/Macos**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **النوافذ**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;Cument_model_path>**: الطريق إلى`model_name.zip`ملف،
        التي يجب أن تحتوي على (وفقًا لمحرك TTS) جميع الملفات الإلزامية<br>(انظر ./lib/models.py).

### للحصول على دليل مفصل مع قائمة جميع المعلمات التي يجب استخدامها

-   **Linux/Macos**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **النوافذ**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **أو لجميع نظام التشغيل**
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

ملاحظة: في وضع Gradio/GUI ، لإلغاء تحويل التشغيل ، فقط انقر فوق[x]من مكون تحميل الكتاب الإلكتروني.

### باستخدام Docker

يمكنك أيضًا استخدام Docker لتشغيل الكتاب الاليكتروني إلى محول AudiObook. 
تضمن هذه الطريقة الاتساق عبر بيئات مختلفة وتبسيط الإعداد.

#### تشغيل حاوية Docker

لتشغيل حاوية Docker وبدء واجهة Gradio ، استخدم الأمر التالي:

\-رون مع وحدة المعالجة المركزية فقط

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-رون مع تسريع وحدة معالجة الرسومات (NVIDIA متوافق فقط)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### بناء حاوية Docker

-   يمكنك بناء صورة Docker مع الأمر:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

سيبدأ هذا الأمر واجهة Gradio على المنفذ 7860. (LocalHost: 7860)

-   لمزيد من الخيارات أضف المعلمة`--help`

## مواقع ملفات حاوية Docker

جميع eBook2AudiObooks سيكون لها قاعدة dir من`/home/user/app/`على سبيل المثال:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## دليل Docker Headless

أولا لسحب Docker من الأحدث مع

```bash
docker pull athomasson2/ebook2audiobook
```

-   قبل تشغيل هذا ، تحتاج إلى إنشاء DIR اسمه "محلى المدخلات" في dir الحالي الخاص بك
    التي سيتم ربطها ، هذا هو المكان الذي يمكنك وضع ملفات الإدخال الخاصة بك لالتقاط صورة Docker

```bash
mkdir input-folder && mkdir Audiobooks
```

-   في الأمر أدناه مبادلة**your_input_file.txt**باسم ملف الإدخال الخاص بك

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   وهذا يجب أن يكون!
-   سيتم العثور على الكتب الصوتية المخرج في مجلد المسمار المسموع الذي سيتم تحديد موقعه أيضًا
    في Dir Local ، قمت بتشغيل أمر Docker هذا في

## للحصول على أمر المساعدة للمعلمات الأخرى ، هل يمكنك تشغيل هذا البرنامج

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

وسيؤدي ذلك إلى إخراج هذا[مساعدة الإخراج أمر](#help-command-output)

### Docker Compose

يستخدم هذا المشروع Docker لتشغيل محليًا. يمكنك تمكين أو تعطيل دعم GPU 
عن طريق الإعداد سواء`*gpu-enabled`أو`*gpu-disabled`في`docker-compose.yml`

#### خطوات لتشغيل

1.  **استنساخ المستودع**(إذا لم تقم بالفعل):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **تعيين دعم GPU (معطل بشكل افتراضي)**لتمكين دعم GPU ، تعديل`docker-compose.yml`والتغيير`*gpu-disabled`ل`*gpu-enabled`
3.  **ابدأ الخدمة:**
    ```bash
    docker-compose up -d
    ```
4.  **الوصول إلى الخدمة:**ستكون الخدمة متاحة على http&#x3A; // localhost: 7860.

### واجهة Docker واجهة المستخدم الرسومية

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## استئجار وحدة معالجة الرسومات

ليس لديك الأجهزة لتشغيلها أو تريد استئجار وحدة معالجة الرسومات؟

#### يمكنك تكرار مساحة Hugginface واستئجار وحدة معالجة الرسومات مقابل حوالي 0.40 دولار في الساعة

[عانق الفضاء العرض التوضيحي](#huggingface-space-demo)

#### أو يمكنك محاولة استخدام Google Colab مجانًا!

(كن على علم بأنه سيصبح وقتًا طويلاً بعد قليل من عدم العبث مع Google Colab)[جوجل كولاب مجاني](#free-google-colab)

## قضايا العرف المشتركة

-   Docker تتعثر في تنزيل النماذج المضبوطة.
    (هذا لا يحدث لكل جهاز كمبيوتر ولكن يبدو أن البعض يواجه هذه المشكلة)
    يبدو أن تعطيل شريط التقدم لإصلاح المشكلة ،
    كما نوقش[هنا في #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)مثال على إضافة هذا الإصلاح في`docker run`يأمر

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## نماذج TTS ذات ضبطها

يمكنك ضبط طراز XTTS الخاص بك بسهولة مع هذا الريبو[XTTS-Finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

إذا كنت ترغب في استئجار وحدة معالجة الرسومات بسهولة ، فيمكنك أيضًا تكرار هذه المعانقة[XTTS-Finetune-Webui-Space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

مساحة يمكنك استخدامها لإلغاء تسجيل بيانات التدريب بسهولة أيضًا[DENOISE-HAGGINGAGEFACE-Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### مجموعة TTS ذات ضبطها

للعثور على مجموعتنا من نماذج TTS التي تم ضبطها بالفعل ،
يزور[رابط الوجه المعانقة هذا](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)للحصول على طراز XTTS مخصص ، يكون مقطع الصوت المرجع للمرجع الصوتي إلزاميًا:

## العروض التوضيحية

**صوت يوم ممطر**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**ديفيد أتينبورو صوت**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## تدعم تنسيقات الكتاب الاليكتروني

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **أفضل النتائج**:`.epub`أو`.mobi`لاكتشاف الفصل التلقائي

## الإخراج

-   يخلق أ`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(تعيين في ./lib/conf.py) ملف مع البيانات الوصفية والفصول.
-   **مثال**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## القضايا الشائعة:

-   وحدة المعالجة المركزية بطيئة (أفضل على CPU Server SMP) في حين أن GPU NVIDIA يمكن أن يكون لها تحويل في الوقت الفعلي تقريبًا.[مناقشة حول هذا](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)من أجل جيل متعدد اللغات أسرع ، أود أن أقترح بلدي الآخر[المشروع الذي يستخدم piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)بدلاً من
    (لا يحتوي على صفر صوت استنساخ ، وهو أصوات Siri ذات جودة Siri ، ولكنها أسرع بكثير على وحدة المعالجة المركزية).
-   "أواجه مشكلات تبعية" - ما عليك سوى استخدام Docker ، وذاته بالكامل وله وضع مقطوع الرأس ،
     يضيف`--help`المعلمة في نهاية الأمر Docker Run لمزيد من المعلومات.
-   "أنا أتلقى مشكلة صوتية مقطوعة!" - يرجى تقديم مسألة من هذا ،
     نحن لا نتحدث كل لغة ونحتاج إلى تقديم المشورة من المستخدمين لضبط منطق تقسيم الجملة.

## ما أحتاجه للمساعدة! 🙌

## [يمكن العثور على قائمة كاملة بالأشياء هنا](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   أي مساعدة من أشخاص يتحدثون أي من اللغات المدعومة للمساعدة في أساليب تقسيم الجملة المناسبة
-   من المحتمل أن تقوم بإنشاء أدلة ReadMe للغات المتعددة (لأن اللغة الوحيدة التي أعرفها هي اللغة الإنجليزية 😔)

## شكر خاص

-   **طبخ TTS**:[coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **عيار**:[موقع عيار](https://calibre-ebook.com)
-   **FFMPEG**:[موقع FFMPEG](https://ffmpeg.org)
-   [@ShakenBake15 لتحسين طريقة حفظ الفصل](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

يمكنك عرض الرمز[هنا](legacy/v1.0).

## انضم إلى الخادم الخاص بنا!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
