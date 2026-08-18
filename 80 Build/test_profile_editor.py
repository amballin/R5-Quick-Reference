#!/usr/bin/env python3
"""Integration tests for guarded Stage 2 profile-editor transactions."""

from pathlib import Path
import shutil
import tempfile
import unittest


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent

import sys

if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from profile_editor import ProfileConflictError, ProfileEditorModel, PrototypeError
from profile_loader import load_yaml


class ProfileEditorTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="profile-editor-tests-")
        self.root = Path(self.temporary.name) / "repository"
        self.root.mkdir()
        for directory in ("00 Master", "10 Profiles", "50 Field Guide", "60 Assets", "90 Testing"):
            shutil.copytree(PROJECT_ROOT / directory, self.root / directory)
        catalog = self.root / "80 Build" / "profile_editor" / "canon_options.yaml"
        catalog.parent.mkdir(parents=True)
        shutil.copy2(PROJECT_ROOT / "80 Build" / "profile_editor" / "canon_options.yaml", catalog)
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

    def test_updates_existing_profile_after_exact_review(self):
        review = self.model.review_profile(self.payload(title="Fireworks Review Test"))
        self.assertIn("Fireworks Review Test", review["diff"])
        result = self.model.save_profile(review["reviewToken"])
        saved = load_yaml(self.root / "10 Profiles" / "Fireworks.yaml")
        self.assertEqual(saved["title"], "Fireworks Review Test")
        self.assertEqual(result["validation"], "passed")
        self.assertTrue(Path(result["backup"]).is_dir())

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
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_baseline_plan_validates_decisions_without_writing_sources(self):
        baseline_path = self.root / "00 Master" / "baseline.yaml"
        profile_paths = sorted((self.root / "10 Profiles").glob("*.yaml"))
        before_baseline = baseline_path.read_bytes()
        before_profiles = {path: path.read_bytes() for path in profile_paths}
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


if __name__ == "__main__":
    unittest.main()
