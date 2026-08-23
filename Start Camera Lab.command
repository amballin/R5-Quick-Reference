#!/bin/bash

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CAMERA_LAB_LAUNCHER="$SCRIPT_DIR/80 Build/scripts/start-camera-lab.sh"

clear
echo "Starting Canon EOS R5 Camera Lab..."
echo

if [[ ! -x "$CAMERA_LAB_LAUNCHER" ]]; then
    echo "Camera Lab's internal launcher is missing or is not executable:"
    echo "  $CAMERA_LAB_LAUNCHER"
    echo
    read -r -p "Press Return to close this window. "
    exit 1
fi

"$CAMERA_LAB_LAUNCHER"
STATUS=$?

if [[ "$STATUS" -ne 0 && "$STATUS" -ne 130 ]]; then
    echo
    echo "Camera Lab could not start. Review the message above for details."
    read -r -p "Press Return to close this window. "
fi

exit "$STATUS"
