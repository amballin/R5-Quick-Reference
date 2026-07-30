from asset_manager import ProjectPaths
from spreadsheet_revisions import (
    registration_definition_fingerprints,
    tracker_definition_fingerprints,
)
from verification_status import STATUS_VERSION, load_status

from .common import error, load_yaml_checked


def validate(root):
    issues = []
    paths = ProjectPaths(root)
    try:
        status = load_status(paths)
    except Exception as exc:
        return [error("verification_status", paths.verification_status_file, str(exc))]
    source = load_yaml_checked(paths.verification_tracker_source_file) or {}
    if status.get("version") != STATUS_VERSION:
        issues.append(error("verification_status", paths.verification_status_file, "Unsupported status version."))
        return issues
    valid_ids = tracker_definition_fingerprints(source)
    valid_registration = registration_definition_fingerprints(source)
    statuses = set((source.get("lists") or {}).get("main_status") or [])
    for test_id, state in status.get("tests", {}).items():
        if test_id not in valid_ids:
            issues.append(error("verification_status", paths.verification_status_file, f"Unknown active Test ID: {test_id}"))
            continue
        if state.get("status") not in statuses:
            issues.append(error("verification_status", paths.verification_status_file, f"{test_id} has invalid Status."))
        if state.get("status") == "Verified" and state.get("verified_against") != valid_ids[test_id]:
            issues.append(
                error(
                    "verification_status",
                    paths.verification_status_file,
                    f"{test_id} is Verified against an older definition. Run reconcile-verification-status.sh.",
                )
            )
    for setting, state in status.get("registration", {}).items():
        if setting not in valid_registration:
            issues.append(error("verification_status", paths.verification_status_file, f"Unknown registration setting: {setting}"))
            continue
        passed = any(
            state.get(key) == "Pass"
            for key in ("c1_configured", "c1_read_back", "c2_configured", "c2_read_back", "c3_configured", "c3_read_back")
        )
        if passed and state.get("verified_against") != valid_registration[setting]:
            issues.append(
                error(
                    "verification_status",
                    paths.verification_status_file,
                    f"{setting} registration passed against an older target. Run reconcile-verification-status.sh.",
                )
            )
    return issues
