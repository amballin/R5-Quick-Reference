#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
PROFILE_EDITOR_ORIGIN="http://127.0.0.1:8765"
PROFILE_EDITOR_PID=""

cleanup() {
    if [[ -n "$PROFILE_EDITOR_PID" ]] && kill -0 "$PROFILE_EDITOR_PID" >/dev/null 2>&1; then
        kill "$PROFILE_EDITOR_PID" >/dev/null 2>&1 || true
        wait "$PROFILE_EDITOR_PID" >/dev/null 2>&1 || true
    fi
}

trap cleanup EXIT
trap 'exit 130' INT TERM

if ! command -v open >/dev/null 2>&1 || ! open -Ra "Google Chrome"; then
    echo "Google Chrome is not installed or cannot be opened."
    exit 1
fi

if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Profile Editor cannot start because port 8765 is already in use."
    echo "Stop the existing Profile Editor, then try again."
    exit 1
fi

cd "$PROJECT_ROOT"
python3 -B "$PROJECT_ROOT/80 Build/profile_editor.py" &
PROFILE_EDITOR_PID=$!

READY=0
for _ in {1..100}; do
    if curl -fsS "$PROFILE_EDITOR_ORIGIN/" >/dev/null 2>&1; then
        READY=1
        break
    fi
    if ! kill -0 "$PROFILE_EDITOR_PID" >/dev/null 2>&1; then
        wait "$PROFILE_EDITOR_PID"
        exit 1
    fi
    sleep 0.1
done

if [[ "$READY" -ne 1 ]]; then
    echo "Profile Editor did not become ready at $PROFILE_EDITOR_ORIGIN/"
    exit 1
fi

open -a "Google Chrome" "$PROFILE_EDITOR_ORIGIN/"
echo "Profile Editor is running. Use Stop Profile Editor in the page header to stop it cleanly."

wait "$PROFILE_EDITOR_PID"
