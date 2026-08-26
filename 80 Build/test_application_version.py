#!/usr/bin/env python3
"""Tests for shared Profile Editor and Camera Lab versioning."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from application_version import application_version_info, complete_development_update


BASE_COMMIT = "a" * 40
NEXT_COMMIT = "b" * 40


class ApplicationVersionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="application-version-tests-")
        self.root = Path(self.temporary.name)
        version_file = self.root / "00 Master" / "application_version.yaml"
        version_file.parent.mkdir(parents=True)
        version_file.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "major": 0,
                    "minor": 42,
                    "base_commit": BASE_COMMIT,
                    "incremental": 6,
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary.cleanup()

    @patch("application_version.project_context_info")
    @patch("application_version._git_state")
    def test_shared_version_uses_configured_incremental_at_base_commit(self, git_state, context):
        git_state.return_value = (BASE_COMMIT, 0)
        context.return_value = {"kind": "prototype", "label": "Prototype · test", "branch": "test"}
        info = application_version_info(self.root)
        self.assertEqual(info["version"], "0.42.6")
        self.assertEqual(info["context_name"], "Prototype")

    @patch("application_version.project_context_info")
    @patch("application_version._git_state")
    def test_commit_advances_minor_and_resets_incremental(self, git_state, context):
        git_state.return_value = (NEXT_COMMIT, 1)
        context.return_value = {"kind": "main", "label": "Main project", "branch": "main"}
        info = application_version_info(self.root)
        self.assertEqual(info["version"], "0.43.0")
        self.assertEqual(info["context_name"], "Main")

    @patch("application_version.project_context_info")
    @patch("application_version._git_state")
    def test_completed_update_reanchors_after_commit_and_advances_once(self, git_state, context):
        git_state.side_effect = [(NEXT_COMMIT, 1), (NEXT_COMMIT, 0)]
        context.return_value = {"kind": "prototype", "label": "Prototype · test", "branch": "test"}
        info = complete_development_update(self.root)
        self.assertEqual(info["version"], "0.43.1")
        payload = yaml.safe_load((self.root / "00 Master/application_version.yaml").read_text())
        self.assertEqual(payload["base_commit"], NEXT_COMMIT)
        self.assertEqual(payload["minor"], 43)
        self.assertEqual(payload["incremental"], 1)


if __name__ == "__main__":
    unittest.main()
