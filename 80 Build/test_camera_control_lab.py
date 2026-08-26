from http.client import HTTPConnection
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from camera_control.dev_server import create_server
from camera_control.errors import CameraSelectionError, CameraSessionError, WrongCameraModelError
from camera_control.profile_comparison import _conditional_evaluation, _conditional_status, list_profiles
from camera_control.service import CameraControlService, camera_lab_info
from camera_control.simulated_backend import SimulatedBackend
from project_context import active_branch


class CameraControlServiceTests(unittest.TestCase):
    def test_contextual_comparison_evaluates_exact_ranges_and_guidance(self):
        cases = [
            ("exposure.exposure_compensation", "0", "0", "match"),
            ("exposure.exposure_compensation", "0 to +1/3", "+1/3", "equivalent"),
            ("exposure.exposure_compensation", "0 to +1/3", "+2/3", "difference"),
            ("exposure.exposure_compensation", "Adjust for background", "0", "conditional"),
            ("lens.aperture.target", "Auto", "Auto", "match"),
            ("lens.aperture.target", "f/8", "f/8.0", "equivalent"),
            ("lens.aperture.target", "f/8–f/11", "f/8.0", "equivalent"),
            ("lens.aperture.target", "f/8–f/11", "Auto", "difference"),
            ("lens.aperture.target", "f/8–f/11; bracket before f/16", "f/8.0", "conditional"),
            ("shutter.target", "Auto", "Auto", "match"),
            ("shutter.target", "1/200", "1/200", "match"),
            ("shutter.target", "1/2000–1/4000", "1/2500", "equivalent"),
            ("shutter.target", "2–6 s (start at 4 s)", "4 sec", "equivalent"),
            ("shutter.target", "1/2000–1/4000", "Auto", "difference"),
            ("shutter.target", "1/1000–1/2000 outdoor; 1/640–1/1000 indoor", "1/1000", "conditional"),
        ]
        for path, expected, actual, status in cases:
            with self.subTest(path=path, expected=expected, actual=actual):
                self.assertEqual(_conditional_status(path, expected, actual)[0], status)

    def test_contextual_comparison_requires_and_applies_authored_choices(self):
        shutter = "1/1000–1/2000 outdoor; 1/640–1/1000 indoor"
        unresolved = _conditional_evaluation("shutter.target", shutter, "1/800")
        self.assertEqual(unresolved["status"], "conditional")
        self.assertEqual(unresolved["context_prompt"]["question"], "Which lighting condition applies?")
        self.assertEqual(
            [(option["id"], option["target"]) for option in unresolved["context_prompt"]["options"]],
            [("outdoor", "1/1000–1/2000"), ("indoor", "1/640–1/1000")],
        )

        indoor = _conditional_evaluation("shutter.target", shutter, "1/800", "indoor")
        self.assertEqual(indoor["status"], "equivalent")
        self.assertEqual(indoor["context_prompt"]["selected_target"], "1/640–1/1000")

        action = _conditional_evaluation(
            "shutter.target",
            "1/200–1/320 portraits; 1/500+ action",
            "1/1000",
            "action",
        )
        self.assertEqual(action["status"], "equivalent")
        slower_action = _conditional_evaluation(
            "shutter.target",
            "1/200–1/320 portraits; 1/500+ action",
            "1/200",
            "action",
        )
        self.assertEqual(slower_action["status"], "difference")

        groups = _conditional_evaluation(
            "lens.aperture.target",
            "f/1.8–f/4 single; f/4–f/8 groups",
            "f/5.6",
            "groups",
        )
        self.assertEqual(groups["status"], "equivalent")

    def test_contextual_comparison_does_not_invent_unwritten_targets(self):
        background = _conditional_evaluation(
            "exposure.exposure_compensation",
            "Adjust for background",
            "0",
        )
        self.assertEqual(background["status"], "conditional")
        self.assertNotIn("context_prompt", background)
        bracketing = _conditional_evaluation(
            "lens.aperture.target",
            "f/8–f/11; bracket before f/16",
            "f/8.0",
        )
        self.assertEqual(bracketing["status"], "conditional")
        self.assertNotIn("context_prompt", bracketing)

    def test_camera_lab_info_exposes_version_and_source_derived_build(self):
        first = camera_lab_info()
        second = camera_lab_info()
        self.assertEqual(first, second)
        self.assertEqual(first["version"], "0.42.6")
        self.assertRegex(first["build"], r"^[0-9a-f]{8}$")
        branch = active_branch(PROJECT_ROOT)
        self.assertEqual(first["context_name"], "Main" if branch == "main" else "Prototype")
        self.assertEqual(first["project_context"]["branch"], branch)
        self.assertEqual(first["project_context"]["kind"], "main" if branch == "main" else "prototype")

    def test_native_helper_pumps_canon_events_before_property_scans(self):
        source = (BUILD_DIR / "camera_control" / "native" / "edsdk_helper.c").read_text(encoding="utf-8")
        self.assertIn("EdsSetPropertyEventHandler", source)
        self.assertIn('emit_error("EdsGetEvent(Capabilities)"', source)
        self.assertIn('emit_error("EdsGetEvent(Poll)"', source)

    def test_camera_lab_launcher_reopens_a_valid_running_lab(self):
        with tempfile.TemporaryDirectory(prefix="camera-lab-launcher-test-") as temporary:
            fake_bin = Path(temporary)
            (fake_bin / "open").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (fake_bin / "curl").write_text(
                "#!/bin/sh\nprintf '%s\\n' '{\"ok\":true,\"read_only\":true,\"backend_mode\":\"edsdk\",\"app\":{\"version\":\"0.42.6\",\"project_context\":{}}}'\n",
                encoding="utf-8",
            )
            (fake_bin / "open").chmod(0o755)
            (fake_bin / "curl").chmod(0o755)
            result = subprocess.run(
                [str(PROJECT_ROOT / "80 Build/scripts/start-camera-lab.sh")],
                check=False,
                capture_output=True,
                text=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Camera Lab is already running on port 8770", result.stdout)

    def test_backend_restart_replaces_the_server_process_with_simulator(self):
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        with tempfile.TemporaryDirectory(prefix="camera-lab-restart-sdk-") as sdk_path:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-B",
                    str(BUILD_DIR / "camera_control" / "dev_server.py"),
                    "--backend",
                    "edsdk",
                    "--sdk-path",
                    sdk_path,
                    "--port",
                    str(port),
                ],
                cwd=PROJECT_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            def get(path):
                connection = HTTPConnection("127.0.0.1", port, timeout=1)
                connection.request("GET", path, headers={"Host": "127.0.0.1"})
                response = connection.getresponse()
                raw = response.read()
                connection.close()
                return response.status, raw

            def post(path, token, payload):
                connection = HTTPConnection("127.0.0.1", port, timeout=2)
                connection.request(
                    "POST",
                    path,
                    body=json.dumps(payload),
                    headers={
                        "Host": "127.0.0.1",
                        "Content-Type": "application/json",
                        "X-Camera-Lab-Token": token,
                    },
                )
                response = connection.getresponse()
                raw = response.read()
                connection.close()
                return response.status, json.loads(raw)

            try:
                for _ in range(100):
                    try:
                        status, raw = get("/api/camera-control/status")
                        payload = json.loads(raw)
                        if status == 200 and payload["backend_mode"] == "edsdk":
                            break
                    except (ConnectionError, OSError, json.JSONDecodeError):
                        pass
                    time.sleep(0.05)
                else:
                    self.fail("EDSDK-mode test server did not start")

                _, index = get("/")
                token_match = re.search(rb'<meta name="camera-lab-token" content="([^"]+)">', index)
                self.assertIsNotNone(token_match)
                status, payload = post(
                    "/api/camera-control/restart-backend",
                    token_match.group(1).decode("ascii"),
                    {"backend": "simulated"},
                )
                self.assertEqual(status, 200)
                self.assertTrue(payload["restarting"])

                for _ in range(200):
                    try:
                        status, raw = get("/api/camera-control/status")
                        payload = json.loads(raw)
                        if status == 200 and payload["backend_mode"] == "simulated":
                            break
                    except (ConnectionError, OSError, json.JSONDecodeError):
                        pass
                    time.sleep(0.05)
                else:
                    self.fail("Camera Lab did not restart in simulated mode")
                self.assertIsNone(process.poll(), "The supervised server process should survive replacement")

                _, index = get("/")
                token_match = re.search(rb'<meta name="camera-lab-token" content="([^"]+)">', index)
                self.assertIsNotNone(token_match)
                status, payload = post(
                    "/api/camera-control/shutdown",
                    token_match.group(1).decode("ascii"),
                    {},
                )
                self.assertEqual(status, 200)
                self.assertTrue(payload["shutting_down"])
                process.wait(timeout=5)
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)

    def test_ready_scenario_connects_and_disconnects(self):
        service = CameraControlService()
        discovered = service.discover()
        self.assertEqual(discovered["cameras"], [{"index": 0, "product_name": "EOS R5"}])
        connected = service.connect()
        self.assertTrue(connected["connected"])
        self.assertEqual(connected["camera"]["firmware_version"], "2.2.1")
        self.assertTrue(connected["read_only"])
        disconnected = service.disconnect()
        self.assertFalse(disconnected["connected"])

    def test_sdk_product_prefix_is_accepted(self):
        service = CameraControlService()
        backend = service._new_backend()
        original_discover = backend.discover_cameras
        original_details = backend.read_camera_details
        backend.discover_cameras = lambda: [
            {**camera, "product_name": "Canon EOS R5"} for camera in original_discover()
        ]
        backend.read_camera_details = lambda: {
            **original_details(),
            "product_name": "Canon EOS R5",
        }
        backend.poll_product_name = lambda: "Canon EOS R5"
        service._new_backend = lambda: backend
        connected = service.connect()
        self.assertEqual(connected["camera"]["product_name"], "Canon EOS R5")

    def test_multiple_scenario_requires_index(self):
        service = CameraControlService(simulated_scenario="multiple")
        with self.assertRaises(CameraSelectionError) as caught:
            service.connect()
        self.assertEqual(len(caught.exception.cameras), 2)
        connected = service.connect(1)
        self.assertEqual(connected["camera"]["index"], 1)

    def test_wrong_model_is_rejected(self):
        service = CameraControlService(simulated_scenario="wrong_model")
        with self.assertRaises(WrongCameraModelError):
            service.connect()
        self.assertFalse(service.status()["connected"])

    def test_optional_properties_can_be_unavailable(self):
        service = CameraControlService(simulated_scenario="missing_properties")
        connected = service.connect()
        self.assertIsNone(connected["camera"]["body_id"])
        self.assertIsNone(connected["camera"]["firmware_version"])

    def test_simulated_disconnect_closes_session(self):
        service = CameraControlService()
        service.connect()
        result = service.simulate_disconnect()
        self.assertFalse(result["connected"])
        self.assertTrue(result["reconnect_available"])
        self.assertEqual(result["last_error"]["kind"], "camera_disconnected")

    def test_scenario_change_closes_existing_session(self):
        service = CameraControlService()
        service.connect()
        result = service.set_simulated_scenario("no_camera")
        self.assertFalse(result["connected"])
        self.assertEqual(result["simulated_scenario"], "no_camera")

    def test_capability_scan_is_read_only_and_classifies_writes_as_unverified(self):
        service = CameraControlService()
        service.connect()
        result = service.scan_capabilities()
        self.assertEqual(result["summary"]["total"], 22)
        self.assertEqual(result["summary"]["readable"], 20)
        self.assertEqual(result["summary"]["descriptors_available"], 22)
        self.assertTrue(result["read_only"])
        self.assertFalse(result["write_testing_performed"])
        self.assertTrue(all(not item["write_tested"] for item in result["properties"]))
        self.assertTrue(all(item["write_classification"] == "unverified" for item in result["properties"]))
        by_key = {item["key"]: item for item in result["properties"]}
        self.assertEqual(by_key["exposure_mode"]["value_display"], "M")
        self.assertEqual(by_key["image_quality"]["value_display"], "cRAW")
        self.assertEqual(by_key["af_method"]["value_display"], "Face + Tracking")
        self.assertEqual(by_key["subject_detection"]["read_status"], "unreadable")
        self.assertEqual(by_key["noise_reduction"]["read_status"], "unreadable")
        self.assertEqual(by_key["exposure_mode"]["profile_paths"], ["exposure.mode"])
        self.assertIn("autofocus.operation", result["coverage"]["sdk_readable_paths"])
        self.assertIn("autofocus.eye_detection", result["coverage"]["sdk_readable_paths"])
        self.assertIn("image.cropping_aspect_ratio", result["coverage"]["sdk_readable_paths"])
        self.assertIn("shutter.target", result["coverage"]["conditional_paths"])
        self.assertIn("autofocus.subject_detection", result["coverage"]["manual_or_unmapped_paths"])

    def test_capability_scan_requires_connection(self):
        service = CameraControlService()
        with self.assertRaises(CameraSessionError):
            service.scan_capabilities()

    def test_capability_scan_reconnects_once_after_session_failure(self):
        service = CameraControlService()
        service.connect()

        def fail_scan():
            raise RuntimeError("camera went to sleep")

        service.backend.read_capabilities = fail_scan
        service._new_backend = lambda: SimulatedBackend("ready")
        result = service.scan_capabilities()

        self.assertTrue(result["automatic_reconnect_performed"])
        self.assertTrue(service.status(check_connection=False)["connected"])
        self.assertEqual(result["summary"]["total"], 22)
        self.assertTrue(any(event["kind"] == "automatic_reconnect" for event in service.events))

    def test_capability_scan_failed_recovery_closes_session_and_gives_instructions(self):
        service = CameraControlService()
        service.connect()

        def fail_scan():
            raise RuntimeError("camera remains unavailable")

        service.backend.read_capabilities = fail_scan

        def broken_backend():
            backend = SimulatedBackend("ready")
            backend.read_capabilities = fail_scan
            return backend

        service._new_backend = broken_backend
        with self.assertRaisesRegex(CameraSessionError, "Wake or power-cycle"):
            service.scan_capabilities()

        status = service.status(check_connection=False)
        self.assertFalse(status["connected"])
        self.assertIsNone(status["capabilities"])
        self.assertEqual(status["last_error"]["kind"], "camera_session")

    def test_profile_catalog_excludes_permanent_reference_cards(self):
        service = CameraControlService()
        profiles = service.profiles()["profiles"]
        self.assertEqual(len(profiles), 12)
        names = [item["name"] for item in profiles]
        self.assertIn("Landscape", names)
        self.assertIn("Camera Defaults", names)
        self.assertNotIn("Camera Buttons", names)
        self.assertNotIn("My Menu", names)

    def test_profile_comparison_requires_a_capability_scan(self):
        service = CameraControlService()
        service.connect()
        with self.assertRaisesRegex(CameraSessionError, "scan capabilities"):
            service.compare_profile("Landscape")

    def test_profile_choices_name_the_registered_mode_and_base_card(self):
        profile_list = CameraControlService().profiles()["profiles"]
        profiles = {profile["name"]: profile for profile in profile_list}
        self.assertEqual([profile["name"] for profile in profile_list[:3]], ["Wildlife", "Birds in Flight", "Landscape"])
        self.assertEqual(profiles["Wildlife"]["display_title"], "C1 – Wildlife")
        self.assertEqual(profiles["Birds in Flight"]["display_title"], "C2 – Birds in Flight")
        self.assertEqual(profiles["Landscape"]["display_title"], "C3 – Landscape")
        self.assertEqual(profiles["People"]["display_title"], "C1 – Wildlife → People")
        self.assertEqual(profiles["Wildlife"]["selector_label"], "C1 (Wildlife)")
        self.assertEqual(profiles["Birds in Flight"]["selector_label"], "C2 (Birds in Flight)")
        self.assertEqual(profiles["Landscape"]["selector_label"], "C3 (Landscape)")
        self.assertEqual(profiles["Sports"]["selector_label"], "Sports ← C2 (Birds in Flight)")
        self.assertEqual(profiles["Camera Defaults"]["selector_label"], "Camera Defaults ← C1 (Wildlife)")
        remaining_titles = [profile["title"] for profile in profile_list[3:]]
        self.assertEqual(remaining_titles, sorted(remaining_titles, key=str.casefold))

    def test_profile_choices_reread_changed_saved_cx_foundations(self):
        with tempfile.TemporaryDirectory() as directory:
            profiles_dir = Path(directory)

            def save(name, title, slot, card_id, source_card_id):
                (profiles_dir / f"{name}.yaml").write_text(
                    "\n".join(
                        [
                            f"title: {title}",
                            f"card_id: {card_id}",
                            "card:",
                            "  field_setup:",
                            f"    start: {slot}",
                            f"    source_card_id: {source_card_id}",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )

            save("Macro", "Macro", "C1", "card-macro", "card-macro")
            save("Wildlife", "Wildlife", "C1", "card-wildlife", "card-macro")
            save("Birds in Flight", "Birds in Flight", "C2", "card-birds", "card-birds")
            save("Landscape", "Landscape", "C3", "card-landscape", "card-landscape")

            profile_list = list_profiles(SimpleNamespace(profiles_dir=profiles_dir))
            profiles = {profile["name"]: profile for profile in profile_list}

        self.assertEqual([profile["name"] for profile in profile_list[:3]], ["Macro", "Birds in Flight", "Landscape"])
        self.assertEqual(profiles["Macro"]["selector_label"], "C1 (Macro)")
        self.assertEqual(profiles["Wildlife"]["selector_label"], "Wildlife ← C1 (Macro)")

    def test_profile_comparison_follows_card_order_then_additional_settings(self):
        service = CameraControlService()
        service.connect()
        service.scan_capabilities()
        result = service.compare_profile("Landscape")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["write_testing_performed"])
        self.assertEqual(result["ordering"], "subject_profile_card_then_additional")
        self.assertEqual(
            [item["label"] for item in result["card_findings"][:8]],
            ["Mode", "Shutter", "Shutter Type", "Aperture", "ISO", "AF Operation", "AF Method", "Subject Detection"],
        )
        represented = {
            item["path"]
            for finding in result["card_findings"]
            for item in finding["items"]
        }
        additional = {item["path"] for item in result["additional_findings"]}
        self.assertTrue(represented.isdisjoint(additional))
        self.assertEqual(result["additional_findings"][0]["path"], "exposure.metering")
        by_path = {item["path"]: item for item in result["additional_findings"]}
        self.assertEqual(by_path["exposure.metering"]["status"], "match")
        self.assertEqual(by_path["image.white_balance"]["status"], "equivalent")
        mode = result["card_findings"][0]
        self.assertEqual(mode["access_paths"][0]["label"], "MODE button + Main Dial")
        af_method = next(item for item in result["card_findings"] if item["key"] == "autofocus.method")
        self.assertEqual(
            [route["kind"] for route in af_method["access_paths"]],
            ["direct", "menu"],
        )
        subject = next(item for item in result["card_findings"] if item["key"] == "autofocus.subject_detection")
        self.assertEqual(
            [route["kind"] for route in subject["access_paths"]],
            ["my_menu", "menu"],
        )
        self.assertEqual(subject["access_paths"][0]["label"], "My Menu → SWITCH")
        self.assertEqual(subject["access_paths"][0]["tab"], "SWITCH")
        self.assertEqual(subject["access_paths"][0]["tab_order"], 0)
        self.assertEqual(subject["access_paths"][0]["item_order"], 0)
        self.assertEqual(subject["expected_color"], subject["access_paths"][0]["color"])

        wildlife = service.compare_profile("Wildlife")
        servo_case = next(item for item in wildlife["card_findings"] if item["key"] == "autofocus.servo_af_case")
        af_case_route = next(route for route in servo_case["access_paths"] if route["kind"] == "my_menu")
        self.assertEqual(af_case_route["tab"], "AF Case")
        self.assertEqual(af_case_route["tab_order"], 1)

        focus_bracketing = by_path["image.focus_bracketing"]
        self.assertEqual(focus_bracketing["access_paths"][0]["label"], "My Menu → SWITCH")
        self.assertEqual(focus_bracketing["access_paths"][0]["item_order"], 2)
        for path in ("image.quality", "image.white_balance", "image.picture_style"):
            self.assertEqual(by_path[path]["access_paths"][0]["label"], "Q screen")
        self.assertEqual(by_path["stabilization.lens_is"]["access_paths"][0]["label"], "Lens IS switch")
        reference_note = by_path["image.long_exposure_noise_reduction.note"]
        self.assertEqual(reference_note["status"], "not_applicable")
        self.assertEqual(reference_note["access_paths"][0]["kind"], "reference")
        self.assertFalse(
            [
                finding["path"]
                for finding in result["additional_findings"]
                if not finding["access_paths"]
            ]
        )

    def test_profile_comparison_exposes_context_then_uses_selected_authored_target(self):
        service = CameraControlService()
        service.connect()
        service.scan_capabilities()

        people = service.compare_profile("People")
        shutter = next(item for item in people["card_findings"] if item["key"] == "shutter.target")
        aperture = next(item for item in people["card_findings"] if item["key"] == "lens.aperture.target")
        self.assertEqual(shutter["status"], "conditional")
        self.assertEqual(aperture["status"], "conditional")
        self.assertEqual(shutter["context_prompts"][0]["selected"], None)
        self.assertEqual(aperture["context_prompts"][0]["selected"], None)

        selected = service.compare_profile(
            "People",
            {"shutter.target": "portraits", "lens.aperture.target": "groups"},
        )
        selected_shutter = next(item for item in selected["card_findings"] if item["key"] == "shutter.target")
        selected_aperture = next(item for item in selected["card_findings"] if item["key"] == "lens.aperture.target")
        self.assertIn(selected_shutter["status"], {"match", "equivalent", "difference"})
        self.assertIn(selected_aperture["status"], {"match", "equivalent", "difference"})
        self.assertEqual(selected_shutter["context_prompts"][0]["selected_target"], "1/200–1/320")
        self.assertEqual(selected_aperture["context_prompts"][0]["selected_target"], "f/4–f/8")

    def test_every_comparison_finding_has_a_reviewed_access_route(self):
        service = CameraControlService()
        service.connect()
        service.scan_capabilities()
        missing = []
        for profile in service.profiles()["profiles"]:
            comparison = service.compare_profile(profile["name"])
            for section in ("card_findings", "additional_findings"):
                missing.extend(
                    (profile["name"], finding.get("path") or finding.get("key"))
                    for finding in comparison[section]
                    if not finding["access_paths"]
                )
        self.assertEqual(missing, [])


class CameraLabHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = "test-camera-lab-token"
        cls.service = CameraControlService()
        cls.server = create_server(cls.service, port=0, token=cls.token)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.service.close()
        cls.thread.join(timeout=2)

    def request(self, method, path, payload=None, token=None, host="127.0.0.1"):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=2)
        headers = {"Host": host, "Accept": "application/json"}
        body = None
        if payload is not None:
            body = json.dumps(payload)
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["X-Camera-Lab-Token"] = token
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        content_type = response.getheader("Content-Type", "")
        connection.close()
        if "application/json" in content_type:
            data = json.loads(raw)
        elif content_type.startswith("text/") or "javascript" in content_type:
            data = raw.decode("utf-8")
        else:
            data = raw
        return response.status, response.getheaders(), data

    def setUp(self):
        self.service.set_simulated_scenario("ready")

    def test_index_injects_request_token_and_security_headers(self):
        status, headers, body = self.request("GET", "/")
        header_map = dict(headers)
        self.assertEqual(status, 200)
        self.assertIn(self.token, body)
        self.assertNotIn("__CAMERA_LAB_TOKEN__", body)
        self.assertEqual(header_map["Cache-Control"], "no-store")
        self.assertIn("default-src 'self'", header_map["Content-Security-Policy"])
        self.assertIn('id="recovery-dialog"', body)
        self.assertIn('id="camera-lab-version"', body)
        self.assertIn('id="camera-lab-source-hash"', body)
        self.assertIn('id="stop-camera-lab-button"', body)
        self.assertIn('id="backend-switch-button"', body)
        self.assertIn('id="backend-switch-dialog"', body)
        self.assertIn('id="backend-switch-confirm"', body)
        self.assertIn("Camera Lab remains read-only", body)
        self.assertIn('id="comparison-order"', body)
        self.assertIn('<option value="setup" selected>Setup route</option>', body)
        self.assertIn('id="checklist-rescan-button"', body)
        self.assertIn('id="checklist-clear-button"', body)
        self.assertIn('id="checklist-sdk-count"', body)
        self.assertIn('id="checklist-manual-count"', body)
        self.assertIn('id="checklist-unresolved-count"', body)
        self.assertIn('id="checklist-blocked-count"', body)
        self.assertIn("Manual confirmations are saved only in this browser", body)
        self.assertLess(body.index('id="comparison-panel"'), body.index('id="capability-panel"'))
        self.assertIn('id="additional-finding-section"', body)
        self.assertIn('id="return-to-top"', body)
        self.assertIn("Scan &amp; compare", body)
        self.assertIn('id="cx-setup-panel"', body)
        self.assertIn('id="cx-slot-cards"', body)
        self.assertIn("C1–C3 Maintenance &amp; Validation", body)
        self.assertIn("Maintenance &amp; reverification", body)
        self.assertIn("verified in physical session 3", body)
        self.assertIn('<details class="build-badge header-version">', body)
        self.assertIn('<details id="cx-setup-panel" class="panel collapsible-panel cx-setup-panel">', body)
        self.assertIn('<details id="capability-panel" class="panel collapsible-panel capability-panel" hidden>', body)
        self.assertIn('class="collapse-state"', body)
        self.assertNotIn("Phase 1 guided registration", body)
        self.assertNotIn("Phase 1 read-only comparison", body)
        self.assertIn("Read-only discovery reference", body)
        self.assertIn('aria-label="Return to Compare a Subject/Profile Card"', body)
        self.assertLess(body.index('id="backend-badge"'), body.index('id="backend-switch-button"'))
        self.assertLess(body.index('id="backend-switch-button"'), body.index('id="stop-camera-lab-button"'))
        self.assertLess(body.index("No setting writes"), body.index('id="project-context-badge"'))
        self.assertLess(body.index('id="project-context-badge"'), body.index('id="camera-lab-version"'))
        self.assertLess(body.index('id="cx-setup-panel"'), body.index('id="comparison-panel"'))

        status, _, styles = self.request("GET", "/styles.css")
        self.assertEqual(status, 200)
        self.assertIn("grid-template-columns: auto 52px", styles)
        self.assertIn("grid-template-rows: auto auto auto", styles)
        self.assertIn("grid-row: 1 / span 3", styles)
        self.assertIn(".header-tools .header-meta { grid-column: 1; grid-row: 2; }", styles)
        self.assertIn(".header-tools .header-version { grid-column: 1; grid-row: 3; justify-self: end; }", styles)
        self.assertIn(".collapse-state::before", styles)

    def test_camera_lab_script_rescans_comparison_and_exposes_recovery(self):
        status, _, html = self.request("GET", "/")
        self.assertEqual(status, 200)
        status, _, body = self.request("GET", "/app.js")
        self.assertEqual(status, 200)
        self.assertIn("await compareSelectedProfile({ recordScan: true })", body)
        self.assertIn("showRecoveryInstructions(error.message)", body)
        self.assertIn('elements.compareButton.addEventListener("click", () => runAction(scanAndCompare))', body)
        self.assertIn("function manualGroup(finding)", body)
        self.assertIn("function setupGroup(finding)", body)
        self.assertIn('const checklistStorageKey = "camera-lab-phase1-checklist-v1"', body)
        self.assertIn('evidence_method: "manual_user_confirmed"', body)
        self.assertIn('"Saved as manual_user_confirmed"', body)
        self.assertIn('reason.className = "checklist-reason"', body)
        self.assertIn("function renderChecklistSummary()", body)
        self.assertIn("function checklistFindingKey(finding)", body)
        self.assertIn("function renderCxSetup(profiles)", body)
        self.assertIn("profile.is_foundation", body)
        self.assertIn("button.dataset.cxProfile = profile.name", body)
        self.assertIn("function openCxChecklist(profileName)", body)
        self.assertIn('elements.checklistRescanButton.addEventListener("click", () => runAction(scanAndCompare))', body)
        self.assertIn("window.localStorage.setItem(checklistStorageKey", body)
        self.assertIn('elements.comparisonOrder.value === "setup"', body)
        self.assertIn("contextSelections", body)
        self.assertIn("Choose context before evaluating", body)
        self.assertIn('query.append("context"', body)
        self.assertIn("function updateFloatingReturn()", body)
        self.assertIn('elements.comparisonPanel.scrollIntoView({ behavior: "smooth", block: "start" })', body)
        self.assertIn("session-3 camera-body registration was verified", body)
        self.assertNotIn("window.scrollTo({ top: 0", body)
        self.assertIn("profile.display_title || profile.title", body)
        self.assertIn("profile.selector_label || profile.display_title || profile.title", body)
        self.assertIn('request("/api/camera-control/shutdown", { method: "POST", body: "{}" })', body)
        self.assertIn("function showBackendSwitchConfirmation()", body)
        self.assertIn("elements.backendSwitchDialog.showModal()", body)
        self.assertIn('request("/api/camera-control/restart-backend"', body)
        self.assertIn("elements.backendSwitchConfirm.addEventListener", body)
        self.assertLess(
            body.index("elements.backendSwitchDialog.showModal()"),
            body.index('request("/api/camera-control/restart-backend"'),
        )
        self.assertIn("function renderStoppedState()", body)
        self.assertIn("cameraLabStopped = true", body)
        self.assertIn("window.clearInterval(statusPollId)", body)
        self.assertIn("if (cameraLabStopped || requestPending) return", body)
        self.assertIn("statusPollId = window.setInterval", body)
        self.assertIn('id="project-context-badge"', html)
        self.assertIn("app.project_context", body)
        self.assertIn('new URLSearchParams(window.location.search).get("profile")', body)
        self.assertIn("was selected by Profile Editor", body)
        self.assertIn("not available in Camera Lab", body)

    def test_camera_lab_serves_canonical_silver_logo(self):
        status, headers, body = self.request("GET", "/silver-camera-logo.png")
        self.assertEqual(status, 200)
        self.assertEqual(dict(headers)["Content-Type"], "image/png")
        self.assertEqual(body[:8], b"\x89PNG\r\n\x1a\n")

    def test_post_requires_request_token(self):
        status, _, body = self.request("POST", "/api/camera-control/connect", {})
        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["kind"], "invalid_token")

    def test_backend_restart_requires_token_and_records_confirmed_target(self):
        status, _, body = self.request(
            "POST",
            "/api/camera-control/restart-backend",
            {"backend": "edsdk"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["kind"], "invalid_token")

        original_shutdown = self.server.shutdown
        shutdown_requested = threading.Event()
        with tempfile.TemporaryDirectory(prefix="camera-lab-sdk-test-") as sdk_path:
            self.server.restart_sdk_path = Path(sdk_path)
            self.server.shutdown = shutdown_requested.set
            try:
                status, _, body = self.request(
                    "POST",
                    "/api/camera-control/restart-backend",
                    {"backend": "edsdk"},
                    token=self.token,
                )
                self.assertEqual(status, 200)
                self.assertTrue(body["restarting"])
                self.assertTrue(body["camera_session_closed"])
                self.assertEqual(body["backend"], "edsdk")
                self.assertTrue(shutdown_requested.wait(timeout=1))
                self.assertEqual(self.server.restart_backend, "edsdk")
            finally:
                self.server.shutdown = original_shutdown
                self.server.restart_backend = None
                self.server.restart_sdk_path = None

    def test_backend_restart_rejects_current_mode_without_shutdown(self):
        status, _, body = self.request(
            "POST",
            "/api/camera-control/restart-backend",
            {"backend": "simulated"},
            token=self.token,
        )
        self.assertEqual(status, 400)
        self.assertIn("already running in simulated mode", body["error"]["message"])
        self.assertIsNone(self.server.restart_backend)

    def test_connect_and_status_api(self):
        status, _, body = self.request(
            "POST",
            "/api/camera-control/connect",
            {},
            token=self.token,
        )
        self.assertEqual(status, 200)
        self.assertTrue(body["connected"])
        status, _, body = self.request("GET", "/api/camera-control/status")
        self.assertEqual(status, 200)
        self.assertEqual(body["camera"]["product_name"], "EOS R5")
        self.assertEqual(body["app"]["version"], "0.42.6")
        self.assertRegex(body["app"]["build"], r"^[0-9a-f]{8}$")

    def test_capability_api_returns_read_only_inventory(self):
        status, _, _ = self.request(
            "POST",
            "/api/camera-control/connect",
            {},
            token=self.token,
        )
        self.assertEqual(status, 200)
        status, _, body = self.request("GET", "/api/camera-control/capabilities")
        self.assertEqual(status, 200)
        self.assertEqual(body["summary"]["total"], 22)
        self.assertFalse(body["write_testing_performed"])
        self.assertIn("coverage", body)

    def test_profile_comparison_api_is_read_only_and_card_ordered(self):
        status, _, body = self.request("GET", "/api/camera-control/profiles")
        self.assertEqual(status, 200)
        self.assertIn("Landscape", [item["name"] for item in body["profiles"]])
        status, _, _ = self.request(
            "POST",
            "/api/camera-control/connect",
            {},
            token=self.token,
        )
        self.assertEqual(status, 200)
        status, _, _ = self.request("GET", "/api/camera-control/capabilities")
        self.assertEqual(status, 200)
        status, _, body = self.request("GET", "/api/camera-control/comparison?profile=Landscape")
        self.assertEqual(status, 200)
        self.assertTrue(body["read_only"])
        self.assertEqual(body["ordering"], "subject_profile_card_then_additional")
        self.assertEqual(body["card_findings"][0]["label"], "Mode")

        status, _, body = self.request(
            "GET",
            "/api/camera-control/comparison?profile=People&context=shutter.target%7Cportraits&context=lens.aperture.target%7Cgroups",
        )
        self.assertEqual(status, 200)
        shutter = next(item for item in body["card_findings"] if item["key"] == "shutter.target")
        aperture = next(item for item in body["card_findings"] if item["key"] == "lens.aperture.target")
        self.assertEqual(shutter["context_prompts"][0]["selected"], "portraits")
        self.assertEqual(aperture["context_prompts"][0]["selected"], "groups")
        self.assertTrue(body["read_only"])

    def test_non_loopback_host_is_rejected(self):
        status, _, body = self.request("GET", "/api/camera-control/status", host="camera-lab.example")
        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["kind"], "invalid_host")

    def test_authenticated_shutdown_closes_service_and_stops_server(self):
        token = "shutdown-test-token"
        service = CameraControlService()
        server = create_server(service, port=0, token=token)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            service.connect()
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            connection.request(
                "POST",
                "/api/camera-control/shutdown",
                body="{}",
                headers={
                    "Host": "127.0.0.1",
                    "Content-Type": "application/json",
                    "X-Camera-Lab-Token": token,
                },
            )
            response = connection.getresponse()
            payload = json.loads(response.read())
            connection.close()
            self.assertEqual(response.status, 200)
            self.assertTrue(payload["shutting_down"])
            self.assertTrue(payload["camera_session_closed"])
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.assertFalse(service.status(check_connection=False)["connected"])
        finally:
            server.server_close()
            service.close()


if __name__ == "__main__":
    unittest.main()
