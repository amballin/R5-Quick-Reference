#!/usr/bin/env python3
"""Read-only local profile editor prototype with isolated HTML previews."""

from __future__ import annotations

import argparse
import copy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import sys
from urllib.parse import quote, unquote, urlparse


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
STATIC_DIR = BUILD_DIR / "profile_editor"
CATALOG_FILE = STATIC_DIR / "canon_options.yaml"
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from asset_manager import ProjectPaths
from baseline import merge
from build_validator import discover_profiles, is_reference_card
from html_renderer import LABEL, render_card
from icon_manager import IconManager
from profile_loader import load_baseline, load_yaml
from utilities import flatten


HOST = "127.0.0.1"
DEFAULT_PORT = 8765
PREVIEW_NAME = "_Profile Editor Preview.html"
MAX_REQUEST_BYTES = 1_000_000
SECTION_LABELS = {
    "exposure": "Exposure",
    "autofocus": "Autofocus",
    "drive": "Drive",
    "shutter": "Shutter",
    "lens": "Lens",
    "stabilization": "Stabilization",
    "display": "Display",
    "image": "Image",
    "camera_setup": "Camera Setup",
}
TEXT_PATHS = {
    "shutter.target",
    "lens.aperture.target",
    "lens.aperture.strategy",
    "lens.aperture.note",
    "display.screen_info_settings",
    "image.long_exposure_noise_reduction.note",
}
TOGGLE_SETS = (
    {"enable", "disable"},
    {"enabled", "disabled"},
    {"on", "off"},
    {"true", "false"},
)
REFERENCE_CLASSIFICATIONS = {"Set Once", "Situational", "Ignore", "Avoid", "Unresolved"}


class PrototypeError(ValueError):
    pass


def nested_from_flat(values):
    """Convert dot-separated setting paths into a nested mapping."""
    nested = {}
    for path, value in values.items():
        cursor = nested
        parts = path.split(".")
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = value
    return nested


def friendly_label(path):
    if path in LABEL:
        return LABEL[path]
    return path.split(".")[-1].replace("_", " ").title()


def json_value(value):
    return value


def same_value(left, right):
    return left == right and type(left) is type(right)


