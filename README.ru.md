# 📚 Ebook2audiobook

ЦП/конвертер графического процессора от электронных книг в аудиокниги с главами и метаданными<br/>Используя калибр, FFMPEG, XTTSV2, Fairseq и другие. Поддерживает голосовой клонирование и +1110 языков!

> [!ВАЖНЫЙ]**Этот инструмент предназначен для использования только с не DRM, юридически приобретенными электронными книгами.**<br>Авторы не несут ответственности за какое -либо неправильное использование этого программного обеспечения или любые полученные юридические последствия.<br>Используйте этот инструмент ответственно и в соответствии со всеми применимыми законами.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Спасибо поддержке Ebook2audiobook разработчиков!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Интерфейс графического интерфейса

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Мы покупаем[Арабский (арабский)](./readme/README_AR.md)
-   Жо[китайский](./readme/README_CN.md)
-   a \`a[Английский](README.md)
-   Swe[Шведский (шведский)](./readme/README_SWE.md)
-   фар[Персидский (персидский)](./readme/README_FA.md)
-   она[Итальянский (итальянский)](./readme/README.it.md)

## Оглавление

-   [Ebook2audiobook](#-ebook2audiobook)
-   [Функции](#features)
-   [Docker GUI интерфейс](#docker-gui-interface)
-   [Deggingface Space Demo](#huggingface-space-demo)
-   [Бесплатный Google Colab](#free-google-colab)
-   [Предварительно изготовленные звуки демонстрации](#demos)
-   [Поддерживаемые языки](#supported-languages)
-   [Требования](#hardware-requirements)
-   [Инструкции по установке](#installation-instructions)
-   [Использование](#launching-gradio-web-interface)
    -   [Запуск веб -интерфейса Gradio](#launching-gradio-web-interface)
    -   [Основное использование без головы](#basic--usage)
    -   [Использование модели без головы Custom XTTS](#example-of-custom-model-zip-upload)
    -   [Аренда графического процессора](#renting-a-gpu)
    -   [Вывод команды помощи](#help-command-output)
-   [Тонкие настроенные модели TTS](#fine-tuned-tts-models)
    -   [Для сбора тонких моделей TTS](#fine-tuned-tts-collection)
-   [Использование Docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [Docker Guide](#docker-headless-guide)
    -   [Расположение файлов контейнеров Docker](#docker-container-file-locations)
    -   [Обычные проблемы докера](#common-docker-issues)
-   [Поддерживаемые форматы электронных книг](#supported-ebook-formats)
-   [Выход](#output)
-   [Общие проблемы](#common-issues)
-   [Особая благодарность](#special-thanks)
-   [Присоединяйтесь к нашему серверу!](#join-our--server)
-   [Наследие](#legacy-v10)
-   [Оглавление](#table-of-contents)

## Функции

-   📖 Преобразует электронные книги в текстовый формат с калибром.
-   📚 Разбивает электронную книгу в главы для организованного аудио.
-   🎙 Высококачественный текст в речь с[Coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)и[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) (and more).
-   🗣 Необязательное голосовое клонирование с помощью собственного голосового файла.
-   🌍 Поддерживает +1110 языков (по умолчанию английский).[Список поддерживаемых языков](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥 разработан для работы на 4 ГБ оперативной памяти.

## [Deggingface Space Demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Пространство объятия работает на бесплатном уровне процессора, так что ожидайте очень медленного или тайм -аута LOL, просто не дайте ему гигантские файлы - это все
-   Лучше всего дублировать пространство или работать локально.

## Бесплатный Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Поддерживаемые языки

-   **Арабский (Ара)**
-   **Китайский (ZH)**
-   **Чешский (CES)**
-   **Хорватский (HRV)**
-   **Голландский (NLD)**
-   **Английский (англ)**
-   **Французский (из)**
-   **Немецкий (DEU)**
-   **Не (hin)**
-   **Венгерский (AM)**
-   **Итальянский (ITA)**
-   **Японский (JPN)**
-   **Корейский (Кор)**
-   **Polish (pol)**
-   **Португальский (PO)**
-   **Русский (Рус)**
-   **Испанский (Спа)**
-   **Турецкий (раунд)**
-   **Вьетнамцы (Vie)**
-   [**+1100 языков через Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Аппаратные требования

-   Минимум 4 ГБ оперативной памяти, рекомендуется 8 ГБ
-   Виртуализация включена, если запуск в Windows (только Docker)
-   CPU, GPU (рекомендуется), MPS (еще не оптимизированный и может быть медленнее, чем процессор)

> [!ВАЖНЫЙ]**Перед тем, как разместить вкладку «Установка» или «Проблема с ошибкой».<br>Чтобы убедиться, что ваша проблема еще не существует.**

> [!ПРИМЕЧАНИЕ]**Недостаток какой -либо структуры стандартов, например, что является главой, абзацем, предисловием и т. Д.<br>Сначала вы должны удалить вручную любой текст, который вы не хотите преобразовать в аудио.**

### Инструкции по установке

1.  **Клон репо**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Запуск веб -интерфейса Gradio

1.  **Запустить Ebook2audiobook**:
    -   **Linux/macos**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Окна**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Откройте веб -приложение**: Нажмите на URL, указанный в терминале, чтобы получить доступ к веб -приложению и преобразовать электронные книги.
3.  **Для публичной ссылки**:`python app.py --share`(Все ОС)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!ВАЖНЫЙ]**Если сценарий остановлен и запускается снова, вам нужно обновить свой интерфейс Gradio Gui<br>Чтобы позволить веб -странице воссоединиться с новым сокетом подключения.**

### Основное использование

-   **Linux/macos**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Окна**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--ebook]**: Путь к вашему файлу электронной книги.
-   **[--голос]**: Голосовой путь клонирования файла (необязательно).
-   **[--язык]**: Языковой код в ISO-639-3 (то есть: ita для итальянского, англ английский, Deu для немецкого ...).<br>Язык по умолчанию -ENG, а -Язык является необязательным для языка по умолчанию, установленного в ./lib/lang.py.<br>ISO-639-1 2 буквы также поддерживаются.

### Пример пользовательской загрузки молнии модели

(Должен быть файл .zip, содержащий обязательные файлы модели. Пример для XTTS: config.json, model.pth, vocab.json и ref.wav)

-   **Linux/macos**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Окна**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custom_model_path>**: Путь к`model_name.zip`файл,
        который должен содержать (в соответствии с двигателем TTS) все обязательные файлы<br>(см. ./lib/models.py).

### Для получения подробного руководства со списком всех параметров для использования

-   **Linux/macos**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Окна**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Или для всех ОС**
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

Примечание. В режиме Gradio/GUI, чтобы отменить запущенное преобразование, просто нажмите на[Х]от компонента загрузки электронных книг.

### Использование Docker

Вы также можете использовать Docker для запуска электронной книги для конвертера аудиокнига. 
Этот метод обеспечивает согласованность в разных средах и упрощает настройку.

#### Запуск контейнера Docker

Чтобы запустить контейнер Docker и запустить интерфейс Gradio, используйте следующую команду:

\-Рун только с процессором

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Рун с ускорением GPU (только NVIDIA совместимо)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Построение контейнера Docker

-   Вы можете построить изображение Docker с командой:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Эта команда запустит интерфейс Gradio на порту 7860. (Localhost: 7860)

-   Для получения дополнительных параметров добавить параметр`--help`

## Расположение файлов контейнеров Docker

У всех Ebook2audiobooks будет базовый режиссер`/home/user/app/`Например:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker Guide

сначала для притяжения последних последних

```bash
docker pull athomasson2/ebook2audiobook
```

-   Перед тем, как запустить это, вам нужно создать режиссер с именем «Входной стороны» в своем текущем режиме
    что будет связано, именно здесь вы можете разместить свои входные файлы для изображения Docker, чтобы увидеть

```bash
mkdir input-folder && mkdir Audiobooks
```

-   В команде ниже поменяется**Your_input_file.txt**с именем вашего входного файла

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   И это должно быть!
-   Выходные аудиокниги будут найдены в папке аудиокнига, которая также будет расположена
    В своем местном режиме вы запустили эту команду Docker в

## Чтобы получить команду справки для других параметров, которые есть в этой программе, вы можете запустить это

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

И это вызовет это[Вывод команды помощи](#help-command-output)

### Docker Compose

Этот проект использует Docker Compose для запуска локально. Вы можете включить или отключить поддержку GPU 
установив`*gpu-enabled`или`*gpu-disabled`в`docker-compose.yml`

#### Шаги для запуска

1.  **Клонировать репозиторий**(Если вы еще этого не сделали):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Установите поддержку графического процессора (отключено по умолчанию)**Чтобы включить поддержку GPU, изменить`docker-compose.yml`и изменить`*gpu-disabled`к`*gpu-enabled`
3.  **Начните сервис:**
    ```bash
    docker-compose up -d
    ```
4.  **Доступ к сервису:**Сервис будет доступен по адресу http&#x3A; // localhost: 7860.

### Docker GUI интерфейс

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Аренда графического процессора

У вас нет аппаратного обеспечения для запуска или вы хотите арендовать графический процессор?

#### Вы можете дублировать пространство Hugginface и арендовать графический процессор примерно за 0,40 доллара в час

[Deggingface Space Demo](#huggingface-space-demo)

#### Или вы можете попробовать использовать Google Colab бесплатно!

(Имейте в виду, что после небольшого количества вы не связываетесь с Google Colab)[Бесплатный Google Colab](#free-google-colab)

## Обычные проблемы докера

-   Docker застрял, загружая тонкие модели.
    (Это не происходит для каждого компьютера, но некоторые из них сталкиваются с этой проблемой)
    Отключение панели прогресса, по -видимому, решает проблему,
    Как обсуждалось[Здесь, в #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Пример добавления этого исправления в`docker run`командование

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Тонкие настроенные модели TTS

Вы можете легко настроить свою собственную модель XTTS с этим репо[XTTS-FINETUNE-WEBUI](https://github.com/daswer123/xtts-finetune-webui)

Если вы хотите легко арендовать графический процессор, вы также можете дублировать это объятие[XTTS-FINETUNE-WEBUI SPACE](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Пространство, которое вы можете использовать, чтобы легко избавиться от учебных данных[Denoise-Huggingface-Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Тонкая настраиваемая коллекция TTS

Чтобы найти нашу коллекцию уже настраиваемых моделей TTS,
посещать[Эта связь с объятием лица](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Для XTTS Custom Model A Ref Audio Clip о голосовой ссылке обязательна:

## Демо

**Дождливый день голос**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**Дэвид Аттенборо голос**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Поддерживаемые форматы электронных книг

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Лучшие результаты**:`.epub`или`.mobi`Для автоматического обнаружения главы

## Выход

-   Создает`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Установите файл ./lib/conf.py) с метаданными и главами.
-   **Пример**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Общие проблемы:

