"""Canonical My Menu card-color palette and named-tab assignments."""

from __future__ import annotations

from collections.abc import Mapping
import re
import math

from validators.common import load_yaml_checked


HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
MAX_TABS = 5


class MyMenuColorError(ValueError):
    """Raised when the canonical My Menu color configuration is invalid."""


def load_my_menu_colors(paths):
    data = load_yaml_checked(paths.my_menu_colors_file) or {}
    validate_my_menu_colors(data)
    return data


def validate_my_menu_colors(data):
    if not isinstance(data, Mapping):
        raise MyMenuColorError("My Menu colors must be a mapping.")
    if data.get("schema_version") != 1:
        raise MyMenuColorError("My Menu colors require schema_version 1.")
    unknown = sorted(set(data) - {"schema_version", "palette", "assignments"})
    if unknown:
        raise MyMenuColorError(f"Unknown My Menu color keys: {', '.join(unknown)}")
    palette = data.get("palette")
    if not isinstance(palette, Mapping) or len(palette) < MAX_TABS:
        raise MyMenuColorError("My Menu color palette must provide at least five choices.")
    palette_colors = []
    for label, color in palette.items():
        if not isinstance(label, str) or not label.strip():
            raise MyMenuColorError("My Menu palette labels must be non-empty strings.")
        if not isinstance(color, str) or not HEX_COLOR.fullmatch(color):
            raise MyMenuColorError(f"Invalid My Menu palette color: {label}")
        palette_colors.append(color.casefold())
    if len(palette_colors) != len(set(palette_colors)):
        raise MyMenuColorError("My Menu palette colors must be unique.")
    if "Light Red" in palette and "Coral" in palette:
        light_red = _rgb(palette["Light Red"])
        coral = _rgb(palette["Coral"])
        if math.dist(light_red, coral) < 50:
            raise MyMenuColorError("Light Red and Coral must remain visually distinct.")

    assignments = data.get("assignments")
    if not isinstance(assignments, Mapping) or not assignments:
        raise MyMenuColorError("My Menu color assignments must be a non-empty mapping.")
    if len(assignments) > MAX_TABS:
        raise MyMenuColorError("My Menu supports at most five named color assignments.")
    names = set()
    choices = []
    for name, choice in assignments.items():
        if not isinstance(name, str) or not name.strip():
            raise MyMenuColorError("My Menu assignment names must be non-empty strings.")
        key = name.strip().casefold()
        if key in names:
            raise MyMenuColorError(f"Duplicate My Menu color assignment: {name}")
        names.add(key)
        if choice not in palette:
            raise MyMenuColorError(f"Unknown My Menu palette choice for {name}: {choice}")
        choices.append(choice)
    if len(choices) != len(set(choices)):
        raise MyMenuColorError("Named My Menu tabs must use distinct colors.")


def assigned_color_map(data):
    palette = data["palette"]
    return {
        name.strip().casefold(): palette[choice]
        for name, choice in data["assignments"].items()
    }


def menu_color(data, name, fallback_index=0):
    assigned = assigned_color_map(data).get(str(name or "").strip().casefold())
    if assigned:
        return assigned
    colors = list(data["palette"].values())
    return colors[min(max(fallback_index, 0), len(colors) - 1)]


def _rgb(value):
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))
