from collections import Counter
import re

from control_reference import (
    CONTROL_TABLE_PATTERN,
    card_reference_rows,
    inject_control_tables,
)

from .common import error, load_yaml_checked, resolved_paths


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

DEPRECATED_AF_WORKFLOW_PATTERN = re.compile(
    r"\bregistered[- ]AF\b|"
    r"\bAF presets?\b|"
    r"\bregister\s*/\s*recall shooting func(?:tion|\.)?\b",
    re.IGNORECASE,
)

DEPRECATED_AF_REPLACEMENT = (
    "Use the current control model: AF-ON temporarily selects Face + Tracking, "
    "AE Lock temporarily selects 1-Point AF, both maintain AF Operation and Servo AF "
    "characteristics, and C1-C3 are complete registered shooting environments."
)


def validate(paths_or_root):
    paths = resolved_paths(paths_or_root)
    root = paths.application_root
    issues = []
    project_path = paths.controls_file
    current_path = root / "data" / "canon_r5_custom_controls_current.yaml"
    external_pack = paths.profile_pack.mode == "external"

    try:
        project = load_yaml_checked(project_path)
    except Exception as exc:
        return [error("controls", project_path, f"Control record parse error: {exc}")]
    current = None
    if not external_pack:
        try:
            current = load_yaml_checked(current_path)
        except Exception as exc:
            return [error("controls", current_path, f"Control record parse error: {exc}")]

    issues.extend(_status_issues(project_path, project.get("controls"), "controls"))
    issues.extend(_status_issues(project_path, project.get("dials"), "dials"))
    project_controls = _normalize_entries(project.get("controls"))
    project_dials = _normalize_entries(project.get("dials"))
    project_modes = _mode_mapping(project.get("custom_shooting_modes"))
    if not external_pack:
        issues.extend(_status_issues(current_path, current.get("buttons"), "buttons"))
        issues.extend(_status_issues(current_path, current.get("dials"), "dials"))
        current_controls = _normalize_entries(current.get("buttons"))
        if project_controls != current_controls:
            issues.append(error("controls", current_path, "Button/control records do not agree with controls.yaml."))
        current_dials = _normalize_entries(current.get("dials"))
        if project_dials != current_dials:
            issues.append(error("controls", current_path, "Dial records do not agree with controls.yaml."))
        current_modes = _mode_mapping(current.get("custom_shooting_modes"))
        if project_modes != current_modes:
            issues.append(error("controls", current_path, "C1-C3 mappings do not agree with controls.yaml."))
    if set(project_modes) != {"C1", "C2", "C3"}:
        issues.append(error("controls", project_path, "C1-C3 mappings must define C1, C2, and C3."))

    if not external_pack:
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

    profile_ids = _profile_ids(paths.profiles_dir)
    assigned_ids = []
    for mode, mapping in project_modes.items():
        profile_id = mapping.get("profile_id")
        if profile_id not in profile_ids:
            issues.append(error("controls", project_path, f"{mode} references missing canonical profile_id: {profile_id}"))
        else:
            assigned_ids.append(profile_id)
        if not isinstance(mapping.get("field_label"), str) or not mapping["field_label"].strip():
            issues.append(error("controls", project_path, f"{mode} requires a non-empty field label."))
        if mapping.get("status") not in {"owner_confirmed", "approved_target_pending_camera_verification"}:
            issues.append(error("controls", project_path, f"{mode} must be owner-confirmed or pending camera verification."))
    if len(assigned_ids) == 3 and len(set(assigned_ids)) != 3:
        issues.append(error("controls", project_path, "C1, C2, and C3 must use three different profiles."))

    for profile_path in sorted(paths.profiles_dir.glob("*.yaml")):
        try:
            profile = load_yaml_checked(profile_path)
        except Exception:
            continue
        setup = ((profile.get("card") or {}).get("field_setup") or {}) if isinstance(profile, dict) else {}
        start = setup.get("start") if isinstance(setup, dict) else None
        if start not in project_modes:
            continue
        expected = project_modes[start].get("profile_id")
        if setup.get("source_card_id") != expected:
            issues.append(
                error(
                    "controls",
                    profile_path,
                    f"card.field_setup.source_card_id must match the global {start} assignment: {expected}",
                )
            )

    issues.extend(_canonical_setting_issues(paths))
    issues.extend(_deprecated_af_workflow_issues(paths))
    issues.extend(_derived_reference_issues(paths, project))
    return issues


