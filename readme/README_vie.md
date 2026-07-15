# 📚 ebook2audiobook (E2A)
Bộ chuyển đổi CPU/GPU từ sách điện tử sang sách nói với các chương và siêu dữ liệu<br/>
sử dụng các engine TTS tiên tiến và nhiều hơn nữa.<br/>
Hỗ trợ nhân bản giọng nói và 1158 ngôn ngữ!
> [!IMPORTANT]
**Công cụ này chỉ dành để sử dụng với các sách điện tử không có DRM và được mua hợp pháp.** <br>
Các tác giả không chịu trách nhiệm cho bất kỳ việc lạm dụng phần mềm này hay bất kỳ hậu quả pháp lý nào phát sinh. <br>
Hãy sử dụng công cụ này một cách có trách nhiệm và tuân thủ mọi luật hiện hành.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Cảm ơn bạn đã hỗ trợ các nhà phát triển ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Chạy cục bộ

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Chạy từ xa
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Giao diện đồ họa (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Nhấp để xem hình ảnh của GUI web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Bản demo

**Bản demo giọng mặc định mới**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Thêm bản demo</summary>

**Giọng ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Giọng ngày mưa**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Giọng Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Giọng David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Ví dụ**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Mục lục
- [ebook2audiobook](#-ebook2audiobook)
- [Tính năng](#features)
- [Giao diện đồ họa](#gui-interface)
- [Bản demo](#demos)
- [Ngôn ngữ được hỗ trợ](#supported-languages)
- [Yêu cầu tối thiểu](#hardware-requirements)
- [Cách dùng](#instructions)
  - [Chạy cục bộ](#instructions)
    - [Khởi chạy giao diện web Gradio](#instructions)
    - [Cách dùng Headless cơ bản](#basic-usage)
    - [Cách dùng mô hình XTTS tùy chỉnh ở chế độ Headless](#example-of-custom-model-zip-upload)
    - [Đầu ra lệnh trợ giúp](#help-command-output)
  - [Chạy từ xa](#run-remotely)
  - [Docker](#docker)
    - [Các bước để chạy](#docker)
  
- [Cloned Voices](#cloned-voices)
- [Các mô hình TTS đã tinh chỉnh](#fine-tuned-tts-models)
  - [Bộ sưu tập các mô hình TTS đã tinh chỉnh](#fine-tuned-tts-collection)
  - [Huấn luyện XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Định dạng sách điện tử được hỗ trợ](#supported-ebook-formats)
- [Định dạng đầu ra](#output-and-process-formats)
- [Quay lại phiên bản cũ hơn](#reverting-to-older-versions)
- [Các vấn đề thường gặp](#common-issues)
- [Lời cảm ơn đặc biệt](#special-thanks)
- [Mục lục](#table-of-contents)


## Tính năng
- 🔧 **Các engine TTS được hỗ trợ**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Chuyển đổi nhiều định dạng tệp**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Vùng văn bản** để chuyển trực tiếp một đoạn văn bản ngắn thành âm thanh
- 🔍 **Quét OCR** cho các tệp có trang văn bản dưới dạng hình ảnh
- 🔊 **Chuyển văn bản thành giọng nói chất lượng cao**, từ gần thời gian thực đến giọng gần như thật
- 🗣️ **Nhân bản giọng nói tùy chọn** bằng tệp giọng nói của riêng bạn
- 🌐 **Hỗ trợ 1158 ngôn ngữ** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Thân thiện với tài nguyên thấp** — chạy trên **2 GB RAM / 1 GB VRAM (tối thiểu)**
- 🎵 **Định dạng đầu ra sách nói**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Hỗ trợ thẻ SML** — kiểm soát chi tiết các điểm ngắt, khoảng dừng, chuyển giọng và hơn thế nữa ([see below](#sml-tags-available))
- 🧩 **Mô hình tùy chỉnh tùy chọn** bằng mô hình do bạn tự huấn luyện (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Các mô hình thiết lập sẵn đã tinh chỉnh** được huấn luyện bởi Nhóm E2A<br/>
     <i>(Liên hệ với chúng tôi nếu bạn cần thêm các mô hình đã tinh chỉnh, hoặc nếu bạn muốn chia sẻ mô hình của mình vào danh sách thiết lập sẵn chính thức)</i>


##  Yêu cầu phần cứng
- 2 GB RAM tối thiểu, 8 GB khuyến nghị.
- 1 GB VRAM tối thiểu, 4 GB khuyến nghị.
- Bật ảo hóa nếu chạy trên Windows (chỉ Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Các engine TTS hiện đại rất chậm trên CPU, vì vậy hãy dùng TTS chất lượng thấp hơn như YourTTS, Tacotron2, v.v.</i>

## Ngôn ngữ được hỗ trợ
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 ngôn ngữ và phương ngữ tại đây**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Định dạng sách điện tử được hỗ trợ
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Kết quả tốt nhất**: `.epub` hoặc `.mobi` để tự động phát hiện chương

## Định dạng đầu ra và xử lý
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Định dạng xử lý có thể được thay đổi trong lib/conf.py

## Các thẻ SML có sẵn
- `[break]` — khoảng lặng (phạm vi ngẫu nhiên **0.3–0.6 sec.**)
- `[pause]` — khoảng lặng (phạm vi ngẫu nhiên **1.0–1.6 sec.**)
- `[pause:N]` — khoảng dừng cố định (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — chuyển giọng từ giọng mặc định hoặc giọng được chọn từ GUI/CLI

**Hãy xem repo khác của chúng tôi dành riêng cho việc thêm SML tự động vào sách điện tử của bạn -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Trước khi đăng vấn đề cài đặt hoặc lỗi, hãy tìm kiếm cẩn thận trong tab các vấn đề đang mở và đã đóng<br>
để chắc chắn rằng vấn đề của bạn chưa tồn tại.**

>[!NOTE]
**Định dạng EPUB thiếu bất kỳ cấu trúc chuẩn nào như thế nào là một chương, đoạn văn, lời nói đầu, v.v.<br>
Vì vậy, trước tiên bạn nên xóa thủ công bất kỳ văn bản nào bạn không muốn chuyển thành âm thanh.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Cài đặt / Chạy ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Trình khởi chạy Mac**  
     Nhấp đúp vào `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Lưu ý cho người dùng Windows: scoop được cài đặt để cài các chương trình còn thiếu mà không cần quyền quản trị viên.</i>
   
1. **Mở ứng dụng Web**: Nhấp vào URL được cung cấp trong terminal để truy cập ứng dụng web và chuyển đổi sách điện tử. `http://localhost:7860/`
2. **Để có liên kết công khai**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Nếu tập lệnh bị dừng và chạy lại, bạn cần làm mới giao diện GUI Gradio của mình<br>
để trang web kết nối lại với socket kết nối mới.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Đường dẫn đến tệp sách điện tử của bạn
  - **[--voice]**: Đường dẫn tệp nhân bản giọng nói (tùy chọn)
  - **[--language]**: Mã ngôn ngữ ở ISO-639-3 (ví dụ: ita cho tiếng Ý, eng cho tiếng Anh, deu cho tiếng Đức...).<br>
    Ngôn ngữ mặc định là eng và --language là tùy chọn cho ngôn ngữ mặc định được đặt trong ./lib/lang.py.<br>
    Các mã ISO-639-1 gồm 2 chữ cái cũng được hỗ trợ.


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
     
- **<custom_model_path>**: Đường dẫn đến tệp `model_name.zip`,
      tệp này phải chứa (tùy theo engine tts) tất cả các tệp bắt buộc<br>
      (xem ./lib/models.py).

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

LƯU Ý: ở chế độ gradio/gui, để hủy một quá trình chuyển đổi đang chạy, chỉ cần nhấp vào [X] trên thành phần tải lên sách điện tử.
MẸO: nếu cần thêm khoảng dừng, hãy thêm '[pause:3]' cho 3 giây, v.v.

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

## Giọng nói được nhân bản
Bạn có thể tải lên bất kỳ âm thanh giọng nói nào ở bất kỳ định dạng âm thanh nào được hỗ trợ, thời lượng lý tưởng là khoảng 1 đến 5 phút.
Không có vấn đề gì nếu bản ghi âm có nền ồn ào hoặc phát nhạc trên đó — E2A sẽ làm sạch giọng nói cho bạn.

Danh sách giọng nói nhân bản tích hợp chủ yếu bằng tiếng Anh. Nếu bạn cần giọng nói bằng các ngôn ngữ khác để được chính thức
đã thêm vào danh sách, vui lòng liên hệ với chúng tôi và chúng tôi sẽ thêm chúng sau khi đánh giá.

## Các mô hình TTS đã tinh chỉnh (fine-tuned)
#### Tinh chỉnh mô hình XTTSv2 của riêng bạn

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Khử nhiễu dữ liệu huấn luyện

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Bộ sưu tập các mô hình TTS đã tinh chỉnh

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Đối với mô hình tùy chỉnh XTTSv2, một đoạn âm thanh tham chiếu của giọng nói là bắt buộc:

## Tùy chỉnh Ebook2Audiobook của riêng bạn
Bạn được tự do sửa đổi libs/conf.py để thêm hoặc bớt các cài đặt mà bạn muốn. Nếu định làm vậy, chỉ cần tạo
một bản sao của conf.py gốc để mỗi lần cập nhật ebook2audiobook bạn sẽ sao lưu conf.py đã sửa đổi của mình và đặt
lại bản gốc. Bạn phải lên kế hoạch cho quy trình tương tự với models.py. Nếu bạn muốn biến mô hình tùy chỉnh của riêng mình
thành một mô hình ebook2audiobook đã tinh chỉnh chính thức, vui lòng liên hệ với chúng tôi và chúng tôi sẽ thêm nó vào danh sách thiết lập sẵn.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Các vấn đề thường gặp:
- GPU NVIDIA/ROCm/XPU/MPS của tôi không được phát hiện?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU chậm (tốt hơn trên CPU smp máy chủ) trong khi GPU có thể chuyển đổi gần như thời gian thực.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Tuy nhiên nó không có nhân bản giọng nói zero-shot, và là giọng chất lượng Siri, nhưng nhanh hơn nhiều trên cpu).
- "Tôi gặp vấn đề về phụ thuộc" - Chỉ cần dùng docker, nó hoàn toàn độc lập và có chế độ headless,
   thêm tham số `--help` ở cuối lệnh docker run để biết thêm thông tin.
- "Tôi gặp vấn đề âm thanh bị cắt cụt!" - VUI LÒNG TẠO MỘT ISSUE VỀ VIỆC NÀY,
   chúng tôi không nói được mọi ngôn ngữ và cần lời khuyên từ người dùng để tinh chỉnh logic chia câu.😊

## ***** LỘ TRÌNH *****
- Tất cả các Tính năng đều mở cho Đóng góp công khai ⭐
- Mọi sự giúp đỡ từ những người nói bất kỳ ngôn ngữ nào được hỗ trợ để giúp chúng tôi cải thiện các mô hình ⭐
- [x] Xem trước các Khối/Chương trước khi bắt đầu chuyển đổi
- [ ] Chỉnh sửa theo từng câu đã chuyển đổi để thay đổi văn bản chính xác
- [x] Tích hợp thẻ SML cho giọng nói, khoảng dừng, điểm ngắt và nhiều thay đổi hơn 
- [x] Thông tin tham số -h -help bằng các ngôn ngữ khác nhau
- [x] Quét OCR cho PDF / JPG / BMP / PNG / TIFF
- [x] Thư mục Notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Làm cho việc chia văn bản tiếng Trung không cắt từ và cải thiện thời gian dừng [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Kaggle Notebook
- [x] Google Colab Notebook
- [ ] Tích hợp Audiobookshelf
- [ ] [Tạo một ứng dụng IOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Tạo một ứng dụng android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)

#### Tùy chọn bổ sung
- [x] Tùy chọn dịch sách điện tử
- [x] Các lựa chọn định dạng đầu ra
- [x] Thư mục sách điện tử theo lô
- [x] Chuyển đổi đa xử lý
- [x] Chuyển đổi thư mục sách điện tử theo lô
- [x] Phát hiện thiết bị GPU
- [x] Khử nhiễu bất kỳ âm thanh tham chiếu nào cho việc tải lên nhân bản giọng nói,
- [x] Tải lên mô hình tùy chỉnh (hiện chỉ XTTSv2. thêm theo yêu cầu)
- [ ] Thêm mô hình ngôn ngữ tiếng Bồ Đào Nha châu Âu cho ít nhất xttsv2, fairseq, vits, piper (hoan nghênh sự giúp đỡ)
- [ ] Thêm mô hình ngôn ngữ tiếng Sindhi cho ít nhất xttsv2, fairseq, vits, piper (hoan nghênh sự giúp đỡ)

#### Động cơ TTS
- [x] XTTSv2
- [x] Vỏ cây
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Huyền Vũ
- [x] GlowTTS
- [x] Piper.
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] tiếng cá (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Siêu âm (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Kiểu-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Dịch Readme
- [x] Tiếng Ả Rập (ara)
- [x] Tiếng Trung (zho)
- [x] English (eng)
- [x] Tây Ban Nha (spa)
- [x] Tiếng Pháp (fra)
- [x] Tiếng Đức (deu)
- [x] Tiếng Ý (ita)
- [x] Tiếng Bồ Đào Nha (por)
- [x] Tiếng Ba Lan (pol)
- [x] Tiếng Thổ Nhĩ Kỳ (tur)
- [x] Tiếng Nga (rus)
- [x] Tiếng Hà Lan (nld)
- [x] Tiếng Séc (ces)
- [x] Tiếng Nhật (jpn)
- [x] Tiếng Hindi (hin)
- [x] Tiếng Bengali (ben)
- [x] Hungarian (hun)
- [x] Tiếng Hàn (kor)
- [x] Vietnamese (VIE)
- [x] Tiếng Thụy Điển (swe)
- [x] Tiếng Ba Tư (FAS)
- [x] Yoruba (yor)
- [x] Tiếng Swahili (swa)
- [x] Tiếng Indonesia (ind)
- [x] Tiếng Slovak (slk)
- [x] Tiếng Croatia (hrv)

#### 🐍 Khả năng tương thích hệ điều hành
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Phần thừa thãi để huấn luyện mô hình và những thứ tương tự (tất cả các mô hình Coqui-tts được hỗ trợ và piper-tts trong một lệnh đơn giản) 
- Để biết thông tin về việc này @DrewThomasson, anh ấy hiện đang phát triển nó, [repo đang trong quá trình thực hiện tại đây](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Tạo một gui huấn luyện dễ sử dụng cho tất cả các mô hình coqui-tts trong các công thức huấn luyện định dạng ljspeech [tại đây từ coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Thông tin chuẩn hóa mã Python cho người đóng góp
- không có dòng trống giữa mã, ngoại trừ giữa các hàm và lớp.
- dấu nháy đơn được dùng cho tất cả khóa ngoại trừ dict() và json. dict['key'] luôn được gọi bằng dấu nháy đơn
- thụt lề 4 dấu cách, hoàn toàn không dùng tab
- định kiểu nghiêm ngặt cho tất cả các hàm cũng như khai báo đối số và giá trị trả về của chúng
- không có dấu cách giữa đối số và định kiểu của nó, không có dấu cách giữa hàm, "->" và giá trị trả về

Ví dụ:

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

## Cần quyên góp phần cứng cho việc thử nghiệm beta
Chúng tôi chấp nhận bất kỳ loại phần cứng nào để thử nghiệm quá trình phát triển của mình, chẳng hạn như:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson nếu bạn muốn giúp đỡ bằng bất kỳ cách nào! 😃
<!--
## Bạn có cần thuê GPU để tăng cường dịch vụ từ chúng tôi không?
- Một cuộc thăm dò đang mở tại đây https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Lời cảm ơn đặc biệt
Đối với tất cả những người đóng góp tài chính và mã, mỗi đóng góp và đề xuất giúp cải thiện chất lượng của E2A.