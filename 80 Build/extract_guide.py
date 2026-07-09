#!/usr/bin/env python3
import argparse
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.parts.append(text)


def parse_args():
    parser = argparse.ArgumentParser(description="Extract a Canon guide into a profile candidate.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source", help="Local Canon guide file, such as YAML, HTML, or text.")
    source.add_argument("--url", help="Canon guide URL to download and extract.")
    parser.add_argument("--name", required=True, help="Guide/profile name for the extraction folder.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing extraction folder.")
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = root / "70 Canon Guides" / "Extracted" / safe_name(args.name)
    if output_dir.exists():
        if not args.force:
            raise SystemExit(f"Extraction folder already exists: {output_dir}. Use --force to refresh it.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    source_text, source_label, source_url = read_input(args)
    source_data = parse_possible_yaml(source_text)
    plain_text = document_text(source_text, source_data)
    baseline = load_yaml(root / "00 Master" / "baseline.yaml")
    baseline_defaults = baseline.get("defaults", {})
    baseline_flat = flatten(baseline_defaults)

    metadata = build_metadata(args.name, source_data, source_label, source_url)
    extracted = extract_settings(source_data, plain_text)
    compared = compare_to_baseline(extracted, baseline_flat)
    profile = build_profile_candidate(args.name, metadata, compared, source_data, plain_text)

    write_metadata(output_dir / "guide_metadata.yaml", metadata)
    write_summary(output_dir / "guide_summary.md", args.name, source_data, plain_text, extracted)
    write_yaml(output_dir / "profile_candidate.yaml", profile)
    write_comparison(output_dir / "comparison_to_baseline.md", compared)
    write_report(output_dir / "extraction_report.md", args.name, source_label, compared, profile)

    validate_outputs(output_dir, profile, baseline_flat)
    print(f"Extraction created: {output_dir}")
    print(f"Settings extracted: {len(extracted)}")
    print(f"Overrides created: {len(flatten(profile.get('overrides', {})))}")


def read_input(args):
    if args.url:
        request = Request(args.url, headers={"User-Agent": "PhotographyReferenceSystem/1.0"})
        with urlopen(request, timeout=30) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="replace"), args.url, args.url

    path = Path(args.source).expanduser()
    text = path.read_text(encoding="utf-8", errors="replace")
    return text, str(path), None


