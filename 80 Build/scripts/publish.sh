#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

candidate="80 Build/.publish_metadata.candidate.yaml"
metadata="80 Build/publish_metadata.yaml"
rm -f "$candidate"

include_png=false
include_settings_downloads=false
while (( $# )); do
  case "$1" in
    --png) include_png=true ;;
    --settings-downloads) include_settings_downloads=true ;;
    *) echo "Usage: $0 [--png] [--settings-downloads]" >&2; exit 2 ;;
  esac
  shift
done

build_args=(--publish)
if "$include_png"; then
  build_args+=(--png)
fi
if "$include_settings_downloads"; then
  python3 "80 Build/settings_downloads.py" validate
  build_args+=(--settings-downloads)
fi
PRS_PUBLISH_AUTHORIZED=1 python3 "80 Build/build.py" "${build_args[@]}"

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
