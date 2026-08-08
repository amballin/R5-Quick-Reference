from html import escape
import os
from pathlib import Path
import re
from urllib.parse import quote

from validators.common import load_yaml_checked
from site_navigation import SITE_NAV_CSS, site_navigation

from utilities import flatten


DEFAULT_CARD_COLORS = {
    "background": "#1e3553",
    "text": "#ffffff",
}

FIELD_ACCESS_COLORS = {
    "access-switch": "#72dda8",
    "access-menu-2": "#f0bf69",
    "access-menu-3": "#c6a6ff",
    "access-menu-4": "#ff9fba",
    "access-menu-5": "#80d8ff",
    "access-menu-6": "#ff9b7a",
}

LABEL = {
    "exposure.mode": "Mode",
    "exposure.metering": "Metering",
    "autofocus.operation": "AF Operation",
    "autofocus.servo_af_case": "Servo AF Case",
    "autofocus.tracking_sensitivity": "Track / Accel",
    "autofocus.accel_decel_tracking": "Accel./Decel. Tracking",
    "autofocus.switching_tracked_subjects": "Switching Tracked Subjects",
    "autofocus.subject_detection": "Subject Detection",
    "autofocus.eye_detection": "Eye Detection",
    "autofocus.method": "AF Method",
    "autofocus.touch_drag_af": "Touch & Drag AF",
    "autofocus.touch_drag_positioning_method": "Positioning method",
    "autofocus.touch_drag_active_area": "Active touch area",
    "drive.mode": "Drive",
    "display.high_speed_display": "High Speed Display",
    "shutter.target": "Shutter",
    "shutter.type": "Shutter Type",
    "lens.aperture.target": "Aperture",
    "stabilization.image_stabilization.mode": "Image Stabilization",
    "stabilization.ibis": "IBIS",
    "stabilization.lens_is": "Lens IS",
    "exposure.iso.mode": "ISO",
    "exposure.iso.value": "ISO Value",
    "exposure.auto_iso.maximum": "Auto ISO Max",
    "exposure.exposure_compensation": "Exposure Comp",
    "display.screen_info_settings": "Screen Info",
    "display.histogram": "Histogram",
    "display.highlight_alert": "Highlight Alert",
    "image.quality": "Image Quality",
    "image.cropping_aspect_ratio": "Crop / Aspect",
    "image.white_balance": "White Balance",
    "image.focus_bracketing": "Focus Bracketing",
    "image.highlight_tone_priority": "Highlight Tone Priority",
    "image.high_iso_noise_reduction": "High ISO NR",
    "image.long_exposure_noise_reduction.value": "Long Exposure NR",
    "camera_setup.custom_shooting_mode_auto_update": "C1-C3 Auto Update",
    "camera_setup.electronic_full_time_mf": "Electronic Full-time MF",
    "camera_setup.ibis_high_res_shot": "IBIS High Res Shot",
    "camera_setup.continuous_af": "Continuous AF",
}

REQUIRED_CARD_SETTINGS = {
    "exposure.mode",
    "autofocus.operation",
    "autofocus.servo_af_case",
    "autofocus.tracking_sensitivity",
    "autofocus.accel_decel_tracking",
    "autofocus.switching_tracked_subjects",
    "autofocus.subject_detection",
    "autofocus.eye_detection",
    "autofocus.method",
    "drive.mode",
    "display.high_speed_display",
    "shutter.target",
    "shutter.type",
    "lens.aperture.target",
    "stabilization.image_stabilization.mode",
    "exposure.iso.mode",
    "exposure.auto_iso.maximum",
}

CAMERA_DEFAULT_EXTRA_SETTINGS = {
    "exposure.metering",
    "shutter.type",
    "stabilization.ibis",
    "stabilization.lens_is",
    "display.highlight_alert",
    "image.quality",
    "image.white_balance",
    "image.long_exposure_noise_reduction.value",
}

