#!/usr/bin/env bash

if [[ "$OSTYPE" = "darwin"* && -z "$SWITCHED_TO_ZSH" && "$(ps -p $$ -o comm=)" != "zsh" ]]; then
    export SWITCHED_TO_ZSH=1
    exec env zsh "$0" "$@"
fi

unset SWITCHED_TO_ZSH

ARCH=$(uname -m)
PYTHON_VERSION="3.12"

export PYTHONUTF8="1"
export PYTHONIOENCODING="utf-8"
export TTS_CACHE="./models"

ARGS=("$@")

declare -A arguments # associative array
declare -a programs_missing # indexed array

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
FULL_DOCKER="full_docker"

SCRIPT_MODE="$NATIVE"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

WGET=$(which wget 2>/dev/null)
REQUIRED_PROGRAMS=("curl" "calibre" "ffmpeg" "nodejs" "espeak-ng" "rust" "sox")
PYTHON_ENV="python_env"
CURRENT_ENV=""

if [[ "$OSTYPE" != "linux"* && "$OSTYPE" != "darwin"* ]]; then
	echo "Error: OS $OSTYPE unsupported."
	exit 1;
fi

if [[ "$OSTYPE" = "darwin"* ]]; then
	CONDA_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-$(uname -m).sh"
	CONFIG_FILE="$HOME/.zshrc"
	if [[ "$ARCH" == "x86_64" ]]; then
		PYTHON_VERSION="3.11"
	fi
elif [[ "$OSTYPE" = "linux"* ]]; then
	CONDA_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
	CONFIG_FILE="$HOME/.bashrc"
fi

CONDA_INSTALLER="/tmp/Miniforge3.sh"
CONDA_INSTALL_DIR="$HOME/Miniforge3"
CONDA_PATH="$CONDA_INSTALL_DIR/bin"
CONDA_ENV="$CONDA_INSTALL_DIR/etc/profile.d/conda.sh"

export TMPDIR="$SCRIPT_DIR/.cache"
export PATH="$CONDA_PATH:$PATH"

# Check if the current script is run inside a docker container
if [[ -n "$container" || -f /.dockerenv ]]; then
	SCRIPT_MODE="$FULL_DOCKER"
else
	if [[ -n "${arguments['script_mode']+exists}" ]]; then
		if [ "${arguments['script_mode']}" = "$NATIVE" ]; then
			SCRIPT_MODE="${arguments['script_mode']}"
		fi
	fi
fi

if [[ -n "${arguments['help']+exists}" && ${arguments['help']} = true ]]; then
	python app.py "${ARGS[@]}"
