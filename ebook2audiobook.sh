#!/usr/bin/env bash

PYTHON_VERSION="3.11"

ARGS="$@"

NATIVE="native"
DOCKER_UTILS="docker_utils"
FULL_DOCKER="full_docker"

SCRIPT_MODE=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REQUIRED_PROGRAMS=("calibre" "ffmpeg")
DOCKER_UTILS_IMG="utils"
PYTHON_ENV="python_env"

if [[ "$OSTYPE" = "darwin"* ]]; then
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
else
	MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
fi

MINICONDA_INSTALLER="/tmp/Miniconda3-latest.sh"
CONDA_PATH="$HOME/miniconda3/bin"
INSTALL_DIR="$HOME/miniconda3"
CONFIG_FILE="$HOME/.bashrc"
PATH="$CONDA_PATH:$PATH"

# Check if the current script is run inside a docker container
if [[ -n "$container" || -f /.dockerenv ]]; then
	SCRIPT_MODE="$FULL_DOCKER"
fi

declare -a programs_missing

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

function docker_check {
	if ! command -v docker &> /dev/null; then
		echo -e "\e[33mDocker is not installed.\e[0m"
		return 1
	else
		# Check if Docker service is running
		if ! docker info >/dev/null 2>&1; then
			echo "\e[33mDocker is not running\e[0m"
			return 1
		fi
		return 0
	fi
}

function conda_check {
	if ! command -v conda &> /dev/null; then
		echo -e "\e[33mMiniconda is not installed!\e[0m"
		echo -e "\e[33mDownloading Miniconda installer...\e[0m"
		wget -O "$MINICONDA_INSTALLER" "$MINICONDA_URL"
		if [[ -f "$MINICONDA_INSTALLER" ]]; then
			echo -e "\e[33mInstalling Miniconda...\e[0m"
			bash "$MINICONDA_INSTALLER" -b -p "$INSTALL_DIR"
			rm -f "$MINICONDA_INSTALLER"
			if [[ -f "$INSTALL_DIR/bin/conda" ]]; then
				echo -e "\e[33Miniconda installed successfully!\e[0m"
				return 0
			else
				echo -e "\e[31mMiniconda installation failed.\e[0m"		
				return 1
			fi
		else
			echo -e "\e[31mFailed to download Miniconda installer.\e[0m"
			echo -e "\e[33mI'ts better to use the install.sh to install everything needed.\e[0m"
			return 1
		fi
	fi
	return 0
}

if [ "$SCRIPT_MODE" != "$FULL_DOCKER" ]; then
	if [ "$SCRIPT_MODE" = "$DOCKER_UTILS" ]; then
		if docker_check; then
			if [[ "$(docker images -q $DOCKER_UTILS_IMG 2> /dev/null)" = "" ]]; then
				echo -e "\e[33mDocker image '$DOCKER_UTILS_IMG' not found. Installing it now...\e[0m"
				pip install --upgrade pip && \
				pip install pydub nltk beautifulsoup4 ebooklib unidic translate coqui-tts tqdm mecab mecab-python3 docker gradio>=4.44.0  && \
				python -m unidic download && \
				python -m spacy download en_core_web_sm && \
				pip install -e .
			fi	
		else
			echo -e "\e[33mDocker failed to run. Try to run ebook2audiobook in full docker mode.\e[0m"
			exit 1
		fi
	else
		if required_programs_check "${REQUIRED_PROGRAMS[@]}"; then
			SCRIPT_MODE="$NATIVE"
		else
			if [[ "$OSTYPE" = "darwin"* ]]; then
				PACK_MGR="brew install"
					if ! command -v brew &> /dev/null; then
						echo "Homebrew is not installed. Installing Homebrew..."
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
				fi
				
			fi

			if [ -z "$WGET" ]; then
				echo -e "\e[33m wget is missing! trying to install it... \e[0m"
				if [ "$PACK_MGR" != "" ]; then
					eval "$PACK_MGR wget $PACK_MGR_OPTIONS"
					WGET=$(which wget 2>/dev/null)
				else
					echo "Cannot recognize your package manager. Please install wget manually."
					exit 1
				fi
			fi
			
			if [ "$WGET" != "" ]; then
				for program in "${programs_missing[@]}"; do
					if [ "$program" = "ffmpeg" ];then
						eval "$PACK_MGR ffmpeg $PKG_MGR_OPTIONS"				
						if command -v ffmpeg >/dev/null 2>&1; then
							echo "FFmpeg installed successfully!"
						else
							echo "FFmpeg installation failed."
						fi
					elif [ "$program" = "calibre" ];then				
						# avoid conflict with calibre builtin lxml
						pip uninstall lxml -y 2>/dev/null
						
						if [[ "$OSTYPE" = "darwin"* ]]; then
							echo "Installing Calibre for macOS using Homebrew..."
							eval "$PACK_MGR --cask calibre"
						else
							echo "Installing Calibre for Linux..."
							$WGET -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin
						fi

						if command -v calibre >/dev/null 2>&1; then
							echo "Calibre installed successfully!"
						else
							echo "Calibre installation failed."
						fi
					fi
				done
				
				if ! required_programs_check "${REQUIRED_PROGRAMS[@]}"; then
					echo -e "\e[33mYou can run 'ebook2audiobook.sh --script_mode docker_utils' to avoid to install $REQUIRED_PROGRAMS natively.\e[0m"
					exit 1
				fi
			else
				echo "Cannot install wget. Please install wget manually."
				exit 1
			fi
		fi
	fi
	conda_check
fi

if [ "$SCRIPT_MODE" = "$NATIVE" ]; then
	echo -e "\e[33mRunning in $NATIVE mode\e[0m"
	if [[ -n "$VIRTUAL_ENV" || -n "$CONDA_DEFAULT_ENV" ]]; then
		python app.py --script_mode "$NATIVE" $ARGS
	else
		if [[ ! -d $SCRIPT_DIR/$PYTHON_ENV ]]; then
			conda create --prefix $SCRIPT_DIR/$PYTHON_ENV python=$PYTHON_VERSION -y
		fi
		source "$CONFIG_FILE"
		conda activate $SCRIPT_DIR/$PYTHON_ENV
		python app.py --script_mode "$NATIVE" $ARGS
		conda deactivate
	fi
elif [ "$SCRIPT_MODE" = "$DOCKER_UTILS" ]; then
	echo -e "\e[33mRunning in $DOCKER_UTILS mode\e[0m"
	if [[ ! -d $SCRIPT_DIR/$PYTHON_ENV ]]; then
		conda create --prefix $SCRIPT_DIR/$PYTHON_ENV python=$PYTHON_VERSION -y
	fi
	source "$CONFIG_FILE"
	conda activate $SCRIPT_DIR/$PYTHON_ENV
	python app.py --script_mode "$DOCKER_UTILS" $ARGS
	conda deactivate
elif [ "$SCRIPT_MODE" = "$FULL_DOCKER" ]; then
	echo -e "\e[33mRunning in $FULL_DOCKER mode\e[0m"
	python app.py --script_mode "$FULL_DOCKER" $ARGS
else
	echo -e "\e[33mebook2audiobook is not correctly installed.\e[0m"
	exit 1
fi

exit 0
