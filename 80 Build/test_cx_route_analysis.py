#!/usr/bin/env python3
"""Tests for derived Cx foundation changes and card indicators."""

from copy import deepcopy
from pathlib import Path
import re
import sys
import unittest


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from asset_manager import ProjectPaths
from baseline import merge
from cx_route_analysis import (
    CxRouteAnalysisError,
    analyze_selected_foundation,
    row_requires_change,
)
from html_renderer import rapid_setup_rows, settings_section, table
from profile_loader import load_baseline, load_yaml


class CxRouteAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {
            "defaults": {
                "autofocus": {"subject_detection": "Animals"},
                "drive": {"mode": "High Speed Continuous"},
                "stabilization": {"ibis": "On", "lens_is": "On"},
            }
        }
        self.foundation = {
            "card_id": "11111111-1111-4111-8111-111111111111",
            "title": "Wildlife",
            "overrides": {"autofocus": {"subject_detection": "Animals"}},
        }
        self.profile = {
            "card_id": "22222222-2222-4222-8222-222222222222",
            "title": "People",
            "card": {"field_setup": {"start": "C1", "source_card_id": "11111111-1111-4111-8111-111111111111"}},
            "overrides": {
                "autofocus": {"subject_detection": "People"},
                "drive": {"mode": "Low Speed Continuous"},
            },
        }
        self.profiles = {"Wildlife": self.foundation, "People": self.profile}
        self.merged = merge(self.baseline["defaults"], self.profile["overrides"])

    def test_reports_only_visible_values_that_differ_from_foundation(self):
        result = analyze_selected_foundation(
            self.profile,
            self.merged,
            self.profiles,
            self.baseline,
            {"autofocus.subject_detection", "stabilization.ibis", "stabilization.lens_is"},
        )
        self.assertEqual(result["foundation_label"], "C1 Wildlife")
        self.assertEqual(result["changed_paths"], {"autofocus.subject_detection"})

    def test_combined_row_changes_when_any_underlying_value_changes(self):
        self.merged["stabilization"]["lens_is"] = "Off"
        result = analyze_selected_foundation(
            self.profile,
            self.merged,
            self.profiles,
            self.baseline,
            {"stabilization.ibis", "stabilization.lens_is"},
        )
        self.assertTrue(row_requires_change("stabilization.ibis", result["changed_paths"]))

    def test_foundation_profile_has_no_changes(self):
        source = {
            **self.foundation,
            "card": {"field_setup": {"start": "C1", "source_card_id": "11111111-1111-4111-8111-111111111111"}},
        }
        merged = merge(self.baseline["defaults"], source["overrides"])
        profiles = {**self.profiles, "Wildlife": source}
        result = analyze_selected_foundation(
            source, merged, profiles, self.baseline, {"autofocus.subject_detection"}
        )
        self.assertEqual(result["changed_paths"], set())

    def test_access_only_card_marks_every_visible_setting_for_verification(self):
        profile = {
            "title": "Defaults",
            "card": {"field_setup": {"access_only": True}},
            "overrides": {},
        }
        result = analyze_selected_foundation(
            profile,
            self.baseline["defaults"],
            {},
            self.baseline,
            {"drive.mode", "stabilization.ibis"},
        )
        self.assertEqual(result["changed_paths"], {"drive.mode", "stabilization.ibis"})
        self.assertEqual(result["legend_label"], "Verify/set — no Cx foundation")

    def test_profile_without_field_setup_marks_every_visible_setting(self):
        result = analyze_selected_foundation(
            {"title": "Unregistered", "overrides": {}},
            self.baseline["defaults"],
            {},
            self.baseline,
            {"autofocus.subject_detection"},
        )
        self.assertEqual(result["changed_paths"], {"autofocus.subject_detection"})
        self.assertEqual(result["change_label"], "Verify or set — no Cx foundation")

    def test_rejects_unknown_foundation_without_mutating_inputs(self):
        before = deepcopy((self.profile, self.merged, self.profiles, self.baseline))
        broken = deepcopy(self.profile)
        broken["card"]["field_setup"]["source_card_id"] = "33333333-3333-4333-8333-333333333333"
        with self.assertRaisesRegex(CxRouteAnalysisError, "exactly one profile"):
            analyze_selected_foundation(
                broken, self.merged, self.profiles, self.baseline, {"drive.mode"}
            )
        self.assertEqual((self.profile, self.merged, self.profiles, self.baseline), before)


class CxCardIndicatorIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = ProjectPaths(PROJECT_ROOT)
        cls.baseline = load_baseline(cls.paths)

    def rendered_rows(self, name):
        profile = load_yaml(self.paths.profile_file(name))
        merged = merge(self.baseline["defaults"], profile.get("overrides") or {})
        return profile, merged, table(profile, merged, paths=self.paths, baseline=self.baseline)

    def test_my_menu_color_remains_when_matching_cx_and_delta_marks_only_difference(self):
        _profile, _merged, html = self.rendered_rows("People")
        rows = re.findall(r"<tr>.*?</tr>", html)
        subject = next(row for row in rows if "Subject Detection" in row)
        stabilization = next(row for row in rows if "Image Stabilization" in row)
        self.assertIn('field-value access-switch', subject)
        self.assertIn('style="color:#72dda8"', subject)
        self.assertIn(">Δ</span>", subject)
        self.assertRegex(subject, r'field-change" style="color:#72dda8"[^>]*>')
        self.assertIn('field-value access-switch', stabilization)
        self.assertNotIn(">Δ</span>", stabilization)

    def test_foundation_card_reserves_blank_column_and_has_no_delta(self):
        _profile, _merged, html = self.rendered_rows("Wildlife")
        self.assertIn('class="has-change-column"', html)
        self.assertIn('class="field-change" aria-hidden="true"', html)
        self.assertNotIn(">Δ</span>", html)

    def test_settings_section_includes_foundation_legend(self):
        profile = load_yaml(self.paths.profile_file("People"))
        merged = merge(self.baseline["defaults"], profile.get("overrides") or {})
        html = settings_section(profile, merged, paths=self.paths, baseline=self.baseline)
        self.assertIn("Δ</span> Change from C1 Wildlife", html)

    def test_subject_card_leads_with_changed_rows_in_setup_route_order(self):
        profile = load_yaml(self.paths.profile_file("People"))
        merged = merge(self.baseline["defaults"], profile.get("overrides") or {})
        html = settings_section(profile, merged, paths=self.paths, baseline=self.baseline)
        change_section, settings = html.split("<h2>Settings</h2>", 1)
        self.assertIn("<h2>Change from C1 Wildlife</h2>", change_section)
        self.assertIn("Q screen", change_section)
        self.assertIn("My Menu → SWITCH", change_section)
        self.assertLess(change_section.index("Q screen"), change_section.index("My Menu → SWITCH"))
        self.assertIn("Subject Detection", change_section)
        self.assertNotIn("Image Stabilization", change_section)
        self.assertIn("Image Stabilization", settings)

    def test_foundation_card_reports_that_no_camera_changes_are_needed(self):
        profile = load_yaml(self.paths.profile_file("Wildlife"))
        merged = merge(self.baseline["defaults"], profile.get("overrides") or {})
        html = settings_section(profile, merged, paths=self.paths, baseline=self.baseline)
        self.assertIn("<h2>Change from C1 Wildlife</h2>", html)
        self.assertIn("No camera changes are needed from this foundation.", html)

    def test_setup_cards_use_full_rapid_route_instead_of_shooting_order(self):
        profile = load_yaml(self.paths.profile_file("Camera Defaults"))
        merged = merge(self.baseline["defaults"], profile.get("overrides") or {})
        rows = rapid_setup_rows(profile, merged, self.paths)
        groups = [row["route"]["group_label"] for row in rows]
        html = settings_section(profile, merged, paths=self.paths, baseline=self.baseline)
        self.assertIn("<h2>Rapid Camera Setup</h2>", html)
        self.assertNotIn("<h2>Settings</h2>", html)
        self.assertIn("Buttons, dials & switches", groups)
        self.assertIn("Q screen", groups)
        self.assertIn("My Menu → SWITCH", groups)
        self.assertLess(groups.index("Buttons, dials & switches"), groups.index("Q screen"))
        self.assertLess(groups.index("Q screen"), groups.index("My Menu → SWITCH"))

    def test_every_editable_profile_card_renders_change_column(self):
        rendered_routes = 0
        for source in sorted(self.paths.profiles_dir.glob("*.yaml")):
            profile = load_yaml(source)
            if profile.get("card_type") == "reference":
                continue
            merged = merge(self.baseline["defaults"], profile.get("overrides") or {})
            html = table(profile, merged, paths=self.paths, baseline=self.baseline)
            setup = ((profile.get("card") or {}).get("field_setup") or {})
            if setup.get("start"):
                rendered_routes += 1
                self.assertIn('class="has-change-column"', html, source.name)
            else:
                self.assertIn('class="has-change-column"', html, source.name)
                self.assertIn(">Δ</span>", html, source.name)
        self.assertGreater(rendered_routes, 0)

    def test_non_cx_settings_section_uses_verification_legend(self):
        profile = deepcopy(load_yaml(self.paths.profile_file("Travel")))
        profile["title"] = "Unregistered Test Profile"
        profile.get("card", {}).pop("field_setup", None)
        merged = merge(self.baseline["defaults"], profile.get("overrides") or {})
        html = settings_section(profile, merged, paths=self.paths, baseline=self.baseline)
        self.assertIn("Δ</span> Verify/set — no Cx foundation", html)


if __name__ == "__main__":
    unittest.main()
