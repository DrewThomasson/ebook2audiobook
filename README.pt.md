# 📚 ebook2audioBook

Conversor de CPU/GPU de eBooks para audiolivros com capítulos e metadados<br/>Usando Caliber, FFMPEG, XTTSV2, Fairseq e muito mais. Suporta clonagem de voz e +1110 idiomas!

> [!IMPORTANTE]**Esta ferramenta destina-se apenas ao uso apenas com eBooks não-DRM e legalmente adquiridos.**<br>Os autores não são responsáveis ​​por qualquer uso indevido deste software ou por quaisquer consequências legais resultantes.<br>Use esta ferramenta com responsabilidade e de acordo com todas as leis aplicáveis.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Graças ao apoio aos desenvolvedores do eBook2audioBook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Interface da GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Compramos[Árabe (árabe)](./readme/README_AR.md)
-   Zho[chinês](./readme/README_CN.md)
-   a \`a[Inglês](README.md)
-   swe[Sueco (sueco)](./readme/README_SWE.md)
-   fas[Persa (persa)](./readme/README_FA.md)
-   ela[Italiano (Italian)](./readme/README.it.md)

## Índice

-   [ebook2audioBook](#-ebook2audiobook)
-   [Características](#features)
-   [Interface Docker GUI](#docker-gui-interface)
-   [Demoção do espaço Huggingface](#huggingface-space-demo)
-   [Google Colab grátis](#free-google-colab)
-   [Demos de áudio pré-fabricados](#demos)
-   [Idiomas suportados](#supported-languages)
-   [Requisitos](#hardware-requirements)
-   [Instruções de instalação](#installation-instructions)
-   [Uso](#launching-gradio-web-interface)
    -   [Lançando a interface da web gradio](#launching-gradio-web-interface)
    -   [Uso básico sem cabeça](#basic--usage)
    -   [Uso do modelo XTTS personalizado sem cabeça](#example-of-custom-model-zip-upload)
    -   [Alugando uma GPU](#renting-a-gpu)
    -   [Saída de comando de ajuda](#help-command-output)
-   [Modelos TTS ajustados finos](#fine-tuned-tts-models)
    -   [Para a coleta de modelos TTS ajustados](#fine-tuned-tts-collection)
-   [Usando o docker](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker compor](#docker-compose)
    -   [Guia sem cabeça do Docker](#docker-headless-guide)
    -   [Locais de arquivo de contêineres do Docker](#docker-container-file-locations)
    -   [Questões comuns do Docker](#common-docker-issues)
-   [Formatos de e -book suportados](#supported-ebook-formats)
-   [Saída](#output)
-   [Questões comuns](#common-issues)
-   [Obrigado especial](#special-thanks)
-   [Junte -se ao nosso servidor!](#join-our--server)
-   [Legado](#legacy-v10)
-   [Índice](#table-of-contents)

## Características

-   📖 Converte os eBooks em formato de texto com calibre.
-   📚 divide o eBook em capítulos para áudio organizado.
-   🎙️ de alta qualidade texto em fala com[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)e[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(e muito mais).
-   🗣️ Clonagem de voz opcional com seu próprio arquivo de voz.
-   🌍 suporta +1110 idiomas (inglês por padrão).[Lista de idiomas suportados](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ Projetado para ser executado em 4 GB de RAM.

## [Demoção do espaço Huggingface](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Huggingface Space está funcionando em uma camada de CPU gratuita, então espere muito lento ou tempo limite lol, apenas não dê arquivos gigantes é tudo
-   Melhor para duplicar o espaço ou executar localmente.

## Google Colab grátis

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Idiomas suportados

-   **Arabic (ara)**
-   **Chinês (ZH)**
-   **Tcheco (CES)**
-   **Croata (VFC)**
-   **Holandês (NLD)**
-   **Inglês (Eng)**
-   **Francês (de)**
-   **German (deu)**
-   **Não (hin)**
-   **Húngaro (AM)**
-   **Italiano (ITA)**
-   **Japonês (JPN)**
-   **Coreano (COR)**
-   **Polonês (Pol)**
-   **Portuguese (por)**
-   **Russo (rus)**
-   **Espanhol (spa)**
-   **Turco (redondo)**
-   **Vietnamita (VIE)**
-   [**+1100 idiomas via Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Requisitos de hardware

-   4 GB RAM Mínimo, 8 GB recomendado
-   Virtualização ativada se estiver executando no Windows (somente Docker)
-   CPU, GPU (recomendado), MPS (ainda não otimizado e pode ser mais lento que a CPU) compatível

> [!IMPORTANTE]**Antes de publicar uma pesquisa de instalação ou bug, pesquise cuidadosamente na guia de problemas abertos e fechados<br>para ter certeza de que seu problema não existe já.**

> [!OBSERVAÇÃO]**Falta de qualquer estrutura de padrões como o que é um capítulo, parágrafo, prefácio etc.<br>Você deve primeiro remover manualmente qualquer texto que não deseja ser convertido em áudio.**

### Instruções de instalação

1.  **Repo Clone**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Lançando a interface da web gradio

1.  **Execute ebook2audiobook**:
    -   **Linux/MacOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Windows**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Abra o aplicativo da web**: Clique no URL fornecido no terminal para acessar o aplicativo da web e converter eBooks.
3.  **Para link público**:`python app.py --share`(all OS)`./ebook2audiobook.sh --share`(Linux/MacOS)`ebook2audiobook.cmd --share`(Windows)

> [!IMPORTANTE]**Se o script for interrompido e executado novamente, você precisará atualizar sua interface gradio gui<br>Para deixar a página da web se reconectar ao novo soquete de conexão.**

### Uso básico

-   **Linux/MacOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--ebook]**: Caminho para o seu arquivo de e -book.
-   **[--voz]**: Caminho do arquivo de clonagem de voz (opcional).
-   **[--linguagem]**: Código do idioma no ISO-639-3 (ou seja: ITA para italiano, Eng for English, deu para alemão ...).<br>O idioma padrão é Eng e -Language é opcional para o idioma padrão definido em ./lib/lang.py.<br>Os códigos ISO-639-1 2 também são suportados.

### Exemplo de upload de Zip de modelo personalizado

(Deve ser um arquivo .zip que contém os arquivos de modelo obrigatório. Exemplo para xtts: config.json, model.tth, vocab.json e ref.wav)

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;Custom_model_Path>**: Caminho para`model_name.zip`arquivo,
        que devem conter (de acordo com o mecanismo TTS) todos os arquivos obrigatórios<br>(Veja ./lib/models.py).

### Para guia detalhado com lista de todos os parâmetros para usar

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Windows**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Ou para todos os os os**
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

Nota: No modo Gradio/GUI, para cancelar uma conversão em execução, basta clicar em[X]Do componente de upload do eBook.

### Usando o docker

Você também pode usar o Docker para executar o conversor de e -book para audiolivros. 
Esse método garante consistência em diferentes ambientes e simplifica a configuração.

#### Executando o contêiner do Docker

Para executar o contêiner do docker e iniciar a interface gradio, use o seguinte comando:

\-Run apenas com CPU

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-RUN com aceleração da GPU (somente compatível com a NVIDIA)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Construindo o recipiente do docker

-   Você pode construir a imagem do Docker com o comando:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Este comando iniciará a interface Gradio na porta 7860. (Localhost: 7860)

-   Para mais opções, adicione o parâmetro`--help`

## Locais de arquivo de contêineres do Docker

Todos os eBook2audioBooks terão a base direta de`/home/user/app/`Por exemplo:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Guia sem cabeça do Docker

primeiro para um puxão do Docker do mais recente com

```bash
docker pull athomasson2/ebook2audiobook
```

-   Antes de executar isso, você precisa criar um diretor chamado "Foldador de entrada" em seu diretor atual
    que estará vinculado, é aqui que você pode colocar seus arquivos de entrada para a imagem do Docker para ver

```bash
mkdir input-folder && mkdir Audiobooks
```

-   No comando abaixo, trocou**Your_input_file.txt**com o nome do seu arquivo de entrada

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   E deve ser isso!
-   Os audiolivros de saída serão encontrados na pasta de audiolivros que também serão localizados
    No seu diretor local, você executou este comando do Docker em

## Para obter o comando de ajuda para os outros parâmetros que este programa possui, você pode executar isso

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

e isso irá produzir isso[Saída de comando de ajuda](#help-command-output)

### Docker compor

Este projeto usa o Docker compor para ser executado localmente. Você pode ativar ou desativar o suporte à GPU 
definindo também`*gpu-enabled`ou`*gpu-disabled`em`docker-compose.yml`

#### Etapas para executar

1.  **Clone o repositório**(se você ainda não o fez):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Defina o suporte da GPU (desativado por padrão)**Para ativar o suporte da GPU, modifique`docker-compose.yml`e mudar`*gpu-disabled`para`*gpu-enabled`
3.  **Inicie o serviço:**
    ```bash
    docker-compose up -d
    ```
4.  **Acesse o serviço:**O serviço estará disponível em http&#x3A; // localhost: 7860.

### Interface Docker GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Renting a GPU

Não tem o hardware para executá -lo ou deseja alugar uma GPU?

#### Você pode duplicar o espaço Hugginface e alugar uma GPU por cerca de US $ 0,40 por hora

[Demoção do espaço Huggingface](#huggingface-space-demo)

#### Ou você pode tentar usar o Google Colab gratuitamente!

(Esteja ciente de que vai tempo depois de um pouco de você não mexer com o Google Colab)[Google Colab grátis](#free-google-colab)

## Questões comuns do Docker

-   Docker fica preso ao baixar modelos ajustados.
    (Isso não acontece para todos os computador, mas alguns parecem encontrar esse problema)
    Desativar a barra de progresso parece corrigir o problema,
    como discutido[Aqui em #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Exemplo de adicionar essa correção no`docker run`comando

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Modelos TTS ajustados finos

Você pode ajustar seu próprio modelo XTTS facilmente com este repo[XTTS-FineTune-Webui](https://github.com/daswer123/xtts-finetune-webui)

Se você deseja alugar uma GPU facilmente, também pode duplicar este Huggingface[xtts-finetune-webui-space](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Um espaço que você pode usar para desmontar os dados de treinamento facilmente também[Denoise-Huggingface Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Coleção TTS Fine TTS

Para encontrar nossa coleção de modelos TTS já ajustados,
visita[Este link de rosto abraçado](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Para um clipe de áudio do Modelo Custom A REC da Extle, é obrigatório: é obrigatório:

## Demos

**Voz do dia chuvoso**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Formatos de e -book suportados

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Melhores resultados**:`.epub`ou`.mobi`Para detecção automática de capítulo

## Saída

-   Cria um`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Set em ./lib/conf.py) Arquivo com metadados e capítulos.
-   **Exemplo**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Questões comuns:

-   A CPU é lenta (melhor na CPU SMP do servidor), enquanto a NVIDIA GPU pode ter conversão quase em tempo real.[Discussão sobre isso](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Para uma geração multilíngue mais rápida, eu sugeriria meu outro[projeto que usa Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)em vez de
    (No entanto, ele não tem clonagem de voz zero e é voz de qualidade da Siri, mas é muito mais rápida na CPU).
-   "Estou tendo problemas de dependência" - basta usar o Docker, está totalmente independente e tem um modo sem cabeça,
     adicionar`--help`Parâmetro no final do comando Docker Run para obter mais informações.
-   "Estou recebendo um problema de áudio truncado!" - Por favor, faça um problema disso,
     Não falamos todos os idiomas e precisamos aconselhar dos usuários para ajustar a lógica de divisão da frase.😊

## Com o que eu preciso de ajuda! 🙌

## [Lista completa de coisas pode ser encontrada aqui](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Qualquer ajuda de pessoas que falam qualquer um dos idiomas suportados para ajudar nos métodos adequados de divisão de frases
-   Potencialmente criando guias de leitura para vários idiomas (porque o único idioma que conheço é inglês 😔)

## Obrigado especial

-   **Cozinhando tts**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Calibre**:[Calibre Website](https://calibre-ebook.com)
-   **Ffmpeg**:[Site do FFMPEG](https://ffmpeg.org)
-   [@SKAKENBAKE15 Para um melhor método de economia de capítulos](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legado v1.0](legacy/v1.0)

Você pode ver o código[aqui](legacy/v1.0).

## Junte -se ao nosso servidor!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
