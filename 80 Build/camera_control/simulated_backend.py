"""Deterministic camera backend for Camera Lab development.

Only this simulator implements guarded setting mutation.  The Canon EDSDK
backends intentionally do not share or implement this interface.
"""

from __future__ import annotations

from .capability_mapping import VALUE_MAPS
from .capability_registry import CAPABILITY_PROPERTIES, simulated_capabilities


SCENARIOS = {
    "ready": "One EOS R5",
    "no_camera": "No camera",
    "multiple": "Multiple cameras",
    "wrong_model": "Wrong Canon model",
    "missing_properties": "Missing optional properties",
    "busy": "Camera session busy",
    "disconnect": "Disconnect after connection",
    "guarded_success": "Guarded run: successful write and readback",
    "guarded_readback_mismatch": "Guarded run: readback mismatch",
    "guarded_unsupported_value": "Guarded run: unsupported value",
    "guarded_missing_prerequisite": "Guarded run: missing prerequisite",
    "guarded_busy": "Guarded run: camera busy",
    "guarded_disconnect": "Guarded run: disconnect",
    "guarded_identity_change": "Guarded run: changed camera identity",
}


class SimulatedBackend:
    def __init__(self, scenario="ready"):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown simulated scenario: {scenario}")
        self.scenario = scenario
        self.initialized = False
        self.open_camera = None
        self.disconnected = False
        self.setting_values = {key: value for key, _, _, value in CAPABILITY_PROPERTIES}
        self.guarded_step_started = False
        self.write_count = 0

    def initialize(self):
        self.initialized = True

    def discover_cameras(self):
        if not self.initialized:
            raise RuntimeError("Simulated SDK is not initialized")
        if self.scenario == "no_camera":
            return []
        if self.scenario == "multiple":
            return [
                {"index": 0, "product_name": "EOS R5"},
                {"index": 1, "product_name": "EOS R5"},
            ]
        if self.scenario == "wrong_model":
            return [{"index": 0, "product_name": "EOS R5 Mark II"}]
        return [{"index": 0, "product_name": "EOS R5"}]

    def open_session(self, index):
        if self.scenario == "busy":
            raise RuntimeError("Simulated camera is busy in another application")
        cameras = self.discover_cameras()
        if not any(camera["index"] == index for camera in cameras):
            raise RuntimeError(f"Simulated camera index {index} is unavailable")
        self.open_camera = index

    def read_camera_details(self):
        if self.open_camera is None:
            raise RuntimeError("No simulated camera session is open")
        if self.scenario == "wrong_model":
            return {
                "product_name": "EOS R5 Mark II",
                "body_id": "SIM-R5M2-0001",
                "firmware_version": "1.0.0",
                "battery_raw": 100,
                "lens_name": "Simulated RF 100-500mm F4.5-7.1 L IS USM",
            }
        if self.scenario == "missing_properties":
            return {
                "product_name": "EOS R5",
                "body_id": None,
                "firmware_version": None,
                "battery_raw": None,
                "lens_name": None,
            }
        return {
            "product_name": "EOS R5",
            "body_id": "SIM-R5-0001",
            "firmware_version": "2.2.1",
            "battery_raw": 100,
            "lens_name": "Simulated RF 100-500mm F4.5-7.1 L IS USM",
        }

    def poll_product_name(self):
        if self.open_camera is None or self.disconnected or self.scenario == "disconnect":
            raise RuntimeError("Simulated USB connection was lost")
        if self.scenario == "guarded_disconnect" and self.guarded_step_started:
            self.disconnected = True
            raise RuntimeError("Simulated USB connection was lost during the guarded run")
        if self.scenario == "guarded_identity_change" and self.guarded_step_started:
            return "EOS R6"
        return self.read_camera_details()["product_name"]

    def read_capabilities(self):
        if self.open_camera is None or self.disconnected:
            raise RuntimeError("No connected simulated camera is available for capability discovery")
        return simulated_capabilities(self.setting_values)

    def guarded_prerequisite(self, key, value_raw):
        if self.scenario == "guarded_missing_prerequisite":
            return False, "Attach the required simulated lens before continuing."
        return True, None

    def supports_guarded_value(self, key, value_raw):
        if self.scenario == "guarded_unsupported_value":
            return False
        return value_raw in VALUE_MAPS.get(key, {})

    def begin_guarded_step(self):
        self.guarded_step_started = True

    def read_guarded_setting(self, key):
        if self.open_camera is None or self.disconnected:
            raise RuntimeError("No connected simulated camera is available")
        if self.scenario == "guarded_busy" and self.guarded_step_started:
            raise RuntimeError("Simulated camera is busy")
        if key not in self.setting_values:
            raise RuntimeError(f"Unknown simulated property: {key}")
        return self.setting_values[key]

    def write_guarded_setting(self, key, value_raw):
        if self.open_camera is None or self.disconnected:
            raise RuntimeError("No connected simulated camera is available")
        if self.scenario == "guarded_busy":
            raise RuntimeError("Simulated camera is busy")
        if not self.supports_guarded_value(key, value_raw):
            raise RuntimeError(f"Simulated value {value_raw} is unsupported for {key}")
        self.write_count += 1
        if self.scenario != "guarded_readback_mismatch":
            self.setting_values[key] = value_raw

    def sdk_details(self):
        return {
            "path": "Simulated EDSDK",
            "framework_version": "camera-lab-simulator-1",
        }

    def trigger_disconnect(self):
        if self.open_camera is None:
            raise RuntimeError("Connect the simulated camera before disconnecting it")
        self.disconnected = True

    def shutdown(self):
        self.open_camera = None
        self.initialized = False
        self.guarded_step_started = False
