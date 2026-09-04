#!/usr/bin/env python3
"""Tests for guarded new private profile-pack creation."""

from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest import mock

import yaml

from profile_pack import EMBEDDED_SOURCE_PATHS, SOURCE_PATHS, resolve_profile_pack
from profile_pack_creation import ProfilePackCreationError, ProfilePackCreator
from profile_pack_selection import ProfilePackSelectionStore
from profile_editor import EditorHandler, ProfileEditorModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProfilePackCreationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.destination = self.base / "My Canon EOS R5 Profiles"
        self.validated = []
        self.creator = ProfilePackCreator(
            PROJECT_ROOT,
            source_validator=lambda paths: self.validated.append(paths) or [],
        )

    def tearDown(self):
        self.temporary.cleanup()

    def review(self, **overrides):
        values = {
            "pack_name": "My Canon EOS R5 Profiles",
            "destination": str(self.destination),
            "pending_changes": 0,
        }
        values.update(overrides)
        return self.creator.review(**values)

    def test_review_is_non_mutating_and_exposes_exact_creation_plan(self):
        review = self.review()
        self.assertFalse(self.destination.exists())
        self.assertEqual(review["packName"], "My Canon EOS R5 Profiles")
        self.assertEqual(review["destination"], str(self.destination))
        self.assertIn("pack_name: My Canon EOS R5 Profiles", review["manifestYaml"])
        self.assertIn("profile-pack.yaml", review["sourceFiles"])
        self.assertIn("AGENTS.md", review["sourceFiles"])
        self.assertIn("10 Profiles/Wildlife.yaml", review["sourceFiles"])
        self.assertEqual(review["sourceFileCount"], len(review["sourceFiles"]))
        self.assertIn("without a commit, remote, or push", review["gitAction"])

    def test_create_migrates_valid_pack_initializes_local_git_and_selects_no_remote(self):
        review = self.review()
        context = self.creator.create(review["reviewToken"], True)
        self.assertEqual(context.root, self.destination)
        self.assertEqual(context.pack_name, "My Canon EOS R5 Profiles")
        self.assertEqual(len(self.validated), 1)
        self.assertTrue((self.destination / ".git").is_dir())
        self.assertTrue((self.destination / "AGENTS.md").is_file())
        manifest = yaml.safe_load((self.destination / "profile-pack.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["pack_id"], context.pack_id)
        for key, destination_relative in SOURCE_PATHS.items():
            destination = self.destination / destination_relative
            source = PROJECT_ROOT / EMBEDDED_SOURCE_PATHS[key]
            self.assertEqual(destination.is_dir(), source.is_dir())
            if source.is_file():
                self.assertEqual(destination.read_bytes(), source.read_bytes())
        self.assertEqual(resolve_profile_pack(PROJECT_ROOT, self.destination).pack_id, context.pack_id)
        remotes = subprocess.run(
            ["git", "-C", str(self.destination), "remote"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(remotes.stdout.strip(), "")
        head = subprocess.run(
            ["git", "-C", str(self.destination), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(head.returncode, 0)
        with self.assertRaisesRegex(ProfilePackCreationError, "missing or expired"):
            self.creator.create(review["reviewToken"], True)

    def test_creation_rejects_drafts_existing_or_nested_destinations_and_missing_confirmation(self):
        with self.assertRaisesRegex(ProfilePackCreationError, "browser draft"):
            self.review(pending_changes=1)
        self.destination.mkdir()
        with self.assertRaisesRegex(ProfilePackCreationError, "already exists"):
            self.review()
        nested = PROJECT_ROOT / "new-private-profile-pack"
        with self.assertRaisesRegex(ProfilePackCreationError, "outside and separate"):
            self.review(destination=str(nested))
        self.destination.rmdir()
        review = self.review()
        with self.assertRaisesRegex(ProfilePackCreationError, "explicit confirmation"):
            self.creator.create(review["reviewToken"], False)
        self.assertFalse(self.destination.exists())

    def test_creation_rechecks_source_and_rolls_back_failed_validation(self):
        review = self.review()
        with mock.patch.object(self.creator, "_embedded_fingerprint", return_value="changed"):
            with self.assertRaisesRegex(ProfilePackCreationError, "changed after review"):
                self.creator.create(review["reviewToken"], True)
        self.assertFalse(self.destination.exists())

        failing = ProfilePackCreator(
            PROJECT_ROOT,
            source_validator=lambda _paths: ["forced validation failure"],
        )
        review = failing.review("My Canon EOS R5 Profiles", str(self.destination), 0)
        with self.assertRaisesRegex(ProfilePackCreationError, "forced validation failure"):
            failing.create(review["reviewToken"], True)
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.base.glob(".profile-pack-create-*")), [])

    def test_name_and_destination_are_guarded(self):
        for name in ("", " leading", "bad/path", "x" * 81):
            with self.subTest(name=name):
                with self.assertRaises(ProfilePackCreationError):
                    self.review(pack_name=name)
        with self.assertRaisesRegex(ProfilePackCreationError, "absolute path"):
            self.review(destination="relative-pack")
        (self.base / "Backup").mkdir()
        with self.assertRaisesRegex(ProfilePackCreationError, "prohibited folder name"):
            self.review(destination=str(self.base / "Backup" / "My Pack"))

    def test_macos_picker_returns_an_exact_path_and_handles_cancel(self):
        with mock.patch(
            "profile_pack_creation.subprocess.run",
            return_value=SimpleNamespace(
                returncode=0,
                stdout="/Users/example/My Camera Profiles\n",
                stderr="",
            ),
        ) as run:
            result = self.creator.choose_destination("My Camera Profiles")
        self.assertEqual(
            result,
            {"cancelled": False, "destination": "/Users/example/My Camera Profiles"},
        )
        self.assertEqual(run.call_args.args[0][0], "osascript")
        self.assertEqual(run.call_args.args[0][-1], "My Camera Profiles")

        with mock.patch(
            "profile_pack_creation.subprocess.run",
            return_value=SimpleNamespace(
                returncode=0,
                stdout="__PROFILE_PACK_PICKER_CANCELLED__\n",
                stderr="",
            ),
        ):
            self.assertEqual(
                self.creator.choose_destination("My Camera Profiles"),
                {"cancelled": True},
            )

    def test_editor_creation_registers_selects_and_returns_no_private_path(self):
        workspace = self.base / "workspace"
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(workspace)}):
            model = ProfileEditorModel(PROJECT_ROOT)
            store = ProfilePackSelectionStore(PROJECT_ROOT)

            class BoundHandler(EditorHandler):
                pass

            BoundHandler.model = model
            BoundHandler.selection_store = store
            BoundHandler.pack_creator = self.creator
            BoundHandler.model_switch_lock = threading.Lock()
            handler = object.__new__(BoundHandler)
            handler.model = model
            review = self.creator.review(
                "My Canon EOS R5 Profiles", str(self.destination), 0
            )
            result = handler._create_profile_pack(review["reviewToken"], True)
            selected = store.selected_context()

        self.assertTrue(result["created"])
        self.assertEqual(selected.root, self.destination)
        self.assertEqual(BoundHandler.model.paths.profile_pack.pack_id, selected.pack_id)
        self.assertNotIn(str(self.destination), json.dumps(result))
        self.assertEqual(
            result["git"],
            {
                "initialized": True,
                "committed": False,
                "remoteConfigured": False,
                "pushed": False,
            },
        )

    def test_created_pack_passes_the_real_combined_source_validator(self):
        destination = self.base / "Validated Canon EOS R5 Profiles"
        creator = ProfilePackCreator(PROJECT_ROOT)
        review = creator.review(
            "Validated Canon EOS R5 Profiles", str(destination), 0
        )
        context = creator.create(review["reviewToken"], True)
        self.assertEqual(context.root, destination)

    def test_editor_registration_failure_removes_only_the_new_pack(self):
        model = ProfileEditorModel(PROJECT_ROOT)

        class FailingStore:
            @staticmethod
            def remember_selected(_context):
                raise RuntimeError("forced registration failure")

        class BoundHandler(EditorHandler):
            pass

        BoundHandler.model = model
        BoundHandler.selection_store = FailingStore()
        BoundHandler.pack_creator = self.creator
        BoundHandler.model_switch_lock = threading.Lock()
        handler = object.__new__(BoundHandler)
        handler.model = model
        review = self.review()
        with self.assertRaisesRegex(RuntimeError, "forced registration failure"):
            handler._create_profile_pack(review["reviewToken"], True)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
