"""Read-only impact analysis for proposed baseline changes.

The analyzer compares current and proposed baseline defaults against authored
profile overrides.  It does not mutate its inputs or write project files.  Its
result is composed only of JSON-serializable dictionaries, lists, and scalar
values so a later guarded UI can present the same repository-owned analysis.
"""

from __future__ import annotations

import copy
from collections import Counter
from collections.abc import Mapping
import re


CLASSIFICATION_INHERITED_CHANGE = "inherited_change"
CLASSIFICATION_OVERRIDE_PROTECTED = "override_protected"
CLASSIFICATION_OVERRIDE_REDUNDANT = "override_redundant"
CLASSIFICATION_OVERRIDE_INVALID_PATH = "override_invalid_path"
CLASSIFICATION_OVERRIDE_INVALID_TYPE = "override_invalid_type"

ACTION_REVIEW_BASELINE_CHANGE = "review_baseline_change"
ACTION_KEEP_OVERRIDE = "keep_override"
ACTION_REMOVE_OVERRIDE = "remove_override"
ACTION_REPAIR_OVERRIDE = "repair_override"

DECISION_FOLLOW_BASELINE = "follow_baseline"
DECISION_PRESERVE_PREVIOUS = "preserve_previous"
VALID_INHERITED_DECISIONS = {
    DECISION_FOLLOW_BASELINE,
    DECISION_PRESERVE_PREVIOUS,
}
REGISTERED_MODE_KEYS = ("c1", "c2", "c3")


class BaselineImpactError(ValueError):
    """Raised when impact-analysis input does not match the project model."""


def analyze_baseline_impact(current_baseline, proposed_baseline, profiles):
    """Return the profile impact of replacing one baseline with another.

    ``current_baseline`` and ``proposed_baseline`` are complete baseline
    mappings containing ``defaults``. ``profiles`` maps stable source names to
    loaded profile mappings. Permanent ``card_type: reference`` cards are
    skipped because they do not inherit the shooting baseline.
    """

    current_defaults = _baseline_defaults(current_baseline, "Current baseline")
    proposed_defaults = _baseline_defaults(proposed_baseline, "Proposed baseline")
    profile_map = _profiles(profiles)
    current_values = _flatten(current_defaults)
    proposed_values = _flatten(proposed_defaults)
    changed_paths = sorted(
        path
        for path in set(current_values) | set(proposed_values)
        if not _same_present_value(path, current_values, proposed_values)
    )

    skipped_reference_cards = sorted(
        name
        for name, profile in profile_map.items()
        if profile.get("card_type") == "reference"
    )
    inheriting_profiles = {
        name: profile
        for name, profile in profile_map.items()
        if profile.get("card_type") != "reference"
    }

    changes = []
    classifications = Counter()
    affected_profiles = set()
    decision_profiles = set()
    for path in changed_paths:
        current_present = path in current_values
        proposed_present = path in proposed_values
        current_value = current_values.get(path)
        proposed_value = proposed_values.get(path)
        profile_impacts = []
        for name, profile in sorted(inheriting_profiles.items()):
            overrides = profile.get("overrides") or {}
            if not isinstance(overrides, Mapping):
                raise BaselineImpactError(f"Profile overrides must be a mapping: {name}")
            override_values = _flatten(overrides)
            impact = _profile_impact(
                name=name,
                title=profile.get("title") or name,
                path=path,
                current_present=current_present,
                current_value=current_value,
                proposed_present=proposed_present,
                proposed_value=proposed_value,
                override_values=override_values,
            )
            profile_impacts.append(impact)
            classifications[impact["classification"]] += 1
            if impact["classification"] != CLASSIFICATION_OVERRIDE_PROTECTED:
                affected_profiles.add(name)
            if impact["requires_decision"]:
                decision_profiles.add(name)
        changes.append(
            {
                "path": path,
                "change_type": _change_type(
                    current_present,
                    current_value,
                    proposed_present,
                    proposed_value,
                ),
                "current_baseline_present": current_present,
                "current_baseline_value": current_value,
                "proposed_baseline_present": proposed_present,
                "proposed_baseline_value": proposed_value,
                "profiles": profile_impacts,
            }
        )

    return {
        "summary": {
            "changed_settings": len(changes),
            "profile_setting_impacts": sum(classifications.values()),
            "affected_profiles": len(affected_profiles),
            "profiles_requiring_decision": len(decision_profiles),
            "classifications": dict(sorted(classifications.items())),
            "reference_cards_skipped": len(skipped_reference_cards),
        },
        "changes": changes,
        "skipped_reference_cards": skipped_reference_cards,
    }


