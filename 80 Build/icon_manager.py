import os
from urllib.parse import quote

import yaml


ICON_COLOR_FILTER = (
    "brightness(0) saturate(100%) invert(76%) sepia(32%) saturate(784%) "
    "hue-rotate(178deg) brightness(103%) contrast(101%)"
)

FIELD_ALIASES = {
    "autofocus.method": "af_method",
    "autofocus.operation": "af_operation",
    "autofocus.subject_detection": "subject_detection",
    "drive.mode": "drive",
    "exposure.auto_iso.maximum": "iso",
    "exposure.exposure_compensation": "exposure_compensation",
    "exposure.iso.mode": "iso",
    "exposure.iso.value": "iso",
    "exposure.metering": "metering",
    "exposure.mode": "mode",
    "image.long_exposure_noise_reduction.value": "long_exposure_nr",
    "image.quality": "image_quality_raw",
    "image.white_balance": "white_balance",
    "lens.aperture.target": "aperture",
    "display.histogram": "histogram",
    "display.highlight_alert": "highlight_alert",
    "shutter.type": "shutter",
    "shutter.target": "shutter",
    "stabilization.image_stabilization.mode": "image_stabilization",
    "stabilization.ibis": "image_stabilization",
    "stabilization.lens_is": "image_stabilization",
}

OFFICIAL_MODE_METADATA = "60 Assets/icons/canon_r5_official/modes.yaml"
MODE_SELECT_ICON = "60 Assets/icons/canon_r5_official/mode-select.svg"

SHOOTING_MODE_VALUE_IDS = {
    "A+": "mode-a-plus",
    "Scene Intelligent Auto": "mode-a-plus",
    "Fv": "mode-fv",
    "P": "mode-p",
    "Tv": "mode-tv",
    "Av": "mode-av",
    "M": "mode-m",
    "Manual": "mode-m",
    "Manual Exposure": "mode-m",
    "BULB": "mode-bulb",
    "Bulb": "mode-bulb",
    "C1": "mode-c1",
    "C2": "mode-c2",
    "C3": "mode-c3",
}

FOCUS_FEATURE_IDS = {
    "Focus Bracketing": "focus-bracketing",
    "Focus Guide": "focus-guide",
    "MF Peaking": "focus-mf-peaking",
    "MF peaking settings": "focus-mf-peaking",
}

OFFICIAL_VALUE_ICONS = {
    ("autofocus.operation", "Manual Focus"): "60 Assets/icons/canon_r5_official/lens_mf.svg",
    ("autofocus.operation", "One Shot AF"): "60 Assets/icons/canon_r5_official/lens_af.svg",
    ("autofocus.operation", "One-Shot AF"): "60 Assets/icons/canon_r5_official/lens_af.svg",
    ("autofocus.operation", "Servo AF"): "60 Assets/icons/canon_r5_official/lens_af.svg",
    ("autofocus.eye_detection", "Disable"): "60 Assets/icons/canon_r5_official/eye_detection.svg",
    ("autofocus.eye_detection", "Enable"): "60 Assets/icons/canon_r5_official/eye_detection.svg",
    ("autofocus.method", "1-Point AF"): "60 Assets/icons/canon_r5_official/one_point_af.svg",
    ("autofocus.method", "Expand AF Area"): "60 Assets/icons/canon_r5_official/expand_af_area.svg",
    ("autofocus.method", "Face + Tracking"): "60 Assets/icons/canon_r5_official/face_tracking.svg",
    ("autofocus.method", "Face+Tracking"): "60 Assets/icons/canon_r5_official/face_tracking.svg",
    ("autofocus.method", "Spot AF"): "60 Assets/icons/canon_r5_official/spot_af.svg",
    ("drive.mode", "High Speed Continuous"): "60 Assets/icons/canon_r5_official/high_speed_continuous_shooting.svg",
    ("drive.mode", "High Speed Continuous+"): "60 Assets/icons/canon_r5_official/high_speed_continuous_shooting_plus.svg",
    ("drive.mode", "Low Speed Continuous"): "60 Assets/icons/canon_r5_official/low_speed_continuous_shooting.svg",
    ("drive.mode", "Single Shooting"): "60 Assets/icons/canon_r5_official/single_shooting.svg",
    ("drive.mode", "Single Shot"): "60 Assets/icons/canon_r5_official/single_shooting.svg",
    ("drive.mode", "Self-timer: 10 sec."): "60 Assets/icons/canon_r5_official/self_timer_10_sec_remote_control.svg",
    ("drive.mode", "Self-timer: 2 sec."): "60 Assets/icons/canon_r5_official/self_timer_2_sec_remote_control.svg",
    ("exposure.metering", "Center-weighted"): "60 Assets/icons/canon_r5_official/center_weighted_average_metering.svg",
    ("exposure.metering", "Center-weighted average"): "60 Assets/icons/canon_r5_official/center_weighted_average_metering.svg",
    ("exposure.metering", "Evaluative"): "60 Assets/icons/canon_r5_official/evaluative_metering.svg",
    ("exposure.metering", "Partial"): "60 Assets/icons/canon_r5_official/partial_metering.svg",
    ("exposure.metering", "Spot"): "60 Assets/icons/canon_r5_official/spot_metering.svg",
}


