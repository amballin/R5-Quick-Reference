#!/usr/bin/env python3
"""Tests for ownership, cleanup, and recovery of Apple Numbers automation."""

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

import numbers_automation
from numbers_automation import (
    NUMBERS_BUSY_MARKER,
    NUMBERS_CLEANUP_MARKER,
    NumbersApplication,
    NumbersAutomationError,
    numbers_resume_recovery,
    run_numbers_applescript,
)
from spreadsheet_downloads import _matrix_finalize_script, _setup_finalize_script
from asset_manager import ProjectPaths


class NumbersAutomationTests(unittest.TestCase):
    def setUp(self):
        self.application = NumbersApplication("com.apple.Numbers", Path("/Applications/Numbers.app"))

    def test_existing_numbers_session_is_never_touched(self):
        with patch.object(numbers_automation, "_running_numbers_bundle_ids", return_value={"com.apple.Numbers"}), \
                patch.object(numbers_automation, "ensure_numbers_running") as launch:
            with self.assertRaisesRegex(NumbersAutomationError, NUMBERS_BUSY_MARKER):
                run_numbers_applescript("return 1", "test")
        launch.assert_not_called()

    def test_successful_operation_quits_automation_owned_numbers(self):
        result = subprocess.CompletedProcess(["osascript"], 0, stdout="ready\n", stderr="")
        with patch.object(numbers_automation, "_running_numbers_bundle_ids", return_value=set()), \
                patch.object(numbers_automation, "numbers_applications", return_value=[self.application]), \
                patch.object(numbers_automation, "ensure_numbers_running") as launch, \
                patch.object(numbers_automation, "_quit_numbers") as quit_numbers, \
                patch.object(numbers_automation.subprocess, "run", return_value=result):
            completed, application = run_numbers_applescript(
                "return \"ready\"", "test", success=lambda candidate: candidate.stdout.strip() == "ready"
            )
        launch.assert_called_once_with(self.application, cleanup_on_failure=True)
        quit_numbers.assert_called_once_with(self.application)
        self.assertIs(completed, result)
        self.assertEqual(application, self.application)

    def test_cleanup_failure_returns_simple_resume_recovery(self):
        result = subprocess.CompletedProcess(["osascript"], 0, stdout="ready\n", stderr="")
        with patch.object(numbers_automation, "_running_numbers_bundle_ids", return_value=set()), \
                patch.object(numbers_automation, "numbers_applications", return_value=[self.application]), \
                patch.object(numbers_automation, "ensure_numbers_running"), \
                patch.object(numbers_automation, "_quit_numbers", side_effect=NumbersAutomationError("still open")), \
                patch.object(numbers_automation.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(NumbersAutomationError, NUMBERS_CLEANUP_MARKER) as stopped:
                run_numbers_applescript("return \"ready\"", "test")
        recovery = numbers_resume_recovery(str(stopped.exception), "resume-local-build")
        self.assertEqual(recovery["actions"], ["resume-local-build"])
        self.assertIn("Save and close every Numbers window", recovery["summary"])

    def test_finalize_scripts_stay_backgrounded_and_close_documents(self):
        paths = ProjectPaths(BUILD_DIR.parent)
        matrix = _matrix_finalize_script(paths, Path("/tmp/matrix.numbers"), 10, 8, 4, 7)
        setup = _setup_finalize_script(paths, Path("/tmp/setup.numbers"))
        for script in (matrix, setup):
            self.assertNotIn("activate", script)
            self.assertIn("close targetDocument saving yes", script)
            self.assertLess(script.index("close targetDocument saving yes"), script.index("return finalizedProperties"))


if __name__ == "__main__":
    unittest.main()
