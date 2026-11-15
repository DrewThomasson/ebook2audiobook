<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Conversor CPU/GPU de e-book para audiolivro com capítulos e metadados<br/>
usando motores TTS avançados e muito mais.<br/>
Suporta clonagem de voz e 1696 idiomas!
> [!IMPORTANT]
**Esta ferramenta destina-se a ser usada apenas com e-books sem DRM e adquiridos legalmente.** <br>
Os autores não se responsabilizam por qualquer uso indevido deste software nem por quaisquer consequências legais decorrentes. <br>
Use esta ferramenta de forma responsável e em conformidade com todas as leis aplicáveis.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Obrigado por apoiar os desenvolvedores do ebook2audiobook!
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### Executar localmente
[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)Instruções
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### Executar remotamente
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### Interface gráfica (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Clique para ver imagens da GUI web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
## Demos

**Demo da nova voz padrão**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Mais demos</summary>

**Voz ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Voz de dia chuvoso**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Voz Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Voz David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Exemplo**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

<a id="table-of-contents"></a>
## Índice
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
## Recursos
- 🔧 **Motores TTS suportados**: `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Converter múltiplos formatos de ficheiro**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Área de texto** para converter diretamente um texto curto em áudio
- 🔍 **Digitalização OCR** para ficheiros com páginas de texto em forma de imagens
- 🔊 **Conversão de texto em fala de alta qualidade**, de quase tempo real a uma voz quase real
- 🗣️ **Clonagem de voz opcional** usando o seu próprio ficheiro de voz
- 🌐 **Supports 1696 languages** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Adequado a recursos limitados** — funciona com **2 GB de RAM / 1 GB de VRAM (mínimo)**
- 🎵 **Formatos de saída do audiolivro**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Tags SML suportadas** — controlo granular de quebras, pausas, mudança de voz e muito mais ([see below](#sml-tags-available))
- 🧩 **Modelo personalizado opcional** usando o seu próprio modelo treinado (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modelos de predefinição ajustados** treinados pela equipa E2A<br/>
     <i>(Contacte-nos se precisar de modelos ajustados adicionais, ou se quiser partilhar os seus na lista oficial de predefinições)</i>


<a id="hardware-requirements"></a>
##  Requisitos de hardware
- 2 GB de RAM mín., 8 GB recomendado.
- 1 GB de VRAM mín., 4 GB recomendado.
- Virtualização ativada se for executado no Windows (apenas Docker).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Os motores TTS modernos são muito lentos na CPU, por isso use TTS de menor qualidade como YourTTS, Tacotron2, etc.</i>

<a id="supported-languages"></a>
## Idiomas suportados
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## Formatos de e-book suportados
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Melhores resultados**: `.epub` ou `.mobi` para a deteção automática de capítulos

<a id="output-and-process-formats"></a>
## Formatos de saída e de processamento
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- O formato de processamento pode ser alterado em lib/conf.py

## Tags SML disponíveis
- `[break]` — silêncio (intervalo aleatório **0.3–0.6 sec.**)
- `[pause]` — silêncio (intervalo aleatório **1.0–1.6 sec.**)
- `[pause:N]` — pausa fixa (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — mudar de voz a partir da voz padrão ou selecionada na GUI/CLI
- `[emotion:sadness]...[/emotion]` — Apenas Zonos: emoção por uma passagem (felicidade, tristeza, desgosto, medo, surpresa, raiva, outro, neutro) ou uma mistura como `[emotion:sadness=0.7,neutral=0.3]`; outros motores a ignoram

**Veja o nosso outro repositório dedicado a adicionar SML automaticamente no seu e-book -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!IMPORTANT]
**Antes de publicar um problema de instalação ou um bug, pesquise cuidadosamente no separador de problemas abertos e fechados<br>
para ter a certeza de que o seu problema ainda não existe.**

NOTA
**O formato EPUB não tem qualquer estrutura padrão que defina o que é um capítulo, um parágrafo, um prefácio, etc.<br>
Por isso, deve primeiro remover manualmente qualquer texto que não queira converter em áudio.**


<a id="instructions"></a>
### Instruções
1. **Clonar repositório**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Instalar / Executar o ebook2audiobook**:

   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Observação para usuários do MacOS: o homebrew está instalado para instalar programas ausentes.</i>
     
   - **Launcher para Mac**  
     Faça duplo clique em `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     ou
     Clique duas vezes em `ebook2audiobook.cmd`

     <i>Nota para utilizadores de Windows: o scoop é instalado para instalar os programas em falta sem privilégios de administrador.</i>
   
