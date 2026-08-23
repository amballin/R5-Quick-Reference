#!/usr/bin/env python3
"""Loopback-only Camera Lab server for rapid USB interface development."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import secrets
import sys
import threading
from urllib.parse import parse_qs, urlparse

if __package__ in {None, ""}:
    BUILD_DIR = Path(__file__).resolve().parents[1]
    if str(BUILD_DIR) not in sys.path:
        sys.path.insert(0, str(BUILD_DIR))
    from camera_control.errors import CameraControlError
    from camera_control.service import CameraControlService
else:
    from .errors import CameraControlError
    from .service import CameraControlService


HOST = "127.0.0.1"
DEFAULT_PORT = 8770
MAX_REQUEST_BYTES = 64 * 1024
STATIC_DIR = Path(__file__).resolve().parent / "static"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_CAMERA_LOGO = PROJECT_ROOT / "60 Assets" / "Card Logos" / "png" / "Silver Logo.png"
ALLOWED_STATIC = {
    "/": STATIC_DIR / "index.html",
    "/index.html": STATIC_DIR / "index.html",
    "/app.js": STATIC_DIR / "app.js",
    "/styles.css": STATIC_DIR / "styles.css",
    "/silver-camera-logo.png": SILVER_CAMERA_LOGO,
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run the standalone read-only EOS R5 Camera Lab.")
    parser.add_argument("--backend", choices=("simulated", "edsdk"), default="simulated")
    parser.add_argument("--sdk-path", help="Canon-provided EDSDK framework directory or binary.")
    parser.add_argument("--scenario", default="ready", help="Initial simulated scenario.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    if args.port < 1 or args.port > 65535:
        parser.error("--port must be between 1 and 65535")
    if args.backend == "edsdk" and args.scenario != "ready":
        parser.error("--scenario is available only with the simulated backend")
    return args


class CameraLabHandler(BaseHTTPRequestHandler):
    service = None
    request_token = None
    server_version = "EOSR5CameraLab/0.1"

    def log_message(self, format_string, *args):
        sys.stderr.write(f"Camera Lab: {format_string % args}\n")

    def _host_is_allowed(self):
        host = self.headers.get("Host", "").split(":", 1)[0].strip("[]").lower()
        return host in {"127.0.0.1", "localhost", "::1"}

    def _security_headers(self, content_type):
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        )

    def _send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self._security_headers("application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, kind, message):
        self._send_json(
            {"ok": False, "error": {"kind": kind, "message": message}},
            status=status,
        )

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid Content-Length") from exc
        if length < 0 or length > MAX_REQUEST_BYTES:
            raise ValueError("Request body is too large")
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Request body must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("Request JSON must be an object")
        return payload

    def _serve_static(self, path):
        source = ALLOWED_STATIC.get(path)
        if source is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = source.read_bytes()
        if source.name == "index.html":
            body = body.replace(b"__CAMERA_LAB_TOKEN__", self.request_token.encode("ascii"))
        content_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type == "application/javascript":
            content_type += "; charset=utf-8"
        self.send_response(HTTPStatus.OK)
        self._security_headers(content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._host_is_allowed():
            self._send_error(HTTPStatus.FORBIDDEN, "invalid_host", "Camera Lab accepts loopback requests only.")
            return
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/camera-control/status":
                self._send_json(self.service.status())
            elif path == "/api/camera-control/cameras":
                self._send_json(self.service.discover())
            elif path == "/api/camera-control/camera":
                self._send_json(self.service.current_camera())
            elif path == "/api/camera-control/events":
                self._send_json(self.service.event_log())
            elif path == "/api/camera-control/capabilities":
                self._send_json(self.service.scan_capabilities())
            elif path == "/api/camera-control/profiles":
                self._send_json(self.service.profiles())
            elif path == "/api/camera-control/comparison":
                profile = (parse_qs(parsed.query).get("profile") or [None])[0]
                if not profile:
                    raise ValueError("profile query parameter is required")
                self._send_json(self.service.compare_profile(profile))
            elif path.startswith("/api/"):
                self._send_error(HTTPStatus.NOT_FOUND, "not_found", "Unknown Camera Lab endpoint.")
            else:
                self._serve_static(path)
        except ValueError as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "invalid_request", str(exc))
        except CameraControlError as exc:
            self._send_json(exc.as_dict(), status=HTTPStatus.CONFLICT)
        except Exception as exc:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "server_error", str(exc))

    def do_POST(self):
        if not self._host_is_allowed():
            self._send_error(HTTPStatus.FORBIDDEN, "invalid_host", "Camera Lab accepts loopback requests only.")
            return
        if not secrets.compare_digest(self.headers.get("X-Camera-Lab-Token", ""), self.request_token):
            self._send_error(HTTPStatus.FORBIDDEN, "invalid_token", "Camera Lab request token is missing or invalid.")
            return
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/camera-control/connect":
                index = payload.get("camera_index")
                if index is not None and (not isinstance(index, int) or isinstance(index, bool) or index < 0):
                    raise ValueError("camera_index must be a non-negative integer")
                result = self.service.connect(index)
            elif path == "/api/camera-control/disconnect":
                result = self.service.disconnect()
            elif path == "/api/camera-control/simulation-scenario":
                scenario = payload.get("scenario")
                if not isinstance(scenario, str):
                    raise ValueError("scenario must be a string")
                result = self.service.set_simulated_scenario(scenario)
            elif path == "/api/camera-control/simulate-disconnect":
                result = self.service.simulate_disconnect()
            elif path == "/api/camera-control/shutdown":
                self.service.close()
                result = {
                    "ok": True,
                    "shutting_down": True,
                    "camera_session_closed": True,
                }
            else:
                self._send_error(HTTPStatus.NOT_FOUND, "not_found", "Unknown Camera Lab endpoint.")
                return
            self._send_json(result)
            if path == "/api/camera-control/shutdown":
                threading.Thread(target=self.server.shutdown, daemon=True).start()
        except ValueError as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "invalid_request", str(exc))
        except CameraControlError as exc:
            self._send_json(exc.as_dict(), status=HTTPStatus.CONFLICT)
        except Exception as exc:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "server_error", str(exc))


def create_server(service, port=DEFAULT_PORT, token=None):
    handler = type(
        "BoundCameraLabHandler",
        (CameraLabHandler,),
        {"service": service, "request_token": token or secrets.token_urlsafe(32)},
    )
    return ThreadingHTTPServer((HOST, port), handler)


def main(argv=None):
    args = parse_args(argv)
    service = CameraControlService(
        backend_mode=args.backend,
        sdk_path=args.sdk_path,
        simulated_scenario=args.scenario,
    )
    server = create_server(service, port=args.port)
    print(f"EOS R5 Camera Lab: http://{HOST}:{server.server_port}/")
    print(f"Backend: {args.backend} • Camera-setting writes: disabled")
    print("Press Control-C to stop.")
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping Camera Lab.")
    finally:
        server.server_close()
        service.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
