#!/usr/bin/env python3
"""Reliable Apple Numbers discovery, launch, and AppleScript execution."""

from dataclasses import dataclass
import json
from pathlib import Path
import plistlib
import subprocess
import time
from typing import Optional


NUMBERS_BUNDLE_IDS = ("com.apple.Numbers", "com.apple.iWork.Numbers")
LAUNCH_TIMEOUT_SECONDS = 20


class NumbersAutomationError(RuntimeError):
    """Raised when no supported Numbers application can complete an operation."""


@dataclass(frozen=True)
class NumbersApplication:
    bundle_id: str
    path: Optional[Path] = None

    @property
    def label(self):
        return f"{self.bundle_id} ({self.path})" if self.path else self.bundle_id


def run_numbers_applescript(script, operation, success=None):
    """Launch each supported Numbers candidate, then run an AppleScript operation."""
    errors = []
    for application in numbers_applications():
        try:
            ensure_numbers_running(application)
        except NumbersAutomationError as exc:
            errors.append(f"{application.label}: {exc}")
            continue
        result = subprocess.run(
            [
                "osascript",
                "-e",
                script.replace("__BUNDLE_ID__", application.bundle_id),
            ],
            capture_output=True,
            text=True,
        )
        valid = result.returncode == 0 and (success is None or success(result))
        if valid:
            return result, application
        detail = result.stderr.strip() or result.stdout.strip() or "operation did not produce the expected result"
        errors.append(f"{application.label}: {detail}")
    raise NumbersAutomationError(_failure_message(operation, errors))


def open_numbers_document(path):
    """Launch Numbers explicitly and open a document without requiring a manual start."""
    path = Path(path).resolve()
    errors = []
    for application in numbers_applications():
        try:
            ensure_numbers_running(application)
        except NumbersAutomationError as exc:
            errors.append(f"{application.label}: {exc}")
            continue
        command = ["open", "-gj"]
        if application.path:
            command.extend(["-a", str(application.path)])
        else:
            command.extend(["-b", application.bundle_id])
        command.append(str(path))
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(
                f"{application.label}: {result.stderr.strip() or 'launch failed'}"
            )
            continue
        return application
    raise NumbersAutomationError(_failure_message("open the workbook", errors))


def ensure_numbers_running(application, launch=True):
    """Explicitly launch a Numbers candidate and wait for AppleScript responsiveness."""
    if launch:
        command = ["open", "-gj"]
        if application.path:
            command.extend(["-a", str(application.path)])
        else:
            command.extend(["-b", application.bundle_id])
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise NumbersAutomationError(result.stderr.strip() or "application launch failed")

    probe = (
        f'tell application id {json.dumps(application.bundle_id)}\n'
        "launch\n"
        "count documents\n"
        "end tell"
    )
    deadline = time.monotonic() + LAUNCH_TIMEOUT_SECONDS
    last_error = "application did not become responsive"
    while time.monotonic() < deadline:
        result = subprocess.run(
            ["osascript", "-e", probe],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return
        last_error = result.stderr.strip() or last_error
        time.sleep(0.25)
    raise NumbersAutomationError(last_error)


def numbers_applications():
    """Return supported bundle IDs, preferring a real Numbers.app path when found."""
    discovered = _discover_numbers_paths()
    applications = []
    seen = set()
    for bundle_id in NUMBERS_BUNDLE_IDS:
        for path in discovered.get(bundle_id, ()):
            key = (bundle_id, str(path))
            if key not in seen:
                applications.append(NumbersApplication(bundle_id, path))
                seen.add(key)
        key = (bundle_id, None)
        if key not in seen:
            applications.append(NumbersApplication(bundle_id))
            seen.add(key)
    return applications


def _discover_numbers_paths():
    paths = []
    for candidate in (
        Path("/Applications/Numbers.app"),
        Path.home() / "Applications" / "Numbers.app",
    ):
        if candidate.is_dir():
            paths.append(candidate.resolve())
    for bundle_id in NUMBERS_BUNDLE_IDS:
        result = subprocess.run(
            ["mdfind", f"kMDItemCFBundleIdentifier == '{bundle_id}'"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                candidate = Path(line.strip())
                if candidate.suffix == ".app" and candidate.is_dir():
                    paths.append(candidate.resolve())

    discovered = {bundle_id: [] for bundle_id in NUMBERS_BUNDLE_IDS}
    for path in paths:
        bundle_id = _bundle_identifier(path)
        if bundle_id in discovered and path not in discovered[bundle_id]:
            discovered[bundle_id].append(path)
    return discovered


def _bundle_identifier(application_path):
    plist_path = application_path / "Contents" / "Info.plist"
    try:
        with plist_path.open("rb") as source:
            return plistlib.load(source).get("CFBundleIdentifier")
    except (OSError, plistlib.InvalidFileException):
        return None


def _failure_message(operation, errors):
    detail = "; ".join(errors) if errors else "neither supported bundle ID was available"
    return (
        f"Could not use Apple Numbers to {operation}. Tried "
        f"{', '.join(NUMBERS_BUNDLE_IDS)}. {detail}"
    )
