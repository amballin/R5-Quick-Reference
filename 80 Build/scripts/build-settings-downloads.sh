#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "build-settings-downloads.sh is retained as a Matrix compatibility alias."
exec "./80 Build/scripts/build-matrix-downloads.sh"
