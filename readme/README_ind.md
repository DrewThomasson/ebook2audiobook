# 📚 ebook2audiobook (E2A)
Konverter CPU/GPU dari E-Book ke buku audio dengan bab dan metadata<br/>
menggunakan mesin TTS canggih dan banyak lagi.<br/>
Mendukung kloning suara dan 1158 bahasa!
> [!IMPORTANT]
**Alat ini ditujukan hanya untuk digunakan dengan eBook tanpa DRM yang diperoleh secara legal.** <br>
Penulis tidak bertanggung jawab atas penyalahgunaan perangkat lunak ini atau konsekuensi hukum yang timbul. <br>
Gunakan alat ini secara bertanggung jawab dan sesuai dengan semua hukum yang berlaku.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Terima kasih telah mendukung pengembang ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Jalankan secara lokal

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Jalankan dari jarak jauh
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Antarmuka GUI
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Klik untuk melihat gambar GUI Web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demo

**Demo Suara Default Baru**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Demo lainnya</summary>

**Suara ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Suara Hari Hujan**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Suara Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Suara David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Contoh**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Daftar Isi
- [ebook2audiobook](#-ebook2audiobook)
- [Fitur](#features)
- [Antarmuka GUI](#gui-interface)
- [Demo](#demos)
- [Bahasa yang Didukung](#supported-languages)
- [Persyaratan Minimum](#hardware-requirements)
- [Penggunaan](#instructions)
  - [Jalankan secara Lokal](#instructions)
    - [Meluncurkan Antarmuka Web Gradio](#instructions)
    - [Penggunaan Headless Dasar](#basic-usage)
    - [Penggunaan Model XTTS Kustom Headless](#example-of-custom-model-zip-upload)
    - [Keluaran perintah bantuan](#help-command-output)
  - [Jalankan dari Jarak Jauh](#run-remotely)
  - [Docker](#docker)
    - [Langkah-langkah Menjalankan](#docker)
  
- [Cloned Voices](#cloned-voices)
- [Model TTS yang Disetel Halus](#fine-tuned-tts-models)
  - [Koleksi Model TTS yang Disetel Halus](#fine-tuned-tts-collection)
  - [Melatih XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Format eBook yang Didukung](#supported-ebook-formats)
- [Format Keluaran](#output-and-process-formats)
- [Mengembalikan ke Versi lebih lama](#reverting-to-older-versions)
- [Masalah Umum](#common-issues)
- [Terima Kasih Khusus](#special-thanks)
- [Daftar Isi](#table-of-contents)


## Fitur
- 🔧 **Mesin TTS yang didukung**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Mengonversi berbagai format file**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Area Teks** untuk langsung mengonversi teks pendek menjadi audio
- 🔍 **Pemindaian OCR** untuk file dengan halaman teks berupa gambar
- 🔊 **Text-to-speech berkualitas tinggi**, dari hampir waktu nyata hingga suara hampir nyata
- 🗣️ **Kloning suara opsional** menggunakan file suara Anda sendiri
- 🌐 **Mendukung 1158 bahasa** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Ramah sumber daya rendah** — berjalan pada **2 GB RAM / 1 GB VRAM (minimum)**
- 🎵 **Format keluaran buku audio**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Tag SML didukung** — kontrol terperinci atas jeda, hentian, peralihan suara, dan lainnya ([see below](#sml-tags-available))
- 🧩 **Model kustom opsional** menggunakan model latih Anda sendiri (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Model preset yang disetel halus** yang dilatih oleh Tim E2A<br/>
     <i>(Hubungi kami jika Anda memerlukan model yang disetel halus tambahan, atau jika Anda ingin membagikan milik Anda ke daftar preset resmi)</i>


##  Persyaratan Perangkat Keras
- RAM 2GB min, 8GB direkomendasikan.
- VRAM 1GB min, 4GB direkomendasikan.
- Virtualisasi diaktifkan jika berjalan di windows (hanya Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Mesin TTS modern sangat lambat di CPU, jadi gunakan TTS berkualitas lebih rendah seperti YourTTS, Tacotron2 dll.</i>

## Bahasa yang Didukung
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 bahasa dan dialek di sini**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Format eBook yang Didukung
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Hasil terbaik**: `.epub` atau `.mobi` untuk deteksi bab otomatis

## Format Keluaran dan proses
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Format proses dapat diubah di lib/conf.py

## Tag SML yang tersedia
- `[break]` — hening (rentang acak **0.3–0.6 sec.**)
- `[pause]` — hening (rentang acak **1.0–1.6 sec.**)
- `[pause:N]` — jeda tetap (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — alihkan suara dari suara default atau suara yang dipilih dari GUI/CLI

**Lihat repo kami yang lain yang didedikasikan untuk menambahkan SML secara otomatis di eBook Anda -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Sebelum memposting masalah pemasangan atau bug, cari dengan cermat di TAB masalah yang terbuka dan tertutup<br>
untuk memastikan masalah Anda belum ada.**

>[!NOTE]
**Format EPUB tidak memiliki struktur standar apa pun seperti apa itu bab, paragraf, kata pengantar, dll.<br>
Jadi Anda harus terlebih dahulu menghapus secara manual teks apa pun yang tidak ingin Anda konversi menjadi audio.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Pasang / Jalankan ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Peluncur Mac**  
     Klik dua kali `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Catatan untuk pengguna Windows: scoop dipasang untuk memasang program yang hilang tanpa hak istimewa administrator.</i>
   
1. **Buka Aplikasi Web**: Klik URL yang disediakan di terminal untuk mengakses aplikasi web dan mengonversi eBook. `http://localhost:7860/`
2. **Untuk Tautan Publik**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Jika skrip dihentikan dan dijalankan lagi, Anda perlu menyegarkan antarmuka GUI gradio Anda<br>
agar halaman web dapat terhubung kembali ke soket koneksi yang baru.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Jalur ke file eBook Anda
  - **[--voice]**: Jalur file kloning suara (opsional)
  - **[--language]**: Kode bahasa dalam ISO-639-3 (yaitu: ita untuk Italia, eng untuk Inggris, deu untuk Jerman...).<br>
    Bahasa default adalah eng dan --language bersifat opsional untuk bahasa default yang diatur di ./lib/lang.py.<br>
    Kode ISO-639-1 2 huruf juga didukung.


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
     
- **<custom_model_path>**: Jalur ke file `model_name.zip`,
      yang harus berisi (sesuai mesin tts) semua file wajib<br>
      (lihat ./lib/models.py).

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

CATATAN: dalam mode gradio/gui, untuk membatalkan konversi yang sedang berjalan, cukup klik [X] dari komponen unggah eBook.
TIPS: jika perlu jeda lebih lama, tambahkan '[pause:3]' untuk 3 dtk. dll.

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

## Suara Kloning
Anda dapat mengunggah audio suara apa pun dalam format audio yang didukung, durasi ideal adalah sekitar 1 hingga 5 mn.
Tidak masalah jika rekaman memiliki latar belakang berisik atau musik yang diputar di atasnya — E2A akan membersihkan suara untuk Anda.

Daftar suara kloning bawaan terutama dalam bahasa Inggris. Jika Anda membutuhkan suara dalam bahasa lain untuk secara resmi
ditambahkan ke daftar, silakan hubungi kami dan kami akan menambahkannya setelah ditinjau.

## Model TTS yang Disetel Halus (fine-tuned)
#### Setel Halus model XTTSv2 Anda sendiri

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Menghilangkan derau dari data pelatihan

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Koleksi Model TTS yang Disetel Halus

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Untuk model kustom XTTSv2, klip audio referensi dari suara referensi wajib ada:

## Kustomisasi Ebook2Audiobook Anda sendiri
Anda bebas memodifikasi libs/conf.py untuk menambah atau menghapus pengaturan yang Anda inginkan. Jika Anda berencana melakukannya, cukup buat
salinan conf.py asli sehingga pada setiap pembaruan ebook2audiobook Anda akan mencadangkan conf.py yang dimodifikasi dan mengembalikan
yang asli. Anda harus merencanakan proses yang sama untuk models.py. Jika Anda ingin menjadikan model kustom Anda sendiri
sebagai model ebook2audiobook resmi yang disetel halus, silakan hubungi kami dan kami akan menambahkannya ke daftar preset.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Masalah Umum:
- GPU NVIDIA/ROCm/XPU/MPS saya tidak terdeteksi?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU lambat (lebih baik di CPU smp server) sementara GPU dapat melakukan konversi hampir waktu nyata.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Namun ia tidak memiliki kloning suara zero-shot, dan merupakan suara berkualitas Siri, tetapi jauh lebih cepat di cpu).
- "Saya mengalami masalah dependensi" - Cukup gunakan docker, sepenuhnya mandiri dan memiliki mode headless,
   tambahkan parameter `--help` di akhir perintah docker run untuk informasi lebih lanjut.
- "Saya mendapat masalah audio terpotong!" - HARAP BUAT ISSUE TENTANG INI,
   kami tidak berbicara setiap bahasa dan memerlukan saran dari pengguna untuk menyetel halus logika pemisahan kalimat.😊

## ***** PETA JALAN *****
- Semua Fitur terbuka untuk Kontribusi publik ⭐
- Bantuan apa pun dari orang yang berbicara salah satu bahasa yang didukung untuk membantu kami meningkatkan model ⭐
- [x] Pratinjau Blok/Bab sebelum memulai konversi
- [ ] Edit per kalimat yang dikonversi untuk perubahan teks yang presisi
- [x] Integrasi tag SML untuk suara, jeda, hentian, dan lebih banyak perubahan 
- [x] Info parameter -h -help dalam berbagai bahasa
- [x] Pemindaian OCR untuk PDF / JPG / BMP / PNG / TIFF
- [x] Folder Notebook [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Membuat pemisahan teks Tiongkok tidak memisahkan kata dan meningkatkan pengaturan waktu jeda [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] Integrasi Audiobookshelf
- [ ] [Membuat aplikasi IOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Membuat aplikasi android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Opsi Tambahan
- [x] Opsi Terjemahan eBook
- [x] Pilihan format keluaran
- [x] Folder eBook batch
- [x] Konversi multiproses
- [x] Konversi folder eBook batch
- [x] Deteksi Perangkat GPU
- [x] Menghilangkan derau dari audio referensi apa pun untuk unggah kloning suara,
- [x] Unggah model kustom (hanya XTTSv2 untuk saat ini. lebih banyak atas permintaan)
- [ ] Menambahkan model bahasa Portugis Eropa setidaknya untuk xttsv2, fairseq, vits, piper (bantuan dipersilakan)
- [ ] Menambahkan model bahasa Sindhi setidaknya untuk xttsv2, fairseq, vits, piper (bantuan dipersilakan)

#### Mesin tts
- [x] XTTSv2
- [x] Gonggong
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Kura-kura
- [x] GlowTTS
- [x] Piper
- [ ] GPT - SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fish - speech (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5 - tts (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonik (https://github.com/supertone-inc/supertonic)
- [ ] Spark - tts (https://github.com/sparkaudio/spark-tts)
- [ ] index - tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro - tts (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Style - tts2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus - tts (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3 - tts (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Terjemahan Readme
- [ ] Arab (ara)
- [ ] Bahasa Mandarin (zho)
- [x] English (eng)
- [ ] Spanyol (spa)
- [ ] Prancis (fra)
- [ ] Jerman (deu)
- [ ] Italia (ita)
- [ ] Portugis (por)
- [ ] Polandia (pol)
- [ ] Turki (tur)
- [ ] Rusia (rus)
- [ ] Belanda (nld)
- [ ] Ceko (ces)
- [ ] Jepang (jpn)
- [ ] Hindi (hin)
- [ ] Bengali (ben)
- [ ] Hungaria (hun)
- [ ] Korea (kor)
- [ ] Vietnam (vie)
- [ ] Swedia (swe)
- [ ] Persia (fas)
- [ ] Yoruba (tahun)
- [ ] Swahili (swa)
- [ ] Bahasa Indonesia (ind)
- [ ] Slowakia (slk)
- [ ] Kroasia (hrv)

#### 🐍 Kompatibilitas OS
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Ekstra Berlebihan untuk melatih model dan semacamnya (Semua model Coqui-tts yang didukung dan piper-tts dalam satu perintah mudah) 
- Untuk info tentang ini @DrewThomasson, dia saat ini sedang mengerjakan pengembangannya, [repo dalam pengerjaan di sini](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Membuat gui pelatihan yang mudah digunakan untuk semua model coqui-tts dalam resep pelatihan format ljspeech [di sini dari coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informasi normalisasi Kode Python untuk kontributor
- tidak ada baris kosong di antara kode, kecuali di antara fungsi dan kelas.
- tanda kutip tunggal digunakan untuk semua kunci kecuali untuk dict() dan json. dict['key'] selalu dipanggil dengan tanda kutip tunggal
- indentasi 4 spasi, sama sekali bukan tab
- pengetikan ketat untuk semua fungsi serta deklarasi argumen dan nilai kembaliannya
- tidak ada spasi antara argumen dan pengetikannya, tidak ada spasi antara fungsi, "->" dan nilai kembalian

Contoh:

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

## Donasi perangkat keras untuk uji beta dicari
Kami menerima segala jenis perangkat keras untuk menguji pengembangan kami seperti:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson jika Anda ingin membantu dengan cara apa pun! 😃
<!--
## Apakah Anda perlu menyewa GPU untuk meningkatkan layanan dari kami?
- Sebuah jajak pendapat dibuka di sini https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Terima Kasih Khusus
Kepada semua kontributor keuangan dan kode, setiap kontribusi dan saran membantu meningkatkan kualitas E2A.