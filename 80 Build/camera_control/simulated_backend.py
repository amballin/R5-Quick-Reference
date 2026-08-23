"""Deterministic read-only camera backend for Camera Lab development."""

from __future__ import annotations

from .capability_registry import simulated_capabilities


SCENARIOS = {
    "ready": "One EOS R5",
    "no_camera": "No camera",
    "multiple": "Multiple cameras",
    "wrong_model": "Wrong Canon model",
    "missing_properties": "Missing optional properties",
    "busy": "Camera session busy",
    "disconnect": "Disconnect after connection",
}


class SimulatedBackend:
    def __init__(self, scenario="ready"):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown simulated scenario: {scenario}")
        self.scenario = scenario
        self.initialized = False
        self.open_camera = None
        self.disconnected = False

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
            }
        if self.scenario == "missing_properties":
            return {
                "product_name": "EOS R5",
                "body_id": None,
                "firmware_version": None,
                "battery_raw": None,
            }
        return {
            "product_name": "EOS R5",
            "body_id": "SIM-R5-0001",
            "firmware_version": "2.2.1",
            "battery_raw": 100,
        }

    def poll_product_name(self):
        if self.open_camera is None or self.disconnected or self.scenario == "disconnect":
            raise RuntimeError("Simulated USB connection was lost")
        return self.read_camera_details()["product_name"]

    def read_capabilities(self):
        if self.open_camera is None or self.disconnected:
            raise RuntimeError("No connected simulated camera is available for capability discovery")
        return simulated_capabilities()

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
