#!/usr/bin/env bash

# Parameters passed to the script
PARAMS="$@"

# Check for conda and docker installation
if ! command -v conda &> /dev/null; then
    echo -e "\e[31mConda is not installed. Please install it first.\e[0m"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "\e[31mDocker is not installed. Please install it first.\e[0m"
    exit 1
fi

# Docker image name
DOCKER_IMG="utils"

# Activate conda only if conda is installed and the environment exists
if [[ -d ./python_env ]]; then
    # Check if Docker image exists
    if [[ "$(docker images -q $DOCKER_IMG 2> /dev/null)" != "" ]]; then
        # Source conda and activate the environment
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate ./python_env

        # Run the Python application with passed parameters
        python app.py "$@"
        
        # Deactivate conda environment
        conda deactivate
		exit 0
    else
        echo -e "\e[31mDocker image '$DOCKER_IMG' not found. Please build or pull the image.\e[0m"
    fi
else
    echo -e "\e[31mConda environment './python_env' not found.\e[0m"
fi

# If we reach here, something went wrong
echo -e "\e[33m ebook2audiobookXTTS is not correctly installed. Try running install.sh again. \e[0m"

exit 1
