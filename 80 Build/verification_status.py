#!/usr/bin/env python3
"""Synchronize the local Setup workbook with the Git-tracked verification status."""

import argparse
from copy import deepcopy
from datetime import date, datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import yaml

from asset_manager import ProjectPaths
from spreadsheet_revisions import (
    source_fingerprint,
    tracker_definition_fingerprints,
    workbook_revision,
)
from camera_setup_tracker import effective_registration_definition_fingerprints
from validators.common import load_yaml_checked


STATUS_VERSION = 1
WORKING_MARKER_VERSION = 2
WORKING_COPY_CURRENT = 0
WORKING_COPY_PENDING = 1
WORKING_COPY_STALE = 2
WORKING_COPY_CONFLICT = 3
NEEDS_RETEST = "Inconclusive—needs retest"
MUTABLE_CHECKLIST_FIELDS = (
    "status",
    "test_date",
    "session_id",
    "evidence_files",
    "observation",
    "next_action",
    "evidence_class",
    "updated_in_project",
)
DEFAULT_NODE = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
DEFAULT_NODE_MODULES = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
NUMBERS_BUNDLE_IDS = ("com.apple.Numbers", "com.apple.iWork.Numbers")


class VerificationStatusError(RuntimeError):
    """Raised when verification status cannot be synchronized safely."""


def empty_status():
    return {
        "version": STATUS_VERSION,
        "updated": None,
        "tests": {},
        "registration": {},
        "sessions": [],
        "retired_tests": {},
        "history": [],
    }


def load_status(paths):
    path = paths.verification_status_file
    if not path.is_file():
        raise VerificationStatusError(f"Verification status file is missing: {path}")
    data = load_yaml_checked(path) or {}
    if data.get("version") != STATUS_VERSION:
        raise VerificationStatusError(f"Unsupported verification status version: {path}")
    expected = empty_status()
    for key, default in expected.items():
        data.setdefault(key, deepcopy(default))
    if not isinstance(data["tests"], dict) or not isinstance(data["registration"], dict):
        raise VerificationStatusError("Verification tests and registration status must be mappings.")
    if not isinstance(data["sessions"], list) or not isinstance(data["history"], list):
        raise VerificationStatusError("Verification sessions and history must be lists.")
    return data


def reconcile_status(paths, write=True):
    source = load_yaml_checked(paths.verification_tracker_source_file) or {}
    status = load_status(paths)
    original = deepcopy(status)
    now = datetime.now().astimezone().isoformat()
    test_fingerprints = tracker_definition_fingerprints(source)
    defaults = (load_yaml_checked(paths.baseline_file) or {}).get("defaults") or {}
    registration_fingerprints = effective_registration_definition_fingerprints(source, defaults)

    for test_id in list(status["tests"]):
        state = status["tests"][test_id]
        current = test_fingerprints.get(test_id)
        if current is None:
            status["retired_tests"][test_id] = {
                "retired": now,
                "reason": "Test definition was removed.",
                "state": state,
            }
            _record_history(status, "test_retired", test_id, state, None, now)
            del status["tests"][test_id]
            continue
        verified_against = state.get("verified_against")
        if state.get("status") == "Verified" and verified_against != current:
            previous = deepcopy(state)
            state["status"] = NEEDS_RETEST
            state["current_definition"] = current
            state["retest_reason"] = "The test definition changed after this result was recorded."
            _record_history(status, "definition_changed", test_id, previous, state, now)

    for setting, state in status["registration"].items():
        current = registration_fingerprints.get(setting)
        if current is None:
            continue
        recorded = state.get("verified_against")
        passed = any(
            state.get(key) == "Pass"
            for key in (
                "c1_configured",
                "c1_read_back",
                "c2_configured",
                "c2_read_back",
                "c3_configured",
                "c3_read_back",
            )
        )
        if passed and recorded != current:
            previous = deepcopy(state)
            changed = False
            for key in ("c1_configured", "c1_read_back", "c2_configured", "c2_read_back", "c3_configured", "c3_read_back"):
                if state.get(key) == "Pass":
                    state[key] = "Needs retest"
                    changed = True
            if changed:
                state["current_definition"] = current
                state["retest_reason"] = "A C1-C3 target changed after this result was recorded."
                _record_history(status, "registration_definition_changed", setting, previous, state, now)

    changed = status != original
    if changed:
        status["updated"] = now
        if write:
            write_status(paths, status)
    return status, changed


