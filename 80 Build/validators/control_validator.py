from .common import error, load_yaml_checked


EVIDENCE_STATUSES = {
    "verified_canon_capability",
    "owner_confirmed",
    "approved_target_pending_camera_verification",
    "recommendation",
    "unresolved",
}

DEPRECATED_SETTING_VALUES = {
    "One Shot AF": "One-Shot AF",
    "Single Shooting": "Single Shot",
}


def validate(root):
    issues = []
    project_path = root / "controls.yaml"
    current_path = root / "data" / "canon_r5_custom_controls_current.yaml"

    try:
        project = load_yaml_checked(project_path)
    except Exception as exc:
        return [error("controls", project_path, f"Control record parse error: {exc}")]
    try:
        current = load_yaml_checked(current_path)
    except Exception as exc:
        return [error("controls", current_path, f"Control record parse error: {exc}")]

    issues.extend(_status_issues(project_path, project.get("controls"), "controls"))
    issues.extend(_status_issues(project_path, project.get("dials"), "dials"))
    issues.extend(_status_issues(current_path, current.get("buttons"), "buttons"))
    issues.extend(_status_issues(current_path, current.get("dials"), "dials"))

    project_controls = _normalize_entries(project.get("controls"))
    current_controls = _normalize_entries(current.get("buttons"))
    if project_controls != current_controls:
        issues.append(error("controls", current_path, "Button/control records do not agree with controls.yaml."))

    project_dials = _normalize_entries(project.get("dials"))
    current_dials = _normalize_entries(current.get("dials"))
    if project_dials != current_dials:
        issues.append(error("controls", current_path, "Dial records do not agree with controls.yaml."))

    project_modes = _mode_mapping(project.get("custom_shooting_modes"))
    current_modes = _mode_mapping(current.get("custom_shooting_modes"))
    if project_modes != current_modes:
        issues.append(error("controls", current_path, "C1-C3 mappings do not agree with controls.yaml."))
    if set(project_modes) != {"C1", "C2", "C3"}:
        issues.append(error("controls", project_path, "C1-C3 mappings must define C1, C2, and C3."))

    owner_scope = (
        current.get("evidence", {})
        .get("owner_confirmation", {})
        .get("status")
    )
    if owner_scope != "applies_only_to_entries_marked_owner_confirmed":
        issues.append(
            error(
                "controls",
                current_path,
                "Owner-confirmation scope must apply only to entries marked owner_confirmed.",
            )
        )

    profile_titles = _profile_titles(root)
    assigned_titles = []
    for mode, mapping in project_modes.items():
        profile_title = mapping.get("profile_title")
        if profile_title not in profile_titles:
            issues.append(error("controls", project_path, f"{mode} references missing canonical profile: {profile_title}"))
        else:
            assigned_titles.append(profile_title)
        if not isinstance(mapping.get("field_label"), str) or not mapping["field_label"].strip():
            issues.append(error("controls", project_path, f"{mode} requires a non-empty field label."))
        if mapping.get("status") != "approved_target_pending_camera_verification":
            issues.append(error("controls", project_path, f"{mode} must remain an approved target pending camera verification."))
    if len(assigned_titles) == 3 and len(set(assigned_titles)) != 3:
        issues.append(error("controls", project_path, "C1, C2, and C3 must use three different profiles."))

    for profile_path in sorted((root / "10 Profiles").glob("*.yaml")):
        try:
            profile = load_yaml_checked(profile_path)
        except Exception:
            continue
        setup = ((profile.get("card") or {}).get("field_setup") or {}) if isinstance(profile, dict) else {}
        start = setup.get("start") if isinstance(setup, dict) else None
        if start not in project_modes:
            continue
        expected = project_modes[start].get("profile_title")
        if setup.get("source_profile") != expected:
            issues.append(
                error(
                    "controls",
                    profile_path,
                    f"card.field_setup.source_profile must match the global {start} assignment: {expected}",
                )
            )

    issues.extend(_canonical_setting_issues(root))
    return issues


def _status_issues(path, entries, label):
    issues = []
    if not isinstance(entries, list):
        return [error("controls", path, f"{label} must be a list.")]
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            issues.append(error("controls", path, f"{label} item {index} must be a mapping."))
            continue
        status = entry.get("status")
        if status not in EVIDENCE_STATUSES:
            issues.append(error("controls", path, f"{label} item {index} has invalid evidence status: {status}"))
    return issues


def _normalize_entries(entries):
    normalized = []
    for entry in entries or []:
        info = entry.get("info_details") or {}
        normalized_info = {
            str(key).lower().replace(" ", "_"): value
            for key, value in info.items()
        }
        normalized.append(
            {
                "control": entry.get("control"),
                "assignment": entry.get("assignment"),
                "operation": entry.get("operation"),
                "status": entry.get("status"),
                "info_details": normalized_info,
            }
        )
    return normalized


def _mode_mapping(data):
    if not isinstance(data, dict):
        return {}
    return {
        mode: data.get(mode)
        for mode in ("C1", "C2", "C3")
        if isinstance(data.get(mode), dict)
    }


def _profile_titles(root):
    titles = set()
    for path in sorted((root / "10 Profiles").glob("*.yaml")):
        try:
            profile = load_yaml_checked(path)
        except Exception:
            continue
        title = profile.get("title") if isinstance(profile, dict) else None
        if isinstance(title, str):
            titles.add(title)
    return titles


def _canonical_setting_issues(root):
    issues = []
    paths = [root / "00 Master" / "baseline.yaml"]
    paths.extend(sorted((root / "10 Profiles").glob("*.yaml")))
    for path in paths:
        try:
            data = load_yaml_checked(path)
        except Exception:
            continue
        for value in _scalar_values(data):
            replacement = DEPRECATED_SETTING_VALUES.get(value)
            if replacement:
                issues.append(error("controls", path, f"Use canonical setting value {replacement!r}, not {value!r}."))
    return issues


def _scalar_values(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from _scalar_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _scalar_values(child)
    else:
        yield value
