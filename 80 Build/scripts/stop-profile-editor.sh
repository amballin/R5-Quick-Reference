#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck source=profile-editor-runtime.sh
source "$SCRIPT_DIR/profile-editor-runtime.sh"

PROFILE_EDITOR_PID="$(profile_editor_find_owned_pid || true)"
PROFILE_EDITOR_PID_PORT="$PROFILE_EDITOR_PORT"
if [[ -z "$PROFILE_EDITOR_PID" ]]; then
    PROFILE_EDITOR_PID="$(profile_editor_find_legacy_pid || true)"
    if [[ -n "$PROFILE_EDITOR_PID" ]]; then
        PROFILE_EDITOR_PID_PORT=8765
        echo "Found an older verified prototype editor on port 8765."
    fi
fi
if [[ -z "$PROFILE_EDITOR_PID" ]]; then
    LISTENER_PID="$(profile_editor_listener_pid || true)"
    if [[ -n "$LISTENER_PID" ]]; then
        echo "Port $PROFILE_EDITOR_PORT is used by an unrecognized process ($LISTENER_PID). Nothing was stopped."
        exit 1
    fi
    profile_editor_forget_pid
    echo "Profile Editor is not running for this project; port $PROFILE_EDITOR_PORT is already free."
    exit 0
fi

if ! profile_editor_stop_pid "$PROFILE_EDITOR_PID" "$PROFILE_EDITOR_PID_PORT"; then
    echo "Profile Editor process $PROFILE_EDITOR_PID did not stop cleanly. Nothing else was stopped."
    exit 1
fi

echo "Profile Editor stopped. Port $PROFILE_EDITOR_PID_PORT is free."
