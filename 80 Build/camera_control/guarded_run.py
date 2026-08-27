"""Simulator-only planning and one-setting guarded execution for Camera Lab."""

from __future__ import annotations

from copy import deepcopy
import re

from .capability_mapping import VALUE_MAPS, decode_value, enrich_properties
from .connector import normalize_product_name
from .errors import CameraSessionError
from .native_backend import NativeHelperBackend
from .physical_write_policy import qualification_candidates
from .session_journal import SessionJournal, utc_now
from .simulated_backend import SimulatedBackend


CLASS_SKIPPED = "already_matching_skipped"
CLASS_AUTOMATIC = "simulator_automatic"
CLASS_PHYSICAL = "physical_automatic"
CLASS_MANUAL = "manual"
CLASS_BLOCKED = "blocked_or_unsupported"

FINAL_STEP_STATES = {"skipped", "simulator_verified", "camera_verified", "manual_user_confirmed"}
REQUIRED_PREFLIGHT_TEXT = ("still_movie_context", "lens", "flash", "cards")


def _normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()


def _target_raw(property_key, expected):
    wanted = _normalized(expected)
    if not wanted or wanted in {"not set", "none"}:
        return None
    aliases = {
        ("white_balance", "awb"): "awb ambience priority",
        ("drive_mode", "high speed continuous"): "high speed continuous",
        ("af_mode", "servo af"): "servo af",
    }
    wanted = aliases.get((property_key, wanted), wanted)
    matches = [raw for raw, label in VALUE_MAPS.get(property_key, {}).items() if _normalized(label) == wanted]
    return matches[0] if len(matches) == 1 else None


def _finding_items(comparison):
    seen = set()
    for finding in comparison["card_findings"] + comparison["additional_findings"]:
        items = finding.get("items") or [finding]
        for item in items:
            path = item.get("path")
            if not path or path in seen:
                continue
            seen.add(path)
            yield item, finding.get("access_paths") or item.get("access_paths") or []


def _manual_group(access_paths):
    route = str((access_paths or [{}])[0].get("label") or "Other camera settings").strip()
    route_lower = route.casefold()
    if "main dial" in route_lower or "exposure dial" in route_lower:
        return "exposure_controls", "Exposure controls"
    if route_lower.startswith("my menu"):
        section = re.split(r"\s*[→>]\s*", route, maxsplit=1)
        detail = section[1] if len(section) > 1 else "saved controls"
        return f"my_menu:{_normalized(detail)}", f"My Menu — {detail}"
    if route_lower.startswith("q screen"):
        return "q_screen", "Q screen"
    if "lens is switch" in route_lower:
        return "lens_stabilization", "Lens stabilization controls"
    menu = re.match(r"^(AF\d+|Shooting \d+|Playback \d+|Set-up \d+)(?:\s*>\s*([^>]+))?", route)
    if menu:
        page = menu.group(1)
        subsection = (menu.group(2) or "").strip()
        if subsection and ("settings" in subsection.casefold() or "shooting info" in subsection.casefold()):
            return f"{_normalized(page)}:{_normalized(subsection)}", f"{page} — {subsection}"
        return _normalized(page), page
    return _normalized(route) or "other", route


