#!/usr/bin/env bash

set -euo pipefail

: "${HOME:=$PWD}"

SWITCHED_TO_ZSH="${SWITCHED_TO_ZSH:-0}"

# =========================================================
# FORCE ZSH ON MACOS (Finder-friendly)
# =========================================================
if [[ "${OSTYPE:-}" == darwin* && "$SWITCHED_TO_ZSH" -eq 0 && "$(ps -p $$ -o comm= 2>/dev/null || true)" != "zsh" ]]; then
	export SWITCHED_TO_ZSH=1
	exec env zsh "$0" "$@"
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
SCRIPT_NAME="$(basename "$script_path")"
INSTALLED_LOG="$SCRIPT_DIR/.installed"

CONDA_HOME="$HOME/Miniforge3"
CONDA_BIN_PATH="$CONDA_HOME/bin"

# heavy directories (atomic delete, no traversal)
SKIP_DIRS=("python_env" "Miniforge3")

# =========================================================
# HEADER
# =========================================================
echo
echo "========================================"
echo "  $APP_NAME – Uninstaller"
echo "========================================"
echo "Install location:"
echo "  $SCRIPT_DIR"
echo

# =========================================================
# USER CONFIRMATION
# =========================================================
if [[ -t 0 ]]; then
	echo "This will uninstall $APP_NAME."
	echo "Components listed in .installed will be removed."
	echo
	printf "Press Enter to continue or Ctrl+C to abort..."
	read -r _ || true
	echo
fi

# =========================================================
# SAFE PATH CLEANUP
# =========================================================
remove_from_path() {
	local target="$1"
	echo "Removing from PATH: $target"
	IFS=':' read -r -a parts <<< "${PATH:-}"
	PATH=""
	for p in "${parts[@]}"; do
		[[ "$p" == "$target" ]] && continue
		PATH="${PATH:+$PATH:}$p"
	done
	export PATH
}

# =========================================================
# DESKTOP / MENU CLEANUP (macOS) – SIMPLE & CORRECT
# =========================================================
if [[ "${OSTYPE:-}" == darwin* ]]; then
	APP_BUNDLE="$HOME/Applications/$APP_NAME.app"
	DESKTOP_ALIAS="$HOME/Desktop/Ebook2Audiobook"

	echo "Cleaning macOS shortcuts"

	if [[ -d "$APP_BUNDLE" ]]; then
		echo "$APP_BUNDLE"
		rm -rf "$APP_BUNDLE"
	fi

	if [[ -e "$DESKTOP_ALIAS" ]]; then
		echo "$DESKTOP_ALIAS"
		rm -f "$DESKTOP_ALIAS"
	fi
fi

# =========================================================
# PROCESS .installed (CONTROLLED REMOVAL)
# =========================================================
REMOVE_CONDA=0
if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "Miniforge3" "$INSTALLED_LOG"; then
	REMOVE_CONDA=1
fi

# =========================================================
# MINIFORGE REMOVAL (FAST)
# =========================================================
if [[ "$REMOVE_CONDA" -eq 1 && -d "$CONDA_HOME" ]]; then
	echo "$CONDA_HOME"
	rm -rf "$CONDA_HOME"
	remove_from_path "$CONDA_BIN_PATH"
fi

# =========================================================
# CLEAN REPOSITORY CONTENT (FIRST LEVEL ONLY)
# =========================================================
echo
echo "Cleaning repository content..."

for item in "$SCRIPT_DIR"/* "$SCRIPT_DIR"/.*; do
	name="$(basename "$item")"
	[[ "$name" == "*" || "$name" == "." || "$name" == ".." ]] && continue
	[[ "$name" == "$SCRIPT_NAME" ]] && continue

	echo "$name"
	rm -rf "$item"
done

if [[ -f "$INSTALLED_LOG" ]]; then
	echo ".installed"
	rm -f "$INSTALLED_LOG"
fi

# =========================================================
# FINAL MESSAGE
# =========================================================
echo
echo "================================================"
echo "  Uninstallation completed."
echo
echo "  The application content has been removed."
echo "  Please remove the empty repository folder manually:"
echo
echo "    $SCRIPT_DIR"
echo
echo "================================================"
echo

if [[ -t 0 ]]; then
	printf "Press Enter to continue..."
	read -r _ || true
fi

exit 0