#!/usr/bin/env python3
"""Review exact Camera Lab evidence for deliberate tracker promotion."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path

from build_validator import discover_profiles, is_reference_card
from camera_setup_tracker import effective_registration_definition_fingerprints
from profile_loader import load_yaml
from verification_status import load_status, working_copy_state, WORKING_COPY_CONFLICT, WORKING_COPY_PENDING


ELIGIBLE_STEP_STATES = {"camera_verified", "manual_user_confirmed"}


class CameraLabTrackerImportError(RuntimeError):
    """Raised when machine-local evidence cannot be promoted safely."""


def inspect_evidence(paths, journal_root=None):
    """Return completed physical sessions and exact registration candidates."""
    state, message = working_copy_state(paths)
    workbook_blocked = state in {WORKING_COPY_PENDING, WORKING_COPY_CONFLICT}
    root = (
        Path(journal_root).expanduser().resolve()
        if journal_root
        else paths.local_workspace_dir / "Camera Lab" / "Guarded Runs"
    )
    assignment_by_title = _assignment_titles(paths)
    registration_by_path = _registration_paths(paths)
    imported = _imported_candidate_ids(load_status(paths))
    sessions = []
    candidates_by_id = {}
    if root.is_dir():
        for path in sorted(root.glob("*.json"), reverse=True):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if record.get("backend") != "edsdk" or record.get("status") != "complete":
                continue
            session_id = record.get("session_id")
            if not isinstance(session_id, str) or not session_id.strip():
                continue
            profile = record.get("profile") or {}
            title = str(profile.get("title") or profile.get("name") or "").strip()
            slot = assignment_by_title.get(title)
            session = {
                "sessionId": record.get("session_id"),
                "profile": title or "Unknown profile",
                "slot": slot,
                "completedAt": record.get("completed_at"),
                "firmware": (record.get("camera") or {}).get("firmware"),
                "eligibleCount": 0,
                "skippedReason": None,
            }
            if paths.profile_pack.mode == "external":
                recorded_pack = record.get("profile_pack") or {}
                if recorded_pack.get("pack_id") != paths.profile_pack.pack_id:
                    session["skippedReason"] = (
                        "The journal does not belong to the active profile pack."
                    )
                    sessions.append(session)
                    continue
            if not slot:
                session["skippedReason"] = "The profile is not currently assigned to C1, C2, or C3."
                sessions.append(session)
                continue
            for step in record.get("steps") or []:
                promoted = _step_evidence(step)
                setting = registration_by_path.get(str(step.get("path") or ""))
                if not promoted or not setting:
                    continue
                candidate_id = f"{session_id}:{slot}:{setting}"
                candidate = {
                    "candidateId": candidate_id,
                    "sessionId": session_id,
                    "profile": title,
                    "slot": slot,
                    "setting": setting,
                    "path": step.get("path"),
                    "target": step.get("target"),
                    "evidenceMethod": promoted,
                    "completedAt": step.get("completed_at") or record.get("completed_at"),
                    "journalFile": path.name,
                    "journalSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "alreadyImported": candidate_id in imported,
                }
                if candidate_id not in candidates_by_id:
                    candidates_by_id[candidate_id] = candidate
                    session["eligibleCount"] += 1
            if not session["eligibleCount"]:
                session["skippedReason"] = "No exact C1-C3 registration setting evidence was found."
            sessions.append(session)
    candidates = list(candidates_by_id.values())
    candidates.sort(key=lambda item: (item["completedAt"] or "", item["slot"], item["setting"]), reverse=True)
    return {
        "journalLocation": (
            "Pack-scoped machine-local Camera Lab evidence"
            if paths.profile_pack.mode == "external"
            else "Machine-local Camera Lab evidence"
        ),
        "workbookBlocked": workbook_blocked,
        "workbookMessage": message,
        "sessions": sessions,
        "candidates": candidates,
        "eligibleCount": sum(not item["alreadyImported"] for item in candidates),
        "boundary": (
            "Only exact evidence from completed physical-camera sessions can mark the matching "
            "C1-C3 setting as configured. Read-back, registration, operational tests, backups, and "
            "Canon capability claims remain unchanged."
        ),
    }


def build_candidate_status(paths, candidate_ids, journal_root=None):
    inventory = inspect_evidence(paths, journal_root=journal_root)
    if inventory["workbookBlocked"]:
        raise CameraLabTrackerImportError(inventory["workbookMessage"])
    requested = {str(value) for value in (candidate_ids or []) if str(value)}
    if not requested:
        raise CameraLabTrackerImportError("Select at least one new Camera Lab evidence item.")
    available = {
        item["candidateId"]: item
        for item in inventory["candidates"]
        if not item["alreadyImported"]
    }
    missing = sorted(requested - set(available))
    if missing:
        raise CameraLabTrackerImportError(
            "One or more selected evidence items changed, were already imported, or are no longer eligible."
        )
    status = load_status(paths)
    original = deepcopy(status)
    definition = load_yaml(paths.verification_tracker_source_file) or {}
    defaults = (load_yaml(paths.baseline_file) or {}).get("defaults") or {}
    fingerprints = effective_registration_definition_fingerprints(definition, defaults)
    now = datetime.now().astimezone().isoformat()
    applied = []
    for candidate_id in sorted(requested):
        item = available[candidate_id]
        key = item["slot"].casefold()
        field = f"{key}_configured"
        notes_field = f"{key}_notes"
        registration = status["registration"].setdefault(item["setting"], {})
        previous = deepcopy(registration)
        registration[field] = "Pass"
        note = (
            f"Camera Lab {item['evidenceMethod']} · {item['profile']} · "
            f"session {item['sessionId'][:8]} · {item['completedAt'] or 'time unavailable'}."
        )
        existing = str(registration.get(notes_field) or "").strip()
        if note not in existing:
            registration[notes_field] = f"{existing} {note}".strip()
        registration["verified_against"] = fingerprints.get(item["setting"])
        status.setdefault("history", []).append(
            {
                "timestamp": now,
                "event": "camera_lab_evidence_import",
                "id": candidate_id,
                "previous": previous or None,
                "current": deepcopy(registration),
                "evidence": {
                    "method": item["evidenceMethod"],
                    "journal": item["journalFile"],
                    "profile": item["profile"],
                    "path": item["path"],
                    "target": item["target"],
                    "completed_at": item["completedAt"],
                },
            }
        )
        applied.append(item)
    status["updated"] = now
    return original, status, applied


def _assignment_titles(paths):
    controls = load_yaml(paths.root / "controls.yaml") or {}
    profiles = {}
    for path in discover_profiles(paths):
        profile = load_yaml(path) or {}
        if not is_reference_card(profile):
            profiles[profile.get("card_id")] = str(profile.get("title") or path.stem)
    result = {}
    for slot in ("C1", "C2", "C3"):
        card_id = ((controls.get("custom_shooting_modes") or {}).get(slot) or {}).get("profile_id")
        title = profiles.get(card_id)
        if title:
            result[title] = slot
    return result


def _registration_paths(paths):
    definition = load_yaml(paths.verification_tracker_source_file) or {}
    return {
        str(row.get("baseline_key")): str(row.get("setting"))
        for row in ((definition.get("registration") or {}).get("rows") or [])
        if row.get("baseline_key") and row.get("setting")
    }


def _step_evidence(step):
    status = step.get("status")
    method = str(step.get("evidence_method") or "")
    if status in ELIGIBLE_STEP_STATES and method and not method.startswith("simulator"):
        return method
    if (
        status == "skipped"
        and step.get("skip_kind") == "already_correct"
        and step.get("comparison_status") == "match"
        and step.get("property_key")
        and step.get("rechecked_at")
    ):
        return "sdk_verified"
    return None


def _imported_candidate_ids(status):
    return {
        str(item.get("id"))
        for item in status.get("history") or []
        if item.get("event") == "camera_lab_evidence_import" and item.get("id")
    }
