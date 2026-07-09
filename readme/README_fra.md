# 📚 ebook2audiobook (E2A)
Convertisseur CPU/GPU d'e-book en livre audio avec chapitres et métadonnées<br/>
utilisant des moteurs TTS avancés et bien plus encore.<br/>
Prend en charge le clonage de voix et 1158 langues !
> [!IMPORTANT]
**Cet outil est destiné à être utilisé uniquement avec des e-books sans DRM, acquis légalement.** <br>
Les auteurs ne sont pas responsables d'une quelconque utilisation abusive de ce logiciel ni des conséquences juridiques qui en découleraient. <br>
Utilisez cet outil de manière responsable et dans le respect de toutes les lois applicables.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Merci de soutenir les développeurs d'ebook2audiobook !
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 

### Exécution locale

[![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   


<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Exécution à distance
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Interface graphique (GUI)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Cliquez pour voir les images de l'interface web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Démos

**Démo de la nouvelle voix par défaut**  

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Plus de démos</summary>

**Voix ASMR** 

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Voix jour de pluie**  

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Voix Scarlett**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**Voix David Attenborough** 

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Exemple**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## README.md

## Table des matières
- [ebook2audiobook](#-ebook2audiobook)
- [Fonctionnalités](#features)
- [Interface graphique](#gui-interface)
- [Démos](#demos)
- [Langues prises en charge](#supported-languages)
- [Configuration minimale requise](#hardware-requirements)
- [Utilisation](#instructions)
  - [Exécution locale](#instructions)
    - [Lancement de l'interface web Gradio](#instructions)
    - [Utilisation de base en mode headless](#basic-usage)
    - [Utilisation d'un modèle XTTS personnalisé en mode headless](#example-of-custom-model-zip-upload)
    - [Sortie de la commande d'aide](#help-command-output)
  - [Exécution à distance](#run-remotely)
  - [Docker](#docker)
    - [Étapes d'exécution](#docker)
    - [Problèmes Docker courants](#common-docker-issues)
  
- [Modèles TTS affinés](#fine-tuned-tts-models)
  - [Collection de modèles TTS affinés](#fine-tuned-tts-collection)
  - [Entraîner XTTSv2](#fine-tune-your-own-xttsv2-model)
- [Formats d'e-book pris en charge](#supported-ebook-formats)
- [Formats de sortie](#output-and-process-formats)
- [Revenir à une version antérieure](#reverting-to-older-versions)
- [Problèmes courants](#common-issues)
- [Remerciements particuliers](#special-thanks)
- [Table des matières](#table-of-contents)


## Fonctionnalités
- 🔧 **Moteurs TTS pris en charge** : `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- 📚 **Convertir plusieurs formats de fichier** : `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **Zone de texte** pour convertir directement un texte court en audio
- 🔍 **Reconnaissance OCR** pour les fichiers dont les pages de texte sont des images
- 🔊 **Synthèse vocale de haute qualité**, du quasi temps réel à une voix quasi naturelle
- 🗣️ **Clonage de voix optionnel** à l'aide de votre propre fichier vocal
- 🌐 **Prend en charge 1158 langues** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Adapté aux ressources limitées** — fonctionne avec **2 Go de RAM / 1 Go de VRAM (minimum)**
- 🎵 **Formats de sortie du livre audio** : mono or stereo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Balises SML prises en charge** — contrôle fin des coupures, pauses, changements de voix et plus encore ([see below](#sml-tags-available))
- 🧩 **Modèle personnalisé optionnel** utilisant votre propre modèle entraîné (XTTSv2, VITS, FAIRSEQ, PIPER, others on request)
- 🎛️ **Modèles préréglés affinés** entraînés par l'équipe E2A<br/>
     <i>(Contactez-nous si vous avez besoin de modèles affinés supplémentaires, ou si vous souhaitez partager les vôtres dans la liste officielle des préréglages)</i>


##  Configuration matérielle requise
- 2 Go de RAM min., 8 Go recommandés.
- 1 Go de VRAM min., 4 Go recommandés.
- Virtualisation activée si l'exécution se fait sous Windows (Docker uniquement).
- CPU, XPU (intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (CPU Apple Silicon)

*<i> Les moteurs TTS modernes sont très lents sur CPU, utilisez donc des TTS de moindre qualité comme YourTTS, Tacotron2, etc.</i>

## Langues prises en charge
| **Arabic (ar)**    | **Chinese (zh)**    | **English (en)**   | **Spanish (es)**   |
|:------------------:|:------------------:|:------------------:|:------------------:|
| **French (fr)**    | **German (de)**     | **Italian (it)**   | **Portuguese (pt)** |
| **Polish (pl)**    | **Turkish (tr)**    | **Russian (ru)**   | **Dutch (nl)**     |
| **Czech (cs)**     | **Japanese (ja)**   | **Hindi (hi)**     | **Bengali (bn)**   |
| **Hungarian (hu)** | **Korean (ko)**     | **Vietnamese (vi)**| **Swedish (sv)**   |
| **Persian (fa)**   | **Yoruba (yo)**     | **Swahili (sw)**   | **Indonesian (id)**|
| **Slovak (sk)**    | **Croatian (hr)**   | **Tamil (ta)**     | **Danish (da)**    |
- [**+1130 langues et dialectes ici**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)


## Formats d'e-book pris en charge
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Meilleurs résultats** : `.epub` ou `.mobi` pour la détection automatique des chapitres

## Formats de sortie et de traitement
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Le format de traitement peut être modifié dans lib/conf.py

## Balises SML disponibles
- `[break]` — silence (plage aléatoire **0.3–0.6 sec.**)
- `[pause]` — silence (plage aléatoire **1.0–1.6 sec.**)
- `[pause:N]` — pause fixe (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — changer de voix par rapport à la voix par défaut ou sélectionnée depuis l'interface graphique/CLI

**Consultez notre autre dépôt dédié à l'ajout automatique de SML dans votre e-book -> [E2A-SML](./components/E2A-SML)**

> [!IMPORTANT]
**Avant de publier un problème d'installation ou un bug, recherchez attentivement dans l'onglet des problèmes ouverts et fermés<br>
pour être sûr que votre problème n'existe pas déjà.**

>[!NOTE]
**Le format EPUB ne possède aucune structure standard définissant ce qu'est un chapitre, un paragraphe, une préface, etc.<br>
Vous devez donc d'abord supprimer manuellement tout texte que vous ne souhaitez pas convertir en audio.**


### Instructions 
1. **Clone repo**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Installer / Exécuter ebook2audiobook** :

   - **Linux/MacOS**  
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note for MacOS users: homebrew is installed to install missing programs.</i>
     
   - **Lanceur Mac**  
     Double-cliquez sur `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     or
     Double click `ebook2audiobook.cmd`

     <i>Note pour les utilisateurs Windows : scoop est installé afin d'installer les programmes manquants sans privilèges administrateur.</i>
   
1. **Ouvrir l'application web** : Cliquez sur l'URL fournie dans le terminal pour accéder à l'application web et convertir les e-books. `http://localhost:7860/`
2. **Pour un lien public** :
   `./ebook2audiobook.command --share` (Linux/MacOS)
   `ebook2audiobook.cmd --share` (Windows)
   `python app.py --share` (all OS)

> [!IMPORTANT]
**Si le script est arrêté puis relancé, vous devez actualiser votre interface graphique Gradio<br>
pour permettre à la page web de se reconnecter au nouveau socket de connexion.**

### Basic  Usage
   - **Linux/MacOS**:
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]** : Chemin vers votre fichier e-book
  - **[--voice]** : Chemin du fichier de clonage de voix (optionnel)
  - **[--language]** : Code de langue au format ISO-639-3 (ex. : ita pour l'italien, eng pour l'anglais, deu pour l'allemand...).<br>
    La langue par défaut est eng et --language est optionnel pour la langue par défaut définie dans ./lib/lang.py.<br>
    Les codes ISO-639-1 à 2 lettres sont également pris en charge.


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
     
- **<custom_model_path>** : Chemin vers le fichier `model_name.zip`,
      qui doit contenir (selon le moteur TTS) tous les fichiers obligatoires<br>
      (voir ./lib/models.py).

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

NOTE : en mode gradio/gui, pour annuler une conversion en cours, cliquez simplement sur le [X] du composant d'envoi d'e-book.
ASTUCE : s'il faut un peu plus de pause, ajoutez '[pause:3]' pour 3 sec., etc.

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
  
### Problèmes Docker courants
- Mon GPU NVIDIA n'est pas détecté ?? -> [Page wiki PROBLÈMES GPU](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

## Modèles TTS affinés (fine-tuned)
#### Affinez votre propre modèle XTTSv2

[Universal_TTS_Finetune](./components/Universal_TTS_Finetune) [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)


#### Débruiter les données d'entraînement

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


### Collection de modèles TTS affinés

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Pour un modèle personnalisé XTTSv2, un extrait audio de référence de la voix est obligatoire :

## Votre propre personnalisation d'Ebook2Audiobook
Vous êtes libre de modifier libs/conf.py pour ajouter ou supprimer les réglages souhaités. Si vous prévoyez de le faire, faites simplement
une copie du conf.py d'origine afin qu'à chaque mise à jour d'ebook2audiobook vous puissiez sauvegarder votre conf.py modifié et remettre
l'original. Vous devez prévoir le même processus pour models.py. Si vous souhaitez faire de votre propre modèle personnalisé
un modèle affiné officiel d'ebook2audiobook, contactez-nous et nous l'ajouterons à la liste des préréglages.

## Reverting to older Versions
Releases can be found -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

## Problèmes courants :
- Mon GPU NVIDIA/ROCm/XPU/MPS n'est pas détecté ?? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  Le CPU est lent (meilleur sur un CPU SMP de serveur) tandis que le GPU permet une conversion quasi en temps réel.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Il n'a cependant pas de clonage de voix zero-shot, et les voix sont de qualité Siri, mais c'est bien plus rapide sur CPU).
- « J'ai des problèmes de dépendances » - Utilisez simplement Docker, il est entièrement autonome et dispose d'un mode headless,
   ajoutez le paramètre `--help` à la fin de la commande docker run pour plus d'informations.
- « J'ai un problème d'audio tronqué ! » - VEUILLEZ OUVRIR UN ISSUE À CE SUJET,
   nous ne parlons pas toutes les langues et avons besoin des conseils des utilisateurs pour affiner la logique de découpage des phrases.😊

## ***** FEUILLE DE ROUTE *****
- Toutes les fonctionnalités ouvertes aux contributions publiques ⭐
- Toute aide de personnes parlant l'une des langues prises en charge pour nous aider à améliorer les modèles ⭐
- [x] Prévisualiser les blocs/chapitres avant de démarrer la conversion
- [ ] Édition par phrase convertie pour une modification chirurgicale du texte
- [x] Intégration des balises SML pour la voix, la pause, la coupure et d'autres changements 
- [x] Infos des paramètres -h -help dans différentes langues
- [x] Reconnaissance OCR pour PDF / JPG / BMP / PNG / TIFF
- [x] Dossier de notebooks [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Faire en sorte que le découpage du texte chinois ne coupe pas les mots et améliorer le timing des pauses [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker compose
- [x] Podman compose   
- [x] Notebook Kaggle
- [x] Notebook Google Colab
- [ ] [Créer une application iOS](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] [Créer une application Android](https://github.com/DrewThomasson/ebook2audiobook/pull/35#issuecomment-2496495212)
- [ ] Intégration Audiobookshelf

#### Options supplémentaires
- [x] Option de traduction de l'e-book
- [x] Choix du format de sortie
- [x] Traitement par lot d'un dossier d'e-books
- [x] Conversion en multitraitement
- [x] Conversion par lot d'un dossier d'e-books
- [x] Détection du périphérique GPU
- [x] Débruiter n'importe quel audio de référence pour le clonage de voix envoyé,
- [x] Envoi de modèle personnalisé (XTTSv2 uniquement pour l'instant. plus sur demande)
- [ ] Ajouter un modèle de langue portugais européen pour xttsv2, fairseq, vits, piper au minimum (aide bienvenue)
- [ ] Ajouter un modèle de langue sindhi pour xttsv2, fairseq, vits, piper au minimum (aide bienvenue)

#### Moteurs TTS
- [x] XTTSv2
- [x] Écorce
- [x] Fairseq
- [x] VITS
- [x] Tacotron2
- [x] YourTTS
- [x] Tortue terrestre
- [x] GlowTTS
- [x] Piper
- [ ] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [ ] fish-speech (https://github.com/fishaudio/fish-speech)
- [ ] ChatTTS (https://github.com/2noise/ChatTTS)
- [ ] CosyVoice (https://github.com/FunAudioLLM/CosyVoice)
- [ ] F5-TTS (https://github.com/swivid/f5-tts)
- [ ] chatterbox (https://github.com/resemble-ai/chatterbox)
- [ ] Supertonic (https://github.com/supertone-inc/supertonic)
- [ ] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [ ] index-tts (https://github.com/index-tts/index-tts)
- [ ] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [ ] Kokoro-TTS (https://github.com/hexgrad/kokoro)
- [ ] OmniVoice (https://github.com/k2-fsa/OmniVoice)
- [ ] Zonos (https://github.com/Zyphra/Zonos)
- [ ] Style-TTS2 (https://github.com/yl4579/StyleTTS2)
- [ ] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [ ] NewTTS (https://github.com/neuphonic/neutts?tab=readme-ov-file)
- [ ] VIbeVoice (https://github.com/vibevoice-community/VibeVoice)
- [ ] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)

#### Traduction du Readme
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

#### 🐍 Compatibilité des systèmes d'exploitation
- [x] 🍎 Mac Intel x86
- [x] 🪟 Windows x86
- [x] 🐧 Linux x86
- [x] 🖥️🍏 Apple Silicon Mac
- [x] 🪟💪 ARM Windows
- [x] 🐧💪 ARM Linux

**********

## Bonus ultime pour l'entraînement de modèles et plus encore (tous les modèles Coqui-tts pris en charge et piper-tts en une seule commande facile) 
- Pour plus d'infos à ce sujet, @DrewThomasson travaille actuellement à son développement, [dépôt en cours de développement ici](https://github.com/DrewThomasson/Universal_TTS_Finetune)
- [ ] Créer une interface d'entraînement facile à utiliser pour tous les modèles coqui-tts au format ljspeech [recettes d'entraînement de coqui tts ici](https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech)


## Informations de normalisation du code Python pour les contributeurs
- pas de ligne vide entre le code, sauf entre les fonctions et les classes.
- guillemet simple utilisé pour toutes les clés sauf pour dict() et json. dict['key'] toujours appelé avec un guillemet simple
- indentation de 4 espaces, pas de tabulation du tout
- typage strict pour toutes les fonctions ainsi que la déclaration de leurs arguments et valeurs de retour
- pas d'espace entre l'argument et son typage, pas d'espace entre la fonction, le « -> » et la valeur de retour

Exemple :

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

## Don de matériel pour les tests bêta recherché
Nous acceptons tout type de matériel pour tester notre développement, comme :
- Nvidia supporting cuda >= 11.8
- XPU intel cards
- ROCm AMD cards supporting ROCm >=5.7

@DrewThomasson si vous voulez aider de quelque manière que ce soit ! 😃
<!--
## Avez-vous besoin de louer un GPU pour booster notre service ?
- Un sondage est ouvert ici https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Remerciements particuliers
- **Coqui TTS**: [Coqui TTS GitHub](https://github.com/idiap/coqui-ai-TTS)
- **Calibre**: [Calibre Website](https://calibre-ebook.com)
- **FFmpeg**: [FFmpeg Website](https://ffmpeg.org)
- [@shakenbake15 pour une meilleure méthode de sauvegarde des chapitres](https://github.com/DrewThomasson/ebook2audiobook/issues/8) 
