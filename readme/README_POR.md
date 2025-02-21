📚 ebook2audioBook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
Conversor de CPU/GPU de eBooks para audiolivros com capítulos e metadados <br/>
Usando Caliber, FFMPEG, XTTSV2, Fairseq e muito mais. Suporta clonagem de voz e +1110 idiomas! [!IMPORTANTE]
** Esta ferramenta destina-se apenas ao uso apenas com eBooks adquiridos legalmente e não-DRM. ** <br>
Os autores não são responsáveis ​​por qualquer uso indevido deste software ou por quaisquer consequências legais resultantes. <br>
Use esta ferramenta com responsabilidade e de acordo com todas as leis aplicáveis. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko--fi-f16061?style=for-the-badge&logo=ko-fi&logocolor=white)] (https: // ko-fi .com/athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_web_gui] (Assets/Demo_Web_Gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العربية (árabe)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文 (chinês)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
swe [svenska (sueco)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فار liv (persa)] (./ readme/readme_fa.md)


## Table of Contents
[ebook2audiobook] (#-ebook2audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Recursos] (#Recursos)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Interface Docker GUI] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Huggingface Space Demo] (#huggingface-space-democulgo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Google Colab gratuito] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Demos de áudio pré-fabricados] (#demos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Idiomas suportados] (#idiomas suportados)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Requisitos] (#requisitos de hardware)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Instruções de instalação] (#Instrução de instalação)
- [Output](#output)
- [Common Issues](#common-issues)
[Uso] (#Lançamento de gradio-web-interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Lançar a interface da web gradio] (#lançamento de gradio-web-interface)


[Uso básico sem cabeça] (#básico-uso)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Uso do modelo XTTS personalizado sem cabeça] (#Exemplo-of-Custom-Model-Zip-Upload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Alugando uma GPU] (#Renting-a-GPU)


[Saída de comando de ajuda] (#Help-Command-Output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Modelos TTS ajustados finos] (#modelos tuned-tts)


[Para a coleta de modelos TTS ajustados finos] (#coleta de TTS tunst-tts)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (#Running-the-Docker-container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (#Building-the-Docker-container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (#Docker-Compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Docker Headless Guide] (#Docker sem cabeça-guia)
- **Japanese (jpn)**
- **Korean (kor)**
[Locais de arquivos de contêineres do docker] (#Docker-container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Common Docker Issues] (#comuns-Docker-Itsues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Formatos de eBook suportados] (#suportado-ebook-formats)


[Saída] (#saída)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Questões comuns] (#comuns)


[Agradecimentos especiais] (#Especial-Thanks)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Características
```bash
📖 Converte os eBooks em formato de texto com calibre. 📚 divide o eBook em capítulos para áudio organizado. 🎙️ Texto de alta qualidade para falar com [coqui xttsv2] (https://huggingface.co/coqui/xtts-v2) e [Fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ exemplos/mms) (e muito mais). 🗣️ Clonagem de voz opcional com seu próprio arquivo de voz. 🌍 suporta +1110 idiomas (inglês por padrão). [Lista de idiomas suportados] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥️ Projetado para ser executado em 4 GB de RAM. [Hugging Space Demo] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [Abraçar o rosto] (https://img.shields.io/badge/hugging%20face-spaces-elellow?style=for-the-badge&logo=huggingface)] (https://huggingface.co/spaces/dhomosson /ebook2audioBook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Huggingface Space está funcionando em uma camada de CPU gratuita, então espere muito lento ou tempo limite lol, apenas não dê arquivos gigantes é tudo
   - **Windows**
     ```bash
Melhor para duplicar o espaço ou executar localmente. Google Colab grátis
     ```
Também Main/Notebooks/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Idiomas suportados
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** árabe (ara) **

> [!IMPORTANT]
** Chinês (Zho) **
to let the web page reconnect to the new connection socket.**

** tcheco (CES) **
   - **Linux/MacOS**:
     ```bash
** Croata (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** holandês (nld) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Inglês (Eng) **
     ```
     
** Francês (Fra) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** alemão (deu) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** húngaro (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** italiano (ITA) **
     ```
   - **Windows**
** japonês (jpn) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Coreano (Kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** polonês (pol) **


** Português (POR) **
   - **Linux/MacOS**
     ```bash
** russo (rus) **
     ```
   - **Windows**
** Espanhol (spa) **
     .\ebook2audiobook.cmd --help
     ```
** turco (tur) **
    ```python
     app.py --help
** vietnamita (vie) **

<a id="help-command-output"></a>
[** +1100 Idiomas via Fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Requisitos de hardware
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4 GB RAM Mínimo, 8 GB recomendado
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualização ativada se estiver executando no Windows (somente Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (recomendado), MPS (ainda não otimizado e pode ser mais lento que a CPU) compatível

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

1
para ter certeza de que seu problema não existe já. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Falta de qualquer estrutura de padrões como o que é um capítulo, parágrafo, prefácio etc. <br>
você deve primeiro remover manualmente qualquer texto que não queira ser convertido em áudio. **

Instruções de instalação

** clone repo **
  --headless            Run the script in headless mode
Lançando a interface da web gradio
  --ebooks_dir EBOOKS_DIR
** Run Ebook2audioBook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/macOS **

optional parameters:
**Windows**
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Abra o aplicativo da web **: Clique no URL fornecido no terminal para acessar o aplicativo da web e converter eBooks. ** Para link público **:
`python app.py - -share` (todos os sistemas operacionais)
`./ebook2audioBook.sh - -share` (Linux/MacOS)
`ebook2audiobook.cmd - -share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!IMPORTANTE]
** Se o script for interrompido e executado novamente, você precisará atualizar sua interface gradio gui <br>
Para deixar a página da web se reconectar ao novo soquete de conexão. **
                        (Optional) Fine tuned model path. Default is builtin model.
Uso básico
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/MacOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
**Windows**
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-Ebook] **: caminho para o seu arquivo de e-book. ** [-Voz] **: Caminho do arquivo de clonagem de voz (opcional). ** [-Idioma] **: Código do idioma no ISO-639-3 (ou seja: Ita para italiano, Eng para o inglês, deu para alemão ...). <br>
A linguagem padrão é Eng e -Language é opcional para a linguagem padrão definida em ./lib/lang.py. <br>
Os códigos ISO-639-1 2 também são suportados. Exemplo de upload de Zip de modelo personalizado
  --repetition_penalty REPETITION_PENALTY
(Deve ser um arquivo .zip que contém os arquivos de modelo obrigatório. Exemplo para xtts: config.json, model.tth, vocab.json e ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
**Windows**
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <Custom_Model_Path> **: caminho para `model_name.zip` arquivo,
    que devem conter (de acordo com o mecanismo TTS) todos os arquivos obrigatórios <br>
    (Veja ./lib/models.py). Para guia detalhado com lista de todos os parâmetros para usar
  --output_dir OUTPUT_DIR
** Linux/macOS **
  --version             Show the version of the script and exit

**Windows**
Windows:
    Gradio/GUI:
** ou para todos os os **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "help-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Nota: No modo Gradio/GUI, para cancelar uma conversão em execução, basta clicar no [x] no componente de upload do e -book. Usando o docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Você também pode usar o Docker para executar o conversor de e -book para audiolivros. Esse método garante consistência em diferentes ambientes e simplifica a configuração. Executando o contêiner do Docker

Para executar o contêiner do docker e iniciar a interface gradio, use o seguinte comando:

### Using Docker
-Run apenas com CPU
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Construindo o recipiente do docker

Você pode construir a imagem do Docker com o comando:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Este comando iniciará a interface Gradio na porta 7860. (Localhost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Para mais opções, adicione o parâmetro `--help`
```


Todos os eBook2audioBooks terão a base de `/home/user/app/` `
Por exemplo:
`tmp` =`/home/user/app/tmp`
`Audiobooks` =`/home/user/app/audiobooks`
```
Guia sem cabeça do Docker
- For more options add the parameter `--help`


## Docker container file locations
Antes de executar isso, você precisa criar um diretor chamado "Foldador de entrada" em seu diretor atual
que estará vinculado, é aqui que você pode colocar seus arquivos de entrada para a imagem do Docker para ver
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
E deve ser isso! Os audiolivros de saída serão encontrados na pasta de audiolivros que também serão localizados
No seu diretor local, você executou este comando do Docker em
docker pull athomasson2/ebook2audiobook
Para obter o comando de ajuda para os outros parâmetros que este programa possui, você pode executar isso
- Before you do run this you need to create a dir named "input-folder" in your current dir
e isso irá produzir isso 
[Saída de comando de ajuda] (#Help-Command-Output)
mkdir input-folder && mkdir Audiobooks
Docker compor
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Este projeto usa o Docker compor para ser executado localmente. Você pode ativar ou desativar o suporte à GPU 
Definindo `*gpu-inabed` ou`*gpu-Disabled` em `Docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Etapas para executar
    athomasson2/ebook2audiobook \
** Clone o repositório ** (se você ainda não o fez):
```
- And that should be it! 
** Defina o suporte da GPU (desativado por padrão) **
Para ativar o suporte à GPU, modifique `Docker-compose.yml` e altere`*gpu-Disabled` para `*gpu-inabed`


** Inicie o serviço: **

```bash
** Acesse o serviço: **

```
! [Demo_web_gui] (Assets/Demo_Web_Gui.gif)
[Help command output](#help-command-output)


Não tem o hardware para executá -lo ou deseja alugar uma GPU? Você pode duplicar o espaço Hugginface e alugar uma GPU por cerca de US $ 0,40 por hora
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Huggingface Space Demo] (#huggingface-space-democulgo)


[Google Colab gratuito] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Questões comuns do Docker
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker fica preso ao baixar modelos ajustados. (Isso não acontece para todos os computador, mas alguns parecem encontrar esse problema)
Desativar a barra de progresso parece corrigir o problema,
Conforme discutido [aqui em #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Exemplo de adicionar essa correção no comando `Docker Run`
3. **Start the service:**
Modelos TTS ajustados finos
    docker-compose up -d
Você pode ajustar seu próprio modelo XTTS facilmente com este repo
[XTTS-FineTune-Webui] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-FineTune-Webui-Space] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Um espaço que você pode usar para desmontar os dados de treinamento facilmente também
[Denoise-Huggingface-space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Coleção TTS Fine TTS
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Para encontrar nossa coleção de modelos TTS já ajustados,


## Renting a GPU
Demos
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Voz do dia chuvoso **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough Voice **


Formatos de e -book suportados
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** melhores resultados **: `.epub` ou` .mobi` para detecção automática de capítulos
    -p 7860:7860 athomasson2/ebook2audiobook
Saída


! [Exemplo] (https://github.com/drewthomasson/voxnovels/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Questões comuns:

A CPU é lenta (melhor na CPU SMP do servidor), enquanto a NVIDIA GPU pode ter conversão quase em tempo real. [Discussão sobre isso] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
Para uma geração multilíngue mais rápida, eu sugeriria meu outro

(No entanto, ele não tem clonagem de voz zero e é voz de qualidade da Siri, mas é muito mais rápida na CPU). "Estou tendo problemas de dependência" - basta usar o Docker, está totalmente independente e tem um modo sem cabeça,
 Adicione o parâmetro `--help` no final do comando Docker Run para obter mais informações. "Estou recebendo um problema de áudio truncado!" - Por favor, faça um problema disso,

### Fine Tuned TTS Collection
Com o que eu preciso de ajuda! 🙌
[Lista completa de coisas pode ser encontrada aqui] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potencialmente criando guias de leitura para vários idiomas (porque o único idioma que conheço é o inglês 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui tts **: [Coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** FFMPEG **: [Site do FFMPEG] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy/V1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Você pode visualizar o código [aqui] (Legacy/V1.0). Junte -se ao nosso servidor! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)