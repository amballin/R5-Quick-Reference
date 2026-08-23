#!/usr/bin/env python3
"""Build machine-local macOS application wrappers for the local project tools."""

from __future__ import annotations

import argparse
import os
import plistlib
import shlex
import shutil
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AppWrapper:
    name: str
    bundle_id: str
    executable: str
    command_file: str
    launch_in_terminal: bool = True


APP_WRAPPERS = (
    AppWrapper(
        name="R5 Camera Lab",
        bundle_id="com.amballin.canon-eos-r5.camera-lab",
        executable="r5-camera-lab",
        command_file="80 Build/scripts/start-camera-lab.sh",
        launch_in_terminal=False,
    ),
    AppWrapper(
        name="R5 Profile Editor",
        bundle_id="com.amballin.canon-eos-r5.profile-editor",
        executable="r5-profile-editor",
        command_file="Start Profile Editor.command",
    ),
)


def default_local_workspace(project_root: Path) -> Path:
    configured = os.environ.get("PRS_LOCAL_WORKSPACE")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(f"{project_root} Local")


def _runner_source(wrapper: AppWrapper, project_root: Path) -> str:
    command_path = project_root / wrapper.command_file
    app_name = shlex.quote(wrapper.name)
    command_file = shlex.quote(str(command_path))
    common = f"""#!/bin/bash

set -u

APP_NAME={app_name}
COMMAND_FILE={command_file}

show_missing_launcher() {{
    /usr/bin/osascript - "$APP_NAME" "$COMMAND_FILE" <<'APPLESCRIPT'
on run argv
    display alert ((item 1 of argv) & " cannot start.") message ("The project launcher is missing:\n" & (item 2 of argv) & "\n\nRebuild the application wrappers from the current project folder.") as critical
end run
APPLESCRIPT
}}

if [[ ! -x "$COMMAND_FILE" ]]; then
    show_missing_launcher
    exit 1
fi

if [[ "${{R5_APP_WRAPPER_DRY_RUN:-0}}" == "1" ]]; then
    printf '%s\n' "$COMMAND_FILE"
    exit 0
fi
"""
    if wrapper.launch_in_terminal:
        return common + """
/usr/bin/open -a "Terminal" "$COMMAND_FILE"
"""

    log_file = shlex.quote(
        str(default_local_workspace(project_root) / "Logs" / f"{wrapper.name}.log")
    )
    return common + f"""
LOG_FILE={log_file}
LOG_DIR="$(dirname -- "$LOG_FILE")"

show_launch_failure() {{
    /usr/bin/osascript - "$APP_NAME" "$LOG_FILE" "$1" <<'APPLESCRIPT'
on run argv
    display alert ((item 1 of argv) & " stopped.") message ("It could not start or stopped unexpectedly (status " & (item 3 of argv) & ").\n\nDetails were saved to:\n" & (item 2 of argv)) as critical
end run
APPLESCRIPT
}}

if ! /bin/mkdir -p "$LOG_DIR"; then
    /usr/bin/osascript - "$APP_NAME" "$LOG_DIR" <<'APPLESCRIPT'
on run argv
    display alert ((item 1 of argv) & " cannot start.") message ("Its machine-local log folder could not be created:\n" & (item 2 of argv)) as critical
end run
APPLESCRIPT
    exit 1
fi

"$COMMAND_FILE" > "$LOG_FILE" 2>&1
STATUS=$?

if [[ "$STATUS" -ne 0 && "$STATUS" -ne 130 ]]; then
    show_launch_failure "$STATUS"
fi

exit "$STATUS"
"""


def _info_plist(wrapper: AppWrapper) -> bytes:
    payload = {
        "CFBundleDisplayName": wrapper.name,
        "CFBundleExecutable": wrapper.executable,
        "CFBundleIdentifier": wrapper.bundle_id,
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": wrapper.name,
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1",
        "LSMinimumSystemVersion": "12.0",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    }
    return plistlib.dumps(payload, fmt=plistlib.FMT_XML, sort_keys=True)


def _validate_project_root(project_root: Path) -> None:
    identity = project_root / "00 Master/project_identity.yaml"
    if not identity.is_file():
        raise RuntimeError(f"Authoritative project identity is missing: {identity}")
    for wrapper in APP_WRAPPERS:
        command_path = project_root / wrapper.command_file
        if not command_path.is_file():
            raise RuntimeError(f"Application launcher is missing: {command_path}")
        if not os.access(command_path, os.X_OK):
            raise RuntimeError(f"Application launcher is not executable: {command_path}")


def _validate_app(app_path: Path, wrapper: AppWrapper, project_root: Path) -> None:
    info_path = app_path / "Contents/Info.plist"
    executable_path = app_path / "Contents/MacOS" / wrapper.executable
    if not info_path.is_file() or not executable_path.is_file():
        raise RuntimeError(f"Application wrapper is incomplete: {app_path}")
    with info_path.open("rb") as handle:
        info = plistlib.load(handle)
    expected = {
        "CFBundleDisplayName": wrapper.name,
        "CFBundleExecutable": wrapper.executable,
        "CFBundleIdentifier": wrapper.bundle_id,
        "CFBundlePackageType": "APPL",
    }
    for key, value in expected.items():
        if info.get(key) != value:
            raise RuntimeError(f"{app_path} has an invalid {key}: {info.get(key)!r}")
    mode = executable_path.stat().st_mode
    if not mode & stat.S_IXUSR:
        raise RuntimeError(f"Application executable is not executable: {executable_path}")
    runner = executable_path.read_text(encoding="utf-8")
    expected_launcher = str(project_root / wrapper.command_file)
    if expected_launcher not in runner:
        raise RuntimeError(f"Application wrapper does not target {expected_launcher}")


def _install_app(staged_app: Path, destination: Path) -> None:
    previous = None
    if destination.exists():
        previous = destination.with_name(f".{destination.name}.previous")
        if previous.exists():
            shutil.rmtree(previous)
        destination.rename(previous)
    try:
        staged_app.rename(destination)
    except Exception:
        if previous is not None and previous.exists() and not destination.exists():
            previous.rename(destination)
        raise
    if previous is not None and previous.exists():
        shutil.rmtree(previous)


def build_app_wrappers(project_root: Path, output_dir: Optional[Path] = None):
    project_root = project_root.resolve()
    _validate_project_root(project_root)
    if output_dir is None:
        output_dir = default_local_workspace(project_root) / "Applications"
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    with tempfile.TemporaryDirectory(prefix="r5-app-wrappers-", dir=output_dir) as temporary:
        staging_root = Path(temporary)
        for wrapper in APP_WRAPPERS:
            staged_app = staging_root / f"{wrapper.name}.app"
            macos_dir = staged_app / "Contents/MacOS"
            macos_dir.mkdir(parents=True)
            (staged_app / "Contents/Info.plist").write_bytes(_info_plist(wrapper))
            executable_path = macos_dir / wrapper.executable
            executable_path.write_text(_runner_source(wrapper, project_root), encoding="utf-8")
            executable_path.chmod(0o755)
            _validate_app(staged_app, wrapper, project_root)

            destination = output_dir / staged_app.name
            _install_app(staged_app, destination)
            _validate_app(destination, wrapper, project_root)
            installed.append(destination)
    return installed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build R5 Camera Lab.app and R5 Profile Editor.app."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Authoritative project root. Defaults to this script's repository.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional output folder. Defaults to the machine-local Applications folder.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for app_path in build_app_wrappers(args.project_root, args.output_dir):
        print(app_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
