#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

python3 "80 Build/settings_downloads.py" build

echo "Excel and Apple Numbers settings downloads are ready and verified."
