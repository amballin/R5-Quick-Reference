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
from numbers_automation import (
    NumbersAutomationError,
    open_numbers_document,
    run_numbers_applescript,
)
from spreadsheet_ooxml import (
    border_color_attributes,
    excel_column,
    worksheet_dimensions,
)
from spreadsheet_revisions import source_fingerprint, spreadsheet_build_id, workbook_revision
from validators.common import load_yaml_checked


MANIFEST_VERSION = 2
PUBLISHED_MANIFEST_VERSION = 1
SUPPORTED_TARGETS = ("matrix", "setup")
REFRESH_COMMAND = r"./80\ Build/scripts/build-all-spreadsheet-downloads.sh"


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
            "shared": layouts.get("shared") or {},
            "xlsx": paths.subject_settings_summary_file,
            "numbers": paths.subject_settings_numbers_file,
            "manifest": paths.subject_settings_download_manifest_file,
        }
    return {
        "target": target,
        "layout": layout,
        "shared": layouts.get("shared") or {},
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
                "build_id": spreadsheet_build_id(paths, target),
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
    repeat with documentIndex from (count documents) to 1 by -1
        set openDocument to document documentIndex
        if name of openDocument starts with {document_name} then
            close openDocument saving no
        end if
    end repeat
    set sourceDocument to open POSIX file {source_path}
    save sourceDocument in POSIX file {target_path}
    close sourceDocument saving yes
end tell
"""
    try:
        run_numbers_applescript(
            apple_script,
            f"convert the {target} workbook",
            success=lambda _result: temporary.is_file() and temporary.stat().st_size > 0,
        )
    except NumbersAutomationError as exc:
        temporary.unlink(missing_ok=True)
        raise SpreadsheetDownloadError(str(exc)) from exc
    numbers.unlink(missing_ok=True)
    temporary.replace(numbers)
    print(f"Excel {target} workbook converted automatically: {numbers}")
    return numbers


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
        defaults_layout = spec["layout"]["registered_profiles"]["defaults_sheet"]
        defaults_rows, defaults_columns = worksheet_dimensions(
            spec["xlsx"],
            defaults_layout["worksheet"],
        )
        expected_rows = matrix_rows - spec["layout"]["excel"]["import_only_rows"]
        script = _matrix_finalize_script(
            paths,
            numbers,
            expected_rows,
            matrix_columns,
            defaults_rows,
            defaults_columns,
        )
        numbers_layout = spec["layout"]["numbers"]
        defaults_numbers_layout = defaults_layout["numbers"]
        expected = (
            f"{expected_rows}, {matrix_columns}, {numbers_layout['header_rows']}, true, "
            f"{numbers_layout['header_columns']}, true, {defaults_rows}, {defaults_columns}, "
            f"{defaults_numbers_layout['header_rows']}, true, "
            f"{defaults_numbers_layout['header_columns']}, true"
        )
    else:
        expected_rows = 1 + len(
            (load_yaml_checked(paths.verification_tracker_source_file) or {}).get("tests") or []
        )
        script = _setup_finalize_script(paths, numbers)
        expected = f"{expected_rows}, 18, 1, true, 1, true, Dashboard"
    try:
        result, _application = run_numbers_applescript(
            script,
            f"finalize the {target} conversion",
            success=lambda candidate: candidate.stdout.strip() == expected,
        )
    except NumbersAutomationError as exc:
        raise SpreadsheetDownloadError(str(exc)) from exc
    if result.stdout.strip() != expected:
        raise SpreadsheetDownloadError(
            f"Numbers returned unexpected finalized {target} properties: "
            f"{result.stdout.strip()}"
        )
    print(f"Numbers {target} conversion finalized with native frozen headers.")
    return numbers


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
    if target == "setup":
        border_colors = border_color_attributes(spec["xlsx"])
        expected_rgb = (
            ((spec["shared"].get("colors") or {}))
            .get("blue", "")
            .replace("#", "")
            .upper()
        )
        expected_rgb = f"FF{expected_rgb}"
        if not border_colors or any(
            color.get("rgb") != expected_rgb or "indexed" in color
            for color in border_colors
        ):
            raise SpreadsheetDownloadError(
                "The setup workbook borders are not stored as unambiguous RGB blue; "
                "Apple Numbers may display a conflicting indexed color."
            )
    payload = {
        "version": MANIFEST_VERSION,
        "target": target,
        "prepared": datetime.now().astimezone().isoformat(),
        "workbook_revision": workbook_revision(paths, target),
        "source_fingerprint": source_fingerprint(paths, target),
        "build_id": spreadsheet_build_id(paths, target),
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
    if payload.get("workbook_revision") != workbook_revision(paths, target):
        raise SpreadsheetDownloadError(
            f"Prepared {target} workbook revision is stale. Rebuild its downloads."
        )
    if payload.get("source_fingerprint") != source_fingerprint(paths, target):
        raise SpreadsheetDownloadError(
            f"Prepared {target} source inputs changed. Rebuild its downloads."
        )
    if payload.get("build_id") != spreadsheet_build_id(paths, target):
        raise SpreadsheetDownloadError(
            f"Prepared {target} spreadsheet build ID is stale. Rebuild its downloads."
        )
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
    payloads = {}
    issues = {}
    for target in targets:
        try:
            payloads[target] = validate_download_manifest(paths, target)
        except SpreadsheetDownloadError as exc:
            issues[target] = str(exc)
    if issues:
        raise SpreadsheetDownloadError(format_refresh_issues(issues))
    return payloads


def derived_download_issues(paths, targets=SUPPORTED_TARGETS):
    """Return every stale local or published spreadsheet family requiring refresh."""
    issues = {}
    try:
        published = _published_release_from_head(paths)
    except SpreadsheetDownloadError as exc:
        published = {"targets": {}}
        published_error = str(exc)
    else:
        published_error = None
    published_targets = published.get("targets") or {}

    for target in targets:
        spec = target_spec(paths, target)
        local_artifacts = (spec["manifest"], spec["xlsx"], spec["numbers"])
        if any(path.exists() for path in local_artifacts):
            try:
                validate_download_manifest(paths, target)
            except SpreadsheetDownloadError as exc:
                issues[target] = str(exc)
            continue
        prior = published_targets.get(target)
        if prior:
            if prior.get("source_fingerprint") != source_fingerprint(paths, target):
                issues[target] = "Published downloads no longer match current source inputs."
            elif prior.get("workbook_revision") != workbook_revision(paths, target):
                issues[target] = "Published workbook revision is outdated."
        elif published_error:
            issues[target] = published_error
    return issues


def format_refresh_issues(issues):
    lines = ["Stale spreadsheet-derived artifacts were detected:"]
    for target in SUPPORTED_TARGETS:
        if target in issues:
            label = "Matrix/settings" if target == "matrix" else "Setup"
            lines.append(f"  - {label}: {issues[target]}")
    lines.append(f"Run: {REFRESH_COMMAND}")
    return "\n".join(lines)


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


def prepare_spreadsheet_release(
    paths,
    target_dir,
    replace_targets=(),
    preserve_existing=False,
):
    """Copy replacement downloads and safely preserve compatible published downloads."""
    target_dir = Path(target_dir)
    replace_targets = tuple(dict.fromkeys(replace_targets))
    unknown = sorted(set(replace_targets) - set(SUPPORTED_TARGETS))
    if unknown:
        raise SpreadsheetDownloadError(f"Unknown spreadsheet release targets: {unknown}")
    needs_existing = preserve_existing and set(replace_targets) != set(SUPPORTED_TARGETS)
    existing = _published_release_from_head(paths) if needs_existing else {
        "version": PUBLISHED_MANIFEST_VERSION,
        "targets": {},
    }
    existing_targets = existing.get("targets") or {}
    target_dir.mkdir(parents=True, exist_ok=True)
    release = {
        "version": PUBLISHED_MANIFEST_VERSION,
        "generated": datetime.now().astimezone().isoformat(),
        "targets": {},
    }
    copied = []
    for target in SUPPORTED_TARGETS:
        if target in replace_targets:
            local = validate_download_manifest(paths, target)
            spec = target_spec(paths, target)
            entry = {
                "workbook_revision": local["workbook_revision"],
                "source_fingerprint": local["source_fingerprint"],
                "build_id": local["build_id"],
                "prepared": local["prepared"],
                "files": {},
            }
            for key in ("xlsx", "numbers"):
                source = spec[key]
                name = spec["layout"][f"{key}_name"]
                destination = target_dir / name
                shutil.copy2(source, destination)
                copied.append(destination)
                entry["files"][key] = {
                    "name": name,
                    "sha256": _sha256(destination),
                }
            release["targets"][target] = entry
            continue

        prior = existing_targets.get(target)
        if not prior:
            continue
        current_fingerprint = source_fingerprint(paths, target)
        if prior.get("source_fingerprint") != current_fingerprint:
            raise SpreadsheetDownloadError(
                f"Published {target} downloads no longer match their source inputs. "
                f"Rebuild them or publish with --remove-spreadsheet-downloads."
            )
        if prior.get("workbook_revision") != workbook_revision(paths, target):
            raise SpreadsheetDownloadError(
                f"Published {target} workbook revision is outdated. "
                f"Rebuild it or publish with --remove-spreadsheet-downloads."
            )
        expected_build_id = spreadsheet_build_id(paths, target)
        if prior.get("build_id") not in {None, expected_build_id}:
            raise SpreadsheetDownloadError(
                f"Published {target} spreadsheet build ID is outdated. "
                f"Rebuild it or publish with --remove-spreadsheet-downloads."
            )
        preserved["build_id"] = expected_build_id
        preserved = deepcopy_json(prior)
        for key in ("xlsx", "numbers"):
            file_entry = (preserved.get("files") or {}).get(key) or {}
            name = file_entry.get("name")
            expected_hash = file_entry.get("sha256")
            if not name or not expected_hash:
                raise SpreadsheetDownloadError(
                    f"Published {target} release metadata is incomplete."
                )
            content = _git_show(paths, f"docs/downloads/{name}")
            actual_hash = hashlib.sha256(content).hexdigest()
            if actual_hash != expected_hash:
                raise SpreadsheetDownloadError(
                    f"Published {target} {key} hash does not match its release metadata."
                )
            destination = target_dir / name
            destination.write_bytes(content)
            copied.append(destination)
        release["targets"][target] = preserved

    if release["targets"]:
        manifest = target_dir / "spreadsheet-releases.json"
        manifest.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")
        copied.append(manifest)
    elif target_dir.exists():
        target_dir.rmdir()
    return {
        "files": copied,
        "targets": tuple(
            target for target in SUPPORTED_TARGETS if target in release["targets"]
        ),
        "manifest": release,
    }


def validate_published_release(paths, root=None):
    root = Path(root or paths.merged_build_output_dir)
    manifest_path = root / "downloads" / "spreadsheet-releases.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpreadsheetDownloadError(f"Published release manifest is invalid: {exc}") from exc
    if payload.get("version") != PUBLISHED_MANIFEST_VERSION:
        raise SpreadsheetDownloadError("Published spreadsheet release manifest version is unsupported.")
    for target, entry in (payload.get("targets") or {}).items():
        if target not in SUPPORTED_TARGETS:
            raise SpreadsheetDownloadError(f"Unknown published spreadsheet target: {target}")
        if entry.get("source_fingerprint") != source_fingerprint(paths, target):
            raise SpreadsheetDownloadError(f"Published {target} release has a stale source fingerprint.")
        if entry.get("build_id") != spreadsheet_build_id(paths, target):
            raise SpreadsheetDownloadError(f"Published {target} release has a stale spreadsheet build ID.")
        for key in ("xlsx", "numbers"):
            file_entry = (entry.get("files") or {}).get(key) or {}
            path = root / "downloads" / str(file_entry.get("name") or "")
            if not path.is_file() or _sha256(path) != file_entry.get("sha256"):
                raise SpreadsheetDownloadError(f"Published {target} {key} file is missing or changed.")
    return payload


def _published_release_from_head(paths):
    try:
        content = _git_show(paths, "docs/downloads/spreadsheet-releases.json")
    except SpreadsheetDownloadError:
        legacy = []
        for target in SUPPORTED_TARGETS:
            spec = target_spec(paths, target)
            for key in ("xlsx", "numbers"):
                name = spec["layout"][f"{key}_name"]
                if _git_path_exists(paths, f"docs/downloads/{name}"):
                    legacy.append(name)
        if legacy:
            raise SpreadsheetDownloadError(
                "Published spreadsheet downloads predate safe release metadata. "
                "Rebuild the affected downloads before the next publish."
            )
        return {"version": PUBLISHED_MANIFEST_VERSION, "targets": {}}
    try:
        payload = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SpreadsheetDownloadError(f"Published spreadsheet metadata is invalid: {exc}") from exc
    if payload.get("version") != PUBLISHED_MANIFEST_VERSION:
        raise SpreadsheetDownloadError("Published spreadsheet metadata version is unsupported.")
    return payload


def _git_show(paths, repository_path):
    result = subprocess.run(
        ["git", "show", f"HEAD:{repository_path}"],
        cwd=paths.root,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SpreadsheetDownloadError(f"Published Git file is missing: {repository_path}")
    return result.stdout


def _git_path_exists(paths, repository_path):
    result = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{repository_path}"],
        cwd=paths.root,
        capture_output=True,
    )
    return result.returncode == 0


def deepcopy_json(value):
    return json.loads(json.dumps(value))


def migrate_setup_working_copy(paths, source_path):
    source_path = Path(source_path).expanduser().resolve()
    if not source_path.is_file():
        raise SpreadsheetDownloadError(f"Migration source is missing: {source_path}")
    from verification_status import build_working_copy, import_workbook_status

    import_workbook_status(paths, source_path)
    build_working_copy(paths)
    print(f"Migrated status and rebuilt local working copy: {paths.setup_tracker_working_numbers_file}")
    return {
        "xlsx": paths.setup_tracker_working_file,
        "numbers": paths.setup_tracker_working_numbers_file,
    }


def _matrix_finalize_script(
    paths,
    numbers,
    expected_rows,
    expected_columns,
    defaults_expected_rows,
    defaults_columns,
):
    spec = target_spec(paths, "matrix")
    layout = spec["layout"]
    quoted_path = json.dumps(str(numbers))
    imported_rows = expected_rows + layout["excel"]["import_only_rows"]
    defaults = layout["registered_profiles"]["defaults_sheet"]
    first_data_row = layout["numbers"]["header_rows"] + 1
    last_visible_defaults_column = 1 + len(layout["registered_profiles"]["keys"])
    return f"""
tell application id "__BUNDLE_ID__"
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
            set normalFont to font name of cell "A{first_data_row}"
            set boldFont to font name of cell "C{first_data_row}"
            set header row count to {layout["numbers"]["header_rows"]}
            set header rows frozen to true
            set header column count to {layout["numbers"]["header_columns"]}
            set header columns frozen to true
            set width of column "A" to 85
            set width of column "B" to 80
            set width of column "C" to 80
            set font name of range "A{first_data_row}:A{expected_rows}" to normalFont
            set alignment of range "A{first_data_row}:A{expected_rows}" to left
            set font name of range "B{first_data_row}:B{expected_rows}" to boldFont
            set alignment of range "B{first_data_row}:B{expected_rows}" to center
            set font name of range "C{first_data_row}:C{expected_rows}" to boldFont
            set alignment of range "C{first_data_row}:C{expected_rows}" to right
            set font name of range "A{layout['numbers']['header_rows']}:{excel_column(expected_columns)}{layout['numbers']['header_rows']}" to boldFont
            set position to {{0, 110}}
        end tell
    end tell
    tell sheet {json.dumps(defaults["worksheet"])} of targetDocument
        tell table 1
            if column count is {defaults_columns + 1} then delete column {defaults_columns + 1}
            if row count is {defaults_expected_rows + 1} then delete row {defaults_expected_rows + 1}
            if column count is not {defaults_columns} then error "Unexpected C1-C3 Defaults column count."
            if row count is not {defaults_expected_rows} then error "Unexpected C1-C3 Defaults row count."
            set header row count to {defaults["numbers"]["header_rows"]}
            set header rows frozen to true
            set header column count to {defaults["numbers"]["header_columns"]}
            set header columns frozen to true
            set width of column "A" to 160
            repeat with columnIndex from 2 to {last_visible_defaults_column}
                set width of column columnIndex to 130
            end repeat
            repeat with columnIndex from {last_visible_defaults_column + 1} to {defaults_columns}
                set width of column columnIndex to 2
            end repeat
        end tell
    end tell
    save targetDocument
    tell table 1 of sheet 1 of targetDocument to set mainProperties to ¬
        {{row count, column count, header row count, header rows frozen, ¬
            header column count, header columns frozen}}
    tell table 1 of sheet {json.dumps(defaults["worksheet"])} of targetDocument to set defaultsProperties to ¬
        {{row count, column count, header row count, header rows frozen, ¬
            header column count, header columns frozen}}
    set finalizedProperties to mainProperties & defaultsProperties
    close targetDocument saving yes
    return finalizedProperties
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
    tell table 1 of sheet {json.dumps(checklist["name"])} of targetDocument to set finalizedProperties to ¬
        {{row count, column count, header row count, header rows frozen, ¬
            header column count, header columns frozen, name of active sheet of targetDocument}}
    close targetDocument saving yes
    return finalizedProperties
end tell
"""


def _open_in_numbers(xlsx):
    try:
        open_numbers_document(xlsx)
    except NumbersAutomationError as exc:
        raise SpreadsheetDownloadError(str(exc)) from exc
    print("Numbers was opened with the current Excel workbook.")


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare spreadsheet downloads.")
    parser.add_argument("target", choices=SUPPORTED_TARGETS + ("all",))
    parser.add_argument(
        "action",
        choices=("build", "generate", "prepare", "convert", "finalize", "verify", "validate", "migrate", "diagnose"),
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--no-launch", action="store_true")
    parser.add_argument("--source")
    return parser.parse_args()


def main():
    args = parse_args()
    paths = ProjectPaths(args.root)
    try:
        if args.target == "all":
            if args.action == "diagnose":
                issues = derived_download_issues(paths)
                if issues:
                    print(format_refresh_issues(issues))
                    return 2
                print("Matrix/settings and Setup spreadsheet-derived artifacts are current.")
                return 0
            if args.action == "validate":
                validate_download_manifests(paths, SUPPORTED_TARGETS)
                print("Prepared Matrix/settings and Setup manifests are valid.")
                return 0
            raise SpreadsheetDownloadError("The all target supports only diagnose or validate.")
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
        if args.action == "validate" and REFRESH_COMMAND not in str(exc):
            print(f"Run: {REFRESH_COMMAND}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
