"""Resolve authored profiles and compare them with read-only camera evidence."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

import yaml

from asset_manager import ProjectPaths
from baseline import merge
from html_renderer import (
    LABEL,
    card_setting_order,
    field_setup_value_colors,
    settings_rows,
)
from my_menu_colors import load_my_menu_colors, menu_color
from utilities import flatten


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATHS = ProjectPaths(PROJECT_ROOT)

COMBINED_PATHS = {
    "autofocus.tracking_sensitivity": [
        "autofocus.tracking_sensitivity",
        "autofocus.accel_decel_tracking",
    ],
    "exposure.iso.mode": [
        "exposure.iso.mode",
        "exposure.iso.value",
        "exposure.auto_iso.maximum",
    ],
    "stabilization.ibis": [
        "stabilization.image_stabilization.mode",
        "stabilization.ibis",
        "stabilization.lens_is",
    ],
}

STATUS_PRIORITY = {
    "difference": 0,
    "unreadable": 1,
    "conditional": 2,
    "manual_confirmation_needed": 3,
    "equivalent": 4,
    "match": 5,
    "not_applicable": 6,
}

REFERENCE_GUIDANCE_PATHS = {
    "image.long_exposure_noise_reduction.note",
    "lens.aperture.note",
    "lens.aperture.strategy",
    "shutter.efcs.status",
}


def list_profiles():
    loaded_profiles = []
    titles_by_card_id = {}
    for source in sorted(PATHS.profiles_dir.glob("*.yaml"), key=lambda item: item.stem.casefold()):
        data = _load_yaml(source)
        loaded_profiles.append((source, data))
        if data.get("card_id"):
            titles_by_card_id[data["card_id"]] = data.get("title") or source.stem

    profiles = []
    for source, data in loaded_profiles:
        if data.get("card_type") == "reference":
            continue
        title = data.get("title") or source.stem
        field_setup = ((data.get("card") or {}).get("field_setup") or {})
        start = field_setup.get("start")
        base_title = titles_by_card_id.get(field_setup.get("source_card_id"))
        foundation_title = f"{start} – {base_title}" if start and base_title else None
        display_title = (
            foundation_title
            if foundation_title and data.get("card_id") == field_setup.get("source_card_id")
            else f"{foundation_title} → {title}"
            if foundation_title
            else title
        )
        profiles.append(
            {
                "name": source.stem,
                "title": title,
                "display_title": display_title,
                "foundation": foundation_title,
                "display_category": data.get("display_category") or "subject",
            }
        )
    return profiles


def compare_profile(profile_name, properties):
    profile_info = next((item for item in list_profiles() if item["name"] == profile_name), None)
    if profile_info is None:
        raise ValueError(f"Unknown profile: {profile_name}")

    profile = _load_yaml(PATHS.profile_file(profile_name))
    baseline = _load_yaml(PATHS.baseline_file)
    merged = merge(baseline["defaults"], profile.get("overrides") or {})
    merged_fields = flatten(merged)
    properties_by_path = _properties_by_path(properties)
    access_config = (_load_yaml(PATHS.setting_access_file) or {}).get("setting_access") or {}
    menu_access = _saved_menu_access()
    value_colors = field_setup_value_colors(profile, merged, PATHS)

    represented = set()
    card_findings = []
    for row in settings_rows(profile, merged, PATHS):
        paths = [path for path in COMBINED_PATHS.get(row["key"], [row["key"]]) if path in merged_fields]
        represented.update(paths)
        items = [
            _compare_path(path, merged_fields[path], merged_fields, properties_by_path)
            for path in paths
        ]
        card_findings.append(
            {
                "key": row["key"],
                "label": row["label"],
                "expected": str(row["value"]),
                "expected_color": value_colors.get(row["key"]),
                "actual": _card_actual(items),
                "actual_raw": _card_actual_raw(items),
                "status": _combined_status(items),
                "items": items,
                "access_paths": _access_paths(paths, access_config, menu_access),
            }
        )

    ordered_paths = [path for path in card_setting_order(PATHS) if path in merged_fields]
    ordered_paths.extend(sorted(set(merged_fields) - set(ordered_paths)))
    additional_findings = [
        {
            **_compare_path(path, merged_fields[path], merged_fields, properties_by_path),
            "expected_color": value_colors.get(path),
            "access_paths": _access_paths([path], access_config, menu_access),
        }
        for path in ordered_paths
        if path not in represented
    ]

    statuses = Counter(item["status"] for item in card_findings + additional_findings)
    return {
        "profile": profile_info,
        "read_only": True,
        "write_testing_performed": False,
        "ordering": "subject_profile_card_then_additional",
        "card_findings": card_findings,
        "additional_findings": additional_findings,
        "summary": {
            "card_rows": len(card_findings),
            "additional_settings": len(additional_findings),
            "statuses": dict(sorted(statuses.items())),
        },
    }


def _load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _properties_by_path(properties):
    mapped = {}
    for item in properties:
        for path in item.get("profile_paths") or []:
            mapped[path] = item
    return mapped


def _saved_menu_access():
    mapped = {}
    saved_tabs = (_load_yaml(PATHS.my_menu_file) or {}).get("tabs") or []
    catalog = _load_yaml(PATHS.root / "80 Build" / "profile_editor" / "canon_options.yaml") or {}
    items = {
        item["id"]: item
        for section in catalog.get("reference_sections") or []
        for item in section.get("items") or []
        if isinstance(item, dict) and item.get("id")
    }
    colors = load_my_menu_colors(PATHS)
    for tab_order, tab in enumerate(saved_tabs):
        tab_name = str(tab.get("name") or "").strip()
        for item_order, item_id in enumerate(tab.get("items") or []):
            path = (items.get(item_id) or {}).get("setting_path")
            if not path:
                continue
            mapped.setdefault(path, []).append(
                {
                    "kind": "my_menu",
                    "label": f"My Menu → {tab_name}",
                    "color": menu_color(colors, tab_name, tab_order),
                    "tab": tab_name,
                    "tab_order": tab_order,
                    "item_order": item_order,
                }
            )
    return mapped


def _access_paths(paths, access_config, menu_access):
    """Return reviewed routes in practical fastest-path order."""
    ranked = []
    for path in paths:
        if path in REFERENCE_GUIDANCE_PATHS:
            ranked.append(
                (50, {"kind": "reference", "label": "Reference guidance — not a camera setting"})
            )
            continue
        access = access_config.get(path) or {}
        for label in _segments(access.get("best_access")):
            normalized = label.casefold()
            if normalized.startswith("mm-") or "c1-c3 registered profile" in normalized:
                continue
            if normalized == "set once":
                continue
            if "menu" in normalized and "q screen" not in normalized:
                continue
            rank = 20 if "q screen" in normalized or normalized.startswith("q ") else 10
            ranked.append((rank, {"kind": "quick" if rank == 20 else "direct", "label": label}))
        for route in menu_access.get(path) or []:
            ranked.append((30, route))
        for label in _segments(access.get("menu_location")):
            normalized = label.casefold()
            if normalized.startswith("my menu") or ">" not in label:
                continue
            ranked.append((40, {"kind": "menu", "label": label}))

    unique = []
    seen = set()
    for _, route in sorted(ranked, key=lambda item: item[0]):
        key = (route["kind"], _normalize(route["label"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(route)
    return unique


def _segments(value):
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def _compare_path(path, expected, merged_fields, properties_by_path):
    property_item = properties_by_path.get(path)
    finding = {
        "path": path,
        "label": LABEL.get(path, _path_label(path)),
        "expected": "Not set" if expected is None else str(expected),
        "actual": None,
        "actual_raw": None,
        "status": "manual_confirmation_needed",
        "evidence_method": None,
        "reason": "No reviewed SDK readback mapping is available.",
    }
    if path in REFERENCE_GUIDANCE_PATHS:
        finding.update(
            status="not_applicable",
            evidence_method="reference_guidance",
            reason="This is authored reference guidance, not a camera setting.",
        )
        return finding
    if property_item is None:
        return finding

    finding["actual"] = property_item.get("value_display")
    finding["actual_raw"] = property_item.get("value_raw")
    finding["evidence_method"] = property_item.get("read_status")
    if property_item.get("read_status") != "sdk_verified":
        finding["status"] = "unreadable"
        finding["reason"] = "The reviewed SDK property did not return a usable value."
        return finding
    if property_item.get("capability_classification") == "conditional":
        finding["status"] = "conditional"
        finding["reason"] = "The profile target requires shooting-mode, lens, range, or field context."
        return finding

    status = _direct_status(path, expected, merged_fields, property_item)
    finding["status"] = status
    finding["reason"] = {
        "match": "The camera readback matches the selected profile.",
        "equivalent": "The camera uses a reviewed equivalent representation.",
        "difference": "The camera readback differs from the selected profile.",
        "not_applicable": "This value is not applicable in the selected profile context.",
    }[status]
    return finding


def _direct_status(path, expected, merged_fields, property_item):
    raw = property_item.get("value_raw")
    actual = property_item.get("value_display")
    if path == "exposure.iso.mode":
        matches = (str(expected).casefold() == "auto" and raw == 0) or (
            str(expected).casefold() == "fixed" and raw not in {None, 0}
        )
        return "match" if matches else "difference"
    if path == "exposure.iso.value":
        if str(merged_fields.get("exposure.iso.mode")).casefold() == "auto" and expected is None:
            return "not_applicable"
        return "match" if _normalize(actual) == _normalize(f"ISO {expected}") else "difference"
    if path == "image.white_balance" and _normalize(expected) == "awb" and _normalize(actual).startswith("awb"):
        return "equivalent" if _normalize(actual) != "awb" else "match"

    expected_normalized = _normalized_alias(expected)
    actual_normalized = _normalized_alias(actual)
    if expected_normalized == actual_normalized:
        return "match"
    return "difference"


def _normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()


def _normalized_alias(value):
    normalized = _normalize(value)
    return {
        "single shot": "single shooting",
        "enabled": "enable",
        "disabled": "disable",
    }.get(normalized, normalized)


def _combined_status(items):
    return min((item["status"] for item in items), key=lambda status: STATUS_PRIORITY[status])


def _card_actual(items):
    reported = [item for item in items if item.get("actual") is not None]
    if not reported:
        return "Manual confirmation needed"
    if len(items) == 1:
        return str(reported[0]["actual"])
    return "; ".join(f"{item['label']}: {item['actual']}" for item in reported)


def _card_actual_raw(items):
    reported = [item for item in items if item.get("actual_raw") is not None]
    if not reported:
        return None
    if len(items) == 1:
        return reported[0]["actual_raw"]
    return "; ".join(f"{item['label']}: {item['actual_raw']}" for item in reported)


def _path_label(path):
    return path.rsplit(".", 1)[-1].replace("_", " ").title()