class IconManager:
    """Load icon mappings and return HTML image tags for setting fields."""

    def __init__(self, paths):
        self.paths = paths
        self.fields = self._load_fields()
        self.official_modes = self._load_official_modes()

    def icon_html(self, field_key, label, value=None):
        icon_path = self._icon_path(field_key, value)
        if icon_path is None:
            return label
        src = self._relative_url(icon_path)
        return (
            '<span class="setting-label">'
            f'<img src="{src}" alt="" aria-hidden="true" '
            'class="setting-icon" onerror="this.hidden=true">'
            f"<span>{label}</span>"
            "</span>"
        )

    def icon_path(self, field_key, value=None):
        return self._icon_path(field_key, value)

    def _load_fields(self):
        if not self.paths.icon_map_file.exists():
            return {}
        with open(self.paths.icon_map_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        return data.get("fields", {}) or {}

    def _load_official_modes(self):
        metadata_path = self.paths.root / OFFICIAL_MODE_METADATA
        if not metadata_path.exists():
            return {}
        with open(metadata_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or []
        if not isinstance(data, list):
            return {}
        return {
            str(entry.get("id")): entry
            for entry in data
            if isinstance(entry, dict) and entry.get("id") and entry.get("icon")
        }

    def _icon_path(self, field_key, value=None):
        if field_key == "exposure.mode":
            mode_select_path = self.paths.root / MODE_SELECT_ICON
            if mode_select_path.exists():
                return mode_select_path
        official_id = self._official_metadata_id(field_key, value)
        if official_id:
            entry = self.official_modes.get(official_id)
            if entry:
                icon_path = self.paths.root / "60 Assets/icons/canon_r5_official" / entry["icon"]
                if icon_path.exists():
                    return icon_path
        official_icon = OFFICIAL_VALUE_ICONS.get((field_key, str(value).strip())) if value is not None else None
        if official_icon:
            official_path = self.paths.root / official_icon
            if official_path.exists():
                return official_path
        field_id = FIELD_ALIASES.get(field_key, field_key)
        icon = self.fields.get(field_id)
        if not icon:
            return None
        svg_path = self.paths.icon_asset_dir / icon.get("svg", "")
        if svg_path.exists():
            return svg_path
        png_path = self.paths.icon_asset_dir / icon.get("png", "")
        if png_path.exists():
            return png_path
        return None

    def _official_metadata_id(self, field_key, value=None):
        value_text = str(value).strip() if value is not None else ""
        if field_key == "exposure.mode":
            return SHOOTING_MODE_VALUE_IDS.get(value_text)
        if value_text in FOCUS_FEATURE_IDS:
            return FOCUS_FEATURE_IDS[value_text]
        label_text = str(field_key).replace("_", " ").replace(".", " ").strip().lower()
        for label, metadata_id in FOCUS_FEATURE_IDS.items():
            if label.lower() in label_text:
                return metadata_id
        return None

    def _relative_url(self, icon_path):
        relative = os.path.relpath(icon_path, self.paths.html_output_dir)
        return quote(relative.replace(os.sep, "/"), safe="/")
