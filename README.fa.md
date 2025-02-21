# 📚 ebook2audiobook

مبدل CPU/GPU از کتابهای الکترونیکی به کتابهای صوتی با فصل ها و ابرداده ها<br/>با استفاده از کالیبر ، ffmpeg ، xttsv2 ، fairseq و موارد دیگر. از کلونینگ صوتی و زبانهای +1110 پشتیبانی می کند!

> [مهم!]**This tool is intended for use with non-DRM, legally acquired eBooks only.**<br>نویسندگان مسئول هرگونه سوء استفاده از این نرم افزار یا پیامدهای قانونی حاصل نیستند.<br>از این ابزار با مسئولیت پذیری و مطابق با کلیه قوانین قابل اجرا استفاده کنید.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

با تشکر از پشتیبانی Ebook2AudioBook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### رابط GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   ما خریداری می کنیم[عربی (عربی)](./readme/README_AR.md)
-   یار[چینی](./readme/README_CN.md)
-   a \`a[انگلیسی](README.md)
-   سخاب[سوئدی (سوئدی)](./readme/README_SWE.md)
-   FAS[فارسی (Persian)](./readme/README_FA.md)
-   او[ایتالیایی (ایتالیایی)](./readme/README.it.md)

## فهرست مطالب

-   [کتاب الکترونیکی 2AudioBook](#-ebook2audiobook)
-   [ویژگی](#features)
-   [رابط Docker GUI](#docker-gui-interface)
-   [نسخه ی نمایشی فضای بغل کردن](#huggingface-space-demo)
-   [Google Colab رایگان](#free-google-colab)
-   [نسخه های نمایشی صوتی از قبل ساخته شده](#demos)
-   [زبانهای پشتیبانی شده](#supported-languages)
-   [الزام](#hardware-requirements)
-   [دستورالعمل نصب](#installation-instructions)
-   [استفاده](#launching-gradio-web-interface)
    -   [راه اندازی رابط وب Gradio](#launching-gradio-web-interface)
    -   [استفاده اساسی بدون سر](#basic--usage)
    -   [استفاده از مدل XTTS سفارشی بدون سر](#example-of-custom-model-zip-upload)
    -   [اجاره یک پردازنده گرافیکی](#renting-a-gpu)
    -   [راهنما خروجی فرمان](#help-command-output)
-   [مدل های TTS خوب تنظیم شده](#fine-tuned-tts-models)
    -   [برای جمع آوری مدل های TTS تنظیم شده](#fine-tuned-tts-collection)
-   [با استفاده از داکر](#using-docker)
    -   [داکر دویدن](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [داکر آهنگسازی](#docker-compose)
    -   [راهنمای بدون سر داکر](#docker-headless-guide)
    -   [مکان های فایل کانتینر Docker](#docker-container-file-locations)
    -   [مسائل مشترک داکر](#common-docker-issues)
-   [فرمت های کتاب الکترونیکی پشتیبانی شده](#supported-ebook-formats)
-   [خروجی](#output)
-   [مسائل مشترک](#common-issues)
-   [با تشکر خاص](#special-thanks)
-   [به سرور ما بپیوندید!](#join-our--server)
-   [میراث](#legacy-v10)
-   [فهرست مطالب](#table-of-contents)

## ویژگی

-   book کتابهای الکترونیکی را به قالب متن با کالیبر تبدیل می کند.
-   📚 کتاب الکترونیکی را به فصل های صوتی سازمان یافته تقسیم می کند.
-   🎙 با کیفیت بالا متن به گفتار با[coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)وت[تبهکار](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(و بیشتر)
-   cloning کلونینگ صوتی اختیاری با پرونده صوتی خود.
-   🌍 از زبانهای +1110 پشتیبانی می کند (انگلیسی به طور پیش فرض).[لیست زبانهای پشتیبانی شده](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥 طراحی شده برای اجرای روی رم 4 گیگابایتی.

## [نسخه ی نمایشی فضای بغل کردن](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   فضای بغل کردن در ردیف پردازنده رایگان در حال اجرا است ، بنابراین انتظار بسیار آهسته یا زمان بندی را داشته باشید ، فقط به آن پرونده های غول پیکر ندهید
-   بهترین کار برای کپی کردن فضا یا اجرای محلی.

## Google Colab رایگان

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## زبانهای پشتیبانی شده

-   **عربی (ARA)**
-   **چینی (ZH)**
-   **چک (CES)**
-   **کرواسی (HRV)**
-   **هلندی (NLD)**
-   **انگلیسی (مهندس)**
-   **فرانسوی (از)**
-   **آلمانی (DEU)**
-   **نه (هین)**
-   **مجارستانی (AM)**
-   **ایتالیایی (ita)**
-   **ژاپنی (JPN)**
-   **کره ای (COR)**
-   **لهستانی (POL)**
-   **پرتغالی (POR)**
-   **روسی (روس)**
-   **اسپانیایی (آبگرم)**
-   **ترکی (دور)**
-   **ویتنامی (VIE)**
-   [**+1100 زبان از طریق Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## الزامات سخت افزاری

-   حداقل 4 گیگابایت رم ، 8 گیگابایت توصیه می شود
-   مجازی سازی در صورت اجرای روی ویندوز فعال شده است (فقط Docker)
-   CPU ، GPU (توصیه شده) ، MPS (هنوز بهینه نشده و می تواند کندتر از CPU باشد) سازگار است

> [مهم!]**قبل از ارسال یک جستجوی نصب یا اشکال با دقت در برگه موارد باز و بسته شده<br>برای اطمینان از اینکه مسئله شما قبلاً وجود ندارد.**

> [توجه داشته باشید!]**عدم وجود ساختار استاندارد مانند فصل ، پاراگراف ، پیشگفتار و غیره.<br>ابتدا باید متنی را که نمی خواهید به صورت صوتی تبدیل کنید ، به صورت دستی حذف کنید.**

### دستورالعمل نصب

1.  **بازپای کلون**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### راه اندازی رابط وب Gradio

1.  **ebook2audiobook را اجرا کنید**:
    -   **لینوکس/مکوس**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **ویندوز**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **برنامه وب را باز کنید**: برای دسترسی به برنامه وب و تبدیل کتابهای الکترونیکی ، روی URL ارائه شده در ترمینال کلیک کنید.
3.  **برای پیوند عمومی**:`python app.py --share`(همه سیستم عامل)`./ebook2audiobook.sh --share`(لینوکس/مکوس)`ebook2audiobook.cmd --share`(ویندوز)

> [مهم!]**اگر اسکریپت متوقف شده و دوباره اجرا شود ، باید رابط GRADIO GUI خود را تازه کنید<br>برای اینکه صفحه وب مجدداً به سوکت اتصال جدید وصل شود.**

### استفاده اساسی

-   **لینوکس/مکوس**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **ویندوز**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--کتاب]**: مسیر به پرونده کتاب الکترونیکی خود.
-   **[--]**: مسیر پرونده کلونینگ صوتی (اختیاری).
-   **[--زبان]**: کد زبان در ISO-639-3 (یعنی: ita برای ایتالیایی ، مهندس انگلیسی ، deu برای آلمانی ...).<br>زبان پیش فرض ENG است و -زبان برای زبان پیش فرض تنظیم شده در ./lib/lang.py اختیاری است.<br>کدهای حروف ISO-639-1 2 نیز پشتیبانی می شوند.

### نمونه بارگذاری زیپ مدل سفارشی

(باید یک فایل .zip باشد که حاوی پرونده های مدل اجباری است. مثال برای XTTS: config.json ، model.pth ، vocab.json و ref.wav)

-   **لینوکس/مکوس**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **ویندوز**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;Puart_Model_Path>**: مسیر به`model_name.zip` file,
        which must contain (according to the tts engine) all the mandatory files<br>(نگاه کنید به ./lib/models.py).

### برای راهنمای دقیق با لیست کلیه پارامترها برای استفاده

-   **لینوکس/مکوس**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **ویندوز**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **یا برای همه سیستم عامل**
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

توجه: در حالت Gradio/GUI ، برای لغو تبدیل در حال اجرا ، فقط روی کلیک کنید[x]از مؤلفه بارگذاری کتاب.

### با استفاده از داکر

همچنین می توانید از Docker برای اجرای کتاب الکترونیکی به مبدل AudioBook استفاده کنید. 
این روش سازگاری را در محیط های مختلف تضمین می کند و تنظیم را ساده می کند.

#### در حال اجرا ظرف Docker

برای اجرای ظرف Docker و شروع رابط Gradio ، از دستور زیر استفاده کنید:

فقط با CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-run با سرعت GPU (فقط Nvidia سازگار)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### ساخت ظرف داکر

-   می توانید تصویر Docker را با دستور بسازید:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

این دستور رابط Gradio را در پورت 7860 شروع می کند. (LocalHost: 7860)

-   برای گزینه های بیشتر پارامتر را اضافه کنید`--help`

## مکان های فایل کانتینر Docker

همه ebook2audiobooks پایه پایه دارند`/home/user/app/`به عنوان مثال:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## راهنمای بدون سر داکر

اولین بار برای کشیدن Docker از جدیدترین

```bash
docker pull athomasson2/ebook2audiobook
```

-   قبل از اجرای این کار ، باید در DIR فعلی خود یک DIR به نام "ورودی ورودی" ایجاد کنید
    که به آن پیوند داده خواهد شد ، اینجاست که می توانید پرونده های ورودی خود را برای دیدن تصویر Docker قرار دهید

```bash
mkdir input-folder && mkdir Audiobooks
```

-   در دستور زیر مبادله کنید**your_input_file.txt**با نام پرونده ورودی خود

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   و این باید باشد!
-   کتابهای صوتی خروجی در پوشه AudioBook که در آن قرار دارد نیز یافت می شود
    در DIR محلی خود این دستور Docker را اجرا کردید

## برای به دست آوردن دستور راهنما برای سایر پارامترهای این برنامه می توانید این کار را اجرا کنید

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

و این باعث می شود این[راهنما خروجی فرمان](#help-command-output)

### داکر آهنگسازی

این پروژه از Docker Compose برای اجرای محلی استفاده می کند. می توانید پشتیبانی GPU را فعال یا غیرفعال کنید 
با تنظیم هر یک`*gpu-enabled`یا`*gpu-disabled`در`docker-compose.yml`

#### مراحل اجرا

1.  **کلون مخزن**(اگر قبلاً این کار را نکرده اید):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **تنظیم پشتیبانی GPU (به طور پیش فرض غیرفعال)**برای فعال کردن پشتیبانی GPU ، اصلاح کنید`docker-compose.yml`و تغییر`*gpu-disabled`به`*gpu-enabled`
3.  **سرویس را شروع کنید:**
    ```bash
    docker-compose up -d
    ```
4.  **دسترسی به سرویس:**این سرویس در http&#x3A; // localhost: 7860 در دسترس خواهد بود.

### رابط Docker GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## اجاره یک پردازنده گرافیکی

سخت افزاری برای اجرای آن ندارید یا می خواهید GPU را اجاره کنید؟

#### می توانید فضای Hugginface را کپی کرده و یک GPU را با قیمت حدود 0.40 دلار در ساعت اجاره کنید

[نسخه ی نمایشی فضای بغل کردن](#huggingface-space-demo)

#### یا می توانید از Google Colab به صورت رایگان استفاده کنید!

(توجه داشته باشید که بعد از کمی از آشفتگی شما با Google Colab ، وقت می گذارد)[Google Colab رایگان](#free-google-colab)

## مسائل مشترک داکر

-   Docker gets stuck downloading Fine-Tuned models.
    (This does not happen for every computer but some appear to run into this issue)
    Disabling the progress bar appears to fix the issue,
    as discussed [اینجا در شماره 191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)نمونه ای از اضافه کردن این رفع در`docker run`فرمان

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## مدل های TTS خوب تنظیم شده

شما می توانید مدل XTTS خود را به راحتی با این repo تنظیم کنید[xtts-finetune-webui](https://github.com/daswer123/xtts-finetune-webui)

اگر می خواهید یک GPU را به راحتی اجاره کنید ، می توانید این بغل کردن را نیز کپی کنید[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

فضایی که می توانید از آن استفاده کنید تا داده های آموزشی را نیز به راحتی انجام دهید[فضای denoise-huggingface](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### مجموعه TTS تنظیم دقیق

برای یافتن مجموعه ما از مدل های TTS که قبلاً خوب تنظیم شده است ،
بازدید[این پیوند چهره بغل](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:

## دموکرات

**صدای روز بارانی**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**صدای دیوید آتتنبورو**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## فرمت های کتاب الکترونیکی پشتیبانی شده

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **بهترین نتایج**:`.epub`یا`.mobi`برای تشخیص خودکار فصل

## خروجی

-   ایجاد می کند`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(تنظیم کنید ./lib/conf.py) پرونده با ابرداده و فصل.
-   **نمونه**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## موضوعات مشترک:

-   CPU آهسته است (در CPU SMP سرور بهتر است) در حالی که GPU NVIDIA می تواند تقریباً واقعی تبدیل کند.[بحث در مورد این](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)برای نسل چند زبانه سریعتر من دیگری را پیشنهاد می کنم[پروژه ای که از piper-tts استفاده می کند](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)در عوض
    (هرچند کلونینگ صوتی صفر ندارد و صداهای با کیفیت سیری است ، اما در CPU بسیار سریعتر است).
-   "من دارای مشکلات وابستگی هستم" - فقط از Docker استفاده کنید ، کاملاً موجود در آن است و حالت بی سر دارد ،
     اضافه کردن`--help`پارامتر در انتهای دستور Docker Run برای اطلاعات بیشتر.
-   "من یک مسئله صوتی کوتاه می گیرم!" - لطفاً این موضوع را مطرح کنید ،
     ما به هر زبانی صحبت نمی کنیم و نیاز به مشاوره کاربران برای تنظیم دقیق منطق تقسیم جمله.

## آنچه من به کمک نیاز دارم! 🙌

## [لیست کامل موارد را می توان در اینجا یافت](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   هرگونه کمک از افرادی که در هر یک از زبانهای پشتیبانی شده صحبت می کنند برای کمک به روشهای مناسب تقسیم جمله
-   به طور بالقوه ایجاد راهنماهای readme برای چندین زبان (زیرا تنها زبانی که من می دانم انگلیسی است)

## با تشکر خاص

-   **پخت و پز tts**:[coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **کالیبر**:[وب سایت کالیبر](https://calibre-ebook.com)
-   **ffmpeg**:[وب سایت ffmpeg](https://ffmpeg.org)
-   [@ShakenBake15 برای روش ذخیره بهتر فصل](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [میراث v1.0](legacy/v1.0)

می توانید کد را مشاهده کنید[در اینجا](legacy/v1.0).

## به سرور ما بپیوندید!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
