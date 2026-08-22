from collections import Counter
from uuid import UUID

from .common import error, flatten_paths, load_yaml_checked


LIST_KEYS = ["checklist", "watch_for", "common_mistakes", "notes"]
CARD_TYPES = {"profile", "reference"}
DISPLAY_CATEGORIES = {"subject", "reference"}
ICON_POSITIONS = {"header", "left", "right"}
FIELD_SETUP_STARTS = {"C1", "C2", "C3"}


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
    profile_ids = _profile_ids(profile_paths)
    card_setting_paths = _card_setting_paths(root)
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
            reference_source = data.get("reference_source")
            if reference_source == "my_menu":
                if "reference_settings" in data:
                    issues.append(error("profiles", path, "My Menu reference rows are derived and must not be authored."))
            else:
                if reference_source is not None:
                    issues.append(error("profiles", path, f"Unknown reference_source: {reference_source}."))
                issues.extend(_validate_reference_settings(path, data.get("reference_settings")))
        elif not isinstance(overrides, dict):
            issues.append(error("profiles", path, "overrides must be a mapping."))
        else:
            issues.extend(_validate_overrides(path, overrides, baseline_paths, baseline_values))
        for key in LIST_KEYS:
            if key in data and not isinstance(data[key], list):
                issues.append(error("profiles", path, f"{key} must be a list."))
        issues.extend(_validate_card_icons(path, data.get("card")))
        issues.extend(
            _validate_field_setup(
                path,
                data.get("card"),
                profile_ids,
                card_setting_paths,
                card_type,
                display_category,
            )
        )
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


def _validate_field_setup(path, card, profile_ids, card_setting_paths, card_type, display_category):
    if card is None or not isinstance(card, dict) or "field_setup" not in card:
        return []
    if card_type == "reference":
        return [error("profiles", path, "Reference cards must not define card.field_setup.")]
    setup = card.get("field_setup")
    if not isinstance(setup, dict):
        return [error("profiles", path, "card.field_setup must be a mapping.")]
    issues = []
    unknown = sorted(set(setup) - {"start", "source_card_id", "access_only", "my_menus"})
    if unknown:
        issues.append(error("profiles", path, f"Unknown card.field_setup keys: {', '.join(unknown)}."))
    access_only = setup.get("access_only", False)
    if not isinstance(access_only, bool):
        issues.append(error("profiles", path, "card.field_setup.access_only must be true or false."))
        access_only = False
    if access_only:
        if display_category != "reference":
            issues.append(error("profiles", path, "Access-only field setup requires display_category: reference."))
        if "start" in setup or "source_card_id" in setup:
            issues.append(error("profiles", path, "Access-only field setup must omit start and source_card_id."))
    else:
        start_present = "start" in setup
        source_present = "source_card_id" in setup
        if start_present != source_present:
            issues.append(error("profiles", path, "card.field_setup.start and source_card_id must be provided together."))
        if start_present and setup.get("start") not in FIELD_SETUP_STARTS:
            issues.append(error("profiles", path, "card.field_setup.start must be C1, C2, or C3."))
        source_card_id = setup.get("source_card_id")
        if source_present and not _valid_uuid(source_card_id):
            issues.append(error("profiles", path, "card.field_setup.source_card_id must be a canonical UUID."))
        elif source_present and source_card_id not in profile_ids:
            issues.append(error("profiles", path, f"card.field_setup.source_card_id does not match a card: {source_card_id}"))
    menus = setup.get("my_menus", [])
    if not isinstance(menus, list):
        issues.append(error("profiles", path, "card.field_setup.my_menus must be a list."))
        return issues
    if len(menus) > 5:
        issues.append(error("profiles", path, "card.field_setup.my_menus supports at most five tabs."))
    if access_only and not menus:
        issues.append(error("profiles", path, "Access-only field setup requires at least one My Menu tab."))
    if not access_only and "start" not in setup and not menus:
        issues.append(error("profiles", path, "Field setup without a Cx foundation requires at least one My Menu tab."))
    if display_category == "reference" and "start" not in setup and menus and not access_only:
        issues.append(error("profiles", path, "Reference-category field setup without a Cx foundation requires access_only: true."))
    names = []
    assigned_settings = []
    for index, menu in enumerate(menus, start=1):
        if not isinstance(menu, dict):
            issues.append(error("profiles", path, f"card.field_setup.my_menus item {index} must be a mapping."))
            continue
        unknown_menu_keys = sorted(set(menu) - {"name", "settings"})
        if unknown_menu_keys:
            issues.append(
                error(
                    "profiles",
                    path,
                    f"card.field_setup.my_menus item {index} has unknown keys: {', '.join(unknown_menu_keys)}.",
                )
            )
        name = menu.get("name")
        if not isinstance(name, str) or not name.strip():
            issues.append(error("profiles", path, f"card.field_setup.my_menus item {index} requires a non-empty name."))
        else:
            names.append(name.casefold())
        settings = menu.get("settings")
        if not isinstance(settings, list) or not settings:
            issues.append(
                error("profiles", path, f"card.field_setup.my_menus item {index} requires a non-empty settings list.")
            )
            continue
        for setting in settings:
            if not isinstance(setting, str) or not setting.strip():
                issues.append(
                    error("profiles", path, f"card.field_setup.my_menus item {index} settings must be non-empty strings.")
                )
            elif setting not in card_setting_paths:
                issues.append(error("profiles", path, f"Field-setup setting is not in card display order: {setting}"))
            else:
                assigned_settings.append(setting)
    duplicate_names = _duplicates(names)
    if duplicate_names:
        issues.append(error("profiles", path, f"Duplicate My Menu names in card.field_setup: {', '.join(duplicate_names)}."))
    duplicate_settings = _duplicates(assigned_settings)
    if duplicate_settings:
        issues.append(
            error("profiles", path, f"Settings assigned to more than one My Menu tab: {', '.join(duplicate_settings)}.")
        )
    return issues


def _profile_ids(profile_paths):
    values = set()
    for path in profile_paths:
        try:
            data = load_yaml_checked(path) or {}
        except Exception:
            continue
        card_id = data.get("card_id")
        if isinstance(card_id, str):
            values.add(card_id)
    return values


def _valid_uuid(value):
    if not isinstance(value, str):
        return False
    try:
        return str(UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def _card_setting_paths(root):
    try:
        layout = load_yaml_checked(root / "00 Master" / "card_layout.yaml") or {}
    except Exception:
        return set()
    return set((layout.get("card_layout") or {}).get("display_order") or [])


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
