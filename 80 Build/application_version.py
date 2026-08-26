#!/usr/bin/env python3
"""Shared development version for Profile Editor and Camera Lab."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile

import yaml

from project_context import project_context_info


VERSION_FILE = Path("00 Master/application_version.yaml")


class ApplicationVersionError(ValueError):
    pass


def _load(project_root: Path):
    version_path = project_root / VERSION_FILE
    try:
        payload = yaml.safe_load(version_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ApplicationVersionError(f"Application version metadata is unreadable: {version_path}") from exc
    required = {"schema_version", "major", "minor", "base_commit", "incremental"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise ApplicationVersionError("Application version metadata has unexpected fields.")
    if payload["schema_version"] != 1:
        raise ApplicationVersionError("Application version metadata requires schema_version 1.")
    for field in ("major", "minor", "incremental"):
        value = payload[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ApplicationVersionError(f"Application version {field} must be a nonnegative integer.")
    base_commit = payload["base_commit"]
    if not isinstance(base_commit, str) or len(base_commit) != 40 or any(
        character not in "0123456789abcdef" for character in base_commit.lower()
    ):
        raise ApplicationVersionError("Application version base_commit must be a full Git commit hash.")
    return payload


def _git_state(project_root: Path, base_commit: str):
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if head.returncode:
        return None, None
    head_commit = head.stdout.strip()
    distance = subprocess.run(
        ["git", "rev-list", "--count", f"{base_commit}..{head_commit}"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_commit, head_commit],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if distance.returncode or ancestor.returncode:
        return head_commit, None
    try:
        return head_commit, int(distance.stdout.strip())
    except ValueError:
        return head_commit, None


def application_version_info(project_root: Path):
    project_root = Path(project_root).resolve()
    configured = _load(project_root)
    head_commit, commit_distance = _git_state(project_root, configured["base_commit"])
    minor = configured["minor"]
    incremental = configured["incremental"]
    if commit_distance is not None and commit_distance > 0:
        minor += commit_distance
        incremental = 0
    context = project_context_info(project_root)
    context_name = {"main": "Main", "prototype": "Prototype"}.get(context["kind"], "Unknown")
    return {
        "major": configured["major"],
        "minor": minor,
        "incremental": incremental,
        "version": f"{configured['major']}.{minor}.{incremental}",
        "context_name": context_name,
        "project_context": context,
        "head_commit": head_commit,
        "base_commit": configured["base_commit"],
    }


def complete_development_update(project_root: Path):
    project_root = Path(project_root).resolve()
    configured = _load(project_root)
    current = application_version_info(project_root)
    if not current["head_commit"]:
        raise ApplicationVersionError("A Git checkout is required to complete a development update.")
    if current["head_commit"] == configured["base_commit"]:
        configured["incremental"] += 1
    else:
        configured["minor"] = current["minor"]
        configured["base_commit"] = current["head_commit"]
        configured["incremental"] = 1
    version_path = project_root / VERSION_FILE
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=version_path.parent, delete=False
    ) as handle:
        yaml.safe_dump(configured, handle, sort_keys=False)
        staged_path = Path(handle.name)
    staged_path.replace(version_path)
    return application_version_info(project_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read or advance the shared local-app version.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--complete-update", action="store_true")
    args = parser.parse_args()
    info = (
        complete_development_update(args.project_root)
        if args.complete_update
        else application_version_info(args.project_root)
    )
    print(f"{info['version']} · {info['context_name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
