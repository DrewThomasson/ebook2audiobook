📚 ebook2audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
Konwerter procesora/GPU z ebooków do audiobooków z rozdziałami i metadanami <br/>
Korzystanie z Caliber, FFMPEG, XTTSV2, FAIRSEQ i innych. Obsługuje klonowanie głosowe i +1110 języków! [!WAŻNY]
** To narzędzie jest przeznaczone do użytku z nie-DRM, wyłącznie nabywanym ebookami. ** <br>
Autorzy nie ponoszą odpowiedzialności za jakiekolwiek niewłaściwe wykorzystanie tego oprogramowania lub wynikających z tego konsekwencji prawnych. <br>
Użyj tego narzędzia odpowiedzialnie i zgodnie ze wszystkimi obowiązującymi przepisami. [! ”

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko--fi-f16061?style=for-the-badge&logo=ko-fi&logocolor=white)]] (https: // ko-fi .com/ATHOMASSON2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_Web_Gui] (Assets/Demo_Web_Gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
Ara [العربية (arabski)] (./ readme/readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
Zho [中文 (chiński)] (./ readme/readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
SWE [svenska (szwedzki)] (./ readme/readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فارسی (perska)] (./ readme/readme_fa.md)


## Table of Contents
[ebook2audiobook] (#-ebook2audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Funkcje] (#funkcje)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Interfejs Docker GUI] (#Docker-Gui-Interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[Demo przestrzenne Huggingface] (#Huggingface-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Darmowy Google Colab] (#Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Wstępnie wykonane demo audio] (#DEMO)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Języki obsługiwane] (#obsługiwane języki)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Wymagania] (#odporności na sprzęt)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Instrukcje instalacyjne] (#instalowanie instalacji)
- [Output](#output)
- [Common Issues](#common-issues)
[Zastosowanie] (#uruchamianie-gradio-WEB-Interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Uruchamianie interfejsu internetowego Gradio] (#uruchamianie-gradio-WEB-Interface)


[Podstawowe użycie bezgłowych] (#podstawowe-wykorzystanie)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Bezgłowe niestandardowe użycie modelu XTTS] (#Przykład-Custom-Model-Zip-Propload)
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Wynajem GPU] (#Renting-A-GPU)


[Wyjście polecenia pomocy] (#Help-Command-Output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Modele TTS z drobnamionami] (#modele o drobnoziarnistym tts)


[W celu zbierania modeli dopracowanych TTS] (#drobnoziarniste-tts-collection)
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
[Docker Headless Guide] (#Docker-Headless-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Lokalizacje plików kontenera Docker] (#Docker-Container-File-Lokations)
- **Portuguese (por)**
- **Russian (rus)**
[Common Docker Problemy] (#Common-Docker-Insuies)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Obsługiwane formaty ebooków] (#obsługiwane-ebook-formaty)


[Wyjście] (#wyjście)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Wspólne problemy] (#powszechne)


[Specjalne podziękowania] (#Special-Thanks)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (#Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Cechy
```bash
📖 Konwertuje ebooki na format tekstu za pomocą kalibru. 📚 Rozdziela ebook na rozdziały zorganizowanego dźwięku. 🎙️ Wysokiej jakości tekst-meety z [coqui xttsv2] (https://huggingface.co/coqui/xtts-v2) i [fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ Przykłady/MMS) (i więcej). 🗣️ Opcjonalne klonowanie głosu za pomocą własnego pliku głosowego. 🌍 Obsługuje języki +1110 (domyślnie angielski). [Lista obsługiwanych języków] (https://dl.fbaipublicfiles.com/mm/tts/all-tts-languages.html)
```

🖥️ Zaprojektowany do działania na 4 GB pamięci RAM. [Demo przestrzenne Huggingface] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [Przytulanie twarzy] (https://img.shields.io/badge/hugging%20face-spaces-yellow?style=for-the-badge&logo=huggingface)] (https://huggingface.co/spaces/drewthomasson /ebook2audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
Przestrzeń Huggingface działa na bezpłatnym poziomie procesora, więc spodziewaj się bardzo wolnego lub limitu czasu lol, po prostu nie podawaj mu gigantycznych plików to wszystko
   - **Windows**
     ```bash
Najlepiej zduplikować przestrzeń lub działać lokalnie. Bezpłatny Google Colab
     ```
[! [Bezpłatne Google Colab] (https://colab.research.google.com/assets/colab-badge.svg)]] (https://colab.research.google.com/github/drewthomasson/ebook2audiobook/blob/ Main/notebooks/colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Obsługiwane języki
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arabski (ara) **

> [!IMPORTANT]
** Chiński (Zho) **
to let the web page reconnect to the new connection socket.**

** Czech (CES) **
   - **Linux/MacOS**:
     ```bash
** Chorwacki (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Holender (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** English (Eng) **
     ```
     
** francuski (fra) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** Niemiecki (deu) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** Węgier (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** Włoski (ITA) **
     ```
   - **Windows**
** Japoński (jpn) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Koreański (Kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Polski (pol) **


** Portugalski (POR) **
   - **Linux/MacOS**
     ```bash
** Rosjan (Rus) **
     ```
   - **Windows**
** Hiszpański (spa) **
     .\ebook2audiobook.cmd --help
     ```
** Turkish (Tur) **
    ```python
     app.py --help
** Wietnamski (Vie) **

<a id="help-command-output"></a>
[** +1100 Języki przez fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Wymagania sprzętowe
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
Minimum 4 GB RAM, zalecane 8 GB
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Wirtualizacja włączona, jeśli działa w systemie Windows (tylko Docker)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (zalecane), MPS (jeszcze nie zoptymalizowane i może być wolniejsze niż procesor)

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

** Wcześniej, aby dokładnie opublikować instalację lub problem z błędem, wyszukaj na zakładce otwartej i zamkniętej problemy <br>
Aby upewnić się, że twój problem jeszcze nie istnieje. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Brak jakiejkolwiek struktury standardów, takich jak rozdział, akapit, przedmowa itp. <br>
Powinieneś najpierw usunąć ręcznie dowolny tekst, którego nie chcesz konwertować w dźwięku. **

Instrukcje instalacyjne

** Repo klonów **
  --headless            Run the script in headless mode
Uruchomienie interfejsu internetowego Gradio
  --ebooks_dir EBOOKS_DIR
** Uruchom ebook2audiobook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux/MacOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Otwórz aplikację internetową **: Kliknij adres URL podany w terminalu, aby uzyskać dostęp do aplikacji internetowej i przekonwertować ebooki. ** dla linku publicznego **:
`Python App.py -Share` (All OS)
`./ebook2audiobook.sh --share` (Linux/MacOS)
`ebook2audiobook.cmd --share` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!WAŻNY]
** Jeśli skrypt zostanie zatrzymany i uruchom ponownie, musisz odświeżyć interfejs Gradio GUI <br>
Aby strona internetowa połącz się z nowym gniazdem połączenia. **
                        (Optional) Fine tuned model path. Default is builtin model.
Podstawowe użycie
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux/MacOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [-ebook] **: Ścieżka do pliku ebooków. ** [-głos] **: Ścieżka pliku klonowania głosu (opcjonalnie). ** [-Język] **: Kod języka w ISO-639-3 (tj.: ITA dla włoskiego, eng for angielski, deu dla niemieckiego ...). <br>
Domyślny język to eng i -language jest opcjonalny dla domyślnego języka ustawionego w ./lib/lang.py. <br>
Obsługiwane są również kody liter ISO-639-1 2. Przykład niestandardowego przesyłania modelu zamka
  --repetition_penalty REPETITION_PENALTY
(Musi być plik .zip zawierający obowiązkowe pliki modelu. Przykład dla XTTS: config.json, model.pth, vocab.json i ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux/MacOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
** <Custom_model_path> **: Ścieżka do plik `Model_name.zip`,
    które muszą zawierać (zgodnie z silnikiem TTS) wszystkie obowiązkowe pliki <br>
    (Patrz ./lib/models.py). Aby uzyskać szczegółowy przewodnik z listą wszystkich parametrów do użycia
  --output_dir OUTPUT_DIR
** Linux/MacOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** lub dla wszystkich OS **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "help-command-output"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Uwaga: W trybie Gradio/GUI, aby anulować działającą konwersję, wystarczy kliknąć [X] z komponentu przesyłania ebooków. Korzystanie z Dockera
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Możesz także użyć Docker, aby uruchomić ebook do konwertera audiobook. Ta metoda zapewnia spójność w różnych środowiskach i upraszcza konfigurację. Uruchamianie kontenera Docker

Aby uruchomić kontener Docker i uruchomić interfejs Gradio, użyj następującego polecenia:

### Using Docker
-Run tylko z procesorem
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Budowanie kontenera Docker

Możesz zbudować obraz Docker za pomocą polecenia:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
To polecenie uruchomi interfejs Gradio na porcie 7860. (LocalHost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Aby uzyskać więcej opcji, dodaj parametr `--help`
```


Wszystkie ebook2audiobooks będą miały podstawowy reż `/home/użytkownik/app/`
Na przykład:
`tmp` =`/home/user/app/tmp`
`audiobooks` =`/home/user/app/audiobooks`
```
Docker Bezgłowy przewodnik
- For more options add the parameter `--help`


## Docker container file locations
Zanim go uruchomisz
które zostaną połączone, tutaj możesz umieścić swoje pliki wejściowe dla obrazu Docker
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
I to powinno to być! Wyjściowe audiobooki zostaną znalezione w folderze audiobook, który również zostanie zlokalizowany
W lokalnym reż
docker pull athomasson2/ebook2audiobook
Aby uzyskać polecenie pomocy dla innych parametrów ten program, możesz to uruchomić
- Before you do run this you need to create a dir named "input-folder" in your current dir
A to to wyprowadzi 
[Wyjście polecenia pomocy] (#Help-Command-Output)
mkdir input-folder && mkdir Audiobooks
Docker komponuje
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
W tym projekcie wykorzystuje Docker Compose do działania lokalnie. Możesz włączyć lub wyłączyć obsługę GPU 
Ustawiając `*GPU-obsługę` lub `*GPU-Disabled` in` Docker-Compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Kroki do uruchomienia
    athomasson2/ebook2audiobook \
** Klonuj repozytorium ** (jeśli jeszcze tego nie zrobiłeś):
```
- And that should be it! 
** Ustaw obsługę GPU (domyślnie wyłączone) **
Aby włączyć obsługę GPU, zmodyfikuj `Docker-Compose.yml` i zmień`*GPU-Disabled` to `*GPU-ENABLED`


** Uruchom usługę: **

```bash
** Dostęp do usługi: **

```
! [Demo_Web_Gui] (Assets/Demo_Web_Gui.gif)
[Help command output](#help-command-output)


Nie masz sprzętu, aby go uruchomić, czy chcesz wynająć procesor graficzny? Możesz zduplikować przestrzeń Hugginface i wypożyczyć procesor graficzny za około 0,40 USD za godzinę
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[Demo przestrzenne Huggingface] (#Huggingface-Space-Demo)


[Darmowy Google Colab] (#Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Typowe problemy dokujące
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker utknie w celu pobierania dopracowanych modeli. (Nie zdarza się to dla każdego komputera, ale niektóre wydają się napotykać ten problem)
Wydaje się, że wyłączenie paska postępu rozwiązuje problem,
Jak omówiono [tutaj w #191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Przykład dodania tej poprawki w poleceniu „Docker Run”
3. **Start the service:**
Modele TTS z drobnamionami TTS
    docker-compose up -d
Możesz łatwo dostroić własny model XTTS za pomocą tego repozytorium
[XTTS-FINETUNE-WEBUI] (https://github.com/daswer123/xtts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-FINETUNE-WEBUI-SPACE] (https://huggingface.co/spaces/drewthomasson/xtts-finetune-ebui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Miejsce, które możesz użyć, aby łatwo usunąć dane szkoleniowe
[Denoise-huggingface-SPACE] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Zbiór TTS z doskonale strojony
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Aby znaleźć naszą kolekcję już dopracowanych modeli TTS,


## Renting a GPU
Dema
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** Głos deszczowy **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** David Attenborough Voice **


Obsługiwane formaty ebooków
- Docker gets stuck downloading Fine-Tuned models.
`.Epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Najlepsze wyniki **: `.Epub` lub` .mobi` do automatycznego wykrywania rozdziałów
    -p 7860:7860 athomasson2/ebook2audiobook
Wyjście


!
You can fine-tune your own xtts model easily with this repo
Powszechne problemy:

Procesor jest powolny (lepszy na serwerze SMP CPU), podczas gdy NVIDIA GPU może mieć prawie konwersję w czasie rzeczywistym. [Dyskusja na temat tego] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
Dla szybszego generacji wielojęzycznej sugerowałbym drugiego

(Nie ma jednak zerowego klonowania głosu i jest głosami jakości Siri, ale jest znacznie szybszy na procesorze). „Mam problemy z zależnością” - po prostu użyj dokera, jest w pełni samodzielny i ma tryb bezgłowy,
 Dodaj parametr `--Help` na końcu polecenia Docker Run, aby uzyskać więcej informacji. „Dostaję obcięty problem z dźwiękiem!” - Proszę o to,

### Fine Tuned TTS Collection
Z czego potrzebuję pomocy! 🙌
[Pełna lista rzeczy można znaleźć tutaj] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Potencjalnie tworzenie przewodników ReadMe dla wielu języków (ponieważ jedynym znanym językiem jest angielski 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui tts **: [coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [Witryna FFMPEG] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy V1.0] (Legacy/v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Możesz wyświetlić kod [tutaj] (Legacy/v1.0). Dołącz do naszego serwera! [! ”