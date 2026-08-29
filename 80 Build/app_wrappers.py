#!/usr/bin/env python3
"""Build machine-local macOS application wrappers for the local project tools."""

from __future__ import annotations

import argparse
import hashlib
import os
import plistlib
import shlex
import shutil
import stat
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from project_context import project_context_info


@dataclass(frozen=True)
class AppWrapper:
    name: str
    bundle_id: str
    executable: str
    command_file: str
    icon_name: str
    launch_in_terminal: bool = True
    detach_after_launch: bool = False


APP_WRAPPERS = (
    AppWrapper(
        name="R5 Camera Lab",
        bundle_id="com.amballin.canon-eos-r5.camera-lab",
        executable="r5-camera-lab",
        command_file="80 Build/scripts/start-camera-lab.sh",
        icon_name="camera-lab",
        launch_in_terminal=False,
        detach_after_launch=True,
    ),
    AppWrapper(
        name="R5 Profile Editor",
        bundle_id="com.amballin.canon-eos-r5.profile-editor",
        executable="r5-profile-editor",
        command_file="80 Build/scripts/start-profile-editor.sh",
        icon_name="camera-pencil",
        launch_in_terminal=False,
        detach_after_launch=True,
    ),
)


def default_local_workspace(project_root: Path) -> Path:
    configured = os.environ.get("PRS_LOCAL_WORKSPACE")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(f"{project_root} Local")


def effective_bundle_id(wrapper: AppWrapper, project_root: Path) -> str:
    """Give a development Profile Editor its own macOS application identity."""
    context = project_context_info(project_root)
    if wrapper.name != "R5 Profile Editor" or context.get("kind") != "prototype":
        return wrapper.bundle_id
    root_suffix = hashlib.sha256(str(project_root.resolve()).encode("utf-8")).hexdigest()[:12]
    return f"{wrapper.bundle_id}.prototype.w{root_suffix}"


def icon_variant(project_root: Path) -> str:
    """Use release-green icons on main and prototype-amber icons elsewhere."""
    return "production" if project_context_info(project_root).get("kind") == "main" else "prototype"


def icon_source_path(wrapper: AppWrapper, project_root: Path) -> Path:
    filename = f"{icon_variant(project_root)}-{wrapper.icon_name}.png"
    return project_root / "60 Assets" / "app-icons" / filename


