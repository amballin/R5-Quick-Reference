from collections import Counter

from .common import error, flatten_paths, load_yaml_checked


LIST_KEYS = ["checklist", "watch_for", "common_mistakes", "notes"]
CARD_TYPES = {"profile", "reference"}
DISPLAY_CATEGORIES = {"subject", "reference"}
ICON_POSITIONS = {"header", "left", "right"}


def validate(root):
    issues = []
    baseline_path = root / "00 Master" / "baseline.yaml"
    baseline_paths = set()
    baseline_values = {}
    try:
        baseline = load_yaml_checked(baseline_path)
        defaults = baseline.get("defaults", {})
        baseline_paths = flatten_paths(defaults)
        baseline_values = _flatten_values(defaults)
    except Exception:
        pass

    profile_paths = sorted((root / "10 Profiles").glob("*.yaml"))
    stems = [path.stem.lower() for path in profile_paths]
    titles = []
    appendix_ids = _appendix_ids(root)

    for duplicate in _duplicates(stems):
        issues.append(error("profiles", root / "10 Profiles", f"Duplicate profile filename stem: {duplicate}"))

    for path in profile_paths:
        try:
            data = load_yaml_checked(path)
        except Exception as exc:
            issues.append(error("profiles", path, f"Profile YAML parse error: {exc}"))
            continue
        if not isinstance(data, dict):
            issues.append(error("profiles", path, "Profile must be a mapping."))
            continue
        issues.extend(_required_profile_keys(path, data))
        title = data.get("title")
        if isinstance(title, str):
            titles.append(title.lower())
        card_type = data.get("card_type", "profile")
        if card_type not in CARD_TYPES:
            issues.append(error("profiles", path, f"card_type must be one of: {', '.join(sorted(CARD_TYPES))}."))
        display_category = data.get("display_category")
        if display_category is not None and display_category not in DISPLAY_CATEGORIES:
            issues.append(error("profiles", path, f"display_category must be one of: {', '.join(sorted(DISPLAY_CATEGORIES))}."))
        display_order = data.get("display_order")
        if display_order is not None and (not isinstance(display_order, int) or isinstance(display_order, bool)):
            issues.append(error("profiles", path, "display_order must be an integer."))
        overrides = data.get("overrides", {})
        if card_type == "reference":
            if "inherits" in data:
                issues.append(error("profiles", path, "Reference cards must not inherit the shooting baseline."))
            if "overrides" in data:
                issues.append(error("profiles", path, "Reference cards must not define shooting-profile overrides."))
            issues.extend(_validate_reference_settings(path, data.get("reference_settings")))
        elif not isinstance(overrides, dict):
            issues.append(error("profiles", path, "overrides must be a mapping."))
        else:
            issues.extend(_validate_overrides(path, overrides, baseline_paths, baseline_values))
        for key in LIST_KEYS:
            if key in data and not isinstance(data[key], list):
                issues.append(error("profiles", path, f"{key} must be a list."))
        issues.extend(_validate_card_icons(path, data.get("card")))
        issues.extend(_validate_appendix_links(path, data.get("appendix_links"), appendix_ids))

    for duplicate in _duplicates(titles):
        issues.append(error("profiles", root / "10 Profiles", f"Duplicate profile title: {duplicate}"))
    return issues


def _validate_card_icons(path, card):
    if card is None:
        return []
    if not isinstance(card, dict):
        return [error("profiles", path, "card must be a mapping.")]
    icons = card.get("icons")
    if icons is None:
        return []
    if not isinstance(icons, dict):
        return [error("profiles", path, "card.icons must be a mapping.")]
    issues = []
    unknown = sorted(set(icons) - ICON_POSITIONS)
    if unknown:
        issues.append(error("profiles", path, f"Unknown card icon positions: {', '.join(unknown)}."))
    for position, value in icons.items():
        if value is not None and not isinstance(value, str):
            issues.append(error("profiles", path, f"card.icons.{position} must be a string or null."))
    return issues


