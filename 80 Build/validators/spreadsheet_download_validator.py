from asset_manager import ProjectPaths
from spreadsheet_downloads import (
    SUPPORTED_TARGETS,
    SpreadsheetDownloadError,
    target_spec,
    validate_download_manifest,
)
from .common import error


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
                issues.append(error("spreadsheet_downloads", manifest, str(exc)))

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
    return issues