CAMERA_SETUP_SETTINGS = {
    "shutter.type",
    "autofocus.touch_drag_af",
    "autofocus.touch_drag_positioning_method",
    "autofocus.touch_drag_active_area",
    "display.screen_info_settings",
    "display.histogram",
    "display.highlight_alert",
    "display.high_speed_display",
    "image.highlight_tone_priority",
    "image.high_iso_noise_reduction",
    "image.long_exposure_noise_reduction.value",
    "image.cropping_aspect_ratio",
    "camera_setup.custom_shooting_mode_auto_update",
    "camera_setup.electronic_full_time_mf",
    "camera_setup.ibis_high_res_shot",
    "camera_setup.continuous_af",
}


def settings_rows(profile, merged, paths=None):
    """Return the settings rows in the same order used by the HTML table."""
    if profile.get("card_type") == "reference":
        return [
            {
                "key": reference_setting_key(item["control"]),
                "label": item["control"],
                "value": item["assignment"],
            }
            for item in profile.get("reference_settings") or []
        ]
    merged_fields = flatten(merged)
    override_fields = flatten(profile.get("overrides", {}))
    if is_camera_setup(profile):
        keys = set(CAMERA_SETUP_SETTINGS) | set(override_fields)
    else:
        keys = required_card_settings(paths) | set(override_fields)
    if is_camera_defaults(profile):
        keys |= CAMERA_DEFAULT_EXTRA_SETTINGS
    rows = []
    for key in card_setting_order(paths):
        label = LABEL[key]
        if key in keys and key in merged_fields:
            if key == "autofocus.servo_af_case" and not servo_af(merged_fields):
                continue
            if key == "autofocus.tracking_sensitivity":
                if not servo_af(merged_fields) or automatic_servo_af_case(merged_fields):
                    continue
                value = (
                    f"{display_value(merged_fields.get('autofocus.tracking_sensitivity'))} / "
                    f"{display_value(merged_fields.get('autofocus.accel_decel_tracking'))}"
                )
                rows.append({"key": key, "label": label, "value": value})
                continue
            if key == "autofocus.accel_decel_tracking":
                continue
            if key == "autofocus.switching_tracked_subjects" and not subject_switching_supported(merged_fields):
                continue
            if key == "display.high_speed_display" and not high_speed_display_relevant(merged_fields):
                continue
            if manual_focus(merged_fields) and key in {
                "autofocus.subject_detection",
                "autofocus.eye_detection",
                "autofocus.method",
            }:
                continue
            if af_method_not_used(merged_fields) and key in {
                "autofocus.subject_detection",
                "autofocus.eye_detection",
            }:
                continue
            if key == "stabilization.lens_is":
                continue
            if key == "stabilization.ibis":
                row = stabilization_system_row(keys, merged_fields)
                if row is None:
                    continue
                rows.append(row)
                continue
            value = merged_fields[key]
            if value is None:
                value = "—"
            if key == "exposure.auto_iso.maximum":
                continue
            if key == "exposure.iso.value":
                continue
            if key == "exposure.iso.mode":
                value = iso_display_value(merged_fields)
            rows.append({"key": key, "label": label, "value": value})
    return rows


def reference_setting_key(control):
    """Return a stable renderer key for a reference-card control label."""
    slug = re.sub(r"[^a-z0-9]+", "_", str(control).casefold()).strip("_")
    return f"reference.{slug}"


def required_card_settings(paths=None):
    if paths is None:
        return set(REQUIRED_CARD_SETTINGS)
    layout_path = paths.root / "00 Master" / "card_layout.yaml"
    try:
        layout = load_yaml_checked(layout_path) or {}
        entries = (layout.get("card_layout") or {}).get("always_show") or []
        keys = {entry.get("key") for entry in entries if isinstance(entry, dict) and entry.get("key")}
        return keys or set(REQUIRED_CARD_SETTINGS)
    except (OSError, ValueError):
        return set(REQUIRED_CARD_SETTINGS)


def card_setting_order(paths=None):
    """Return the configured display order, followed by any unconfigured legacy fields."""
    configured = []
    if paths is not None:
        layout_path = paths.root / "00 Master" / "card_layout.yaml"
        try:
            layout = load_yaml_checked(layout_path) or {}
            configured = (layout.get("card_layout") or {}).get("display_order") or []
        except (OSError, ValueError):
            configured = []
    known = [key for key in configured if key in LABEL]
    return known + [key for key in LABEL if key not in known]


