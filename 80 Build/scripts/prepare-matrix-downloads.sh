#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

case "${1:-}" in
  "")
    python3 "80 Build/spreadsheet_downloads.py" matrix generate
    python3 "80 Build/spreadsheet_downloads.py" matrix prepare
    ;;
  --verify)
    python3 "80 Build/spreadsheet_downloads.py" matrix finalize
    python3 "80 Build/spreadsheet_downloads.py" matrix verify
    ;;
  *)
    echo "Usage: $0 [--verify]" >&2
    exit 2
    ;;
esac
