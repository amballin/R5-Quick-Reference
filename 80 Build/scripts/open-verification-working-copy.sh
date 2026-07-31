#!/usr/bin/env bash
set -euo pipefail

VERIFICATION_SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
VERIFICATION_PROJECT_ROOT="$(CDPATH= cd -- "$VERIFICATION_SCRIPT_DIR/../.." && pwd)"
VERIFICATION_LOCAL_DIR="$(
    cd "$VERIFICATION_PROJECT_ROOT"
    python3 -c 'import sys; sys.path.insert(0, "80 Build"); from asset_manager import ProjectPaths; print(ProjectPaths(sys.argv[1]).verification_working_dir)' "$VERIFICATION_PROJECT_ROOT"
)"
VERIFICATION_XLSX="$VERIFICATION_LOCAL_DIR/EOS R5 On-Camera Verification Tracker.xlsx"
VERIFICATION_NUMBERS="$VERIFICATION_LOCAL_DIR/EOS R5 On-Camera Verification Tracker.numbers"

if [[ ! -e "$VERIFICATION_XLSX" && ! -e "$VERIFICATION_NUMBERS" ]]; then
    echo "No local verification tracker exists. Creating one from Git-tracked status."
    "$VERIFICATION_SCRIPT_DIR/build-verification-working-copy.sh"
fi

if [[ -e "$VERIFICATION_NUMBERS" && ( ! -e "$VERIFICATION_XLSX" || "$VERIFICATION_NUMBERS" -nt "$VERIFICATION_XLSX" ) ]]; then
    VERIFICATION_TARGET="$VERIFICATION_NUMBERS"
else
    VERIFICATION_TARGET="$VERIFICATION_XLSX"
fi

if ! python3 "$VERIFICATION_PROJECT_ROOT/80 Build/verification_status.py" check --root "$VERIFICATION_PROJECT_ROOT"; then
    echo "NOTICE: This tracker contains changes not yet imported into Git-tracked status."
fi

echo "Opening verification tracker: $VERIFICATION_TARGET"
open "$VERIFICATION_TARGET"
