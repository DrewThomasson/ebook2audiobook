📚 Ebook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
ЦП/конвертер графического процессора от электронных книг в аудиокниги с главами и метаданными <br/>
Используя калибр, FFMPEG, XTTSV2, Fairseq и другие. Поддерживает голосовой клонирование и +1110 языков! [!ВАЖНЫЙ]
** Этот инструмент предназначен для использования только с не DRM, юридически приобретенными электронными книгами. ** <br>
Авторы не несут ответственности за какое -либо неправильное использование этого программного обеспечения или любые полученные юридические последствия. <br>
Используйте этот инструмент ответственно и в соответствии со всеми применимыми законами. [!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko-fi-f16061?style=for-the-badge&logo=ko-fi&logocolor=white)] (https: // Ko-fi .com/athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [demo_web_gui] (Assets/demo_web_gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
Ara [العربية (арабский)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文 (китайский)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
swe [svenska (шведский)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
Fas [فارسی (персидский)] (./ readme/readme_fa.md)


## Table of Contents
[ebook2audiobook] (#-ebook2audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Особенности] (#функции)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Интерфейс Gui Docker] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Demo Demo Guggingface Space] (#guggingface-space-demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Бесплатно Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Предварительно изготовленные демоверсии аудио] (#демонстрации)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Поддерживаемые языки] (#поддерживаемые языки)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Требования] (#оборудование для оборудования)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Инструкции по установке] (#Установка-инструктики)
- [Output](#output)
- [Common Issues](#common-issues)
[Использование] (#Запуск-градио-Web-Interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Запуск веб-интерфейса Gradio] (#Запуск Gradio-Web-Interface)


[Основное использование без головы] (#Basic-Usage)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Использование модели Custom XTTS без головы] (#Пример примера модели-zip-Zip-Zip-upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Аренда графического процессора] (#randing-a-gpu)


[Вывод команды справки] (#вспомогательный результат)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Тонкие настроенные модели TTS] (#тонкие модели TTS)


[Для сбора тонко настроенных моделей TTS] (#тонко настроенный TTS-коллекция)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker run] (#chrunge the-docker-container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Строительство-докера-контейнер)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#Docker-Compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Guide] (#Docker-Head-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Расположение файлов контейнера Docker] (#Docker-Container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Общие проблемы с докером] (#Common-Docker-Issues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Поддерживаемые форматы электронных книг] (#поддерживаемые форматы книги)


[Вывод] (#вывод)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Общие проблемы] (#Общие выпуски)


[Специальное спасибо] (#Специальные спасибо)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Функции
```bash
📖 Преобразует электронные книги в текстовый формат с калибром. 📚 Разбивает электронную книгу в главы для организованного аудио. 🎙 Высококачественный текст в речь с [coqui xttsv2] (https://huggingface.co/coqui/xtts-v2) и [fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ Примеры/мс) (и больше). 🗣 Необязательное голосовое клонирование с помощью собственного голосового файла. 🌍 Поддерживает +1110 языков (по умолчанию английский). [Список поддерживаемых языков] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥 разработан для работы на 4 ГБ оперативной памяти. [Demo Demo GuggingFace] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [Объятие лица] (https://img.shields.io/badge/hugging%20face-paces-yellow?style=for-the-badge&logo=huggingface)] (https://huggingface.co/spaces/drewthomasson /ebook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Пространство объятия работает на бесплатном уровне процессора, так что ожидайте очень медленного или тайм -аута LOL, просто не дайте ему гигантские файлы - это все
   - **Windows**
     ```bash
Лучше всего дублировать пространство или работать локально. Бесплатный Google Colab
     ```
[! [Бесплатно Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)] (https://colab.research.google.com/github/drewthomasson/ebook2audiobook/blob/ Main/Notebooks/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Поддерживаемые языки
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** арабский (Ара) **

> [!IMPORTANT]
** Китайский (Жо) **
to let the web page reconnect to the new connection socket.**

** Чешский (CES) **
   - **Linux/MacOS**:
     ```bash
** Хорватский (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** голландский (nld) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** английский (англ) **
     ```
     
** французский (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Немецкий (DEU) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Венгерский (хун) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** Итальянский (ITA) **
     ```
   - **Windows**
** Японский (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Корейский (KOR) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Польский (Пол) **


** Португальский (POR) **
   - **Linux/MacOS**
     ```bash
** русский (Рус) **
     ```
   - **Windows**
** Испанский (Спа) **
     .\ebook2audiobook.cmd --help
     ```
** турецкий (тур) **
    ```python
     app.py --help
** Вьетнамцы (Vie) **

<a id="help-command-output"></a>
[** +1100 языки через Fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Аппаратные требования
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
Минимум 4 ГБ оперативной памяти, рекомендуется 8 ГБ
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Виртуализация включена, если запуск в Windows (только Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (рекомендуется), MPS (еще не оптимизированный и может быть медленнее, чем процессор)

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Прежде чем опубликовать вкладку «Установка» или «Проблема с ошибкой» на вкладку «Открытые и закрытые проблемы» <br>
Чтобы убедиться, что ваша проблема еще не существует. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Недостаток какой -либо структуры стандартов, такая как глава, абзац, предисловие и т. Д. <br>
Сначала вы должны удалить вручную любой текст, который вы не хотите преобразовать в аудио. **

Инструкции по установке

** клон репо **
  --headless            Run the script in headless mode
Запуск веб -интерфейса Gradio
  --ebooks_dir EBOOKS_DIR
** запустить Ebook2audiobook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** linux/macos **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Откройте веб -приложение **: Нажмите на URL, указанный в терминале, чтобы получить доступ к веб -приложению и преобразовать электронные книги. ** для публичной ссылки **:
`python app.py -share` (все ОС)
`./ebook2audiobook.sh -share` (linux/macos)
`ebook2audiobook.cmd -share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!ВАЖНЫЙ]
** Если сценарий остановлен и запускается снова, вам нужно обновить свой интерфейс Gradio Gui <br>
Чтобы позволить веб -странице воссоединиться с новым сокетом подключения. **
                        (Optional) Fine tuned model path. Default is builtin model.
Основное использование
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** linux/macos **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-ebook] **: Путь к вашему файлу электронной книги. ** [-Голос] **: Голосовой путь клонирования файла (необязательно). ** [-Язык] **: языковой код в ISO-639-3 (то есть: ita для итальянского, англ.
Язык по умолчанию eng, а -Язык является необязательным для языка по умолчанию.
ISO-639-1 2 буквы также поддерживаются. Пример пользовательской загрузки молнии модели
  --repetition_penalty REPETITION_PENALTY
(Должен быть файл .zip, содержащий обязательные файлы модели. Пример для XTTS: config.json, model.pth, vocab.json и ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** linux/macos **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <cament_model_path> **: path to `model_name.zip` file,
    который должен содержать (в соответствии с двигателем TTS) все обязательные файлы <br>
    (см. ./lib/models.py). Для получения подробного руководства со списком всех параметров для использования
  --output_dir OUTPUT_DIR
** linux/macos **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** или для всей ОС **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "Help-Command-Output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
ПРИМЕЧАНИЕ. В режиме Gradio/GUI, чтобы отменить запущенное преобразование, просто нажмите на компонент загрузки электронной книги. Использование Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Вы также можете использовать Docker для запуска электронной книги для конвертера аудиокнига. Этот метод обеспечивает согласованность в разных средах и упрощает настройку. Запуск контейнера Docker

Чтобы запустить контейнер Docker и запустить интерфейс Gradio, используйте следующую команду:

### Using Docker
-Рун только с процессором
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Построение контейнера Docker

Вы можете построить изображение Docker с командой:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Эта команда запустит интерфейс Gradio на порту 7860. (Localhost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Для получения дополнительных параметров добавить параметр `-help`
```


У всех Ebook2audiobooks будет базовый режиссер `/home/user/app/`
Например:
`tmp` =`/home/user/app/tmp`
`adiobooks` =`/home/user/app/audiobooks`
```
Docker Guide
- For more options add the parameter `--help`


## Docker container file locations
Перед тем, как запустить это, вам нужно создать режиссер с именем «Входной стороны» в своем текущем режиме
что будет связано, именно здесь вы можете разместить свои входные файлы для изображения Docker, чтобы увидеть
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
И это должно быть! Выходные аудиокниги будут найдены в папке аудиокнига, которая также будет расположена
В своем местном режиме вы запустили эту команду Docker в
docker pull athomasson2/ebook2audiobook
Чтобы получить команду справки для других параметров, которые есть в этой программе, вы можете запустить это
- Before you do run this you need to create a dir named "input-folder" in your current dir
И это вызовет это 
[Вывод команды справки] (#вспомогательный результат)
mkdir input-folder && mkdir Audiobooks
Docker Compose
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Этот проект использует Docker Compose для запуска локально. Вы можете включить или отключить поддержку GPU 
Установив либо `*GPU-inablet`, либо`*GPU-DISALBAUD` в `docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Шаги для запуска
    athomasson2/ebook2audiobook \
** Клонировать репозиторий ** (если вы еще этого не сделали):
```
- And that should be it! 
** Установите поддержку GPU (по умолчанию отключено) **
Чтобы включить поддержку GPU, измените `docker-compose.yml` и изменить`*GPU-DISALTED` на `*GPU-с поддержкой


** Начните службу: **

```bash
** Доступ к сервису: **

```
! [demo_web_gui] (Assets/demo_web_gui.gif)
[Help command output](#help-command-output)


У вас нет аппаратного обеспечения для запуска или вы хотите арендовать графический процессор? Вы можете дублировать пространство Hugginface и арендовать графический процессор примерно за 0,40 доллара в час
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Demo Demo Guggingface Space] (#guggingface-space-demo)


[Бесплатно Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Обычные проблемы докера
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker застрял, загружая тонкие модели. (Это не происходит для каждого компьютера, но некоторые из них сталкиваются с этой проблемой)
Отключение панели прогресса, по -видимому, решает проблему,
Как обсуждалось [здесь, в #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Пример добавления этого исправления в команде `docker run`
3. **Start the service:**
Тонкие настроенные модели TTS
    docker-compose up -d
Вы можете легко настроить свою собственную модель XTTS с этим репо
[XTTS-finetune-webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-finetune-webui-пространство] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Пространство, которое вы можете использовать, чтобы легко избавиться от учебных данных
[Denoise-DugingFice-Space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Тонкая настраиваемая коллекция TTS
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Чтобы найти нашу коллекцию уже настраиваемых моделей TTS,


## Renting a GPU
Демо
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Дождливый день голос **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** Дэвид Аттенборо голос **


Поддерживаемые форматы электронных книг
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Лучшие результаты **: `.epub` или` .mobi` для автоматического обнаружения главы
    -p 7860:7860 athomasson2/ebook2audiobook
Выход


! [Пример] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Общие проблемы:

ЦП Медленно (лучше на серверном процессоре SMP), в то время как графический процессор NVIDIA может иметь практически в реальном времени преобразование. [Обсуждение об этом] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
Для более быстрого многоязычного поколения я бы предложил свой другой

(Тем не менее, он не имеет клонирования голоса с нулевым выстрелом, и это качественные голоса, но это намного быстрее на процессоре). «У меня проблемы с зависимостью» - просто используйте Docker, он полностью сдерживается и имеет режим без головы,
 Добавьте параметр `-help` в конце команды Docker Run для получения дополнительной информации. "Я получаю усеченную проблему аудио!" - Пожалуйста, сделайте вопрос об этом,

### Fine Tuned TTS Collection
Чем мне нужна помощь! 🙌
[Полный список вещей можно найти здесь] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Потенциально создание гидов для чтения для нескольких языков (потому что единственный язык, который я знаю, - это английский 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** coqui tts **: [coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [веб -сайт ffmpeg] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Вы можете просмотреть код [здесь] (Legacy/v1.0). Присоединяйтесь к нашему серверу! [!