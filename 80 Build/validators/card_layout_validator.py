from .common import error, load_yaml_checked


REQUIRED_KEYS = [
    "exposure.mode",
    "shutter.target",
    "lens.aperture.target",
    "exposure.iso.mode",
    "exposure.auto_iso.maximum",
    "autofocus.operation",
    "autofocus.method",
    "autofocus.subject_detection",
    "autofocus.eye_detection",
    "drive.mode",
    "stabilization.image_stabilization.mode",
]

REQUIRED_DISPLAY_ORDER = [
    "exposure.mode",
    "exposure.metering",
    "shutter.target",
    "shutter.type",
    "lens.aperture.target",
    "exposure.iso.mode",
    "exposure.iso.value",
    "exposure.auto_iso.maximum",
    "exposure.exposure_compensation",
    "autofocus.operation",
    "autofocus.method",
    "autofocus.subject_detection",
    "autofocus.eye_detection",
    "drive.mode",
    "stabilization.image_stabilization.mode",
    "stabilization.ibis",
    "stabilization.lens_is",
    "image.focus_bracketing",
    "image.long_exposure_noise_reduction.value",
    "display.histogram",
    "display.highlight_alert",
    "image.quality",
    "image.white_balance",
    "image.highlight_tone_priority",
    "image.high_iso_noise_reduction",
    "camera_setup.electronic_full_time_mf",
    "camera_setup.ibis_high_res_shot",
    "camera_setup.continuous_af",
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
    display_order = (data.get("card_layout") or {}).get("display_order")
    if not isinstance(entries, list):
        return [error("card_layout", path, "card_layout.always_show must be a list.")]
    issues = []
    if not isinstance(display_order, list) or not display_order:
        issues.append(error("card_layout", path, "card_layout.display_order must be a non-empty list."))
        display_order = []
    elif any(not isinstance(key, str) or not key.strip() for key in display_order):
        issues.append(error("card_layout", path, "card_layout.display_order entries must be non-empty strings."))
    if len(display_order) != len(set(display_order)):
        issues.append(error("card_layout", path, "display_order contains duplicate keys."))
    if display_order and display_order != REQUIRED_DISPLAY_ORDER:
        issues.append(error("card_layout", path, "display_order must match the approved Quick Reference sequence."))
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
    missing_order = [key for key in keys if key not in display_order]
    if missing_order:
        issues.append(error("card_layout", path, f"display_order is missing always-shown keys: {', '.join(missing_order)}."))
    return issues
