#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validators import (  # noqa: E402
    baseline_validator,
    card_layout_validator,
    appendix_validator,
    canon_guides_validator,
    control_validator,
    finish_day_guide_validator,
    icon_validator,
    governance_validator,
    link_validator,
    output_validator,
    pwa_validator,
    profile_validator,
    setting_access_validator,
    spreadsheet_download_validator,
    spreadsheet_spec_validator,
    stabilization_validator,
    structure,
    verification_status_validator,
    workflow_guides_validator,
    yaml_validator,
)


VALIDATORS = [
    ("Project Structure", structure.validate),
    ("YAML", yaml_validator.validate),
    ("Baseline", baseline_validator.validate),
    ("Card Layout", card_layout_validator.validate),
    ("Setting Access Map", setting_access_validator.validate),
    ("Spreadsheet Specifications", spreadsheet_spec_validator.validate),
    ("Spreadsheet Downloads", spreadsheet_download_validator.validate),
    ("Verification Status", verification_status_validator.validate),
    ("Governance Documents", governance_validator.validate),
    ("Finish-Day HTML Guide", finish_day_guide_validator.validate),
    ("Local Workflow HTML Guides", workflow_guides_validator.validate),
    ("Camera Controls", control_validator.validate),
    ("Required Appendices", appendix_validator.validate),
    ("Profiles and Overrides", profile_validator.validate),
    ("Icon Library", icon_validator.validate),
    ("Canon Guides", canon_guides_validator.validate),
    ("Stabilization Reference", stabilization_validator.validate),
    ("Build Output", output_validator.validate),
    ("Merged Build PWA", pwa_validator.validate),
    ("Links", link_validator.validate),
]

SOURCE_ONLY_VALIDATORS = [
    ("Project Structure", structure.validate),
    ("YAML", yaml_validator.validate),
    ("Baseline", baseline_validator.validate),
    ("Card Layout", card_layout_validator.validate),
    ("Setting Access Map", setting_access_validator.validate),
    ("Spreadsheet Specifications", spreadsheet_spec_validator.validate),
    ("Verification Status", verification_status_validator.validate),
    ("Governance Documents", governance_validator.validate),
    ("Finish-Day Guide Source", finish_day_guide_validator.validate_source),
    ("Local Workflow Guide Sources", workflow_guides_validator.validate_source),
    ("Camera Controls", control_validator.validate),
    ("Required Appendices", appendix_validator.validate),
    ("Profiles and Overrides", profile_validator.validate),
    ("Icon Library", icon_validator.validate),
    ("Canon Guides", canon_guides_validator.validate),
    ("Stabilization Reference", stabilization_validator.validate),
    ("Links", link_validator.validate),
]


def parse_args():
    parser = argparse.ArgumentParser(description="Validate the Photography Reference System.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Validate editable sources before a build without checking stale generated output.",
    )
    return parser.parse_args()


def run(root, source_only=False):
    issues = []
    validators = SOURCE_ONLY_VALIDATORS if source_only else VALIDATORS
    for _, validator in validators:
        issues.extend(validator(root))
    return issues


def print_report(issues, source_only=False):
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    title = "Photography Reference System Source Validation" if source_only else "Photography Reference System Validation"
    print(title)
    print()
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print()
    if not issues:
        print("No validation issues found.")
        return
    for issue in issues:
        print(f"[{issue.level.upper()}] {issue.area}: {issue.path}")
        print(f"    {issue.message}")


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    issues = run(root, source_only=args.source_only)
    print_report(issues, source_only=args.source_only)
    return 1 if any(issue.level == "error" for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
