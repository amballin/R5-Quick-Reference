#!/usr/bin/env python3
"""Regression tests for the shared guarded Finish Day workflow."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent

import sys

if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from finish_day import FinishDayError, FinishDayWorkflow


class FinishDayWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="finish-day-tests-")
        base = Path(self.temporary.name)
        self.root = base / "repository"
        self.remote = base / "remote.git"
        self.local = base / "local"
        (self.root / "80 Build" / "scripts").mkdir(parents=True)
        (self.root / "docs").mkdir()
        shutil.copy2(
            PROJECT_ROOT / "80 Build" / "scripts" / "git-status-report.sh",
            self.root / "80 Build" / "scripts" / "git-status-report.sh",
        )
        (self.root / "80 Build" / "verification_status.py").write_text(
            "print('Verification status current')\n", encoding="utf-8"
        )
        (self.root / "80 Build" / "validator.py").write_text(
            "print('Validation passed')\n", encoding="utf-8"
        )
        (self.root / "80 Build" / "build.py").write_text(
            "from pathlib import Path\n"
            "Path('docs/site.txt').write_text('generated\\n', encoding='utf-8')\n"
            "print('Build passed')\n",
            encoding="utf-8",
        )
        (self.root / "docs" / "site.txt").write_text("published\n", encoding="utf-8")
        (self.root / "source.txt").write_text("initial\n", encoding="utf-8")
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        subprocess.run(
            ["git", "init", "-b", "codex/finish-day-prototype"],
            cwd=self.root,
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "config", "user.name", "Finish Day Test"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "finish-day@example.invalid"], cwd=self.root, check=True
        )
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "Fixture"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", str(self.remote)], cwd=self.root, check=True)
        subprocess.run(
            ["git", "push", "-u", "origin", "codex/finish-day-prototype"],
            cwd=self.root,
            check=True,
            capture_output=True,
        )
        self.environment = patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(self.local)})
        self.environment.start()
        self.workflow = FinishDayWorkflow(self.root)

    def tearDown(self):
        self.environment.stop()
        self.temporary.cleanup()

    def test_prepare_commit_and_push_stay_on_matching_prototype_branch(self):
        (self.root / "source.txt").write_text("updated\n", encoding="utf-8")
        inspected = self.workflow.inspect(0)
        self.assertEqual(inspected["phase"], "prepare")
        self.assertEqual(inspected["upstream"], "origin/codex/finish-day-prototype")

        prepared = self.workflow.prepare(0, True)
        self.assertEqual(prepared["phase"], "commit")
        self.assertTrue(prepared["docsBackup"])
        self.assertEqual((self.root / "docs" / "site.txt").read_text(encoding="utf-8"), "published\n")
        self.assertTrue((Path(prepared["docsBackup"]) / "docs-working-tree.tar.gz").is_file())
        self.assertTrue(any("source.txt" in line for line in prepared["sourceFiles"]))
        self.assertFalse(any("docs/" in line for line in prepared["sourceFiles"]))

        committed = self.workflow.commit(prepared["reviewToken"], "Update source", True)
        self.assertEqual(committed["phase"], "push")
        pages = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^..HEAD", "--", "docs"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(pages.stdout, "")

        pushed = self.workflow.push(True)
        self.assertEqual(pushed["phase"], "complete")
        self.assertEqual(pushed["upstream"], "origin/codex/finish-day-prototype")
        branches = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"],
            cwd=self.remote,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(branches, ["codex/finish-day-prototype"])

    def test_review_expires_when_source_changes(self):
        (self.root / "source.txt").write_text("updated\n", encoding="utf-8")
        prepared = self.workflow.prepare(0, True)
        (self.root / "source.txt").write_text("changed after review\n", encoding="utf-8")
        with self.assertRaisesRegex(FinishDayError, "changed after Finish Day review"):
            self.workflow.commit(prepared["reviewToken"], "Unsafe commit", True)
        count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(count, "1")

    def test_confirmations_and_pending_drafts_are_required(self):
        (self.root / "source.txt").write_text("updated\n", encoding="utf-8")
        with self.assertRaisesRegex(FinishDayError, "confirmation"):
            self.workflow.prepare(0, False)
        with self.assertRaisesRegex(FinishDayError, "unsaved browser drafts"):
            self.workflow.prepare(1, True)


if __name__ == "__main__":
    unittest.main()
