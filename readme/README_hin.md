<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

अध्यायों और मेटाडेटा के साथ ई-बुक से ऑडियोबुक में बदलने वाला CPU/GPU कन्वर्टर<br/>
उन्नत TTS इंजनों आदि का उपयोग करते हुए।<br/>
वॉयस क्लोनिंग और 1696 भाषाओं का समर्थन करता है!
> [!IMPORTANT] 
**यह टूल केवल DRM-मुक्त, वैध रूप से प्राप्त ई-बुक्स के साथ उपयोग के लिए है।** <br>
लेखक इस सॉफ़्टवेयर के किसी भी दुरुपयोग या उससे उत्पन्न किसी भी कानूनी परिणाम के लिए ज़िम्मेदार नहीं हैं। <br>
इस टूल का उपयोग ज़िम्मेदारी से और सभी लागू कानूनों के अनुपालन में करें।

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Ebook2audiobook डेवलपर्स का समर्थन करने के लिए धन्यवाद!
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### स्थानीय रूप से चलाएँ
[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge) ](#instructions)
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### दूरस्थ रूप से चलाएं
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### ग्राफ़िकल इंटरफ़ेस (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>वेब GUI की छवियां देखने के लिए क्लिक करें</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
## डेमो

**नई डिफ़ॉल्ट आवाज़ का डेमो**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>और डेमो</summary>

**ASMR आवाज़** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**बरसात के दिन की आवाज़**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**स्कारलेट आवाज़**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**डेविड एटनबरो आवाज़** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**उदाहरण**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

<a id="table-of-contents"></a>
## विषय-सूची
- [ebook2audiobook](#ebook2audiobook)
- [Features](#features)
- [GUI Interface](#gui-interface)
- [Demos](#demos)
- [Supported Languages](#supported-languages)
- [Minimum Requirements](#hardware-requirements)
- [Usage](#instructions)
  - [Run Locally](#instructions)
    - [Launching Gradio Web Interface](#instructions)
    - [Basic Headless Usage](#basic-usage)
    - [Headless Custom XTTS Model Usage](#example-of-custom-model-zip-upload)
    - [Help command output](#help-command-output)
  - [Run Remotely](#run-remotely)
  - [Docker](#docker)
    - [Steps to Run](#docker)
- [Tools](#tools)
  - [Preload models for offline installs](#preload-models)
  - [Translate ebooks out of e2a](#translate-ebooks)

- [Cloned Voices](#cloned-voices)
- [Fine Tuned TTS models](#fine-tuned-tts-models) 
  - [Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
  - [Train TTS Model](#fine-tune-your-own-tts-model)
- [Supported eBook Formats](#supported-ebook-formats)
- [Output Formats](#output-and-process-formats)
- [Revert to older Version](#reverting-to-older-versions)
- [Common Issues](#common-issues)
- [Contributing](#contributing)
- [Special Thanks](#special-thanks)
- [Table of Contents](#table-of-contents)


<a id="features"></a>
## विशेषताएं
- 🔧 **टीटीएस इंजन समर्थित**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **अनेक फ़ाइल प्रारूप परिवर्तित करें**: , , , , , , , , , , , , , , , , , , , , , , `.epub` `.mobi` `.azw3` `.fb2` `.lrf` `.rb` `.snb` `.tcr` `.pdf` `.txt` `.rtf` `.doc` `.docx` `.html` `.odt` `.azw` `.tiff` `.tif` `.png` `.jpg` `.jpeg` `.bmp` `.zip`
- 💻 छोटे पाठ को सीधे ऑडियो में बदलने के लिए **पाठ क्षेत्र**
- 🔍 छवियों के रूप में पाठ पृष्ठों वाली फ़ाइलों के लिए **OCR स्कैनिंग**
- 🔊 **उच्च गुणवत्ता वाला टेक्स्ट-टू-स्पीच**, लगभग वास्तविक समय से लेकर लगभग वास्तविक आवाज़ तक
- 🗣️ अपनी स्वयं की आवाज़ फ़ाइल का उपयोग करके **वैकल्पिक वॉयस क्लोनिंग**
- 🌐 **1696 भाषाओं को सपोर्ट करता है** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **कम संसाधन अनुकूल** — **2 GB RAM / 1 GB VRAM (न्यूनतम)** पर चलता है
- 🎵 **ऑडियोबुक आउटपुट प्रारूप**: mono or stereo , , , , , , , , , `aac` `flac` `mp3` `m4b` `m4a` `mp4` `mov` `ogg` `wav` `webm`
- 🧠 **SML टैग समर्थित** — रुकावटों, विरामों, आवाज़ बदलने आदि पर सूक्ष्म नियंत्रण () [see below](#sml-tags-available)
- 🧩 अपने स्वयं के प्रशिक्षित मॉडल का उपयोग करके **वैकल्पिक कस्टम मॉडल** (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ E2A टीम द्वारा प्रशिक्षित **फ़ाइन-ट्यून किए गए प्रीसेट मॉडल** <br/>
     (यदि आपको अतिरिक्त फ़ाइन-ट्यून किए गए मॉडलों की आवश्यकता है, या यदि आप आधिकारिक प्रीसेट सूची में अपने मॉडल साझा करना चाहते हैं, तो हमसे संपर्क करें) <i> </i>


<a id="hardware-requirements"></a>
##  हार्डवेयर आवश्यकताएं
- RAM 2GB न्यूनतम, 8GB अनुशंसित।
- VRAM 1GB न्यूनतम, 4GB अनुशंसित।
- windows पर चलाने पर वर्चुअलाइज़ेशन सक्षम (केवल Docker)।
- CPU, XPU (intel, AMD, ARM)*।
- CUDA, ROCm, JETSON
- एमपीएस (एप्पल सिलिकॉन सीपीयू)

*<i> आधुनिक TTS इंजन CPU पर बहुत धीमे हैं, इसलिए YourTTS, Tacotron2 आदि जैसे निम्न गुणवत्ता वाले TTS का उपयोग करें।</i>

<a id="supported-languages"></a>
## समर्थित भाषाएं
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## समर्थित ई-बुक प्रारूप
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **सर्वोत्तम परिणाम**: स्वचालित अध्याय पहचान के लिए `.epub` या `.mobi`

<a id="output-and-process-formats"></a>
## आउटपुट और प्रसंस्करण प्रारूप
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- प्रसंस्करण प्रारूप को lib/conf.py में बदला जा सकता है

## उपलब्ध SML टैग
- `[break]` — मौन (यादृच्छिक सीमा **0.3–0.6 sec.**)
- `[pause]` — मौन (यादृच्छिक सीमा **1.0–1.6 sec.**)
- `[pause:N]` — निश्चित विराम (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — डिफ़ॉल्ट या GUI/CLI से चुनी गई आवाज़ से आवाज़ बदलें
- `[emotion:sadness]...[/emotion]` — Zonos only: emotion for a passage (happiness, sadness, disgust, fear, surprise, anger, other, neutral) or a mix like `[emotion:sadness=0.7,neutral=0.3]`; other engines ignore it

**आपकी ई-बुक में स्वचालित रूप से SML जोड़ने के लिए समर्पित हमारे दूसरे रेपो को देखें -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT] 
**इंस्टॉलेशन या बग समस्या पोस्ट करने से पहले, खुली और बंद समस्याओं वाले टैब में सावधानी से खोजें<br>
यह सुनिश्चित करने के लिए कि आपकी समस्या पहले से मौजूद नहीं है।**

नोट
**EPUB प्रारूप में ऐसी कोई मानक संरचना नहीं है जो परिभाषित करे कि अध्याय, अनुच्छेद, प्रस्तावना आदि क्या हैं।<br>
इसलिए आपको पहले उस सभी पाठ को मैन्युअल रूप से हटा देना चाहिए जिसे आप ऑडियो में नहीं बदलना चाहते।**


<a id="instructions"></a>
### निर्देश
1. **रिपॉज़िटरी क्लोन करें**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **ebook2audiobook इंस्टॉल / चलाएं**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>MacOS उपयोगकर्ताओं के लिए ध्यान दें: गुम प्रोग्राम इंस्टॉल करने के लिए homebrew इंस्टॉल किया जाता है।</i>
     
   - **Mac लॉन्चर**  
     `Mac Ebook2Audiobook Launcher.command` पर डबल क्लिक करें


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     या
     `ebook2audiobook.cmd` पर डबल क्लिक करें

     <i>Windows उपयोगकर्ताओं के लिए ध्यान दें: व्यवस्थापक विशेषाधिकारों के बिना गुम प्रोग्रामों को इंस्टॉल करने के लिए scoop इंस्टॉल किया जाता है।</i>
   
1. **वेब ऐप खोलें**: वेब ऐप तक पहुंचने और ई-बुक्स को बदलने के लिए टर्मिनल में दिए गए URL पर क्लिक करें। `http://localhost:7860/`
2. **सार्वजनिक लिंक के लिए**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (सभी ऑपरेटिंग सिस्टम, केवल एक बार इंस्टॉल किया गया और अपने python_env फ़ोल्डर के पायथन के साथ)

> [!IMPORTANT] 
**यदि स्क्रिप्ट को रोककर फिर से चलाया जाता है, तो आपको अपने Gradio GUI इंटरफ़ेस को रिफ़्रेश करना होगा<br>
ताकि वेब पेज नए कनेक्शन सॉकेट से फिर से जुड़ सके।**

<a id="basic-usage"></a>
### बुनियादी उपयोग
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: आपकी ई-बुक फ़ाइल का पथ
  - **[--voice]**: वॉयस क्लोनिंग फ़ाइल पथ (वैकल्पिक)
  - **[--language]**: ISO-639-3 में भाषा कोड (अर्थात्: इतालवी के लिए ita, अंग्रेज़ी के लिए eng, जर्मन के लिए deu...)।<br>
    डिफ़ॉल्ट भाषा eng है और ./lib/lang.py में सेट की गई डिफ़ॉल्ट भाषा के लिए --language वैकल्पिक है।<br>
    2 अक्षर वाले ISO-639-1 कोड भी समर्थित हैं।


<a id="example-of-custom-model-zip-upload"></a>
###  कस्टम मॉडल Zip अपलोड का उदाहरण
  (यह अनिवार्य मॉडल फ़ाइलों वाली .zip फ़ाइल होनी चाहिए। XTTSv2 के लिए उदाहरण: config.json, model.pth, vocab.json और ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>ध्यान दें: आपके कस्टम मॉडल की ref.wav हमेशा रूपांतरण के लिए चुनी गई आवाज़ होती है</i>
     
- **<custom_model_path>**: `model_name.zip` फ़ाइल का पथ,
      जिसमें (tts इंजन के अनुसार) सभी अनिवार्य फ़ाइलें होनी चाहिए<br>
      (देखें ./lib/models.py)।

### सभी उपयोग योग्य पैरामीटर की सूची के साथ विस्तृत गाइड
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **या सभी OS के लिए**
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
  --abs_url ABS_URL     Audiobookshelf server URL (e.g. http://localhost:13378).
  --abs_api_token ABS_API_TOKEN
                        Audiobookshelf API token.
  --abs_library ABS_LIBRARY
                        Audiobookshelf library ID.
  --enable_interlude    Add MusicGen music before the first chapter, between chapters, and at the end of the audiobook. Settings are in ./lib/conf_interlude.py
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
	[emotion:sadness]...[/emotion] — Zonos only: emotion for a passage (happiness, sadness, disgust, fear, surprise, anger, other, neutral) or a mix like [emotion:sadness=0.7,neutral=0.3]; other engines ignore it

```

ध्यान दें: gradio/gui मोड में, चल रहे रूपांतरण को रद्द करने के लिए, बस ई-बुक अपलोड घटक के [X] पर क्लिक करें।
सुझाव: यदि थोड़े अधिक विराम की आवश्यकता हो, तो 3 सेकंड के लिए '[pause:3]' जोड़ें आदि।

<a id="docker"></a>
### Docker
1. **रिपॉज़िटरी क्लोन करें**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **कंटेनर बिल्ड करें**
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
4. **कंटेनर चलाएँ:**
```bash
Docker run image:
    Gradio/GUI:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc...]
    Headless mode:
        CPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
          docker run --security-opt label=disable -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" -v "e2a_venvs:/app/lib/classes/tts_engines/venvs" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[5/6/7 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
Docker Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 docker compose --profile cuda up --no-log-prefix
        Run Headless mode:
               DEVICE_TAG=cu128 docker compose --profile cuda run --rm ebook2audiobook-cuda --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
Podman Compose (i.e. cuda 12.8:
        Run Gradio GUI:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile cuda up
        Run Headless mode:
               DEVICE_TAG=cu128 podman-compose -f podman-compose.yml --profile cuda run --rm ebook2audiobook-cuda --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
```
- ध्यान दें: Docker में MPS उपलब्ध नहीं है, इसलिए CPU का उपयोग करना होगा
- ध्यान दें: नामित वॉल्यूम `e2a_venvs` अपने-अपने venv में इंस्टॉल किए गए TTS इंजनों (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM आदि) को
  कंटेनर के अलग-अलग रन के बीच सुरक्षित रखता है, इसलिए उन्हें हर बार दोबारा इंस्टॉल नहीं करना पड़ता। उन्हें रीसेट करने के लिए: `docker volume rm e2a_venvs`

<a id="tools"></a>
## टूल्स
स्टैंडअलोन टूल्स, जो e2a के अपने Python (`python_env`, e2a के पहले लॉन्च पर बनाया जाता है) से चलते हैं।

<a id="preload-models"></a>
### ऑफ़लाइन इंस्टॉल के लिए मॉडल पहले से डाउनलोड करें: `tools/preload_models.py`
e2a द्वारा उपयोग किए जाने वाले हर मॉडल (TTS इंजन और उनके फ़ाइन-ट्यून, वॉइस कन्वर्ज़न, stanza, pyannote, demucs,
संगीत इंटरल्यूड, argos-translate पैकेज, tesseract डेटा, jieba और आवाज़ें) को एक ही फ़ोल्डर में डाउनलोड करता है, जिसकी संरचना
बिल्कुल `./models` जैसी होती है, जैसे कोई USB ड्राइव। ऑफ़लाइन मशीन पर उस फ़ोल्डर को e2a के `./models` में कॉपी करें
और उसके बगल में लिखे गए `voices` फ़ोल्डर को e2a के `./voices` में।
हर पूरा हुआ काम `<models_dir>/.e2a_downloads.json` में दर्ज होता है: दोबारा चलाने पर पूरे हो चुके काम छोड़ दिए जाते हैं और
बीच में रुके काम (ctrl-c, क्रैश, निकाली गई ड्राइव) उनकी अधूरी फ़ाइलें हटाने के बाद फिर से शुरू किए जाते हैं।
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` कुछ भी डाउनलोड किए बिना कामों और उनकी स्थिति (पूरा, बाधित, लंबित) की सूची दिखाता है।

```bash
usage: preload_models.py [-h] [--only ONLY] [--skip SKIP] [--languages LANGUAGES]
                         [--audiocpp_packages AUDIOCPP_PACKAGES] [--refresh] [--dry_run]
                         models_dir

Download every model e2a uses into one folder laid out exactly like ./models (i.e. a USB key for offline
installs).

positional arguments:
  models_dir            Target folder, i.e. /media/user/KEY/models or E:\models

options:
  -h, --help            show this help message and exit
  --only ONLY           Comma list of categories: common,xtts,bark,tortoise,vits,fairseq,glowtts,tacotron,yo
                        urtts,piper,zonos,audiocpp,audiocpp_server,gptsovits,f5tts,omnivoice,orpheus,sparktt
                        s,chattts,csm,openvoice,melotts,phonon,stanza,pyannote,demucs,interlude,argos,tessda
                        ta,jieba,voices
  --skip SKIP           Comma list of categories to leave out
  --languages LANGUAGES
                        Comma list of e2a ISO-639-3 codes (eng,fra,ita...): single-language models and fine-
                        tunes for these only, multilingual models only for engines speaking one of them
  --audiocpp_packages AUDIOCPP_PACKAGES
                        audiocpp_server category: auto (the packages this machine runs, GPU and CPU), all
                        (every platform, for a key used elsewhere), or a comma list of audiocpp_packages
                        keys from lib/conf_models.py
  --refresh             Run every job again, even those already marked done (files already there are still
                        not downloaded twice)
  --dry_run             List every download job with its state (done, interrupted, todo) and exit
```

<a id="translate-ebooks"></a>
### e2a के बाहर ईबुक का अनुवाद: `tools/translate_ebook.sh` / `tools/translate_ebook.cmd`
EPUB/AZW3 फ़ाइलों, पूरे फ़ोल्डर (उसके सबफ़ोल्डरों के लिए `-r`) या पथों की सूची (`@list.txt`) का
ऑफ़लाइन अनुवाद करके अनुवादित ईबुक बनाता है, इसके लिए इस फ़ाइल में शामिल Argos Translate calibre प्लगइन का उपयोग होता है:
`tools/argostranslate-calibre-plugin.zip`। यह ऑडियोबुक रूपांतरण से स्वतंत्र है: यह केवल ईबुक लिखता है।
इसके लिए calibre चाहिए (जो e2a के लिए पहले से आवश्यक है) और यह e2a के `python_env` और argos-translate पैकेजों पर चलता है:
e2a द्वारा पहले से उपयोग की जा रही भाषा जोड़ी दोबारा डाउनलोड नहीं होती, गुम जोड़ी पहली बार उपयोग पर डाउनलोड होती है।
प्लगइन पहली बार उपयोग पर e2a की अपनी calibre प्रोफ़ाइल (`./run`) में इंस्टॉल होता है, आपका calibre अछूता रहता है।
`--to fra,ara,spa` एक साथ कई भाषाओं में अनुवाद करता है, हर भाषा के लिए एक ईबुक, और `--to all` उन सभी
भाषाओं में जिन तक स्रोत पहुँचता है (`--from`, अन्यथा हर पुस्तक की अपनी भाषा; `--no_download` के साथ केवल इंस्टॉल की गई भाषा जोड़ियाँ)।
`--list --from eng` उन भाषाओं की सूची दिखाता है जिनमें अंग्रेज़ी से अनुवाद होता है (इंस्टॉल की गई, डाउनलोड योग्य, या किसी अन्य स्रोत भाषा के लिए
अंग्रेज़ी के माध्यम से)।
calibre का `ebook-convert` जिन अन्य फ़ॉर्मैट (PDF, DOCX, MOBI, TXT, ...) को पढ़ता है, वे पहली भाषा से पहले
एक बार EPUB में बदले जाते हैं और EPUB के रूप में अनुवादित होते हैं: जब उनमें कोई भाषा दर्ज न हो, जैसा PDF और TXT में अक्सर होता है, तब `--from` आवश्यक है।
`-o` या `--output_dir` के बिना, हर अनुवाद उसकी पुस्तक के बगल में `<name>.<lang>.<ext>` नाम से सहेजा जाता है,
और जिस पुस्तक का अनुवाद पहले से मौजूद है उसे छोड़ दिया जाता है (दोबारा अनुवाद के लिए `--overwrite`)।
`tools/` फ़ोल्डर में मौजूद लॉन्चर `tools/translate_ebook.py` को `python_env` के साथ चलाते हैं, कुछ भी सक्रिय करने की ज़रूरत नहीं,
किसी भी फ़ोल्डर से (सापेक्ष पथ वहीं से लिए जाते हैं जहाँ से इसे शुरू किया गया):
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - या सीधे `python_env` के Python से: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`)। किसी अन्य Python से शुरू करने पर,
     स्क्रिप्ट खुद को `python_env` के Python से फिर से शुरू कर लेती है।
   - **Docker**: इसे e2a कंटेनर के अंदर चलाएँ, जैसे `docker exec -it <container> python3 tools/translate_ebook.py ...`
     कंटेनर से दिखने वाले पथों के साथ।
   - **गति**: argostranslate अपनी डिफ़ॉल्ट सेटिंग्स पर चलता है (CTranslate2 थ्रेड और सबसे तेज़ कंप्यूट टाइप चुनता है,
     CPU पर int8), e2a के float32 वाले 1 थ्रेड पर नहीं। इन्हें बदलने के लिए `ARGOS_INTRA_THREADS` या `ARGOS_COMPUTE_TYPE` सेट करें।

```bash
usage: translate_ebook.py [-h] [-t LANG[,LANG...]] [-f LANG] [-r] [-o OUTPUT] [--output_dir OUTPUT_DIR]
                          [--overwrite] [-m {replace,bilingual}] [--device {cpu,cuda,auto}]
                          [--batch_size BATCH_SIZE] [--no_cache] [--no_download] [--allow_changes] [--list]
                          [books ...]

Translate ebooks offline, out of e2a, with the Argos Translate calibre plugin
(tools/argostranslate-calibre-plugin.zip). EPUB/AZW3 are translated as they are, the other formats
calibre's ebook-convert reads (PDF, DOCX, MOBI, ...) are converted to EPUB once, before the first
language, and their translations saved as EPUB. It runs on e2a's python_env and argos-translate packages
(models/argos-translate): a language pair e2a already uses is not downloaded again, a missing one is
downloaded on first use (direct or through English). The plugin is installed into e2a's own calibre
profile (run/) on first use, your calibre setup is left untouched.
Translated paths are printed on stdout, progress and logs on stderr.

positional arguments:
  books                 Ebook files (EPUB, AZW3, or PDF, DOCX, MOBI... converted to EPUB first) or folders
                        to translate; @list.txt reads paths from a file, one per line

options:
  -h, --help            show this help message and exit
  -t, --to LANG[,LANG...]
                        Target language(s), ISO-639-1 or ISO-639-3 codes, comma separated for several (fr,
                        fra or fra,ara,spa): one translated ebook per language. all: every language the
                        source reaches (see --list --from), installed ones only with --no_download
  -f, --from LANG       Source language, ISO-639-1 or ISO-639-3 code (default: read from each book)
  -r, --recursive       Also look for books in the subfolders of the given folders
  -o, --output OUTPUT   Output file, single input only, same extension as the input, .epub for a converted
                        one (default: <name>.<lang>.<ext> next to the input)
  --output_dir OUTPUT_DIR
                        Write the translations into this folder (subfolders are mirrored with -r) instead of
                        next to each book
  --overwrite           Translate again even if the output file already exists (skipped otherwise)
  -m, --mode {replace,bilingual}
                        replace: the translation replaces the text. bilingual: each paragraph is followed by
                        its translation, saved as <name>.<lang>.bilingual.<ext> (default: replace)
  --device {cpu,cuda,auto}
                        Device argostranslate runs on (default: cpu)
  --batch_size BATCH_SIZE
                        Segments sent to the translation worker per request (default: 16)
  --no_cache            Neither read nor write the translation cache (run/argos_translate/cache.sqlite), the
                        one that makes a second run of the same book near instant
  --no_download         Never download a missing argos-translate package, fail instead
  --allow_changes       Only when argostranslate is missing from python_env: install it even if packages
                        already there would change version
  --list                List the installed and the downloadable language pairs, then exit. With --from
                        and/or --to: only their pairs, plus the targets a source reaches through English

examples:
  translate_ebook.py book.epub --to fr
  translate_ebook.py book.epub --to fra,ara,spa
  translate_ebook.py book.azw3 --from en --to deu -o /path/to/book_deu.azw3
  translate_ebook.py /path/to/books -r --to es,it --output_dir /path/to/books_translated
  translate_ebook.py book.epub --from eng --to all
  translate_ebook.py @books.txt --to ita --mode bilingual
  translate_ebook.py --list
  translate_ebook.py --list --from eng
```

<a id="cloned-voices"></a>
## क्लोन की गई आवाज़ें
आप किसी भी समर्थित ऑडियो प्रारूप में कोई भी ध्वनि ऑडियो अपलोड कर सकते हैं, आदर्श अवधि लगभग 1 से 5 मिलियन है।
इससे कोई फर्क नहीं पड़ता कि रिकॉर्डिंग में शोरगुल वाला बैकग्राउंड है या संगीत बज रहा है — E2A आपकी आवाज़ को साफ़ कर देगा।

अंतर्निहित क्लोन की गई आवाज़ों की सूची मुख्य रूप से अंग्रेजी में है। अगर आपको आधिकारिक रूप से अन्य भाषाओं में आवाज़ें चाहिए
सूची में जोड़ा गया, कृपया हमसे संपर्क करें और हम समीक्षा के बाद उन्हें जोड़ देंगे।

<a id="fine-tuned-tts-models"></a>
## फ़ाइन-ट्यून किए गए (fine-tuned) TTS मॉडल
<a id="fine-tune-your-own-tts-model"></a>
#### अपने खुद के टीटीएस मॉडल को ठीक करें

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### प्रशिक्षण डेटा का शोर हटाना

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### फ़ाइन-ट्यून किए गए TTS मॉडल का संग्रह

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

कस्टम XTTSv2 मॉडल के लिए, आवाज़ का एक संदर्भ ऑडियो क्लिप अनिवार्य है:

## आपका स्वयं का Ebook2Audiobook अनुकूलन
आप अपनी इच्छित सेटिंग्स जोड़ने या हटाने के लिए libs/conf.py को स्वतंत्र रूप से संशोधित कर सकते हैं। यदि आप ऐसा करने की योजना बना रहे हैं, तो बस
मूल conf.py की एक प्रतिलिपि बना लें ताकि प्रत्येक ebook2audiobook अद्यतन पर आप अपने संशोधित conf.py का बैकअप ले सकें और
मूल को वापस रख सकें। आपको models.py के लिए भी वही प्रक्रिया योजना बनानी होगी। यदि आप अपने स्वयं के कस्टम मॉडल को
एक आधिकारिक फ़ाइन-ट्यून किया गया ebook2audiobook मॉडल बनाना चाहते हैं, तो कृपया हमसे संपर्क करें और हम इसे प्रीसेट सूची में जोड़ देंगे।

<a id="reverting-to-older-versions"></a>
## पुराने संस्करणों पर लौटना
रिलीज़ यहाँ मिल सकती हैं -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## सामान्य समस्याएं:
- मेरा NVIDIA/ROCm/XPU/MPS GPU नहीं पहचाना जा रहा?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  CPU धीमा है (सर्वर smp CPU पर बेहतर) जबकि GPU लगभग वास्तविक समय का रूपांतरण कर सकता है।
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (हालांकि इसमें zero-shot वॉयस क्लोनिंग नहीं है, और ये Siri गुणवत्ता की आवाज़ें हैं, लेकिन यह cpu पर बहुत तेज़ है)।
- "मुझे निर्भरता संबंधी समस्याएं हो रही हैं" - बस docker का उपयोग करें, यह पूरी तरह से स्वतंत्र है और इसमें headless मोड है,
   अधिक जानकारी के लिए docker run कमांड के अंत में `--help` पैरामीटर जोड़ें।
- "मुझे कटे हुए ऑडियो की समस्या हो रही है!" - कृपया इस बारे में एक ISSUE बनाएं,
   हम हर भाषा नहीं बोलते और वाक्य विभाजन तर्क को बेहतर बनाने के लिए हमें उपयोगकर्ताओं की सलाह की आवश्यकता है।😊

## ***** रोडमैप *****
- सभी विशेषताएं सार्वजनिक योगदान के लिए खुली हैं ⭐
- मॉडलों को बेहतर बनाने में हमारी मदद करने के लिए किसी भी समर्थित भाषा को बोलने वाले लोगों से कोई भी सहायता ⭐
- [x] रूपांतरण शुरू करने से पहले ब्लॉक/अध्यायों का पूर्वावलोकन
- [x] सूक्ष्म पाठ परिवर्तन के लिए रूपांतरित वाक्य के अनुसार संपादन
- [x] म्यूज़िक इंट्रो, इंटरल्यूड और एंडिंग जनरेट करें; इंटरल्यूड और एंडिंग में बदलाव करें
- [x] आवाज़, विराम, रुकावट और अधिक परिवर्तनों के लिए SML टैग एकीकरण
- [x] विभिन्न भाषाओं में -h -help पैरामीटर जानकारी
- [x] PDF / JPG / BMP / PNG / TIFF के लिए OCR स्कैनिंग
- [x] Notebooks फ़ोल्डर [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] चीनी पाठ विभाजन को शब्दों को न तोड़ने योग्य बनाना और विराम की समयबद्धता में सुधार करना [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] डॉकरफ़ाइल
- [x] डॉकर कंपोज़
- [x] पॉडमैन कंपोज़
- [x] कैगल नोटबुक
- [x] Google Colab नोटबुक
- [x] Audiobookshelf एकीकरण
- [x] ई-बुक अनुवाद विकल्प
- [x] आउटपुट प्रारूप विकल्प
- [x] मल्टीप्रोसेसिंग रूपांतरण
- [x] बैच ई-बुक फ़ोल्डर रूपांतरण
- [x] GPU डिवाइस पहचान
- [x] वॉयस क्लोनिंग अपलोड के लिए किसी भी बैकग्राउंड रेफ़रेंस ऑडियो को डीनोइज़ करें
- [x] कस्टम फ़ाइन - ट्यून मॉडल अपलोड

#### यूज़र के अनुरोध
- [ ] कम से कम xttsv2, fairseq, vits, piper के लिए यूरोपीय पुर्तगाली भाषा मॉडल जोड़ें (सहायता का स्वागत है)
- [ ] कम से कम xttsv2, fairseq, vits, piper के लिए सिंधी भाषा मॉडल जोड़ें (सहायता का स्वागत है)

#### टीटीएस इंजन
- [x] ड्रामाबॉक्स (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] FireRed ऑडियो / FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] फिश - स्पीच/ फिश ऑडियो (https://github.com/fishaudio/fish-speech)[cite: 1]
- [x] हिग्स ऑडियो टीटीएस (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] माया1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1]
- [x] F5 - TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen3 - TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1]
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1]
- [x] Voxtral TTS (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] चैटरबॉक्स (https://github.com/resemble-ai/chatterbox)[cite: 1]
- [x] CosyVoice / CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1]
- [x] इंडेक्स - टीटीएस/ इंडेक्स टीटीएस2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] ब्रीज़ टीटीएस (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] कन्फ्यूशियस4 टीटीएस (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] डॉट्स टीटीएस (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT - SOVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] कोकोरो - टीटीएस (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] कुगेलऑडियो (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] मैग्पी टीटीएस (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] मॉस टीटीएस लोकल / नैनो (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] पॉकेट टीटीएस (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] ग्रैडियम फोनॉन (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] सुपरटोनिक (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] पाइपर (https://github.com/rhasspy/piper)[cite: 1]
- [x] विट्स (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] फेयरसेक (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] टैकोट्रॉन2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] कछुआ (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] ज़ोनोस (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] छाल (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] ऑर्फ़ियस - टीटीएस (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] स्पार्क - टीटीएस (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Readme अनुवाद
- [x] अरबी (आरा)
- [x] चीनी (zho)
- [x] अंग्रेज़ी (ENG)
- [x] स्पेनिश (SPA)
- [x] फ़्रेंच (FRA)
- [x] जर्मन (deu)
- [x] इटैलियन (ITA)
- [x] पुर्तगाली (POR)
- [x] पोलिश (POL)
- [x] तुर्की (TUR)
- [x] रूसी (RUS)
- [x] डच (nld)
- [x] चेक (ces)
- [x] जापानी (jpn)
- [x] हिन्दी (hin)
- [x] बंगाली (बेन)
- [x] हंगेरियन (HUN)
- [x] कोरियाई (कोर)
- [x] वियतनामी (VIE)
- [x] स्वीडिश (SWE)
- [x] फ़ारसी (फास)
- [x] योरुबा (योर)
- [x] स्वाहिली (SWA)
- [x] इंडोनेशियाई (ind)
- [x] स्लोवाक (SLK)
- [x] क्रोएशियाई (hrv)

#### 💻 OS संगतता
- [x] 🪟 Windows x86
- [x] 🪟 आर्म विंडो
- [x] 🍎 मैक इंटेल x86
- [x] 🍎 एप्पल सिलिकॉन मैक
- [x] 🐧 Linux x86
- [x] 🐧 आर्म लिनक्स

**********

<a id="contributing"></a>
## योगदान
कोई समस्या या पुल अनुरोध खोलने से पहले, [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md) पढ़ें: पायथन कोड सामान्यीकरण नियम,
शाखा और पुल अनुरोध वर्कफ़्लो, जीयूआई लीजेंड्स और रीडमी अनुवाद, एक टीटीएस इंजन जोड़ना, परीक्षण।

## बीटा परीक्षणों के लिए हार्डवेयर दान की तलाश है
हम अपने विकास का परीक्षण करने के लिए किसी भी प्रकार का हार्डवेयर स्वीकार करते हैं जैसे:
- Nvidia सपोर्टिंग cuda >= 11.8
- XPU इंटेल कार्ड
- ROCm AMD कार्ड ROCm को सपोर्ट करते हैं >=5.7

@DrewThomasson यदि आप किसी भी तरह से मदद करना चाहते हैं! 😃
<!--
## क्या आपको हमारी सेवा को बढ़ावा देने के लिए GPU किराए पर लेने की आवश्यकता है?
- यहां एक मतदान खुला है https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## क्रेडिट
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- A deep learning toolkit for Text-to-Speech, battle-tested in research and production.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Fast and local neural text-to-speech engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- Zonos2 के लिए ggml अनुमान कोड।
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- ggml द्वारा संचालित, ऑडियो मॉडल के लिए एक ऑल - इन - वन, शुद्ध C++ अनुमान इंजन।

<a id="special-thanks"></a>
## विशेष धन्यवाद
सभी वित्तीय और कोड योगदानकर्ताओं के लिए, प्रत्येक योगदान और सुझाव E2A की गुणवत्ता में सुधार करने में मदद करता है।