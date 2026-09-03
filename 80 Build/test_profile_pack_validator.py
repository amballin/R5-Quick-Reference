#!/usr/bin/env python3
"""CLI and source-routing tests for external profile-pack validation."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_profile_pack_build import PROJECT_ROOT, write_pack_from_embedded_sources


class ProfilePackValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.pack = self.base / "private-pack"
        self.workspace = self.base / "workspace"
        write_pack_from_embedded_sources(self.pack)

    def tearDown(self):
        self.temp.cleanup()

    def _validate(self):
        env = {**os.environ, "PRS_LOCAL_WORKSPACE": str(self.workspace)}
        return subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "80 Build" / "validator.py"),
                "--root",
                str(PROJECT_ROOT),
                "--profile-pack",
                str(self.pack),
                "--source-only",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def test_external_source_validation_cli_passes_and_names_pack(self):
        completed = self._validate()
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("External profile pack: Embedded parity fixture", completed.stdout)
        self.assertIn("Errors: 0", completed.stdout)
        self.assertIn("Profile Editor guarded-write readiness passed for the selected external pack", completed.stdout)

    def test_external_source_validation_reads_pack_baseline(self):
        (self.pack / "00 Master" / "baseline.yaml").write_text("{}\n", encoding="utf-8")
        completed = self._validate()
        self.assertEqual(completed.returncode, 1)
        self.assertIn(str(self.pack / "00 Master" / "baseline.yaml"), completed.stdout)
        self.assertIn("Missing required key: metadata", completed.stdout)


if __name__ == "__main__":
    unittest.main()
