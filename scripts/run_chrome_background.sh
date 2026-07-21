#!/usr/bin/env bash
# =============================================================================
# RUN CHROME IN BACKGROUND (--headless=new) FOR PLAYWRIGHT / CDP AUTOMATION
# =============================================================================
# Launches Chrome with remote debugging on port 9222 using $HOME/ChromeDebugProfile
# without stealing macOS window focus or creating visible windows.
#
# Usage:
#   bash scripts/run_chrome_background.sh [--status | --stop | --headed]
# =============================================================================

set -euo pipefail

PORT="9222"
PROFILE_DIR="$HOME/ChromeDebugProfile"
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/output/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/chrome_daemon.log"

ACTION="start"
HEADLESS_FLAG="--headless=new"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --status) ACTION="status"; shift ;;
        --stop) ACTION="stop"; shift ;;
        --headed) HEADLESS_FLAG=""; shift ;;
        *) echo "Unknown option: $1"; echo "Usage: $0 [--status | --stop | --headed]"; exit 1 ;;
    esac
done

check_status() {
    if curl -s "http://localhost:${PORT}/json/version" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

if [[ "$ACTION" == "status" ]]; then
    if check_status; then
        echo "✅ Chrome CDP is running and reachable on port ${PORT}."
        curl -s "http://localhost:${PORT}/json/version" | python3 -m json.tool || true
        exit 0
    else
        echo "⚪ Chrome CDP is NOT running on port ${PORT}."
        exit 1
    fi
fi

if [[ "$ACTION" == "stop" ]]; then
    if check_status; then
        echo "Stopping Chrome listening on port ${PORT}..."
        PIDS=$(pgrep -f -- "--remote-debugging-port=${PORT}" || true)
        if [[ -n "$PIDS" ]]; then
            kill $PIDS || true
            sleep 2
        fi
        if check_status; then
            echo "Force killing Chrome on port ${PORT}..."
            pkill -9 -f -- "--remote-debugging-port=${PORT}" || true
        fi
        echo "✅ Chrome stopped."
    else
        echo "⚪ Chrome was not running on port ${PORT}."
    fi
    exit 0
fi

# ACTION == start
if check_status; then
    echo "✅ Chrome is already running on port ${PORT}."
    echo "To restart or run with different flags, stop it first: bash scripts/run_chrome_background.sh --stop"
    exit 0
fi

if [[ ! -x "$CHROME_BIN" ]]; then
    echo "❌ ERROR: Chrome binary not found at: $CHROME_BIN"
    exit 1
fi

mkdir -p "$PROFILE_DIR"

if [[ -n "$HEADLESS_FLAG" ]]; then
    echo "🚀 Launching Chrome in background (--headless=new) on port ${PORT}..."
else
    echo "🚀 Launching Chrome in headed mode on port ${PORT}..."
fi

nohup "$CHROME_BIN" \
    --remote-debugging-port="${PORT}" \
    --user-data-dir="${PROFILE_DIR}" \
    ${HEADLESS_FLAG} \
    --disable-gpu \
    --no-first-run \
    --no-default-browser-check \
    > "${LOG_FILE}" 2>&1 &

echo "Waiting for Chrome CDP port ${PORT} to become ready..."
for i in {1..15}; do
    if check_status; then
        echo "✅ Chrome launched successfully and listening on port ${PORT}!"
        echo "   Profile : ${PROFILE_DIR}"
        echo "   Log     : ${LOG_FILE}"
        echo "   Mode    : ${HEADLESS_FLAG:-Headed}"
        exit 0
    fi
    sleep 1
done

echo "❌ ERROR: Chrome did not respond on port ${PORT} after 15 seconds. Check ${LOG_FILE}."
exit 1
