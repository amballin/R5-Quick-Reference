"""Static safety boundaries for simulated and explicitly gated EOS R5 writes."""

import ast
import re

import yaml

from .common import error


REQUIRED_SCENARIOS = {
    "guarded_success",
    "guarded_readback_mismatch",
    "guarded_unsupported_value",
    "guarded_missing_prerequisite",
    "guarded_busy",
    "guarded_disconnect",
    "guarded_identity_change",
}


def validate(root):
    issues = []
    paths = {
        "guarded": root / "80 Build/camera_control/guarded_run.py",
        "journal": root / "80 Build/camera_control/session_journal.py",
        "manual_confirmations": root / "80 Build/camera_control/manual_confirmation_ledger.py",
        "simulator": root / "80 Build/camera_control/simulated_backend.py",
        "server": root / "80 Build/camera_control/dev_server.py",
        "native": root / "80 Build/camera_control/native_backend.py",
        "ctypes": root / "80 Build/camera_control/edsdk_backend.py",
        "helper": root / "80 Build/camera_control/native/edsdk_helper.c",
        "policy": root / "80 Build/camera_control/physical_write_policy.py",
        "qualification": root / "80 Build/camera_control/write_qualification.py",
        "catalog": root / "00 Master/camera_capabilities.yaml",
        "ui": root / "80 Build/camera_control/static/app.js",
        "html": root / "80 Build/camera_control/static/index.html",
        "comparison": root / "80 Build/camera_control/profile_comparison.py",
        "editor_options": root / "80 Build/profile_editor/canon_options.yaml",
    }
    if any(not path.is_file() for path in paths.values()):
        return [
            error("camera_guarded_run", path, "Required guarded-run safety source is missing.")
            for path in paths.values()
            if not path.is_file()
        ]

    guarded = paths["guarded"].read_text(encoding="utf-8")
    simulator = paths["simulator"].read_text(encoding="utf-8")
    server = paths["server"].read_text(encoding="utf-8")
    journal = paths["journal"].read_text(encoding="utf-8")
    manual_confirmations = paths["manual_confirmations"].read_text(encoding="utf-8")
    helper = paths["helper"].read_text(encoding="utf-8")
    policy = paths["policy"].read_text(encoding="utf-8")
    qualification = paths["qualification"].read_text(encoding="utf-8")
    catalog = paths["catalog"].read_text(encoding="utf-8")
    ui = paths["ui"].read_text(encoding="utf-8")
    html = paths["html"].read_text(encoding="utf-8")
    comparison = paths["comparison"].read_text(encoding="utf-8")
    editor_options = paths["editor_options"].read_text(encoding="utf-8")

    for scenario in sorted(REQUIRED_SCENARIOS):
        if f'"{scenario}"' not in simulator:
            issues.append(error("camera_guarded_run", paths["simulator"], f"Missing deterministic scenario: {scenario}"))
    for phrase in (
        'self.service.backend_mode == "simulated"',
        "self.service.physical_write_enabled",
        "isinstance(self.service.backend, SimulatedBackend)",
        "write_guarded_setting",
        "read_guarded_setting",
        "_process_simulator_automatic_steps",
        "_complete_manual_group",
        "_recheck_already_correct",
        '"operator_actions"',
    ):
        if phrase not in guarded:
            issues.append(error("camera_guarded_run", paths["guarded"], f"Simulator guard is incomplete: {phrase}"))
    if 'path.startswith("/api/camera-control/guarded-run/") and not self._guarded_endpoint_available()' not in server:
        issues.append(error("camera_guarded_run", paths["server"], "EDSDK mode must return not-found for guarded-run POST routes."))
    if 'path == "/api/camera-control/guarded-run" and self._guarded_endpoint_available()' not in server:
        issues.append(error("camera_guarded_run", paths["server"], "Guarded-run journal reads must be simulator-gated."))
    if '"Camera Lab" / "Guarded Runs"' not in journal:
        issues.append(error("camera_guarded_run", paths["journal"], "Session journals must use the machine-local Camera Lab/Guarded Runs folder."))
    for required in (
        '"Manual Confirmations.json"',
        '"camera_session_id"',
        '"target_normalized"',
        '"firmware_version"',
        '"lens_name"',
        '"current_mode"',
    ):
        if required not in manual_confirmations:
            issues.append(error("camera_guarded_run", paths["manual_confirmations"], f"Shared manual-confirmation scope is missing: {required}"))

    for key in ("ctypes",):
        tree = ast.parse(paths[key].read_text(encoding="utf-8"), filename=str(paths[key]))
        prohibited = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and ("write_guarded" in node.name or "write_physical" in node.name or "set_camera_setting" in node.name)
        ]
        if prohibited:
            issues.append(error("camera_guarded_run", paths[key], f"Real-camera backend exposes guarded mutation methods: {prohibited}"))

    native_tree = ast.parse(paths["native"].read_text(encoding="utf-8"), filename=str(paths["native"]))
    native_writes = [
        node.name for node in ast.walk(native_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and "write" in node.name
    ]
    if native_writes != ["write_physical_setting"]:
        issues.append(error("camera_guarded_run", paths["native"], f"Unexpected native write surface: {native_writes}"))
    if helper.count("EdsSetPropertyData(") != 2:
        issues.append(error("camera_guarded_run", paths["helper"], "Native helper must contain only activation and one guarded setting-write call."))
    for required in (
        "activate_limited_properties",
        "write_qualified_candidate",
        "is_write_qualification_candidate",
        "WriteValueNotInDescriptor",
        'strncmp(command, "WRITE ", 6)',
    ):
        if required not in helper:
            issues.append(error("camera_guarded_run", paths["helper"], f"Physical write guard is missing: {required}"))
    if "EdsSetCsdFileData" in helper or 'strcmp(command, "SET' in helper:
        issues.append(error("camera_guarded_run", paths["helper"], "Native helper must expose no CSD or generic setting mutation command."))
    catalog_payload = yaml.safe_load(catalog) or {}
    tracked_candidates = {
        item.get("key")
        for item in catalog_payload.get("properties") or []
        if item.get("write_qualification_candidate") is True
    }
    candidate_block = re.search(r"CANDIDATES\[\]\s*=\s*\{(?P<body>.*?)\};", helper, re.DOTALL)
    compiled_candidates = set(re.findall(r'"([a-z0-9_]+)"', candidate_block.group("body"))) if candidate_block else set()
    if tracked_candidates != compiled_candidates:
        issues.append(
            error(
                "camera_guarded_run",
                paths["helper"],
                f"Tracked and compiled physical-write allowlists differ: tracked={sorted(tracked_candidates)}, compiled={sorted(compiled_candidates)}",
            )
        )
    for required in (
        "--enable-physical-writes",
        "physical_write_enabled",
        "sdk_written_and_verified",
        '"Physical Write Evidence.json"',
    ):
        source = server + guarded + policy + qualification + catalog
        if required not in source:
            issues.append(error("camera_guarded_run", paths["policy"], f"Phase 2B safety contract is missing: {required}"))
    for required in (
        'id="physical-write-mode-button"',
        'id="physical-write-mode-dialog"',
        'id="physical-write-mode-confirm"',
    ):
        if required not in html:
            issues.append(error("camera_guarded_run", paths["html"], f"Guarded-write mode control is missing: {required}"))
    for required in (
        "Apply this profile to camera",
        "Review what will change",
        "Advanced setup — safely enable additional automatic settings",
        'id="apply-result"',
        'id="guarded-plan-details"',
        'id="guarded-active-workspace"',
        'id="guarded-step-settings"',
    ):
        if required not in html:
            issues.append(error("camera_guarded_run", paths["html"], f"User-facing profile application flow is missing: {required}"))
    for required in (
        "showPhysicalWriteModeConfirmation",
        "restartWithPhysicalWriteMode",
        "physical_write_enabled: physicalWriteEnabled",
        'body: JSON.stringify({ backend, physical_write_enabled: false })',
        "renderApplyResult",
        'title = "Profile applied successfully"',
        '"Stopped — profile not fully applied"',
        "Do not treat this profile as complete",
        "guardedStepInstruction",
        "elements.guardedPlanDetails.hidden = processingOneStep",
        "persistGuardedPreflight",
        "window.sessionStorage.setItem",
        "manual_group_label",
        "I changed these settings — rescan once",
        "sharedManualContext",
        "shared_manual_confirmation",
        'request("/api/camera-control/manual-confirmations/revoke"',
    ):
        if required not in ui:
            issues.append(error("camera_guarded_run", paths["ui"], f"Explicit write-mode restart guard is missing: {required}"))
    if "kEdsPropID_LensName" not in helper or '"lens_name"' not in paths["native"].read_text(encoding="utf-8"):
        issues.append(error("camera_guarded_run", paths["helper"], "Connected-lens readback must be retained for guarded preflight."))
    for label in ("Initial priority (0)", "On subject (1)", "Switch subject (2)"):
        if label not in comparison or label not in editor_options:
            issues.append(error("camera_guarded_run", paths["comparison"], f"Numbered Switching tracked subjects label is missing: {label}"))
    return issues
