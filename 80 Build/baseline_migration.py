"""Deterministic source candidates for a reviewed baseline migration.

This module deliberately has no UI or filesystem-write policy.  It converts a
complete migration plan into the exact baseline/profile bytes that a guarded
caller may validate, review, back up, and commit as one transaction.
"""

from __future__ import annotations

import copy
from datetime import date
import difflib
from pathlib import Path

import yaml


class BaselineMigrationError(ValueError):
    """Raised when a migration plan cannot safely produce source candidates."""


def build_migration_candidates(current_baseline, proposed_baseline, profiles, plan, *, today=None):
    """Return changed source files as ``{relative_path: yaml_bytes}``.

    The inputs are never mutated.  A plan must be complete and contain no
    unresolved decisions. Planned obsolete My Menu cues are removed before
    missing card cues are appended.
    """

    if not isinstance(plan, dict) or plan.get("complete") is not True:
        raise BaselineMigrationError("A complete baseline migration plan is required.")
    if plan.get("unresolved_decisions"):
        raise BaselineMigrationError("Unresolved migration decisions must be completed first.")
    if not isinstance(current_baseline, dict) or not isinstance(proposed_baseline, dict):
        raise BaselineMigrationError("Current and proposed baselines must be mappings.")
    if not isinstance(profiles, dict):
        raise BaselineMigrationError("Profiles must be a mapping keyed by source name.")

    effective_date = today or date.today()
    candidates = {}
    if proposed_baseline != current_baseline:
        baseline = copy.deepcopy(proposed_baseline)
        _touch_metadata(baseline, effective_date)
        baseline_bytes = dump_yaml(baseline)
        if baseline_bytes != dump_yaml(current_baseline):
            candidates["00 Master/baseline.yaml"] = baseline_bytes

    changed_profiles = {}
    for action in plan.get("overrides_to_add") or []:
        profile = _editable_profile(changed_profiles, profiles, action)
        _set_nested(profile.setdefault("overrides", {}), action["path"], copy.deepcopy(action["override_value"]))
    for action in plan.get("overrides_to_remove") or []:
        profile = _editable_profile(changed_profiles, profiles, action)
        overrides = profile.get("overrides")
        if not isinstance(overrides, dict) or not _delete_nested(overrides, action["path"]):
            raise BaselineMigrationError(
                f"Planned override no longer exists: {action.get('profile')} / {action.get('path')}"
            )
    for action in plan.get("profile_card_cues_to_remove") or []:
        profile = _editable_profile(changed_profiles, profiles, action)
        _remove_my_menu_cue(profile, action)
    for action in plan.get("profile_card_cues_to_add") or []:
        profile = _editable_profile(changed_profiles, profiles, action)
        _add_my_menu_cue(profile, action)

    for name, profile in sorted(changed_profiles.items(), key=lambda item: item[0].casefold()):
        original = profiles[name]
        if profile == original:
            continue
        _touch_metadata(profile, effective_date)
        candidates[f"10 Profiles/{name}.yaml"] = dump_yaml(profile)
    return candidates


def migration_diff(before, candidates):
    """Return one exact unified diff for an ordered set of candidate files."""

    chunks = []
    for relative in sorted(candidates):
        prior = before.get(relative)
        if prior is None:
            raise BaselineMigrationError(f"Migration source no longer exists: {relative}")
        candidate = candidates[relative]
        if prior == candidate:
            continue
        chunks.append(
            "".join(
                difflib.unified_diff(
                    prior.decode("utf-8").splitlines(keepends=True),
                    candidate.decode("utf-8").splitlines(keepends=True),
                    fromfile=f"a/{relative}",
                    tofile=f"b/{relative}",
                )
            )
        )
    return "".join(chunks)


def dump_yaml(value):
    return yaml.safe_dump(
        value,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
        default_flow_style=False,
    ).encode("utf-8")


def _editable_profile(changed, profiles, action):
    name = action.get("profile") if isinstance(action, dict) else None
    if not isinstance(name, str) or name not in profiles:
        raise BaselineMigrationError(f"Migration references an unknown profile: {name}")
    source = profiles[name]
    if not isinstance(source, dict) or source.get("card_type") == "reference":
        raise BaselineMigrationError(f"Migration profile is not editable: {name}")
    return changed.setdefault(name, copy.deepcopy(source))


