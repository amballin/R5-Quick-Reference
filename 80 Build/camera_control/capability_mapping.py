"""Human-readable EOS R5 capability decoding and profile-path coverage."""

from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "00 Master" / "camera_capabilities.yaml"
BASELINE_PATH = PROJECT_ROOT / "00 Master" / "baseline.yaml"


VALUE_MAPS = {
    "battery_level": {-1: "External power", 0xFFFFFFFF: "External power", 0xFFFFFFFE: "Unknown power", 0: "Empty", 9: "Low", 19: "Quarter", 49: "Half", 69: "High", 80: "Normal"},
    "storage_destination": {1: "Camera card", 2: "Computer", 3: "Camera card + computer"},
    "image_quality": {
        0x0063FF0F: "cRAW",
        0x0064FF0F: "RAW",
        0x0010FF0F: "JPEG Large",
        0x0013FF0F: "JPEG Large Fine",
        0x0012FF0F: "JPEG Large Normal",
        0x00630013: "cRAW + JPEG Large Fine",
        0x00630012: "cRAW + JPEG Large Normal",
        0x00640013: "RAW + JPEG Large Fine",
        0x00640012: "RAW + JPEG Large Normal",
    },
    "white_balance": {0: "AWB (ambience priority)", 23: "AWB (white priority)", 1: "Daylight", 2: "Cloudy", 3: "Tungsten", 4: "Fluorescent", 5: "Flash", 6: "Custom 1", 8: "Shade", 9: "Color temperature", 15: "Custom 2", 16: "Custom 3", 18: "Custom 4", 19: "Custom 5"},
    "color_space": {1: "sRGB", 2: "Adobe RGB"},
    "picture_style": {129: "Standard", 130: "Portrait", 131: "Landscape", 132: "Neutral", 133: "Faithful", 134: "Monochrome", 135: "Auto", 136: "Fine Detail", 33: "User Defined 1", 34: "User Defined 2", 35: "User Defined 3"},
    "exposure_mode": {0: "P", 1: "Tv", 2: "Av", 3: "M", 4: "Bulb", 7: "C1", 16: "C2", 17: "C3", 55: "Fv"},
    "drive_mode": {0: "Single Shooting", 1: "Medium Speed Continuous", 4: "High Speed Continuous", 5: "Low Speed Continuous", 16: "Self-timer: 10 sec", 17: "Self-timer: 2 sec", 18: "High Speed Continuous+", 19: "Silent Single Shooting", 20: "Silent Continuous", 21: "Silent High Speed Continuous", 22: "Silent Low Speed Continuous"},
    "iso_speed": {0: "Auto", 0x28: "ISO 6", 0x30: "ISO 12", 0x38: "ISO 25", 0x40: "ISO 50", 0x48: "ISO 100", 0x4B: "ISO 125", 0x4D: "ISO 160", 0x50: "ISO 200", 0x53: "ISO 250", 0x55: "ISO 320", 0x58: "ISO 400", 0x5B: "ISO 500", 0x5D: "ISO 640", 0x60: "ISO 800", 0x63: "ISO 1000", 0x65: "ISO 1250", 0x68: "ISO 1600", 0x6B: "ISO 2000", 0x6D: "ISO 2500", 0x70: "ISO 3200", 0x73: "ISO 4000", 0x75: "ISO 5000", 0x78: "ISO 6400", 0x7B: "ISO 8000", 0x7D: "ISO 10000", 0x80: "ISO 12800", 0x83: "ISO 16000", 0x85: "ISO 20000", 0x88: "ISO 25600", 0x8B: "ISO 32000", 0x8D: "ISO 40000", 0x90: "ISO 51200", 0x93: "ISO 64000", 0x95: "ISO 80000", 0x98: "ISO 102400"},
    "metering_mode": {1: "Spot", 3: "Evaluative", 4: "Partial", 5: "Center-weighted average"},
    "af_mode": {0: "One-Shot AF", 1: "Servo AF", 2: "AI Focus AF", 3: "Manual Focus"},
    "aperture": {0x08: "f/1.0", 0x10: "f/1.4", 0x18: "f/2.0", 0x20: "f/2.8", 0x28: "f/4.0", 0x30: "f/5.6", 0x38: "f/8.0", 0x40: "f/11", 0x48: "f/16", 0x50: "f/22", 0x58: "f/32", 0xFF: "Auto"},
    "shutter_speed": {
        0x04: "Auto", 0x0C: "Bulb", 0x10: "30 sec", 0x13: "25 sec", 0x14: "20 sec", 0x18: "15 sec", 0x1B: "13 sec", 0x1C: "10 sec", 0x20: "8 sec", 0x23: "6 sec", 0x25: "5 sec", 0x28: "4 sec", 0x2B: "3.2 sec", 0x2C: "3 sec", 0x2D: "2.5 sec", 0x30: "2 sec", 0x33: "1.6 sec", 0x34: "1.5 sec", 0x35: "1.3 sec", 0x38: "1 sec", 0x3B: "0.8 sec", 0x3C: "0.7 sec", 0x3D: "0.6 sec", 0x40: "0.5 sec", 0x43: "0.4 sec", 0x45: "0.3 sec", 0x48: "1/4", 0x4B: "1/5", 0x4C: "1/6", 0x50: "1/8", 0x53: "1/10", 0x55: "1/13", 0x58: "1/15", 0x5B: "1/20", 0x5D: "1/25", 0x60: "1/30", 0x63: "1/40", 0x65: "1/50", 0x68: "1/60", 0x6B: "1/80", 0x6D: "1/100", 0x70: "1/125", 0x73: "1/160", 0x75: "1/200", 0x78: "1/250", 0x7B: "1/320", 0x7D: "1/400", 0x80: "1/500", 0x83: "1/640", 0x85: "1/800", 0x88: "1/1000", 0x8B: "1/1250", 0x8D: "1/1600", 0x90: "1/2000", 0x93: "1/2500", 0x95: "1/3200", 0x98: "1/4000", 0x9B: "1/5000", 0x9D: "1/6400", 0xA0: "1/8000"
    },
    "exposure_compensation": {0xE8: "-3", 0xEB: "-2 2/3", 0xED: "-2 1/3", 0xF0: "-2", 0xF3: "-1 2/3", 0xF5: "-1 1/3", 0xF8: "-1", 0xFB: "-2/3", 0xFD: "-1/3", 0: "0", 3: "+1/3", 5: "+2/3", 8: "+1", 11: "+1 1/3", 13: "+1 2/3", 16: "+2", 19: "+2 1/3", 21: "+2 2/3", 24: "+3"},
    "noise_reduction": {0: "Off", 1: "On 1", 2: "On 2", 3: "On", 4: "Auto"},
    "ibis_high_res_shot": {0: "Off", 1: "On"},
    "af_method": {
        0x00: "Quick Mode", 0x01: "1-Point AF", 0x02: "Face + Tracking",
        0x03: "FlexiZone - Multi", 0x04: "Zone AF", 0x05: "Expand AF Area",
        0x06: "Expand AF Area: Around", 0x07: "Large Zone AF: Horizontal",
        0x08: "Large Zone AF: Vertical", 0x09: "Tracking AF", 0x0A: "Spot AF",
        0x0B: "Flexible Zone AF 1", 0x0C: "Flexible Zone AF 2",
        0x0D: "Flexible Zone AF 3", 0x0E: "Whole Area AF",
        0x0F: "No Tracking Spot AF", 0x10: "No Tracking 1-Point AF",
        0x11: "No Tracking Expand AF Area",
        0x12: "No Tracking Expand AF Area: Around",
    },
    "cropping_aspect_ratio": {0: "Full-frame", 1: "1:1", 2: "4:3", 7: "16:9", 13: "1.6x crop"},
    "continuous_af": {0: "Off", 1: "On"},
    "eye_detection": {0: "Disable", 1: "Enable"},
    "subject_detection": {0: "None", 1: "People", 2: "Animals", 3: "Vehicles", 4: "None"},
}


