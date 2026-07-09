from html import escape
from pathlib import Path
from urllib.parse import quote

from utilities import flatten


DEFAULT_CARD_COLORS = {
    "background": "#1e3553",
    "text": "#ffffff",
}

LABEL = {
    "exposure.mode": "Mode",
    "exposure.metering": "Metering",
    "autofocus.operation": "AF Operation",
    "autofocus.subject_detection": "Subject Detection",
    "autofocus.eye_detection": "Eye Detection",
    "autofocus.method": "AF Method",
    "drive.mode": "Drive",
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
    "display.histogram": "Histogram",
    "display.highlight_alert": "Highlight Alert",
    "image.quality": "Image Quality",
    "image.white_balance": "White Balance",
    "image.highlight_tone_priority": "Highlight Tone Priority",
    "image.high_iso_noise_reduction": "High ISO NR",
    "image.long_exposure_noise_reduction.value": "Long Exposure NR",
    "camera_setup.electronic_full_time_mf": "Electronic Full-time MF",
    "camera_setup.ibis_high_res_shot": "IBIS High Res Shot",
    "camera_setup.continuous_af": "Continuous AF",
}

REQUIRED_CARD_SETTINGS = {
    "exposure.mode",
    "autofocus.operation",
    "autofocus.subject_detection",
    "autofocus.eye_detection",
    "autofocus.method",
    "drive.mode",
    "shutter.target",
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


def settings_rows(profile, merged):
    """Return the settings rows in the same order used by the HTML table."""
    merged_fields = flatten(merged)
    override_fields = flatten(profile.get("overrides", {}))
    if is_camera_setup(profile):
        keys = set(override_fields)
    else:
        keys = REQUIRED_CARD_SETTINGS | set(override_fields)
    if is_camera_defaults(profile):
        keys |= CAMERA_DEFAULT_EXTRA_SETTINGS
    rows = []
    for key, label in LABEL.items():
        if key in keys and key in merged_fields:
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
                continue
            if key == "exposure.auto_iso.maximum":
                continue
            if key == "exposure.iso.value":
                continue
            if key == "exposure.iso.mode":
                value = iso_display_value(merged_fields)
            rows.append({"key": key, "label": label, "value": value})
    return rows


def is_camera_defaults(profile):
    return profile.get("title") == "Camera Defaults"


def is_camera_setup(profile):
    return profile.get("title") == "Camera Setup"


def manual_focus(merged_fields):
    return merged_fields.get("autofocus.operation") == "Manual Focus"


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


def table(profile, merged, icon_manager=None):
    """Render the settings table with optional field-based icons."""
    html = "<table>"
    for row in settings_rows(profile, merged):
        rendered_label = row["label"]
        if icon_manager is not None:
            rendered_label = icon_manager.icon_html(row["key"], row["label"], row["value"])
        html += f"<tr><td>{rendered_label}</td><td>{row['value']}</td></tr>"
    return html + "</table>"


def bullets(items):
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def render_card(template, profile_name, profile, merged, icon_manager=None, baseline=None, paths=None):
    """Replace the existing card template placeholders."""
    colors = card_colors(profile, baseline)
    return (
        template.replace("{{TITLE}}", profile.get("title", profile_name))
        .replace("{{SUBTITLE_BLOCK}}", subtitle_block(profile, baseline))
        .replace("{{BACKGROUND_COLOR}}", colors["background"])
        .replace("{{TEXT_COLOR}}", colors["text"])
        .replace("{{HEADER_ICON_LEFT}}", header_icon_html(paths, profile, baseline, "left"))
        .replace("{{HEADER_ICON_RIGHT}}", header_icon_html(paths, profile, baseline, "right"))
        .replace("{{SETTINGS}}", table(profile, merged, icon_manager))
        .replace("{{CHECKLIST}}", bullets(profile.get("checklist") or []))
        .replace("{{WATCH}}", bullets(profile.get("watch_for") or []))
        .replace("{{MISTAKES}}", bullets(profile.get("common_mistakes") or []))
        .replace("{{NOTES}}", bullets(profile.get("notes") or []))
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
        "left": resolve_card_icon(paths, icons.get("left")),
        "right": resolve_card_icon(paths, icons.get("right")),
    }


def header_icon_html(paths, profile, baseline, side):
    if paths is None:
        return ""
    icon_path = card_icon_paths(paths, profile, baseline).get(side)
    if not icon_path:
        return ""
    try:
        src = icon_path.relative_to(paths.html_output_dir).as_posix()
    except ValueError:
        src = Path("../../") / icon_path.relative_to(paths.root)
        src = src.as_posix()
    return f'<img src="{quote(str(src), safe="/.")}" alt="" aria-hidden="true">'


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
