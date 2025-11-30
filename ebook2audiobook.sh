#!/usr/bin/env bash

if [[ "$OSTYPE" == darwin* && -z "$SWITCHED_TO_ZSH" && "$(ps -p $$ -o comm=)" != "zsh" ]]; then
	export SWITCHED_TO_ZSH=1
	exec env zsh "$0" "$@"
fi

if [[ -n "$BASH_SOURCE" ]]; then
	script_path="${BASH_SOURCE[0]}"
elif [[ -n "$ZSH_VERSION" ]]; then
	script_path="${(%):-%x}"
else
	script_path="$0"
fi

export SCRIPT_DIR="$(cd "$(dirname "$script_path")" >/dev/null 2>&1 && pwd -P)"
export PYTHONUTF8="1"
export PYTHONIOENCODING="utf-8"
export TTS_CACHE="$SCRIPT_DIR/models"
export TESSDATA_PREFIX="$SCRIPT_DIR/models/tessdata"
export TMPDIR="$SCRIPT_DIR/tmp"
export CONDA_HOME="$HOME/Miniforge3"
export CONDA_BIN_PATH="$CONDA_HOME/bin"
export CONDA_ENV="$CONDA_HOME/etc/profile.d/conda.sh"
export PATH="$CONDA_BIN_PATH:$PATH"

cd "$SCRIPT_DIR"

NATIVE="native"
FULL_DOCKER="full_docker"
ARCH=$(uname -m)
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "3.12")
MIN_PYTHON_VERSION="3.10"
MAX_PYTHON_VERSION="3.12"
PYTHON_ENV="python_env"
SCRIPT_MODE="$NATIVE"
APP_NAME="ebook2audiobook"
APP_VERSION=$(<"$SCRIPT_DIR/VERSION.txt")
REQUIRED_PROGRAMS=("curl" "pkg-config" "calibre" "ffmpeg" "nodejs" "espeak-ng" "rust" "sox" "tesseract")
CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
BREW_INSTALLER_URL="https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
MINIFORGE_MACOSX_INSTALLER_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-$(uname -m).sh"
MINIFORGE_LINUX_INSTALLER_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
RUST_INSTALLER_URL="https://sh.rustup.rs"
INSTALLED_LOG="$SCRIPT_DIR/.installed"
UNINSTALLER="$SCRIPT_DIR/uninstall.sh"
INSTALL_PKG=""
WGET=$(which wget 2>/dev/null)
DOCKER_IMG_NAME="ebook2audiobook:latest"

declare -A arguments # associative array
declare -a programs_missing # indexed array