def plan_baseline_migration(
    current_baseline,
    proposed_baseline,
    profiles,
    decisions,
    registration=None,
    setting_menu_items=None,
    menu_tabs=None,
):
    """Return a validated, read-only migration plan for a baseline proposal.

    ``decisions`` is a list of objects containing ``profile``, ``path``, and
    ``decision``. Decisions are accepted only for inherited changes and must
    explicitly choose whether that profile follows the proposed baseline or
    preserves its previous effective value as a new override. Missing choices
    remain visible as unresolved plan items; stale, duplicate, or inapplicable
    choices are rejected.
    """

    analysis = analyze_baseline_impact(current_baseline, proposed_baseline, profiles)
    inherited = {}
    invalid = []
    follows = []
    overrides_to_add = []
    overrides_to_remove = []
    overrides_to_keep = []
    profile_card_cues_to_add = []

    for change in analysis["changes"]:
        path = change["path"]
        for impact in change["profiles"]:
            item = _plan_item(path, impact)
            classification = impact["classification"]
            if classification == CLASSIFICATION_INHERITED_CHANGE:
                inherited[(impact["name"], path)] = item
            elif classification == CLASSIFICATION_OVERRIDE_REDUNDANT:
                overrides_to_remove.append(item)
            elif classification == CLASSIFICATION_OVERRIDE_PROTECTED:
                overrides_to_keep.append(item)
            elif classification in {
                CLASSIFICATION_OVERRIDE_INVALID_PATH,
                CLASSIFICATION_OVERRIDE_INVALID_TYPE,
            }:
                invalid.append({**item, "reason": classification})

    selected = _migration_decisions(decisions, set(inherited))
    unresolved = list(invalid)
    for key, item in inherited.items():
        decision = selected.get(key)
        if decision is None:
            unresolved.append({**item, "reason": "decision_required"})
        elif decision == DECISION_FOLLOW_BASELINE:
            follows.append(item)
        else:
            overrides_to_add.append(
                {
                    **item,
                    "override_value": item["previous_effective_value"],
                }
            )

    for items in (
        follows,
        overrides_to_add,
        overrides_to_remove,
        overrides_to_keep,
        unresolved,
    ):
        items.sort(key=lambda item: (item["path"], item["profile"].casefold()))

    if setting_menu_items is not None and menu_tabs is not None:
        coverage = analyze_my_menu_routes(
            current_baseline,
            proposed_baseline,
            profiles,
            registration or {},
            setting_menu_items,
            menu_tabs,
        )
        for profile in coverage["profiles"]:
            source_profile = profiles.get(profile["name"]) or {}
            card = source_profile.get("card") or {}
            field_setup = card.get("field_setup") or {} if isinstance(card, Mapping) else {}
            route_is_authored = (
                isinstance(field_setup, Mapping)
                and str(field_setup.get("start") or "").upper() in {"C1", "C2", "C3"}
                and isinstance(field_setup.get("source_profile"), str)
                and bool(field_setup["source_profile"].strip())
            )
            if not route_is_authored:
                continue
            for cue in profile["missing_card_cues"]:
                if len(cue["available_in_tabs"]) != 1:
                    raise BaselineImpactError(
                        "A missing My Menu card cue must resolve to exactly one configured tab: "
                        f"{profile['name']} / {cue['path']}"
                    )
                profile_card_cues_to_add.append(
                    {
                        "profile": profile["name"],
                        "title": profile["title"],
                        "tab": cue["available_in_tabs"][0],
                        "path": cue["path"],
                        "item_id": cue["item_id"],
                        "yaml_path": "card.field_setup.my_menus",
                    }
                )
        profile_card_cues_to_add.sort(
            key=lambda item: (
                item["title"].casefold(),
                item["tab"].casefold(),
                item["path"],
            )
        )

    return {
        "complete": not unresolved,
        "summary": {
            "profiles_following_baseline": len(follows),
            "overrides_to_add": len(overrides_to_add),
            "overrides_to_remove": len(overrides_to_remove),
            "overrides_to_keep": len(overrides_to_keep),
            "profile_card_cues_to_add": len(profile_card_cues_to_add),
            "unresolved_decisions": len(unresolved),
        },
        "profiles_following_baseline": follows,
        "overrides_to_add": overrides_to_add,
        "overrides_to_remove": overrides_to_remove,
        "overrides_to_keep": overrides_to_keep,
        "profile_card_cues_to_add": profile_card_cues_to_add,
        "unresolved_decisions": unresolved,
    }


