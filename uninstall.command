#!/usr/bin/env bash

set -euo pipefail

: "${HOME:=$PWD}"

# Zsh safety: allow empty globs (re-run safe)
setopt NULL_GLOB 2>/dev/null || true

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

# heavy directories deleted atomically (no traversal)
SKIP_DIRS=("python_env" "Miniforge3")

# macOS shortcuts (KNOWN, FIXED PATHS)
APP_BUNDLE="$HOME/Applications/$APP_NAME.app"
DESKTOP_ALIAS="$HOME/Desktop/ebook2audiobook"

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
	IFS=':' read -r -a parts <<< "${PATH:-}"
	PATH=""
	for p in "${parts[@]}"; do
		[[ "$p" == "$target" ]] && continue
		PATH="${PATH:+$PATH:}$p"
	done
	export PATH
}

# =========================================================
# macOS SHORTCUT CLEANUP (NO TESTS, GUARDED)
# =========================================================
if [[ "${OSTYPE:-}" == darwin* ]]; then
	echo "Cleaning macOS shortcuts"

	if [[ -n "$APP_BUNDLE" && "$APP_BUNDLE" != "/" ]]; then
		rm -rf "$APP_BUNDLE" 2>/dev/null || true
	fi

	if [[ -n "$DESKTOP_ALIAS" && "$DESKTOP_ALIAS" != "/" ]]; then
		rm -f "$DESKTOP_ALIAS" 2>/dev/null || true
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
# MINIFORGE REMOVAL (FAST, GUARDED)
# =========================================================
if [[ "$REMOVE_CONDA" -eq 1 && -n "$CONDA_HOME" && "$CONDA_HOME" != "/" ]]; then
	echo "$CONDA_HOME"
	rm -rf "$CONDA_HOME" 2>/dev/null || true
	remove_from_path "$CONDA_BIN_PATH"
fi

# =========================================================
# FAST DELETE HEAVY REPO DIRS (NO LISTING)
# =========================================================
for d in "${SKIP_DIRS[@]}"; do
	path="$SCRIPT_DIR/$d"
	if [[ -n "$path" && "$path" != "/" ]]; then
		rm -rf "$path" 2>/dev/null || true
	fi
done

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

	if [[ -n "$item" && "$item" != "/" ]]; then
		rm -rf "$item" 2>/dev/null || true
	fi
done

# remove .installed if still present
if [[ -n "$INSTALLED_LOG" && "$INSTALLED_LOG" != "/" ]]; then
	rm -f "$INSTALLED_LOG" 2>/dev/null || true
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
