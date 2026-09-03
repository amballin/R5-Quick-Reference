#!/usr/bin/env python3
"""End-to-end parity checks for an explicit external profile pack."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml

from asset_manager import ProjectPaths
from appendix_renderer import render_appendices
from offline_index import render_offline_index
from profile_pack import SOURCE_PATHS
from pwa import generate_pwa
from validator import run as run_validation


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK_ID = "b076218f-7cda-4fe8-8afb-7008cfd53ca2"


def _load_root_build():
    spec = importlib.util.spec_from_file_location("profile_pack_root_build", PROJECT_ROOT / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROOT_BUILD = _load_root_build()


def write_pack_from_embedded_sources(pack):
    pack.mkdir()
    subprocess.run(
        ["git", "init", "-q", str(pack)],
        check=True,
        capture_output=True,
        text=True,
    )
    manifest = {
        "manifest_version": 1,
        "pack_id": PACK_ID,
        "pack_name": "Embedded parity fixture",
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
    (pack / "profile-pack.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    embedded = {
        **SOURCE_PATHS,
        "owned_equipment": "data/stabilization_reference.yaml",
        "registration_targets": "90 Testing/eos_r5_verification_tracker.yaml",
    }
    for key, destination_relative in SOURCE_PATHS.items():
        source = PROJECT_ROOT / embedded[key]
        destination = pack / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)


class ProfilePackBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.pack = self.base / "private-pack"
        self.workspace = self.base / "workspace"
        write_pack_from_embedded_sources(self.pack)

    def tearDown(self):
        self.temp.cleanup()

    def _render_reference_bundle(self):
        reference_workspace = self.workspace / "embedded"
        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(reference_workspace)}):
            paths = ProjectPaths(PROJECT_ROOT)
            profile_names = ROOT_BUILD.profile_names_to_build(paths, None)
            render_appendices(paths)
            successes, failures, _ = ROOT_BUILD.build_profiles(paths, profile_names)
            self.assertEqual(len(successes), len(profile_names))
            self.assertEqual(failures, [])
            publish_display = ROOT_BUILD.display_publish_metadata(
                ROOT_BUILD.load_publish_metadata(
                    PROJECT_ROOT / "80 Build" / "publish_metadata.yaml"
                )
            )
            render_offline_index(
                paths,
                publish_display,
                preserve_spreadsheet_downloads=False,
            )
            (paths.merged_build_output_dir / "profile-pack-provenance.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            generate_pwa(paths, build_version="parity-test")
            return self._tree_bytes(paths.merged_build_output_dir)

    def test_external_cli_matches_embedded_bundle_and_never_writes_application_outputs(self):
        reference = self._render_reference_bundle()
        protected = [
            PROJECT_ROOT / "docs",
            PROJECT_ROOT / "FINISH_DAY.html",
            PROJECT_ROOT / "WORKFLOWS" / "local-build.html",
        ]
        before = {path: self._tree_or_file_bytes(path) for path in protected}
        external_workspace = self.workspace / "external"
        argv = [
            "build.py",
            "--root",
            str(PROJECT_ROOT),
            "--profile-pack",
            str(self.pack),
        ]
        with (
            mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(external_workspace)}),
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(ROOT_BUILD.time, "sleep", return_value=None),
            mock.patch("pwa.time.time", return_value=1),
        ):
            paths = ProjectPaths(PROJECT_ROOT, profile_pack_root=self.pack)
            source_issues = run_validation(paths, source_only=True)
            self.assertEqual(
                [issue for issue in source_issues if issue.level == "error"],
                [],
            )
            self.assertEqual(ROOT_BUILD.main(), 0)

        with mock.patch.dict(os.environ, {"PRS_LOCAL_WORKSPACE": str(external_workspace)}):
            paths = ProjectPaths(PROJECT_ROOT, profile_pack_root=self.pack)
            external = self._tree_bytes(paths.merged_build_output_dir)
            pages = self._tree_bytes(paths.pages_output_dir)
            full_issues = run_validation(paths)
            self.assertEqual(
                [issue for issue in full_issues if issue.level == "error"],
                [],
            )
        provenance = external.pop("profile-pack-provenance.json")
        reference.pop("profile-pack-provenance.json")
        normalized_external = {
            name: data.replace(b"photography-reference-1", b"photography-reference-parity-test")
            for name, data in external.items()
        }
        self.assertEqual(reference, normalized_external)
        self.assertIn(PACK_ID.encode("utf-8"), provenance)
        private_path = str(self.pack).encode("utf-8")
        application_path = str(PROJECT_ROOT).encode("utf-8")
        self.assertTrue(all(private_path not in data for data in external.values()))
        self.assertTrue(all(application_path not in data for data in external.values()))
        self.assertNotIn(private_path, provenance)
        self.assertNotIn(application_path, provenance)
        self.assertEqual(
            {**external, "profile-pack-provenance.json": provenance},
            pages,
        )
        self.assertEqual(before, {path: self._tree_or_file_bytes(path) for path in protected})

    @staticmethod
    def _tree_bytes(root):
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    @classmethod
    def _tree_or_file_bytes(cls, path):
        if path.is_dir():
            return cls._tree_bytes(path)
        return path.read_bytes() if path.exists() else None


if __name__ == "__main__":
    unittest.main()
