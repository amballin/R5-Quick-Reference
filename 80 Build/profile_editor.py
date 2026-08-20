#!/usr/bin/env python3
"""Guarded local profile editor with isolated previews and reviewed YAML saves."""

from __future__ import annotations

import argparse
import copy
from datetime import date, datetime
import difflib
import hashlib
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import quote, unquote, urlparse

import yaml


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
STATIC_DIR = BUILD_DIR / "profile_editor"
CATALOG_FILE = STATIC_DIR / "canon_options.yaml"
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from asset_manager import ProjectPaths
from baseline import merge
from baseline_impact import (
    BaselineImpactError,
    analyze_baseline_impact,
    analyze_cx_impact,
    analyze_my_menu_routes,
    plan_baseline_migration,
)
from baseline_migration import (
    BaselineMigrationError,
    build_migration_candidates,
    migration_diff,
)
from build_validator import discover_profiles, is_reference_card
from html_renderer import LABEL, displayed_card_setting_paths, render_card
from icon_manager import IconManager
from my_menu import MyMenuError, load_my_menu, validate_my_menu, used_tabs
from my_menu_colors import MyMenuColorError, load_my_menu_colors, validate_my_menu_colors
from my_menu_reference import reference_settings as my_menu_reference_settings
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
PROFILE_STATUSES = {"Draft", "Review", "Final"}
PROFILE_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9 .&+()'_-]{0,79}")
REVIEW_TTL_SECONDS = 30 * 60
MAX_PENDING_REVIEWS = 20
EDITOR_VERSION = "1.0.0"
EDITOR_BUILD_FILES = (
    "00 Master/my_menu.yaml",
    "00 Master/my_menu_colors.yaml",
    "10 Profiles/My Menu.yaml",
    "20 Templates/card.html",
    "80 Build/baseline_impact.py",
    "80 Build/baseline_migration.py",
    "80 Build/cx_route_analysis.py",
    "80 Build/html_renderer.py",
    "80 Build/my_menu_colors.py",
    "80 Build/my_menu.py",
    "80 Build/my_menu_reference.py",
    "80 Build/profile_editor.py",
    "80 Build/profile_editor/app.js",
    "80 Build/profile_editor/index.html",
    "80 Build/profile_editor/styles.css",
)


class PrototypeError(ValueError):
    pass


