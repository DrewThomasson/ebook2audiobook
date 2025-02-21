# 📚 eBook2audiobook

E -Kitaplardan Sesli Kitaplara Bölüm ve Meta Verilerle CPU/GPU Dönüştürücü<br/>Kalibre, FFMPEG, XTTSV2, Fairseq ve daha fazlasını kullanarak. Ses klonlama ve +1110 dillerini destekler!

> [!ÖNEMLİ]**Bu araç, yalnızca DRM olmayan, yasal olarak edinilmiş e-kitaplarla kullanılmak üzere tasarlanmıştır.**<br>Yazarlar bu yazılımın kötüye kullanılmasından veya sonuçta ortaya çıkan yasal sonuçlardan sorumlu değildir.<br>Bu aracı sorumlu ve yürürlükteki tüm yasalara uygun olarak kullanın.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Destek Ebook2audiobook geliştiricileri için teşekkürler!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### GUI arayüzü

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Alış[Arapça (Arapça)](./readme/README_AR.md)
-   Zho[Çince](./readme/README_CN.md)
-   A \`[İngilizce](README.md)
-   çukur[İsveççe (İsveççe)](./readme/README_SWE.md)
-   fas[Farsça (Farsça)](./readme/README_FA.md)
-   o[İtalyan (İtalyan)](./readme/README.it.md)

## İçindekiler

-   [Ebook2audiobook](#-ebook2audiobook)
-   [Özellikler](#features)
-   [Docker GUI arayüzü](#docker-gui-interface)
-   [Huggingface uzay demosu](#huggingface-space-demo)
-   [Ücretsiz Google Colab](#free-google-colab)
-   [Önceden hazırlanmış ses demoları](#demos)
-   [Desteklenen Diller](#supported-languages)
-   [Gereksinim](#hardware-requirements)
-   [Kurulum Talimatları](#installation-instructions)
-   [Kullanım](#launching-gradio-web-interface)
    -   [Gradio Web Arayüzünü Başlatma](#launching-gradio-web-interface)
    -   [Temel Başsız Kullanım](#basic--usage)
    -   [Başsız Özel Xtts Model Kullanımı](#example-of-custom-model-zip-upload)
    -   [Bir GPU kiralamak](#renting-a-gpu)
    -   [Ortaya Çıktıya Yardım Edin](#help-command-output)
-   [İnce ayarlanmış TTS modelleri](#fine-tuned-tts-models)
    -   [İnce ayarlanmış TTS modellerinin toplanması için](#fine-tuned-tts-collection)
-   [Docker'ı kullanma](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [Docker başsız rehber](#docker-headless-guide)
    -   [Docker Container Dosya Konumları](#docker-container-file-locations)
    -   [Ortak Docker sorunları](#common-docker-issues)
-   [Desteklenen e -kitap formatları](#supported-ebook-formats)
-   [Çıktı](#output)
-   [Ortak sorunlar](#common-issues)
-   [Özel Teşekkürler](#special-thanks)
-   [Sunucumuza katılın!](#join-our--server)
-   [Miras](#legacy-v10)
-   [İçindekiler](#table-of-contents)

## Özellikler

-   📖 e -kitapları kalibre ile metin biçimine dönüştürür.
-   📚 E -kitabı organize ses için bölümlere ayırır.
-   🎙️ Yüksek kaliteli metin-konuşma ile[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)Ve[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(ve daha fazlası).
-   🗣️ Kendi sesli dosyanızla isteğe bağlı ses klonlama.
-   🌍 +1110 dilini destekler (varsayılan olarak İngilizce).[Desteklenen Dillerin Listesi](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   4GB RAM üzerinde çalışacak şekilde tasarlanmıştır.

## [Huggingface uzay demosu](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingface alanı ücretsiz CPU katmanında çalışıyor, bu yüzden çok yavaş veya zaman aşımı bekleyin lol, sadece dev dosyalar vermeyin hepsi
-   Alanı çoğaltmak veya yerel olarak koşmak için en iyisi.

## Ücretsiz Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Desteklenen Diller

-   **Arapça (ARA)**
-   **Çince (ZH)**
-   **Çek (CES)**
-   **Hırvat (HRV)**
-   **Hollandalı (NLD)**
-   **İngilizce (Eng)**
-   **Fransızca (from)**
-   **Almanca (Deu)**
-   **Değil (hin)**
-   **Macar (AM)**
-   **İtalyan (ITA)**
-   **Japonca (JPN)**
-   **Korece (COR)**
-   **Lehçe (POL)**
-   **Portekizce (POR)**
-   **Russian (rus)**
-   **İspanyolca (Spa)**
-   **Türk (Yuvarlak)**
-   **Vietnamca (VIE)**
-   [**Fairseq üzerinden +1100 dil**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Donanım Gereksinimleri

-   Minimum 4GB RAM, 8GB önerilir
-   Windows'ta çalışıyorsanız sanallaştırma etkinleştirildi (yalnızca Docker)
-   CPU, GPU (Önerilen), MPS (henüz optimize edilmemiş ve CPU'dan daha yavaş olabilir) uyumlu

> [!ÖNEMLİ]**Bir yükleme veya hata sorunu göndermeden önce Açılan ve Kapalı Sorunlar sekmesine dikkatle arama<br>Sorununuzun zaten mevcut olmadığından emin olmak için.**

> [!NOT]**Bölüm, paragraf, önsöz vb. Gibi herhangi bir standart yapısından yoksun olmak<br>Önce sesle dönüştürülmek istemediğiniz metinleri manuel olarak kaldırmalısınız.**

### Kurulum Talimatları

1.  **Klon repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Gradio Web Arayüzünü Başlatma

1.  **Ebook2audiobook çalıştırın**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Pencere**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Web uygulamasını aç**: Web uygulamasına erişmek ve e -kitapları dönüştürmek için terminalde sağlanan URL'yi tıklayın.
3.  **Halka açık bağlantı için**:`python app.py --share`(Tüm işletim sistemi)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!ÖNEMLİ]**Komut dosyası durdurulur ve tekrar çalıştırılırsa, Gradio GUI arayüzünüzü yenilemeniz gerekir<br>Web sayfasının yeni bağlantı soketine yeniden bağlanmasına izin vermek için.**

### Temel Kullanım

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Pencere**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Book]**: E -kitap dosyanıza giden yol.
-   **[--ses]**: Ses klonlama dosyası yolu (isteğe bağlı).
-   **[--dil]**: ISO-639-3'te dil kodu (yani: İtalyan için ita, İngilizce için Eng, Almanca için Deu ...).<br>Varsayılan dil ENG'dir ve --lib/lang.py'de ayarlanan varsayılan dil için isteğe bağlıdır.<br>ISO-639-1 2 harf kodları da desteklenir.

### Özel Model Zip Yükleme Örneği

(Zorunlu model dosyalarını içeren bir .zip dosyası olmalıdır. XTTS örneği: config.json, model.pth, vocab.json ve ref.wav)

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Pencere**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;custy_model_path>**: Yol`model_name.zip`dosya,
        (TTS motoruna göre) tüm zorunlu dosyaları içermelidir<br>(Bkz. ./lib/models.py).

### Kullanılacak tüm parametrelerin listesi ile ayrıntılı kılavuz için

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Pencere**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Veya tüm işletim sistemleri için**
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

Not: Gradio/GUI modunda, çalışan bir dönüşümü iptal etmek için[X]e -kitap yükleme bileşeninden.

### Docker'ı kullanma

Ayrıca e -kitabı sesli kitap dönüştürücüsüne çalıştırmak için Docker'ı da kullanabilirsiniz. 
Bu yöntem, farklı ortamlarda tutarlılık sağlar ve kurulumu basitleştirir.

#### Docker kabını çalıştırma

Docker konteynerini çalıştırmak ve Gradio arabirimini başlatmak için aşağıdaki komutu kullanın:

\-Yalnızca CPU ile Run

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-GPU hızlandırma ile run (sadece nvidia uyumlu)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Docker konteynerinin oluşturulması

-   Docker görüntüsünü komutla oluşturabilirsiniz:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Bu komut 7860 bağlantı noktasında Gradio arayüzünü başlatacaktır. (Localhost: 7860)

-   Daha fazla seçenek için parametreyi ekleyin`--help`

## Docker Container Dosya Konumları

Tüm ebook2audiobooks, temel direklere sahip olacak`/home/user/app/`Örneğin:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker başsız rehber

Birincisi,

```bash
docker pull athomasson2/ebook2audiobook
```

-   Bunu çalıştırmadan önce, mevcut direğinizde "Giriş-Kol" adlı bir DIR oluşturmanız gerekir.
    hangi bağlantılı olacak, burası Docker görüntüsünün görmek için giriş dosyalarınızı koyabileceğiniz yerdir.

```bash
mkdir input-folder && mkdir Audiobooks
```

-   Aşağıdaki komutta takas**Your_input_file.txt**Girdi dosyanızın adıyla

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   Ve bu olmalı!
-   Çıktı sesli kitaplar, ayrıca bulunacak olan sesli kitap klasöründe bulunacaktır.
    Yerel direğinizde bu Docker komutunu çalıştırdınız

## Diğer parametreler için yardım komutunu almak için bu program bunu çalıştırabilirsiniz

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

Ve bu bunu çıkaracak[Ortaya Çıktıya Yardım Edin](#help-command-output)

### Docker Compose

Bu proje, yerel olarak çalıştırmak için Docker Compose'u kullanıyor. GPU desteğini etkinleştirebilir veya devre dışı bırakabilirsiniz 
Her ikisini de ayarlayarak`*gpu-enabled`veya`*gpu-disabled`içinde`docker-compose.yml`

#### Koşmak İçin Adımlar

1.  **Depoyu klonla**(Henüz yapmadıysanız):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **GPU desteğini ayarlayın (varsayılan olarak devre dışı bırakıldı)**GPU desteğini etkinleştirmek için değiştirin`docker-compose.yml`ve değişim`*gpu-disabled`ile`*gpu-enabled`
3.  **Hizmeti başlatın:**
    ```bash
    docker-compose up -d
    ```
4.  **Hizmete erişin:**Hizmet http&#x3A; // localhost: 7860 adresinden satışa sunulacak.

### Docker GUI arayüzü

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Bir GPU kiralamak

Çalışacak donanımınız yok mu yoksa bir GPU kiralamak mı istiyorsunuz?

#### Hugginface alanını çoğaltabilir ve saatte yaklaşık 0,40 $ karşılığında bir GPU kiralayabilirsiniz

[Huggingface uzay demosu](#huggingface-space-demo)

#### Veya Google Colab'ı ücretsiz kullanmayı deneyebilirsiniz!

(Google Colab ile uğraşmadığınızdan sonra zaman aşımı olacağını unutmayın)[Ücretsiz Google Colab](#free-google-colab)

## Ortak Docker sorunları

-   Docker, ince ayarlı modelleri indirmeye sıkışır.
    (Bu her bilgisayar için olmaz, ancak bazıları bu soruna giriyor gibi görünüyor)
    Sorunu çözmek için ilerleme çubuğunu devre dışı bırakma gibi görünüyor,
    Tartışıldığı gibi[#191'de burada](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Bu düzeltmeyi ekleme örneği`docker run`emretmek

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## İnce ayarlanmış TTS modelleri

Bu repo ile kendi XTTS modelinize kolayca ince ayar yapabilirsiniz[Xtts-Finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Bir GPU kiralamak istiyorsanız, bu Huggingface'yi de çoğaltabilirsiniz[Xtts-Finetune-Webui-Space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Eğitim verilerini kolayca gürlemek için kullanabileceğiniz bir alan da[denoise huggingface uzay](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### İnce ayarlanmış TTS koleksiyonu

Zaten ince ayarlanmış TTS modelleri koleksiyonumuzu bulmak için,
ziyaret etmek[Bu sarılma yüz bağlantısı](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Bir XTTS Özel Model için Ses Referansının Ses Klibi zorunludur:

## Demolar

**Yağmurlu Gün Sesi**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Desteklenen e -kitap formatları

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **En iyi sonuçlar**:`.epub`veya`.mobi`Otomatik bölüm tespiti için

## Çıktı

-   Yaratır`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Meta veri ve bölümlerle ./lib/conf.py dosyasında ayarlayın.
-   **Örnek**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Ortak Sorunlar:

