# 📚 ebook2audiobook (E2A)
CPU/GPU конвертер из электронной книги в аудиокнигу с главами и метаданными<br/>
с использованием передовых движков TTS и многого другого.<br/>
Поддерживает клонирование голоса и 1158 языков!
> Важно
**Этот инструмент предназначен для использования только с электронными книгами без DRM, приобретёнными законным путём.** <br>
Авторы не несут ответственности за любое неправомерное использование этого программного обеспечения или за вытекающие из этого правовые последствия. <br>
Используйте этот инструмент ответственно и в соответствии со всеми применимыми законами.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Спасибо за поддержку разработчиков ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Запуск локально

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Запуск удалённо
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Графический интерфейс (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Нажмите, чтобы увидеть изображения веб-интерфейса</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Демо

**Демо нового голоса по умолчанию**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Больше демо</summary>

**Голос ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Голос дождливого дня**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Голос Скарлетт**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Голос Дэвида Аттенборо** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Пример**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Содержание
- [ebook2audiobook](#-ebook2audiobook)
- [Возможности](#features)
- [Графический интерфейс](#gui-interface)
- [Демо](#demos)
- [Поддерживаемые языки](#supported-languages)
- [Минимальные требования](#hardware-requirements)
- [Использование](#instructions)
  - [Запуск локально](#instructions)
    - [Запуск веб-интерфейса Gradio](#instructions)
    - [Базовое использование в режиме headless](#basic-usage)
    - [Использование пользовательской модели XTTS в режиме headless](#example-of-custom-model-zip-upload)
    - [Вывод команды справки](#help-command-output)
  - [Запуск удалённо](#run-remotely)
  - [Docker](#docker)
    - [Шаги для запуска](#docker)
    - [Распространённые проблемы с Docker](#common-docker-issues)
  
- [Дообученные модели TTS](#fine-tuned-tts-models)
  - [Коллекция дообученных моделей TTS](#fine-tuned-tts-collection)
  - [Обучение XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Поддерживаемые форматы электронных книг](#supported-ebook-formats)
- [Форматы вывода](#output-and-process-formats)
- [Возврат к более старой версии](#reverting-to-older-versions)
- [Распространённые проблемы](#common-issues)
- [Особая благодарность](#special-thanks)
- [Содержание](#table-of-contents)


## Возможности
- 🔧 **Поддерживаемые движки TTS**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Преобразование нескольких форматов файлов**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Текстовое поле** для прямого преобразования короткого текста в аудио
- 🔍 **Сканирование OCR** для файлов с текстовыми страницами в виде изображений
- 🔊 **Высококачественное преобразование текста в речь**, от почти реального времени до почти настоящего голоса
- 🗣️ **Необязательное клонирование голоса** с использованием вашего собственного голосового файла
- 🌐 **Поддерживает 1158 языков** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Дружелюбен к слабым ресурсам** — работает на **2 ГБ ОЗУ / 1 ГБ VRAM (минимум)**
- 🎵 **Форматы вывода аудиокниги**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Поддержка тегов SML** — точный контроль над прерываниями, паузами, сменой голоса и многим другим ([see below](#sml-tags-available))
- 🧩 **Необязательная пользовательская модель** с использованием вашей собственной обученной модели (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Дообученные предустановленные модели**, обученные командой E2A<br/>
     <i>(Свяжитесь с нами, если вам нужны дополнительные дообученные модели, или если вы хотите поделиться своими в официальном списке предустановок)</i>


##  Требования к оборудованию
- 2 ГБ ОЗУ мин., 8 ГБ рекомендуется.
- 1 ГБ VRAM мин., 4 ГБ рекомендуется.
- Виртуализация включена при запуске в Windows (только Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Современные движки TTS очень медленны на CPU, поэтому используйте TTS более низкого качества, такие как YourTTS, Tacotron2 и т. д.</i>

## Поддерживаемые языки
| **Арабский (ar)**    | **Китайский (zh)**    | **Английский (en)**   | **Испанский (ые)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **Французский (fr)**    | **Немецкий (de)**     | **Итальянский (it)**   | **Португальский (pt)** |
| **Польский (pl)**    | **Турецкий (tr)**    | **Русский (ru)**   | **Голландский (nl)**     |
| **Чешский (cs)**     | **Японский (ja)**   | **Хинди (hi)**     | **Бенгальский (bn)**   |
| **Венгерский (hu)** | **Корейский (ko)**     | **Вьетнамский (vi)**| **Шведский (sv)**   |
| **Персидский (fa)**   | **Йоруба (yo)**     | **Суахили (sw)**   | **Индонезийский (id)**|
| **Словацкий (sk)**    | **Хорватский (hr)**   | **Тамильский (ta)**     | **Датский (da)**    |
- [**+1130 языков и диалектов здесь**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Поддерживаемые форматы электронных книг
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Лучшие результаты**: `.epub` или `.mobi` для автоматического определения глав

## Форматы вывода и обработки
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Формат обработки можно изменить в lib/conf.py

## Доступные теги SML
- `[break]` — тишина (случайный диапазон **0.3–0.6 sec.**)
- `[pause]` — тишина (случайный диапазон **1.0–1.6 sec.**)
- `[pause:N]` — фиксированная пауза (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — переключение голоса с голоса по умолчанию или выбранного из GUI/CLI

**Проверьте наш другой репозиторий, предназначенный для автоматического добавления SML в вашу электронную книгу -> [E2A-SML](./components/E2A-SML)**

> Важно
**Прежде чем сообщать о проблеме с установкой или ошибке, внимательно поищите во вкладке открытых и закрытых задач<br>
чтобы убедиться, что вашей проблемы ещё не существует.**

Примечание
**Формат EPUB не имеет какой-либо стандартной структуры, определяющей, что такое глава, абзац, предисловие и т. д.<br>
Поэтому сначала вам следует вручную удалить весь текст, который вы не хотите преобразовывать в аудио.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Установите / Запустите ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Лаунчер для Mac**  
     Дважды щёлкните `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Примечание для пользователей Windows: устанавливается scoop для установки отсутствующих программ без прав администратора.</i>
   
1. **Откройте веб-приложение**: Нажмите на URL, указанный в терминале, чтобы получить доступ к веб-приложению и преобразовывать электронные книги. `http://localhost:7860/`
2. **Для публичной ссылки**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (все ОС)

> Важно
**Если скрипт остановлен и запущен снова, вам нужно обновить ваш интерфейс Gradio GUI<br>
чтобы веб-страница смогла повторно подключиться к новому сокету соединения.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Путь к файлу вашей электронной книги
  - **[--voice]**: Путь к файлу для клонирования голоса (необязательно)
  - **[--language]**: Код языка в ISO-639-3 (т. е.: ita для итальянского, eng для английского, deu для немецкого...).<br>
    Язык по умолчанию — eng, и --language является необязательным для языка по умолчанию, заданного в ./lib/lang.py.<br>
    Также поддерживаются двухбуквенные коды ISO-639-1.


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
     
- **<custom_model_path>**: Путь к файлу `model_name.zip`,
      который должен содержать (в зависимости от движка tts) все обязательные файлы<br>
      (см. ./lib/models.py).

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

ПРИМЕЧАНИЕ: в режиме gradio/gui, чтобы отменить выполняющееся преобразование, просто нажмите [X] компонента загрузки электронной книги.
СОВЕТ: если нужна чуть большая пауза, добавьте '[pause:3]' для 3 сек. и т. д.

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
  
### Распространённые проблемы с Docker
- Мой графический процессор NVIDIA не обнаружен?? -> [Страница вики ПРОБЛЕМЫ С GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Дообученные (fine-tuned) модели TTS
#### Дообучите свою собственную модель XTTSv2

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Шумоподавление обучающих данных

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Коллекция дообученных моделей TTS

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Для пользовательской модели XTTSv2 обязателен референсный аудиоклип голоса:

## Ваша собственная настройка Ebook2Audiobook
Вы можете свободно изменять libs/conf.py, чтобы добавлять или удалять нужные вам настройки. Если вы планируете это сделать, просто сделайте
копию оригинального conf.py, чтобы при каждом обновлении ebook2audiobook вы могли создать резервную копию вашего изменённого conf.py и вернуть
оригинал. Вы должны спланировать тот же процесс для models.py. Если вы хотите сделать свою собственную модель
официальной дообученной моделью ebook2audiobook, пожалуйста, свяжитесь с нами, и мы добавим её в список предустановок.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Распространённые проблемы:
- Мой графический процессор NVIDIA/ROCm/XPU/MPS не обнаружен?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU медленный (лучше на серверном SMP CPU), тогда как GPU может обеспечить почти преобразование в реальном времени.
   [Обсуждение этого](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Однако у него нет клонирования голоса zero-shot, и это голоса качества Siri, но он намного быстрее на cpu).
- «У меня проблемы с зависимостями» - Просто используйте docker, он полностью автономен и имеет режим headless,
   добавьте параметр `--help` в конец команды docker run для получения дополнительной информации.
- «У меня проблема с обрезанным звуком!» - ПОЖАЛУЙСТА, СОЗДАЙТЕ ОБ ЭТОМ ISSUE,
   мы не говорим на каждом языке и нуждаемся в советах пользователей, чтобы доработать логику разбиения предложений.😊

## ДК
- Все функции открыты для публичных вкладов ⭐
- Любая помощь от людей, говорящих на любом из поддерживаемых языков, чтобы помочь нам улучшить модели ⭐
- [x] Предварительный просмотр блоков/глав перед началом преобразования
- [ ] Редактировать по предложению, преобразованному для изменения хирургического текста
- [x] Интеграция тегов SML для голоса, паузы, перерыва и других изменений
- [x] -h -help информация о параметрах на разных языках
- [x] Сканирование OCR для PDF / JPG / BMP / PNG / tiff
- [x] Папка записных книжек [Обсуждалось здесь](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Сделать так, чтобы разделение текста на китайском языке не разделяло слова, и улучшить время паузы [Обсуждалось здесь](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] <bpt i="1" type="283" x="1"/>Docker Compose<ept i="1"/>;
- [x] Подман сочиняет
- [x] Ноутбук Kaggle
- [x] Записная книжка Google Colab
- [ ] [Make a IOS app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Make an android app](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Интеграция с аудиокнижной полкой

#### Дополнительные параметры
- [x] Опция перевода электронной книги
- [x] Варианты формата вывода
- [x] Папка для пакетной обработки электронных книг
- [x] Преобразование с многопроцессорной обработкой
- [x] Пакетное преобразование папки электронных книг
- [x] Обнаружение устройства GPU
- [x] Шумоподавление любого референсного аудио для загруженного клонирования голоса,
- [x] Загрузка пользовательской модели (пока только XTTSv2. больше по запросу)
- [ ] Добавить языковую модель европейского португальского хотя бы для xttsv2, fairseq, vits, piper (помощь приветствуется)
- [ ] Добавить языковую модель синдхи хотя бы для xttsv2, fairseq, vits, piper (помощь приветствуется)

#### Двигатели TTS
- [x] XTTSv2
- [x] Кора
- [x] Fairseq
- [x] ВИТС
- [x] Tacotron2
- [x] YourTTS
- [x] Черепаха
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fish-speech (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Style-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Перевод Readme
- [x] Арабский (ara)
- [x] Китайский (zho)
- [x] Английский (ENG)
- [x] Испанский (спа)
- [x] Французский (фра)
- [x] Немецкий (DEU)
- [x] Итальянский (ита)
- [x] Португальский (por)
- [x] Польский (pol)
- [x] Турецкий (tur)
- [x] Russian (rus)
- [x] Голландский (nld)
- [x] Чешский (ces)
- [x] Японский (jpn)
- [x] Хинди
- [x] Бенгальский (ben)
- [x] Hungarian (HUN)
- [x] Корейский (кор)
- [x] Вьетнамский (VIE)
- [x] Шведский (Swe)
- [x] Персидский (фас)
- [x] Йоруба (йор)
- [x] Суахили (сва)
- [x] Индонезийский (инд.)
- [x] Словацкий (slk)
- [x] Хорватский (грн)

#### 🐍 Совместимость с ОС
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] Linux (rpm-based) x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] Окна 🪟💪 РЫЧАГА
- [x] 🐧💪 ARM LINUX

**********

## Дополнительный избыток для обучения моделей и подобного (все поддерживаемые модели Coqui-tts и piper-tts в одной простой команде) 
- За информацией об этом @DrewThomasson, он сейчас работает над разработкой этого, [репозиторий в разработке здесь](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Создать простой в использовании графический интерфейс обучения для всех моделей coqui-tts в обучающих рецептах формата ljspeech [здесь от coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Информация о нормализации кода Python для участников
- никакой пустой строки между кодом, кроме как между функциями и классами.
- одинарные кавычки используются для всех ключей, кроме dict() и json. dict['key'] всегда вызывается с одинарными кавычками
- отступ в 4 пробела, вообще без табуляции
- строгая типизация для всех функций, а также объявления их аргументов и возвращаемых значений
- никакого пробела между аргументом и его типизацией, никакого пробела между функцией, «->» и возвращаемым значением

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

## Требуется пожертвование оборудования для бета-тестов
Мы принимаем любое оборудование для тестирования нашей разработки, например:
- Nvidia поддерживает cuda >= 11,8
- Карты XPU Intel
- Карты ROCm AMD, поддерживающие ROCm >=5,7

@DrewThomasson, если вы хотите помочь любым способом! 😃
<!--
## Нужно ли вам арендовать GPU для усиления нашего сервиса?
- Опрос открыт здесь https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Особая благодарность
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 за лучший метод сохранения глав](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
