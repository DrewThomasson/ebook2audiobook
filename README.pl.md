# 📚 ebook2audiobook

Konwerter CPU/GPU z ebooków do audiobooków z rozdziałami i metadanami<br/>Korzystanie z Caliber, FFMPEG, XTTSV2, FAIRSEQ i innych. Obsługuje klonowanie głosowe i +1110 języków!

> [!WAŻNY]**To narzędzie jest przeznaczone do użytku z nie-DRM, prawnie nabywanymi ebookami.**<br>Autorzy nie ponoszą odpowiedzialności za jakiekolwiek niewłaściwe wykorzystanie tego oprogramowania lub wynikających z tego konsekwencji prawnych.<br>Użyj tego narzędzia odpowiedzialnie i zgodnie ze wszystkimi obowiązującymi przepisami.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Dzięki wsparciu programistów ebook2audiobook!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Interfejs GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Kupujemy[Arabski (arabski)](./readme/README_AR.md)
-   Zho[chiński](./readme/README_CN.md)
-   a \`a[angielski](README.md)
-   swe[Szwedzki (szwedzki)](./readme/README_SWE.md)
-   Fas[Pers (perski)](./readme/README_FA.md)
-   ona[Włoch (włoski)](./readme/README.it.md)

## Spis treści

-   [ebook2audiobook](#-ebook2audiobook)
-   [Cechy](#features)
-   [Interfejs Docker GUI](#docker-gui-interface)
-   [Demo przestrzenne Hisgingface](#huggingface-space-demo)
-   [Bezpłatny Google Colab](#free-google-colab)
-   [Zakładone wersje audio](#demos)
-   [Obsługiwane języki](#supported-languages)
-   [Wymagania](#hardware-requirements)
-   [Instrukcje instalacyjne](#installation-instructions)
-   [Stosowanie](#launching-gradio-web-interface)
    -   [Uruchomienie interfejsu internetowego Gradio](#launching-gradio-web-interface)
    -   [Podstawowe użycie bezgłego](#basic--usage)
    -   [Bezgłowe niestandardowe użycie modelu XTTS](#example-of-custom-model-zip-upload)
    -   [Wynajem GPU](#renting-a-gpu)
    -   [Pomoc Wyjście polecenia](#help-command-output)
-   [Modele TTS z drobnamionami TTS](#fine-tuned-tts-models)
    -   [Do zbierania dopracowanych modeli TTS](#fine-tuned-tts-collection)
-   [Korzystanie z Dockera](#using-docker)
    -   [Docker Run](#running-the-docker-container)
    -   [Docker Build](#building-the-docker-container)
    -   [Docker komponuje](#docker-compose)
    -   [Docker Bezgłowy przewodnik](#docker-headless-guide)
    -   [Lokalizacje plików kontenera Docker](#docker-container-file-locations)
    -   [Typowe problemy Docker](#common-docker-issues)
-   [Obsługiwane formaty ebooków](#supported-ebook-formats)
-   [Wyjście](#output)
-   [Powszechne problemy](#common-issues)
-   [Specjalne podziękowania](#special-thanks)
-   [Dołącz do naszego serwera!](#join-our--server)
-   [Dziedzictwo](#legacy-v10)
-   [Spis treści](#table-of-contents)

## Cechy

-   📖 Konwertuje ebooki na format tekstu za pomocą kalibru.
-   📚 Rozdziela ebook na rozdziały zorganizowanego dźwięku.
-   🎙️ wysokiej jakości tekst na mowę z[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)I[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(i więcej).
-   🗣️ Opcjonalne klonowanie głosu za pomocą własnego pliku głosowego.
-   🌍 Obsługuje języki +1110 (domyślnie angielski).[Lista obsługiwanych języków](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ Zaprojektowany do działania na 4 GB pamięci RAM.

## [Demo przestrzenne Hisgingface](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   Przestrzeń Huggingface działa na bezpłatnym poziomie procesora, więc spodziewaj się bardzo wolnego lub limitu czasu lol, po prostu nie podawaj mu gigantycznych plików to wszystko
-   Najlepiej zduplikować przestrzeń lub działać lokalnie.

## Bezpłatny Google Colab

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Obsługiwane języki

-   **Arabski (ARA)**
-   **Chiński (ZH)**
-   **Czech (CES)**
-   **Chorwacki (HRV)**
-   **Holendrzy (NLD)**
-   **Angielski (eng)**
-   **Francuski (od)**
-   **Niemiecki (DEU)**
-   **Nie (Hin)**
-   **Węgierski (AM)**
-   **Włoski (ITA)**
-   **Japoński (JPN)**
-   **Koreański (cor)**
-   **Polski (Pol)**
-   **Portugalski (POR)**
-   **Rosjan (Rus)**
-   **Hiszpański (spa)**
-   **Turecki (okrągły)**
-   **Wietnamski (Vie)**
-   [**+1100 języków za pośrednictwem fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Wymagania sprzętowe

-   Minimum 4 GB RAM, zalecane 8 GB
-   Wirtualizacja włączona, jeśli działa w systemie Windows (tylko Docker)
-   CPU, GPU (zalecane), MPS (jeszcze nie zoptymalizowane i może być wolniejsze niż procesor)

> [!WAŻNY]**Przed opublikowaniem uważnie instalacji lub problemu z błędem wyszukaj na zakładce otwartej i zamkniętej<br>Aby upewnić się, że Twój problem jeszcze nie istnieje.**

> [!NOTATKA]**Brak struktury standardów, takich jak rozdział, akapit, przedmowa itp.<br>Najpierw powinieneś usunąć ręcznie dowolny tekst, którego nie chcesz konwertować w dźwięku.**

### Instrukcje instalacyjne

1.  **Repozytorium klonów**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Uruchomienie interfejsu internetowego Gradio

1.  **Uruchom ebook2audiobook**:
    -   **Linux/MacOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Okna**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Otwórz aplikację internetową**: Kliknij adres URL podany w terminalu, aby uzyskać dostęp do aplikacji internetowej i przekonwertować ebooki.
3.  **Dla linku publicznego**:`python app.py --share`(All OS)`./ebook2audiobook.sh --share`(Linux/MacOS)`ebook2audiobook.cmd --share`(Windows)

> [!WAŻNY]**Jeśli skrypt zostanie zatrzymany i uruchom ponownie, musisz odświeżyć interfejs Gradio GUI<br>Aby strona internetowa połącz się z nowym gniazdem połączenia.**

### Podstawowe użycie

-   **Linux/MacOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Okna**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--Ebook]**: Ścieżka do pliku ebooków.
-   **[--głos]**: Ścieżka pliku klonowania głosu (opcjonalnie).
-   **[--język]**: Kod językowy w ISO-639-3 (tj.: ITA dla włoskiego, eng for angielski, deu dla niemieckiego ...).<br>Język domyślny jest ENG i -Language jest opcjonalny dla domyślnego języka ustawionego w ./lib/lang.py.<br>Obsługiwane są również kody liter ISO-639-1 2.

### Przykład niestandardowego przesyłania modelu zamka

(Musi być plik .zip zawierający obowiązkowe pliki modelu. Przykład dla XTTS: config.json, model.pth, vocab.json i ref.wav)

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Okna**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;Custom_model_path>**: Ścieżka do`model_name.zip`plik,
        które muszą zawierać (zgodnie z silnikiem TTS) wszystkie obowiązkowe pliki<br>(Patrz ./lib/models.py).

### Aby uzyskać szczegółowy przewodnik z listą wszystkich parametrów do użycia

-   **Linux/MacOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Okna**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Lub dla wszystkich systemów operacyjnych**
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

Uwaga: w trybie gradio/gui, aby anulować działającą konwersję, po prostu kliknij[X]Z komponentu przesyłania ebooków.

### Korzystanie z Dockera

Możesz także użyć Docker, aby uruchomić ebook do konwertera audiobook. 
Ta metoda zapewnia spójność w różnych środowiskach i upraszcza konfigurację.

#### Uruchamianie kontenera Docker

Aby uruchomić kontener Docker i uruchomić interfejs Gradio, użyj następującego polecenia:

\-Run tylko z procesorem

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run z szybkością GPU (tylko kompatybilny z NVIDIA)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Budowanie kontenera Docker

-   Możesz zbudować obraz Docker za pomocą polecenia:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

To polecenie uruchomi interfejs Gradio na porcie 7860. (LocalHost: 7860)

-   Aby uzyskać więcej opcji, dodaj parametr`--help`

## Lokalizacje plików kontenera Docker

Wszystkie ebook2audiobooks będą miały podstawy`/home/user/app/`Na przykład:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Docker Bezgłowy przewodnik

Najpierw na wyciągnięcie najnowszego dokera z

```bash
docker pull athomasson2/ebook2audiobook
```

-   Zanim go uruchomisz
    które zostaną połączone, tutaj możesz umieścić swoje pliki wejściowe dla obrazu Docker

```bash
mkdir input-folder && mkdir Audiobooks
```

-   W poniższym poleceniu wymieniaj**Twój_input_file.txt**z nazwą pliku wejściowego

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   I to powinno to być!
-   Wyjściowe audiobooki zostaną znalezione w folderze audiobook, który również zostanie zlokalizowany
    W lokalnym reż

## Aby uzyskać polecenie pomocy dla innych parametrów ten program, możesz to uruchomić

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

A to to wyprowadzi[Pomoc Wyjście polecenia](#help-command-output)

### Docker komponuje

W tym projekcie wykorzystuje Docker Compose do działania lokalnie. Możesz włączyć lub wyłączyć obsługę GPU 
ustawiając jedno z nich`*gpu-enabled`Lub`*gpu-disabled`W`docker-compose.yml`

#### Kroki do uruchomienia

1.  **Klon repozytorium**(Jeśli jeszcze tego nie zrobiłeś):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Ustaw obsługę GPU (domyślnie wyłączone)**Aby włączyć obsługę GPU, zmodyfikuj`docker-compose.yml`i zmień`*gpu-disabled`Do`*gpu-enabled`
3.  **Rozpocznij usługę:**
    ```bash
    docker-compose up -d
    ```
4.  **Uzyskaj dostęp do usługi:**Usługa będzie dostępna na stronie http&#x3A; // localhost: 7860.

### Interfejs Docker GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Wynajem GPU

Nie masz sprzętu, aby go uruchomić, czy chcesz wynająć procesor graficzny?

#### Możesz zduplikować przestrzeń Hugginface i wypożyczyć procesor graficzny za około 0,40 USD za godzinę

[Demo przestrzenne Hisgingface](#huggingface-space-demo)

#### Lub możesz spróbować używać Google Colab za darmo!

(Pamiętaj, że po odrobinie bałaganu z Colab Google nie będzie się bawić)[Bezpłatny Google Colab](#free-google-colab)

## Typowe problemy Docker

-   Docker utknie w celu pobierania modeli dostosowanych.
    (Nie zdarza się to dla każdego komputera, ale niektóre wydają się napotykać ten problem)
    Wydaje się, że wyłączenie paska postępu rozwiązuje problem,
    Jak omówiono[tutaj, w #191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Przykład dodania tej poprawki w`docker run`rozkaz

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Modele TTS z drobnamionami TTS

Możesz łatwo dostroić własny model XTTS za pomocą tego repozytorium[XTTS-FINETUNE-WEBUI](https://github.com/daswer123/xtts-finetune-webui)

Jeśli chcesz łatwo wypożyczyć procesor graficzny, możesz również powielić tę przytulanie[XTTS-FINETUNE-WEBUI-SPACE](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Miejsce, które możesz użyć, aby łatwo usunąć dane szkoleniowe[Denoise-Huggingface-Space](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Zbiór TTS z doskonale strojony

Aby znaleźć naszą kolekcję już dopracowanych modeli TTS,
odwiedzać[Ten przytulny link do twarzy](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)W przypadku niestandardowego modelu XTTS klip audio odniesienia głosu jest obowiązkowy:

## Dema

**Deszczowy głos**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**David Attenborough Voice**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Obsługiwane formaty ebooków

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Najlepsze wyniki**:`.epub`Lub`.mobi`do automatycznego wykrywania rozdziałów

## Wyjście

-   Tworzy`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Ustaw w ./lib/conf.py) Plik z metadanami i rozdziałami.
-   **Przykład**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Powszechne problemy:

