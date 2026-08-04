import json

from asset_manager import ProjectPaths
from spreadsheet_downloads import (
    SUPPORTED_TARGETS,
    SpreadsheetDownloadError,
    target_spec,
    validate_download_manifest,
    validate_published_release,
)
from spreadsheet_revisions import source_fingerprint
from .common import error, warning


def validate(root):
    issues = []
    paths = ProjectPaths(root)
    for target in SUPPORTED_TARGETS:
        spec = target_spec(paths, target)
        manifest = spec["manifest"]
        if manifest.exists():
            try:
                validate_download_manifest(paths, target)
            except SpreadsheetDownloadError as exc:
                issues.append(
                    warning(
                        "spreadsheet_downloads",
                        manifest,
                        f"{exc} Rebuild before replacement publication.",
                    )
                )

    downloads_dir = paths.merged_build_output_dir / "downloads"
    if downloads_dir.exists():
        for target in SUPPORTED_TARGETS:
            spec = target_spec(paths, target)
            names = (spec["layout"]["xlsx_name"], spec["layout"]["numbers_name"])
            present = [(downloads_dir / name).exists() for name in names]
            if any(present):
                for name in names:
                    path = downloads_dir / name
                    if not path.is_file() or path.stat().st_size == 0:
                        issues.append(
                            error(
                                "spreadsheet_downloads",
                                path,
                                f"Published {target} download is missing or empty.",
                            )
                        )
        issues.extend(_validate_release(paths, downloads_dir, downloads_dir / "spreadsheet-releases.json"))
    docs_manifest = paths.published_spreadsheet_manifest_file
    if docs_manifest.exists():
        issues.extend(_validate_release(paths, paths.pages_output_dir, docs_manifest))
    return issues


def _validate_release(paths, root, manifest_path):
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    fingerprint_issues = []
    for target, entry in (payload.get("targets") or {}).items():
        if target in SUPPORTED_TARGETS and entry.get("source_fingerprint") != source_fingerprint(paths, target):
            fingerprint_issues.append(
                error(
                    "spreadsheet_downloads",
                    manifest_path,
                    f"Published {target} release has a stale source fingerprint.",
                )
            )
    if fingerprint_issues:
        return fingerprint_issues
    try:
        validate_published_release(paths, root=root)
    except SpreadsheetDownloadError as exc:
        return [error("spreadsheet_downloads", manifest_path, str(exc))]
    return []
