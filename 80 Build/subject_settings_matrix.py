import json
import os
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess

from baseline import merge
from html_renderer import (
    LABEL,
    af_method_not_used,
    automatic_servo_af_case,
    high_speed_display_relevant,
    iso_display_value,
    manual_focus,
    stabilization_system_row,
    subject_switching_supported,
)
from validators.common import flatten_paths, load_yaml_checked
from spreadsheet_ooxml import enable_automatic_row_heights, ensure_freeze_panes, hide_columns
from spreadsheet_revisions import short_fingerprint, source_fingerprint, workbook_revision


DEFAULT_NODE = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
DEFAULT_NODE_MODULES = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
DISPLAY_KEY = {
    "exposure.iso.value": "exposure.iso.mode",
    "exposure.auto_iso.maximum": "exposure.iso.mode",
    "stabilization.lens_is": "stabilization.ibis",
}


def generate_subject_settings_matrix(paths):
    """Create the optional Excel matrix for all authored subject profiles."""
    profiles = _subject_profiles(paths)
    baseline = load_yaml_checked(paths.baseline_file) or {}
    access = load_yaml_checked(paths.setting_access_file) or {}
    access = access.get("setting_access") or {}
    layouts = load_yaml_checked(paths.spreadsheet_layouts_file) or {}
    layout = ((layouts.get("workbooks") or {}).get("matrix") or {})
    tracker = load_yaml_checked(paths.verification_tracker_source_file) or {}
    registration = tracker.get("registration") or {}
    registered_profiles = _registered_profiles(
        registration,
        baseline.get("defaults") or {},
        ((layout.get("registered_profiles") or {}).get("keys") or []),
    )
    ordered_keys = _summary_keys(paths, profiles, access)
    rows = _summary_rows(
        ordered_keys,
        profiles,
        registered_profiles,
        baseline.get("defaults") or {},
        access,
    )

    paths.reports_output_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = paths.reports_output_dir / ".subject-settings-runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    modules_dir = _artifact_modules(paths)
    node_link = runtime_dir / "node_modules"
    if node_link.is_symlink() or node_link.exists():
        if node_link.is_dir() and not node_link.is_symlink():
            shutil.rmtree(node_link)
        else:
            node_link.unlink()
    node_link.symlink_to(modules_dir, target_is_directory=True)

    payload_path = runtime_dir / "payload.json"
    preview_path = runtime_dir / "preview.png"
    defaults_preview_path = runtime_dir / "defaults-preview.png"
    payload = {
        "output": str(paths.subject_settings_summary_file),
        "preview": str(preview_path),
        "defaults_preview": str(defaults_preview_path),
        "runtime_dir": str(runtime_dir),
        "profiles": [
            {
                "title": profile["title"],
                "release": profile["release"],
                "card_start": _card_start_label(
                    profile.get("field_setup") or {}, profile["title"], profile.get("source_profile") or ""
                ),
            }
            for profile in profiles
        ],
        "registered_profiles": [
            {
                "key": profile["key"],
                "heading": profile["heading"],
            }
            for profile in registered_profiles
        ],
        "rows": rows,
        "layout": layout,
        "shared_layout": layouts.get("shared") or {},
        "workbook_revision": workbook_revision(paths, "matrix"),
        "source_fingerprint": source_fingerprint(paths, "matrix"),
        "release_label": (
            f"Workbook revision {workbook_revision(paths, 'matrix')} • "
            f"Source {short_fingerprint(source_fingerprint(paths, 'matrix'))} • "
            f"Generated {datetime.now().astimezone().date().isoformat()}"
        ),
    }
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    command = [
        _node_binary(),
        str(paths.root / "80 Build" / "render_subject_settings_matrix.mjs"),
        str(payload_path),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
    finally:
        payload_path.unlink(missing_ok=True)
    header_row = (layout.get("card_start_controls") or {})["row"] + 1
    defaults_layout = (layout.get("registered_profiles") or {})["defaults_sheet"]
    enable_automatic_row_heights(
        paths.subject_settings_summary_file,
        {
            layout["worksheet"]: [(header_row, header_row + len(rows))],
            defaults_layout["worksheet"]: [(2, 2 + len(rows))],
        },
    )
    excel_layout = layout.get("excel") or {}
    ensure_freeze_panes(
        paths.subject_settings_summary_file,
        layout["worksheet"],
        frozen_rows=excel_layout["freeze_rows"],
        frozen_columns=excel_layout["freeze_columns"],
    )
    defaults_excel_layout = defaults_layout.get("excel") or {}
    ensure_freeze_panes(
        paths.subject_settings_summary_file,
        defaults_layout["worksheet"],
        frozen_rows=defaults_excel_layout["freeze_rows"],
        frozen_columns=defaults_excel_layout["freeze_columns"],
    )
    visible_column_count = 3 + len(registered_profiles) + 1 + len(profiles) + 2
    helper_column_count = len(registered_profiles) + 1 + len(profiles)
    hide_columns(
        paths.subject_settings_summary_file,
        layout["worksheet"],
        first_column=visible_column_count + 1,
        last_column=visible_column_count + helper_column_count,
    )
    defaults_first_helper_column = visible_column_count + 1
    defaults_last_helper_column = defaults_first_helper_column + len(registered_profiles) - 1
    hide_columns(
        paths.subject_settings_summary_file,
        defaults_layout["worksheet"],
        first_column=2 + len(registered_profiles),
        last_column=defaults_last_helper_column,
    )
    inspect_sidecar = Path(f"{paths.subject_settings_summary_file}.inspect.ndjson")
    inspect_sidecar.unlink(missing_ok=True)
    return {
        "XLSX": 1 if paths.subject_settings_summary_file.exists() else 0,
        "subject_settings_preview": preview_path,
        "subject_settings_defaults_preview": defaults_preview_path,
    }


generate_subject_settings_summary = generate_subject_settings_matrix


def remove_subject_settings_matrix(paths):
    for path in (
        paths.subject_settings_summary_file,
        paths.subject_settings_numbers_file,
        paths.subject_settings_download_manifest_file,
        paths.reports_output_dir / ".subject-settings-runtime",
    ):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists() or path.is_symlink():
            path.unlink()


remove_subject_settings_summary = remove_subject_settings_matrix


def _subject_profiles(paths):
    profiles = []
    all_profiles = {}
    for profile_path in sorted(paths.profiles_dir.glob("*.yaml")):
        all_profiles[profile_path.stem] = load_yaml_checked(profile_path) or {}
    for profile_path in sorted(paths.profiles_dir.glob("*.yaml")):
        profile = all_profiles[profile_path.stem]
        if profile.get("card_type") == "reference":
            continue
        category = profile.get("display_category") or "subject"
        if category != "subject":
            continue
        profiles.append(
            {
                "title": profile.get("title") or profile_path.stem,
                "display_order": profile.get("display_order", 100),
                "release": (profile.get("metadata") or {}).get("release") is True,
                "field_setup": (profile.get("card") or {}).get("field_setup") or {},
                "source_profile": _source_title((profile.get("card") or {}).get("field_setup") or {}, all_profiles),
                "overrides": profile.get("overrides") or {},
            }
        )
    return sorted(profiles, key=lambda item: (item["display_order"], item["title"].lower()))


def _card_start_label(field_setup, profile_title="", source_profile=""):
    start = field_setup.get("start")
    menu_names = [
        menu.get("name")
        for menu in field_setup.get("my_menus") or []
        if isinstance(menu, dict) and menu.get("name")
    ]
    if field_setup.get("access_only") is True:
        return f"{profile_title} + " + " + ".join(menu_names) if menu_names else profile_title
    if not start or not source_profile:
        return "No Cx + " + " + ".join(menu_names) if menu_names else ""
    route = f"{start} {source_profile}"
    if menu_names:
        route += " + " + " + ".join(menu_names)
    return route


def _source_title(field_setup, profiles):
    source_card_id = field_setup.get("source_card_id")
    for name, profile in profiles.items():
        if profile.get("card_id") == source_card_id:
            return profile.get("title") or name
    return ""


def _summary_keys(paths, profiles, access):
    layout = load_yaml_checked(paths.card_layout_file) or {}
    card_layout = layout.get("card_layout") or {}
    keys = {
        entry.get("key")
        for entry in card_layout.get("always_show") or []
        if isinstance(entry, dict) and entry.get("key")
    }
    for profile in profiles:
        keys.update(flatten_paths(profile["overrides"]))
    normalized = {DISPLAY_KEY.get(key, key) for key in keys} | set(access)
    return [key for key in card_layout.get("display_order") or [] if key in normalized]


def _summary_rows(ordered_keys, profiles, registered_profiles, defaults, access):
    rows = []
    for card_order, key in enumerate(ordered_keys, start=1):
        access_entry = access[key]
        values = []
        for profile in profiles:
            merged = merge(defaults, profile["overrides"])
            values.append(_spreadsheet_value(_summary_value(key, merged)))
        rows.append(
            {
                "key": key,
                "setting": _setting_label(key),
                "best_access": access_entry["best_access"],
                "menu_location": access_entry["menu_location"],
                "default_value": _spreadsheet_value(_summary_value(key, defaults)),
                "registered_values": [
                    _spreadsheet_value(_summary_value(key, profile["merged"]))
                    for profile in registered_profiles
                ],
                "values": values,
                "card_order": card_order,
                "rapid_order": access_entry["rapid_order"],
            }
        )
    return rows


def _spreadsheet_value(value):
    if isinstance(value, str) and re.fullmatch(r"-?\d+", value):
        return int(value)
    if isinstance(value, str) and re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def _registered_profiles(registration, defaults, configured_keys):
    definitions = {
        profile["key"]: profile
        for profile in registration.get("profiles") or []
        if isinstance(profile, dict) and profile.get("key")
    }
    missing = [key for key in configured_keys if key not in definitions]
    if missing:
        raise ValueError(f"Missing configured Cx registration profiles: {missing}")
    profiles = []
    for key in configured_keys:
        overrides = {}
        for row in registration.get("rows") or []:
            baseline_key = row.get("baseline_key")
            if baseline_key and row.get(key) not in (None, ""):
                _apply_registration_value(overrides, baseline_key, row[key])
        profiles.append(
            {
                "key": key,
                "heading": definitions[key]["heading"],
                "merged": merge(defaults, overrides),
            }
        )
    return profiles


def _apply_registration_value(overrides, baseline_key, raw_value):
    if isinstance(raw_value, bool):
        value = "On" if raw_value else "Off"
    else:
        value = str(raw_value).split(";", 1)[0].strip()
    if baseline_key == "exposure.iso.mode":
        if re.fullmatch(r"\d+", value):
            _set_nested(overrides, "exposure.iso.mode", "Fixed")
            _set_nested(overrides, "exposure.iso.value", value)
        else:
            _set_nested(overrides, baseline_key, value)
        return
    if baseline_key == "exposure.auto_iso.maximum":
        match = re.match(r"\d+", value)
        value = match.group(0) if match else value
    _set_nested(overrides, baseline_key, value)


def _set_nested(target, dotted_key, value):
    current = target
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def _summary_value(key, merged):
    fields = _flatten(merged)
    if key == "autofocus.servo_af_case" and fields.get("autofocus.operation") != "Servo AF":
        return "Not Used"
    if key in {"autofocus.tracking_sensitivity", "autofocus.accel_decel_tracking"}:
        if fields.get("autofocus.operation") != "Servo AF":
            return "Not Used"
        if automatic_servo_af_case(fields):
            return "Auto"
    if key == "autofocus.switching_tracked_subjects" and not subject_switching_supported(fields):
        return "Not Used"
    if key == "display.high_speed_display" and not high_speed_display_relevant(fields):
        return "Not Used"
    if manual_focus(fields) and key in {
        "autofocus.method",
        "autofocus.subject_detection",
        "autofocus.eye_detection",
    }:
        return "Not Used"
    if af_method_not_used(fields) and key in {
        "autofocus.subject_detection",
        "autofocus.eye_detection",
    }:
        return "Not Used"
    if key == "exposure.iso.mode":
        return _display(iso_display_value(fields))
    if key == "stabilization.ibis":
        row = stabilization_system_row(
            {"stabilization.ibis", "stabilization.lens_is"},
            fields,
        )
        return _display(row["value"] if row else None)
    return _display(fields.get(key))


def _setting_label(key):
    if key == "autofocus.tracking_sensitivity":
        return "Tracking Sensitivity"
    if key == "stabilization.ibis":
        return "IBIS / Lens IS"
    return LABEL[key]


def _display(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "On" if value else "Off"
    return str(value)


def _flatten(data, prefix=""):
    result = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten(value, path))
        else:
            result[path] = value
    return result


def _artifact_modules(paths):
    configured = os.environ.get("PRS_ARTIFACT_TOOL_NODE_MODULES")
    candidates = [
        Path(configured).expanduser() if configured else None,
        paths.root / "node_modules",
        Path(DEFAULT_NODE_MODULES),
    ]
    for candidate in candidates:
        if candidate and (candidate / "@oai" / "artifact-tool").is_dir():
            return candidate.resolve()
    raise RuntimeError(
        "The optional settings-summary build requires @oai/artifact-tool. "
        "Set PRS_ARTIFACT_TOOL_NODE_MODULES to the node_modules directory that contains it."
    )


def _node_binary():
    return os.environ.get("NODE") or shutil.which("node") or DEFAULT_NODE
