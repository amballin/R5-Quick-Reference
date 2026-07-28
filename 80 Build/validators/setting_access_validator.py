from .common import error, flatten_paths, load_yaml_checked


REQUIRED_FIELDS = {"best_access", "menu_location", "rapid_order"}


def validate(root):
    access_path = root / "00 Master" / "setting_access.yaml"
    if not access_path.exists():
        return [error("setting_access", access_path, "Setting-access mapping is missing.")]
    try:
        data = load_yaml_checked(access_path) or {}
    except Exception as exc:
        return [error("setting_access", access_path, f"Setting-access mapping parse error: {exc}")]

    mapping = data.get("setting_access")
    if not isinstance(mapping, dict) or not mapping:
        return [error("setting_access", access_path, "setting_access must be a non-empty mapping.")]

    issues = []
    rapid_orders = []
    for key, entry in mapping.items():
        if not isinstance(key, str) or not key.strip():
            issues.append(error("setting_access", access_path, "Setting-access keys must be non-empty strings."))
            continue
        if not isinstance(entry, dict):
            issues.append(error("setting_access", access_path, f"{key} must map to an object."))
            continue
        missing = sorted(REQUIRED_FIELDS - set(entry))
        if missing:
            issues.append(error("setting_access", access_path, f"{key} is missing: {', '.join(missing)}."))
        for field in ("best_access", "menu_location"):
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(error("setting_access", access_path, f"{key}.{field} must be a non-empty string."))
        rapid_order = entry.get("rapid_order")
        if not isinstance(rapid_order, int):
            issues.append(error("setting_access", access_path, f"{key}.rapid_order must be an integer."))
        else:
            rapid_orders.append(rapid_order)

    if len(rapid_orders) != len(set(rapid_orders)):
        issues.append(error("setting_access", access_path, "rapid_order values must be unique."))

    summary_keys = _subject_summary_keys(root)
    missing_keys = [key for key in summary_keys if key not in mapping]
    if missing_keys:
        issues.append(
            error(
                "setting_access",
                access_path,
                f"Missing access details for subject-summary settings: {', '.join(missing_keys)}.",
            )
        )
    layout = load_yaml_checked(root / "00 Master" / "card_layout.yaml") or {}
    display_order = (layout.get("card_layout") or {}).get("display_order") or []
    unknown_keys = sorted(set(mapping) - set(display_order))
    if unknown_keys:
        issues.append(
            error(
                "setting_access",
                access_path,
                f"Access details reference settings outside card_layout.display_order: {', '.join(unknown_keys)}.",
            )
        )
    return issues


def _subject_summary_keys(root):
    layout = load_yaml_checked(root / "00 Master" / "card_layout.yaml") or {}
    order = (layout.get("card_layout") or {}).get("display_order") or []
    always_show = (layout.get("card_layout") or {}).get("always_show") or []
    keys = {
        entry.get("key")
        for entry in always_show
        if isinstance(entry, dict) and isinstance(entry.get("key"), str)
    }
    for profile_path in sorted((root / "10 Profiles").glob("*.yaml")):
        profile = load_yaml_checked(profile_path) or {}
        if profile.get("card_type") == "reference":
            continue
        category = profile.get("display_category") or "subject"
        if category != "subject":
            continue
        keys.update(flatten_paths(profile.get("overrides") or {}))

    display_keys = {
        "exposure.iso.value": "exposure.iso.mode",
        "exposure.auto_iso.maximum": "exposure.iso.mode",
        "stabilization.lens_is": "stabilization.ibis",
    }
    normalized = {display_keys.get(key, key) for key in keys}
    return [key for key in order if key in normalized]
