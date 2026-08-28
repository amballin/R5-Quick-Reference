#!/usr/bin/env python3
"""Regression tests for guarded branch integration."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


BUILD_DIR = Path(__file__).resolve().parent

import sys

if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from integrate_branch import BranchIntegrationError, BranchIntegrationWorkflow


class BranchIntegrationWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="branch-integration-tests-")
        base = Path(self.temporary.name)
        self.root = base / "repository"
        self.remote = base / "remote.git"
        self.local = base / "local"
        self.root.mkdir()
        (self.root / "80 Build").mkdir()
        (self.root / "docs").mkdir()
        (self.root / "80 Build" / "validator.py").write_text(
            "print('Validation passed')\n", encoding="utf-8"
        )
        (self.root / "80 Build" / "build.py").write_text(
            "from pathlib import Path\n"
            "Path('docs/site.txt').write_text('generated locally\\n', encoding='utf-8')\n"
            "print('Build passed')\n",
            encoding="utf-8",
        )
        (self.root / "docs" / "site.txt").write_text("published main\n", encoding="utf-8")
        (self.root / "source.txt").write_text("initial\n", encoding="utf-8")
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Integration Test"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "integration@example.invalid"], cwd=self.root, check=True
        )
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "Initial main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", str(self.remote)], cwd=self.root, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=self.root, check=True, capture_output=True)
        self.initial_main = self.git("rev-parse", "HEAD")
        subprocess.run(["git", "checkout", "-b", "codex/integration-test"], cwd=self.root, check=True, capture_output=True)
        (self.root / "source.txt").write_text("branch update\n", encoding="utf-8")
        subprocess.run(["git", "add", "source.txt"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "Branch update"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(
            ["git", "push", "-u", "origin", "codex/integration-test"],
            cwd=self.root,
            check=True,
            capture_output=True,
        )
        self.branch_commit = self.git("rev-parse", "HEAD")
        self.environment = patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(self.local)})
        self.environment.start()
        self.workflow = BranchIntegrationWorkflow(self.root)

    def tearDown(self):
        self.workflow.close()
        self.environment.stop()
        self.temporary.cleanup()

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args],
            cwd=cwd or self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def remote_ref(self, branch):
        return self.git("rev-parse", f"refs/heads/{branch}", cwd=self.remote)

    def test_prepare_merge_push_and_resync_are_separately_guarded(self):
        inspected = self.workflow.inspect(0)
        self.assertEqual(inspected["phase"], "review")
        self.assertEqual(inspected["target"], "origin/main")
        self.assertTrue(any("Branch update" in line for line in inspected["commits"]))

        prepared = self.workflow.prepare(0, True)
        self.assertEqual(prepared["phase"], "merge-main")
        self.assertEqual(self.remote_ref("main"), self.initial_main)
        self.assertTrue(any("source.txt" in line for line in prepared["files"]))
        self.assertFalse(any("docs/" in line for line in prepared["files"]))

        merged = self.workflow.merge_main(prepared["reviewToken"], True)
        self.assertEqual(merged["phase"], "push-main")
        self.assertEqual(self.remote_ref("main"), self.initial_main)

        pushed = self.workflow.push_main(True)
        self.assertEqual(pushed["phase"], "resync")
        integrated_main = self.remote_ref("main")
        self.assertNotEqual(integrated_main, self.initial_main)
        self.assertEqual(self.remote_ref("codex/integration-test"), self.branch_commit)

        completed = self.workflow.resync_branch(True)
        self.assertEqual(completed["phase"], "complete")
        self.assertEqual(self.remote_ref("codex/integration-test"), integrated_main)
        self.assertEqual(self.git("rev-parse", "HEAD"), integrated_main)
        self.assertEqual((self.root / "docs" / "site.txt").read_text(encoding="utf-8"), "published main\n")

    def test_conflict_stops_without_changing_either_branch(self):
        other = Path(self.temporary.name) / "main-edit"
        subprocess.run(["git", "clone", str(self.remote), str(other)], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "main"], cwd=other, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Main Test"], cwd=other, check=True)
        subprocess.run(["git", "config", "user.email", "main@example.invalid"], cwd=other, check=True)
        (other / "source.txt").write_text("conflicting main update\n", encoding="utf-8")
        subprocess.run(["git", "add", "source.txt"], cwd=other, check=True)
        subprocess.run(["git", "commit", "-m", "Conflicting main update"], cwd=other, check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=other, check=True, capture_output=True)
        changed_main = self.remote_ref("main")

        with self.assertRaisesRegex(BranchIntegrationError, "conflicts with current main"):
            self.workflow.prepare(0, True)
        self.assertEqual(self.remote_ref("main"), changed_main)
        self.assertEqual(self.remote_ref("codex/integration-test"), self.branch_commit)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.branch_commit)

    def test_confirmations_and_clean_synchronized_branch_are_required(self):
        with self.assertRaisesRegex(BranchIntegrationError, "confirmation"):
            self.workflow.prepare(0, False)
        (self.root / "uncommitted.txt").write_text("local\n", encoding="utf-8")
        inspected = self.workflow.inspect(0)
        self.assertEqual(inspected["phase"], "blocked")
        self.assertTrue(any("Finish Day" in blocker for blocker in inspected["blockers"]))

    def test_prepare_reports_merge_and_validation_progress(self):
        events = []
        prepared = self.workflow.prepare(
            0,
            True,
            progress=lambda stage, **details: events.append((stage, details)),
        )
        self.assertEqual(prepared["phase"], "merge-main")
        stages = [stage for stage, _details in events]
        self.assertIn("Creating isolated integration worktree", stages)
        self.assertIn("Testing the branch merge", stages)
        self.assertIn("Development build", stages)
        self.assertIn("Creating reviewed integration candidate", stages)


if __name__ == "__main__":
    unittest.main()
