"""Explicit reversible qualification for one physical EOS R5 property/value pair."""

from __future__ import annotations

from copy import deepcopy

from .capability_mapping import VALUE_MAPS, decode_value
from .connector import normalize_product_name
from .errors import CameraSessionError
from .native_backend import NativeHelperBackend
from .physical_write_policy import EVIDENCE_METHOD, PhysicalWriteEvidence, qualification_candidates
from .session_journal import SessionJournal, utc_now


class PhysicalWriteQualificationManager:
    def __init__(self, service, journal_root=None, evidence_path=None):
        self.service = service
        self.journal = SessionJournal(journal_root)
        self.evidence = PhysicalWriteEvidence(evidence_path)

    def candidates(self):
        self._require_available()
        if self.service.capabilities is None:
            raise CameraSessionError("Scan physical camera capabilities before qualifying a setting write.")
        definitions = qualification_candidates()
        choices = []
        for observed in self.service.capabilities.get("properties") or []:
            key = observed.get("key")
            if key not in definitions or observed.get("read_status") != "sdk_verified":
                continue
            allowed = []
            for raw in observed.get("allowed_values_raw") or []:
                if raw == observed.get("value_raw") or raw not in VALUE_MAPS.get(key, {}):
                    continue
                allowed.append({"value_raw": raw, "label": decode_value(key, raw)})
            choices.append(
                {
                    "key": key,
                    "label": observed.get("label") or definitions[key].get("label"),
                    "current_raw": observed.get("value_raw"),
                    "current": decode_value(key, observed.get("value_raw")),
                    "targets": allowed,
                    "dependencies": definitions[key].get("dependencies") or [],
                }
            )
        return {"ok": True, "candidates": choices}

    def prepare(self, property_key, target_raw, preflight):
        self._require_available()
        if not (self.service.camera or {}).get("body_id"):
            raise CameraSessionError("A readable EOS R5 body identifier is required for body-scoped write evidence.")
        if not (self.service.camera or {}).get("firmware_version") or not (self.service.sdk or {}).get("framework_version"):
            raise CameraSessionError("Camera firmware and Canon EDSDK version are required before qualification.")
        cleaned = self.service.guarded_runs.validate_preflight(preflight)
        if isinstance(target_raw, bool) or not isinstance(target_raw, int):
            raise CameraSessionError("Qualification target must be one reviewed raw integer value.")
        candidate = next(
            (item for item in self.candidates()["candidates"] if item["key"] == property_key),
            None,
        )
        if candidate is None:
            raise CameraSessionError("The selected property is not readable and qualification-allowlisted.")
        if target_raw not in {item["value_raw"] for item in candidate["targets"]}:
            raise CameraSessionError("The selected target is not in the camera's current reviewed descriptor.")
        original_raw = self.service.backend.read_physical_setting(property_key)
        if original_raw != candidate["current_raw"]:
            raise CameraSessionError("The property changed after the capability scan; rescan before qualification.")
        record = self.journal.create(
            {
                "schema_version": 1,
                "kind": "camera_lab_physical_write_qualification",
                "backend": "edsdk",
                "profile_pack": dict(self.service.app_info.get("profile_pack") or {}),
                "status": "qualification_planned",
                "camera": self._camera_identity(),
                "sdk": {"framework_version": (self.service.sdk or {}).get("framework_version")},
                "preflight": cleaned,
                "property_key": property_key,
                "label": candidate["label"],
                "original_raw": original_raw,
                "original": decode_value(property_key, original_raw),
                "target_raw": target_raw,
                "target": decode_value(property_key, target_raw),
                "operations": [],
                "confirmed_at": None,
                "completed_at": None,
                "failure": None,
                "restore_required": False,
            }
        )
        return self.public(record)

    def confirm(self, session_id, confirmed):
        if confirmed is not True:
            raise CameraSessionError("Explicit physical-write qualification confirmation is required.")
        record = self.journal.load(session_id)
        if record.get("status") != "qualification_planned":
            raise CameraSessionError("Only a planned physical-write qualification can be confirmed.")
        self._verify_identity(record)
        record["status"] = "qualification_confirmed"
        record["confirmed_at"] = utc_now()
        return self.public(self.journal.save(record))

    def execute(self, session_id):
        self._require_available()
        record = self.journal.load(session_id)
        if record.get("status") != "qualification_confirmed":
            raise CameraSessionError("Confirm the reversible physical-write qualification before executing it.")
        self._verify_identity(record)
        key = record["property_key"]
        original = record["original_raw"]
        target = record["target_raw"]
        current = self.service.backend.read_physical_setting(key)
        record["operations"].append({"operation": "read_original", "value_raw": current, "at": utc_now()})
        if current != original:
            return self._fail(record, "The setting changed after preview; rescan and prepare a new qualification.")

        target_attempted = False
        target_verified = False
        primary_failure = None
        try:
            target_attempted = True
            self.service.backend.write_physical_setting(key, target)
            record["operations"].append({"operation": "write_target", "value_raw": target, "at": utc_now()})
            observed_target = self.service.backend.read_physical_setting(key)
            record["operations"].append(
                {"operation": "read_target", "value_raw": observed_target, "at": utc_now()}
            )
            if observed_target != target:
                raise CameraSessionError(
                    f"Qualification readback mismatch: expected {decode_value(key, target)}, "
                    f"observed {decode_value(key, observed_target)}."
                )
            target_verified = True
        except Exception as exc:
            primary_failure = str(exc)

        restore_failure = None
        if target_attempted:
            try:
                self._verify_identity(record)
                self.service.backend.write_physical_setting(key, original)
                record["operations"].append({"operation": "restore_original", "value_raw": original, "at": utc_now()})
                observed_original = self.service.backend.read_physical_setting(key)
                record["operations"].append(
                    {"operation": "read_restored", "value_raw": observed_original, "at": utc_now()}
                )
                if observed_original != original:
                    raise CameraSessionError(
                        f"Restore readback mismatch: expected {decode_value(key, original)}, "
                        f"observed {decode_value(key, observed_original)}."
                    )
            except Exception as exc:
                restore_failure = str(exc)

        if restore_failure:
            record["restore_required"] = True
            return self._fail(
                record,
                f"Qualification stopped and the original value was not verified restored. "
                f"Use the camera controls to restore {record['label']} to {record['original']}. "
                f"Details: {restore_failure}",
            )
        if primary_failure or not target_verified:
            return self._fail(record, f"Qualification failed; the original value was restored. {primary_failure or ''}".strip())

        evidence = self.evidence.record(
            record["camera"], record["sdk"], key, [original, target], record["session_id"]
        )
        record["status"] = "qualification_complete"
        record["completed_at"] = utc_now()
        record["failure"] = None
        record["evidence_method"] = EVIDENCE_METHOD
        record["verified_values_raw"] = evidence["verified_values_raw"]
        return self.public(self.journal.save(record))

    def get(self, session_id):
        return self.public(self.journal.load(session_id))

    def _fail(self, record, message):
        record["status"] = "qualification_failed"
        record["failure"] = message
        record["failed_at"] = utc_now()
        return self.public(self.journal.save(record))

    def _require_available(self):
        if (
            self.service.backend_mode != "edsdk"
            or not self.service.physical_write_enabled
            or not isinstance(self.service.backend, NativeHelperBackend)
            or self.service.camera is None
        ):
            raise CameraSessionError(
                "Physical write qualification is unavailable unless an EOS R5 is connected in explicitly enabled EDSDK mode."
            )

    def _camera_identity(self):
        details = self.service.backend.read_camera_details()
        return {
            "product_name": normalize_product_name(details.get("product_name")),
            "body_id": details.get("body_id"),
            "firmware_version": details.get("firmware_version"),
        }

    def _verify_identity(self, record):
        expected_pack = record.get("profile_pack") or {}
        active_pack = self.service.app_info.get("profile_pack") or {}
        if expected_pack and expected_pack.get("pack_id") != active_pack.get("pack_id"):
            raise CameraSessionError("The qualification belongs to a different profile pack.")
        if not expected_pack and self.service.external_pack:
            raise CameraSessionError("This qualification predates external profile-pack identity records; prepare a new qualification.")
        self.service.assert_profile_pack_current()
        observed = self._camera_identity()
        if observed != record.get("camera"):
            raise CameraSessionError("Camera identity changed; physical write qualification stopped.")

    @staticmethod
    def public(record):
        return {"ok": True, "qualification": deepcopy(record)}
