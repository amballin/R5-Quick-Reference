#!/usr/bin/env python3
"""Tests for simulator-only Phase 2A guarded-run planning and execution."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from camera_control.errors import CameraSessionError
from camera_control.capability_mapping import VALUE_MAPS
from camera_control.capability_registry import simulated_capabilities
from camera_control.native_backend import NativeHelperBackend
from camera_control.service import CameraControlService


PREFLIGHT = {
    "still_movie_context": "still",
    "current_mode": "Fv",
    "lens": "RF 100-500mm F4.5-7.1 L IS USM",
    "flash": "None",
    "cards": "CFexpress + SD",
    "applications_closed": True,
    "camera_backup_confirmed": True,
    "backup_filename": "C123_CFG.CSD",
}


class FakePhysicalBackend(NativeHelperBackend):
    """No-SDK test double that still satisfies the concrete physical backend gate."""

    def __init__(self, scenario="success"):
        self.scenario = scenario
        self.values = {item["key"]: item["value_raw"] for item in simulated_capabilities()}
        self.write_calls = []
        self.write_started = False

    def poll_product_name(self):
        if self.scenario == "disconnect" and self.write_started:
            raise CameraSessionError("Simulated physical camera disconnected")
        if self.scenario == "identity_change" and self.write_started:
            return "EOS R6"
        return "EOS R5"

    def read_camera_details(self):
        return {
            "product_name": self.poll_product_name(),
            "body_id": "TEST-R5-0001",
            "firmware_version": "2.2.1",
            "battery_raw": 100,
            "lens_name": "RF24-240mm F4-6.3 IS USM",
        }

    def read_capabilities(self):
        properties = simulated_capabilities(self.values)
        for item in properties:
            if item["key"] in VALUE_MAPS:
                item["allowed_values_raw"] = list(VALUE_MAPS[item["key"]])
        return properties

    def read_physical_setting(self, key):
        if self.scenario == "disconnect" and self.write_started:
            raise CameraSessionError("Simulated physical camera disconnected")
        return self.values[key]

    def write_physical_setting(self, key, value_raw):
        original = self.values[key]
        self.write_calls.append((key, value_raw))
        self.write_started = True
        if self.scenario == "busy":
            raise CameraSessionError("Simulated physical camera is busy")
        if self.scenario == "target_mismatch" and len(self.write_calls) == 1:
            return
        if self.scenario == "restore_mismatch" and len(self.write_calls) == 2:
            return
        self.values[key] = value_raw
        return {"ok": True, "property_key": key, "value_raw": value_raw, "original": original}

    def shutdown(self):
        pass


class GuardedRunTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="camera-lab-guarded-run-")

    def tearDown(self):
        self.temporary.cleanup()

    def service(self, scenario="guarded_success"):
        service = CameraControlService(
            simulated_scenario=scenario,
            journal_root=self.temporary.name,
        )
        service.connect()
        service.scan_capabilities()
        return service

    def physical_service(self, scenario="success"):
        root = Path(self.temporary.name)
        service = CameraControlService(
            backend_mode="edsdk",
            physical_write_enabled=True,
            journal_root=root / "runs",
            physical_evidence_path=root / "physical-write-evidence.json",
        )
        backend = FakePhysicalBackend(scenario)
        service.backend = backend
        service.camera = {
            "index": 0,
            "product_name": "EOS R5",
            "body_id": "TEST-R5-0001",
            "firmware_version": "2.2.1",
            "battery_raw": 100,
            "lens_name": "RF24-240mm F4-6.3 IS USM",
        }
        service.sdk = {"framework_version": "13.20.20.0", "path": "test-double"}
        service.capabilities = service._capability_payload(backend.read_capabilities())
        return service

    @staticmethod
    def prepare(service):
        return service.prepare_guarded_run("Landscape", dict(PREFLIGHT))["guarded_run"]

    @staticmethod
    def run_until_terminal(service, run):
        result = service.confirm_guarded_run(run["session_id"], True)
        while result["guarded_run"]["status"] not in {"complete", "failed", "blocked"}:
            current = result["guarded_run"]["steps"][result["guarded_run"]["current_step"]]
            result = service.execute_guarded_step(
                run["session_id"],
                manual_confirmed=current["classification"] == "manual",
            )
        return result["guarded_run"]

    def test_success_auto_processes_simulator_writes_and_groups_operator_work(self):
        service = self.service()
        run = self.prepare(service)
        self.assertEqual(run["status"], "planned")
        self.assertEqual(run["summary"]["classifications"]["simulator_automatic"], 4)
        self.assertEqual(run["summary"]["classifications"]["blocked_or_unsupported"], 0)
        self.assertEqual(run["preflight"]["backup_filename"], "C123_CFG.CSD")
        self.assertEqual(run["preflight"]["lens"], "Simulated RF 100-500mm F4.5-7.1 L IS USM")
        self.assertEqual(run["preflight"]["lens_source"], "camera_readback")
        self.assertEqual(run["camera"]["product_name"], "EOS R5")
        self.assertTrue(run["pre_change_snapshot"])
        self.assertEqual(run["c123_checkpoint"]["registrations"]["C2"], "Birds in Flight")
        self.assertEqual(run["summary"]["completed_steps"], 15)
        self.assertEqual(run["summary"]["actions"]["total"], 17)
        self.assertEqual(run["summary"]["operator_actions"]["total"], 13)
        self.assertTrue(
            all(
                step["status"] == "skipped"
                for step in run["steps"]
                if step["classification"] == "already_matching_skipped"
            )
        )

        started = service.confirm_guarded_run(run["session_id"], True)["guarded_run"]
        self.assertEqual(started["status"], "in_progress")
        self.assertEqual(started["summary"]["automatic_actions"], {"completed": 4, "total": 4})
        self.assertEqual(started["summary"]["operator_actions"]["current"], 1)
        current = started["steps"][started["current_step"]]
        self.assertEqual(current["manual_group_label"], "Exposure controls")
        group = [
            step for step in started["steps"]
            if step.get("manual_group_key") == current.get("manual_group_key")
            and step["classification"] == "manual"
        ]
        self.assertEqual([step["label"] for step in group], ["Shutter", "Aperture"])

        while started["status"] not in {"complete", "failed", "blocked"}:
            started = service.execute_guarded_step(run["session_id"], manual_confirmed=True)["guarded_run"]
        complete = started
        self.assertEqual(complete["status"], "complete")
        automatic = [step for step in complete["steps"] if step["classification"] == "simulator_automatic"]
        self.assertTrue(all(step["status"] == "simulator_verified" for step in automatic))
        self.assertTrue(all(step["simulated_writes"] == 1 for step in automatic))
        self.assertEqual(service.backend.write_count, len(automatic))
        self.assertFalse(complete["summary"]["partial"])

        journal = Path(self.temporary.name) / f"{run['session_id']}.json"
        saved = json.loads(journal.read_text(encoding="utf-8"))
        self.assertNotIn("token", json.dumps(saved).casefold())
        self.assertEqual(saved["status"], "complete")

        second = self.prepare(service)
        self.assertEqual(second["summary"]["classifications"]["simulator_automatic"], 0)

    def test_explicit_confirmation_is_required(self):
        service = self.service()
        run = self.prepare(service)
        with self.assertRaisesRegex(CameraSessionError, "Confirm or deliberately resume"):
            service.execute_guarded_step(run["session_id"])
        with self.assertRaisesRegex(CameraSessionError, "Explicit"):
            service.confirm_guarded_run(run["session_id"], False)

    def test_already_correct_items_auto_clear_but_are_rechecked_before_start(self):
        service = self.service()
        run = self.prepare(service)
        already_correct = [
            step for step in run["steps"]
            if step.get("skip_kind") == "already_correct" and step.get("target_raw") is not None
        ]
        self.assertTrue(already_correct)
        self.assertTrue(all(step["status"] == "skipped" for step in already_correct))
        changed = already_correct[0]
        service.backend.setting_values[changed["property_key"]] = changed["target_raw"] + 1
        with self.assertRaisesRegex(CameraSessionError, "changed after the review"):
            service.confirm_guarded_run(run["session_id"], True)

    def test_manual_route_group_uses_one_rescan_and_one_confirmation(self):
        service = self.service()
        run = self.prepare(service)
        started = service.confirm_guarded_run(run["session_id"], True)["guarded_run"]
        current = started["steps"][started["current_step"]]
        self.assertEqual(current["manual_group_label"], "Exposure controls")
        original_read = service.backend.read_capabilities
        scan_count = 0

        def counted_read():
            nonlocal scan_count
            scan_count += 1
            return original_read()

        service.backend.read_capabilities = counted_read
        advanced = service.execute_guarded_step(run["session_id"], manual_confirmed=True)["guarded_run"]
        self.assertEqual(scan_count, 1)
        exposure = [
            step for step in advanced["steps"]
            if step.get("manual_group_key") == "exposure_controls"
        ]
        self.assertEqual(len(exposure), 2)
        self.assertTrue(all(step["status"] in {"camera_verified", "manual_user_confirmed"} for step in exposure))
        self.assertEqual(advanced["summary"]["operator_actions"]["completed"], 1)

    def test_manual_confirmation_is_shared_only_for_exact_target_and_camera_session(self):
        service = self.service()
        run = self.prepare(service)
        started = service.confirm_guarded_run(run["session_id"], True)["guarded_run"]
        current = started["steps"][started["current_step"]]
        self.assertEqual(current["manual_group_label"], "Exposure controls")
        service.execute_guarded_step(run["session_id"], manual_confirmed=True)
        context = {"still_movie_context": "still", "flash": "None", "cards": "CFexpress + SD"}

        travel = service.compare_profile("Travel", manual_confirmation_context=context)
        shared = [
            finding for finding in travel["card_findings"] + travel["additional_findings"]
            if finding.get("shared_manual_confirmation")
        ]
        self.assertTrue(any(finding["label"] == "Shutter" and finding["expected"] == "Auto" for finding in shared))
        fireworks = service.compare_profile("Fireworks", manual_confirmation_context=context)
        self.assertFalse(
            any(finding.get("shared_manual_confirmation") for finding in fireworks["card_findings"] + fireworks["additional_findings"])
        )

        removed = service.revoke_manual_confirmations(
            [{"path": "shutter.target", "target": "Auto"}], context
        )
        self.assertEqual(removed["removed"], 1)
        travel = service.compare_profile("Travel", manual_confirmation_context=context)
        self.assertFalse(any(finding.get("shared_manual_confirmation") for finding in travel["card_findings"] + travel["additional_findings"]))

        service.disconnect()
        service.connect()
        service.scan_capabilities()
        landscape = service.compare_profile("Landscape", manual_confirmation_context=context)
        self.assertFalse(any(finding.get("shared_manual_confirmation") for finding in landscape["card_findings"] + landscape["additional_findings"]))
        ledger = Path(self.temporary.name) / "manual-confirmations.json"
        self.assertTrue(ledger.is_file())
        self.assertNotIn("token", ledger.read_text(encoding="utf-8").casefold())

    def test_readback_mismatch_stops_and_can_be_deliberately_resumed(self):
        service = self.service("guarded_readback_mismatch")
        run = self.prepare(service)
        failed = self.run_until_terminal(service, run)
        self.assertEqual(failed["status"], "failed")
        self.assertIn("Readback mismatch", failed["failure"])
        self.assertTrue(failed["summary"]["partial"])
        self.assertNotEqual(failed["status"], "complete")

        service.backend.scenario = "guarded_success"
        resumed = service.resume_guarded_run(run["session_id"])["guarded_run"]
        self.assertEqual(resumed["status"], "in_progress")
        while resumed["status"] not in {"complete", "failed", "blocked"}:
            current = resumed["steps"][resumed["current_step"]]
            resumed = service.execute_guarded_step(
                run["session_id"], current["classification"] == "manual"
            )["guarded_run"]
        self.assertEqual(resumed["status"], "complete")

    def test_unsupported_value_is_previewed_as_blocked(self):
        service = self.service("guarded_unsupported_value")
        run = self.prepare(service)
        self.assertGreater(run["summary"]["classifications"]["blocked_or_unsupported"], 0)
        self.assertTrue(any("unsupported" in step["reason"] for step in run["steps"]))
        with self.assertRaisesRegex(CameraSessionError, "blocked or unsupported"):
            service.confirm_guarded_run(run["session_id"], True)

    def test_missing_prerequisite_is_previewed_as_blocked(self):
        service = self.service("guarded_missing_prerequisite")
        run = self.prepare(service)
        blocked = [step for step in run["steps"] if step["classification"] == "blocked_or_unsupported"]
        self.assertTrue(blocked)
        self.assertTrue(all("lens" in step["reason"].casefold() for step in blocked))

    def test_busy_disconnect_and_identity_change_stop_immediately(self):
        expected = {
            "guarded_busy": "busy",
            "guarded_disconnect": "connection was lost",
            "guarded_identity_change": "identity changed",
        }
        for scenario, message in expected.items():
            with self.subTest(scenario=scenario):
                service = self.service(scenario)
                failed = self.run_until_terminal(service, self.prepare(service))
                self.assertEqual(failed["status"], "failed")
                self.assertIn(message, failed["failure"].casefold())
                self.assertTrue(failed["summary"]["partial"])

    def test_invalid_preflight_and_movie_context_are_rejected(self):
        service = self.service()
        for field in ("applications_closed", "camera_backup_confirmed"):
            invalid = dict(PREFLIGHT)
            invalid[field] = False
            with self.subTest(field=field), self.assertRaises(CameraSessionError):
                service.prepare_guarded_run("Landscape", invalid)

    def test_camera_lens_readback_overrides_typed_preflight(self):
        service = self.physical_service()
        entered = dict(PREFLIGHT)
        entered["lens"] = "100mm Macro"
        run = service.prepare_guarded_run("Landscape", entered)["guarded_run"]
        self.assertEqual(run["preflight"]["lens"], "RF24-240mm F4-6.3 IS USM")
        self.assertEqual(run["preflight"]["lens_source"], "camera_readback")
        movie = dict(PREFLIGHT, still_movie_context="movie")
        with self.assertRaisesRegex(CameraSessionError, "still-photo"):
            service.prepare_guarded_run("Landscape", movie)

    def test_abort_preserves_noncomplete_journal(self):
        service = self.service()
        run = self.prepare(service)
        aborted = service.abort_guarded_run(run["session_id"])["guarded_run"]
        self.assertEqual(aborted["status"], "aborted")
        self.assertNotEqual(aborted["status"], "complete")
        self.assertTrue((Path(self.temporary.name) / f"{run['session_id']}.json").is_file())

    def test_edsdk_mode_is_read_only_unless_explicitly_enabled(self):
        service = CameraControlService(backend_mode="edsdk", journal_root=self.temporary.name)
        with self.assertRaisesRegex(CameraSessionError, "unavailable"):
            service.prepare_guarded_run("Landscape", dict(PREFLIGHT))
        self.assertFalse(service.status(check_connection=False)["physical_write_enabled"])
        self.assertTrue(hasattr(NativeHelperBackend, "write_physical_setting"))
        backend = NativeHelperBackend(physical_write_enabled=False)
        with self.assertRaisesRegex(CameraSessionError, "not explicitly enabled"):
            backend.write_physical_setting("picture_style", 132)
        enabled = NativeHelperBackend(physical_write_enabled=True)
        commands = []
        enabled._command = lambda command: commands.append(command) or {"ok": True}
        enabled.write_physical_setting("picture_style", 132)
        self.assertEqual(commands, ["WRITE picture_style 132"])

    def test_reversible_physical_qualification_records_body_scoped_evidence(self):
        service = self.physical_service()
        status = service.status(check_connection=False)
        self.assertFalse(status["read_only"])
        self.assertTrue(status["physical_write_enabled"])
        candidates = service.physical_write_candidates()["candidates"]
        picture = next(item for item in candidates if item["key"] == "picture_style")
        target = next(item["value_raw"] for item in picture["targets"] if item["value_raw"] == 132)
        planned = service.prepare_write_qualification("picture_style", target, dict(PREFLIGHT))["qualification"]
        with self.assertRaisesRegex(CameraSessionError, "Confirm"):
            service.execute_write_qualification(planned["session_id"])
        service.confirm_write_qualification(planned["session_id"], True)
        complete = service.execute_write_qualification(planned["session_id"])["qualification"]
        self.assertEqual(complete["status"], "qualification_complete")
        self.assertEqual(service.backend.write_calls, [("picture_style", 132), ("picture_style", 129)])
        self.assertEqual(service.backend.values["picture_style"], 129)
        self.assertTrue(
            service.physical_write_evidence.supports(
                service.camera, service.sdk, "picture_style", 132
            )
        )
        evidence = json.loads((Path(self.temporary.name) / "physical-write-evidence.json").read_text())
        self.assertNotIn("token", json.dumps(evidence).casefold())

    def test_qualification_failure_restores_original_or_requires_manual_restore(self):
        for scenario, restore_required in (
            ("target_mismatch", False),
            ("restore_mismatch", True),
            ("identity_change", True),
            ("busy", True),
            ("disconnect", True),
        ):
            with self.subTest(scenario=scenario):
                service = self.physical_service(scenario)
                planned = service.prepare_write_qualification("picture_style", 132, dict(PREFLIGHT))["qualification"]
                service.confirm_write_qualification(planned["session_id"], True)
                failed = service.execute_write_qualification(planned["session_id"])["qualification"]
                self.assertEqual(failed["status"], "qualification_failed")
                self.assertEqual(failed["restore_required"], restore_required)
                self.assertFalse(
                    service.physical_write_evidence.supports(
                        service.camera, service.sdk, "picture_style", 132
                    )
                )

    def test_physical_guarded_plan_blocks_unqualified_values(self):
        service = self.physical_service()
        run = service.prepare_guarded_run("Fireworks", dict(PREFLIGHT))["guarded_run"]
        self.assertGreater(run["summary"]["classifications"]["blocked_or_unsupported"], 0)
        self.assertEqual(run["summary"]["classifications"]["physical_automatic"], 0)
        with self.assertRaisesRegex(CameraSessionError, "blocked or unsupported"):
            service.confirm_guarded_run(run["session_id"], True)

    def test_qualified_physical_run_writes_each_setting_once_and_reads_back(self):
        service = self.physical_service()
        for key, target in (("af_mode", 3), ("eye_detection", 0), ("picture_style", 132)):
            planned = service.prepare_write_qualification(key, target, dict(PREFLIGHT))["qualification"]
            service.confirm_write_qualification(planned["session_id"], True)
            result = service.execute_write_qualification(planned["session_id"])["qualification"]
            self.assertEqual(result["status"], "qualification_complete")
        service.backend.write_calls.clear()

        run = service.prepare_guarded_run("Fireworks", dict(PREFLIGHT))["guarded_run"]
        self.assertEqual(run["summary"]["classifications"]["physical_automatic"], 3)
        self.assertEqual(run["summary"]["classifications"]["blocked_or_unsupported"], 0)
        result = service.confirm_guarded_run(run["session_id"], True)
        while result["guarded_run"]["status"] not in {"complete", "failed", "blocked"}:
            current = result["guarded_run"]["steps"][result["guarded_run"]["current_step"]]
            result = service.execute_guarded_step(
                run["session_id"], manual_confirmed=current["classification"] == "manual"
            )
        complete = result["guarded_run"]
        self.assertEqual(complete["status"], "complete")
        automatic = [step for step in complete["steps"] if step["classification"] == "physical_automatic"]
        self.assertTrue(all(step["status"] == "camera_verified" for step in automatic))
        self.assertTrue(all(step["physical_writes"] == 1 for step in automatic))
        self.assertEqual(len(service.backend.write_calls), 3)


if __name__ == "__main__":
    unittest.main()