def load_catalog():
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


def decode_value(key, value):
    if value is None:
        return None
    if key == "available_shots":
        return f"{value} shots"
    return VALUE_MAPS.get(key, {}).get(value, f"Raw {value}")


def enrich_properties(properties):
    definitions = {item["key"]: item for item in load_catalog()["properties"]}
    enriched = []
    for observed in properties:
        item = dict(observed)
        definition = definitions.get(item.get("key"), {})
        item["value_display"] = decode_value(item.get("key"), item.get("value_raw"))
        item["allowed_values_display"] = [
            decode_value(item.get("key"), value) for value in item.get("allowed_values_raw") or []
        ]
        item["profile_paths"] = list(definition.get("profile_paths") or [])
        item["capability_classification"] = definition.get("capability_classification", "unmapped")
        item["dependencies"] = list(definition.get("dependencies") or [])
        enriched.append(item)
    return enriched


def capability_coverage():
    catalog = load_catalog()
    mapped = {}
    for item in catalog["properties"]:
        for path in item.get("profile_paths") or []:
            mapped[path] = item["capability_classification"]
    baseline = yaml.safe_load(BASELINE_PATH.read_text(encoding="utf-8"))["defaults"]
    all_paths = sorted(_flatten_paths(baseline))
    exact = sorted(path for path, status in mapped.items() if status == "sdk_readable")
    conditional = sorted(path for path, status in mapped.items() if status == "conditional")
    unmapped = [path for path in all_paths if path not in mapped]
    return {
        "baseline_setting_count": len(all_paths),
        "sdk_readable_paths": exact,
        "conditional_paths": conditional,
        "manual_or_unmapped_paths": unmapped,
        "summary": {
            "sdk_readable": len(exact),
            "conditional": len(conditional),
            "manual_or_unmapped": len(unmapped),
        },
    }


def _flatten_paths(value, prefix=""):
    paths = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(child, dict):
                paths.extend(_flatten_paths(child, path))
            else:
                paths.append(path)
    return paths
