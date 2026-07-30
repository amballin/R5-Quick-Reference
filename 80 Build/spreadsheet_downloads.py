#!/usr/bin/env python3
"""Generate, convert, verify, migrate, and publish spreadsheet downloads."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from asset_manager import ProjectPaths
from spreadsheet_ooxml import excel_column, worksheet_dimensions
from validators.common import load_yaml_checked


MANIFEST_VERSION = 1
NUMBERS_BUNDLE_IDS = ("com.apple.Numbers", "com.apple.iWork.Numbers")
SUPPORTED_TARGETS = ("matrix", "setup")


class SpreadsheetDownloadError(RuntimeError):
    """Raised when a prepared spreadsheet download is missing, stale, or invalid."""


SettingsDownloadError = SpreadsheetDownloadError


def target_spec(paths, target):
    if target not in SUPPORTED_TARGETS:
        raise SpreadsheetDownloadError(f"Unknown spreadsheet target: {target}")
    layouts = load_yaml_checked(paths.spreadsheet_layouts_file) or {}
    layout = ((layouts.get("workbooks") or {}).get(target) or {})
    if not layout:
        raise SpreadsheetDownloadError(f"Spreadsheet layout is missing for target: {target}")
    if target == "matrix":
        return {
            "target": target,
            "layout": layout,
            "xlsx": paths.subject_settings_summary_file,
            "numbers": paths.subject_settings_numbers_file,
            "manifest": paths.subject_settings_download_manifest_file,
        }
    return {
        "target": target,
        "layout": layout,
        "xlsx": paths.setup_tracker_file,
        "numbers": paths.setup_tracker_numbers_file,
        "manifest": paths.setup_tracker_download_manifest_file,
    }


def download_catalog(paths, targets=SUPPORTED_TARGETS):
    catalog = []
    for target in targets:
        spec = target_spec(paths, target)
        catalog.append(
            {
                "target": target,
                "title": spec["layout"]["web_title"],
                "xlsx_name": spec["layout"]["xlsx_name"],
                "numbers_name": spec["layout"]["numbers_name"],
            }
        )
    return catalog


def generate_excel(paths, target, output_path=None, migration_source=None):
    if target == "matrix":
        if output_path or migration_source:
            raise SpreadsheetDownloadError("Matrix generation does not support migration output.")
        from subject_settings_matrix import generate_subject_settings_matrix

        return generate_subject_settings_matrix(paths)
    from camera_setup_tracker import generate_camera_setup_tracker

    return generate_camera_setup_tracker(
        paths,
        output_path=output_path,
        migration_source=migration_source,
    )


def build_spreadsheet_download(paths, target):
    generate_excel(paths, target)
    convert_numbers_automatically(paths, target)
    finalize_numbers_conversion(paths, target)
    verify_prepared_download(paths, target)


def prepare_numbers_conversion(paths, target, launch_numbers=True):
    spec = target_spec(paths, target)
    xlsx = spec["xlsx"]
    if not xlsx.is_file():
        raise SpreadsheetDownloadError(f"Excel workbook is missing: {xlsx}")
    spec["manifest"].unlink(missing_ok=True)
    print(f"Excel {target} workbook is ready.")
    print(f"Open in Numbers: {xlsx}")
    print(f"Save the converted Numbers document as: {spec['numbers']}")
    print(f"Then run the {target} preparation script with --verify.")
    if launch_numbers:
        _open_in_numbers(xlsx)
    return spec


def convert_numbers_automatically(paths, target, xlsx_path=None, numbers_path=None):
    spec = target_spec(paths, target)
    xlsx = Path(xlsx_path or spec["xlsx"])
    numbers = Path(numbers_path or spec["numbers"])
    if not xlsx.is_file():
        raise SpreadsheetDownloadError(f"Excel workbook is missing: {xlsx}")
    if xlsx == spec["xlsx"] and numbers == spec["numbers"]:
        spec["manifest"].unlink(missing_ok=True)
    numbers.parent.mkdir(parents=True, exist_ok=True)
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
            print(f"Excel {target} workbook converted automatically: {numbers}")
            return numbers
        errors.append(result.stderr.strip())
    temporary.unlink(missing_ok=True)
    detail = next((item for item in errors if item), "Apple Numbers was not found.")
    raise SpreadsheetDownloadError(f"Could not convert the {target} workbook: {detail}")


def finalize_numbers_conversion(paths, target, numbers_path=None):
    spec = target_spec(paths, target)
    numbers = Path(numbers_path or spec["numbers"])
    if not numbers.is_file():
        raise SpreadsheetDownloadError(f"Numbers conversion is missing: {numbers}")
    if target == "matrix":
        matrix_rows, matrix_columns = worksheet_dimensions(
            spec["xlsx"],
            spec["layout"]["worksheet"],
        )
        expected_rows = matrix_rows - spec["layout"]["excel"]["import_only_rows"]
        script = _matrix_finalize_script(paths, numbers, expected_rows, matrix_columns)
        expected = f"{expected_rows}, {matrix_columns}, 1, true, 3, true"
    else:
        expected_rows = 1 + len(
            (load_yaml_checked(paths.verification_tracker_source_file) or {}).get("tests") or []
        )
        script = _setup_finalize_script(paths, numbers)
        expected = f"{expected_rows}, 18, 1, true, 1, true, Dashboard"
    errors = []
    for bundle_id in NUMBERS_BUNDLE_IDS:
        result = subprocess.run(
            ["osascript", "-e", script.replace("__BUNDLE_ID__", bundle_id)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            if result.stdout.strip() != expected:
                raise SpreadsheetDownloadError(
                    f"Numbers returned unexpected finalized {target} properties: "
                    f"{result.stdout.strip()}"
                )
            print(f"Numbers {target} conversion finalized with native frozen headers.")
            return numbers
        errors.append(result.stderr.strip())
    detail = next((item for item in errors if item), "Apple Numbers was not found.")
    raise SpreadsheetDownloadError(f"Could not finalize the {target} conversion: {detail}")


def verify_prepared_download(paths, target, write_manifest=True):
    spec = target_spec(paths, target)
    for path in (spec["xlsx"], spec["numbers"]):
        if not path.is_file():
            raise SpreadsheetDownloadError(f"Prepared download is missing: {path}")
        if path.stat().st_size == 0:
            raise SpreadsheetDownloadError(f"Prepared download is empty: {path}")
    if spec["numbers"].stat().st_mtime_ns < spec["xlsx"].stat().st_mtime_ns:
        raise SpreadsheetDownloadError(
            f"The {target} Numbers document is older than its Excel source."
        )
    payload = {
        "version": MANIFEST_VERSION,
        "target": target,
        "prepared": datetime.now().astimezone().isoformat(),
        "xlsx": {
            "name": spec["xlsx"].name,
            "sha256": _sha256(spec["xlsx"]),
        },
        "numbers": {
            "name": spec["numbers"].name,
            "sha256": _sha256(spec["numbers"]),
        },
    }
    if write_manifest:
        spec["manifest"].parent.mkdir(parents=True, exist_ok=True)
        spec["manifest"].write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Prepared {target} downloads verified: {spec['manifest']}")
    return payload


def validate_download_manifest(paths, target="matrix"):
    spec = target_spec(paths, target)
    manifest = spec["manifest"]
    if not manifest.is_file():
        raise SpreadsheetDownloadError(
            f"Prepared {target} manifest is missing. Run its build-downloads script first."
        )
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpreadsheetDownloadError(f"Could not read {manifest}: {exc}") from exc
    if payload.get("version") != MANIFEST_VERSION or payload.get("target") != target:
        raise SpreadsheetDownloadError(f"Unsupported prepared-download manifest: {manifest}")
    for key in ("xlsx", "numbers"):
        path = spec[key]
        entry = payload.get(key)
        if not isinstance(entry, dict) or entry.get("name") != path.name:
            raise SpreadsheetDownloadError(f"Invalid {key} entry in {manifest}")
        if not path.is_file() or entry.get("sha256") != _sha256(path):
            raise SpreadsheetDownloadError(f"Prepared {target} {key} file changed: {path}")
    verify_prepared_download(paths, target, write_manifest=False)
    return payload


def validate_download_manifests(paths, targets):
    return {target: validate_download_manifest(paths, target) for target in targets}


def copy_prepared_downloads(paths, target_dir, targets=("matrix",)):
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for target in targets:
        validate_download_manifest(paths, target)
        spec = target_spec(paths, target)
        for source, name in (
            (spec["xlsx"], spec["layout"]["xlsx_name"]),
            (spec["numbers"], spec["layout"]["numbers_name"]),
        ):
            destination = target_dir / name
            shutil.copy2(source, destination)
            copied.append(destination)
    return copied


def migrate_setup_working_copy(paths, source_path):
    source_path = Path(source_path).expanduser().resolve()
    if not source_path.is_file():
        raise SpreadsheetDownloadError(f"Migration source is missing: {source_path}")
    paths.verification_working_dir.mkdir(parents=True, exist_ok=True)
    generate_excel(
        paths,
        "setup",
        output_path=paths.setup_tracker_working_file,
        migration_source=source_path,
    )
    convert_numbers_automatically(
        paths,
        "setup",
        xlsx_path=paths.setup_tracker_working_file,
        numbers_path=paths.setup_tracker_working_numbers_file,
    )
    finalize_numbers_conversion(
        paths,
        "setup",
        numbers_path=paths.setup_tracker_working_numbers_file,
    )
    print(f"Migrated local working copy: {paths.setup_tracker_working_numbers_file}")
    return {
        "xlsx": paths.setup_tracker_working_file,
        "numbers": paths.setup_tracker_working_numbers_file,
    }


def _matrix_finalize_script(paths, numbers, expected_rows, expected_columns):
    spec = target_spec(paths, "matrix")
    layout = spec["layout"]
    quoted_path = json.dumps(str(numbers))
    imported_rows = expected_rows + layout["excel"]["import_only_rows"]
    return f"""
