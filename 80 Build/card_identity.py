"""Stable card identity and structured-reference helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from uuid import UUID

import yaml


CARD_ID_KEY = "card_id"
SOURCE_CARD_ID_KEY = "source_card_id"


class CardIdentityError(ValueError):
    """Raised when card identity cannot be resolved uniquely."""


def canonical_uuid(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError):
        return None
    return str(parsed)


def valid_card_id(value):
    return canonical_uuid(value) == value


def index_profiles(profiles):
    """Return card-id and title indexes for a mapping of loaded profiles."""
    by_id = {}
    by_title = {}
    for name, profile in (profiles or {}).items():
        if not isinstance(profile, Mapping):
            continue
        card_id = profile.get(CARD_ID_KEY)
        title = profile.get("title") or name
        if isinstance(card_id, str):
            if card_id in by_id:
                raise CardIdentityError(f"Duplicate card_id: {card_id}")
            by_id[card_id] = (name, profile)
        if isinstance(title, str):
            if title in by_title:
                raise CardIdentityError(f"Duplicate card title: {title}")
            by_title[title] = (name, profile)
    return by_id, by_title


def profile_by_id(profiles, card_id):
    by_id, _ = index_profiles(profiles)
    match = by_id.get(card_id)
    if match is None:
        raise CardIdentityError(f"Unknown card_id: {card_id}")
    return match


def profile_by_title(profiles, title):
    _, by_title = index_profiles(profiles)
    match = by_title.get(title)
    if match is None:
        raise CardIdentityError(f"Unknown card title: {title}")
    return match


def source_profile(profiles, profile):
    setup = ((profile.get("card") or {}).get("field_setup") or {})
    card_id = setup.get(SOURCE_CARD_ID_KEY) if isinstance(setup, Mapping) else None
    if not card_id:
        return None
    return profile_by_id(profiles, card_id)


def source_profile_title(profiles, profile):
    match = source_profile(profiles, profile)
    if match is None:
        return ""
    name, source = match
    return str(source.get("title") or name)


def load_profiles(root):
    profiles = {}
    for path in sorted((Path(root) / "10 Profiles").glob("*.yaml")):
        with path.open("r", encoding="utf-8") as handle:
            profiles[path.stem] = yaml.safe_load(handle) or {}
    return profiles


def narrative_mentions(root, title, excluded_paths=()):
    """Return conservative authored-text mentions outside generated output."""
    root = Path(root).resolve()
    excluded = {Path(path).resolve() for path in excluded_paths}
    matches = []
    suffixes = {".md", ".yaml", ".yml"}
    ignored_parts = {".git", "docs", "__pycache__"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if path.resolve() in excluded or ignored_parts.intersection(path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, start=1):
            if title in line:
                matches.append({"file": str(path.relative_to(root)), "line": number, "text": line.strip()[:240]})
    return matches
