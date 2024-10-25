#!/usr/bin/env bash

PARAMS="$@"

SCRIPT_MODE=""

NATIVE="native"
DOCKER_UTILS="docker_utils"
FULL_DOCKER="full_docker"

REQUIRED_PROGRAMS=("calibre" "ffmpeg")
PYTHON_ENV_DOCKER_UTILS="./python_env"


function check_external_programs {
    programs=("$@")
    for program_name in "${programs[@]}"; do
        if ! command -v "$program_name" > /dev/null 2>&1; then
            echo -e "\e[33m${program_name} is not installed\e[0m"
            return 1
        fi
    done
    return 0
}

function check_docker {
    if [ -f /.dockerenv ] || grep -qE '(docker|lxc)' /proc/1/cgroup 2>/dev/null; then
        echo "Running in Docker"
        return 0
    fi
    if [[ "$OSTYPE" == "darwin"* ]]; then 
        if pgrep -xq "Docker"; then
            return 0
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if systemctl is-active --quiet docker; then
            return 0
        fi
    fi
    return 1
}

if check_external_programs "${REQUIRED_PROGRAMS[@]}"; then
    echo -e "\e[33mRunning in native mode\e[0m"
	SCRIPT_MODE="$NATIVE"
elif check_docker; then
	if [[ -d $PYTHON_ENV_DOCKER_UTILS ]]; then
		echo -e "\e[33mRunning in docker utils mode\e[0m"
		PYTHON_INSTALL_ENV="$(readlink -f $PYTHON_ENV_DOCKER_UTILS)"
		SCRIPT_MODE="$DOCKER_UTILS"
	else
		# Method 1: Check if the "container" environment variable is set
		if [[ -n "$container" || -f /.dockerenv ]]; then
			echo -e "\e[33mRunning inside Docker (detected via environment variable)\e[0m"
			SCRIPT_MODE="$FULL_DOCKER"
		else
			SCRIPT_MODE="$NATIVE"
		fi
	fi
else
    echo -e "\e[33mCould not determine in which mode to run the script. Exiting...\e[0m"
    exit 1
fi

if [ "$SCRIPT_MODE" = "$NATIVE" ]; then
	python app.py --script_mode "$NATIVE" $PARAMS
	exit 0
elif [ "$SCRIPT_MODE" = "$DOCKER_UTILS" ]; then
	CONDA_PATH="$HOME/miniconda3/bin"
	CONFIG_FILE="$HOME/.bashrc"
	PATH=$CONDA_PATH:$PATH
	DOCKER_UTILS_NAME="utils"
	
	source "$CONFIG_FILE"

	if ! command -v conda &> /dev/null; then
		echo -e "\e[33mConda is not installed. Please install it first.\e[0m"
	elif command -v docker &> /dev/null; then
		if [[ "$(docker images -q $DOCKER_UTILS_NAME 2> /dev/null)" != "" ]]; then
			source $(conda info --base)/etc/profile.d/conda.sh
			conda activate $PYTHON_INSTALL_ENV
			python app.py "$@"
			python app.py --script_mode "docker_utils" $PARAMS
			conda deactivate
			exit 0
		else
			echo -e "\e[33mDocker image '$DOCKER_UTILS_NAME' not found. Please build or pull the image.\e[0m"
		fi
	else
		echo -e "\e[33mDocker is not installed. Please install it first.\e[0m"
	fi
elif [ "$SCRIPT_MODE" = "$FULL_DOCKER" ]; then
	python app.py --script_mode "$FULL_DOCKER" $PARAMS
	exit 0
else
	echo -e "\e[33mebook2audiobook is not correctly installed. Try running install.sh again. \e[0m"
fi

exit 1
