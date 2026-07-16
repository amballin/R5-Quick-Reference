#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

candidate="80 Build/.publish_metadata.candidate.yaml"
metadata="80 Build/publish_metadata.yaml"
rm -f "$candidate"

PRS_PUBLISH_AUTHORIZED=1 python3 "80 Build/build.py" --publish

test -f docs/index.html || { echo "Publish failed: docs/index.html was not generated." >&2; exit 1; }
test -f "$candidate" || { echo "Publish failed: candidate metadata was not generated." >&2; exit 1; }

branch="$(git symbolic-ref --quiet --short HEAD)"
parent="$(git rev-parse HEAD)"
temporary_index="$(mktemp)"
trap 'rm -f "$temporary_index" "$candidate"' EXIT
rm -f "$temporary_index"

export GIT_INDEX_FILE="$temporary_index"
git read-tree "$parent"
git add docs
metadata_blob="$(git hash-object -w "$candidate")"
git update-index --add --cacheinfo 100644,"$metadata_blob","$metadata"

if git diff-index --cached --quiet "$parent"; then
  echo "Publish failed: the generated site has no changes to deploy." >&2
  exit 1
fi

tree="$(git write-tree)"
commit="$(printf '%s\n' 'Update R5 reference' | git commit-tree "$tree" -p "$parent")"
git push origin "$commit:refs/heads/$branch"
git update-ref "refs/heads/$branch" "$commit" "$parent"
mv "$candidate" "$metadata"
echo "Website published successfully."
