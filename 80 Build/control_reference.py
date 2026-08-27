"""Render canonical camera controls as card rows and Markdown tables."""

from __future__ import annotations

import re
from pathlib import Path

from validators.common import load_yaml_checked


CONTROL_TABLE_PATTERN = re.compile(
    r"<!--\s*CONTROL_REFERENCE_TABLE:\s*(controls|dials)\s*-->",
    re.IGNORECASE,
)

CARD_CONTROL_LABELS = {
    "Shutter half-press": "Shutter button half-press",
    "AF-ON": "AF-ON button",
    "AE Lock": "AE Lock button",
    "AF Point Selection": "AF Point Selection button",
    "SET": "SET button",
    "Depth-of-field preview": "DOF button",
    "M-Fn": "M-Fn button",
}

# Default/unassigned controls remain useful in the complete reference tables but
# do not belong on the concise Camera Buttons card.
CARD_OMITTED_CONTROLS = {"Movie Record", "MODE", "LCD panel illumination"}

INFO_LABELS = {
    "af_operation": "AF Operation",
    "af_method": "AF Method",
    "servo_af_characteristics": "Servo AF characteristics",
}


def _root(paths_or_root):
    root = paths_or_root if isinstance(paths_or_root, (str, Path)) else paths_or_root.root
    return Path(root)


def load_control_source(paths_or_root):
    source = load_yaml_checked(_root(paths_or_root) / "controls.yaml") or {}
    if not isinstance(source, dict):
        raise ValueError("controls.yaml must contain a mapping.")
    return source


def _entries(source, group):
    entries = source.get(group)
    if not isinstance(entries, list):
        raise ValueError(f"controls.yaml {group} must be a list.")
    return entries


def _normalized_info_key(value):
    return str(value).strip().casefold().replace(" ", "_")


def entry_detail(entry):
    """Return one display detail assembled only from canonical structured fields."""
    parts = []
    info = entry.get("info_details") or {}
    for key, value in info.items():
        normalized = _normalized_info_key(key)
        label = INFO_LABELS.get(normalized, str(key).replace("_", " ").strip().title())
        parts.append(f"{label}: {value}")
    for field in ("operation", "notes"):
        value = entry.get(field)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip().rstrip("."))
    return "; ".join(parts) or "—"


def card_reference_rows(paths_or_root):
    """Return renderer-ready rows for the derived Camera Buttons card."""
    source = load_control_source(paths_or_root)
    rows = []
    for group in ("controls", "dials"):
        for entry in _entries(source, group):
            control = entry.get("control")
            assignment = entry.get("assignment")
            if not isinstance(control, str) or not isinstance(assignment, str):
                raise ValueError(f"controls.yaml {group} entries require control and assignment strings.")
            if group == "controls" and control in CARD_OMITTED_CONTROLS:
                continue
            rows.append(
                {
                    "key": reference_setting_key(CARD_CONTROL_LABELS.get(control, control)),
                    "label": CARD_CONTROL_LABELS.get(control, control),
                    "value": assignment,
                    "detail": entry_detail(entry) if group == "controls" else "",
                }
            )
    return rows


def card_reference_settings(paths_or_root):
    """Return editor-friendly forms of the same derived card rows."""
    return [
        {
            "control": row["label"],
            "assignment": row["value"],
            "detail": row.get("detail", ""),
        }
        for row in card_reference_rows(paths_or_root)
    ]


def reference_setting_key(control):
    slug = re.sub(r"[^a-z0-9]+", "_", str(control).casefold()).strip("_")
    return f"reference.{slug}"


def markdown_table(paths_or_root, group):
    """Generate a complete Markdown control or dial table."""
    source = load_control_source(paths_or_root)
    if group == "controls":
        lines = [
            "| Physical control | Assignment | INFO details or operation |",
            "|---|---|---|",
        ]
        for entry in _entries(source, group):
            lines.append(
                f"| {_markdown_cell(entry.get('control'))} | "
                f"{_markdown_cell(entry.get('assignment'))} | "
                f"{_markdown_cell(entry_detail(entry))} |"
            )
        return "\n".join(lines)
    if group == "dials":
        lines = [
            "| Physical control | Assignment | Operation |",
            "|---|---|---|",
        ]
        for entry in _entries(source, group):
            lines.append(
                f"| {_markdown_cell(entry.get('control'))} | "
                f"{_markdown_cell(entry.get('assignment'))} | "
                f"{_markdown_cell(entry_detail(entry))} |"
            )
        return "\n".join(lines)
    raise ValueError(f"Unknown canonical control-table group: {group}")


def inject_control_tables(markdown, paths_or_root):
    """Replace canonical control-table markers without rewriting source Markdown."""
    return CONTROL_TABLE_PATTERN.sub(
        lambda match: markdown_table(paths_or_root, match.group(1).casefold()),
        markdown,
    )


def _markdown_cell(value):
    if value is None:
        return "—"
    return str(value).replace("|", r"\|").replace("\n", " ").strip() or "—"
