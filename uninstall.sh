#!/usr/bin/env bash

if [[ "$OSTYPE" = "darwin"* && -z "$SWITCHED_TO_ZSH" && "$(ps -p $$ -o comm=)" != "zsh" ]]; then
    export SWITCHED_TO_ZSH=1
    exec env zsh "$0" "$@"
fi

if [ -n "$BASH_SOURCE" ]; then
    script_path="${BASH_SOURCE[0]}"
elif [ -n "$ZSH_VERSION" ]; then
    script_path="${(%):-%x}"
else
    script_path="$0"
fi

APP_NAME="ebook2audiobook"
SCRIPT_DIR="$(cd "$(dirname "$script_path")" >/dev/null 2>&1 && pwd -P)"
SCRIPT_NAME="$(basename "$script_path")"
INSTALLED_LOG="$SCRIPT_DIR/.installed"
MINIFORGE_PATH="$HOME/Miniforge3"
UNINSTALLER="uninstall.sh"
UNINSTALLER_PATH="$SCRIPT_DIR/$UNINSTALLER"
TEMP_UNINSTALLER="/tmp/${APP_NAME}_uninstaller.sh"

function remove_homebrew() {
    local BREW_PATH=""
    local BREW_BIN=""
    local UNINSTALLER="/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)\""
    if [[ -d "/opt/homebrew" ]]; then
        BREW_PATH="/opt/homebrew"
    elif [[ -d "/usr/local/Homebrew" ]]; then
        BREW_PATH="/usr/local/Homebrew"
    else
        BREW_PATH=""
    fi
    BREW_BIN="$BREW_PATH/bin/brew"
    if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "Homebrew" "$INSTALLED_LOG"; then
        if [[ -x "$BREW_BIN" ]]; then
            echo "[INFO] Homebrew detected at: $BREW_PATH"
            "$BREW_BIN" list -1 | while read -r pkg; do
                echo "  → Uninstalling $pkg"
                "$BREW_BIN" uninstall --force --ignore-dependencies "$pkg" >/dev/null 2>&1
            done
            echo "[INFO] Running Homebrew cleanup..."
            "$BREW_BIN" cleanup -s >/dev/null 2>&1 || true
            echo "[INFO] Executing official Homebrew uninstall script..."
            zsh -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)" >/dev/null 2>&1
            echo "[INFO] Removing residual Homebrew directories..."
            sudo rm -rf "$BREW_PATH" \
                        "$HOME/Library/Caches/Homebrew" \
                        "$HOME/Library/Logs/Homebrew" \
                        "$HOME/Library/Preferences/com.apple.Homebrew.plist" \
                        "$HOME/Library/Preferences/Homebrew"

            echo "[SUCCESS] Homebrew completely removed."
        fi
    fi
}

echo
echo "========================================"
echo "  Uninstalling $APP_NAME"
echo "========================================"
echo

if [[ "$SCRIPT_NAME" == "UNINSTALLER"* ]]; then
    echo "Copying uninstaller to temp and relaunching..."
    cp "$0" "$TEMP_UNINSTALLER"
    chmod +x "$TEMP_UNINSTALLER"
    exec "$TEMP_UNINSTALLER"
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    APP_BUNDLE="$HOME/Applications/$APP_NAME.app"
    DESKTOP_DIR="$(osascript -e 'POSIX path of (path to desktop folder)' 2>/dev/null | sed 's:/$::')"
    DESKTOP_SHORTCUT="$DESKTOP_DIR/$APP_NAME"
    if [[ -d "$APP_BUNDLE" ]]; then
        echo "Removing app bundle..."
        rm -rf "$APP_BUNDLE"
    fi
    rm -f "$DESKTOP_SHORTCUT" 2>&1 > /dev/null
elif [[ "$OSTYPE" == "linux"* ]]; then
    MENU_ENTRY="$HOME/.local/share/applications/$APP_NAME.desktop"
    DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
    DESKTOP_SHORTCUT="$DESKTOP_DIR/$APP_NAME.desktop"
    if [[ -f "$MENU_ENTRY" ]]; then
        echo "Removing app menu entry..."
        rm -f "$MENU_ENTRY"
        update-desktop-database ~/.local/share/applications >/dev/null 2>&1 || true
    fi
    rm -f "$DESKTOP_SHORTCUT" 2>&1 > /dev/null
fi

if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "homebrew" "$INSTALLED_LOG"; then
    remove_homebrew
fi

if [[ -f "$INSTALLED_LOG" ]] && grep -iqFx "Miniforge3" "$INSTALLED_LOG"; then
    if [[ -d "$MINIFORGE_PATH" ]]; then
        echo "Removing Miniforge3 installation at: $MINIFORGE_PATH"
        rm -rf "$MINIFORGE_PATH"
    else
        echo "Miniforge3 folder not found, skipping."
    fi
fi

if [[ -d "$SCRIPT_DIR" ]]; then
    echo "Removing main application folder: $SCRIPT_DIR"
    rm -rf "$SCRIPT_DIR"
fi

echo "Cleaning up temporary uninstaller..."
rm -f "$TEMP_UNINSTALLER" || true

echo
echo "Uninstall complete."

exit 0