from .common import error, load_yaml_checked


REQUIRED_KEYS = [
    "exposure.mode",
    "autofocus.operation",
    "autofocus.subject_detection",
    "autofocus.eye_detection",
    "autofocus.method",
    "drive.mode",
    "shutter.target",
    "lens.aperture.target",
    "exposure.auto_iso.maximum",
    "stabilization.image_stabilization.mode",
    "exposure.iso.mode",
]


def validate(root):
    path = root / "00 Master" / "card_layout.yaml"
    if not path.exists():
        return [error("card_layout", path, "Card layout file is missing.")]
    try:
        data = load_yaml_checked(path) or {}
    except Exception as exc:
        return [error("card_layout", path, f"Card layout parse error: {exc}")]
    entries = (data.get("card_layout") or {}).get("always_show")
    if not isinstance(entries, list):
        return [error("card_layout", path, "card_layout.always_show must be a list.")]
    issues = []
    keys = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict) or not entry.get("key") or not entry.get("label"):
            issues.append(error("card_layout", path, f"always_show entry {index} must have key and label."))
            continue
        keys.append(entry["key"])
    if len(keys) != len(set(keys)):
        issues.append(error("card_layout", path, "always_show contains duplicate keys."))
    if keys != REQUIRED_KEYS:
        issues.append(error("card_layout", path, "always_show must match the ordered required settings in Card Specification.md."))
    return issues
