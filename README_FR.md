# ðŸ“š ebook2audiobook (E2A)
Convertisseur CPU/GPU d'ebook en livre audio avec chapitres et mÃ©tadonnÃ©es,<br/>
utilisant des moteurs TTS avancÃ©s et bien plus encore.<br/>
Supporte le clonage de voix et 1158 langues !

> [!IMPORTANT]
**Cet outil est destinÃ© uniquement aux livres numÃ©riques lÃ©galement acquis, sans DRM.**<br>
Les auteurs dÃ©clinent toute responsabilitÃ© en cas de mauvaise utilisation ou de consÃ©quences juridiques.<br>
Utilisez cet outil de maniÃ¨re responsable et conformÃ©ment aux lois applicables.

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/63Tv3F65k6)](https://discord.gg/63Tv3F65k6)

### Soutenir les dÃ©veloppeurs d'ebook2audiobook !
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)

### Lancer localement

[![DÃ©marrage rapide](https://img.shields.io/badge/D%C3%A9marrage%20rapide-blue?style=for-the-badge)](#instructions)

[![Docker Build](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml/badge.svg)](https://github.com/DrewThomasson/ebook2audiobook/actions/workflows/Docker-Build.yml)  [![TÃ©lÃ©charger](https://img.shields.io/badge/T%C3%A9l%C3%A9charger-Maintenant-blue.svg)](https://github.com/DrewThomasson/ebook2audiobook/releases/latest)

<a href="https://github.com/DrewThomasson/ebook2audiobook">
  <img src="https://img.shields.io/badge/Plateforme-mac%20|%20linux%20|%20windows-lightgrey" alt="Plateforme">
</a><a href="https://hub.docker.com/r/athomasson2/ebook2audiobook">
<img alt="Docker Pull Count" src="https://img.shields.io/docker/pulls/athomasson2/ebook2audiobook.svg"/>
</a>

### Lancer Ã  distance
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/ebook2audiobook)
[![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)
[![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/Rihcus/ebook2audiobookXTTS/blob/main/Notebooks/kaggle-ebook2audiobook.ipynb)

#### Interface graphique
![demo_web_gui](assets/demo_web_gui.gif)

<details>
  <summary>Cliquer pour voir les captures d'Ã©cran de l'interface</summary>
  <img width="1728" alt="Interface 1" src="assets/gui_1.png">
  <img width="1728" alt="Interface 2" src="assets/gui_2.png">
  <img width="1728" alt="Interface 3" src="assets/gui_3.png">
</details>

---

## Table des matiÃ¨res
- [FonctionnalitÃ©s](#fonctionnalitÃ©s)
- [Configuration matÃ©rielle requise](#configuration-matÃ©rielle-requise)
- [Langues supportÃ©es](#langues-supportÃ©es)
- [Formats d'ebook supportÃ©s](#formats-debook-supportÃ©s)
- [Formats de sortie](#formats-de-sortie)
- [Tags SML](#tags-sml)
- [Instructions d'utilisation](#instructions)
  - [Lancer localement](#instructions)
  - [Mode GUI Gradio](#instructions)
  - [Mode sans interface (headless)](#utilisation-de-base)
  - [Docker](#docker)
- [ModÃ¨les TTS affinÃ©s](#modÃ¨les-tts-affinÃ©s)
- [Personnalisation](#personnalisation)
- [ProblÃ¨mes frÃ©quents](#problÃ¨mes-frÃ©quents)
- [NouveautÃ©s v26.5.20](#nouveautÃ©s-v26520)
- [Feuille de route](#feuille-de-route)

---

## FonctionnalitÃ©s
- ðŸ”§ **Moteurs TTS supportÃ©s** : `XTTSv2`, `Bark`, `Fairseq`, `VITS`, `Tacotron2`, `Tortoise`, `GlowTTS`, `YourTTS`
- ðŸ“š **Formats de fichiers convertibles** : `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lrf`, `.rb`, `.snb`, `.tcr`, `.pdf`, `.txt`, `.rtf`, `.doc`, `.docx`, `.html`, `.odt`, `.azw`, `.tiff`, `.tif`, `.png`, `.jpg`, `.jpeg`, `.bmp`
- ðŸ’» **Zone de texte** pour convertir directement un texte court en audio
- ðŸ” **Scan OCR** pour les fichiers dont les pages de texte sont des images
- ðŸ”Š **SynthÃ¨se vocale de haute qualitÃ©**, du quasi-temps-rÃ©el Ã  la voix quasi-rÃ©elle
- ðŸ—£ï¸ **Clonage de voix optionnel** avec votre propre fichier audio
- ðŸŒ **Supporte 1158 langues** ([liste des langues supportÃ©es](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html))
- ðŸ’» **Peu gourmand en ressources** â€” fonctionne avec **2 Go de RAM / 1 Go de VRAM (minimum)**
- ðŸŽµ **Formats de sortie audio** : mono ou stÃ©rÃ©o `aac`, `flac`, `mp3`, `m4b`, `m4a`, `mp4`, `mov`, `ogg`, `wav`, `webm`
- ðŸ§  **Tags SML supportÃ©s** â€” contrÃ´le fin des pauses, silences, changements de voix ([voir ci-dessous](#tags-sml))
- ðŸ§© **ModÃ¨le personnalisÃ© optionnel** avec votre propre modÃ¨le entraÃ®nÃ© (XTTSv2 uniquement, autres sur demande)
- ðŸŽ›ï¸ **ModÃ¨les prÃ©-entraÃ®nÃ©s** par l'Ã©quipe E2A<br/>
     <i>(Contactez-nous si vous avez besoin de modÃ¨les supplÃ©mentaires, ou si vous souhaitez partager le vÃ´tre)</i>

---

## Configuration matÃ©rielle requise
- 2 Go de RAM minimum, 8 Go recommandÃ©s.
- 1 Go de VRAM minimum, 4 Go recommandÃ©s.
- Virtualisation activÃ©e si vous utilisez Windows (Docker uniquement).
- CPU, XPU (Intel, AMD, ARM)*.
- CUDA, ROCm, JETSON
- MPS (Apple Silicon)

*<i>Les moteurs TTS modernes sont trÃ¨s lents sur CPU â€” prÃ©fÃ©rez des moteurs plus lÃ©gers comme YourTTS ou Tacotron2.</i>

---

## Langues supportÃ©es
| **Arabe (ar)**       | **Chinois (zh)**     | **Anglais (en)**    | **Espagnol (es)**   |
|:--------------------:|:--------------------:|:-------------------:|:-------------------:|
| **FranÃ§ais (fr)**    | **Allemand (de)**    | **Italien (it)**    | **Portugais (pt)**  |
| **Polonais (pl)**    | **Turc (tr)**        | **Russe (ru)**      | **NÃ©erlandais (nl)**|
| **TchÃ¨que (cs)**     | **Japonais (ja)**    | **Hindi (hi)**      | **Bengali (bn)**    |
| **Hongrois (hu)**    | **CorÃ©en (ko)**      | **Vietnamien (vi)** | **SuÃ©dois (sv)**    |
| **Persan (fa)**      | **Yoruba (yo)**      | **Swahili (sw)**    | **IndonÃ©sien (id)** |
| **Slovaque (sk)**    | **Croate (hr)**      | **Tamoul (ta)**     | **Danois (da)**     |
- [**+1130 autres langues et dialectes**](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)

---

## Formats d'ebook supportÃ©s
- `.epub`, `.pdf`, `.mobi`, `.txt`, `.html`, `.rtf`, `.chm`, `.lit`,
  `.pdb`, `.fb2`, `.odt`, `.cbr`, `.cbz`, `.prc`, `.lrf`, `.pml`,
  `.snb`, `.cbc`, `.rb`, `.tcr`
- **Meilleurs rÃ©sultats** : `.epub` ou `.mobi` pour la dÃ©tection automatique des chapitres

## Formats de sortie
- `.m4b`, `.m4a`, `.mp4`, `.webm`, `.mov`, `.mp3`, `.flac`, `.wav`, `.ogg`, `.aac`
- Le format de traitement peut Ãªtre modifiÃ© dans `lib/conf.py`

---

## Tags SML
Les tags SML permettent un contrÃ´le prÃ©cis de la synthÃ¨se vocale, directement dans le texte source.

| Tag | Effet |
|-----|-------|
| `[break]` | Silence court (durÃ©e alÃ©atoire **0,3â€“0,6 sec.**) |
| `[pause]` | Silence long (durÃ©e alÃ©atoire **1,0â€“1,6 sec.**) |
| `[pause:N]` | Pause fixe de **N secondes** |
| `[voice:/chemin/vers/voix]...[/voice]` | Changer de voix sur un passage |

**Voir aussi notre dÃ©pÃ´t dÃ©diÃ© Ã  l'ajout automatique de tags SML dans vos ebooks â†’ [E2A-SML](https://github.com/DrewThomasson/E2A-SML)**

> [!NOTE]
**Avant de signaler un problÃ¨me d'installation ou un bug, cherchez soigneusement dans les issues ouvertes et fermÃ©es<br>
pour vÃ©rifier que le problÃ¨me n'existe pas dÃ©jÃ .**

> [!NOTE]
**Le format EPUB ne dispose d'aucune structure standard dÃ©finissant ce qu'est un chapitre, un paragraphe, une prÃ©face, etc.<br>
Il est recommandÃ© de supprimer manuellement le texte que vous ne souhaitez pas convertir en audio.**

---

## Instructions

### 1. Cloner le dÃ©pÃ´t
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
```

### 2. Installer / Lancer ebook2audiobook

**Linux/macOS**
```bash
./ebook2audiobook.command
```
*Note pour macOS : Homebrew est installÃ© automatiquement pour les programmes manquants.*

**Lanceur macOS**
Double-cliquez sur `Mac Ebook2Audiobook Launcher.command`

**Windows**
```bat
ebook2audiobook.cmd
```
ou double-cliquez sur `ebook2audiobook.cmd`

*Note pour Windows : Scoop est installÃ© automatiquement pour les programmes manquants, sans droits administrateur.*

### 3. Ouvrir l'interface Web
Cliquez sur l'URL affichÃ©e dans le terminal : `http://localhost:7860/`

### 4. Lien public (partage)
```bash
# Linux/macOS
./ebook2audiobook.command --share
# Windows
ebook2audiobook.cmd --share
# Tous OS
python app.py --share
```

> [!IMPORTANT]
**Si le script est arrÃªtÃ© puis relancÃ©, vous devez rafraÃ®chir l'interface Gradio<br>
pour que la page web se reconnecte au nouveau socket.**

---

## Utilisation de base

**Linux/macOS :**
```bash
./ebook2audiobook.command --headless --ebook <chemin_ebook> --voice <chemin_voix> --language <code_langue>
```

**Windows :**
```bat
ebook2audiobook.cmd --headless --ebook <chemin_ebook> --voice <chemin_voix> --language <code_langue>
```

| ParamÃ¨tre | Description |
|-----------|-------------|
| `--ebook` | Chemin vers votre fichier ebook |
| `--voice` | Fichier audio pour le clonage de voix (optionnel) |
| `--language` | Code langue ISO-639-3 (ex. : `fra` pour franÃ§ais, `eng` pour anglais, `deu` pour allemandâ€¦)<br>Les codes ISO-639-1 Ã  2 lettres sont aussi acceptÃ©s. |

### Exemple avec modÃ¨le personnalisÃ© (zip)
Le fichier zip doit contenir les fichiers du modÃ¨le obligatoires. Pour XTTSv2 : `config.json`, `model.pth`, `vocab.json` et `ref.wav`.

**Linux/macOS :**
```bash
./ebook2audiobook.command --headless --ebook <chemin_ebook> --language <langue> --custom_model <chemin_modele.zip>
```

**Windows :**
```bat
ebook2audiobook.cmd --headless --ebook <chemin_ebook> --language <langue> --custom_model <chemin_modele.zip>
```

*Note : le fichier `ref.wav` de votre modÃ¨le personnalisÃ© est toujours utilisÃ© comme voix de rÃ©fÃ©rence.*

### Aide complÃ¨te
```bash
# Linux/macOS
./ebook2audiobook.command --help
# Windows
ebook2audiobook.cmd --help
# Tous OS
python app.py --help
```

---

## Docker

### 1. Cloner le dÃ©pÃ´t
```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
```

### 2. Construire le conteneur
```bash
# Windows - Docker simple :
ebook2audiobook.cmd --script_mode build_docker
# Windows - Docker Compose :
ebook2audiobook.cmd --script_mode build_docker --docker_mode compose
# Windows - Podman Compose :
ebook2audiobook.cmd --script_mode build_docker --docker_mode podman

# Linux/Mac - Docker simple :
./ebook2audiobook.command --script_mode build_docker
# Linux/Mac - Docker Compose :
./ebook2audiobook.command --script_mode build_docker --docker_mode compose
# Linux/Mac - Podman Compose :
./ebook2audiobook.command --script_mode build_docker --docker_mode podman
```

### 3. Lancer le conteneur

```bash
# Mode GUI/Gradio - CPU :
docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" \
  -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" \
  --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu

# Mode GUI/Gradio - CUDA :
docker run ... --gpus all athomasson2/ebook2audiobook:cu130

# Mode GUI/Gradio - ROCm :
docker run ... --device=/dev/kfd --device=/dev/dri athomasson2/ebook2audiobook:rocm6.4

# Mode GUI/Gradio - XPU (Intel) :
docker run ... --device=/dev/dri athomasson2/ebook2audiobook:xpu

# Mode GUI/Gradio - JETSON :
docker run ... --runtime nvidia athomasson2/ebook2audiobook:jetson61

# Mode headless (sans interface) - CPU :
docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" \
  -v "./models:/app/models" -v "./voices:/app/voices" -v "./tmp:/app/tmp" \
  --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu \
  --headless --ebook "/app/ebooks/monlivre.epub" [--voice /app/voices/mavoix.wav ...]
```

**Docker Compose (ex. CUDA 12.8) :**
```bash
# Interface graphique :
DEVICE_TAG=cu128 docker compose --profile gpu up --no-log-prefix
# Mode headless :
DEVICE_TAG=cu128 docker compose --profile gpu run --rm ebook2audiobook \
  --headless --ebook "/app/ebooks/monlivre.epub" ...
```

*Note : MPS (Apple Silicon) n'est pas exposÃ© dans Docker â€” utilisez le profil CPU.*

### ProblÃ¨mes Docker courants
- Mon GPU NVIDIA/ROCm/XPU n'est pas dÃ©tectÃ© ? â†’ [Page Wiki GPU ISSUES](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)

---

## ModÃ¨les TTS affinÃ©s

### Affiner votre propre modÃ¨le XTTSv2
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/xtts-finetune-webui-gpu)
[![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=flat&logo=kaggle&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/kaggle-xtts-finetune-webui-gradio-gui.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/v25/Notebooks/finetune/xtts/colab_xtts_finetune_webui.ipynb)

### DÃ©bruiter vos donnÃ©es d'entraÃ®nement
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?style=flat&logo=huggingface)](https://huggingface.co/spaces/drewThomasson/DeepFilterNet2_no_limit)
[![GitHub](https://img.shields.io/badge/DeepFilterNet-181717?logo=github)](https://github.com/Rikorose/DeepFilterNet)

### Collection de modÃ¨les affinÃ©s
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Models-yellow?style=flat&logo=huggingface)](https://huggingface.co/drewThomasson/fineTunedTTSModels/tree/main)

Pour un modÃ¨le XTTSv2 personnalisÃ©, un clip audio de rÃ©fÃ©rence (`ref.wav`) est obligatoire.

---

## Personnalisation
Vous Ãªtes libre de modifier `lib/conf.py` pour ajouter ou retirer des paramÃ¨tres. Si vous prÃ©voyez de le faire, conservez une copie de l'original â€” lors de chaque mise Ã  jour d'ebook2audiobook, restaurez votre `conf.py` modifiÃ©. MÃªme chose pour `lib/models.py`. Si vous souhaitez proposer votre modÃ¨le personnalisÃ© comme preset officiel, contactez-nous.

## Revenir Ã  une version antÃ©rieure
Les releases sont disponibles â†’ [ici](https://github.com/DrewThomasson/ebook2audiobook/releases)
```bash
git checkout tags/NUMERO_VERSION  # Exemple : git checkout tags/v25.7.7
```

---

## ProblÃ¨mes frÃ©quents
- **Mon GPU NVIDIA/ROCm/XPU/MPS n'est pas dÃ©tectÃ© ?** â†’ [Page Wiki GPU ISSUES](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES)
- **Le CPU est lent** (meilleur sur CPU serveur SMP) tandis que le GPU permet une conversion quasi-temps-rÃ©el.
  Pour une gÃ©nÃ©ration multilingue plus rapide, consultez le projet [ebook2audiobookpiper-tts](https://github.com/DrewThomasson/ebook2audiobookpiper-tts) (pas de clonage de voix, qualitÃ© Siri, mais beaucoup plus rapide sur CPU).
- **"J'ai des problÃ¨mes de dÃ©pendances"** â€” Utilisez Docker, il est entiÃ¨rement autonome et dispose d'un mode headless.
- **"J'ai un problÃ¨me d'audio tronquÃ© !"** â€” Merci d'ouvrir un ticket, nous avons besoin des retours des utilisateurs pour affiner la logique de dÃ©coupage des phrases.

---

## NouveautÃ©s v26.5.20

### Nouveau thÃ¨me Â« Polar Night Â»
L'interface graphique adopte un thÃ¨me bleu nuit plus lisible :
- Fond `#0d1320`, accent bleu ciel `#7db8e6`, bouton Convertir vert Ã©meraude
- Police d'affichage Fraunces + Manrope pour l'interface
- Mode sombre forcÃ© dÃ¨s le chargement de la page

### Corrections de bugs (~40 corrections)

**Moteurs TTS**
- **Cache de modÃ¨les** : les moteurs VITS, Fairseq, GlowTTS, Tacotron2 et Tortoise rechargaient le modÃ¨le entier Ã  chaque livre. DÃ©sormais `session['model_cache']` est synchronisÃ© aprÃ¨s chaque rÃ©Ã©criture de clÃ©.
- **Fuite de fichiers temporaires** : les 4 moteurs Ã  conversion de voix crÃ©aient des milliers de fichiers `.wav` temporaires de la voix cible (un par phrase). DÃ©sormais mis en cache par voix dans `resampled_wav_cache`.
- **Latence XTTS** : `self.speaker` restait Ã  `None` aprÃ¨s l'initialisation, forÃ§ant le recalcul des latents conditionnels Ã  chaque phrase. DÃ©sormais dÃ©rivÃ© du stem de la voix rÃ©solue.
- **`create_vtt()` cassÃ©** : tous les 8 moteurs appelaient `self._build_vtt_file()` (inexistant). CorrigÃ© pour dÃ©lÃ©guer Ã  la vraie fonction `build_vtt_file(self.session)`.
- **sox path** : validation avec `shutil.which('sox')` avant usage, message d'erreur clair si absent.
- **`subprocess.run(..., check=True)`** ajoutÃ© partout pour remonter les erreurs de processus externes.

**Interface graphique (Gradio)**
- `session['voice']` ne rÃ©initialise plus `session['ebook_src']` par erreur.
- `chain_enable` : `session['status']` â†’ `session.get('status')` â€” plus de `KeyError` sur session expirÃ©e.
- Autosave : stocker une exception dans le state Gradio cassait toutes les sauvegardes suivantes.
- `click_gr_deletion` : statut DELETION correctement rÃ©initialisÃ© Ã  READY.
- `click_gr_blocks_cancel_btn` : dÃ©rÃ©fÃ©rencement sÃ©curisÃ© de `session['blocks_current']`.
- `confirm_voice_del` : vÃ©rification `commonpath` pour bloquer la traversÃ©e de chemin.
- `start_conversion` : re-lecture correcte de la session dans le bloc `except`.

**Noyau (core.py)**
- `get_cover()` : `return True` â†’ `return None` (Ã©vitait d'ouvrir stdout accidentellement).
- `year2words()` : rÃ©Ã©criture â€” gestion correcte de `KeyError` sur la langue.
- Lecture `.txt` : `encoding='utf-8', errors='replace'`.

**Configuration (conf.py)**
- `ESPEAK_DATA_PATH` : liste de candidats testant le sous-chemin `eSpeak NG\espeak-ng-data` (installation scoop).
- `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` : prÃ©vient les erreurs d'encodage sur Windows.
- `VERSION.txt` rÃ©solu relativement Ã  `__file__` â€” plus d'erreur si le rÃ©pertoire de travail est diffÃ©rent.

**Installeur / app.py**
- VÃ©rification de port : `0.0.0.0` â†’ `127.0.0.1` (Ã©coute correcte sur l'interface locale).
- Chargement sÃ©curisÃ© des checkpoints de modÃ¨les (`weights_only=True`).
- ROCm (device_installer.py) : bloc d'indentation corrigÃ©, `name` assignÃ© avant usage.
- `vram_detector.py` ROCm : dÃ©tection GPU corrigÃ©e.
- `argos_translator.py`, `redirect_console.py`, `voice_extractor.py` : corrections mineures.

---

## Feuille de route
- Toutes les fonctionnalitÃ©s sont ouvertes aux contributions â­
- Aide bienvenue pour amÃ©liorer les modÃ¨les dans les langues supportÃ©es â­
- [x] AperÃ§u des blocs/chapitres avant la conversion
- [ ] Conversion parallÃ¨le avec workers
- [ ] Ã‰dition phrase par phrase pour corrections chirurgicales
- [x] Tags SML (voix, pause, break, etc.)
- [x] Aide `-h` multilingue
- [x] OCR pour PDF / JPG / BMP / PNG / TIFF
- [x] Notebooks (Colab, Kaggle)
- [x] Dockerfile / Docker Compose / Podman Compose
- [ ] Application iOS
- [ ] Application Android
- [ ] IntÃ©gration Audiobookshelf

### Moteurs TTS
- [x] XTTSv2 â€” [x] Bark â€” [x] Fairseq â€” [x] VITS â€” [x] Tacotron2 â€” [x] YourTTS â€” [x] Tortoise â€” [x] GlowTTS
- [ ] Piper-TTS â€” [ ] CosyVoice â€” [ ] Kokoro-TTS â€” [ ] Orpheus-TTS â€” [ ] F5-TTS â€” [ ] Spark-TTS

### Traductions du README
- [x] Anglais (eng)
- [x] FranÃ§ais (fra) â† *ce fichier*
- [ ] Arabe (ara) â€” [ ] Chinois (zho) â€” [ ] Espagnol (spa) â€” [ ] Allemand (deu)
- [ ] Italien (ita) â€” [ ] Portugais (por) â€” [ ] Polonais (pol) â€” [ ] Russe (rus)

---

## Remerciements
Merci Ã  tous les contributeurs, testeurs et membres de la communautÃ© Discord qui rendent ce projet possible !

[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/athomasson2)