tell application id "__BUNDLE_ID__"
    activate
    open POSIX file {quoted_path}
    set targetDocument to front document
    tell sheet 1 of targetDocument
        if (count of images) is not 1 then error "Expected one removable banner image."
        tell table 1
            if column count is {expected_columns + 1} then delete column {expected_columns + 1}
            if row count is {imported_rows + 1} then delete row {imported_rows + 1}
            if column count is not {expected_columns} then error "Unexpected Matrix column count."
            if row count is {imported_rows} and header row count is 0 then
                repeat {layout["excel"]["import_only_rows"]} times
                    delete row 1
                end repeat
            else if row count is not {expected_rows} then
                error "Unexpected Matrix row count."
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
            set font name of range "A2:A{expected_rows}" to normalFont
            set alignment of range "A2:A{expected_rows}" to left
            set font name of range "B2:B{expected_rows}" to boldFont
            set alignment of range "B2:B{expected_rows}" to center
            set font name of range "C2:C{expected_rows}" to boldFont
            set alignment of range "C2:C{expected_rows}" to right
            set font name of range "A1:{excel_column(expected_columns)}1" to boldFont
            set position to {{0, 110}}
        end tell
    end tell
    save targetDocument
    tell table 1 of sheet 1 of targetDocument to return ¬
        {{row count, column count, header row count, header rows frozen, ¬
            header column count, header columns frozen}}