def analyze_cx_impact(current_baseline, proposed_baseline, profiles, registration):
    """Report C1–C3 and declared starting-route impact without rewriting routes."""

    current_defaults = _baseline_defaults(current_baseline, "Current baseline")
    proposed_defaults = _baseline_defaults(proposed_baseline, "Proposed baseline")
    profile_map = _profiles(profiles)
    current_values = _flatten(current_defaults)
    proposed_values = _flatten(proposed_defaults)
    changed_paths = sorted(
        path
        for path in set(current_values) | set(proposed_values)
        if not _same_present_value(path, current_values, proposed_values)
    )
    definitions, rows = _registration_definition(registration)

    registered_modes = []
    affected_by_start = {}
    effective_setting_changes = 0
    for key in REGISTERED_MODE_KEYS:
        overrides = _registration_overrides(rows, key)
        override_values = _flatten(overrides)
        current_effective = _flatten(_deep_merge(current_defaults, overrides))
        proposed_effective = _flatten(_deep_merge(proposed_defaults, overrides))
        settings = []
        affected_paths = []
        for path in changed_paths:
            changed = not _same_present_value(path, current_effective, proposed_effective)
            if changed:
                affected_paths.append(path)
                effective_setting_changes += 1
            settings.append(
                {
                    "path": path,
                    "current_effective_present": path in current_effective,
                    "current_effective_value": current_effective.get(path),
                    "proposed_effective_present": path in proposed_effective,
                    "proposed_effective_value": proposed_effective.get(path),
                    "changed": changed,
                    "registration_override": path in override_values,
                }
            )
        start = key.upper()
        mode = {
            "key": key,
            "start": start,
            "heading": definitions[key]["heading"],
            "affected": bool(affected_paths),
            "affected_paths": affected_paths,
            "settings": settings,
        }
        registered_modes.append(mode)
        affected_by_start[start] = affected_paths

    route_warnings = []
    for name, profile in sorted(profile_map.items()):
        if profile.get("card_type") == "reference":
            continue
        card = profile.get("card") or {}
        field_setup = card.get("field_setup") or {} if isinstance(card, Mapping) else {}
        if not isinstance(field_setup, Mapping):
            continue
        start = str(field_setup.get("start") or "").upper()
        affected_paths = affected_by_start.get(start) or []
        if not affected_paths:
            continue
        route_warnings.append(
            {
                "name": name,
                "title": profile.get("title") or name,
                "start": start,
                "source_profile": field_setup.get("source_profile") or "",
                "affected_paths": list(affected_paths),
            }
        )

    return {
        "summary": {
            "registered_modes": len(registered_modes),
            "affected_registered_modes": sum(mode["affected"] for mode in registered_modes),
            "effective_setting_changes": effective_setting_changes,
            "profiles_with_affected_starting_mode": len(route_warnings),
        },
        "registered_modes": registered_modes,
        "route_warnings": route_warnings,
    }


