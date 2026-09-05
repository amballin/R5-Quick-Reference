#!/usr/bin/env python3
"""Integration tests for guarded Stage 2 profile-editor transactions."""

from copy import deepcopy
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent

import sys

if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from profile_editor import (
    GuardedJobManager,
    MAIN_EDITOR_PORT,
    PROTOTYPE_EDITOR_PORT,
    ProfileConflictError,
    ProfileEditorModel,
    PrototypeError,
    create_server,
    default_editor_port,
)
from profile_loader import load_yaml
from application_version import application_version_info
from project_context import project_context_info
from validators import control_validator, profile_validator, spreadsheet_spec_validator


class ProfileEditorTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="profile-editor-tests-")
        self.root = Path(self.temporary.name) / "repository"
        self.root.mkdir()
        for directory in ("00 Master", "10 Profiles", "20 Templates", "50 Field Guide", "60 Assets", "90 Testing", "data"):
            shutil.copytree(PROJECT_ROOT / directory, self.root / directory)
        shutil.copy2(PROJECT_ROOT / "controls.yaml", self.root / "controls.yaml")
        catalog = self.root / "80 Build" / "profile_editor" / "canon_options.yaml"
        catalog.parent.mkdir(parents=True)
        shutil.copy2(PROJECT_ROOT / "80 Build" / "profile_editor" / "canon_options.yaml", catalog)
        shutil.copy2(
            PROJECT_ROOT / "80 Build" / "profile_editor" / "control_options.yaml",
            catalog.parent / "control_options.yaml",
        )
        for relative in (
            "80 Build/baseline_impact.py",
            "80 Build/application_version.py",
            "80 Build/baseline_migration.py",
            "80 Build/card_identity.py",
            "80 Build/cx_route_analysis.py",
            "80 Build/feature_interactions.py",
            "80 Build/finish_day.py",
            "80 Build/integrate_branch.py",
            "80 Build/cleanup_review.py",
            "80 Build/lens_guidance.py",
            "80 Build/html_renderer.py",
            "80 Build/my_menu.py",
            "80 Build/my_menu_colors.py",
            "80 Build/my_menu_reference.py",
            "80 Build/numbers_automation.py",
            "80 Build/control_reference.py",
            "80 Build/camera_lab_tracker_import.py",
            "80 Build/asset_manager.py",
            "80 Build/profile_editor.py",
            "80 Build/profile_pack_git.py",
            "80 Build/profile_pack.py",
            "80 Build/profile_pack_creation.py",
            "80 Build/profile_pack_templates/AGENTS.md",
            "80 Build/profile_pack_selection.py",
            "80 Build/profile_editor/app.js",
            "80 Build/profile_editor/index.html",
            "80 Build/profile_editor/styles.css",
            "80 Build/project_context.py",
            "80 Build/publication_workflow.py",
            "80 Build/release_notes.py",
            "80 Build/spreadsheet_revisions.py",
            "80 Build/spreadsheet_downloads.py",
            "80 Build/subject_settings_matrix.py",
            "80 Build/camera_setup_tracker.py",
            "80 Build/render_subject_settings_matrix.mjs",
            "80 Build/render_camera_setup_tracker.mjs",
            "80 Build/spreadsheet_ooxml.py",
            "80 Build/publish_metadata.yaml",
            "80 Build/scripts/profile-editor-runtime.sh",
            "80 Build/scripts/build-all-spreadsheet-downloads.sh",
            "80 Build/scripts/preflight-git.sh",
            "80 Build/scripts/git-status-report.sh",
            "80 Build/scripts/publish.sh",
            "80 Build/scripts/start-profile-editor.sh",
            "80 Build/scripts/stop-profile-editor.sh",
        ):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PROJECT_ROOT / relative, destination)
        self.model = ProfileEditorModel(
            self.root,
            source_validator=lambda _root: [],
            derived_artifact_checker=lambda: {
                "status": "current",
                "refreshNeeded": False,
                "details": [],
                "blockers": [],
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def payload(self, name="Fireworks", **changes):
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
                "displayCategory": "subject",
                "release": False,
                "overrides": draft["originalOverrides"],
                "lensChoices": [
                    {
                        "lensId": "rf_24_240_is",
                        "accessoryId": "",
                        "role": "primary",
                        "useWhen": "General field use",
                        "fieldCheck": "Confirm framing and stabilization",
                    }
                ],
                "lensGuidanceFingerprint": draft["lensGuidanceFingerprint"],
            }
        )
        self.model.save_profile(review["reviewToken"])
        return self.model.profile_detail(name)

    def migration_payload(self, model=None, **changes):
        model = model or self.model
        values = dict(model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        analysis = model.baseline_impact(values)
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
        payload = {
            "values": values,
            "decisions": decisions,
            "myMenuTabs": None,
            "acknowledgeCxImpact": True,
            "acknowledgeMyMenuImpact": True,
        }
        payload.update(changes)
        return payload

    def test_updates_existing_profile_after_exact_review(self):
        review = self.model.review_profile(self.payload(title="Fireworks Review Test"))
        self.assertIn("Fireworks Review Test", review["diff"])
        self.assertEqual(review["sourceFiles"], ["10 Profiles/Fireworks.yaml"])
        result = self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Fireworks.yaml")
        self.assertEqual(saved["title"], "Fireworks Review Test")
        self.assertEqual(result["validation"], "passed")
        self.assertTrue(Path(result["backup"]).is_dir())

    def test_cx_foundation_fit_recommends_lowest_visible_row_count_without_selecting_it(self):
        detail = self.model.cx_foundation_detail("Wildlife")
        by_start = {item["start"]: item for item in detail["fit"]}

        self.assertEqual(detail["assignments"]["C1"], "Wildlife")
        self.assertEqual(by_start["C1"]["change_count"], 0)
        self.assertTrue(by_start["C1"]["recommended"])
        self.assertEqual(detail["selectedStart"], "C1")
        self.assertTrue(all(item["total_rows"] > 0 for item in detail["fit"]))

    def test_cx_assignments_require_three_distinct_editable_profiles(self):
        with self.assertRaisesRegex(PrototypeError, "three different profiles"):
            self.model.review_cx_assignments(
                {"C1": "Wildlife", "C2": "Wildlife", "C3": "Landscape"}
            )

    def test_cx_selection_review_changes_only_the_selected_card_route(self):
        review = self.model.review_cx_selection("Fireworks", "C1")

        self.assertEqual(review["reviewKind"], "selection")
        self.assertIn("10 Profiles/Fireworks.yaml", review["diff"])
        self.assertIn("start: C1", review["diff"])
        wildlife_id = load_yaml(self.root / "10 Profiles" / "Wildlife.yaml")["card_id"]
        self.assertIn(f"source_card_id: {wildlife_id}", review["diff"])

        result = self.model.save_cx_review(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Fireworks.yaml")
        self.assertEqual(saved["card"]["field_setup"]["start"], "C1")
        self.assertEqual(saved["card"]["field_setup"]["source_card_id"], wildlife_id)
        self.assertEqual(result["validation"], "passed")

    def test_cx_assignment_save_synchronizes_controls_registration_and_card_routes(self):
        assignments = {"C1": "Landscape", "C2": "Birds in Flight", "C3": "Wildlife"}
        rows_before = deepcopy(load_yaml(self.root / "90 Testing" / "eos_r5_verification_tracker.yaml")["registration"]["rows"])
        review = self.model.review_cx_assignments(assignments)

        self.assertEqual(review["reviewKind"], "assignments")
        self.assertIn("controls.yaml", review["diff"])
        self.assertIn("90 Testing/eos_r5_verification_tracker.yaml", review["diff"])
        result = self.model.save_cx_review(review["reviewToken"])

        controls = load_yaml(self.root / "controls.yaml")
        current = load_yaml(self.root / "data" / "canon_r5_custom_controls_current.yaml")
        tracker = load_yaml(self.root / "90 Testing" / "eos_r5_verification_tracker.yaml")
        wildlife = load_yaml(self.root / "10 Profiles" / "Wildlife.yaml")
        landscape = load_yaml(self.root / "10 Profiles" / "Landscape.yaml")
        self.assertEqual(controls["custom_shooting_modes"]["C1"]["profile_id"], landscape["card_id"])
        self.assertEqual(current["custom_shooting_modes"]["C3"]["profile_id"], wildlife["card_id"])
        self.assertEqual(
            controls["custom_shooting_modes"]["C1"]["status"],
            "approved_target_pending_camera_verification",
        )
        self.assertEqual(controls["custom_shooting_modes"]["C2"]["status"], "owner_confirmed")
        self.assertEqual(
            current["custom_shooting_modes"]["C3"]["status"],
            "approved_target_pending_camera_verification",
        )
        self.assertNotIn("unresolved_items", controls["custom_shooting_modes"]["C1"])
        self.assertEqual(
            controls["custom_shooting_modes"]["registration_state"]["C1"],
            "approved_target_pending_camera_verification",
        )
        self.assertEqual(
            [item["heading"] for item in tracker["registration"]["profiles"]],
            ["C1 Landscape", "C2 Birds in Flight", "C3 Wildlife"],
        )
        self.assertEqual(tracker["registration"]["rows"], rows_before)
        self.assertEqual(wildlife["card"]["field_setup"]["source_card_id"], landscape["card_id"])
        self.assertEqual(landscape["card"]["field_setup"]["source_card_id"], wildlife["card_id"])
        self.assertEqual(result["assignments"], assignments)
        self.assertFalse([issue for issue in control_validator.validate(self.root) if issue.level == "error"])

    def test_camera_buttons_review_synchronizes_sources_and_downgrades_changed_confirmation(self):
        detail = self.model.control_editor_detail()
        af_on = next(item for item in detail["controls"] if item["control"] == "AF-ON")
        af_on["assignment"] = "Metering start"
        af_on["status"] = "owner_confirmed"
        review = self.model.review_control_editor(
            {"controls": detail["controls"], "dials": detail["dials"]}
        )
        self.assertIn("controls.yaml", review["diff"])
        self.assertIn("data/canon_r5_custom_controls_current.yaml", review["diff"])
        self.assertNotIn("custom_shooting_modes:", review["diff"])
        self.assertNotIn("retired_evidence:", review["diff"])
        result = self.model.save_control_editor(review["reviewToken"])
        self.assertEqual(result["validation"], "passed")
        project = load_yaml(self.root / "controls.yaml")
        current = load_yaml(self.root / "data" / "canon_r5_custom_controls_current.yaml")
        project_af_on = next(item for item in project["controls"] if item["control"] == "AF-ON")
        current_af_on = next(item for item in current["buttons"] if item["control"] == "AF-ON")
        self.assertEqual(project_af_on["status"], "approved_target_pending_camera_verification")
        self.assertEqual(current_af_on["status"], "approved_target_pending_camera_verification")
        self.assertEqual(project_af_on["assignment"], current_af_on["assignment"])
        self.assertFalse([issue for issue in control_validator.validate(self.root) if issue.level == "error"])

    def test_camera_buttons_editor_exposes_defaults_options_icons_and_plain_status_help(self):
        detail = self.model.control_editor_detail()
        af_on = detail["options"]["controls"]["AF-ON"]
        self.assertEqual(af_on["default"], "Metering and AF start")
        self.assertIn("Face + Tracking", af_on["info_fields"]["AF Method"]["options"])
        self.assertIn("icon_btn-af-on.svg", af_on["iconUrl"])
        self.assertTrue(all(
            detail["options"][group][item["control"]].get("default")
            for group in ("controls", "dials")
            for item in detail[group]
        ))
        self.assertTrue(all(
            detail["options"][group][item["control"]].get("iconUrl")
            for group in ("controls", "dials")
            for item in detail[group]
        ))
        confirmed = next(
            option for option in detail["evidenceStatusOptions"]
            if option["value"] == "owner_confirmed"
        )
        self.assertIn("Physically checked", confirmed["help"])

    def test_camera_buttons_preview_uses_unsaved_candidate_without_writing_source(self):
        detail = self.model.control_editor_detail()
        source = self.root / "controls.yaml"
        before = source.read_bytes()
        af_on = next(item for item in detail["controls"] if item["control"] == "AF-ON")
        af_on["assignment"] = "Metering start"
        movie = next(item for item in detail["controls"] if item["control"] == "Movie Record")
        movie["assignment"] = "Movie recording"
        preview = self.model.preview_control_editor({
            "controls": detail["controls"],
            "dials": detail["dials"],
        })
        rendered = preview.read_text(encoding="utf-8")
        self.assertIn("Metering start", rendered)
        self.assertIn("icon_btn-af-on.svg", rendered)
        self.assertIn("Movie Record", rendered)
        self.assertIn("icon_btn-mov.svg", rendered)
        self.assertEqual(source.read_bytes(), before)

    def test_camera_lab_evidence_review_promotes_only_exact_physical_configured_state(self):
        journal_root = Path(self.temporary.name) / "guarded-runs"
        journal_root.mkdir()
        session_id = "a" * 32
        (journal_root / f"{session_id}.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "backend": "edsdk",
                    "status": "complete",
                    "session_id": session_id,
                    "profile": {"name": "Wildlife", "title": "Wildlife"},
                    "camera": {"firmware": "2.2.1"},
                    "completed_at": "2026-08-30T12:00:00-04:00",
                    "steps": [
                        {
                            "path": "exposure.metering",
                            "property_key": "metering_mode",
                            "label": "Metering",
                            "target": "Evaluative",
                            "status": "camera_verified",
                            "evidence_method": "sdk_written_and_verified",
                            "completed_at": "2026-08-30T12:00:00-04:00",
                        },
                        {
                            "path": "exposure.metering",
                            "property_key": "metering_mode",
                            "label": "Metering duplicate",
                            "target": "Evaluative",
                            "status": "camera_verified",
                            "evidence_method": "sdk_written_and_verified",
                            "completed_at": "2026-08-30T12:00:01-04:00",
                        },
                        {
                            "path": "lens.aperture.note",
                            "label": "Aperture note",
                            "target": "Manual context",
                            "status": "manual_user_confirmed",
                            "evidence_method": "manual_group_user_confirmed",
                        },
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        model = ProfileEditorModel(
            self.root,
            source_validator=lambda _root: [],
            camera_lab_journal_root=journal_root,
        )
        inventory = model.camera_lab_evidence_detail()
        self.assertEqual(inventory["eligibleCount"], 1)
        item = next(candidate for candidate in inventory["candidates"] if not candidate["alreadyImported"])
        read_back_before = load_yaml(
            self.root / "90 Testing" / "eos_r5_verification_status.yaml"
        )["registration"]["Metering"].get("c1_read_back")
        review = model.review_camera_lab_evidence([item["candidateId"]], 0)
        self.assertIn("camera_lab_evidence_import", review["diff"])
        with patch("verification_status.build_working_copy"):
            result = model.save_camera_lab_evidence(review["reviewToken"], True)
        self.assertEqual(result["validation"], "passed")
        status = load_yaml(self.root / "90 Testing" / "eos_r5_verification_status.yaml")
        self.assertEqual(status["registration"]["Metering"]["c1_configured"], "Pass")
        self.assertEqual(status["registration"]["Metering"].get("c1_read_back"), read_back_before)
        self.assertTrue(
            any(entry.get("event") == "camera_lab_evidence_import" for entry in status["history"])
        )
        self.assertFalse([issue for issue in profile_validator.validate(self.root) if issue.level == "error"])
        with self.assertRaisesRegex(ProfileConflictError, "expired or was already used"):
            self.model.save_cx_review(review["reviewToken"])

    def test_no_cx_selection_preserves_my_menu_routes(self):
        before = load_yaml(self.root / "10 Profiles" / "People.yaml")
        menus = deepcopy(before["card"]["field_setup"]["my_menus"])
        review = self.model.review_cx_selection("People", "")
        self.model.save_cx_review(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "People.yaml")

        self.assertNotIn("start", saved["card"]["field_setup"])
        self.assertNotIn("source_profile", saved["card"]["field_setup"])
        self.assertEqual(saved["card"]["field_setup"]["my_menus"], menus)

    def test_cx_assignment_validation_failure_rolls_back_every_written_file(self):
        model = ProfileEditorModel(self.root, source_validator=lambda _root: ["forced failure"])
        assignments = {"C1": "Landscape", "C2": "Birds in Flight", "C3": "Wildlife"}
        paths = [
            self.root / "controls.yaml",
            self.root / "data" / "canon_r5_custom_controls_current.yaml",
            self.root / "90 Testing" / "eos_r5_verification_tracker.yaml",
            self.root / "10 Profiles" / "Wildlife.yaml",
            self.root / "10 Profiles" / "Landscape.yaml",
        ]
        before = {path: path.read_bytes() for path in paths}
        review = model.review_cx_assignments(assignments)

        with self.assertRaisesRegex(PrototypeError, "prior source was restored"):
            model.save_cx_review(review["reviewToken"])
        self.assertEqual({path: path.read_bytes() for path in paths}, before)

    def test_cx_foundation_is_a_separate_workspace_after_profiles(self):
        html = (self.root / "80 Build" / "profile_editor" / "index.html").read_text(encoding="utf-8")
        script = (self.root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")

        self.assertLess(html.index('data-view="profiles"'), html.index('data-view="cx-foundation"'))
        self.assertLess(html.index('data-view="cx-foundation"'), html.index('data-view="my-menu"'))
        self.assertIn('id="cx-fit-results"', html)
        self.assertIn("item.recommended", script)
        self.assertIn('badge.textContent = "Your selection"', script)
        self.assertIn("if (occupiedStart) state.cxAssignments[occupiedStart] = previous", script)
        self.assertIn("The lowest-change result is a recommendation only", script)

        styles = (self.root / "80 Build" / "profile_editor" / "styles.css").read_text(encoding="utf-8")
        self.assertIn('.cx-fit-option input[type="radio"]', styles)
        self.assertIn("width: 1.2rem", styles)
        self.assertIn("@media (max-width: 1450px)", styles)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", styles)

    def test_review_shows_effective_value_when_override_returns_to_auto_baseline(self):
        payload = self.payload("Fireworks")
        overrides = dict(payload["overrides"])
        self.assertEqual(overrides.pop("lens.aperture.target"), "f/8–f/11")
        review = self.model.review_profile({**payload, "overrides": overrides})

        aperture = next(
            change for change in review["effectiveChanges"]
            if change["path"] == "lens.aperture.target"
        )
        self.assertEqual(aperture["beforeDisplay"], "f/8–f/11")
        self.assertEqual(aperture["beforeSource"], "profile customization")
        self.assertEqual(aperture["afterDisplay"], "Auto")
        self.assertEqual(aperture["afterSource"], "inherited from baseline")
        self.assertIn("-      target: f/8–f/11", review["diff"])

    def test_profile_review_dialog_renders_effective_changes_before_exact_yaml(self):
        html = (self.root / "80 Build" / "profile_editor" / "index.html").read_text(encoding="utf-8")
        script = (self.root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="review-effective-list"', html)
        self.assertLess(html.index("Effective setting changes"), html.index("Exact YAML changes"))
        self.assertIn("review.effectiveChanges || []", script)
        self.assertIn("change.afterDisplay", script)

    def test_recognized_text_values_use_canonical_case_for_every_setting(self):
        checked = []
        for path, baseline in self.model.default_fields.items():
            if not isinstance(baseline, str) or not any(character.isalpha() for character in baseline):
                continue
            mixed_case = baseline.swapcase()
            clean = self.model._validate_overrides({path: mixed_case})
            self.assertEqual(clean, {}, f"{path} did not normalize {mixed_case!r} to {baseline!r}")
            checked.append(path)
        self.assertIn("lens.aperture.target", checked)
        self.assertIn("autofocus.method", checked)
        self.assertIn("drive.mode", checked)

    def test_case_normalization_preserves_unrecognized_custom_values(self):
        clean = self.model._validate_overrides({"lens.aperture.target": "f/8"})
        self.assertEqual(clean, {"lens.aperture.target": "f/8"})

    def test_blank_restores_baseline_for_every_setting_type(self):
        checked = []
        for path in self.model.default_fields:
            clean = self.model._validate_overrides({path: ""})
            self.assertEqual(clean, {}, f"{path} retained a blank override")
            checked.append(path)
        self.assertIn("lens.aperture.target", checked)
        self.assertIn("exposure.auto_iso.maximum", checked)
        self.assertIn("exposure.iso.value", checked)

    def test_mixed_case_auto_review_is_inherited_not_an_override(self):
        payload = self.payload("Travel")
        overrides = dict(payload["overrides"])
        overrides["lens.aperture.target"] = "AUto"
        review = self.model.review_profile({**payload, "title": "Travel normalization test", "overrides": overrides})

        self.assertFalse(any(
            change["path"] == "lens.aperture.target"
            for change in review["effectiveChanges"]
        ))
        self.assertNotIn("AUto", review["candidateYaml"])
        self.assertNotIn("aperture:", review["candidateYaml"])

    def test_browser_normalizes_recognized_free_text_choices_before_override_comparison(self):
        script = (self.root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")
        self.assertIn('choice.value.toLocaleLowerCase("en-US")', script)
        self.assertIn('control.value.toLocaleLowerCase("en-US")', script)
        self.assertIn("return canonical ? canonical.value : control.value", script)
        self.assertIn("updateSetting(setting, value, blanked || recognizedSpellingChanged)", script)

    def test_blank_input_repopulates_the_baseline_and_stage_label_is_removed(self):
        html = (self.root / "80 Build" / "profile_editor" / "index.html").read_text(encoding="utf-8")
        script = (self.root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("Stage 3 · Review &amp; Build", html)
        self.assertIn('if (control.value === "") return setting.baseline', script)
        self.assertIn("updateSetting(setting, value, blanked || recognizedSpellingChanged)", script)

    def test_creates_baseline_derived_profile_as_unreleased_draft(self):
        detail = self.model.profile_draft("create")
        payload = {
            "operation": "create",
            "sourceProfile": None,
            "targetName": "Rainy Day",
            "sourceFingerprint": None,
            "title": "Rainy Day",
            "subtitle": "Baseline test",
            "status": "Final",
            "displayCategory": "subject",
            "release": True,
            "overrides": {"drive.mode": "Single Shot"},
            "lensChoices": [
                {
                    "lensId": "rf_24_240_is",
                    "accessoryId": "",
                    "role": "primary",
                    "useWhen": "General field use",
                    "fieldCheck": "Confirm framing and stabilization",
                }
            ],
            "lensGuidanceFingerprint": detail["lensGuidanceFingerprint"],
        }
        self.assertEqual(detail["metadata"], {"status": "Draft", "release": False})
        review = self.model.review_profile(payload)
        self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Rainy Day.yaml")
        self.assertEqual(saved["metadata"]["status"], "Draft")
        self.assertFalse(saved["metadata"]["release"])
        self.assertRegex(saved["card_id"], r"^[0-9a-f-]{36}$")
        self.assertEqual(saved["inherits"], "baseline")
        self.assertEqual(saved["overrides"], {"drive": {"mode": "Single Shot"}})

    def test_new_profile_filename_follows_title_until_manually_changed(self):
        script = (self.root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function profileFilenameFromTitle(title)", script)
        self.assertIn('state.filenameFollowsTitle = detail.operation === "create"', script)
        self.assertIn("elements.filenameInput.value = profileFilenameFromTitle(elements.titleInput.value)", script)
        self.assertIn("state.filenameFollowsTitle = false", script)

    def test_rejects_an_existing_new_profile_filename_case_insensitively(self):
        detail = self.model.profile_draft("create")
        payload = {
            "operation": "create",
            "sourceProfile": None,
            "targetName": "fireworks",
            "sourceFingerprint": None,
            "title": "Another Fireworks Card",
            "subtitle": "",
            "status": "Draft",
            "displayCategory": "subject",
            "release": False,
            "overrides": detail["originalOverrides"],
            "lensChoices": [
                {
                    "lensId": "rf_24_240_is",
                    "accessoryId": "",
                    "role": "primary",
                    "useWhen": "General field use",
                    "fieldCheck": "Confirm framing and stabilization",
                }
            ],
            "lensGuidanceFingerprint": detail["lensGuidanceFingerprint"],
        }
        with self.assertRaisesRegex(ProfileConflictError, "already exists"):
            self.model.review_profile(payload)

    def test_profile_section_is_editable_and_new_profile_appears_in_cx_foundation(self):
        detail = self.model.profile_draft("create")
        payload = {
            "operation": "create",
            "sourceProfile": None,
            "targetName": "Test Setup Card",
            "sourceFingerprint": None,
            "title": "Test Setup Card",
            "subtitle": "",
            "status": "Draft",
            "displayCategory": "reference",
            "release": False,
            "overrides": detail["originalOverrides"],
            "lensChoices": [],
            "lensGuidanceFingerprint": detail["lensGuidanceFingerprint"],
        }
        review = self.model.review_profile(payload)
        self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Test Setup Card.yaml")
        self.assertEqual(saved["display_category"], "reference")
        cx_profiles = {item["name"] for item in self.model.cx_foundation_detail()["profiles"]}
        self.assertIn("Test Setup Card", cx_profiles)

    def test_shooting_mode_catalog_does_not_offer_cx_recall_slots(self):
        detail = self.model.profile_detail("Fireworks")
        mode = next(
            setting
            for section in detail["sections"]
            for setting in section["settings"]
            if setting["path"] == "exposure.mode"
        )
        self.assertEqual(mode["label"], "Shooting Mode")
        self.assertNotIn("C1", mode["choices"])
        self.assertNotIn("C2", mode["choices"])
        self.assertNotIn("C3", mode["choices"])
        self.assertIn("Cx Foundation", mode["catalogNote"])

    def test_moves_unreleased_profile_to_deleted_cards_and_restores_exact_source(self):
        detail = self.create_unreleased_profile("Removal Test")
        source = self.root / "10 Profiles" / "Removal Test.yaml"
        before = source.read_bytes()
        review = self.model.review_profile_removal("Removal Test", detail["sourceFingerprint"])
        self.assertIn("--- a/10 Profiles/Removal Test.yaml", review["diff"])
        self.assertIn("+++ /dev/null", review["diff"])
        result = self.model.save_profile_removal(review["reviewToken"])
        self.assertFalse(source.exists())
        self.assertTrue(Path(result["backup"]).is_dir())
        self.assertTrue((Path(result["backup"]) / "before" / "10 Profiles" / "Removal Test.yaml").is_file())
        self.assertEqual(self.model.deleted_cards()[0]["cardId"], detail["cardId"])
        cx_profiles = {item["name"] for item in self.model.cx_foundation_detail()["profiles"]}
        self.assertNotIn("Removal Test", cx_profiles)

        restore = self.model.review_profile_restore(detail["cardId"])
        self.assertIn("--- /dev/null", restore["diff"])
        self.model.save_profile_restore(restore["reviewToken"])
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(self.model.deleted_cards(), [])

    def test_discard_blocks_released_assigned_and_routed_profiles(self):
        wildlife = self.model.profile_detail("Wildlife")
        with self.assertRaisesRegex(PrototypeError, "Only unreleased"):
            self.model.review_profile_removal("Wildlife", wildlife["sourceFingerprint"])

        macro = self.model.profile_detail("Macro")
        with self.assertRaisesRegex(PrototypeError, "associated with appendices"):
            self.model.review_profile_removal("Macro", macro["sourceFingerprint"])

        controls_path = self.root / "controls.yaml"
        controls_text = controls_path.read_text(encoding="utf-8")
        landscape_id = self.model.profiles["Landscape"]["card_id"]
        macro_id = self.model.profiles["Macro"]["card_id"]
        controls_path.write_text(
            controls_text.replace(f"profile_id: {landscape_id}", f"profile_id: {macro_id}", 1),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(PrototypeError, "assigned to C3"):
            self.model.review_profile_removal("Macro", macro["sourceFingerprint"])

        controls_path.write_text(controls_text, encoding="utf-8")
        people = self.model.profiles["People"]
        people.setdefault("card", {})["field_setup"] = {
            "start": "C3",
            "source_card_id": macro_id,
        }
        with self.assertRaisesRegex(PrototypeError, "used as Cx foundation by People"):
            self.model.review_profile_removal("Macro", macro["sourceFingerprint"])

    def test_discard_rejects_concurrent_change_and_restores_on_validation_failure(self):
        detail = self.create_unreleased_profile("Removal Failure Test")
        review = self.model.review_profile_removal("Removal Failure Test", detail["sourceFingerprint"])
        source = self.root / "10 Profiles" / "Removal Failure Test.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n# external change\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfileConflictError, "changed after review"):
            self.model.save_profile_removal(review["reviewToken"])

        source.write_text(source.read_text(encoding="utf-8").replace("\n# external change\n", ""), encoding="utf-8")
        failing = ProfileEditorModel(self.root, source_validator=lambda _root: ["forced validation failure"])
        detail = failing.profile_detail("Removal Failure Test")
        review = failing.review_profile_removal("Removal Failure Test", detail["sourceFingerprint"])
        before = source.read_bytes()
        with self.assertRaisesRegex(PrototypeError, "restored automatically"):
            failing.save_profile_removal(review["reviewToken"])
        self.assertEqual(source.read_bytes(), before)

    def test_duplicates_existing_profile_as_unreleased_draft(self):
        detail = self.model.profile_draft("duplicate", "Wildlife")
        payload = {
            "operation": "duplicate",
            "sourceProfile": "Wildlife",
            "targetName": "Wildlife Alternate",
            "sourceFingerprint": detail["sourceFingerprint"],
            "title": "Wildlife Alternate",
            "subtitle": "",
            "status": "Final",
            "displayCategory": "subject",
            "release": True,
            "overrides": detail["originalOverrides"],
            "lensChoices": detail["lensChoices"],
            "lensGuidanceFingerprint": detail["lensGuidanceFingerprint"],
        }
        review = self.model.review_profile(payload)
        self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Wildlife Alternate.yaml")
        source = load_yaml(self.root / "10 Profiles" / "Wildlife.yaml")
        self.assertEqual(saved["overrides"], source["overrides"])
        self.assertEqual(saved["metadata"]["status"], "Draft")
        self.assertFalse(saved["metadata"]["release"])
        self.assertNotEqual(saved["card_id"], source["card_id"])

    def test_blocks_save_when_source_changes_after_review(self):
        review = self.model.review_profile(self.payload(title="Conflict Test"))
        source = self.root / "10 Profiles" / "Fireworks.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n# external change\n", encoding="utf-8")
        with self.assertRaises(ProfileConflictError):
            self.model.save_profile(review["reviewToken"])

    def test_rolls_back_when_post_save_validation_fails(self):
        failing = ProfileEditorModel(self.root, source_validator=lambda _root: ["forced validation failure"])
        before = (self.root / "10 Profiles" / "Fireworks.yaml").read_bytes()
        detail = failing.profile_detail("Fireworks")
        payload = {
            "operation": "update",
            "sourceProfile": "Fireworks",
            "targetName": "Fireworks",
            "sourceFingerprint": detail["sourceFingerprint"],
            "title": "Rollback Test",
            "subtitle": detail["subtitle"],
            "status": detail["metadata"]["status"],
            "displayCategory": detail["displayCategory"],
            "release": detail["metadata"]["release"],
            "overrides": detail["originalOverrides"],
            "lensChoices": detail["lensChoices"],
            "lensGuidanceFingerprint": detail["lensGuidanceFingerprint"],
        }
        review = failing.review_profile(payload)
        with self.assertRaisesRegex(PrototypeError, "restored automatically"):
            failing.save_profile(review["reviewToken"])
        self.assertEqual((self.root / "10 Profiles" / "Fireworks.yaml").read_bytes(), before)

    def test_reference_cards_remain_read_only(self):
        reference = next(item for item in self.model.profile_list() if item["cardType"] == "reference")
        with self.assertRaisesRegex(PrototypeError, "Reference cards cannot be duplicated"):
            self.model.profile_draft("duplicate", reference["name"])

    def test_baseline_detail_is_a_read_only_complete_value_draft(self):
        detail = self.model.baseline_detail()
        self.assertTrue(detail["readOnly"])
        self.assertEqual(detail["sourceFile"], "00 Master/baseline.yaml")
        self.assertEqual(detail["values"], self.model.default_fields)
        self.assertGreater(len(detail["sections"]), 1)

    def test_saved_my_menu_shortcuts_resolve_to_profile_setting_identities(self):
        route_catalog = self.model._my_menu_route_catalog()
        self.assertEqual(route_catalog["autofocus.operation"], "af1_af_operation")
        self.assertEqual(route_catalog["autofocus.eye_detection"], "af1_eye_detection")
        self.assertEqual(route_catalog["exposure.iso.mode"], "shoot2_iso_speed_settings")

        values = dict(self.model.baseline_detail()["values"])
        result = self.model.baseline_impact(values)
        configured = {
            item["item_id"]: item
            for item in result["my_menu_impact"]["unreferenced_configured_items"]
        }
        self.assertNotIn("af1_af_operation", configured)
        self.assertNotIn("af1_eye_detection", configured)
        self.assertNotIn("shoot2_iso_speed_settings", configured)

    def test_profile_review_synchronizes_saved_my_menu_cues_without_menu_editing(self):
        payload = self.payload("Fireworks", title="Fireworks cue sync")
        profile, *_rest = self.model._candidate_profile(payload)
        menus = profile["card"]["field_setup"]["my_menus"]
        by_name = {tab["name"]: tab["settings"] for tab in menus}

        self.assertIn("shutter.type", by_name["SWITCH"])
        self.assertIn("stabilization.image_stabilization.mode", by_name["SWITCH"])

    def test_new_profile_review_adds_saved_my_menu_cues_automatically(self):
        draft = self.model.profile_draft("create")
        profile, *_rest = self.model._candidate_profile(
            {
                "operation": "create",
                "sourceProfile": None,
                "targetName": "Automatic Menu Test",
                "sourceFingerprint": None,
                "title": "Automatic Menu Test",
                "subtitle": "",
                "status": "Draft",
                "displayCategory": "subject",
                "release": False,
                "overrides": draft["originalOverrides"],
            }
        )

        menus = profile["card"]["field_setup"]["my_menus"]
        self.assertTrue(menus)
        self.assertEqual([tab["name"] for tab in menus], ["SWITCH", "AF Case"])

    def test_editor_info_exposes_version_and_source_derived_build(self):
        first = self.model.editor_info()
        second = self.model.editor_info()
        self.assertEqual(first, second)
        self.assertEqual(first["version"], application_version_info(self.root)["version"])
        self.assertEqual(first["context_name"], "Unknown")
        self.assertRegex(first["build"], r"^[0-9a-f]{8}$")
        self.assertEqual(first["project_context"]["kind"], "unknown")
        self.assertIsNone(first["project_context"]["branch"])

    def test_project_context_distinguishes_main_and_prototype_branches(self):
        git_dir = self.root / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        self.assertEqual(
            project_context_info(self.root),
            {"kind": "main", "label": "Main project", "branch": "main"},
        )
        (git_dir / "HEAD").write_text("ref: refs/heads/codex/profile-editor-prototype\n", encoding="utf-8")
        self.assertEqual(
            project_context_info(self.root),
            {
                "kind": "prototype",
                "label": "Prototype · codex/profile-editor-prototype",
                "branch": "codex/profile-editor-prototype",
            },
        )

    def test_default_editor_port_separates_main_and_prototype(self):
        git_dir = self.root / ".git"
        git_dir.mkdir(exist_ok=True)
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        self.assertEqual(default_editor_port(self.root), MAIN_EDITOR_PORT)
        (git_dir / "HEAD").write_text(
            "ref: refs/heads/codex/profile-editor-prototype\n", encoding="utf-8"
        )
        self.assertEqual(default_editor_port(self.root), PROTOTYPE_EDITOR_PORT)

    def test_profile_editor_runtime_requires_exact_process_ownership(self):
        runtime = (PROJECT_ROOT / "80 Build/scripts/profile-editor-runtime.sh").read_text(
            encoding="utf-8"
        )
        launcher = (PROJECT_ROOT / "80 Build/scripts/start-profile-editor.sh").read_text(
            encoding="utf-8"
        )
        stopper = (PROJECT_ROOT / "80 Build/scripts/stop-profile-editor.sh").read_text(
            encoding="utf-8"
        )
        for safeguard in (
            '"$command_line" == *"$PROFILE_EDITOR_PROGRAM"*',
            '"$process_cwd" == "$PROJECT_ROOT"',
            '-iTCP:"$port"',
            '"http://127.0.0.1:$port/api/editor-info"',
        ):
            self.assertIn(safeguard, runtime)
        self.assertIn("Profile Editor is already running", launcher)
        self.assertIn("older Profile Editor for this prototype", launcher)
        self.assertIn("used by an unrecognized process", launcher)
        self.assertIn('[[ "$STATUS" -eq 143 ]]', launcher)
        self.assertIn("profile_editor_stop_pid", stopper)
        self.assertIn("profile_editor_find_legacy_pid", stopper)
        self.assertIn("Nothing was stopped", stopper)

    def test_profile_editor_and_camera_lab_use_shared_version_source(self):
        editor = (PROJECT_ROOT / "80 Build/profile_editor.py").read_text(encoding="utf-8")
        lab = (PROJECT_ROOT / "80 Build/camera_control/service.py").read_text(encoding="utf-8")
        for source in (editor, lab):
            self.assertIn("application_version_info", source)
            self.assertNotIn('VERSION = "1.0.0"', source)

    def test_camera_lab_launch_accepts_only_saved_subject_profiles(self):
        class FakeLauncher:
            def __init__(self):
                self.names = []

            def launch(self, name):
                self.names.append(name)
                return {"url": f"http://127.0.0.1:8770/?profile={name}", "started": True, "reused": False}

        launcher = FakeLauncher()
        self.model.camera_lab_launcher = launcher
        result = self.model.launch_camera_lab("Landscape")
        self.assertEqual(launcher.names, ["Landscape"])
        self.assertTrue(result["started"])
        with self.assertRaisesRegex(PrototypeError, "Subject/Profile Cards"):
            self.model.launch_camera_lab("My Menu")

    def test_profile_editor_ui_has_guarded_independent_camera_lab_and_stop_actions(self):
        editor = self.root / "80 Build" / "profile_editor"
        html = (editor / "index.html").read_text(encoding="utf-8")
        javascript = (editor / "app.js").read_text(encoding="utf-8")
        stylesheet = (editor / "styles.css").read_text(encoding="utf-8")
        self.assertIn('meta name="profile-editor-token"', html)
        self.assertIn('id="open-camera-lab"', html)
        self.assertIn('id="stop-profile-editor"', html)
        self.assertNotIn('id="project-context-badge"', html)
        self.assertIn('id="profile-pack-select"', html)
        self.assertIn('<span class="profile-pack-label">Profile Pack:</span>', html)
        self.assertIn('id="editor-version"', html)
        self.assertIn('id="editor-source-hash"', html)
        self.assertLess(html.index(">User guide<"), html.index('id="open-camera-lab"'))
        self.assertLess(html.index('id="open-camera-lab"'), html.index('id="stop-profile-editor"'))
        self.assertLess(html.index('id="stop-profile-editor"'), html.index('id="profile-pack-select"'))
        self.assertLess(html.index('id="profile-pack-select"'), html.index('id="editor-version"'))
        self.assertIn('<details class="build-badge header-version">', html)
        self.assertIn(".header-meta { grid-column: 1; grid-row: 2;", stylesheet)
        self.assertIn(".header-version { grid-column: 1; grid-row: 3; justify-self: end; }", stylesheet)
        self.assertIn('request("/api/camera-lab-launch"', javascript)
        self.assertIn('request("/api/editor-shutdown"', javascript)
        self.assertIn("profilePayloadChanged(profileDraftPayload())", javascript)
        self.assertIn("Camera Lab, if running, remains independent", javascript)
        self.assertIn("info.project_context", javascript)
        self.assertIn("Git branch ${projectContext.branch}", javascript)
        self.assertIn("switchProfilePack", javascript)
        self.assertIn("Camera Lab evidence can be deliberately promoted", javascript)
        self.assertIn("grid-template-rows: auto auto auto", stylesheet)
        self.assertIn("grid-row: 1 / span 3", stylesheet)

    def test_profile_editor_ui_exposes_daily_release_and_sharing_workspaces(self):
        editor = self.root / "80 Build" / "profile_editor"
        html = (editor / "index.html").read_text(encoding="utf-8")
        javascript = (editor / "app.js").read_text(encoding="utf-8")
        stylesheet = (editor / "styles.css").read_text(encoding="utf-8")
        self.assertLess(html.index('data-view="today"'), html.index('data-view="profiles"'))
        self.assertIn('id="today-view"', html)
        self.assertIn('id="release-publish-view"', html)
        self.assertIn('id="setup-sharing-view"', html)
        self.assertIn('id="app-sidebar"', html)
        self.assertIn('id="finish-day-view"', html)
        self.assertIn('id="branch-integration-view"', html)
        self.assertIn('id="cleanup-review-view"', html)
        self.assertIn("Integrate Branch", html)
        self.assertIn("Edit Profiles", html)
        self.assertIn("Launch separate app", html)
        self.assertIn("Fork owner’s project", html)
        self.assertIn('id="new-profile-pack-name"', html)
        self.assertIn('id="new-profile-pack-destination"', html)
        self.assertIn('id="choose-profile-pack-destination"', html)
        self.assertIn('id="switch-to-embedded-for-creation"', html)
        self.assertIn('id="profile-pack-creation-dialog"', html)
        self.assertIn('id="create-profile-pack"', html)
        self.assertIn('id="profile-pack-git-panel"', html)
        self.assertIn('id="profile-starter-panel"', html)
        self.assertIn('id="profile-starter-dialog"', html)
        self.assertIn("Add Profiles from Catalog", html)
        self.assertNotIn("Add profile starters to this pack", html)
        self.assertIn("Profile Packs &amp; Sharing", html)
        self.assertIn("How the editor protects your work", html)
        self.assertLess(html.index('id="today-view"'), html.index('class="safety-note"'))
        self.assertIn('id="application-git-summary"', html)
        self.assertIn('id="profile-pack-git-summary"', html)
        self.assertIn('id="combined-handoff-status"', html)
        self.assertIn('id="review-profile-pack-commit"', html)
        self.assertIn('id="review-profile-pack-remote"', html)
        self.assertIn('id="push-profile-pack"', html)
        self.assertIn('id="profile-pack-step-select"', html)
        self.assertIn('id="profile-pack-step-push"', html)
        self.assertIn('id="profile-pack-git-progress"', html)
        self.assertIn('id="profile-pack-git-receipt"', html)
        self.assertIn("Latest verified result", html)
        self.assertIn('id="change-profile-pack-remote"', html)
        self.assertIn("Leave README", html)
        self.assertIn("HTTPS is recommended", html)
        self.assertNotIn("His profiles", html)
        self.assertIn('request("/api/workflow-preflight"', javascript)
        self.assertIn('switchView("profiles")', javascript)
        self.assertIn('switchView("release-publish")', javascript)
        self.assertIn('window.scrollTo({ top: 0, behavior: "auto" })', javascript)
        self.assertIn('request("/api/profile-pack-creation-reviews"', javascript)
        self.assertIn('request("/api/profile-pack-creations"', javascript)
        self.assertIn('request("/api/profile-pack-destination-picker"', javascript)
        self.assertIn('request("/api/profile-pack-git-status"', javascript)
        self.assertIn('request("/api/profile-pack-git-commit-reviews"', javascript)
        self.assertIn('request("/api/profile-pack-git-commits"', javascript)
        self.assertIn('request("/api/profile-pack-git-remote-reviews"', javascript)
        self.assertIn('request("/api/profile-pack-git-remotes"', javascript)
        self.assertIn('request("/api/profile-pack-git-pushes"', javascript)
        self.assertIn('request("/api/profile-starter-options"', javascript)
        self.assertIn('request("/api/profile-starter-reviews"', javascript)
        self.assertIn('request("/api/profile-starter-saves"', javascript)
        self.assertIn("profileEditor.profilePackRemoteJob", javascript)
        self.assertIn("profileEditor.profilePackPushJob", javascript)
        self.assertIn("PROFILE_PACK_RECEIPT_KEY", javascript)
        self.assertIn("reconcileProfilePackReceipt", javascript)
        self.assertIn("No repository-creation or push action is needed", javascript)
        self.assertIn('"setup-sharing"', javascript)
        self.assertIn(".day-workflow", stylesheet)
        self.assertIn(".sharing-flow", stylesheet)
        self.assertIn(".profile-pack-creation-panel", stylesheet)
        self.assertIn("height: calc(100vh - 2rem)", stylesheet)
        self.assertIn("--sidebar-available-height", stylesheet)
        self.assertIn("updateSidebarViewport", javascript)
        self.assertIn("max-height: calc(100vh - 2rem)", stylesheet)
        self.assertIn('.sharing-panel input[type="checkbox"]', stylesheet)
        self.assertIn('.review-confirmation input[type="checkbox"]', stylesheet)
        self.assertIn(".profile-pack-setup-steps", stylesheet)
        self.assertIn('request("/api/finish-day-status"', javascript)
        self.assertIn('request("/api/finish-day-prepare"', javascript)
        self.assertIn('request("/api/finish-day-commit"', javascript)
        self.assertIn('request("/api/finish-day-push"', javascript)
        self.assertIn('request("/api/branch-integration-status"', javascript)
        self.assertIn('request("/api/branch-integration-prepare"', javascript)
        self.assertIn('request("/api/branch-integration-approve-catalog"', javascript)
        self.assertIn('request("/api/branch-integration-merge-main"', javascript)
        self.assertIn('request("/api/branch-integration-push-main"', javascript)
        self.assertIn('request("/api/branch-integration-resync"', javascript)
        self.assertIn('request("/api/guarded-job-status"', javascript)
        self.assertIn('request("/api/cleanup-status"', javascript)
        self.assertIn('request("/api/cleanup-delete"', javascript)
        self.assertIn('request("/api/publication-status"', javascript)
        self.assertIn('request("/api/publication-notes-review"', javascript)
        self.assertIn('request("/api/publication-notes-save"', javascript)
        self.assertIn('request("/api/publication-review"', javascript)
        self.assertIn('request("/api/publication-start"', javascript)
        self.assertIn('request("/api/main-editor-launch"', javascript)
        self.assertIn("Watch command log", html)
        self.assertIn("Publish live website", html)
        self.assertIn("Automatic (recommended)", html)
        self.assertIn("Force rebuild and republish both", html)
        self.assertIn("Open Main project editor", html)
        self.assertIn("Permanently delete only the exact checked items", html)
        self.assertIn('<span>Push the reviewed integration commit to <code>origin/main</code>.', html)
        self.assertIn('id="branch-catalog-owner-review"', html)
        self.assertIn("Approve protected catalog changes", html)
        self.assertIn(".integration-steps", stylesheet)
        self.assertIn('id="branch-integration-app-status"', html)
        self.assertIn("appRefresh?.message", javascript)
        self.assertIn("Publication stopped — not completed or verified", javascript)
        self.assertIn("Publication complete and verified", javascript)
        self.assertIn("#publication-progress.is-stopped", stylesheet)
        self.assertIn('id="local-build-progress"', html)
        self.assertIn('id="local-build-progress-stage"', html)
        self.assertIn('id="local-build-progress-elapsed"', html)
        self.assertIn('id="local-build-progress-command"', html)
        self.assertIn('id="local-build-progress-log"', html)
        self.assertIn('id="local-build-details"', html)
        self.assertIn('id="resume-local-build"', html)
        self.assertIn('id="resume-finish-day"', html)
        self.assertIn('id="resume-publication"', html)
        self.assertIn("Resume after closing Numbers", html)
        self.assertIn("resume-local-build", javascript)
        self.assertIn("Show status details", html)
        self.assertIn('localBuild: "profileEditor.localBuildJob"', javascript)
        self.assertIn("reconnectLocalBuild", javascript)
        self.assertIn('id="workflow-preflight-recovery"', html)
        self.assertIn('id="finish-day-confirm-spreadsheet"', html)
        self.assertIn('id="branch-integration-recovery"', html)
        self.assertIn('id="publication-recovery"', html)
        self.assertIn('request("/api/preflight-pull"', javascript)
        self.assertIn("retry-with-spreadsheet-refresh", javascript)

    def test_guarded_job_manager_reports_progress_and_result(self):
        manager = GuardedJobManager()

        def action(progress):
            progress("Running source validation", command="$ validator", output="started")
            progress("Running source validation", output="passed", completed=True)
            return {"phase": "commit"}

        started = manager.start("test", action)
        result = None
        for _attempt in range(100):
            result = manager.status(started["jobId"])
            if result["status"] != "running":
                break
            threading.Event().wait(0.01)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["result"], {"phase": "commit"})
        self.assertTrue(any("$ validator" in entry for entry in result["log"]))

    def test_guarded_job_manager_preserves_failure_reason_in_progress_log(self):
        manager = GuardedJobManager()

        def action(progress):
            progress("Publishing and verifying the live website", command="$ publish.sh")
            raise RuntimeError("Publication did not complete. Upload verification failed.")

        started = manager.start("publication", action)
        result = None
        for _attempt in range(100):
            result = manager.status(started["jobId"])
            if result["status"] != "running":
                break
            threading.Event().wait(0.01)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stage"], "Stopped")
        self.assertIn("Upload verification failed", result["error"])
        self.assertTrue(any("Publishing and verifying the live website stopped" in entry for entry in result["log"]))
        self.assertTrue(any("Upload verification failed" in entry for entry in result["log"]))

    def test_guarded_job_manager_preserves_structured_recovery(self):
        manager = GuardedJobManager()

        def action(_progress):
            raise PrototypeError(
                "Spreadsheet refresh permission required.",
                recovery={"kind": "integration-spreadsheet-refresh", "actions": ["retry"]},
            )

        started = manager.start("branch-integration-prepare", action)
        result = None
        for _attempt in range(100):
            result = manager.status(started["jobId"])
            if result["status"] != "running":
                break
            threading.Event().wait(0.01)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["recovery"]["kind"], "integration-spreadsheet-refresh")

    def test_workflow_preflight_classifies_ready_notice_and_blocked_results(self):
        outcomes = (
            (0, "PREFLIGHT PASSED: Repository is clean and synchronized.", "ready"),
            (0, "PREFLIGHT NOTICE: Intentional local edits may be validated and tested.", "notice"),
            (1, "PREFLIGHT BLOCKED: This clone is behind its upstream.", "blocked"),
        )
        for return_code, output, expected in outcomes:
            with self.subTest(expected=expected), patch("profile_editor.subprocess.run") as run:
                run.return_value = SimpleNamespace(returncode=return_code, stdout=output)
                result = self.model.workflow_preflight()
            self.assertEqual(result["status"], expected)
            self.assertNotIn("PREFLIGHT", result["summary"])
            self.assertEqual(
                run.call_args.args[0][0],
                str((self.root / "80 Build" / "scripts" / "preflight-git.sh").resolve()),
            )
        with patch("profile_editor.subprocess.run") as run:
            run.return_value = SimpleNamespace(
                returncode=1,
                stdout="PREFLIGHT BLOCKED: This clone is behind its upstream.\nWhen clean, use: git pull --ff-only",
            )
            behind = self.model.workflow_preflight()
        self.assertIn("pull-latest", behind["recoveryActions"])

    def test_git_status_uses_current_branch_and_requires_matching_upstream(self):
        remote = Path(self.temporary.name) / "remote.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "init", "-b", "codex/profile-editor-prototype"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        for key, value in (("user.name", "Profile Editor Test"), ("user.email", "profile-editor@example.invalid")):
            subprocess.run(["git", "config", key, value], cwd=self.root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "Fixture"], cwd=self.root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=self.root, check=True)
        subprocess.run(
            ["git", "push", "-u", "origin", "codex/profile-editor-prototype"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        status_script = self.root / "80 Build" / "scripts" / "git-status-report.sh"

        current = subprocess.run([str(status_script)], cwd=self.root, capture_output=True, text=True, check=False)
        self.assertEqual(current.returncode, 0, current.stdout + current.stderr)
        self.assertIn("Expected: codex/profile-editor-prototype", current.stdout)
        self.assertIn("STATUS: CLEAN AND SYNCHRONIZED", current.stdout)

        explicitly_wrong = subprocess.run(
            [str(status_script)],
            cwd=self.root,
            env={**os.environ, "PRS_EXPECTED_BRANCH": "main"},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(explicitly_wrong.returncode, 50)
        self.assertIn("STATUS: WRONG BRANCH", explicitly_wrong.stdout)

        subprocess.run(
            ["git", "push", "origin", "HEAD:main"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "branch", "--set-upstream-to=origin/main"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        mismatched = subprocess.run([str(status_script)], cwd=self.root, capture_output=True, text=True, check=False)
        self.assertEqual(mismatched.returncode, 51)
        self.assertIn("STATUS: UNEXPECTED UPSTREAM", mismatched.stdout)
        self.assertIn("origin/codex/profile-editor-prototype", mismatched.stdout)

    def test_publish_script_blocks_prototype_branch_before_building(self):
        subprocess.run(
            ["git", "init", "-b", "codex/profile-editor-prototype"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        publisher = self.root / "80 Build" / "scripts" / "publish.sh"
        completed = subprocess.run(
            [str(publisher)],
            cwd=self.root,
            env={**os.environ, "PRS_LOCAL_WORKSPACE": str(Path(self.temporary.name) / "local")},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("PUBLICATION BLOCKED", completed.stderr)
        self.assertIn("only from 'main'", completed.stderr)
        self.assertFalse((self.root / "80 Build" / ".publish_metadata.candidate.yaml").exists())

    def test_publication_release_notes_are_exact_reviewed_backed_up_and_validated(self):
        from publication_workflow import PublicationWorkflow

        workflow = PublicationWorkflow(self.root)

        def git_result(*arguments):
            if arguments == ("branch", "--show-current"):
                return "main"
            if arguments == ("status", "--porcelain=v1", "--untracked-files=all"):
                return ""
            raise AssertionError(arguments)

        workflow._git = git_result
        workflow._run = lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="Source validation passed")
        review = workflow.review_release_notes(
            None,
            ["Added Terminal-free guarded publication.", "Added exact live-release verification."],
        )
        self.assertEqual(review["nextVersion"], "2.05")
        self.assertIn('"2.05"', review["diff"])
        saved = workflow.save_release_notes(review["reviewToken"], True)
        notes = load_yaml(self.root / "00 Master" / "release_notes.yaml")
        self.assertEqual(
            notes["releases"]["2.05"]["highlights"],
            ["Added Terminal-free guarded publication.", "Added exact live-release verification."],
        )
        self.assertTrue(Path(saved["backup"]).is_dir())
        self.assertTrue((Path(saved["backup"]) / "release_notes.yaml").is_file())

    def test_publication_review_binds_options_and_simulated_publish_requires_receipts(self):
        from publication_workflow import PublicationWorkflow

        workflow = PublicationWorkflow(self.root)
        ready = {
            "phase": "ready",
            "branch": "main",
            "upstream": "origin/main",
            "currentVersion": "2.03",
            "nextVersion": "3.00",
            "releaseKind": "major",
            "majorVersion": 3,
            "notesReady": True,
            "highlights": ["Major release highlight."],
            "spreadsheetState": {"status": "current", "output": "current"},
            "blockers": [],
            "output": "ready",
        }
        workflow.inspect = lambda *args, **kwargs: dict(ready)
        workflow._git = lambda *args: "abc123" if args == ("rev-parse", "HEAD") else ""
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            if Path(command[0]).name == "publish.sh":
                return SimpleNamespace(returncode=0, stdout="PUBLICATION COMPLETE AND VERIFIED.\nWebsite published successfully.")
            if Path(command[0]).name == "git-status-report.sh":
                return SimpleNamespace(returncode=0, stdout="STATUS: CLEAN AND SYNCHRONIZED")
            return SimpleNamespace(returncode=0, stdout="prepared")

        workflow._run = run
        review = workflow.review_publication(0, 3, "replace")
        result = workflow.publish(review["reviewToken"], True)
        self.assertEqual(result["phase"], "complete")
        self.assertEqual(result["version"], "3.00")
        self.assertTrue(any(Path(command[0]).name == "build-all-spreadsheet-downloads.sh" for command in commands))
        builder_command = next(command for command in commands if Path(command[0]).name == "build-all-spreadsheet-downloads.sh")
        self.assertIn("--force-release-workbooks", builder_command)
        publish_command = next(command for command in commands if Path(command[0]).name == "publish.sh")
        self.assertIn("--major-version", publish_command)
        self.assertIn("--spreadsheet-downloads", publish_command)
        self.assertIn("STATUS: CLEAN AND SYNCHRONIZED", result["output"])

    def test_publication_automatic_mode_preserves_current_and_refreshes_only_stale_family(self):
        from publication_workflow import PublicationWorkflow, PublicationWorkflowError

        workflow = PublicationWorkflow(self.root)
        base = {
            "phase": "ready",
            "branch": "main",
            "upstream": "origin/main",
            "currentVersion": "2.04",
            "nextVersion": "2.05",
            "releaseKind": "minor",
            "majorVersion": None,
            "notesReady": True,
            "highlights": ["Release highlight."],
            "blockers": [],
            "output": "ready",
        }
        workflow._git = lambda *args: "abc123" if args == ("rev-parse", "HEAD") else ""

        current = dict(base)
        current["spreadsheetState"] = {"status": "current", "refreshTargets": [], "output": "current"}
        workflow.inspect = lambda *args, **kwargs: dict(current)
        review = workflow.review_publication(0, None, "automatic")
        self.assertEqual(review["spreadsheetTargets"], [])

        stale = dict(base)
        stale["spreadsheetState"] = {
            "status": "refresh-needed",
            "refreshTargets": ["matrix"],
            "output": "matrix stale",
        }
        workflow.inspect = lambda *args, **kwargs: dict(stale)
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            if Path(command[0]).name == "publish.sh":
                return SimpleNamespace(returncode=0, stdout="PUBLICATION COMPLETE AND VERIFIED.")
            if Path(command[0]).name == "git-status-report.sh":
                return SimpleNamespace(returncode=0, stdout="STATUS: CLEAN AND SYNCHRONIZED")
            return SimpleNamespace(returncode=0, stdout="prepared")

        workflow._run = run
        review = workflow.review_publication(0, None, "automatic")
        result = workflow.publish(review["reviewToken"], True)
        self.assertEqual(result["spreadsheetTargets"], ["matrix"])
        builder_command = next(command for command in commands if Path(command[0]).name == "build-all-spreadsheet-downloads.sh")
        self.assertNotIn("--force-release-workbooks", builder_command)
        publish_command = next(command for command in commands if Path(command[0]).name == "publish.sh")
        self.assertIn("--matrix-downloads", publish_command)
        self.assertNotIn("--spreadsheet-downloads", publish_command)

        attempts = 0

        def recoverable_run(command, **kwargs):
            nonlocal attempts
            if Path(command[0]).name == "build-all-spreadsheet-downloads.sh":
                attempts += 1
                if attempts == 1:
                    return SimpleNamespace(
                        returncode=1,
                        stdout="NUMBERS_BUSY_RECOVERY: Apple Numbers is already open.",
                    )
                return SimpleNamespace(returncode=0, stdout="prepared")
            if Path(command[0]).name == "publish.sh":
                return SimpleNamespace(returncode=0, stdout="PUBLICATION COMPLETE AND VERIFIED.")
            return SimpleNamespace(returncode=0, stdout="STATUS: CLEAN AND SYNCHRONIZED")

        workflow._run = recoverable_run
        review = workflow.review_publication(0, None, "automatic")
        with self.assertRaisesRegex(PublicationWorkflowError, "Apple Numbers is already open") as stopped:
            workflow.publish(review["reviewToken"], True)
        recovery = stopped.exception.recovery
        self.assertEqual(recovery["actions"], ["resume-publication"])
        self.assertEqual(recovery["reviewToken"], review["reviewToken"])
        resumed = workflow.publish(recovery["reviewToken"], True)
        self.assertEqual(resumed["phase"], "complete")

    def test_publication_model_uses_guarded_background_job_without_publishing_in_test(self):
        class FakePublication:
            def inspect(self, pending, major):
                return {"phase": "ready", "pending": pending, "major": major}

            def publish(self, token, confirmed, progress=None):
                progress("Simulated publication", command="$ publish.sh", completed=True)
                return {"phase": "complete", "token": token, "confirmed": confirmed}

        self.model.publication_workflow = FakePublication()
        self.assertEqual(self.model.publication_status(0, None)["phase"], "ready")
        started = self.model.start_website_publication("review-token", True)
        result = None
        for _attempt in range(100):
            result = self.model.guarded_job_status(started["jobId"])
            if result["status"] != "running":
                break
            threading.Event().wait(0.01)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["result"]["phase"], "complete")
        self.assertTrue(any("Simulated publication" in entry for entry in result["log"]))

    def test_profile_editor_lifecycle_actions_require_token_and_shutdown_server(self):
        token = "profile-editor-test-token"
        self.model.finish_day_status = lambda pending: {
            "phase": "complete",
            "pendingChanges": pending,
            "branch": "codex/profile-editor-prototype",
        }
        self.model.branch_integration_status = lambda pending: {
            "phase": "review",
            "pendingChanges": pending,
            "branch": "codex/profile-editor-prototype",
            "target": "origin/main",
        }
        server = create_server(self.model, port=0, token=token)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/editor-shutdown",
                body="{}",
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            connection.close()

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/profile-starter-reviews",
                body=json.dumps({"cardIds": [], "pendingChanges": 0}),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            connection.close()

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/profile-pack-git-status",
                body=json.dumps({"pendingChanges": 0}),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            connection.close()

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/profile-pack-creation-reviews",
                body=json.dumps(
                    {
                        "packName": "Unauthorized Pack",
                        "destination": "/private/tmp/unauthorized-profile-pack",
                        "pendingChanges": 0,
                    }
                ),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            connection.close()

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/finish-day-status",
                body=json.dumps({"pendingChanges": 0}),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            connection.close()

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/finish-day-status",
                body=json.dumps({"pendingChanges": 0}),
                headers={
                    "Content-Type": "application/json",
                    "X-Profile-Editor-Token": token,
                },
            )
            response = connection.getresponse()
            payload = json.loads(response.read())
            connection.close()
            self.assertEqual(response.status, 200)
            self.assertEqual(payload["phase"], "complete")

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/branch-integration-status",
                body=json.dumps({"pendingChanges": 0}),
                headers={
                    "Content-Type": "application/json",
                    "X-Profile-Editor-Token": token,
                },
            )
            response = connection.getresponse()
            payload = json.loads(response.read())
            connection.close()
            self.assertEqual(response.status, 200)
            self.assertEqual(payload["phase"], "review")

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/editor-shutdown",
                body="{}",
                headers={
                    "Content-Type": "application/json",
                    "X-Profile-Editor-Token": token,
                },
            )
            response = connection.getresponse()
            payload = json.loads(response.read())
            connection.close()
            self.assertEqual(response.status, 200)
            self.assertTrue(payload["server_closed"])
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
        finally:
            server.server_close()

    def test_card_preview_notes_link_opens_field_guide_and_returns_to_preview(self):
        preview = self.model.preview("Camera Buttons", {})
        preview_html = preview.read_text(encoding="utf-8")
        link = (
            "/field-guide/html/Custom%20Controls%20%26%20Menus%2C%20"
            "Back-Button%20AF%20%26%20Dial%20Strategies.html"
            "?return=../Cards/Camera%20Buttons.html"
        )
        self.assertIn('href="../../field-guide/html/', preview_html)

        server = create_server(self.model, port=0, token="preview-link-test-token")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
            connection.request("GET", link)
            response = connection.getresponse()
            field_guide_html = response.read().decode("utf-8")
            connection.close()
            self.assertEqual(response.status, 200)
            self.assertIn("Custom Controls &amp; Menus, Back-Button AF &amp; Dial Strategies", field_guide_html)

            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request("GET", "/field-guide/Cards/Camera%20Buttons.html")
            response = connection.getresponse()
            returned_preview = response.read().decode("utf-8")
            connection.close()
            self.assertEqual(response.status, 200)
            self.assertIn("<h1>Camera Buttons</h1>", returned_preview)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_profile_detail_exposes_card_order_and_visible_setting_paths(self):
        detail = self.model.profile_detail("Birds in Flight")
        self.assertEqual(
            detail["cardSettingPaths"][:8],
            [
                "exposure.mode",
                "shutter.target",
                "shutter.type",
                "lens.aperture.target",
                "exposure.iso.mode",
                "exposure.iso.value",
                "exposure.auto_iso.maximum",
                "exposure.exposure_compensation",
            ],
        )
        self.assertNotIn("exposure.metering", detail["cardSettingPaths"])
        self.assertEqual(detail["settingOrder"][:5], [
            "exposure.mode",
            "exposure.metering",
            "shutter.target",
            "shutter.type",
            "lens.aperture.target",
        ])

    def test_card_setting_paths_follow_draft_visibility_rules(self):
        detail = self.model.profile_detail("Birds in Flight")
        overrides = dict(detail["originalOverrides"])
        overrides["autofocus.operation"] = "Manual Focus"
        visible = self.model.card_setting_paths("Birds in Flight", overrides)
        self.assertNotIn("autofocus.method", visible)
        self.assertNotIn("autofocus.subject_detection", visible)
        self.assertNotIn("autofocus.eye_detection", visible)

    def test_profile_editor_layout_keeps_preview_beside_ordered_settings(self):
        editor = self.root / "80 Build" / "profile_editor"
        html = (editor / "index.html").read_text(encoding="utf-8")
        javascript = (editor / "app.js").read_text(encoding="utf-8")
        stylesheet = (editor / "styles.css").read_text(encoding="utf-8")
        self.assertIn('class="app-sidebar"', html)
        self.assertIn('id="card-settings"', html)
        self.assertIn('id="preview-panel"', html)
        self.assertIn("payload.cardSettingPaths", javascript)
        self.assertIn("position: sticky", stylesheet)

    def test_profile_editor_exposes_draft_ledger_and_guarded_local_build(self):
        editor = self.root / "80 Build" / "profile_editor"
        html = (editor / "index.html").read_text(encoding="utf-8")
        javascript = (editor / "app.js").read_text(encoding="utf-8")
        self.assertLess(html.index('data-view="today"'), html.index('data-view="profiles"'))
        self.assertLess(html.index('data-view="profiles"'), html.index('data-view="review-build"'))
        expected_sidebar_order = [
            "today", "profiles", "review-build", "finish-day", "cx-foundation", "my-menu",
            "camera-buttons", "baseline", "deleted-cards", "branch-integration",
            "release-publish", "cleanup-review", "setup-sharing", "dictionary",
        ]
        positions = [html.index(f'data-view="{view}"') for view in expected_sidebar_order]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(html.index('data-view="release-publish"'), html.index('data-view="dictionary"'))
        self.assertIn('id="pending-change-list"', html)
        self.assertIn('id="build-confirm-dialog"', html)
        self.assertIn('id="display-category-input"', html)
        self.assertIn('id="discard-profile-button"', html)
        self.assertIn('id="discard-profile-dialog"', html)
        self.assertIn('id="deleted-cards-view"', html)
        self.assertIn('id="restore-profile-dialog"', html)
        self.assertIn('id="profile-removal-reason"', html)
        self.assertIn("How to move a card here", html)
        self.assertIn("Silver%20Logo.png", html)
        self.assertIn("Restore saved profile", html)
        self.assertIn('id="import-verification-tracker"', html)
        self.assertIn('id="preview-camera-buttons"', html)
        self.assertIn('id="camera-buttons-preview-frame"', html)
        self.assertIn("camera-control-icon", javascript)
        self.assertIn("Canon default:", javascript)
        self.assertIn("Card detail", javascript)
        self.assertIn("cameraButtonCardDetail", javascript)
        self.assertIn("Live text shown beneath this assignment", javascript)
        preview_panel = html.index('id="camera-buttons-preview-panel"')
        preview_button = html.index('id="preview-camera-buttons"')
        self.assertGreater(preview_button, preview_panel)
        self.assertIn("Other / exact camera label", javascript)
        self.assertIn('request("/api/camera-buttons-preview"', javascript)
        self.assertIn('window.addEventListener("beforeunload"', javascript)
        self.assertIn("profileDrafts: new Map()", javascript)
        self.assertIn("await loadCxFoundations(true)", javascript)
        self.assertIn('request("/api/profile-removal-reviews"', javascript)
        self.assertIn('request("/api/profile-restore-reviews"', javascript)
        self.assertIn("state.cxSelectionDrafts.has(state.detail.name)", javascript)
        self.assertIn("state.activeProfileName = name", javascript)
        self.assertIn("profile.name === state.activeProfileName", javascript)
        self.assertIn("elements.profileActionMenu.open = false", javascript)
        self.assertIn("Permanent reference cards cannot be moved", javascript)

    def test_confirmed_preflight_pull_is_fast_forward_only(self):
        model = self.model
        model._preflight_checker = lambda: {
            "status": "ready",
            "summary": "Repository is clean and synchronized.",
            "output": "",
        }
        results = [
            SimpleNamespace(returncode=0, stdout=""),
            SimpleNamespace(returncode=0, stdout="codex/profile-editor-prototype\n"),
            SimpleNamespace(returncode=0, stdout="origin/codex/profile-editor-prototype\n"),
            SimpleNamespace(returncode=0, stdout="fetched\n"),
            SimpleNamespace(returncode=0, stdout="0\t2\n"),
            SimpleNamespace(returncode=0, stdout="updated\n"),
        ]
        with patch("profile_editor.subprocess.run", side_effect=results) as run:
            result = model.pull_latest(0, True)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(run.call_args_list[-1].args[0], ["git", "pull", "--ff-only"])

    def test_build_readiness_blocks_pending_drafts_and_source_errors(self):
        pending = self.model.build_readiness(2)
        self.assertFalse(pending["ready"])
        self.assertIn("Resolve 2 unsaved browser drafts", pending["blockers"][0])
        failing = ProfileEditorModel(self.root, source_validator=lambda _root: ["forced source failure"])
        readiness = failing.build_readiness(0)
        self.assertFalse(readiness["ready"])
        self.assertEqual(readiness["sourceValidation"], "failed")

    def test_build_readiness_reports_safe_conditional_spreadsheet_refresh(self):
        model = ProfileEditorModel(
            self.root,
            source_validator=lambda _root: [],
            derived_artifact_checker=lambda: {
                "status": "refresh-needed",
                "refreshNeeded": True,
                "details": ["Matrix/settings requires refresh."],
                "blockers": [],
            },
        )
        readiness = model.build_readiness(0)
        self.assertTrue(readiness["ready"])
        self.assertTrue(readiness["derivedArtifacts"]["refreshNeeded"])

        with patch("profile_editor.subprocess.run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = "passed"
            result = model.run_local_build(0, True)
        self.assertEqual([step["step"] for step in result["steps"]], [
            "Source validation",
            "Spreadsheet refresh",
            "Development build",
            "Full validation",
        ])
        self.assertTrue(run.call_args_list[1].args[0][0].endswith("build-all-spreadsheet-downloads.sh"))

    def test_derived_artifact_diagnostics_distinguish_stale_from_unsafe(self):
        for relative in ("80 Build/verification_status.py", "80 Build/spreadsheet_downloads.py"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# test fixture\n", encoding="utf-8")
        with patch("profile_editor.subprocess.run") as run:
            run.side_effect = [
                SimpleNamespace(returncode=2, stdout="Verification working copy is safely stale."),
                SimpleNamespace(returncode=2, stdout="Matrix/settings requires refresh."),
            ]
            stale = self.model._inspect_derived_artifacts()
            run.side_effect = [
                SimpleNamespace(returncode=3, stdout="Verification workbook has unimported edits."),
                SimpleNamespace(returncode=0, stdout="Spreadsheet downloads are current."),
            ]
            unsafe = self.model._inspect_derived_artifacts()
        self.assertEqual(stale["status"], "refresh-needed")
        self.assertTrue(stale["refreshNeeded"])
        self.assertEqual(unsafe["status"], "blocked")
        self.assertIn("unimported edits", unsafe["blockers"][0])

    def test_build_readiness_blocks_unsafe_spreadsheet_refresh(self):
        model = ProfileEditorModel(
            self.root,
            source_validator=lambda _root: [],
            derived_artifact_checker=lambda: {
                "status": "blocked",
                "refreshNeeded": False,
                "details": [],
                "blockers": ["Verification workbook has unimported edits."],
            },
        )
        readiness = model.build_readiness(0)
        self.assertFalse(readiness["ready"])
        self.assertIn("unimported edits", readiness["blockers"][0])

    def test_local_build_requires_confirmation_and_runs_only_documented_steps(self):
        with self.assertRaisesRegex(PrototypeError, "confirmation"):
            self.model.run_local_build(0, False)
        with self.assertRaisesRegex(PrototypeError, "Resolve 1 unsaved browser draft"):
            self.model.run_local_build(1, True)
        with patch("profile_editor.subprocess.run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = "passed"
            result = self.model.run_local_build(0, True)
        self.assertEqual(result["status"], "passed")
        self.assertEqual([step["step"] for step in result["steps"]], [
            "Source validation",
            "Development build",
            "Full validation",
        ])
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual([command[1:] for command in commands], [
            ["80 Build/validator.py", "--source-only"],
            ["80 Build/build.py"],
            ["80 Build/validator.py"],
        ])
        self.assertFalse(any("git" in command or "publish" in command for command in commands))

    def test_local_build_exposes_simple_numbers_resume_recovery(self):
        model = ProfileEditorModel(
            self.root,
            source_validator=lambda _root: [],
            derived_artifact_checker=lambda: {
                "status": "refresh-needed",
                "refreshNeeded": True,
                "details": ["Setup requires refresh."],
                "blockers": [],
            },
        )
        results = [
            SimpleNamespace(returncode=0, stdout="source passed"),
            SimpleNamespace(
                returncode=1,
                stdout="NUMBERS_BUSY_RECOVERY: Apple Numbers is already open.",
            ),
        ]
        with patch("profile_editor.subprocess.run", side_effect=results):
            with self.assertRaisesRegex(PrototypeError, "Apple Numbers is already open") as stopped:
                model.run_local_build(0, True)
        self.assertEqual(stopped.exception.recovery["kind"], "numbers-close-and-resume")
        self.assertEqual(stopped.exception.recovery["actions"], ["resume-local-build"])
        self.assertIn("Resume after closing Numbers", stopped.exception.recovery["summary"])

    def test_local_build_background_job_reports_reconnectable_step_progress(self):
        with patch(
            "profile_editor.subprocess.run",
            return_value=SimpleNamespace(returncode=0, stdout="passed"),
        ):
            started = self.model.start_local_build(0, True)
            result = None
            for _attempt in range(100):
                result = self.model.guarded_job_status(started["jobId"])
                if result["status"] != "running":
                    break
                threading.Event().wait(0.01)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["result"]["status"], "passed")
        self.assertTrue(any("Source validation (1 of 3)" in entry for entry in result["log"]))
        self.assertTrue(any("80 Build/validator.py" in entry and "--source-only" in entry for entry in result["log"]))
        self.assertTrue(any(entry.startswith("✓ Full validation (3 of 3)") for entry in result["log"]))

    def test_verification_tracker_import_is_confirmed_and_serialized(self):
        with self.assertRaisesRegex(PrototypeError, "confirmation"):
            self.model.import_verification_tracker(0, False)
        with self.assertRaisesRegex(PrototypeError, "unsaved browser draft"):
            self.model.import_verification_tracker(1, True)
        with patch("profile_editor.subprocess.run") as run:
            run.return_value = SimpleNamespace(returncode=0, stdout="Verification status imported")
            result = self.model.import_verification_tracker(0, True)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(
            run.call_args.args[0][1:],
            ["80 Build/verification_status.py", "import"],
        )

    def test_change_indicator_compares_with_saved_foundation_not_baseline(self):
        detail = self.model.profile_detail("Birds in Flight")
        overrides = dict(detail["originalOverrides"])
        overrides.pop("exposure.mode", None)
        baseline_preview = self.model.preview("Birds in Flight", overrides).read_text(encoding="utf-8")
        mode_row = next(row for row in baseline_preview.split("</tr>") if ">Mode<" in row)
        self.assertIn("Δ", mode_row)
        saved_preview = self.model.preview("Birds in Flight", detail["originalOverrides"]).read_text(encoding="utf-8")
        saved_mode_row = next(row for row in saved_preview.split("</tr>") if ">Mode<" in row)
        self.assertNotIn("Δ", saved_mode_row)

    def test_preview_surfaces_structured_compatibility_notes(self):
        detail = self.model.profile_detail("Macro")
        rendered = self.model.preview("Macro", detail["originalOverrides"]).read_text(encoding="utf-8")
        self.assertIn("<h2>Lens Choices</h2>", rendered)
        self.assertIn("EF 100mm Macro", rendered)
        self.assertIn("MP-E 65mm", rendered)
        self.assertIn("<h2>Compatibility</h2>", rendered)
        self.assertIn("Flash photography is unavailable during EOS R5 Focus Bracketing", rendered)

    def test_lens_choice_draft_controls_primary_order_preview_and_guarded_save(self):
        detail = self.model.profile_detail("Macro")
        choices = deepcopy(detail["lensChoices"])
        choices.reverse()
        choices[0]["role"] = "primary"
        choices[1]["role"] = "alternative"
        choices[0]["useWhen"] = "Extreme magnification is the assignment"
        payload = self.payload("Macro", lensChoices=choices)

        preview = self.model.preview_draft(payload).read_text(encoding="utf-8")
        self.assertLess(preview.index("MP-E 65mm"), preview.index("EF 100mm Macro"))
        self.assertIn("Extreme magnification is the assignment", preview)

        review = self.model.review_profile(payload)
        self.assertIn("00 Master/profile_lens_guidance.yaml", review["sourceFiles"])
        self.assertIn("role: primary", review["diff"])
        result = self.model.save_profile(review["reviewToken"])
        self.assertEqual(result["sourceFiles"], ["00 Master/profile_lens_guidance.yaml"])

        saved = self.model.profile_detail("Macro")["lensChoices"]
        self.assertEqual(saved[0]["lensId"], "mp_e_65")
        self.assertEqual(saved[0]["role"], "primary")
        self.assertEqual(saved[1]["role"], "alternative")

    def test_lens_choice_review_rejects_missing_primary_and_concurrent_guidance_change(self):
        detail = self.model.profile_detail("Travel")
        invalid = deepcopy(detail["lensChoices"])
        for choice in invalid:
            choice["role"] = "alternative"
        with self.assertRaisesRegex(PrototypeError, "exactly one primary"):
            self.model.review_profile(self.payload("Travel", lensChoices=invalid))

        changed = deepcopy(detail["lensChoices"])
        changed[0]["fieldCheck"] = "Confirm the intended field check"
        review = self.model.review_profile(self.payload("Travel", lensChoices=changed))
        source = self.root / "00 Master" / "profile_lens_guidance.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n# external change\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfileConflictError, "Lens guidance changed after review"):
            self.model.save_profile(review["reviewToken"])

    def test_profile_editor_exposes_owned_lens_controls(self):
        detail = self.model.profile_detail("Birds in Flight")
        self.assertEqual(len(detail["lensChoices"]), 3)
        self.assertTrue(any(item["id"] == "ef_s_10_18_is_stm" for item in detail["lensCatalog"]))
        extender_lens = next(item for item in detail["lensCatalog"] if item["id"] == "ef_100_400_is_ii")
        self.assertEqual(extender_lens["accessories"][0]["id"], "extender_ef_1_4x")
        html = (self.root / "80 Build" / "profile_editor" / "index.html").read_text(encoding="utf-8")
        script = (self.root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="lens-guidance-group"', html)
        self.assertIn("function renderLensChoices()", script)
        self.assertIn("function moveLensChoice(from, to)", script)

    def test_desktop_preview_frame_fits_inside_sticky_panel(self):
        styles = (self.root / "80 Build" / "profile_editor" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("height: calc(100vh - 2rem)", styles)
        self.assertIn("#preview-frame { display: block; flex: 1 1 auto", styles)
        self.assertIn("height: auto; min-height: 0", styles)

    def test_reviews_and_saves_named_my_menu_color_assignments(self):
        assignments = dict(self.model.my_menu_colors["assignments"])
        assignments.update({"SWITCH": "Gold", "AF Case": "Green"})
        review = self.model.review_my_menu_colors(assignments)
        self.assertIn("SWITCH: Gold", review["diff"])
        result = self.model.save_my_menu_colors(review["reviewToken"])
        saved = load_yaml(self.root / "00 Master" / "my_menu_colors.yaml")
        self.assertEqual(saved["assignments"], assignments)
        self.assertEqual(result["validation"], "passed")
        self.assertTrue(Path(result["backup"]).is_dir())
        detail = self.model.profile_detail("People")
        preview = self.model.preview("People", detail["originalOverrides"])
        rendered = preview.read_text(encoding="utf-8")
        subject_row = next(row for row in rendered.split("</tr>") if "Subject Detection" in row)
        self.assertIn('field-value access-switch" style="color:#f0bf69"', subject_row)
        self.assertIn('field-change" style="color:#f0bf69"', subject_row)

    def test_rejects_duplicate_named_my_menu_colors(self):
        assignments = dict(self.model.my_menu_colors["assignments"])
        assignments.update({"SWITCH": "Green", "AF Case": "Green"})
        with self.assertRaisesRegex(PrototypeError, "distinct colors"):
            self.model.review_my_menu_colors(assignments)

    def test_blocks_my_menu_color_save_after_concurrent_change(self):
        assignments = dict(self.model.my_menu_colors["assignments"])
        assignments.update({"SWITCH": "Gold", "AF Case": "Green"})
        review = self.model.review_my_menu_colors(assignments)
        source = self.root / "00 Master" / "my_menu_colors.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n# external change\n", encoding="utf-8")
        with self.assertRaises(ProfileConflictError):
            self.model.save_my_menu_colors(review["reviewToken"])

    def test_persists_my_menu_layout_and_updates_dynamic_reference_card(self):
        tabs = [
            {
                "name": "SWITCH",
                "colorChoice": "Green",
                "items": ["af1_subject_to_detect", "shoot6_shutter_mode", "", "", "", ""],
            },
            {
                "name": "FIELD",
                "colorChoice": "Light Red",
                "items": ["shoot7_is_mode", "shoot1_cropping_aspect_ratio", "", "", "", ""],
            },
        ]
        review = self.model.review_my_menu_configuration(tabs)
        self.assertIn("00 Master/my_menu.yaml", review["diff"])
        self.assertIn("FIELD", review["diff"])
        result = self.model.save_my_menu_configuration(review["reviewToken"])
        saved = load_yaml(self.root / "00 Master" / "my_menu.yaml")
        self.assertEqual([tab["name"] for tab in saved["tabs"]], ["SWITCH", "FIELD"])
        self.assertEqual(result["colors"]["assignments"]["FIELD"], "Light Red")
        detail = self.model.profile_detail("My Menu")
        self.assertFalse(detail["editableDraft"])
        self.assertEqual(
            [row["assignment"] for row in detail["referenceSettings"] if row["rowType"] == "section"],
            ["SWITCH", "FIELD"],
        )
        preview = self.model.preview("My Menu", {})
        rendered = preview.read_text(encoding="utf-8")
        self.assertIn("MY MENU2", rendered)
        self.assertIn("FIELD", rendered)
        self.assertIn("IS (Image Stabilizer) mode", rendered)

    def test_my_menu_save_rolls_back_both_sources_after_validation_failure(self):
        failing = ProfileEditorModel(self.root, source_validator=lambda _root: ["forced validation failure"])
        sources = [self.root / "00 Master" / "my_menu.yaml", self.root / "00 Master" / "my_menu_colors.yaml"]
        before = {path: path.read_bytes() for path in sources}
        tabs = [
            {"name": "SWITCH", "colorChoice": "Green", "items": ["af1_subject_to_detect"]},
            {"name": "AF Case", "colorChoice": "Gold", "items": ["af3_servo_af_characteristics"]},
        ]
        review = failing.review_my_menu_configuration(tabs)
        with self.assertRaisesRegex(PrototypeError, "restored automatically"):
            failing.save_my_menu_configuration(review["reviewToken"])
        self.assertEqual({path: path.read_bytes() for path in sources}, before)

    def test_baseline_impact_reports_profiles_without_writing_sources(self):
        baseline_path = self.root / "00 Master" / "baseline.yaml"
        profile_path = self.root / "10 Profiles" / "People.yaml"
        before_baseline = baseline_path.read_bytes()
        before_profile = profile_path.read_bytes()
        values = dict(self.model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        result = self.model.baseline_impact(values)
        classifications = result["summary"]["classifications"]
        self.assertEqual(result["summary"]["changed_settings"], 1)
        self.assertGreater(classifications["inherited_change"], 0)
        self.assertGreater(classifications["override_redundant"], 0)
        self.assertEqual(baseline_path.read_bytes(), before_baseline)
        self.assertEqual(profile_path.read_bytes(), before_profile)

    def test_zero_baseline_change_can_review_and_save_profile_only_my_menu_cue(self):
        people = deepcopy(self.model.profiles["People"])
        switch = next(
            menu
            for menu in people["card"]["field_setup"]["my_menus"]
            if menu["name"] == "SWITCH"
        )
        switch["settings"].remove("autofocus.subject_detection")
        people_path = self.root / "10 Profiles" / "People.yaml"
        people_path.write_bytes(self.model._dump_profile(people))
        model = ProfileEditorModel(self.root, source_validator=lambda _root: [])
        values = dict(model.baseline_detail()["values"])
        analysis = model.baseline_impact(values)
        self.assertEqual(analysis["summary"]["changed_settings"], 0)
        people_impact = next(
            profile for profile in analysis["my_menu_impact"]["profiles"]
            if profile["name"] == "People"
        )
        self.assertTrue(
            any(cue["path"] == "autofocus.subject_detection" for cue in people_impact["missing_card_cues"])
        )
        review = model.review_baseline_migration({
            "values": values,
            "decisions": [],
            "myMenuTabs": None,
            "acknowledgeCxImpact": True,
            "acknowledgeMyMenuImpact": True,
        })
        self.assertNotIn("00 Master/baseline.yaml", review["sourceFiles"])
        self.assertIn("10 Profiles/People.yaml", review["sourceFiles"])
        result = model.save_baseline_migration(review["reviewToken"])
        self.assertEqual(result["validation"], "passed")
        saved = load_yaml(people_path)
        switch = next(menu for menu in saved["card"]["field_setup"]["my_menus"] if menu["name"] == "SWITCH")
        self.assertIn("autofocus.subject_detection", switch["settings"])

    def test_zero_baseline_change_plans_all_non_cx_card_cues(self):
        field_test = deepcopy(self.model.profiles["Travel"])
        field_test["title"] = "Field Test"
        field_test.pop("card", None)
        defaults = deepcopy(self.model.profiles["Camera Defaults"])
        defaults["card"]["field_setup"]["my_menus"] = [
            menu for menu in defaults["card"]["field_setup"]["my_menus"]
            if menu["name"] != "test"
        ]
        essentials = deepcopy(self.model.profiles["Camera Setup Essentials"])
        essentials["card"].pop("field_setup", None)
        for name, profile in (
            ("Field Test", field_test),
            ("Camera Defaults", defaults),
            ("Camera Setup Essentials", essentials),
        ):
            (self.root / "10 Profiles" / f"{name}.yaml").write_bytes(self.model._dump_profile(profile))
        model = ProfileEditorModel(self.root, source_validator=lambda _root: [])
        values = dict(model.baseline_detail()["values"])
        plan = model.baseline_plan(values, [])
        self.assertTrue(plan["complete"])
        self.assertGreater(plan["summary"]["profile_card_cues_to_add"], 0)
        self.assertEqual(
            {item["profile"] for item in plan["profile_card_cues_to_add"]},
            {"Field Test", "Camera Setup Essentials"},
        )
        review = model.review_baseline_migration({
            "values": values,
            "decisions": [],
            "myMenuTabs": None,
            "acknowledgeCxImpact": True,
            "acknowledgeMyMenuImpact": True,
        })
        self.assertEqual(
            set(review["sourceFiles"]),
            {
                "10 Profiles/Field Test.yaml",
                "10 Profiles/Camera Setup Essentials.yaml",
            },
        )

    def test_zero_baseline_change_removes_card_cues_for_removed_my_menu_tab(self):
        field_test = deepcopy(self.model.profiles["Travel"])
        field_test["title"] = "Field Test"
        field_test.setdefault("card", {})["field_setup"] = {
            "my_menus": [{"name": "test", "settings": ["shutter.type"]}],
        }
        field_test_path = self.root / "10 Profiles" / "Field Test.yaml"
        field_test_path.write_bytes(self.model._dump_profile(field_test))
        model = ProfileEditorModel(self.root, source_validator=lambda _root: [])
        tabs = [
            tab for tab in model.dictionary_detail()["myMenu"]["saved_tabs"]
            if tab["name"] != "test"
        ]
        values = dict(model.baseline_detail()["values"])
        plan = model.baseline_plan(values, [], tabs)
        removals = [
            item for item in plan["profile_card_cues_to_remove"]
            if item["tab"] == "test"
        ]
        self.assertGreater(len(removals), 0)
        self.assertTrue(any(item["profile"] == "Field Test" for item in removals))
        review = model.review_baseline_migration({
            "values": values,
            "decisions": [],
            "myMenuTabs": tabs,
            "acknowledgeCxImpact": True,
            "acknowledgeMyMenuImpact": True,
        })
        self.assertNotIn("00 Master/baseline.yaml", review["sourceFiles"])
        self.assertIn("10 Profiles/Field Test.yaml", review["sourceFiles"])
        result = model.save_baseline_migration(review["reviewToken"])
        self.assertEqual(result["validation"], "passed")
        field_test = load_yaml(field_test_path)
        self.assertNotIn(
            "test",
            [menu["name"] for menu in field_test.get("card", {}).get("field_setup", {}).get("my_menus", [])],
        )

    def test_baseline_impact_rejects_added_or_removed_paths(self):
        values = dict(self.model.baseline_detail()["values"])
        removed = dict(values)
        removed.pop("shutter.type")
        with self.assertRaisesRegex(PrototypeError, "cannot remove settings"):
            self.model.baseline_impact(removed)
        added = dict(values)
        added["unapproved.setting"] = "value"
        with self.assertRaisesRegex(PrototypeError, "cannot add settings"):
            self.model.baseline_impact(added)

    def test_baseline_impact_rejects_incompatible_values(self):
        values = dict(self.model.baseline_detail()["values"])
        values["exposure.auto_iso.maximum"] = "not a number"
        with self.assertRaisesRegex(PrototypeError, "must be an integer"):
            self.model.baseline_impact(values)

    def test_baseline_impact_reports_cx_and_starting_mode_warnings_without_writes(self):
        tracker_path = self.root / "90 Testing" / "eos_r5_verification_tracker.yaml"
        baseline_path = self.root / "00 Master" / "baseline.yaml"
        profile_path = self.root / "10 Profiles" / "Wildlife.yaml"
        before = {
            tracker_path: tracker_path.read_bytes(),
            baseline_path: baseline_path.read_bytes(),
            profile_path: profile_path.read_bytes(),
        }
        values = dict(self.model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        result = self.model.baseline_impact(values)
        cx_impact = result["cx_impact"]
        self.assertEqual(
            [mode["heading"] for mode in cx_impact["registered_modes"]],
            ["C1 Wildlife", "C2 Birds in Flight", "C3 Landscape"],
        )
        self.assertGreater(cx_impact["summary"]["affected_registered_modes"], 0)
        self.assertTrue(
            any(warning["start"] == "C1" for warning in cx_impact["route_warnings"])
        )
        self.assertGreaterEqual(result["my_menu_impact"]["summary"]["profiles_analyzed"], 10)
        camera_defaults = next(
            profile
            for profile in result["my_menu_impact"]["profiles"]
            if profile["name"] == "Camera Defaults"
        )
        self.assertFalse(camera_defaults["access_only"])
        self.assertEqual(camera_defaults["start"], "C1")
        self.assertEqual(camera_defaults["source_profile"], "Wildlife")
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_baseline_impact_checks_session_my_menu_availability_without_writes(self):
        catalog_path = self.root / "80 Build" / "profile_editor" / "canon_options.yaml"
        profile_path = self.root / "10 Profiles" / "People.yaml"
        before = {catalog_path: catalog_path.read_bytes(), profile_path: profile_path.read_bytes()}
        values = dict(self.model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        tabs = [
            {"name": "SWITCH", "items": []},
            {
                "name": "AF Case",
                "items": [
                    "af3_servo_af_characteristics",
                    "af3_tracking_sensitivity",
                    "af3_accel_decel_tracking",
                    "af4_switching_tracked_subjects",
                ],
            },
        ]
        result = self.model.baseline_impact(values, tabs)
        people = next(
            profile
            for profile in result["my_menu_impact"]["profiles"]
            if profile["name"] == "People"
        )
        subject_route = next(
            item
            for item in people["declared_settings"]
            if item["path"] == "autofocus.subject_detection"
        )
        self.assertTrue(subject_route["displayed_after"])
        self.assertTrue(subject_route["availability_problem"])
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_baseline_plan_validates_decisions_without_writing_sources(self):
        baseline_path = self.root / "00 Master" / "baseline.yaml"
        profile_paths = sorted((self.root / "10 Profiles").glob("*.yaml"))
        before_baseline = baseline_path.read_bytes()
        before_profiles = {path: path.read_bytes() for path in profile_paths}
        travel_menus = self.model.profiles["Travel"]["card"]["field_setup"].get("my_menus") or []
        for menu in travel_menus:
            if menu.get("name") == "AF Case":
                menu["settings"] = [
                    path for path in menu.get("settings") or []
                    if path != "autofocus.servo_af_case"
                ]
        values = dict(self.model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        analysis = self.model.baseline_impact(values)
        decisions = [
            {
                "profile": profile["name"],
                "path": change["path"],
                "decision": "preserve_previous",
            }
            for change in analysis["changes"]
            for profile in change["profiles"]
            if profile["classification"] == "inherited_change"
        ]
        result = self.model.baseline_plan(values, decisions)
        self.assertTrue(result["complete"])
        self.assertEqual(result["summary"]["overrides_to_add"], len(decisions))
        self.assertGreater(result["summary"]["overrides_to_remove"], 0)
        self.assertGreater(result["summary"]["profile_card_cues_to_add"], 0)
        self.assertTrue(
            any(
                item["profile"] == "Travel" and item["tab"] == "AF Case"
                for item in result["profile_card_cues_to_add"]
            )
        )
        self.assertEqual(baseline_path.read_bytes(), before_baseline)
        self.assertEqual({path: path.read_bytes() for path in profile_paths}, before_profiles)

    def test_baseline_plan_reports_missing_choices_as_unresolved(self):
        values = dict(self.model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        result = self.model.baseline_plan(values, [])
        self.assertFalse(result["complete"])
        self.assertGreater(result["summary"]["unresolved_decisions"], 0)

    def test_baseline_plan_rejects_stale_decisions(self):
        values = dict(self.model.baseline_detail()["values"])
        values["shutter.type"] = "Mechanical"
        with self.assertRaisesRegex(PrototypeError, "Stale or inapplicable"):
            self.model.baseline_plan(
                values,
                [{
                    "profile": "Not a profile",
                    "path": "shutter.type",
                    "decision": "follow_baseline",
                }],
            )

    def test_applies_reviewed_baseline_migration_to_all_candidate_sources(self):
        review = self.model.review_baseline_migration(self.migration_payload())
        self.assertIn("00 Master/baseline.yaml", review["sourceFiles"])
        self.assertIn("--- a/00 Master/baseline.yaml", review["diff"])
        self.assertGreater(len(review["sourceFiles"]), 1)
        result = self.model.save_baseline_migration(review["reviewToken"])
        saved_baseline = load_yaml(self.root / "00 Master" / "baseline.yaml")
        self.assertEqual(saved_baseline["defaults"]["shutter"]["type"], "Mechanical")
        self.assertEqual(result["validation"], "passed")
        self.assertTrue(Path(result["backup"]).is_dir())
        with self.assertRaisesRegex(ProfileConflictError, "expired or was already used"):
            self.model.save_baseline_migration(review["reviewToken"])

    def test_baseline_migration_preserves_explicit_registration_matching_new_baseline(self):
        def spreadsheet_errors(root):
            return [
                issue.message
                for issue in spreadsheet_spec_validator.validate(root)
                if issue.level == "error"
            ]

        model = ProfileEditorModel(self.root, source_validator=spreadsheet_errors)
        values = dict(model.baseline_detail()["values"])
        values["exposure.mode"] = "Tv"
        analysis = model.baseline_impact(values)
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
        review = model.review_baseline_migration({
            "values": values,
            "decisions": decisions,
            "myMenuTabs": None,
            "acknowledgeCxImpact": True,
            "acknowledgeMyMenuImpact": True,
        })
        result = model.save_baseline_migration(review["reviewToken"])

        saved_baseline = load_yaml(self.root / "00 Master" / "baseline.yaml")
        tracker = load_yaml(self.root / "90 Testing" / "eos_r5_verification_tracker.yaml")
        mode_row = next(
            row for row in tracker["registration"]["rows"] if row["setting"] == "Mode"
        )
        self.assertEqual(saved_baseline["defaults"]["exposure"]["mode"], "Tv")
        self.assertEqual(mode_row["c2"], "Tv")
        self.assertEqual(result["validation"], "passed")

    def test_baseline_migration_requires_both_warning_acknowledgements(self):
        with self.assertRaisesRegex(PrototypeError, "C1–C3"):
            self.model.review_baseline_migration(
                self.migration_payload(acknowledgeCxImpact=False)
            )
        with self.assertRaisesRegex(PrototypeError, "My Menu"):
            self.model.review_baseline_migration(
                self.migration_payload(acknowledgeMyMenuImpact=False)
            )

    def test_baseline_migration_blocks_if_any_reviewed_source_changes(self):
        review = self.model.review_baseline_migration(self.migration_payload())
        baseline_path = self.root / "00 Master" / "baseline.yaml"
        baseline_path.write_bytes(baseline_path.read_bytes() + b"\n# concurrent edit\n")
        with self.assertRaisesRegex(ProfileConflictError, "changed after review"):
            self.model.save_baseline_migration(review["reviewToken"])

    def test_baseline_migration_restores_every_written_file_on_validation_failure(self):
        failing = ProfileEditorModel(self.root, source_validator=lambda _root: ["forced migration failure"])
        review = failing.review_baseline_migration(self.migration_payload(failing))
        paths = [self.root / relative for relative in review["sourceFiles"]]
        before = {path: path.read_bytes() for path in paths}
        with self.assertRaisesRegex(PrototypeError, "every written source was restored"):
            failing.save_baseline_migration(review["reviewToken"])
        self.assertEqual({path: path.read_bytes() for path in paths}, before)


if __name__ == "__main__":
    unittest.main()
