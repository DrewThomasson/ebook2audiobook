#!/usr/bin/env bash

PYTHON_VERSION="3.12"
export TTS_CACHE="./models"

ARGS="$@"

# Declare an associative array
declare -A arguments

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --*)
            key="${1/--/}" # Remove leading '--'
            if [[ -n "$2" && ! "$2" =~ ^-- ]]; then
                # If the next argument is a value (not another option)
                arguments[$key]="$2"
                shift # Move past the value
            else
                # Set to true for flags without values
                arguments[$key]=true
            fi
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift # Move to the next argument
done

NATIVE="native"
DOCKER_UTILS="docker_utils"
FULL_DOCKER="full_docker"

SCRIPT_MODE="$NATIVE"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

WGET=$(which wget 2>/dev/null)
REQUIRED_PROGRAMS=("calibre" "ffmpeg")
DOCKER_UTILS_IMG="utils"
PYTHON_ENV="python_env"
CURRENT_ENV=""

if [[ "$OSTYPE" != "linux"* && "$OSTYPE" != "darwin"* ]]; then
	echo "Error: OS $OSTYPE unsupported."
	exit 1;
fi

ARCH=$(arch)

if [[ "$OSTYPE" == "linux"* ]]; then
	if [[ "$ARCH" == "x86_64" ]]; then
		CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
	elif [[ "$ARCH" == "aarch64" ]]; then
		CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
	else
		echo "Error: Unsupported architecture for Linux: $ARCH."
		exit 1
	fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
	if [[ "$ARCH" == "x86_64" ]]; then
		CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
	elif [[ "$ARCH" == "arm64" ]]; then
		CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
	else
		echo "Error: Unsupported architecture for MacOS: $ARCH. Are you possibly using Rosetta?"
		exit 1
	fi
fi

CONDA_INSTALLER=/tmp/Miniconda3-latest.sh
CONDA_INSTALL_DIR=$HOME/miniconda3
CONDA_PATH=$HOME/miniconda3/bin
CONDA_ENV=~/miniconda3/etc/profile.d/conda.sh
CONFIG_FILE="$HOME/.bashrc"
PATH="$CONDA_PATH:$PATH"

declare -a programs_missing

# Check if the current script is run inside a docker container
if [[ -n "$container" || -f /.dockerenv ]]; then
	SCRIPT_MODE="$FULL_DOCKER"
else
	if [[ -n "${arguments['script_mode']+exists}" ]]; then
		if [ "${arguments['script_mode']}" = "$NATIVE" ] || [ "${arguments['script_mode']}" = "$DOCKER_UTILS" ]; then
			SCRIPT_MODE="${arguments['script_mode']}"
		fi
	fi
fi

# Check if running in a Conda or Python virtual environment
if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
    CURRENT_ENV="$CONDA_PREFIX"
elif [[ -n "$VIRTUAL_ENV" ]]; then
    CURRENT_ENV="$VIRTUAL_ENV"
fi

# If neither environment variable is set, check Python path
if [[ -z "$CURRENT_ENV" ]]; then
    PYTHON_PATH=$(which python 2>/dev/null)
    if [[ ( -n "$CONDA_PREFIX" && "$PYTHON_PATH" == "$CONDA_PREFIX/bin/python" ) || ( -n "$VIRTUAL_ENV" && "$PYTHON_PATH" == "$VIRTUAL_ENV/bin/python" ) ]]; then
        CURRENT_ENV="${CONDA_PREFIX:-$VIRTUAL_ENV}"
    fi
fi

# Output result if a virtual environment is detected
if [[ -n "$CURRENT_ENV" ]]; then
    echo -e "Current python virtual environment detected: $CURRENT_ENV."
    echo -e "This script runs with its own virtual env and must be out of any other virtual environment when it's launched."
    echo -e "If you are using miniconda then you would type in:"
    echo -e "conda deactivate"
    exit 1
fi

