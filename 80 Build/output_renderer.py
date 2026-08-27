import html
import json
import os
import re
import shutil
import subprocess

from cx_route_analysis import row_requires_change

from html_renderer import (
    card_colors,
    card_icon_paths,
    card_note_items,
    field_setup_change_summary,
    field_setup_summary,
    field_setup_value_colors,
    profile_subtitle,
    settings_rows,
)
from lens_guidance import compatibility_messages, resolved_choices


DEFAULT_NODE = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
DEFAULT_NODE_MODULES = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"


def render_pdf(paths, profile_name, profile, merged, icon_manager, baseline=None):
    """Generate an explicitly requested fixed PDF card output."""
    paths.pdf_output_dir.mkdir(parents=True, exist_ok=True)
    payload_path = paths.root / "80 Build" / ".render_payload.json"
    payload = _payload(paths, profile_name, profile, merged, icon_manager, baseline)
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    try:
        env = os.environ.copy()
        node_modules = os.environ.get("NODE_PATH") or _node_modules(paths)
        if node_modules:
            env["NODE_PATH"] = node_modules
        command = [_node_binary(), str(paths.root / "80 Build" / "render_card_pdf.js"), str(payload_path)]
        subprocess.run(command, check=True, env=env, capture_output=True, text=True)
    finally:
        try:
            payload_path.unlink()
        except FileNotFoundError:
            pass


def _node_binary():
    return os.environ.get("NODE") or shutil.which("node") or DEFAULT_NODE


def _node_modules(paths):
    local_modules = paths.root / "node_modules"
    if local_modules.exists():
        return str(local_modules)
    if os.path.exists(DEFAULT_NODE_MODULES):
        return DEFAULT_NODE_MODULES
    return ""


def _payload(paths, profile_name, profile, merged, icon_manager, baseline=None):
    rows = []
    value_colors = field_setup_value_colors(profile, merged, paths)
    change_summary = field_setup_change_summary(profile, merged, baseline, paths)
    changed_paths = (change_summary or {}).get("changed_paths") or set()
    for row in settings_rows(profile, merged, paths):
        icon_path = icon_manager.icon_path(row["key"], row["value"])
        rows.append(
            {
                "label": row["label"],
                "value": str(row["value"]),
                "detail": str(row.get("detail") or ""),
                "row_type": row.get("row_type", "item"),
                "section_color": row.get("section_color", ""),
                "icon": str(icon_path) if icon_path else "",
                "access_color": value_colors.get(row["key"], ""),
                "change_required": bool(change_summary and row_requires_change(row["key"], changed_paths)),
                "change_color": value_colors.get(row["key"], "") or card_colors(profile, baseline)["text"],
            }
        )
    header_icons = card_icon_paths(paths, profile, baseline)
    return {
        "title": profile.get("title", profile_name),
        "subtitle": profile_subtitle(profile, baseline),
        "field_setup": field_setup_summary(profile, merged, paths),
        "change_legend": (change_summary or {}).get("legend_label", ""),
        "colors": card_colors(profile, baseline),
        "header_icons": {
            "left": str(header_icons["left"]) if header_icons["left"] else "",
            "right": str(header_icons["right"]) if header_icons["right"] else "",
        },
        "pdf": str(paths.pdf_output_file(profile_name)),
        "rows": rows,
        "lens_choices": [
            (
                f'{choice["role_label"]} — {choice["display_name"]}: '
                f'{choice["use_when"]}. Check: {choice["field_check"]}'
            )
            for choice in resolved_choices(profile, paths.root)
        ],
        "compatibility": compatibility_messages(profile, merged, paths.root, surface="card"),
        "checklist": _plain_text_items(profile.get("checklist") or []),
        "watch_for": _plain_text_items(profile.get("watch_for") or []),
        "common_mistakes": _plain_text_items(profile.get("common_mistakes") or []),
        "notes": _plain_text_items(card_note_items(profile, paths, merged)),
    }


def _plain_text_items(items):
    """Keep static card outputs readable when an HTML card item contains a link."""
    return [html.unescape(re.sub(r"<[^>]+>", "", str(item))) for item in items]
