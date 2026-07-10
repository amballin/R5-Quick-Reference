#!/usr/bin/env bash
set -euo pipefail

cd "/Users/andy/Documents/Photography Reference System"

python3 build.py

git add .

if git diff --cached --quiet; then
  echo "No changes to publish."
  exit 0
fi

git commit -m "Update R5 reference"
git push
