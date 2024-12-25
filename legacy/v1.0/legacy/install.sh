#!/usr/bin/env bash

WGET=$(which wget 2>/dev/null)
CONDA_VERSION=$(conda --version 2>/dev/null)
DOCKER_UTILS=$(which docker 2>/dev/null)
DOCKER_UTILS_NEEDED=false
PACK_MGR=""
PACK_MGR_OPTIONS=""

if [[ "$OSTYPE" == "darwin"* ]]; then
	PACK_MGR="brew install"
elif command -v emerge &> /dev/null; then
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

check_programs_installed() {
	local programs=("$@")
	declare -a programs_missing
	
	for program in "${programs[@]}"; do
		if command -v "$program" >/dev/null 2>&1; then
			echo "$program is installed."
		else
			echo "$program is not installed."
			programs_missing+=($program)
		fi
	done
	
	local count=${#programs_missing[@]}
	
	if [[ $count -eq 0 || "$PKG_MGR" = "" ]]; then
		DOCKER_UTILS_NEEDED=true
	else
		for program in "${programs_missing[@]}"; do
			if [ "$program" = "ffmpeg" ];then
				eval "$PKG_MGR ffmpeg $PKG_MGR_OPTIONS"				
				if command -v ffmpeg >/dev/null 2>&1; then
					echo "FFmpeg installed successfully!"
				else
					echo "FFmpeg installation failed."
					DOCKER_UTILS_NEEDED=true
					break
				fi
			elif [ "$program" = "calibre" ];then				
				# avoid conflict with calibre builtin lxml
				pip uninstall lxml -y 2>/dev/null
				
				if [[ "$OSTYPE" == "Linux" ]]; then
					echo "Installing Calibre for Linux..."
					$WGET -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin
				elif [[ "$OSTYPE" == "Darwin"* ]]; then
					echo "Installing Calibre for macOS using Homebrew..."
					eval "$PACK_MGR --cask calibre"
				fi

				if command -v calibre >/dev/null 2>&1; then
					echo "Calibre installed successfully!"
				else
					echo "Calibre installation failed."
				fi
			fi
		done
	fi
}

# Check for Homebrew on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
	echo "Detected macOS."
	if ! command -v brew &> /dev/null; then
		echo "Homebrew is not installed. Installing Homebrew..."
		/usr/bin/env bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
		eval "$(/opt/homebrew/bin/brew shellenv)"
	fi
fi

if [ -z "$WGET" ]; then
	echo -e "\e[33m wget is missing! trying to install it... \e[0m"
	if [ "$PACK_MGR" != "" ]; then
		eval "$PACK_MGR wget $PACK_MGR_OPTIONS"
	else
		echo "Cannot recognize your package manager. Please install wget manually."
	fi
	WGET=$(which wget 2>/dev/null)
fi

if [[ -n "$WGET" && -z "$CONDA_VERSION" ]]; then
	echo -e "\e[33m conda is missing! trying to install it... \e[0m"
	
	if [[ "$OSTYPE" == "darwin"* ]]; then
		$WGET https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O Miniconda3-latest.sh
	else
		$WGET https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda3-latest.sh
	fi

	chmod +x Miniconda3-latest.sh
	./Miniconda3-latest.sh -b -u && \
	~/miniconda3/bin/conda init && \
	rm -f Miniconda3-latest.sh

	# Source the appropriate shell configuration file
	SHELL_RC=~/miniconda3/etc/profile.d/conda.sh
	source $SHELL_RC

	CONDA_VERSION=$(conda --version 2>/dev/null)
	echo -e "\e[32m===============>>> conda is installed! <<===============\e[0m"
fi

check_programs_installed()

if [ $DOCKER_UTILS_NEEDED = true ]; then
	if [[ -n "$WGET" && -z "$DOCKER_UTILS" ]]; then
		echo -e "\e[33m docker is missing! trying to install it... \e[0m"
		if [[ "$OSTYPE" == "darwin"* ]]; then
			echo "Installing Docker using Homebrew..."
			brew install --cask docker
		else
			$WGET -qO get-docker.sh https://get.docker.com && \
			sudo sh get-docker.sh && \
			sudo systemctl start docker && \
			sudo systemctl enable docker && \
			docker run hello-world && \
			DOCKER_UTILS=$(which docker 2>/dev/null)
			rm -f get-docker.sh
		fi
		echo -e "\e[32m===============>>> docker is installed! <<===============\e[0m"
	fi
fi

if [[ -n "$WGET" && -n "$CONDA_VERSION" ]]; then
	SHELL_RC=~/miniconda3/etc/profile.d/conda.sh
	echo -e "\e[33m Installing ebook2audiobook... \e[0m"
	if [ $DOCKER_UTILS_NEEDED = true ]; then
		conda create --prefix $(pwd)/python_env python=3.11 -y
		source $SHELL_RC
		conda activate $(pwd)/python_env
		$DOCKER_UTILS build -f DockerfileUtils -t utils .
	fi
	pip install --upgrade pip && \
	pip install pydub nltk beautifulsoup4 ebooklib translate coqui-tts tqdm mecab mecab-python3 unidic gradio>=4.44.0 docker && \
	python -m unidic download && \
	python -m spacy download en_core_web_sm && \
	pip install -e .
	if [ $DOCKER_UTILS_NEEDED = true ]; then
		conda deactivate
		conda deactivate
	fi
	echo -e "\e[32m******************* ebook2audiobook installation successful! *******************\e[0m"
	echo -e "\e[33mTo launch ebook2audiobook:\e[0m"
	echo -e "- in command line mode: ./ebook2audiobook.sh --headless [other options]"
	echo -e "- in graphic web mode: ./ebook2audiobook.sh [--share]"
fi

exit 0
