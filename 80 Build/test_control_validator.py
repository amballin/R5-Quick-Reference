#!/usr/bin/env python3
"""Focused tests for camera-control terminology enforcement."""

import sys
import tempfile
import unittest
from pathlib import Path


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from validators.control_validator import _deprecated_af_workflow_issues  # noqa: E402


class DeprecatedAfWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="control-terminology-test-")
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_rejects_each_retired_workflow_term(self):
        phrases = (
            "Switch to registered AF function",
            "Use the registered-AF behavior",
            "Configure a registered AF override",
            "Treat this as an AF preset",
            "Use Register/Recall Shooting Function",
            "Canon abbreviation: Register/recall shooting func.",
        )
        for index, phrase in enumerate(phrases):
            with self.subTest(phrase=phrase):
                path = self.write(f"10 Profiles/Test {index}.yaml", f"notes:\n  - {phrase}\n")
                issues = _deprecated_af_workflow_issues(self.root)
                matches = [issue for issue in issues if issue.path == str(path)]
                self.assertEqual(len(matches), 1)
                self.assertIn("deprecated AF workflow terminology", matches[0].message)
                self.assertIn("AF-ON temporarily selects Face + Tracking", matches[0].message)

    def test_accepts_current_control_and_registered_mode_language(self):
        self.write(
            "50 Field Guide/Current.md",
            "AF-ON selects Face + Tracking. AE Lock selects 1-Point AF. "
            "C1 Wildlife is a complete registered shooting environment.\n",
        )
        self.assertEqual(_deprecated_af_workflow_issues(self.root), [])

    def test_excludes_literal_official_canon_reference(self):
        self.write(
            "50 Field Guide/Appendices/Canon EOS R5 Official Icon Reference.md",
            "Canon label: Switch to registered AF function.\n",
        )
        self.assertEqual(_deprecated_af_workflow_issues(self.root), [])


if __name__ == "__main__":
    unittest.main()
