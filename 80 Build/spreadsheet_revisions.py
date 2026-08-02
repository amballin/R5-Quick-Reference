"""Deterministic revisions for spreadsheet releases and verification definitions."""

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

from validators.common import load_yaml_checked


MUTABLE_TEST_FIELDS = {
    "status",
    "test_date",
    "session_id",
    "evidence_files",
    "observation",
    "updated_in_project",
}


def workbook_revision(paths, target):
    layouts = load_yaml_checked(paths.spreadsheet_layouts_file) or {}
    layout = ((layouts.get("workbooks") or {}).get(target) or {})
    revision = layout.get("revision")
    if not isinstance(revision, int) or revision < 1:
        raise ValueError(f"{target} workbook revision must be a positive integer.")
    return revision


def source_fingerprint(paths, target):
    layouts = load_yaml_checked(paths.spreadsheet_layouts_file) or {}
    payload = {
        "shared_layout": layouts.get("shared") or {},
        "workbook_layout": ((layouts.get("workbooks") or {}).get(target) or {}),
    }
    code_files = []
    if target == "matrix":
        payload.update(
            {
                "baseline": load_yaml_checked(paths.baseline_file) or {},
                "card_layout": load_yaml_checked(paths.card_layout_file) or {},
                "setting_access": load_yaml_checked(paths.setting_access_file) or {},
                "profiles": {
                    path.name: load_yaml_checked(path) or {}
                    for path in sorted(paths.profiles_dir.glob("*.yaml"))
                },
            }
        )
        code_files = [
            paths.root / "80 Build" / "subject_settings_matrix.py",
            paths.root / "80 Build" / "render_subject_settings_matrix.mjs",
            paths.root / "80 Build" / "html_renderer.py",
        ]
    elif target == "setup":
        payload["tracker"] = load_yaml_checked(paths.verification_tracker_source_file) or {}
        payload["baseline"] = load_yaml_checked(paths.baseline_file) or {}
        code_files = [
            paths.root / "80 Build" / "camera_setup_tracker.py",
            paths.root / "80 Build" / "render_camera_setup_tracker.mjs",
        ]
    else:
        raise ValueError(f"Unknown spreadsheet target: {target}")
    code_files.extend(
        [
            paths.root / "80 Build" / "spreadsheet_revisions.py",
            paths.root / "80 Build" / "spreadsheet_ooxml.py",
        ]
    )
    digest = hashlib.sha256(_canonical_json(payload))
    for path in code_files:
        digest.update(path.relative_to(paths.root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def test_definition_fingerprint(test):
    definition = {
        key: value
        for key, value in test.items()
        if key not in MUTABLE_TEST_FIELDS
    }
    return _fingerprint(definition)


def registration_definition_fingerprints(source):
    registration = source.get("registration") or {}
    profiles = registration.get("profiles") or []
    return {
        row["setting"]: _fingerprint(
            {
                "setting": row["setting"],
                "targets": {
                    profile["key"]: row.get(profile["key"], "")
                    for profile in profiles
                },
            }
        )
        for row in registration.get("rows") or []
    }


def tracker_definition_fingerprints(source):
    return {
        test["test_id"]: test_definition_fingerprint(test)
        for test in source.get("tests") or []
    }


def short_fingerprint(value):
    return value.split(":", 1)[-1][:12]


def _fingerprint(value):
    return f"sha256:{hashlib.sha256(_canonical_json(value)).hexdigest()}"


def _canonical_json(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    ).encode("utf-8")


def _json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Unsupported fingerprint value: {type(value).__name__}")
