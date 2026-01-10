#!/bin/zsh
# -*- coding: utf-8 -*-
#
# 🍎 Простой запуск ebook2audiobook на macOS
# Просто дважды кликните на этот файл!
#

set -e

# Определяем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" && pwd )"
cd "$SCRIPT_DIR"

# Красивый вывод
echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║      📚 ebook2audiobook - Установка на macOS      ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Проверяем macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Этот скрипт работает только на macOS!"
    echo "   Для Linux/Windows используйте ebook2audiobook.sh"
    exit 1
fi

echo "✅ Операционная система: macOS $(sw_vers -productVersion)"
echo "✅ Архитектура: $(uname -m)"
echo ""

# Проверяем наличие основного скрипта
if [[ ! -f "$SCRIPT_DIR/ebook2audiobook.sh" ]]; then
    echo "❌ Не найден файл ebook2audiobook.sh"
    echo "   Убедитесь, что вы находитесь в правильной директории"
    exit 1
fi

# Даем права на выполнение
chmod +x "$SCRIPT_DIR/ebook2audiobook.sh"

echo "🚀 Запускаю установку и настройку..."
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  Это может занять 15-30 минут при первом запуске │"
echo "│                                                 │"
echo "│  Что будет установлено:                         │"
echo "│  • Homebrew (если не установлен)                │"
echo "│  • Calibre, FFmpeg, espeak-ng                   │"
echo "│  • Python окружение через Miniforge3            │"
echo "│  • Все необходимые библиотеки                   │"
echo "└─────────────────────────────────────────────────┘"
echo ""

# Спрашиваем пользователя
read "response?Продолжить установку? (y/n): "
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "❌ Установка отменена"
    exit 0
fi

echo ""
echo "⏳ Начинаю установку..."
echo ""

# Запускаем основной скрипт
"$SCRIPT_DIR/ebook2audiobook.sh"

# Проверяем успешность
if [[ $? -eq 0 ]]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║                                                   ║"
    echo "║          ✅ Установка завершена успешно!          ║"
    echo "║                                                   ║"
    echo "║   Откройте в браузере: http://localhost:7860     ║"
    echo "║                                                   ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""
    echo "💡 Совет: Добавьте этот скрипт в Dock для быстрого запуска!"
    echo ""
else
    echo ""
    echo "❌ Произошла ошибка при установке"
    echo "   Проверьте логи выше для деталей"
    echo ""
    exit 1
fi

# Держим окно открытым
read "?Нажмите Enter для выхода..."
