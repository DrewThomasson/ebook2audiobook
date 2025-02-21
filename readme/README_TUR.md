📚 eBook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
E -Kitaplardan Bölümler ve Meta Veri ile Sesli Kitaplara CPU/GPU Dönüştürücü <br/>
Kalibre, FFMPEG, XTTSV2, Fairseq ve daha fazlasını kullanarak. Ses klonlama ve +1110 dillerini destekler! [!ÖNEMLİ]
** Bu araç, DRM olmayan, yasal olarak elde edilen e-kitaplarla kullanılmak üzere tasarlanmıştır. ** <br>
Yazarlar bu yazılımın kötüye kullanılmasından veya sonuçta ortaya çıkan yasal sonuçlardan sorumlu değildir. <br>
Bu aracı sorumlu ve yürürlükteki tüm yasalara uygun olarak kullanın. [!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [KO-FI] (https://img.shields.io/badge/ko-fi-f16061?style=for-the-the-badge&logo=ko-fi&logocolor=white)] (https: // ko-fi .com/athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_web_gui] (varlıklar/demo_web_gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
Ara [العربية (Arapça)] (./ Readme/Readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
Zho [中文 (Çince)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
Swe [Svenska (İsveççe)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
Fas [فارسی (Farsça)] (./ Readme/Readme_fa.md)


## Table of Contents
[Ebook2audiobook] (#-Ebook2audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Özellikler] (#özellikler)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Docker GUI arayüzü] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Huggingface Uzay Demosu] (#Huggingface-uzay-demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Ücretsiz Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Önceden yapılmış ses demoları] (#demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Desteklenen Diller] (#desteklenen diller)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Gereksinimler] (#donanım talepleri)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Kurulum Talimatları] (#kurulum-dizileri)
- [Output](#output)
- [Common Issues](#common-issues)
[Kullanım] (#lansman-grado-web-interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Gradio Web Arayüzünü Başlatma] (#Lansman-Ladio-Web-Interface)


[Temel başsız kullanım] (#Basic-kullanım)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Başsız Özel XTTS Model Kullanımı] (#Custom-Model-Zip-Upload örneği)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[GPU kiralıyor] (#kiralama-a-gpu)


[Yardım komut çıktısı] (#yardım-komut çıkışı)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[İnce ayarlanmış TTS modelleri] (#İnce Tuned-TTS modelleri)


[İnce ayarlanmış TTS modellerinin toplanması için] (#ince-tuned-tts-collection)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Docker-Container Running)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Bina-Doklatıcı-Container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#docker-compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Rehberi] (#Docker-Başsız Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Docker Container Dosya Konumları] (#Docker-Container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Ortak Docker sorunları] (#Common-docker-Issues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Desteklenen e-kitap formatları] (#Desteklenen-e-kitap formatları)


[Çıktı] (#çıktı)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Ortak Sorunlar] (#Ortak Düzenler)


[Özel teşekkürler] (#Özel teşekkürler)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Miras] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Özellikler
```bash
📖 e -kitapları kalibre ile metin biçimine dönüştürür. 📚 Ebook'u organize ses için bölümlere ayırır. 🎙️ [Coqui XTTSV2] (https://huggingface.co/coqui/xtts-v2) ve [Fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ örnekler/mms) (ve daha fazlası). 🗣️ Kendi sesli dosyanızla isteğe bağlı ses klonlama. 🌍 +1110 dilini destekler (varsayılan olarak İngilizce). [Desteklenen Dillerin Listesi] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

4GB RAM üzerinde çalışacak şekilde tasarlanmıştır. [Huggingface Uzay Demosu] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [Hugging Yüz] (https://img.shields.io/badge/hugging%20face-nkey?style=for-the-badge&logo=huggingface)] (https://huggingface.co/spaces/drewthomassson /ebook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Huggingface alanı ücretsiz CPU katmanında çalışıyor, bu yüzden çok yavaş veya zaman aşımı bekleyin lol, sadece dev dosyalar vermeyin hepsi
   - **Windows**
     ```bash
Alanı çoğaltmak veya yerel olarak koşmak için en iyisi. Ücretsiz Google Colab
     ```
[! [Ücretsiz Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)] (https://colab.research.google.com/github/drewromasson/Ebook2audiobook/blob/ ana/dizüstü bilgisayarlar/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Desteklenen Diller
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arapça (ARA) **

> [!IMPORTANT]
** Çince (zho) **
to let the web page reconnect to the new connection socket.**

** Çek (CES) **
   - **Linux/MacOS**:
     ```bash
** Hırvat (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Hollandalı (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** İngilizce (Eng) **
     ```
     
** Fransızca (FRA) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Almanca (Deu) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Macar (Hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** İtalyan (ita) **
     ```
   - **Windows**
** Japon (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Korece (KOR) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** cila (POL) **


** Portekizce (POR) **
   - **Linux/MacOS**
     ```bash
** Rusça (RUS) **
     ```
   - **Windows**
** İspanyolca (Spa) **
     .\ebook2audiobook.cmd --help
     ```
** Türk (Tur) **
    ```python
     app.py --help
** Vietnamca (VIE) **

<a id="help-command-output"></a>
[** +1100 Fairseq üzerinden **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Donanım Gereksinimleri
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
Minimum 4GB RAM, 8GB önerilir
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Windows'ta çalışıyorsanız sanallaştırma etkinleştirildi (yalnızca Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (Önerilen), MPS (henüz optimize edilmemiş ve CPU'dan daha yavaş olabilir) uyumlu

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Bir yükleme veya hata sorunu yayınlamak için açılan ve kapalı sorunlar sekmesine dikkatle arama yapın <br>
Sorununuzun zaten mevcut olmadığından emin olmak için. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Bölüm, paragraf, önsöz vb. Gibi herhangi bir standart yapısından yoksun olmak <br>
Önce sesle dönüştürülmek istemediğiniz metni manuel olarak kaldırmalısınız. **

Kurulum Talimatları

** klon repo **
  --headless            Run the script in headless mode
Gradio Web Arayüzünü Başlatma
  --ebooks_dir EBOOKS_DIR
** ebook2audiobook çalıştırın **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** linux/macOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Web uygulamasını açın **: Web uygulamasına erişmek ve e -kitapları dönüştürmek için terminalde sağlanan URL'yi tıklayın. ** Halka açık bağlantı için **:
`python app.py -share` (tüm işletim sistemleri)
`./ebook2audiobook.sh --Share` (linux/macOS)
`ebook2audiobook.cmd --Share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!ÖNEMLİ]
** Komut dosyası durdurulur ve tekrar çalıştırılırsa, Gradio GUI arayüzünüzü yenilemeniz gerekir <br>
Web sayfasının yeni bağlantı soketine yeniden bağlanmasına izin vermek için. **
                        (Optional) Fine tuned model path. Default is builtin model.
Temel Kullanım
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** linux/macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-e-kitap] **: e-kitap dosyanıza giden yol. ** [-ses] **: ses klonlama dosya yolu (isteğe bağlı). ** [-dil] **: ISO-639-3'teki dil kodu (yani: İtalyan için ITA, İngilizce için Eng, Almanca için Deu ...). <br>
Varsayılan dil ENG'dir ve ./lib/lang.py. <br> adresinde ayarlanan varsayılan dil için isteğe bağlıdır.
ISO-639-1 2 harf kodları da desteklenir. Özel Model Zip Yükleme Örneği
  --repetition_penalty REPETITION_PENALTY
(Zorunlu model dosyalarını içeren bir .zip dosyası olmalıdır. XTTS örneği: config.json, model.pth, vocab.json ve ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** linux/macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <custy_model_path> **: `model_name.zip` dosyasına giden yol,
    (TTS motoruna göre) tüm zorunlu dosyaları içermelidir <br>
    (Bkz. ./lib/models.py). Kullanılacak tüm parametrelerin listesi ile ayrıntılı kılavuz için
  --output_dir OUTPUT_DIR
** linux/macOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** veya tüm işletim sistemleri için **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a ID = "Yardım-komut-çıktı"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Not: Gradio/GUI modunda, çalışan bir dönüşümü iptal etmek için e -kitap yükleme bileşeninden [x] 'e tıklayın. Docker'ı kullanma
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Ayrıca e -kitabı sesli kitap dönüştürücüsüne çalıştırmak için Docker'ı da kullanabilirsiniz. Bu yöntem, farklı ortamlarda tutarlılık sağlar ve kurulumu basitleştirir. Docker kabını çalıştırma

Docker konteynerini çalıştırmak ve Gradio arabirimini başlatmak için aşağıdaki komutu kullanın:

### Using Docker
-Yalnızca CPU ile Run
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Docker konteynerinin oluşturulması

Docker görüntüsünü komutla oluşturabilirsiniz:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Bu komut 7860 bağlantı noktasında Gradio arayüzünü başlatacaktır. (Localhost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Daha fazla seçenek için `--help` parametresini ekleyin
```


Tüm Ebook2audiobooks, `/Home/User/App/` `
Örneğin:
`tmp` =`/home/user/app/tmp`
`` audiobooks '' = `/home/user/uygulama/sesli kitaplar '
```
Docker başsız rehber
- For more options add the parameter `--help`


## Docker container file locations
Bunu çalıştırmadan önce, mevcut direğinizde "Giriş-Kol" adlı bir DIR oluşturmanız gerekir.
hangi bağlantılı olacak, burası Docker görüntüsünün görmek için giriş dosyalarınızı koyabileceğiniz yerdir.
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
Ve bu olmalı! Çıktı sesli kitaplar, ayrıca bulunacak olan sesli kitap klasöründe bulunacaktır.
Yerel direğinizde bu Docker komutunu çalıştırdınız
docker pull athomasson2/ebook2audiobook
Diğer parametreler için yardım komutunu almak için bu program bunu çalıştırabilirsiniz
- Before you do run this you need to create a dir named "input-folder" in your current dir
Ve bu bunu çıkaracak 
[Yardım komut çıktısı] (#yardım-komut çıkışı)
mkdir input-folder && mkdir Audiobooks
Docker Compose
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Bu proje, yerel olarak çalıştırmak için Docker Compose'u kullanıyor. GPU desteğini etkinleştirebilir veya devre dışı bırakabilirsiniz 
`docker-compose.yml '' de`*gpu özellikli 'veya `*gpu-disabl' ayarlayarak
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Koşmak İçin Adımlar
    athomasson2/ebook2audiobook \
** Depoyu klonla ** (henüz yapmadıysanız):
```
- And that should be it! 
** GPU desteğini ayarlayın (varsayılan olarak devre dışı) **
GPU desteğini etkinleştirmek için `docker-compose.yml 'değiştirin ve`*gpu-disabling'i'*gpu özellikli 'olarak değiştirin


** Hizmeti başlatın: **

```bash
** Hizmete erişin: **

```
! [Demo_web_gui] (varlıklar/demo_web_gui.gif)
[Help command output](#help-command-output)


Çalışacak donanımınız yok mu yoksa bir GPU kiralamak mı istiyorsunuz? Hugginface alanını çoğaltabilir ve saatte yaklaşık 0,40 $ karşılığında bir GPU kiralayabilirsiniz
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Huggingface Uzay Demosu] (#Huggingface-uzay-demo)


[Ücretsiz Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Ortak Docker sorunları
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker, ince ayarlı modelleri indirmeye sıkışır. (Bu her bilgisayar için olmaz, ancak bazıları bu soruna giriyor gibi görünüyor)
Sorunu çözmek için ilerleme çubuğunu devre dışı bırakma gibi görünüyor,
Tartışıldığı gibi [ #191'de] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Bu düzeltmeyi `` Docker Run 'komutuna ekleme örneği
3. **Start the service:**
İnce ayarlanmış TTS modelleri
    docker-compose up -d
Bu repo ile kendi XTTS modelinize kolayca ince ayar yapabilirsiniz
[XTTS-FINETUNE-WEBUI] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-FINETUNE-WEBUI-SPACE] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Eğitim verilerini kolayca gürlemek için kullanabileceğiniz bir alan da
[denoise-huggingface-space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
İnce ayarlanmış TTS koleksiyonu
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Zaten ince ayarlanmış TTS modelleri koleksiyonumuzu bulmak için,


## Renting a GPU
Demolar
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Yağmurlu gün sesi **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough Voice **


Desteklenen e -kitap formatları
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,.
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** En iyi sonuçlar **: `.epub` veya` .mobi` Otomatik bölüm algılama için
    -p 7860:7860 athomasson2/ebook2audiobook
Çıktı


! [Örnek] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc059692d71278a88/readme_files/example_in_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Ortak Sorunlar:

CPU yavaş (sunucu SMP CPU'da daha iyi), NVIDIA GPU neredeyse gerçek zamanlı dönüşüm olabilir. [Bu konuda tartışma] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
Daha hızlı çok dilli nesil için diğerlerimi öneririm

(Yine de sıfır atış ses klonlaması yoktur ve Siri kalite sesleridir, ancak CPU'da çok daha hızlıdır). "Bağımlılık sorunlarım var" - sadece docker'ı kullanın, tamamen kendi kendine içerdiği ve başsız bir modu var,
 Daha fazla bilgi için Docker Run komutunun sonuna `--help` parametresi ekleyin. "Kesik bir ses sorunu alıyorum!" - Lütfen bunun bir sorununu yapın,

### Fine Tuned TTS Collection
Neyle yardıma ihtiyacım var! 🙌
[Şeylerin tam listesi burada bulunabilir] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potansiyel olarak birden çok dil için ReadMe Kılavuzları Oluşturma (Bildiğim tek dil İngilizce'dir 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** coqui tts **: [Coqui tts GitHub] (https://github.com/idiap/coquii-a-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [ffmpeg web sitesi] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (miras/v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Kodu [burada] görüntüleyebilirsiniz (Legacy/V1.0). Sunucumuza katılın! [!