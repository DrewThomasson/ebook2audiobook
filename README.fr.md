# 📚 eBook2Audiobook

Convertisseur CPU / GPU des livres électroniques aux livres audio avec des chapitres et des métadonnées<br/>Utilisation de calibre, FFMPEG, XTSTV2, FAIRSEQ et plus encore. Prend en charge le clonage vocal et +1110 langues!

> [!IMPORTANT]**Cet outil est destiné à être utilisé avec des livres électroniques non DRM, acquis légalement.**<br>Les auteurs ne sont pas responsables de toute utilisation abusive de ce logiciel ou de toute conséquence juridique qui en résulte.<br>Utilisez cet outil de manière responsable et conformément à toutes les lois applicables.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

Merci à Support Ebook2Audiobook Develoers!<br>[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

#### Interface GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## README.md

-   Nous achetons[Arabe (arabe)](./readme/README_AR.md)
-   Zho[Chinois](./readme/README_CN.md)
-   un \`a[Anglais](README.md)
-   swe[Suédois (suédois)](./readme/README_SWE.md)
-   fas[Persan (persan)](./readme/README_FA.md)
-   elle[Italien (italien)](./readme/README.it.md)

## Table des matières

-   [ebook2Audiobook](#-ebook2audiobook)
-   [Caractéristiques](#features)
-   [Interface Docker GUI](#docker-gui-interface)
-   [Démo d'espace en étreinte](#huggingface-space-demo)
-   [Google Colab gratuit](#free-google-colab)
-   [Démos audio pré-faites](#demos)
-   [Langues prises en charge](#supported-languages)
-   [Exigences](#hardware-requirements)
-   [Instructions d'installation](#installation-instructions)
-   [Usage](#launching-gradio-web-interface)
    -   [Lancement d'interface Web Gradio](#launching-gradio-web-interface)
    -   [Utilisation sans tête de base](#basic--usage)
    -   [Utilisation du modèle XTTS personnalisé sans tête](#example-of-custom-model-zip-upload)
    -   [Louer un GPU](#renting-a-gpu)
    -   [Aide à la sortie de la commande](#help-command-output)
-   [Modèles TTS à réglage fin](#fine-tuned-tts-models)
    -   [Pour la collecte de modèles TTS affinés](#fine-tuned-tts-collection)
-   [Utilisation de Docker](#using-docker)
    -   [Run docker](#running-the-docker-container)
    -   [Docker](#building-the-docker-container)
    -   [Docker Compose](#docker-compose)
    -   [Guide Docker Headless](#docker-headless-guide)
    -   [Emplacements de fichiers de conteneur Docker](#docker-container-file-locations)
    -   [Problèmes de docker communs](#common-docker-issues)
-   [Formats de livres électroniques pris en charge](#supported-ebook-formats)
-   [Sortir](#output)
-   [Problèmes communs](#common-issues)
-   [Merci spécial](#special-thanks)
-   [Rejoignez notre serveur!](#join-our--server)
-   [Héritage](#legacy-v10)
-   [Table des matières](#table-of-contents)

## Caractéristiques

-   📖 Convertit les livres électroniques en format texte avec calibre.
-   📚 Divise Ebook en chapitres pour l'audio organisé.
-   🎙️ Texte à dispection de haute qualité avec[Coqui xttsv2](https://huggingface.co/coqui/XTTS-v2)et[Fairseq](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)(et plus).
-   🗣️ Clonage vocal facultatif avec votre propre fichier vocal.
-   🌍 prend en charge +1110 langues (anglais par défaut).[Liste des langues prises en charge](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
-   🖥️ Conçu pour fonctionner sur 4 Go de RAM.

## [Démo d'espace en étreinte](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)

-   HuggingFace Space fonctionne sur le niveau CPU gratuit, alors attendez-vous à très lent ou à délai lol, ne lui donnez pas des fichiers géants est tout
-   Mieux vaut dupliquer l'espace ou fonctionner localement.

## Google Colab gratuit

[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)

## Langues prises en charge

-   **Arabe (ARA)**
-   **Chinois (ZH)**
-   **Czech (ces)**
-   **Croate (HRV)**
-   **Néerlandais (NLD)**
-   **Anglais (Eng)**
-   **Français (de)**
-   **Allemand (DEU)**
-   **Pas (hin)**
-   **Hongrois (AM)**
-   **Italien (ita)**
-   **Japonais (JPN)**
-   **Coréen (COR)**
-   **Polon (Pol)**
-   **Portugais (POR)**
-   **Russe (RUS)**
-   **Espagnol (spa)**
-   **Turc (rond)**
-   **Vietnamese (vie)**
-   [**+1100 langues via Fairseq**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

## Exigences matérielles

-   4 Go de RAM minimum, 8 Go recommandé
-   Virtualisation activée si elle s'exécute sur Windows (Docker uniquement)
-   CPU, GPU (recommandé), MPS (pas encore optimisé et peut être plus lent que le CPU)

> [!IMPORTANT]**Avant de publier soigneusement une installation d'installation ou de bug<br>Pour être sûr que votre problème n'existe pas déjà.**

> [!NOTE]**Manque de toute structure de normes comme ce qui est un chapitre, un paragraphe, une préface, etc.<br>Vous devez d'abord supprimer manuellement n'importe quel texte que vous ne souhaitez pas être converti en audio.**

### Instructions d'installation

1.  **Repo clone**

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
```

### Lancement d'interface Web Gradio

1.  **Exécuter eBook2Audiobook**:
    -   **Linux / macOS**
        ```bash
        ./ebook2audiobook.sh  # Run Launch script
        ```
    -   **Fenêtre**
        ```bash
        .\ebook2audiobook.cmd  # Run launch script or double click on it (Bypass windows alerts)
        ```
2.  **Ouvrez l'application Web**: Cliquez sur l'URL fournie dans le terminal pour accéder à l'application Web et convertir les livres électroniques.
3.  **Pour le lien public**:`python app.py --share`(All OS)`./ebook2audiobook.sh --share`(Linux / macOS)`ebook2audiobook.cmd --share`(Windows)

> [!IMPORTANT]**Si le script est arrêté et exécuté, vous devez actualiser votre interface Gradio GUI<br>Pour permettre à la page Web de se reconnecter à la nouvelle prise de connexion.**

### Utilisation de base

-   **Linux / macOS**:
    ```bash
    ./ebook2audiobook.sh --headless --ebook <path_to_ebook_file> \
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **Fenêtre**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <path_to_ebook_file>
        --voice [path_to_voice_file] --language [language_code]
    ```
-   **[--ebook]**: Chemin vers votre fichier d'ebook.
-   **[--voix]**: Chemin de fichier de clonage vocal (facultatif).
-   **[--langue]**: Code linguistique dans ISO-639-3 (c'est-à-dire: ita pour italien, eng pour l'anglais, le deu pour l'allemand ...).<br>La langue par défaut est Eng et --Language est facultative pour le jeu de langues par défaut dans ./lib/lang.py.<br>Les codes ISO-639-1 2 lettres sont également pris en charge.

### Exemple de téléchargement de zip de modèle personnalisé

(Doit être un fichier .zip contenant les fichiers de modèle obligatoires. Exemple pour XTTS: config.json, model.pth, vocab.json et ref.wav)

-   **Linux / macOS**
    ```bash
    ./ebook2audiobook.sh --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **Fenêtre**
    ```bash
    .\ebook2audiobook.cmd --headless --ebook <ebook_file_path> \
        --voice <target_voice_file_path> --language <language> --custom_model <custom_model_path>
    ```
-   **&lt;personnalisé_model_path>**: Chemin vers`model_name.zip`déposer,
        qui doit contenir (selon le moteur TTS) tous les fichiers obligatoires<br>(Voir ./lib/models.py).

### Pour un guide détaillé avec la liste de tous les paramètres à utiliser

-   **Linux / macOS**
    ```bash
    ./ebook2audiobook.sh --help
    ```
-   **Fenêtre**
    ```bash
    .\ebook2audiobook.cmd --help
    ```
-   **Ou pour tous les OS**
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

Remarque: En mode Gradio / GUI, pour annuler une conversion en cours, cliquez simplement sur le[X]à partir du composant de téléchargement du livre électronique.

### Utilisation de Docker

Vous pouvez également utiliser Docker pour exécuter le convertisseur Ebook to Audiobook. 
Cette méthode garantit la cohérence dans différents environnements et simplifie la configuration.

#### Exécution du conteneur Docker

Pour exécuter le conteneur Docker et démarrer l'interface Gradio, utilisez la commande suivante:

\-Run avec CPU uniquement

```powershell
docker run --rm -p 7860:7860 athomasson2/ebook2audiobook
```

\-Run avec accélération du GPU (NVIDIA compatible uniquement)

```powershell
docker run --rm --gpus all -p 7860:7860 athomasson2/ebook2audiobook
```

#### Construire le conteneur Docker

-   Vous pouvez créer l'image Docker avec la commande:

```powershell
docker build --platform linux/amd64 -t athomasson2/ebook2audiobook .
```

Cette commande démarrera l'interface Gradio sur le port 7860. (LocalHost: 7860)

-   Pour plus d'options, ajoutez le paramètre`--help`

## Emplacements de fichiers de conteneur Docker

Tous les eBook2Audiobooks auront le dir de base de`/home/user/app/`Par exemple:`tmp`=`/home/user/app/tmp``audiobooks`=`/home/user/app/audiobooks`

## Guide Docker Headless

Premier pour une traction Docker de la dernière avec

```bash
docker pull athomasson2/ebook2audiobook
```

-   Avant d'exécuter ceci, vous devez créer un DIR nommé "Input-Folder" dans votre Dir actuel
    Ce qui sera lié, c'est là que vous pouvez mettre vos fichiers d'entrée pour l'image Docker pour voir

```bash
mkdir input-folder && mkdir Audiobooks
```

-   Dans la commande ci-dessous, échanger**Your_input_file.txt**avec le nom de votre fichier d'entrée

```bash
docker run --rm \
    -v $(pwd)/input-folder:/home/user/app/input_folder \
    -v $(pwd)/audiobooks:/home/user/app/audiobooks \
    athomasson2/ebook2audiobook \
    --headless --ebook /input_folder/YOUR_EBOOK_FILE
```

-   Et ça devrait être ça!
-   Les livres audio de sortie se trouvent dans le dossier des livres audio qui seront également situés
    Dans votre Dir local, vous avez dirigé cette commande docker dans

## Pour obtenir la commande d'aide pour les autres paramètres de ce programme, vous pouvez exécuter ceci

```bash
docker run --rm athomasson2/ebook2audiobook --help

```

Et cela sortira ceci[Aide à la sortie de la commande](#help-command-output)

### Docker Compose

Ce projet utilise Docker Compose pour s'exécuter localement. Vous pouvez activer ou désactiver le support GPU 
En définissant soit`*gpu-enabled`ou`*gpu-disabled`dans`docker-compose.yml`

#### Étapes pour fonctionner

1.  **Cloner le référentiel**(Si vous ne l'avez pas déjà fait):
    ```bash
    git clone https://github.com/DrewThomasson/ebook2audiobook.git
    cd ebook2audiobook
    ```
2.  **Définir la prise en charge du GPU (désactivé par défaut)**Pour activer le support GPU, modifiez`docker-compose.yml`et changer`*gpu-disabled`à`*gpu-enabled`
3.  **Démarrer le service:**
    ```bash
    docker-compose up -d
    ```
4.  **Accéder au service:**Le service sera disponible sur http&#x3A; // localhost: 7860.

### Interface Docker GUI

![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Click to see images of Web GUI</summary>
  <img width="1728" alt="GUI Screen 1" src="assets/gui_1.png">
  <img width="1728" alt="GUI Screen 2" src="assets/gui_2.png">
  <img width="1728" alt="GUI Screen 3" src="assets/gui_3.png">
</details>

## Louer un GPU

Vous n'avez pas le matériel pour l'exécuter ou vous souhaitez louer un GPU?

#### Vous pouvez dupliquer l'espace Hugginface et louer un GPU pour environ 0,40 $ l'heure

[Démo d'espace en étreinte](#huggingface-space-demo)

#### Ou vous pouvez essayer d'utiliser le Google Colab gratuitement!

(Sachez que cela sera chronométré après un peu de votre ne pas jouer avec le Google Colab)[Google Colab gratuit](#free-google-colab)

## Problèmes de docker communs

-   Docker est coincé à télécharger des modèles affinés.
    (Cela ne se produit pas pour chaque ordinateur mais certains semblent rencontrer ce problème)
    La désactivation de la barre de progression semble résoudre le problème,
    comme indiqué[Ici dans # 191](https://github.com/DrewThomasson/ebook2audiobook/issues/191)Exemple d'ajout de ce correctif dans le`docker run`commande

```Dockerfile
docker run --rm --gpus all -e HF_HUB_DISABLE_PROGRESS_BARS=1 -e HF_HUB_ENABLE_HF_TRANSFER=0 \
    -p 7860:7860 athomasson2/ebook2audiobook
```

## Modèles TTS à réglage fin

Vous pouvez facilement affiner votre propre modèle XTTS avec ce repo[XTTS-FINETUNE-WEBUI](https://github.com/daswer123/xtts-finetune-webui)

Si vous souhaitez louer un GPU facilement, vous pouvez également dupliquer ce câlin étreint[XTTS-FINETUNE-WEBUI-SPACE](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)

Un espace que vous pouvez utiliser pour dés-noter les données de formation facilement[Denoise-HuggingFace-espace](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)

### Collection TTS à réglage fin

Pour trouver notre collection de modèles TTS déjà affinés,
visite[Ce lien de visage étreint](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)Pour un modèle personnalisé XTTS, un clip audio REF de la référence vocale est obligatoire:

## Démos

**Voix du jour de la pluie**<https://github.com/user-attachments/assets/d25034d9-c77f-43a9-8f14-0d167172b080>

**Voix de David Attenborough**<https://github.com/user-attachments/assets/0d437a41-0b0d-48ed-8c9b-02763d5e48ea>

## Formats de livres électroniques pris en charge

-   `.epub`,`.pdf`,`.mobi`,`.txt`,`.html`,`.rtf`,`.chm`,`.lit`,`.pdb`,`.fb2`,`.odt`,`.cbr`,`.cbz`,`.prc`,`.lrf`,`.pml`,`.snb`,`.cbc`,`.rb`,`.tcr`
-   **Meilleurs résultats**:`.epub`ou`.mobi`Pour la détection automatique des chapitres

## Sortir

-   Crée un`['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']`(Définissez le fichier ./lib/conf.py) avec des métadonnées et des chapitres.
-   **Exemple**![Example](https://github.com/DrewThomasson/VoxNovel/blob/dc5197dff97252fa44c391dc0596902d71278a88/readme_files/example_in_app.jpeg)

## Problèmes courants:

-   Le processeur est lent (mieux sur le SMP serveur CPU) tandis que NVIDIA GPU peut avoir une conversion presque en temps réel.[Discussion about this](https://github.com/DrewThomasson/ebook2audiobook/discussions/19#discussioncomment-10879846)Pour une génération multilingue plus rapide, je suggérerais mon autre[Projet qui utilise Piper-Tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts)plutôt
    (Il n'a cependant pas de clonage vocal zéro et est des voix de qualité Siri, mais elle est beaucoup plus rapide sur CPU).
-   "J'ai des problèmes de dépendance" - utilisez simplement le docker, c'est entièrement autonome et a un mode sans tête,
     ajouter`--help`Paramètre à la fin de la commande docker run pour plus d'informations.
-   "Je reçois un problème audio tronqué!" - Veuillez en faire un problème,
     Nous ne parlons pas toutes les langues et avons besoin de conseiller des utilisateurs pour affiner la logique de division de la phrase.

## Ce avec quoi j'ai besoin d'aide! 🙌

## [La liste complète des choses peut être trouvée ici](https://github.com/DrewThomasson/ebook2audiobook/issues/32)

-   Toute aide de personnes qui parlent l'une des langues prises en charge pour aider à des méthodes de division des phrases appropriées
-   Créer potentiellement des guides de réadme pour plusieurs langues (car la seule langue que je connaisse est l'anglais 😔)

## Merci spécial

-   **TTS de cuisine**:[Coqui tts github](https://github.com/idiap/coqui-ai-TTS)
-   **Calibre**:[Calibre Website](https://calibre-ebook.com)
-   **Ffmpeg**:[Site Web ffmpeg](https://ffmpeg.org)
-   [@ shakenbake15 pour une meilleure méthode d'économie de chapitre](https://github.com/DrewThomasson/ebook2audiobook/issues/8)

### [Legacy v1.0](legacy/v1.0)

Vous pouvez afficher le code[ici](legacy/v1.0).

## Rejoignez notre serveur!

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)
