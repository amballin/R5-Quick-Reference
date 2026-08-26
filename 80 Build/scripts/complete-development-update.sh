#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

exec python3 -B "$PROJECT_ROOT/80 Build/application_version.py" \
    --project-root "$PROJECT_ROOT" \
    --complete-update