def analyze_my_menu_routes(
    current_baseline,
    proposed_baseline,
    profiles,
    registration,
    setting_menu_items,
    menu_tabs,
):
    """Report My Menu coverage for settings that are visible on merged cards.

    My Menu is a stable fast-access configuration, not a transition recipe.
    Baseline changes may alter which conditional rows a merged card displays,
    but matching a C1-C3 starting value never makes a shortcut unnecessary.
    ``setting_menu_items`` supplies explicit setting-path identities and
    ``menu_tabs`` is the session-only arrangement to inspect. No input is
    mutated and no routing or My Menu configuration is rewritten.
    """

    from html_renderer import displayed_card_setting_paths

    current_defaults = _baseline_defaults(current_baseline, "Current baseline")
    proposed_defaults = _baseline_defaults(proposed_baseline, "Proposed baseline")
    profile_map = _profiles(profiles)
    route_catalog = _setting_menu_items(setting_menu_items)
    configured_tabs, configuration_warnings = _configured_menu_tabs(menu_tabs)
    configured_item_tabs = {}
    for tab in configured_tabs.values():
        for item_id in tab["items"]:
            configured_item_tabs.setdefault(item_id, []).append(tab["name"])

    route_profiles = []
    warning_profiles = 0
    declared_settings = 0
    displayed_assignments = 0
    hidden_assignments = 0
    unavailable_settings = 0
    missing_card_cues = 0
    newly_visible_missing_cues = 0
    omitted_tabs = 0
    referenced_configured_items = set()

    for name, profile in sorted(profile_map.items()):
        if profile.get("card_type") == "reference":
            continue
        field_setup = _field_setup(name, profile)
        start = str(field_setup.get("start") or "").upper()
        if start and start not in {key.upper() for key in REGISTERED_MODE_KEYS}:
            raise BaselineImpactError(f"Profile has an unsupported starting mode: {name} / {start}")

        overrides = profile.get("overrides") or {}
        if not isinstance(overrides, Mapping):
            raise BaselineImpactError(f"Profile overrides must be a mapping: {name}")
        merged_current = _deep_merge(current_defaults, overrides)
        merged_proposed = _deep_merge(proposed_defaults, overrides)
        visible_current = displayed_card_setting_paths(profile, merged_current)
        visible_proposed = displayed_card_setting_paths(profile, merged_proposed)

        for path in visible_proposed:
            item_id = route_catalog.get(path)
            if item_id in configured_item_tabs:
                referenced_configured_items.add(item_id)

        declarations, tabs = _declared_menu_routes(name, field_setup)
        declared_paths = {item["path"] for item in declarations}
        declaration_results = []
        for declaration in declarations:
            path = declaration["path"]
            tab_name = declaration["tab"]
            item_id = route_catalog.get(path)
            configured = configured_tabs.get(tab_name.casefold())
            displayed_before = path in visible_current
            displayed_after = path in visible_proposed
            item_available = bool(item_id and configured and item_id in configured["items"])
            identity_missing = item_id is None
            availability_problem = displayed_after and not item_available
            record = {
                "tab": tab_name,
                "path": path,
                "item_id": item_id,
                "displayed_before": displayed_before,
                "displayed_after": displayed_after,
                "became_hidden": displayed_before and not displayed_after,
                "became_visible": not displayed_before and displayed_after,
                "identity_missing": identity_missing,
                "tab_present": configured is not None,
                "item_available": item_available,
                "availability_problem": availability_problem,
            }
            declaration_results.append(record)
            declared_settings += 1
            displayed_assignments += int(displayed_after)
            hidden_assignments += int(not displayed_after)
            unavailable_settings += int(availability_problem)

        tab_results = []
        for tab_name, paths in tabs:
            displayed_paths = sorted(path for path in paths if path in visible_proposed)
            shown_on_card = bool(displayed_paths)
            omitted_tabs += int(not shown_on_card)
            configured = configured_tabs.get(tab_name.casefold())
            tab_results.append(
                {
                    "name": tab_name,
                    "declared_paths": list(paths),
                    "displayed_paths": displayed_paths,
                    "shown_on_card": shown_on_card,
                    "configured": configured is not None,
                }
            )

        missing = []
        for path in sorted(visible_proposed):
            item_id = route_catalog.get(path)
            available_in = sorted(configured_item_tabs.get(item_id, []))
            if not available_in or path in declared_paths:
                continue
            item = {
                "path": path,
                "item_id": item_id,
                "newly_visible": path not in visible_current,
                "available_in_tabs": available_in,
            }
            missing.append(item)
            missing_card_cues += 1
            newly_visible_missing_cues += int(item["newly_visible"])

        warnings = (
            sum(item["availability_problem"] for item in declaration_results)
            + len(missing)
        )
        warning_profiles += int(warnings > 0)
        if declarations or missing:
            route_profiles.append(
                {
                    "name": name,
                    "title": profile.get("title") or name,
                    "start": start,
                    "source_profile": field_setup.get("source_profile") or "",
                    "access_only": field_setup.get("access_only") is True,
                    "warning_count": warnings,
                    "declared_settings": declaration_results,
                    "tabs": tab_results,
                    "missing_card_cues": missing,
                }
            )

    unreferenced_items = []
    item_paths = {item_id: path for path, item_id in route_catalog.items()}
    for item_id, tab_names in sorted(configured_item_tabs.items()):
        if item_id in referenced_configured_items:
            continue
        unreferenced_items.append(
            {
                "item_id": item_id,
                "path": item_paths.get(item_id),
                "tabs": sorted(tab_names),
            }
        )

    return {
        "summary": {
            "profiles_analyzed": len(route_profiles),
            "profiles_with_warnings": warning_profiles,
            "declared_settings": declared_settings,
            "displayed_assignments": displayed_assignments,
            "hidden_assignments": hidden_assignments,
            "unavailable_settings": unavailable_settings,
            "missing_card_cues": missing_card_cues,
            "newly_visible_missing_cues": newly_visible_missing_cues,
            "omitted_tabs": omitted_tabs,
            "unreferenced_configured_items": len(unreferenced_items),
        },
        "configuration_warnings": configuration_warnings,
        "unreferenced_configured_items": unreferenced_items,
        "profiles": route_profiles,
    }


