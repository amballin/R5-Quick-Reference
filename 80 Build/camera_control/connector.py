"""Read-only EOS R5 connection orchestration independent of the native backend."""

from __future__ import annotations

import re
import time

from .errors import (
    CameraDisconnectedError,
    CameraSelectionError,
    CameraSessionError,
    NoCameraError,
    WrongCameraModelError,
)


EXPECTED_MODEL = "EOS R5"


def normalize_product_name(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def is_expected_model(value):
    product_name = normalize_product_name(value)
    return product_name in {EXPECTED_MODEL, f"Canon {EXPECTED_MODEL}"}


def _camera_choices(cameras):
    return [
        {
            "index": camera.get("index"),
            "product_name": camera.get("product_name"),
        }
        for camera in cameras
    ]


def _select_camera(cameras, camera_index):
    if not cameras:
        raise NoCameraError(
            "No Canon camera was found. Check camera power, sleep state, USB cable, and competing camera applications."
        )
    if camera_index is None and len(cameras) > 1:
        raise CameraSelectionError(
            "More than one Canon camera is connected. Rerun with --camera-index using one of the reported indexes.",
            cameras=_camera_choices(cameras),
        )
    selected_index = cameras[0]["index"] if camera_index is None else camera_index
    selected = next((camera for camera in cameras if camera.get("index") == selected_index), None)
    if selected is None:
        raise CameraSelectionError(
            f"Camera index {selected_index} is not available.",
            cameras=_camera_choices(cameras),
        )
    return selected


def probe_camera(backend, camera_index=None, watch_seconds=0, poll_interval=1.0, sleep=time.sleep):
    """Open one EOS R5 session, read identity, optionally poll, and always clean up."""
    result = None
    primary_error = None
    try:
        backend.initialize()
        cameras = backend.discover_cameras()
        selected = _select_camera(cameras, camera_index)
        backend.open_session(selected["index"])
        details = backend.read_camera_details()
        product_name = normalize_product_name(details.get("product_name"))
        if not is_expected_model(product_name):
            actual = product_name or "unavailable"
            raise WrongCameraModelError(
                f"Connected camera is {actual}, not {EXPECTED_MODEL}. This project will not operate on another model."
            )

        polls_completed = 0
        deadline = time.monotonic() + max(0, watch_seconds)
        while watch_seconds > 0 and time.monotonic() < deadline:
            sleep(min(poll_interval, max(0, deadline - time.monotonic())))
            try:
                observed = normalize_product_name(backend.poll_product_name())
            except Exception as exc:
                raise CameraDisconnectedError(
                    "The EOS R5 stopped responding during the connection watch. Reconnect it and begin a new session."
                ) from exc
            if not is_expected_model(observed):
                raise CameraDisconnectedError(
                    "The connected camera identity changed or became unavailable during the connection watch."
                )
            polls_completed += 1

        result = {
            "ok": True,
            "camera": {
                "index": selected["index"],
                "product_name": product_name,
                "body_id": details.get("body_id"),
                "firmware_version": details.get("firmware_version"),
                "battery_raw": details.get("battery_raw"),
            },
            "sdk": backend.sdk_details(),
            "watch": {
                "requested_seconds": watch_seconds,
                "polls_completed": polls_completed,
            },
            "read_only": True,
            "session_closed_cleanly": False,
        }
    except (NoCameraError, CameraSelectionError, WrongCameraModelError, CameraDisconnectedError) as exc:
        primary_error = exc
    except Exception as exc:
        primary_error = CameraSessionError(f"Canon camera session failed: {exc}")

    cleanup_error = None
    try:
        backend.shutdown()
    except Exception as exc:
        cleanup_error = exc

    if primary_error is not None:
        if cleanup_error is not None:
            primary_error.args = (
                f"{primary_error} Session cleanup also reported: {cleanup_error}",
            )
        raise primary_error
    if cleanup_error is not None:
        raise CameraSessionError(f"Camera responded, but the SDK session did not close cleanly: {cleanup_error}")

    result["session_closed_cleanly"] = True
    return result
