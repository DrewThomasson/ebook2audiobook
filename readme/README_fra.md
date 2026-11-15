<a id="ebook2audiobook"></a>
# 📚 ebook2audiobook (E2A)
<a href="https://trendshift.io/repositories/12252?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-12252" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/12252" alt="DrewThomasson%2Febook2audiobook | Trendshift" width="250" height="55"/></a>

Convertisseur CPU/GPU de E-Book en livre audio avec chapitres et métadonnées<br/>
en utilisant des moteurs TTS avancés et bien plus encore.<br/>
Prend en charge le clonage vocal et 1696 langues !
> Important
**Cet outil est destiné à être utilisé uniquement avec des livres électroniques non MDR acquis légalement.** <br>
Les auteurs ne sont pas responsables de toute utilisation abusive de ce logiciel ou des conséquences juridiques qui en découlent. <br>
Utilisez cet outil de manière responsable et conformément à toutes les lois applicables.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Merci de soutenir les développeurs d'ebook2audiobook !
<p>
  <a href="https://ko-fi.com/athomasson2">
    <img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Ko-Fi">
  </a>
  <a href="https://secure.job-currency.com/_spec/short_r.php/0BJCp4">
    <img src="https://img.shields.io/badge/JOB-2E7D32?style=for-the-badge&logo=bitcoin&logoColor=white" alt="JOB">
  </a>
</p>

