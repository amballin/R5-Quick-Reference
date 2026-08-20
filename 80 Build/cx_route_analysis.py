"""Derived comparisons between a profile card and its selected Cx foundation.

The selected foundation is the profile named by ``card.field_setup.source_profile``.
That profile expresses the complete authored intent represented by the registered
Cx, including ranges and field guidance that cannot be compared safely with a
single concrete registration-workbook value.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping

from utilities import flatten


COMBINED_ROW_PATHS = {
    "autofocus.tracking_sensitivity": {
        "autofocus.tracking_sensitivity",
        "autofocus.accel_decel_tracking",
    },
    "stabilization.ibis": {
        "stabilization.ibis",
        "stabilization.lens_is",
    },
    "exposure.iso.mode": {
        "exposure.iso.mode",
        "exposure.iso.value",
        "exposure.auto_iso.maximum",
    },
}


class CxRouteAnalysisError(ValueError):
    """Raised when a selected Cx foundation cannot be resolved safely."""


def analyze_selected_foundation(profile, merged, profiles, baseline, setting_paths):
    """Compare visible target settings with the selected Cx foundation.

    Returns ``None`` only for permanent references. Profile cards without a
    selected Cx conservatively mark every visible target for verification.
    Inputs are not mutated.
    """

    if not isinstance(profile, Mapping) or profile.get("card_type") == "reference":
        return None
    setup = ((profile.get("card") or {}).get("field_setup") or {})
    if not isinstance(setup, Mapping):
        setup = {}
    start = str(setup.get("start") or "").upper()
    source_title = setup.get("source_profile")
    if not start and not source_title:
        return {
            "start": "",
            "source_profile": "",
            "foundation_label": "No Cx foundation",
            "change_label": "Verify or set — no Cx foundation",
            "legend_label": "Verify/set — no Cx foundation",
            "changed_paths": set(setting_paths or []),
        }
    if start not in {"C1", "C2", "C3"}:
        raise CxRouteAnalysisError(f"Unsupported Cx starting mode: {start or 'missing'}")
    if not isinstance(source_title, str) or not source_title.strip():
        raise CxRouteAnalysisError(f"{start} requires a source profile.")
    source_title = source_title.strip()
    foundation = _profile_by_title(profiles, source_title)
    defaults = _baseline_defaults(baseline)
    foundation_overrides = foundation.get("overrides") or {}
    if not isinstance(foundation_overrides, Mapping):
        raise CxRouteAnalysisError(f"Foundation profile overrides must be a mapping: {source_title}")
    if not isinstance(merged, Mapping):
        raise CxRouteAnalysisError("Merged profile values must be a mapping.")
    foundation_values = flatten(_deep_merge(defaults, foundation_overrides))
    target_values = flatten(merged)
    visible = set(setting_paths or [])
    changed = {
        path
        for path in visible
        if not _same_present_value(path, foundation_values, target_values)
    }
    return {
        "start": start,
        "source_profile": source_title,
        "foundation_label": f"{start} {source_title}",
        "change_label": f"Change from {start} {source_title}",
        "legend_label": f"Change from {start} {source_title}",
        "changed_paths": changed,
    }


def represented_paths(row_key):
    """Return all source paths represented by one rendered card row."""

    return set(COMBINED_ROW_PATHS.get(row_key) or {row_key})


def row_requires_change(row_key, changed_paths):
    return bool(represented_paths(row_key) & set(changed_paths or []))


def _profile_by_title(profiles, title):
    if isinstance(profiles, Mapping):
        candidates = [
            profile
            for profile in profiles.values()
            if isinstance(profile, Mapping) and profile.get("title") == title
        ]
    else:
        candidates = []
    if len(candidates) != 1:
        raise CxRouteAnalysisError(
            f"Cx foundation title must resolve to exactly one profile: {title}"
        )
    return candidates[0]


def _baseline_defaults(baseline):
    if not isinstance(baseline, Mapping) or not isinstance(baseline.get("defaults"), Mapping):
        raise CxRouteAnalysisError("Baseline defaults must be a mapping.")
    return baseline["defaults"]


def _deep_merge(base, overrides):
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _same_present_value(path, left, right):
    if (path in left) != (path in right):
        return False
    left_value = left.get(path)
    right_value = right.get(path)
    return left_value == right_value and type(left_value) is type(right_value)
