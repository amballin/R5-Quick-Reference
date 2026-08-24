#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck source=profile-editor-runtime.sh
source "$SCRIPT_DIR/profile-editor-runtime.sh"

PROFILE_EDITOR_PID=""

cleanup() {
    if [[ -n "$PROFILE_EDITOR_PID" ]] && kill -0 "$PROFILE_EDITOR_PID" >/dev/null 2>&1; then
        kill -TERM "$PROFILE_EDITOR_PID" >/dev/null 2>&1 || true
        wait "$PROFILE_EDITOR_PID" >/dev/null 2>&1 || true
    fi
    if [[ -n "$PROFILE_EDITOR_PID" ]]; then
        profile_editor_forget_pid "$PROFILE_EDITOR_PID"
    fi
}

trap cleanup EXIT
trap 'exit 130' INT TERM

if ! command -v open >/dev/null 2>&1 || ! open -Ra "Google Chrome"; then
    echo "Google Chrome is not installed or cannot be opened."
    exit 1
fi

EXISTING_PID="$(profile_editor_find_owned_pid || true)"
if [[ -n "$EXISTING_PID" ]]; then
    if profile_editor_is_ready; then
        open -a "Google Chrome" "$PROFILE_EDITOR_URL"
        echo "Profile Editor is already running on port $PROFILE_EDITOR_PORT; Google Chrome reopened it."
        exit 0
    fi
    echo "Cleaning up an unresponsive Profile Editor process for this project."
    if ! profile_editor_stop_pid "$EXISTING_PID"; then
        echo "Profile Editor could not safely stop its unresponsive process $EXISTING_PID."
        echo "Use Stop Profile Editor.command, then try again."
        exit 1
    fi
fi

LEGACY_PID="$(profile_editor_find_legacy_pid || true)"
if [[ -n "$LEGACY_PID" ]]; then
    echo "An older Profile Editor for this prototype is still running on port 8765 (process $LEGACY_PID)."
    echo "Use Stop Profile Editor.command once to clear it, then reopen this application on port $PROFILE_EDITOR_PORT."
    exit 1
fi

LISTENER_PID="$(profile_editor_listener_pid || true)"
if [[ -n "$LISTENER_PID" ]]; then
    echo "Profile Editor cannot start because port $PROFILE_EDITOR_PORT is used by an unrecognized process ($LISTENER_PID)."
    echo "The launcher did not stop that process."
    exit 1
fi

cd "$PROJECT_ROOT"
python3 -B "$PROFILE_EDITOR_PROGRAM" --port "$PROFILE_EDITOR_PORT" &
PROFILE_EDITOR_PID=$!
profile_editor_record_pid "$PROFILE_EDITOR_PID"

READY=0
for _ in {1..100}; do
    if profile_editor_is_ready; then
        READY=1
        break
    fi
    if ! kill -0 "$PROFILE_EDITOR_PID" >/dev/null 2>&1; then
        set +e
        wait "$PROFILE_EDITOR_PID"
        STATUS=$?
        set -e
        profile_editor_forget_pid "$PROFILE_EDITOR_PID"
        PROFILE_EDITOR_PID=""
        if [[ "$STATUS" -eq 0 ]]; then
            STATUS=1
        fi
        exit "$STATUS"
    fi
    sleep 0.1
done

if [[ "$READY" -ne 1 ]]; then
    echo "Profile Editor did not become ready at $PROFILE_EDITOR_URL"
    exit 1
fi

open -a "Google Chrome" "$PROFILE_EDITOR_URL"
echo "Profile Editor is running on port $PROFILE_EDITOR_PORT. Use Stop Profile Editor in the page header to stop it cleanly."

set +e
wait "$PROFILE_EDITOR_PID"
STATUS=$?
set -e
profile_editor_forget_pid "$PROFILE_EDITOR_PID"
PROFILE_EDITOR_PID=""
if [[ "$STATUS" -eq 143 ]]; then
    STATUS=0
fi
exit "$STATUS"
