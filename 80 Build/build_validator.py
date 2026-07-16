from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

from utilities import flatten


def discover_profiles(paths):
    return sorted(paths.profiles_dir.glob("*.yaml"))


def is_reference_card(data):
    return data.get("card_type") == "reference"


def profile_name_from_path(path):
    return path.stem


def validate_project(paths):
    results = []
    if not paths.baseline_file.exists():
        results.append(("error", "missing_baseline", str(paths.baseline_file)))

    profile_paths = discover_profiles(paths)
    lowered = [path.stem.lower() for path in profile_paths]
    duplicates = [name for name, count in Counter(lowered).items() if count > 1]
    for name in duplicates:
        results.append(("error", "duplicate_profile_name", name))

    for path in profile_paths:
        try:
            data = _load_yaml(path)
        except Exception as exc:
            results.append(("error", "profile_yaml_syntax", f"{path}: {exc}"))
            continue
        if not is_reference_card(data) and data.get("inherits") != "baseline":
            results.append(("error", "profile_inheritance", f"{path}: inherits must be baseline"))

    results.extend(validate_assets(paths))
    results.extend(validate_canon_official_modes(paths))
    results.extend(validate_required_appendices(paths))
    return results


def validate_assets(paths):
    results = []
    if not paths.icon_map_file.exists():
        return results
    try:
        icon_map = _load_yaml(paths.icon_map_file) or {}
    except Exception as exc:
        return [("error", "icon_map_yaml_syntax", f"{paths.icon_map_file}: {exc}")]

    fields = icon_map.get("fields", {}) or {}
    for field_id, entry in fields.items():
        svg = paths.icon_asset_dir / entry.get("svg", "")
        png = paths.icon_asset_dir / entry.get("png", "")
        if not svg.exists() and not png.exists():
            results.append(("warning", "missing_icon_asset", field_id))
    return results


