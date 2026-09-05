#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
CAMERA_LAB_ORIGIN="http://127.0.0.1:8770"
CAMERA_LAB_URL="$CAMERA_LAB_ORIGIN/"
BACKEND="edsdk"
CAMERA_LAB_PID=""
PROFILE_NAME=""
PROFILE_PACK_ROOT=""

usage() {
    echo "Usage: ./80\\ Build/scripts/start-camera-lab.sh [--simulated] [--profile NAME] [--profile-pack PATH]"
    echo
    echo "Without an option, starts the physical Canon EDSDK connection."
    echo "Use --simulated to start the Camera Lab simulator instead."
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --simulated)
            BACKEND="simulated"
            shift
            ;;
        --profile)
            if [[ $# -lt 2 || -z "$2" ]]; then
                usage
                exit 2
            fi
            PROFILE_NAME="$2"
            shift 2
            ;;
        --profile-pack)
            if [[ $# -lt 2 || -z "$2" ]]; then
                usage
                exit 2
            fi
            PROFILE_PACK_ROOT="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            usage
            exit 2
            ;;
    esac
done

EXPECTED_PACK_ID="$(python3 -B -c '
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "80 Build"))
from profile_pack import resolve_profile_pack
context = resolve_profile_pack(root, explicit_root=sys.argv[2] or None)
print(context.pack_id)
' "$PROJECT_ROOT" "$PROFILE_PACK_ROOT")"

if [[ -n "$PROFILE_NAME" ]]; then
    ENCODED_PROFILE="$(python3 -c 'import sys; from urllib.parse import quote; print(quote(sys.argv[1]))' "$PROFILE_NAME")"
    CAMERA_LAB_URL="$CAMERA_LAB_ORIGIN/?profile=$ENCODED_PROFILE"
fi

if ! command -v open >/dev/null 2>&1 || ! open -Ra "Google Chrome"; then
    echo "Google Chrome is not installed or cannot be opened."
    exit 1
fi

CAMERA_LAB_STATUS="$(curl -fsS "$CAMERA_LAB_ORIGIN/api/camera-control/status" 2>/dev/null || true)"
if [[ -n "$CAMERA_LAB_STATUS" ]] && python3 -c '
import json, sys
payload = json.loads(sys.argv[1])
app = payload.get("app")
valid = (
    payload.get("ok") is True
    and payload.get("backend_mode") in {"edsdk", "simulated"}
    and isinstance(app, dict)
    and isinstance(app.get("version"), str)
    and isinstance(app.get("project_context"), dict)
    and isinstance(app.get("profile_pack"), dict)
    and app["profile_pack"].get("pack_id") == sys.argv[2]
)
raise SystemExit(0 if valid else 1)
' "$CAMERA_LAB_STATUS" "$EXPECTED_PACK_ID" 2>/dev/null; then
    open -a "Google Chrome" "$CAMERA_LAB_URL"
    echo "Camera Lab is already running on port 8770; Google Chrome reopened it."
    exit 0
fi

if [[ -n "$CAMERA_LAB_STATUS" ]]; then
    RUNNING_PACK="$(python3 -c '
import json, sys
try:
    app = json.loads(sys.argv[1]).get("app") or {}
    pack = app.get("profile_pack") or {}
    print(pack.get("pack_name") or "another profile pack")
except Exception:
    pass
' "$CAMERA_LAB_STATUS")"
    if [[ -n "$RUNNING_PACK" ]]; then
        echo "Camera Lab is already running with $RUNNING_PACK."
        echo "Stop that Camera Lab session, then open the selected profile pack again."
        exit 1
    fi
fi

if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:8770 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Camera Lab cannot start because port 8770 is already in use."
    echo "Stop the existing Camera Lab with Control-C, then run this command again."
    exit 1
fi

SERVER_COMMAND=(python3 -B "$PROJECT_ROOT/80 Build/camera_control/dev_server.py")
if [[ -n "$PROFILE_PACK_ROOT" ]]; then
    SERVER_COMMAND+=(--profile-pack "$PROFILE_PACK_ROOT")
fi
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
