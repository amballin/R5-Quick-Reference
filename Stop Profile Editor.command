#!/bin/bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
STOPPER="$SCRIPT_DIR/80 Build/scripts/stop-profile-editor.sh"

clear
echo "Stopping Canon EOS R5 Profile Editor..."
echo

"$STOPPER"
STATUS=$?

echo
read -r -p "Press Return to close this window. "
exit "$STATUS"
