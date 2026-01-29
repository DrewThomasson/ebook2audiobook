#!/usr/bin/env bash

# =========================================================
# ZSH RELAUNCH (macOS)
# =========================================================
if [[ "$OSTYPE" == "darwin"* && -z "$SWITCHED_TO_ZSH" && "$(ps -p $$ -o comm=)" != "zsh" ]]; then
	export SWITCHED_TO_ZSH=1
	exec env zsh "$0" "$@"
fi

# =========================================================
# SCRIPT PATH RESOLUTION (BASH + ZSH)
# =========================================================
if [[ -n "$BASH_SOURCE" ]]; then
	script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/$(basename "${BASH_SOURCE[0]}")"
elif [[ -n "$ZSH_VERSION" ]]; then
	script_path="$(cd "$(dirname "${(%):-%x}")" && pwd -P)/$(basename "${(%):-%x}")"
else
	script_path="$(cd "$(dirname "$0")" && pwd -P)/$(basename "$0")"
fi

APP_NAME="ebook2audiobook"
SCRIPT_DIR="$(dirname "$script_path")"
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

# =========================================================
# SAFE PATH CLEANUP
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
# SELF-RELAUNCH FROM /tmp (FINAL FIX)
# =========================================================
if [[ "$script_path" != "$TEMP_UNINSTALLER" ]]; then
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
	rm -rf "$HOME/Applications/$APP_NAME.app" 2>/dev/null || true
elif [[ "$OSTYPE" == "linux"* ]]; then
	rm -f "$HOME/.local/share/applications/$APP_NAME.desktop" 2>/dev/null || true
	update-desktop-database ~/.local/share/applications >/dev/null 2>&1 || true
fi

# =========================================================
# MINIFORGE REMOVAL (CONTROLLED)
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
echo "[INFO] Removing application directory: $SCRIPT_DIR"
rm -rf "$SCRIPT_DIR"

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