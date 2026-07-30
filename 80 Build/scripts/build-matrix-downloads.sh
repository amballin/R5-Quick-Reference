#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

python3 "80 Build/spreadsheet_downloads.py" matrix build

echo "Excel and Apple Numbers Matrix downloads are ready and verified."