def _setting_menu_items(setting_menu_items):
    if not isinstance(setting_menu_items, Mapping):
        raise BaselineImpactError("My Menu setting identity must be a mapping.")
    normalized = {}
    for path, item_id in setting_menu_items.items():
        if not isinstance(path, str) or not path or not isinstance(item_id, str) or not item_id:
            raise BaselineImpactError("My Menu setting identity entries must use non-empty strings.")
        normalized[path] = item_id
    return normalized


def _configured_menu_tabs(menu_tabs):
    if not isinstance(menu_tabs, list):
        raise BaselineImpactError("My Menu configuration must be a list.")
    configured = {}
    warnings = []
    for index, tab in enumerate(menu_tabs, start=1):
        if not isinstance(tab, Mapping):
            raise BaselineImpactError("Each My Menu configuration tab must be a mapping.")
        name = str(tab.get("name") or "").strip()
        items = tab.get("items") or []
        if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
            raise BaselineImpactError(f"My Menu tab items must be strings: tab {index}")
        if not name:
            continue
        key = name.casefold()
        if key in configured:
            warnings.append(f"Duplicate configured My Menu tab name: {name}")
            configured[key]["items"].update(item for item in items if item)
            continue
        configured[key] = {"name": name, "items": {item for item in items if item}}
    return configured, warnings


def _field_setup(name, profile):
    card = profile.get("card") or {}
    if not isinstance(card, Mapping):
        raise BaselineImpactError(f"Profile card must be a mapping: {name}")
    field_setup = card.get("field_setup") or {}
    if not isinstance(field_setup, Mapping):
        raise BaselineImpactError(f"Profile field setup must be a mapping: {name}")
    return field_setup