-   ЦП Медленно (лучше на серверном процессоре SMP), в то время как графический процессор NVIDIA может иметь практически в реальном времени преобразование.[Обсуждение об этом](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Для более быстрого многоязычного поколения я бы предложил свой другой[Проект, который использует Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)вместо
    (Тем не менее, он не имеет клонирования голоса с нулевым выстрелом, и это качественные голоса, но это намного быстрее на процессоре).
-   «У меня проблемы с зависимостью» - просто используйте Docker, он полностью сдерживается и имеет режим без головы,
     добавлять`--help`Параметр в конце команды Docker Run для получения дополнительной информации.
-   "Я получаю усеченную проблему аудио!" - Пожалуйста, сделайте вопрос об этом,
     Мы не говорим на каждом языке и не нуждаемся в совет от пользователей, чтобы точно настроить логику разделения предложения.

## Чем мне нужна помощь! 🙌

## [Полный список вещей можно найти здесь](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Любая помощь людей, говорящих на любом из поддерживаемых языков, чтобы помочь с надлежащими методами разделения предложений
-   Потенциально создание гидов Readme для нескольких языков (потому что единственный язык, который я знаю, - это английский 😔)

## Особая благодарность

-   **Приготовление TTS**:[Coqui TTS Github](https://github.com/idiap/coqui-ai-TTS)
-   **Калибр**:[Сайт калибра](https://calibre-ebook.com)
-   **Ffmpeg**:[FFMPEG веб -сайт](https://ffmpeg.org)
-   [@shakenbake15 для лучшего метода сохранения главы](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Вы можете просмотреть код[здесь](legacy/v1.0).

## Присоединяйтесь к нашему серверу!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
