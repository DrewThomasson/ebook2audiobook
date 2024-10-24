#!/usr/bin/env bash

# Parameters passed to the script
PARAMS="$@"
CONDA_PATH="$HOME/miniconda3/bin"
CONFIG_FILE="$HOME/.bashrc"
PATH=$CONDA_PATH:$PATH

source "$CONFIG_FILE"

# Check for conda and docker installation
if ! command -v conda &> /dev/null; then
    echo -e "\e[31mConda is not installed. Please install it first.\e[0m"
    exit 1
fi

if [[ -d ./python_env ]]; then

	if ! command -v docker &> /dev/null; then
		echo -e "\e[31mDocker is not installed. Please install it first.\e[0m"
		exit 1
	fi

	# Docker image name
	DOCKER_IMG="utils"
	
    # Check if Docker image exists
    if [[ "$(docker images -q $DOCKER_IMG 2> /dev/null)" != "" ]]; then
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate ./python_env
        python app.py "$@"
        conda deactivate
		exit 0
    else
        echo -e "\e[31mDocker image '$DOCKER_IMG' not found. Please build or pull the image.\e[0m"
    fi
else
    python app.py "$@"
	exit 0
fi

# If we reach here, something went wrong
echo -e "\e[33m ebook2audiobook is not correctly installed. Try running install.sh again. \e[0m"

exit 1