end tell
"""


def _setup_finalize_script(paths, numbers):
    spec = target_spec(paths, "setup")
    layout = spec["layout"]
    checklist = layout["sheets"]["checklist"]
    alignment = checklist.get("banner_alignment") or {}
    left_px = alignment.get("left_px", 0)
    table_top_px = alignment.get("numbers_table_top_px", 110)
    quoted_path = json.dumps(str(numbers))
    expected_rows = 1 + len((load_yaml_checked(paths.verification_tracker_source_file) or {}).get("tests") or [])
    imported_rows = expected_rows + checklist["excel"]["import_only_rows"]
    return f"""
tell application id "__BUNDLE_ID__"
    activate
    open POSIX file {quoted_path}
    set targetDocument to front document
    tell sheet {json.dumps(checklist["name"])} of targetDocument
        if (count of images) is not 1 then error "Expected one removable Checklist banner image."
        set position of image 1 to {{{left_px}, 0}}
        tell table 1
            if column count is 19 then delete column 19
            if row count is {imported_rows + 1} then delete row {imported_rows + 1}
            if column count is not 18 then error "Expected 18 Setup Checklist columns."
            if row count is {imported_rows} and header row count is 0 then
                repeat {checklist["excel"]["import_only_rows"]} times
                    delete row 1
                end repeat
            else if row count is not {expected_rows} then
                error "Unexpected Setup Checklist row count."
            end if
            set normalFont to font name of cell "A2"
            set boldFont to font name of cell "A1"
            set header row count to 1
            set header rows frozen to true
            set header column count to 1
            set header columns frozen to true
            set width of column "A" to 96
            set alignment of range "F2:F{expected_rows}" to center
            set font name of range "G2:G{expected_rows}" to boldFont
            set alignment of range "G2:G{expected_rows}" to center
            set font name of range "A1:R1" to boldFont
            set position to {{{left_px}, {table_top_px}}}
        end tell
    end tell
    tell table 1 of sheet {json.dumps(layout["sheets"]["registration"]["name"])} of targetDocument
        if column count is 14 then delete column 14
        if row count is 22 then delete row 22
        set header row count to 4
        set header rows frozen to true
        set header column count to 1
        set header columns frozen to true
        if header row count is not 4 or header rows frozen is not true or ¬
            header column count is not 1 or header columns frozen is not true then
            error "C1-C3 Registration headers were not frozen."
        end if
    end tell
    tell table 1 of sheet {json.dumps(layout["sheets"]["sessions"]["name"])} of targetDocument
        if column count is 13 then delete column 13
        if row count is 25 then delete row 25
    end tell
    tell table 1 of sheet {json.dumps(layout["sheets"]["lists"]["name"])} of targetDocument
        if column count is 5 then delete column 5
    end tell
    tell table 1 of sheet {json.dumps(layout["sheets"]["menu"]["name"])} of targetDocument
        if column count is 6 then delete column 6
        if row count is {expected_rows + 1} then delete row {expected_rows + 1}
        set header row count to 1
        set header rows frozen to true
        set header column count to 1
        set header columns frozen to true
    end tell
    set active sheet of targetDocument to sheet {json.dumps(layout["sheets"]["dashboard"]["name"])} of targetDocument
    save targetDocument
    tell table 1 of sheet {json.dumps(checklist["name"])} of targetDocument to return ¬
        {{row count, column count, header row count, header rows frozen, ¬
            header column count, header columns frozen, name of active sheet of targetDocument}}