class ProfileEditorModel:
    def __init__(self, root=PROJECT_ROOT):
        self.paths = ProjectPaths(root)
        self.baseline = load_baseline(self.paths)
        self.defaults = self.baseline.get("defaults") or {}
        self.default_fields = flatten(self.defaults)
        self.icon_manager = IconManager(self.paths)
        self.profiles = self._load_profiles()
        self.option_catalog = self._load_option_catalog()
        self.catalog_settings = self.option_catalog.get("settings") or {}
        self._validate_option_catalog()
        self.reference_sections = self.option_catalog.get("reference_sections") or []
        self.my_menu_catalog = self.option_catalog.get("my_menu") or {}
        self._validate_reference_catalog()
        self.setting_order = self._setting_order()
        self.choices = self._choice_catalog()

    def _load_profiles(self):
        profiles = {}
        for path in discover_profiles(self.paths):
            data = load_yaml(path) or {}
            profiles[path.stem] = data
        return profiles

    def _load_option_catalog(self):
        data = load_yaml(CATALOG_FILE) or {}
        if not isinstance(data, dict):
            raise PrototypeError(f"Canon option catalog must be a mapping: {CATALOG_FILE}")
        return data

    def _validate_option_catalog(self):
        metadata = self.option_catalog.get("metadata")
        if not isinstance(metadata, dict):
            raise PrototypeError("Canon option catalog metadata is missing.")
        if not isinstance(self.catalog_settings, dict) or not self.catalog_settings:
            raise PrototypeError("Canon option catalog settings are missing.")
        expected = {
            path
            for path in self.default_fields
            if path.split(".", 1)[0] in {"exposure", "autofocus", "drive"}
        }
        missing = sorted(expected - set(self.catalog_settings))
        unknown = sorted(set(self.catalog_settings) - set(self.default_fields))
        if missing:
            raise PrototypeError(f"Canon option catalog is missing: {', '.join(missing)}")
        if unknown:
            raise PrototypeError(f"Canon option catalog has unknown settings: {', '.join(unknown)}")
        for path, entry in self.catalog_settings.items():
            if not isinstance(entry, dict):
                raise PrototypeError(f"Canon option entry must be a mapping: {path}")
            if entry.get("section") != path.split(".", 1)[0]:
                raise PrototypeError(f"Canon option section does not match its path: {path}")
            if entry.get("control") not in {"select", "combo", "text", "number"}:
                raise PrototypeError(f"Canon option control is invalid: {path}")
            source = str(entry.get("source") or "")
            if not source.startswith("https://cam.start.canon/"):
                raise PrototypeError(f"Canon option source is not an official Canon manual URL: {path}")
            choices = entry.get("choices")
            if not isinstance(choices, list) or not choices:
                raise PrototypeError(f"Canon option choices are missing: {path}")
            values = []
            for choice in choices:
                if not isinstance(choice, dict) or "value" not in choice or not choice.get("label"):
                    raise PrototypeError(f"Canon option choice is incomplete: {path}")
                value = choice["value"]
                if any(same_value(value, existing) for existing in values):
                    raise PrototypeError(f"Canon option choice is duplicated: {path}={value}")
                values.append(value)
            if self.icon_manager.icon_path(path, self.default_fields[path]) is None:
                raise PrototypeError(f"Approved setting icon is missing: {path}")

    def _validate_reference_catalog(self):
        if not isinstance(self.reference_sections, list) or not self.reference_sections:
            raise PrototypeError("Camera reference sections are missing.")
        section_keys = set()
        item_ids = set()
        for section in self.reference_sections:
            if not isinstance(section, dict) or not section.get("key") or not section.get("label"):
                raise PrototypeError("Camera reference section is incomplete.")
            if section["key"] in section_keys:
                raise PrototypeError(f"Duplicate camera reference section: {section['key']}")
            section_keys.add(section["key"])
            source = str(section.get("source") or "")
            if not source.startswith("https://cam.start.canon/"):
                raise PrototypeError(f"Camera reference section source is not an official Canon URL: {section['key']}")
            items = section.get("items")
            if not isinstance(items, list) or not items:
                raise PrototypeError(f"Camera reference section has no items: {section['key']}")
            for item in items:
                if not isinstance(item, dict):
                    raise PrototypeError(f"Camera reference item must be a mapping: {section['key']}")
                required = {"id", "label", "menu_location", "canon_default", "recommended", "classification", "visit_again"}
                allowed = required | {"note", "my_menu_eligible", "source"}
                unknown = sorted(set(item) - allowed)
                if unknown:
                    raise PrototypeError(f"Camera reference item {item.get('id', '?')} has unknown fields: {', '.join(unknown)}")
                missing = sorted(key for key in required if key not in item or item[key] in {None, ""})
                if missing:
                    raise PrototypeError(f"Camera reference item {item.get('id', '?')} is missing: {', '.join(missing)}")
                non_text = sorted(key for key in required if not isinstance(item.get(key), str))
                if non_text:
                    raise PrototypeError(f"Camera reference item {item.get('id', '?')} requires text fields: {', '.join(non_text)}")
                if item["id"] in item_ids:
                    raise PrototypeError(f"Duplicate camera reference item: {item['id']}")
                item_ids.add(item["id"])
                if item["classification"] not in REFERENCE_CLASSIFICATIONS:
                    raise PrototypeError(f"Invalid classification for {item['id']}: {item['classification']}")
        if not isinstance(self.my_menu_catalog, dict):
            raise PrototypeError("My Menu catalog must be a mapping.")
        tabs = self.my_menu_catalog.get("recommended_tabs") or []
        if not isinstance(tabs, list) or not tabs:
            raise PrototypeError("Recommended My Menu tabs are missing.")
        for tab in tabs:
            if not isinstance(tab, dict) or not tab.get("name") or not isinstance(tab.get("items"), list):
                raise PrototypeError("Recommended My Menu tab is incomplete.")
            if len(tab["items"]) > 6:
                raise PrototypeError(f"Recommended My Menu tab exceeds six items: {tab['name']}")

    def _setting_order(self):
        layout = load_yaml(self.paths.card_layout_file) or {}
        configured = (layout.get("card_layout") or {}).get("display_order") or []
        return configured + sorted(set(self.default_fields) - set(configured))

    def _choice_catalog(self):
        catalog = {path: [] for path in self.default_fields}
        for path, value in self.default_fields.items():
            entry = self.catalog_settings.get(path)
            if entry:
                for choice in entry.get("choices") or []:
                    self._append_choice(catalog[path], choice["value"])
            self._append_choice(catalog[path], value)
        for profile in self.profiles.values():
            for path, value in flatten(profile.get("overrides") or {}).items():
                if path in catalog:
                    self._append_choice(catalog[path], value)
        for path, values in catalog.items():
            if path in self.catalog_settings:
                continue
            lowered = {str(value).casefold() for value in values if value is not None}
            for toggle_set in TOGGLE_SETS:
                if lowered & toggle_set:
                    for option in sorted(toggle_set):
                        self._append_choice(values, self._toggle_spelling(option, values))
                    break
        return catalog

    @staticmethod
    def _append_choice(values, value):
        if not any(same_value(value, existing) for existing in values):
            values.append(value)

    @staticmethod
    def _toggle_spelling(option, existing):
        for value in existing:
            if str(value).casefold() == option:
                return value
        return option.title()

    def profile_list(self):
        items = []
        for name, profile in self.profiles.items():
            reference = is_reference_card(profile)
            items.append(
                {
                    "name": name,
                    "title": profile.get("title", name),
                    "cardType": "reference" if reference else "profile",
                    "editableDraft": not reference,
                }
            )
        return sorted(items, key=lambda item: (item["cardType"] == "reference", item["title"].casefold()))

    def dictionary_detail(self):
        sections = copy.deepcopy(self.reference_sections)
        eligible = []
        for section in sections:
            for item in section["items"]:
                item["source"] = item.get("source") or section["source"]
                if item.get("my_menu_eligible"):
                    eligible.append({
                        "id": item["id"],
                        "label": item["label"],
                        "menuLocation": item["menu_location"],
                    })
        return {
            "metadata": copy.deepcopy(self.option_catalog.get("metadata") or {}),
            "sections": sections,
            "myMenu": copy.deepcopy(self.my_menu_catalog),
            "myMenuEligible": sorted(eligible, key=lambda item: item["label"].casefold()),
        }

    def profile_detail(self, name):
        profile = self._profile(name)
        if is_reference_card(profile):
            return {
                "name": name,
                "title": profile.get("title", name),
                "cardType": "reference",
                "editableDraft": False,
                "sourceFile": f"10 Profiles/{name}.yaml",
                "referenceSettings": profile.get("reference_settings") or [],
                "sections": [],
                "originalOverrides": {},
            }

        original = flatten(profile.get("overrides") or {})
        effective = flatten(merge(self.defaults, profile.get("overrides") or {}))
        sections = []
        section_map = {}
        for path in self.setting_order:
            if path not in self.default_fields:
                continue
            section_key = path.split(".", 1)[0]
            section = section_map.get(section_key)
            if section is None:
                section = {
                    "key": section_key,
                    "label": SECTION_LABELS.get(section_key, friendly_label(section_key)),
                    "settings": [],
                }
                section_map[section_key] = section
                sections.append(section)
            baseline_value = self.default_fields[path]
            choices = self.choices.get(path, [])
            section["settings"].append(
                {
                    "path": path,
                    "label": self._catalog_value(path, "label", friendly_label(path)),
                    "baseline": json_value(baseline_value),
                    "effective": json_value(effective.get(path)),
                    "overridden": path in original,
                    "valueType": self._value_type(baseline_value),
                    "control": self._control(path, choices, baseline_value),
                    "choices": [json_value(value) for value in choices],
                    "choiceDetails": self._choice_details(path, choices),
                    "allowCustom": bool(self._catalog_value(path, "allow_custom", False)),
                    "catalogSource": self._catalog_value(path, "source"),
                    "catalogNote": self._catalog_value(path, "note"),
                    "iconUrl": self._icon_url(path, effective.get(path)),
                }
            )
        return {
            "name": name,
            "title": profile.get("title", name),
            "cardType": "profile",
            "editableDraft": True,
            "sourceFile": f"10 Profiles/{name}.yaml",
            "sections": sections,
            "originalOverrides": original,
        }

    @staticmethod
    def _value_type(value):
        if value is None:
            return "nullable"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        return "string"

    def _control(self, path, choices, baseline_value):
        configured = self._catalog_value(path, "control")
        if configured:
            return configured
        if path in TEXT_PATHS or path.endswith((".target", ".note", ".strategy")):
            return "text"
        if isinstance(baseline_value, (bool, int, float)) and not isinstance(baseline_value, bool):
            return "number" if len(choices) < 2 else "select"
        return "select" if len(choices) >= 2 else "text"

    def _choice_details(self, path, choices):
        details = []
        catalog_choices = self._catalog_value(path, "choices", []) or []
        for value in choices:
            catalog_choice = next(
                (choice for choice in catalog_choices if same_value(choice.get("value"), value)),
                None,
            )
            details.append(
                {
                    "value": json_value(value),
                    "label": str((catalog_choice or {}).get("label") or ("—" if value is None else value)),
                    "origin": (catalog_choice or {}).get("origin", "existing_profile"),
                    "conditional": (catalog_choice or {}).get("conditional"),
                    "iconUrl": self._icon_url(path, value),
                }
            )
        return details

    def _catalog_value(self, path, key, default=None):
        entry = self.catalog_settings.get(path) or {}
        return entry.get(key, default)

    def _icon_url(self, path, value):
        icon_path = self.icon_manager.icon_path(path, value)
        if icon_path is None:
            icon_path = self.icon_manager.icon_path(path)
        if icon_path is None:
            return None
        relative = icon_path.resolve().relative_to(self.paths.root)
        return "/source/" + quote(relative.as_posix(), safe="/")

    def preview(self, name, flat_overrides):
        profile = copy.deepcopy(self._profile(name))
        if is_reference_card(profile):
            raise PrototypeError("Reference cards do not use profile overrides.")
        clean = self._validate_overrides(flat_overrides)
        nested = nested_from_flat(clean)
        profile["overrides"] = nested
        merged = merge(self.defaults, nested)
        template = self.paths.card_template.read_text(encoding="utf-8")
        html = render_card(
            template,
            name,
            profile,
            merged,
            IconManager(self.paths),
            self.baseline,
            self.paths,
        )
        html = self._rewrite_preview_links(html)
        output = self.paths.html_output_dir / PREVIEW_NAME
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html, encoding="utf-8")
        return output

    def _validate_overrides(self, values):
        if not isinstance(values, dict):
            raise PrototypeError("Draft overrides must be an object.")
        clean = {}
        for path, value in values.items():
            if path not in self.default_fields:
                raise PrototypeError(f"Unknown baseline setting: {path}")
            value = self._coerce_value(path, value)
            if not same_value(value, self.default_fields[path]):
                clean[path] = value
        return clean

    def _coerce_value(self, path, value):
        baseline = self.default_fields[path]
        if baseline is None:
            if value is None or isinstance(value, (str, int, float, bool)):
                return value
            raise PrototypeError(f"Unsupported value for {path}.")
        if isinstance(baseline, bool):
            if isinstance(value, bool):
                return value
            if isinstance(value, str) and value.casefold() in {"true", "false"}:
                return value.casefold() == "true"
            raise PrototypeError(f"{path} must be true or false.")
        if isinstance(baseline, int):
            if isinstance(value, bool):
                raise PrototypeError(f"{path} must be an integer.")
            try:
                return int(value)
            except (TypeError, ValueError) as exc:
                raise PrototypeError(f"{path} must be an integer.") from exc
        if isinstance(baseline, float):
            try:
                return float(value)
            except (TypeError, ValueError) as exc:
                raise PrototypeError(f"{path} must be a number.") from exc
        if not isinstance(value, str):
            raise PrototypeError(f"{path} must be text.")
        if "<" in value or ">" in value:
            raise PrototypeError(f"{path} cannot contain HTML angle brackets in this prototype.")
        return value

    def _rewrite_preview_links(self, html):
        encoded_root = quote(self.paths.root.name)
        html = re.sub(rf'(?:\.\./)+{re.escape(encoded_root)}/', "/source/", html)
        html = html.replace('href="../../merged-build/index.html"', 'href="#"')
        return html

    def _profile(self, name):
        if name not in self.profiles:
            raise PrototypeError(f"Unknown profile: {name}")
        return self.profiles[name]