### Exécuter localement
Instructions [![Quick Start](https://img.shields.io/badge/Quick%20Start-blue?style=for-the-badge)
[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)   

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Platform-mac%20|%20linux%20|%20windows-lightgrey" alt="Platform">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

<a id="run-remotely"></a>
### exécuter à distance
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb) [![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

<a id="gui-interface"></a>
#### Interface GUI
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Cliquez pour voir les images de l'interface graphique Web</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

<a id="demos"></a>
## Démos

**Nouvelle démo vocale par défaut**

https://github.com/user-attachments/assets/750035dc-e355-46f1-9286-05c1d9e88cea  

<details>
  <summary>Plus de démos</summary>

**ASMR Voice**

https://github.com/user-attachments/assets/68eee9a1-6f71-4903-aacd-47397e47e422

**Rainy Day Voice**

https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080  

**Scarlett Voice**

https://github.com/user-attachments/assets/b12009ee-ec0d-45ce-a1ef-b3a52b9f8693

**David Attenborough Voice**

https://github.com/user-attachments/assets/81c4baad-117e-4db5-ac86-efc2b7fea921

**Exemple**

![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
</details>

## Lisezmoi.md

<a id="table-of-contents"></a>
## Table des matières
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
## Caractéristiques
- 🔧 **Moteurs TTS pris en charge** : `XTTSv2, Bark, Fairseq, VITS, Tacotron2, Tortoise, GlowTTS, YourTTS, Piper, Zonos, GPT-SoVITS, OmniVoice, Breeze TTS, Chatterbox, Confucius4 TTS, CosyVoice3, Dots TTS, DramaBox, FireRed Audio, FireRedTTS3, Fish Audio, Higgs Audio TTS, Index TTS2, Irodori TTS, Kokoro TTS, KugelAudio, Magpie TTS, Maya1, MioTTS, Moss TTS Local, Moss TTS Nano, NeuTTS, Pocket TTS, Qwen3 TTS, Supertonic, VibeVoice, VoxCPM2, Voxtral TTS, F5-TTS, Orpheus-TTS, ChatTTS, Spark-TTS, OpenVoice, MeloTTS`
- 📚 **Convertir plusieurs formats de fichiers** : `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.zip`
- 💻 **TextArea** pour convertir directement un texte court en audio
- 🔍 **Numérisation OCR** pour les fichiers avec des pages de texte en tant qu'images
- 🔊 **Du texte à la parole de haute qualité** de la voix en temps quasi réel à la voix en temps quasi réel
- 🗣️ **Clonage vocal facultatif** à l'aide de votre propre fichier vocal
- 🌐 **Prend en charge 1696 langues** ([supported languages list](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- 💻 **Adapté aux faibles ressources** — fonctionne sur **2 Go de RAM / 1 Go de VRAM (minimum)**
- 🎵 **Formats de sortie des livres audio** : mono ou stéréo `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- 🧠 **Tags SML pris en charge** — contrôle fin des pauses, des pauses, de la commutation vocale et plus encore ([see below](#sml-tags-available))
- 🧩 **Modèle personnalisé en option** en utilisant votre propre modèle formé (XTTSv2, VITS, FAIRSEQ, PIPER, autres sur demande)
- 🎛️ **Modèles prédéfinis affinés** formés par l'équipe E2A<br/>
     <i>(Contactez-nous si vous avez besoin de modèles affinés supplémentaires ou si vous souhaitez partager le vôtre avec la liste officielle des préréglages)</i>


<a id="hardware-requirements"></a>
##  Exigences Matérielles
- 2 Go de RAM minimum, 8 Go recommandés.
- 1 Go de VRAM minimum, 4 Go recommandés.
- Virtualisation activée si elle est exécutée sur Windows (Docker uniquement).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon CPU)

*<i> Les moteurs TTS modernes sont très lents sur le processeur, alors utilisez des TTS de qualité inférieure comme YourTTS, Tacotron2, etc.</i>

<a id="supported-languages"></a>
## Langues prises en charge
[+1696 languages here](SUPPORTED_LANGUAGES.md)


<a id="supported-ebook-formats"></a>
## Formats de livres électroniques pris en charge
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Meilleurs résultats** : `.epub` ou `.mobi` pour la détection automatique de chapitre

<a id="output-and-process-formats"></a>
## Formats de sortie et de processus
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Le format du processus peut être modifié dans lib/conf.py

## Balises SML disponibles
- `[break]` — silence (plage aléatoire **0,3-0,6 sec.**)
- `[pause]` — silence (plage aléatoire **1,0-1,6 sec.**)
- `[pause:N]` — pause fixe (**N sec.**)
- `[voice:/path/to/voice/file]...[/voice]` — changer la voix de la voix par défaut ou sélectionnée à partir de l'interface graphique/CLI
- `[emotion:sadness]...[/emotion]` — Zonos uniquement : émotion pour un passage (bonheur, tristesse, dégoût, peur, surprise, colère, autre, neutre) ou un mélange comme `[emotion:sadness=0.7,neutral=0.3]` ; d'autres moteurs l'ignorent

**Consultez notre autre dépôt dédié à l'ajout automatique de SML dans votre ebook -> [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> Important
**Avant de publier une recherche de problème d'installation ou de bogue avec soin dans l'ONGLET des problèmes ouverts et fermés<br>
pour vous assurer que votre problème n'existe pas déjà.**

REMARQUE
**Le format ePub n'a pas de structure standard telle qu'un chapitre, un paragraphe, une préface, etc.<br>
Vous devez donc d'abord supprimer manuellement tout texte que vous ne souhaitez pas convertir en audio.**


<a id="instructions"></a>
### Instructions
1. **Cloner le dépôt**
	```bash
	git clone https://github.com/DrewThomasson/ebook2audiobook.git
	cd ebook2audiobook
	```

2. **Installer / Exécuter ebook2audiobook** :

   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
     <i>Note pour les utilisateurs de MacOS : homebrew est installé pour installer les programmes manquants.</i>
     
   - **Lanceur Mac**
     Double clic `Mac Ebook2Audiobook Launcher.command`


   - **Windows**  
     ```bash
     ebook2audiobook.cmd
     ```
     ou
     Double-cliquez sur `ebook2audiobook.cmd`

     <i>Remarque pour les utilisateurs de Windows : scoop est installé pour installer les programmes manquants sans privilèges d'administrateur.</i>
   
1. **Ouvrez l'application Web** : cliquez sur l'URL fournie dans le terminal pour accéder à l'application Web et convertir les livres électroniques. `http://localhost:7860/`
2. **Pour le lien public** :
   `./ebook2audiobook.command --share` (Linux/MacOS)
   Windows. `ebook2audiobook.cmd --share`
   `python app.py --share` (tous les systèmes d'exploitation, uniquement une fois installé et avec le Python de son dossier python_env)

> Important
**Si le script est arrêté et exécuté à nouveau, vous devez actualiser votre interface graphique gradio<br>
pour permettre à la page Web de se reconnecter à la nouvelle prise de connexion.**

<a id="basic-usage"></a>
### Utilisation de base
   - **Linux/MacOS** :
     ```bash
     ./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <path_to_ebook_file> --voice <path_to_voice_file> --language <language_code>
     ```
     
  - **[--ebook]** : Chemin d'accès à votre fichier eBook
  - **[--voice]** : Chemin du fichier de clonage vocal (facultatif)
  - **[--language]** : Code de langue en ISO-639-3 (i.e. : ita pour l'italien, eng pour l'anglais, deu pour l'allemand...).<br>
    La langue par défaut est eng et --language est facultatif pour la langue par défaut définie dans ./lib/lang.py.<br>
    Les codes ISO-639-1 à 2 lettres sont également pris en charge.


<a id="example-of-custom-model-zip-upload"></a>
###  Exemple d'envoi d'un modèle personnalisé en zip
  (doit être un fichier .zip contenant les fichiers obligatoires du modèle. Exemple pour XTTSv2 : config.json, model.pth, vocab.json et ref.wav)
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --headless --ebook <ebook_file_path> --language <language> --custom_model <custom_model_path>
     ```
     <i>Remarque : le ref.wav de votre modèle personnalisé est toujours la voix sélectionnée pour la conversion</i>
     
- **<custom_model_path>** : chemin du fichier `model_name.zip`,
      qui doit contenir (selon le moteur tts) tous les fichiers obligatoires<br>
      (voir ./lib/models.py).

### Guide détaillé avec la liste de tous les paramètres utilisables
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command --help
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd --help
     ```
   - **Ou pour tous les systèmes d'exploitation**
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

REMARQUE : en mode gradio/gui, pour annuler une conversion en cours, cliquez simplement sur le [X] du composant de téléchargement de livre électronique.
ASTUCE : s'il faut une pause plus longue, ajoutez '[pause:3]' pour 3 s, etc.

<a id="docker"></a>
### Docker
1. **Cloner le dépôt** :
```bash
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
   cd ebook2audiobook
```
2. **Construire le conteneur**
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
4. **Lancer le conteneur :**
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
- REMARQUE : MPS n'est pas exposé dans Docker, le CPU doit donc être utilisé
- REMARQUE : le volume nommé `e2a_venvs` conserve les moteurs TTS installés dans leur propre venv (GPT-SoVITS, Zonos, OmniVoice, F5-TTS, Orpheus, Spark-TTS, ChatTTS, OpenVoice, MeloTTS, CSM, etc.)
  d'une exécution du conteneur à l'autre, ils ne sont donc pas réinstallés à chaque fois. Pour les réinitialiser : `docker volume rm e2a_venvs`

<a id="tools"></a>
## Outils
Outils autonomes, exécutés avec le Python propre à e2a (`python_env`, créé au premier lancement d'e2a).

<a id="preload-models"></a>
### Précharger les modèles pour les installations hors ligne : `tools/preload_models.py`
Télécharge tous les modèles utilisés par e2a (moteurs TTS et leurs fine-tunes, conversion de voix, stanza, pyannote, demucs,
interludes musicaux, paquets argos-translate, données tesseract, jieba, et les voix) dans un seul dossier organisé
exactement comme `./models`, par exemple sur une clé USB. Sur la machine hors ligne, copiez ce dossier dans `./models` d'e2a
et le dossier `voices` écrit à côté dans `./voices` d'e2a.
Chaque tâche terminée est enregistrée dans `<models_dir>/.e2a_downloads.json` : une nouvelle exécution saute ce qui est fait et relance
ce qui a été interrompu (ctrl-c, plantage, clé débranchée) après avoir supprimé ses fichiers partiels.
   - **Linux/MacOS**
     ```bash
     ./python_env/bin/python tools/preload_models.py /media/user/KEY/models --languages eng,fra
     ```
   - **Windows**
     ```bash
     python_env\Scripts\python.exe tools\preload_models.py E:\models --languages eng,fra
     ```
   - `--dry_run` liste les tâches et leur état (terminée, interrompue, en attente) sans rien télécharger.

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
### Traduire des ebooks hors d'e2a : `tools/translate_ebook.sh` / `tools/translate_ebook.cmd`
Traduit des fichiers EPUB/AZW3, un dossier entier (`-r` pour ses sous-dossiers) ou une liste de chemins (`@list.txt`)
en ebooks traduits, hors ligne, avec le plugin calibre Argos Translate fourni dans
`tools/argostranslate-calibre-plugin.zip`. Indépendant de la conversion en livre audio : il n'écrit que des ebooks.
Il nécessite calibre (déjà requis par e2a) et utilise le `python_env` et les paquets argos-translate d'e2a :
une paire de langues déjà utilisée par e2a n'est pas retéléchargée, une paire manquante est téléchargée à la première utilisation.
Le plugin est installé à la première utilisation dans le profil calibre propre à e2a (`./run`), votre calibre reste intact.
`--to fra,ara,spa` traduit en plusieurs langues à la fois, un ebook par langue, et `--to all` dans toutes les
langues atteintes depuis la source (`--from`, sinon la langue de chaque livre ; seulement les paires installées avec `--no_download`).
`--list --from eng` liste les langues vers lesquelles l'anglais traduit (installées, téléchargeables, ou via l'anglais pour
une autre source).
Les autres formats lus par `ebook-convert` de calibre (PDF, DOCX, MOBI, TXT, ...) sont convertis une seule fois en EPUB, avant la
première langue, puis traduits en EPUB : `--from` est nécessaire quand ils n'indiquent aucune langue, comme souvent les PDF et TXT.
Sans `-o` ni `--output_dir`, chaque traduction est enregistrée à côté de son livre sous `<name>.<lang>.<ext>`,
et un livre dont la traduction existe déjà est ignoré (`--overwrite` pour le traduire à nouveau).
Les lanceurs du dossier `tools/` exécutent `tools/translate_ebook.py` avec `python_env`, rien à activer,
depuis n'importe quel dossier (les chemins relatifs partent de l'endroit où il est lancé) :
   - **Linux/MacOS**
     ```bash
     ./tools/translate_ebook.sh /path/to/books -r --to fra,spa --output_dir /path/to/books_translated
     ```
   - **Windows**
     ```bash
     tools\translate_ebook.cmd C:\books -r --to fra,spa --output_dir C:\books_translated
     ```
   - Ou directement avec le Python de `python_env` : `./python_env/bin/python tools/translate_ebook.py ...`
     (Windows : `python_env\Scripts\python.exe tools\translate_ebook.py ...`). Lancé avec un autre Python,
     le script se relance lui-même avec celui de `python_env`.
   - **Docker** : exécutez-le dans le conteneur e2a, par ex. `docker exec -it <container> python3 tools/translate_ebook.py ...`
     avec les chemins vus depuis le conteneur.
   - **Vitesse** : argostranslate utilise ses propres réglages par défaut (CTranslate2 choisit les threads et le type de calcul le plus rapide,
     int8 sur CPU), et non le thread unique en float32 d'e2a. Définissez `ARGOS_INTRA_THREADS` ou `ARGOS_COMPUTE_TYPE` pour les remplacer.

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
## Voix clonées
Vous pouvez télécharger n'importe quel audio vocal dans n'importe lequel des formats audio pris en charge, la durée idéale est d'environ 1 à 5 min.
Peu importe si l'enregistrement a un fond bruyant ou de la musique qui y joue — E2A nettoiera la voix pour vous.

La liste des voix clonées intégrée est principalement en anglais. Si vous avez besoin de voix dans d'autres langues pour être officiellement
ajouté à la liste, veuillez nous contacter et nous les ajouterons après vérification.

<a id="fine-tuned-tts-models"></a>
## Modèles TTS affinés
<a id="fine-tune-your-own-tts-model"></a>
#### Affinez votre propre modèle TTS

[Universal_TTS_Finetune](https://github.com/DrewThomasson/Universal_TTS_Finetune)

#### Données d'entraînement au débruitage

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit) [![GitHub Repo](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)


<a id="fine-tuned-tts-collection"></a>
### Collection TTS affinée

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Pour un modèle personnalisé XTTSv2, un clip audio de référence de la référence vocale est obligatoire :

## Votre propre personnalisation Ebook2Audiobook
Vous êtes libre de modifier libs/conf.py pour ajouter ou supprimer les paramètres que vous souhaitez. Si vous prévoyez de le faire, faites simplement
une copie du fichier conf.py original, donc à chaque mise à jour de ebook2audiobook, vous sauvegarderez votre fichier conf.py modifié et mettrez
revenir à l'original. Vous devez planifier le même processus pour models.py. Si vous souhaitez créer votre propre modèle personnalisé
en tant que modèle officiel ebook2audiobook affiné, veuillez nous contacter et nous l'ajouterons à la liste des préréglages.

<a id="reverting-to-older-versions"></a>
## Revenir à une version antérieure
Les versions publiées sont disponibles -> [here](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/VERSION_NUM # Locally/Compose -> Example: git checkout tags/v25.7.7
```

<a id="common-issues"></a>
## Questions courantes :
- Mon GPU NVIDIA/ROCm/XPU/MPS n'est pas détecté ? ? -> [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
-  Le processeur est lent (mieux sur le processeur smp du serveur) tandis que le GPU peut avoir une conversion presque en temps réel.
   [Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
   (Il n'y a pas de clonage de voix à zéro, et il s'agit de voix de qualité Siri, mais c'est beaucoup plus rapide sur le processeur).
- "J'ai des problèmes de dépendances" - Utilisez simplement Docker, il est entièrement autonome et dispose d'un mode headless,
   ajoutez le paramètre `--help` à la fin de la commande docker run pour plus d'informations.
- « Je reçois un problème audio tronqué ! « - S'IL VOUS PLAÎT FAIRE UN PROBLÈME À CE SUJET,
   nous ne parlons pas toutes les langues et avons besoin des conseils des utilisateurs pour affiner la logique de fractionnement des phrases.😊

## Feuille de route
- Toutes les fonctionnalités ouvertes aux contributions publiques ⭐
- Toute aide de personnes parlant l'une des langues prises en charge pour nous aider à améliorer les modèles ⭐
- [x] Prévisualisez les blocs/chapitres avant de commencer la conversion
- [x] Modifier par phrase convertie pour le changement de texte chirurgical
- [x] Générer des intros de musique, des intermèdes et des fins ; éditer les intermèdes et les fins
- [x] Intégration de balises SML pour la voix, la pause, la pause et d'autres modifications
- [x] -h -help informations sur les paramètres dans différentes langues
- [x] Numérisation OCR pour PDF / JPG / BMP / PNG / TIFF
- [x] Dossier des blocs-notes [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/5#issuecomment-2408773254)
- [x] Faire en sorte que le fractionnement du texte chinois ne divise pas les mots et améliore la synchronisation des pauses [Talked about here](https://github.com/DrewThomasson/ebook2audiobookXTTS/issues/18#issuecomment-2401154894)
- [x] Dockerfile
- [x] Docker Compose
- [x] Podman compose
- [x] Carnet Kaggle
- [x] Bloc-notes Google Colab
- [x] Intégration Audiobookshelf
- [x] Option Traduction de livre électronique
- [x] Choix du format de sortie
- [x] Conversion multiprocesseur
- [x] Conversion par lots du dossier ebook
- [x] Détection des dispositifs
- [x] Dénoisez tout son de référence d'arrière-plan pour le téléchargement de clonage vocal
- [x] Téléchargement personnalisé du modèle affiné

#### Demandes utilisateur
- [ ] Ajouter un modèle de langue portugaise européenne pour xttsv2, fairseq, vits, piper au moins (aide bienvenue)
- [ ] Ajouter un modèle en langue sindhi pour xttsv2, fairseq, vits, piper au moins (aide bienvenue)

#### Moteurs TTS
- [x] DramaBox (https://github.com/dramabox-ai/dramabox)[cite: 1]
- [x] Audio FireRed/ FireRedTTS3 (https://github.com/FireRedTeam/FireRedTTS)[cite: 1]
- [x] Voix de poisson/Audio de poisson (https://github.com/fishaudio/fish-speech)[cite: 1]
- [x] Higgs Audio TTS (https://github.com/higgs-audio/higgs-audio)[cite: 1]
- [x] Maya1 (https://github.com/maya-ai/maya1)[cite: 1]
- [x] OmniVoice (https://github.com/k2-fsa/OmniVoice)[cite: 1]
- [x] F5-TTS (https://github.com/swivid/f5-tts)[cite: 1]
- [x] Qwen3-TTS (https://huggingface.co/spaces/Qwen/Qwen3-TTS)[cite: 1]
- [x] VibeVoice (https://github.com/vibevoice-community/VibeVoice)[cite: 1]
- [x] VoxCPM2 (https://github.com/voxcpm/voxcpm)[cite: 1]
- [x] Voxtral TTS (https://github.com/voxtral/voxtral-tts)[cite: 1]
- [x] Chatterbox (https://github.com/resemble-ai/chatterbox)[cite: 1]
- [x] CosyVoice / CosyVoice3 (https://github.com/FunAudioLLM/CosyVoice)[cite: 1]
- [x] Indice-tts / Indice TTS2 (https://github.com/index-tts/index-tts)[cite: 1]
- [x] XTTSv2 (https://github.com/coqui-ai/XTTS)[cite: 1]
- [x] Breeze TTS (https://github.com/FreedomIntelligence/Breeze-TTS)[cite: 1]
- [x] Confucius4 TTS (https://github.com/confucius-tts/confucius4)[cite: 1]
- [x] Points TTS (https://github.com/dot-audio/dots-tts)[cite: 1]
- [x] GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)[cite: 1]
- [x] Kokoro-TTS (https://github.com/hexgrad/kokoro)[cite: 1]
- [x] KugelAudio (https://github.com/kugel-audio/kugelaudio)[cite: 1]
- [x] Magpie TTS (https://github.com/magpie-tts/magpie-tts)[cite: 1]
- [x] MioTTS (https://github.com/mio-tts/miotts)[cite: 1]
- [x] Moss TTS Local / Nano (https://github.com/OpenBMB/MossTTS)[cite: 1]
- [x] NewTTS / NeuTTS (https://github.com/neuphonic/neutts)[cite: 1]
- [x] Pocket TTS (https://github.com/pocket-tts/pocket-tts)[cite: 1]
- [x] Gradium Phonon (https://github.com/gradium-ai/xn-ptts)[cite: 1]
- [x] Supertonique (https://github.com/supertone-inc/supertonic)[cite: 1]
- [x] Irodori TTS (https://github.com/irodori-tts/irodori-tts)[cite: 1]
- [x] Piper (https://github.com/rhasspy/piper)[cite: 1]
- [x] VITS (https://github.com/jaywalnut330/vits)[cite: 1]
- [x] Fairseq (https://github.com/facebookresearch/fairseq)[cite: 1]
- [x] GlowTTS (https://github.com/jaywalnut330/glow-tts)[cite: 1]
- [x] Tacotron2 (https://github.com/NVIDIA/Tacotron2)[cite: 1]
- [x] Tortue (https://github.com/neonbjb/tortoise-tts)[cite: 1]
- [x] Zonos (https://github.com/Zyphra/Zonos)[cite: 1]
- [x] Écorce (https://github.com/suno-ai/bark)[cite: 1]
- [x] YourTTS (https://github.com/Edresson/YourTTS)[cite: 1]
- [x] Orpheus-TTS (https://github.com/canopyai/Orpheus-TTS)
- [x] OpenVoice (https://github.com/myshell-ai/OpenVoice)
- [x] ChatTTS (https://github.com/2noise/ChatTTS)
- [x] Spark-TTS (https://github.com/sparkaudio/spark-tts)
- [x] MeloTTS (https://github.com/myshell-ai/MeloTTS)
- [x] Gestion de la réussite des clients 0 https://github.com/SesameAILabs/csm)

#### Readme Translation
- [x] Arabe (ara)
- [x] Chinois (zho)
- [x] FRANCAIS (FR)
- [x] Espagnol (spa)
- [x] Français (FRA)
- [x] Allemand (deu)
- [x] Italien (ita)
- [x] Portugais (por)
- [x] Polonais (POL)
- [x] Turc (tur)
- [x] Russe (rus)
- [x] Néerlandais (nld)
- [x] Tchèque (ces)
- [x] Japonais (JPN)
- [x] Hindi (hin)
- [x] Bengali (ben)
- [x] Hongrois - HUN
- [x] Coréen (kor)
- [x] Vietnamien (vie)
- [x] Suédois (swe)
- [x] Persan (fas)
- [x] Yoruba (yor)
- [x] Swahili (swa)
- [x] Indonésien (ind)
- [x] Slovaque (slovaque)
- [x] Croate (hrv)

#### OS compatibles
- [x] 🪟 Windows x86
- [x] Fenêtres 🪟 DE BRAS
- [x] 🍎 Mac Intel x86
- [x] 🍎 Apple Silicon Mac
- [x] 🐧 Linux x86
- [x] 🐧 ARM LINUX

**********

<a id="contributing"></a>
## Contribuer
Avant d'ouvrir un ticket ou une demande d'extraction, lisez [CONTRIBUTING.md](https://github.com/DrewThomasson/ebook2audiobook/blob/main/CONTRIBUTING.md) : Règles de normalisation du code Python,
flux de travail de demande de branchement et de tirage, légendes de l'interface graphique et traductions README, ajout d'un moteur TTS, test.

## Don de matériel pour les tests bêta recherchés
Nous acceptons tout type de matériel pour tester notre développement comme :
- Nvidia soutenant cuda >= 11,8
- Cartes intel XPU
- Cartes ROCm AMD prenant en charge ROCm >=5,7

@ DrewThomasson si vous voulez vraiment aider ! 😃
<!--
## Avez-vous besoin de louer un GPU pour améliorer le service de notre part ?
- Un sondage est ouvert ici https://github.com/DrewThomasson/ebook2audiobook/discussions/889
-->

## Crédits
- [Coqui-tts](https://github.com/idiap/coqui-ai-TTS) - Une boîte à outils d'apprentissage en profondeur pour la synthèse vocale, testée au combat dans la recherche et la production.
- [Piper-tts](https://github.com/OHF-Voice/piper1-gpl) -- Moteur de synthèse vocale neuronal rapide et local.
- [Zonos2.cpp](https://github.com/Zyphra/zonos2.cpp) -- code d'inférence ggml pour Zonos2.
- [Audio.cpp](https://github.com/0xShug0/audio.cpp) - Un moteur d'inférence C++ pur tout-en-un pour les modèles audio, alimenté par ggml.

<a id="special-thanks"></a>
## Remerciements particuliers
Pour tous les contributeurs financiers et de code, chaque contribution et suggestion contribue à améliorer la qualité d'E2A.