end tell
"""


def _open_in_numbers(xlsx):
    errors = []
    for bundle_id in NUMBERS_BUNDLE_IDS:
        result = subprocess.run(
            ["open", "-b", bundle_id, str(xlsx)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("Numbers was opened with the current Excel workbook.")
            return
        errors.append(result.stderr.strip())
    detail = next((item for item in errors if item), "Apple Numbers was not found.")
    raise SpreadsheetDownloadError(f"Could not open Numbers: {detail}")


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare spreadsheet downloads.")
    parser.add_argument("target", choices=SUPPORTED_TARGETS)
    parser.add_argument(
        "action",
        choices=("build", "generate", "prepare", "convert", "finalize", "verify", "validate", "migrate"),
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--no-launch", action="store_true")
    parser.add_argument("--source")
    return parser.parse_args()


def main():
    args = parse_args()
    paths = ProjectPaths(args.root)
    try:
        if args.action == "build":
            build_spreadsheet_download(paths, args.target)
        elif args.action == "generate":
            generate_excel(paths, args.target)
        elif args.action == "prepare":
            prepare_numbers_conversion(paths, args.target, launch_numbers=not args.no_launch)
        elif args.action == "convert":
            convert_numbers_automatically(paths, args.target)
            finalize_numbers_conversion(paths, args.target)
            verify_prepared_download(paths, args.target)
        elif args.action == "finalize":
            finalize_numbers_conversion(paths, args.target)
        elif args.action == "verify":
            verify_prepared_download(paths, args.target)
        elif args.action == "validate":
            validate_download_manifest(paths, args.target)
            print(f"Prepared {args.target} manifest is valid.")
        elif args.action == "migrate":
            if args.target != "setup" or not args.source:
                raise SpreadsheetDownloadError("Setup migration requires --source <earlier.xlsx>.")
            migrate_setup_working_copy(paths, args.source)
    except SpreadsheetDownloadError as exc:
        print(f"Spreadsheet preparation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
