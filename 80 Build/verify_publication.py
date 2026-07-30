#!/usr/bin/env python3
"""Verify that the latest commit is a complete, synchronized publication."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

import yaml

from asset_manager import ProjectPaths
from publish_metadata import display_publish_metadata, load_publish_metadata
from spreadsheet_downloads import (
    SpreadsheetDownloadError,
    validate_download_manifest,
    validate_published_release,
)


METADATA_PATH = "80 Build/publish_metadata.yaml"
RELEASE_MANIFEST_PATH = "docs/downloads/spreadsheet-releases.json"


class PublicationVerificationError(RuntimeError):
    """Raised when the latest publication is incomplete or inconsistent."""


def verify_publication(paths, required_targets=(), require_no_spreadsheets=False):
    current = load_publish_metadata(paths.root / METADATA_PATH)
    committed = _yaml_from_git(paths, f"HEAD:{METADATA_PATH}")
    previous = _yaml_from_git(paths, f"HEAD^:{METADATA_PATH}")
    if committed != _plain_metadata(current):
        raise PublicationVerificationError(
            "Working publish metadata does not match the latest commit."
        )
    _verify_version_transition(previous["version"], committed["version"])

    expected_display = (
        f"Version {current['version']['major']}.{current['version']['minor']:02d}"
    )
    index_path = paths.pages_output_dir / "index.html"
    if not index_path.is_file() or expected_display not in index_path.read_text(encoding="utf-8"):
        raise PublicationVerificationError(
            f"Published index does not display {expected_display}."
        )

    if _git(["diff", "--quiet", "HEAD", "--", METADATA_PATH, "docs"], paths, check=False):
        raise PublicationVerificationError(
            "Publish metadata or docs differ from the latest commit."
        )

    release = validate_published_release(paths, root=paths.pages_output_dir)
    published_targets = set((release.get("targets") or {}).keys())
    if require_no_spreadsheets:
        if published_targets or (paths.root / RELEASE_MANIFEST_PATH).exists():
            raise PublicationVerificationError(
                "Spreadsheet downloads remain although explicit removal was requested."
            )
    else:
        missing = sorted(set(required_targets) - published_targets)
        if missing:
            raise PublicationVerificationError(
                f"Published spreadsheet release is missing: {', '.join(missing)}."
            )
        for target in required_targets:
            local = validate_download_manifest(paths, target)
            published = release["targets"][target]
            for key in ("xlsx", "numbers"):
                local_entry = local[key]
                published_entry = (published.get("files") or {}).get(key) or {}
                if (
                    local_entry.get("name") != published_entry.get("name")
                    or local_entry.get("sha256") != published_entry.get("sha256")
                ):
                    raise PublicationVerificationError(
                        f"Published {target} {key} does not match the prepared file."
                    )

    head = _git_text(["rev-parse", "HEAD"], paths)
    upstream = _git_text(["rev-parse", "@{upstream}"], paths)
    if head != upstream:
        raise PublicationVerificationError(
            "Latest publication commit is not synchronized with the upstream branch."
        )

    return {
        "display": display_publish_metadata(current),
        "targets": tuple(sorted(published_targets)),
        "commit": head,
    }


def _verify_version_transition(previous, current):
    old_major, old_minor = previous["major"], previous["minor"]
    new_major, new_minor = current["major"], current["minor"]
    ordinary = new_major == old_major and new_minor == old_minor + 1
    major = new_major > old_major and new_minor == 0
    if not (ordinary or major):
        raise PublicationVerificationError(
            f"Latest commit did not advance the website version correctly: "
            f"{old_major}.{old_minor:02d} -> {new_major}.{new_minor:02d}."
        )


def _plain_metadata(metadata):
    return {
        "version": dict(metadata["version"]),
        "published": metadata["published"],
    }


def _yaml_from_git(paths, object_name):
    text = _git_text(["show", object_name], paths)
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise PublicationVerificationError(
            f"Could not read committed publish metadata: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise PublicationVerificationError("Committed publish metadata is invalid.")
    return data


def _git_text(arguments, paths):
    result = subprocess.run(
        ["git", *arguments],
        cwd=paths.root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "Git command failed."
        raise PublicationVerificationError(detail)
    return result.stdout.strip()


def _git(arguments, paths, check=True):
    result = subprocess.run(
        ["git", *arguments],
        cwd=paths.root,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise PublicationVerificationError(result.stderr.strip() or "Git command failed.")
    return result.returncode


def parse_args():
    parser = argparse.ArgumentParser(description="Verify the latest website publication.")
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--require-target",
        action="append",
        choices=("matrix", "setup"),
        default=[],
    )
    parser.add_argument("--require-no-spreadsheets", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.require_no_spreadsheets and args.require_target:
        print(
            "Publication verification options conflict.",
            file=sys.stderr,
        )
        return 2
    try:
        result = verify_publication(
            ProjectPaths(args.root),
            required_targets=args.require_target,
            require_no_spreadsheets=args.require_no_spreadsheets,
        )
    except (
        OSError,
        PublicationVerificationError,
        SpreadsheetDownloadError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(f"PUBLICATION VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    targets = ", ".join(result["targets"]) if result["targets"] else "none"
    print("PUBLICATION VERIFIED")
    print(f"Release: {result['display']}")
    print(f"Spreadsheet targets: {targets}")
    print(f"Commit: {result['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
