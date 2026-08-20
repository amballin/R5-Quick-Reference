"""Materialize the persisted My Menu layout as reference-card rows."""

from __future__ import annotations

from validators.common import load_yaml_checked
from my_menu import load_my_menu, used_tabs
from my_menu_colors import load_my_menu_colors, menu_color


def catalog_items(paths):
    catalog_path = paths.root / "80 Build" / "profile_editor" / "canon_options.yaml"
    catalog = load_yaml_checked(catalog_path) or {}
    return {
        item["id"]: item
        for section in catalog.get("reference_sections") or []
        for item in section.get("items") or []
        if isinstance(item, dict) and item.get("id")
    }


def reference_rows(paths):
    items = catalog_items(paths)
    configuration = load_my_menu(paths, items)
    colors = load_my_menu_colors(paths)
    rows = []
    for tab_index, tab in enumerate(used_tabs(configuration), start=1):
        rows.append(
            {
                "key": f"reference.my_menu_{tab_index}",
                "label": f"MY MENU{tab_index}",
                "value": tab["name"],
                "row_type": "section",
                "section_color": menu_color(colors, tab["name"], tab_index - 1),
            }
        )
        for item_index, item_id in enumerate(tab["items"], start=1):
            item = items[item_id]
            rows.append(
                {
                    "key": f"reference.my_menu_{tab_index}_item_{item_index}",
                    "label": f"Item {item_index}",
                    "value": item["label"],
                    "detail": item.get("menu_location") or "",
                    "row_type": "item",
                }
            )
    return rows


def reference_settings(paths):
    """Editor-friendly form of the same rows used by card rendering."""
    return [
        {
            "control": row["label"],
            "assignment": row["value"],
            "detail": row.get("detail", ""),
            "rowType": row.get("row_type", "item"),
            "color": row.get("section_color", ""),
        }
        for row in reference_rows(paths)
    ]
