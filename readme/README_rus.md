# 📚 ebook2audiobook (E2A)

CPU/GPU конвертер из электронной книги в аудиокнигу с главами и метаданными<br/>
с использованием передовых движков TTS и многое другое.<br/>
Поддерживает клонирование голоса и 1158 языков!
> [!IMPORTANT]
**Этот инструмент предназначен только для использования с легальными электронными книгами без DRM.** <br>
Авторы не несут ответственности за любое неправильное использование этого программного обеспечения
или любые вытекающие из этого юридические последствия.<br>
Используйте этот инструмент ответственно и в соответствии со всеми применимыми законами.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Отблагодарить разработчиков за поддержку ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Запуск локально

[![Быстрый старт](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Запуск удаленно
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Графический интерфейс
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Нажмите, чтобы увидеть изображения веб-GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Демо

**Демонстрация нового голосового режима по умолчанию**

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Больше демо</summary>

**Голос ASMR**

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Голос Rainy Day**

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Голос Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Голос David Attenborough**

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Пример**

![Пример](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Содержание
- [ebook2audiobook](#-ebook2audiobook)
- [Функции](#функции)
- [Графический интерфейс](#графический-интерфейс)
- [Демо](#демо)
- [Поддерживаемые языки](#поддерживаемые-языки)
- [Минимальные требования](#требования-к-оборудованию)
- [Использование](#инструкция)
  - [Запуск локально](#инструкция)
    - [Запуск веб-интерфейса Gradio](#инструкция)
    - [Базовое автономное использование](#основное-использование)
    - [Использование автономной пользовательской модели XTTS](#пример-загрузки-zip-файла-пользовательской-модели)
    - [Вывод команды помощи](#help-command-output)
  - [Запуск удаленно](#запуск-удаленно)
  - [Docker](#docker)
    - [Шаги для запуска](#docker)
    - [Распространённые проблемы с Docker](#распространённые-проблемы-с-docker)
  
- [Тщательно настроенные TTS-модели](#тщательно-настроенные-tts-модели)
  - [Коллекция настроенных моделей TTS](#коллекция-точно-настроенных-tts)
  - [Обучение XTTSv2](#тонкая-настройка-собственной-xttsv2-модели)
- [Поддерживаемые форматы электронных книг](#поддерживаемые-форматы-электронных-книг)
- [Форматы вывода и обработки](#форматы-вывода-и-обработки)
- [Возврат к старым версиям](#возврат-к-старым-версиям)
- [Распространённые проблемы](#распространённые-проблемы)
- [Особые благодарности](#особые-благодарности)
- [Содержание](#содержание)


## Функции
- 🔧 **Поддерживаемые движки TTS**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Конвертирование нескольких форматов файлов**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`
- 💻 **Текстовое поле** для прямого преобразования короткого текста в аудио
- 🔍 **OCR-сканирование** файлов с текстовыми страницами в виде изображений
- 🔊 **Высококачественный синтез речи** от почти реального времени до почти естественного голоса
- 🗣️ **Опциональное клонирование голоса** с использованием вашего собственного голосового файла
- 🌐 **Поддержка 1158 языков** ([список поддерживаемых языков](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Дружелюбно к системам с низкими ресурсами** — работает на** 2 Гб ОЗУ / 1 Гб ГОЗУ (минимум)**
- 🎵 **Форматы аудиокниг**: моно или стерео `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Поддержка тегов SML** — детальный контроль разрывов, пауз, смены голоса и многое другое ([смотри ниже](#sml-tags-available))
- 🧩 **Необязательная пользовательская модель** с использованием вашей собственной обученной модели (XTTSv2, VITS, FAIRSEQ, PIPER, другие по запросу)
- 🎛️ **Преднастройки моделей с тонкой настройкой**, обученные командой E2A<br/>
     <i>(Свяжитесь с нами, если Вам нужны дополнительные доработанные модели или если хотите поделиться своей моделью в официальном списке пресетов)</i>


## Требования к оборудованию
- 2ГБ ОЗУ минимально, 8ГБ рекомендуется.
- 1ГБ ГОЗУ минимум, 4ГБ рекомендуется.
- Виртуализация включена, если работает на Windows (только Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon CPU)

*<i> Современные TTS-движки очень медленные на CPU, поэтому используйте TTS более низкого качества, такие как YourTTS, Tacotron2 и т.д.</i>

## Поддерживаемые языки
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Русский (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 языков и диалектов здесь**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Поддерживаемые форматы электронных книг
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Лучшие результаты**: `.epub` или `.mobi` для автоматического определения глав

## Форматы вывода и обработки
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Формат можно изменить в lib/conf.py

## Доступные теги SML
- `[break]` — тишина (случайный диапазон **0.3–0.6 с.**)
- `[pause]` — тишина (случайный диапазон **1.0–1.6 с.**)
- `[pause:N]` — фиксированная пауза (**N с.**)
- `[voice:/путь/к/голосовому/файлу]...[/voice]` — сменить голос с голоса по умолчанию или выбранного через GUI/CLI

**Проверьте наш другой репозиторий, посвященный автоматическому добавлению SML в вашу электронную книгу -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**Перед тем как отправлять проблему с установкой или ошибкой, тщательно ищите во вкладках открытых и закрытых проблем,<br>
чтобы убедиться, что ваша проблема уже не существует.

>[!NOTE]
**Формат EPUB не имеет какой-либо стандартной структуры, такой как глава, абзац, предисловие и т.д.<br>
поэтому Вам сначала следует вручную удалить любой текст, который вы не хотите преобразовывать в аудио.**

### Инструкция

1. **Клонировать репозиторий**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Установить / запустить ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Примечание для пользователей MacOS: homebrew установлен для установки отсутствующих программ.</i>
     
   - **Mac Launcher**  
     Двойной клик `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     или
     двойной клик `ebook2audiobook.cmd`

     <i>Примечание для пользователей Windows: scoop установлен для установки отсутствующих программ без прав администратора.</i>
   
1. **Открыть веб-приложение**: щелкните по URL, указанному в терминале для получения доступа к веб-приложению и конвертации электронных книг. `http://localhost:7860/`
2. **Для публичной ссылки**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Если скрипт остановлен и запущен снова, необходимо обновить интерфейс gradio GUI<br>
чтобы веб-страница могла повторно подключиться к новому сокету соединения.**

### Основное использование
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: путь к файлу электронной книги
  - **[--voice]**: путь к файлу клонирования голоса (необязательно)
  - **[--language]**: Код языка в ISO-639-3 (например: ita для итальянского, eng для английского, rus для русского...).<br>
    Язык по умолчанию — английский, и параметр --language необязателен для языка по умолчанию, установленного в ./lib/lang.py.<br>
    Поддерживаются также коды ISO-639-1 из 2 букв.

### Пример загрузки ZIP-файла пользовательской модели
  (должен быть файлом .zip, содержащим обязательные файлы модели. Пример для XTTSv2: config.json, model.pth, vocab.json и ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Примечание: ref.wav вашей пользовательской модели всегда является голосом, выбранным для конверсии</i>
     
- **<путь_к_пользовательской_модели>**: путь к файлу `model_name.zip`,
      который должен содержать (согласно движку TTS) все обязательные файлы<br>
      (смотри ./lib/models.py).

### Для подробного руководства с перечнем всех параметров для использования
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Для всех других ОС**
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

Конвертируйте электронные книги в аудиокниги с помощью модели синтеза речи. Вы можете либо запустить интерфейс Gradio,
либо выполнить скрипт в автономном режиме для прямого конвертирования.

options:
  -h, --help            показать это сообщение справки и выйти
  --session SESSION     сессия для возобновления конверсии в случае прерывания, сбоя или повторного использования
                               пользовательских моделей и пользовательских клонированных голосов.

**** Следующий вариант предназначен только для режима gradio/gui:
  --share               (Необязательно) Включить общедоступную ссылку для совместного использования Gradio.

**** Следующие параметры предназначены только для режима --headless:
  --headless            Запуск скрипта в автономном режиме
  --ebook EBOOK         путь к файлу электронной книги для конвертации. Нельзя использовать, если указан --ebooks_dir.
  --ebooks_dir EBOOKS_DIR
                        Относительный или абсолютный путь к директории с файлами для конвертации.
                             Нельзя использовать, если присутствует опция --ebook.
  --text TEXT           Исходный текст для конвертации. Нельзя использовать, если присутствуют --ebook или --ebooks_dir.
  --language LANGUAGE   Язык электронной книги. Язык по умолчанию установлен
                             в ./lib/lang.py и используется как стандартный, если не указан другой.
                             Все совместимые коды языков находятся в ./lib/lang.py

дополнительные параметры:
  --translate ISO3      (Необязательно) Перевести электронную книгу на целевой язык (код ISO 639-3, например eng, fra, deu)
                            перед синтезом речи. Используется argostranslate. Целевой язык становится фактическим языком для TTS
                            на этой сессии. Создается копия исходной электронной книги с суффиксом _<iso3>, чтобы переведенные
                            и непереведенные версии оставались изолированными (отдельная папка процесса, аудиофрагменты и итоговый файл).
  --voice VOICE         (Необязательно) Путь к файлу клонирования голоса для движка TTS.
                            Если файл отсутствует, используется голос по умолчанию.
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
                        (Необязательно) Путь к директории вывода. По умолчанию установлен в ./lib/conf.py
  --version             Показать версию скрипта и выйти

Пример использования:
Windows:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file' --language rus
Linux/Mac:
    Gradio/GUI:
    ./ebook2audiobook.command
    Headless mode:
    ./ebook2audiobook.command --headless --ebook '/path/to/file' --language rus

Доступные SML-теги:
	[break] — тишина (случайный диапазон **0.3–0.6 с.**)
	[pause] — тишина (случайный диапазон **1.0–1.6 sec.**)
	[pause:N] — фиксированная пауза (**N с.**)
	[voice:/path/to/voice/file]...[/voice] — сменить голос с голоса по умолчанию или выбранного голоса через GUI/CLI

```

ПРИМЕЧАНИЕ: в режиме gradio/gui, чтобы отменить выполняемое преобразование, просто нажмите на [X] в компоненте загрузки электронной книги.
СОВЕТ: если нужно сделать небольшую паузу, добавьте '[pause:3]' на 3 секунды и т.д.

### Docker
1. **Клонируйте репозиторий**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Сборка контейнера**
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
4. **Запуск контейнера:**
```bash
Запуск образа Docker:
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
- ПРИМЕЧАНИЕ: MPS не доступен в Docker, поэтому необходимо использовать ЦПУ
  
### Распространённые проблемы с Docker
- Мой графический процессор NVIDIA не обнаруживается?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Тщательно настроенные TTS-модели
#### Тонкая настройка собственной XTTSv2-модели

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)

#### Удаление шума из обучающих данных

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)

### Коллекция точно настроенных TTS

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Для пользовательской модели XTTSv2 обязательным является эталонный аудиоклип голосовой ссылки:

## Ваша собственная настройка Ebook2Audiobook
Вы можете свободно изменять libs/conf.py, чтобы добавить или удалить настройки по вашему желанию.
Если вы планируете это сделать, то сделайте копию оригинального conf.py, чтобы при каждом обновлении
ebook2audiobook могли сохранить изменённый conf.py и вернуть обратно оригинальный. Аналогичный процесс
нужно проделать и для models.py. Если хотите сделать собственную кастомную модель как официальную
настроенную модель ebook2audiobook, пожалуйста, свяжитесь с нами, и мы добавим её в список предустановок.

## Возврат к старым версиям
Релизы можно найти -> [здесь](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Пример: git checkout tags/v25.7.7
```

## Распространённые проблемы:
- Мой GPU NVIDIA/ROCm/XPU/MPS не определяется?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  ЦП медленный (лучше на серверном SMP ЦП), в то время как ГП может обеспечивать почти реальное время конверсии.
   [Обсуждалось здесь](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Однако у него нет технологии голосового клонирования с нуля, и голоса качества Siri, но он работает гораздо быстрее на процессоре).
- "У меня проблемы с зависимостями" - Просто используйте Docker, он полностью автономный и имеет автономный режим,
добавьте параметр `--help` в конце команды запуска Docker для получения дополнительной информации.
- "У меня обрезается аудио!" - ПОЖАЛУЙСТА, СОЗДАЙТЕ ТЕМУ ОБ ЭТОМ, мы не говорим на всех языках и нуждаемся в советах пользователей
для доработки логики разделения предложений.😊

## ***** ROADMAP *****
- Все функции открыты для общественных вкладов ⭐
- Любая помощь от людей, говорящих на любых поддерживаемых языках, чтобы помочь нам улучшить модели ⭐
- [x] Просмотр блоков/глав перед началом конвертации
- [ ] Редактирование по предложению после конвертации для хирургических изменений текста
- [x] Интеграция тегов SML для голоса, паузы, прерывания и других изменений
- [x] -h -help информация о параметрах на разных языках
- [x] OCR сканирование для PDF / JPG / BMP / PNG / TIFF
- [x] Папка с блокнотами [Обсуждалось здесь](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Сделать так, чтобы разбиение китайского текста не разрывало слова и улучшение тайминга пауз [Обсуждалось здесь](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose
- [x] Kaggle Notebook
- [x] Google Colab Notebook
- [ ] [Создать IOS приложение](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Создать приложение для android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Интеграция Audiobookshelf

#### Дополнительные параметры
- [x] Опция перевода электронных книг
- [x] Выбор формата вывода
- [x] Папка для пакетной обработки электронных книг
- [x] Многопроцессорное преобразование
- [x] Конвертация папки с электронными книгами пакетно
- [x] Обнаружение GPU устройства
- [x] Удаление шума с любого аудио для загрузки клонированного голоса
- [x] Загрузка пользовательской модели (пока только XTTSv2. больше по запросу)
- [ ] Добавить модель Xttsv2 португальского pt_PT, доработанную для европейского португальского (нужна помощь)

#### TTS-движки
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

#### Перевод Readme
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
- [x] [Russian (rus)](README.ru.md)
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

#### 🐍 OСовместимоость с ОСС
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Дополнительный Overkill для обучения моделей и прочего (Все поддерживаемые модели Coqui-tts и piper-tts в одной простой команде)
- Для информации об этом @DrewThomasson, он в настоящее время работает над разработкой этого, [репозиторий в разработке здесь](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Сделать простую в использовании тренировочную GUI для всех моделей coqui-tts в формате LJSpeech тренировочных рецептов [здесь от coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Информация по нормализации кода Python для участников:
- нет пустых строк между кодом, кроме как между функциями и классами.
- одинарные кавычки используются для всех ключей, кроме dict() и json. dict['key'] всегда вызывается с одинарной кавычкой
- отступ 4 пробела, табуляция не используется
- строгая типизация для всех функций, включая объявление аргументов и возвращаемых значений
- нет пробела между аргументом и его типом, нет пробелов между функцией, "->" и возвращаемым значением

Пример:

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

## Требуются пожертвования оборудования для бета-тестов
Мы принимаем любое оборудование для тестирования нашей разработки, такое как:
- Nvidia с поддержкой CUDA >= 11.8
- XPU карты Intel
- ROCm карты AMD с поддержкой ROCm >= 5.7

@DrewThomasson если вы хотите чем-то помочь! 😃
<!--
## Вам нужно арендовать GPU, чтобы повысить качество сервиса для нас?
- Здесь открыт опрос https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Особые благодарности
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Вебсайт Calibre](https://calibre-ebook.com)
- **FFmpeg**: [Вебсайт FFmpeg](https://ffmpeg.org)
- [@shakenbake15 для лучшего способа сохранения главы](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
