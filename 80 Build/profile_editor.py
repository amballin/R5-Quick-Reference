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
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen
from uuid import uuid4

import yaml


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
STATIC_DIR = BUILD_DIR / "profile_editor"
CATALOG_FILE = STATIC_DIR / "canon_options.yaml"
CONTROL_CATALOG_FILE = STATIC_DIR / "control_options.yaml"
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from asset_manager import ProjectPaths
from application_version import application_version_info
from appendix_renderer import render_appendices
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
from card_identity import (
    CardIdentityError,
    index_profiles,
    narrative_mentions,
    profile_by_id,
    profile_by_title,
    valid_card_id,
)
from cleanup_review import CleanupReview, CleanupReviewError
from camera_lab_tracker_import import (
    CameraLabTrackerImportError,
    build_candidate_status as build_camera_lab_candidate_status,
    inspect_evidence as inspect_camera_lab_evidence,
)
from cx_route_analysis import CxRouteAnalysisError, analyze_foundation_fit
from finish_day import FinishDayError, FinishDayWorkflow
from integrate_branch import BranchIntegrationError, BranchIntegrationWorkflow
from html_renderer import LABEL, displayed_card_setting_paths, render_card
from icon_manager import IconManager
from lens_guidance import load_sources as load_lens_sources
from my_menu import MyMenuError, load_my_menu, validate_my_menu, used_tabs
from my_menu_colors import MyMenuColorError, load_my_menu_colors, validate_my_menu_colors
from my_menu_reference import reference_settings as my_menu_reference_settings
from control_reference import (
    CARD_CONTROL_LABELS,
    card_reference_settings as control_reference_settings,
    reference_setting_key as control_reference_setting_key,
)
from profile_loader import load_baseline, load_yaml
from profile_pack import (
    EMBEDDED_SOURCE_PATHS,
    ProfilePackError,
    profile_pack_revision,
    resolve_profile_pack,
)
from profile_pack_creation import ProfilePackCreationError, ProfilePackCreator
from profile_pack_git import ProfilePackGitError, ProfilePackGitWorkflow
from profile_pack_selection import (
    ProfilePackSelectionError,
    ProfilePackSelectionStore,
)
from project_context import project_context_info
from numbers_automation import numbers_resume_recovery
from publication_workflow import (
    MainEditorLauncher,
    PublicationWorkflow,
    PublicationWorkflowError,
)
from utilities import flatten


HOST = "127.0.0.1"
MAIN_EDITOR_PORT = 8765
PROTOTYPE_EDITOR_PORT = 8766
DEFAULT_PORT = MAIN_EDITOR_PORT
CAMERA_LAB_ORIGIN = "http://127.0.0.1:8770"
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
DISPLAY_CATEGORIES = {"subject", "reference"}
LENS_ROLES = {"primary", "alternative", "specialist"}
CONTROL_EVIDENCE_STATUSES = {
    "verified_canon_capability",
    "owner_confirmed",
    "approved_target_pending_camera_verification",
    "recommendation",
    "unresolved",
}
PROFILE_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9 .&+()'_-]{0,79}")
REVIEW_TTL_SECONDS = 30 * 60
MAX_PENDING_REVIEWS = 20
EXTERNAL_PACK_EDITOR_ENDPOINTS = {
    "/api/profile-pack-switch",
    "/api/camera-lab-launch",
    "/api/preview",
    "/api/profile-drafts",
    "/api/profile-reviews",
    "/api/profile-saves",
    "/api/profile-removal-reviews",
    "/api/profile-removals",
    "/api/profile-restore-reviews",
    "/api/profile-restores",
    "/api/baseline-impact",
    "/api/baseline-plan",
    "/api/baseline-migration-reviews",
    "/api/baseline-migration-saves",
    "/api/my-menu-color-reviews",
    "/api/my-menu-color-saves",
    "/api/my-menu-reviews",
    "/api/my-menu-saves",
    "/api/cx-foundation-fit",
    "/api/cx-assignment-reviews",
    "/api/cx-selection-reviews",
    "/api/cx-foundation-saves",
    "/api/camera-buttons-preview",
    "/api/camera-buttons-reviews",
    "/api/camera-buttons-saves",
    "/api/camera-lab-evidence-reviews",
    "/api/camera-lab-evidence-saves",
    "/api/profile-pack-git-status",
    "/api/profile-pack-git-commit-reviews",
    "/api/profile-pack-git-commits",
    "/api/profile-pack-git-remote-reviews",
    "/api/profile-pack-git-remotes",
    "/api/profile-pack-git-pushes",
    "/api/profile-starter-reviews",
    "/api/profile-starter-saves",
}
EDITOR_BUILD_FILES = (
    "00 Master/application_version.yaml",
    "00 Master/feature_interactions.yaml",
    "00 Master/profile_lens_guidance.yaml",
    "80 Build/application_version.py",
    "80 Build/asset_manager.py",
    "controls.yaml",
    "data/canon_r5_custom_controls_current.yaml",
    "data/stabilization_reference.yaml",
    "00 Master/my_menu.yaml",
    "00 Master/my_menu_colors.yaml",
    "10 Profiles/My Menu.yaml",
    "20 Templates/card.html",
    "90 Testing/eos_r5_verification_tracker.yaml",
    "80 Build/baseline_impact.py",
    "80 Build/baseline_migration.py",
    "80 Build/card_identity.py",
    "80 Build/cx_route_analysis.py",
    "80 Build/feature_interactions.py",
    "80 Build/finish_day.py",
    "80 Build/integrate_branch.py",
    "80 Build/cleanup_review.py",
    "80 Build/lens_guidance.py",
    "80 Build/control_reference.py",
    "80 Build/camera_lab_tracker_import.py",
    "80 Build/html_renderer.py",
    "80 Build/my_menu_colors.py",
    "80 Build/my_menu.py",
    "80 Build/my_menu_reference.py",
    "80 Build/numbers_automation.py",
    "80 Build/profile_editor.py",
    "80 Build/profile_pack.py",
    "80 Build/profile_pack_creation.py",
    "80 Build/profile_pack_git.py",
    "80 Build/profile_pack_templates/AGENTS.md",
    "80 Build/profile_pack_selection.py",
    "80 Build/profile_editor/app.js",
    "80 Build/profile_editor/control_options.yaml",
    "80 Build/profile_editor/index.html",
    "80 Build/profile_editor/styles.css",
    "80 Build/project_context.py",
    "80 Build/publication_workflow.py",
    "80 Build/scripts/profile-editor-runtime.sh",
    "80 Build/scripts/start-profile-editor.sh",
    "80 Build/scripts/stop-profile-editor.sh",
)


def default_editor_port(project_root=PROJECT_ROOT):
    """Keep main and development worktrees on distinct loopback ports."""
    context = project_context_info(Path(project_root).resolve())
    return MAIN_EDITOR_PORT if context.get("kind") == "main" else PROTOTYPE_EDITOR_PORT


class PrototypeError(ValueError):
    def __init__(self, message, *, recovery=None):
        super().__init__(message)
        self.recovery = recovery


class ProfileConflictError(PrototypeError):
    pass


class GuardedJobManager:
    """Run one long guarded workflow at a time and expose reconnectable progress."""

    def __init__(self):
        self._jobs = {}
        self._lock = threading.RLock()

    def start(self, kind, action):
        with self._lock:
            running = next((job for job in self._jobs.values() if job["status"] == "running"), None)
            if running:
                raise PrototypeError(
                    "Another long-running guarded action is already in progress.",
                    recovery={
                        "kind": "guarded-action-running",
                        "summary": "Return to the running workflow to watch its progress or wait for it to finish.",
                        "jobId": running["jobId"],
                        "jobKind": running["kind"],
                        "actions": ["reconnect-running-action"],
                    },
                )
            job_id = secrets.token_urlsafe(24)
            now = time.time()
            job = {
                "jobId": job_id,
                "kind": kind,
                "status": "running",
                "stage": "Starting",
                "command": "",
                "log": [],
                "startedAt": now,
                "updatedAt": now,
                "result": None,
                "error": None,
                "recovery": None,
            }
            self._jobs[job_id] = job

        def progress(stage, command="", output="", completed=False):
            with self._lock:
                current = self._jobs.get(job_id)
                if not current:
                    return
                current["stage"] = stage
                current["command"] = command
                current["updatedAt"] = time.time()
                marker = "✓" if completed else "▶"
                entry = f"{marker} {stage}"
                if command:
                    entry += f"\n{command}"
                if output:
                    entry += f"\n{str(output).strip()}"
                current["log"].append(entry)
                while sum(len(item) for item in current["log"]) > 80_000:
                    current["log"].pop(0)

        def worker():
            try:
                result = action(progress)
            except Exception as exc:
                with self._lock:
                    failed_stage = job["stage"] or "Guarded workflow"
                    job["status"] = "failed"
                    job["stage"] = "Stopped"
                    job["command"] = ""
                    job["error"] = str(exc)
                    job["recovery"] = getattr(exc, "recovery", None)
                    job["log"].append(f"✕ {failed_stage} stopped\n{exc}")
                    while sum(len(item) for item in job["log"]) > 80_000:
                        job["log"].pop(0)
                    job["updatedAt"] = time.time()
            else:
                with self._lock:
                    job["status"] = "complete"
                    job["stage"] = "Complete"
                    job["command"] = ""
                    job["result"] = result
                    job["updatedAt"] = time.time()

        threading.Thread(target=worker, daemon=True).start()
        return {"jobId": job_id, "kind": kind, "status": "running"}

    def status(self, job_id):
        with self._lock:
            job = self._jobs.get(str(job_id or ""))
            if not job:
                raise PrototypeError(
                    "That workflow progress record is unavailable or expired. Refresh this workflow's status to continue.",
                    recovery={"kind": "expired-progress", "actions": ["retry-status"]},
                )
            return {
                **job,
                "log": list(job["log"]),
                "elapsedSeconds": max(0, int(time.time() - job["startedAt"])),
            }