else
	# Check if running in a Conda or Python virtual environment
	if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
		CURRENT_ENV="$CONDA_PREFIX"
	elif [[ -n "$VIRTUAL_ENV" ]]; then
		CURRENT_ENV="$VIRTUAL_ENV"
	fi

	# If neither environment variable is set, check Python path
	if [[ -z "$CURRENT_ENV" ]]; then
		PYTHON_PATH=$(which python 2>/dev/null)
		if [[ ( -n "$CONDA_PREFIX" && "$PYTHON_PATH" = "$CONDA_PREFIX/bin/python" ) || ( -n "$VIRTUAL_ENV" && "$PYTHON_PATH" = "$VIRTUAL_ENV/bin/python" ) ]]; then
			CURRENT_ENV="${CONDA_PREFIX:-$VIRTUAL_ENV}"
		fi
	fi

	# Output result if a virtual environment is detected
	if [[ -n "$CURRENT_ENV" ]]; then
		echo -e "Current python virtual environment detected: $CURRENT_ENV."
		echo -e "This script runs with its own virtual env and must be out of any other virtual environment when it's launched."
		echo -e "If you are using conda then you would type in:"
		echo -e "conda deactivate"
		exit 1
	fi
	
	# Check if .cache folder exists inside the eb2ab folder for Miniforge3
	if [[ ! -d .cache ]]; then
		mkdir .cache
	fi

	function required_programs_check {
		local programs=("$@")
		programs_missing=()
		for program in "${programs[@]}"; do
			if [ "$program" = "nodejs" ]; then
				bin="node"
			elif [ "$program" = "rust" ]; then
				if command -v apt-get &> /dev/null; then
					bin="rustc"
				fi
			else
				bin="$program"
			fi
			if ! command -v "$bin" >/dev/null 2>&1; then
				echo -e "\e[33m$program is not installed.\e[0m"
				programs_missing+=("$program")
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
		if [[ "$OSTYPE" = "darwin"* ]]; then
			echo -e "\e[33mInstalling required programs...\e[0m"
			if [ ! -d $TMPDIR ]; then
				mkdir -p $TMPDIR
			fi
			SUDO=""
			PACK_MGR="brew install"
				if ! command -v brew &> /dev/null; then
					echo -e "\e[33mHomebrew is not installed. Installing Homebrew...\e[0m"
					/usr/bin/env bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
					echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> $HOME/.zprofile
					eval "$(/opt/homebrew/bin/brew shellenv)"
				fi
		else
			SUDO="sudo"
			echo -e "\e[33mInstalling required programs. NOTE: you must have 'sudo' priviliges to install ebook2audiobook.\e[0m"
			PACK_MGR_OPTIONS=""
			if command -v emerge &> /dev/null; then
				PACK_MGR="emerge"
			elif command -v dnf &> /dev/null; then
				PACK_MGR="dnf install"
				PACK_MGR_OPTIONS="-y"
			elif command -v yum &> /dev/null; then
				PACK_MGR="yum install"
				PACK_MGR_OPTIONS="-y"
			elif command -v zypper &> /dev/null; then
				PACK_MGR="zypper install"
				PACK_MGR_OPTIONS="-y"
			elif command -v pacman &> /dev/null; then
				PACK_MGR="pacman -Sy"
			elif command -v apt-get &> /dev/null; then
				$SUDO apt-get update
				PACK_MGR="apt-get install"
				PACK_MGR_OPTIONS="-y"
			elif command -v apk &> /dev/null; then
				PACK_MGR="apk add"
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
					$WGET -nv -O- https://download.calibre-ebook.com/linux-installer.sh | $SUDO sh /dev/stdin
				fi
				if command -v $program >/dev/null 2>&1; then
					echo -e "\e[32m===============>>> Calibre is installed! <<===============\e[0m"
				else
					eval "$SUDO $PACK_MGR $program $PACK_MGR_OPTIONS"				
					if command -v $program >/dev/null 2>&1; then
						echo -e "\e[32m===============>>> $program is installed! <<===============\e[0m"
					else
						echo "$program installation failed."
					fi
				fi	
			elif [ "$program" = "rust" ]; then
				if command -v apt-get &> /dev/null; then
					app="rustc"
				else
					app="$program"
				fi
				curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
				source $HOME/.cargo/env
				if command -v $app &>/dev/null; then
					echo -e "\e[32m===============>>> $program is installed! <<===============\e[0m"
				else
					echo "$program installation failed."
				fi
			else
				eval "$SUDO $PACK_MGR $program $PACK_MGR_OPTIONS"				
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
			echo "Some programs didn't install successfuly, please report the log to the support"
		fi
	}

	function conda_check {
		if ! command -v conda &> /dev/null || [ ! -f "$CONDA_ENV" ]; then
			echo -e "\e[33mDownloading Miniforge3 installer...\e[0m"
			if [[ "$OSTYPE" = "darwin"* ]]; then
				curl -fsSLo "$CONDA_INSTALLER" "$CONDA_URL"
			else
				wget -O "$CONDA_INSTALLER" "$CONDA_URL"
			fi
			if [[ -f "$CONDA_INSTALLER" ]]; then
				echo -e "\e[33mInstalling Miniforge3...\e[0m"
				bash "$CONDA_INSTALLER" -b -u -p "$CONDA_INSTALL_DIR"
				rm -f "$CONDA_INSTALLER"
				if [[ -f "$CONDA_INSTALL_DIR/bin/conda" ]]; then
					$CONDA_INSTALL_DIR/bin/conda config --set auto_activate_base false
					source $CONDA_ENV
					echo -e "\e[32m===============>>> conda is installed! <<===============\e[0m"
				else
					echo -e "\e[31mconda installation failed.\e[0m"		
					return 1
				fi
			else
				echo -e "\e[31mFailed to download Miniforge3 installer.\e[0m"
				echo -e "\e[33mI'ts better to use the install.sh to install everything needed.\e[0m"
				return 1
			fi
		fi
		if [[ ! -d "$SCRIPT_DIR/$PYTHON_ENV" ]]; then
			# Use this condition to chmod writable folders once
			chmod -R 777 ./audiobooks ./tmp ./models
			conda create --prefix "$SCRIPT_DIR/$PYTHON_ENV" python=$PYTHON_VERSION -y
			conda init > /dev/null 2>&1
			source $CONDA_ENV
			conda activate "$SCRIPT_DIR/$PYTHON_ENV"
			python -m pip cache purge > /dev/null 2>&1
			python -m pip install --upgrade pip
			python -m pip install --upgrade --no-cache-dir --use-pep517 --progress-bar=on -r requirements.txt
			tts_version=$(python -c "import importlib.metadata; print(importlib.metadata.version('coqui-tts'))" 2>/dev/null)
			if [[ -n "$tts_version" ]]; then
				if [[ "$(printf '%s\n' "$tts_version" "0.26.1" | sort -V | tail -n1)" == "0.26.1" ]]; then
					python -m pip install --no-cache-dir --use-pep517 --progress-bar=on 'transformers<=4.51.3'
				fi
			fi
			conda deactivate
		fi
		return 0
	}

	if [ "$SCRIPT_MODE" = "$FULL_DOCKER" ]; then
		python app.py --script_mode "$SCRIPT_MODE" "${ARGS[@]}"
		conda deactivate
		conda deactivate
	elif [ "$SCRIPT_MODE" = "$NATIVE" ]; then
		pass=true
		if [ "$SCRIPT_MODE" = "$NATIVE" ]; then		   
			if ! required_programs_check "${REQUIRED_PROGRAMS[@]}"; then
				if ! install_programs; then
					pass=false
				fi
			fi
		fi
		if [ $pass = true ]; then
			if conda_check; then
				conda init > /dev/null 2>&1
				source $CONDA_ENV
				conda activate "$SCRIPT_DIR/$PYTHON_ENV"
				python app.py --script_mode "$SCRIPT_MODE" "${ARGS[@]}"
				conda deactivate
				conda deactivate
			fi
		fi
	else
		echo -e "\e[33mebook2audiobook is not correctly installed or run.\e[0m"
	fi
fi

exit 0