def _derived_reference_issues(paths, project):
    root = paths.application_root
    issues = []
    card_path = paths.profiles_dir / "Camera Buttons.yaml"
    try:
        card = load_yaml_checked(card_path) or {}
        if card.get("reference_source") != "controls":
            issues.append(error("controls", card_path, "Camera Buttons must derive its rows from controls.yaml."))
        if "reference_settings" in card:
            issues.append(error("controls", card_path, "Derived Camera Buttons rows must not be authored in profile YAML."))
        if not card_reference_rows(paths):
            issues.append(error("controls", card_path, "Canonical control data produced no Camera Buttons rows."))
    except Exception as exc:
        issues.append(error("controls", card_path, f"Derived Camera Buttons readiness failed: {exc}"))

    markdown_paths = (
        root / "50 Field Guide" / "Appendices" / "Canon EOS R5 Custom Controls Current Configuration.md",
        root / "50 Field Guide" / "Setting Deep Dives" / "Custom Controls & Menus, Back-Button AF & Dial Strategies.md",
    )
    expected = Counter({"controls": 1, "dials": 1})
    for path in markdown_paths:
        try:
            source = path.read_text(encoding="utf-8")
            markers = Counter(item.casefold() for item in CONTROL_TABLE_PATTERN.findall(source))
            if markers != expected:
                issues.append(
                    error(
                        "controls",
                        path,
                        "Canonical control references require exactly one controls marker and one dials marker.",
                    )
                )
                continue
            rendered = inject_control_tables(source, paths)
            if CONTROL_TABLE_PATTERN.search(rendered):
                issues.append(error("controls", path, "Canonical control-table marker was not expanded."))
            for group in ("controls", "dials"):
                for entry in project.get(group) or []:
                    control = entry.get("control") if isinstance(entry, dict) else None
                    assignment = entry.get("assignment") if isinstance(entry, dict) else None
                    if control and control not in rendered:
                        issues.append(error("controls", path, f"Generated table is missing control: {control}"))
                    if assignment and assignment not in rendered:
                        issues.append(error("controls", path, f"Generated table is missing assignment: {assignment}"))
        except Exception as exc:
            issues.append(error("controls", path, f"Canonical control-table generation failed: {exc}"))
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


def _profile_ids(profiles_dir):
    values = set()
    for path in sorted(profiles_dir.glob("*.yaml")):
        try:
            profile = load_yaml_checked(path)
        except Exception:
            continue
        card_id = profile.get("card_id") if isinstance(profile, dict) else None
        if isinstance(card_id, str):
            values.add(card_id)
    return values


def _canonical_setting_issues(paths):
    issues = []
    source_paths = [paths.baseline_file]
    source_paths.extend(sorted(paths.profiles_dir.glob("*.yaml")))
    for path in source_paths:
        try:
            data = load_yaml_checked(path)
        except Exception:
            continue
        for value in _scalar_values(data):
            replacement = DEPRECATED_SETTING_VALUES.get(value)
            if replacement:
                issues.append(error("controls", path, f"Use canonical setting value {replacement!r}, not {value!r}."))
    return issues


def _deprecated_af_workflow_issues(paths_or_root):
    """Reject retired registered-AF operating language in active user-facing sources."""
    if hasattr(paths_or_root, "profile_pack"):
        paths = paths_or_root
        root = paths.application_root
        controls_file = paths.controls_file
        profiles_dir = paths.profiles_dir
        external = paths.profile_pack.mode == "external"
    else:
        paths = None
        root = paths_or_root
        controls_file = root / "controls.yaml"
        profiles_dir = root / "10 Profiles"
        external = False
    issues = []
    excluded = {
        root / "50 Field Guide" / "Appendices" / "Canon EOS R5 Official Icon Reference.md",
    }
    source_paths = [
        controls_file,
        root / "data" / "canon_r5_custom_controls_current.yaml",
    ]
    for directory, patterns in (
        (profiles_dir, ("*.yaml",)),
        (root / "50 Field Guide", ("*.md",)),
        (root / "WORKFLOWS", ("*.md",)),
        (root / "90 Testing", ("*.md",)),
    ):
        for pattern in patterns:
            source_paths.extend(directory.rglob(pattern))

    if external:
        source_paths.extend(
            [paths.registration_targets_file, paths.verification_status_file]
        )
    else:
        source_paths.extend((root / "90 Testing").rglob("*.yaml"))

    for path in sorted(set(source_paths)):
        if path in excluded or not path.is_file():
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append(error("controls", path, f"Could not inspect AF terminology: {exc}"))
            continue
        for line_number, line in enumerate(source.splitlines(), start=1):
            match = DEPRECATED_AF_WORKFLOW_PATTERN.search(line)
            if match:
                issues.append(
                    error(
                        "controls",
                        path,
                        f"Line {line_number} uses deprecated AF workflow terminology "
                        f"{match.group(0)!r}. {DEPRECATED_AF_REPLACEMENT}",
                    )
                )
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
