#!/usr/bin/env python3
"""Focused tests for canonical Canon feature-interaction rules."""

import copy
import sys
import unittest
from pathlib import Path

import yaml


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from feature_interactions import evaluate, load_catalog, validate_catalog  # noqa: E402
from utilities import flatten  # noqa: E402


class FeatureInteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(PROJECT_ROOT)
        baseline = yaml.safe_load((PROJECT_ROOT / "00 Master" / "baseline.yaml").read_text(encoding="utf-8"))
        cls.known_paths = set(flatten(baseline["defaults"]))

    def ids(self, settings, **kwargs):
        return {rule["id"] for rule in evaluate(settings, self.catalog, **kwargs)}

    def test_manual_focus_and_focus_bracketing_rules_match(self):
        ids = self.ids(
            {
                "autofocus": {"operation": "Manual Focus"},
                "image": {"focus_bracketing": "Enable"},
            },
            surface="card",
        )
        self.assertIn("manual_focus_disables_af_features", ids)
        self.assertIn("focus_bracketing_disables_flash", ids)

    def test_high_speed_display_rule_respects_electronic_exception(self):
        settings = {
            "display": {"high_speed_display": "Enable"},
            "drive": {"mode": "High Speed Continuous+"},
            "shutter": {"type": "Mechanical"},
        }
        self.assertIn("high_speed_display_selectable_context", self.ids(settings, surface="card"))
        settings["shutter"]["type"] = "Electronic"
        self.assertNotIn("high_speed_display_selectable_context", self.ids(settings, surface="card"))

    def test_lens_rules_do_not_guess_missing_context(self):
        settings = {"stabilization": {"ibis": "On", "lens_is": "On"}}
        self.assertNotIn("lens_is_switch_replaces_camera_menu", self.ids(settings, surface="editor"))
        context = {"lens": {"has_optical_is": True, "has_is_switch": True, "is_enabled": True}}
        ids = self.ids(settings, surface="editor", context=context)
        self.assertIn("lens_is_switch_replaces_camera_menu", ids)
        self.assertIn("lens_and_body_is_coordinate", ids)

    def test_card_surface_excludes_context_only_lens_messages(self):
        settings = {"stabilization": {"ibis": "On", "lens_is": "On"}}
        context = {"lens": {"has_optical_is": True, "has_is_switch": True, "is_enabled": True}}
        self.assertNotIn("lens_is_switch_replaces_camera_menu", self.ids(settings, surface="card", context=context))

    def test_catalog_rejects_unknown_setting_path(self):
        changed = copy.deepcopy(self.catalog)
        changed["rules"][0]["effects"][0]["setting_paths"].append("unknown.setting")
        errors = validate_catalog(changed, self.known_paths)
        self.assertTrue(any("unknown effect setting path unknown.setting" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