REQUIRED_CANON_MODE_IDS = {
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

CANON_PROFILE_REFERENCES = {
    "exposure.mode": {
        "A+": "mode-a-plus",
        "Scene Intelligent Auto": "mode-a-plus",
        "Fv": "mode-fv",
        "P": "mode-p",
        "Tv": "mode-tv",
        "Av": "mode-av",
        "M": "mode-m",
        "Manual": "mode-m",
        "Manual Exposure": "mode-m",
        "BULB": "mode-bulb",
        "Bulb": "mode-bulb",
        "C1": "mode-c1",
        "C2": "mode-c2",
        "C3": "mode-c3",
    },
    "image.focus_bracketing": {"Enable": "focus-bracketing", "On": "focus-bracketing"},
    "autofocus.focus_guide": {"Enable": "focus-guide", "On": "focus-guide"},
    "autofocus.mf_peaking": {"Enable": "focus-mf-peaking", "On": "focus-mf-peaking"},
}


def validate_canon_official_modes(paths):
    results = []
    icon_dir = paths.root / "60 Assets" / "icons" / "canon_r5_official"
    metadata_path = icon_dir / "modes.yaml"
    if not icon_dir.exists():
        return [("error", "missing_canon_icon_dir", str(icon_dir))]
    if not metadata_path.exists():
        return [("error", "missing_canon_metadata", str(metadata_path))]
    try:
        entries = _load_yaml(metadata_path)
    except Exception as exc:
        return [("error", "invalid_canon_modes_yaml", f"{metadata_path}: {exc}")]
    if not isinstance(entries, list):
        return [("error", "invalid_canon_modes_yaml", f"{metadata_path}: expected a list")]

    ids = []
    filenames = []
    entries_by_id = {}
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            results.append(("error", "invalid_canon_metadata_entry", f"{metadata_path}: entry {index} must be a mapping"))
            continue
        entry_id = entry.get("id")
        if entry_id:
            ids.append(entry_id)
            entries_by_id[entry_id] = entry
        else:
            results.append(("error", "missing_canon_metadata_entry", f"{metadata_path}: entry {index} missing id"))
        for field in ("label", "canon_name", "plain_description", "icon", "source"):
            if not entry.get(field):
                results.append(("error", "missing_canon_metadata_entry", f"{entry_id or index}: missing {field}"))
        icon_name = entry.get("icon")
        if icon_name:
            filenames.append(icon_name)
            icon_path = icon_dir / icon_name
            if not icon_path.exists():
                results.append(("error", "missing_canon_icon", str(icon_path)))
            elif icon_path.suffix.lower() != ".svg":
                results.append(("error", "missing_canon_icon", f"{icon_path}: Canon mode/focus assets must be SVG"))
            elif not _valid_svg(icon_path):
                results.append(("error", "invalid_svg", str(icon_path)))
        source = str(entry.get("source", ""))
        if not source.startswith("https://cam.start.canon/"):
            results.append(("error", "missing_canon_source_reference", f"{entry_id or index}: {source}"))

    for duplicate in _duplicates(ids):
        results.append(("error", "duplicate_canon_metadata", duplicate))
    for duplicate in _duplicates(filenames):
        results.append(("error", "duplicate_filename", duplicate))
    for required_id in sorted(REQUIRED_CANON_MODE_IDS - set(ids)):
        results.append(("error", "missing_metadata_entry", required_id))

    referenced_icons = {entry.get("icon") for entry in entries_by_id.values()}
    for required_id in REQUIRED_CANON_MODE_IDS:
        entry = entries_by_id.get(required_id)
        if not entry:
            continue
        icon_name = entry.get("icon")
        if not icon_name or not (icon_dir / icon_name).exists():
            results.append(("error", "missing_canon_icon", required_id))

    results.extend(validate_profile_canon_icon_references(paths, entries_by_id))

    for icon_path in icon_dir.glob("*.svg"):
        if icon_path.name.startswith(("mode-", "focus-")) and icon_path.name not in referenced_icons:
            results.append(("warning", "profile_references_missing_metadata", str(icon_path)))
    return results


def validate_profile_canon_icon_references(paths, entries_by_id):
    results = []
    for path in discover_profiles(paths):
        try:
            profile = _load_yaml(path)
            baseline = _load_yaml(paths.baseline_file).get("defaults", {})
        except Exception:
            continue
        if is_reference_card(profile):
            continue
        merged = _deep_merge(baseline, profile.get("overrides", {}) or {})
        fields = flatten(merged)
        for field_key, values in CANON_PROFILE_REFERENCES.items():
            value = fields.get(field_key)
            if value is None:
                continue
            metadata_id = values.get(str(value).strip())
            if not metadata_id:
                continue
            entry = entries_by_id.get(metadata_id)
            if not entry:
                results.append(("error", "profile_references_missing_metadata", f"{path}: {field_key}={value}"))
                continue
            icon_path = paths.root / "60 Assets" / "icons" / "canon_r5_official" / entry.get("icon", "")
            if not icon_path.exists():
                results.append(("error", "profile_references_missing_icons", f"{path}: {field_key}={value}"))
    return results


def validate_required_appendices(paths):
    results = []
    manifest_path = paths.root / "50 Field Guide" / "required_appendices.yaml"
    if not manifest_path.exists():
        return [("error", "missing_required_appendices_manifest", str(manifest_path))]
    try:
        manifest = _load_yaml(manifest_path)
    except Exception as exc:
        return [("error", "required_appendices_yaml_syntax", f"{manifest_path}: {exc}")]

    appendices = manifest.get("appendices", []) or []
    required_sections = manifest.get("required_sections", []) or []
    if not appendices:
        results.append(("error", "required_appendices_empty", str(manifest_path)))
    if not required_sections:
        results.append(("error", "required_appendix_sections_empty", str(manifest_path)))

    profile_titles = _profile_titles(paths)
    appendix_ids = {entry.get("id") for entry in appendices if isinstance(entry, dict)}

    for entry in appendices:
        if not isinstance(entry, dict):
            results.append(("error", "invalid_required_appendix_entry", str(manifest_path)))
            continue
        appendix_id = entry.get("id", "<missing id>")
        title = entry.get("title", appendix_id)
        relative_file = entry.get("file")
        if not relative_file:
            results.append(("error", "required_appendix_missing_file", appendix_id))
            continue
        path = paths.root / "50 Field Guide" / relative_file
        if not path.exists():
            results.append(("error", "missing_required_appendix", f"{title}: {path}"))
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        headings = _headings(text)
        skipped_sections = set(entry.get("skip_required_sections", []) or [])
        for section in required_sections:
            if section in skipped_sections:
                continue
            if section not in headings:
                results.append(("error", "required_appendix_missing_section", f"{path}: {section}"))
        if entry.get("strict_topics"):
            normalized_text = _normalize(text)
            for topic in entry.get("required_topics", []) or []:
                if _normalize(str(topic)) not in normalized_text:
                    results.append(("error", "required_appendix_missing_topic", f"{path}: {topic}"))
        for profile in entry.get("profiles", []) or []:
            if profile not in profile_titles:
                results.append(("error", "required_appendix_missing_profile_ref", f"{appendix_id}: {profile}"))
        for related in entry.get("related_appendices", []) or []:
            if related not in appendix_ids:
                results.append(("error", "required_appendix_missing_related_ref", f"{appendix_id}: {related}"))
    return results


def _load_yaml(path):
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _valid_svg(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return False
    return root.tag.endswith("svg")


def _duplicates(values):
    return [value for value, count in Counter(values).items() if count > 1]


def _deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _headings(text):
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped.lstrip("#").strip())
    return headings


def _profile_titles(paths):
    titles = set()
    for path in discover_profiles(paths):
        try:
            data = _load_yaml(path)
        except Exception:
            continue
        title = data.get("title")
        if isinstance(title, str):
            titles.add(title)
    return titles


def _normalize(value):
    return " ".join(value.lower().replace("-", " ").split())
