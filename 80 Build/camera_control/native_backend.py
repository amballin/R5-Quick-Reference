"""Persistent native EDSDK helper backend for macOS library-validation isolation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import threading

from .edsdk_backend import NativeSdkError, resolve_sdk_binary
from .errors import CameraSessionError, SdkUnavailableError
from .physical_write_policy import qualification_candidates


SOURCE_FILE = Path(__file__).resolve().parent / "native" / "edsdk_helper.c"
ENTITLEMENTS_FILE = Path(__file__).resolve().parent / "native" / "helper.entitlements"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _framework_root(binary):
    for candidate in [binary.parent, *binary.parents]:
        if candidate.suffix == ".framework":
            return candidate
    raise SdkUnavailableError(f"EDSDK binary is not inside a framework: {binary}")


def _framework_version(framework):
    candidates = [
        framework / "Resources" / "Info.plist",
        framework / "Versions" / "Current" / "Resources" / "Info.plist",
        framework / "Versions" / "A" / "Resources" / "Info.plist",
    ]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            with candidate.open("rb") as handle:
                info = plistlib.load(handle)
            return info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")
        except (OSError, plistlib.InvalidFileException):
            return None
    return None


def _local_workspace():
    override = os.environ.get("PRS_LOCAL_WORKSPACE")
    if override:
        return Path(override).expanduser().resolve()
    return PROJECT_ROOT.parent / f"{PROJECT_ROOT.name} Local"


def _source_fingerprint(source, framework_binary):
    digest = hashlib.sha256()
    digest.update(source.read_bytes())
    digest.update(ENTITLEMENTS_FILE.read_bytes())
    digest.update(framework_binary.read_bytes())
    header_dir = _header_dir(_framework_root(framework_binary))
    for name in ("EDSDK.h", "EDSDKTypes.h", "EDSDKErrors.h"):
        digest.update((header_dir / name).read_bytes())
    return digest.hexdigest()[:16]


def _header_dir(framework):
    candidates = [
        framework.parent / "Header",
        framework.parent.parent / "Header",
        _local_workspace() / "SDK" / "Header",
    ]
    for candidate in candidates:
        if (candidate / "EDSDK.h").is_file():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    raise SdkUnavailableError(f"Canon EDSDK headers were not found. Searched: {searched}")


def _run_checked(command, failure_label):
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SdkUnavailableError(f"{failure_label}: {detail}")


def _existing_helper_app(path):
    path = Path(path).expanduser()
    if path.suffix != ".app":
        return None
    executable = path / "Contents" / "MacOS" / "edsdk-helper"
    framework = path / "Contents" / "Frameworks" / "EDSDK.framework"
    if executable.is_file() and framework.is_dir():
        return executable.resolve(), framework.resolve()
    raise SdkUnavailableError(f"Native EDSDK helper app is incomplete: {path}")


def build_native_helper(sdk_path):
    existing = _existing_helper_app(sdk_path) if sdk_path else None
    if existing:
        source_framework = existing[1]
        binary = resolve_sdk_binary(source_framework)
    else:
        binary = resolve_sdk_binary(sdk_path)
        source_framework = _framework_root(binary)
    header_dir = _header_dir(source_framework)
    fingerprint = _source_fingerprint(SOURCE_FILE, binary)
    sdk_dir = _local_workspace() / "SDK"
    sdk_dir.mkdir(parents=True, exist_ok=True)
    output_app = sdk_dir / "EDSDKHelper.app"
    manifest = output_app / "Contents" / "Resources" / "build.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        cached = _existing_helper_app(output_app)
        if data.get("fingerprint") == fingerprint and cached:
            return cached

    temp_root = Path(tempfile.mkdtemp(prefix=".edsdk-helper-", dir=sdk_dir))
    candidate_app = temp_root / "EDSDKHelper.app"
    contents = candidate_app / "Contents"
    executable = contents / "MacOS" / "edsdk-helper"
    embedded_framework = contents / "Frameworks" / "EDSDK.framework"
    resources = contents / "Resources"
    try:
        executable.parent.mkdir(parents=True)
        resources.mkdir(parents=True)
        shutil.copytree(source_framework, embedded_framework, symlinks=True)
        info = {
            "CFBundleDevelopmentRegion": "English",
            "CFBundleExecutable": "edsdk-helper",
            "CFBundleIdentifier": "com.canon.camera-reference.edsdk-helper",
            "CFBundleInfoDictionaryVersion": "6.0",
            "CFBundleName": "EOS R5 EDSDK Helper",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "1",
            "LSBackgroundOnly": True,
        }
        with (contents / "Info.plist").open("wb") as handle:
            plistlib.dump(info, handle)
        _run_checked(
            [
                "codesign",
                "--force",
                "--deep",
                "--sign",
                "-",
                "--timestamp=none",
                str(embedded_framework),
            ],
            "Embedded EDSDK framework signing failed",
        )
        _run_checked(
            [
                "clang",
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-D__MACOS__",
                "-I",
                str(header_dir),
                "-F",
                str(contents / "Frameworks"),
                "-framework",
                "EDSDK",
                "-Wl,-rpath,@executable_path/../Frameworks",
                str(SOURCE_FILE),
                "-o",
                str(executable),
            ],
            "Native EDSDK helper compilation failed",
        )
        (resources / "build.json").write_text(
            json.dumps({"fingerprint": fingerprint}, indent=2) + "\n",
            encoding="utf-8",
        )
        _run_checked(
            [
                "codesign",
                "--force",
                "--sign",
                "-",
                "--timestamp=none",
                "--options",
                "runtime",
                "--entitlements",
                str(ENTITLEMENTS_FILE),
                str(candidate_app),
            ],
            "Native EDSDK helper app signing failed",
        )
        _run_checked(
            ["codesign", "--verify", "--deep", "--strict", str(candidate_app)],
            "Native EDSDK helper app verification failed",
        )
        previous = sdk_dir / ".EDSDKHelper.previous.app"
        if previous.exists():
            shutil.rmtree(previous)
        if output_app.exists():
            output_app.replace(previous)
        candidate_app.replace(output_app)
        if previous.exists():
            shutil.rmtree(previous)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)
    return _existing_helper_app(output_app)


class NativeHelperBackend:
    """Use a small ad-hoc-signed helper process to own the EDSDK session."""

    def __init__(self, sdk_path=None, physical_write_enabled=False):
        self.sdk_path = sdk_path
        self.physical_write_enabled = bool(physical_write_enabled)
        self.process = None
        self.helper_path = None
        self.framework = None
        self.details = None
        self.lock = threading.RLock()

    def _read_response(self):
        line = self.process.stdout.readline()
        if line == "":
            stderr = self.process.stderr.read().strip()
            raise CameraSessionError(
                f"Native EDSDK helper stopped unexpectedly{': ' + stderr if stderr else '.'}"
            )
        try:
            response = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CameraSessionError(f"Native EDSDK helper returned invalid data: {line.strip()}") from exc
        if not response.get("ok"):
            raise NativeSdkError(response.get("operation", "NativeHelper"), response.get("code", 0xFFFFFFFF))
        return response

    def _command(self, command):
        with self.lock:
            if self.process is None or self.process.poll() is not None:
                raise CameraSessionError("Native EDSDK helper is not running")
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            return self._read_response()

    def initialize(self):
        self.helper_path, self.framework = build_native_helper(self.sdk_path)
        command = [str(self.helper_path)]
        if self.physical_write_enabled:
            command.append("--enable-physical-writes")
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._read_response()

    def discover_cameras(self):
        return self._command("DISCOVER")["cameras"]

    def open_session(self, index):
        self.details = self._command(f"CONNECT {index}")

    def read_camera_details(self):
        if self.details is None:
            self.details = self._command("DETAILS")
        return {
            "product_name": self.details.get("product_name"),
            "body_id": self.details.get("body_id"),
            "firmware_version": self.details.get("firmware_version"),
            "battery_raw": self.details.get("battery_raw"),
            "lens_name": self.details.get("lens_name"),
        }

    def poll_product_name(self):
        return self._command("POLL")["product_name"]

    def read_capabilities(self):
        return self._command("CAPABILITIES")["properties"]

    def read_physical_setting(self, key):
        if key not in qualification_candidates():
            raise CameraSessionError(f"Physical setting is not qualification-allowlisted: {key}")
        observed = next(
            (item for item in self.read_capabilities() if item.get("key") == key),
            None,
        )
        if observed is None or observed.get("read_status") != "sdk_verified":
            raise CameraSessionError(f"Physical setting is not readable: {key}")
        return observed.get("value_raw")

    def write_physical_setting(self, key, value_raw):
        if not self.physical_write_enabled:
            raise CameraSessionError("Native physical setting writes were not explicitly enabled at launch.")
        if key not in qualification_candidates():
            raise CameraSessionError(f"Physical setting is not qualification-allowlisted: {key}")
        if isinstance(value_raw, bool) or not isinstance(value_raw, int) or not 0 <= value_raw <= 0xFFFFFFFF:
            raise CameraSessionError("Physical write value must be an unsigned 32-bit integer.")
        return self._command(f"WRITE {key} {value_raw}")

    def sdk_details(self):
        return {
            "path": str(self.framework) if self.framework else str(self.sdk_path or ""),
            "framework_version": _framework_version(self.framework) if self.framework else None,
            "helper": str(self.helper_path) if self.helper_path else None,
        }

    def shutdown(self):
        process = self.process
        self.process = None
        self.details = None
        if process is None:
            return
        if process.poll() is None:
            try:
                process.stdin.write("QUIT\n")
                process.stdin.flush()
                process.stdout.readline()
                process.wait(timeout=3)
            except Exception:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()
