#!/usr/bin/env bash

# Shared, source-only runtime helpers for the Profile Editor launch and recovery commands.

PROFILE_EDITOR_SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$PROFILE_EDITOR_SCRIPT_DIR/../.." && pwd)"
PROFILE_EDITOR_PROGRAM="$PROJECT_ROOT/80 Build/profile_editor.py"
PROFILE_EDITOR_PORT="$(python3 -B "$PROFILE_EDITOR_PROGRAM" --print-default-port)"
PROFILE_EDITOR_ORIGIN="http://127.0.0.1:$PROFILE_EDITOR_PORT"
PROFILE_EDITOR_URL="$PROFILE_EDITOR_ORIGIN/"
LOCAL_WORKSPACE="${PRS_LOCAL_WORKSPACE:-${PROJECT_ROOT} Local}"
PROFILE_EDITOR_RUN_DIR="$LOCAL_WORKSPACE/Run"
PROFILE_EDITOR_PID_FILE="$PROFILE_EDITOR_RUN_DIR/R5 Profile Editor.pid"

profile_editor_listener_pid() {
    local port="${1:-$PROFILE_EDITOR_PORT}"
    command -v lsof >/dev/null 2>&1 || return 1
    lsof -nP -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null | head -n 1
}

profile_editor_pid_matches() {
    local pid="$1"
    local port="${2:-$PROFILE_EDITOR_PORT}"
    local command_line=""
    local process_cwd=""
    [[ "$pid" =~ ^[0-9]+$ ]] || return 1
    kill -0 "$pid" >/dev/null 2>&1 || return 1
    command_line="$(ps -p "$pid" -o command= 2>/dev/null || true)"
    [[ "$command_line" == *"$PROFILE_EDITOR_PROGRAM"* ]] || return 1
    process_cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -n 1)"
    [[ "$process_cwd" == "$PROJECT_ROOT" ]] || return 1
    lsof -nP -a -p "$pid" -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

profile_editor_is_ready() {
    local port="${1:-$PROFILE_EDITOR_PORT}"
    curl -fsS "http://127.0.0.1:$port/api/editor-info" >/dev/null 2>&1
}

profile_editor_record_pid() {
    local pid="$1"
    local temporary="$PROFILE_EDITOR_PID_FILE.$$"
    mkdir -p "$PROFILE_EDITOR_RUN_DIR"
    printf '%s\n' "$pid" > "$temporary"
    mv -f "$temporary" "$PROFILE_EDITOR_PID_FILE"
}

profile_editor_forget_pid() {
    local expected_pid="${1:-}"
    local recorded_pid=""
    [[ -f "$PROFILE_EDITOR_PID_FILE" ]] || return 0
    IFS= read -r recorded_pid < "$PROFILE_EDITOR_PID_FILE" || true
    if [[ -z "$expected_pid" || "$recorded_pid" == "$expected_pid" ]]; then
        rm -f "$PROFILE_EDITOR_PID_FILE"
    fi
}

profile_editor_find_owned_pid() {
    local pid=""
    if [[ -f "$PROFILE_EDITOR_PID_FILE" ]]; then
        IFS= read -r pid < "$PROFILE_EDITOR_PID_FILE" || true
        if profile_editor_pid_matches "$pid"; then
            printf '%s\n' "$pid"
            return 0
        fi
        profile_editor_forget_pid "$pid"
    fi
    pid="$(profile_editor_listener_pid || true)"
    if [[ -n "$pid" ]] && profile_editor_pid_matches "$pid"; then
        profile_editor_record_pid "$pid"
        printf '%s\n' "$pid"
        return 0
    fi
    return 1
}

profile_editor_find_legacy_pid() {
    local legacy_port=8765
    local pid=""
    [[ "$PROFILE_EDITOR_PORT" -ne "$legacy_port" ]] || return 1
    pid="$(profile_editor_listener_pid "$legacy_port" || true)"
    if [[ -n "$pid" ]] && profile_editor_pid_matches "$pid" "$legacy_port" && profile_editor_is_ready "$legacy_port"; then
        printf '%s\n' "$pid"
        return 0
    fi
    return 1
}

profile_editor_stop_pid() {
    local pid="$1"
    local port="${2:-$PROFILE_EDITOR_PORT}"
    local attempt
    profile_editor_pid_matches "$pid" "$port" || return 1
    kill -TERM "$pid"
    for attempt in {1..50}; do
        if ! kill -0 "$pid" >/dev/null 2>&1; then
            profile_editor_forget_pid "$pid"
            return 0
        fi
        sleep 0.1
    done
    return 1
}
