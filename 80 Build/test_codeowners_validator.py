#!/usr/bin/env python3
"""Tests for the exact GitHub application-owner routing boundary."""

from pathlib import Path
import tempfile
import unittest

from validators.codeowners_validator import EXPECTED_RULES, validate


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CodeownersValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / ".github").mkdir()
        self.path = self.root / ".github" / "CODEOWNERS"
        self.path.write_text("\n".join(EXPECTED_RULES) + "\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def test_repository_codeowners_boundary_is_current(self):
        self.assertEqual(validate(PROJECT_ROOT), [])

    def test_rejects_missing_boundary(self):
        self.path.unlink()
        self.assertTrue(any("missing" in issue.message for issue in validate(self.root)))

    def test_rejects_removed_or_reassigned_rule(self):
        self.path.write_text("\n".join(EXPECTED_RULES[:-1]) + "\n", encoding="utf-8")
        self.assertTrue(validate(self.root))

        reassigned = list(EXPECTED_RULES)
        reassigned[-1] = "/10\\ Profiles/ @someone-else"
        self.path.write_text("\n".join(reassigned) + "\n", encoding="utf-8")
        self.assertTrue(validate(self.root))

    def test_rejects_silent_broadening_or_later_override(self):
        lines = list(EXPECTED_RULES)
        lines.append("* @someone-else")
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertTrue(validate(self.root))


if __name__ == "__main__":
    unittest.main()