def parse_possible_yaml(text):
    try:
        data = yaml.safe_load(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def document_text(source_text, source_data):
    if source_data:
        return yaml.safe_dump(source_data, sort_keys=False)
    if "<html" in source_text.lower() or "<body" in source_text.lower():
        parser = TextExtractor()
        parser.feed(source_text)
        return "\n".join(parser.parts)
    return source_text


def build_metadata(name, data, source_label, source_url):
    meta = data.get("metadata", {}) if isinstance(data, dict) else {}
    profile = data.get("profile", {}) if isinstance(data, dict) else {}
    url = source_url or (data.get("url") if isinstance(data, dict) else None)
    camera = profile.get("camera") or meta.get("camera_models") or meta.get("camera")
    cameras = camera if isinstance(camera, list) else ([camera] if camera else [])
    return {
        "metadata": {"record_type": "extracted_guide_metadata"},
        "title": meta.get("article") or profile.get("name") or name,
        "source": meta.get("source") or source_from_label(source_label),
        "author": meta.get("author") or "Not specified",
        "publication_date": meta.get("publication_date") or meta.get("date") or "Not specified",
        "camera_models": cameras,
        "photography_category": profile.get("category") or meta.get("category") or "Not specified",
        "url": url or "Not specified",
        "date_processed": date.today().isoformat(),
    }


def source_from_label(label):
    parsed = urlparse(label)
    return parsed.netloc if parsed.scheme else "Local file"


def extract_settings(data, text):
    settings = []
    if isinstance(data, dict):
        settings.extend(extract_from_yaml(data))
    settings.extend(extract_from_text(text))
    return dedupe_settings(settings)


def extract_from_yaml(data):
    settings = []
    add = settings.append
    starting = data.get("starting_point", {})
    exposure = data.get("exposure", {})
    focus = data.get("focus", {})
    drive = data.get("drive_and_release", {})
    stabilization = data.get("stabilization", {})
    r5 = data.get("canon_r5_settings", {})
    wb = data.get("white_balance_and_color", {})

    value = first(starting.get("exposure_mode"), exposure.get("mode"))
    if value:
        add(setting("Exposure Mode", "exposure.mode", value))
    value = first(starting.get("shutter_speed"), nested(exposure, "shutter", "default"))
    if value:
        add(setting("Shutter Target", "shutter.target", normalize_shutter(value)))
    settings.extend(aperture_settings(starting, exposure))
    value = first(starting.get("iso"), nested(exposure, "iso", "default"))
    if value:
        add(setting("ISO Mode", "exposure.iso.mode", "Fixed"))
        add(setting("ISO Value", "exposure.iso.value", normalize_iso_value(value)))
    if str(nested(exposure, "iso", "auto_iso")).lower() == "off":
        add(setting("ISO Mode", "exposure.iso.mode", "Fixed"))
    value = first(focus.get("af_operation"))
    if value:
        add(setting("AF Operation", "autofocus.operation", value))
    value = first(drive.get("drive_mode"))
    if value:
        add(setting("Drive Mode", "drive.mode", value))
    value = first(stabilization.get("ibis"))
    if value:
        add(setting("IBIS", "stabilization.ibis", normalize_on_off(value)))
    value = first(stabilization.get("lens_is"))
    if value:
        add(setting("Lens IS", "stabilization.lens_is", normalize_on_off(value)))
    value = first(starting.get("white_balance"), wb.get("white_balance"))
    if value:
        add(setting("White Balance", "image.white_balance", value))
    value = first(starting.get("file_format"))
    if value:
        add(setting("Image Quality", "image.quality", value))
    if r5:
        mapped = [
            ("Histogram", "display.histogram", r5.get("histogram")),
            ("Highlight Alert", "display.highlight_alert", r5.get("highlight_alert")),
            ("Long Exposure NR", "image.long_exposure_noise_reduction.value", r5.get("long_exposure_noise_reduction")),
            ("High ISO NR", "image.high_iso_noise_reduction", r5.get("high_iso_noise_reduction")),
            ("Highlight Tone Priority", "image.highlight_tone_priority", r5.get("highlight_tone_priority")),
            ("Picture Style", "image.picture_style", r5.get("picture_style")),
        ]
        for label, path, value in mapped:
            if value:
                add(setting(label, path, simplify_value(value, path)))
    return settings


def extract_from_text(text):
    settings = []
    lowered = text.lower()
    if "manual exposure" in lowered:
        settings.append(setting("Exposure Mode", "exposure.mode", "Manual"))
    if "manual focus" in lowered:
        settings.append(setting("AF Operation", "autofocus.operation", "Manual Focus"))
    if "single shot" in lowered:
        settings.append(setting("Drive Mode", "drive.mode", "Single Shot"))
    if "daylight" in lowered and "white balance" in lowered:
        settings.append(setting("White Balance", "image.white_balance", "Daylight"))
    if "raw" in lowered:
        settings.append(setting("Image Quality", "image.quality", "RAW"))
    if "highlight alert" in lowered:
        settings.append(setting("Highlight Alert", "display.highlight_alert", "Enabled"))
    if "rgb histogram" in lowered:
        settings.append(setting("Histogram", "display.histogram", "RGB"))

    aperture = re.search(r"f/\d+(?:\.\d+)?", text, re.IGNORECASE)
    if aperture:
        settings.append(setting("Aperture Target", "lens.aperture.target", aperture.group(0)))
        settings.append(setting("Aperture Strategy", "lens.aperture.strategy", "Guide Selected"))
        settings.append(setting("Aperture Note", "lens.aperture.note", "Specific aperture recommendation extracted from the guide."))
    iso = re.search(r"ISO\s*(\d+)", text, re.IGNORECASE)
    if iso:
        settings.append(setting("ISO Mode", "exposure.iso.mode", "Fixed"))
        settings.append(setting("ISO Value", "exposure.iso.value", int(iso.group(1))))
    shutter = re.search(r"(\d+(?:\.\d+)?)\s*(?:sec|second|seconds|s)\b", text, re.IGNORECASE)
    if shutter:
        settings.append(setting("Shutter", "shutter.target", f"{shutter.group(1)} s"))
    if "ibis off" in lowered or "image stabilizer off" in lowered:
        settings.append(setting("IBIS", "stabilization.ibis", "Off"))
    if "lens is off" in lowered or "stabilization off" in lowered:
        settings.append(setting("Lens IS", "stabilization.lens_is", "Off"))
    return settings


def aperture_settings(starting, exposure):
    aperture = nested(exposure, "aperture")
    target = first(starting.get("aperture"), nested(exposure, "aperture", "default"))
    settings = []
    if not target:
        return settings

    settings.append(setting("Aperture Target", "lens.aperture.target", target))

    if isinstance(aperture, dict):
        strategy = aperture.get("strategy") or aperture.get("approach")
        note = aperture.get("note")
        detail_note = aperture_note(aperture)
    else:
        strategy = None
        note = None
        detail_note = None

    if not strategy:
        strategy = "Guide Selected"
    settings.append(setting("Aperture Strategy", "lens.aperture.strategy", strategy))

    note = first(note, detail_note)
    if note:
        settings.append(setting("Aperture Note", "lens.aperture.note", note))

    return settings


def aperture_note(aperture):
    details = []
    for key, value in aperture.items():
        if key in {"default", "strategy", "approach", "note"}:
            continue
        label = key.replace("_", " ")
        details.append(f"{label}: {value}")
    return "; ".join(details) if details else None


def compare_to_baseline(settings, baseline_flat):
    compared = []
    for item in settings:
        path = item["path"]
        value = item["value"]
        if path not in baseline_flat:
            status = "NEW"
            baseline_value = None
        else:
            baseline_value = baseline_flat[path]
            status = "UNCHANGED" if normalize_compare(value) == normalize_compare(baseline_value) else "OVERRIDE"
        compared.append({**item, "status": status, "baseline": baseline_value})
    return compared


def build_profile_candidate(name, metadata, compared, data, text):
    overrides = {}
    for item in compared:
        if item["status"] == "OVERRIDE":
            set_nested(overrides, item["path"].split("."), item["value"])
    return {
        "metadata": {
            "version": 1.0,
            "status": "Draft",
            "last_updated": date.today().isoformat(),
            "source": metadata["title"],
        },
        "title": name,
        "inherits": "baseline",
        "overrides": overrides,
        "checklist": checklist_items(data, text),
        "watch_for": watch_items(data, text),
        "common_mistakes": mistake_items(data, text),
        "notes": note_items(data, text),
    }


def checklist_items(data, text):
    if isinstance(data, dict) and "field_checklist" in data:
        items = []
        for values in data["field_checklist"].values():
            if isinstance(values, list):
                items.extend(values)
        return concise(items, 10)
    return concise(lines_with_keywords(text, ["check", "set", "confirm", "enable", "focus"]), 10)


def watch_items(data, text):
    if isinstance(data, dict) and "adjustments" in data:
        return [key.replace("_", " ").title() for key in data["adjustments"].keys()]
    return concise(lines_with_keywords(text, ["watch", "avoid", "smoke", "blur", "highlight"]), 8)


def mistake_items(data, text):
    if isinstance(data, dict) and "avoid" in data:
        return concise(data["avoid"], 8)
    return concise(lines_with_keywords(text, ["mistake", "avoid", "do not", "don't"]), 8)


def note_items(data, text):
    notes = []
    if isinstance(data, dict):
        for section in ("focus", "stabilization", "technique", "drive_and_release", "composition"):
            value = data.get(section)
            if isinstance(value, dict):
                notes.extend(flatten_text_values(value))
    return concise(notes or lines_with_keywords(text, ["use", "start", "review", "compose"]), 10)


def write_metadata(path, metadata):
    write_yaml(path, metadata)


def write_summary(path, name, data, text, settings):
    lines = [
        f"# Guide Summary: {name}",
        "",
        "## Purpose",
        "",
        purpose_text(data, text),
        "",
        "## Recommended Settings",
        "",
    ]
    lines.extend(f"- {item['label']}: {item['value']}" for item in settings)
    lines.extend(["", "## Recommended Techniques", ""])
    lines.extend(f"- {item}" for item in note_items(data, text)[:8])
    lines.extend(["", "## Important Cautions", ""])
    lines.extend(f"- {item}" for item in mistake_items(data, text)[:8])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_comparison(path, compared):
    groups = {"UNCHANGED": [], "OVERRIDE": [], "NEW": []}
    for item in compared:
        groups[item["status"]].append(item)
    lines = ["# Comparison To Baseline", ""]
    headings = {
        "UNCHANGED": "Already In Baseline",
        "OVERRIDE": "Added As Overrides",
        "NEW": "Information Requiring Manual Review",
    }
    for status, heading in headings.items():
        lines.extend([f"## {heading}", ""])
        if groups[status]:
            for item in groups[status]:
                if status == "OVERRIDE":
                    lines.append(f"- `{item['path']}`: `{item['baseline']}` -> `{item['value']}`")
                else:
                    lines.append(f"- `{item['path']}`: `{item['value']}`")
        else:
            lines.append("- None")
        lines.append("")
    lines.extend(["## Ignored Because Duplicated", ""])
    unchanged = groups["UNCHANGED"]
    lines.extend(f"- `{item['path']}`" for item in unchanged)
    if not unchanged:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(path, name, source_label, compared, profile):
    overrides = flatten(profile.get("overrides", {}))
    manual = [item for item in compared if item["status"] == "NEW"]
    lines = [
        "# Extraction Report",
        "",
        f"- Guide processed: {name}",
        f"- Source: `{source_label}`",
        f"- Profiles affected: {name}",
        f"- Settings extracted: {len(compared)}",
        f"- Overrides created: {len(overrides)}",
        f"- Checklist items: {len(profile.get('checklist', []))}",
        f"- Watch-for items: {len(profile.get('watch_for', []))}",
        f"- Common mistakes: {len(profile.get('common_mistakes', []))}",
        f"- Items requiring manual review: {len(manual)}",
        f"- Confidence score: {'medium-high' if len(overrides) else 'medium'}",
        "",
        "## Overrides",
        "",
    ]
    lines.extend(f"- `{path}`: `{value}`" for path, value in sorted(overrides.items()))
    if not overrides:
        lines.append("- None")
    lines.extend(["", "## Manual Review", ""])
    lines.extend(f"- `{item['path']}`: `{item['value']}`" for item in manual)
    if not manual:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_outputs(output_dir, profile, baseline_flat):
    yaml.safe_load((output_dir / "profile_candidate.yaml").read_text())
    overrides = flatten(profile.get("overrides", {}))
    unknown = sorted(set(overrides) - set(baseline_flat))
    if unknown:
        raise SystemExit(f"profile_candidate.yaml contains unknown override paths: {unknown}")
    duplicates = [path for path, value in overrides.items() if normalize_compare(value) == normalize_compare(baseline_flat.get(path))]
    if duplicates:
        raise SystemExit(f"profile_candidate.yaml duplicates baseline settings: {duplicates}")


def safe_name(value):
    return re.sub(r"[^A-Za-z0-9._ -]+", "", value).strip().replace("/", "-")


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def write_yaml(path, data):
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def flatten(data, prefix=""):
    output = {}
    if not isinstance(data, dict):
        return output
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            output.update(flatten(value, name))
        else:
            output[name] = value
    return output


def set_nested(target, keys, value):
    current = target
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = value


def nested(data, *keys):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def first(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return None


def setting(label, path, value):
    return {"label": label, "path": path, "value": value}


def dedupe_settings(settings):
    deduped = {}
    for item in settings:
        deduped.setdefault(item["path"], item)
    return list(deduped.values())


def normalize_on_off(value):
    text = str(value)
    if "off" in text.lower():
        return "Off"
    if "on" in text.lower() or "enabled" in text.lower():
        return "On"
    return value


def simplify_value(value, path=None):
    text = str(value)
    if path == "display.histogram" and "rgb" in text.lower():
        return "RGB"
    if "enabled" in text.lower():
        return "Enabled"
    if "off" == text.lower():
        return "Off"
    if "standard or neutral" in text.lower():
        return "Neutral"
    return value


def normalize_iso_value(value):
    text = str(value).strip()
    if text.isdigit():
        return int(text)
    return value


def normalize_shutter(value):
    text = str(value).strip()
    return re.sub(r"\bsec(?:ond|onds)?\b", "s", text, flags=re.IGNORECASE)


def normalize_compare(value):
    return str(value).strip().lower()


def flatten_text_values(value):
    items = []
    if isinstance(value, dict):
        for nested_value in value.values():
            items.extend(flatten_text_values(nested_value))
    elif isinstance(value, list):
        for item in value:
            items.extend(flatten_text_values(item))
    elif isinstance(value, str):
        items.append(value)
    return items


def lines_with_keywords(text, keywords):
    lines = []
    for line in text.splitlines():
        clean = line.strip(" -\t")
        if clean and any(keyword in clean.lower() for keyword in keywords):
            lines.append(clean)
    return concise(lines, 10)


def concise(items, limit):
    seen = []
    for item in items:
        text = str(item).strip()
        if text and text not in seen:
            seen.append(text)
    return seen[:limit]


def purpose_text(data, text):
    if isinstance(data, dict):
        purpose = nested(data, "summary", "purpose")
        if purpose:
            return str(purpose).strip()
    for line in text.splitlines():
        if len(line.strip()) > 50:
            return line.strip()
    return "Extract useful shooting guidance and camera-setting recommendations from the guide."


if __name__ == "__main__":
    main()
