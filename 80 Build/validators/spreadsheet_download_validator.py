from asset_manager import ProjectPaths
from spreadsheet_downloads import (
    SUPPORTED_TARGETS,
    SpreadsheetDownloadError,
    target_spec,
    validate_download_manifest,
    validate_published_release,
)
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
        try:
            validate_published_release(paths)
        except SpreadsheetDownloadError as exc:
            issues.append(error("spreadsheet_downloads", downloads_dir, str(exc)))
    docs_manifest = paths.published_spreadsheet_manifest_file
    if docs_manifest.exists():
        try:
            validate_published_release(paths, root=paths.pages_output_dir)
        except SpreadsheetDownloadError as exc:
            issues.append(error("spreadsheet_downloads", docs_manifest, str(exc)))
    return issues
