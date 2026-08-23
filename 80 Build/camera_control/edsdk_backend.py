"""Minimal read-only ctypes adapter for Canon EDSDK connection probing."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
import plistlib

from .errors import SdkUnavailableError


PROP_PRODUCT_NAME = 0x00000002
PROP_FIRMWARE_VERSION = 0x00000007
PROP_BATTERY_LEVEL = 0x00000008
PROP_BODY_ID_EX = 0x00000015


class NativeSdkError(RuntimeError):
    def __init__(self, operation, code):
        self.operation = operation
        self.code = int(code)
        super().__init__(f"{operation} returned EDSDK error 0x{self.code:08X}")


def _binary_options(path):
    path = Path(path).expanduser()
    if path.suffix == ".framework" or path.name == "EDSDK.framework":
        return [
            path / "EDSDK",
            path / "Versions" / "Current" / "EDSDK",
            path / "Versions" / "A" / "EDSDK",
        ]
    return [path]


def resolve_sdk_binary(explicit_path=None):
    requested = explicit_path or os.environ.get("CANON_EDSDK_FRAMEWORK")
    candidates = []
    if requested:
        candidates.extend(_binary_options(requested))
    else:
        candidates.extend(_binary_options("/Library/Frameworks/EDSDK.framework"))
        candidates.extend(_binary_options(Path.home() / "Library/Frameworks/EDSDK.framework"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    searched = ", ".join(str(candidate) for candidate in candidates)
    hint = "Set CANON_EDSDK_FRAMEWORK or pass --sdk-path with the Canon-provided EDSDK framework."
    raise SdkUnavailableError(f"Canon EDSDK was not found. Searched: {searched}. {hint}")


def _framework_version(binary):
    framework = next((parent for parent in [binary.parent, *binary.parents] if parent.suffix == ".framework"), None)
    if framework is None:
        return None
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


class EdsdkBackend:
    """Own EDSDK initialization, references, and one optional camera session."""

    def __init__(self, sdk_path=None):
        self.binary = resolve_sdk_binary(sdk_path)
        try:
            self.library = ctypes.CDLL(str(self.binary))
        except OSError as exc:
            raise SdkUnavailableError(f"Canon EDSDK could not be loaded from {self.binary}: {exc}") from exc
        self._configure_functions()
        self.initialized = False
        self.camera_list = None
        self.cameras = []
        self.open_camera = None

    def _configure_functions(self):
        ref = ctypes.c_void_p
        uint32_pointer = ctypes.POINTER(ctypes.c_uint32)
        ref_pointer = ctypes.POINTER(ref)

        self.library.EdsInitializeSDK.argtypes = []
        self.library.EdsInitializeSDK.restype = ctypes.c_uint32
        self.library.EdsTerminateSDK.argtypes = []
        self.library.EdsTerminateSDK.restype = ctypes.c_uint32
        self.library.EdsGetCameraList.argtypes = [ref_pointer]
        self.library.EdsGetCameraList.restype = ctypes.c_uint32
        self.library.EdsGetChildCount.argtypes = [ref, uint32_pointer]
        self.library.EdsGetChildCount.restype = ctypes.c_uint32
        self.library.EdsGetChildAtIndex.argtypes = [ref, ctypes.c_int32, ref_pointer]
        self.library.EdsGetChildAtIndex.restype = ctypes.c_uint32
        self.library.EdsOpenSession.argtypes = [ref]
        self.library.EdsOpenSession.restype = ctypes.c_uint32
        self.library.EdsCloseSession.argtypes = [ref]
        self.library.EdsCloseSession.restype = ctypes.c_uint32
        self.library.EdsGetPropertySize.argtypes = [
            ref,
            ctypes.c_uint32,
            ctypes.c_int32,
            uint32_pointer,
            uint32_pointer,
        ]
        self.library.EdsGetPropertySize.restype = ctypes.c_uint32
        self.library.EdsGetPropertyData.argtypes = [
            ref,
            ctypes.c_uint32,
            ctypes.c_int32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        self.library.EdsGetPropertyData.restype = ctypes.c_uint32
        self.library.EdsRelease.argtypes = [ref]
        self.library.EdsRelease.restype = ctypes.c_uint32

    @staticmethod
    def _check(operation, code):
        if code != 0:
            raise NativeSdkError(operation, code)

    def initialize(self):
        self._check("EdsInitializeSDK", self.library.EdsInitializeSDK())
        self.initialized = True

    def discover_cameras(self):
        camera_list = ctypes.c_void_p()
        self._check("EdsGetCameraList", self.library.EdsGetCameraList(ctypes.byref(camera_list)))
        self.camera_list = camera_list
        count = ctypes.c_uint32()
        self._check("EdsGetChildCount", self.library.EdsGetChildCount(camera_list, ctypes.byref(count)))
        discovered = []
        for index in range(count.value):
            camera = ctypes.c_void_p()
            self._check(
                f"EdsGetChildAtIndex({index})",
                self.library.EdsGetChildAtIndex(camera_list, index, ctypes.byref(camera)),
            )
            self.cameras.append(camera)
            product_name = self._optional_string(camera, PROP_PRODUCT_NAME)
            discovered.append({"index": index, "product_name": product_name})
        return discovered

    def open_session(self, index):
        try:
            camera = self.cameras[index]
        except IndexError as exc:
            raise NativeSdkError("SelectCamera", 0xFFFFFFFF) from exc
        self._check("EdsOpenSession", self.library.EdsOpenSession(camera))
        self.open_camera = camera

    def _property_buffer(self, camera, property_id):
        data_type = ctypes.c_uint32()
        size = ctypes.c_uint32()
        self._check(
            f"EdsGetPropertySize(0x{property_id:08X})",
            self.library.EdsGetPropertySize(
                camera,
                property_id,
                0,
                ctypes.byref(data_type),
                ctypes.byref(size),
            ),
        )
        if size.value == 0:
            raise NativeSdkError(f"EmptyProperty(0x{property_id:08X})", 0xFFFFFFFF)
        buffer = ctypes.create_string_buffer(size.value)
        self._check(
            f"EdsGetPropertyData(0x{property_id:08X})",
            self.library.EdsGetPropertyData(camera, property_id, 0, size.value, buffer),
        )
        return buffer.raw

    def _optional_string(self, camera, property_id):
        try:
            raw = self._property_buffer(camera, property_id)
        except NativeSdkError:
            return None
        value = raw.split(b"\x00", 1)[0]
        return value.decode("utf-8", errors="replace").strip() or None

    def _optional_uint32(self, camera, property_id):
        try:
            raw = self._property_buffer(camera, property_id)
        except NativeSdkError:
            return None
        if len(raw) < ctypes.sizeof(ctypes.c_uint32):
            return None
        return int.from_bytes(raw[:4], byteorder="little", signed=False)

    def read_camera_details(self):
        if self.open_camera is None:
            raise NativeSdkError("ReadWithoutOpenSession", 0xFFFFFFFF)
        product_name = self._optional_string(self.open_camera, PROP_PRODUCT_NAME)
        if not product_name:
            raise NativeSdkError("ReadProductName", 0xFFFFFFFF)
        return {
            "product_name": product_name,
            "body_id": self._optional_string(self.open_camera, PROP_BODY_ID_EX),
            "firmware_version": self._optional_string(self.open_camera, PROP_FIRMWARE_VERSION),
            "battery_raw": self._optional_uint32(self.open_camera, PROP_BATTERY_LEVEL),
        }

    def poll_product_name(self):
        if self.open_camera is None:
            raise NativeSdkError("PollWithoutOpenSession", 0xFFFFFFFF)
        product_name = self._optional_string(self.open_camera, PROP_PRODUCT_NAME)
        if not product_name:
            raise NativeSdkError("PollProductName", 0xFFFFFFFF)
        return product_name

    def sdk_details(self):
        return {
            "path": str(self.binary),
            "framework_version": _framework_version(self.binary),
        }

    def shutdown(self):
        errors = []
        if self.open_camera is not None:
            code = self.library.EdsCloseSession(self.open_camera)
            if code != 0:
                errors.append(NativeSdkError("EdsCloseSession", code))
            self.open_camera = None
        for camera in reversed(self.cameras):
            self.library.EdsRelease(camera)
        self.cameras = []
        if self.camera_list is not None:
            self.library.EdsRelease(self.camera_list)
            self.camera_list = None
        if self.initialized:
            code = self.library.EdsTerminateSDK()
            if code != 0:
                errors.append(NativeSdkError("EdsTerminateSDK", code))
            self.initialized = False
        if errors:
            raise errors[0]
