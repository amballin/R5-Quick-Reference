#!/bin/bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROFILE_EDITOR_ORIGIN="http://127.0.0.1:8765"
PROFILE_EDITOR_URL="$PROFILE_EDITOR_ORIGIN/"
PROFILE_EDITOR_PID=""

cleanup() {
    if [[ -n "$PROFILE_EDITOR_PID" ]] && kill -0 "$PROFILE_EDITOR_PID" >/dev/null 2>&1; then
        kill "$PROFILE_EDITOR_PID" >/dev/null 2>&1 || true
        wait "$PROFILE_EDITOR_PID" >/dev/null 2>&1 || true
    fi
}

trap cleanup EXIT
trap 'exit 130' INT TERM

clear
echo "Starting Canon EOS R5 Profile Editor..."
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "Profile Editor cannot start because Python 3 is not installed."
    read -r -p "Press Return to close this window. "
    exit 1
fi

if ! command -v open >/dev/null 2>&1 || ! open -Ra "Google Chrome"; then
    echo "Google Chrome is not installed or cannot be opened."
    read -r -p "Press Return to close this window. "
    exit 1
fi

if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Profile Editor cannot start because port 8765 is already in use."
    echo "Stop the existing Profile Editor with Control-C, then try again."
    echo
    read -r -p "Press Return to close this window. "
    exit 1
fi

cd "$SCRIPT_DIR" || exit 1
python3 -B "$SCRIPT_DIR/80 Build/profile_editor.py" &
PROFILE_EDITOR_PID=$!

READY=0
for _ in {1..100}; do
    if curl -fsS "$PROFILE_EDITOR_URL" >/dev/null 2>&1; then
        READY=1
        break
    fi
    if ! kill -0 "$PROFILE_EDITOR_PID" >/dev/null 2>&1; then
        wait "$PROFILE_EDITOR_PID"
        STATUS=$?
        echo
        echo "Profile Editor could not start. Review the message above for details."
        read -r -p "Press Return to close this window. "
        if [[ "$STATUS" -eq 0 ]]; then
            exit 1
        fi
        exit "$STATUS"
    fi
    sleep 0.1
done

if [[ "$READY" -ne 1 ]]; then
    echo "Profile Editor did not become ready at $PROFILE_EDITOR_URL"
    echo
    read -r -p "Press Return to close this window. "
    exit 1
fi

open -a "Google Chrome" "$PROFILE_EDITOR_URL"
echo
echo "Profile Editor is running in Google Chrome."
echo "Press Control-C here to stop Profile Editor cleanly."

wait "$PROFILE_EDITOR_PID"
STATUS=$?

if [[ "$STATUS" -ne 0 && "$STATUS" -ne 130 ]]; then
    echo
    echo "Profile Editor stopped unexpectedly. Review the message above for details."
    read -r -p "Press Return to close this window. "
fi

exit "$STATUS"
