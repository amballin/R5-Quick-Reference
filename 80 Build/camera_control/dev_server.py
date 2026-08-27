#!/usr/bin/env python3
"""Loopback-only Camera Lab server with explicit guarded physical-write gates."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
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
    parser = argparse.ArgumentParser(description="Run EOS R5 Camera Lab with a read-only real-camera backend.")
    parser.add_argument("--backend", choices=("simulated", "edsdk"), default="simulated")
    parser.add_argument("--sdk-path", help="Canon-provided EDSDK framework directory or binary.")
    parser.add_argument("--scenario", default="ready", help="Initial simulated scenario.")
    parser.add_argument(
        "--enable-physical-writes",
        action="store_true",
        help="Expose reversible qualification and evidence-gated writes in EDSDK mode.",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    if args.port < 1 or args.port > 65535:
        parser.error("--port must be between 1 and 65535")
    if args.backend == "edsdk" and args.scenario != "ready":
        parser.error("--scenario is available only with the simulated backend")
    if args.backend != "edsdk" and args.enable_physical_writes:
        parser.error("--enable-physical-writes is available only with the EDSDK backend")
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

    def _guarded_endpoint_available(self):
        return self.service.backend_mode == "simulated" or self.service.physical_write_enabled

    def _qualification_endpoint_available(self):
        return self.service.backend_mode == "edsdk" and self.service.physical_write_enabled

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
                query = parse_qs(parsed.query)
                profile = (query.get("profile") or [None])[0]
                if not profile:
                    raise ValueError("profile query parameter is required")
                context_choices = {}
                for encoded_choice in query.get("context") or []:
                    context_path, separator, choice = encoded_choice.partition("|")
                    if not separator or not context_path or not choice:
                        raise ValueError("context query parameters must use path|choice")
                    context_choices[context_path] = choice
                manual_context = None
                encoded_manual_context = (query.get("manual_context") or [None])[0]
                if encoded_manual_context:
                    manual_context = json.loads(encoded_manual_context)
                    if not isinstance(manual_context, dict) or any(
                        key not in {"still_movie_context", "flash", "cards"}
                        or not isinstance(value, str)
                        or len(value) > 500
                        for key, value in manual_context.items()
                    ):
                        raise ValueError("manual_context must contain only short still/movie, flash, and cards text")
                self._send_json(self.service.compare_profile(profile, context_choices, manual_context))
            elif path == "/api/camera-control/guarded-run" and self._guarded_endpoint_available():
                query = parse_qs(parsed.query)
                session_id = (query.get("session_id") or [None])[0]
                if not session_id:
                    raise ValueError("session_id query parameter is required")
                self._send_json(self.service.guarded_run(session_id))
            elif path == "/api/camera-control/write-qualification/candidates" and self._qualification_endpoint_available():
                self._send_json(self.service.physical_write_candidates())
            elif path == "/api/camera-control/write-qualification" and self._qualification_endpoint_available():
                query = parse_qs(parsed.query)
                session_id = (query.get("session_id") or [None])[0]
                if not session_id:
                    raise ValueError("session_id query parameter is required")
                self._send_json(self.service.write_qualification(session_id))
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
            if path.startswith("/api/camera-control/guarded-run/") and not self._guarded_endpoint_available():
                self._send_error(HTTPStatus.NOT_FOUND, "not_found", "Unknown Camera Lab endpoint.")
                return
            if path.startswith("/api/camera-control/write-qualification/") and not self._qualification_endpoint_available():
                self._send_error(HTTPStatus.NOT_FOUND, "not_found", "Unknown Camera Lab endpoint.")
                return
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
            elif path == "/api/camera-control/guarded-run/prepare":
                profile = payload.get("profile")
                if not isinstance(profile, str) or not profile:
                    raise ValueError("profile is required")
                preflight = payload.get("preflight")
                context_choices = payload.get("context_choices") or {}
                if not isinstance(context_choices, dict) or any(
                    not isinstance(key, str) or not isinstance(value, str)
                    for key, value in context_choices.items()
                ):
                    raise ValueError("context_choices must be a string map")
                result = self.service.prepare_guarded_run(profile, preflight, context_choices)
            elif path == "/api/camera-control/guarded-run/confirm":
                result = self.service.confirm_guarded_run(payload.get("session_id"), payload.get("confirmed"))
            elif path == "/api/camera-control/guarded-run/next":
                result = self.service.execute_guarded_step(
                    payload.get("session_id"), payload.get("manual_confirmed") is True
                )
            elif path == "/api/camera-control/guarded-run/resume":
                result = self.service.resume_guarded_run(payload.get("session_id"))
            elif path == "/api/camera-control/guarded-run/abort":
                result = self.service.abort_guarded_run(payload.get("session_id"))
            elif path == "/api/camera-control/manual-confirmations/revoke":
                confirmations = payload.get("confirmations")
                if not isinstance(confirmations, list) or any(
                    not isinstance(item, dict)
                    or not isinstance(item.get("path"), str)
                    or not isinstance(item.get("target"), str)
                    for item in confirmations
                ):
                    raise ValueError("confirmations must contain path and target strings")
                result = self.service.revoke_manual_confirmations(confirmations, payload.get("manual_context"))
            elif path == "/api/camera-control/write-qualification/prepare":
                result = self.service.prepare_write_qualification(
                    payload.get("property_key"), payload.get("target_raw"), payload.get("preflight")
                )
            elif path == "/api/camera-control/write-qualification/confirm":
                result = self.service.confirm_write_qualification(
                    payload.get("session_id"), payload.get("confirmed")
                )
            elif path == "/api/camera-control/write-qualification/execute":
                result = self.service.execute_write_qualification(payload.get("session_id"))
            elif path == "/api/camera-control/restart-backend":
                backend = payload.get("backend")
                if backend not in {"edsdk", "simulated"}:
                    raise ValueError("backend must be edsdk or simulated")
                physical_write_enabled = payload.get("physical_write_enabled", False)
                if not isinstance(physical_write_enabled, bool):
                    raise ValueError("physical_write_enabled must be true or false")
                if backend != "edsdk" and physical_write_enabled:
                    raise ValueError("Physical writes can be enabled only with the EDSDK backend")
                if (
                    backend == self.service.backend_mode
                    and physical_write_enabled == self.service.physical_write_enabled
                ):
                    raise ValueError("Camera Lab is already running in the requested mode")
                if backend == "edsdk" and (
                    self.server.restart_sdk_path is None
                    or not self.server.restart_sdk_path.is_dir()
                ):
                    raise ValueError(
                        f"The machine-local Canon EDSDK helper was not found: {self.server.restart_sdk_path}"
                    )
                self.service.close()
                self.server.restart_backend = backend
                self.server.restart_physical_writes = physical_write_enabled
                result = {
                    "ok": True,
                    "restarting": True,
                    "backend": backend,
                    "physical_write_enabled": physical_write_enabled,
                    "camera_session_closed": True,
                }
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
            if path in {"/api/camera-control/shutdown", "/api/camera-control/restart-backend"}:
                threading.Thread(target=self.server.shutdown, daemon=True).start()
        except ValueError as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "invalid_request", str(exc))
        except CameraControlError as exc:
            self._send_json(exc.as_dict(), status=HTTPStatus.CONFLICT)
        except Exception as exc:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "server_error", str(exc))


def create_server(service, port=DEFAULT_PORT, token=None, restart_sdk_path=None):
    handler = type(
        "BoundCameraLabHandler",
        (CameraLabHandler,),
        {"service": service, "request_token": token or secrets.token_urlsafe(32)},
    )
    server = ThreadingHTTPServer((HOST, port), handler)
    server.restart_backend = None
    server.restart_physical_writes = False
    server.restart_sdk_path = (
        Path(restart_sdk_path).expanduser().resolve()
        if restart_sdk_path
        else None
    )
    return server


def main(argv=None):
    args = parse_args(argv)
    if args.sdk_path:
        restart_sdk_path = Path(args.sdk_path).expanduser().resolve()
    else:
        local_workspace = Path(
            os.environ.get("PRS_LOCAL_WORKSPACE", f"{PROJECT_ROOT} Local")
        ).expanduser().resolve()
        restart_sdk_path = local_workspace / "SDK" / "EDSDKHelper.app"
    service = CameraControlService(
        backend_mode=args.backend,
        sdk_path=args.sdk_path,
        simulated_scenario=args.scenario,
        physical_write_enabled=args.enable_physical_writes,
    )
    server = create_server(
        service,
        port=args.port,
        restart_sdk_path=restart_sdk_path,
    )
    print(f"EOS R5 Camera Lab: http://{HOST}:{server.server_port}/")
    write_state = "explicitly enabled" if service.physical_write_enabled else "disabled"
    print(f"Backend: {args.backend} • Real-camera setting writes: {write_state}")
    print("Press Control-C to stop.")
    restart_backend = None
    restart_physical_writes = False
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping Camera Lab.")
    finally:
        restart_backend = server.restart_backend
        restart_physical_writes = server.restart_physical_writes
        server.server_close()
        service.close()
    if restart_backend:
        restart_args = [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            "--backend",
            restart_backend,
            "--sdk-path",
            str(restart_sdk_path),
            "--port",
            str(args.port),
        ]
        if restart_physical_writes and restart_backend == "edsdk":
            restart_args.append("--enable-physical-writes")
        os.execv(sys.executable, restart_args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
