================================================================================
ebook2audiobook — local install notes
================================================================================

Project    : DrewThomasson/ebook2audiobook
Local path : /mnt/applications/Linux Applications/_Handy Scripts/_Workshop/
             ebook2audiobook/
Installed  : 02/05/2026
Status     : Working end-to-end (TXT input -> CUDA XTTSv2 -> FLAC + cover + VTT)
Hardware   : NVIDIA GeForce RTX 4070 Ti (12 GB) on CachyOS Linux

This Docs/ folder describes:

  01_INSTALL.txt          What was installed and where
  02_PATCHES.txt          Five+ patches applied to upstream files
  03_USAGE.txt            How to launch and use the tool
  04_VOICES.txt           Description of each shipped voice sample
  05_TROUBLESHOOTING.txt  Known errors and their fixes
  06_MOVING.txt           How to relocate the project

Quick start:

    cd /mnt/applications/Linux\ Applications/_Handy\ Scripts/_Workshop/ebook2audiobook
    ./start.sh

Open http://0.0.0.0:7860/ in a browser (start.sh does this for you).

To stop: Ctrl+C in the terminal running start.sh.

================================================================================
