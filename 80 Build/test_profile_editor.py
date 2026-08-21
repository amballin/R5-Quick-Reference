#!/usr/bin/env python3
"""Integration tests for guarded Stage 2 profile-editor transactions."""

from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent

import sys

if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from profile_editor import ProfileConflictError, ProfileEditorModel, PrototypeError
from profile_loader import load_yaml
from validators import spreadsheet_spec_validator


class ProfileEditorTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="profile-editor-tests-")
        self.root = Path(self.temporary.name) / "repository"
        self.root.mkdir()
        for directory in ("00 Master", "10 Profiles", "20 Templates", "50 Field Guide", "60 Assets", "90 Testing"):
            shutil.copytree(PROJECT_ROOT / directory, self.root / directory)
        catalog = self.root / "80 Build" / "profile_editor" / "canon_options.yaml"
        catalog.parent.mkdir(parents=True)
        shutil.copy2(PROJECT_ROOT / "80 Build" / "profile_editor" / "canon_options.yaml", catalog)
        for relative in (
            "80 Build/baseline_impact.py",
            "80 Build/baseline_migration.py",
            "80 Build/cx_route_analysis.py",
            "80 Build/html_renderer.py",
            "80 Build/my_menu.py",
            "80 Build/my_menu_colors.py",
            "80 Build/my_menu_reference.py",
            "80 Build/profile_editor.py",
            "80 Build/profile_editor/app.js",
            "80 Build/profile_editor/index.html",
            "80 Build/profile_editor/styles.css",
        ):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PROJECT_ROOT / relative, destination)
        self.model = ProfileEditorModel(self.root, source_validator=lambda _root: [])

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
            "release": detail["metadata"]["release"],
            "overrides": detail["originalOverrides"],
        }
        payload.update(changes)
        return payload

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
        result = self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Fireworks.yaml")
        self.assertEqual(saved["title"], "Fireworks Review Test")
        self.assertEqual(result["validation"], "passed")
        self.assertTrue(Path(result["backup"]).is_dir())

    def test_review_shows_effective_value_when_blank_override_returns_to_auto_baseline(self):
        payload = self.payload("Travel")
        overrides = dict(payload["overrides"])
        self.assertEqual(overrides.pop("lens.aperture.target"), "")
        review = self.model.review_profile({**payload, "overrides": overrides})

        aperture = next(
            change for change in review["effectiveChanges"]
            if change["path"] == "lens.aperture.target"
        )
        self.assertEqual(aperture["beforeDisplay"], "Blank")
        self.assertEqual(aperture["beforeSource"], "profile customization")
        self.assertEqual(aperture["afterDisplay"], "Auto")
        self.assertEqual(aperture["afterSource"], "inherited from baseline")
        self.assertIn("-      target: ''", review["diff"])

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
        review = self.model.review_profile({**payload, "overrides": overrides})

        aperture = next(
            change for change in review["effectiveChanges"]
            if change["path"] == "lens.aperture.target"
        )
        self.assertEqual(aperture["afterDisplay"], "Auto")
        self.assertEqual(aperture["afterSource"], "inherited from baseline")
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
            "release": True,
            "overrides": {"drive.mode": "Single Shot"},
        }
        self.assertEqual(detail["metadata"], {"status": "Draft", "release": False})
        review = self.model.review_profile(payload)
        self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Rainy Day.yaml")
        self.assertEqual(saved["metadata"]["status"], "Draft")
        self.assertFalse(saved["metadata"]["release"])
        self.assertEqual(saved["inherits"], "baseline")
        self.assertEqual(saved["overrides"], {"drive": {"mode": "Single Shot"}})

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
            "release": True,
            "overrides": detail["originalOverrides"],
        }
        review = self.model.review_profile(payload)
        self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Wildlife Alternate.yaml")
        source = load_yaml(self.root / "10 Profiles" / "Wildlife.yaml")
        self.assertEqual(saved["overrides"], source["overrides"])
        self.assertEqual(saved["metadata"]["status"], "Draft")
        self.assertFalse(saved["metadata"]["release"])

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
            "release": detail["metadata"]["release"],
            "overrides": detail["originalOverrides"],
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

    def test_editor_info_exposes_version_and_source_derived_build(self):
        first = self.model.editor_info()
        second = self.model.editor_info()
        self.assertEqual(first, second)
        self.assertEqual(first["version"], "1.0.0")
        self.assertRegex(first["build"], r"^[0-9a-f]{8}$")

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
        self.assertLess(html.index('data-view="profiles"'), html.index('data-view="my-menu"'))
        self.assertLess(html.index('data-view="my-menu"'), html.index('data-view="baseline"'))
        self.assertLess(html.index('data-view="baseline"'), html.index('data-view="review-build"'))
        self.assertLess(html.index('data-view="review-build"'), html.index('data-view="dictionary"'))
        self.assertIn('id="pending-change-list"', html)
        self.assertIn('id="build-confirm-dialog"', html)
        self.assertIn('window.addEventListener("beforeunload"', javascript)
        self.assertIn("profileDrafts: new Map()", javascript)

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
        self.assertTrue(camera_defaults["access_only"])
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
