#!/usr/bin/env python3
"""Prepare and validate downloadable Excel and Apple Numbers settings summaries."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from asset_manager import ProjectPaths


WEB_XLSX_NAME = "Subject Settings Matrix.xlsx"
WEB_NUMBERS_NAME = "Subject Settings Matrix.numbers"
MANIFEST_VERSION = 1
NUMBERS_BUNDLE_IDS = ("com.apple.Numbers", "com.apple.iWork.Numbers")


class SettingsDownloadError(RuntimeError):
    """Raised when the prepared spreadsheet downloads are missing or stale."""


def prepare_numbers_conversion(paths, launch_numbers=True):
    """Invalidate prior readiness and open the current XLSX for manual Numbers conversion."""
    xlsx = paths.subject_settings_summary_file
    numbers = paths.subject_settings_numbers_file
    manifest = paths.subject_settings_download_manifest_file
    if not xlsx.is_file():
        raise SettingsDownloadError(
            f"Excel summary is missing: {xlsx}. Run the settings-summary build first."
        )
    manifest.unlink(missing_ok=True)
    print("Excel summary is ready.")
    print(f"Open in Numbers: {xlsx}")
    print(f"Save the converted Numbers document as: {numbers}")
    print(
        'Then run: ./80\\ Build/scripts/prepare-settings-downloads.sh --verify'
    )
    if launch_numbers:
        launch_error = None
        for bundle_id in NUMBERS_BUNDLE_IDS:
            try:
                subprocess.run(
                    ["open", "-b", bundle_id, str(xlsx)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print("Numbers was opened with the current Excel summary.")
                launch_error = None
                break
            except (OSError, subprocess.CalledProcessError) as exc:
                launch_error = exc
        if launch_error is not None:
            print(
                f"Could not open Apple Numbers automatically ({launch_error}). "
                "Use the paths above for the manual conversion.",
                file=sys.stderr,
            )
    return {"xlsx": xlsx, "numbers": numbers}


def convert_numbers_automatically(paths):
    """Convert the current XLSX to a fresh Numbers document without manual steps."""
    xlsx = paths.subject_settings_summary_file
    numbers = paths.subject_settings_numbers_file
    manifest = paths.subject_settings_download_manifest_file
    if not xlsx.is_file():
        raise SettingsDownloadError(
            f"Excel summary is missing: {xlsx}. Run the settings-summary build first."
        )
    manifest.unlink(missing_ok=True)
    temporary = numbers.with_name(f".{numbers.stem}-converting.numbers")
    temporary.unlink(missing_ok=True)
    source_path = json.dumps(str(xlsx))
    target_path = json.dumps(str(temporary))
    document_name = json.dumps(numbers.stem)
    apple_script = f"""
tell application id "__BUNDLE_ID__"
    repeat with openDocument in documents
        if name of openDocument starts with {document_name} then
            close openDocument saving no
        end if
    end repeat
    set sourceDocument to open POSIX file {source_path}
    save sourceDocument in POSIX file {target_path}
    close sourceDocument saving yes
end tell
"""
    errors = []
    for bundle_id in NUMBERS_BUNDLE_IDS:
        result = subprocess.run(
            ["osascript", "-e", apple_script.replace("__BUNDLE_ID__", bundle_id)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and temporary.is_file() and temporary.stat().st_size:
            numbers.unlink(missing_ok=True)
            temporary.replace(numbers)
            print(f"Excel summary converted automatically: {numbers}")
            return
        errors.append(result.stderr.strip())
    temporary.unlink(missing_ok=True)
    detail = next((item for item in errors if item), "Apple Numbers was not found.")
    raise SettingsDownloadError(f"Could not convert the Excel summary: {detail}")


def generate_excel_summary(paths):
    """Generate only the Excel settings summary without running a website build."""
    from subject_settings_summary import generate_subject_settings_summary

    generate_subject_settings_summary(paths)


def build_settings_downloads(paths):
    """Generate, convert, finalize, and verify both spreadsheet downloads."""
    generate_excel_summary(paths)
    convert_numbers_automatically(paths)
    finalize_numbers_conversion(paths)
    verify_prepared_downloads(paths)


def finalize_numbers_conversion(paths):
    """Convert the saved import into a native Numbers table with a frozen header."""
    numbers = paths.subject_settings_numbers_file
    if not numbers.is_file():
        raise SettingsDownloadError(
            f"Numbers conversion is missing: {numbers}. Save the imported workbook first."
        )
    quoted_path = json.dumps(str(numbers))
    apple_script = f"""