1. **Abrir a aplicação web**: Clique no URL fornecido no terminal para aceder à aplicação web e converter e-books. `http://localhost:7860/`
2. **Para um link público**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (todos os sistemas operacionais, apenas uma vez instalado e com o Python da sua pasta python_env)

> [!IMPORTANT]
**Se o script for parado e executado novamente, precisa de atualizar a sua interface gráfica Gradio<br>
para permitir que a página web se volte a ligar ao novo socket de ligação.**

<a id="basic-usage"></a>
### Utilização Básica
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]**: Caminho para o seu ficheiro de e-book
  - **[--voice]**: Caminho do ficheiro de clonagem de voz (opcional)
  - **[--language]**: Código de idioma em ISO-639-3 (ex.: ita para italiano, eng para inglês, deu para alemão...).<br>
    O idioma padrão é eng e --language é opcional para o idioma padrão definido em ./lib/lang.py.<br>
    Os códigos ISO-639-1 de 2 letras também são suportados.


<a id="example-of-custom-model-zip-upload"></a>
###  Exemplo de envio de modelo personalizado em Zip
  (deve ser um ficheiro .zip que contenha os ficheiros de modelo obrigatórios. Exemplo para XTTSv2: config.json, model.pth, vocab.json e ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Nota: o ref.wav do seu modelo personalizado é sempre a voz selecionada para a conversão</i>
     
- **<custom_model_path>**: Caminho para o ficheiro `model_name.zip`,
      que deve conter (consoante o motor TTS) todos os ficheiros obrigatórios<br>
      (ver ./lib/models.py).

### Para Guia Detalhado com lista de todos os Parâmetros a serem usados
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Ou para todos os sistemas operacionais**
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

NOTA: no modo gradio/gui, para cancelar uma conversão em curso, basta clicar no [X] do componente de envio do e-book.
DICA: se precisar de mais alguma pausa, adicione '[pause:3]' para 3 seg., etc.

<a id="docker"></a>
### Docker
1. **Clonar o repositório**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Construir o contêiner**
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
4. **Executar o contêiner:**
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
- NOTA: O MPS não está exposto no docker, portanto, a CPU deve ser usada
- NOTA: o volume nomeado `e2a_venvs` mantém os motores TTS instalados em seu próprio venv (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM etc.)
  em execuções de contêineres, para que eles não sejam reinstalados a cada vez. Para redefini-los: `docker volume rm e2a_venvs`

<a id="tools"></a>
## Ferramentas
Ferramentas autônomas, executadas com o próprio Python da e2a (`python_env`, criado pelo primeiro lançamento da e2a).

<a id="preload-models"></a>
### Modelos de pré-carregamento para instalações offline: `tools/preload_models.py`
Faz o download de todos os modelos que o e2a usa (motores TTS e seus ajustes finos, conversão de voz, stanza, pyannote, demucs,
interlúdios de música, pacotes argos-translate, dados tesseract, jieba e as vozes) em uma pasta disposta
exatamente como `./models`, ou seja, uma chave USB. Na máquina offline, copie essa pasta para `./models` do e2a
e a pasta `voices` gravada ao lado dela para `./voices` do e2a.
Cada trabalho terminado é gravado em `<models_dir>/.e2a_downloads.json`: uma nova execução ignora o que está feito e começa
novamente o que foi interrompido (ctrl-c, falha, chave desconectada) após remover os seus arquivos parciais.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` lista os trabalhos e seu estado (concluído, interrompido, pendente) sem baixar nada.

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
### Traduzir ebooks da e2a: `tools/translate_ebook.sh`/`tools/translate_ebook.cmd`
Traduz arquivos EPUB/AZW3, uma pasta inteira (`-r` para suas subpastas) ou uma lista de caminhos (`@list.txt`)
em ebooks traduzidos, offline, com o plugin Argos Translate para calibre incluído em
`tools/argostranslate-calibre-plugin.zip`. Independente da conversão do audiolivro: ele só escreve ebooks.
Ele precisa do calibre (já exigido pelo e2a) e é executado no `python_env` e nos pacotes argos-translate do e2a:
um par de idiomas que o e2a já usa não é baixado novamente, um que está faltando é baixado no primeiro uso.
O plugin é instalado na primeira utilização no próprio perfil de calibre da e2a (`./run`), o seu calibre é deixado intacto.
`--to fra,ara,spa` traduz para vários idiomas ao mesmo tempo, um e-book por idioma, e `--to all` para todos os
idiomas alcançáveis a partir da origem (`--from`, senão o próprio idioma de cada livro; apenas os instalados com `--no_download`).
`--list --from eng` lista os idiomas para os quais o inglês traduz (instalados, para download ou através do inglês para
outra origem).
Outros formatos lidos pelo `ebook-convert` do calibre (PDF, DOCX, MOBI, TXT, ...) são convertidos para EPUB uma vez, antes do
primeiro idioma, e traduzidos como EPUB: `--from` é necessário quando não indicam idioma, como costuma acontecer com PDF e TXT.
Sem `-o` ou `--output_dir`, cada tradução é salva ao lado do seu livro como `<name>.<lang>.<ext>`,
e um livro cuja tradução já existe é ignorado (`--overwrite` para traduzi-lo novamente).
Os lançadores na pasta `tools/` executam `tools/translate_ebook.py` com `python_env`, nada para ativar,
de qualquer pasta (os caminhos relativos são retirados de onde é iniciado):
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Ou diretamente com o Python do `python_env`: `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows: `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Iniciado com qualquer outro Python,
     o script se reinicia com o do `python_env`.
   - **Docker**: executá-lo dentro do contêiner do e2a, por exemplo, `docker exec -it <container> python3 tools/translate_ebook.py ...`
     com caminhos vistos a partir do contentor.
   - **Velocidade**: o argostranslate é executado em seus próprios padrões (o CTranslate2 escolhe os threads e o tipo de computação mais rápido,
     int8 na CPU), não no 1 thread do e2a no float32. Defina `ARGOS_INTRA_THREADS` ou `ARGOS_COMPUTE_TYPE` para substituí-los.

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
## Vozes Clonadas
Você pode carregar qualquer áudio de voz em qualquer um dos formatos de áudio suportados, a duração ideal é de cerca de 1 a 5 minutos.
Não importa se a gravação tem um fundo barulhento ou música tocando sobre ela — a E2A limpará a voz para você.

A lista de vozes clonadas incorporada é principalmente em inglês. Se precisar que vozes em outros idiomas sejam oficialmente
adicionado à lista, entre em contacto connosco e iremos adicioná-los após análise.

<a id="fine-tuned-tts-models"></a>
## Modelos TTS ajustados (fine-tuned)
<a id="fine-tune-your-own-tts-model"></a>
#### Ajuste o seu próprio modelo TTS

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Remover ruído dos dados de treino

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### Coleção de modelos TTS ajustados

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Para um modelo personalizado XTTSv2 é obrigatório um clipe de áudio de referência da voz:

## A sua própria personalização do Ebook2Audiobook
É livre de modificar o libs/conf.py para adicionar ou remover as definições que desejar. Se planeia fazê-lo, faça apenas
uma cópia do conf.py original para que, em cada atualização do ebook2audiobook, possa guardar o seu conf.py modificado e repor
o original. Deve planear o mesmo processo para o models.py. Se desejar tornar o seu próprio modelo personalizado
num modelo ajustado oficial do ebook2audiobook, contacte-nos e iremos adicioná-lo à lista de predefinições.

<a id="reverting-to-older-versions"></a>
## Reverter para versões mais antigas
As versões podem ser encontradas -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## Problemas comuns:
- A minha GPU NVIDIA/ROCm/XPU/MPS não está a ser detetada?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  A CPU é lenta (melhor numa CPU SMP de servidor) enquanto a GPU pode ter uma conversão quase em tempo real.
 [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (No entanto, não tem clonagem de voz zero-shot, e as vozes são de qualidade Siri, mas é muito mais rápido na CPU).
- «Estou com problemas de dependências» - Use simplesmente o Docker, é totalmente autónomo e tem um modo headless,
   adicione o parâmetro  no final do comando docker run para mais informações. `--help`
- «Estou com um problema de áudio truncado!» - POR FAVOR, ABRA UM ISSUE SOBRE ISTO,
   não falamos todos os idiomas e precisamos do conselho dos utilizadores para afinar a lógica de divisão de frases.😊

## Roteiro
- Todos os recursos abertos a contribuições públicas ⭐
- Qualquer ajuda de pessoas que falem algum dos idiomas suportados para nos ajudar a melhorar os modelos ⭐
- [x] Pré-visualizar blocos/capítulos antes de iniciar a conversão
- [x] Edição por frase convertida para uma alteração cirúrgica do texto
- [x] Gerar introduções, interlúdios e finais de música; editar interlúdios e finais
- [x] Integração de tags SML para voz, pausa, quebra e mais alterações
- [x] Informação dos parâmetros -h -help em diferentes idiomas
- [x] Digitalização OCR para PDF / JPG / BMP / PNG / TIFF
- [x] Pasta de notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Fazer com que a divisão de texto em chinês não separe palavras e melhorar a sincronização das pausas [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Composição do Docker
- [x] Podman compõe
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [x] Integração com o Audiobookshelf
- [x] Opção de tradução do e-book
- [x] Escolhas do formato de saída
- [x] Conversão com multiprocessamento
- [x] Conversão em lote de uma pasta de e-books
- [x] Deteção do dispositivo GPU
- [x] Denoise qualquer áudio de referência de fundo para upload de clonagem de voz
- [x] Upload de modelo personalizado ajustado

#### Solicitações de Usuários
- [ ] Adicionar um modelo de idioma português europeu para xttsv2, fairseq, vits, piper pelo menos (ajuda bem-vinda)
- [ ] Adicionar um modelo de idioma sindi para xttsv2, fairseq, vits, piper pelo menos (ajuda bem-vinda)

#### Motores TTS
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] Áudio FireRed/ FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Fala de peixe/Áudio de peixe (https://github.com/fishaudio/fish-speech)[cite: 1]
- [x] Áudio Higgs TTS (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] Maya1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1]
- [x] F5-TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1]
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1]
- [x] Voxtral TTS (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] Chatterbox (https://github.com/resemble-ai/chatterbox)[cite: 1]
- [x] CosyVoice / CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1]
- [x] Índice-tts / Índice TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Confúcio4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Pontos TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Pocket TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonic (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Tartaruga (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Casca (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] CSM (https://github.com/SesameAILabs/csm)

#### Tradução do Readme
- [x] Árabe (ara)
- [x] Chinês (zho)
- [x] Inglês (ENG)
- [x] Espanhol (spa)
- [x] Francês (fra)
- [x] Alemão (deu)
- [x] Italiano (ita)
- [x] Português (por)
- [x] Polaco (pol)
- [x] Turco (tur)
- [x] Russo (rus)
- [x] Holandês (nld)
- [x] Checo (ces)
- [x] Japonês (jpn)
- [x] Hindi (hin)
- [x] Bengali (ben)
- [x] Húngaro (hun)
- [x] Coreano (kor)
- [x] Vietnamita (vie)
- [x] Sueco (swe)
- [x] Persa (fas)
- [x] Iorubá (yor)
- [x] Swahili (swa)
- [x] Indonésio (ind)
- [x] Eslovaco (slk)
- [x] Croata (hrv)

#### Compatibilidade SO:
- [x] 🪟 Windows x86
- [x] 🪟 ARM Windows
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

<a id="contributing"></a>
## Contribuir
Antes de abrir um problema ou uma solicitação pull, leia [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md): Regras de normalização de código Python,
fluxo de trabalho de solicitação de ramificação e pull, legendas de GUI e traduções de README, adicionando um mecanismo TTS, teste.

## Procura-se doação de hardware para testes beta
Aceitamos qualquer tipo de hardware para testar o nosso desenvolvimento, como:
- Nvidia cuda de suporte >= 11,8
- Cartões XPU Intel
- Placas AMD ROCm que suportam ROCm >=5,7

@DrewThomasson se quiser ajudar de alguma forma! 😃
<!--
## Precisa de alugar uma GPU para potenciar o nosso serviço?
- Está aberta uma sondagem aqui https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Créditos
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) -- A deep learning toolkit for Text-to-Speech, battle-tested in research and production.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Fast and local neural text-to-speech engine.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- código de inferência ggml para Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) -- Um mecanismo de inferência C++ puro e tudo-em-um para modelos de áudio, alimentado por ggml.

<a id="special-thanks"></a>
## Agradecimentos especiais
Para todos os contribuintes financeiros e de código, cada contribuição e sugestão ajuda a melhorar a qualidade do E2A.