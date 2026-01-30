#!/usr/bin/env bash

set -euo pipefail

: "${HOME:=$PWD}"

CURRENT_PYVENV=""
SWITCHED_TO_ZSH="${SWITCHED_TO_ZSH:-0}"

if [[ "${OSTYPE:-}" == darwin* && "$SWITCHED_TO_ZSH" -eq 0 && "$(ps -p $$ -o comm= 2>/dev/null || true)" != "zsh" ]]; then
	export SWITCHED_TO_ZSH=1
	exec env zsh "$0" "$@"
fi

# =========================================================
# HEADER
# =========================================================
echo
echo "========================================"
echo "  ebook2audiobook – Uninstaller"
echo "========================================"
echo

# =========================================================
# OPTIONAL INTERACTIVE PAUSE (SAFE)
# =========================================================
if [[ -t 0 ]]; then
	printf "Press Enter to continue or Ctrl+C to abort..."
	read -r _ || true
	echo
fi

# =========================================================
# SCRIPT PATH RESOLUTION (BASH + ZSH)
# =========================================================
if [[ -n "${BASH_SOURCE:-}" ]]; then
	script_path="${BASH_SOURCE[0]}"
elif [[ -n "${ZSH_VERSION:-}" ]]; then
	script_path="${(%):-%x}"
else
	script_path="$0"
fi

APP_NAME="ebook2audiobook"
SCRIPT_DIR="$(cd "$(dirname "$script_path")" >/dev/null 2>&1 && pwd -P)"
INSTALLED_LOG="$SCRIPT_DIR/.installed"
CONDA_HOME="$HOME/Miniforge3"
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

echo
echo "========================================"
echo "  Uninstalling $APP_NAME"
echo "========================================"
echo

# =========================================================
# DESKTOP / MENU CLEANUP
# =========================================================
if [[ "${OSTYPE:-}" == darwin* ]]; then
	rm -rf "$HOME/Applications/$APP_NAME.app" 2>/dev/null || true
elif [[ "${OSTYPE:-}" == linux* ]]; then
	rm -f "$HOME/.local/share/applications/$APP_NAME.desktop" 2>/dev/null || true
	update-desktop-database ~/.local/share/applications >/dev/null 2>&1 || true
fi

# =========================================================
# MINIFORGE REMOVAL (ONLY IF INSTALLED BY APP)
# =========================================================
if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "Miniforge3" "$INSTALLED_LOG"; then
	if [[ -d "$CONDA_HOME" ]]; then
		echo "[INFO] Removing Miniforge3 from: $CONDA_HOME"
		rm -rf "$CONDA_HOME"
	fi
	remove_from_path "$CONDA_BIN_PATH"
fi

# =========================================================
# DELETE APPLICATION CONTENTS (SHELL-AGNOSTIC)
# =========================================================
if [[ -d "$SCRIPT_DIR" ]]; then
	echo "[INFO] Removing application contents from:"
	echo "       $SCRIPT_DIR"
	rm -rf "$SCRIPT_DIR"
fi

# =========================================================
# FINAL USER MESSAGE
# =========================================================
echo
echo "================================================"
echo "  Uninstallation completed successfully."
echo "  All application files have been removed."
echo "  You may now close this terminal."
echo "================================================"
echo

exit 0