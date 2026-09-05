#!/usr/bin/env python3
"""Guarded Profile Editor coverage for one explicitly selected profile pack."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

import yaml

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from profile_editor import EditorHandler, ProfileEditorModel, PrototypeError  # noqa: E402
from profile_pack_selection import ProfilePackSelectionStore  # noqa: E402
from test_profile_pack_build import PROJECT_ROOT, write_pack_from_embedded_sources  # noqa: E402


class ProfilePackEditorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace_environment = mock.patch.dict(
            os.environ,
            {"PRS_LOCAL_WORKSPACE": str(Path(self.temporary.name) / "workspace")},
        )
        self.workspace_environment.start()
        self.pack = Path(self.temporary.name) / "private-pack"
        write_pack_from_embedded_sources(self.pack)
        self.model = ProfileEditorModel(PROJECT_ROOT, profile_pack_root=self.pack)

    def tearDown(self):
        self.workspace_environment.stop()
        self.temporary.cleanup()

    def profile_payload(self, name="Fireworks", **changes):
        detail = self.model.profile_detail(name)
        payload = {
            "operation": "update",
            "sourceProfile": name,
            "targetName": name,
            "sourceFingerprint": detail["sourceFingerprint"],
            "title": detail["title"],
            "subtitle": detail["subtitle"],
            "status": detail["metadata"]["status"],
            "displayCategory": detail["displayCategory"],
            "release": detail["metadata"]["release"],
            "overrides": detail["originalOverrides"],
            "lensChoices": detail["lensChoices"],
            "lensGuidanceFingerprint": detail["lensGuidanceFingerprint"],
        }
        payload.update(changes)
        return payload

    def create_unreleased_profile(self, name):
        draft = self.model.profile_draft("create")
        review = self.model.review_profile(
            {
                "operation": "create",
                "sourceProfile": None,
                "targetName": name,
                "sourceFingerprint": None,
                "title": name,
                "subtitle": "",
                "status": "Draft",
                "displayCategory": "reference",
                "release": False,
                "overrides": draft["originalOverrides"],
                "lensChoices": [],
                "lensGuidanceFingerprint": draft["lensGuidanceFingerprint"],
            }
        )
        result = self.model.save_profile(review["reviewToken"])
        self.model.accept_profile_pack_state()
        return result

    def migration_payload(self):
        values = dict(self.model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        analysis = self.model.baseline_impact(values)
        decisions = [
            {
                "profile": profile["name"],
                "path": change["path"],
                "decision": "follow_baseline",
            }
            for change in analysis["changes"]
            for profile in change["profiles"]
            if profile["classification"] == "inherited_change"
        ]
        return {
            "values": values,
            "decisions": decisions,
            "myMenuTabs": None,
            "acknowledgeCxImpact": True,
            "acknowledgeMyMenuImpact": True,
        }

    def test_external_pack_loads_with_path_free_guarded_identity(self):
        info = self.model.editor_info()
        self.assertFalse(info["read_only"])
        self.assertEqual(info["pack_access"], "guarded-write")
        self.assertEqual(info["application"]["project_id"], "canon-eos-r5-camera-reference")
        self.assertEqual(info["profile_pack"]["pack_name"], "Embedded parity fixture")
        self.assertEqual(info["profile_pack"]["mode"], "external")
        self.assertNotIn(str(self.pack), json.dumps(info))
        self.assertTrue(self.model.profile_list())
        self.assertEqual(self.model._cx_assignments(), {"C1": "Wildlife", "C2": "Birds in Flight", "C3": "Landscape"})
        self.assertTrue(self.model.control_editor_detail()["controls"])

    def test_external_pack_change_requires_restart(self):
        baseline = self.pack / "00 Master" / "baseline.yaml"
        baseline.write_text(baseline.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(PrototypeError, "sources changed"):
            self.model.assert_profile_pack_current()

    def test_external_pack_boundary_allows_pack_editors_camera_lab_and_evidence_promotion(self):
        self.model.assert_mutation_allowed("/api/profile-saves")
        self.model.assert_mutation_allowed("/api/camera-lab-launch")
        self.model.assert_mutation_allowed("/api/camera-lab-evidence-reviews")
        self.model.assert_mutation_allowed("/api/camera-lab-evidence-saves")
        self.model.assert_mutation_allowed("/api/profile-pack-git-status")
        self.model.assert_mutation_allowed("/api/profile-pack-git-commit-reviews")
        self.model.assert_mutation_allowed("/api/profile-pack-git-commits")
        self.model.assert_mutation_allowed("/api/profile-pack-git-remote-reviews")
        self.model.assert_mutation_allowed("/api/profile-pack-git-remotes")
        self.model.assert_mutation_allowed("/api/profile-pack-git-pushes")
        self.model.assert_mutation_allowed("/api/profile-starter-reviews")
        self.model.assert_mutation_allowed("/api/profile-starter-saves")
        with self.assertRaisesRegex(PrototypeError, "outside the guarded"):
            self.model.assert_mutation_allowed("/api/local-build")
        with self.assertRaisesRegex(PrototypeError, "outside the guarded"):
            self.model.assert_mutation_allowed("/api/profile-pack-creations")

    def test_adds_reviewed_official_profile_and_lens_guidance_without_overwrite(self):
        macro_id = "48850916-669d-592f-9e3f-defc3994445e"
        (self.pack / "10 Profiles" / "Macro.yaml").unlink()
        guidance_path = self.pack / "00 Master" / "profile_lens_guidance.yaml"
        guidance = yaml.safe_load(guidance_path.read_text(encoding="utf-8"))
        guidance["profiles"] = [
            entry for entry in guidance["profiles"] if entry.get("card_id") != macro_id
        ]
        guidance_path.write_text(yaml.safe_dump(guidance, sort_keys=False), encoding="utf-8")
        self.model = ProfileEditorModel(PROJECT_ROOT, profile_pack_root=self.pack)

        options = self.model.profile_starter_options()
        self.assertIn("Macro", [item["title"] for item in options["available"]])
        self.assertIn("application catalog", options["message"])
        with self.assertRaisesRegex(PrototypeError, "browser draft"):
            self.model.review_profile_starters([macro_id], 1)
        review = self.model.review_profile_starters([macro_id], 0)
        self.assertEqual(review["profiles"], ["Macro"])
        self.assertIn("from the application catalog", review["summary"])
        self.assertIn("10 Profiles/Macro.yaml", review["sourceFiles"])
        self.assertIn("00 Master/profile_lens_guidance.yaml", review["sourceFiles"])
        self.assertIn("/dev/null", review["diff"])
        with self.assertRaisesRegex(PrototypeError, "explicit confirmation"):
            self.model.save_profile_starters(review["reviewToken"], False)

        result = self.model.save_profile_starters(review["reviewToken"], True)
        self.model.accept_profile_pack_state()
        self.assertEqual(result["addedProfiles"], ["Macro"])
        self.assertTrue((self.pack / "10 Profiles" / "Macro.yaml").is_file())
        saved_guidance = yaml.safe_load(guidance_path.read_text(encoding="utf-8"))
        self.assertIn(macro_id, [entry.get("card_id") for entry in saved_guidance["profiles"]])
        transaction = json.loads((Path(result["backup"]) / "transaction.json").read_text())
        self.assertEqual(transaction["profile_pack"]["pack_id"], self.model.paths.profile_pack.pack_id)
        self.assertNotIn("Macro", [item["title"] for item in self.model.profile_starter_options()["available"]])
        with self.assertRaisesRegex(PrototypeError, "unavailable or already present"):
            self.model.review_profile_starters([macro_id], 0)

    def test_official_profile_addition_rolls_back_after_validation_failure(self):
        macro_id = "48850916-669d-592f-9e3f-defc3994445e"
        macro_path = self.pack / "10 Profiles" / "Macro.yaml"
        macro_path.unlink()
        guidance_path = self.pack / "00 Master" / "profile_lens_guidance.yaml"
        guidance = yaml.safe_load(guidance_path.read_text(encoding="utf-8"))
        guidance["profiles"] = [
            entry for entry in guidance["profiles"] if entry.get("card_id") != macro_id
        ]
        guidance_path.write_text(yaml.safe_dump(guidance, sort_keys=False), encoding="utf-8")
        before_guidance = guidance_path.read_bytes()
        self.model = ProfileEditorModel(
            PROJECT_ROOT,
            profile_pack_root=self.pack,
            source_validator=lambda _paths: ["forced validation failure"],
        )
        review = self.model.review_profile_starters([macro_id], 0)
        with self.assertRaisesRegex(PrototypeError, "prior pack source was restored"):
            self.model.save_profile_starters(review["reviewToken"], True)
        self.assertFalse(macro_path.exists())
        self.assertEqual(guidance_path.read_bytes(), before_guidance)

    def test_external_pack_git_status_is_routed_to_the_selected_pack_workflow(self):
        workflow = mock.Mock()
        workflow.inspect.return_value = {
            "phase": "initial-commit",
            "packId": self.model.paths.profile_pack.pack_id,
            "application": {"label": "Application"},
            "pack": {"label": "Private profile pack"},
        }
        self.model.profile_pack_git_workflow = workflow
        status = self.model.profile_pack_git_status(0)
        self.assertEqual(status["phase"], "initial-commit")
        self.assertEqual(status["packId"], self.model.paths.profile_pack.pack_id)
        self.assertEqual(status["application"]["label"], "Application")
        self.assertEqual(status["pack"]["label"], "Private profile pack")
        workflow.inspect.assert_called_once_with(0)

    def test_cli_check_accepts_explicit_pack_as_guarded(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(PROJECT_ROOT / "80 Build" / "profile_editor.py"),
                "--profile-pack",
                str(self.pack),
                "--check",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("guarded external pack", completed.stdout)
        self.assertIn("Embedded parity fixture", completed.stdout)

    def test_ui_declares_external_pack_identity_and_guarded_boundary(self):
        editor = PROJECT_ROOT / "80 Build" / "profile_editor"
        html = (editor / "index.html").read_text(encoding="utf-8")
        script = (editor / "app.js").read_text(encoding="utf-8")
        styles = (editor / "styles.css").read_text(encoding="utf-8")
        self.assertIn('id="profile-pack-select"', html)
        self.assertNotIn('id="project-context-badge"', html)
        self.assertIn('id="external-pack-boundary-banner"', html)
        self.assertIn('info.profile_pack', script)
        self.assertIn('pack.pack_name', script)
        self.assertIn('request("/api/profile-packs")', script)
        self.assertIn("Camera Lab evidence can be deliberately promoted", script)
        self.assertIn('"review-build"', script)
        self.assertIn("configureExternalEvidenceReview", script)
        self.assertIn("enforceExternalPackBoundary", script)
        self.assertIn('"setup-sharing"', script)
        self.assertIn('profilePackCreationPanel.hidden = state.externalPack', script)
        self.assertIn("Create another pack", html)
        self.assertIn('id="profile-pack-git-panel"', html)
        self.assertIn('id="combined-handoff-status"', html)
        self.assertIn('request("/api/profile-pack-git-status"', script)
        self.assertIn("AGENTS.md is included", script)
        self.assertIn("external-pack-boundary-banner", styles)
        self.assertIn("#session-summary[hidden]", styles)

    def test_external_camera_lab_evidence_updates_only_active_pack_status(self):
        workspace = Path(self.temporary.name) / "evidence-workspace"
        application_status = PROJECT_ROOT / "90 Testing" / "eos_r5_verification_status.yaml"
        application_before = application_status.read_bytes()
        pack_status = self.pack / "90 Testing" / "eos_r5_verification_status.yaml"
        pack_before = pack_status.read_bytes()
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            model = ProfileEditorModel(
                PROJECT_ROOT,
                profile_pack_root=self.pack,
                source_validator=lambda _paths: [],
            )
            journal_root = model.paths.local_workspace_dir / "Camera Lab" / "Guarded Runs"
            journal_root.mkdir(parents=True)
            session_id = "5" * 32
            journal = {
                "schema_version": 1,
                "backend": "edsdk",
                "status": "complete",
                "session_id": session_id,
                "profile_pack": {
                    "mode": "external",
                    "pack_id": model.paths.profile_pack.pack_id,
                    "pack_name": model.paths.profile_pack.pack_name,
                },
                "profile": {"name": "Wildlife", "title": "Wildlife"},
                "camera": {"firmware": "2.2.1"},
                "completed_at": "2026-09-03T15:00:00-04:00",
                "steps": [
                    {
                        "path": "exposure.metering",
                        "property_key": "metering_mode",
                        "label": "Metering",
                        "target": "Evaluative",
                        "status": "camera_verified",
                        "evidence_method": "sdk_written_and_verified",
                        "completed_at": "2026-09-03T15:00:00-04:00",
                    }
                ],
            }
            (journal_root / f"{session_id}.json").write_text(
                json.dumps(journal) + "\n", encoding="utf-8"
            )
            inventory = model.camera_lab_evidence_detail()
            self.assertEqual(inventory["eligibleCount"], 1)
            self.assertNotIn(str(workspace), json.dumps(inventory))
            candidate = next(item for item in inventory["candidates"] if not item["alreadyImported"])
            review = model.review_camera_lab_evidence([candidate["candidateId"]], 0)
            result = model.save_camera_lab_evidence(review["reviewToken"], True)
            model.accept_profile_pack_state()

        self.assertNotEqual(pack_status.read_bytes(), pack_before)
        self.assertEqual(application_status.read_bytes(), application_before)
        self.assertFalse((workspace / "Profile Packs" / model.paths.profile_pack.pack_id / "Verification").exists())
        backup = Path(result["backup"])
        self.assertTrue(backup.is_relative_to((workspace / "Profile Packs").resolve()))
        transaction = json.loads((backup / "transaction.json").read_text(encoding="utf-8"))
        self.assertEqual(transaction["profile_pack"]["pack_id"], model.paths.profile_pack.pack_id)
        saved = yaml.safe_load(pack_status.read_text(encoding="utf-8"))
        self.assertTrue(
            any(
                entry.get("event") == "camera_lab_evidence_import"
                and entry.get("id") == candidate["candidateId"]
                for entry in saved["history"]
            )
        )

    def test_external_camera_lab_evidence_rejects_missing_or_other_pack_identity(self):
        journal_root = Path(self.temporary.name) / "foreign-journals"
        journal_root.mkdir()
        for index, recorded_pack in enumerate((None, {"pack_id": "00000000-0000-4000-8000-000000000001"})):
            session_id = str(index + 6) * 32
            record = {
                "schema_version": 1,
                "backend": "edsdk",
                "status": "complete",
                "session_id": session_id,
                "profile": {"name": "Wildlife", "title": "Wildlife"},
                "camera": {"firmware": "2.2.1"},
                "completed_at": "2026-09-03T15:00:00-04:00",
                "steps": [],
            }
            if recorded_pack is not None:
                record["profile_pack"] = recorded_pack
            (journal_root / f"{session_id}.json").write_text(
                json.dumps(record) + "\n", encoding="utf-8"
            )
        model = ProfileEditorModel(
            PROJECT_ROOT,
            profile_pack_root=self.pack,
            camera_lab_journal_root=journal_root,
        )
        inventory = model.camera_lab_evidence_detail()
        self.assertEqual(inventory["eligibleCount"], 0)
        self.assertEqual(len(inventory["sessions"]), 2)
        self.assertTrue(
            all("does not belong" in item["skippedReason"] for item in inventory["sessions"])
        )

    def test_guarded_switch_uses_manifest_name_and_persists_without_returning_path(self):
        workspace = Path(self.temporary.name) / "switch-workspace"
        second_pack = Path(self.temporary.name) / "second-pack"
        write_pack_from_embedded_sources(second_pack)
        manifest_path = second_pack / "profile-pack.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest["pack_id"] = "439f0b7d-b965-4e41-ae32-e2b159ff5599"
        manifest["pack_name"] = "Andy's Travel Camera Profiles"
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            store = ProfilePackSelectionStore(PROJECT_ROOT)

            class BoundHandler(EditorHandler):
                model = self.model
                selection_store = store
                model_switch_lock = threading.Lock()

            handler = object.__new__(BoundHandler)
            with self.assertRaisesRegex(PrototypeError, "Save or discard"):
                handler._switch_profile_pack(
                    {"path": str(second_pack), "pendingChanges": 1, "confirmSwitch": True}
                )
            result = handler._switch_profile_pack(
                {"path": str(second_pack), "pendingChanges": 0, "confirmSwitch": True}
            )
            selected = store.selected_context()
        self.assertEqual(result["profile_pack"]["pack_name"], "Andy's Travel Camera Profiles")
        self.assertEqual(selected.pack_name, "Andy's Travel Camera Profiles")
        self.assertNotIn(str(second_pack), json.dumps(result))
        self.assertEqual(BoundHandler.model.paths.profile_pack.pack_id, selected.pack_id)

    def test_my_menu_color_save_changes_only_pack_and_records_pack_backup(self):
        workspace = Path(self.temporary.name) / "workspace"
        application_source = PROJECT_ROOT / "00 Master" / "my_menu_colors.yaml"
        pack_source = self.pack / "00 Master" / "my_menu_colors.yaml"
        application_before = application_source.read_bytes()
        pack_before = pack_source.read_bytes()
        assignments = dict(self.model.my_menu_colors["assignments"])
        names = list(assignments)
        assignments[names[0]], assignments[names[1]] = assignments[names[1]], assignments[names[0]]
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            review = self.model.review_my_menu_colors(assignments)
            result = self.model.save_my_menu_colors(review["reviewToken"])
            self.model.accept_profile_pack_state()
        self.assertNotEqual(pack_source.read_bytes(), pack_before)
        self.assertEqual(application_source.read_bytes(), application_before)
        backup = Path(result["backup"])
        self.assertTrue(backup.is_relative_to((workspace / "Profile Packs").resolve()))
        manifest = json.loads((backup / "transaction.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["profile_pack"]["pack_id"], self.model.paths.profile_pack.pack_id)
        self.model.assert_profile_pack_current()

    def test_failed_external_save_restores_pack_bytes(self):
        workspace = Path(self.temporary.name) / "rollback-workspace"
        source = self.pack / "00 Master" / "my_menu_colors.yaml"
        before = source.read_bytes()
        model = ProfileEditorModel(
            PROJECT_ROOT,
            profile_pack_root=self.pack,
            source_validator=lambda _paths: ["forced external validation failure"],
        )
        assignments = dict(model.my_menu_colors["assignments"])
        names = list(assignments)
        assignments[names[0]], assignments[names[1]] = assignments[names[1]], assignments[names[0]]
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            review = model.review_my_menu_colors(assignments)
            with self.assertRaisesRegex(PrototypeError, "prior source state was restored"):
                model.save_my_menu_colors(review["reviewToken"])
        self.assertEqual(source.read_bytes(), before)

    def test_profile_save_changes_only_pack_profile_and_records_pack_backup(self):
        workspace = Path(self.temporary.name) / "profile-workspace"
        application_source = PROJECT_ROOT / "10 Profiles" / "Fireworks.yaml"
        application_guidance = PROJECT_ROOT / "00 Master" / "profile_lens_guidance.yaml"
        pack_source = self.pack / "10 Profiles" / "Fireworks.yaml"
        pack_guidance = self.pack / "00 Master" / "profile_lens_guidance.yaml"
        application_before = application_source.read_bytes()
        application_guidance_before = application_guidance.read_bytes()
        pack_before = pack_source.read_bytes()
        pack_guidance_before = pack_guidance.read_bytes()
        payload = self.profile_payload(subtitle="External profile-pack transaction test")
        payload["lensChoices"][0]["useWhen"] += " from the private pack"
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            review = self.model.review_profile(
                payload
            )
            result = self.model.save_profile(review["reviewToken"])
            self.model.accept_profile_pack_state()
        self.assertNotEqual(pack_source.read_bytes(), pack_before)
        self.assertNotEqual(pack_guidance.read_bytes(), pack_guidance_before)
        self.assertEqual(application_source.read_bytes(), application_before)
        self.assertEqual(application_guidance.read_bytes(), application_guidance_before)
        manifest = json.loads((Path(result["backup"]) / "transaction.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["profile_pack"]["pack_id"], self.model.paths.profile_pack.pack_id)
        self.model.assert_profile_pack_current()

    def test_cx_assignment_save_changes_pack_sources_without_legacy_app_mirror(self):
        workspace = Path(self.temporary.name) / "cx-workspace"
        application_mirror = PROJECT_ROOT / "data" / "canon_r5_custom_controls_current.yaml"
        application_before = application_mirror.read_bytes()
        pack_controls = self.pack / "controls.yaml"
        pack_before = pack_controls.read_bytes()
        assignments = self.model._cx_assignments()
        assignments["C1"], assignments["C3"] = assignments["C3"], assignments["C1"]
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            review = self.model.review_cx_assignments(assignments)
            self.assertNotIn("--- a/data/canon_r5_custom_controls_current.yaml", review["diff"])
            result = self.model.save_cx_review(review["reviewToken"])
            self.model.accept_profile_pack_state()
        self.assertNotEqual(pack_controls.read_bytes(), pack_before)
        self.assertEqual(application_mirror.read_bytes(), application_before)
        manifest = json.loads((Path(result["backup"]) / "transaction.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["profile_pack"]["pack_id"], self.model.paths.profile_pack.pack_id)
        self.model.assert_profile_pack_current()

    def test_camera_buttons_save_changes_pack_without_legacy_app_mirror(self):
        workspace = Path(self.temporary.name) / "buttons-workspace"
        application_mirror = PROJECT_ROOT / "data" / "canon_r5_custom_controls_current.yaml"
        application_before = application_mirror.read_bytes()
        pack_controls = self.pack / "controls.yaml"
        pack_before = pack_controls.read_bytes()
        detail = self.model.control_editor_detail()
        af_on = next(item for item in detail["controls"] if item["control"] == "AF-ON")
        af_on["assignment"] = "Metering start"
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            review = self.model.review_control_editor(
                {"controls": detail["controls"], "dials": detail["dials"]}
            )
            self.assertEqual(review["sourceFiles"], ["controls.yaml"])
            result = self.model.save_control_editor(review["reviewToken"])
            self.model.accept_profile_pack_state()
        self.assertNotEqual(pack_controls.read_bytes(), pack_before)
        self.assertEqual(application_mirror.read_bytes(), application_before)
        manifest = json.loads((Path(result["backup"]) / "transaction.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["profile_pack"]["pack_id"], self.model.paths.profile_pack.pack_id)
        self.model.assert_profile_pack_current()

    def test_deleted_cards_remove_and_restore_stay_namespaced_to_pack(self):
        workspace = Path(self.temporary.name) / "deleted-workspace"
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            self.create_unreleased_profile("External Removal Test")
            detail = self.model.profile_detail("External Removal Test")
            review = self.model.review_profile_removal(
                "External Removal Test", detail["sourceFingerprint"]
            )
            removed = self.model.save_profile_removal(review["reviewToken"])
            self.model.accept_profile_pack_state()
            entries = self.model.deleted_cards()
            self.assertEqual([item["cardId"] for item in entries], [detail["cardId"]])
            restore = self.model.review_profile_restore(detail["cardId"])
            restored = self.model.save_profile_restore(restore["reviewToken"])
            self.model.accept_profile_pack_state()
        self.assertTrue((self.pack / "10 Profiles" / "External Removal Test.yaml").is_file())
        self.assertEqual(self.model.deleted_cards(), [])
        self.assertTrue(Path(removed["backup"]).is_relative_to((workspace / "Profile Packs").resolve()))
        self.assertTrue(Path(restored["backup"]).is_relative_to((workspace / "Profile Packs").resolve()))
        self.model.assert_profile_pack_current()

    def test_my_menu_layout_save_changes_only_pack_sources(self):
        workspace = Path(self.temporary.name) / "menu-layout-workspace"
        application_sources = [
            PROJECT_ROOT / "00 Master" / "my_menu.yaml",
            PROJECT_ROOT / "00 Master" / "my_menu_colors.yaml",
        ]
        application_before = {path: path.read_bytes() for path in application_sources}
        tabs = [
            {
                "name": "SWITCH",
                "colorChoice": "Green",
                "items": ["af1_subject_to_detect", "shoot6_shutter_mode"],
            },
            {
                "name": "FIELD",
                "colorChoice": "Light Red",
                "items": ["shoot7_is_mode", "shoot1_cropping_aspect_ratio"],
            },
        ]
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            review = self.model.review_my_menu_configuration(tabs)
            result = self.model.save_my_menu_configuration(review["reviewToken"])
            self.model.accept_profile_pack_state()
        self.assertEqual(
            [tab["name"] for tab in self.model.my_menu["tabs"]],
            ["SWITCH", "FIELD"],
        )
        self.assertEqual({path: path.read_bytes() for path in application_sources}, application_before)
        manifest = json.loads((Path(result["backup"]) / "transaction.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["profile_pack"]["pack_id"], self.model.paths.profile_pack.pack_id)
        self.model.assert_profile_pack_current()

    def test_baseline_migration_changes_only_pack_and_validates_combined_sources(self):
        workspace = Path(self.temporary.name) / "baseline-workspace"
        application_baseline = PROJECT_ROOT / "00 Master" / "baseline.yaml"
        application_before = application_baseline.read_bytes()
        pack_baseline = self.pack / "00 Master" / "baseline.yaml"
        pack_before = pack_baseline.read_bytes()
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            review = self.model.review_baseline_migration(self.migration_payload())
            result = self.model.save_baseline_migration(review["reviewToken"])
            self.model.accept_profile_pack_state()
        self.assertNotEqual(pack_baseline.read_bytes(), pack_before)
        self.assertEqual(application_baseline.read_bytes(), application_before)
        manifest = json.loads((Path(result["backup"]) / "transaction.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["profile_pack"]["pack_id"], self.model.paths.profile_pack.pack_id)
        self.model.assert_profile_pack_current()


if __name__ == "__main__":
    unittest.main()