def _appendix_ids(root):
    manifest_path = root / "50 Field Guide" / "required_appendices.yaml"
    try:
        manifest = load_yaml_checked(manifest_path) or {}
    except Exception:
        return set()
    return {
        entry.get("id")
        for entry in manifest.get("appendices", []) or []
        if isinstance(entry, dict) and entry.get("id")
    }


def _validate_appendix_links(path, links, appendix_ids):
    if links is None:
        return []
    if not isinstance(links, list):
        return [error("profiles", path, "appendix_links must be a list.")]
    issues = []
    for index, item in enumerate(links, start=1):
        if not isinstance(item, dict):
            issues.append(error("profiles", path, f"appendix_links item {index} must be a mapping."))
            continue
        appendix_id = item.get("id")
        if not isinstance(appendix_id, str) or not appendix_id.strip():
            issues.append(error("profiles", path, f"appendix_links item {index} requires a non-empty id."))
        elif appendix_id not in appendix_ids:
            issues.append(error("profiles", path, f"appendix_links item {index} references missing appendix id: {appendix_id}"))
        label = item.get("label")
        if label is not None and (not isinstance(label, str) or not label.strip()):
            issues.append(error("profiles", path, f"appendix_links item {index} label must be a non-empty string."))
    return issues


def _validate_reference_settings(path, settings):
    issues = []
    if not isinstance(settings, list) or not settings:
        return [error("profiles", path, "Reference cards require a non-empty reference_settings list.")]
    for index, item in enumerate(settings, start=1):
        if not isinstance(item, dict):
            issues.append(error("profiles", path, f"reference_settings item {index} must be a mapping."))
            continue
        for key in ("control", "assignment"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                issues.append(error("profiles", path, f"reference_settings item {index} requires a non-empty {key}."))
    return issues


def _required_profile_keys(path, data):
    issues = []
    required = ("metadata", "title") if data.get("card_type") == "reference" else ("metadata", "title", "inherits")
    for key in required:
        if key not in data:
            issues.append(error("profiles", path, f"Missing required key: {key}."))
        if "metadata" in data and not isinstance(data["metadata"], dict):
            issues.append(error("profiles", path, "metadata must be a mapping."))
        elif "metadata" in data and "release" in data["metadata"] and not isinstance(data["metadata"]["release"], bool):
            issues.append(error("profiles", path, "metadata.release must be a boolean."))
    if "title" in data and not isinstance(data["title"], str):
        issues.append(error("profiles", path, "title must be a string."))
    if "subtitle" in data and data["subtitle"] is not None and not isinstance(data["subtitle"], str):
        issues.append(error("profiles", path, "subtitle must be a string or null."))
    if data.get("card_type") != "reference" and data.get("inherits") != "baseline":
        issues.append(error("profiles", path, "inherits must be baseline."))
    return issues


def _validate_overrides(path, overrides, baseline_paths, baseline_values):
    issues = []
    override_values = _flatten_values(overrides)
    for override_path, override_value in sorted(override_values.items()):
        if baseline_paths and override_path not in baseline_paths:
            issues.append(error("overrides", path, f"Override path is not present in baseline defaults: {override_path}"))
            continue
        if override_path in baseline_values and not _compatible_type(baseline_values[override_path], override_value):
            expected = type(baseline_values[override_path]).__name__
            actual = type(override_value).__name__
            issues.append(error("overrides", path, f"Override path {override_path} has type {actual}; expected {expected}."))
        elif override_path in baseline_values and baseline_values[override_path] == override_value:
            issues.append(error("overrides", path, f"Override duplicates the baseline value: {override_path}"))
    return issues


def _duplicates(values):
    return [value for value, count in Counter(values).items() if count > 1]


def _flatten_values(data, prefix=""):
    values = {}
    if not isinstance(data, dict):
        return values
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            values.update(_flatten_values(value, name))
        else:
            values[name] = value
    return values


def _compatible_type(expected, actual):
    if expected is None:
        return True
    if isinstance(expected, bool):
        return isinstance(actual, bool)
    if isinstance(expected, int) and not isinstance(expected, bool):
        return isinstance(actual, int) and not isinstance(actual, bool)
    if isinstance(expected, float):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool)
    return isinstance(actual, type(expected))
