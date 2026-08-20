#!/usr/bin/env python3
"""Tests for subject-settings Matrix route labels."""

from pathlib import Path
import sys
import unittest


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from subject_settings_matrix import _card_start_label


class SubjectSettingsMatrixRouteTests(unittest.TestCase):
    def test_non_cx_route_keeps_named_my_menu_access(self):
        label = _card_start_label(
            {
                "my_menus": [
                    {"name": "AF Case", "settings": ["autofocus.switching_tracked_subjects"]},
                    {"name": "SWITCH", "settings": ["shutter.type"]},
                ]
            },
            "Androo",
        )
        self.assertEqual(label, "No Cx + AF Case + SWITCH")

    def test_profile_without_route_remains_blank(self):
        self.assertEqual(_card_start_label({}, "Unrouted"), "")


if __name__ == "__main__":
    unittest.main()
