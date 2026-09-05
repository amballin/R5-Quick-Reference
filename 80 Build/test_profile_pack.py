#!/usr/bin/env python3
"""Tests for embedded and external private profile-pack resolution."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

from asset_manager import ProjectPaths
from profile_pack import (
    EMBEDDED_SOURCE_PATHS,
    ProfilePackError,
    SOURCE_PATHS,
    resolve_profile_pack,
)


class ProfilePackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.application = self.base / "application"
        self.pack = self.base / "private-pack"
        (self.application / "00 Master").mkdir(parents=True)
        (self.application / "00 Master" / "project_identity.yaml").write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "project_id": "canon-eos-r5-camera-reference",
                    "project_name": "Canon EOS R5 Camera Reference",
                    "repository_role": "authoritative-source",
                    "artifact_type": "source-repository",
                    "camera": {"manufacturer": "Canon", "model": "EOS R5"},
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "init", "-q", str(self.application)],
            check=True,
            capture_output=True,
            text=True,
        )
        self._write_external_pack()

    def tearDown(self):
        self.temp.cleanup()

    def _manifest(self):
        return {
            "manifest_version": 1,
            "pack_id": "b076218f-7cda-4fe8-8afb-7008cfd53ca2",
            "pack_name": "Test EOS R5 pack",
            "repository_role": "private-profile-pack",
            "artifact_type": "source-repository",
            "camera": {"manufacturer": "Canon", "model": "EOS R5"},
            "compatibility": {
                "application_project_id": "canon-eos-r5-camera-reference",
                "profile_pack_contract": 1,
            },
            "sources": dict(SOURCE_PATHS),
            "publication": {"default_profile_policy": "explicit-release-only"},
        }

    def _write_external_pack(self):
        self.pack.mkdir()
        subprocess.run(
            ["git", "init", "-q", str(self.pack)],
            check=True,
            capture_output=True,
            text=True,
        )
        (self.pack / "profile-pack.yaml").write_text(
            yaml.safe_dump(self._manifest(), sort_keys=False),
            encoding="utf-8",
        )
        for key, relative in SOURCE_PATHS.items():
            path = self.pack / relative
            if key == "profiles":
                path.mkdir(parents=True)
                (path / "Test.yaml").write_text(
                    "card_id: b365a0f1-c6f1-4f4c-81dc-036ac46e9bf1\n",
                    encoding="utf-8",
                )
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"source: {key}\n", encoding="utf-8")

    def _rewrite_manifest(self, change):
        manifest = self._manifest()
        change(manifest)
        (self.pack / "profile-pack.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )

    def test_embedded_mode_preserves_established_paths(self):
        context = resolve_profile_pack(self.application)
        self.assertEqual(context.mode, "embedded")
        self.assertEqual(context.root, self.application.resolve())
        for key, relative in EMBEDDED_SOURCE_PATHS.items():
            self.assertEqual(context.source(key), self.application / relative)
        paths = ProjectPaths(self.application)
        self.assertEqual(paths.root, self.application.resolve())
        self.assertEqual(paths.baseline_file, self.application / "00 Master" / "baseline.yaml")
        self.assertEqual(paths.profiles_dir, self.application / "10 Profiles")
        self.assertEqual(
            paths.verification_status_file,
            self.application / "90 Testing" / "eos_r5_verification_status.yaml",
        )

    def test_external_manifest_resolves_every_canonical_source(self):
        context = resolve_profile_pack(self.application, self.pack)
        self.assertEqual(context.mode, "external")
        self.assertEqual(context.pack_id, "b076218f-7cda-4fe8-8afb-7008cfd53ca2")
        for key, relative in SOURCE_PATHS.items():
            self.assertEqual(context.source(key), self.pack / relative)
        paths = ProjectPaths(self.application, profile_pack_root=self.pack)
        self.assertEqual(paths.application_root, self.application.resolve())
        self.assertEqual(paths.profile_pack_root, self.pack.resolve())
        self.assertEqual(paths.baseline_file, self.pack / "00 Master" / "baseline.yaml")
        self.assertEqual(paths.profiles_dir, self.pack / "10 Profiles")
        self.assertEqual(
            paths.verification_tracker_source_file,
            self.pack / "90 Testing" / "eos_r5_registration_targets.yaml",
        )
        self.assertNotEqual(paths.pages_output_dir, self.application / "docs")
        self.assertEqual(
            paths.pages_output_dir,
            paths.output_dir / "pages",
        )
        self.assertEqual(
            paths.mutable_source_path("00 Master/my_menu.yaml"),
            self.pack / "00 Master" / "my_menu.yaml",
        )
        self.assertEqual(
            paths.mutable_source_path("10 Profiles/New.yaml"),
            self.pack / "10 Profiles" / "New.yaml",
        )
        with self.assertRaisesRegex(ValueError, "not owned"):
            paths.mutable_source_path("data/canon_r5_custom_controls_current.yaml")

    def test_manifest_requires_user_friendly_pack_name(self):
        self._rewrite_manifest(lambda manifest: manifest.update({"pack_name": "/private/pack"}))
        with self.assertRaisesRegex(ProfilePackError, "user-friendly label"):
            resolve_profile_pack(self.application, self.pack)

    def test_external_output_is_namespaced_by_pack_id(self):
        paths = ProjectPaths(self.application, profile_pack_root=self.pack)
        self.assertEqual(
            paths.local_workspace_dir,
            self.application.parent
            / f"{self.application.name} Local"
            / "Profile Packs"
            / "b076218f-7cda-4fe8-8afb-7008cfd53ca2",
        )

    def test_fingerprint_is_stable_and_content_sensitive(self):
        first = resolve_profile_pack(self.application, self.pack).fingerprint()
        second = resolve_profile_pack(self.application, self.pack).fingerprint()
        self.assertEqual(first, second)
        target = self.pack / "10 Profiles" / "Test.yaml"
        target.write_text(target.read_text(encoding="utf-8") + "title: Changed\n", encoding="utf-8")
        third = resolve_profile_pack(self.application, self.pack).fingerprint()
        self.assertNotEqual(first, third)

    def test_rejects_all_zero_pack_id(self):
        self._rewrite_manifest(
            lambda item: item.__setitem__("pack_id", "00000000-0000-0000-0000-000000000000")
        )
        with self.assertRaisesRegex(ProfilePackError, "all-zero"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_unknown_manifest_key(self):
        self._rewrite_manifest(lambda item: item.__setitem__("unexpected", True))
        with self.assertRaisesRegex(ProfilePackError, "unknown keys"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_duplicate_manifest_key(self):
        path = self.pack / "profile-pack.yaml"
        path.write_text(path.read_text(encoding="utf-8") + "pack_name: Duplicate\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfilePackError, "Duplicate manifest key"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_wrong_application_identity(self):
        identity = self.application / "00 Master" / "project_identity.yaml"
        content = yaml.safe_load(identity.read_text(encoding="utf-8"))
        content["repository_role"] = "generated-output"
        identity.write_text(yaml.safe_dump(content, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(ProfilePackError, "unexpected repository_role"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_wrong_camera(self):
        self._rewrite_manifest(
            lambda item: item.__setitem__("camera", {"manufacturer": "Canon", "model": "EOS R6"})
        )
        with self.assertRaisesRegex(ProfilePackError, "Canon EOS R5"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_unsupported_contract(self):
        self._rewrite_manifest(
            lambda item: item["compatibility"].__setitem__("profile_pack_contract", 2)
        )
        with self.assertRaisesRegex(ProfilePackError, "Unsupported profile-pack contract"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_noncanonical_or_traversing_source(self):
        self._rewrite_manifest(
            lambda item: item["sources"].__setitem__("baseline", "../baseline.yaml")
        )
        with self.assertRaisesRegex(ProfilePackError, "must be '00 Master/baseline.yaml'"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_missing_source(self):
        (self.pack / "00 Master" / "my_menu.yaml").unlink()
        with self.assertRaisesRegex(ProfilePackError, "source is missing: my_menu"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_source_symlink_that_escapes_pack(self):
        outside = self.base / "outside-baseline.yaml"
        outside.write_text("source: outside\n", encoding="utf-8")
        baseline = self.pack / "00 Master" / "baseline.yaml"
        baseline.unlink()
        baseline.symlink_to(outside)
        with self.assertRaisesRegex(ProfilePackError, "escapes the pack root"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_nested_profile_symlink_that_escapes_pack(self):
        outside = self.base / "outside-profile.yaml"
        outside.write_text("title: Outside\n", encoding="utf-8")
        (self.pack / "10 Profiles" / "Outside.yaml").symlink_to(outside)
        with self.assertRaisesRegex(ProfilePackError, "escapes the pack root"):
            resolve_profile_pack(self.application, self.pack)

    def test_rejects_same_or_nested_repository_roots(self):
        with self.assertRaisesRegex(ProfilePackError, "separate, non-nested repositories"):
            resolve_profile_pack(self.application, self.application)

    def test_rejects_context_for_a_different_application(self):
        context = resolve_profile_pack(self.application, self.pack)
        other = self.base / "other-application"
        with self.assertRaisesRegex(ValueError, "different application root"):
            ProjectPaths(other, profile_pack_context=context)

    def test_rejects_nested_checkout_as_pack_root(self):
        nested = self.pack / "nested"
        nested.mkdir()
        with self.assertRaisesRegex(ProfilePackError, "does not match its Git root"):
            resolve_profile_pack(self.application, nested)

    def test_rejects_profile_pack_containing_another_manifest(self):
        nested = self.pack / "Nested Pack"
        nested.mkdir()
        (nested / "profile-pack.yaml").write_text(
            yaml.safe_dump(self._manifest(), sort_keys=False),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ProfilePackError,
            "cannot contain another profile pack.*separate sibling folder",
        ):
            resolve_profile_pack(self.application, self.pack)


if __name__ == "__main__":
    unittest.main()
