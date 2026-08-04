#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
STATUS_SCRIPT="$SCRIPT_DIR/git-status-report.sh"

"$STATUS_SCRIPT"
RESULT=$?

spreadsheet_notice() {
    echo
    echo "Spreadsheet note: Release files stay on this Mac and are not required for ordinary development or Git synchronization."
    echo "Rebuild them only when publishing replacement spreadsheet downloads."
    echo "If spreadsheet source or layout changed, website publication will stop until the affected workbook is rebuilt or its downloads are deliberately removed."
    local verification_message verification_result
    verification_message="$(python3 "$SCRIPT_DIR/../verification_status.py" check --root "$SCRIPT_DIR/../.." 2>&1)"
    verification_result=$?
    case "$verification_result" in
        0)
            echo "Verification status: $verification_message"
            return 0
            ;;
        1)
            echo "PREFLIGHT NOTICE: $verification_message"
            echo "Import the working tracker before finishing or switching computers."
            return 0
            ;;
        2)
            echo "PREFLIGHT BLOCK: $verification_message"
            echo "Run the open-tracker helper to rebuild it safely before testing or Finish Day."
            return 1
            ;;
        3)
            echo "PREFLIGHT BLOCK: $verification_message"
            echo "Import the working tracker before rebuilding, testing, or switching computers."
            return 1
            ;;
        *)
            echo "PREFLIGHT BLOCK: Tracker state could not be verified."
            return 1
            ;;
    esac
}

echo
case "$RESULT" in
    0)
        echo "PREFLIGHT PASSED: Repository is clean and synchronized."
        echo "Documented next steps:"
        echo '  python3 "80 Build/validator.py" --source-only &&'
        echo '  python3 "80 Build/build.py" &&'
        echo '  python3 "80 Build/validator.py"'
        spreadsheet_notice || exit 1
        exit 0
        ;;
    10)
        echo "PREFLIGHT NOTICE: Intentional local edits may be validated and tested."
        echo "Confirm every listed change belongs to the current work before continuing."
        echo "Documented commands:"
        echo '  python3 "80 Build/validator.py" --source-only &&'
        echo '  python3 "80 Build/build.py" &&'
        echo '  python3 "80 Build/validator.py"'
        spreadsheet_notice || exit 1
        exit 0
        ;;
    20)
        echo "PREFLIGHT NOTICE: Local commits are not yet on the remote."
        echo "You may continue on this Mac, but do not switch Macs until they are pushed."
        spreadsheet_notice || exit 1
        exit 0
        ;;
    30)
        echo "PREFLIGHT BLOCKED: This clone is behind its upstream."
        echo "When the working tree is clean, use: git pull --ff-only"
        exit 1
        ;;
    40)
        echo "PREFLIGHT BLOCKED: Local and remote histories have diverged."
        echo "Manual review is required; no automatic merge will be attempted."
        exit 1
        ;;
    50|51|52|53)
        echo "PREFLIGHT BLOCKED: Repository safety could not be confirmed."
        exit 1
        ;;
    *)
        echo "PREFLIGHT BLOCKED: Unexpected status result $RESULT."
        exit 1
        ;;
esac
