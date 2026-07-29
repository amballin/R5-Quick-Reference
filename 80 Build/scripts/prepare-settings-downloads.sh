#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

case "${1:-}" in
  "")
    python3 "80 Build/settings_downloads.py" generate
    python3 "80 Build/settings_downloads.py" prepare
    ;;
  --verify)
    python3 "80 Build/settings_downloads.py" finalize
    python3 "80 Build/settings_downloads.py" verify
    ;;
  *)
    echo "Usage: $0 [--verify]" >&2
    exit 2
    ;;
esac
