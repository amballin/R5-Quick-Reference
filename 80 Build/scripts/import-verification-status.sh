#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
python3 "80 Build/verification_status.py" import "$@"
