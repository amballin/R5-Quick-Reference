#!/usr/bin/env python3
"""Report profile impact from worktree baseline changes relative to a Git ref."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import yaml

from baseline_impact import BaselineImpactError, analyze_baseline_impact
from validators.common import load_yaml_checked


BASELINE_RELATIVE = Path("00 Master") / "baseline.yaml"
PROFILES_RELATIVE = Path("10 Profiles")


class BaselineImpactCheckError(RuntimeError):
    """Raised when the repository comparison cannot be completed."""


def repository_baseline(root, ref):
    if not ref or any(character in ref for character in "\r\n"):
        raise BaselineImpactCheckError("The base Git ref must be a nonempty single line.")
    result = subprocess.run(
        ["git", "show", f"{ref}:{BASELINE_RELATIVE.as_posix()}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or "Git could not read the baseline."
        raise BaselineImpactCheckError(f"Unable to read baseline from {ref}: {detail}")
    try:
        baseline = yaml.safe_load(result.stdout)
    except yaml.YAMLError as exc:
        raise BaselineImpactCheckError(f"Baseline from {ref} is invalid YAML: {exc}") from exc
    if not isinstance(baseline, dict):
        raise BaselineImpactCheckError(f"Baseline from {ref} must be a YAML mapping.")
    return baseline


def worktree_profiles(root):
    profiles = {}
    for path in sorted((root / PROFILES_RELATIVE).glob("*.yaml")):
        profile = load_yaml_checked(path) or {}
        profiles[path.stem] = profile
    if not profiles:
        raise BaselineImpactCheckError("No profile YAML files were found in 10 Profiles.")
    return profiles


def analyze_repository(root, base_ref="HEAD"):
    root = Path(root).resolve()
    current = repository_baseline(root, base_ref)
    proposed = load_yaml_checked(root / BASELINE_RELATIVE) or {}
    profiles = worktree_profiles(root)
    try:
        return analyze_baseline_impact(current, proposed, profiles)
    except BaselineImpactError as exc:
        raise BaselineImpactCheckError(str(exc)) from exc


def text_report(analysis, base_ref):
    summary = analysis["summary"]
    lines = [
        "Baseline Impact Check",
        "",
        f"Comparison: {base_ref} -> working tree",
        f"Changed baseline settings: {summary['changed_settings']}",
        f"Affected profiles: {summary['affected_profiles']}",
        f"Profiles requiring a decision: {summary['profiles_requiring_decision']}",
    ]
    if not analysis["changes"]:
        lines.extend(("", "No semantic baseline-default changes found."))
        return "\n".join(lines)

    lines.extend(("", "Review required:"))
    for change in analysis["changes"]:
        lines.append(
            f"- {change['path']}: {change['current_baseline_value']!r} "
            f"-> {change['proposed_baseline_value']!r}"
        )
        classifications = {}
        for profile in change["profiles"]:
            classifications.setdefault(profile["classification"], []).append(profile["title"])
        for classification, titles in sorted(classifications.items()):
            lines.append(f"  {classification}: {', '.join(sorted(titles, key=str.casefold))}")
    lines.extend(
        (
            "",
            "Exit status 1 indicates semantic baseline changes that require review. "
            "Use the Profile Editor for a guarded migration.",
        )
    )
    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root. Defaults to the current directory.")
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Git ref containing the baseline to compare. Defaults to HEAD.",
    )
    parser.add_argument("--json", action="store_true", help="Print the complete analysis as JSON.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        analysis = analyze_repository(args.root, args.base_ref)
    except (BaselineImpactCheckError, OSError, yaml.YAMLError) as exc:
        print(f"BASELINE IMPACT CHECK ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(analysis, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(text_report(analysis, args.base_ref))
    return 1 if analysis["summary"]["changed_settings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
