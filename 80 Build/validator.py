#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validators import (  # noqa: E402
    baseline_validator,
    appendix_validator,
    canon_guides_validator,
    icon_validator,
    link_validator,
    output_validator,
    pwa_validator,
    profile_validator,
    structure,
    yaml_validator,
)


VALIDATORS = [
    ("Project Structure", structure.validate),
    ("YAML", yaml_validator.validate),
    ("Baseline", baseline_validator.validate),
    ("Required Appendices", appendix_validator.validate),
    ("Profiles and Overrides", profile_validator.validate),
    ("Icon Library", icon_validator.validate),
    ("Canon Guides", canon_guides_validator.validate),
    ("Build Output", output_validator.validate),
    ("Merged Build PWA", pwa_validator.validate),
    ("Links", link_validator.validate),
]


def parse_args():
    parser = argparse.ArgumentParser(description="Validate the Photography Reference System.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    return parser.parse_args()


def run(root):
    issues = []
    for _, validator in VALIDATORS:
        issues.extend(validator(root))
    return issues


def print_report(issues):
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    print("Photography Reference System Validation")
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
    issues = run(root)
    print_report(issues)
    return 1 if any(issue.level == "error" for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