def import_workbook_status(paths, source_path=None):
    selected_source, extraction_source, temporary = _select_import_source(paths, source_path)
    try:
        extracted = _extract_workbook(paths, extraction_source)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

    definition = load_yaml_checked(paths.verification_tracker_source_file) or {}
    valid_statuses = set((definition.get("lists") or {}).get("main_status") or [])
    valid_evidence = set((definition.get("lists") or {}).get("evidence_class") or [])
    current_tests = tracker_definition_fingerprints(definition)
    defaults = (load_yaml_checked(paths.baseline_file) or {}).get("defaults") or {}
    current_registration = effective_registration_definition_fingerprints(definition, defaults)
    workbook_tests = ((extracted.get("metadata") or {}).get("tests") or {})
    workbook_registration = ((extracted.get("metadata") or {}).get("registration") or {})
    test_definitions = {
        str(test.get("test_id")): test
        for test in definition.get("tests") or []
        if test.get("test_id")
    }
    status = load_status(paths)
    now = datetime.now().astimezone().isoformat()

    imported_ids = set()
    for row in extracted.get("checklist") or []:
        test_id = str(row.get("test_id") or "").strip()
        if not test_id:
            continue
        imported_ids.add(test_id)
        if test_id not in current_tests:
            status["retired_tests"][test_id] = {
                "retired": now,
                "reason": "Workbook row no longer exists in the current test definition.",
                "state": _clean_test_state(row),
            }
            continue
        state = _clean_test_state(row)
        if state["status"] not in valid_statuses:
            raise VerificationStatusError(f"{test_id} has unsupported Status: {state['status']}")
        if state.get("evidence_class") and state["evidence_class"] not in valid_evidence:
            raise VerificationStatusError(
                f"{test_id} has unsupported Evidence Class: {state['evidence_class']}"
            )
        workbook_fingerprint = workbook_tests.get(test_id)
        current_fingerprint = current_tests[test_id]
        if state["status"] == "Verified":
            state["verified_against"] = workbook_fingerprint
            if workbook_fingerprint != current_fingerprint:
                state["status"] = NEEDS_RETEST
                state["current_definition"] = current_fingerprint
                state["retest_reason"] = (
                    "The workbook test definition is older than the current project definition."
                )
        previous = status["tests"].get(test_id)
        default_state = _default_test_state(test_definitions[test_id])
        if state == default_state:
            if previous is not None:
                _record_history(status, "spreadsheet_reset", test_id, previous, None, now)
            status["tests"].pop(test_id, None)
        else:
            if previous != state:
                _record_history(status, "spreadsheet_import", test_id, previous, state, now)
            status["tests"][test_id] = state

    for setting, row in (extracted.get("registration") or {}).items():
        if setting not in current_registration:
            continue
        state = {key: _scalar(value) for key, value in row.items()}
        workbook_fingerprint = workbook_registration.get(setting)
        current_fingerprint = current_registration[setting]
        passed = any(
            state.get(key) == "Pass"
            for key in ("c1_configured", "c1_read_back", "c2_configured", "c2_read_back", "c3_configured", "c3_read_back")
        )
        if passed:
            state["verified_against"] = workbook_fingerprint
        if passed and workbook_fingerprint != current_fingerprint:
            for key in ("c1_configured", "c1_read_back", "c2_configured", "c2_read_back", "c3_configured", "c3_read_back"):
                if state.get(key) == "Pass":
                    state[key] = "Needs retest"
            state["current_definition"] = current_fingerprint
            state["retest_reason"] = "The workbook C1-C3 target is older than the current project target."
        previous = status["registration"].get(setting)
        if state == _default_registration_state():
            if previous is not None:
                _record_history(status, "registration_reset", setting, previous, None, now)
            status["registration"].pop(setting, None)
        else:
            if previous != state:
                _record_history(status, "registration_import", setting, previous, state, now)
            status["registration"][setting] = state

    status["sessions"] = [
        {key: _scalar(value) for key, value in row.items()}
        for row in extracted.get("sessions") or []
        if any(_scalar(value) not in ("", None) for value in row.values())
    ]
    status["updated"] = now
    write_status(paths, status)
    mark_working_synced(paths, extracted.get("metadata") or {})
    print(f"Verification status imported from: {selected_source}")
    print(f"Git-tracked status updated: {paths.verification_status_file}")
    return status


def build_working_copy(paths):
    from camera_setup_tracker import generate_camera_setup_tracker
    from spreadsheet_downloads import convert_numbers_automatically, finalize_numbers_conversion

    state, message = working_copy_state(paths)
    if state in (WORKING_COPY_PENDING, WORKING_COPY_CONFLICT):
        raise VerificationStatusError(
            message + " Import the existing tracker before rebuilding it."
        )
    status, changed = reconcile_status(paths, write=True)
    paths.verification_working_dir.mkdir(parents=True, exist_ok=True)
    generate_camera_setup_tracker(
        paths,
        output_path=paths.setup_tracker_working_file,
        status_data=status,
    )
    convert_numbers_automatically(
        paths,
        "setup",
        xlsx_path=paths.setup_tracker_working_file,
        numbers_path=paths.setup_tracker_working_numbers_file,
    )
    finalize_numbers_conversion(
        paths,
        "setup",
        numbers_path=paths.setup_tracker_working_numbers_file,
    )
    mark_working_synced(paths)
    if changed:
        print("Changed definitions were marked for retest in the tracked status.")
    print(f"Verification working copy generated: {paths.setup_tracker_working_numbers_file}")


