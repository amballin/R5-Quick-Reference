#!/bin/bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
LAUNCHER="$SCRIPT_DIR/80 Build/scripts/start-profile-editor.sh"

clear
echo "Starting Canon EOS R5 Profile Editor..."
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "Profile Editor cannot start because Python 3 is not installed."
    read -r -p "Press Return to close this window. "
    exit 1
fi

"$LAUNCHER"
STATUS=$?

if [[ "$STATUS" -ne 0 && "$STATUS" -ne 130 ]]; then
    echo
    echo "Profile Editor could not start or stop cleanly. Review the message above for details."
    read -r -p "Press Return to close this window. "
fi

exit "$STATUS"