tell application id "__BUNDLE_ID__"
    activate
    open POSIX file {quoted_path}
    set targetDocument to front document
    tell sheet 1 of targetDocument
        if (count of images) is not 1 then error "Expected one removable banner image."
        tell table 1
            if column count is not 17 then error "Expected 17 settings-summary columns."
            if row count is 21 and header row count is 0 then
                repeat 4 times
                    delete row 1
                end repeat
            else if row count is not 17 then
                error "Expected 21 imported rows or 17 finalized rows."
            end if
            set normalFont to font name of cell "A2"
            set boldFont to font name of cell "C2"
            set header row count to 1
            set header rows frozen to true
            set header column count to 3
            set header columns frozen to true
            set width of column "A" to 85
            set width of column "B" to 80
            set width of column "C" to 80
            set font name of range "A2:A17" to normalFont
            set alignment of range "A2:A17" to left
            set font name of range "B2:B17" to boldFont
            set alignment of range "B2:B17" to center
            set font name of range "C2:C17" to boldFont
            set alignment of range "C2:C17" to right
            set font name of range "A1:Q1" to boldFont
            set position to {{0, 110}}
            if width of column "A" is not 85 then error "Column A width was not preserved."
            if width of column "B" is not 80 then error "Column B width was not preserved."
            if width of column "C" is not 80 then error "Column C width was not preserved."
            if font name of cell "A2" is not normalFont or alignment of cell "A2" is not left then
                error "Column A formatting was not preserved."
            end if
            if font name of cell "B2" is not boldFont or alignment of cell "B2" is not center then
                error "Column B formatting was not preserved."
            end if
            if font name of cell "C2" is not boldFont or alignment of cell "C2" is not right then
                error "Column C formatting was not preserved."
            end if
            if font name of cell "A1" is not boldFont or font name of cell "Q1" is not boldFont then
                error "The complete header row was not bold."
            end if
        end tell
    end tell
    save targetDocument
    tell table 1 of sheet 1 of targetDocument to return ¬
        {{row count, column count, header row count, header rows frozen, ¬
            header column count, header columns frozen}}
end tell
"""
    errors = []
    for bundle_id in NUMBERS_BUNDLE_IDS:
        result = subprocess.run(
            ["osascript", "-e", apple_script.replace("__BUNDLE_ID__", bundle_id)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            if result.stdout.strip() != "17, 17, 1, true, 3, true":
                raise SettingsDownloadError(
                    "Numbers returned unexpected finalized table properties: "
                    f"{result.stdout.strip()}"
                )
            print(
                "Numbers conversion finalized: banner separated, native header created, "
                "header row frozen, columns A:C frozen, and A:C formatting enforced."
            )
            return
        errors.append(result.stderr.strip())
    detail = next((item for item in errors if item), "Apple Numbers was not found.")
    raise SettingsDownloadError(f"Could not finalize the Numbers conversion: {detail}")


def verify_prepared_downloads(paths, write_manifest=True):
    """Verify that the Numbers conversion is newer than its Excel source."""
    xlsx = paths.subject_settings_summary_file
    numbers = paths.subject_settings_numbers_file
    for path in (xlsx, numbers):
        if not path.is_file():
            raise SettingsDownloadError(f"Prepared download is missing: {path}")
        if path.stat().st_size == 0:
            raise SettingsDownloadError(f"Prepared download is empty: {path}")
    if numbers.stat().st_mtime_ns < xlsx.stat().st_mtime_ns:
        raise SettingsDownloadError(
            "The Numbers document is older than the Excel summary. "
            "Convert the current Excel summary again before publishing."
        )
    payload = {
        "version": MANIFEST_VERSION,
        "prepared": datetime.now().astimezone().isoformat(),
        "xlsx": {
            "name": xlsx.name,
            "sha256": _sha256(xlsx),
        },
        "numbers": {
            "name": numbers.name,
            "sha256": _sha256(numbers),
        },
    }
    if write_manifest:
        manifest = paths.subject_settings_download_manifest_file
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Prepared settings downloads verified: {manifest}")
    return payload


def validate_download_manifest(paths):
    """Validate the readiness manifest and its exact source-file hashes."""
    manifest = paths.subject_settings_download_manifest_file
    if not manifest.is_file():
        raise SettingsDownloadError(
            "Prepared-download manifest is missing. Run "
            "./80 Build/scripts/prepare-settings-downloads.sh --verify first."
        )
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SettingsDownloadError(f"Could not read {manifest}: {exc}") from exc
    if payload.get("version") != MANIFEST_VERSION:
        raise SettingsDownloadError(f"Unsupported prepared-download manifest: {manifest}")
    expected = {
        "xlsx": paths.subject_settings_summary_file,
        "numbers": paths.subject_settings_numbers_file,
    }
    for key, path in expected.items():
        entry = payload.get(key)
        if not isinstance(entry, dict) or entry.get("name") != path.name:
            raise SettingsDownloadError(f"Invalid {key} entry in {manifest}")
        if not path.is_file() or entry.get("sha256") != _sha256(path):
            raise SettingsDownloadError(
                f"Prepared {key} file changed after verification: {path}"
            )
    verify_prepared_downloads(paths, write_manifest=False)
    return payload


def copy_prepared_downloads(paths, target_dir):
    """Copy verified download files into a generated website directory."""
    validate_download_manifest(paths)
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for source, name in (
        (paths.subject_settings_summary_file, WEB_XLSX_NAME),
        (paths.subject_settings_numbers_file, WEB_NUMBERS_NAME),
    ):
        target = target_dir / name
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare or verify Excel and Apple Numbers website downloads."
    )
    parser.add_argument(
        "action",
        choices=(
            "build",
            "generate",
            "prepare",
            "convert",
            "finalize",
            "verify",
            "validate",
        ),
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--no-launch", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    paths = ProjectPaths(args.root)
    try:
        if args.action == "build":
            build_settings_downloads(paths)
        elif args.action == "generate":
            generate_excel_summary(paths)
        elif args.action == "prepare":
            prepare_numbers_conversion(paths, launch_numbers=not args.no_launch)
        elif args.action == "convert":
            convert_numbers_automatically(paths)
            finalize_numbers_conversion(paths)
            verify_prepared_downloads(paths)
        elif args.action == "finalize":
            finalize_numbers_conversion(paths)
        elif args.action == "verify":
            verify_prepared_downloads(paths)
        else:
            validate_download_manifest(paths)
            print("Prepared settings-download manifest is valid.")
    except SettingsDownloadError as exc:
        print(f"Settings download preparation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