def is_camera_defaults(profile):
    return profile.get("title") == "Camera Defaults"


def is_camera_setup(profile):
    return profile.get("title") == "Camera Setup Essentials"


def manual_focus(merged_fields):
    return merged_fields.get("autofocus.operation") == "Manual Focus"


def servo_af(merged_fields):
    return merged_fields.get("autofocus.operation") == "Servo AF"


def automatic_servo_af_case(merged_fields):
    value = str(merged_fields.get("autofocus.servo_af_case") or "").casefold()
    return value in {"case a", "case a (auto)", "auto"}


def subject_switching_supported(merged_fields):
    method = re.sub(r"\s+", " ", str(merged_fields.get("autofocus.method") or "").casefold().replace("+", " ")).strip()
    return method in {
        "face tracking",
        "zone af",
        "large zone af",
        "large zone af (horizontal)",
        "large zone af (vertical)",
    }


def high_speed_display_relevant(merged_fields):
    return (
        merged_fields.get("drive.mode") == "High Speed Continuous"
        or merged_fields.get("shutter.type") == "Electronic"
    )


def display_value(value):
    return "—" if value is None else str(value)


def af_method_not_used(merged_fields):
    return merged_fields.get("autofocus.method") == "Not Used"


def stabilization_system_row(keys, merged_fields):
    parts = [
        ("stabilization.ibis", "IBIS"),
        ("stabilization.lens_is", "Lens IS"),
    ]
    active = [
        (key, label, merged_fields.get(key))
        for key, label in parts
        if key in keys and merged_fields.get(key) is not None
    ]
    if not active:
        return None
    if len(active) == 1:
        key, label, value = active[0]
        return {"key": key, "label": label, "value": value}
    return {
        "key": "stabilization.ibis",
        "label": "IBIS/Lens IS",
        "value": " / ".join(str(value) for _, _, value in active),
    }


def iso_display_value(merged_fields):
    mode = merged_fields.get("exposure.iso.mode")
    if mode == "Fixed":
        return merged_fields.get("exposure.iso.value", mode)
    maximum = merged_fields.get("exposure.auto_iso.maximum")
    if mode == "Auto" and maximum is not None:
        return f"{mode} - {maximum}"
    return mode


def table(profile, merged, icon_manager=None, paths=None):
    """Render the settings table with optional field-based icons."""
    html = "<table>"
    access_classes = field_setup_setting_classes(profile)
    for row in settings_rows(profile, merged, paths):
        rendered_label = row["label"]
        if icon_manager is not None:
            rendered_label = icon_manager.icon_html(row["key"], row["label"], row["value"])
        access_class = access_classes.get(row["key"])
        class_attribute = f' class="field-value {access_class}"' if access_class else ""
        html += f"<tr><td>{rendered_label}</td><td{class_attribute}>{row['value']}</td></tr>"
    return html + "</table>"


def bullets(items):
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def render_card(template, profile_name, profile, merged, icon_manager=None, baseline=None, paths=None):
    """Replace the existing card template placeholders."""
    colors = card_colors(profile, baseline)
    return (
        template.replace("{{TITLE}}", profile.get("title", profile_name))
        .replace("{{SUBTITLE_BLOCK}}", subtitle_block(profile, baseline))
        .replace("{{FIELD_SETUP_STRIP}}", field_setup_strip(profile))
        .replace("{{BACKGROUND_COLOR}}", colors["background"])
        .replace("{{TEXT_COLOR}}", colors["text"])
        .replace("{{SITE_NAV_CSS}}", SITE_NAV_CSS)
        .replace(
            "{{NAVIGATION_HEADER}}",
            site_navigation(
                "../../merged-build/index.html",
                "../../merged-build/index.html",
                right_html=header_icon_html(paths, profile, baseline, "header"),
            ),
        )
        .replace("{{HEADER_ICON_LEFT}}", header_icon_html(paths, profile, baseline, "left"))
        .replace("{{HEADER_ICON_RIGHT}}", header_icon_html(paths, profile, baseline, "right"))
        .replace("{{SETTINGS_SECTION}}", settings_section(profile, merged, icon_manager, paths))
        .replace("{{CHECKLIST}}", bullets(profile.get("checklist") or []))
        .replace("{{WATCH}}", bullets(profile.get("watch_for") or []))
        .replace("{{MISTAKES}}", bullets(profile.get("common_mistakes") or []))
        .replace("{{NOTES}}", bullets(card_note_items(profile, paths)))
    )


