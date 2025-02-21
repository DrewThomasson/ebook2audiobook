# Ebook2AudioBook

Bộ chuyển đổi CPU/GPU từ sách điện tử sang audiobook với các chương và siêu dữ liệu<br/>Sử dụng Calibre, FFMPEG, XTTSV2, Fairseq và nhiều hơn nữa. Hỗ trợ nhân bản giọng nói và ngôn ngữ +1110!

> [!QUAN TRỌNG]**Công cụ này được sử dụng để sử dụng với các ebook không phải DRM, chỉ có được hợp pháp.**<br>Các tác giả không chịu trách nhiệm cho bất kỳ lạm dụng phần mềm này hoặc bất kỳ hậu quả pháp lý nào.<br>Sử dụng công cụ này có trách nhiệm và phù hợp với tất cả các luật hiện hành.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Cảm ơn hỗ trợ các nhà phát triển Ebook2AudioBook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Giao diện GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Chúng tôi mua[Tiếng Ả Rập (tiếng Ả Rập)](./readme/README_AR.md)
-   Zho[Trung Quốc](./readme/README_CN.md)
-   a \`a[Tiếng Anh](README.md)
-   Swe[Thụy Điển (Thụy Điển)](./readme/README_SWE.md)
-   fas[Ba Tư (Ba Tư)](./readme/README_FA.md)
-   cô ấy[Ý (Ý)](./readme/README.it.md)

## Mục lục

-   [Ebook2Audiobook](#-ebook2audiobook)
-   [Đặc trưng](#features)
-   [Giao diện docker GUI](#docker-gui-interface)
-   [Huggingface Space Demo](#huggingface-space-demo)
-   [Google colab miễn phí](#free-google-colab)
-   [Bản trình diễn âm thanh được tạo sẵn](#demos)
-   [Ngôn ngữ được hỗ trợ](#supported-languages)
-   [Yêu cầu](#hardware-requirements)
-   [Hướng dẫn cài đặt](#installation-instructions)
-   [Cách sử dụng](#launching-gradio-web-interface)
    -   [Khởi chạy giao diện web Gradio](#launching-gradio-web-interface)
    -   [Sử dụng không đầu cơ bản](#basic--usage)
    -   [Sử dụng mô hình XTTS không đầu không đầu](#example-of-custom-model-zip-upload)
    -   [Thuê GPU](#renting-a-gpu)
    -   [Giúp lệnh đầu ra](#help-command-output)
-   [Các mô hình TTS được điều chỉnh tốt](#fine-tuned-tts-models)
    -   [Để thu thập các mô hình TTS tinh chỉnh](#fine-tuned-tts-collection)
-   [Sử dụng Docker](#using-docker)
    -   [Docker chạy](#running-the-docker-container)
    -   [Docker xây dựng](#building-the-docker-container)
    -   [Docker sáng tác](#docker-compose)
    -   [Hướng dẫn không đầu docker](#docker-headless-guide)
    -   [Vị trí tệp container docker](#docker-container-file-locations)
    -   [Các vấn đề chung của Docker](#common-docker-issues)
-   [Các định dạng ebook được hỗ trợ](#supported-ebook-formats)
-   [Đầu ra](#output)
-   [Các vấn đề phổ biến](#common-issues)
-   [Cảm ơn đặc biệt](#special-thanks)
-   [Tham gia máy chủ của chúng tôi!](#join-our--server)
-   [Di sản](#legacy-v10)
-   [Mục lục](#table-of-contents)

## Đặc trưng

-   Chuyển đổi sách điện tử thành định dạng văn bản với tầm cỡ.
-   Chia sách điện tử thành các chương cho âm thanh có tổ chức.
-   🎙 Text-to-Speech chất lượng cao với[Coqui XTTSV2](https://huggingface.co/coqui/XTTS-v2)Và[FAIRSEQ](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(và nhiều hơn nữa).
-   🗣 Nhân bản bằng giọng nói tùy chọn với tệp giọng nói của riêng bạn.
-   Hỗ trợ +1110 Ngôn ngữ (tiếng Anh theo mặc định).[Danh sách các ngôn ngữ được hỗ trợ](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   Được thiết kế để chạy trên RAM 4GB.

## [Huggingface Space Demo](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Không gian HuggingFace đang chạy trên tầng CPU miễn phí, vì vậy hãy mong đợi rất chậm hoặc thời gian chờ lol, chỉ cần không cho nó các tệp khổng lồ là tất cả
-   Tốt nhất để sao chép không gian hoặc chạy cục bộ.

## Google colab miễn phí

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Ngôn ngữ được hỗ trợ

-   **Tiếng Ả Rập (ARA)**
-   **Trung Quốc (ZH)**
-   **Séc (CES)**
-   **Croatia (HRV)**
-   **Hà Lan (NLD)**
-   **Tiếng Anh (Tiếng Anh)**
-   **Tiếng Pháp (từ)**
-   **Đức (Deu)**
-   **Không (hin)**
-   **Hungary (AM)**
-   **Ý (ITA)**
-   **Nhật Bản (JPN)**
-   **Hàn Quốc (COR)**
-   **Ba Lan (Pol)**
-   **Tiếng Bồ Đào Nha (por)**
-   **Nga (RUS)**
-   **Tây Ban Nha (Spa)**
-   **Thổ Nhĩ Kỳ (tròn)**
-   **Việt Nam (VIE)**
-   [**+1100 ngôn ngữ qua fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Yêu cầu phần cứng

-   RAM tối thiểu 4GB, được đề xuất 8GB
-   Virtualization được bật nếu chạy trên Windows (chỉ có Docker)
-   CPU, GPU (được đề xuất), MPS (chưa được tối ưu hóa và có thể chậm hơn CPU) tương thích

> [!QUAN TRỌNG]**Trước đây để đăng cẩn thận việc tìm kiếm lỗi hoặc lỗi về việc tìm kiếm lỗi cho tab các vấn đề đã mở và đóng<br>Để chắc chắn rằng vấn đề của bạn chưa tồn tại.**

> [!GHI CHÚ]**Thiếu bất kỳ cấu trúc tiêu chuẩn nào như chương, đoạn văn, lời nói đầu, v.v.<br>Trước tiên bạn nên xóa thủ công bất kỳ văn bản nào bạn không muốn được chuyển đổi trong âm thanh.**

### Hướng dẫn cài đặt

1.  **Clone repo**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Khởi chạy giao diện web Gradio

1.  **Chạy ebook2audiobook**:
    -   **Linux/macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Windows**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Mở ứng dụng web**: Nhấp vào URL được cung cấp trong thiết bị đầu cuối để truy cập ứng dụng web và chuyển đổi ebook.
3.  **Cho liên kết công khai**:`python app.py --share`(Tất cả hệ điều hành)`./ebook2audiobook.sh --share`(Linux/macOS)`ebook2audiobook.cmd --share`(Windows)

> [!QUAN TRỌNG]**Nếu tập lệnh được dừng và chạy lại, bạn cần làm mới giao diện gui gui<br>Để cho trang web kết nối lại với ổ cắm kết nối mới.**

### Cách sử dụng cơ bản

-   **Linux/macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--ebook]**: Đường dẫn đến tệp ebook của bạn.
-   **[--tiếng nói]**: Đường dẫn tệp nhân bản giọng nói (tùy chọn).
-   **[--ngôn ngữ]**: Mã ngôn ngữ trong ISO-639-3 (tức là: ITA cho tiếng Ý, Eng cho tiếng Anh, DEU cho tiếng Đức ...).<br>Ngôn ngữ mặc định là Eng và -Ngôn ngữ là tùy chọn cho ngôn ngữ mặc định được đặt trong ./lib/lang.py.<br>Mã chữ ISO-639-1 2 cũng được hỗ trợ.

### Ví dụ về tải lên zip mô hình tùy chỉnh

.

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;Custom_model_path>**: Path to `model_name.zip`tài liệu,
        phải chứa (theo công cụ TTS) tất cả các tệp bắt buộc<br>(Xem ./lib/models.py).

### Đối với hướng dẫn chi tiết với danh sách tất cả các tham số để sử dụng

-   **Linux/macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Hoặc cho tất cả hệ điều hành**
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

Lưu ý: ở chế độ gradio/gui, để hủy chuyển đổi đang chạy, chỉ cần nhấp vào[X]Từ thành phần tải lên ebook.

### Sử dụng Docker

Bạn cũng có thể sử dụng Docker để chạy Sách điện tử sang Audiobook Converter. 
Phương pháp này đảm bảo tính nhất quán trên các môi trường khác nhau và đơn giản hóa thiết lập.

#### Chạy container docker

Để chạy container Docker và khởi động giao diện Gradio, hãy sử dụng lệnh sau:

\-Run chỉ với CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run với GPU Speedup (chỉ tương thích NVIDIA)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Xây dựng container docker

-   Bạn có thể xây dựng hình ảnh Docker bằng lệnh:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Lệnh này sẽ bắt đầu giao diện Gradio trên cổng 7860. (LocalHost: 7860)

-   Để biết thêm tùy chọn, hãy thêm tham số`--help`

## Vị trí tệp container docker

Tất cả Ebook2AudioBooks sẽ có cơ sở của`/home/user/app/`Ví dụ:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Hướng dẫn không đầu docker

đầu tiên cho một docker kéo mới nhất với

```bash
docker pull athomasson2/ebook2audiobook
```

-   Trước khi bạn chạy điều này, bạn cần tạo một dir có tên "đầu vào đầu vào" trong DIR hiện tại của bạn
    sẽ được liên kết, đây là nơi bạn có thể đặt các tệp đầu vào của mình cho hình ảnh Docker để xem

```bash
mkdir input-folder && mkdir Audiobooks
```

-   Trong lệnh bên dưới hoán đổi**Your_input_file.txt**với tên của tệp đầu vào của bạn

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   Và đó nên là nó!
-   Audiobook đầu ra sẽ được tìm thấy trong thư mục audiobook cũng sẽ được định vị
    Trong địa phương của bạn, bạn đã chạy lệnh docker này trong

## To get the help command for the other parameters this program has you can run this

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

và điều đó sẽ xuất hiện điều này[Giúp lệnh đầu ra](#help-command-output)

### Docker sáng tác

Dự án này sử dụng Docker Compose để chạy cục bộ. Bạn có thể bật hoặc tắt hỗ trợ GPU 
bằng cách đặt một trong hai`*gpu-enabled`hoặc`*gpu-disabled`TRONG`docker-compose.yml`

#### Các bước để chạy

1.  **Sao chép kho lưu trữ**(nếu bạn chưa có):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Đặt hỗ trợ GPU (đã tắt theo mặc định)**Để bật hỗ trợ GPU, hãy sửa đổi`docker-compose.yml`và thay đổi`*gpu-disabled`ĐẾN`*gpu-enabled`
3.  **Bắt đầu dịch vụ:**
    ```bash
    docker-compose up -d
    ```
4.  **Truy cập Dịch vụ:**Dịch vụ sẽ có sẵn tại http&#x3A; // localhost: 7860.

### Giao diện docker GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Thuê GPU

Không có phần cứng để chạy nó hoặc bạn muốn thuê GPU?

#### Bạn có thể nhân đôi không gian Hugginface và thuê GPU với giá khoảng 0,40 đô la một giờ

[Huggingface Space Demo](#huggingface-space-demo)

#### Hoặc bạn có thể thử sử dụng Google Colab miễn phí!

(Hãy lưu ý rằng nó sẽ hết thời gian sau một chút bạn không gây rối với Google Colab)[Google colab miễn phí](#free-google-colab)

## Các vấn đề chung của Docker

-   Docker bị mắc kẹt tải xuống các mô hình tinh chỉnh.
    (Điều này không xảy ra cho mọi máy tính nhưng một số người dường như gặp phải vấn đề này)
    Vô hiệu hóa thanh tiến trình xuất hiện để khắc phục sự cố,
    như đã thảo luận[Ở đây trong #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Ví dụ về việc thêm bản sửa lỗi này trong`docker run`yêu cầu

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Các mô hình TTS được điều chỉnh tốt

Bạn có thể tinh chỉnh mô hình XTTS của riêng bạn một cách dễ dàng với repo này[XTTS-Finetune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Nếu bạn muốn thuê GPU một cách dễ dàng, bạn cũng có thể nhân đôi cái ôm này[XTTS-Finetune-Webui-Space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Một không gian bạn có thể sử dụng để không có gì dễ dàng nhận được dữ liệu đào tạo[Denoise-Huggingface-Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Bộ sưu tập TTS được điều chỉnh tốt

Để tìm bộ sưu tập các mô hình TTS đã được tinh chỉnh của chúng tôi,
thăm nom[Liên kết khuôn mặt ôm này](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Đối với mô hình tùy chỉnh XTTS, một clip âm thanh ref của tham chiếu bằng giọng nói là bắt buộc:

## Bản trình diễn

**Giọng nói ngày mưa**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**Giọng nói của David Attenborough**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Các định dạng ebook được hỗ trợ

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Kết quả tốt nhất**:`.epub`hoặc`.mobi`Để phát hiện chương tự động

## Đầu ra

-   Tạo ra a`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Đặt trong tệp ./lib/conf.py) với siêu dữ liệu và các chương.
-   **Ví dụ**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Các vấn đề phổ biến:

-   CPU chậm (tốt hơn trên máy chủ SMP CPU) trong khi GPU NVIDIA có thể có chuyển đổi gần như thời gian thực.[Thảo luận về điều này](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Đối với thế hệ đa ngôn ngữ nhanh hơn, tôi sẽ đề nghị người khác của tôi[dự án sử dụng piper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)thay vì
    .
-   "Tôi đang gặp vấn đề phụ thuộc" - chỉ cần sử dụng Docker, nó hoàn toàn khép kín và có chế độ không đầu,
     thêm vào`--help`Tham số ở cuối lệnh docker chạy để biết thêm thông tin.
-   "Tôi đang gặp sự cố âm thanh bị cắt ngắn!" - Vui lòng đưa ra vấn đề về vấn đề này,
     Chúng tôi không nói mọi ngôn ngữ và cần thông báo từ người dùng để tinh chỉnh logic chia tách câu.😊

## Những gì tôi cần giúp đỡ! 🙌

## [Danh sách đầy đủ những thứ có thể được tìm thấy ở đây](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Bất kỳ sự giúp đỡ nào từ những người nói bất kỳ ngôn ngữ được hỗ trợ nào để giúp đỡ với các phương pháp phân tách câu thích hợp
-   Có khả năng tạo hướng dẫn readme cho nhiều ngôn ngữ (vì ngôn ngữ duy nhất tôi biết là tiếng Anh)

## Cảm ơn đặc biệt

-   **Nấu ăn TTS**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Tầm cỡ**:[Trang web tầm cỡ](https://calibre-ebook.com)
-   **Ffmpeg**:[Trang web FFMPEG](https://ffmpeg.org)
-   [@shakenbake15 cho phương pháp tiết kiệm chương tốt hơn](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Di sản v1.0](legacy/v1.0)

Bạn có thể xem mã[đây](legacy/v1.0).

## Tham gia máy chủ của chúng tôi!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
