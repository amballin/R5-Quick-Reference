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

set +e
VERIFICATION_CHECK_MESSAGE="$(
    python3 "$VERIFICATION_PROJECT_ROOT/80 Build/verification_status.py" check --root "$VERIFICATION_PROJECT_ROOT" 2>&1
)"
VERIFICATION_CHECK_RESULT=$?
set -e

case "$VERIFICATION_CHECK_RESULT" in
    0)
        ;;
    1)
        echo "NOTICE: $VERIFICATION_CHECK_MESSAGE"
        echo "Import the tracker before Finish Day."
        ;;
    2)
        echo "$VERIFICATION_CHECK_MESSAGE"
        echo "Refreshing the unchanged tracker from current definitions and Git-tracked status."
        "$VERIFICATION_SCRIPT_DIR/build-verification-working-copy.sh"
        ;;
    3)
        echo "TRACKER SAFETY BLOCK: $VERIFICATION_CHECK_MESSAGE" >&2
        echo "Run ./80\\ Build/scripts/import-verification-status.sh before opening the refreshed tracker." >&2
        exit 1
        ;;
    *)
        echo "TRACKER SAFETY BLOCK: Unexpected tracker check result $VERIFICATION_CHECK_RESULT." >&2
        echo "$VERIFICATION_CHECK_MESSAGE" >&2
        exit 1
        ;;
esac

if [[ -e "$VERIFICATION_NUMBERS" && ( ! -e "$VERIFICATION_XLSX" || "$VERIFICATION_NUMBERS" -nt "$VERIFICATION_XLSX" ) ]]; then
    VERIFICATION_TARGET="$VERIFICATION_NUMBERS"
else
    VERIFICATION_TARGET="$VERIFICATION_XLSX"
fi

echo "Opening verification tracker: $VERIFICATION_TARGET"
open "$VERIFICATION_TARGET"
