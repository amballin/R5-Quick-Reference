#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

candidate="80 Build/.publish_metadata.candidate.yaml"
metadata="80 Build/publish_metadata.yaml"
temporary_index=""
publish_succeeded=false

local_workspace_dir() {
  if [[ -n "${PRS_LOCAL_WORKSPACE:-}" ]]; then
    case "$PRS_LOCAL_WORKSPACE" in
      "~") printf '%s\n' "$HOME" ;;
      "~/"*) printf '%s/%s\n' "$HOME" "${PRS_LOCAL_WORKSPACE#~/}" ;;
      /*) printf '%s\n' "$PRS_LOCAL_WORKSPACE" ;;
      *) printf '%s/%s\n' "$PWD" "$PRS_LOCAL_WORKSPACE" ;;
    esac
  else
    printf '%s Local\n' "$PWD"
  fi
}

log_dir="$(local_workspace_dir)/Logs"
mkdir -p "$log_dir"
log_file="$log_dir/publish-$(date '+%Y%m%d-%H%M%S').log"
exec > >(tee -a "$log_file") 2>&1

on_exit() {
  status=$?
  trap - EXIT
  if [[ -n "$temporary_index" ]]; then
    rm -f "$temporary_index"
  fi
  rm -f "$candidate"
  echo
  if "$publish_succeeded"; then
    echo "PUBLICATION COMPLETE AND VERIFIED."
  else
    echo "PUBLICATION DID NOT COMPLETE."
  fi
  echo "Publish log: $log_file"
  exit "$status"
}
trap on_exit EXIT

rm -f "$candidate"
echo "Publication started: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "Publish log: $log_file"

spreadsheet_args=()
remove_spreadsheets=false
major_version=""
while (( $# )); do
  case "$1" in
    --settings-downloads|--matrix-downloads) spreadsheet_args=(--matrix-downloads) ;;
    --setup-downloads) spreadsheet_args=(--setup-downloads) ;;
    --spreadsheet-downloads) spreadsheet_args=(--spreadsheet-downloads) ;;
    --remove-spreadsheet-downloads) remove_spreadsheets=true ;;
    --major-version)
      if (( $# < 2 )) || [[ ! "$2" =~ ^[0-9]+$ ]]; then
        echo "--major-version requires a nonnegative integer." >&2
        exit 2
      fi
      major_version="$2"
      shift
      ;;
    *) echo "Usage: $0 [--major-version N] [--matrix-downloads|--setup-downloads|--spreadsheet-downloads|--remove-spreadsheet-downloads]" >&2; exit 2 ;;
  esac
  shift
done

if "$remove_spreadsheets" && (( ${#spreadsheet_args[@]} )); then
  echo "Removal cannot be combined with spreadsheet replacement options." >&2
  exit 2
fi

build_args=(--publish)
if (( ${#spreadsheet_args[@]} )); then
  case "${spreadsheet_args[0]}" in
    --matrix-downloads)
      python3 "80 Build/spreadsheet_downloads.py" matrix validate
      ;;
    --setup-downloads)
      python3 "80 Build/spreadsheet_downloads.py" setup validate
      ;;
    --spreadsheet-downloads)
      python3 "80 Build/spreadsheet_downloads.py" matrix validate
      python3 "80 Build/spreadsheet_downloads.py" setup validate
      ;;
  esac
  build_args+=("${spreadsheet_args[0]}")
fi
if "$remove_spreadsheets"; then
  build_args+=(--remove-spreadsheet-downloads)
fi
if [[ -n "$major_version" ]]; then
  build_args+=(--major-version "$major_version")
fi
PRS_PUBLISH_AUTHORIZED=1 python3 "80 Build/build.py" "${build_args[@]}"

test -f docs/index.html || { echo "Publish failed: docs/index.html was not generated." >&2; exit 1; }
test -f "$candidate" || { echo "Publish failed: candidate metadata was not generated." >&2; exit 1; }

branch="$(git symbolic-ref --quiet --short HEAD)"
parent="$(git rev-parse HEAD)"
temporary_index="$(mktemp)"
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
unset GIT_INDEX_FILE
mv "$candidate" "$metadata"
git restore --staged --source=HEAD -- "$metadata" docs

verify_args=()
if (( ${#spreadsheet_args[@]} )); then
  case "${spreadsheet_args[0]}" in
    --matrix-downloads) verify_args+=(--require-target matrix) ;;
    --setup-downloads) verify_args+=(--require-target setup) ;;
    --spreadsheet-downloads)
      verify_args+=(--require-target matrix --require-target setup)
      ;;
  esac
elif "$remove_spreadsheets"; then
  verify_args+=(--require-no-spreadsheets)
fi
python3 "80 Build/verify_publication.py" "${verify_args[@]}"

publish_succeeded=true
echo "Website published successfully."
