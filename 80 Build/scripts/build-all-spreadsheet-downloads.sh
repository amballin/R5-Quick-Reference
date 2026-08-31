#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

force_release_workbooks=false
if [[ "${1:-}" == "--force-release-workbooks" ]]; then
    force_release_workbooks=true
    shift
fi
if (( $# )); then
    echo "Usage: $0 [--force-release-workbooks]" >&2
    exit 2
fi

check_command() {
    local output result
    set +e
    output="$("${@:2}" 2>&1)"
    result=$?
    set -e
    printf -v "$1" '%s' "$output"
    return "$result"
}

verification_message=""
matrix_message=""
setup_message=""
verification_result=0
matrix_result=0
setup_result=0

check_command verification_message python3 "80 Build/verification_status.py" check || verification_result=$?
check_command matrix_message python3 "80 Build/spreadsheet_downloads.py" matrix validate || matrix_result=$?
check_command setup_message python3 "80 Build/spreadsheet_downloads.py" setup validate || setup_result=$?

echo "Derived-artifact diagnostic:"
echo "  Verification: $verification_message"
if [[ "$matrix_result" -eq 0 ]]; then
    echo "  Matrix/settings: current"
else
    echo "  Matrix/settings: $matrix_message"
fi
if [[ "$setup_result" -eq 0 ]]; then
    echo "  Setup: current"
else
    echo "  Setup: $setup_message"
fi

if [[ "$verification_result" -eq 1 || "$verification_result" -eq 3 ]]; then
    echo
    echo "REFRESH BLOCKED: The verification tracker may contain unimported/manual edits." >&2
    echo 'Run: ./80\ Build/scripts/import-verification-status.sh' >&2
    exit 1
fi
if [[ "$verification_result" -ne 0 && "$verification_result" -ne 2 ]]; then
    echo "REFRESH BLOCKED: Verification state could not be determined safely." >&2
    exit 1
fi

rebuilt=false
if [[ "$verification_result" -eq 2 ]]; then
    python3 "80 Build/verification_status.py" build
    rebuilt=true
fi
if [[ "$matrix_result" -ne 0 ]] || "$force_release_workbooks"; then
    python3 "80 Build/spreadsheet_downloads.py" matrix build
    rebuilt=true
fi
if [[ "$setup_result" -ne 0 ]] || "$force_release_workbooks"; then
    python3 "80 Build/spreadsheet_downloads.py" setup build
    rebuilt=true
fi

if "$rebuilt"; then
    if "$force_release_workbooks"; then
        echo "Both release workbook families were force-rebuilt; all spreadsheet-derived artifacts are verified."
    else
        echo "All stale spreadsheet/verification derived artifacts were refreshed and verified."
    fi
else
    echo "All spreadsheet/verification derived artifacts are current; nothing was rebuilt."
fi
