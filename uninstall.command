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

# heavy directories to skip from verbose traversal
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
# PROCESS .installed (CONTROLLED REMOVAL)
# =========================================================
REMOVE_CONDA=0
if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "Miniforge3" "$INSTALLED_LOG"; then
	REMOVE_CONDA=1
fi

# =========================================================
# MINIFORGE REMOVAL (FAST, NO LISTING)
# =========================================================
if [[ "$REMOVE_CONDA" -eq 1 && -d "$CONDA_HOME" ]]; then
	echo "$CONDA_HOME"
	rm -rf "$CONDA_HOME"
	remove_from_path "$CONDA_BIN_PATH"
fi

# =========================================================
# FAST DELETE HEAVY REPO DIRS (NO VERBOSE)
# =========================================================
for d in "${SKIP_DIRS[@]}"; do
	if [[ -d "$SCRIPT_DIR/$d" ]]; then
		echo "$SCRIPT_DIR/$d"
		rm -rf "$SCRIPT_DIR/$d"
	fi
done

# =========================================================
# REMOVE CURRENT REPO CONTENT (RECURSIVE, VERBOSE)
# =========================================================
echo
echo "Cleaning repository content..."

# remove files first
find "$SCRIPT_DIR" -mindepth 1 -type f \
	! -name "$SCRIPT_NAME" \
	$(printf "! -path */%s/* " "${SKIP_DIRS[@]}") \
	-print | while IFS= read -r f; do
		echo "${f#$SCRIPT_DIR/}"
		rm -f "$f"
	done

# then remove directories bottom-up
find "$SCRIPT_DIR" -mindepth 1 -type d \
	$(printf "! -path */%s/* " "${SKIP_DIRS[@]}") \
	-print | sort -r | while IFS= read -r d; do
		echo "${d#$SCRIPT_DIR/}"
		rmdir "$d" 2>/dev/null || true
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