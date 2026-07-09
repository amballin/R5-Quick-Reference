#!/usr/bin/env python3
"""Validate the Canon EOS R5 official icon reference appendix."""

from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data/canon_r5_icons.yaml"
OFFICIAL_ICON_DIR = ROOT / "60 Assets/icons/canon_r5_official"
MODES_PATH = OFFICIAL_ICON_DIR / "modes.yaml"
ALLOWED_CATEGORIES = {
    "af",
    "drive",
    "metering",
    "shutter",
    "exposure",
    "image_quality",
    "white_balance",
    "display",
    "playback",
    "connectivity",
    "flash",
    "special_shooting",
}


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main():
    if not DATA_PATH.exists():
        return fail(f"Missing data file: {DATA_PATH.relative_to(ROOT)}")

    entries = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        return fail("data/canon_r5_icons.yaml must contain a list of icon entries")

    ids = set()
    referenced_assets = set()
    errors = []

    for index, entry in enumerate(entries, start=1):
        entry_id = entry.get("id")
        if not entry_id:
            errors.append(f"Entry {index} is missing id")
        elif entry_id in ids:
            errors.append(f"Duplicate id: {entry_id}")
        else:
            ids.add(entry_id)

        for field in ("canon_name", "category", "source_url"):
            if not entry.get(field):
                errors.append(f"{entry_id or f'Entry {index}'} is missing {field}")

        category = entry.get("category")
        if category and category not in ALLOWED_CATEGORIES:
            errors.append(f"{entry_id} has invalid category: {category}")

        asset_path = entry.get("asset_path")
        if asset_path:
            asset = ROOT / asset_path
            referenced_assets.add(asset.resolve())
            if not asset.exists():
                errors.append(f"{entry_id} asset_path does not exist: {asset_path}")
            if OFFICIAL_ICON_DIR not in asset.resolve().parents:
                errors.append(f"{entry_id} asset_path is outside official icon directory: {asset_path}")

    if OFFICIAL_ICON_DIR.exists():
        for asset in OFFICIAL_ICON_DIR.iterdir():
            if asset.is_dir():
                errors.append(f"Unexpected subdirectory in official icon directory: {asset.relative_to(ROOT)}")
                continue
            if asset == MODES_PATH:
                continue
            if asset.name.startswith(("mode-", "focus-")):
                continue
            if asset.suffix.lower() not in {".svg", ".png"}:
                errors.append(f"Unexpected non-icon file in official icon directory: {asset.relative_to(ROOT)}")
            if asset.resolve() not in referenced_assets:
                errors.append(f"Unreferenced file in official icon directory: {asset.relative_to(ROOT)}")
            sample = asset.read_bytes()[:2048].lower()
            if b"placeholder" in sample or b"generated" in sample:
                errors.append(f"Possible placeholder/generated asset in official icon directory: {asset.relative_to(ROOT)}")

    errors.extend(validate_modes_yaml(referenced_assets))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Canon R5 icon reference validation passed: {len(entries)} entries, {len(referenced_assets)} assets.")
    return 0


def validate_modes_yaml(referenced_assets):
    errors = []
    required = {
        "mode-a-plus",
        "mode-fv",
        "mode-p",
        "mode-tv",
        "mode-av",
        "mode-m",
        "mode-bulb",
        "mode-c1",
        "mode-c2",
        "mode-c3",
        "focus-bracketing",
        "focus-guide",
        "focus-mf-peaking",
    }
    if not MODES_PATH.exists():
        return [f"Missing modes metadata: {MODES_PATH.relative_to(ROOT)}"]
    try:
        entries = yaml.safe_load(MODES_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"Invalid YAML in {MODES_PATH.relative_to(ROOT)}: {exc}"]
    if not isinstance(entries, list):
        return [f"{MODES_PATH.relative_to(ROOT)} must contain a list"]
    ids = set()
    filenames = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"modes.yaml entry {index} must be a mapping")
            continue
        entry_id = entry.get("id")
        if entry_id:
            ids.add(entry_id)
        for field in ("id", "label", "canon_name", "plain_description", "icon", "source"):
            if not entry.get(field):
                errors.append(f"{entry_id or f'modes.yaml entry {index}'} is missing {field}")
        if not str(entry.get("source", "")).startswith("https://cam.start.canon/"):
            errors.append(f"{entry_id} is missing Canon source URL")
        icon_name = entry.get("icon")
        if icon_name:
            filenames.append(icon_name)
            asset = OFFICIAL_ICON_DIR / icon_name
            referenced_assets.add(asset.resolve())
            if not asset.exists():
                errors.append(f"{entry_id} missing Canon icon: {asset.relative_to(ROOT)}")
            elif asset.suffix.lower() != ".svg":
                errors.append(f"{entry_id} icon is not SVG: {asset.relative_to(ROOT)}")
    missing = sorted(required - ids)
    for entry_id in missing:
        errors.append(f"Missing modes.yaml metadata entry: {entry_id}")
    duplicate_names = [name for name in set(filenames) if filenames.count(name) > 1]
    for name in sorted(duplicate_names):
        errors.append(f"Duplicate filename in modes.yaml: {name}")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
