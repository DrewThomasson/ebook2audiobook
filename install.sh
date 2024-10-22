#!/usr/bin/env bash

WGET=$(which wget 2>/dev/null)
CONDA_VERSION=$(conda --version 2>/dev/null)
DOCKER=$(which docker 2>/dev/null)

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
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing wget using Homebrew..."
        brew install wget
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y wget
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y wget
    elif command -v yum &> /dev/null; then
        sudo yum install -y wget
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y wget
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy wget
    elif command -v apk &> /dev/null; then
        sudo apk add wget
    elif command -v emerge &> /dev/null; then
        sudo emerge wget
    else
        echo "Cannot recognize your package manager. Please install wget manually."
        exit 1
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

if [[ -n "$WGET" && -z "$DOCKER" ]]; then
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
		DOCKER=$(which docker 2>/dev/null)
		rm -f get-docker.sh
	fi
	echo -e "\e[32m===============>>> docker is installed! <<===============\e[0m"
fi

if [[ -n "$WGET" && -n "$CONDA_VERSION" && -n "$DOCKER" ]]; then
	SHELL_RC=~/miniconda3/etc/profile.d/conda.sh
	echo -e "\e[33m Installing ebook2audiobookXTTS... \e[0m"
	conda create --prefix $(pwd)/python_env python=3.11 -y && \
	source $SHELL_RC
	conda activate $(pwd)/python_env && \
	$DOCKER build -f DockerfileUtils -t utils . && \
	pip install --upgrade pip && \
	pip install pydub nltk beautifulsoup4 ebooklib translate coqui-tts tqdm mecab mecab-python3 unidic gradio docker && \
	python -m unidic download && \
	python -m spacy download en_core_web_sm && \
	pip install -e . && \
	conda deactivate

	echo -e "\e[32m******************* ebook2audiobookXTTS installation successful! *******************\e[0m"
	echo -e "\e[33mTo launch ebook2audiobookXTTS:\e[0m"
	echo -e "- in command line mode: ./ebook2audiobookXTTS.cmd --headless [other options]"
	echo -e "- in graphic web mode: ./ebook2audiobookXTTS.cmd"
fi

exit 0
