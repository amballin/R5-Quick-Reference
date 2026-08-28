#!/usr/bin/env python3
"""Regression tests for exact optional cleanup review."""

import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch


BUILD_DIR = Path(__file__).resolve().parent

import sys

if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from cleanup_review import CleanupReview, CleanupReviewError


class CleanupReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cleanup-review-tests-")
        base = Path(self.temporary.name)
        self.root = base / "repository"
        self.local = base / "local"
        self.root.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        (self.root / ".gitignore").write_text(".DS_Store\n", encoding="utf-8")
        self.backups = self.local / "Backups"
        self.backups.mkdir(parents=True)
        self.old = self.backups / "20260801-090000-finish-day-docs"
        self.new = self.backups / "20260828-090000-finish-day-docs"
        self.old.mkdir()
        self.new.mkdir()
        (self.old / "recovery.txt").write_text("old backup\n", encoding="utf-8")
        (self.new / "recovery.txt").write_text("new backup\n", encoding="utf-8")
        self.manual = self.backups / "important-manual-backup"
        self.manual.mkdir()
        (self.manual / "keep.txt").write_text("keep\n", encoding="utf-8")
        self.metadata = self.root / ".DS_Store"
        self.metadata.write_bytes(b"metadata")
        self.environment = patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(self.local)})
        self.environment.start()
        self.review = CleanupReview(self.root)

    def tearDown(self):
        self.environment.stop()
        self.temporary.cleanup()

    def test_inventory_protects_newest_and_ignores_unrecognized_backup(self):
        result = self.review.inspect()
        paths = {item["path"] for item in result["candidates"]}
        protected = {item["path"] for item in result["protected"]}
        self.assertIn(str(self.old.resolve()), paths)
        self.assertIn(str(self.metadata.resolve()), paths)
        self.assertIn(str(self.new.resolve()), protected)
        self.assertNotIn(str(self.new.resolve()), paths)
        self.assertNotIn(str(self.manual.resolve()), paths)
        self.assertNotIn(str(self.manual.resolve()), protected)

    def test_exact_confirmed_selection_is_deleted_and_newest_remains(self):
        result = self.review.inspect()
        selected = [
            item["id"]
            for item in result["candidates"]
            if item["path"] in {str(self.old.resolve()), str(self.metadata.resolve())}
        ]
        with self.assertRaisesRegex(CleanupReviewError, "confirmation"):
            self.review.delete(result["reviewToken"], selected, False)
        deleted = self.review.delete(result["reviewToken"], selected, True)
        self.assertEqual(len(deleted["deleted"]), 2)
        self.assertFalse(self.old.exists())
        self.assertFalse(self.metadata.exists())
        self.assertTrue(self.new.is_dir())
        self.assertTrue(self.manual.is_dir())

    def test_changed_candidate_invalidates_review(self):
        result = self.review.inspect()
        old_item = next(
            item for item in result["candidates"] if item["path"] == str(self.old.resolve())
        )
        (self.old / "recovery.txt").write_text("changed after review\n", encoding="utf-8")
        with self.assertRaisesRegex(CleanupReviewError, "changed after review"):
            self.review.delete(result["reviewToken"], [old_item["id"]], True)
        self.assertTrue(self.old.is_dir())


if __name__ == "__main__":
    unittest.main()