def appendix_link_entries(profile, paths=None):
    configured = profile.get("appendix_links") or []
    if not configured or paths is None:
        return []
    manifest = load_yaml_checked(paths.root / "50 Field Guide" / "required_appendices.yaml") or {}
    targets = {
        entry.get("id"): f"{Path(entry.get('file', '')).stem}.html"
        for entry in manifest.get("appendices", []) or []
        if entry.get("id") and entry.get("file")
    }
    return [
        {
            "id": item["id"],
            "label": item.get("label") or item["id"],
            "filename": targets[item["id"]],
        }
        for item in configured
        if isinstance(item, dict) and item.get("id") in targets
    ]


def card_note_items(profile, paths=None):
    items = []
    setup_note = field_setup_note(profile)
    if setup_note:
        items.append(setup_note)
    items.extend(profile.get("notes") or [])
    for link in appendix_link_entries(profile, paths):
        return_target = quote(f"../Cards/{profile.get('title', 'Card')}.html", safe="/.")
        href = quote(f"../../field-guide/html/{link['filename']}", safe="/:#%")
        href = f"{href}?return={return_target}"
        items.append(f'<a href="{href}">{escape(link["label"])}</a>')
    return items


def settings_section(profile, merged, icon_manager=None, paths=None):
    return f"<h2>Settings</h2>{table(profile, merged, icon_manager, paths)}"


def field_setup(profile):
    card = profile.get("card") or {}
    setup = card.get("field_setup") or {}
    return setup if isinstance(setup, dict) else {}


def field_setup_menus(profile):
    """Return My Menu entries with stable renderer-managed color classes."""
    menus = field_setup(profile).get("my_menus") or []
    alternate_number = 2
    rendered = []
    for menu in menus:
        if not isinstance(menu, dict):
            continue
        name = str(menu.get("name") or "").strip()
        if name.casefold() == "switch":
            access_class = "access-switch"
        else:
            access_class = f"access-menu-{min(alternate_number, 6)}"
            alternate_number += 1
        rendered.append(
            {
                **menu,
                "name": name,
                "access_class": access_class,
                "color": FIELD_ACCESS_COLORS[access_class],
            }
        )
    return rendered


def field_setup_setting_classes(profile):
    classes = {}
    for menu in field_setup_menus(profile):
        for key in menu.get("settings") or []:
            classes[key] = menu["access_class"]
    return classes


def field_setup_value_colors(profile):
    return {
        key: FIELD_ACCESS_COLORS[access_class]
        for key, access_class in field_setup_setting_classes(profile).items()
    }


def field_setup_summary(profile):
    setup = field_setup(profile)
    if not setup:
        return None
    return {
        "start": setup.get("start", ""),
        "source_profile": setup.get("source_profile", ""),
        "access_only": setup.get("access_only") is True,
        "menus": field_setup_menus(profile),
    }


def field_setup_strip(profile):
    summary = field_setup_summary(profile)
    if not summary:
        return ""
    parts = []
    if summary["start"]:
        parts.append(f'<span class="field-route-start">{escape(str(summary["start"]))}</span>')
    for menu in summary["menus"]:
        parts.append(
            f'<span class="field-route-menu {menu["access_class"]}">'
            f'★ {escape(menu["name"])}</span>'
        )
    aria_label = "Field access shortcuts" if summary["access_only"] else "Field setup shortcuts"
    return f'<div class="field-route" aria-label="{aria_label}">' + "".join(parts) + "</div>"


def field_setup_note(profile):
    summary = field_setup_summary(profile)
    if not summary:
        return ""
    if summary["access_only"]:
        return (
            "Colored setting values use the matching My Menu tab; white values use "
            "Quick Control, dials, buttons, or normal menu access."
        )
    start = escape(str(summary["start"]))
    source = escape(str(summary["source_profile"]))
    prefix = f"Start from {start} {source} after verifying its registration."
    if not summary["menus"]:
        return prefix
    return (
        f"{prefix} Colored setting values use the matching My Menu tab; "
        "white values use Quick Control, dials, or buttons."
    )


