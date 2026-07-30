#!/usr/bin/env python3
"""Backward-compatible Matrix wrapper for spreadsheet_downloads.py."""

import sys

from spreadsheet_downloads import (
    SettingsDownloadError,
    SpreadsheetDownloadError,
    build_spreadsheet_download,
    convert_numbers_automatically as _convert_numbers_automatically,
    copy_prepared_downloads as _copy_prepared_downloads,
    finalize_numbers_conversion as _finalize_numbers_conversion,
    generate_excel,
    prepare_numbers_conversion as _prepare_numbers_conversion,
    validate_download_manifest as _validate_download_manifest,
    verify_prepared_download as _verify_prepared_download,
)
from spreadsheet_downloads import main as spreadsheet_main

WEB_XLSX_NAME = "Subject Settings Matrix.xlsx"
WEB_NUMBERS_NAME = "Subject Settings Matrix.numbers"


def generate_excel_summary(paths):
    return generate_excel(paths, "matrix")


def build_settings_downloads(paths):
    return build_spreadsheet_download(paths, "matrix")


def convert_numbers_automatically(paths):
    return _convert_numbers_automatically(paths, "matrix")


def prepare_numbers_conversion(paths, launch_numbers=True):
    return _prepare_numbers_conversion(paths, "matrix", launch_numbers=launch_numbers)


def finalize_numbers_conversion(paths):
    return _finalize_numbers_conversion(paths, "matrix")


def verify_prepared_downloads(paths, write_manifest=True):
    return _verify_prepared_download(paths, "matrix", write_manifest=write_manifest)


def validate_download_manifest(paths):
    return _validate_download_manifest(paths, "matrix")


def copy_prepared_downloads(paths, target_dir):
    return _copy_prepared_downloads(paths, target_dir, targets=("matrix",))


def main():
    if len(sys.argv) > 1 and sys.argv[1] in {
        "build",
        "generate",
        "prepare",
        "convert",
        "finalize",
        "verify",
        "validate",
    }:
        sys.argv.insert(1, "matrix")
    return spreadsheet_main()


if __name__ == "__main__":
    raise SystemExit(main())
