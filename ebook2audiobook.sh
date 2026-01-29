#!/usr/bin/env bash

# =========================================================
# ZSH RELAUNCH (macOS SAFETY)
# =========================================================
if [[ "$OSTYPE" == "darwin"* && -z "$SWITCHED_TO_ZSH" && "$(ps -p $$ -o comm=)" != "zsh" ]]; then
	export SWITCHED_TO_ZSH=1
	exec env zsh "$0" "$@"
fi

# =========================================================
# SCRIPT PATH RESOLUTION (BASH + ZSH)
# =========================================================
if [[ -n "$BASH_SOURCE" ]]; then
	script_path="${BASH_SOURCE[0]}"
elif [[ -n "$ZSH_VERSION" ]]; then
	script_path="${(%):-%x}"
else
	script_path="$0"
fi

SCRIPT_DIR="$(cd "$(dirname "$script_path")" >/dev/null 2>&1 && pwd -P)"
SCRIPT_REALPATH="$(cd "$SCRIPT_DIR" && pwd -P)"

APP_NAME="ebook2audiobook"
INSTALLED_LOG="$SCRIPT_DIR/.installed"
TEMP_UNINSTALLER="/tmp/${APP_NAME}_uninstaller.sh"

# =========================================================
# DUAL MINIFORGE DETECTION
# =========================================================
USER_CONDA="$HOME/Miniforge3"
LOCAL_CONDA="$SCRIPT_DIR/Miniforge3"

if [[ -x "$USER_CONDA/bin/conda" ]]; then
	CONDA_HOME="$USER_CONDA"
else
	CONDA_HOME="$LOCAL_CONDA"
fi

CONDA_BIN_PATH="$CONDA_HOME/bin"
CONDA_ENV="$CONDA_HOME/etc/profile.d/conda.sh"

# =========================================================
# SAFE PATH CLEANUP FUNCTION
# =========================================================
remove_from_path() {
	local target="$1"
	IFS=':' read -r -a parts <<< "${PATH:-}"
	PATH=""
	for p in "${parts[@]}"; do
		[[ "$p" == "$target" ]] && continue
		PATH="${PATH:+$PATH:}$p"
	done
	export PATH
}

# =========================================================
# SELF-RELAUNCH FROM /tmp (FIXED)
# =========================================================
if [[ "$SCRIPT_REALPATH" != "/tmp" ]]; then
	echo "[INFO] Relaunching uninstaller from /tmp..."
	cp "$script_path" "$TEMP_UNINSTALLER"
	chmod +x "$TEMP_UNINSTALLER"
	exec "$TEMP_UNINSTALLER"
fi

echo
echo "========================================"
echo "  Uninstalling $APP_NAME"
echo "========================================"
echo

# =========================================================
# DESKTOP / MENU CLEANUP
# =========================================================
if [[ "$OSTYPE" == "darwin"* ]]; then
	APP_BUNDLE="$HOME/Applications/$APP_NAME.app"
	DESKTOP_DIR="$(osascript -e 'POSIX path of (path to desktop folder)' 2>/dev/null | sed 's:/$::')"
	rm -rf "$APP_BUNDLE" 2>/dev/null || true
	rm -f "$DESKTOP_DIR/$APP_NAME" 2>/dev/null || true
elif [[ "$OSTYPE" == "linux"* ]]; then
	MENU_ENTRY="$HOME/.local/share/applications/$APP_NAME.desktop"
	DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
	rm -f "$MENU_ENTRY" "$DESKTOP_DIR/$APP_NAME.desktop" 2>/dev/null || true
	update-desktop-database ~/.local/share/applications >/dev/null 2>&1 || true
fi

# =========================================================
# MINIFORGE REMOVAL (CONTROLLED BY .installed)
# =========================================================
if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "Miniforge3" "$INSTALLED_LOG"; then
	if [[ -d "$CONDA_HOME" ]]; then
		echo "[INFO] Removing Miniforge3 from: $CONDA_HOME"
		rm -rf "$CONDA_HOME"
	fi

	remove_from_path "$CONDA_BIN_PATH"
fi

# =========================================================
# REMOVE APPLICATION FILES
# =========================================================
if [[ -d "$SCRIPT_DIR" ]]; then
	echo "[INFO] Removing application directory: $SCRIPT_DIR"
	rm -rf "$SCRIPT_DIR"
fi

# =========================================================
# FINAL CLEANUP
# =========================================================
rm -f "$TEMP_UNINSTALLER" 2>/dev/null || true

echo
echo "========================================"
echo "  Uninstall complete."
echo "========================================"
echo

exit 0