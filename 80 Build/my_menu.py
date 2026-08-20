"""Canonical persisted EOS R5 My Menu configuration."""

from __future__ import annotations

from collections.abc import Mapping

from validators.common import load_yaml_checked


MAX_TABS = 5
MAX_ITEMS_PER_TAB = 6


class MyMenuError(ValueError):
    """Raised when the persisted My Menu configuration is invalid."""


def load_my_menu(paths, known_item_ids=None):
    data = load_yaml_checked(paths.my_menu_file) or {}
    validate_my_menu(data, known_item_ids)
    return data


def validate_my_menu(data, known_item_ids=None):
    if not isinstance(data, Mapping):
        raise MyMenuError("My Menu configuration must be a mapping.")
    if data.get("schema_version") != 1:
        raise MyMenuError("My Menu configuration requires schema_version 1.")
    unknown = sorted(set(data) - {"schema_version", "tabs"})
    if unknown:
        raise MyMenuError(f"Unknown My Menu configuration keys: {', '.join(unknown)}")
    tabs = data.get("tabs")
    if not isinstance(tabs, list) or not tabs:
        raise MyMenuError("My Menu configuration requires at least one used tab.")
    if len(tabs) > MAX_TABS:
        raise MyMenuError("My Menu supports at most five used tabs.")
    known = set(known_item_ids) if known_item_ids is not None else None
    names = set()
    item_ids = set()
    for index, tab in enumerate(tabs, start=1):
        if not isinstance(tab, Mapping):
            raise MyMenuError(f"My Menu tab {index} must be a mapping.")
        extra = sorted(set(tab) - {"name", "items"})
        if extra:
            raise MyMenuError(f"Unknown keys in My Menu tab {index}: {', '.join(extra)}")
        name = tab.get("name")
        if not isinstance(name, str) or not name.strip():
            raise MyMenuError(f"My Menu tab {index} requires a non-empty name.")
        normalized = name.strip().casefold()
        if normalized in names:
            raise MyMenuError(f"Duplicate My Menu tab name: {name}")
        names.add(normalized)
        items = tab.get("items")
        if not isinstance(items, list) or not items:
            raise MyMenuError(f"Used My Menu tab {name} requires at least one item.")
        if len(items) > MAX_ITEMS_PER_TAB:
            raise MyMenuError(f"My Menu tab {name} exceeds six items.")
        for item_id in items:
            if not isinstance(item_id, str) or not item_id.strip():
                raise MyMenuError(f"My Menu tab {name} contains an invalid item identity.")
            if item_id in item_ids:
                raise MyMenuError(f"My Menu item is assigned more than once: {item_id}")
            if known is not None and item_id not in known:
                raise MyMenuError(f"My Menu item is not in the Canon settings catalog: {item_id}")
            item_ids.add(item_id)


def used_tabs(data):
    return [
        {"name": tab["name"].strip(), "items": list(tab["items"])}
        for tab in data["tabs"]
    ]
