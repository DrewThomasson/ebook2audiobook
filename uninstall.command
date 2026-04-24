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
	# Refuse to operate on empty or dangerous targets
	[[ -z "$target" ]] && return 0
	case "$target" in
		/|/bin|/usr/bin|/sbin|/usr/sbin|/usr/local/bin) return 0 ;;
	esac

	local new_path=""
	local rest="${PATH:-}"
	local p
	while [[ -n "$rest" ]]; do
		if [[ "$rest" == *:* ]]; then
			p="${rest%%:*}"
			rest="${rest#*:}"
		else
			p="$rest"
			rest=""
		fi
		[[ -z "$p" ]] && continue
		[[ "$p" == "$target" ]] && continue
		new_path="${new_path:+$new_path:}$p"
	done
	PATH="$new_path"
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
# LINUX SHORTCUT CLEANUP (NO TESTS, GUARDED)
# =========================================================
if [[ "${OSTYPE:-}" == linux* ]]; then
	echo "Cleaning Linux shortcuts"

	if [[ -n "$DESKTOP_ALIAS" && "$DESKTOP_ALIAS" != "/" ]]; then
		rm -f "$DESKTOP_ALIAS" 2>/dev/null || true
	fi
fi

# =========================================================
# PROCESS .installed (CONTROLLED REMOVAL)
# =========================================================
REMOVE_CONDA=0
if [[ -f "$INSTALLED_LOG" ]] && grep -iqF "Miniforge3" "$INSTALLED_LOG"; then
	REMOVE_CONDA=1
fi

# =========================================================
# SAFE PATH CLEANUP
# =========================================================
remove_from_path() {
	local target="$1"
	local new_path=""
	local rest="${PATH:-}"
	local p
	while [[ -n "$rest" ]]; do
		if [[ "$rest" == *:* ]]; then
			p="${rest%%:*}"
			rest="${rest#*:}"
		else
			p="$rest"
			rest=""
		fi
		[[ "$p" == "$target" ]] && continue
		new_path="${new_path:+$new_path:}$p"
	done
	PATH="$new_path"
	export PATH
}

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

# Make unmatched globs expand to nothing instead of erroring (zsh) or staying literal (bash)
if [[ -n "${ZSH_VERSION:-}" ]]; then
	setopt local_options null_glob
else
	shopt -s nullglob 2>/dev/null || true
fi

for item in "$SCRIPT_DIR"/* "$SCRIPT_DIR"/.*; do
	name="${item##*/}"
	[[ "$name" == "." || "$name" == ".." ]] && continue
	[[ "$name" == "$SCRIPT_NAME" ]] && continue
	echo "-> $item"
	if [[ -n "$item" && "$item" != "/" ]]; then
		/bin/rm -rf "$item"
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
