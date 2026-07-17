import html
import json
import os
import re
import shutil
import subprocess

from html_renderer import appendix_link_entries, card_colors, card_icon_paths, profile_subtitle, settings_rows


DEFAULT_NODE = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
DEFAULT_NODE_MODULES = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"


def render_png_pdf(paths, profile_name, profile, merged, icon_manager, baseline=None, include_png=False, include_pdf=False):
    """Generate explicitly requested fixed PNG and/or PDF card outputs."""
    if include_png:
        paths.png_output_dir.mkdir(parents=True, exist_ok=True)
        paths.phone_png_output_dir.mkdir(parents=True, exist_ok=True)
    if include_pdf:
        paths.pdf_output_dir.mkdir(parents=True, exist_ok=True)
    payload_path = paths.root / "80 Build" / ".render_payload.json"
    payload = _payload(paths, profile_name, profile, merged, icon_manager, baseline, include_png, include_pdf)
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    try:
        env = os.environ.copy()
        node_modules = os.environ.get("NODE_PATH") or _node_modules(paths)
        if node_modules:
            env["NODE_PATH"] = node_modules
        command = [_node_binary(), str(paths.root / "80 Build" / "render_card_outputs.js"), str(payload_path)]
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


def _payload(paths, profile_name, profile, merged, icon_manager, baseline=None, include_png=False, include_pdf=False):
    rows = []
    for row in settings_rows(profile, merged, paths):
        icon_path = icon_manager.icon_path(row["key"], row["value"])
        rows.append(
            {
                "label": row["label"],
                "value": str(row["value"]),
                "icon": str(icon_path) if icon_path else "",
            }
        )
    header_icons = card_icon_paths(paths, profile, baseline)
    return {
        "title": profile.get("title", profile_name),
        "subtitle": profile_subtitle(profile, baseline),
        "colors": card_colors(profile, baseline),
        "header_icons": {
            "left": str(header_icons["left"]) if header_icons["left"] else "",
            "right": str(header_icons["right"]) if header_icons["right"] else "",
        },
        "png": str(paths.png_output_file(profile_name)) if include_png else "",
        "phone_png": str(paths.phone_png_output_file(profile_name)) if include_png else "",
        "pdf": str(paths.pdf_output_file(profile_name)) if include_pdf else "",
        "rows": rows,
        "checklist": _plain_text_items(profile.get("checklist") or []),
        "watch_for": _plain_text_items(profile.get("watch_for") or []),
        "common_mistakes": _plain_text_items(profile.get("common_mistakes") or []),
        "notes": _plain_text_items(profile.get("notes") or [])
        + [entry["label"] for entry in appendix_link_entries(profile, paths)],
    }


def _plain_text_items(items):
    """Keep static card outputs readable when an HTML card item contains a link."""
    return [html.unescape(re.sub(r"<[^>]+>", "", str(item))) for item in items]
