"""Stateful read-only service shared by Camera Lab and future editor integration."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import threading

from .connector import EXPECTED_MODEL, is_expected_model, normalize_product_name
from .capability_mapping import capability_coverage, enrich_properties
from .errors import (
    CameraControlError,
    CameraDisconnectedError,
    CameraSelectionError,
    CameraSessionError,
    NoCameraError,
    WrongCameraModelError,
)
from .simulated_backend import SCENARIOS, SimulatedBackend
from .native_backend import NativeHelperBackend
from .profile_comparison import compare_profile as build_profile_comparison
from .profile_comparison import list_profiles


CAMERA_LAB_VERSION = "1.0.0"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAMERA_LAB_ROOT = Path(__file__).resolve().parent
CAMERA_LAB_BUILD_INPUTS = (
    PROJECT_ROOT / "00 Master" / "baseline.yaml",
    PROJECT_ROOT / "00 Master" / "camera_capabilities.yaml",
    PROJECT_ROOT / "00 Master" / "card_layout.yaml",
    PROJECT_ROOT / "00 Master" / "my_menu.yaml",
    PROJECT_ROOT / "00 Master" / "my_menu_colors.yaml",
    PROJECT_ROOT / "00 Master" / "setting_access.yaml",
    PROJECT_ROOT / "controls.yaml",
)
CAMERA_LAB_SOURCE_SUFFIXES = {".c", ".css", ".entitlements", ".h", ".html", ".js", ".py"}


def camera_lab_info():
    digest = hashlib.sha256()
    sources = {
        source
        for source in CAMERA_LAB_ROOT.rglob("*")
        if source.is_file() and source.suffix in CAMERA_LAB_SOURCE_SUFFIXES
    }
    sources.update(source for source in CAMERA_LAB_BUILD_INPUTS if source.is_file())
    sources.update((PROJECT_ROOT / "10 Profiles").glob("*.yaml"))
    for source in sorted(sources):
        relative = source.relative_to(PROJECT_ROOT)
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(source.read_bytes())
        digest.update(b"\0")
    return {"version": CAMERA_LAB_VERSION, "build": digest.hexdigest()[:8]}


class CameraControlService:
    """Own at most one SDK backend and camera session."""

    def __init__(self, backend_mode="simulated", sdk_path=None, simulated_scenario="ready"):
        if backend_mode not in {"simulated", "edsdk"}:
            raise ValueError("backend_mode must be simulated or edsdk")
        if simulated_scenario not in SCENARIOS:
            raise ValueError(f"Unknown simulated scenario: {simulated_scenario}")
        self.backend_mode = backend_mode
        self.sdk_path = sdk_path
        self.simulated_scenario = simulated_scenario
        self.backend = None
        self.camera = None
        self.sdk = None
        self.capabilities = None
        self.last_camera_index = None
        self.last_error = None
        self.app_info = camera_lab_info()
        self.events = deque(maxlen=100)
        self.lock = threading.RLock()
        self._event("service_ready", f"Camera Lab started in {backend_mode} mode.")

    def _event(self, kind, message):
        self.events.append(
            {
                "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "kind": kind,
                "message": message,
            }
        )

    def _new_backend(self):
        if self.backend_mode == "simulated":
            return SimulatedBackend(self.simulated_scenario)
        return NativeHelperBackend(self.sdk_path)

    @staticmethod
    def _camera_choices(cameras):
        return [
            {"index": camera.get("index"), "product_name": camera.get("product_name")}
            for camera in cameras
        ]

    @staticmethod
    def _select_camera(cameras, camera_index):
        if not cameras:
            raise NoCameraError("No Canon camera was found.")
        if camera_index is None and len(cameras) > 1:
            raise CameraSelectionError(
                "More than one Canon camera is connected. Select the intended camera.",
                cameras=CameraControlService._camera_choices(cameras),
            )
        selected_index = cameras[0]["index"] if camera_index is None else camera_index
        selected = next((camera for camera in cameras if camera.get("index") == selected_index), None)
        if selected is None:
            raise CameraSelectionError(
                f"Camera index {selected_index} is unavailable.",
                cameras=CameraControlService._camera_choices(cameras),
            )
        return selected

    def _shutdown_backend(self):
        backend = self.backend
        self.backend = None
        self.camera = None
        self.sdk = None
        self.capabilities = None
        if backend is not None:
            backend.shutdown()

    def _record_error(self, exc):
        self.last_error = {
            "kind": getattr(exc, "error_kind", "camera_session"),
            "message": str(exc),
        }
        self._event("error", str(exc))

    def status(self, check_connection=True):
        with self.lock:
            if check_connection and self.backend is not None and self.camera is not None:
                try:
                    observed = normalize_product_name(self.backend.poll_product_name())
                    if not is_expected_model(observed):
                        raise CameraDisconnectedError("Connected camera identity changed or became unavailable.")
                except Exception as exc:
                    error = exc if isinstance(exc, CameraControlError) else CameraDisconnectedError(
                        "The EOS R5 stopped responding. Reconnect it and begin a new session."
                    )
                    self._record_error(error)
                    try:
                        self._shutdown_backend()
                    except Exception as cleanup_exc:
                        self._event("cleanup_error", str(cleanup_exc))
            return {
                "ok": True,
                "backend_mode": self.backend_mode,
                "app": dict(self.app_info),
                "simulated_scenario": self.simulated_scenario if self.backend_mode == "simulated" else None,
                "connected": self.camera is not None,
                "camera": dict(self.camera) if self.camera else None,
                "sdk": dict(self.sdk) if self.sdk else None,
                "capabilities": dict(self.capabilities) if self.capabilities else None,
                "reconnect_available": self.last_camera_index is not None,
                "last_error": dict(self.last_error) if self.last_error else None,
                "read_only": True,
                "available_scenarios": SCENARIOS if self.backend_mode == "simulated" else {},
            }

    def discover(self):
        with self.lock:
            if self.camera is not None:
                return {"ok": True, "cameras": [dict(self.camera)], "connected": True}
            backend = self._new_backend()
            try:
                backend.initialize()
                cameras = backend.discover_cameras()
                sdk = backend.sdk_details()
                self.last_error = None
                self._event("discovery", f"Found {len(cameras)} camera(s).")
                return {"ok": True, "cameras": self._camera_choices(cameras), "sdk": sdk, "connected": False}
            except CameraControlError:
                raise
            except Exception as exc:
                raise CameraSessionError(f"Camera discovery failed: {exc}") from exc
            finally:
                try:
                    backend.shutdown()
                except Exception as exc:
                    self._event("cleanup_error", str(exc))

    def connect(self, camera_index=None):
        with self.lock:
            if self.camera is not None:
                return self.status(check_connection=True)
            backend = self._new_backend()
            self.backend = backend
            try:
                backend.initialize()
                cameras = backend.discover_cameras()
                selected = self._select_camera(cameras, camera_index)
                backend.open_session(selected["index"])
                details = backend.read_camera_details()
                product_name = normalize_product_name(details.get("product_name"))
                if not is_expected_model(product_name):
                    actual = product_name or "unavailable"
                    raise WrongCameraModelError(
                        f"Connected camera is {actual}, not {EXPECTED_MODEL}. Camera Lab will not operate on another model."
                    )
                self.camera = {
                    "index": selected["index"],
                    "product_name": product_name,
                    "body_id": details.get("body_id"),
                    "firmware_version": details.get("firmware_version"),
                    "battery_raw": details.get("battery_raw"),
                }
                self.last_camera_index = selected["index"]
                self.sdk = backend.sdk_details()
                self.last_error = None
                self._event("connected", f"Connected to {product_name} at index {selected['index']}.")
                return self.status(check_connection=False)
            except Exception as exc:
                error = exc if isinstance(exc, CameraControlError) else CameraSessionError(
                    f"Camera connection failed: {exc}"
                )
                self._record_error(error)
                try:
                    self._shutdown_backend()
                except Exception as cleanup_exc:
                    error.args = (f"{error} Session cleanup also reported: {cleanup_exc}",)
                raise error

    def disconnect(self):
        with self.lock:
            was_connected = self.camera is not None
            self._shutdown_backend()
            self.last_error = None
            self._event("disconnected", "Camera session closed." if was_connected else "No camera session was open.")
            return self.status(check_connection=False)

    def set_simulated_scenario(self, scenario):
        with self.lock:
            if self.backend_mode != "simulated":
                raise CameraSessionError("Simulation controls are unavailable in EDSDK mode.")
            if scenario not in SCENARIOS:
                raise CameraSessionError(f"Unknown simulated scenario: {scenario}")
            self._shutdown_backend()
            self.simulated_scenario = scenario
            self.last_error = None
            self._event("scenario", f"Simulation changed to: {SCENARIOS[scenario]}.")
            return self.status(check_connection=False)

    def simulate_disconnect(self):
        with self.lock:
            if self.backend_mode != "simulated" or not isinstance(self.backend, SimulatedBackend):
                raise CameraSessionError("Connect a simulated camera before using simulated disconnect.")
            self.backend.trigger_disconnect()
            self._event("simulation", "Simulated USB disconnect triggered.")
            return self.status(check_connection=True)

    def current_camera(self):
        with self.lock:
            status = self.status(check_connection=True)
            return {"ok": True, "camera": status["camera"], "connected": status["connected"]}

    def scan_capabilities(self):
        with self.lock:
            status = self.status(check_connection=True)
            automatic_reconnect_performed = False
            if (not status["connected"] or self.backend is None) and self.last_camera_index is None:
                raise CameraSessionError("Connect the EOS R5 before scanning its capabilities.")

            if not status["connected"] or self.backend is None:
                self._reconnect_for_scan()
                automatic_reconnect_performed = True

            try:
                properties = self.backend.read_capabilities()
            except Exception as exc:
                first_error = exc if isinstance(exc, CameraControlError) else CameraSessionError(
                    f"Capability scan failed: {exc}"
                )
                self._record_error(first_error)
                try:
                    self._shutdown_backend()
                except Exception as cleanup_exc:
                    self._event("cleanup_error", str(cleanup_exc))

                if automatic_reconnect_performed:
                    error = self._scan_recovery_error(first_error)
                    self._record_error(error)
                    raise error from first_error

                try:
                    self._reconnect_for_scan()
                    automatic_reconnect_performed = True
                    properties = self.backend.read_capabilities()
                except Exception as recovery_exc:
                    try:
                        self._shutdown_backend()
                    except Exception as cleanup_exc:
                        self._event("cleanup_error", str(cleanup_exc))
                    error = self._scan_recovery_error(recovery_exc)
                    self._record_error(error)
                    raise error from recovery_exc
            normalized = []
            for observed in properties:
                item = dict(observed)
                item["write_tested"] = False
                item["write_classification"] = "unverified"
                item["descriptor_suggests_configurable"] = (
                    item.get("descriptor_status") == "sdk_verified"
                    and item.get("descriptor_access") in {"write", "read_write"}
                )
                normalized.append(item)
            normalized = enrich_properties(normalized)
            readable = sum(item.get("read_status") == "sdk_verified" for item in normalized)
            descriptors = sum(item.get("descriptor_status") == "sdk_verified" for item in normalized)
            self.capabilities = {
                "evidence_method": "sdk_verified",
                "read_only": True,
                "write_testing_performed": False,
                "properties": normalized,
                "summary": {
                    "total": len(normalized),
                    "readable": readable,
                    "unreadable": len(normalized) - readable,
                    "descriptors_available": descriptors,
                },
                "coverage": capability_coverage(),
            }
            self._event(
                "capability_scan",
                f"Read {readable} of {len(normalized)} capability properties; no writes attempted.",
            )
            return {
                "ok": True,
                "camera": dict(self.camera),
                "sdk": dict(self.sdk),
                "automatic_reconnect_performed": automatic_reconnect_performed,
                **self.capabilities,
            }

    def _reconnect_for_scan(self):
        self._event("automatic_reconnect", "Camera session stopped responding; reconnecting once before scanning.")
        try:
            self.connect(self.last_camera_index)
        except Exception as exc:
            raise self._scan_recovery_error(exc) from exc

    @staticmethod
    def _scan_recovery_error(exc):
        return CameraSessionError(
            "Automatic camera reconnection failed. Wake or power-cycle the EOS R5, close EOS Utility, "
            "reconnect the USB cable, then retry the scan. If it still fails, restart Camera Lab. "
            f"Details: {exc}"
        )

    def profiles(self):
        return {"ok": True, "profiles": list_profiles()}

    def compare_profile(self, profile_name):
        with self.lock:
            status = self.status(check_connection=True)
            if not status["connected"] or self.capabilities is None:
                raise CameraSessionError("Connect the EOS R5 and scan capabilities before comparing a profile.")
            try:
                comparison = build_profile_comparison(profile_name, self.capabilities["properties"])
            except ValueError as exc:
                raise CameraSessionError(str(exc)) from exc
            self._event("profile_comparison", f"Compared {comparison['profile']['title']} without changing the camera.")
            return {"ok": True, **comparison}

    def event_log(self):
        with self.lock:
            return {"ok": True, "events": list(reversed(self.events))}

    def close(self):
        with self.lock:
            try:
                self._shutdown_backend()
            finally:
                self._event("service_stopped", "Camera Lab stopped.")
