Ebook2AudioBook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
Bộ chuyển đổi CPU/GPU từ sách điện tử sang audiobook với các chương và siêu dữ liệu <br/>
Sử dụng Calibre, FFMPEG, XTTSV2, Fairseq và nhiều hơn nữa. Hỗ trợ nhân bản giọng nói và ngôn ngữ +1110! [!QUAN TRỌNG]
** Công cụ này chỉ dành cho việc sử dụng với Sách điện tử không phải DRM, có được hợp pháp. ** <br>
Các tác giả không chịu trách nhiệm cho bất kỳ lạm dụng phần mềm này hoặc bất kỳ hậu quả pháp lý nào. <br>
Sử dụng công cụ này có trách nhiệm và phù hợp với tất cả các luật hiện hành. [!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! .com/Athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [demo_web_gui] (tài sản/demo_web_gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ARA [الع (tiếng Ả Rập)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
Zho [中文 (tiếng Trung)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
Swe [svenska (Thụy Điển)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فار (tiếng Ba Tư)] (./ readme/readme_fa.md)


## Table of Contents
[Ebook2Audiobook] (#-Ebook2Audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Tính năng] (#tính năng)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Giao diện GUI Docker] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Huggingface Space Demo] (#HuggingFace-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Google colab miễn phí] (#miễn phí google-colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Bản trình diễn âm thanh được tạo sẵn] (#Demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Ngôn ngữ được hỗ trợ] (#Ngôn ngữ được hỗ trợ)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Yêu cầu] (#Phần cứng-Quarnements)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Hướng dẫn cài đặt] (#Cài đặt-Thông báo)
- [Output](#output)
- [Common Issues](#common-issues)
[Sử dụng] (#Launching-Gradio-Web-Carterface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
.


[Sử dụng không đầu cơ bản] (#cơ bản-sử dụng)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Sử dụng mô hình XTTS tùy chỉnh không đầu] (#Ví dụ về-Custom-Model-Zip-Upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Cho thuê GPU] (#Cho thuê-A-GPU)


[Trợ giúp đầu ra lệnh] (#Trợ giúp-ra lệnh-đầu ra)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Các mô hình TTS được điều chỉnh tốt] (#FINED-TUNED-TTS-MODELS)


[Đối với bộ sưu tập các mô hình TTS được điều chỉnh tốt] (#tinh chỉnh-tts-collection)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Running-the-Docker-Container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Building-the-Docker-Container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#Docker-Compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Hướng dẫn không đầu Docker] (#Docker không có đầu-Hướng dẫn)
- **Japanese (jpn)**
- **Korean (kor)**
[Vị trí tệp container Docker] (#Docker-Container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Các vấn đề thông thường của Docker] (#Thocker-docker-vấn đề)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Định dạng ebook được hỗ trợ] (#-Sách được hỗ trợ)


[Đầu ra] (#đầu ra)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Các vấn đề phổ biến] (#Phát hành chung)


[Cảm ơn đặc biệt] (#đặc biệt-cảm ơn)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Đặc trưng
```bash
Chuyển đổi sách điện tử thành định dạng văn bản với tầm cỡ. Chia sách điện tử thành các chương cho âm thanh có tổ chức. Text-to-Speech chất lượng cao với [Coqui XTTSV2] (https://huggingface.co/coqui/XTTS-v2) và [Fairseq] (https://github.com/facebookResearch/fairseq/tree/main/ Ví dụ/MMS) (và nhiều hơn nữa). 🗣 Nhân bản bằng giọng nói tùy chọn với tệp giọng nói của riêng bạn. Hỗ trợ +1110 Ngôn ngữ (tiếng Anh theo mặc định). [Danh sách các ngôn ngữ được hỗ trợ] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-lango.html)
```

Được thiết kế để chạy trên RAM 4GB. [HuggingFace Space Demo] (https://huggingface.co/spaces/drewthomasson/ ebook2audiobook)
1. **Run ebook2audiobook**:
[! /ebook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Không gian HuggingFace đang chạy trên tầng CPU miễn phí, vì vậy hãy mong đợi rất chậm hoặc thời gian chờ LOL, chỉ cần không cho nó các tệp khổng lồ là tất cả
   - **Windows**
     ```bash
Tốt nhất để sao chép không gian hoặc chạy cục bộ. Google colab miễn phí
     ```
[! [Google Colab miễn phí] (https://colab.research.google.com/assets/colab-badge.svg)] Main/Notebooks/colab_eBook2Audiobook.ipynb)
3. **For Public Link**:
Ngôn ngữ được hỗ trợ
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Tiếng Ả Rập (ARA) **

> [!IMPORTANT]
** Trung Quốc (Zho) **
to let the web page reconnect to the new connection socket.**

** Séc (CES) **
   - **Linux/MacOS**:
     ```bash
** Croatia (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Hà Lan (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Tiếng Anh (Tiếng Anh) **
     ```
     
** Pháp (fra) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Đức (deu) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Hungary (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** Ý (ita) **
     ```
   - **Windows**
** Nhật Bản (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Hàn Quốc (KOR) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Ba Lan (Pol) **


** Bồ Đào Nha (por) **
   - **Linux/MacOS**
     ```bash
** Nga (Rus) **
     ```
   - **Windows**
** Tây Ban Nha (spa) **
     .\ebook2audiobook.cmd --help
     ```
** Thổ Nhĩ Kỳ (Tur) **
    ```python
     app.py --help
** Việt Nam (VIE) **

<a id="help-command-output"></a>
[** +1100 Ngôn ngữ qua Fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-lango.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Yêu cầu phần cứng
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
RAM tối thiểu 4GB, được đề xuất 8GB
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualization được bật nếu chạy trên Windows (chỉ có Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (được đề xuất), MPS (chưa được tối ưu hóa và có thể chậm hơn CPU) tương thích

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Trước khi đăng cẩn thận việc tìm kiếm lỗi hoặc lỗi về lỗi cho tab các vấn đề đã mở và đóng <br>
Để chắc chắn rằng vấn đề của bạn chưa tồn tại. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Thiếu bất kỳ cấu trúc tiêu chuẩn nào như chương, đoạn văn, lời nói đầu, v.v. <br>
Trước tiên bạn nên xóa thủ công bất kỳ văn bản nào bạn không muốn được chuyển đổi trong âm thanh. **

Hướng dẫn cài đặt

** Clone repo **
  --headless            Run the script in headless mode
Khởi chạy giao diện web Gradio
  --ebooks_dir EBOOKS_DIR
** Chạy ebook2audiobook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Mở ứng dụng web **: Nhấp vào URL được cung cấp trong thiết bị đầu cuối để truy cập ứng dụng web và chuyển đổi sách điện tử. ** Đối với liên kết công khai **:
`Ứng dụng Python.py --Share` (Tất cả HĐH)
`.
`ebook2audiobook.cmd --Share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!QUAN TRỌNG]
** Nếu tập lệnh được dừng và chạy lại, bạn cần phải làm mới giao diện gui Gradio của mình <br>
Để cho trang web kết nối lại với ổ cắm kết nối mới. **
                        (Optional) Fine tuned model path. Default is builtin model.
Cách sử dụng cơ bản
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-ebook] **: Đường dẫn đến tệp ebook của bạn. ** [-Voice] **: Đường dẫn tệp nhân bản bằng giọng nói (tùy chọn). ** [-Ngôn ngữ] **: Mã ngôn ngữ trong ISO-639-3 (tức là: Ita cho tiếng Ý, Eng cho tiếng Anh, Deu cho tiếng Đức ...). <br>
Ngôn ngữ mặc định là Eng và -Ngôn ngữ là tùy chọn cho ngôn ngữ mặc định được đặt trong ./lib/lang.py. <br>
Mã chữ ISO-639-1 2 cũng được hỗ trợ. Ví dụ về tải lên zip mô hình tùy chỉnh
  --repetition_penalty REPETITION_PENALTY
.
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** M
    trong đó phải chứa (theo công cụ TTS) tất cả các tệp bắt buộc <br>
    (Xem ./lib/models.py). Đối với hướng dẫn chi tiết với danh sách tất cả các tham số để sử dụng
  --output_dir OUTPUT_DIR
** Linux/macOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** hoặc cho tất cả hệ điều hành **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "Trợ giúp-command-plut"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Lưu ý: Trong chế độ gradio/GUI, để hủy chuyển đổi đang chạy, chỉ cần nhấp vào [x] từ thành phần tải lên ebook. Sử dụng Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Bạn cũng có thể sử dụng Docker để chạy Sách điện tử sang Audiobook Converter. Phương pháp này đảm bảo tính nhất quán trên các môi trường khác nhau và đơn giản hóa thiết lập. Chạy container docker

Để chạy container Docker và khởi động giao diện Gradio, hãy sử dụng lệnh sau:

### Using Docker
-Run chỉ với CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Xây dựng container docker

Bạn có thể xây dựng hình ảnh Docker bằng lệnh:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Lệnh này sẽ bắt đầu giao diện Gradio trên cổng 7860. (LocalHost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Để biết thêm tùy chọn, hãy thêm tham số `--Help`
```


Tất cả Ebook2AudioBooks sẽ có cơ sở của `/home/user/app/`
Ví dụ:
`tmp` =`/home/user/app/tmp`
`audiobooks` =`/home/user/app/audiobooks`
```
Hướng dẫn không đầu docker
- For more options add the parameter `--help`


## Docker container file locations
Trước khi bạn chạy điều này, bạn cần tạo một dir có tên "đầu vào đầu vào" trong DIR hiện tại của bạn
sẽ được liên kết, đây là nơi bạn có thể đặt các tệp đầu vào của mình cho hình ảnh Docker để xem
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
Và đó nên là nó! Audiobook đầu ra sẽ được tìm thấy trong thư mục audiobook cũng sẽ được định vị
Trong địa phương của bạn, bạn đã chạy lệnh docker này trong
docker pull athomasson2/ebook2audiobook
Để nhận lệnh trợ giúp cho các tham số khác, chương trình này có bạn có thể chạy cái này
- Before you do run this you need to create a dir named "input-folder" in your current dir
và điều đó sẽ xuất hiện điều này 
[Trợ giúp đầu ra lệnh] (#Trợ giúp-ra lệnh-đầu ra)
mkdir input-folder && mkdir Audiobooks
Docker sáng tác
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Dự án này sử dụng Docker Compose để chạy cục bộ. Bạn có thể bật hoặc tắt hỗ trợ GPU 
Bằng cách cài đặt `*gpu-hỗ trợ` hoặc`*gpu-disables` trong `docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Các bước để chạy
    athomasson2/ebook2audiobook \
** nhân bản kho lưu trữ ** (nếu bạn chưa có):
```
- And that should be it! 
** Đặt hỗ trợ GPU (đã tắt theo mặc định) **
Để kích hoạt hỗ trợ GPU, hãy sửa đổi `docker-compose.yml` và thay đổi`*gpu-deMable` thành `*gpu-kích hoạt`


** Bắt đầu dịch vụ: **

```bash
** Truy cập dịch vụ: **

```
! [demo_web_gui] (tài sản/demo_web_gui.gif)
[Help command output](#help-command-output)


Không có phần cứng để chạy nó hoặc bạn muốn thuê GPU? Bạn có thể nhân đôi không gian Hugginface và thuê GPU với giá khoảng 0,40 đô la một giờ
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Huggingface Space Demo] (#HuggingFace-Space-Demo)


[Google colab miễn phí] (#miễn phí google-colab)
1. **Clone the Repository** (if you haven't already):
Các vấn đề chung của Docker
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker bị mắc kẹt tải xuống các mô hình tinh chỉnh. (Điều này không xảy ra cho mọi máy tính nhưng một số người dường như gặp phải vấn đề này)
Vô hiệu hóa thanh tiến trình xuất hiện để khắc phục sự cố,
Như đã thảo luận [ở đây trong #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Ví dụ về việc thêm bản sửa lỗi này vào lệnh `docker chạy`
3. **Start the service:**
Các mô hình TTS được điều chỉnh tốt
    docker-compose up -d
Bạn có thể tinh chỉnh mô hình XTTS của riêng bạn một cách dễ dàng với repo này
[XTTS-Finetune-Webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[
![demo_web_gui](assets/demo_web_gui.gif)

Một không gian bạn có thể sử dụng để không có gì dễ dàng nhận được dữ liệu đào tạo
[Denise-HuggingFace-Space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Bộ sưu tập TTS được điều chỉnh tốt
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Để tìm bộ sưu tập các mô hình TTS đã được tinh chỉnh của chúng tôi,


## Renting a GPU
Bản trình diễn
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Giọng nói ngày mưa **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** giọng nói của David Attenborough **


Các định dạng ebook được hỗ trợ
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,`.
`.pdb`,` .fb2`, `.Odt`,` .cbr`, `.cbz`,`.
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Kết quả tốt nhất **: `.epub` hoặc` .mobi` để phát hiện chương tự động
    -p 7860:7860 athomasson2/ebook2audiobook
Đầu ra


! [Ví dụ] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_app.
You can fine-tune your own xtts model easily with this repo
Các vấn đề phổ biến:

CPU chậm (tốt hơn trên máy chủ SMP CPU) trong khi GPU NVIDIA có thể có chuyển đổi gần như thời gian thực. .
Đối với thế hệ đa ngôn ngữ nhanh hơn, tôi sẽ đề nghị người khác của tôi

. "Tôi đang gặp vấn đề phụ thuộc" - chỉ cần sử dụng Docker, nó hoàn toàn khép kín và có chế độ không đầu,
 Thêm tham số `--Help` ở cuối lệnh docker chạy để biết thêm thông tin. "Tôi đang gặp sự cố âm thanh bị cắt ngắn!" - Vui lòng đưa ra vấn đề về vấn đề này,

### Fine Tuned TTS Collection
Những gì tôi cần giúp đỡ! 🙌
[Danh sách đầy đủ những điều có thể được tìm thấy ở đây] (https://github.com/drewthomasson/ ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Có khả năng tạo hướng dẫn readme cho nhiều ngôn ngữ (vì ngôn ngữ duy nhất tôi biết là tiếng Anh)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


*.
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [trang web ffmpeg] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/V1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Bạn có thể xem mã [tại đây] (Legacy/V1.0). Tham gia máy chủ của chúng tôi! [!