def _validate_source_icon(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise RuntimeError(f"Application icon is not a valid PNG: {path}")
    width, height, _, color_type = struct.unpack(">IIBB", data[16:26])
    if (width, height) != (1024, 1024):
        raise RuntimeError(f"Application icon must be 1024x1024: {path}")
    if color_type not in {4, 6}:
        raise RuntimeError(f"Application icon must include transparency: {path}")


def _write_icns(source: Path, destination: Path, scratch_root: Path) -> None:
    icon_dir = scratch_root / f"{source.stem}-icon-pngs"
    icon_dir.mkdir()
    chunks = []
    icon_types = {
        16: b"icp4",
        32: b"icp5",
        64: b"icp6",
        128: b"ic07",
        256: b"ic08",
        512: b"ic09",
        1024: b"ic10",
    }
    for pixel_size, icon_type in icon_types.items():
        target = icon_dir / f"icon-{pixel_size}.png"
        subprocess.run(
            ["/usr/bin/sips", "-z", str(pixel_size), str(pixel_size), str(source), "--out", str(target)],
            check=True,
            capture_output=True,
        )
        png = target.read_bytes()
        chunks.append(icon_type + struct.pack(">I", len(png) + 8) + png)
    body = b"".join(chunks)
    destination.write_bytes(b"icns" + struct.pack(">I", len(body) + 8) + body)


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
    runner = common + f"""
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

run_launcher() {{
    printf '\n[%s] Launching %s\n' "$(/bin/date '+%Y-%m-%d %H:%M:%S')" "$APP_NAME" >> "$LOG_FILE"
    "$COMMAND_FILE" >> "$LOG_FILE" 2>&1
    STATUS=$?

    if [[ "$STATUS" -ne 0 && "$STATUS" -ne 130 ]]; then
        show_launch_failure "$STATUS"
    fi

    return "$STATUS"
}}
"""
    if wrapper.detach_after_launch:
        return runner + """
(
    run_launcher
) </dev/null >/dev/null 2>&1 &
exit 0
"""
    return runner + """
run_launcher
exit $?
"""


def _info_plist(wrapper: AppWrapper, project_root: Path) -> bytes:
    payload = {
        "CFBundleDisplayName": wrapper.name,
        "CFBundleExecutable": wrapper.executable,
        "CFBundleIdentifier": effective_bundle_id(wrapper, project_root),
        "CFBundleIconFile": "AppIcon.icns",
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
        icon_path = icon_source_path(wrapper, project_root)
        if not icon_path.is_file():
            raise RuntimeError(f"Application icon is missing: {icon_path}")
        _validate_source_icon(icon_path)


def _validate_app(app_path: Path, wrapper: AppWrapper, project_root: Path) -> None:
    info_path = app_path / "Contents/Info.plist"
    executable_path = app_path / "Contents/MacOS" / wrapper.executable
    icon_path = app_path / "Contents/Resources/AppIcon.icns"
    if not info_path.is_file() or not executable_path.is_file() or not icon_path.is_file():
        raise RuntimeError(f"Application wrapper is incomplete: {app_path}")
    with info_path.open("rb") as handle:
        info = plistlib.load(handle)
    expected = {
        "CFBundleDisplayName": wrapper.name,
        "CFBundleExecutable": wrapper.executable,
        "CFBundleIdentifier": effective_bundle_id(wrapper, project_root),
        "CFBundleIconFile": "AppIcon.icns",
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


def _app_digest(app_path: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in app_path.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(app_path)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
        digest.update(oct(path.stat().st_mode & 0o777).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _build_staged_app(
    staging_root: Path,
    wrapper: AppWrapper,
    project_root: Path,
) -> Path:
    staged_app = staging_root / f"{wrapper.name}.app"
    macos_dir = staged_app / "Contents/MacOS"
    resources_dir = staged_app / "Contents/Resources"
    macos_dir.mkdir(parents=True)
    resources_dir.mkdir(parents=True)
    (staged_app / "Contents/Info.plist").write_bytes(_info_plist(wrapper, project_root))
    _write_icns(
        icon_source_path(wrapper, project_root),
        resources_dir / "AppIcon.icns",
        staging_root,
    )
    executable_path = macos_dir / wrapper.executable
    executable_path.write_text(_runner_source(wrapper, project_root), encoding="utf-8")
    executable_path.chmod(0o755)
    _validate_app(staged_app, wrapper, project_root)
    return staged_app


def refresh_app_wrappers(
    project_root: Path,
    output_dir: Optional[Path] = None,
    *,
    force: bool = False,
):
    """Build only missing or byte-stale wrappers and report the exact outcome."""
    project_root = project_root.resolve()
    _validate_project_root(project_root)
    if output_dir is None:
        output_dir = default_local_workspace(project_root) / "Applications"
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    apps = []
    with tempfile.TemporaryDirectory(prefix="r5-app-wrappers-", dir=output_dir) as temporary:
        staging_root = Path(temporary)
        for wrapper in APP_WRAPPERS:
            staged_app = _build_staged_app(staging_root, wrapper, project_root)
            destination = output_dir / staged_app.name
            prior_state = "missing"
            if destination.exists():
                try:
                    _validate_app(destination, wrapper, project_root)
                    prior_state = (
                        "current"
                        if _app_digest(destination) == _app_digest(staged_app)
                        else "stale"
                    )
                except (OSError, RuntimeError, ValueError, plistlib.InvalidFileException):
                    prior_state = "stale"
            rebuilt = force or prior_state != "current"
            if rebuilt:
                _install_app(staged_app, destination)
            _validate_app(destination, wrapper, project_root)
            apps.append(
                {
                    "name": wrapper.name,
                    "path": str(destination),
                    "priorState": prior_state,
                    "rebuilt": rebuilt,
                }
            )
    rebuilt_names = [item["name"] for item in apps if item["rebuilt"]]
    if rebuilt_names:
        message = "Rebuilt " + " and ".join(rebuilt_names) + "."
        status = "rebuilt"
    else:
        message = "R5 Profile Editor and R5 Camera Lab app wrappers are current."
        status = "current"
    return {
        "status": status,
        "rebuilt": bool(rebuilt_names),
        "apps": apps,
        "message": message,
    }


def build_app_wrappers(project_root: Path, output_dir: Optional[Path] = None):
    result = refresh_app_wrappers(project_root, output_dir, force=True)
    return [Path(item["path"]) for item in result["apps"]]


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