function required_programs_check {
	local programs=("$@")
	for program in "${programs[@]}"; do
		if ! command -v "$program" >/dev/null 2>&1; then
			echo -e "\e[33m$program is not installed.\e[0m"
			programs_missing+=($program)
		fi
	done
	local count=${#programs_missing[@]}
	if [[ $count -eq 0 ]]; then
		return 0
	else
		return 1
	fi
}

function install_programs {
	echo -e "\e[33mInstalling required programs. NOTE: you must have 'sudo' priviliges or it will fail.\e[0m"
	if [[ "$OSTYPE" = "darwin"* ]]; then
		PACK_MGR="brew install"
			if ! command -v brew &> /dev/null; then
				echo -e "\e[33mHomebrew is not installed. Installing Homebrew...\e[0m"
				/usr/bin/env bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
				echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
				eval "$(/opt/homebrew/bin/brew shellenv)"
			fi
	else
		if command -v emerge &> /dev/null; then
			PACK_MGR="sudo emerge"
		elif command -v dnf &> /dev/null; then
			PACK_MGR="sudo dnf install"
			PACK_MGR_OPTIONS="-y"
		elif command -v yum &> /dev/null; then
			PACK_MGR="sudo yum install"
			PACK_MGR_OPTIONS="-y"
		elif command -v zypper &> /dev/null; then
			PACK_MGR="sudo zypper install"
			PACK_MGR_OPTIONS="-y"
		elif command -v pacman &> /dev/null; then
			PACK_MGR="sudo pacman -Sy"
		elif command -v apt-get &> /dev/null; then
			sudo apt-get update
			PACK_MGR="sudo apt-get install"
			PACK_MGR_OPTIONS="-y"
		elif command -v apk &> /dev/null; then
			PACK_MGR="sudo apk add"
		else
			echo "Cannot recognize your applications package manager. Please install the required applications manually."
			return 1
		fi
		
	fi
	if [ -z "$WGET" ]; then
		echo -e "\e[33m wget is missing! trying to install it... \e[0m"
		result=$(eval "$PACK_MGR wget $PACK_MGR_OPTIONS" 2>&1)
		result_code=$?
		if [ $result_code -eq 0 ]; then
			WGET=$(which wget 2>/dev/null)
		else
			echo "Cannot 'wget'. Please install 'wget'  manually."
			return 1
		fi
	fi
	for program in "${programs_missing[@]}"; do
		if [ "$program" = "calibre" ];then				
			# avoid conflict with calibre builtin lxml
			pip uninstall lxml -y 2>/dev/null
			echo -e "\e[33mInstalling Calibre...\e[0m"
			if [[ "$OSTYPE" = "darwin"* ]]; then
				eval "$PACK_MGR --cask calibre"
			else
				$WGET -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin
			fi
			if command -v calibre >/dev/null 2>&1; then
				echo -e "\e[32m===============>>> Calibre is installed! <<===============\e[0m"
			else
				echo "Calibre installation failed."
			fi
		else
			eval "$PACK_MGR $program $PKG_MGR_OPTIONS"				
			if command -v $program >/dev/null 2>&1; then
				echo -e "\e[32m===============>>> $program is installed! <<===============\e[0m"
			else
				echo "$program installation failed."
			fi
		fi
	done
	if required_programs_check "${REQUIRED_PROGRAMS[@]}"; then
		return 0
	else
		echo -e "\e[33mYou can run 'ebook2audiobook.sh --script_mode docker_utils' to avoid to install $REQUIRED_PROGRAMS natively.\e[0m"
		return 1
	fi
}

function conda_check {
	if ! command -v conda &> /dev/null; then
		echo -e "\e[33mconda is not installed!\e[0m"
		echo -e "\e[33mDownloading conda installer...\e[0m"
		wget -O "$CONDA_INSTALLER" "$CONDA_URL"
		if [[ -f "$CONDA_INSTALLER" ]]; then
			echo -e "\e[33mInstalling Miniconda...\e[0m"
			bash "$CONDA_INSTALLER" -u -b -p "$CONDA_INSTALL_DIR"
			rm -f "$CONDA_INSTALLER"
			if [[ -f "$CONDA_INSTALL_DIR/bin/conda" ]]; then
				conda init
				echo -e "\e[32m===============>>> conda is installed! <<===============\e[0m"
			else
				echo -e "\e[31mconda installation failed.\e[0m"		
				return 1
			fi
		else
			echo -e "\e[31mFailed to download Miniconda installer.\e[0m"
			echo -e "\e[33mI'ts better to use the install.sh to install everything needed.\e[0m"
			return 1
		fi
	fi
	if [[ ! -d $SCRIPT_DIR/$PYTHON_ENV ]]; then
		# Use this condition to chmod writable folders once
		chmod -R 777 ./audiobooks ./tmp ./models
		conda create --prefix $SCRIPT_DIR/$PYTHON_ENV python=$PYTHON_VERSION -y
		source $CONDA_ENV
		conda activate $SCRIPT_DIR/$PYTHON_ENV
		python -m pip install --upgrade pip
		python -m pip install --upgrade -r requirements.txt --progress-bar=on
		conda deactivate
	fi
	return 0
}

function docker_check {
	if ! command -v docker &> /dev/null; then
		echo -e "\e[33m docker is missing! trying to install it... \e[0m"
		if [[ "$OSTYPE" == "darwin"* ]]; then
			echo "Installing Docker using Homebrew..."
			$PACK_MGR --cask docker $PACK_MGR_OPTIONS
		else
			$WGET -qO get-docker.sh https://get.docker.com && \
			sudo sh get-docker.sh
			sudo systemctl start docker
			sudo systemctl enable docker
			docker run hello-world
			rm -f get-docker.sh
		fi
		echo -e "\e[32m===============>>> docker is installed! <<===============\e[0m"
		docker_build
	else
		# Check if Docker service is running
		if docker info >/dev/null 2>&1; then
			if [[ "$(docker images -q $DOCKER_UTILS_IMG 2> /dev/null)" = "" ]]; then
				docker_build
			fi
		else
			echo -e "\e[33mDocker is not running\e[0m"
			return 1
		fi
	fi
	return 0
}

function docker_build {
# Check if the Docker socket is accessible
	if [[ -e /var/run/docker.sock || -e /run/docker.sock ]]; then
		echo -e "\e[33mDocker image '$DOCKER_UTILS_IMG' not found. Trying to build it...\e[0m"
		docker build -f DockerfileUtils -t utils .
	else
		echo -e "\e[33mcannot connect to docker socket. Check if the docker socket is running.\e[0m"
	fi
}

if [ "$SCRIPT_MODE" = "$FULL_DOCKER" ]; then
	echo -e "\e[33mRunning in $FULL_DOCKER mode\e[0m"
	python app.py --script_mode $SCRIPT_MODE $ARGS
elif [[ "$SCRIPT_MODE" == "$NATIVE" || "$SCRIPT_MODE" = "$DOCKER_UTILS" ]]; then
	pass=true
	if [ "$SCRIPT_MODE" == "$NATIVE" ]; then
		echo -e "\e[33mRunning in $NATIVE mode\e[0m"
		if ! required_programs_check "${REQUIRED_PROGRAMS[@]}"; then
			if ! install_programs; then
				pass=false
			fi
		fi
	else
		echo -e "\e[33mRunning in $DOCKER_UTILS mode\e[0m"
		if conda_check; then
			if docker_check; then
				source $CONDA_ENV
				conda activate $SCRIPT_DIR/$PYTHON_ENV
				python app.py --script_mode $DOCKER_UTILS $ARGS
				conda deactivate
			fi
		fi
	fi
	if [ $pass = true ]; then
		if conda_check; then
			source $CONDA_ENV
			conda activate $SCRIPT_DIR/$PYTHON_ENV
			python app.py --script_mode $SCRIPT_MODE $ARGS
			conda deactivate
		fi
	fi
else
	echo -e "\e[33mebook2audiobook is not correctly installed or run.\e[0m"
fi

exit 0
