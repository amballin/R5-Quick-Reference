#!/usr/bin/env python3
"""Focused tests for field-card lens choices and compatibility."""

import sys
import unittest
from pathlib import Path

import yaml


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from baseline import merge  # noqa: E402
from lens_guidance import compatibility_messages, resolved_choices  # noqa: E402
from validators.lens_guidance_validator import validate  # noqa: E402


class LensGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = yaml.safe_load((PROJECT_ROOT / "00 Master" / "baseline.yaml").read_text(encoding="utf-8"))["defaults"]

    def profile(self, name):
        return yaml.safe_load((PROJECT_ROOT / "10 Profiles" / f"{name}.yaml").read_text(encoding="utf-8"))

    def test_every_subject_has_valid_guidance(self):
        self.assertEqual(validate(PROJECT_ROOT), [])

    def test_macro_lists_primary_and_specialist_lenses(self):
        profile = self.profile("Macro")
        choices = resolved_choices(profile, PROJECT_ROOT)
        self.assertEqual([item["display_name"] for item in choices], ["EF 100mm Macro", "MP-E 65mm"])
        self.assertEqual([item["role"] for item in choices], ["primary", "specialist"])

    def test_adapted_lenses_surface_control_ring_once(self):
        profile = self.profile("Macro")
        merged = merge(self.baseline, profile.get("overrides") or {})
        messages = compatibility_messages(profile, merged, PROJECT_ROOT)
        matches = [item for item in messages if "programmable ring remains available" in item]
        self.assertEqual(len(matches), 1)

    def test_ef_s_choice_surfaces_forced_crop(self):
        profile = self.profile("Travel")
        merged = merge(self.baseline, profile.get("overrides") or {})
        messages = compatibility_messages(profile, merged, PROJECT_ROOT)
        self.assertTrue(any("forces 1.6× crop" in item for item in messages))

    def test_mp_e_choice_surfaces_manual_focus_limitation(self):
        profile = self.profile("Macro")
        merged = merge(self.baseline, profile.get("overrides") or {})
        messages = compatibility_messages(profile, merged, PROJECT_ROOT)
        self.assertTrue(any("MP-E 65mm is manual-focus only" in item for item in messages))


if __name__ == "__main__":
    unittest.main()