def _set_nested(mapping, path, value):
    if not isinstance(mapping, dict):
        raise BaselineMigrationError(f"Override parent must be a mapping: {path}")
    parts = _path_parts(path)
    cursor = mapping
    for part in parts[:-1]:
        child = cursor.setdefault(part, {})
        if not isinstance(child, dict):
            raise BaselineMigrationError(f"Override path crosses a scalar value: {path}")
        cursor = child
    cursor[parts[-1]] = value


def _delete_nested(mapping, path):
    parts = _path_parts(path)
    cursor = mapping
    parents = []
    for part in parts[:-1]:
        child = cursor.get(part)
        if not isinstance(child, dict):
            return False
        parents.append((cursor, part, child))
        cursor = child
    if parts[-1] not in cursor:
        return False
    del cursor[parts[-1]]
    for parent, key, child in reversed(parents):
        if child:
            break
        del parent[key]
    return True


def _add_my_menu_cue(profile, action):
    tab_name = action.get("tab")
    path = action.get("path")
    if not isinstance(tab_name, str) or not tab_name.strip() or not isinstance(path, str):
        raise BaselineMigrationError("A planned My Menu cue requires a tab and setting path.")
    card = profile.setdefault("card", {})
    if not isinstance(card, dict):
        raise BaselineMigrationError("Profile card must be a mapping.")
    setup = card.setdefault("field_setup", {})
    if not isinstance(setup, dict):
        raise BaselineMigrationError("Profile field setup must be a mapping.")
    if (
        profile.get("display_category") == "reference"
        and not setup.get("start")
        and not setup.get("source_card_id")
    ):
        setup["access_only"] = True
    menus = setup.setdefault("my_menus", [])
    if not isinstance(menus, list):
        raise BaselineMigrationError("Profile My Menu cues must be a list.")
    tab = next(
        (
            item
            for item in menus
            if isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and item["name"].casefold() == tab_name.casefold()
        ),
        None,
    )
    if tab is None:
        tab = {"name": tab_name, "settings": []}
        menus.append(tab)
    settings = tab.setdefault("settings", [])
    if not isinstance(settings, list):
        raise BaselineMigrationError(f"My Menu cue settings must be a list: {tab_name}")
    if path not in settings:
        settings.append(path)


def _remove_my_menu_cue(profile, action):
    tab_name = action.get("tab")
    path = action.get("path")
    if not isinstance(tab_name, str) or not tab_name.strip() or not isinstance(path, str):
        raise BaselineMigrationError("A planned My Menu cue removal requires a tab and setting path.")
    card = profile.get("card")
    setup = card.get("field_setup") if isinstance(card, dict) else None
    menus = setup.get("my_menus") if isinstance(setup, dict) else None
    if not isinstance(menus, list):
        raise BaselineMigrationError(
            f"Planned My Menu cue no longer exists: {action.get('profile')} / {tab_name} / {path}"
        )
    removed = False
    retained_menus = []
    for tab in menus:
        if not isinstance(tab, dict):
            raise BaselineMigrationError("Profile My Menu cues must contain mappings.")
        name = tab.get("name")
        settings = tab.get("settings")
        if not isinstance(name, str) or not isinstance(settings, list):
            raise BaselineMigrationError("Profile My Menu cue is incomplete.")
        candidate = copy.deepcopy(tab)
        if name.casefold() == tab_name.casefold() and path in settings:
            candidate["settings"] = [setting for setting in settings if setting != path]
            removed = True
        if candidate["settings"]:
            retained_menus.append(candidate)
    if not removed:
        raise BaselineMigrationError(
            f"Planned My Menu cue no longer exists: {action.get('profile')} / {tab_name} / {path}"
        )
    if retained_menus:
        setup["my_menus"] = retained_menus
        return
    setup.pop("my_menus", None)
    if setup.get("access_only") is True and not setup.get("start") and not setup.get("source_card_id"):
        setup.pop("access_only", None)
    if not setup:
        card.pop("field_setup", None)
    if not card:
        profile.pop("card", None)


def _touch_metadata(document, value):
    metadata = document.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        raise BaselineMigrationError("Source metadata must be a mapping.")
    metadata["last_updated"] = value


def _path_parts(path):
    if not isinstance(path, str) or not path or any(not part for part in path.split(".")):
        raise BaselineMigrationError(f"Invalid setting path: {path}")
    return path.split(".")