class IndentedYamlDumper(yaml.SafeDumper):
    """Keep canonical nested list indentation used by lens-guidance source."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


class CameraLabLauncher:
    """Start or reuse the independent Camera Lab and open a saved profile."""

    def __init__(self, paths_or_root=PROJECT_ROOT):
        self.paths = (
            paths_or_root
            if hasattr(paths_or_root, "profile_pack")
            else ProjectPaths(paths_or_root)
        )
        self.root = self.paths.application_root
        self.start_script = self.root / "80 Build" / "scripts" / "start-camera-lab.sh"
        self.log_file = self.paths.local_workspace_dir / "Logs" / "R5 Camera Lab.log"

    @staticmethod
    def profile_url(profile_name):
        return f"{CAMERA_LAB_ORIGIN}/?profile={quote(profile_name)}"

    def _running_status(self):
        try:
            with urlopen(f"{CAMERA_LAB_ORIGIN}/api/camera-control/status", timeout=0.5) as response:
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError):
            return None
        if payload.get("ok") is not True or payload.get("backend_mode") not in {"edsdk", "simulated"}:
            return None
        return payload

    def _is_running(self):
        payload = self._running_status()
        return bool(
            payload
            and ((payload.get("app") or {}).get("profile_pack") or {}).get("pack_id")
            == self.paths.profile_pack.pack_id
        )

    @staticmethod
    def _open_url(url):
        result = subprocess.run(
            ["/usr/bin/open", "-a", "Google Chrome", url],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise PrototypeError("Camera Lab is running, but Google Chrome could not open it.")

    def launch(self, profile_name):
        url = self.profile_url(profile_name)
        running = self._running_status()
        if running:
            running_pack = ((running.get("app") or {}).get("profile_pack") or {})
            if running_pack.get("pack_id") != self.paths.profile_pack.pack_id:
                name = running_pack.get("pack_name") or "another profile pack"
                raise PrototypeError(
                    f"Camera Lab is already running with {name}. Stop it before opening "
                    f"{self.paths.profile_pack.pack_name}."
                )
            self._open_url(url)
            return {"url": url, "started": False, "reused": True}
        if not self.start_script.is_file() or not os.access(self.start_script, os.X_OK):
            raise PrototypeError(f"Camera Lab launcher is missing or not executable: {self.start_script}")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.log_file.open("ab") as log_handle:
            command = [str(self.start_script), "--profile", profile_name]
            if self.paths.profile_pack.mode == "external":
                command.extend(["--profile-pack", str(self.paths.profile_pack_root)])
            process = subprocess.Popen(
                command,
                cwd=self.root,
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if self._is_running():
                return {"url": url, "started": True, "reused": False}
            return_code = process.poll()
            if return_code is not None:
                raise PrototypeError(
                    f"Camera Lab could not start (status {return_code}). Review {self.log_file}."
                )
            time.sleep(0.1)
        raise PrototypeError(f"Camera Lab did not become ready. Review {self.log_file}.")


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
    def __init__(
        self,
        root=PROJECT_ROOT,
        source_validator=None,
        derived_artifact_checker=None,
        camera_lab_launcher=None,
        preflight_checker=None,
        finish_day_workflow=None,
        branch_integration_workflow=None,
        cleanup_review=None,
        publication_workflow=None,
        main_editor_launcher=None,
        camera_lab_journal_root=None,
        profile_pack_git_workflow=None,
        profile_pack_root=None,
        project_paths=None,
    ):
        if profile_pack_root is not None and project_paths is not None:
            raise ValueError("Choose profile_pack_root or project_paths, not both.")
        self.paths = project_paths or ProjectPaths(root, profile_pack_root=profile_pack_root)
        self.external_pack = self.paths.profile_pack.mode == "external"
        self.read_only = False
        self._profile_pack_fingerprint = self.paths.profile_pack.fingerprint()
        self.catalog_file = self.paths.root / "80 Build" / "profile_editor" / "canon_options.yaml"
        self.control_catalog_file = (
            self.paths.root / "80 Build" / "profile_editor" / "control_options.yaml"
        )
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
        self.lens_guidance, self.lens_equipment = load_lens_sources(self.paths)
        self.setting_order = self._setting_order()
        self.choices = self._choice_catalog()
        self._source_validator = source_validator or self._validate_project_sources
        self._derived_artifact_checker = derived_artifact_checker or self._inspect_derived_artifacts
        self._preflight_checker = preflight_checker or self._run_workflow_preflight
        self._pending_reviews = {}
        self._pending_migration_reviews = {}
        self._pending_color_reviews = {}
        self._pending_cx_reviews = {}
        self._pending_discard_reviews = {}
        self._pending_restore_reviews = {}
        self._pending_special_reviews = {}
        self._pending_profile_starter_reviews = {}
        self._write_lock = threading.RLock()
        self._build_lock = threading.Lock()
        self.guarded_jobs = GuardedJobManager()
        self.camera_lab_launcher = camera_lab_launcher or CameraLabLauncher(self.paths)
        self.finish_day_workflow = finish_day_workflow or FinishDayWorkflow(self.paths.root)
        self.branch_integration_workflow = branch_integration_workflow or BranchIntegrationWorkflow(self.paths.root)
        self.cleanup_review = cleanup_review or CleanupReview(self.paths.root)
        self.publication_workflow = publication_workflow or PublicationWorkflow(self.paths.root)
        self.main_editor_launcher = main_editor_launcher or MainEditorLauncher(self.paths.root)
        self.camera_lab_journal_root = camera_lab_journal_root
        self.profile_pack_git_workflow = profile_pack_git_workflow
        if self.external_pack and self.profile_pack_git_workflow is None:
            self.profile_pack_git_workflow = ProfilePackGitWorkflow(
                self.paths.root,
                self.paths.profile_pack_root,
                self.paths.profile_pack.pack_id,
            )

    def profile_starter_options(self):
        """Return official subject profiles that are absent from this pack."""
        if not self.external_pack:
            return {
                "available": [],
                "message": "Select a private profile pack before adding official profiles.",
            }
        active_ids = {
            str(profile.get("card_id") or "")
            for profile in self.profiles.values()
        }
        available = []
        for card_id, entry in self._official_profile_catalog().items():
            profile = entry["profile"]
            if card_id in active_ids:
                continue
            available.append(
                {
                    "cardId": card_id,
                    "title": str(profile.get("title") or entry["path"].stem),
                    "filename": entry["path"].name,
                }
            )
        available.sort(key=lambda item: item["title"].casefold())
        return {
            "available": available,
            "message": (
                "All official subject profiles are already in this pack."
                if not available
                else "Choose official profile starters to add to this pack."
            ),
        }

    def review_profile_starters(self, card_ids, pending_changes):
        if not self.external_pack:
            raise PrototypeError("Official profiles can be added only to a private profile pack.")
        try:
            pending = int(pending_changes)
        except (TypeError, ValueError) as exc:
            raise PrototypeError("Pending-change count must be an integer.") from exc
        if pending:
            raise PrototypeError("Save or discard every browser draft before adding profiles.")
        if (
            not isinstance(card_ids, list)
            or not card_ids
            or any(not isinstance(card_id, str) for card_id in card_ids)
        ):
            raise PrototypeError("Select at least one official profile to add.")
        if len(card_ids) != len(set(card_ids)):
            raise PrototypeError("Official profile selections must not contain duplicates.")

        catalog = self._official_profile_catalog()
        available_ids = {
            item["cardId"] for item in self.profile_starter_options()["available"]
        }
        unknown = sorted(set(card_ids) - available_ids)
        if unknown:
            raise PrototypeError(
                "Selected profiles are unavailable or already present: " + ", ".join(unknown)
            )
        selected = sorted(
            (catalog[card_id] for card_id in card_ids),
            key=lambda entry: str(entry["profile"].get("title") or "").casefold(),
        )
        existing_names = {path.name.casefold() for path in self.paths.profiles_dir.glob("*.yaml")}
        conflicts = [entry["path"].name for entry in selected if entry["path"].name.casefold() in existing_names]
        if conflicts:
            raise PrototypeError(
                "An existing pack file would be overwritten: " + ", ".join(conflicts)
            )

        profiles_relative = Path(self.paths.profile_pack_relative_source("profiles"))
        candidates = {
            (profiles_relative / entry["path"].name).as_posix(): entry["path"].read_bytes()
            for entry in selected
        }
        guidance_relative = self.paths.profile_pack_relative_source("profile_lens_guidance")
        guidance_path = self.paths.profile_lens_guidance_file
        guidance_before = guidance_path.read_bytes()
        guidance = load_yaml(guidance_path) or {}
        application_guidance_path = (
            self.paths.application_root / EMBEDDED_SOURCE_PATHS["profile_lens_guidance"]
        )
        application_guidance = load_yaml(application_guidance_path) or {}
        selected_ids = {entry["profile"]["card_id"] for entry in selected}
        existing_guidance_ids = {
            entry.get("card_id")
            for entry in guidance.get("profiles", []) or []
            if isinstance(entry, dict)
        }
        additions = [
            copy.deepcopy(entry)
            for entry in application_guidance.get("profiles", []) or []
            if isinstance(entry, dict)
            and entry.get("card_id") in selected_ids
            and entry.get("card_id") not in existing_guidance_ids
        ]
        if additions:
            guidance.setdefault("profiles", []).extend(additions)
        guidance_candidate = self._dump_lens_guidance(guidance)
        if guidance_candidate != guidance_before:
            candidates[guidance_relative] = guidance_candidate

        self._validate_profile_starter_candidates(candidates)
        diff_parts = []
        for relative, candidate in sorted(candidates.items()):
            target = self._source_path(relative)
            before = target.read_bytes() if target.exists() else b""
            diff_parts.append(
                "".join(
                    difflib.unified_diff(
                        before.decode("utf-8").splitlines(keepends=True),
                        candidate.decode("utf-8").splitlines(keepends=True),
                        fromfile=f"a/{relative}" if before else "/dev/null",
                        tofile=f"b/{relative}",
                    )
                )
            )
        review = {
            "created": time.monotonic(),
            "pack_fingerprint": self._profile_pack_fingerprint,
            "card_ids": [entry["profile"]["card_id"] for entry in selected],
            "profiles": [str(entry["profile"].get("title") or entry["path"].stem) for entry in selected],
            "candidates": candidates,
            "candidate_sha256": {
                relative: self._sha256(data) for relative, data in candidates.items()
            },
            "source_sha256": {
                str(entry["path"]): self._sha256(entry["path"].read_bytes())
                for entry in selected
            },
            "guidance_source_sha256": self._sha256(guidance_before),
            "application_guidance_sha256": self._sha256(application_guidance_path.read_bytes()),
            "application_guidance_path": application_guidance_path,
            "diff": "".join(diff_parts),
        }
        with self._write_lock:
            self._expire_profile_starter_reviews()
            while len(self._pending_profile_starter_reviews) >= MAX_PENDING_REVIEWS:
                oldest = min(
                    self._pending_profile_starter_reviews,
                    key=lambda key: self._pending_profile_starter_reviews[key]["created"],
                )
                del self._pending_profile_starter_reviews[oldest]
            token = secrets.token_urlsafe(24)
            self._pending_profile_starter_reviews[token] = review
        return {
            "reviewToken": token,
            "profiles": review["profiles"],
            "sourceFiles": sorted(candidates),
            "diff": review["diff"],
            "summary": f"Add {len(selected)} official profile starter{'s' if len(selected) != 1 else ''} to this private pack.",
        }

    def save_profile_starters(self, review_token, confirmed):
        if confirmed is not True:
            raise PrototypeError("Adding official profiles requires explicit confirmation.")
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed official-profile token is required.")
        with self._write_lock:
            self._expire_profile_starter_reviews()
            review = self._pending_profile_starter_reviews.pop(review_token, None)
            if review is None:
                raise ProfileConflictError(
                    "This official-profile review expired or was already used. Review again."
                )
            self.assert_profile_pack_current()
            if self._profile_pack_fingerprint != review["pack_fingerprint"]:
                raise ProfileConflictError("The private profile pack changed after review. Review again.")
            for source, expected_sha in review["source_sha256"].items():
                path = Path(source)
                if not path.is_file() or self._sha256(path.read_bytes()) != expected_sha:
                    raise ProfileConflictError("The application profile catalog changed after review. Review again.")
            application_guidance_path = review["application_guidance_path"]
            if self._sha256(application_guidance_path.read_bytes()) != review["application_guidance_sha256"]:
                raise ProfileConflictError("Application lens guidance changed after review. Review again.")
            guidance_relative = self.paths.profile_pack_relative_source("profile_lens_guidance")
            guidance_path = self.paths.profile_lens_guidance_file
            guidance_before = guidance_path.read_bytes()
            if self._sha256(guidance_before) != review["guidance_source_sha256"]:
                raise ProfileConflictError("Pack lens guidance changed after review. Review again.")
            for relative in review["candidates"]:
                if relative == guidance_relative:
                    continue
                if self._source_path(relative).exists():
                    raise ProfileConflictError(f"{relative} appeared after review. Nothing was overwritten.")
            for relative, candidate in review["candidates"].items():
                if self._sha256(candidate) != review["candidate_sha256"][relative]:
                    raise ProfileConflictError("The reviewed profile candidate is no longer valid.")
            self._validate_profile_starter_candidates(review["candidates"])
            backup = self._create_profile_starter_backup(review, guidance_before)
            written = []
            try:
                for relative, candidate in review["candidates"].items():
                    target = self._source_path(relative)
                    prior = target.read_bytes() if target.exists() else None
                    self._atomic_write(target, candidate, prior)
                    written.append((relative, prior))
                errors = self._source_validation_errors()
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_errors = []
                for relative, prior in reversed(written):
                    target = self._source_path(relative)
                    try:
                        if prior is None:
                            target.unlink(missing_ok=True)
                        else:
                            self._atomic_write(target, prior, target.read_bytes())
                    except Exception as rollback_exc:  # pragma: no cover
                        rollback_errors.append(f"{relative}: {rollback_exc}")
                if rollback_errors:
                    raise PrototypeError(
                        f"Profile addition failed and rollback was incomplete. Recovery backup: {backup}. "
                        + "; ".join(rollback_errors)
                    ) from exc
                raise PrototypeError(
                    f"Profile addition failed; prior pack source was restored. Recovery backup: {backup}. {exc}"
                ) from exc
            self._reload_profiles()
            return {
                "addedProfiles": review["profiles"],
                "sourceFiles": [relative for relative, _prior in written],
                "backup": str(backup),
                "validation": "passed",
            }

    def _official_profile_catalog(self):
        catalog = {}
        profiles_dir = self.paths.application_root / EMBEDDED_SOURCE_PATHS["profiles"]
        for path in sorted(profiles_dir.glob("*.yaml")):
            profile = load_yaml(path) or {}
            card_id = profile.get("card_id")
            if (
                isinstance(card_id, str)
                and profile.get("card_type", "profile") == "profile"
                and profile.get("display_category", "subject") == "subject"
            ):
                catalog[card_id] = {"path": path, "profile": profile}
        return catalog

    def _validate_profile_starter_candidates(self, candidates):
        from validators import lens_guidance_validator, profile_validator

        with tempfile.TemporaryDirectory(prefix="profile-editor-official-profiles-") as temporary:
            shadow = Path(temporary)
            for directory in ("00 Master", "10 Profiles", "50 Field Guide", "data"):
                (shadow / directory).mkdir(parents=True, exist_ok=True)
            for relative in (
                "00 Master/card_layout.yaml",
                "50 Field Guide/required_appendices.yaml",
            ):
                shutil.copy2(self.paths.root / relative, shadow / relative)
            shutil.copy2(self.paths.baseline_file, shadow / "00 Master" / "baseline.yaml")
            shutil.copy2(
                self.paths.owned_equipment_file,
                shadow / "data" / "stabilization_reference.yaml",
            )
            for source in discover_profiles(self.paths):
                shutil.copy2(source, shadow / "10 Profiles" / source.name)
            guidance_relative = self.paths.profile_pack_relative_source("profile_lens_guidance")
            guidance_candidate = candidates.get(
                guidance_relative,
                self.paths.profile_lens_guidance_file.read_bytes(),
            )
            (shadow / "00 Master" / "profile_lens_guidance.yaml").write_bytes(guidance_candidate)
            profiles_prefix = self.paths.profile_pack_relative_source("profiles").rstrip("/") + "/"
            for relative, data in candidates.items():
                if relative.startswith(profiles_prefix):
                    (shadow / "10 Profiles" / Path(relative).name).write_bytes(data)
            errors = [
                issue.message
                for validator in (profile_validator, lens_guidance_validator)
                for issue in validator.validate(shadow)
                if issue.level == "error"
            ]
            if errors:
                raise PrototypeError("Official profile candidate validation failed: " + "; ".join(errors))

    def _create_profile_starter_backup(self, review, guidance_before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base = self.paths.backups_dir / f"{timestamp}-profile-editor-add-official-profiles"
        backup = base
        counter = 2
        while backup.exists():
            backup = base.with_name(f"{base.name}-{counter}")
            counter += 1
        before_path = backup / "before" / "00 Master" / "profile_lens_guidance.yaml"
        before_path.parent.mkdir(parents=True)
        before_path.write_bytes(guidance_before)
        for relative, candidate in review["candidates"].items():
            target = backup / "candidate" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(candidate)
        (backup / "transaction.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "profile_pack": self._backup_pack_identity(),
                    "created": datetime.now().astimezone().isoformat(),
                    "operation": "add-official-profile-starters",
                    "card_ids": review["card_ids"],
                    "profiles": review["profiles"],
                    "candidate_sha256": review["candidate_sha256"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return backup

    def camera_lab_evidence_detail(self):
        try:
            return inspect_camera_lab_evidence(self.paths, journal_root=self.camera_lab_journal_root)
        except CameraLabTrackerImportError as exc:
            raise PrototypeError(str(exc)) from exc

    def review_camera_lab_evidence(self, candidate_ids, pending_changes):
        try:
            pending = int(pending_changes)
        except (TypeError, ValueError) as exc:
            raise PrototypeError("Pending-change count must be an integer.") from exc
        if pending:
            raise PrototypeError("Resolve every browser draft before reviewing Camera Lab evidence.")
        try:
            _before, candidate, applied = build_camera_lab_candidate_status(
                self.paths, candidate_ids, journal_root=self.camera_lab_journal_root
            )
        except CameraLabTrackerImportError as exc:
            raise PrototypeError(str(exc)) from exc
        relative = self.paths.profile_pack_relative_source("verification_status")
        return self._create_special_review(
            "camera-lab-evidence",
            {relative: self._dump_yaml(candidate)},
            f"Promote {len(applied)} exact Camera Lab evidence item{'s' if len(applied) != 1 else ''} into C1-C3 configured status.",
            {
                "applied": applied,
                "candidateIds": [item["candidateId"] for item in applied],
                "journalFingerprints": {
                    item["candidateId"]: item["journalSha256"] for item in applied
                },
            },
        )

    def save_camera_lab_evidence(self, review_token, confirmed):
        if confirmed is not True:
            raise PrototypeError("Camera Lab evidence import confirmation is required.")
        return self._save_special_review(review_token, "camera-lab-evidence")

    def control_editor_detail(self):
        controls = load_yaml(self.paths.controls_file) or {}
        catalog = load_yaml(self.control_catalog_file) or {}
        if not isinstance(catalog, dict):
            raise PrototypeError("Camera Buttons option catalog must be a mapping.")
        option_groups = {}
        for group in ("controls", "dials"):
            configured = catalog.get(group) or {}
            if not isinstance(configured, dict):
                raise PrototypeError(f"Camera Buttons option catalog {group} must be a mapping.")
            option_groups[group] = {}
            for row in controls.get(group) or []:
                control = row.get("control")
                options = copy.deepcopy(configured.get(control) or {})
                if not options.get("default") or not isinstance(options.get("assignment_options"), list):
                    raise PrototypeError(f"Camera Buttons option catalog is incomplete for {control}.")
                label = CARD_CONTROL_LABELS.get(control, control)
                options["displayLabel"] = label
                options["iconUrl"] = self._icon_url(control_reference_setting_key(label), None)
                option_groups[group][control] = options
        evidence = catalog.get("evidence_statuses") or {}
        return {
            "controls": copy.deepcopy(controls.get("controls") or []),
            "dials": copy.deepcopy(controls.get("dials") or []),
            "evidenceStatuses": sorted(CONTROL_EVIDENCE_STATUSES),
            "evidenceStatusOptions": [
                {
                    "value": value,
                    "label": (evidence.get(value) or {}).get("label", value),
                    "help": (evidence.get(value) or {}).get("help", ""),
                }
                for value in evidence
                if value in CONTROL_EVIDENCE_STATUSES
            ],
            "options": option_groups,
            "source": copy.deepcopy(catalog.get("source") or {}),
            "boundary": (
                "Edit only the existing control and dial assignments. C1-C3 assignments remain in "
                "Cx Foundation. Optional default buttons appear on the card automatically when customized. "
                "A changed confirmed behavior returns to pending camera verification."
            ),
        }

    def _candidate_control_sources(self, payload):
        if not isinstance(payload, dict):
            raise PrototypeError("Camera Buttons input must be an object.")
        controls_path = self.paths.controls_file
        current_path = self.paths.root / "data" / "canon_r5_custom_controls_current.yaml"
        controls = load_yaml(controls_path) or {}
        current = {} if self.external_pack else (load_yaml(current_path) or {})
        for group, current_group in (("controls", "buttons"), ("dials", "dials")):
            existing = controls.get(group) or []
            existing_current = current.get(current_group) or []
            current_by_control = {item.get("control"): item for item in existing_current}
            submitted = payload.get(group)
            if not isinstance(submitted, list) or len(submitted) != len(existing):
                raise PrototypeError(f"Camera Buttons {group} must keep every existing row in order.")
            rows = []
            for index, (saved, draft) in enumerate(zip(existing, submitted), start=1):
                if not isinstance(draft, dict) or draft.get("control") != saved.get("control"):
                    raise PrototypeError(f"Camera Buttons {group} row {index} changed its physical control identity.")
                row = copy.deepcopy(saved)
                for field in ("assignment", "operation"):
                    value = str(draft.get(field) or "").strip()
                    if field == "assignment" and not value:
                        raise PrototypeError(f"{saved['control']} requires an assignment.")
                    if value:
                        row[field] = value
                    else:
                        row.pop(field, None)
                info = draft.get("info_details") or draft.get("infoDetails") or {}
                if not isinstance(info, dict):
                    raise PrototypeError(f"{saved['control']} INFO details must be named values.")
                clean_info = {
                    str(key).strip(): str(value).strip()
                    for key, value in info.items()
                    if str(key).strip() and str(value).strip()
                }
                if clean_info:
                    row["info_details"] = clean_info
                else:
                    row.pop("info_details", None)
                note = str(draft.get("notes") or "").strip()
                if note:
                    row["notes"] = note
                else:
                    row.pop("notes", None)
                requested_status = str(draft.get("status") or "").strip()
                if requested_status not in CONTROL_EVIDENCE_STATUSES:
                    raise PrototypeError(f"{saved['control']} has an invalid evidence status.")
                behavior_changed = any(
                    row.get(field) != saved.get(field)
                    for field in ("assignment", "operation", "info_details")
                )
                row["status"] = (
                    "approved_target_pending_camera_verification"
                    if behavior_changed and saved.get("status") == "owner_confirmed"
                    else requested_status
                )
                rows.append(row)
            controls[group] = copy.deepcopy(rows)
            if not self.external_pack:
                current_rows = []
                for saved, row in zip(existing, rows):
                    current_row = copy.deepcopy(current_by_control.get(saved.get("control")) or saved)
                    for field in ("assignment", "operation", "status"):
                        if field in row:
                            current_row[field] = row[field]
                        else:
                            current_row.pop(field, None)
                    if row.get("info_details") != saved.get("info_details"):
                        current_row["info_details"] = {
                            str(key).casefold().replace(" ", "_"): value
                            for key, value in (row.get("info_details") or {}).items()
                        }
                        if not current_row["info_details"]:
                            current_row.pop("info_details", None)
                    if row.get("notes") != saved.get("notes"):
                        if row.get("notes"):
                            current_row["notes"] = row["notes"]
                        else:
                            current_row.pop("notes", None)
                    current_rows.append(current_row)
                current[current_group] = current_rows
        return controls, current

    def preview_control_editor(self, payload):
        controls, _current = self._candidate_control_sources(payload)
        profile = copy.deepcopy(self._profile("Camera Buttons"))
        return self._render_preview("Camera Buttons", profile, control_source=controls)

    def review_control_editor(self, payload):
        relative_controls = self.paths.profile_pack_relative_source("controls")
        controls_path = self.paths.controls_file
        current_path = self.paths.root / "data" / "canon_r5_custom_controls_current.yaml"
        controls, current = self._candidate_control_sources(payload)
        candidates = {
            relative_controls: self._replace_control_sections(
                controls_path.read_text(encoding="utf-8"), controls["controls"], controls["dials"], "controls"
            ).encode("utf-8"),
        }
        if not self.external_pack:
            candidates["data/canon_r5_custom_controls_current.yaml"] = self._replace_control_sections(
                current_path.read_text(encoding="utf-8"), current["buttons"], current["dials"], "buttons"
            ).encode("utf-8")
        return self._create_special_review(
            "camera-buttons",
            candidates,
            "Update the synchronized Camera Buttons assignments and evidence states.",
            {},
        )

    def save_control_editor(self, review_token):
        return self._save_special_review(review_token, "camera-buttons")

    def launch_camera_lab(self, profile_name):
        self.assert_profile_pack_current()
        name = self._validate_profile_name(profile_name)
        profile = self._profile(name)
        if is_reference_card(profile):
            raise PrototypeError("Camera Lab accepts saved Subject/Profile Cards, not reference cards.")
        return self.camera_lab_launcher.launch(name)

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
                    "cardId": profile.get("card_id"),
                    "title": profile.get("title", name),
                    "cardType": "reference" if reference else "profile",
                    "editableDraft": not reference,
                }
            )
        return sorted(items, key=lambda item: (item["cardType"] == "reference", item["title"].casefold()))

    def _lens_choice_catalog(self):
        accessories = {
            item.get("id"): item
            for item in self.lens_equipment.get("accessories") or []
            if isinstance(item, dict) and item.get("id")
        }
        catalog = []
        for lens in self.lens_equipment.get("lenses") or []:
            if not isinstance(lens, dict) or not lens.get("id"):
                continue
            compatible = [
                {
                    "id": accessory_id,
                    "name": accessory.get("name", accessory_id),
                    "displaySuffix": accessory.get("display_suffix", ""),
                }
                for accessory_id, accessory in accessories.items()
                if lens["id"] in (accessory.get("compatible_lens_ids") or [])
            ]
            catalog.append(
                {
                    "id": lens["id"],
                    "name": lens.get("short_name") or lens.get("name") or lens["id"],
                    "fullName": lens.get("name") or lens.get("short_name") or lens["id"],
                    "mount": lens.get("mount"),
                    "accessories": compatible,
                }
            )
        return catalog

    def _lens_choices_for_card_id(self, card_id):
        entry = next(
            (
                item
                for item in self.lens_guidance.get("profiles") or []
                if isinstance(item, dict) and item.get("card_id") == card_id
            ),
            None,
        )
        choices = []
        for choice in (entry or {}).get("choices") or []:
            choices.append(
                {
                    "lensId": choice.get("lens_id"),
                    "accessoryId": choice.get("accessory_id") or "",
                    "role": choice.get("role"),
                    "useWhen": choice.get("use_when", ""),
                    "fieldCheck": choice.get("field_check", ""),
                }
            )
        return choices

    def _clean_lens_choices(self, choices, *, required):
        if choices is None:
            choices = []
        if not isinstance(choices, list):
            raise PrototypeError("Lens choices must be a list.")
        if len(choices) > 3:
            raise PrototypeError("A card can list at most three lens choices.")
        if required and not choices:
            raise PrototypeError("A subject card requires at least one lens choice.")
        lenses = {
            item.get("id"): item
            for item in self.lens_equipment.get("lenses") or []
            if isinstance(item, dict)
        }
        accessories = {
            item.get("id"): item
            for item in self.lens_equipment.get("accessories") or []
            if isinstance(item, dict)
        }
        clean = []
        seen = set()
        for index, choice in enumerate(choices, start=1):
            if not isinstance(choice, dict):
                raise PrototypeError(f"Lens choice {index} must be an object.")
            lens_id = str(choice.get("lensId") or "")
            accessory_id = str(choice.get("accessoryId") or "")
            role = str(choice.get("role") or "")
            if lens_id not in lenses:
                raise PrototypeError(f"Lens choice {index} is not in the owned-lens catalog.")
            if role not in LENS_ROLES:
                raise PrototypeError(f"Lens choice {index} has an invalid role.")
            if accessory_id:
                accessory = accessories.get(accessory_id)
                if accessory is None or lens_id not in (accessory.get("compatible_lens_ids") or []):
                    raise PrototypeError(f"Lens choice {index} uses an incompatible accessory.")
            key = (lens_id, accessory_id)
            if key in seen:
                raise PrototypeError("The same lens and accessory combination cannot be listed twice.")
            seen.add(key)
            use_when = self._single_line(choice.get("useWhen"), "When to use", 240, required=True)
            field_check = self._single_line(choice.get("fieldCheck"), "Field check", 240, required=True)
            configured = {
                "lens_id": lens_id,
                "role": role,
                "use_when": use_when,
                "field_check": field_check,
            }
            if accessory_id:
                configured["accessory_id"] = accessory_id
            clean.append(configured)
        if required and sum(choice["role"] == "primary" for choice in clean) != 1:
            raise PrototypeError("A subject card requires exactly one primary lens choice.")
        return clean

    def _candidate_lens_guidance(self, profile, payload, operation, source_name):
        display_category = payload.get("displayCategory")
        required = display_category == "subject"
        choices = payload.get("lensChoices")
        if choices is None:
            if operation == "create":
                choices = []
            else:
                choices = self._lens_choices_for_card_id(self._profile(source_name).get("card_id"))
        clean = self._clean_lens_choices(choices, required=required)
        candidate = copy.deepcopy(self.lens_guidance)
        profiles = list(candidate.get("profiles") or [])
        if operation == "update" and source_name:
            source_card_id = self._profile(source_name).get("card_id")
            source_index = next(
                (index for index, item in enumerate(profiles) if item.get("card_id") == source_card_id),
                None,
            )
            replacement = {"card_id": profile.get("card_id"), "choices": clean}
            if required and source_index is not None:
                profiles[source_index] = replacement
            elif required:
                profiles.append(replacement)
            elif source_index is not None:
                profiles.pop(source_index)
        elif required:
            profiles.append({"card_id": profile.get("card_id"), "choices": clean})
        candidate["profiles"] = profiles
        return candidate

    def cx_foundation_detail(self, profile_name=None, assignments=None, flat_overrides=None):
        """Return global assignments and advisory fit for one shooting profile."""
        saved_assignments = self._cx_assignments()
        candidate_assignments = self._validate_cx_assignments(assignments or saved_assignments)
        shooting = [item for item in self.profile_list() if item["editableDraft"]]
        if not shooting:
            raise PrototypeError("No editable shooting profiles are available.")
        names = {item["name"] for item in shooting}
        if profile_name not in names:
            profile_name = shooting[0]["name"]
        profile = copy.deepcopy(self._profile(profile_name))
        if flat_overrides is not None:
            profile["overrides"] = nested_from_flat(self._validate_overrides(flat_overrides))
        setting_paths = self._card_setting_paths(profile)
        try:
            fit = analyze_foundation_fit(
                profile,
                self.profiles,
                self.baseline,
                setting_paths,
                candidate_assignments,
            )
        except CxRouteAnalysisError as exc:
            raise PrototypeError(str(exc)) from exc
        setup = ((profile.get("card") or {}).get("field_setup") or {})
        selected = str(setup.get("start") or "")
        return {
            "sourceFiles": (
                [
                    self.paths.profile_pack_relative_source("controls"),
                    self.paths.profile_pack_relative_source("registration_targets"),
                ]
                if self.external_pack
                else [
                    "controls.yaml",
                    "data/canon_r5_custom_controls_current.yaml",
                    "90 Testing/eos_r5_verification_tracker.yaml",
                ]
            ),
            "assignments": saved_assignments,
            "candidateAssignments": candidate_assignments,
            "profiles": shooting,
            "selectedProfile": profile_name,
            "selectedStart": selected if selected in {"C1", "C2", "C3"} else "",
            "fit": fit,
        }

    def review_cx_assignments(self, assignments):
        clean = self._validate_cx_assignments(assignments)
        candidates = self._cx_assignment_candidates(clean)
        return self._create_cx_review(
            candidates,
            f"Update C1-C3 assignments and synchronized routes ({len(candidates)} files).",
            "assignments",
        )

    def review_cx_selection(self, profile_name, start):
        if not isinstance(profile_name, str) or profile_name not in self.profiles:
            raise PrototypeError("Select an editable profile.")
        profile = copy.deepcopy(self._profile(profile_name))
        if is_reference_card(profile):
            raise PrototypeError("Reference cards cannot select a Cx foundation.")
        start = str(start or "").upper()
        if start not in {"", "C1", "C2", "C3"}:
            raise PrototypeError("Cx foundation must be C1, C2, C3, or No Cx.")
        setup = profile.setdefault("card", {}).setdefault("field_setup", {})
        if start:
            setup["start"] = start
            setup["source_card_id"] = self._card_id_for_title(self._cx_assignments()[start])
            setup.pop("access_only", None)
        else:
            setup.pop("start", None)
            setup.pop("source_card_id", None)
            if not setup:
                profile.get("card", {}).pop("field_setup", None)
        relative = f"10 Profiles/{profile_name}.yaml"
        return self._create_cx_review(
            {relative: self._dump_profile(profile)},
            f"Set {profile.get('title', profile_name)} card foundation to {start or 'No Cx'}.",
            "selection",
        )

    def save_cx_review(self, review_token):
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed Cx Foundation token is required.")
        with self._write_lock:
            self._expire_cx_reviews()
            review = self._pending_cx_reviews.pop(review_token, None)
            if review is None:
                raise ProfileConflictError(
                    "This Cx Foundation review expired or was already used. Review the current draft again."
                )
            before = {}
            for relative, expected_sha in review["source_sha256"].items():
                data = self._source_path(relative).read_bytes()
                if self._sha256(data) != expected_sha:
                    raise ProfileConflictError(
                        f"{relative} changed after review. Reload Cx Foundation and review again."
                    )
                before[relative] = data
            backup = self._create_cx_backup(review, before)
            written = []
            try:
                for relative, candidate in review["candidates"].items():
                    if self._sha256(candidate) != review["candidate_sha256"][relative]:
                        raise ProfileConflictError("The reviewed Cx Foundation candidate is no longer valid.")
                    if candidate == before[relative]:
                        continue
                    target = self._source_path(relative)
                    self._atomic_write(target, candidate, before[relative])
                    written.append(relative)
                errors = self._source_validation_errors()
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_errors = []
                for relative in reversed(written):
                    target = self._source_path(relative)
                    try:
                        self._atomic_write(target, before[relative], target.read_bytes())
                    except Exception as rollback_exc:  # pragma: no cover
                        rollback_errors.append(f"{relative}: {rollback_exc}")
                if rollback_errors:
                    raise PrototypeError(
                        f"Cx Foundation save failed and rollback was incomplete. Recovery backup: {backup}. "
                        + "; ".join(rollback_errors)
                    ) from exc
                raise PrototypeError(
                    f"Cx Foundation save failed; prior source was restored. Recovery backup: {backup}. {exc}"
                ) from exc
            self.verification_tracker = load_yaml(self.paths.verification_tracker_source_file) or {}
            self.registration = self.verification_tracker.get("registration") or {}
            self._reload_profiles()
            return {
                "sourceFiles": written,
                "backup": str(backup),
                "validation": "passed",
                "reviewKind": review["kind"],
                "assignments": self._cx_assignments(),
            }

    def _cx_assignments(self):
        controls = load_yaml(self.paths.controls_file) or {}
        modes = controls.get("custom_shooting_modes") or {}
        assignments = {}
        for start in ("C1", "C2", "C3"):
            card_id = str((modes.get(start) or {}).get("profile_id") or "").strip()
            try:
                name, profile = profile_by_id(self.profiles, card_id)
            except CardIdentityError as exc:
                raise PrototypeError(str(exc)) from exc
            assignments[start] = str(profile.get("title") or name)
        return assignments

    def _validate_cx_assignments(self, assignments):
        if not isinstance(assignments, dict):
            raise PrototypeError("C1-C3 assignments must be an object.")
        eligible = {
            profile.get("title", name)
            for name, profile in self.profiles.items()
            if not is_reference_card(profile)
        }
        clean = {}
        for start in ("C1", "C2", "C3"):
            title = assignments.get(start)
            if not isinstance(title, str) or title not in eligible:
                raise PrototypeError(f"{start} must identify an editable shooting profile.")
            clean[start] = title
        if len(set(clean.values())) != 3:
            raise PrototypeError("C1, C2, and C3 must use three different profiles.")
        return clean

    def _cx_assignment_candidates(self, assignments):
        relative_controls = self.paths.profile_pack_relative_source("controls")
        relative_current = "data/canon_r5_custom_controls_current.yaml"
        relative_tracker = self.paths.profile_pack_relative_source("registration_targets")
        controls_path = self.paths.controls_file
        current_path = self.paths.root / relative_current
        tracker_path = self.paths.registration_targets_file
        controls = load_yaml(controls_path) or {}
        current = load_yaml(current_path) or {}
        tracker = load_yaml(tracker_path) or {}
        old_assignments = self._cx_assignments()
        registration = tracker.setdefault("registration", {})
        profile_entries = registration.get("profiles") or []
        by_key = {str(item.get("key") or "").upper(): item for item in profile_entries if isinstance(item, dict)}
        for start, title in assignments.items():
            entry = by_key.get(start)
            if entry is None:
                raise PrototypeError(f"Registration tracker is missing {start.lower()}.")
            entry["heading"] = f"{start} {title}"
        replacements = {
            f"{start} {old_assignments[start]}": f"{start} {assignments[start]}"
            for start in ("C1", "C2", "C3")
            if old_assignments[start] != assignments[start]
        }
        tracker_text = tracker_path.read_text(encoding="utf-8")
        for start in ("C1", "C2", "C3"):
            if old_assignments[start] != assignments[start]:
                tracker_text = self._replace_tracker_assignment_labels(
                    tracker_text,
                    start,
                    old_assignments[start],
                    assignments[start],
                )
        for start, title in assignments.items():
            tracker_text = re.sub(
                rf"(^    - key: {start.lower()}\n      heading: ).*$",
                rf"\g<1>{title if title.startswith(start + ' ') else start + ' ' + title}",
                tracker_text,
                count=1,
                flags=re.MULTILINE,
            )
        candidates = {
            relative_controls: self._replace_cx_mode_assignments(
                controls_path.read_text(encoding="utf-8"), assignments, old_assignments
            ).encode("utf-8"),
            relative_tracker: tracker_text.encode("utf-8"),
        }
        if not self.external_pack:
            candidates[relative_current] = self._replace_cx_mode_assignments(
                current_path.read_text(encoding="utf-8"), assignments, old_assignments
            ).encode("utf-8")
        for name, profile in self.profiles.items():
            if is_reference_card(profile):
                continue
            candidate = copy.deepcopy(profile)
            setup = ((candidate.get("card") or {}).get("field_setup") or {})
            start = str(setup.get("start") or "").upper()
            if start not in assignments:
                continue
            setup["source_card_id"] = self._card_id_for_title(assignments[start])
            relative = f"10 Profiles/{name}.yaml"
            candidates[relative] = self._dump_profile(candidate)
        if self.external_pack:
            relative_status = self.paths.profile_pack_relative_source("verification_status")
            candidates[relative_status] = self._reconciled_verification_status_candidate(
                candidates[relative_tracker]
            )
        return candidates

    def _reconciled_verification_status_candidate(self, tracker_candidate, baseline_candidate=None):
        from verification_status import reconcile_status

        with tempfile.TemporaryDirectory(prefix="profile-editor-cx-status-") as temporary:
            root = Path(temporary)
            baseline = root / "baseline.yaml"
            tracker = root / "registration-targets.yaml"
            status = root / "verification-status.yaml"
            baseline.write_bytes(baseline_candidate or self.paths.baseline_file.read_bytes())
            tracker.write_bytes(tracker_candidate)
            status.write_bytes(self.paths.verification_status_file.read_bytes())
            reconcile_status(
                SimpleNamespace(
                    baseline_file=baseline,
                    verification_tracker_source_file=tracker,
                    verification_status_file=status,
                ),
                write=True,
            )
            return status.read_bytes()

    @staticmethod
    def _replace_tracker_assignment_labels(text, start, old_title, new_title):
        text = text.replace(f"{start} {old_title}", f"{start} {new_title}")
        for suffix in ("CONFIG", "REG", "READ", "OPS"):
            pattern = rf"(^  - test_id: {start}-{suffix}-01\n)(.*?)(?=^  - test_id:|^registration:)"
            match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
            if not match:
                raise PrototypeError(f"Cannot locate the {start}-{suffix} verification workflow block.")
            block = match.group(0).replace(old_title, new_title)
            if suffix == "OPS":
                block = re.sub(
                    r"(^    expected_result: )[^\n]*$",
                    rf"\g<1>{start} recalls the complete approved {new_title} registration target and controls behave as intended.",
                    block,
                    count=1,
                    flags=re.MULTILINE,
                )
            text = text[:match.start()] + block + text[match.end():]
        return text

    def _replace_cx_mode_assignments(self, text, assignments, old_assignments):
        changed_starts = []
        for start, title in assignments.items():
            if title == old_assignments.get(start):
                continue
            changed_starts.append(start)
            block_pattern = rf"(^  {start}:\n)(.*?)(?=^  C[123]:\n|^  notes:|^  restriction:)"
            match = re.search(block_pattern, text, flags=re.MULTILINE | re.DOTALL)
            if not match:
                raise PrototypeError(f"Cannot locate the {start} control mapping.")
            block = match.group(0)
            profile_id = self._card_id_for_title(title)
            block = re.sub(r"(^    profile_id: ).*$", rf"\g<1>{profile_id}", block, count=1, flags=re.MULTILINE)
            block = re.sub(r"(^    field_label: ).*$", rf"\g<1>{title}", block, count=1, flags=re.MULTILINE)
            block = re.sub(
                r"(^    status: ).*$",
                r"\g<1>approved_target_pending_camera_verification",
                block,
                count=1,
                flags=re.MULTILINE,
            )
            block = re.sub(r"^    unresolved_items:.*\n", "", block, flags=re.MULTILINE)
            text = text[:match.start()] + block + text[match.end():]
        for start in changed_starts:
            text = re.sub(
                rf"(^    {start}: ).*$",
                r"\g<1>approved_target_pending_camera_verification",
                text,
                count=1,
                flags=re.MULTILINE,
            )
        return text

    def _profile_by_title(self, title):
        try:
            return profile_by_title(self.profiles, title)[1]
        except CardIdentityError as exc:
            raise PrototypeError(str(exc)) from exc

    def _card_id_for_title(self, title):
        profile = self._profile_by_title(title)
        card_id = profile.get("card_id")
        if not isinstance(card_id, str) or not card_id:
            raise PrototypeError(f"Card is missing its immutable ID: {title}")
        return card_id

    def _create_cx_review(self, candidates, summary, kind):
        before = {relative: self._source_path(relative).read_bytes() for relative in candidates}
        changed = {relative: data for relative, data in candidates.items() if data != before[relative]}
        if not changed:
            raise PrototypeError("The Cx Foundation draft matches the saved source.")
        before = {relative: before[relative] for relative in changed}
        diff = "".join(
            "".join(
                difflib.unified_diff(
                    before[relative].decode("utf-8").splitlines(keepends=True),
                    candidate.decode("utf-8").splitlines(keepends=True),
                    fromfile=f"a/{relative}",
                    tofile=f"b/{relative}",
                )
            )
            for relative, candidate in changed.items()
        )
        review = {
            "created": time.monotonic(),
            "kind": kind,
            "candidates": changed,
            "source_sha256": {relative: self._sha256(data) for relative, data in before.items()},
            "candidate_sha256": {relative: self._sha256(data) for relative, data in changed.items()},
            "diff": diff,
        }
        with self._write_lock:
            self._expire_cx_reviews()
            token = secrets.token_urlsafe(24)
            self._pending_cx_reviews[token] = review
        if kind == "assignments":
            summary = f"Update C1-C3 assignments and synchronized routes ({len(changed)} files)."
        return {"reviewToken": token, "reviewKind": kind, "summary": summary, "diff": diff}

    def _create_cx_backup(self, review, before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base = self.paths.backups_dir / f"{timestamp}-profile-editor-cx-foundation"
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
            "profile_pack": self._backup_pack_identity(),
            "created": datetime.now().astimezone().isoformat(),
            "operation": f"cx-foundation-{review['kind']}",
            "source_sha256": review["source_sha256"],
            "candidate_sha256": review["candidate_sha256"],
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

    def _create_special_review(self, kind, candidates, summary, metadata):
        before = {relative: self._source_path(relative).read_bytes() for relative in candidates}
        changed = {relative: data for relative, data in candidates.items() if data != before[relative]}
        if not changed:
            raise PrototypeError("The reviewed changes already match the saved source.")
        self._validate_special_candidates(kind, changed)
        diff = "".join(
            "".join(
                difflib.unified_diff(
                    before[relative].decode("utf-8").splitlines(keepends=True),
                    candidate.decode("utf-8").splitlines(keepends=True),
                    fromfile=f"a/{relative}",
                    tofile=f"b/{relative}",
                )
            )
            for relative, candidate in changed.items()
        )
        review = {
            "created": time.monotonic(),
            "kind": kind,
            "candidates": changed,
            "source_sha256": {relative: self._sha256(before[relative]) for relative in changed},
            "candidate_sha256": {relative: self._sha256(data) for relative, data in changed.items()},
            "summary": summary,
            "diff": diff,
            "metadata": copy.deepcopy(metadata),
        }
        with self._write_lock:
            self._expire_special_reviews()
            while len(self._pending_special_reviews) >= MAX_PENDING_REVIEWS:
                oldest = min(
                    self._pending_special_reviews,
                    key=lambda key: self._pending_special_reviews[key]["created"],
                )
                del self._pending_special_reviews[oldest]
            token = secrets.token_urlsafe(24)
            self._pending_special_reviews[token] = review
        return {
            "reviewToken": token,
            "reviewKind": kind,
            "summary": summary,
            "sourceFiles": sorted(changed),
            "diff": diff,
            **copy.deepcopy(metadata),
        }

    def _save_special_review(self, review_token, expected_kind):
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed change token is required.")
        with self._write_lock:
            self._expire_special_reviews()
            review = self._pending_special_reviews.pop(review_token, None)
            if review is None or review.get("kind") != expected_kind:
                raise ProfileConflictError(
                    "This review expired, was already used, or belongs to another editor action. Review again."
                )
            before = {}
            for relative, expected_sha in review["source_sha256"].items():
                current = self._source_path(relative).read_bytes()
                if self._sha256(current) != expected_sha:
                    raise ProfileConflictError(f"{relative} changed after review. Reload and review again.")
                before[relative] = current
            if expected_kind == "camera-lab-evidence":
                try:
                    inventory = inspect_camera_lab_evidence(
                        self.paths, journal_root=self.camera_lab_journal_root
                    )
                except CameraLabTrackerImportError as exc:
                    raise ProfileConflictError(str(exc)) from exc
                if inventory.get("workbookBlocked"):
                    raise ProfileConflictError(inventory.get("workbookMessage") or "The tracker is blocked.")
                current = {
                    item["candidateId"]: item["journalSha256"]
                    for item in inventory.get("candidates") or []
                    if not item.get("alreadyImported")
                }
                expected = review["metadata"].get("journalFingerprints") or {}
                if any(current.get(candidate_id) != digest for candidate_id, digest in expected.items()):
                    raise ProfileConflictError("Camera Lab evidence changed after review. Review the current evidence again.")
            self._validate_special_candidates(expected_kind, review["candidates"])
            backup = self._create_special_backup(review, before)
            written = []
            try:
                for relative, candidate in review["candidates"].items():
                    if self._sha256(candidate) != review["candidate_sha256"][relative]:
                        raise ProfileConflictError("The reviewed candidate bytes are no longer valid.")
                    target = self._source_path(relative)
                    self._atomic_write(target, candidate, before[relative])
                    written.append(relative)
                if expected_kind == "camera-lab-evidence" and not self.external_pack:
                    from verification_status import build_working_copy

                    build_working_copy(self.paths)
                errors = self._source_validation_errors()
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_errors = []
                for relative in reversed(written):
                    target = self._source_path(relative)
                    try:
                        self._atomic_write(target, before[relative], target.read_bytes())
                    except Exception as rollback_exc:  # pragma: no cover
                        rollback_errors.append(f"{relative}: {rollback_exc}")
                if (
                    expected_kind == "camera-lab-evidence"
                    and not self.external_pack
                    and not rollback_errors
                ):
                    try:
                        from verification_status import build_working_copy

                        build_working_copy(self.paths)
                    except Exception as rollback_exc:  # pragma: no cover
                        rollback_errors.append(f"verification working copy: {rollback_exc}")
                if rollback_errors:
                    raise PrototypeError(
                        f"Save failed and rollback was incomplete. Recovery backup: {backup}. "
                        + "; ".join(rollback_errors)
                    ) from exc
                raise PrototypeError(
                    f"Save failed; prior source was restored. Recovery backup: {backup}. {exc}"
                ) from exc
            self.verification_tracker = load_yaml(self.paths.verification_tracker_source_file) or {}
            self.registration = self.verification_tracker.get("registration") or {}
            return {
                "sourceFiles": written,
                "backup": str(backup),
                "validation": "passed",
                "reviewKind": expected_kind,
                **copy.deepcopy(review["metadata"]),
            }

    def _validate_special_candidates(self, kind, candidates):
        for relative, data in candidates.items():
            try:
                loaded = yaml.safe_load(data.decode("utf-8"))
            except Exception as exc:
                raise PrototypeError(f"Candidate YAML is invalid for {relative}: {exc}") from exc
            if not isinstance(loaded, dict):
                raise PrototypeError(f"Candidate YAML must be a mapping: {relative}")
        with tempfile.TemporaryDirectory(prefix=f"profile-editor-{kind}-candidate-") as temporary:
            shadow = Path(temporary)
            if kind == "camera-buttons":
                if self.external_pack:
                    candidate = yaml.safe_load(candidates[self.paths.profile_pack_relative_source("controls")])
                    assigned = {
                        str((candidate.get("custom_shooting_modes") or {}).get(start, {}).get("profile_id") or "")
                        for start in ("C1", "C2", "C3")
                    }
                    known = {str(profile.get("card_id") or "") for profile in self.profiles.values()}
                    if "" in assigned or not assigned <= known or len(assigned) != 3:
                        raise PrototypeError("Camera Buttons candidate has invalid C1-C3 profile identities.")
                    return
                for directory in ("10 Profiles", "50 Field Guide", "WORKFLOWS", "90 Testing"):
                    source = self.paths.root / directory
                    destination = shadow / directory
                    if source.is_dir():
                        shutil.copytree(source, destination)
                for relative in (
                    "00 Master/baseline.yaml",
                    "controls.yaml",
                    "data/canon_r5_custom_controls_current.yaml",
                ):
                    destination = shadow / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(self.paths.root / relative, destination)
                for relative, data in candidates.items():
                    target = shadow / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                from validators import control_validator

                errors = [issue.message for issue in control_validator.validate(shadow) if issue.level == "error"]
            else:
                validation_sources = (
                    (self.paths.baseline_file, "00 Master/baseline.yaml"),
                    (
                        self.paths.verification_tracker_source_file,
                        "90 Testing/eos_r5_verification_tracker.yaml",
                    ),
                    (
                        self.paths.verification_status_file,
                        "90 Testing/eos_r5_verification_status.yaml",
                    ),
                )
                for source, relative in validation_sources:
                    destination = shadow / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                for relative, data in candidates.items():
                    target = (
                        shadow / "90 Testing/eos_r5_verification_status.yaml"
                        if relative == self.paths.profile_pack_relative_source("verification_status")
                        else shadow / relative
                    )
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                from validators import verification_status_validator

                errors = [
                    issue.message
                    for issue in verification_status_validator.validate(shadow)
                    if issue.level == "error"
                ]
            if errors:
                raise PrototypeError("Candidate validation failed: " + "; ".join(errors))

    def _create_special_backup(self, review, before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base = self.paths.backups_dir / f"{timestamp}-profile-editor-{review['kind']}"
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
            "profile_pack": self._backup_pack_identity(),
            "created": datetime.now().astimezone().isoformat(),
            "operation": review["kind"],
            "source_sha256": review["source_sha256"],
            "candidate_sha256": review["candidate_sha256"],
            "metadata": review["metadata"],
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

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
            relative: self._source_path(relative).read_bytes()
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
                data = self._source_path(relative).read_bytes()
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
                    target = self._source_path(relative)
                    if candidate != before[relative]:
                        self._atomic_write(target, candidate, before[relative])
                        written.append(relative)
                errors = self._source_validation_errors()
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_errors = []
                for relative in reversed(written):
                    target = self._source_path(relative)
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

    @staticmethod
    def _replace_control_sections(source, first_rows, dial_rows, first_key):
        def rendered(key, rows):
            return yaml.dump(
                {key: rows},
                Dumper=IndentedYamlDumper,
                sort_keys=False,
                allow_unicode=True,
                width=1000,
                default_flow_style=False,
            )

        first_pattern = rf"^{re.escape(first_key)}:\n.*?(?=^dials:\n)"
        dial_pattern = r"^dials:\n.*?(?=^custom_shooting_modes:\n)"
        updated, first_count = re.subn(
            first_pattern,
            rendered(first_key, first_rows) + "\n",
            source,
            count=1,
            flags=re.MULTILINE | re.DOTALL,
        )
        updated, dial_count = re.subn(
            dial_pattern,
            rendered("dials", dial_rows) + "\n",
            updated,
            count=1,
            flags=re.MULTILINE | re.DOTALL,
        )
        if first_count != 1 or dial_count != 1:
            raise PrototypeError("Cannot locate the canonical Camera Buttons source sections.")
        return updated

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
            "profile_pack": self._backup_pack_identity(),
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
                errors = self._source_validation_errors()
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
            "profile_pack": self._backup_pack_identity(),
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
        version_info = application_version_info(self.paths.root)
        return {
            "version": version_info["version"],
            "build": digest.hexdigest()[:8],
            "context_name": version_info["context_name"],
            "project_context": version_info["project_context"],
            "read_only": self.read_only,
            "pack_access": "guarded-write" if self.external_pack else "embedded",
            "application": {
                "project_id": "canon-eos-r5-camera-reference",
                "project_name": "Canon EOS R5 Camera Reference",
            },
            "profile_pack": {
                "mode": self.paths.profile_pack.mode,
                "pack_id": self.paths.profile_pack.pack_id,
                "pack_name": self.paths.profile_pack.pack_name,
                "fingerprint": self._profile_pack_fingerprint[:12],
            },
        }

    def assert_profile_pack_current(self):
        """Reject a moved, replaced, incompatible, or changed external pack."""
        if not self.external_pack:
            return
        try:
            current = resolve_profile_pack(
                self.paths.application_root,
                explicit_root=self.paths.profile_pack_root,
            )
            fingerprint = current.fingerprint()
        except ProfilePackError as exc:
            raise PrototypeError(f"Selected profile pack is no longer valid: {exc}") from exc
        if current.pack_id != self.paths.profile_pack.pack_id:
            raise PrototypeError("Selected profile-pack identity changed. Stop and select the intended pack again.")
        if fingerprint != self._profile_pack_fingerprint:
            raise PrototypeError("Selected profile-pack sources changed. Restart the editor to review the current pack.")

    def assert_mutation_allowed(self, endpoint):
        self.assert_profile_pack_current()
        if self.external_pack and endpoint not in EXTERNAL_PACK_EDITOR_ENDPOINTS:
            raise PrototypeError(
                "This action is outside the guarded external-pack editing boundary. "
                "Application Git, builds, spreadsheets, cleanup, integration, and publication remain disabled."
            )

    def accept_profile_pack_state(self):
        """Accept exact bytes written by one successful guarded transaction."""
        if self.external_pack:
            current = resolve_profile_pack(
                self.paths.application_root,
                explicit_root=self.paths.profile_pack_root,
            )
            if current.pack_id != self.paths.profile_pack.pack_id:
                raise PrototypeError("Selected profile-pack identity changed during the transaction.")
            self._profile_pack_fingerprint = current.fingerprint()

    def _backup_pack_identity(self):
        return profile_pack_revision(self.paths.profile_pack)

    def workflow_preflight(self):
        result = self._preflight_checker()
        if "recoveryActions" not in result:
            result["recoveryActions"] = self._preflight_recovery_actions(
                result.get("status"), result.get("output", "")
            )
        return result

    @staticmethod
    def _preflight_recovery_actions(status, output):
        if status != "blocked":
            return []
        text = str(output or "").casefold()
        actions = []
        if "git pull --ff-only" in text or "status: behind" in text:
            actions.append("pull-latest")
        if "import-verification-status" in text or "unimported" in text:
            actions.append("import-verification-tracker")
        if "build-all-spreadsheet-downloads" in text or "safely rebuildable" in text:
            actions.append("open-review-build")
        actions.append("retry-preflight")
        return list(dict.fromkeys(actions))

    def pull_latest(self, pending_changes, confirmed):
        try:
            pending = int(pending_changes)
        except (TypeError, ValueError) as exc:
            raise PrototypeError("Pending-change count must be an integer.") from exc
        if pending:
            raise PrototypeError("Resolve every browser draft before pulling remote changes.")
        if confirmed is not True:
            raise PrototypeError("Pulling the latest remote changes requires confirmation.")
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=self.paths.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if status.returncode:
            raise PrototypeError(status.stdout.strip() or "The working tree status could not be checked.")
        if status.stdout.strip():
            raise PrototypeError("The working tree is not clean. Review local changes before pulling.")
        branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=self.paths.root,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False,
        ).stdout.strip()
        upstream = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
            cwd=self.paths.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False,
        )
        if not branch or upstream.returncode or upstream.stdout.strip() != f"origin/{branch}":
            raise PrototypeError("The current branch must track its exact same-named origin branch before pulling.")
        fetched = subprocess.run(
            ["git", "fetch", "--prune", "origin"], cwd=self.paths.root,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10 * 60, check=False,
        )
        if fetched.returncode:
            raise PrototypeError("Origin could not be refreshed. Check the network and remote access, then retry.")
        counts = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}"],
            cwd=self.paths.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False,
        )
        if counts.returncode:
            raise PrototypeError(counts.stdout.strip() or "The local and remote branches could not be compared.")
        try:
            ahead, behind = (int(value) for value in counts.stdout.split())
        except (TypeError, ValueError) as exc:
            raise PrototypeError("The local and remote branch comparison was not understood.") from exc
        if ahead:
            raise PrototypeError("Local and remote histories are not a safe fast-forward. No pull was attempted.")
        if behind:
            pulled = subprocess.run(
                ["git", "pull", "--ff-only"], cwd=self.paths.root,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10 * 60, check=False,
            )
            if pulled.returncode:
                raise PrototypeError("Fast-forward pull did not complete.\n" + pulled.stdout[-80_000:].strip())
        return self.workflow_preflight()

    def _run_workflow_preflight(self):
        script = self.paths.root / "80 Build" / "scripts" / "preflight-git.sh"
        if not script.is_file() or not os.access(script, os.X_OK):
            raise PrototypeError(f"Preflight launcher is missing or not executable: {script}")
        try:
            completed = subprocess.run(
                [str(script)],
                cwd=self.paths.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=3 * 60,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise PrototypeError("Preflight timed out after 3 minutes.") from exc
        except OSError as exc:
            raise PrototypeError(f"Preflight could not start: {exc}") from exc
        output = completed.stdout[-80_000:].strip()
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        blocked_line = next(
            (line for line in lines if line.startswith(("PREFLIGHT BLOCKED:", "PREFLIGHT BLOCK:"))),
            None,
        )
        notice_line = next((line for line in lines if line.startswith("PREFLIGHT NOTICE:")), None)
        passed_line = next((line for line in lines if line.startswith("PREFLIGHT PASSED:")), None)
        if completed.returncode or blocked_line:
            status = "blocked"
            summary = blocked_line or "Preflight did not confirm that this project is safe to use."
        elif notice_line:
            status = "notice"
            summary = notice_line
        elif passed_line:
            status = "ready"
            summary = passed_line
        else:
            status = "notice"
            summary = "Preflight completed. Review its details before editing."
        return {
            "status": status,
            "summary": summary.removeprefix("PREFLIGHT PASSED: ")
            .removeprefix("PREFLIGHT NOTICE: ")
            .removeprefix("PREFLIGHT BLOCKED: ")
            .removeprefix("PREFLIGHT BLOCK: "),
            "output": output,
            "returnCode": completed.returncode,
        }

    def build_readiness(self, pending_changes):
        try:
            pending = int(pending_changes)
        except (TypeError, ValueError) as exc:
            raise PrototypeError("Pending-change count must be an integer.") from exc
        if pending < 0:
            raise PrototypeError("Pending-change count cannot be negative.")
        source_errors = self._source_validation_errors()
        derived_artifacts = self._derived_artifact_checker()
        blockers = []
        if pending:
            blockers.append(
                f"Resolve {pending} unsaved browser {('draft' if pending == 1 else 'drafts')} before building."
            )
        blockers.extend(source_errors)
        blockers.extend(derived_artifacts["blockers"])
        return {
            "ready": not blockers,
            "pendingChanges": pending,
            "sourceValidation": "passed" if not source_errors else "failed",
            "derivedArtifacts": derived_artifacts,
            "blockers": blockers,
        }

    def _inspect_derived_artifacts(self):
        verification_script = self.paths.root / "80 Build" / "verification_status.py"
        spreadsheet_script = self.paths.root / "80 Build" / "spreadsheet_downloads.py"
        if not verification_script.exists() and not spreadsheet_script.exists():
            # Minimal test fixtures do not include the workbook subsystem.
            return {"status": "current", "refreshNeeded": False, "details": [], "blockers": []}
        if not verification_script.is_file() or not spreadsheet_script.is_file():
            return {
                "status": "blocked",
                "refreshNeeded": False,
                "details": [],
                "blockers": ["Spreadsheet readiness cannot be checked because a required build script is missing."],
            }

        checks = (
            ("Verification", [sys.executable, str(verification_script), "check"], {0: "current", 2: "stale"}),
            ("Matrix/settings and Setup", [sys.executable, str(spreadsheet_script), "all", "diagnose"], {0: "current", 2: "stale"}),
        )
        details = []
        blockers = []
        refresh_needed = False
        for label, command, outcomes in checks:
            try:
                completed = subprocess.run(
                    command,
                    cwd=self.paths.root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=60,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                blockers.append(f"{label} spreadsheet readiness check failed: {exc}")
                continue
            output = completed.stdout.strip()
            outcome = outcomes.get(completed.returncode)
            if outcome == "stale":
                refresh_needed = True
                details.append(output or f"{label} artifacts require refresh.")
            elif outcome != "current":
                blockers.append(output or f"{label} spreadsheet readiness check failed.")

        return {
            "status": "blocked" if blockers else ("refresh-needed" if refresh_needed else "current"),
            "refreshNeeded": refresh_needed,
            "details": details,
            "blockers": blockers,
        }

    def run_local_build(self, pending_changes, confirmed, progress_callback=None):
        readiness = self.build_readiness(pending_changes)
        if not readiness["ready"]:
            raise PrototypeError("Local build is blocked: " + " ".join(readiness["blockers"]))
        if confirmed is not True:
            raise PrototypeError("Local build confirmation is required.")
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("A local build is already running.")
        commands = [
            ("Source validation", [sys.executable, "80 Build/validator.py", "--source-only"], 15 * 60),
        ]
        if readiness["derivedArtifacts"]["refreshNeeded"]:
            commands.append(
                (
                    "Spreadsheet refresh",
                    [str(self.paths.root / "80 Build" / "scripts" / "build-all-spreadsheet-downloads.sh")],
                    30 * 60,
                )
            )
        commands.extend(
            [
                ("Development build", [sys.executable, "80 Build/build.py"], 15 * 60),
                ("Full validation", [sys.executable, "80 Build/validator.py"], 15 * 60),
            ]
        )
        results = []
        try:
            for index, (label, command, timeout) in enumerate(commands, start=1):
                stage = f"{label} ({index} of {len(commands)})"
                command_text = "$ " + shlex.join(str(part) for part in command)
                if progress_callback:
                    progress_callback(stage, command=command_text)
                try:
                    completed = subprocess.run(
                        command,
                        cwd=self.paths.root,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired as exc:
                    if progress_callback:
                        progress_callback(stage, command=command_text, output=f"Timed out after {timeout // 60} minutes.")
                    raise PrototypeError(f"{label} timed out after {timeout // 60} minutes.") from exc
                output = completed.stdout[-80_000:]
                results.append({"step": label, "label": label, "status": "passed" if completed.returncode == 0 else "failed", "output": output})
                if completed.returncode:
                    if progress_callback:
                        progress_callback(stage, command=command_text, output=output or "Command failed without output.")
                    raise PrototypeError(
                        f"{label} failed.\n{output}",
                        recovery=numbers_resume_recovery(output, "resume-local-build"),
                    )
                if progress_callback:
                    progress_callback(stage, command=command_text, output=output or "(no output)", completed=True)
            return {"status": "passed", "steps": results}
        finally:
            self._build_lock.release()

    def finish_day_status(self, pending_changes):
        try:
            return self.finish_day_workflow.inspect(pending_changes)
        except FinishDayError as exc:
            raise PrototypeError(str(exc), recovery=getattr(exc, "recovery", None)) from exc

    def prepare_finish_day(
        self, pending_changes, confirmed, progress_callback=None, allow_spreadsheet_refresh=False
    ):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("A local build, tracker import, or Finish Day action is already running.")
        try:
            try:
                return self.finish_day_workflow.prepare(
                    pending_changes,
                    confirmed,
                    progress=progress_callback,
                    allow_spreadsheet_refresh=allow_spreadsheet_refresh,
                )
            except FinishDayError as exc:
                raise PrototypeError(str(exc), recovery=getattr(exc, "recovery", None)) from exc
        finally:
            self._build_lock.release()

    def commit_finish_day(self, review_token, message, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("A local build, tracker import, or Finish Day action is already running.")
        try:
            try:
                return self.finish_day_workflow.commit(review_token, message, confirmed)
            except FinishDayError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def push_finish_day(self, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("A local build, tracker import, or Finish Day action is already running.")
        try:
            try:
                return self.finish_day_workflow.push(confirmed)
            except FinishDayError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def _pack_git(self):
        if not self.external_pack or self.profile_pack_git_workflow is None:
            raise PrototypeError("Select a private profile pack before using its Git workflow.")
        return self.profile_pack_git_workflow

    def profile_pack_git_status(self, pending_changes):
        try:
            return self._pack_git().inspect(pending_changes)
        except ProfilePackGitError as exc:
            raise PrototypeError(str(exc)) from exc

    def review_profile_pack_git_commit(self, pending_changes):
        try:
            return self._pack_git().review_commit(pending_changes)
        except ProfilePackGitError as exc:
            raise PrototypeError(str(exc)) from exc

    def commit_profile_pack_git(self, review_token, message, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded Git action is already running.")
        try:
            try:
                return self._pack_git().commit(review_token, message, confirmed)
            except ProfilePackGitError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def review_profile_pack_git_remote(self, remote_url, pending_changes):
        try:
            return self._pack_git().review_remote(remote_url, pending_changes)
        except ProfilePackGitError as exc:
            raise PrototypeError(str(exc)) from exc

    def configure_profile_pack_git_remote(self, review_token, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded Git action is already running.")
        try:
            try:
                return self._pack_git().configure_remote(review_token, confirmed)
            except ProfilePackGitError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def start_configure_profile_pack_git_remote(self, review_token, confirmed):
        def action(progress):
            if not self._build_lock.acquire(blocking=False):
                raise PrototypeError("Another build or guarded Git action is already running.")
            try:
                try:
                    return self._pack_git().configure_remote(review_token, confirmed, progress=progress)
                except ProfilePackGitError as exc:
                    raise PrototypeError(str(exc)) from exc
            finally:
                self._build_lock.release()

        return self.guarded_jobs.start("profile-pack-remote", action)

    def push_profile_pack_git(self, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded Git action is already running.")
        try:
            try:
                return self._pack_git().push(confirmed)
            except ProfilePackGitError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def start_push_profile_pack_git(self, confirmed):
        def action(progress):
            if not self._build_lock.acquire(blocking=False):
                raise PrototypeError("Another build or guarded Git action is already running.")
            try:
                try:
                    return self._pack_git().push(confirmed, progress=progress)
                except ProfilePackGitError as exc:
                    raise PrototypeError(str(exc)) from exc
            finally:
                self._build_lock.release()

        return self.guarded_jobs.start("profile-pack-push", action)

    def branch_integration_status(self, pending_changes):
        try:
            return self.branch_integration_workflow.inspect(pending_changes)
        except BranchIntegrationError as exc:
            raise PrototypeError(str(exc), recovery=getattr(exc, "recovery", None)) from exc

    def prepare_branch_integration(
        self, pending_changes, confirmed, progress_callback=None, allow_spreadsheet_refresh=False
    ):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded Git action is already running.")
        try:
            try:
                return self.branch_integration_workflow.prepare(
                    pending_changes,
                    confirmed,
                    progress=progress_callback,
                    allow_spreadsheet_refresh=allow_spreadsheet_refresh,
                )
            except BranchIntegrationError as exc:
                raise PrototypeError(str(exc), recovery=getattr(exc, "recovery", None)) from exc
        finally:
            self._build_lock.release()

    def merge_branch_to_main(self, review_token, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded Git action is already running.")
        try:
            try:
                return self.branch_integration_workflow.merge_main(review_token, confirmed)
            except BranchIntegrationError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def push_integrated_main(self, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded Git action is already running.")
        try:
            try:
                return self.branch_integration_workflow.push_main(confirmed)
            except BranchIntegrationError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def resync_integrated_branch(self, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded Git action is already running.")
        try:
            try:
                return self.branch_integration_workflow.resync_branch(confirmed)
            except BranchIntegrationError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def start_finish_day_prepare(self, pending_changes, confirmed, allow_spreadsheet_refresh=False):
        return self.guarded_jobs.start(
            "finish-day-prepare",
            lambda progress: self.prepare_finish_day(
                pending_changes,
                confirmed,
                progress_callback=progress,
                allow_spreadsheet_refresh=allow_spreadsheet_refresh,
            ),
        )

    def start_local_build(self, pending_changes, confirmed):
        return self.guarded_jobs.start(
            "local-build",
            lambda progress: self.run_local_build(
                pending_changes, confirmed, progress_callback=progress
            ),
        )

    def start_branch_integration_prepare(
        self, pending_changes, confirmed, allow_spreadsheet_refresh=False
    ):
        return self.guarded_jobs.start(
            "branch-integration-prepare",
            lambda progress: self.prepare_branch_integration(
                pending_changes,
                confirmed,
                progress_callback=progress,
                allow_spreadsheet_refresh=allow_spreadsheet_refresh,
            ),
        )

    def publication_status(self, pending_changes, major_version=None):
        try:
            return self.publication_workflow.inspect(pending_changes, major_version)
        except PublicationWorkflowError as exc:
            raise PrototypeError(str(exc)) from exc

    def review_publication_notes(self, major_version, highlights):
        try:
            return self.publication_workflow.review_release_notes(major_version, highlights)
        except PublicationWorkflowError as exc:
            raise PrototypeError(str(exc)) from exc

    def save_publication_notes(self, review_token, confirmed):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded workflow action is already running.")
        try:
            try:
                return self.publication_workflow.save_release_notes(review_token, confirmed)
            except PublicationWorkflowError as exc:
                raise PrototypeError(str(exc)) from exc
        finally:
            self._build_lock.release()

    def review_publication(self, pending_changes, major_version, spreadsheet_mode):
        try:
            return self.publication_workflow.review_publication(
                pending_changes, major_version, spreadsheet_mode
            )
        except PublicationWorkflowError as exc:
            raise PrototypeError(str(exc)) from exc

    def publish_website(self, review_token, confirmed, progress_callback=None):
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("Another build or guarded workflow action is already running.")
        try:
            try:
                return self.publication_workflow.publish(
                    review_token, confirmed, progress=progress_callback
                )
            except PublicationWorkflowError as exc:
                raise PrototypeError(str(exc), recovery=getattr(exc, "recovery", None)) from exc
        finally:
            self._build_lock.release()

    def start_website_publication(self, review_token, confirmed):
        return self.guarded_jobs.start(
            "website-publication",
            lambda progress: self.publish_website(
                review_token, confirmed, progress_callback=progress
            ),
        )

    def launch_main_editor(self):
        try:
            return self.main_editor_launcher.launch()
        except PublicationWorkflowError as exc:
            raise PrototypeError(str(exc)) from exc

    def guarded_job_status(self, job_id):
        return self.guarded_jobs.status(job_id)

    def cleanup_status(self):
        return self.cleanup_review.inspect()

    def delete_cleanup_candidates(self, review_token, candidate_ids, confirmed):
        try:
            return self.cleanup_review.delete(review_token, candidate_ids, confirmed)
        except CleanupReviewError as exc:
            raise PrototypeError(str(exc)) from exc

    def import_verification_tracker(self, pending_changes, confirmed):
        try:
            pending = int(pending_changes)
        except (TypeError, ValueError) as exc:
            raise PrototypeError("Pending-change count must be an integer.") from exc
        if pending:
            raise PrototypeError("Resolve every unsaved browser draft before importing the verification tracker.")
        if confirmed is not True:
            raise PrototypeError("Verification tracker import confirmation is required.")
        if not self._build_lock.acquire(blocking=False):
            raise PrototypeError("A local build or tracker import is already running.")
        try:
            try:
                completed = subprocess.run(
                    [sys.executable, "80 Build/verification_status.py", "import"],
                    cwd=self.paths.root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=15 * 60,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise PrototypeError("Verification tracker import timed out after 15 minutes.") from exc
            output = completed.stdout[-80_000:]
            if completed.returncode:
                raise PrototypeError(f"Verification tracker import failed.\n{output}")
            return {"status": "passed", "output": output}
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
        if self.external_pack:
            relative_baseline = self.paths.profile_pack_relative_source("baseline")
            relative_status = self.paths.profile_pack_relative_source("verification_status")
            candidates[relative_status] = self._reconciled_verification_status_candidate(
                self.paths.registration_targets_file.read_bytes(),
                candidates.get(relative_baseline, self.paths.baseline_file.read_bytes()),
            )
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
                        target = self._source_path(relative)
                        self._atomic_write(target, review["candidates"][relative], before[relative])
                        written.append(relative)
                    errors = self._source_validation_errors()
                    if errors:
                        raise PrototypeError("Post-migration source validation failed: " + "; ".join(errors))
                except Exception as exc:
                    rollback_errors = []
                    for relative in reversed(written):
                        target = self._source_path(relative)
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
            target = self._source_path(relative)
            if not target.is_file():
                raise ProfileConflictError(f"Migration source no longer exists: {relative}")
            before[relative] = target.read_bytes()
        return before

    def _validate_migration_candidates(self, candidates):
        from validators import baseline_validator, profile_validator, yaml_validator

        with tempfile.TemporaryDirectory(prefix="baseline-migration-candidate-") as temporary:
            shadow = Path(temporary)
            shutil.copytree(self.paths.root / "00 Master", shadow / "00 Master")
            shutil.copytree(self.paths.profiles_dir, shadow / "10 Profiles")
            shutil.copytree(self.paths.root / "50 Field Guide", shadow / "50 Field Guide")
            shutil.copy2(self.paths.baseline_file, shadow / "00 Master" / "baseline.yaml")
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
            "profile_pack": self._backup_pack_identity(),
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
            if profile.get("reference_source") == "my_menu":
                reference_settings = my_menu_reference_settings(self.paths)
            elif profile.get("reference_source") == "controls":
                reference_settings = control_reference_settings(self.paths)
            else:
                reference_settings = profile.get("reference_settings") or []
            return {
                "name": name,
                "cardId": profile.get("card_id"),
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
                "card_id": str(uuid4()),
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
        profile["card_id"] = str(uuid4())
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
        lens_source_id = profile.get("card_id")
        if operation == "duplicate" and source_name:
            lens_source_id = self._profile(source_name).get("card_id")
        lens_choices = self._lens_choices_for_card_id(lens_source_id) if operation != "create" else []
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
            "cardId": profile.get("card_id"),
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
            "displayCategory": profile.get("display_category") or "subject",
            "discardBlockers": (
                self._profile_discard_blockers(name)
                if operation == "update" and name in self.profiles
                else []
            ),
            "sections": sections,
            "settingOrder": [path for path in self.setting_order if path in self.default_fields],
            "cardSettingPaths": self._card_setting_paths(profile),
            "originalOverrides": original,
            "lensChoices": lens_choices,
            "lensCatalog": self._lens_choice_catalog(),
            "lensGuidanceFingerprint": self._sha256(
                self.paths.profile_lens_guidance_file.read_bytes()
            ),
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
            "sourceFiles": [
                *([f"10 Profiles/{review['target_name']}.yaml"] if review["profile_changed"] else []),
                *(["00 Master/profile_lens_guidance.yaml"] if review["guidance_changed"] else []),
            ],
            "diff": review["diff"],
            "candidateYaml": review["candidate"].decode("utf-8"),
            "summary": review["summary"],
            "effectiveChanges": review["effective_changes"],
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
            self._validate_candidate(
                review["target_name"], review["candidate"], review["guidance_candidate"]
            )
            target = self._profile_path(review["target_name"])
            before = target.read_bytes() if target.exists() else None
            guidance_path = self.paths.profile_lens_guidance_file
            guidance_before = guidance_path.read_bytes()
            backup = self._create_transaction_backup(review, before, guidance_before)
            try:
                if review["profile_changed"]:
                    self._atomic_write(target, review["candidate"], before)
                if review["guidance_changed"]:
                    self._atomic_write(
                        guidance_path, review["guidance_candidate"], guidance_before
                    )
                errors = self._source_validation_errors()
                if errors:
                    raise PrototypeError("Post-save source validation failed: " + "; ".join(errors))
            except Exception as exc:
                rollback_error = None
                try:
                    if review["guidance_changed"]:
                        self._atomic_write(
                            guidance_path,
                            guidance_before,
                            guidance_path.read_bytes() if guidance_path.exists() else None,
                        )
                    if review["profile_changed"]:
                        if before is None:
                            target.unlink(missing_ok=True)
                        else:
                            self._atomic_write(
                                target, before, target.read_bytes() if target.exists() else None
                            )
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
                "sourceFiles": [
                    *([f"10 Profiles/{review['target_name']}.yaml"] if review["profile_changed"] else []),
                    *(["00 Master/profile_lens_guidance.yaml"] if review["guidance_changed"] else []),
                ],
                "backup": str(backup),
                "sourceFingerprint": self._profile_fingerprint(review["target_name"]),
                "validation": "passed",
            }

    def review_profile_removal(self, profile_name, source_fingerprint):
        profile = self._profile(profile_name)
        if is_reference_card(profile):
            raise PrototypeError("Reference cards cannot be moved to Deleted Cards.")
        if bool((profile.get("metadata") or {}).get("release", False)):
            raise PrototypeError("Only unreleased cards can be moved to Deleted Cards.")
        if source_fingerprint != self._profile_fingerprint(profile_name):
            raise ProfileConflictError("The profile changed after it was loaded. Reload it before removal.")
        blockers = self._profile_discard_blockers(profile_name)
        if blockers:
            raise PrototypeError("Resolve these structured references before removal: " + "; ".join(blockers))
        target = self._profile_path(profile_name)
        before = target.read_bytes()
        diff = "".join(
            difflib.unified_diff(
                before.decode("utf-8").splitlines(keepends=True),
                [],
                fromfile=f"a/10 Profiles/{profile_name}.yaml",
                tofile="/dev/null",
            )
        )
        review = {
            "created": time.monotonic(),
            "target_name": profile_name,
            "card_id": profile.get("card_id"),
            "title": str(profile.get("title") or profile_name),
            "source_fingerprint": source_fingerprint,
            "source_sha256": self._sha256(before),
            "diff": diff,
        }
        with self._write_lock:
            self._expire_discard_reviews()
            while len(self._pending_discard_reviews) >= MAX_PENDING_REVIEWS:
                oldest = min(
                    self._pending_discard_reviews,
                    key=lambda key: self._pending_discard_reviews[key]["created"],
                )
                del self._pending_discard_reviews[oldest]
            token = secrets.token_urlsafe(24)
            self._pending_discard_reviews[token] = review
        return {
            "reviewToken": token,
            "sourceFile": f"10 Profiles/{profile_name}.yaml",
            "summary": f"Move unreleased card {profile_name}.yaml to the recoverable Deleted Cards holding area.",
            "diff": diff,
            "narrativeMentions": self._profile_narrative_mentions(profile_name),
        }

    def save_profile_removal(self, review_token):
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed removal token is required.")
        with self._write_lock:
            self._expire_discard_reviews()
            review = self._pending_discard_reviews.pop(review_token, None)
            if review is None:
                raise ProfileConflictError("This removal review expired or was already used. Review it again.")
            name = review["target_name"]
            target = self._profile_path(name)
            if not target.is_file():
                raise ProfileConflictError("The profile no longer exists. Reload Profiles.")
            before = target.read_bytes()
            if self._sha256(before) != review["source_sha256"]:
                raise ProfileConflictError("The profile changed after review. Reload it and review again.")
            profile = self._profile(name)
            if bool((profile.get("metadata") or {}).get("release", False)):
                raise ProfileConflictError("The profile is now released and cannot be removed.")
            blockers = self._profile_discard_blockers(name)
            if blockers:
                raise ProfileConflictError(
                    "Profile dependencies changed after review: " + "; ".join(blockers)
                )
            backup = self._create_discard_backup(review, before)
            deleted = self._write_deleted_card(review, before)
            try:
                target.unlink()
                directory = os.open(target.parent, os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
                errors = self._source_validation_errors()
                if errors:
                    raise PrototypeError("Post-removal source validation failed: " + "; ".join(errors))
            except Exception as exc:
                try:
                    self._atomic_write(target, before, None)
                    self._remove_deleted_entry(deleted)
                except Exception as rollback_exc:  # pragma: no cover - catastrophic filesystem failure
                    raise PrototypeError(
                        f"Removal failed and automatic restore also failed. Recovery backup: {backup}. "
                        f"Removal error: {exc}. Restore error: {rollback_exc}"
                    ) from exc
                raise PrototypeError(
                    f"Removal failed; the active card was restored automatically. Recovery backup: {backup}. {exc}"
                ) from exc
            self._reload_profiles()
            return {
                "removedProfile": name,
                "cardId": review["card_id"],
                "sourceFile": f"10 Profiles/{name}.yaml",
                "deletedCard": str(deleted),
                "backup": str(backup),
                "validation": "passed",
            }

    def deleted_cards(self):
        root = self.paths.deleted_cards_dir
        if not root.is_dir():
            return []
        entries = []
        for folder in sorted(root.iterdir()):
            if not folder.is_dir():
                continue
            manifest_path = folder / "manifest.json"
            card_path = folder / "card.yaml"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                data = card_path.read_bytes()
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            recorded_pack = manifest.get("profile_pack") or {}
            if self.external_pack and recorded_pack.get("pack_id") != self.paths.profile_pack.pack_id:
                continue
            if self._sha256(data) != manifest.get("source_sha256"):
                continue
            entries.append(
                {
                    "cardId": manifest.get("card_id"),
                    "name": manifest.get("target_profile"),
                    "title": manifest.get("title"),
                    "removed": manifest.get("removed"),
                    "sourceFile": manifest.get("source_file"),
                }
            )
        return entries

    def review_profile_restore(self, card_id):
        folder, manifest, data = self._deleted_card_entry(card_id)
        name = manifest["target_profile"]
        target = self._profile_path(name)
        if target.exists():
            raise ProfileConflictError(f"Cannot restore because 10 Profiles/{name}.yaml already exists.")
        if any(profile.get("card_id") == card_id for profile in self.profiles.values()):
            raise ProfileConflictError(f"Cannot restore because card_id is already active: {card_id}")
        self._validate_candidate(name, data)
        diff = "".join(
            difflib.unified_diff(
                [],
                data.decode("utf-8").splitlines(keepends=True),
                fromfile="/dev/null",
                tofile=f"b/10 Profiles/{name}.yaml",
            )
        )
        review = {
            "created": time.monotonic(),
            "card_id": card_id,
            "target_name": name,
            "deleted_folder": str(folder),
            "source_sha256": self._sha256(data),
            "candidate": data,
            "diff": diff,
        }
        with self._write_lock:
            self._expire_restore_reviews()
            token = secrets.token_urlsafe(24)
            self._pending_restore_reviews[token] = review
        return {
            "reviewToken": token,
            "summary": f"Restore {name}.yaml from Deleted Cards to active project source.",
            "sourceFile": f"10 Profiles/{name}.yaml",
            "diff": diff,
        }

    def save_profile_restore(self, review_token):
        if not isinstance(review_token, str) or not review_token:
            raise PrototypeError("A reviewed restore token is required.")
        with self._write_lock:
            self._expire_restore_reviews()
            review = self._pending_restore_reviews.pop(review_token, None)
            if review is None:
                raise ProfileConflictError("This restore review expired or was already used. Review it again.")
            folder, manifest, data = self._deleted_card_entry(review["card_id"])
            if str(folder) != review["deleted_folder"] or self._sha256(data) != review["source_sha256"]:
                raise ProfileConflictError("The Deleted Cards entry changed after review.")
            name = review["target_name"]
            target = self._profile_path(name)
            if target.exists() or any(profile.get("card_id") == review["card_id"] for profile in self.profiles.values()):
                raise ProfileConflictError("The restore target or card identity is now in use.")
            backup = self._create_restore_backup(review, data)
            try:
                self._atomic_write(target, data, None)
                errors = self._source_validation_errors()
                if errors:
                    raise PrototypeError("Post-restore source validation failed: " + "; ".join(errors))
            except Exception as exc:
                if target.exists():
                    target.unlink()
                raise PrototypeError(
                    f"Restore failed; Deleted Cards remains unchanged. Recovery backup: {backup}. {exc}"
                ) from exc
            cleanup_warning = None
            try:
                self._remove_deleted_entry(folder)
            except Exception as exc:  # Keep the validated active source if holding-area cleanup fails.
                cleanup_warning = (
                    "The card was restored and validated, but its recoverable holding copy could not be "
                    f"removed: {exc}"
                )
            self._reload_profiles()
            result = {
                "restoredProfile": name,
                "cardId": review["card_id"],
                "sourceFile": f"10 Profiles/{name}.yaml",
                "backup": str(backup),
                "validation": "passed",
            }
            if cleanup_warning:
                result["warning"] = cleanup_warning
            return result

    def preview_draft(self, payload):
        profile, target_name, operation, source_name, _fingerprint = self._candidate_profile(payload)
        guidance = self._candidate_lens_guidance(profile, payload, operation, source_name)
        return self._render_preview(target_name, profile, guidance)

    def _prepare_review(self, payload):
        profile, target_name, operation, source_name, source_fingerprint = self._candidate_profile(payload)
        candidate = self._dump_profile(profile)
        guidance_path = self.paths.profile_lens_guidance_file
        guidance_before = guidance_path.read_bytes()
        guidance_source_sha256 = payload.get("lensGuidanceFingerprint")
        if not isinstance(guidance_source_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", guidance_source_sha256
        ):
            raise PrototypeError("The lens-guidance source fingerprint is missing or invalid.")
        if self._sha256(guidance_before) != guidance_source_sha256:
            raise ProfileConflictError(
                "Lens guidance changed after this profile was loaded. Reload the profile and review again."
            )
        guidance_data = self._candidate_lens_guidance(profile, payload, operation, source_name)
        guidance_candidate = self._dump_lens_guidance(guidance_data)
        self._confirm_target_state(operation, source_name, target_name, source_fingerprint)
        self._validate_candidate(target_name, candidate, guidance_candidate)
        target = self._profile_path(target_name)
        before = target.read_text(encoding="utf-8") if target.exists() else ""
        before_label = f"a/10 Profiles/{target_name}.yaml" if before else "/dev/null"
        profile_diff = "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                candidate.decode("utf-8").splitlines(keepends=True),
                fromfile=before_label,
                tofile=f"b/10 Profiles/{target_name}.yaml",
            )
        )
        guidance_diff = "".join(
            difflib.unified_diff(
                guidance_before.decode("utf-8").splitlines(keepends=True),
                guidance_candidate.decode("utf-8").splitlines(keepends=True),
                fromfile="a/00 Master/profile_lens_guidance.yaml",
                tofile="b/00 Master/profile_lens_guidance.yaml",
            )
        )
        diff = profile_diff + guidance_diff
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
            "profile_changed": bool(profile_diff),
            "guidance_candidate": guidance_candidate,
            "guidance_candidate_sha256": self._sha256(guidance_candidate),
            "guidance_source_sha256": guidance_source_sha256,
            "guidance_changed": bool(guidance_diff),
            "diff": diff,
            "summary": (
                f"Update lens choices for {target_name}."
                if guidance_diff and not profile_diff
                else self._review_summary(operation, source_name, target_name)
            ),
            "effective_changes": self._effective_setting_changes(operation, source_name, profile),
        }

    def _effective_setting_changes(self, operation, source_name, candidate_profile):
        """Describe effective before/after values represented by this exact review."""
        if operation == "create" or not source_name:
            return []
        source_profile = self._profile(source_name)
        source_overrides = flatten(source_profile.get("overrides") or {})
        candidate_overrides = flatten(candidate_profile.get("overrides") or {})
        before = flatten(merge(self.defaults, source_profile.get("overrides") or {}))
        after = flatten(merge(self.defaults, candidate_profile.get("overrides") or {}))
        changes = []
        for path in self.setting_order:
            if path not in self.default_fields or same_value(before.get(path), after.get(path)):
                continue
            changes.append(
                {
                    "path": path,
                    "label": self._catalog_value(path, "label", friendly_label(path)),
                    "beforeValue": json_value(before.get(path)),
                    "beforeDisplay": self._review_value_display(before.get(path)),
                    "beforeSource": "profile customization" if path in source_overrides else "baseline",
                    "afterValue": json_value(after.get(path)),
                    "afterDisplay": self._review_value_display(after.get(path)),
                    "afterSource": "profile customization" if path in candidate_overrides else "inherited from baseline",
                }
            )
        return changes

    @staticmethod
    def _review_value_display(value):
        if value == "":
            return "Blank"
        if value is None:
            return "Not set"
        if isinstance(value, bool):
            return "True" if value else "False"
        return str(value)

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
        display_category = payload.get("displayCategory")
        if display_category not in DISPLAY_CATEGORIES:
            raise PrototypeError("Card section must be Subjects or Camera Setup & Controls.")

        source_profile_snapshot = None
        if operation == "create":
            if source_name not in {None, ""} or source_fingerprint not in {None, ""}:
                raise PrototypeError("A baseline-derived profile must not identify a source profile.")
            profile = {
                "card_id": str(uuid4()),
                "metadata": self._new_profile_metadata(),
                "title": title,
                "inherits": "baseline",
                "overrides": nested_from_flat(clean_overrides),
            }
        else:
            if not isinstance(source_name, str) or not source_name:
                raise PrototypeError("The source profile is required.")
            source = copy.deepcopy(self._profile(source_name))
            source_profile_snapshot = copy.deepcopy(source)
            if is_reference_card(source):
                raise PrototypeError("Reference cards remain read-only.")
            if not isinstance(source_fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", source_fingerprint):
                raise PrototypeError("The source profile fingerprint is missing or invalid.")
            if operation == "update" and target_name != source_name:
                raise PrototypeError("Renaming an existing profile is not available in Stage 2.")
            profile = source
            if operation == "duplicate":
                profile["card_id"] = str(uuid4())
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
            profile["title"] = title
            profile["inherits"] = "baseline"
            profile["overrides"] = nested_from_flat(clean_overrides)
        if display_category == "reference":
            profile["display_category"] = "reference"
        else:
            profile.pop("display_category", None)
        if subtitle:
            profile["subtitle"] = subtitle
        else:
            profile.pop("subtitle", None)
        if operation != "update" or profile != source_profile_snapshot:
            self._synchronize_profile_my_menu_cues(profile)
        if operation == "update" and profile != source_profile_snapshot:
            profile.setdefault("metadata", {})["last_updated"] = date.today()
        return profile, target_name, operation, source_name or None, source_fingerprint or None

    def _synchronize_profile_my_menu_cues(self, profile):
        """Match this card's visible setting cues to the persisted My Menu layout."""
        merged = merge(self.defaults, profile.get("overrides") or {})
        visible = set(displayed_card_setting_paths(profile, merged, self.paths))
        route_catalog = self._my_menu_route_catalog()
        desired = []
        for tab in used_tabs(self.my_menu):
            item_ids = set(tab.get("items") or [])
            settings = [
                path
                for path in self.setting_order
                if path in visible and route_catalog.get(path) in item_ids
            ]
            if settings:
                desired.append({"name": tab["name"], "settings": settings})

        card = profile.get("card")
        setup = card.get("field_setup") if isinstance(card, dict) else None
        if desired:
            if not isinstance(card, dict):
                card = profile.setdefault("card", {})
            if not isinstance(setup, dict):
                setup = card.setdefault("field_setup", {})
            setup["my_menus"] = desired
            if (
                profile.get("display_category") == "reference"
                and not setup.get("start")
                and not setup.get("source_card_id")
            ):
                setup["access_only"] = True
            return

        if not isinstance(setup, dict):
            return
        setup.pop("my_menus", None)
        if setup.get("access_only") is True and not setup.get("start") and not setup.get("source_card_id"):
            setup.pop("access_only", None)
        if not setup:
            card.pop("field_setup", None)
        if isinstance(card, dict) and not card:
            profile.pop("card", None)

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
        guidance_path = self.paths.profile_lens_guidance_file
        if self._sha256(guidance_path.read_bytes()) != review["guidance_source_sha256"]:
            raise ProfileConflictError(
                "Lens guidance changed after review. Reload the profile and review again."
            )
        if self._sha256(review["guidance_candidate"]) != review["guidance_candidate_sha256"]:
            raise ProfileConflictError("The reviewed lens-guidance candidate is no longer valid.")

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

    def _validate_candidate(self, target_name, candidate, guidance_candidate=None):
        from validators import lens_guidance_validator, profile_validator
        from validators.common import load_yaml_checked

        with tempfile.TemporaryDirectory(prefix="profile-editor-candidate-") as temporary:
            shadow = Path(temporary)
            (shadow / "00 Master").mkdir(parents=True)
            (shadow / "10 Profiles").mkdir()
            (shadow / "50 Field Guide").mkdir()
            (shadow / "data").mkdir()
            for relative in (
                "00 Master/baseline.yaml",
                "00 Master/card_layout.yaml",
                "50 Field Guide/required_appendices.yaml",
            ):
                source = self.paths.baseline_file if relative == "00 Master/baseline.yaml" else self.paths.root / relative
                destination = shadow / relative
                shutil.copy2(source, destination)
            shutil.copy2(
                self.paths.owned_equipment_file,
                shadow / "data" / "stabilization_reference.yaml",
            )
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
            if guidance_candidate is not None:
                (shadow / "00 Master" / "profile_lens_guidance.yaml").write_bytes(
                    guidance_candidate
                )
                errors.extend(
                    issue.message
                    for issue in lens_guidance_validator.validate(shadow)
                    if issue.level == "error"
                )
            if errors:
                raise PrototypeError("Candidate profile validation failed: " + "; ".join(errors))

    def _create_transaction_backup(self, review, before, guidance_before):
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
        if review["guidance_changed"]:
            guidance_before_dir = backup / "before" / "00 Master"
            guidance_candidate_dir = backup / "candidate" / "00 Master"
            guidance_before_dir.mkdir(parents=True)
            guidance_candidate_dir.mkdir(parents=True)
            (guidance_before_dir / "profile_lens_guidance.yaml").write_bytes(guidance_before)
            (guidance_candidate_dir / "profile_lens_guidance.yaml").write_bytes(
                review["guidance_candidate"]
            )
        manifest = {
            "version": 1,
            "profile_pack": self._backup_pack_identity(),
            "created": datetime.now().astimezone().isoformat(),
            "operation": review["operation"],
            "source_profile": review["source_name"],
            "source_fingerprint": review["source_fingerprint"],
            "target_profile": review["target_name"],
            "target_existed": before is not None,
            "candidate_sha256": review["candidate_sha256"],
            "lens_guidance_changed": review["guidance_changed"],
            "lens_guidance_source_sha256": review["guidance_source_sha256"],
            "lens_guidance_candidate_sha256": review["guidance_candidate_sha256"],
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

    def _create_discard_backup(self, review, before):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", review["target_name"]).strip("-").lower()
        base = self.paths.backups_dir / f"{timestamp}-profile-editor-discard-{safe_name}"
        backup = base
        counter = 2
        while backup.exists():
            backup = base.with_name(f"{base.name}-{counter}")
            counter += 1
        before_dir = backup / "before" / "10 Profiles"
        before_dir.mkdir(parents=True)
        (before_dir / f"{review['target_name']}.yaml").write_bytes(before)
        manifest = {
            "version": 1,
            "profile_pack": self._backup_pack_identity(),
            "created": datetime.now().astimezone().isoformat(),
            "operation": "move_unreleased_profile_to_deleted_cards",
            "card_id": review["card_id"],
            "target_profile": review["target_name"],
            "source_sha256": review["source_sha256"],
            "recovery": f"Restore before/10 Profiles/{review['target_name']}.yaml to 10 Profiles/.",
        }
        (backup / "transaction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return backup

    def _write_deleted_card(self, review, data):
        root = self.paths.deleted_cards_dir.resolve()
        root.mkdir(parents=True, exist_ok=True)
        target = (root / review["card_id"]).resolve()
        if target.parent != root:
            raise PrototypeError("Deleted Cards identity path is invalid.")
        if target.exists():
            raise ProfileConflictError("This card already has a Deleted Cards entry.")
        temporary = Path(tempfile.mkdtemp(prefix=".card-", dir=root))
        try:
            (temporary / "card.yaml").write_bytes(data)
            manifest = {
                "version": 1,
                "profile_pack": self._backup_pack_identity(),
                "card_id": review["card_id"],
                "title": review["title"],
                "target_profile": review["target_name"],
                "source_file": f"10 Profiles/{review['target_name']}.yaml",
                "source_sha256": review["source_sha256"],
                "removed": datetime.now().astimezone().isoformat(),
                "recovery": "Use Profile Editor → Deleted Cards → Restore.",
            }
            (temporary / "manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            os.replace(temporary, target)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
        return target

    def _deleted_card_entry(self, card_id):
        if not valid_card_id(card_id):
            raise PrototypeError("Select a valid Deleted Cards entry.")
        root = self.paths.deleted_cards_dir.resolve()
        folder = (root / card_id).resolve()
        if folder.parent != root or not folder.is_dir():
            raise PrototypeError("Deleted Cards entry was not found.")
        try:
            manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
            data = (folder / "card.yaml").read_bytes()
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise PrototypeError("Deleted Cards entry is incomplete or unreadable.") from exc
        recorded_pack = manifest.get("profile_pack") or {}
        if self.external_pack and recorded_pack.get("pack_id") != self.paths.profile_pack.pack_id:
            raise ProfileConflictError("Deleted Cards entry belongs to a different profile pack.")
        if manifest.get("card_id") != card_id or self._sha256(data) != manifest.get("source_sha256"):
            raise ProfileConflictError("Deleted Cards integrity check failed.")
        name = manifest.get("target_profile")
        if not isinstance(name, str) or self._validate_profile_name(name) != name:
            raise ProfileConflictError("Deleted Cards restore target is invalid.")
        return folder, manifest, data

    def _remove_deleted_entry(self, folder):
        root = self.paths.deleted_cards_dir.resolve()
        folder = Path(folder).resolve()
        if folder.parent != root or not folder.is_dir():
            raise PrototypeError("Refusing to remove an invalid Deleted Cards path.")
        shutil.rmtree(folder)

    def _create_restore_backup(self, review, data):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", review["target_name"]).strip("-").lower()
        backup = self.paths.backups_dir / f"{timestamp}-profile-editor-restore-{safe_name}"
        counter = 2
        while backup.exists():
            backup = self.paths.backups_dir / f"{timestamp}-profile-editor-restore-{safe_name}-{counter}"
            counter += 1
        source_dir = backup / "deleted-card"
        source_dir.mkdir(parents=True)
        (source_dir / f"{review['target_name']}.yaml").write_bytes(data)
        (backup / "transaction.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "profile_pack": self._backup_pack_identity(),
                    "created": datetime.now().astimezone().isoformat(),
                    "operation": "restore_profile_from_deleted_cards",
                    "card_id": review["card_id"],
                    "target_profile": review["target_name"],
                    "source_sha256": review["source_sha256"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
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
    def _dump_lens_guidance(guidance):
        rendered = yaml.dump(
            guidance,
            Dumper=IndentedYamlDumper,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
            default_flow_style=False,
        )
        rendered = rendered.replace(
            "schema_version: 1\ncamera:", "schema_version: 1\n\ncamera:"
        ).replace("  model: EOS R5\nprofiles:", "  model: EOS R5\n\nprofiles:")
        parts = rendered.split("\n  - card_id:")
        rendered = parts[0] + "".join(
            ("\n" if index > 1 else "") + "\n  - card_id:" + part
            for index, part in enumerate(parts[1:], start=1)
        )
        return rendered.encode("utf-8")

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
        self.lens_guidance, self.lens_equipment = load_lens_sources(self.paths)
        self.choices = self._choice_catalog()

    def _reload_project_data(self):
        self.baseline = load_baseline(self.paths)
        self.defaults = self.baseline.get("defaults") or {}
        self.default_fields = flatten(self.defaults)
        self.profiles = self._load_profiles()
        self.lens_guidance, self.lens_equipment = load_lens_sources(self.paths)
        self._validate_option_catalog()
        self.setting_order = self._setting_order()
        self.choices = self._choice_catalog()

    def _profile_path(self, name):
        path = self.paths.profile_file(name).resolve()
        if path.parent != self.paths.profiles_dir.resolve():
            raise PrototypeError("Profile path must stay inside 10 Profiles.")
        return path

    def _source_path(self, relative):
        try:
            return self.paths.mutable_source_path(relative)
        except ValueError as exc:
            raise PrototypeError(str(exc)) from exc

    def _profile_fingerprint(self, name):
        path = self._profile_path(name)
        if not path.is_file():
            raise ProfileConflictError(f"Profile source no longer exists: {name}.yaml")
        return self._sha256(path.read_bytes())

    def _profile_discard_blockers(self, name):
        profile = self._profile(name)
        card_id = profile.get("card_id")
        blockers = []
        controls = load_yaml(self.paths.controls_file) or {}
        modes = controls.get("custom_shooting_modes") or {}
        assigned = [start for start in ("C1", "C2", "C3") if (modes.get(start) or {}).get("profile_id") == card_id]
        if assigned:
            blockers.append(f"assigned to {', '.join(assigned)}")
        routed = []
        for other_name, other in self.profiles.items():
            if other_name == name or is_reference_card(other):
                continue
            setup = ((other.get("card") or {}).get("field_setup") or {})
            if setup.get("source_card_id") == card_id:
                routed.append(str(other.get("title") or other_name))
        if routed:
            blockers.append("used as Cx foundation by " + ", ".join(sorted(routed, key=str.casefold)))
        manifest = load_yaml(self.paths.root / "50 Field Guide" / "required_appendices.yaml") or {}
        appendices = [
            str(entry.get("title") or entry.get("id"))
            for entry in manifest.get("appendices", []) or []
            if isinstance(entry, dict) and card_id in (entry.get("profile_ids") or [])
        ]
        if appendices:
            blockers.append("associated with appendices: " + ", ".join(appendices))
        return blockers

    def _profile_narrative_mentions(self, name):
        profile = self._profile(name)
        title = str(profile.get("title") or name)
        excluded = [self._profile_path(name)]
        return narrative_mentions(self.paths.root, title, excluded_paths=excluded)

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

    def _expire_discard_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [
            token
            for token, review in self._pending_discard_reviews.items()
            if review["created"] < cutoff
        ]
        for token in expired:
            del self._pending_discard_reviews[token]

    def _expire_restore_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [
            token
            for token, review in self._pending_restore_reviews.items()
            if review["created"] < cutoff
        ]
        for token in expired:
            del self._pending_restore_reviews[token]

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

    def _expire_cx_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [
            token
            for token, review in self._pending_cx_reviews.items()
            if review["created"] < cutoff
        ]
        for token in expired:
            del self._pending_cx_reviews[token]

    def _expire_special_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [
            token
            for token, review in self._pending_special_reviews.items()
            if review["created"] < cutoff
        ]
        for token in expired:
            del self._pending_special_reviews[token]

    def _expire_profile_starter_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        expired = [
            token
            for token, review in self._pending_profile_starter_reviews.items()
            if review["created"] < cutoff
        ]
        for token in expired:
            del self._pending_profile_starter_reviews[token]

    @staticmethod
    def _validate_project_sources(root):
        from validator import run

        return [issue.message for issue in run(root, source_only=True) if issue.level == "error"]

    def _source_validation_errors(self):
        target = self.paths if self.external_pack else self.paths.root
        return list(self._source_validator(target))

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

    def _render_preview(self, name, profile, lens_guidance_data=None, control_source=None):
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
            lens_guidance_data=lens_guidance_data,
            lens_equipment_data=self.lens_equipment,
            control_source=control_source,
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
        if value == "":
            return baseline
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
        for choice in self.choices.get(path, []):
            if isinstance(choice, str) and choice.casefold() == value.casefold():
                return choice
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
    request_token = None
    selection_store = None
    pack_creator = None
    model_switch_lock = None

    def do_GET(self):
        self.model = type(self).model
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path.startswith("/api/") and path != "/api/profile-packs":
                self.model.assert_profile_pack_current()
            if path == "/api/profile-packs":
                return self._json(self.selection_store.catalog(self.model.paths.profile_pack))
            if path == "/api/profiles":
                return self._json({"profiles": self.model.profile_list()})
            if path == "/api/dictionary":
                return self._json(self.model.dictionary_detail())
            if path == "/api/baseline":
                return self._json(self.model.baseline_detail())
            if path == "/api/cx-foundations":
                return self._json(self.model.cx_foundation_detail())
            if path == "/api/camera-buttons":
                return self._json(self.model.control_editor_detail())
            if path == "/api/camera-lab-evidence":
                return self._json(self.model.camera_lab_evidence_detail())
            if path == "/api/deleted-cards":
                return self._json({"cards": self.model.deleted_cards()})
            if path == "/api/editor-info":
                return self._json(self.model.editor_info())
            if path == "/api/profile-pack-creation-options":
                return self._json(self.pack_creator.creation_options())
            if path == "/api/profile-starter-options":
                return self._json(self.model.profile_starter_options())
            if path.startswith("/api/profiles/"):
                name = unquote(path.removeprefix("/api/profiles/"))
                return self._json(self.model.profile_detail(name))
            if path == "/preview/card.html":
                preview = self.model.paths.html_output_dir / PREVIEW_NAME
                return self._file(preview, "text/html; charset=utf-8")
            if path.startswith("/field-guide/html/"):
                self.model.assert_profile_pack_current()
                render_appendices(self.model.paths)
                relative = unquote(path.removeprefix("/field-guide/html/"))
                return self._safe_file(
                    self.model.paths.field_guide_html_output_dir,
                    relative,
                )
            if path.startswith("/field-guide/Cards/") or path == "/field-guide/index.html":
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
        self.model = type(self).model
        parsed = urlparse(self.path)
        if parsed.path not in {
            "/api/editor-shutdown",
            "/api/profile-pack-switch",
            "/api/profile-pack-destination-picker",
            "/api/profile-pack-creation-reviews",
            "/api/profile-pack-creations",
            "/api/profile-pack-git-status",
            "/api/profile-pack-git-commit-reviews",
            "/api/profile-pack-git-commits",
            "/api/profile-pack-git-remote-reviews",
            "/api/profile-pack-git-remotes",
            "/api/profile-pack-git-pushes",
            "/api/profile-starter-reviews",
            "/api/profile-starter-saves",
            "/api/camera-lab-launch",
            "/api/workflow-preflight",
            "/api/preflight-pull",
            "/api/preview",
            "/api/profile-drafts",
            "/api/profile-reviews",
            "/api/profile-saves",
            "/api/profile-removal-reviews",
            "/api/profile-removals",
            "/api/profile-restore-reviews",
            "/api/profile-restores",
            "/api/baseline-impact",
            "/api/baseline-plan",
            "/api/baseline-migration-reviews",
            "/api/baseline-migration-saves",
            "/api/my-menu-color-reviews",
            "/api/my-menu-color-saves",
            "/api/my-menu-reviews",
            "/api/my-menu-saves",
            "/api/cx-foundation-fit",
            "/api/cx-assignment-reviews",
            "/api/cx-selection-reviews",
            "/api/cx-foundation-saves",
            "/api/camera-buttons-preview",
            "/api/camera-buttons-reviews",
            "/api/camera-buttons-saves",
            "/api/camera-lab-evidence-reviews",
            "/api/camera-lab-evidence-saves",
            "/api/build-readiness",
            "/api/verification-tracker-import",
            "/api/local-build",
            "/api/finish-day-status",
            "/api/finish-day-prepare",
            "/api/finish-day-commit",
            "/api/finish-day-push",
            "/api/branch-integration-status",
            "/api/branch-integration-prepare",
            "/api/branch-integration-merge-main",
            "/api/branch-integration-push-main",
            "/api/branch-integration-resync",
            "/api/guarded-job-status",
            "/api/cleanup-status",
            "/api/cleanup-delete",
            "/api/publication-status",
            "/api/publication-notes-review",
            "/api/publication-notes-save",
            "/api/publication-review",
            "/api/publication-start",
            "/api/main-editor-launch",
        }:
            return self._json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
        protected_lifecycle_paths = {
            "/api/editor-shutdown",
            "/api/profile-pack-switch",
            "/api/profile-pack-destination-picker",
            "/api/profile-pack-creation-reviews",
            "/api/profile-pack-creations",
            "/api/profile-pack-git-status",
            "/api/profile-pack-git-commit-reviews",
            "/api/profile-pack-git-commits",
            "/api/profile-pack-git-remote-reviews",
            "/api/profile-pack-git-remotes",
            "/api/profile-pack-git-pushes",
            "/api/profile-starter-reviews",
            "/api/profile-starter-saves",
            "/api/camera-lab-launch",
            "/api/workflow-preflight",
            "/api/preflight-pull",
            "/api/finish-day-status",
            "/api/finish-day-prepare",
            "/api/finish-day-commit",
            "/api/finish-day-push",
            "/api/branch-integration-status",
            "/api/branch-integration-prepare",
            "/api/branch-integration-merge-main",
            "/api/branch-integration-push-main",
            "/api/branch-integration-resync",
            "/api/guarded-job-status",
            "/api/cleanup-status",
            "/api/cleanup-delete",
            "/api/publication-status",
            "/api/publication-notes-review",
            "/api/publication-notes-save",
            "/api/publication-review",
            "/api/publication-start",
            "/api/main-editor-launch",
        }
        if parsed.path in protected_lifecycle_paths and not secrets.compare_digest(
            self.headers.get("X-Profile-Editor-Token", ""), self.request_token
        ):
            return self._json({"error": "Profile Editor request token is missing or invalid."}, HTTPStatus.FORBIDDEN)
        try:
            if parsed.path == "/api/profile-pack-switch":
                pass
            elif self.model.external_pack and parsed.path != "/api/editor-shutdown":
                try:
                    self.model.assert_mutation_allowed(parsed.path)
                except PrototypeError as exc:
                    return self._json({"error": str(exc)}, HTTPStatus.FORBIDDEN)
            else:
                self.model.assert_profile_pack_current()
            payload = self._request_json()
            if parsed.path == "/api/editor-shutdown":
                result = {"stopping": True, "server_closed": True}
                self._json(result)
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            if parsed.path == "/api/profile-pack-switch":
                return self._json(self._switch_profile_pack(payload))
            if parsed.path == "/api/profile-pack-destination-picker":
                return self._json(
                    self.pack_creator.choose_destination(payload.get("suggestedName") or "")
                )
            if parsed.path == "/api/profile-pack-creation-reviews":
                return self._json(
                    self.pack_creator.review(
                        payload.get("packName"),
                        payload.get("destination"),
                        payload.get("pendingChanges"),
                        payload.get("optionalProfileIds"),
                    )
                )
            if parsed.path == "/api/profile-pack-creations":
                return self._json(
                    self._create_profile_pack(
                        payload.get("reviewToken"), payload.get("confirmCreate")
                    )
                )
            if parsed.path == "/api/profile-starter-reviews":
                return self._json(
                    self.model.review_profile_starters(
                        payload.get("cardIds"), payload.get("pendingChanges")
                    )
                )
            if parsed.path == "/api/profile-starter-saves":
                return self._json(
                    self.model.save_profile_starters(
                        payload.get("reviewToken"), payload.get("confirmAdd")
                    )
                )
            if parsed.path == "/api/profile-pack-git-status":
                return self._json(
                    self.model.profile_pack_git_status(payload.get("pendingChanges"))
                )
            if parsed.path == "/api/profile-pack-git-commit-reviews":
                return self._json(
                    self.model.review_profile_pack_git_commit(payload.get("pendingChanges"))
                )
            if parsed.path == "/api/profile-pack-git-commits":
                return self._json(
                    self.model.commit_profile_pack_git(
                        payload.get("reviewToken"),
                        payload.get("message"),
                        payload.get("confirmCommit"),
                    )
                )
            if parsed.path == "/api/profile-pack-git-remote-reviews":
                return self._json(
                    self.model.review_profile_pack_git_remote(
                        payload.get("remote"), payload.get("pendingChanges")
                    )
                )
            if parsed.path == "/api/profile-pack-git-remotes":
                return self._json(
                    self.model.start_configure_profile_pack_git_remote(
                        payload.get("reviewToken"), payload.get("confirmRemote")
                    )
                )
            if parsed.path == "/api/profile-pack-git-pushes":
                return self._json(
                    self.model.start_push_profile_pack_git(payload.get("confirmPush"))
                )
            if parsed.path == "/api/camera-lab-launch":
                return self._json(self.model.launch_camera_lab(payload.get("profile")))
            if parsed.path == "/api/workflow-preflight":
                return self._json(self.model.workflow_preflight())
            if parsed.path == "/api/preflight-pull":
                return self._json(
                    self.model.pull_latest(
                        payload.get("pendingChanges"), payload.get("confirmPull")
                    )
                )
            if parsed.path == "/api/profile-drafts":
                return self._json(self.model.profile_draft(payload.get("operation"), payload.get("sourceProfile")))
            if parsed.path == "/api/profile-reviews":
                return self._json(self.model.review_profile(payload))
            if parsed.path == "/api/profile-saves":
                return self._json(self.model.save_profile(payload.get("reviewToken")))
            if parsed.path == "/api/profile-removal-reviews":
                return self._json(
                    self.model.review_profile_removal(
                        payload.get("profile"), payload.get("sourceFingerprint")
                    )
                )
            if parsed.path == "/api/profile-removals":
                return self._json(self.model.save_profile_removal(payload.get("reviewToken")))
            if parsed.path == "/api/profile-restore-reviews":
                return self._json(self.model.review_profile_restore(payload.get("cardId")))
            if parsed.path == "/api/profile-restores":
                return self._json(self.model.save_profile_restore(payload.get("reviewToken")))
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
            if parsed.path == "/api/cx-foundation-fit":
                return self._json(
                    self.model.cx_foundation_detail(
                        payload.get("profile"),
                        payload.get("assignments"),
                        payload.get("overrides"),
                    )
                )
            if parsed.path == "/api/cx-assignment-reviews":
                return self._json(self.model.review_cx_assignments(payload.get("assignments")))
            if parsed.path == "/api/cx-selection-reviews":
                return self._json(
                    self.model.review_cx_selection(payload.get("profile"), payload.get("start"))
                )
            if parsed.path == "/api/cx-foundation-saves":
                return self._json(self.model.save_cx_review(payload.get("reviewToken")))
            if parsed.path == "/api/camera-buttons-preview":
                output = self.model.preview_control_editor(payload)
                return self._json({
                    "previewUrl": "/preview/card.html",
                    "outputFile": str(output),
                })
            if parsed.path == "/api/camera-buttons-reviews":
                return self._json(self.model.review_control_editor(payload))
            if parsed.path == "/api/camera-buttons-saves":
                return self._json(self.model.save_control_editor(payload.get("reviewToken")))
            if parsed.path == "/api/camera-lab-evidence-reviews":
                return self._json(
                    self.model.review_camera_lab_evidence(
                        payload.get("candidateIds"), payload.get("pendingChanges")
                    )
                )
            if parsed.path == "/api/camera-lab-evidence-saves":
                return self._json(
                    self.model.save_camera_lab_evidence(
                        payload.get("reviewToken"), payload.get("confirmImport")
                    )
                )
            if parsed.path == "/api/build-readiness":
                return self._json(self.model.build_readiness(payload.get("pendingChanges")))
            if parsed.path == "/api/verification-tracker-import":
                return self._json(
                    self.model.import_verification_tracker(
                        payload.get("pendingChanges"), payload.get("confirmImport")
                    )
                )
            if parsed.path == "/api/local-build":
                return self._json(
                    self.model.start_local_build(
                        payload.get("pendingChanges"), payload.get("confirmLocalBuild")
                    )
                )
            if parsed.path == "/api/finish-day-status":
                return self._json(self.model.finish_day_status(payload.get("pendingChanges")))
            if parsed.path == "/api/finish-day-prepare":
                return self._json(
                    self.model.start_finish_day_prepare(
                        payload.get("pendingChanges"),
                        payload.get("confirmPrepare"),
                        payload.get("confirmSpreadsheetRefresh"),
                    )
                )
            if parsed.path == "/api/finish-day-commit":
                return self._json(
                    self.model.commit_finish_day(
                        payload.get("reviewToken"),
                        payload.get("message"),
                        payload.get("confirmCommit"),
                    )
                )
            if parsed.path == "/api/finish-day-push":
                return self._json(self.model.push_finish_day(payload.get("confirmPush")))
            if parsed.path == "/api/branch-integration-status":
                return self._json(self.model.branch_integration_status(payload.get("pendingChanges")))
            if parsed.path == "/api/branch-integration-prepare":
                return self._json(
                    self.model.start_branch_integration_prepare(
                        payload.get("pendingChanges"),
                        payload.get("confirmPrepare"),
                        payload.get("confirmSpreadsheetRefresh"),
                    )
                )
            if parsed.path == "/api/branch-integration-merge-main":
                return self._json(
                    self.model.merge_branch_to_main(
                        payload.get("reviewToken"), payload.get("confirmMergeMain")
                    )
                )
            if parsed.path == "/api/branch-integration-push-main":
                return self._json(self.model.push_integrated_main(payload.get("confirmPushMain")))
            if parsed.path == "/api/branch-integration-resync":
                return self._json(self.model.resync_integrated_branch(payload.get("confirmResync")))
            if parsed.path == "/api/guarded-job-status":
                return self._json(self.model.guarded_job_status(payload.get("jobId")))
            if parsed.path == "/api/cleanup-status":
                return self._json(self.model.cleanup_status())
            if parsed.path == "/api/cleanup-delete":
                return self._json(
                    self.model.delete_cleanup_candidates(
                        payload.get("reviewToken"),
                        payload.get("candidateIds"),
                        payload.get("confirmDelete"),
                    )
                )
            if parsed.path == "/api/publication-status":
                return self._json(
                    self.model.publication_status(
                        payload.get("pendingChanges"), payload.get("majorVersion")
                    )
                )
            if parsed.path == "/api/publication-notes-review":
                return self._json(
                    self.model.review_publication_notes(
                        payload.get("majorVersion"), payload.get("highlights")
                    )
                )
            if parsed.path == "/api/publication-notes-save":
                return self._json(
                    self.model.save_publication_notes(
                        payload.get("reviewToken"), payload.get("confirmSave")
                    )
                )
            if parsed.path == "/api/publication-review":
                return self._json(
                    self.model.review_publication(
                        payload.get("pendingChanges"),
                        payload.get("majorVersion"),
                        payload.get("spreadsheetMode"),
                    )
                )
            if parsed.path == "/api/publication-start":
                return self._json(
                    self.model.start_website_publication(
                        payload.get("reviewToken"), payload.get("confirmPublish")
                    )
                )
            if parsed.path == "/api/main-editor-launch":
                return self._json(self.model.launch_main_editor())
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
            payload = {"error": str(exc)}
            if getattr(exc, "recovery", None):
                payload["recovery"] = exc.recovery
            return self._json(payload, HTTPStatus.CONFLICT)
        except PrototypeError as exc:
            payload = {"error": str(exc)}
            if getattr(exc, "recovery", None):
                payload["recovery"] = exc.recovery
            return self._json(payload, HTTPStatus.BAD_REQUEST)
        except ProfilePackSelectionError as exc:
            return self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except ProfilePackCreationError as exc:
            return self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            return self._json({"error": f"Profile editor operation failed: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _switch_profile_pack(self, payload):
        if payload.get("pendingChanges") != 0:
            raise PrototypeError("Save or discard every browser draft before switching profile packs.")
        if payload.get("confirmSwitch") is not True:
            raise PrototypeError("Profile-pack switching requires explicit confirmation.")
        pack_id = payload.get("packId")
        path = payload.get("path")
        if pack_id is not None and not isinstance(pack_id, str):
            raise PrototypeError("The selected profile-pack identity is invalid.")
        if path is not None and not isinstance(path, str):
            raise PrototypeError("The profile-pack path must be text.")
        pack_id = (pack_id or "").strip()
        path = (path or "").strip()
        if bool(pack_id) == bool(path):
            raise PrototypeError("Choose one remembered profile pack or provide one exact new path.")
        with self.model_switch_lock:
            context = (
                self.selection_store.resolve_path(path)
                if path
                else self.selection_store.resolve_registered(pack_id)
            )
            replacement = ProfileEditorModel(
                project_paths=ProjectPaths(
                    self.model.paths.application_root,
                    profile_pack_context=context,
                )
            )
            self.selection_store.remember_selected(context)
            type(self).model = replacement
            self.model = replacement
        return {
            "switched": True,
            "profile_pack": replacement.editor_info()["profile_pack"],
            "reload": True,
        }

    def _create_profile_pack(self, review_token, confirm_create):
        with self.model_switch_lock:
            context = self.pack_creator.create(review_token, confirm_create)
            try:
                replacement = ProfileEditorModel(
                    project_paths=ProjectPaths(
                        self.model.paths.application_root,
                        profile_pack_context=context,
                    )
                )
                self.selection_store.remember_selected(context)
            except Exception:
                self.pack_creator.discard_created(context.root)
                raise
            type(self).model = replacement
            self.model = replacement
        return {
            "created": True,
            "profile_pack": replacement.editor_info()["profile_pack"],
            "git": {
                "initialized": True,
                "committed": False,
                "remoteConfigured": False,
                "pushed": False,
            },
            "reload": True,
        }

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
        replacements = None
        if relative == "index.html":
            replacements = {b"__PROFILE_EDITOR_TOKEN__": self.request_token.encode("ascii")}
        return self._safe_file(STATIC_DIR, relative, replacements=replacements)

    def _source_file(self, relative):
        return self._safe_file(self.model.paths.root, relative)

    def _safe_file(self, root, relative, replacements=None):
        root = root.resolve()
        candidate = (root / relative).resolve()
        if candidate != root and root not in candidate.parents:
            raise FileNotFoundError(relative)
        return self._file(candidate, replacements=replacements)

    def _file(self, path, content_type=None, replacements=None):
        if not path.is_file():
            raise FileNotFoundError(path)
        data = path.read_bytes()
        for old, new in (replacements or {}).items():
            data = data.replace(old, new)
        mime = content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, payload, status=HTTPStatus.OK):
        if (
            status == HTTPStatus.OK
            and self.command == "POST"
            and self.model.external_pack
            and urlparse(self.path).path in EXTERNAL_PACK_EDITOR_ENDPOINTS
        ):
            self.model.accept_profile_pack_state()
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
    parser.add_argument("--port", type=int)
    parser.add_argument(
        "--print-default-port",
        action="store_true",
        help="Print the context-specific default port and exit.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Load all prototype data and report readiness without starting the server.",
    )
    parser.add_argument(
        "--profile-pack",
        metavar="PATH",
        help="Load one explicit compatible private profile pack in guarded-write mode.",
    )
    parser.add_argument(
        "--embedded",
        action="store_true",
        help="Ignore a saved profile-pack selection for this launch and use embedded sources.",
    )
    return parser.parse_args()


def create_server(model, port=DEFAULT_PORT, token=None, selection_store=None, pack_creator=None):
    selection_store = selection_store or ProfilePackSelectionStore(model.paths.application_root)
    pack_creator = pack_creator or ProfilePackCreator(model.paths.application_root)
    handler = type(
        "BoundEditorHandler",
        (EditorHandler,),
        {
            "model": model,
            "request_token": token or secrets.token_urlsafe(32),
            "selection_store": selection_store,
            "pack_creator": pack_creator,
            "model_switch_lock": threading.Lock(),
        },
    )
    return ThreadingHTTPServer((HOST, port), handler)


def main():
    args = parse_args()
    if args.profile_pack and args.embedded:
        print("Choose --profile-pack or --embedded, not both.", file=sys.stderr)
        return 2
    if args.print_default_port:
        print(default_editor_port())
        return 0
    port = args.port if args.port is not None else default_editor_port()
    selection_store = ProfilePackSelectionStore(PROJECT_ROOT)
    try:
        if args.profile_pack:
            context = resolve_profile_pack(PROJECT_ROOT, explicit_root=args.profile_pack)
        elif args.embedded:
            context = resolve_profile_pack(PROJECT_ROOT)
        else:
            context = selection_store.selected_context()
        model = ProfileEditorModel(
            project_paths=ProjectPaths(PROJECT_ROOT, profile_pack_context=context)
        )
    except (ProfilePackError, ProfilePackSelectionError, ValueError) as exc:
        print(f"Profile-pack error: {exc}", file=sys.stderr)
        return 2
    if args.check:
        for profile in model.profile_list():
            model.profile_detail(profile["name"])
        mode = "guarded external pack" if model.external_pack else "embedded sources"
        print(f"Profile editor check passed: {len(model.profiles)} profiles loaded from {mode}.")
        if model.external_pack:
            print(
                f"Profile pack: {model.paths.profile_pack.pack_name} "
                f"({model.paths.profile_pack.pack_id})"
            )
        print(f"Preview output: {model.paths.html_output_dir / PREVIEW_NAME}")
        return 0
    if not 1 <= port <= 65535:
        print("Port must be between 1 and 65535.", file=sys.stderr)
        return 2
    server = create_server(model, port=port, selection_store=selection_store)
    print("Canon Camera Reference — guarded profile editor")
    if model.external_pack:
        print(
            f"Guarded profile pack: {model.paths.profile_pack.pack_name} "
            f"({model.paths.profile_pack.pack_id})"
        )
    print(f"Open http://{HOST}:{port}")
    print("Use Stop Profile Editor in the page header, or press Control-C here.")
    print("Profile saves require exact diff review, backup, and validation.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProfile editor stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
