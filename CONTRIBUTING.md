# Contributing to ebook2audiobook (E2A)

Thanks for taking the time to contribute! Every bug report, language fix, voice, model and pull request
helps to improve the quality of E2A.

By participating in this project you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

> [!IMPORTANT]
**This tool is intended for use with non-DRM, legally acquired eBooks only.**<br>
Never attach copyrighted eBooks or audio to an issue or a pull request.

## Table of Contents
- [Ways to Contribute](#ways-to-contribute)
- [Reporting Issues](#reporting-issues)
- [Requesting Features](#requesting-features)
- [Development Setup](#development-setup)
- [Project Layout](#project-layout)
- [Branches and Pull Requests](#branches-and-pull-requests)
- [Python Code Normalization](#python-code-normalization)
- [Launch Scripts](#launch-scripts)
- [User-Facing Strings (Legends)](#user-facing-strings-legends)
- [README and Translations](#readme-and-translations)
- [Adding or Changing a TTS Engine](#adding-or-changing-a-tts-engine)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [License](#license)

<a id="ways-to-contribute"></a>
## Ways to Contribute
- **Bug reports** with a full terminal log (see [Reporting Issues](#reporting-issues))
- **Language help**: E2A supports 1696 languages and we don't speak them all. Native speakers are welcome to
  report truncated audio, bad sentence splitting, wrong number reading, etc.
- **Translations** of the GUI legends and the README
- **Voices**: clean voice samples in languages other than English to add to the built-in voices list
  (open an issue, we add them to the [E2A-Voices](https://huggingface.co/datasets/ebook2audiobook/E2A-Voices) dataset after review)
- **Fine-tuned models** to add to the presets list (see [Fine Tuned TTS models](README.md#fine-tuned-tts-models))
- **New TTS engines** and engine improvements
- **Hardware for beta tests** (CUDA, ROCm, XPU cards), see [README](README.md#hardware-donation-for-beta-tests-wanted)
- **Code**: every item of the [ROADMAP](README.md#-roadmap-) is open to public contributions

For questions and general discussion, use [GitHub Discussions](https://github.com/DrewThomasson/ebook2audiobook/discussions)
or our [Discord](https://discord.gg/63Tv3F65k6), not the issue tracker.

<a id="reporting-issues"></a>
## Reporting Issues
> [!IMPORTANT]
**For a security vulnerability, read the [Security Policy](SECURITY.md) first, then use the `Security report` template.**

1. **Search first.** Check the open **and closed** issues to be sure your issue does not exist already.
   Also check [Common Issues](README.md#common-issues) and the [GPU ISSUES Wiki Page](https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES).
2. **Use the right template**: `CPU Bug report` or `GPU Bug report`, and fill every field
   (OS, script mode Native/Docker, E2A version from `VERSION.txt`, Gradio/Headless, hardware).
3. **Attach the full terminal log as a file**, from the launch command until the end.
   Don't paste it as a comment.
4. Include the exact command line you used, the TTS engine, the language and, when possible,
   a small public-domain text that reproduces the problem.

> [!WARNING]
**Don't copy/paste any A.I. generated "solution" into an issue: it will be closed without notice.**<br>
A.I. tools are fine to help you write code, but you must understand, test and stand behind what you submit.

<a id="requesting-features"></a>
## Requesting Features
Search the issues and Discussions first, then open a `Feature request` describing what you need,
with a screenshot, a schema or a code sample when it helps. For large changes (new engine, new GUI tab,
new pipeline step), open the request **before** writing the code so we can agree on the approach.

<a id="development-setup"></a>
## Development Setup
Requirements: `git` and an internet connection. The launch scripts install everything else
(Python 3.10–3.12 through `uv`, calibre, ffmpeg, tesseract, the device-specific PyTorch build, etc.).

1. Fork the repository on GitHub, then clone your fork:
	```bash
	git clone https://github.com/<your_username>/ebook2audiobook.git
	cd ebook2audiobook
	git remote add upstream https://github.com/DrewThomasson/ebook2audiobook.git
	```
2. Run E2A once to build the environment:
   - **Linux/MacOS**
     ```bash
     ./ebook2audiobook.command
     ```
   - **Windows**
     ```bash
     ebook2audiobook.cmd
     ```
   The first launch creates `python_env/`, the Python environment used by E2A and by everything under `tools/`.
   Engines with conflicting dependencies are installed on first use in their own venv under
   `lib/classes/tts_engines/venvs/`.
3. Work with the same entry points users have:
   - GUI: `./ebook2audiobook.command` then open `http://localhost:7860/`
   - Headless: `./ebook2audiobook.command --headless --ebook <path_to_ebook_file> --language <language_code>`
   - All parameters: `./ebook2audiobook.command --help`
4. Docker (optional): `./ebook2audiobook.command --script_mode build_docker` (see [Docker](README.md#docker)).

> [!NOTE]
**`python_env/`, `models/`, `tmp/`, `run/`, `audiobooks/` and the engine venvs are local only and ignored by git.<br>
Never commit them, nor any generated audio.**

<a id="project-layout"></a>
## Project Layout
| Path | Content |
|---|---|
| `app.py` | Entry point and CLI arguments |
| `ebook2audiobook.command` / `ebook2audiobook.cmd` | Launch and install scripts (Linux/MacOS / Windows) |
| `lib/conf.py` | Global settings (paths, formats, devices) |
| `lib/conf_models.py` | TTS engines list (`TTS_ENGINES`) and their settings (`default_engine_settings`) |
| `lib/conf_lang.py` | Languages and language-specific text rules |
| `lib/core.py` | Conversion pipeline (extraction, sentence splitting, TTS, assembly) |
| `lib/gradio.py`, `lib/header.css`, `lib/header.js` | Web GUI |
| `lib/lang/` | GUI/CLI strings (`legends_<iso3>.py`) |
| `lib/classes/` | Shared classes (TTS manager, device detection, translation, voice extraction, etc.) |
| `lib/classes/tts_engines/` | One module per TTS engine, plus `common/`, `presets/` and `workers/` |
| `components/` | GPU detection and runtime fixes |
| `voices/` | Built-in voices downloaded on first run from the E2A-Voices dataset, `voices/<iso3>/<age>/<gender>/` |
| `tools/` | Standalone tools, i18n sync scripts and CI test files |
| `readme/` | Translated READMEs (generated) |
| `Notebooks/` | Colab and Kaggle notebooks |
| `.github/workflows/` | CI workflows |

<a id="branches-and-pull-requests"></a>
## Branches and Pull Requests
- Create a dedicated branch in your fork for each change:
	```bash
	git checkout -b fix/short-description
	```
- One topic per pull request. Small, focused PRs are reviewed and merged much faster than large ones.
- Keep your branch up to date with the target branch of your pull request, and never commit merge conflict markers.
- In the PR description, explain **what** changed and **why**, link the related issue (`Fixes #123`),
  and list how you tested it (OS, device, engine, language, GUI and/or headless).
- Keep the PR free of unrelated changes: no mass reformatting, no renaming, no drive-by refactors.
- Answer review comments and push the fixes to the same branch. PRs inactive for 10 days are marked stale
  and closed 10 days later.

<a id="python-code-normalization"></a>
## Python Code Normalization
All Python code must follow these rules. Match the style of the surrounding code and don't reformat
code you didn't change. Don't run auto-formatters like `black` or `ruff format` on the project:
their output does not follow these rules.

- no blank line between code, unless between functions and classes.
- single quote used for all key unless for dict() and json. dict['key'] always called with single quote
- 4 spaces indentation, not tab at all
- strict typing for all functions and its arguments declaration and return values
- no space between the argument and its typing, no space between the function, the "->" and the return value

Example:

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

Also:
- E2A runs on Windows, Linux, MacOS, ARM and Docker, on CPU, CUDA, ROCm, XPU, MPS and Jetson.
  Use `os.path` for paths, never hardcode `/` or `\`, and don't assume a device is present.
- Comments explain **why**, not what. Keep them short and in English.

<a id="launch-scripts"></a>
## Launch Scripts
`ebook2audiobook.command` (bash, Linux/MacOS) and `ebook2audiobook.cmd` (batch, Windows) do the same job.
A change in one of them (new option, new program to install, new check) must be done in the other one too.
The same applies to `uninstall.command` / `uninstall.cmd` and to `tools/translate_ebook.sh` / `tools/translate_ebook.cmd`.
`ebook2audiobook.sh`, `e2a.sh` and `uninstall.sh` are symlinks: don't replace them with files.

<a id="user-facing-strings-legends"></a>
## User-Facing Strings (Legends)
Every message shown to the user (GUI labels, CLI help, errors, progress) goes through `legends`,
never a hardcoded string:

```python
from lib.lang import legends

error = legends['error_invalid_fine_tuned'].format(model=fine_tuned, models=list(self.models.keys()))
```

- Add or change keys **only in `lib/lang/legends_eng.py`**.
- The [Sync legends translations](.github/workflows/Legends-i18n.yml) workflow translates the new or changed keys
  into the other `legends_<iso3>.py` files automatically when the change reaches `main`.
- Keep `{placeholders}`, `--options`, file names and HTML tags intact: the translator protects them as is.
- Native speakers are welcome to fix a translated legend directly in its `legends_<iso3>.py`.

<a id="readme-and-translations"></a>
## README and Translations
- Edit **only `README.md`** (English). The [Sync README translations](.github/workflows/Readme-i18n.yml) workflow
  updates the 25 `readme/README_<iso3>.md` files when the change reaches `main`.
- Don't edit `tools/readme_i18n/baseline_README.md` or `tools/readme_i18n/cache.json` by hand: the sync
  manages them.
- Fixes to a translation by a native speaker are welcome directly in its `readme/README_<iso3>.md`.
  The sync only retranslates the README blocks whose English source changed, so a fix is kept until then.
- If you add a heading, add its `<a id="..."></a>` anchor and its entry in the Table of Contents.
- `CONTRIBUTING.md` is maintained in English only and is not part of the translation sync.

<a id="adding-or-changing-a-tts-engine"></a>
## Adding or Changing a TTS Engine
Open a feature request first: each engine adds install size, maintenance and CI time.
An engine is made of:

1. **`lib/conf_models.py`**: a key in `TTS_ENGINES` and its entry in `default_engine_settings`
   (samplerate, files, languages, voices, rating, and for an isolated engine its source, python and requirements).
2. **`lib/classes/tts_engines/<engine>.py`**: the engine class, registered by name:
	```python
	class MyEngine(TTSUtils, TTSRegistry, name='myengine'):
	```
   then imported in `lib/classes/tts_engines/__init__.py`. Use the helpers in `common/` (audio, utils,
   voice conversion) instead of duplicating them.
3. **`lib/classes/tts_engines/presets/<engine>_presets.py`**: a `models` dict with at least the `internal` preset
   and the fine-tuned models.
4. **`lib/classes/tts_engines/workers/<engine>_worker.py`** (only if the engine's dependencies conflict with
   `requirements.txt`): the engine then runs in its own uv venv under `lib/classes/tts_engines/venvs/<engine>`
   behind a persistent worker. See `gptsovits.py` and `workers/gptsovits_worker.py` as reference.
5. **Legends** for the new GUI tab, parameters and messages in `lib/lang/legends_eng.py`.
6. **README**: the engine in the ROADMAP `TTS engines` list.
7. **CI**: a headless test step in `.github/workflows/E2A-Test.yml` when the engine can run on the test runner.

Pin upstream sources to a commit or a release (never a moving branch), and state the engine's license and the
license of its model weights in the PR: they must allow redistribution and use by E2A users.

<a id="dependencies"></a>
## Dependencies
- `requirements.txt` is the main environment shared by all engines. Adding or upgrading a package there can break
  other engines: explain why it's needed in the PR, and test at least two engines.
- Packages needed by only one engine with conflicting pins belong to that engine's own venv, not to `requirements.txt`.
- A new system program must be installed by both launch scripts and by the `Dockerfile`.
- Supported Python versions are 3.10 to 3.12.

<a id="testing"></a>
## Testing
There is no unit test suite. Changes are validated by real conversions.

- Test with the headless samples in `tools/workflow-testing/`, i.e.:
	```bash
	./ebook2audiobook.command --headless --language eng --ebook "tools/workflow-testing/test1.txt" --tts_engine XTTS --voice "voices/eng/elder/male/DavidAttenborough.wav"
	```
- Test the GUI too if your change touches `lib/gradio.py`, `lib/core.py` or the session flow.
- Test on every OS and device you have access to, and say in the PR which ones you tested and which ones you couldn't.
- A change to text processing (splitting, numbers, SML tags) must be tested with at least one non-English language,
  ideally one with a non-Latin script.
- The [E2A Test](.github/workflows/E2A-Test.yml) workflow runs headless conversions with several engines on a
  self-hosted runner, on `main`, on releases and on demand. Your manual tests are what gets your PR reviewed.

<a id="commit-messages"></a>
## Commit Messages
- Imperative mood, short first line: `Fix NameError lib_ze in Intel XPU Level Zero detection`
- An optional scope prefix when it helps: `readme_i18n: reject token reorders the retry cannot prove`
- Explain the why in the body when the change is not obvious.
- No `[skip ci]`: it is reserved to the translation bots.

<a id="license"></a>
## License
ebook2audiobook is released under the [Apache License 2.0](LICENSE). By submitting a contribution, you agree
that it is licensed under the same license (section 5 of the license), and you confirm that you have the right
to submit it: your own code, or code, models and voices under a compatible license with their attribution kept.
