#!/usr/bin/env bash

set -euo pipefail

APP_NAME="ebook2audiobook"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
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

# --- Kill running processes ---
echo "Stopping any running $APP_NAME or Python processes..."
pkill -f "$APP_NAME" 2>/dev/null || true
pkill -f "python" 2>/dev/null || true

# --- Remove GUI shortcuts ---
if [[ "$OSTYPE" == "darwin"* ]]; then
    APP_BUNDLE="$HOME/Applications/$APP_NAME.app"
    if [[ -d "$APP_BUNDLE" ]]; then
        echo "Removing macOS app bundle..."
        rm -rf "$APP_BUNDLE"
    fi
elif [[ "$OSTYPE" == "linux"* ]]; then
    DESKTOP_FILE="$HOME/.local/share/applications/${APP_NAME}.desktop"
    if [[ -f "$DESKTOP_FILE" ]]; then
        echo "Removing desktop shortcut..."
        rm -f "$DESKTOP_FILE"
        update-desktop-database ~/.local/share/applications >/dev/null 2>&1 || true
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
echo "✅ Uninstall complete."
exit 0