class ProfileConflictError(PrototypeError):
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
    def __init__(self, root=PROJECT_ROOT, source_validator=None):
        self.paths = ProjectPaths(root)
        self.catalog_file = self.paths.root / "80 Build" / "profile_editor" / "canon_options.yaml"
        self.baseline = load_baseline(self.paths)
        self.defaults = self.baseline.get("defaults") or {}
        self.default_fields = flatten(self.defaults)
        self.verification_tracker = load_yaml(self.paths.verification_tracker_source_file) or {}
        self.registration = self.verification_tracker.get("registration") or {}
        self.icon_manager = IconManager(self.paths)
        self.profiles = self._load_profiles()
        self.option_catalog = self._load_option_catalog()
        self.my_menu_colors = load_my_menu_colors(self.paths)
        self.catalog_settings = self.option_catalog.get("settings") or {}
        self._validate_option_catalog()
        self.reference_sections = self.option_catalog.get("reference_sections") or []
        self.my_menu_catalog = self.option_catalog.get("my_menu") or {}
        self._validate_reference_catalog()
        self.my_menu = load_my_menu(self.paths, self._all_my_menu_item_ids())
        self.setting_order = self._setting_order()
        self.choices = self._choice_catalog()
        self._source_validator = source_validator or self._validate_project_sources
        self._pending_reviews = {}
        self._pending_migration_reviews = {}
        self._pending_color_reviews = {}
        self._write_lock = threading.RLock()
        self._build_lock = threading.Lock()

    def _load_profiles(self):
        profiles = {}
        for path in discover_profiles(self.paths):
            data = load_yaml(path) or {}
            profiles[path.stem] = data
        return profiles

    def _load_option_catalog(self):
        data = load_yaml(self.catalog_file) or {}
        if not isinstance(data, dict):
            raise PrototypeError(f"Canon option catalog must be a mapping: {self.catalog_file}")
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
        setting_paths = set()
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
                allowed = required | {"note", "my_menu_eligible", "setting_path", "source"}
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
                setting_path = item.get("setting_path")
                if setting_path:
                    if setting_path not in self.default_fields:
                        raise PrototypeError(
                            f"Camera reference item has an unknown setting path: {item['id']} / {setting_path}"
                        )
                    if setting_path in setting_paths:
                        raise PrototypeError(f"Duplicate My Menu setting identity: {setting_path}")
                    if not item.get("my_menu_eligible"):
                        raise PrototypeError(
                            f"My Menu setting identity is not menu eligible: {setting_path}"
                        )
                    setting_paths.add(setting_path)
                if item["classification"] not in REFERENCE_CLASSIFICATIONS:
                    raise PrototypeError(f"Invalid classification for {item['id']}: {item['classification']}")
        if not isinstance(self.my_menu_catalog, dict):
            raise PrototypeError("My Menu catalog must be a mapping.")
        tabs = self.my_menu_catalog.get("recommended_tabs") or []
        if not isinstance(tabs, list) or not tabs:
            raise PrototypeError("Recommended My Menu tabs are missing.")
        tab_names = set()
        recommended_item_ids = set()
        for tab in tabs:
            if not isinstance(tab, dict) or not tab.get("name") or not isinstance(tab.get("items"), list):
                raise PrototypeError("Recommended My Menu tab is incomplete.")
            if len(tab["items"]) > 6:
                raise PrototypeError(f"Recommended My Menu tab exceeds six items: {tab['name']}")
            tab_key = tab["name"].casefold()
            if tab_key in tab_names:
                raise PrototypeError(f"Duplicate recommended My Menu tab: {tab['name']}")
            tab_names.add(tab_key)
            for item_id in tab["items"]:
                if item_id not in item_ids:
                    raise PrototypeError(f"Recommended My Menu item is unknown: {item_id}")
                if item_id in recommended_item_ids:
                    raise PrototypeError(f"Recommended My Menu item is duplicated: {item_id}")
                recommended_item_ids.add(item_id)
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
        my_menu = copy.deepcopy(self.my_menu_catalog)
        my_menu["saved_tabs"] = copy.deepcopy(used_tabs(self.my_menu))
        my_menu["sourceFile"] = "00 Master/my_menu.yaml"
        my_menu["colors"] = {
            "sourceFile": "00 Master/my_menu_colors.yaml",
            "palette": copy.deepcopy(self.my_menu_colors["palette"]),
            "assignments": copy.deepcopy(self.my_menu_colors["assignments"]),
        }
        return {
            "metadata": copy.deepcopy(self.option_catalog.get("metadata") or {}),
            "sections": sections,
            "myMenu": my_menu,
            "myMenuEligible": sorted(eligible, key=lambda item: item["label"].casefold()),
        }

    def _all_my_menu_item_ids(self):
        return {
            item["id"]
            for section in self.reference_sections
            for item in section["items"]
            if item.get("my_menu_eligible")
        }

    def review_my_menu_configuration(self, tabs):
        menu_candidate, color_candidate = self._my_menu_configuration_candidates(tabs)
        candidates = {
            "00 Master/my_menu.yaml": self._dump_yaml(menu_candidate),
            "00 Master/my_menu_colors.yaml": self._dump_yaml(color_candidate),
        }
        before = {
            relative: (self.paths.root / relative).read_bytes()
            for relative in candidates
        }
        diff_parts = []
        for relative in candidates:
            if before[relative] == candidates[relative]:
                continue
            diff_parts.append(
                "".join(
                    difflib.unified_diff(
                        before[relative].decode("utf-8").splitlines(keepends=True),
                        candidates[relative].decode("utf-8").splitlines(keepends=True),
                        fromfile=f"a/{relative}",
                        tofile=f"b/{relative}",
                    )
                )
            )
        diff = "".join(diff_parts)
        if not diff:
            raise PrototypeError("The My Menu draft matches the saved configuration.")
        review = {
            "created": time.monotonic(),
            "source_sha256": {relative: self._sha256(data) for relative, data in before.items()},
            "candidate_sha256": {relative: self._sha256(data) for relative, data in candidates.items()},
            "candidates": candidates,
            "diff": diff,
        }
        with self._write_lock:
            self._expire_color_reviews()
            while len(self._pending_color_reviews) >= MAX_PENDING_REVIEWS:
                oldest = min(self._pending_color_reviews, key=lambda key: self._pending_color_reviews[key]["created"])
                del self._pending_color_reviews[oldest]
            token = secrets.token_urlsafe(24)
            self._pending_color_reviews[token] = review
        changed_files = sum(before[name] != candidates[name] for name in candidates)
        return {
            "reviewToken": token,
            "diff": diff,
            "summary": f"Update saved My Menu layout and presentation ({changed_files} file{'s' if changed_files != 1 else ''}).",
        }

    def save_my_menu_configuration(self, review_token):
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed My Menu token is required.")
        with self._write_lock:
            self._expire_color_reviews()
            review = self._pending_color_reviews.pop(review_token, None)
            if review is None or "candidates" not in review:
                raise ProfileConflictError("This My Menu review expired or was already used. Review the current layout again.")
            before = {}
            for relative, expected_sha in review["source_sha256"].items():
                data = (self.paths.root / relative).read_bytes()
                if self._sha256(data) != expected_sha:
                    raise ProfileConflictError(f"{relative} changed after review. Reload the editor and review again.")
                before[relative] = data
            for relative, candidate in review["candidates"].items():
                if self._sha256(candidate) != review["candidate_sha256"][relative]:
                    raise ProfileConflictError("The reviewed My Menu candidate is no longer valid.")
            menu_candidate = yaml.safe_load(review["candidates"]["00 Master/my_menu.yaml"])
            color_candidate = yaml.safe_load(review["candidates"]["00 Master/my_menu_colors.yaml"])
            try:
                validate_my_menu(menu_candidate, self._all_my_menu_item_ids())
                validate_my_menu_colors(color_candidate)
            except (MyMenuError, MyMenuColorError) as exc:
                raise PrototypeError(str(exc)) from exc
            backup = self._create_my_menu_configuration_backup(review, before)
            written = []
            try:
                for relative, candidate in review["candidates"].items():
                    target = self.paths.root / relative
                    if candidate != before[relative]:
                        self._atomic_write(target, candidate, before[relative])
                        written.append(relative)
                errors = list(self._source_validator(self.paths.root))
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_errors = []
                for relative in reversed(written):
                    target = self.paths.root / relative
                    try:
                        self._atomic_write(target, before[relative], target.read_bytes())
                    except Exception as rollback_exc:  # pragma: no cover
                        rollback_errors.append(f"{relative}: {rollback_exc}")
                if rollback_errors:
                    raise PrototypeError(
                        f"My Menu save failed and rollback was incomplete. Recovery backup: {backup}. "
                        + "; ".join(rollback_errors)
                    ) from exc
                raise PrototypeError(
                    f"My Menu save failed; the prior source state was restored automatically. Recovery backup: {backup}. {exc}"
                ) from exc
            finally:
                self._pending_color_reviews.pop(review_token, None)
            self.my_menu = load_my_menu(self.paths, self._all_my_menu_item_ids())
            self.my_menu_colors = load_my_menu_colors(self.paths)
            return {
                "sourceFiles": list(review["candidates"]),
                "backup": str(backup),
                "validation": "passed",
                "tabs": copy.deepcopy(used_tabs(self.my_menu)),
                "colors": copy.deepcopy(self.my_menu_colors),
            }

    def _my_menu_configuration_candidates(self, tabs):
        if not isinstance(tabs, list):
            raise PrototypeError("My Menu tabs must be an array.")
        menu_tabs = []
        assignments = {}
        for index, tab in enumerate(tabs[:5], start=1):
            if not isinstance(tab, dict):
                raise PrototypeError(f"My Menu tab {index} must be an object.")
            name = str(tab.get("name") or "").strip()
            items = [item for item in (tab.get("items") or []) if item]
            color = tab.get("colorChoice")
            if not name and not items:
                continue
            if not name:
                raise PrototypeError(f"MY MENU{index} has items but no tab name.")
            if not items:
                raise PrototypeError(f"My Menu tab {name} requires at least one item.")
            menu_tabs.append({"name": name, "items": items})
            assignments[name] = color
        menu_candidate = {"schema_version": 1, "tabs": menu_tabs}
        color_candidate = {
            "schema_version": 1,
            "palette": copy.deepcopy(self.my_menu_colors["palette"]),
            "assignments": assignments,
        }
        try:
            validate_my_menu(menu_candidate, self._all_my_menu_item_ids())
            validate_my_menu_colors(color_candidate)
        except (MyMenuError, MyMenuColorError) as exc:
            raise PrototypeError(str(exc)) from exc
        return menu_candidate, color_candidate

    @staticmethod
    def _dump_yaml(data):
        return yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
            default_flow_style=False,
        ).encode("utf-8")

    def _create_my_menu_configuration_backup(self, review, before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base = self.paths.backups_dir / f"{timestamp}-profile-editor-my-menu"
        backup = base
        counter = 2
        while backup.exists():
            backup = base.with_name(f"{base.name}-{counter}")
            counter += 1
        for relative, data in before.items():
            target = backup / "before" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for relative, data in review["candidates"].items():
            target = backup / "candidate" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        manifest = {
            "version": 1,
            "created": datetime.now().astimezone().isoformat(),
            "operation": "update-my-menu",
            "source_sha256": review["source_sha256"],
            "candidate_sha256": review["candidate_sha256"],
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

    def review_my_menu_colors(self, assignments):
        candidate_data = self._my_menu_color_candidate(assignments)
        candidate = yaml.safe_dump(
            candidate_data,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
            default_flow_style=False,
        ).encode("utf-8")
        target = self.paths.my_menu_colors_file
        before = target.read_bytes()
        diff = "".join(
            difflib.unified_diff(
                before.decode("utf-8").splitlines(keepends=True),
                candidate.decode("utf-8").splitlines(keepends=True),
                fromfile="a/00 Master/my_menu_colors.yaml",
                tofile="b/00 Master/my_menu_colors.yaml",
            )
        )
        if not diff:
            raise PrototypeError("The My Menu color draft does not change any assignments.")
        review = {
            "created": time.monotonic(),
            "source_sha256": self._sha256(before),
            "candidate_sha256": self._sha256(candidate),
            "candidate": candidate,
            "diff": diff,
        }
        with self._write_lock:
            self._expire_color_reviews()
            while len(self._pending_color_reviews) >= MAX_PENDING_REVIEWS:
                oldest = min(
                    self._pending_color_reviews,
                    key=lambda key: self._pending_color_reviews[key]["created"],
                )
                del self._pending_color_reviews[oldest]
            token = secrets.token_urlsafe(24)
            self._pending_color_reviews[token] = review
        return {
            "reviewToken": token,
            "sourceFile": "00 Master/my_menu_colors.yaml",
            "diff": diff,
            "candidateYaml": candidate.decode("utf-8"),
            "summary": "Update named My Menu card-color assignments.",
        }

    def save_my_menu_colors(self, review_token):
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed My Menu color token is required.")
        with self._write_lock:
            self._expire_color_reviews()
            review = self._pending_color_reviews.get(review_token)
            if review is None:
                raise ProfileConflictError(
                    "This color review expired or was already used. Review the current colors again."
                )
            target = self.paths.my_menu_colors_file
            before = target.read_bytes()
            if self._sha256(before) != review["source_sha256"]:
                raise ProfileConflictError(
                    "My Menu colors changed after review. Reload the editor and review again."
                )
            if self._sha256(review["candidate"]) != review["candidate_sha256"]:
                raise ProfileConflictError("The reviewed My Menu color candidate is no longer valid.")
            candidate_data = yaml.safe_load(review["candidate"])
            try:
                validate_my_menu_colors(candidate_data)
            except MyMenuColorError as exc:
                raise PrototypeError(str(exc)) from exc
            backup = self._create_my_menu_color_backup(review, before)
            try:
                self._atomic_write(target, review["candidate"], before)
                errors = list(self._source_validator(self.paths.root))
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_error = None
                try:
                    self._atomic_write(target, before, target.read_bytes() if target.exists() else None)
                except Exception as rollback_exc:  # pragma: no cover
                    rollback_error = rollback_exc
                if rollback_error is not None:
                    raise PrototypeError(
                        f"Color save failed and automatic rollback also failed. Recovery backup: {backup}. "
                        f"Save error: {exc}. Rollback error: {rollback_error}"
                    ) from exc
                raise PrototypeError(
                    f"Color save failed; the prior source state was restored automatically. "
                    f"Recovery backup: {backup}. {exc}"
                ) from exc
            finally:
                self._pending_color_reviews.pop(review_token, None)
            self.my_menu_colors = load_my_menu_colors(self.paths)
            return {
                "sourceFile": "00 Master/my_menu_colors.yaml",
                "backup": str(backup),
                "validation": "passed",
                "colors": copy.deepcopy(self.my_menu_colors),
            }

    def _my_menu_color_candidate(self, assignments):
        if not isinstance(assignments, dict) or not assignments:
            raise PrototypeError("My Menu color assignments must be a non-empty object.")
        candidate = {
            "schema_version": 1,
            "palette": copy.deepcopy(self.my_menu_colors["palette"]),
            "assignments": {},
        }
        for name, choice in assignments.items():
            if not isinstance(name, str) or not name.strip():
                raise PrototypeError("Every saved My Menu color requires a named tab.")
            candidate["assignments"][name.strip()] = choice
        try:
            validate_my_menu_colors(candidate)
        except MyMenuColorError as exc:
            raise PrototypeError(str(exc)) from exc
        saved_names = {tab["name"] for tab in used_tabs(self.my_menu)}
        if set(candidate["assignments"]) != saved_names:
            raise PrototypeError("Named My Menu colors must match the persisted used tabs.")
        return candidate

    def _create_my_menu_color_backup(self, review, before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base = self.paths.backups_dir / f"{timestamp}-profile-editor-my-menu-colors"
        backup = base
        counter = 2
        while backup.exists():
            backup = base.with_name(f"{base.name}-{counter}")
            counter += 1
        before_dir = backup / "before" / "00 Master"
        candidate_dir = backup / "candidate" / "00 Master"
        before_dir.mkdir(parents=True)
        candidate_dir.mkdir(parents=True)
        (before_dir / "my_menu_colors.yaml").write_bytes(before)
        (candidate_dir / "my_menu_colors.yaml").write_bytes(review["candidate"])
        manifest = {
            "version": 1,
            "created": datetime.now().astimezone().isoformat(),
            "operation": "update-my-menu-colors",
            "source_sha256": review["source_sha256"],
            "candidate_sha256": review["candidate_sha256"],
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

    def baseline_detail(self):
        """Return current baseline controls for a session-only browser draft."""
        detail = self._shooting_profile_detail(
            name="Baseline",
            profile={"title": "Baseline", "overrides": {}},
            operation="update",
            source_name=None,
            source_fingerprint=None,
        )
        return {
            "sourceFile": "00 Master/baseline.yaml",
            "readOnly": True,
            "values": copy.deepcopy(self.default_fields),
            "sections": detail["sections"],
        }

    def editor_info(self):
        digest = hashlib.sha256()
        for relative in EDITOR_BUILD_FILES:
            source = self.paths.root / relative
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(source.read_bytes())
            digest.update(b"\0")
        return {
            "version": EDITOR_VERSION,
            "build": digest.hexdigest()[:8],
        }

    def build_readiness(self, pending_changes):
        try:
            pending = int(pending_changes)
        except (TypeError, ValueError) as exc:
            raise PrototypeError("Pending-change count must be an integer.") from exc
        if pending < 0:
            raise PrototypeError("Pending-change count cannot be negative.")
        source_errors = list(self._source_validator(self.paths.root))
        blockers = []
        if pending:
            blockers.append(
                f"Resolve {pending} unsaved browser {('draft' if pending == 1 else 'drafts')} before building."
            )
        blockers.extend(source_errors)
        return {
            "ready": not blockers,
            "pendingChanges": pending,
            "sourceValidation": "passed" if not source_errors else "failed",
            "blockers": blockers,
        }

    def run_local_build(self, pending_changes, confirmed):
        readiness = self.build_readiness(pending_changes)
        if not readiness["ready"]:
            raise PrototypeError("Local build is blocked: " + " ".join(readiness["blockers"]))
        if confirmed is not True:
            raise PrototypeError("Local build confirmation is required.")
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("A local build is already running.")
        commands = (
            ("Source validation", [sys.executable, "80 Build/validator.py", "--source-only"]),
            ("Development build", [sys.executable, "80 Build/build.py"]),
            ("Full validation", [sys.executable, "80 Build/validator.py"]),
        )
        results = []
        try:
            for label, command in commands:
                try:
                    completed = subprocess.run(
                        command,
                        cwd=self.paths.root,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=15 * 60,
                        check=False,
                    )
                except subprocess.TimeoutExpired as exc:
                    raise PrototypeError(f"{label} timed out after 15 minutes.") from exc
                output = completed.stdout[-80_000:]
                results.append({"step": label, "status": "passed" if completed.returncode == 0 else "failed", "output": output})
                if completed.returncode:
                    raise PrototypeError(f"{label} failed.\n{output}")
            return {"status": "passed", "steps": results}
        finally:
            self._build_lock.release()

    def baseline_impact(self, values, my_menu_tabs=None):
        """Analyze a complete, value-only baseline draft without writing it."""
        proposed = self._proposed_baseline(values)
        try:
            analysis = analyze_baseline_impact(self.baseline, proposed, self.profiles)
            analysis["cx_impact"] = analyze_cx_impact(
                self.baseline,
                proposed,
                self.profiles,
                self.registration,
            )
            analysis["my_menu_impact"] = analyze_my_menu_routes(
                self.baseline,
                proposed,
                self.profiles,
                self.registration,
                self._my_menu_route_catalog(),
                my_menu_tabs
                if my_menu_tabs is not None
                else copy.deepcopy(used_tabs(self.my_menu)),
            )
            return analysis
        except BaselineImpactError as exc:
            raise PrototypeError(str(exc)) from exc

    def _my_menu_route_catalog(self):
        return {
            item["setting_path"]: item["id"]
            for section in self.reference_sections
            for item in section["items"]
            if item.get("setting_path")
        }

    def baseline_plan(self, values, decisions, my_menu_tabs=None):
        """Validate decisions and return a read-only baseline migration plan."""
        proposed = self._proposed_baseline(values)
        try:
            return plan_baseline_migration(
                self.baseline,
                proposed,
                self.profiles,
                decisions,
                self.registration,
                self._my_menu_route_catalog(),
                my_menu_tabs
                if my_menu_tabs is not None
                else copy.deepcopy(used_tabs(self.my_menu)),
            )
        except BaselineImpactError as exc:
            raise PrototypeError(str(exc)) from exc

    def review_baseline_migration(self, payload):
        """Return an exact, one-use review of a complete multi-file migration."""
        if not isinstance(payload, dict):
            raise PrototypeError("Baseline migration review input must be an object.")
        if payload.get("acknowledgeCxImpact") is not True:
            raise PrototypeError("Acknowledge the C1–C3 impact report before reviewing the migration.")
        if payload.get("acknowledgeMyMenuImpact") is not True:
            raise PrototypeError("Acknowledge the My Menu route report before reviewing the migration.")
        values = payload.get("values")
        decisions = payload.get("decisions")
        tabs = payload.get("myMenuTabs")
        proposed = self._proposed_baseline(values)
        plan = self.baseline_plan(values, decisions, tabs)
        if not plan.get("complete"):
            raise PrototypeError("Complete every profile migration decision before review.")
        try:
            candidates = build_migration_candidates(
                self.baseline,
                proposed,
                self.profiles,
                plan,
            )
        except BaselineMigrationError as exc:
            raise PrototypeError(str(exc)) from exc
        before = self._migration_source_bytes(candidates)
        diff = migration_diff(before, candidates)
        if not diff:
            raise PrototypeError("The migration does not change any source files.")
        self._validate_migration_candidates(candidates)
        impact = self.baseline_impact(values, tabs)
        review = {
            "created": time.monotonic(),
            "candidates": candidates,
            "candidate_sha256": {path: self._sha256(data) for path, data in candidates.items()},
            "source_sha256": {path: self._sha256(data) for path, data in before.items()},
            "diff": diff,
            "plan": plan,
            "impact": impact,
            "acknowledgements": {"cx": True, "my_menu": True},
        }
        with self._write_lock:
            self._expire_migration_reviews()
            while len(self._pending_migration_reviews) >= MAX_PENDING_REVIEWS:
                oldest = min(
                    self._pending_migration_reviews,
                    key=lambda key: self._pending_migration_reviews[key]["created"],
                )
                del self._pending_migration_reviews[oldest]
            token = secrets.token_urlsafe(24)
            self._pending_migration_reviews[token] = review
        return {
            "reviewToken": token,
            "sourceFiles": sorted(candidates),
            "diff": diff,
            "summary": plan["summary"],
            "cxImpact": impact["cx_impact"],
            "myMenuImpact": impact["my_menu_impact"],
        }

    def save_baseline_migration(self, review_token):
        """Apply one reviewed migration or restore every source on any failure."""
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed baseline migration token is required.")
        with self._write_lock:
            self._expire_migration_reviews()
            review = self._pending_migration_reviews.get(review_token)
            if review is None:
                raise ProfileConflictError(
                    "This migration review expired or was already used. Review the current plan again."
                )
            try:
                before = self._migration_source_bytes(review["candidates"])
                current_fingerprints = {path: self._sha256(data) for path, data in before.items()}
                if current_fingerprints != review["source_sha256"]:
                    raise ProfileConflictError(
                        "A baseline or affected profile changed after review. Reload and review the migration again."
                    )
                for path, data in review["candidates"].items():
                    if self._sha256(data) != review["candidate_sha256"][path]:
                        raise ProfileConflictError("The reviewed migration candidate is no longer valid.")
                self._validate_migration_candidates(review["candidates"])
                backup = self._create_migration_backup(review, before)
                written = []
                try:
                    for relative in sorted(review["candidates"]):
                        target = self.paths.root / relative
                        self._atomic_write(target, review["candidates"][relative], before[relative])
                        written.append(relative)
                    errors = list(self._source_validator(self.paths.root))
                    if errors:
                        raise PrototypeError("Post-migration source validation failed: " + "; ".join(errors))
                except Exception as exc:
                    rollback_errors = []
                    for relative in reversed(written):
                        target = self.paths.root / relative
                        try:
                            self._atomic_write(target, before[relative], target.read_bytes())
                        except Exception as rollback_exc:  # pragma: no cover - catastrophic filesystem failure
                            rollback_errors.append(f"{relative}: {rollback_exc}")
                    if rollback_errors:
                        raise PrototypeError(
                            f"Migration failed and automatic rollback was incomplete. Recovery backup: {backup}. "
                            f"Migration error: {exc}. Rollback errors: {'; '.join(rollback_errors)}"
                        ) from exc
                    raise PrototypeError(
                        f"Migration failed; every written source was restored automatically. "
                        f"Recovery backup: {backup}. {exc}"
                    ) from exc
                self._reload_project_data()
                return {
                    "sourceFiles": sorted(review["candidates"]),
                    "backup": str(backup),
                    "validation": "passed",
                }
            finally:
                self._pending_migration_reviews.pop(review_token, None)

    def _migration_source_bytes(self, candidates):
        before = {}
        for relative in candidates:
            target = (self.paths.root / relative).resolve()
            try:
                target.relative_to(self.paths.root.resolve())
            except ValueError as exc:
                raise PrototypeError(f"Migration source escapes the project root: {relative}") from exc
            if not target.is_file():
                raise ProfileConflictError(f"Migration source no longer exists: {relative}")
            before[relative] = target.read_bytes()
        return before

    def _validate_migration_candidates(self, candidates):
        from validators import baseline_validator, profile_validator, yaml_validator

        with tempfile.TemporaryDirectory(prefix="baseline-migration-candidate-") as temporary:
            shadow = Path(temporary)
            for directory in ("00 Master", "10 Profiles", "50 Field Guide"):
                shutil.copytree(self.paths.root / directory, shadow / directory)
            for relative, data in candidates.items():
                target = shadow / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            errors = []
            for validator in (yaml_validator.validate, baseline_validator.validate, profile_validator.validate):
                errors.extend(issue.message for issue in validator(shadow) if issue.level == "error")
            if errors:
                raise PrototypeError("Migration candidate validation failed: " + "; ".join(errors))

    def _create_migration_backup(self, review, before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base = self.paths.backups_dir / f"{timestamp}-baseline-migration"
        backup = base
        counter = 2
        while backup.exists():
            backup = base.with_name(f"{base.name}-{counter}")
            counter += 1
        for relative, data in before.items():
            target = backup / "before" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for relative, data in review["candidates"].items():
            target = backup / "candidate" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        manifest = {
            "version": 1,
            "created": datetime.now().astimezone().isoformat(),
            "operation": "baseline_migration",
            "source_files": sorted(review["candidates"]),
            "source_sha256": review["source_sha256"],
            "candidate_sha256": review["candidate_sha256"],
            "acknowledgements": review["acknowledgements"],
            "plan_summary": review["plan"]["summary"],
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

    def _proposed_baseline(self, values):
        if not isinstance(values, dict):
            raise PrototypeError("Baseline draft values must be an object.")
        missing = sorted(set(self.default_fields) - set(values))
        unknown = sorted(set(values) - set(self.default_fields))
        if missing:
            raise PrototypeError(
                "Baseline impact drafts cannot remove settings: " + ", ".join(missing)
            )
        if unknown:
            raise PrototypeError(
                "Baseline impact drafts cannot add settings: " + ", ".join(unknown)
            )
        clean = {
            path: self._coerce_value(path, value)
            for path, value in values.items()
        }
        proposed = copy.deepcopy(self.baseline)
        proposed["defaults"] = nested_from_flat(clean)
        return proposed

    def profile_detail(self, name):
        profile = self._profile(name)
        fingerprint = self._profile_fingerprint(name)
        if is_reference_card(profile):
            reference_settings = (
                my_menu_reference_settings(self.paths)
                if profile.get("reference_source") == "my_menu"
                else profile.get("reference_settings") or []
            )
            return {
                "name": name,
                "title": profile.get("title", name),
                "subtitle": profile.get("subtitle") or "",
                "cardType": "reference",
                "editableDraft": False,
                "sourceFile": f"10 Profiles/{name}.yaml",
                "sourceFingerprint": fingerprint,
                "referenceSettings": reference_settings,
                "sections": [],
                "originalOverrides": {},
            }

        return self._shooting_profile_detail(
            name=name,
            profile=profile,
            operation="update",
            source_name=name,
            source_fingerprint=fingerprint,
        )

    def profile_draft(self, operation, source_name=None):
        if operation == "create":
            title = self._available_profile_name("New Profile")
            profile = {
                "metadata": {
                    "version": 1.0,
                    "status": "Draft",
                    "last_updated": date.today(),
                    "release": False,
                },
                "title": title,
                "inherits": "baseline",
                "overrides": {},
            }
            return self._shooting_profile_detail(
                name=title,
                profile=profile,
                operation="create",
                source_name=None,
                source_fingerprint=None,
            )
        if operation != "duplicate":
            raise PrototypeError("Profile draft operation must be create or duplicate.")
        source = self._profile(source_name)
        if is_reference_card(source):
            raise PrototypeError("Reference cards cannot be duplicated in the profile editor.")
        title = self._available_profile_name(f"{source.get('title', source_name)} Copy")
        profile = copy.deepcopy(source)
        profile["title"] = title
        profile["metadata"] = self._new_profile_metadata(profile.get("metadata"))
        return self._shooting_profile_detail(
            name=title,
            profile=profile,
            operation="duplicate",
            source_name=source_name,
            source_fingerprint=self._profile_fingerprint(source_name),
        )

    def _shooting_profile_detail(
        self,
        *,
        name,
        profile,
        operation,
        source_name,
        source_fingerprint,
    ):

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
            "subtitle": profile.get("subtitle") or "",
            "cardType": "profile",
            "editableDraft": True,
            "operation": operation,
            "sourceProfile": source_name,
            "targetName": name,
            "sourceFile": f"10 Profiles/{source_name or name}.yaml" if source_name else "New profile",
            "sourceFingerprint": source_fingerprint,
            "metadata": {
                "status": (profile.get("metadata") or {}).get("status", "Draft"),
                "release": bool((profile.get("metadata") or {}).get("release", False)),
            },
            "sections": sections,
            "settingOrder": [path for path in self.setting_order if path in self.default_fields],
            "cardSettingPaths": self._card_setting_paths(profile),
            "originalOverrides": original,
        }

    def _card_setting_paths(self, profile):
        if is_reference_card(profile):
            return []
        merged = merge(self.defaults, profile.get("overrides") or {})
        visible = displayed_card_setting_paths(profile, merged, self.paths)
        return [path for path in self.setting_order if path in visible]

    def card_setting_paths(self, name, flat_overrides):
        profile = copy.deepcopy(self._profile(name))
        if is_reference_card(profile):
            return []
        profile["overrides"] = nested_from_flat(self._validate_overrides(flat_overrides))
        return self._card_setting_paths(profile)

    def draft_card_setting_paths(self, payload):
        profile, _target_name, _operation, _source_name, _fingerprint = self._candidate_profile(payload)
        return self._card_setting_paths(profile)

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

    def review_profile(self, payload):
        review = self._prepare_review(payload)
        with self._write_lock:
            self._expire_reviews()
            while len(self._pending_reviews) >= MAX_PENDING_REVIEWS:
                oldest = min(self._pending_reviews, key=lambda key: self._pending_reviews[key]["created"])
                del self._pending_reviews[oldest]
            token = secrets.token_urlsafe(24)
            self._pending_reviews[token] = review
        return {
            "reviewToken": token,
            "operation": review["operation"],
            "targetName": review["target_name"],
            "sourceFile": f"10 Profiles/{review['target_name']}.yaml",
            "diff": review["diff"],
            "candidateYaml": review["candidate"].decode("utf-8"),
            "summary": review["summary"],
        }

    def save_profile(self, review_token):
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed profile token is required.")
        with self._write_lock:
            self._expire_reviews()
            review = self._pending_reviews.get(review_token)
            if review is None:
                raise ProfileConflictError("This review expired or was already used. Review the current draft again.")
            self._confirm_review_source(review)
            self._validate_candidate(review["target_name"], review["candidate"])
            target = self._profile_path(review["target_name"])
            before = target.read_bytes() if target.exists() else None
            backup = self._create_transaction_backup(review, before)
            try:
                self._atomic_write(target, review["candidate"], before)
                errors = list(self._source_validator(self.paths.root))
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_error = None
                try:
                    if before is None:
                        target.unlink(missing_ok=True)
                    else:
                        self._atomic_write(target, before, target.read_bytes() if target.exists() else None)
                except Exception as rollback_exc:  # pragma: no cover - catastrophic filesystem failure
                    rollback_error = rollback_exc
                if rollback_error is not None:
                    raise PrototypeError(
                        f"Save failed and automatic rollback also failed. Recovery backup: {backup}. "
                        f"Save error: {exc}. Rollback error: {rollback_error}"
                    ) from exc
                raise PrototypeError(
                    f"Save failed; the prior source state was restored automatically. Recovery backup: {backup}. {exc}"
                ) from exc
            finally:
                self._pending_reviews.pop(review_token, None)
            self._reload_profiles()
            return {
                "savedProfile": review["target_name"],
                "sourceFile": f"10 Profiles/{review['target_name']}.yaml",
                "backup": str(backup),
                "sourceFingerprint": self._profile_fingerprint(review["target_name"]),
                "validation": "passed",
            }

    def preview_draft(self, payload):
        profile, target_name, _operation, _source_name, _fingerprint = self._candidate_profile(payload)
        return self._render_preview(target_name, profile)

    def _prepare_review(self, payload):
        profile, target_name, operation, source_name, source_fingerprint = self._candidate_profile(payload)
        candidate = self._dump_profile(profile)
        self._confirm_target_state(operation, source_name, target_name, source_fingerprint)
        self._validate_candidate(target_name, candidate)
        target = self._profile_path(target_name)
        before = target.read_text(encoding="utf-8") if target.exists() else ""
        before_label = f"a/10 Profiles/{target_name}.yaml" if before else "/dev/null"
        diff = "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                candidate.decode("utf-8").splitlines(keepends=True),
                fromfile=before_label,
                tofile=f"b/10 Profiles/{target_name}.yaml",
            )
        )
        if not diff:
            raise PrototypeError("The draft does not change the selected profile.")
        return {
            "created": time.monotonic(),
            "operation": operation,
            "source_name": source_name,
            "source_fingerprint": source_fingerprint,
            "target_name": target_name,
            "target_absent": not target.exists(),
            "candidate": candidate,
            "candidate_sha256": self._sha256(candidate),
            "diff": diff,
            "summary": self._review_summary(operation, source_name, target_name),
        }

    def _candidate_profile(self, payload):
        if not isinstance(payload, dict):
            raise PrototypeError("Profile draft must be an object.")
        operation = payload.get("operation")
        if operation not in {"update", "create", "duplicate"}:
            raise PrototypeError("Profile operation must be update, create, or duplicate.")
        source_name = payload.get("sourceProfile")
        source_fingerprint = payload.get("sourceFingerprint")
        target_name = self._validate_profile_name(payload.get("targetName"))
        title = self._single_line(payload.get("title"), "Title", 120, required=True)
        subtitle = self._single_line(payload.get("subtitle"), "Subtitle", 200, required=False)
        clean_overrides = self._validate_overrides(payload.get("overrides", {}))

        if operation == "create":
            if source_name not in {None, ""} or source_fingerprint not in {None, ""}:
                raise PrototypeError("A baseline-derived profile must not identify a source profile.")
            profile = {
                "metadata": self._new_profile_metadata(),
                "title": title,
                "inherits": "baseline",
                "overrides": nested_from_flat(clean_overrides),
            }
        else:
            if not isinstance(source_name, str) or not source_name:
                raise PrototypeError("The source profile is required.")
            source = copy.deepcopy(self._profile(source_name))
            if is_reference_card(source):
                raise PrototypeError("Reference cards remain read-only.")
            if not isinstance(source_fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", source_fingerprint):
                raise PrototypeError("The source profile fingerprint is missing or invalid.")
            if operation == "update" and target_name != source_name:
                raise PrototypeError("Renaming an existing profile is not available in Stage 2.")
            profile = source
            if operation == "duplicate":
                profile["metadata"] = self._new_profile_metadata(profile.get("metadata"))
            else:
                metadata = profile.setdefault("metadata", {})
                status = payload.get("status")
                release = payload.get("release")
                if status not in PROFILE_STATUSES:
                    raise PrototypeError("Profile status must be Draft, Review, or Final.")
                if not isinstance(release, bool):
                    raise PrototypeError("Profile release state must be true or false.")
                metadata["status"] = status
                metadata["release"] = release
                metadata["last_updated"] = date.today()
            profile["title"] = title
            profile["inherits"] = "baseline"
            profile["overrides"] = nested_from_flat(clean_overrides)
        if subtitle:
            profile["subtitle"] = subtitle
        else:
            profile.pop("subtitle", None)
        return profile, target_name, operation, source_name or None, source_fingerprint or None

    def _confirm_review_source(self, review):
        self._confirm_target_state(
            review["operation"],
            review["source_name"],
            review["target_name"],
            review["source_fingerprint"],
        )
        target = self._profile_path(review["target_name"])
        if review["target_absent"] != (not target.exists()):
            raise ProfileConflictError("The target profile changed after review. Reload and review again.")

    def _confirm_target_state(self, operation, source_name, target_name, source_fingerprint):
        target = self._profile_path(target_name)
        if operation in {"create", "duplicate"}:
            conflicts = {name.casefold() for name in self.profiles}
            if target_name.casefold() in conflicts or target.exists():
                raise ProfileConflictError(f"A profile named {target_name} already exists.")
        if operation in {"update", "duplicate"}:
            current = self._profile_fingerprint(source_name)
            if current != source_fingerprint:
                raise ProfileConflictError(
                    f"{source_name}.yaml changed after it was loaded. Reload the profile before reviewing or saving."
                )

    def _validate_candidate(self, target_name, candidate):
        from validators import profile_validator
        from validators.common import load_yaml_checked

        with tempfile.TemporaryDirectory(prefix="profile-editor-candidate-") as temporary:
            shadow = Path(temporary)
            (shadow / "00 Master").mkdir(parents=True)
            (shadow / "10 Profiles").mkdir()
            (shadow / "50 Field Guide").mkdir()
            for relative in (
                "00 Master/baseline.yaml",
                "00 Master/card_layout.yaml",
                "50 Field Guide/required_appendices.yaml",
            ):
                source = self.paths.root / relative
                destination = shadow / relative
                shutil.copy2(source, destination)
            for source in discover_profiles(self.paths):
                if source.stem != target_name:
                    shutil.copy2(source, shadow / "10 Profiles" / source.name)
            candidate_path = shadow / "10 Profiles" / f"{target_name}.yaml"
            candidate_path.write_bytes(candidate)
            try:
                loaded = load_yaml_checked(candidate_path)
            except Exception as exc:
                raise PrototypeError(f"Candidate YAML is invalid: {exc}") from exc
            if not isinstance(loaded, dict):
                raise PrototypeError("Candidate profile must be a YAML mapping.")
            errors = [issue.message for issue in profile_validator.validate(shadow) if issue.level == "error"]
            if errors:
                raise PrototypeError("Candidate profile validation failed: " + "; ".join(errors))

    def _create_transaction_backup(self, review, before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", review["target_name"]).strip("-").lower()
        base = self.paths.backups_dir / f"{timestamp}-profile-editor-{review['operation']}-{safe_name}"
        backup = base
        counter = 2
        while backup.exists():
            backup = base.with_name(f"{base.name}-{counter}")
            counter += 1
        before_dir = backup / "before" / "10 Profiles"
        candidate_dir = backup / "candidate" / "10 Profiles"
        before_dir.mkdir(parents=True)
        candidate_dir.mkdir(parents=True)
        if before is not None:
            (before_dir / f"{review['target_name']}.yaml").write_bytes(before)
        (candidate_dir / f"{review['target_name']}.yaml").write_bytes(review["candidate"])
        manifest = {
            "version": 1,
            "created": datetime.now().astimezone().isoformat(),
            "operation": review["operation"],
            "source_profile": review["source_name"],
            "source_fingerprint": review["source_fingerprint"],
            "target_profile": review["target_name"],
            "target_existed": before is not None,
            "candidate_sha256": review["candidate_sha256"],
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

    @staticmethod
    def _atomic_write(target, data, prior):
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.stem}-", suffix=".yaml.tmp", dir=target.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as output:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            mode = target.stat().st_mode & 0o777 if target.exists() else 0o644
            os.chmod(temporary, mode)
            os.replace(temporary, target)
            directory = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _dump_profile(profile):
        return yaml.safe_dump(
            profile,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
            default_flow_style=False,
        ).encode("utf-8")

    @staticmethod
    def _new_profile_metadata(existing=None):
        version = (existing or {}).get("version", 1.0)
        return {
            "version": version,
            "status": "Draft",
            "last_updated": date.today(),
            "release": False,
        }

    def _reload_profiles(self):
        self.profiles = self._load_profiles()
        self.choices = self._choice_catalog()

    def _reload_project_data(self):
        self.baseline = load_baseline(self.paths)
        self.defaults = self.baseline.get("defaults") or {}
        self.default_fields = flatten(self.defaults)
        self.profiles = self._load_profiles()
        self._validate_option_catalog()
        self.setting_order = self._setting_order()
        self.choices = self._choice_catalog()

    def _profile_path(self, name):
        path = self.paths.profile_file(name).resolve()
        if path.parent != self.paths.profiles_dir.resolve():
            raise PrototypeError("Profile path must stay inside 10 Profiles.")
        return path

    def _profile_fingerprint(self, name):
        path = self._profile_path(name)
        if not path.is_file():
            raise ProfileConflictError(f"Profile source no longer exists: {name}.yaml")
        return self._sha256(path.read_bytes())

    @staticmethod
    def _sha256(data):
        return hashlib.sha256(data).hexdigest()

    def _validate_profile_name(self, value):
        if not isinstance(value, str):
            raise PrototypeError("Profile filename is required.")
        value = value.strip()
        if not PROFILE_NAME_PATTERN.fullmatch(value) or value.endswith((".", " ")) or ".." in value:
            raise PrototypeError(
                "Profile filename must be 1–80 characters using letters, numbers, spaces, and ordinary title punctuation."
            )
        return value

    @staticmethod
    def _single_line(value, label, maximum, required):
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise PrototypeError(f"{label} must be text.")
        value = value.strip()
        if required and not value:
            raise PrototypeError(f"{label} is required.")
        if len(value) > maximum or any(character in value for character in "\r\n\x00"):
            raise PrototypeError(f"{label} must be a single line of at most {maximum} characters.")
        return value

    def _available_profile_name(self, preferred):
        existing = {name.casefold() for name in self.profiles}
        if preferred.casefold() not in existing:
            return preferred
        counter = 2
        while f"{preferred} {counter}".casefold() in existing:
            counter += 1
        return f"{preferred} {counter}"

    @staticmethod
    def _review_summary(operation, source_name, target_name):
        if operation == "update":
            return f"Update existing profile {target_name}.yaml"
        if operation == "duplicate":
            return f"Create {target_name}.yaml from {source_name}.yaml"
        return f"Create baseline-derived profile {target_name}.yaml"

    def _expire_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [token for token, review in self._pending_reviews.items() if review["created"] < cutoff]
        for token in expired:
            del self._pending_reviews[token]

    def _expire_migration_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [
            token
            for token, review in self._pending_migration_reviews.items()
            if review["created"] < cutoff
        ]
        for token in expired:
            del self._pending_migration_reviews[token]

    def _expire_color_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [
            token
            for token, review in self._pending_color_reviews.items()
            if review["created"] < cutoff
        ]
        for token in expired:
            del self._pending_color_reviews[token]

    @staticmethod
    def _validate_project_sources(root):
        from validator import run

        return [issue.message for issue in run(root, source_only=True) if issue.level == "error"]

    def preview(self, name, flat_overrides):
        profile = copy.deepcopy(self._profile(name))
        if is_reference_card(profile):
            if flat_overrides not in ({}, None):
                raise PrototypeError("Reference cards do not use profile overrides.")
            return self._render_preview(name, profile)
        clean = self._validate_overrides(flat_overrides)
        nested = nested_from_flat(clean)
        profile["overrides"] = nested
        return self._render_preview(name, profile)

    def _render_preview(self, name, profile):
        merged = merge(self.defaults, profile.get("overrides") or {})
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
            if path == "/api/baseline":
                return self._json(self.model.baseline_detail())
            if path == "/api/editor-info":
                return self._json(self.model.editor_info())
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
        if parsed.path not in {
            "/api/preview",
            "/api/profile-drafts",
            "/api/profile-reviews",
            "/api/profile-saves",
            "/api/baseline-impact",
            "/api/baseline-plan",
            "/api/baseline-migration-reviews",
            "/api/baseline-migration-saves",
            "/api/my-menu-color-reviews",
            "/api/my-menu-color-saves",
            "/api/my-menu-reviews",
            "/api/my-menu-saves",
            "/api/build-readiness",
            "/api/local-build",
        }:
            return self._json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
        try:
            payload = self._request_json()
            if parsed.path == "/api/profile-drafts":
                return self._json(self.model.profile_draft(payload.get("operation"), payload.get("sourceProfile")))
            if parsed.path == "/api/profile-reviews":
                return self._json(self.model.review_profile(payload))
            if parsed.path == "/api/profile-saves":
                return self._json(self.model.save_profile(payload.get("reviewToken")))
            if parsed.path == "/api/baseline-impact":
                return self._json(
                    self.model.baseline_impact(
                        payload.get("values"),
                        payload.get("myMenuTabs"),
                    )
                )
            if parsed.path == "/api/baseline-plan":
                return self._json(
                    self.model.baseline_plan(
                        payload.get("values"),
                        payload.get("decisions"),
                        payload.get("myMenuTabs"),
                    )
                )
            if parsed.path == "/api/baseline-migration-reviews":
                return self._json(self.model.review_baseline_migration(payload))
            if parsed.path == "/api/baseline-migration-saves":
                return self._json(self.model.save_baseline_migration(payload.get("reviewToken")))
            if parsed.path == "/api/my-menu-color-reviews":
                return self._json(self.model.review_my_menu_colors(payload.get("assignments")))
            if parsed.path == "/api/my-menu-color-saves":
                return self._json(self.model.save_my_menu_colors(payload.get("reviewToken")))
            if parsed.path == "/api/my-menu-reviews":
                return self._json(self.model.review_my_menu_configuration(payload.get("tabs")))
            if parsed.path == "/api/my-menu-saves":
                return self._json(self.model.save_my_menu_configuration(payload.get("reviewToken")))
            if parsed.path == "/api/build-readiness":
                return self._json(self.model.build_readiness(payload.get("pendingChanges")))
            if parsed.path == "/api/local-build":
                return self._json(
                    self.model.run_local_build(
                        payload.get("pendingChanges"), payload.get("confirmLocalBuild")
                    )
                )
            if "operation" in payload:
                output = self.model.preview_draft(payload)
                card_setting_paths = self.model.draft_card_setting_paths(payload)
            else:
                output = self.model.preview(payload.get("profile"), payload.get("overrides", {}))
                card_setting_paths = self.model.card_setting_paths(
                    payload.get("profile"), payload.get("overrides", {})
                )
            return self._json({
                "previewUrl": "/preview/card.html",
                "outputFile": str(output),
                "cardSettingPaths": card_setting_paths,
            })
        except ProfileConflictError as exc:
            return self._json({"error": str(exc)}, HTTPStatus.CONFLICT)
        except PrototypeError as exc:
            return self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            return self._json({"error": f"Profile editor operation failed: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _request_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise PrototypeError("Invalid request length.") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise PrototypeError("Invalid or oversized request.")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PrototypeError("Request body must be valid JSON.") from exc
        if not isinstance(payload, dict):
            raise PrototypeError("Request body must be a JSON object.")
        return payload

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
    print("Canon Camera Reference — guarded profile editor")
    print(f"Open http://{HOST}:{args.port}")
    print("Press Control-C to stop. Profile saves require exact diff review, backup, and validation.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProfile editor stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
