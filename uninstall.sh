#!/usr/bin/env bash

if [[ "$OSTYPE" = "darwin"* && -z "$SWITCHED_TO_ZSH" && "$(ps -p $$ -o comm=)" != "zsh" ]]; then
	export SWITCHED_TO_ZSH=1
	exec env zsh "$0" "$@"
fi

set -euo pipefail

if [ -n "$BASH_SOURCE" ]; then
    script_path="${BASH_SOURCE[0]}"
elif [ -n "$ZSH_VERSION" ]; then
    script_path="${(%):-%x}"
else
    script_path="$0"
fi

APP_NAME="ebook2audiobook"
SCRIPT_DIR="$(cd "$(dirname "$script_path")" >/dev/null 2>&1 && pwd -P)"
INSTALLED_LOG="$SCRIPT_DIR/.installed"
MINIFORGE_PATH="$HOME/Miniforge3"
TEMP_UNINSTALL="/tmp/${APP_NAME}_uninstall.sh"

echo
echo "========================================"
echo "  Uninstalling $APP_NAME"
echo "========================================"
echo

# --- Relaunch from /tmp ---
if [[ "$SCRIPT_DIR" != "/tmp"* ]]; then
    echo "Copying uninstaller to temp and relaunching..."
    cp "$0" "$TEMP_UNINSTALL"
    chmod +x "$TEMP_UNINSTALL"
    exec "$TEMP_UNINSTALL"
fi

# --- Remove GUI shortcuts ---
if [[ "$OSTYPE" == "darwin"* ]]; then
    APP_BUNDLE="$HOME/Applications/$APP_NAME.app"
	DESKTOP_DIR="$(osascript -e 'POSIX path of (path to desktop folder)' 2>/dev/null | sed 's:/$::')"
	DESKTOP_SHORTCUT="$DESKTOP_DIR/$APP_NAME"
    if [[ -d "$APP_BUNDLE" ]]; then
        echo "Removing app bundle..."
        rm -rf "$APP_BUNDLE"
    fi
	if [[ -f "$DESKTOP_SHORTCUT" ]]; then
		echo "Removing desktop shortcut..."
		rm -f "$DESKTOP_SHORTCUT"
	fi
elif [[ "$OSTYPE" == "linux"* ]]; then
	MENU_ENTRY="$HOME/.local/share/applications/$APP_NAME.desktop"
	DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
	DESKTOP_SHORTCUT="$DESKTOP_DIR/$APP_NAME.desktop"
    if [[ -f "$MENU_ENTRY" ]]; then
        echo "Removing app menu entry..."
        rm -f "$MENU_ENTRY"
        update-desktop-database ~/.local/share/applications >/dev/null 2>&1 || true
    fi
	if [[ -f "DESKTOP_SHORTCUT" ]]; then
		echo "Removing desktop shortcut..."
		rm -f "DESKTOP_SHORTCUT"
	fi
fi

# --- Check installed log for Miniforge3 ---
if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "Miniforge3" "$INSTALLED_LOG"; then
    if [[ -d "$MINIFORGE_PATH" ]]; then
        echo "Removing Miniforge3 installation at: $MINIFORGE_PATH"
        rm -rf "$MINIFORGE_PATH"
    else
        echo "Miniforge3 folder not found, skipping."
    fi
else
    echo "Miniforge3 not installed by this app, skipping."
fi

# --- Remove main app folder ---
if [[ -d "$SCRIPT_DIR" ]]; then
    echo "Removing main application folder: $SCRIPT_DIR"
    rm -rf "$SCRIPT_DIR"
fi

# --- Clean up temp copy ---
echo "Cleaning up temporary uninstaller..."
rm -f "$TEMP_UNINSTALL" || true

echo
echo "Uninstall complete."

exit 0