class EditorHandler(BaseHTTPRequestHandler):
    model = None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/profiles":
                return self._json({"profiles": self.model.profile_list()})
            if path == "/api/dictionary":
                return self._json(self.model.dictionary_detail())
            if path.startswith("/api/profiles/"):
                name = unquote(path.removeprefix("/api/profiles/"))
                return self._json(self.model.profile_detail(name))
            if path == "/preview/card.html":
                preview = self.model.paths.html_output_dir / PREVIEW_NAME
                return self._file(preview, "text/html; charset=utf-8")
            if path.startswith("/source/"):
                return self._source_file(unquote(path.removeprefix("/source/")))
            return self._static_file(path)
        except PrototypeError as exc:
            return self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except FileNotFoundError:
            return self._json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            return self._json({"error": f"Prototype error: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/preview":
            return self._json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
        try:
            payload = self._request_json()
            output = self.model.preview(payload.get("profile"), payload.get("overrides", {}))
            return self._json(
                {
                    "previewUrl": "/preview/card.html",
                    "outputFile": str(output),
                    "readOnly": True,
                }
            )
        except PrototypeError as exc:
            return self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            return self._json({"error": f"Could not render preview: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _request_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise PrototypeError("Invalid request length.") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise PrototypeError("Invalid or oversized request.")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PrototypeError("Request body must be valid JSON.") from exc

    def _static_file(self, request_path):
        relative = "index.html" if request_path in {"", "/"} else unquote(request_path.lstrip("/"))
        return self._safe_file(STATIC_DIR, relative)

    def _source_file(self, relative):
        return self._safe_file(self.model.paths.root, relative)

    def _safe_file(self, root, relative):
        root = root.resolve()
        candidate = (root / relative).resolve()
        if candidate != root and root not in candidate.parents:
            raise FileNotFoundError(relative)
        return self._file(candidate)

    def _file(self, path, content_type=None):
        if not path.is_file():
            raise FileNotFoundError(path)
        data = path.read_bytes()
        mime = content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string()}] {format_string % args}")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Load all prototype data and report readiness without starting the server.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    model = ProfileEditorModel()
    if args.check:
        for profile in model.profile_list():
            model.profile_detail(profile["name"])
        print(f"Profile editor check passed: {len(model.profiles)} profiles loaded.")
        print(f"Preview output: {model.paths.html_output_dir / PREVIEW_NAME}")
        return 0
    if not 1 <= args.port <= 65535:
        print("Port must be between 1 and 65535.", file=sys.stderr)
        return 2
    EditorHandler.model = model
    server = ThreadingHTTPServer((HOST, args.port), EditorHandler)
    print("Canon Camera Reference — read-only profile editor prototype")
    print(f"Open http://{HOST}:{args.port}")
    print("Press Control-C to stop. Draft changes are never written to profile YAML.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProfile editor stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