def profile_subtitle(profile, baseline=None):
    if "subtitle" in profile:
        return profile.get("subtitle") or ""
    if baseline:
        return baseline.get("subtitle") or ""
    return ""


def subtitle_block(profile, baseline=None):
    subtitle = profile_subtitle(profile, baseline)
    return f'<div class="sub">{subtitle}</div>' if subtitle else ""


def card_options(profile, baseline=None):
    options = {}
    if baseline:
        options = merge_dicts(options, baseline.get("card") or {})
    options = merge_dicts(options, profile.get("card") or {})
    return options


def card_colors(profile, baseline=None):
    colors = dict(DEFAULT_CARD_COLORS)
    configured = (card_options(profile, baseline).get("colors") or {})
    for key in colors:
        if configured.get(key):
            colors[key] = configured[key]
    return colors


def card_icon_paths(paths, profile, baseline=None):
    icons = (card_options(profile, baseline).get("icons") or {})
    return {
        "header": resolve_card_icon(paths, icons.get("header")),
        "left": resolve_card_icon(paths, icons.get("left")),
        "right": resolve_card_icon(paths, icons.get("right")),
    }


def shared_header_icon_path(paths):
    """Return the baseline icon used by shared Camera Settings headers."""
    if paths is None:
        return None
    try:
        baseline = load_yaml_checked(paths.baseline_file) or {}
    except (OSError, ValueError):
        return None
    return card_icon_paths(paths, {}, baseline).get("header")


def header_icon_html(paths, profile, baseline, side):
    if paths is None:
        return ""
    icon_path = card_icon_paths(paths, profile, baseline).get(side)
    if not icon_path:
        return ""
    src = os.path.relpath(icon_path, paths.html_output_dir).replace(os.sep, "/")
    return f'<img src="{quote(str(src), safe="/.")}" alt="" aria-hidden="true" onerror="this.hidden=true">'


def resolve_card_icon(paths, value):
    if paths is None or value in (None, ""):
        return None
    text = str(value).strip()
    if text.lower() in {"none", "null"}:
        return None

    candidate = Path(text).expanduser()
    if candidate.is_absolute() and candidate.exists():
        return candidate

    candidates = [
        paths.root / text,
        paths.icon_asset_dir / text,
    ]
    if not Path(text).suffix:
        candidates.extend(card_logo_candidates(paths, text))
        candidates.extend(
            [
                paths.icon_asset_dir / "icons/card_icons" / "SVG" / f"{text}.svg",
                paths.icon_asset_dir / "icons/card_icons" / "PNG" / f"{text}.png",
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def card_logo_candidates(paths, text):
    manifest = paths.icon_asset_dir / "Card Logos" / "manifest.yaml"
    if not manifest.exists():
        return []

    normalized = text.strip().lower().replace("_", " ")
    candidates = []
    for icon in read_card_logo_manifest(manifest):
        field_id = str(icon.get("field_id", "")).lower().replace("_", " ")
        label = str(icon.get("label", "")).lower()
        if normalized not in {field_id, label}:
            continue
        # Card logos are often raster originals wrapped in SVG; prefer PNG for HTML reliability.
        if icon.get("png"):
            candidates.append(paths.icon_asset_dir / "Card Logos" / icon["png"])
        if icon.get("svg"):
            candidates.append(paths.icon_asset_dir / "Card Logos" / icon["svg"])
    return candidates


def read_card_logo_manifest(manifest):
    icons = []
    current = None
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("- field_id:"):
            if current:
                icons.append(current)
            current = {"field_id": line.split(":", 1)[1].strip().strip('"')}
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        current[key.strip()] = value.strip().strip('"')
    if current:
        icons.append(current)
    return icons


def merge_dicts(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def write_html_card(paths, profile_name, html):
    paths.html_output_dir.mkdir(parents=True, exist_ok=True)
    paths.html_output_file(profile_name).write_text(html)