def working_copy_state(paths):
    files = [
        path
        for path in (paths.setup_tracker_working_file, paths.setup_tracker_working_numbers_file)
        if path.exists()
    ]
    if not files:
        return WORKING_COPY_CURRENT, "No local verification working copy exists."
    marker_path = paths.verification_import_marker_file
    if not marker_path.is_file():
        return (
            WORKING_COPY_CONFLICT,
            "The verification working copy has no synchronization marker. Import it before rebuilding or opening it.",
        )
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return (
            WORKING_COPY_CONFLICT,
            "The verification import marker is unreadable. Import the working tracker before rebuilding it.",
        )

    changed_files = []
    for path in files:
        recorded = (marker.get("files") or {}).get(path.name)
        if recorded != _sha256(path):
            changed_files.append(path.name)

    current_source = source_fingerprint(paths, "setup")
    current_revision = workbook_revision(paths, "setup")
    recorded_source = marker.get("source_fingerprint")
    try:
        recorded_revision = int(marker.get("workbook_revision"))
    except (TypeError, ValueError):
        recorded_revision = None
    definitions_changed = (
        recorded_source != current_source
        or recorded_revision != current_revision
    )
    recorded_status = marker.get("status_sha256")
    status_changed = (
        not paths.verification_status_file.is_file()
        or recorded_status != _sha256(paths.verification_status_file)
    )

    if changed_files and (definitions_changed or status_changed):
        reasons = []
        if definitions_changed:
            reasons.append("project definitions changed")
        if status_changed:
            reasons.append("canonical YAML status changed")
        return (
            WORKING_COPY_CONFLICT,
            "Verification workbook has unimported edits and "
            + " and ".join(reasons)
            + ". Import it before rebuilding; the importer will preserve evidence and mark changed definitions for retest.",
        )
    if changed_files:
        return (
            WORKING_COPY_PENDING,
            "Verification workbook changed after the last YAML synchronization: "
            + ", ".join(changed_files),
        )
    if definitions_changed or status_changed:
        reasons = []
        if definitions_changed:
            reasons.append("its embedded project definitions are stale")
        if status_changed:
            reasons.append("canonical YAML status changed")
        return (
            WORKING_COPY_STALE,
            "Verification working copy is safely rebuildable because "
            + " and ".join(reasons)
            + " and it has no unimported edits.",
        )
    return WORKING_COPY_CURRENT, "Verification working copy matches current definitions and YAML status."


def working_copy_pending(paths):
    state, message = working_copy_state(paths)
    return state != WORKING_COPY_CURRENT, message