class GuardedRunManager:
    """Build and execute guarded runs without exposing an EDSDK mutation path."""

    def __init__(self, service, journal_root=None, manual_confirmations=None):
        self.service = service
        self.journal = SessionJournal(journal_root)
        self.manual_confirmations = manual_confirmations

    def available_summary(self):
        return self.journal.public_summary(
            self.journal.latest_resumable(backend="simulated" if self.service.backend_mode == "simulated" else "edsdk")
        )

    def prepare(self, profile_name, preflight, context_choices=None):
        backend = self._guarded_backend()
        self._validate_connected()
        preflight = self.validate_preflight(preflight)
        camera = self._camera_identity()
        if not camera.get("firmware_version"):
            raise CameraSessionError("Camera firmware must be available before preparing a guarded run.")

        snapshot_properties = enrich_properties(backend.read_capabilities())
        self.service.capabilities = self.service._capability_payload(snapshot_properties)
        comparison = self.service._build_comparison(profile_name, context_choices)
        steps = self._plan_steps(comparison, snapshot_properties, backend)
        snapshot = [
            {
                "key": item.get("key"),
                "label": item.get("label"),
                "read_status": item.get("read_status"),
                "value_raw": item.get("value_raw"),
                "value_display": item.get("value_display"),
            }
            for item in snapshot_properties
        ]
        record = self.journal.create(
            {
                "schema_version": 1,
                "kind": "camera_lab_simulated_guarded_run",
                "backend": self.service.backend_mode,
                "camera_session_id": self.service.camera_session_id,
                "profile": comparison["profile"],
                "camera": camera,
                "preflight": preflight,
                "pre_change_snapshot": snapshot,
                "c123_checkpoint": {
                    "physical_session": 3,
                    "registrations": {"C1": "Wildlife", "C2": "Birds in Flight", "C3": "Landscape"},
                    "recovery_file": "C123_CFG.CSD",
                    "lens_stabilization": "Mode 1/3 remains equipment-dependent",
                    "registration_execution": "manual_only",
                },
                "steps": steps,
                "current_step": self._next_pending_position(steps),
                "status": "planned",
                "confirmed_at": None,
                "completed_at": None,
                "failure": None,
            }
        )
        return self.public(record)

    def confirm(self, session_id, confirmed):
        if confirmed is not True:
            raise CameraSessionError("Explicit guarded-run confirmation is required.")
        record = self.journal.load(session_id)
        if record.get("status") != "planned":
            raise CameraSessionError("Only a planned guarded run can be confirmed.")
        blocked = [step for step in record["steps"] if step["classification"] == CLASS_BLOCKED]
        if blocked:
            raise CameraSessionError("Resolve every blocked or unsupported step before simulated execution.")
        self._verify_record_identity(record)
        self._recheck_already_correct(record)
        record["status"] = "confirmed"
        record["confirmed_at"] = utc_now()
        record = self.journal.save(record)
        if self.service.backend_mode == "simulated":
            record = self._process_simulator_automatic_steps(record)
        return self.public(record)

    def resume(self, session_id):
        record = self.journal.load(session_id)
        if record.get("status") not in {"confirmed", "in_progress", "failed"}:
            raise CameraSessionError("This guarded run is not resumable; prepare a new run or review its final state.")
        self._verify_record_identity(record)
        record["status"] = "confirmed"
        record["failure"] = None
        record["resumed_at"] = utc_now()
        record = self.journal.save(record)
        if self.service.backend_mode == "simulated":
            record = self._process_simulator_automatic_steps(record)
        return self.public(record)

    def abort(self, session_id):
        record = self.journal.load(session_id)
        if record.get("status") == "complete":
            raise CameraSessionError("A completed guarded run cannot be aborted.")
        record["status"] = "aborted"
        record["aborted_at"] = utc_now()
        return self.public(self.journal.save(record))

    def get(self, session_id):
        return self.public(self.journal.load(session_id))

    def execute_next(self, session_id, manual_confirmed=False):
        backend = self._guarded_backend()
        record = self.journal.load(session_id)
        if record.get("status") not in {"confirmed", "in_progress"}:
            raise CameraSessionError("Confirm or deliberately resume this guarded run before continuing.")
        position = self._next_pending_position(record.get("steps") or [])
        record["current_step"] = position
        if position >= len(record.get("steps") or []):
            return self.public(self.journal.save(self._finish(record)))

        step = record["steps"][position]
        record["status"] = "in_progress"
        try:
            self._verify_record_identity(record)
            if step["classification"] == CLASS_MANUAL:
                if manual_confirmed is not True:
                    result = self.public(self.journal.save(record))
                    result["action_required"] = "manual_confirmation"
                    return result
                self._complete_manual_group(record, step, backend)
            elif step["classification"] == CLASS_BLOCKED:
                step["status"] = "blocked"
                record["status"] = "blocked"
                record["failure"] = step["reason"]
                return self.public(self.journal.save(record))
            elif step["classification"] in {CLASS_AUTOMATIC, CLASS_PHYSICAL}:
                self._execute_automatic_step(record, step, backend)
            else:
                raise CameraSessionError("The current guarded-run step has an invalid classification.")
        except Exception as exc:
            step["status"] = "failed"
            record["status"] = "failed"
            record["failure"] = str(exc)
            record["failed_at"] = utc_now()
            return self.public(self.journal.save(record))

        record["current_step"] = self._next_pending_position(record["steps"])
        if record["current_step"] >= len(record["steps"]):
            record = self._finish(record)
        return self.public(self.journal.save(record))

    def _execute_automatic_step(self, record, step, backend):
        if step["classification"] == CLASS_AUTOMATIC:
            backend.begin_guarded_step()
        self._verify_record_identity(record)
        current = (
            backend.read_guarded_setting(step["property_key"])
            if step["classification"] == CLASS_AUTOMATIC
            else backend.read_physical_setting(step["property_key"])
        )
        step["read_before_raw"] = current
        step["read_before"] = decode_value(step["property_key"], current)
        if current == step["target_raw"]:
            step["status"] = "skipped"
            step["result"] = "The fresh read matched the target; the write was skipped automatically."
        else:
            if step["classification"] == CLASS_AUTOMATIC:
                backend.write_guarded_setting(step["property_key"], step["target_raw"])
                step["simulated_writes"] = 1
                readback = backend.read_guarded_setting(step["property_key"])
            else:
                backend.write_physical_setting(step["property_key"], step["target_raw"])
                step["physical_writes"] = 1
                readback = backend.read_physical_setting(step["property_key"])
            step["readback_raw"] = readback
            step["readback"] = decode_value(step["property_key"], readback)
            if readback != step["target_raw"]:
                raise CameraSessionError(
                    f"Readback mismatch for {step['label']}: expected {step['target']}, "
                    f"observed {step['readback']}."
                )
            if step["classification"] == CLASS_AUTOMATIC:
                step["status"] = "simulator_verified"
                step["evidence_method"] = "simulator_written_and_verified"
                step["result"] = "One simulated write was immediately read back and verified."
            else:
                step["status"] = "camera_verified"
                step["evidence_method"] = "sdk_written_and_verified"
                step["result"] = "One allowlisted EOS R5 write was immediately read back and verified."
        step["completed_at"] = utc_now()

    def _process_simulator_automatic_steps(self, record):
        backend = self._guarded_backend()
        for step in record.get("steps") or []:
            if step.get("classification") != CLASS_AUTOMATIC or step.get("status") in FINAL_STEP_STATES:
                continue
            record["status"] = "in_progress"
            try:
                self._execute_automatic_step(record, step, backend)
            except Exception as exc:
                step["status"] = "failed"
                record["status"] = "failed"
                record["failure"] = str(exc)
                record["failed_at"] = utc_now()
                record["current_step"] = step["index"] - 1
                return self.journal.save(record)
            record["current_step"] = self._next_pending_position(record["steps"])
            record = self.journal.save(record)
        if self._next_pending_position(record.get("steps") or []) >= len(record.get("steps") or []):
            record = self._finish(record)
        elif record.get("status") != "failed":
            record["status"] = "in_progress"
            record["current_step"] = self._next_pending_position(record["steps"])
        return self.journal.save(record)

    def _complete_manual_group(self, record, current, backend):
        group_key = current.get("manual_group_key")
        group = [
            step for step in record.get("steps") or []
            if step.get("classification") == CLASS_MANUAL
            and step.get("manual_group_key") == group_key
            and step.get("status") not in FINAL_STEP_STATES
        ]
        properties = enrich_properties(backend.read_capabilities())
        self.service.capabilities = self.service._capability_payload(properties)
        by_key = {item.get("key"): item for item in properties}
        self._verify_record_identity(record)
        for step in group:
            observed = by_key.get(step.get("property_key"))
            exact_readback = bool(
                observed
                and observed.get("read_status") == "sdk_verified"
                and _normalized(observed.get("value_display")) == _normalized(step.get("target"))
            )
            if exact_readback:
                step["status"] = "camera_verified"
                step["evidence_method"] = "sdk_verified_after_manual_group"
                step["result"] = "Verified by the single group rescan."
                step["readback_raw"] = observed.get("value_raw")
                step["readback"] = observed.get("value_display")
            else:
                step["status"] = "manual_user_confirmed"
                step["evidence_method"] = "manual_group_user_confirmed"
                step["result"] = "Confirmed with the rest of this camera-control group; no exact SDK readback was available."
            step["completed_at"] = utc_now()
        if self.manual_confirmations is not None:
            current_mode = next(
                (
                    item.get("value_display") for item in properties
                    if item.get("key") == "exposure_mode" and item.get("read_status") == "sdk_verified"
                ),
                "",
            )
            self.manual_confirmations.record_group(
                record,
                group,
                self.service.camera_session_id,
                current_mode,
            )

    @staticmethod
    def _next_pending_position(steps):
        for position, step in enumerate(steps):
            if step.get("status") not in FINAL_STEP_STATES:
                return position
        return len(steps)

    def _finish(self, record):
        if not all(step.get("status") in FINAL_STEP_STATES for step in record.get("steps") or []):
            record["status"] = "failed"
            record["failure"] = "The run ended with unresolved steps and is not complete."
            return record
        try:
            self._recheck_already_correct(record)
        except Exception as exc:
            record["status"] = "failed"
            record["failure"] = str(exc)
            record["failed_at"] = utc_now()
            return record
        record["status"] = "complete"
        record["completed_at"] = utc_now()
        record["failure"] = None
        return record

    def _recheck_already_correct(self, record):
        candidates = [
            step for step in record.get("steps") or []
            if step.get("skip_kind") == "already_correct"
            and step.get("property_key")
            and step.get("target_raw") is not None
        ]
        if not candidates:
            return
        backend = self._guarded_backend()
        properties = enrich_properties(backend.read_capabilities())
        self.service.capabilities = self.service._capability_payload(properties)
        by_key = {item.get("key"): item for item in properties}
        self._verify_record_identity(record)
        for step in candidates:
            observed = by_key.get(step["property_key"]) or {}
            if observed.get("read_status") != "sdk_verified" or observed.get("value_raw") != step["target_raw"]:
                step["status"] = "failed"
                step["readback_raw"] = observed.get("value_raw")
                step["readback"] = observed.get("value_display")
                raise CameraSessionError(
                    f"{step['label']} changed after the review. Review the profile again before continuing."
                )
            step["rechecked_at"] = utc_now()
            step["result"] = "Already correct; rechecked automatically without an operator step."

    def _plan_steps(self, comparison, properties, backend):
        by_path = {
            path: item
            for item in properties
            for path in item.get("profile_paths") or []
        }
        steps = []
        for finding, access_paths in _finding_items(comparison):
            path = finding["path"]
            property_item = by_path.get(path)
            classification = CLASS_MANUAL
            reason = finding.get("reason") or "Manual review is required."
            property_key = property_item.get("key") if property_item else None
            target_raw = _target_raw(property_key, finding["expected"]) if property_key else None
            skip_kind = None
            if finding["status"] in {"match", "equivalent", "not_applicable"}:
                classification = CLASS_SKIPPED
                reason = "Already matching, equivalent, or not applicable; skip without writing."
                skip_kind = "not_applicable" if finding["status"] == "not_applicable" else "already_correct"
            elif finding["status"] == "conditional" and finding.get("context_prompt"):
                classification = CLASS_BLOCKED
                reason = "The authored context remains unresolved; choose it before preparing a run."
            elif finding["status"] == "conditional":
                classification = CLASS_MANUAL
                reason = "The equipment- or field-dependent target requires deliberate manual completion."
            elif finding["status"] == "blocked":
                classification = CLASS_BLOCKED
            elif finding["status"] == "difference" and property_item:
                if target_raw is None:
                    classification = CLASS_MANUAL
                    reason = "The authored target has no unambiguous reviewed simulator encoding."
                elif self.service.backend_mode == "simulated" and not backend.supports_guarded_value(property_key, target_raw):
                    classification = CLASS_BLOCKED
                    reason = "The deterministic simulator reports this proposed value as unsupported."
                elif self.service.backend_mode == "simulated":
                    prerequisite_ok, prerequisite = backend.guarded_prerequisite(property_key, target_raw)
                    if prerequisite_ok:
                        classification = CLASS_AUTOMATIC
                        reason = "Simulator-only read, one write, and immediate readback verification."
                    else:
                        classification = CLASS_BLOCKED
                        reason = prerequisite or "A required simulator prerequisite is missing."
                elif property_key not in qualification_candidates():
                    classification = CLASS_BLOCKED
                    reason = "This physical property is outside the reviewed write-qualification allowlist."
                elif target_raw not in set(property_item.get("allowed_values_raw") or []):
                    classification = CLASS_BLOCKED
                    reason = "The target is not in the EOS R5 descriptor read during this session."
                elif self.service.physical_write_evidence.supports(
                    self.service.camera, self.service.sdk or {}, property_key, target_raw
                ):
                    classification = CLASS_PHYSICAL
                    reason = "Body-scoped evidence permits one EOS R5 write with immediate readback."
                else:
                    classification = CLASS_BLOCKED
                    reason = "This exact body, firmware, SDK, property, and value has not passed reversible qualification."
            manual_group_key, manual_group_label = _manual_group(access_paths)
            initially_skipped = classification == CLASS_SKIPPED
            steps.append(
                {
                    "index": len(steps) + 1,
                    "path": path,
                    "property_key": property_key,
                    "label": finding["label"],
                    "target": finding["expected"],
                    "target_raw": target_raw,
                    "observed": finding.get("actual"),
                    "observed_raw": finding.get("actual_raw"),
                    "comparison_status": finding["status"],
                    "classification": classification,
                    "reason": reason,
                    "skip_kind": skip_kind,
                    "manual_group_key": manual_group_key if classification == CLASS_MANUAL else None,
                    "manual_group_label": manual_group_label if classification == CLASS_MANUAL else None,
                    "access_paths": deepcopy(access_paths),
                    "status": "skipped" if initially_skipped else "pending",
                    "completed_at": utc_now() if initially_skipped else None,
                    "result": "No operator action required; recorded from the fresh pre-change snapshot." if initially_skipped else None,
                    "simulated_writes": 0,
                    "physical_writes": 0,
                }
            )
        return steps

    def validate_preflight(self, preflight):
        if not isinstance(preflight, dict):
            raise CameraSessionError("Complete the guarded-run preflight before planning.")
        cleaned = {key: str(preflight.get(key) or "").strip() for key in REQUIRED_PREFLIGHT_TEXT}
        if any(not value for value in cleaned.values()):
            raise CameraSessionError("Still/movie context, lens, flash, and card context are required.")
        if cleaned["still_movie_context"].casefold() != "still":
            raise CameraSessionError("Subject/Profile Card guarded runs require still-photo context.")
        if preflight.get("applications_closed") is not True:
            raise CameraSessionError("Confirm EOS Utility and every other camera-control application are closed.")
        if preflight.get("camera_backup_confirmed") is not True:
            raise CameraSessionError("Confirm a recoverable camera-side card backup before planning.")
        backup_filename = str(preflight.get("backup_filename") or "").strip()
        if not backup_filename.upper().endswith(".CSD"):
            raise CameraSessionError("Record the recoverable camera-side backup filename ending in .CSD.")
        camera_lens = str((self.service.camera or {}).get("lens_name") or "").strip()
        if camera_lens:
            cleaned["lens"] = camera_lens
        cleaned.update(
            {
                "current_mode": str(preflight.get("current_mode") or "Available in pre-change snapshot").strip(),
                "applications_closed": True,
                "camera_backup_confirmed": True,
                "backup_filename": backup_filename,
                "lens_source": "camera_readback" if camera_lens else "manual_confirmation",
            }
        )
        return cleaned

    def _camera_identity(self):
        details = self.service.backend.read_camera_details()
        return {
            "product_name": normalize_product_name(details.get("product_name")),
            "body_id": details.get("body_id"),
            "firmware_version": details.get("firmware_version"),
            "battery_raw": details.get("battery_raw"),
            "lens_name": details.get("lens_name"),
        }

    def _verify_record_identity(self, record):
        if self.service.backend is None or self.service.camera is None:
            raise CameraSessionError("The camera session disconnected; the guarded run stopped immediately.")
        observed_name = normalize_product_name(self.service.backend.poll_product_name())
        if observed_name != (record.get("camera") or {}).get("product_name"):
            raise CameraSessionError("Camera identity changed; the guarded run stopped immediately.")
        observed = self._camera_identity()
        expected = record.get("camera") or {}
        for key in ("product_name", "body_id", "firmware_version", "lens_name"):
            if observed.get(key) != expected.get(key):
                detail = "lens or camera identity" if key == "lens_name" else "camera identity"
                raise CameraSessionError(f"The connected {detail} changed; the guarded run stopped immediately.")

    def _validate_connected(self):
        status = self.service.status(check_connection=True)
        if not status.get("connected"):
            raise CameraSessionError("Connect the EOS R5 backend before using a guarded run.")

    def _guarded_backend(self):
        if self.service.backend_mode == "simulated" and isinstance(self.service.backend, SimulatedBackend):
            return self.service.backend
        if (
            self.service.backend_mode == "edsdk"
            and self.service.physical_write_enabled
            and isinstance(self.service.backend, NativeHelperBackend)
        ):
            return self.service.backend
        raise CameraSessionError("Guarded-run operations are unavailable in this Camera Lab mode.")

    @staticmethod
    def public(record):
        payload = deepcopy(record)
        counts = {
            classification: 0
            for classification in (CLASS_SKIPPED, CLASS_AUTOMATIC, CLASS_PHYSICAL, CLASS_MANUAL, CLASS_BLOCKED)
        }
        for step in payload.get("steps") or []:
            counts[step["classification"]] += 1
        work_items = []
        seen_manual_groups = set()
        for step in payload.get("steps") or []:
            if step.get("classification") == CLASS_SKIPPED:
                continue
            if step.get("classification") == CLASS_MANUAL:
                key = f"manual:{step.get('manual_group_key')}"
                if key in seen_manual_groups:
                    continue
                seen_manual_groups.add(key)
                members = [
                    item for item in payload.get("steps") or []
                    if item.get("classification") == CLASS_MANUAL
                    and item.get("manual_group_key") == step.get("manual_group_key")
                ]
                work_items.append(
                    {
                        "key": key,
                        "kind": "manual_group",
                        "label": step.get("manual_group_label"),
                        "step_indexes": [item["index"] for item in members],
                        "complete": all(item.get("status") in FINAL_STEP_STATES for item in members),
                    }
                )
            else:
                work_items.append(
                    {
                        "key": f"step:{step['index']}",
                        "kind": step.get("classification"),
                        "label": step.get("label"),
                        "step_indexes": [step["index"]],
                        "complete": step.get("status") in FINAL_STEP_STATES,
                    }
                )
        current_position = int(payload.get("current_step", 0))
        current = (payload.get("steps") or [])[current_position] if current_position < len(payload.get("steps") or []) else None
        current_key = None
        if current:
            current_key = (
                f"manual:{current.get('manual_group_key')}"
                if current.get("classification") == CLASS_MANUAL
                else f"step:{current.get('index')}"
            )
        current_action = next(
            (index + 1 for index, item in enumerate(work_items) if item["key"] == current_key),
            len(work_items) if work_items and all(item["complete"] for item in work_items) else 0,
        )
        operator_items = [item for item in work_items if item["kind"] != CLASS_AUTOMATIC]
        current_operator_action = next(
            (index + 1 for index, item in enumerate(operator_items) if item["key"] == current_key),
            len(operator_items) if operator_items and all(item["complete"] for item in operator_items) else 0,
        )
        payload["summary"] = {
            "classifications": counts,
            "completed_steps": sum(step.get("status") in FINAL_STEP_STATES for step in payload.get("steps") or []),
            "total_steps": len(payload.get("steps") or []),
            "actions": {
                "completed": sum(item["complete"] for item in work_items),
                "total": len(work_items),
                "current": current_action,
                "remaining": sum(not item["complete"] for item in work_items),
                "items": work_items,
            },
            "operator_actions": {
                "completed": sum(item["complete"] for item in operator_items),
                "total": len(operator_items),
                "current": current_operator_action,
                "remaining": sum(not item["complete"] for item in operator_items),
            },
            "automatic_actions": {
                "completed": sum(item["complete"] for item in work_items if item["kind"] == CLASS_AUTOMATIC),
                "total": sum(item["kind"] == CLASS_AUTOMATIC for item in work_items),
            },
            "auto_accounted": sum(
                step.get("classification") == CLASS_SKIPPED for step in payload.get("steps") or []
            ),
            "partial": payload.get("status") not in {"complete", "aborted", "planned"},
        }
        return {"ok": True, "guarded_run": payload}