-   Procesor jest powolny (lepszy na serwerze SMP CPU), podczas gdy NVIDIA GPU może mieć prawie konwersję w czasie rzeczywistym.[Dyskusja na ten temat](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Dla szybszego generacji wielojęzycznej sugerowałbym drugiego[Projekt wykorzystujący Piper-TTS](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)Zamiast
    (Nie ma jednak zerowego klonowania głosu i jest głosami jakości Siri, ale jest znacznie szybszy na procesorze).
-   „Mam problemy z zależnością” - po prostu użyj dokera, jest w pełni samodzielny i ma tryb bezgłowy,
     dodać`--help`Parametr na końcu polecenia Docker Run, aby uzyskać więcej informacji.
-   „Dostaję obcięty problem z dźwiękiem!” - Proszę o to,
     Nie mówimy w każdym języku i potrzebujemy doradztwa użytkowników, aby dostroić logikę podziału zdań. 😊

## Z czego potrzebuję pomocy! 🙌

## [Pełną listę rzeczy można znaleźć tutaj](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Wszelkie pomoc osób mówiących w dowolnym z obsługiwanych języków, aby pomóc w odpowiednich metodach podziału zdań
-   Potencjalnie tworzenie przewodników ReadMe dla wielu języków (ponieważ jedynym znanym językiem jest angielski 😔)

## Specjalne podziękowania

-   **Gotowanie TTS**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Kaliber**:[Strona internetowa Calibre](https://calibre-ebook.com)
-   **FFMPEG**:[Witryna FFMPEG](https://ffmpeg.org)
-   [@Shadakenbake15 dla lepszej metody oszczędzania rozdziału](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy V1.0](legacy/v1.0)

Możesz wyświetlić kod[Tutaj](legacy/v1.0).

## Dołącz do naszego serwera!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
