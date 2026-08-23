#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
CAMERA_LAB_ORIGIN="http://127.0.0.1:8770"
CAMERA_LAB_URL="$CAMERA_LAB_ORIGIN/"
BACKEND="edsdk"
CAMERA_LAB_PID=""

usage() {
    echo "Usage: ./80\\ Build/scripts/start-camera-lab.sh [--simulated]"
    echo
    echo "Without an option, starts the physical Canon EDSDK connection."
    echo "Use --simulated to start the Camera Lab simulator instead."
}

if [[ $# -gt 1 ]]; then
    usage
    exit 2
fi

if [[ $# -eq 1 ]]; then
    case "$1" in
        --simulated) BACKEND="simulated" ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            usage
            exit 2
            ;;
    esac
fi

if ! command -v open >/dev/null 2>&1 || ! open -Ra "Google Chrome"; then
    echo "Google Chrome is not installed or cannot be opened."
    exit 1
fi

if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:8770 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Camera Lab cannot start because port 8770 is already in use."
    echo "Stop the existing Camera Lab with Control-C, then run this command again."
    exit 1
fi

SERVER_COMMAND=(python3 -B "$PROJECT_ROOT/80 Build/camera_control/dev_server.py")
if [[ "$BACKEND" == "edsdk" ]]; then
    if [[ -n "${PRS_LOCAL_WORKSPACE:-}" ]]; then
        LOCAL_WORKSPACE="$PRS_LOCAL_WORKSPACE"
    else
        LOCAL_WORKSPACE="${PROJECT_ROOT} Local"
    fi
    HELPER_APP="$LOCAL_WORKSPACE/SDK/EDSDKHelper.app"
    if [[ ! -d "$HELPER_APP" ]]; then
        echo "The machine-local Canon EDSDK helper was not found:"
        echo "  $HELPER_APP"
        echo "Run the documented first-time EDSDK setup, then try again."
        exit 1
    fi
    SERVER_COMMAND+=(--backend edsdk --sdk-path "$HELPER_APP")
else
    SERVER_COMMAND+=(--backend simulated)
fi

cleanup() {
    if [[ -n "$CAMERA_LAB_PID" ]] && kill -0 "$CAMERA_LAB_PID" >/dev/null 2>&1; then
        kill "$CAMERA_LAB_PID" >/dev/null 2>&1 || true
        wait "$CAMERA_LAB_PID" >/dev/null 2>&1 || true
    fi
}

trap cleanup EXIT
trap 'exit 130' INT TERM

cd "$PROJECT_ROOT"
"${SERVER_COMMAND[@]}" &
CAMERA_LAB_PID=$!

READY=0
for _ in {1..100}; do
    if curl -fsS "$CAMERA_LAB_ORIGIN/api/camera-control/status" >/dev/null 2>&1; then
        READY=1
        break
    fi
    if ! kill -0 "$CAMERA_LAB_PID" >/dev/null 2>&1; then
        wait "$CAMERA_LAB_PID"
        exit 1
    fi
    sleep 0.1
done

if [[ "$READY" -ne 1 ]]; then
    echo "Camera Lab did not become ready at $CAMERA_LAB_URL"
    exit 1
fi

open -a "Google Chrome" "$CAMERA_LAB_URL"
echo
echo "Camera Lab is running in $BACKEND mode."
echo "Google Chrome opened $CAMERA_LAB_URL"
echo "Press Control-C here to stop Camera Lab cleanly."

wait "$CAMERA_LAB_PID"