-   CPU yavaş (sunucu SMP CPU'da daha iyi), NVIDIA GPU neredeyse gerçek zamanlı dönüşüm olabilir.[Bununla ilgili tartışma](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Daha hızlı çok dilli nesil için diğerlerimi öneririm[Piper-TTS kullanan proje](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)yerine
    (Yine de sıfır atış ses klonlaması yoktur ve Siri kalite sesleridir, ancak CPU'da çok daha hızlıdır).
-   "Bağımlılık sorunlarım var" - sadece docker'ı kullanın, tamamen kendi kendine içerdiği ve başsız bir modu var,
     eklemek`--help`Daha fazla bilgi için Docker Run komutunun sonundaki parametre.
-   "Kesik bir ses sorunu alıyorum!" - Lütfen bunun bir sorununu yapın,
     Her dili konuşmuyoruz ve cümle bölme mantığını ince ayarlamaları için kullanıcılardan tavsiye almaya ihtiyacımız var.

## Neyle yardıma ihtiyacım var! 🙌

## [Şeylerin tam listesi burada bulunabilir](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Uygun cümle bölme yöntemlerine yardımcı olmak için desteklenen dillerden herhangi birini konuşan kişilerden herhangi bir yardım
-   Potansiyel olarak birden fazla dil için ReadMe Kılavuzları Oluşturma (çünkü bildiğim tek dil İngilizce'dir 😔)

## Özel Teşekkürler

-   **Yemek TTS**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Kalibre**:[Kalibre web sitesi](https://calibre-ebook.com)
-   **Ffmpeg**:[Ffmpeg web sitesi](https://ffmpeg.org)
-   [@shakenBake15 daha iyi bölüm kaydetme yöntemi için](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Kodu görüntüleyebilirsiniz[Burada](legacy/v1.0).

## Sunucumuza katılın!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
