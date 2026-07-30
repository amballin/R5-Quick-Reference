#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/earlier-tracker.xlsx" >&2
  exit 2
fi

python3 "80 Build/spreadsheet_downloads.py" setup migrate --source "$1"
