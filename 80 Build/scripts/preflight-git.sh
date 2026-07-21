#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
STATUS_SCRIPT="$SCRIPT_DIR/git-status-report.sh"

"$STATUS_SCRIPT"
RESULT=$?

echo
case "$RESULT" in
    0)
        echo "PREFLIGHT PASSED: Repository is clean and synchronized."
        echo "Documented next steps:"
        echo '  python3 "80 Build/validator.py"'
        echo '  python3 "80 Build/build.py"'
        exit 0
        ;;
    10)
        echo "PREFLIGHT NOTICE: Intentional local edits may be validated and tested."
        echo "Confirm every listed change belongs to the current work before continuing."
        echo "Documented commands:"
        echo '  python3 "80 Build/validator.py"'
        echo '  python3 "80 Build/build.py"'
        exit 0
        ;;
    20)
        echo "PREFLIGHT NOTICE: Local commits are not yet on the remote."
        echo "You may continue on this Mac, but do not switch Macs until they are pushed."
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
