# 📚 ebook2audiobook (E2A)
Conversor CPU/GPU de e-book para audiolivro com capítulos e metadados<br/>
usando motores TTS avançados e muito mais.<br/>
Suporta clonagem de voz e 1158 idiomas!
> [!IMPORTANT]
**Esta ferramenta destina-se a ser usada apenas com e-books sem DRM e adquiridos legalmente.** <br>
Os autores não se responsabilizam por qualquer uso indevido deste software nem por quaisquer consequências legais decorrentes. <br>
Use esta ferramenta de forma responsável e em conformidade com todas as leis aplicáveis.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Obrigado por apoiar os desenvolvedores do ebook2audiobook!
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Executar localmente

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Executar remotamente
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Interface gráfica (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Clique para ver imagens da GUI web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

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

## Índice
- [ebook2audiobook](#-ebook2audiobook)
- [Recursos](#features)
- [Interface gráfica](#gui-interface)
- [Demos](#demos)
- [Idiomas suportados](#supported-languages)
- [Requisitos mínimos](#hardware-requirements)
- [Utilização](#instructions)
  - [Executar localmente](#instructions)
    - [Iniciar a interface web Gradio](#instructions)
    - [Utilização básica em modo headless](#basic-usage)
    - [Utilização de modelo XTTS personalizado em modo headless](#example-of-custom-model-zip-upload)
    - [Saída do comando de ajuda](#help-command-output)
  - [Executar remotamente](#run-remotely)
  - [Docker](#docker)
    - [Passos para executar](#docker)
    - [Problemas comuns com o Docker](#common-docker-issues)
  
- [Modelos TTS ajustados](#fine-tuned-tts-models)
  - [Coleção de modelos TTS ajustados](#fine-tuned-tts-collection)
  - [Treinar XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Formatos de e-book suportados](#supported-ebook-formats)
- [Formatos de saída](#output-and-process-formats)
- [Reverter para uma versão anterior](#reverting-to-older-versions)
- [Problemas comuns](#common-issues)
- [Agradecimentos especiais](#special-thanks)
- [Índice](#table-of-contents)


## Recursos
- 🔧 **Motores TTS suportados**: `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Converter múltiplos formatos de ficheiro**: `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Área de texto** para converter diretamente um texto curto em áudio
- 🔍 **Digitalização OCR** para ficheiros com páginas de texto em forma de imagens
- 🔊 **Conversão de texto em fala de alta qualidade**, de quase tempo real a uma voz quase real
- 🗣️ **Clonagem de voz opcional** usando o seu próprio ficheiro de voz
- 🌐 **Suporta 1158 idiomas** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Adequado a recursos limitados** — funciona com **2 GB de RAM / 1 GB de VRAM (mínimo)**
- 🎵 **Formatos de saída do audiolivro**: mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Tags SML suportadas** — controlo granular de quebras, pausas, mudança de voz e muito mais ([see below](#sml-tags-available))
- 🧩 **Modelo personalizado opcional** usando o seu próprio modelo treinado (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modelos de predefinição ajustados** treinados pela equipa E2A<br/>
     <i>(Contacte-nos se precisar de modelos ajustados adicionais, ou se quiser partilhar os seus na lista oficial de predefinições)</i>


##  Requisitos de hardware
- 2 GB de RAM mín., 8 GB recomendado.
- 1 GB de VRAM mín., 4 GB recomendado.
- Virtualização ativada se for executado no Windows (apenas Docker).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Os motores TTS modernos são muito lentos na CPU, por isso use TTS de menor qualidade como YourTTS, Tacotron2, etc.</i>

## Idiomas suportados
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 idiomas e dialetos aqui**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Formatos de e-book suportados
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Melhores resultados**: `.epub` ou `.mobi` para a deteção automática de capítulos

## Formatos de saída e de processamento
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- O formato de processamento pode ser alterado em lib/conf.py

## Tags SML disponíveis
- `[break]` — silêncio (intervalo aleatório **0.3–0.6 sec.**)
- `[pause]` — silêncio (intervalo aleatório **1.0–1.6 sec.**)
- `[pause:N]` — pausa fixa (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — mudar de voz a partir da voz padrão ou selecionada na GUI/CLI

**Veja o nosso outro repositório dedicado a adicionar SML automaticamente no seu e-book -> [E2A-SML](./tools/E2A-SML)**

> [!IMPORTANT]
**Antes de publicar um problema de instalação ou um bug, pesquise cuidadosamente no separador de problemas abertos e fechados<br>
para ter a certeza de que o seu problema ainda não existe.**

>[!NOTE]
**O formato EPUB não tem qualquer estrutura padrão que defina o que é um capítulo, um parágrafo, um prefácio, etc.<br>
Por isso, deve primeiro remover manualmente qualquer texto que não queira converter em áudio.**


### Instruções 
1. **Clonar o repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Instalar / Executar o ebook2audiobook**:

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Nota para utilizadores de macOS: o homebrew é instalado para instalar os programas em falta.</i>
     
   - **Launcher para Mac**  
     Faça duplo clique em `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     ou
     Faça duplo clique em `ebook2audiobook.cmd`

     <i>Nota para utilizadores de Windows: o scoop é instalado para instalar os programas em falta sem privilégios de administrador.</i>
   
1. **Abrir a aplicação web**: Clique no URL fornecido no terminal para aceder à aplicação web e converter e-books. `http://localhost:7860/`
2. **Para um link público**:
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Se o script for parado e executado novamente, precisa de atualizar a sua interface gráfica Gradio<br>
para permitir que a página web se volte a ligar ao novo socket de ligação.**

### Utilização básica
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


###  Exemplo de envio de um modelo personalizado em zip
  (deve ser um ficheiro .zip contendo os ficheiros de modelo obrigatórios. Exemplo para XTTSv2: config.json, model.pth, vocab.json e ref.wav)
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

### Para um guia detalhado com a lista de todos os parâmetros a usar
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Ou para todos os sistemas operativos**
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

NOTA: no modo gradio/gui, para cancelar uma conversão em curso, basta clicar no [X] do componente de envio do e-book.
DICA: se precisar de mais alguma pausa, adicione '[pause:3]' para 3 seg., etc.

### Docker
1. **Clonar o repositório**:
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Construir o contentor**
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
4. **Executar o contentor:**
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
- NOTA: o MPS não é exposto no Docker, por isso é necessário usar a CPU
  
### Problemas comuns com o Docker
- A minha GPU NVIDIA não está a ser detetada?? -> [Página wiki de PROBLEMAS DE GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Modelos TTS ajustados (fine-tuned)
#### Ajuste o seu próprio modelo XTTSv2

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Remover ruído dos dados de treino

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Coleção de modelos TTS ajustados

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Para um modelo personalizado XTTSv2 é obrigatório um clipe de áudio de referência da voz:

## A sua própria personalização do Ebook2Audiobook
É livre de modificar o libs/conf.py para adicionar ou remover as definições que desejar. Se planeia fazê-lo, faça apenas
uma cópia do conf.py original para que, em cada atualização do ebook2audiobook, possa guardar o seu conf.py modificado e repor
o original. Deve planear o mesmo processo para o models.py. Se desejar tornar o seu próprio modelo personalizado
num modelo ajustado oficial do ebook2audiobook, contacte-nos e iremos adicioná-lo à lista de predefinições.

## Reverter para versões anteriores
As versões podem ser encontradas -> [aqui](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Problemas comuns:
- A minha GPU NVIDIA/ROCm/XPU/MPS não está a ser detetada?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  A CPU é lenta (melhor numa CPU SMP de servidor) enquanto a GPU pode ter uma conversão quase em tempo real.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (No entanto, não tem clonagem de voz zero-shot, e as vozes são de qualidade Siri, mas é muito mais rápido na CPU).
- «Estou com problemas de dependências» - Use simplesmente o Docker, é totalmente autónomo e tem um modo headless,
   adicione o parâmetro `--help` no final do comando docker run para mais informações.
- «Estou com um problema de áudio truncado!» - POR FAVOR, ABRA UM ISSUE SOBRE ISTO,
   não falamos todos os idiomas e precisamos do conselho dos utilizadores para afinar a lógica de divisão de frases.😊

## ***** ROADMAP *****
- Todos os recursos abertos a contribuições públicas ⭐
- Qualquer ajuda de pessoas que falem algum dos idiomas suportados para nos ajudar a melhorar os modelos ⭐
- [x] Pré-visualizar blocos/capítulos antes de iniciar a conversão
- [ ] Edição por frase convertida para uma alteração cirúrgica do texto
- [x] Integração de tags SML para voz, pausa, quebra e mais alterações 
- [x] Informação dos parâmetros -h -help em diferentes idiomas
- [x] Digitalização OCR para PDF / JPG / BMP / PNG / TIFF
- [x] Pasta de notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Fazer com que a divisão de texto em chinês não separe palavras e melhorar a sincronização das pausas [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] [Criar uma app para iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Criar uma app para Android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Integração com o Audiobookshelf

#### Opções extra
- [x] Opção de tradução do e-book
- [x] Escolhas do formato de saída
- [x] Pasta de e-books em lote
- [x] Conversão com multiprocessamento
- [x] Conversão em lote de uma pasta de e-books
- [x] Deteção do dispositivo GPU
- [x] Remover ruído de qualquer áudio de referência para clonagem de voz enviada,
- [x] Envio de modelo personalizado (apenas XTTSv2 por agora. mais sob pedido)
- [ ] Adicionar um modelo de idioma português europeu para xttsv2, fairseq, vits, piper pelo menos (ajuda bem-vinda)
- [ ] Adicionar um modelo de idioma sindi para xttsv2, fairseq, vits, piper pelo menos (ajuda bem-vinda)

#### Motores TTS
- [x] XTTSv2
- [x] Bark
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Tortoise
- [x] GlowTTS
- [x] Piper-TTS
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] Kokoro-TTS
- [ ] Orpheus-TTS
- [ ] Zonos
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Style-TTS2
- [ ] GPT-SoVITS
- [ ] F5-TTS (https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/38#issuecomment-2453224267)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] Speedy-Speech
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Align-TTS
- [ ] Delightful-TTS
- [ ] Spark-TTS

#### Tradução do Readme
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

#### 🐍 Compatibilidade de sistemas operativos
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Extra exagerado para treinar modelos e afins (todos os modelos Coqui-tts suportados e o piper-tts num único comando simples) 
- Para informações sobre isto, @DrewThomasson está atualmente a trabalhar no seu desenvolvimento, [repositório em desenvolvimento aqui](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Criar uma GUI de treino fácil de usar para todos os modelos coqui-tts nas receitas de treino em formato ljspeech [aqui do coqui tts](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informações de normalização do código Python para colaboradores
- sem linha em branco entre o código, exceto entre funções e classes.
- aspa simples usada para todas as chaves exceto para dict() e json. dict['key'] sempre invocado com aspa simples
- indentação de 4 espaços, nada de tabulações
- tipagem estrita para todas as funções e para a declaração dos seus argumentos e valores de retorno
- sem espaço entre o argumento e a sua tipagem, sem espaço entre a função, o «->» e o valor de retorno

Exemplo:

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

## Procura-se doação de hardware para testes beta
Aceitamos qualquer tipo de hardware para testar o nosso desenvolvimento, como:
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson se quiser ajudar de alguma forma! 😃
<!--
## Precisa de alugar uma GPU para potenciar o nosso serviço?
- Está aberta uma sondagem aqui https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Agradecimentos especiais
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 por um melhor método de guardar capítulos](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
