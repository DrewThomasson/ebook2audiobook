📚 eBook2Audiobook
CPU/GPU Converter from eBooks to audiobooks with chapters and metadata<br/>
Convertisseur CPU / GPU des ebooks aux livres audio avec des chapitres et des métadonnées <br/>
Utilisation de calibre, FFMPEG, XTSTV2, FAIRSEQ et plus encore. Prend en charge le clonage vocal et +1110 langues! [!IMPORTANT]
** Cet outil est destiné à être utilisé avec des livres électroniques non DRM, acquis légalement. ** <br>
Les auteurs ne sont pas responsables de toute utilisation abusive de ce logiciel ou de toute conséquence juridique qui en résulte. <br>
Utilisez cet outil de manière responsable et conformément à toutes les lois applicables. [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

[! [Ko-fi] (https://img.shields.io/badge/ko--fi-f16061?style=for-The-Badge&logo=ko-fi&logocolor=white)] (https: // ko-fi .com / Athomasson2)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2) 


! [Demo_Web_Gui] (Assets / Demo_web_Gui.gif)
![demo_web_gui](assets/demo_web_gui.gif)

<details>
ara [العربية (arabe)] (./ readme / readme_ar.md)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
zho [中文 (chinois)] (./ readme / readme_cn.md)
</details>


## README.md
- ara [العربية (Arabic)](./readme/README_AR.md)
swe [svenska (suédois)] (./ readme / readme_swe.md)
- eng [English](README.md)
- swe [Svenska (Swedish)](./readme/README_SWE.md)
fas [فارسی (persan)] (./ readme / readme_fa.md)


## Table of Contents
[eBook2Audiobook] (# - eBook2Audiobook)
- [Features](#features)
- [Docker GUI Interface](#docker-gui-interface)
[Fonctionnalités] (# fonctionnalités)
- [Free Google Colab](#free-google-colab)
- [Pre-made Audio Demos](#demos)
[Interface Docker GUI] (# docker-Gui-interface)
- [Requirements](#hardware-requirements)
- [Installation Instructions](#installation-instructions)
[HuggingFace Space Demo] (# HuggingFace-Space-Demo)
  - [Launching Gradio Web Interface](#launching-gradio-web-interface)
  - [Basic Headless Usage](#basic--usage)
[Google Colab gratuit] (# Free-Google-Colab)
  - [Renting a GPU](#renting-a-gpu)
  - [Help command output](#help-command-output)
[Démos audio pré-faites] (# démos)
  - [For Collection of Fine-Tuned TTS Models](#fine-tuned-tts-collection)
- [Using Docker](#using-docker)
[Langages pris en charge] (# pris en charge)
  - [Docker Build](#building-the-docker-container)
  - [Docker Compose](#docker-compose)
[Exigences] (# exigences matérielles)
  - [Docker container file locations](#docker-container-file-locations)
  - [Common Docker issues](#common-docker-issues)
[Instructions d'installation] (# Installation-instructions)
- [Output](#output)
- [Common Issues](#common-issues)
[Utilisation] (# Lancement-Gradio-Web-Interface)
- [Join Our  Server!](#join-our--server)
- [Legacy](#legacy-v10)
[Lancement d'interface Web Gradio] (# Lancement-Gradio-Web-Interface)


[Utilisation sans tête sans tête] (# Basic - Usage)
- 📖 Converts eBooks to text format with Calibre.
- 📚 Splits eBook into chapters for organized audio.
[Utilisation du modèle XTTS personnalisé sans headles
- 🗣️ Optional voice cloning with your own voice file.
- 🌍 Supports +1110 languages (English by default). [List of Supported languages](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
[Location d'un GPU] (# Rentative-a-GPU)


[Help Command Output] (# Help-Command-Output)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
- Huggingface space is running on free cpu tier so expect very slow or timeout lol, just do not give it giant files is all
[Modèles TTS à réglage fin] (# modes de TTS fins))


[Pour la collecte de modèles TTS fins] (# Fined-tts-TTS-Collection)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)


## Supported Languages
- **Arabic (ara)**
[Docker Run] (# Runn-the-Docker-Container)
- **Czech (ces)**
- **Croatian (hrv)**
[Docker Build] (# Building-the-Docker-Container)
- **English (eng)**
- **French (fra)**
[Docker Compose] (# docker-compose)
- **Hindi (hin)**
- **Hungarian (hun)**
[Guide Docker Headless] (# Docker-Headless-Guide)
- **Japanese (jpn)**
- **Korean (kor)**
[Docker Container File Locations] (# Docker-Container-File-Locations)
- **Portuguese (por)**
- **Russian (rus)**
[Problèmes de docker communs] (# Common-Docker-Issues)
- **Turkish (tur)**
- **Vietnamese (vie)**
[Formats de livres électroniques pris en charge] (# pris en charge-ebook-formats)


[Sortie] (# sortie)
- 4gb RAM minimum, 8GB recommended
- Virtualization enabled if running on windows (Docker only)
[Problèmes communs] (# Common-Issues)


[Merci spécial] (# spécial-merci)
**Before to post an install or bug issue search carefully to the opened and closed issues TAB<br>
to be sure your issue does not exist already.**


>[!NOTE]
[Legacy] (# Legacy-V10)
you should first remove manually any text you don't want to be converted in audio.**


### Installation Instructions
Caractéristiques
```bash
📖 Convertit les livres électroniques en format texte avec calibre. 📚 Divise Ebook en chapitres pour l'audio organisé. 🎙️ Text-to-speech de haute qualité avec [coqui xttsv2] (https://huggingface.co/coqui/xts-v2) et [Fairseq] (https://github.com/facebookresearch/fairseq/tree/main/ Exemples / MMS) (et plus). 🗣️ Clonage vocal facultatif avec votre propre fichier vocal. 🌍 prend en charge +1110 langues (anglais par défaut). [Liste des langues prises en charge] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
```

🖥️ Conçu pour fonctionner sur 4 Go de RAM. [Huggingface Space Demo] (https://huggingface.co/spaces/drewthomasson/ebook2audiobook)
1. **Run ebook2audiobook**:
[! [Face étreint] (https://img.shields.io/badge/hugging%20face spaces-yellow? / eBook2Audiobook)
     ```bash
     ./ebook2audiobook.sh  # Run Launch script
HuggingFace Space fonctionne sur le niveau CPU gratuit, alors attendez-vous à très lent ou à délai lol, ne lui donnez pas des fichiers géants est tout
   - **Windows**
     ```bash
Mieux vaut dupliquer l'espace ou fonctionner localement. Google Colab gratuit
     ```
[! [Google Colab gratuit] (https://colab.research.google.com/assets/colab-badge.svg)] (https://colab.research.google.com/github/drewthomasson/ebook2audiobook/blob/ Main / Notebooks / colab_ebook2audiobook.ipynb)
3. **For Public Link**:
Langues prises en charge
   `./ebook2audiobook.sh --share` (Linux/MacOS)
** Arabe (Ara) **

> [!IMPORTANT]
** Chinois (Zho) **
to let the web page reconnect to the new connection socket.**

** tchèque (CES) **
   - **Linux/MacOS**:
     ```bash
** Croate (HRV) **
         --voice [path_to_voice_file] --language [language_code]
     ```
** Dutch (NLD) **
     ```bash
     .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
** Anglais (Eng) **
     ```
     
** français (Fra) **
  - **[--voice]**: Voice cloning file path (optional).
  - **[--language]**: Language code in ISO-639-3 (i.e.: ita for italian, eng for english, deu for german...).<br>
** allemand (DEU) **
    The ISO-639-1 2 letters codes are also supported.


###  Example of Custom Model Zip Upload
  (must be a .zip file containing the mandatory model files. Example for XTTS: config.json, model.pth, vocab.json and ref.wav)
** hongrois (hun) **
     ```bash
     ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
** italien (ita) **
     ```
   - **Windows**
** Japonais (JPN) **
     .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
         --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
** Corée (Kor) **
- **<custom_model_path>**: Path to `model_name.zip` file,
      which must contain (according to the tts engine) all the mandatory files<br>
** Polonais (Pol) **


** Portugais (POR) **
   - **Linux/MacOS**
     ```bash
** Russe (RUS) **
     ```
   - **Windows**
** Espagnol (spa) **
     .\ebook2audiobook.cmd --help
     ```
** turc (tur) **
    ```python
     app.py --help
** Vietnamien (Vie) **

<a id="help-command-output"></a>
[** +1100 langues via Fairseq **] (https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
usage: app.py [-h] [--script_mode SCRIPT_MODE] [--session SESSION] [--share]
Exigences matérielles
              [--language LANGUAGE] [--voice VOICE] [--device {cpu,gpu,mps}]
4 Go de RAM minimum, 8 Go recommandé
              [--custom_model CUSTOM_MODEL] [--fine_tuned FINE_TUNED]
              [--output_format OUTPUT_FORMAT] [--temperature TEMPERATURE]
Virtualisation activée si elle s'exécute sur Windows (Docker uniquement)
              [--repetition_penalty REPETITION_PENALTY] [--top_k TOP_K] [--top_p TOP_P]
              [--speed SPEED] [--enable_text_splitting] [--output_dir OUTPUT_DIR]
CPU, GPU (recommandé), MPS (pas encore optimisé et peut être plus lent que le CPU)

Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.

11
Pour être sûr que votre problème n'existe pas déjà. **
  --session SESSION     Session to resume the conversion in case of interruption, crash, 
                            or reuse of custom models and custom cloning voices.

** Manque d'une structure de normes comme ce qui est un chapitre, un paragraphe, une préface, etc. <br>
Vous devez d'abord supprimer manuellement n'importe quel texte que vous ne souhaitez pas être converti en audio. **

Instructions d'installation

** Clone Repo **
  --headless            Run the script in headless mode
Lancement d'interface Web Gradio
  --ebooks_dir EBOOKS_DIR
** Exécutez eBook2Audiobook **:
                            Cannot be used when --ebook is present.
  --language LANGUAGE   Language of the e-book. Default language is set 
** Linux / macOS **

optional parameters:
** Windows **
                            Uses the default voice if not present.
  --device {cpu,gpu,mps}
** Ouvrez l'application Web **: Cliquez sur l'URL fournie dans le terminal pour accéder à l'application Web et convertir les livres électroniques. ** Pour le lien public **:
`python app.py --share` (tous les os)
`./ebook2audiobook.sh --share` (Linux / macOS)
`eBook2Audiobook.cmd --hare` (Windows)
                            Default depends on the selected language. The tts engine should be compatible with the chosen language
  --custom_model CUSTOM_MODEL
[!IMPORTANT]
** Si le script est arrêté et en cours d'exécution, vous devez actualiser votre interface Gradio GUI <br>
Pour laisser la page Web se reconnecter à la nouvelle prise de connexion. **
                        (Optional) Fine tuned model path. Default is builtin model.
Utilisation de base
                        (Optional) Output audio format. Default is set in ./lib/conf.py
** Linux / macOS **:
                        (xtts only, optional) Temperature for the model. 
                            Default to config.json model. Higher temperatures lead to more creative outputs.
** Windows **
                        (xtts only, optional) A length penalty applied to the autoregressive decoder. 
                            Default to config.json model. Not applied to custom models.
** [- ebook] **: Chemin vers votre fichier eBook. ** [- Voice] **: Chemin de fichier de clonage vocal (facultatif). ** [- Langue] **: Code linguistique dans ISO-639-3 (c'est-à-dire: ita pour italien, eng For English, Deu pour allemand ...). <br>
La langue par défaut est Eng et --Language est facultative pour le jeu de langues par défaut dans ./lib/lang.py. <br>
Les codes ISO-639-1 2 lettres sont également pris en charge. Exemple de téléchargement de zip de modèle personnalisé
  --repetition_penalty REPETITION_PENALTY
(Doit être un fichier .zip contenant les fichiers de modèle obligatoires. Exemple pour XTTS: config.json, model.pth, vocab.json et ref.wav)
                            Default to config.json model.
  --top_k TOP_K         (xtts only, optional) Top-k sampling. 
** Linux / macOS **
                            Default to config.json model.
  --top_p TOP_P         (xtts only, optional) Top-p sampling. 
** Windows **
  --speed SPEED         (xtts only, optional) Speed factor for the speech generation. 
                            Default to config.json model.
11
    qui doit contenir (selon le moteur TTS) tous les fichiers obligatoires <br>
    (Voir ./lib/models.py). Pour un guide détaillé avec la liste de tous les paramètres à utiliser
  --output_dir OUTPUT_DIR
** Linux / macOS **
  --version             Show the version of the script and exit

** Windows **
Windows:
    Gradio/GUI:
** ou pour tous les os **
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
<a id = "Help-Command-sortie"> </a>
    Gradio/GUI:
    ./ebook2audiobook.sh
Remarque: En mode Gradio / GUI, pour annuler une conversion en cours d'exécution, cliquez simplement sur le composant [x] du livre de téléchargement du livre électronique. Utilisation de Docker
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
Vous pouvez également utiliser Docker pour exécuter le convertisseur Ebook to Audiobook. Cette méthode garantit la cohérence dans différents environnements et simplifie la configuration. Exécution du conteneur Docker

Pour exécuter le conteneur Docker et démarrer l'interface Gradio, utilisez la commande suivante:

### Using Docker
-Run avec CPU uniquement
This method ensures consistency across different environments and simplifies setup.


#### Running the Docker Container
Construire le conteneur Docker

Vous pouvez créer l'image Docker avec la commande:
```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
Cette commande démarrera l'interface Gradio sur le port 7860. (LocalHost: 7860)
 -Run with GPU Speedup (NVIDIA compatible only)
```powershell
Pour plus d'options, ajoutez le paramètre `- help`
```


Tous les eBook2Audiobooks auront le dir de base de `/ home / user / app /`
Par exemple:
`tmp` =` / home / user / app / tmp`
`AudioRoBooks` =` / Home / User / App / AudioBooks`
```
Guide Docker Headless
- For more options add the parameter `--help`


## Docker container file locations
Avant d'exécuter ceci, vous devez créer un DIR nommé "Input-Folder" dans votre Dir actuel
Ce qui sera lié, c'est là que vous pouvez mettre vos fichiers d'entrée pour l'image Docker pour voir
`tmp` = `/home/user/app/tmp`
`audiobooks` = `/home/user/app/audiobooks`


## Docker headless guide
Et ça devrait être ça! Les livres audio de sortie se trouvent dans le dossier des livres audio qui seront également situés
Dans votre Dir local, vous avez dirigé cette commande docker dans
docker pull athomasson2/ebook2audiobook
Pour obtenir la commande d'aide pour les autres paramètres de ce programme, vous pouvez exécuter ceci
- Before you do run this you need to create a dir named "input-folder" in your current dir
Et cela sortira ceci 
[Help Command Output] (# Help-Command-Output)
mkdir input-folder && mkdir Audiobooks
Docker
- In the command below swap out **YOUR_INPUT_FILE.TXT** with the name of your input file 
Ce projet utilise Docker Compose pour s'exécuter localement. Vous pouvez activer ou désactiver le support GPU 
En définissant `* gpu-compatible` ou` * gpu-disabled` dans `docker-compose.yml`
    -v $(pwd)/input-folder:/home/user/app/input_folder \
Étapes pour fonctionner
    athomasson2/ebook2audiobook \
** Clone le référentiel ** (si vous ne l'avez pas déjà fait):
```
- And that should be it! 
** Définir la prise en charge du GPU (désactivé par défaut) **
Pour activer la prise en charge du GPU, modifiez `docker-compose.yml` et modifiez` * GPU-Disabled` vers `* GPU-compatible`


** Démarrez le service: **

```bash
** Accédez au service: **

```
! [Demo_Web_Gui] (Assets / Demo_web_Gui.gif)
[Help command output](#help-command-output)


Vous n'avez pas le matériel pour l'exécuter ou vous souhaitez louer un GPU? Vous pouvez dupliquer l'espace Hugginface et louer un GPU pour environ 0,40 $ l'heure
This project uses Docker Compose to run locally. You can enable or disable GPU support 
[HuggingFace Space Demo] (# HuggingFace-Space-Demo)


[Google Colab gratuit] (# Free-Google-Colab)
1. **Clone the Repository** (if you haven't already):
Problèmes de docker communs
   git clone https://github.com/DrewThomasson/ebook2audiobook.git
Docker est coincé à télécharger des modèles affinés. (Cela ne se produit pas pour chaque ordinateur mais certains semblent rencontrer ce problème)
La désactivation de la barre de progression semble résoudre le problème,
Comme discuté [ici dans # 191] (https://github.com/drewthomasson/ebook2audiobook/issues/191)
Exemple d'ajout de ce correctif dans la commande `docker run`
3. **Start the service:**
Modèles TTS à réglage fin
    docker-compose up -d
Vous pouvez facilement affiner votre propre modèle XTTS avec ce repo
[XTTS-FINETUNE-WEBUI] (https://github.com/daswer123/xtsts-finetune-webui)
  The service will be available at http://localhost:7860.


[XTTS-FINETUNE-WEBUI-SPACE] (https://huggingface.co/spaces/drewthomasson/xtsts-finetune-webui-gpu)
![demo_web_gui](assets/demo_web_gui.gif)

Un espace que vous pouvez utiliser pour dés-noter les données de formation facilement
[denoise huggingface-space] (https://huggingface.co/spaces/drewthomasson/deepfilternet2_no_limit)
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
Collection TTS à réglage fin
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
Pour trouver notre collection de modèles TTS déjà affinés,


## Renting a GPU
Démos
#### You can duplicate the hugginface space and rent a gpu for around $0.40 an hour
** voix de jour de pluie **

#### Or you can try using the google colab for free!
(Be aware it will time out after a bit of your not messing with the google colab)
** Voix de David Attenborough **


Formats de livres électroniques pris en charge
- Docker gets stuck downloading Fine-Tuned models.
`.epub`,` .pdf`, `.mobi`,` .txt`, `.html`,` .rtf`, `.chm`,` .lit`,
`.pdb`,` .fb2`, `.odt`,` .cbr`, `.cbz`,` .prc`, `.lrf`,` .pml`,
`.snb`,` .cbc`, `.rb`,` .tcr`
  Example of adding this fix in the `docker run` command
```Dockerfile
** Meilleurs résultats **: `.epub` ou` .mobi` pour la détection automatique des chapitres
    -p 7860:7860 athomasson2/ebook2audiobook
Sortir


! [Exemple] (https://github.com/drewthomasson/voxnovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)
You can fine-tune your own xtts model easily with this repo
Problèmes courants:

Le processeur est lent (mieux sur le SMP serveur CPU) tandis que NVIDIA GPU peut avoir une conversion presque en temps réel. [Discussion À ce sujet] (https://github.com/drewthomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)
Pour une génération multilingue plus rapide, je suggérerais mon autre

(Il n'a cependant pas de clonage vocal zéro et est des voix de qualité Siri, mais elle est beaucoup plus rapide sur CPU). "J'ai des problèmes de dépendance" - utilisez simplement le docker, c'est entièrement autonome et a un mode sans tête,
 Ajoutez un paramètre `- help` à la fin de la commande docker run pour plus d'informations. "Je reçois un problème audio tronqué!" - Veuillez en faire un problème,

### Fine Tuned TTS Collection
Ce avec quoi j'ai besoin d'aide! 🙌
[La liste complète des choses peut être trouvée ici] (https://github.com/drewthomasson/ebook2audiobook/issues/32)
For an XTTS custom model a ref audio clip of the voice reference is mandatory:


## Demos
Créer potentiellement des guides de lecture pour plusieurs langues (parce que la seule langue que je connaisse est l'anglais 😔)
https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080


** Coqui tts **: [Coqui tts github] (https://github.com/idiap/coqui-ai-tts)
https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea


## Supported eBook Formats
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
** ffmpeg **: [site Web ffmpeg] (https://ffmpeg.org)
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Best results**: `.epub` or `.mobi` for automatic chapter detection


[Legacy v1.0] (Legacy / v1.0)
- Creates a `['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']` (set in ./lib/conf.py) file with metadata and chapters.
Vous pouvez afficher le code [ici] (Legacy / v1.0). Rejoignez notre serveur! [! [Discord] (https://dcbadge.limes.pink/api/server/https://discord.gg/63tv3f65k6)] (https://discord.gg/63tv3f65k6)