def mark_working_synced(paths, workbook_metadata=None):
    paths.verification_working_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for path in (paths.setup_tracker_working_file, paths.setup_tracker_working_numbers_file):
        if path.exists():
            files[path.name] = _sha256(path)
    metadata = workbook_metadata or {}
    payload = {
        "version": WORKING_MARKER_VERSION,
        "synchronized": datetime.now().astimezone().isoformat(),
        "status_sha256": _sha256(paths.verification_status_file),
        "workbook_revision": metadata.get("workbook_revision") or workbook_revision(paths, "setup"),
        "source_fingerprint": metadata.get("source_fingerprint") or source_fingerprint(paths, "setup"),
        "files": files,
    }
    paths.verification_import_marker_file.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def write_status(paths, status):
    path = paths.verification_status_file
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(
        status,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as temporary:
        temporary.write(text)
        temporary.flush()
        temp_path = Path(temporary.name)
    temp_path.replace(path)


def _clean_test_state(row):
    state = {
        key: _scalar(row.get(key))
        for key in MUTABLE_CHECKLIST_FIELDS
    }
    state["status"] = state.get("status") or "Not started"
    state["evidence_files"] = _evidence_list(state.get("evidence_files"))
    return state


def _default_test_state(test):
    return {
        "status": test.get("status") or "Not started",
        "test_date": "",
        "session_id": "",
        "evidence_files": [],
        "observation": test.get("observation") or "",
        "next_action": test.get("next_action") or "",
        "evidence_class": test.get("evidence_class") or "Approved target pending verification",
        "updated_in_project": "Not applicable" if test.get("project_update", "No") == "No" else "No",
    }


def _default_registration_state():
    return {
        "c1_configured": "Not started",
        "c1_read_back": "Not started",
        "c1_notes": "",
        "c2_configured": "Not started",
        "c2_read_back": "Not started",
        "c2_notes": "",
        "c3_configured": "Not started",
        "c3_read_back": "Not started",
        "c3_notes": "",
    }


def _record_history(status, event, item_id, previous, current, timestamp):
    status["history"].append(
        {
            "timestamp": timestamp,
            "event": event,
            "id": item_id,
            "previous": deepcopy(previous),
            "current": deepcopy(current),
        }
    )


def _select_import_source(paths, requested):
    if requested:
        source = Path(requested).expanduser().resolve()
    else:
        candidates = [
            path
            for path in (paths.setup_tracker_working_file, paths.setup_tracker_working_numbers_file)
            if path.exists()
        ]
        if not candidates:
            raise VerificationStatusError("No local verification working workbook exists.")
        source = max(candidates, key=lambda path: path.stat().st_mtime_ns)
    if not source.exists():
        raise VerificationStatusError(f"Verification workbook is missing: {source}")
    if source.suffix.lower() == ".xlsx":
        return source, source, None
    if source.suffix.lower() != ".numbers":
        raise VerificationStatusError("Verification import supports .xlsx or .numbers files.")
    temporary = paths.verification_working_dir / ".verification-import.xlsx"
    _export_numbers_to_xlsx(source, temporary)
    return source, temporary, temporary


def _export_numbers_to_xlsx(numbers_path, output_path):
    output_path.unlink(missing_ok=True)
    source = json.dumps(str(numbers_path))
    destination = json.dumps(str(output_path))
    script = f"""
tell application id "__BUNDLE_ID__"
    set targetDocument to open POSIX file {source}
    export targetDocument to POSIX file {destination} as Microsoft Excel
    close targetDocument saving yes
end tell
"""
    errors = []
    for bundle_id in NUMBERS_BUNDLE_IDS:
        result = subprocess.run(
            ["osascript", "-e", script.replace("__BUNDLE_ID__", bundle_id)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and output_path.is_file() and output_path.stat().st_size:
            return output_path
        errors.append(result.stderr.strip())
    detail = next((item for item in errors if item), "Apple Numbers was not found.")
    raise VerificationStatusError(f"Could not export Numbers for status import: {detail}")


def _extract_workbook(paths, source_path):
    runtime_dir = paths.verification_working_dir / ".status-import-runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    modules = _artifact_modules(paths)
    node_link = runtime_dir / "node_modules"
    if node_link.is_symlink() or node_link.exists():
        if node_link.is_dir() and not node_link.is_symlink():
            shutil.rmtree(node_link)
        else:
            node_link.unlink()
    node_link.symlink_to(modules, target_is_directory=True)
    output = runtime_dir / "status.json"
    command = [
        _node_binary(),
        str(paths.root / "80 Build" / "extract_verification_status.mjs"),
        str(source_path),
        str(output),
        str(runtime_dir),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise VerificationStatusError(result.stderr.strip() or "Workbook status extraction failed.")
    try:
        return json.loads(output.read_text(encoding="utf-8"))
    finally:
        output.unlink(missing_ok=True)


def _artifact_modules(paths):
    configured = os.environ.get("PRS_ARTIFACT_TOOL_NODE_MODULES")
    candidates = [
        Path(configured).expanduser() if configured else None,
        Path(DEFAULT_NODE_MODULES),
    ]
    for candidate in candidates:
        if candidate and (candidate / "@oai" / "artifact-tool").is_dir():
            return candidate.resolve()
    raise VerificationStatusError(
        "Spreadsheet status import requires the bundled @oai/artifact-tool runtime."
    )


def _node_binary():
    return os.environ.get("NODE") or DEFAULT_NODE


def _evidence_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = _scalar(value)
    if not text:
        return []
    return [
        item.strip()
        for line in str(text).splitlines()
        for item in line.split(";")
        if item.strip()
    ]


def _scalar(value):
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value).strip() if not isinstance(value, (int, float, bool)) else value


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description="Manage Git-tracked EOS R5 verification status.")
    parser.add_argument("action", choices=("build", "import", "reconcile", "check"))
    parser.add_argument("--root", default=".")
    parser.add_argument("--source")
    return parser.parse_args()


def main():
    args = parse_args()
    paths = ProjectPaths(args.root)
    try:
        if args.action == "build":
            build_working_copy(paths)
        elif args.action == "import":
            import_workbook_status(paths, args.source)
        elif args.action == "reconcile":
            _, changed = reconcile_status(paths, write=True)
            print("Verification status reconciled." if changed else "Verification definitions are current.")
        elif args.action == "check":
            state, message = working_copy_state(paths)
            print(message)
            return state
    except VerificationStatusError as exc:
        print(f"Verification status failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
