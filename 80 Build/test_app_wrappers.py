#!/usr/bin/env python3
"""Tests for the machine-local macOS application-wrapper builder."""

from __future__ import annotations

import hashlib
import os
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from app_wrappers import (
    APP_WRAPPERS,
    build_app_wrappers,
    effective_bundle_id,
    icon_source_path,
    icon_variant,
    refresh_app_wrappers,
)


PROJECT_ROOT = BUILD_DIR.parent


def app_digest(app_path: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in app_path.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(app_path)).encode("utf-8"))
        digest.update(path.read_bytes())
        digest.update(oct(path.stat().st_mode & 0o777).encode("ascii"))
    return digest.hexdigest()


class AppWrapperTests(unittest.TestCase):
    def test_builds_named_launchable_app_bundles_deterministically(self):
        with tempfile.TemporaryDirectory(prefix="r5-app-wrapper-tests-") as temporary:
            output_dir = Path(temporary) / "Applications"
            first = build_app_wrappers(PROJECT_ROOT, output_dir)
            first_digests = {path.name: app_digest(path) for path in first}
            second = build_app_wrappers(PROJECT_ROOT, output_dir)
            second_digests = {path.name: app_digest(path) for path in second}

            self.assertEqual(first_digests, second_digests)
            self.assertEqual(
                [path.name for path in second],
                [f"{wrapper.name}.app" for wrapper in APP_WRAPPERS],
            )

            for wrapper, app_path in zip(APP_WRAPPERS, second):
                info_path = app_path / "Contents/Info.plist"
                executable_path = app_path / "Contents/MacOS" / wrapper.executable
                icon_path = app_path / "Contents/Resources/AppIcon.icns"
                with info_path.open("rb") as handle:
                    info = plistlib.load(handle)
                self.assertEqual(info["CFBundleDisplayName"], wrapper.name)
                self.assertEqual(info["CFBundleIdentifier"], effective_bundle_id(wrapper, PROJECT_ROOT))
                self.assertEqual(info["CFBundleIconFile"], "AppIcon.icns")
                self.assertTrue(icon_path.is_file())
                self.assertGreater(icon_path.stat().st_size, 0)
                self.assertTrue(os.access(executable_path, os.X_OK))

                result = subprocess.run(
                    [str(executable_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "R5_APP_WRAPPER_DRY_RUN": "1"},
                )
                self.assertEqual(
                    result.stdout.strip(),
                    str(PROJECT_ROOT / wrapper.command_file),
                )

                runner = executable_path.read_text(encoding="utf-8")
                if wrapper.launch_in_terminal:
                    self.assertIn('/usr/bin/open -a "Terminal"', runner)
                else:
                    self.assertNotIn('/usr/bin/open -a "Terminal"', runner)
                    self.assertIn('"$COMMAND_FILE" >> "$LOG_FILE" 2>&1', runner)
                    self.assertIn(f"{wrapper.name}.log", runner)
                    self.assertIn("show_launch_failure", runner)
                    if wrapper.detach_after_launch:
                        self.assertIn(") </dev/null >/dev/null 2>&1 &", runner)
                    else:
                        self.assertNotIn(") </dev/null >/dev/null 2>&1 &", runner)

            camera_lab = next(wrapper for wrapper in APP_WRAPPERS if wrapper.name == "R5 Camera Lab")
            profile_editor = next(wrapper for wrapper in APP_WRAPPERS if wrapper.name == "R5 Profile Editor")
            self.assertTrue(camera_lab.detach_after_launch)
            self.assertFalse(profile_editor.launch_in_terminal)
            self.assertTrue(profile_editor.detach_after_launch)
            self.assertEqual(profile_editor.command_file, "80 Build/scripts/start-profile-editor.sh")
            variant = icon_variant(PROJECT_ROOT)
            if variant == "prototype":
                self.assertNotEqual(effective_bundle_id(profile_editor, PROJECT_ROOT), profile_editor.bundle_id)
            else:
                self.assertEqual(effective_bundle_id(profile_editor, PROJECT_ROOT), profile_editor.bundle_id)
            self.assertEqual(icon_source_path(camera_lab, PROJECT_ROOT).name, f"{variant}-camera-lab.png")
            self.assertEqual(icon_source_path(profile_editor, PROJECT_ROOT).name, f"{variant}-camera-pencil.png")

    def test_refresh_rebuilds_only_missing_or_stale_apps(self):
        with tempfile.TemporaryDirectory(prefix="r5-app-wrapper-refresh-tests-") as temporary:
            output_dir = Path(temporary) / "Applications"
            first = refresh_app_wrappers(PROJECT_ROOT, output_dir)
            self.assertEqual(first["status"], "rebuilt")
            self.assertTrue(all(item["priorState"] == "missing" for item in first["apps"]))

            current = refresh_app_wrappers(PROJECT_ROOT, output_dir)
            self.assertEqual(current["status"], "current")
            self.assertFalse(any(item["rebuilt"] for item in current["apps"]))

            profile_app = output_dir / "R5 Profile Editor.app"
            executable = profile_app / "Contents/MacOS/r5-profile-editor"
            executable.write_text(executable.read_text(encoding="utf-8") + "\n# stale\n", encoding="utf-8")
            refreshed = refresh_app_wrappers(PROJECT_ROOT, output_dir)
            by_name = {item["name"]: item for item in refreshed["apps"]}
            self.assertTrue(by_name["R5 Profile Editor"]["rebuilt"])
            self.assertEqual(by_name["R5 Profile Editor"]["priorState"], "stale")
            self.assertFalse(by_name["R5 Camera Lab"]["rebuilt"])

    def test_selects_icon_variant_from_project_context(self):
        camera_lab = next(wrapper for wrapper in APP_WRAPPERS if wrapper.name == "R5 Camera Lab")
        profile_editor = next(wrapper for wrapper in APP_WRAPPERS if wrapper.name == "R5 Profile Editor")
        with patch("app_wrappers.project_context_info", return_value={"kind": "main"}):
            self.assertEqual(icon_variant(PROJECT_ROOT), "production")
            self.assertEqual(icon_source_path(camera_lab, PROJECT_ROOT).name, "production-camera-lab.png")
            self.assertEqual(icon_source_path(profile_editor, PROJECT_ROOT).name, "production-camera-pencil.png")
        with patch("app_wrappers.project_context_info", return_value={"kind": "prototype"}):
            self.assertEqual(icon_variant(PROJECT_ROOT), "prototype")
            self.assertEqual(icon_source_path(camera_lab, PROJECT_ROOT).name, "prototype-camera-lab.png")
            self.assertEqual(icon_source_path(profile_editor, PROJECT_ROOT).name, "prototype-camera-pencil.png")


if __name__ == "__main__":
    unittest.main()
