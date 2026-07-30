#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

python3 "80 Build/spreadsheet_downloads.py" matrix build
python3 "80 Build/spreadsheet_downloads.py" setup build

echo "All Excel and Apple Numbers spreadsheet downloads are ready and verified."
