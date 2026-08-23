import json
from pathlib import Path
import sys
import unittest

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from camera_control.connector import probe_camera
from camera_control.errors import (
    CameraDisconnectedError,
    CameraSelectionError,
    NoCameraError,
    WrongCameraModelError,
)


class FakeBackend:
    def __init__(self, cameras=None, details=None, poll_values=None, failures=None):
        self.cameras = cameras or []
        self.details = details or {}
        self.poll_values = list(poll_values or [self.details.get("product_name")])
        self.failures = failures or {}
        self.calls = []
        self.open_index = None

    def _call(self, name):
        self.calls.append(name)
        failure = self.failures.get(name)
        if failure:
            raise failure

    def initialize(self):
        self._call("initialize")

    def discover_cameras(self):
        self._call("discover")
        return self.cameras

    def open_session(self, index):
        self._call(f"open:{index}")
        self.open_index = index

    def read_camera_details(self):
        self._call("read_details")
        return dict(self.details)

    def poll_product_name(self):
        self._call("poll")
        value = self.poll_values.pop(0)
        if isinstance(value, Exception):
            raise value
        return value

    def sdk_details(self):
        self._call("sdk_details")
        return {"path": "/external/EDSDK.framework/EDSDK", "framework_version": "13.test"}

    def shutdown(self):
        self._call("shutdown")


def eos_r5_backend(**kwargs):
    defaults = {
        "cameras": [{"index": 0, "product_name": "EOS R5"}],
        "details": {
            "product_name": "EOS R5",
            "body_id": "1234567890",
            "firmware_version": "2.2.1",
            "battery_raw": 100,
        },
    }
    defaults.update(kwargs)
    return FakeBackend(**defaults)


class ConnectionProbeTests(unittest.TestCase):
    def test_success_is_read_only_and_cleans_up(self):
        backend = eos_r5_backend()
        result = probe_camera(backend)
        self.assertTrue(result["ok"])
        self.assertTrue(result["read_only"])
        self.assertTrue(result["session_closed_cleanly"])
        self.assertEqual(result["camera"]["product_name"], "EOS R5")
        self.assertEqual(backend.calls[-1], "shutdown")
        self.assertFalse(any("write" in call.lower() for call in backend.calls))
        json.dumps(result)

    def test_normalizes_only_product_whitespace(self):
        backend = eos_r5_backend(
            details={
                "product_name": "  EOS   R5 ",
                "body_id": None,
                "firmware_version": None,
                "battery_raw": None,
            }
        )
        result = probe_camera(backend)
        self.assertEqual(result["camera"]["product_name"], "EOS R5")
        self.assertIsNone(result["camera"]["firmware_version"])

    def test_accepts_canon_sdk_product_prefix(self):
        backend = eos_r5_backend(
            details={
                "product_name": "Canon EOS R5",
                "body_id": "1234567890",
                "firmware_version": "2.2.1",
                "battery_raw": 100,
            },
            poll_values=["Canon EOS R5"],
        )
        result = probe_camera(backend, watch_seconds=0.01, poll_interval=0.01)
        self.assertEqual(result["camera"]["product_name"], "Canon EOS R5")

    def test_no_camera_still_shuts_down(self):
        backend = FakeBackend(cameras=[])
        with self.assertRaises(NoCameraError):
            probe_camera(backend)
        self.assertEqual(backend.calls[-1], "shutdown")

    def test_multiple_cameras_requires_selection(self):
        cameras = [
            {"index": 0, "product_name": "EOS R5"},
            {"index": 1, "product_name": "EOS R5"},
        ]
        backend = FakeBackend(cameras=cameras)
        with self.assertRaises(CameraSelectionError) as caught:
            probe_camera(backend)
        self.assertEqual(len(caught.exception.cameras), 2)
        self.assertEqual(backend.calls[-1], "shutdown")

    def test_selected_camera_index_is_opened(self):
        backend = eos_r5_backend(
            cameras=[
                {"index": 0, "product_name": "EOS R6"},
                {"index": 1, "product_name": "EOS R5"},
            ]
        )
        result = probe_camera(backend, camera_index=1)
        self.assertEqual(result["camera"]["index"], 1)
        self.assertIn("open:1", backend.calls)

    def test_wrong_model_is_rejected_and_cleaned_up(self):
        backend = eos_r5_backend(
            cameras=[{"index": 0, "product_name": "EOS R5 Mark II"}],
            details={"product_name": "EOS R5 Mark II"},
        )
        with self.assertRaises(WrongCameraModelError):
            probe_camera(backend)
        self.assertEqual(backend.calls[-1], "shutdown")

    def test_prefixed_wrong_model_is_rejected(self):
        backend = eos_r5_backend(
            details={"product_name": "Canon EOS R5 Mark II"},
        )
        with self.assertRaises(WrongCameraModelError):
            probe_camera(backend)

    def test_disconnect_during_watch_is_reported_and_cleaned_up(self):
        backend = eos_r5_backend(poll_values=[RuntimeError("USB gone")])
        with self.assertRaises(CameraDisconnectedError):
            probe_camera(backend, watch_seconds=1, poll_interval=0, sleep=lambda _: None)
        self.assertEqual(backend.calls[-1], "shutdown")

    def test_cleanup_failure_prevents_success(self):
        backend = eos_r5_backend(failures={"shutdown": RuntimeError("close failed")})
        with self.assertRaisesRegex(Exception, "did not close cleanly"):
            probe_camera(backend)

    def test_primary_and_cleanup_failures_are_both_reported(self):
        backend = FakeBackend(
            cameras=[],
            failures={"shutdown": RuntimeError("close failed")},
        )
        with self.assertRaisesRegex(NoCameraError, "cleanup also reported: close failed"):
            probe_camera(backend)


if __name__ == "__main__":
    unittest.main()
