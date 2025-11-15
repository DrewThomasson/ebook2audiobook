#!/usr/bin/env bash

if [[ "$OSTYPE" = "darwin"* && -z "$SWITCHED_TO_ZSH" && "$(ps -p $$ -o comm=)" != "zsh" ]]; then
	export SWITCHED_TO_ZSH=1
	exec env zsh "$0" "$@"
fi

export SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd -P)"
export PYTHONUTF8="1"
export PYTHONIOENCODING="utf-8"

ARCH=$(uname -m)

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "3.12")

MIN_PYTHON_VERSION="3.10"
MAX_PYTHON_VERSION="3.13"

cd "$SCRIPT_DIR"

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
APP_NAME="ebook2audiobook"
APP_VERSION=$(<"$SCRIPT_DIR/VERSION.txt")
WGET=$(which wget 2>/dev/null)
REQUIRED_PROGRAMS=("curl" "pkg-config" "calibre" "ffmpeg" "nodejs" "espeak-ng" "rust" "sox" "tesseract")
PYTHON_ENV="python_env"
CURRENT_ENV=""
INSTALLED_LOG="$SCRIPT_DIR/.installed"
UNINSTALLER="$SCRIPT_DIR/uninstall.sh"

if [[ "$OSTYPE" != "linux"* && "$OSTYPE" != "darwin"* ]]; then
	echo "Error: OS $OSTYPE unsupported."
	exit 1;
fi

if [[ "$OSTYPE" = "darwin"* ]]; then
	CONDA_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-$(uname -m).sh"
	CONFIG_FILE="$HOME/.zshrc"
elif [[ "$OSTYPE" = "linux"* ]]; then
	CONDA_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
	CONFIG_FILE="$HOME/.bashrc"
fi

CONDA_INSTALLER="/tmp/Miniforge3.sh"
CONDA_INSTALL_DIR="$HOME/Miniforge3"
CONDA_PATH="$CONDA_INSTALL_DIR/bin"
CONDA_ENV="$CONDA_INSTALL_DIR/etc/profile.d/conda.sh"

export TTS_CACHE="$SCRIPT_DIR/models"
export TESSDATA_PREFIX="$SCRIPT_DIR/models/tessdata"
export TMPDIR="$SCRIPT_DIR/.cache"
export PATH="$CONDA_PATH:$PATH"

