#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="http://0.0.0.0:7860/"
PORT=7860
TIMEOUT=180

cd "$SCRIPT_DIR"

# If something already holds :7860, just open the browser and exit.
if (exec 3<>/dev/tcp/127.0.0.1/$PORT) 2>/dev/null; then
    exec 3<&-; exec 3>&-
    echo "Server already running on :$PORT — opening $URL"
    xdg-open "$URL" >/dev/null 2>&1 &
    exit 0
fi

echo "Starting ebook2audiobook server…"
./ebook2audiobook.sh &
SERVER_PID=$!

cleanup() {
    echo
    echo "Stopping server (pid $SERVER_PID)…"
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup INT TERM

echo "Waiting for :$PORT (up to ${TIMEOUT}s)…"
for ((i=0; i<TIMEOUT; i++)); do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Server process exited before opening port. See log above." >&2
        exit 1
    fi
    if (exec 3<>/dev/tcp/127.0.0.1/$PORT) 2>/dev/null; then
        exec 3<&-; exec 3>&-
        echo "Server up. Opening $URL"
        xdg-open "$URL" >/dev/null 2>&1 &
        break
    fi
    sleep 1
done

wait "$SERVER_PID"
