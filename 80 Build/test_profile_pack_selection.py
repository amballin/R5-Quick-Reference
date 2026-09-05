#!/usr/bin/env python3
"""Machine-local Profile Editor selection tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from profile_pack_selection import (  # noqa: E402
    EMBEDDED_PACK_ID,
    ProfilePackSelectionError,
    ProfilePackSelectionStore,
)
from test_profile_pack_build import PROJECT_ROOT, write_pack_from_embedded_sources  # noqa: E402


class ProfilePackSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.pack = self.root / "private-pack"
        write_pack_from_embedded_sources(self.pack)
        self.environment = mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(self.workspace)})
        self.environment.start()
        self.store = ProfilePackSelectionStore(PROJECT_ROOT)

    def tearDown(self):
        self.environment.stop()
        self.temporary.cleanup()

    def test_missing_selection_uses_embedded_sources_without_creating_state(self):
        context = self.store.selected_context()
        self.assertEqual(context.mode, "embedded")
        self.assertFalse(self.store.path.exists())

    def test_selected_pack_persists_only_canonical_root_and_identity(self):
        context = self.store.select_path(self.pack)
        saved = json.loads(self.store.path.read_text(encoding="utf-8"))
        self.assertEqual(saved["selected_pack_id"], context.pack_id)
        self.assertEqual(saved["packs"], [{"pack_id": context.pack_id, "root": str(self.pack.resolve())}])
        self.assertNotIn(context.pack_name, json.dumps(saved))
        self.assertEqual(self.store.path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.store.selected_context().pack_id, context.pack_id)

    def test_catalog_reads_friendly_name_live_from_manifest_without_exposing_path(self):
        context = self.store.select_path(self.pack)
        manifest_path = self.pack / "profile-pack.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest["pack_name"] = "Andy's EOS R5 Field Profiles"
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        catalog = self.store.catalog(context)
        selected = next(item for item in catalog["packs"] if item["pack_id"] == context.pack_id)
        self.assertEqual(selected["pack_name"], "Andy's EOS R5 Field Profiles")
        self.assertNotIn(str(self.pack), json.dumps(catalog))

    def test_switching_to_embedded_keeps_remembered_pack_available(self):
        external = self.store.select_path(self.pack)
        embedded = self.store.select_registered(EMBEDDED_PACK_ID)
        self.assertEqual(embedded.mode, "embedded")
        self.assertEqual(self.store.selected_context().mode, "embedded")
        catalog = self.store.catalog(embedded)
        remembered = next(item for item in catalog["packs"] if item["pack_id"] == external.pack_id)
        self.assertTrue(remembered["available"])
        self.assertFalse(remembered["active"])

    def test_missing_saved_pack_fails_closed(self):
        self.store.select_path(self.pack)
        self.pack.rename(self.root / "moved-pack")
        with self.assertRaisesRegex(ProfilePackSelectionError, "Saved profile pack is unavailable"):
            self.store.selected_context()

    def test_unregistered_identity_is_rejected(self):
        with self.assertRaisesRegex(ProfilePackSelectionError, "not registered"):
            self.store.resolve_registered("00000000-0000-0000-0000-000000000001")

    def test_selection_rejects_a_pack_with_a_nested_manifest(self):
        nested = self.pack / "Nested Pack"
        nested.mkdir()
        (nested / "profile-pack.yaml").write_text("manifest_version: 1\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfilePackSelectionError, "cannot contain another profile pack"):
            self.store.select_path(self.pack)

    def test_confirmed_selection_repairs_corrupt_registry_but_startup_fails_closed(self):
        self.store.path.parent.mkdir(parents=True)
        self.store.path.write_text("not json\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfilePackSelectionError, "unreadable"):
            self.store.selected_context()
        catalog = self.store.catalog(self.store.resolve_registered(EMBEDDED_PACK_ID))
        self.assertEqual([item["pack_id"] for item in catalog["packs"]], [EMBEDDED_PACK_ID])
        selected = self.store.select_path(self.pack)
        self.assertEqual(self.store.selected_context().pack_id, selected.pack_id)

    def test_normal_cli_uses_saved_pack_and_embedded_flag_is_a_recovery_override(self):
        self.store.select_path(self.pack)
        environment = {**os.environ, "PRS_LOCAL_WORKSPACE": str(self.workspace)}
        selected = subprocess.run(
            [sys.executable, "-B", str(BUILD_DIR / "profile_editor.py"), "--check"],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        embedded = subprocess.run(
            [sys.executable, "-B", str(BUILD_DIR / "profile_editor.py"), "--check", "--embedded"],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)
        self.assertIn("Embedded parity fixture", selected.stdout)
        self.assertEqual(embedded.returncode, 0, embedded.stdout + embedded.stderr)
        self.assertIn("embedded sources", embedded.stdout)


if __name__ == "__main__":
    unittest.main()
