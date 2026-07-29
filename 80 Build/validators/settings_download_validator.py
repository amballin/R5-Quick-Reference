from asset_manager import ProjectPaths
from settings_downloads import (
    SettingsDownloadError,
    WEB_NUMBERS_NAME,
    WEB_XLSX_NAME,
    validate_download_manifest,
)
from .common import error


def validate(root):
    issues = []
    paths = ProjectPaths(root)
    manifest = paths.subject_settings_download_manifest_file
    if manifest.exists():
        try:
            validate_download_manifest(paths)
        except SettingsDownloadError as exc:
            issues.append(error("settings_downloads", manifest, str(exc)))

    downloads_dir = paths.merged_build_output_dir / "downloads"
    if downloads_dir.exists():
        for name in (WEB_XLSX_NAME, WEB_NUMBERS_NAME):
            path = downloads_dir / name
            if not path.is_file() or path.stat().st_size == 0:
                issues.append(
                    error(
                        "settings_downloads",
                        path,
                        "Published settings download is missing or empty.",
                    )
                )
    return issues
