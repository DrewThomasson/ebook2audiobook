# Security Policy

## Table of Contents
- [Supported Versions](#supported-versions)
- [Reporting a Vulnerability](#reporting-a-vulnerability)
- [What to Expect](#what-to-expect)
- [Scope](#scope)
- [Security Considerations for Users](#security-considerations-for-users)

<a id="supported-versions"></a>
## Supported Versions
Only the latest release receives security fixes.

| Version | Supported |
|---|---|
| Latest release | :white_check_mark: |
| Any older release | :x: |

Upgrade to the [latest release](https://github.com/DrewThomasson/ebook2audiobook/releases/latest) before reporting.
Your version is in `VERSION.txt`.

<a id="reporting-a-vulnerability"></a>
## Reporting a Vulnerability
Report it in a [new issue](https://github.com/DrewThomasson/ebook2audiobook/issues/new/choose) with the `Security report` template.
Search the open and closed issues first to be sure it hasn't been reported already.

Include:
- E2A version (`VERSION.txt`), OS, script mode (Native/Docker) and process mode (Gradio/Headless)
- The affected component (file, CLI option, GUI element, workflow)
- Steps to reproduce
- The impact: what an attacker can do, and what access they need first (local network, GUI access, a crafted file, etc.)
- A suggested fix, if you have one

> [!IMPORTANT]
**Issues are public: describe the vulnerability and how to reproduce it, but don't post a ready-to-use exploit.<br>
If a full proof of concept is needed, a maintainer will ask you for it.**

Use public-domain texts and your own test files only. Never attach copyrighted eBooks, real personal data or secrets.

> [!WARNING]
**Reports copied from an automated scanner or an A.I. tool without a verified, reproducible impact will be closed.**

<a id="what-to-expect"></a>
## What to Expect
E2A is maintained by volunteers. We aim to:
- acknowledge your report within 7 days
- confirm or decline it in the issue, and keep you informed of the progress
- release a fix, crediting you in the release notes

There is no bug bounty.

<a id="scope"></a>
## Scope
**In scope**
- Path traversal, arbitrary file read or write through uploaded or processed files (eBooks, eBook directories,
  voices, custom model ZIPs, voice maps)
- Code execution through crafted input (eBooks, archives, text, SML tags), beyond the model risk described in
  [Models and voices](#models-and-voices)
- Web GUI session isolation: a user reaching another session's files, audiobooks or settings
- Leak of secrets (Audiobookshelf API token, Hugging Face tokens) in logs, crash reports or the GUI
- Crash report redaction failures: personal data leaving the machine (see [Crash reports](#crash-reports))
- Integrity of downloads: engines, packages, models, voices or sources fetched from a location an attacker can control
- Launch and uninstall scripts, `Dockerfile`, compose files, notebooks and GitHub workflows of this repository

**Out of scope**
- Vulnerabilities in third-party projects (Gradio, PyTorch, coqui-tts, calibre, ffmpeg, the TTS engines, etc.):
  report them upstream. Do tell us if E2A uses them in a vulnerable way or pins an affected version.
- The documented behaviors listed in [Security Considerations for Users](#security-considerations-for-users)
- Denial of service of your own instance through very large or complex eBooks
- Misuse of the tool (DRM, copyright, cloning someone's voice without consent): not a vulnerability,
  see the notice in the [README](README.md)
- Issues of the Hugging Face, Google Colab or Kaggle platforms hosting the demos: report them to the platform

<a id="security-considerations-for-users"></a>
## Security Considerations for Users

<a id="web-gui-exposure"></a>
### Web GUI exposure
- The GUI listens on `0.0.0.0:7860` by default (`interface_host` and `interface_port` in `lib/conf.py`):
  **any device on your network can reach it, and there is no authentication.**
- Anyone who can reach the GUI can upload files and custom models and run conversions on your hardware.
  Treat GUI access as access to the account running E2A.
- To restrict it to your machine:
  - Native: set `interface_host = '127.0.0.1'` in `lib/conf.py`
  - Docker: `-p 127.0.0.1:7860:7860` instead of `-p 7860:7860`
  - Compose: `"127.0.0.1:7860:7860"` in the `ports` of `docker-compose.yml` / `podman-compose.yml`
- For remote access, use a VPN or an SSH tunnel, or a reverse proxy with authentication and HTTPS.
- `--share` creates a public `gradio.live` link through Gradio's relay servers: **anyone with the link has full GUI access.**
  Use it only temporarily, and never on a machine holding private data.

<a id="models-and-voices"></a>
### Models and voices
- Model checkpoints (`.pth`, `.bin`, `.ckpt`, `.pt`) can contain pickled Python code that runs when the model is loaded.
  Only use custom and fine-tuned models from sources you trust, and prefer `.safetensors` models when available.
- On first use, E2A downloads engines, models and voices from Hugging Face, GitHub and PyPI. Engines with their own
  venv install the upstream sources pinned in `lib/conf_models.py`.

<a id="crash-reports"></a>
### Crash reports
- E2A sends anonymized crash reports by default. On an unhandled exception, a JSON report (exception, traceback,
  E2A and package versions, OS and device information, non-identifying settings such as engine, language and device)
  is posted over HTTPS to `bug_report_url` in `lib/conf.py`.
- To diagnose GPU and install problems remotely, the report also holds the GPU model and driver version, the GPU
  library versions (cuDNN, cuBLAS…), GPU memory use at the time of the crash, the GPU selection environment variables
  and `LD_LIBRARY_PATH`. For a GPU error it adds the result of a short GPU test run in a separate process, and for a
  Windows DLL load error the names of the missing or truncated DLLs.
- File paths, your user name, e-mail addresses, IP addresses, tokens and the Audiobookshelf URL and token are redacted
  before sending. Exception messages are truncated, but may still contain a fragment of the text being converted.
- To disable it, set the environment variable `DO_NOT_TRACK=1`, or set `bug_report_enabled = False` in `lib/conf.py`.

<a id="secrets"></a>
### Secrets
- The Audiobookshelf token (`--abs_api_token` or the GUI) is only sent to your Audiobookshelf server (`--abs_url`).
  Prefer an HTTPS URL, and a dedicated Audiobookshelf user limited to the library E2A uploads to.
- Review terminal logs before attaching them to a public issue: remove tokens, paths and anything private.

<a id="installation"></a>
### Installation
- The launch scripts install `uv`, Homebrew (macOS) or Scoop (Windows) and the system programs E2A needs.
  Read them before running if your environment requires it.
- Run E2A as a regular user, not as root or administrator. Docker gives the strongest isolation from your system.
