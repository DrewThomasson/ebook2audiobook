#!/bin/zsh
# Prevent Conda from initializing
export CONDA_SHLVL=0
unset CONDA_PREFIX
unset CONDA_DEFAULT_ENV
# Change directory to the location of the launcher
cd "$(dirname "$0")"
# Execute the ebook2audiobook.sh script
./ebook2audiobook.sh
