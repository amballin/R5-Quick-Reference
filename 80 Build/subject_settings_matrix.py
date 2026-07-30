import json
import os
from pathlib import Path
import shutil
import subprocess

from baseline import merge
from html_renderer import (
    LABEL,
    af_method_not_used,
    iso_display_value,
    manual_focus,
    stabilization_system_row,
)
from validators.common import flatten_paths, load_yaml_checked
from spreadsheet_ooxml import ensure_freeze_panes


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
    ordered_keys = _summary_keys(paths, profiles, access)
    rows = _summary_rows(ordered_keys, profiles, baseline.get("defaults") or {}, access)

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
    payload = {
        "output": str(paths.subject_settings_summary_file),
        "preview": str(preview_path),
        "runtime_dir": str(runtime_dir),
        "profiles": [
            {
                "title": profile["title"],
                "release": profile["release"],
            }
            for profile in profiles
        ],
        "rows": rows,
        "layout": layout,
        "shared_layout": layouts.get("shared") or {},
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
    excel_layout = layout.get("excel") or {}
    ensure_freeze_panes(
        paths.subject_settings_summary_file,
        layout["worksheet"],
        frozen_rows=excel_layout["freeze_rows"],
        frozen_columns=excel_layout["freeze_columns"],
    )
    inspect_sidecar = Path(f"{paths.subject_settings_summary_file}.inspect.ndjson")
    inspect_sidecar.unlink(missing_ok=True)
    return {
        "XLSX": 1 if paths.subject_settings_summary_file.exists() else 0,
        "subject_settings_preview": preview_path,
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
    for profile_path in sorted(paths.profiles_dir.glob("*.yaml")):
        profile = load_yaml_checked(profile_path) or {}
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
                "overrides": profile.get("overrides") or {},
            }
        )
    return sorted(profiles, key=lambda item: (item["display_order"], item["title"].lower()))


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


def _summary_rows(ordered_keys, profiles, defaults, access):
    rows = []
    for card_order, key in enumerate(ordered_keys, start=1):
        access_entry = access[key]
        values = []
        for profile in profiles:
            merged = merge(defaults, profile["overrides"])
            values.append(_summary_value(key, merged))
        rows.append(
            {
                "key": key,
                "setting": _setting_label(key),
                "best_access": access_entry["best_access"],
                "menu_location": access_entry["menu_location"],
                "default_value": _summary_value(key, defaults),
                "values": values,
                "card_order": card_order,
                "rapid_order": access_entry["rapid_order"],
            }
        )
    return rows


def _summary_value(key, merged):
    fields = _flatten(merged)
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
