from collections import Counter
import xml.etree.ElementTree as ET

from .common import error, load_yaml_checked, warning

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

def validate(root):
    issues = []
    icon_map_path = root / "60 Assets" / "icon-map.yaml"
    if not icon_map_path.exists():
        return [error("icons", icon_map_path, "icon-map.yaml is missing.")]
    try:
        data = load_yaml_checked(icon_map_path)
    except Exception as exc:
        return [error("icons", icon_map_path, f"Icon map parse error: {exc}")]
    fields = data.get("fields") if isinstance(data, dict) else None
    if not isinstance(fields, dict):
        return [error("icons", icon_map_path, "fields must be a mapping.")]

    referenced = set()
    svg_refs = []
    png_refs = []
    for field_id, entry in fields.items():
        if not isinstance(entry, dict):
            issues.append(error("icons", icon_map_path, f"Mapping for {field_id} must be a mapping."))
            continue
        for key in ("svg", "png"):
            if key not in entry:
                issues.append(error("icons", icon_map_path, f"{field_id} is missing {key}."))
                continue
            asset = root / "60 Assets" / entry[key]
            referenced.add(asset.resolve())
            if key == "svg":
                svg_refs.append(entry[key])
            else:
                png_refs.append(entry[key])
            if not asset.exists():
                issues.append(error("icons", asset, f"Referenced {key.upper()} icon does not exist."))

    for ref in _duplicates(svg_refs):
        issues.append(error("icons", icon_map_path, f"Duplicate SVG mapping: {ref}"))
    for ref in _duplicates(png_refs):
        issues.append(error("icons", icon_map_path, f"Duplicate PNG mapping: {ref}"))

    canon_dir = root / "60 Assets" / "icons/card_icons"
    if canon_dir.exists():
        for asset in sorted(list((canon_dir / "SVG").glob("*.svg")) + list((canon_dir / "PNG").glob("*.png"))):
            if asset.resolve() not in referenced:
                issues.append(warning("icons", asset, "Icon file is not referenced by icon-map.yaml."))
    issues.extend(validate_canon_official_modes(root))
    return issues


def _duplicates(values):
    return [value for value, count in Counter(values).items() if count > 1]


def validate_canon_official_modes(root):
    issues = []
    icon_dir = root / "60 Assets" / "icons" / "canon_r5_official"
    metadata_path = icon_dir / "modes.yaml"
    if not icon_dir.exists():
        return [error("icons", icon_dir, "Canon official icon directory is missing.")]
    if not metadata_path.exists():
        return [error("icons", metadata_path, "Canon official modes metadata is missing.")]
    try:
        entries = load_yaml_checked(metadata_path)
    except Exception as exc:
        return [error("icons", metadata_path, f"Invalid YAML: {exc}")]
    if not isinstance(entries, list):
        return [error("icons", metadata_path, "modes.yaml must contain a list.")]

    ids = []
    filenames = []
    entries_by_id = {}
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            issues.append(error("icons", metadata_path, f"Entry {index} must be a mapping."))
            continue
        entry_id = entry.get("id")
        if entry_id:
            ids.append(entry_id)
            entries_by_id[entry_id] = entry
        for field in ("id", "label", "canon_name", "plain_description", "icon", "source"):
            if not entry.get(field):
                issues.append(error("icons", metadata_path, f"{entry_id or f'Entry {index}'} is missing {field}."))
        source = str(entry.get("source", ""))
        if not source.startswith("https://cam.start.canon/"):
            issues.append(error("icons", metadata_path, f"{entry_id or f'Entry {index}'} is missing a Canon source URL."))
        icon_name = entry.get("icon")
        if not icon_name:
            continue
        filenames.append(icon_name)
        icon_path = icon_dir / icon_name
        if not icon_path.exists():
            issues.append(error("icons", icon_path, "Missing Canon icon."))
        elif icon_path.suffix.lower() != ".svg":
            issues.append(error("icons", icon_path, "Canon mode/focus icon must be SVG."))
        elif not _valid_svg(icon_path):
            issues.append(error("icons", icon_path, "Invalid SVG."))

    for required_id in sorted(REQUIRED_CANON_MODE_IDS - set(ids)):
        issues.append(error("icons", metadata_path, f"Missing metadata entry: {required_id}."))
    for duplicate in _duplicates(ids):
        issues.append(error("icons", metadata_path, f"Duplicate metadata id: {duplicate}."))
    for duplicate in _duplicates(filenames):
        issues.append(error("icons", metadata_path, f"Duplicate filename: {duplicate}."))
    referenced = set(filenames)
    for icon_path in icon_dir.glob("*.svg"):
        if icon_path.name.startswith(("mode-", "focus-")) and icon_path.name not in referenced:
            issues.append(warning("icons", icon_path, "Profile references may be missing metadata for this Canon icon."))
    return issues


def _valid_svg(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return False
    return root.tag.endswith("svg")
