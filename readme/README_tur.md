# 📚 ebook2audiobook (E2A)
E-Kitaptan bölümler ve meta verilerle sesli kitaba CPU/GPU dönüştürücü<br/>
gelişmiş TTS motorları ve çok daha fazlasını kullanarak.<br/>
Ses klonlamayı ve 1158 dili destekler!
> [!IMPORTANT]
**Bu araç yalnızca DRM içermeyen, yasal olarak edinilmiş e-kitaplarla kullanılmak üzere tasarlanmıştır.** <br>
Yazarlar, bu yazılımın herhangi bir şekilde kötüye kullanılmasından veya bundan kaynaklanan yasal sonuçlardan sorumlu değildir. <br>
Bu aracı sorumlu bir şekilde ve geçerli tüm yasalara uygun olarak kullanın.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### ebook2audiobook geliştiricilerini desteklediğiniz için teşekkürler!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Yerel olarak çalıştırma

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Uzaktan çalıştırma
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Grafik Arayüz (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Web GUI görüntülerini görmek için tıklayın</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Demolar

**Yeni Varsayılan Ses Demosu**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Daha fazla demo</summary>

**ASMR Sesi** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Yağmurlu Gün Sesi**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett Sesi**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David Attenborough Sesi** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Örnek**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## İçindekiler
- [ebook2audiobook](#-ebook2audiobook)
- [Özellikler](#features)
- [Grafik Arayüz](#gui-interface)
- [Demolar](#demos)
- [Desteklenen Diller](#supported-languages)
- [Minimum Gereksinimler](#hardware-requirements)
- [Kullanım](#instructions)
  - [Yerel Olarak Çalıştırma](#instructions)
    - [Gradio Web Arayüzünü Başlatma](#instructions)
    - [Temel Headless Kullanımı](#basic-usage)
    - [Headless Özel XTTS Model Kullanımı](#example-of-custom-model-zip-upload)
    - [Yardım komutu çıktısı](#help-command-output)
  - [Uzaktan Çalıştırma](#run-remotely)
  - [Docker](#docker)
    - [Çalıştırma Adımları](#docker)
    - [Yaygın Docker Sorunları](#common-docker-issues)
  
- [İnce Ayarlı TTS modelleri](#fine-tuned-tts-models)
  - [İnce Ayarlı TTS Modelleri Koleksiyonu](#fine-tuned-tts-collection)
  - [XTTSv2 Eğitimi](#fine-tune-your-own-xttsv2-model)
- [Desteklenen E-Kitap Biçimleri](#supported-ebook-formats)
- [Çıktı Biçimleri](#output-and-process-formats)
- [Eski Sürüme Geri Dönme](#reverting-to-older-versions)
- [Yaygın Sorunlar](#common-issues)
- [Özel Teşekkürler](#special-thanks)
- [İçindekiler](#table-of-contents)


## Özellikler
- 🔧 **Desteklenen TTS Motorları**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Birden fazla dosya biçimini dönüştürme**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Metin Alanı** kısa bir metni doğrudan sese dönüştürmek için
- 🔍 **OCR taraması** metin sayfaları görüntü olan dosyalar için
- 🔊 **Yüksek kaliteli metinden konuşmaya**, neredeyse gerçek zamanlıdan neredeyse gerçek sese kadar
- 🗣️ **İsteğe bağlı ses klonlama** kendi ses dosyanızı kullanarak
- 🌐 **1158 dili destekler** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Düşük kaynak dostu** — **2 GB RAM / 1 GB VRAM (minimum)** ile çalışır
- 🎵 **Sesli kitap çıktı biçimleri**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **SML etiketleri desteklenir** — kesintiler, duraklamalar, ses değiştirme ve daha fazlasının ince ayarlı kontrolü ([see below](#sml-tags-available))
- 🧩 **İsteğe bağlı özel model** kendi eğittiğiniz modeli kullanarak (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **E2A Ekibi tarafından eğitilmiş ince ayarlı ön ayar modelleri**<br/>
     <i>(Ek ince ayarlı modellere ihtiyacınız olursa veya kendinizinkileri resmi ön ayar listesinde paylaşmak isterseniz bizimle iletişime geçin)</i>


##  Donanım Gereksinimleri
- 2 GB RAM min., 8 GB önerilir.
- 1 GB VRAM min., 4 GB önerilir.
- Windows üzerinde çalıştırılıyorsa sanallaştırma etkin (yalnızca Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon CPU)

*<i> Modern TTS motorları CPU'da çok yavaştır, bu yüzden YourTTS, Tacotron2 gibi daha düşük kaliteli TTS kullanın.</i>

## Desteklenen Diller
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 dil ve lehçe burada**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Desteklenen E-Kitap Biçimleri
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **En iyi sonuçlar**: otomatik bölüm algılama için `.epub` veya `.mobi`

## Çıktı ve işlem Biçimleri
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- İşlem biçimi lib/conf.py dosyasında değiştirilebilir

## Kullanılabilir SML etiketleri
- `[break]` — sessizlik (rastgele aralık **0.3–0.6 sec.**)
- `[pause]` — sessizlik (rastgele aralık **1.0–1.6 sec.**)
- `[pause:N]` — sabit duraklama (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — varsayılan sesten veya GUI/CLI'den seçilen sesten ses değiştirme

**E-kitabınıza otomatik olarak SML eklemeye adanmış diğer deposumuza göz atın -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Bir kurulum veya hata sorunu göndermeden önce, açık ve kapalı sorunlar sekmesini dikkatlice arayın<br>
sorununuzun zaten var olmadığından emin olmak için.**

>[!NOTE]
**EPUB biçimi, bölüm, paragraf, önsöz vb. şeylerin ne olduğunu tanımlayan herhangi bir standart yapıdan yoksundur.<br>
Bu yüzden önce sese dönüştürmek istemediğiniz her metni manuel olarak kaldırmalısınız.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook'u kurun / çalıştırın**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Mac Başlatıcı**  
     `Mac Ebook2Audiobook Launcher.command` dosyasına çift tıklayın


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Windows kullanıcıları için not: yönetici ayrıcalıkları olmadan eksik programları kurmak için scoop kurulur.</i>
   
1. **Web Uygulamasını açın**: Web uygulamasına erişmek ve e-kitapları dönüştürmek için terminalde verilen URL'ye tıklayın. `http://localhost:7860/`
2. **Genel Bağlantı için**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Komut dosyası durdurulup tekrar çalıştırılırsa, Gradio GUI arayüzünüzü yenilemeniz gerekir<br>
web sayfasının yeni bağlantı soketine yeniden bağlanmasına izin vermek için.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: E-kitap dosyanızın yolu
  - **[--voice]**: Ses klonlama dosyası yolu (isteğe bağlı)
  - **[--language]**: ISO-639-3 formatında dil kodu (örn.: İtalyanca için ita, İngilizce için eng, Almanca için deu...).<br>
    Varsayılan dil eng'dir ve --language, ./lib/lang.py içinde ayarlanan varsayılan dil için isteğe bağlıdır.<br>
    2 harfli ISO-639-1 kodları da desteklenir.


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
     
- **<custom_model_path>**: `model_name.zip` dosyasının yolu,
      bu dosya (TTS motoruna göre) tüm zorunlu dosyaları içermelidir<br>
      (bkz. ./lib/models.py).

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

NOT: gradio/gui modunda, çalışan bir dönüştürmeyi iptal etmek için e-kitap yükleme bileşenindeki [X] üzerine tıklamanız yeterlidir.
İPUCU: biraz daha duraklamaya ihtiyaç varsa, 3 sn. için '[pause:3]' ekleyin vb.

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
  
### Yaygın Docker Sorunları
- NVIDIA GPU'm algılanmıyor mu?? -> [GPU SORUNLARI Wiki Sayfası](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## İnce Ayarlı (fine-tuned) TTS modelleri
#### Kendi XTTSv2 modelinizi ince ayarlayın

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Eğitim verilerinin gürültüsünü giderme

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### İnce Ayarlı TTS Modelleri Koleksiyonu

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Özel bir XTTSv2 modeli için sesin referans ses klibi zorunludur:

## Kendi Ebook2Audiobook özelleştirmeniz
İstediğiniz ayarları eklemek veya kaldırmak için libs/conf.py dosyasını değiştirmekte özgürsünüz. Bunu yapmayı planlıyorsanız, sadece
orijinal conf.py dosyasının bir kopyasını alın, böylece her ebook2audiobook güncellemesinde değiştirilmiş conf.py dosyanızı yedekleyip
orijinalini geri koyabilirsiniz. Aynı süreci models.py için de planlamalısınız. Kendi özel modelinizi
resmi bir ince ayarlı ebook2audiobook modeli yapmak isterseniz, lütfen bizimle iletişime geçin, onu ön ayar listesine ekleyelim.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Yaygın Sorunlar:
- NVIDIA/ROCm/XPU/MPS GPU'm algılanmıyor mu?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU yavaştır (sunucu smp CPU'sunda daha iyi), GPU ise neredeyse gerçek zamanlı dönüştürme yapabilir.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Ancak zero-shot ses klonlaması yoktur ve sesler Siri kalitesindedir, ama cpu'da çok daha hızlıdır).
- "Bağımlılık sorunları yaşıyorum" - Sadece Docker'ı kullanın, tamamen bağımsızdır ve headless modu vardır,
   daha fazla bilgi için docker run komutunun sonuna `--help` parametresini ekleyin.
- "Kesik ses sorunu yaşıyorum!" - LÜTFEN BUNUNLA İLGİLİ BİR ISSUE AÇIN,
   her dili konuşmuyoruz ve cümle bölme mantığını ince ayarlamak için kullanıcıların tavsiyesine ihtiyacımız var.😊

## ***** YOL HARİTASI *****
- Tüm Özellikler kamuya açık Katkılara açık ⭐
- Modelleri geliştirmemize yardımcı olmak için desteklenen dillerden herhangi birini konuşan kişilerden gelen her türlü yardım ⭐
- [x] Dönüştürmeyi başlatmadan önce Blokları/Bölümleri önizleme
- [ ] Cerrahi metin değişikliği için dönüştürülen cümleye göre düzenleme
- [x] Ses, duraklama, kesinti ve daha fazla değişiklik için SML etiketi entegrasyonu 
- [x] Farklı dillerde -h -help parametre bilgisi
- [x] PDF / JPG / BMP / PNG / TIFF için OCR taraması
- [x] Notebooklar Klasörü [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Çince metin bölmenin kelimeleri bölmemesini sağlamak ve duraklama zamanlamasını iyileştirmek [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle Notebook
- [x] Google Colab Notebook
- [ ] [Bir iOS uygulaması yapmak](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Bir android uygulaması yapmak](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Audiobookshelf entegrasyonu

#### Ekstra Seçenekler
- [x] E-kitap Çeviri seçeneği
- [x] Çıktı biçimi seçenekleri
- [x] Toplu e-kitap klasörü
- [x] Çoklu işlemeyle dönüştürme
- [x] Toplu e-kitap klasörü dönüştürme
- [x] GPU Aygıt algılama
- [x] Yüklenen ses klonlama için herhangi bir referans sesin gürültüsünü gider,
- [x] Özel model yükleme (şimdilik yalnızca XTTSv2. istek üzerine daha fazlası)
- [ ] En azından xttsv2, fairseq, vits, piper için Avrupa Portekizcesi dil modeli ekleme (yardım memnuniyetle karşılanır)
- [ ] En azından xttsv2, fairseq, vits, piper için Sindhi dil modeli ekleme (yardım memnuniyetle karşılanır)

#### TTS motorları
- [x] XTTSv2
- [x] Ağaç kabuğu
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Kara kaplumbağası
- [x] GlowTTS
- [x] Piper
- [ ] GPT - SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fish - speech (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index - tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Stil - TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Readme Çevirisi
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

#### 🐍 İşletim Sistemi Uyumluluğu
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Model eğitmek ve benzeri işler için Ekstra Abartı (desteklenen tüm Coqui-tts modelleri ve piper-tts tek bir kolay komutta) 
- Bununla ilgili bilgi için @DrewThomasson, şu anda bunun geliştirilmesi üzerinde çalışıyor, [devam eden çalışma deposu burada](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] ljspeech formatındaki eğitim tariflerinde tüm coqui-tts modelleri için kullanımı kolay bir eğitim gui'si yapmak [coqui tts'ten burada](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Katkıda bulunanlar için Python Kodu normalleştirme bilgileri
- fonksiyonlar ve sınıflar arasında olması dışında, kod arasında boş satır yok.
- dict() ve json dışında tüm anahtarlar için tek tırnak kullanılır. dict['key'] her zaman tek tırnakla çağrılır
- 4 boşluk girinti, hiç sekme yok
- tüm fonksiyonlar ve bunların argüman bildirimleri ile dönüş değerleri için katı tipleme
- argüman ile tiplemesi arasında boşluk yok, fonksiyon, "->" ve dönüş değeri arasında boşluk yok

Örnek:

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

## Beta testleri için donanım bağışı aranıyor
Geliştirmemizi test etmek için her türlü donanımı kabul ediyoruz, örneğin:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson herhangi bir şekilde yardım etmek isterseniz! 😃
<!--
## Hizmetimizi güçlendirmek için bir GPU kiralamanız mı gerekiyor?
- Burada bir anket açık https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Özel Teşekkürler
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 daha iyi bölüm kaydetme yöntemi için](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