def _declared_menu_routes(name, field_setup):
    my_menus = field_setup.get("my_menus") or []
    if not isinstance(my_menus, list):
        raise BaselineImpactError(f"Profile My Menu routes must be a list: {name}")
    declarations = []
    tabs = []
    for tab in my_menus:
        if not isinstance(tab, Mapping):
            raise BaselineImpactError(f"Profile My Menu route must be a mapping: {name}")
        tab_name = str(tab.get("name") or "").strip()
        settings = tab.get("settings") or []
        if not tab_name or not isinstance(settings, list) or any(not isinstance(path, str) or not path for path in settings):
            raise BaselineImpactError(f"Profile My Menu route is incomplete: {name}")
        paths = []
        for path in settings:
            declarations.append({"tab": tab_name, "path": path})
            paths.append(path)
        tabs.append((tab_name, paths))
    return declarations, tabs


def _effective_differences(start_values, target_values):
    differences = {}
    for path in sorted(set(start_values) | set(target_values)):
        if _same_present_value(path, start_values, target_values):
            continue
        differences[path] = {
            "start_present": path in start_values,
            "start_value": start_values.get(path),
            "target_present": path in target_values,
            "target_value": target_values.get(path),
        }
    return differences


def _registration_definition(registration):
    if not isinstance(registration, Mapping):
        raise BaselineImpactError("C1–C3 registration must be a mapping.")
    definitions = {
        item.get("key"): item
        for item in registration.get("profiles") or []
        if isinstance(item, Mapping) and item.get("key")
    }
    missing = [key for key in REGISTERED_MODE_KEYS if key not in definitions]
    if missing:
        raise BaselineImpactError(
            "C1–C3 registration profiles are missing: " + ", ".join(missing)
        )
    for key in REGISTERED_MODE_KEYS:
        if not definitions[key].get("heading"):
            raise BaselineImpactError(f"C1–C3 registration heading is missing: {key}")
    rows = registration.get("rows") or []
    if not isinstance(rows, list):
        raise BaselineImpactError("C1–C3 registration rows must be a list.")
    return definitions, rows


def _registration_overrides(rows, key):
    overrides = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise BaselineImpactError("Each C1–C3 registration row must be a mapping.")
        path = row.get("baseline_key")
        raw_value = row.get(key)
        if not path or raw_value in (None, ""):
            continue
        _apply_registration_value(overrides, path, raw_value)
    return overrides


def _apply_registration_value(overrides, path, raw_value):
    if isinstance(raw_value, bool):
        value = "On" if raw_value else "Off"
    else:
        value = str(raw_value).split(";", 1)[0].strip()
    if path == "exposure.iso.mode" and re.fullmatch(r"\d+", value):
        _set_nested(overrides, "exposure.iso.mode", "Fixed")
        _set_nested(overrides, "exposure.iso.value", value)
        return
    if path == "exposure.auto_iso.maximum":
        match = re.match(r"\d+", value)
        value = match.group(0) if match else value
    _set_nested(overrides, path, value)


def _set_nested(target, path, value):
    cursor = target
    parts = path.split(".")
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})
    cursor[parts[-1]] = value


def _deep_merge(base, overrides):
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _migration_decisions(decisions, valid_keys):
    if decisions is None:
        decisions = []
    if not isinstance(decisions, list):
        raise BaselineImpactError("Baseline migration decisions must be a list.")
    selected = {}
    for item in decisions:
        if not isinstance(item, Mapping):
            raise BaselineImpactError("Each baseline migration decision must be an object.")
        profile = item.get("profile")
        path = item.get("path")
        decision = item.get("decision")
        key = (profile, path)
        if key in selected:
            raise BaselineImpactError(
                f"Duplicate baseline migration decision: {profile} / {path}"
            )
        if key not in valid_keys:
            raise BaselineImpactError(
                f"Stale or inapplicable baseline migration decision: {profile} / {path}"
            )
        if decision not in VALID_INHERITED_DECISIONS:
            raise BaselineImpactError(
                f"Invalid baseline migration decision for {profile} / {path}: {decision}"
            )
        selected[key] = decision
    return selected