# Parse arguments
ARGS=("$@")
for ((i=0; i<${#ARGS[@]}; i++)); do
	arg="${ARGS[i]}"
	case "$arg" in
		--*)
			key="${arg/--/}"
			next="${ARGS[i+1]}"
			if [[ -n "$next" && ! "$next" =~ ^-- ]]; then
				arguments[$key]="$next"
				((i++))
			else
				arguments[$key]=true
			fi
			;;
		*)
			echo "Unknown option: $arg"
			exit 1
			;;
	esac
done

if [[ -n "${arguments['script_mode']+exists}" && "${arguments['script_mode']}" =~ ^(${NATIVE}|${FULL_DOCKER})$ ]]; then
	SCRIPT_MODE="${arguments['script_mode']}"
fi

if [[ -n "${arguments['install_pkg']+exists}" ]]; then
	INSTALL_PKG="${arguments['install_pkg']}"
fi

[[ "$OSTYPE" != darwin* && "$SCRIPT_MODE" != "$FULL_DOCKER" ]] && SUDO="sudo" || SUDO=""
[[ $OSTYPE == darwin* ]] && SHELL_NAME="zsh" || SHELL_NAME="bash"

############### FUNCTIONS ##############

###### DESKTOP APP
function has_no_display {
	if [[ "$OSTYPE" == darwin* ]]; then
		if pgrep -x WindowServer >/dev/null 2>&1 &&
		   [[ "$(launchctl managername 2>/dev/null)" == "Aqua" ]]; then
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

		if pgrep -x vncserver	>/dev/null 2>&1 || \
		   pgrep -x Xvnc		 >/dev/null 2>&1 || \
		   pgrep -x x11vnc	   >/dev/null 2>&1 || \
		   pgrep -x Xtightvnc	>/dev/null 2>&1 || \
		   pgrep -x Xtigervnc	>/dev/null 2>&1 || \
		   pgrep -x Xrealvnc	 >/dev/null 2>&1; then
			return 0
		fi

		if pgrep -x gnome-shell	   >/dev/null 2>&1 || \
		   pgrep -x plasmashell	   >/dev/null 2>&1 || \
		   pgrep -x xfce4-session	 >/dev/null 2>&1 || \
		   pgrep -x cinnamon		  >/dev/null 2>&1 || \
		   pgrep -x mate-session	  >/dev/null 2>&1 || \
		   pgrep -x lxsession		 >/dev/null 2>&1 || \
		   pgrep -x openbox		   >/dev/null 2>&1 || \
		   pgrep -x i3				>/dev/null 2>&1 || \
		   pgrep -x sway			  >/dev/null 2>&1 || \
		   pgrep -x hyprland		  >/dev/null 2>&1 || \
		   pgrep -x wayfire		   >/dev/null 2>&1 || \
		   pgrep -x river			 >/dev/null 2>&1 || \
		   pgrep -x fluxbox		   >/dev/null 2>&1; then
			return 0   # Desktop environment detected
		fi
		return 1
	fi
}

function open_desktop_app {
	(
		host=127.0.0.1
		port=7860
		url="http://$host:$port/"
		timeout=30
		start_time=$(date +%s)

		while ! nc -z "$host" "$port" >/dev/null 2>&1; do
			sleep 1
			elapsed=$(( $(date +%s) - start_time ))
			if [[ "$elapsed" -ge "$timeout" ]]; then
				exit 0
			fi
		done

		if [[ "$OSTYPE" == darwin* ]]; then
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
	local DESKTOP_DIR="$(osascript -e 'POSIX path of (path to desktop folder)' 2>/dev/null | sed 's:/$::')"
	local DESKTOP_SHORTCUT="$DESKTOP_DIR/$APP_NAME"
	local ICON_PATH="$SCRIPT_DIR/tools/icons/mac/appIcon.icns"
	local OPEN_DESKTOP_APP_DEF=$(declare -f open_desktop_app)
	local ESCAPED_APP_ROOT=$(printf '%q' "$SCRIPT_DIR") # Escape SCRIPT_DIR safely for AppleScript
	if [[ -d "$APP_BUNDLE" ]]; then
		open_desktop_app
		return 0
	fi
	[[ -d "$HOME/Applications" ]] || mkdir "$HOME/Applications"
	if [[ ! -d "$MACOS" || ! -d "$RESOURCES" ]]; then
		mkdir -p "$MACOS" "$RESOURCES"
	fi
	cat > "$MACOS/$APP_NAME" << EOF
#!/bin/zsh

$OPEN_DESKTOP_APP_DEF

open_desktop_app

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
	ln -sf "$APP_BUNDLE" "$DESKTOP_SHORTCUT"
	echo -e "Next launch in GUI mode you just need to double click on the desktop shortcut or go to the launchpad and click on ebook2audiobook icon."
	open_desktop_app
}

function linux_app() {
	local MENU_ENTRY="$HOME/.local/share/applications/$APP_NAME.desktop"
	local DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
	local DESKTOP_SHORTCUT="$DESKTOP_DIR/$APP_NAME.desktop"
	local ICON_PATH="$SCRIPT_DIR/tools/icons/linux/appIcon"
	if [[ -f "$MENU_ENTRY" ]]; then
		open_desktop_app
		return 0
	fi
	mkdir -p "$HOME/.local/share/applications"
	cat > "$MENU_ENTRY" <<EOF
[Desktop Entry]
Type=Application
Name=ebook2audiobook
Exec=$SCRIPT_DIR/ebook2audiobook.sh
Icon=$ICON_PATH
Terminal=true
Categories=Utility;
EOF
	chmod +x "$MENU_ENTRY"
	mkdir -p "$HOME/Desktop" 2>&1 > /dev/null
	cp "$MENU_ENTRY" "$DESKTOP_SHORTCUT"
	chmod +x "$DESKTOP_SHORTCUT"
	if command -v update-desktop-database >/dev/null 2>&1; then
		update-desktop-database ~/.local/share/applications >/dev/null 2>&1
	fi
	echo -e "Next launch in GUI mode you just need to double click on the desktop shortcut or go to menu entry and click on ebook2audiobook icon."
	open_desktop_app
}

function check_desktop_app {
	if [[ " ${ARGS[*]} " == *" --headless "* || has_no_display -eq 1 ]]; then
		return 0
	fi
	if [[ "$OSTYPE" == darwin* ]]; then
		mac_app
	elif [[ "$OSTYPE" == "linux"* ]]; then
		linux_app
	fi
	return 0
}
#################

function check_required_programs {
	local programs=("$@")
	programs_missing=()
	for program in "${programs[@]}"; do
		bin="$program"
		if [[ "$program" == "nodejs" ]]; then
			bin="node"
		fi
		if [[ "$program" == "rust" ]]; then
			if command -v apt-get &>/dev/null; then
				program="rustc"
			fi
			bin="rustc"
		fi
		if [[ "$program" == "tesseract" ]]; then
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
	if [[ "$OSTYPE" == darwin* ]]; then
		echo -e "\e[33mInstalling required programs...\e[0m"
		PACK_MGR="brew install"
			if ! command -v brew &> /dev/null; then
				echo -e "\e[33mHomebrew is not installed. Installing Homebrew...\e[0m"
				/usr/bin/env bash -c "$(curl -fsSL $BREW_INSTALLER_URL)"
				echo >> $HOME/.zprofile
				echo 'eval "$(/usr/local/bin/brew shellenv)"' >> $HOME/.zprofile
				eval "$(/usr/local/bin/brew shellenv)"
				if ! grep -iqFx "homebrew" "$INSTALLED_LOG"; then
					echo "homebrew" >> "$INSTALLED_LOG"
				fi
			fi
	else
		if [[ "$SUDO" == "sudo" ]]; then
			echo -e "\e[33mInstalling required programs. NOTE: you must have 'sudo' priviliges to install ebook2audiobook.\e[0m"
		fi
		local PACK_MGR_OPTIONS=""
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
	if [[ -z "$WGET" ]]; then
		echo -e "\e[33m wget is missing! trying to install it... \e[0m"
		result=$(eval "$PACK_MGR wget $PACK_MGR_OPTIONS" 2>&1)
		result_code=$?
		if [[ $result_code -eq 0 ]]; then
			WGET=$(which wget 2>/dev/null)
		else
			echo "Cannot 'wget'. Please install 'wget'  manually."
			return 1
		fi
	fi
	for program in "${programs_missing[@]}"; do
		if [[ "$program" == "calibre" ]]; then				
			# avoid conflict with calibre builtin lxml
			pip uninstall lxml -y 2>/dev/null
			echo -e "\e[33mInstalling Calibre...\e[0m"
			if [[ "$OSTYPE" == darwin* ]]; then
				eval "$PACK_MGR --cask calibre"
			else
				if [[ "$SUDO" == "sudo" ]]; then
					$SUDO -v && $WGET -nv -O- $CALIBRE_INSTALLER_URL | $SUDO sh /dev/stdin
				else
					$WGET -nv -O- $CALIBRE_INSTALLER_URL | sh /dev/stdin
				fi
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
		elif [[ "$program" == "rust" || "$program" == "rustc" ]]; then
			curl --proto '=https' --tlsv1.2 -sSf $RUST_INSTALLER_URL | sh -s -- -y
			source $HOME/.cargo/env
			if command -v $program &>/dev/null; then
				echo -e "\e[32m===============>>> $program is installed! <<===============\e[0m"
			else
				echo "$program installation failed."
			fi
		elif [[ "$program" == "tesseract" || "$program" == "tesseract-ocr" ]]; then
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
				if [[ -n "$langpack" ]]; then
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
	if check_required_programs "${REQUIRED_PROGRAMS[@]}"; then
		return 0
	else
		echo "Some programs didn't install successfuly, please report the log to the support"
	fi
}

function check_conda {

	function compare_versions {
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

	if ! command -v conda &> /dev/null || [[ ! -f "$CONDA_ENV" ]]; then

		local installer_url
		local installer_path="/tmp/Miniforge3.sh"
		local config_path

		echo -e "\e[33mDownloading Miniforge3 installer...\e[0m"

		if [[ "$OSTYPE" == darwin* ]]; then
			config_path="$HOME/.zshrc"
			curl -fsSLo "$installer_path" "$MINIFORGE_MACOSX_INSTALLER_URL"
		else
			config_path="$HOME/.bashrc"
			wget -O "$installer_path" "$MINIFORGE_LINUX_INSTALLER_URL"
		fi

		if [[ -f "$installer_path" ]]; then
			echo -e "\e[33mInstalling Miniforge3...\e[0m"
			bash "$installer_path" -b -u -p "$CONDA_HOME"
			rm -f "$installer_path"
			if [[ -f "$CONDA_HOME/bin/conda" ]]; then
				if [[ ! -f "$HOME/.condarc" ]]; then
					$CONDA_HOME/bin/conda config --set auto_activate false
				fi
				[[ -f "$config_path" ]] || touch "$config_path"
				grep -qxF 'export PATH="$HOME/Miniforge3/bin:$PATH"' "$config_path" || echo 'export PATH="$HOME/Miniforge3/bin:$PATH"' >> "$config_path"
				source "$config_path"
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
		if [[ "$OSTYPE" == darwin* && "$ARCH" == "x86_64" ]]; then
			PYTHON_VERSION="3.11"
		elif [[ -r /proc/device-tree/model ]]; then
			# Detect Jetson and select correct Python version
			MODEL=$(tr -d '\0' </proc/device-tree/model | tr 'A-Z' 'a-z')
			if [[ "$MODEL" == *jetson* ]]; then
				PYTHON_VERSION="3.10"
			fi
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
		echo -e "\e[33mCreating ./python_env version $PYTHON_VERSION...\e[0m"
		chmod -R u+rwX,go+rX "$SCRIPT_DIR/audiobooks" "$SCRIPT_DIR/tmp" "$SCRIPT_DIR/models"
		conda create --prefix "$SCRIPT_DIR/$PYTHON_ENV" python=$PYTHON_VERSION -y || return 1
		source "$CONDA_ENV" || return 1
		conda activate "$SCRIPT_DIR/$PYTHON_ENV" || return 1
		install_python_packages || return 1
		conda deactivate > /dev/null 2>&1
		conda deactivate > /dev/null 2>&1
	fi
	return 0
}

function install_python_packages {
	echo "[ebook2audiobook] Installing dependencies..."
	python3 -m pip cache purge > /dev/null 2>&1
	python3 -m pip install --upgrade pip > /dev/null 2>&1
	python3 -m pip install --upgrade --no-cache-dir --use-pep517 --progress-bar=on -r "$SCRIPT_DIR/requirements.txt" || exit 1
	torch_ver=$(pip show torch 2>/dev/null | awk '/^Version:/{print $2}')
	if [[ "$(printf '%s\n%s\n' "$torch_ver" "2.2.2" | sort -V | head -n1)" == "$torch_ver" ]]; then
		python3 -m pip install --upgrade --no-cache-dir --use-pep517 "numpy<2" || exit 1
	fi
	python3 -m unidic download || exit 1
	echo "[ebook2audiobook] Installation completed."
	return 0
}

check_device_info() {
python3 - << 'EOF'
import sys
from lib.device_installer import DeviceInstaller
device = DeviceInstaller()
result = device.check_device_info()
if result:
    print(result)
    sys.exit(0)
else:
    sys.exit(1)
EOF
}

install_device_packages() {
python3 - << EOF
import sys
from lib.device_installer import DeviceInstaller
device = DeviceInstaller()
exit_code = device.install_device_packages("""${INSTALL_PKG}""")  # returns 0 or 1
sys.exit(exit_code)
EOF
}

function check_sitecustomized {
	local src_pyfile="$SCRIPT_DIR/components/sitecustomize.py"
	local site_packages_path=$(python3 -c "import sysconfig;print(sysconfig.get_paths()['purelib'])")
	local dst_pyfile="$site_packages_path/sitecustomize.py"
	if [ ! -f "$dst_pyfile" ] || [ "$src_pyfile" -nt "$dst_pyfile" ]; then
		if cp -p "$src_pyfile" "$dst_pyfile"; then
			echo "Installed sitecustomize.py hook in $dst_pyfile"
		else
			echo "sitecustomize.py hook installation error: copy failed" >&2
			exit 1
		fi
	fi
	return 0
}

function build_docker_image {
	local DEVICE_INFO_STR="$1"
	local OS="manylinux_2_28"
	local NAME="$(echo "$DEVICE_INFO_STR" | jq -r '.name')"
	local TAG="$(echo "$DEVICE_INFO_STR" | jq -r '.tag')"
	local ARCH="$(echo "$DEVICE_INFO_STR" | jq -r '.arch')"

	if ! command -v docker >/dev/null 2>&1; then
		echo "Error: Docker is not installed."
		return 1
	fi

	if docker compose version >/dev/null 2>&1; then
		docker compose build \
			--no-cache \
			--progress plain \
			--build-arg DEVICE_INFO_STR="$DEVICE_INFO_STR" \
			|| return 1
	else
		docker build \
			--no-cache \
			--progress plain \
			--build-arg DEVICE_INFO_STR="$DEVICE_INFO_STR" \
			-t "$DOCKER_IMG_NAME" \
			. || return 1
	fi
}


########################################

if [[ ! -f "$INSTALLED_LOG" ]]; then
	touch "$INSTALLED_LOG"
fi

if [[ -n "${arguments['help']+exists}" && ${arguments['help']} == true ]]; then
	python "$SCRIPT_DIR/app.py" "${ARGS[@]}"
else
	if [[ "$SCRIPT_MODE" == "$FULL_DOCKER" ]]; then
		if [[ "$INSTALL_PKG" == "" ]]; then
			if docker image inspect "$DOCKER_IMG_NAME" >/dev/null 2>&1; then
				echo "[STOP] Docker image '$DOCKER_IMG_NAME' already exists. Aborting build."
				echo "Delete it using: docker rmi $DOCKER_IMG_NAME"
				exit 1
			fi
			build_docker_image "$(check_device_info)" || exit 1
		elif [[ "$INSTALL_PKG" != "" ]];then
			check_required_programs "${REQUIRED_PROGRAMS[@]}" || install_programs || exit 1
			install_python_packages || exit 1
			install_device_packages || exit 1
			check_sitecustomized || exit 1
		fi
	elif [[ "$SCRIPT_MODE" == "$NATIVE" ]]; then
		# Check if running in a Conda or Python virtual environment
		if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
			current_pyvenv="$CONDA_PREFIX"
		elif [[ -n "$VIRTUAL_ENV" ]]; then
			current_pyvenv="$VIRTUAL_ENV"
		fi
		# If neither environment variable is set, check Python path
		if [[ -z "$current_pyvenv" ]]; then
			PYTHON_PATH=$(which python 2>/dev/null)
			if [[ ( -n "$CONDA_PREFIX" && "$PYTHON_PATH" == "$CONDA_PREFIX/bin/python" ) || ( -n "$VIRTUAL_ENV" && "$PYTHON_PATH" == "$VIRTUAL_ENV/bin/python" ) ]]; then
				current_pyvenv="${CONDA_PREFIX:-$VIRTUAL_ENV}"
			fi
		fi
		# Output result if a virtual environment is detected
		if [[ -n "$current_pyvenv" ]]; then
			echo -e "Current python virtual environment detected: $current_pyvenv."
			echo -e "This script runs with its own virtual env and must be out of any other virtual environment when it's launched."
			echo -e "If you are using conda then you would type in:"
			echo -e "conda deactivate"
			exit 1
		fi
		check_required_programs "${REQUIRED_PROGRAMS[@]}" || install_programs || exit 1
		check_conda || { echo "check_conda failed"; exit 1; }
		source "$CONDA_ENV" || exit 1
		conda activate "$SCRIPT_DIR/$PYTHON_ENV" || { echo "conda activate failed"; exit 1; }
		check_sitecustomized || exit 1
		check_desktop_app || exit 1
		python "$SCRIPT_DIR/app.py" --script_mode "$SCRIPT_MODE" "${ARGS[@]}" || exit 1
		conda deactivate > /dev/null 2>&1
		conda deactivate > /dev/null 2>&1
	else
		echo -e "\e[33mebook2audiobook is not correctly installed or run.\e[0m"
	fi
fi

exit 0