compare_versions() {
	local ver1=$1
	local ver2=$2
	# Pad each version to 3 parts
	IFS='.' read -r v1_major v1_minor <<<"$ver1"
	IFS='.' read -r v2_major v2_minor <<<"$ver2"

	((v1_major < v2_major)) && return 1
	((v1_major > v2_major)) && return 2
	((v1_minor < v2_minor)) && return 1
	((v1_minor > v2_minor)) && return 2
	return 0
}

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
	python "$SCRIPT_DIR/app.py" "${ARGS[@]}"
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
			bin="$program"
			if [ "$program" = "nodejs" ]; then
				bin="node"
			fi
			if [ "$program" = "rust" ]; then
				if command -v apt-get &>/dev/null; then
					program="rustc"
				fi
				bin="rustc"
			fi
			if [ "$program" = "tesseract" ]; then
				if command -v brew &> /dev/null; then
					program="tesseract"
				elif command -v emerge &> /dev/null; then
					program="tesseract"
				elif command -v dnf &> /dev/null; then
					program="tesseract"
				elif command -v yum &> /dev/null; then
					program="tesseract"
				elif command -v zypper &> /dev/null; then
					program="tesseract-ocr"
				elif command -v pacman &> /dev/null; then
					program="tesseract"
				elif command -v apt-get &> /dev/null; then
					program="tesseract-ocr"
				elif command -v apk &> /dev/null; then
					program="tesseract-ocr"
				else
					echo "Cannot recognize your applications package manager. Please install the required applications manually."
					return 1
				fi
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
					echo >> $HOME/.zprofile
					echo 'eval "$(/usr/local/bin/brew shellenv)"' >> $HOME/.zprofile
					eval "$(/usr/local/bin/brew shellenv)"
					if ! grep -iqFx "homebrew" "$INSTALLED_LOG"; then
						echo "homebrew" >> "$INSTALLED_LOG"
					fi
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
				PACK_MGR="pacman -Sy --noconfirm"
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
			if [ "$program" = "calibre" ]; then				
				# avoid conflict with calibre builtin lxml
				#pip uninstall lxml -y 2>/dev/null
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
			elif [[ "$program" = "rust" || "$program" = "rustc" ]]; then
				curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
				source $HOME/.cargo/env
				if command -v $program &>/dev/null; then
					echo -e "\e[32m===============>>> $program is installed! <<===============\e[0m"
				else
					echo "$program installation failed."
				fi
			elif [[ "$program" = "tesseract" || "$program" = "tesseract-ocr" ]]; then
				eval "$SUDO $PACK_MGR $program $PACK_MGR_OPTIONS"
				if command -v $program >/dev/null 2>&1; then
					echo -e "\e[32m===============>>> $program is installed! <<===============\e[0m"
					sys_lang=$(echo "${LANG:-en}" | cut -d_ -f1 | tr '[:upper:]' '[:lower:]')
					case "$sys_lang" in
						en) tess_lang="eng" ;;
						fr) tess_lang="fra" ;;
						de) tess_lang="deu" ;;
						it) tess_lang="ita" ;;
						es) tess_lang="spa" ;;
						pt) tess_lang="por" ;;
						ar) tess_lang="ara" ;;
						tr) tess_lang="tur" ;;
						ru) tess_lang="rus" ;;
						bn) tess_lang="ben" ;;
						zh) tess_lang="chi_sim" ;;
						fa) tess_lang="fas" ;;
						hi) tess_lang="hin" ;;
						hu) tess_lang="hun" ;;
						id) tess_lang="ind" ;;
						jv) tess_lang="jav" ;;
						ja) tess_lang="jpn" ;;
						ko) tess_lang="kor" ;;
						pl) tess_lang="pol" ;;
						ta) tess_lang="tam" ;;
						te) tess_lang="tel" ;;
						yo) tess_lang="yor" ;;
						*) tess_lang="eng" ;;
					esac
					echo "Detected system language: $sys_lang → installing Tesseract OCR language: $tess_lang"
					langpack=""
					if command -v brew &> /dev/null; then
						langpack="tesseract-lang-$tess_lang"
					elif command -v apt-get &>/dev/null; then
						langpack="tesseract-ocr-$tess_lang"
					elif command -v dnf &>/dev/null || command -v yum &>/dev/null; then
						langpack="tesseract-langpack-$tess_lang"
					elif command -v zypper &>/dev/null; then
						langpack="tesseract-ocr-$tess_lang"
					elif command -v pacman &>/dev/null; then
						langpack="tesseract-data-$tess_lang"
					elif command -v apk &>/dev/null; then
						langpack="tesseract-ocr-$tess_lang"
					else
						echo "Cannot recognize your applications package manager. Please install the required applications manually."
						return 1
					fi
					if [ -n "$langpack" ]; then
						eval "$SUDO $PACK_MGR $langpack $PACK_MGR_OPTIONS"
						if tesseract --list-langs | grep -q "$tess_lang"; then
							echo "Tesseract OCR language '$tess_lang' successfully installed."
						else
							echo "Tesseract OCR language '$tess_lang' not installed properly."
						fi
					fi
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
			if [[ "$OSTYPE" = darwin* ]]; then
				curl -fsSLo "$CONDA_INSTALLER" "$CONDA_URL"
				shell_name="zsh"
			else
				wget -O "$CONDA_INSTALLER" "$CONDA_URL"
				shell_name="bash"
			fi
			if [[ -f "$CONDA_INSTALLER" ]]; then
				echo -e "\e[33mInstalling Miniforge3...\e[0m"
				bash "$CONDA_INSTALLER" -b -u -p "$CONDA_INSTALL_DIR"
				rm -f "$CONDA_INSTALLER"
				if [[ -f "$CONDA_INSTALL_DIR/bin/conda" ]]; then
					if [ ! -f "$HOME/.condarc" ]; then
						$CONDA_INSTALL_DIR/bin/conda config --set auto_activate false
					fi
					[ -f "$CONFIG_FILE" ] || touch "$CONFIG_FILE"
					grep -qxF 'export PATH="$HOME/Miniforge3/bin:$PATH"' "$CONFIG_FILE" || echo 'export PATH="$HOME/Miniforge3/bin:$PATH"' >> "$CONFIG_FILE"
					source "$CONFIG_FILE"
					conda init "$shell_name"
					echo -e "\e[32m===============>>> conda is installed! <<===============\e[0m"
						if ! grep -iqFx "Miniforge3" "$INSTALLED_LOG"; then
							echo "Miniforge3" >> "$INSTALLED_LOG"
						fi
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
			if [[ "$OSTYPE" = "darwin"* && "$ARCH" = "x86_64" ]]; then
				PYTHON_VERSION="3.11"
			else
				compare_versions "$PYTHON_VERSION" "$MIN_PYTHON_VERSION"
				case $? in
					1) PYTHON_VERSION="$MIN_PYTHON_VERSION" ;;
				esac
				compare_versions "$PYTHON_VERSION" "$MAX_PYTHON_VERSION"
				case $? in
					2) PYTHON_VERSION="$MAX_PYTHON_VERSION" ;;
				esac
			fi
			# Use this condition to chmod writable folders once
			chmod -R u+rwX,go+rX "$SCRIPT_DIR/audiobooks" "$SCRIPT_DIR/tmp" "$SCRIPT_DIR/models"
			conda create --prefix "$SCRIPT_DIR/$PYTHON_ENV" python=$PYTHON_VERSION -y
			conda init > /dev/null 2>&1
			source $CONDA_ENV
			conda activate "$SCRIPT_DIR/$PYTHON_ENV"
			python -m pip cache purge > /dev/null 2>&1
			python -m pip install --upgrade pip
			python -m pip install --upgrade --no-cache-dir --use-pep517 --progress-bar=on -r requirements.txt
			tts_version=$(python -c "import importlib.metadata; print(importlib.metadata.version('coqui-tts'))" 2>/dev/null)
			if [[ -n "$tts_version" ]]; then
				if [[ "$(printf '%s\n' "$tts_version" "0.26.1" | sort -V | tail -n1)" = "0.26.1" ]]; then
					python -m pip install --no-cache-dir --use-pep517 --progress-bar=on 'transformers<=4.51.3'
				fi
			fi
			conda deactivate 2>&1 > /dev/null
		fi
		return 0
	}
	
	has_no_display() {
		if [[ "$OSTYPE" = "darwin"* ]]; then
			if pgrep -x WindowServer >/dev/null 2>&1 &&
			   [[ "$(launchctl managername 2>/dev/null)" = "Aqua" ]]; then
				return 0   # macOS GUI
			else
				return 1   # SSH or console mode
			fi
		else
			if [[ -n "$SSH_CONNECTION" || -n "$SSH_CLIENT" || -n "$SSH_TTY" ]]; then
				return 1
			fi

			if [[ -z "$DISPLAY" && -z "$WAYLAND_DISPLAY" ]]; then
				return 1   # No display server → headless
			fi

			if pgrep -x vncserver    >/dev/null 2>&1 || \
			   pgrep -x Xvnc         >/dev/null 2>&1 || \
			   pgrep -x x11vnc        >/dev/null 2>&1 || \
			   pgrep -x Xtightvnc    >/dev/null 2>&1 || \
			   pgrep -x Xtigervnc    >/dev/null 2>&1 || \
			   pgrep -x Xrealvnc     >/dev/null 2>&1; then
				return 0
			fi

			if pgrep -x gnome-shell       >/dev/null 2>&1 || \
			   pgrep -x plasmashell       >/dev/null 2>&1 || \
			   pgrep -x xfce4-session     >/dev/null 2>&1 || \
			   pgrep -x cinnamon          >/dev/null 2>&1 || \
			   pgrep -x mate-session      >/dev/null 2>&1 || \
			   pgrep -x lxsession         >/dev/null 2>&1 || \
			   pgrep -x openbox           >/dev/null 2>&1 || \
			   pgrep -x i3                >/dev/null 2>&1 || \
			   pgrep -x sway              >/dev/null 2>&1 || \
			   pgrep -x hyprland          >/dev/null 2>&1 || \
			   pgrep -x wayfire           >/dev/null 2>&1 || \
			   pgrep -x river              >/dev/null 2>&1 || \
			   pgrep -x fluxbox           >/dev/null 2>&1; then
				return 0   # Desktop environment detected
			fi
			return 1
		fi
	}
	
	function open_gui() {
		(
			host=127.0.0.1
			port=7860
			url="http://$host:$port/"
			timeout=30
			start_time=$(date +%s)

			while ! nc -z "$host" "$port" >/dev/null 2>&1; do
				sleep 1
				elapsed=$(( $(date +%s) - start_time ))
				if [ "$elapsed" -ge "$timeout" ]; then
					exit 0
				fi
			done

			if [[ "$OSTYPE" = "darwin"* ]]; then
				open "$url" >/dev/null 2>&1 &
			elif command -v xdg-open >/dev/null 2>&1; then
				xdg-open "$url" >/dev/null 2>&1 &
			elif command -v gio >/dev/null 2>&1; then
				gio open "$url" >/dev/null 2>&1 &
			elif command -v x-www-browser >/dev/null 2>&1; then
				x-www-browser "$url" >/dev/null 2>&1 &
			else
				echo "No method found to open the default web browser." >&2
			fi
			exit 0
		) &
	}

	function mac_app {
		local APP_BUNDLE="$HOME/Applications/$APP_NAME.app"
		local CONTENTS="$APP_BUNDLE/Contents"
		local MACOS="$CONTENTS/MacOS"
		local RESOURCES="$CONTENTS/Resources"
		local ICON_PATH="$SCRIPT_DIR/tools/icons/mac/appIcon.icns"
		local OPEN_GUI_DEF=$(declare -f open_gui)
		local ESCAPED_APP_ROOT=$(printf '%q' "$SCRIPT_DIR") # Escape SCRIPT_DIR safely for AppleScript
		if [[ -d "$APP_BUNDLE" ]]; then
			open_gui
			return 0
		fi
		[[ -d "$HOME/Applications" ]] || mkdir "$HOME/Applications"
		if [[ ! -d "$MACOS" || ! -d "$RESOURCES" ]]; then
			mkdir -p "$MACOS" "$RESOURCES"
		fi
		cat > "$MACOS/$APP_NAME" << EOF
#!/bin/zsh

$OPEN_GUI_DEF

open_gui

# TODO: replace osascript when log will be available in gradio with
#
# cd "$SCRIPT_DIR"
# ./ebook2audiobook.sh

osascript -e '
tell application "Terminal"
	do script "cd \"${ESCAPED_APP_ROOT}\" && ./ebook2audiobook.sh"
	activate
end tell
'
EOF
		chmod +x "$MACOS/$APP_NAME"
		cp "$ICON_PATH" "$RESOURCES/AppIcon.icns"
		cat > "$CONTENTS/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>en</string>
	<key>CFBundleExecutable</key>
	<string>ebook2audiobook</string>
	<key>CFBundleIdentifier</key>
	<string>com.local.ebook2audiobook</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>ebook2audiobook</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleVersion</key>
	<string>1</string>
	<key>LSMinimumSystemVersion</key>
	<string>10.9</string>
	<key>NSPrincipalClass</key>
	<string>NSApplication</string>
	<key>CFBundleIconFile</key>
	<string>AppIcon</string>
</dict>
</plist>
PLIST
		ln -sf "$APP_BUNDLE" "$HOME/Desktop/$APP_NAME"
		echo -e "\nLauncher created at: $APP_BUNDLE\nNext time in GUI mode you just need to double click on the desktop shortcut or open the launchpad and click on ebook2audiobook icon.\n"
		open_gui
	}

	function linux_app() {
		local DESKTOP_FILE="$HOME/.local/share/applications/ebook2audiobook.desktop"
		local ICON_PATH="$SCRIPT_DIR/tools/icons/linux/appIcon"
		if [[ -f "$DESKTOP_FILE" ]]; then
			open_gui
			return 0
		fi
		mkdir -p "$HOME/.local/share/applications"
		cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=ebook2audiobook
Exec=$SCRIPT_DIR/ebook2audiobook.sh
Icon=$ICON_PATH
Terminal=true
Categories=Utility;
EOF

		chmod +x "$DESKTOP_FILE"
		if command -v update-desktop-database >/dev/null 2>&1; then
			update-desktop-database ~/.local/share/applications >/dev/null 2>&1
		fi
		echo -e "\nLauncher created at: ~/.local/share/applications\nNext time in GUI mode you just need to click on the start menu and click on ebook2audiobook icon.\n"
		open_gui
	}

	function build_gui {
		if [[ " ${ARGS[*]} " = *" --headless "* || has_no_display -eq 1 ]]; then
			return 0
		fi
		if [[ "$OSTYPE" = "darwin"* ]]; then
			mac_app
		elif [[ "$OSTYPE" = "linux"* ]]; then
			linux_app
		fi
		return 0
	}

	if [ "$SCRIPT_MODE" = "$FULL_DOCKER" ]; then
		python "$SCRIPT_DIR/app.py" --script_mode "$SCRIPT_MODE" "${ARGS[@]}"
		conda deactivate 2>&1 > /dev/null
		conda deactivate 2>&1 > /dev/null
	elif [ "$SCRIPT_MODE" = "$NATIVE" ]; then
		pass=true	   
		if ! required_programs_check "${REQUIRED_PROGRAMS[@]}"; then
			if ! install_programs; then
				pass=false
			fi
		fi
		if [ "$pass" = true ]; then
			if conda_check; then
				conda init > /dev/null 2>&1
				source $CONDA_ENV
				conda activate "$SCRIPT_DIR/$PYTHON_ENV"
				build_gui
				python "$SCRIPT_DIR/app.py" --script_mode "$SCRIPT_MODE" "${ARGS[@]}"
				conda deactivate 2>&1 > /dev/null
				conda deactivate 2>&1 > /dev/null
			fi
		fi
	else
		echo -e "\e[33mebook2audiobook is not correctly installed or run.\e[0m"
	fi
fi

exit 0
exit 0
exit 0