def _plan_item(path, impact):
    return {
        "profile": impact["name"],
        "title": impact["title"],
        "path": path,
        "previous_effective_present": impact["old_effective_present"],
        "previous_effective_value": impact["old_effective_value"],
        "proposed_effective_present": impact["new_effective_present"],
        "proposed_effective_value": impact["new_effective_value"],
    }


def _profile_impact(
    *,
    name,
    title,
    path,
    current_present,
    current_value,
    proposed_present,
    proposed_value,
    override_values,
):
    has_override = path in override_values
    override_value = override_values.get(path)
    old_present = current_present or has_override
    old_effective = override_value if has_override else current_value

    if not has_override:
        return _impact_record(
            name,
            title,
            old_present,
            old_effective,
            proposed_present,
            proposed_value,
            False,
            None,
            CLASSIFICATION_INHERITED_CHANGE,
            ACTION_REVIEW_BASELINE_CHANGE,
            True,
        )

    if not proposed_present:
        classification = CLASSIFICATION_OVERRIDE_INVALID_PATH
        action = ACTION_REPAIR_OVERRIDE
        requires_decision = True
    elif not _compatible_type(proposed_value, override_value):
        classification = CLASSIFICATION_OVERRIDE_INVALID_TYPE
        action = ACTION_REPAIR_OVERRIDE
        requires_decision = True
    elif _same_value(proposed_value, override_value):
        classification = CLASSIFICATION_OVERRIDE_REDUNDANT
        action = ACTION_REMOVE_OVERRIDE
        requires_decision = False
    else:
        classification = CLASSIFICATION_OVERRIDE_PROTECTED
        action = ACTION_KEEP_OVERRIDE
        requires_decision = False

    new_present = proposed_present or has_override
    new_effective = override_value
    return _impact_record(
        name,
        title,
        old_present,
        old_effective,
        new_present,
        new_effective,
        True,
        override_value,
        classification,
        action,
        requires_decision,
    )


def _impact_record(
    name,
    title,
    old_present,
    old_effective,
    new_present,
    new_effective,
    has_override,
    override_value,
    classification,
    recommended_action,
    requires_decision,
):
    return {
        "name": name,
        "title": title,
        "old_effective_present": old_present,
        "old_effective_value": old_effective,
        "new_effective_present": new_present,
        "new_effective_value": new_effective,
        "has_override": has_override,
        "override_value": override_value,
        "classification": classification,
        "recommended_action": recommended_action,
        "requires_decision": requires_decision,
    }


def _baseline_defaults(baseline, label):
    if not isinstance(baseline, Mapping):
        raise BaselineImpactError(f"{label} must be a mapping.")
    defaults = baseline.get("defaults")
    if not isinstance(defaults, Mapping):
        raise BaselineImpactError(f"{label} defaults must be a mapping.")
    return defaults


def _profiles(profiles):
    if not isinstance(profiles, Mapping):
        raise BaselineImpactError("Profiles must be a mapping keyed by source name.")
    for name, profile in profiles.items():
        if not isinstance(name, str) or not name:
            raise BaselineImpactError("Profile source names must be non-empty strings.")
        if not isinstance(profile, Mapping):
            raise BaselineImpactError(f"Profile must be a mapping: {name}")
    return profiles


def _flatten(values, prefix=""):
    flattened = {}
    for key, value in values.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            flattened.update(_flatten(value, path))
        else:
            flattened[path] = value
    return flattened


def _same_present_value(path, current_values, proposed_values):
    if (path in current_values) != (path in proposed_values):
        return False
    return _same_value(current_values.get(path), proposed_values.get(path))


def _same_value(left, right):
    return left == right and type(left) is type(right)


def _change_type(current_present, current_value, proposed_present, proposed_value):
    if not current_present:
        return "added"
    if not proposed_present:
        return "removed"
    if not _compatible_type(current_value, proposed_value) or not _compatible_type(proposed_value, current_value):
        return "type_changed"
    return "value_changed"


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
