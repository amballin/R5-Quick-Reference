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


def list_profiles(paths=PATHS):
    loaded_profiles = []
    titles_by_card_id = {}
    for source in sorted(paths.profiles_dir.glob("*.yaml"), key=lambda item: item.stem.casefold()):
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
        is_foundation = bool(
            foundation_title and data.get("card_id") == field_setup.get("source_card_id")
        )
        display_title = (
            foundation_title
            if is_foundation
            else f"{foundation_title} → {title}"
            if foundation_title
            else title
        )
        selector_label = (
            f"{start} ({base_title})"
            if is_foundation
            else f"{title} ← {start} ({base_title})"
            if foundation_title
            else f"{title} ← No Cx"
        )
        profiles.append(
            {
                "name": source.stem,
                "title": title,
                "display_title": display_title,
                "selector_label": selector_label,
                "foundation": foundation_title,
                "foundation_slot": start,
                "is_foundation": is_foundation,
                "display_category": data.get("display_category") or "subject",
            }
        )
    profiles.sort(
        key=lambda item: (
            0 if item["is_foundation"] else 1,
            int(item["foundation_slot"][1:])
            if item["is_foundation"] and str(item["foundation_slot"]).startswith("C")
            else item["title"].casefold(),
        )
    )
    return profiles


def compare_profile(profile_name, properties, context_choices=None):
    context_choices = context_choices or {}
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
            _compare_path(
                path,
                merged_fields[path],
                merged_fields,
                properties_by_path,
                context_choices,
            )
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
                "context_prompts": [
                    item["context_prompt"] for item in items if item.get("context_prompt")
                ],
                "access_paths": _access_paths(paths, access_config, menu_access),
            }
        )

    ordered_paths = [path for path in card_setting_order(PATHS) if path in merged_fields]
    ordered_paths.extend(sorted(set(merged_fields) - set(ordered_paths)))
    additional_findings = [
        {
            **_compare_path(
                path,
                merged_fields[path],
                merged_fields,
                properties_by_path,
                context_choices,
            ),
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


def _compare_path(path, expected, merged_fields, properties_by_path, context_choices):
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
        evaluation = _conditional_evaluation(
            path,
            expected,
            finding["actual"],
            context_choices.get(path),
        )
        finding["status"] = evaluation["status"]
        finding["reason"] = evaluation["reason"]
        if evaluation.get("context_prompt"):
            finding["context_prompt"] = evaluation["context_prompt"]
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


def _conditional_status(path, expected, actual, context_choice=None):
    evaluation = _conditional_evaluation(path, expected, actual, context_choice)
    return evaluation["status"], evaluation["reason"]


def _conditional_evaluation(path, expected, actual, context_choice=None):
    expected_text = str(expected or "").strip()
    actual_text = str(actual or "").strip()
    if _normalized_alias(expected_text) == _normalized_alias(actual_text):
        return {
            "status": "match",
            "reason": "The camera readback matches the selected profile.",
        }

    prompt = _context_prompt(path, expected_text, context_choice)
    if prompt:
        selected = next(
            (option for option in prompt["options"] if option["id"] == context_choice),
            None,
        )
        prompt["selected"] = selected["id"] if selected else None
        prompt["selected_target"] = selected["target"] if selected else None
        if selected is None:
            reason = (
                "The supplied contextual choice is not an authored option; choose one of the listed conditions."
                if context_choice
                else "Choose the applicable authored context before Camera Lab evaluates this target."
            )
            return {"status": "conditional", "reason": reason, "context_prompt": prompt}
        status, reason = _compare_conditional_target(path, selected["target"], actual_text)
        return {
            "status": status,
            "reason": f"Using the authored {selected['label']} target ({selected['target']}). {reason}",
            "context_prompt": prompt,
        }

    status, reason = _compare_conditional_target(path, expected_text, actual_text)
    return {"status": status, "reason": reason}


def _compare_conditional_target(path, expected, actual):

    if path == "exposure.exposure_compensation":
        return _compare_compensation_target(expected, actual)
    if path == "lens.aperture.target":
        return _compare_aperture_target(expected, actual)
    if path == "shutter.target":
        return _compare_shutter_target(expected, actual)
    return "conditional", "The profile target requires shooting-mode, lens, range, or field context."


def _context_prompt(path, expected, selected):
    clauses = [clause.strip() for clause in str(expected or "").split(";") if clause.strip()]
    if len(clauses) < 2:
        return None

    options = []
    for clause in clauses:
        parsed = _contextual_clause(path, clause)
        if parsed is None:
            return None
        target, label = parsed
        options.append(
            {
                "id": re.sub(r"[^a-z0-9]+", "-", label.casefold()).strip("-"),
                "label": label,
                "target": target,
                "authored_clause": clause,
            }
        )
    if len({option["id"] for option in options}) != len(options):
        return None

    labels = {option["label"].casefold() for option in options}
    if labels <= {"single", "groups"}:
        question = "Which subject grouping applies?"
    elif labels <= {"outdoor", "indoor"}:
        question = "Which lighting condition applies?"
    elif labels <= {"portraits", "action"}:
        question = "Which subject situation applies?"
    else:
        question = "Which authored field condition applies?"
    return {
        "path": path,
        "question": question,
        "selected": selected,
        "options": options,
    }


def _contextual_clause(path, clause):
    patterns = {
        "lens.aperture.target": r"(f\s*/\s*\d+(?:\.\d+)?(?:\s*[–-]\s*f\s*/\s*\d+(?:\.\d+)?)?)\s+(.+)",
        "shutter.target": r"((?:\d+(?:\.\d+)?/\d+(?:\.\d+)?)(?:\s*[–-]\s*\d+(?:\.\d+)?/\d+(?:\.\d+)?)?\+?)\s+(.+)",
    }
    match = re.fullmatch(patterns.get(path, r"(?!)"), clause, flags=re.IGNORECASE)
    if not match:
        return None
    target, label = (part.strip() for part in match.groups())
    return target, label


def _compare_compensation_target(expected, actual):
    actual_value = _parse_compensation(actual)
    expected_value = _parse_compensation(expected)
    if expected_value is not None:
        if actual_value is None:
            return "conditional", "The camera exposure-compensation value could not be interpreted safely."
        return _numeric_result(expected_value, actual_value, expected, actual, "exposure compensation")

    bounds = _compensation_range(expected)
    if bounds is not None:
        if actual_value is None:
            return "conditional", "The camera exposure-compensation value could not be interpreted safely."
        if min(bounds) <= actual_value <= max(bounds):
            return "equivalent", "The camera exposure compensation is within the profile's accepted range."
        return "difference", "The camera exposure compensation is outside the profile's accepted range."

    return "conditional", "The exposure-compensation target requires field or background context."


def _compare_aperture_target(expected, actual):
    expected_value = _parse_aperture(expected)
    actual_value = _parse_aperture(actual)
    if expected_value is not None:
        if actual_value is None:
            return "difference", "The profile requires a fixed aperture, but the camera reports Auto."
        return _numeric_result(expected_value, actual_value, expected, actual, "aperture")

    bounds = _simple_aperture_range(expected)
    if bounds is not None:
        if actual_value is None:
            return "difference", "The profile requires an aperture range, but the camera reports Auto."
        if min(bounds) <= actual_value <= max(bounds):
            return "equivalent", "The camera aperture is within the profile's accepted range."
        return "difference", "The camera aperture is outside the profile's accepted range."

    return "conditional", "The aperture target contains subject, grouping, bracketing, lens, or field context that Camera Lab cannot choose automatically."


def _compare_shutter_target(expected, actual):
    expected_value = _parse_shutter_seconds(expected)
    actual_value = _parse_shutter_seconds(actual)
    if expected_value is not None:
        if actual_value is None:
            return "difference", "The profile requires a fixed shutter speed, but the camera reports Auto or an unrecognized value."
        return _numeric_result(expected_value, actual_value, expected, actual, "shutter speed")

    bounds = _simple_shutter_range(expected)
    if bounds is not None:
        if actual_value is None:
            return "difference", "The profile requires a shutter-speed range, but the camera reports Auto or an unrecognized value."
        if min(bounds) <= actual_value <= max(bounds):
            return "equivalent", "The camera shutter speed is within the profile's accepted range."
        return "difference", "The camera shutter speed is outside the profile's accepted range."

    minimum_speed = _minimum_shutter_speed(expected)
    if minimum_speed is not None:
        if actual_value is None:
            return "difference", "The profile requires a minimum shutter speed, but the camera reports Auto or an unrecognized value."
        if actual_value <= minimum_speed:
            return "equivalent", "The camera shutter speed meets or exceeds the profile's authored minimum."
        return "difference", "The camera shutter speed is slower than the profile's authored minimum."

    return "conditional", "The shutter target contains subject, lighting, or field context that Camera Lab cannot choose automatically."


def _numeric_result(expected_value, actual_value, expected, actual, setting):
    if abs(expected_value - actual_value) > 1e-9:
        return "difference", f"The camera {setting} differs from the selected profile."
    if _normalized_alias(expected) == _normalized_alias(actual):
        return "match", "The camera readback matches the selected profile."
    return "equivalent", f"The camera {setting} uses an equivalent numeric representation."


def _parse_compensation(value):
    text = str(value or "").strip().replace("−", "-")
    mixed = re.fullmatch(r"([+-]?)(\d+)\s+(\d+)/(\d+)", text)
    if mixed:
        sign, whole, numerator, denominator = mixed.groups()
        number = int(whole) + int(numerator) / int(denominator)
        return -number if sign == "-" else number
    fraction = re.fullmatch(r"([+-]?)(\d+)/(\d+)", text)
    if fraction:
        sign, numerator, denominator = fraction.groups()
        number = int(numerator) / int(denominator)
        return -number if sign == "-" else number
    decimal = re.fullmatch(r"([+-]?)(\d+(?:\.\d+)?)", text)
    if decimal:
        sign, number = decimal.groups()
        parsed = float(number)
        return -parsed if sign == "-" else parsed
    return None


def _compensation_range(value):
    parts = re.split(r"\s+(?:to|–)\s+", str(value or "").strip(), maxsplit=1, flags=re.IGNORECASE)
    if len(parts) != 2:
        return None
    bounds = tuple(_parse_compensation(part) for part in parts)
    return bounds if all(bound is not None for bound in bounds) else None


def _parse_aperture(value):
    match = re.fullmatch(r"f\s*/\s*(\d+(?:\.\d+)?)", str(value or "").strip(), flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def _simple_aperture_range(value):
    match = re.fullmatch(
        r"f\s*/\s*(\d+(?:\.\d+)?)\s*[–-]\s*f\s*/\s*(\d+(?:\.\d+)?)",
        str(value or "").strip(),
        flags=re.IGNORECASE,
    )
    return (float(match.group(1)), float(match.group(2))) if match else None


def _parse_shutter_seconds(value):
    text = str(value or "").strip().casefold()
    fraction = re.fullmatch(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)", text)
    if fraction:
        return float(fraction.group(1)) / float(fraction.group(2))
    seconds = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:s|sec|secs|second|seconds)", text)
    return float(seconds.group(1)) if seconds else None


def _simple_shutter_range(value):
    text = str(value or "").strip().casefold()
    fractions = re.fullmatch(
        r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)",
        text,
    )
    if fractions:
        return (
            float(fractions.group(1)) / float(fractions.group(2)),
            float(fractions.group(3)) / float(fractions.group(4)),
        )
    seconds = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)\s*(?:s|sec|secs|second|seconds)(?:\s*\(start at \d+(?:\.\d+)?\s*(?:s|sec|secs|second|seconds)\))?",
        text,
    )
    return (float(seconds.group(1)), float(seconds.group(2))) if seconds else None


def _minimum_shutter_speed(value):
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)\s*\+",
        str(value or "").strip(),
    )
    return float(match.group(1)) / float(match.group(2)) if match else None


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
