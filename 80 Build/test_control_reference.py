#!/usr/bin/env python3
"""Tests for control references derived from controls.yaml."""

import sys
import tempfile
import unittest
from pathlib import Path

import yaml


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from control_reference import (  # noqa: E402
    card_reference_rows,
    card_reference_settings,
    inject_control_tables,
    markdown_table,
)


class ControlReferenceTests(unittest.TestCase):
    def test_project_card_and_tables_derive_from_controls(self):
        rows = card_reference_rows(PROJECT_ROOT)
        settings = card_reference_settings(PROJECT_ROOT)
        labels = [row["label"] for row in rows]

        self.assertEqual(len(rows), len(settings))
        self.assertIn("AF-ON button", labels)
        self.assertIn("M-Fn button", labels)
        self.assertNotIn("Movie Record", labels)
        af_on = next(row for row in rows if row["label"] == "AF-ON button")
        self.assertEqual(af_on["value"], "Metering and AF start")
        self.assertIn("AF Method: Face + Tracking", af_on["detail"])

        controls = markdown_table(PROJECT_ROOT, "controls")
        dials = markdown_table(PROJECT_ROOT, "dials")
        self.assertIn("| AF-ON | Metering and AF start |", controls)
        self.assertIn("| Control Ring | Exposure Compensation |", dials)

    def test_one_source_change_reaches_card_and_markdown(self):
        with tempfile.TemporaryDirectory(prefix="control-reference-test-") as temporary:
            root = Path(temporary)
            source = {
                "controls": [
                    {
                        "control": "AF-ON",
                        "assignment": "Test assignment",
                        "status": "owner_confirmed",
                        "info_details": {"af_method": "Test method"},
                    }
                ],
                "dials": [
                    {
                        "control": "Main Dial",
                        "assignment": "Test dial",
                        "status": "owner_confirmed",
                    }
                ],
            }
            (root / "controls.yaml").write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")

            rows = card_reference_rows(root)
            rendered = inject_control_tables(
                "<!-- CONTROL_REFERENCE_TABLE: controls -->\n<!-- CONTROL_REFERENCE_TABLE: dials -->",
                root,
            )
            self.assertEqual(rows[0]["value"], "Test assignment")
            self.assertIn("Test assignment", rendered)
            self.assertIn("Test dial", rendered)
            self.assertNotIn("CONTROL_REFERENCE_TABLE", rendered)

    def test_candidate_source_can_render_without_replacing_canonical_file(self):
        source = yaml.safe_load((PROJECT_ROOT / "controls.yaml").read_text(encoding="utf-8"))
        source["controls"][0]["assignment"] = "Candidate assignment"
        rows = card_reference_rows(PROJECT_ROOT, source=source)
        self.assertEqual(rows[0]["value"], "Candidate assignment")
        self.assertNotIn("Candidate assignment", (PROJECT_ROOT / "controls.yaml").read_text(encoding="utf-8"))

    def test_optional_control_with_custom_behavior_is_automatically_included(self):
        source = yaml.safe_load((PROJECT_ROOT / "controls.yaml").read_text(encoding="utf-8"))
        movie = next(item for item in source["controls"] if item["control"] == "Movie Record")
        self.assertNotIn("Movie Record", [row["label"] for row in card_reference_rows(PROJECT_ROOT, source=source)])

        movie["assignment"] = "Movie recording"
        self.assertIn("Movie Record", [row["label"] for row in card_reference_rows(PROJECT_ROOT, source=source)])


if __name__ == "__main__":
    unittest.main()
