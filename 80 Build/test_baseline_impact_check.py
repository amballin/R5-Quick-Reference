#!/usr/bin/env python3
"""Tests for the repository command-line baseline impact check."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from baseline_impact_check import analyze_repository, main


class BaselineImpactCheckTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="baseline-impact-check-")
        self.root = Path(self.temporary.name)
        (self.root / "00 Master").mkdir()
        (self.root / "10 Profiles").mkdir()
        self.baseline_path = self.root / "00 Master" / "baseline.yaml"
        self.baseline_path.write_text(
            yaml.safe_dump({"defaults": {"drive": {"mode": "Single Shot"}}}, sort_keys=False),
            encoding="utf-8",
        )
        (self.root / "10 Profiles" / "Travel.yaml").write_text(
            yaml.safe_dump(
                {"title": "Travel", "inherits": "baseline", "overrides": {}},
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        self.git("init", "-q")
        self.git("add", "00 Master/baseline.yaml", "10 Profiles/Travel.yaml")
        self.git(
            "-c",
            "user.name=Baseline Impact Tests",
            "-c",
            "user.email=baseline-impact@example.invalid",
            "commit",
            "-q",
            "-m",
            "fixture",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def test_clean_worktree_has_no_semantic_baseline_change(self):
        result = analyze_repository(self.root)
        self.assertEqual(result["summary"]["changed_settings"], 0)

    def test_changed_default_reports_inherited_profile_impact(self):
        self.baseline_path.write_text(
            yaml.safe_dump(
                {"metadata": {"last_updated": "2026-08-20"}, "defaults": {"drive": {"mode": "High Speed Continuous"}}},
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        result = analyze_repository(self.root)
        self.assertEqual(result["summary"]["changed_settings"], 1)
        self.assertEqual(result["changes"][0]["path"], "drive.mode")
        self.assertEqual(result["changes"][0]["profiles"][0]["classification"], "inherited_change")

        output = StringIO()
        with redirect_stdout(output):
            status = main(["--root", str(self.root)])
        self.assertEqual(status, 1)
        self.assertIn("Review required", output.getvalue())
        self.assertIn("Travel", output.getvalue())

    def test_metadata_only_change_is_ignored(self):
        self.baseline_path.write_text(
            yaml.safe_dump(
                {
                    "metadata": {"last_updated": "2026-08-20"},
                    "defaults": {"drive": {"mode": "Single Shot"}},
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        self.assertEqual(analyze_repository(self.root)["summary"]["changed_settings"], 0)

    def test_missing_ref_returns_usage_error(self):
        error = StringIO()
        with redirect_stderr(error):
            status = main(["--root", str(self.root), "--base-ref", "missing-ref"])
        self.assertEqual(status, 2)
        self.assertIn("Unable to read baseline", error.getvalue())


if __name__ == "__main__":
    unittest.main()
