#!/usr/bin/env python3
"""Read-only Canon EOS R5 USB connection probe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    BUILD_DIR = Path(__file__).resolve().parents[1]
    if str(BUILD_DIR) not in sys.path:
        sys.path.insert(0, str(BUILD_DIR))
    from camera_control.connector import probe_camera
    from camera_control.native_backend import NativeHelperBackend
    from camera_control.errors import CameraControlError
else:
    from .connector import probe_camera
    from .native_backend import NativeHelperBackend
    from .errors import CameraControlError


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Open a read-only Canon EDSDK session and verify a connected EOS R5."
    )
    parser.add_argument(
        "--sdk-path",
        help="Canon-provided EDSDK.framework directory or EDSDK binary. Defaults to CANON_EDSDK_FRAMEWORK and standard framework locations.",
    )
    parser.add_argument("--camera-index", type=int, help="Connected camera index when more than one is present.")
    parser.add_argument(
        "--watch-seconds",
        type=int,
        default=0,
        help="Keep the session open for this bounded number of seconds and poll for disconnects.",
    )
    parser.add_argument("--json", action="store_true", help="Print structured JSON output.")
    args = parser.parse_args(argv)
    if args.camera_index is not None and args.camera_index < 0:
        parser.error("--camera-index must be zero or greater")
    if args.watch_seconds < 0 or args.watch_seconds > 3600:
        parser.error("--watch-seconds must be between 0 and 3600")
    return args


def _human_report(result):
    camera = result["camera"]
    sdk = result["sdk"]
    lines = [
        "EOS R5 USB connection verified (read-only).",
        f"Camera index: {camera['index']}",
        f"Product: {camera['product_name']}",
        f"Body ID: {camera['body_id'] or 'Unavailable'}",
        f"Firmware: {camera['firmware_version'] or 'Unavailable'}",
        f"Battery raw value: {camera['battery_raw'] if camera['battery_raw'] is not None else 'Unavailable'}",
        f"EDSDK: {sdk['path']}",
        f"EDSDK framework version: {sdk['framework_version'] or 'Unavailable'}",
        f"Watch polls completed: {result['watch']['polls_completed']}",
        "Camera settings changed: No",
        "Session closed cleanly: Yes",
    ]
    return "\n".join(lines)


def main(argv=None, backend_factory=NativeHelperBackend):
    args = parse_args(argv)
    try:
        backend = backend_factory(args.sdk_path)
        result = probe_camera(
            backend,
            camera_index=args.camera_index,
            watch_seconds=args.watch_seconds,
        )
    except CameraControlError as exc:
        if args.json:
            print(json.dumps(exc.as_dict(), indent=2, sort_keys=True))
        else:
            print(f"USB connection probe stopped: {exc}", file=sys.stderr)
        return exc.exit_code
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_human_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
