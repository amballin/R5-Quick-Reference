#!/usr/bin/env python3
"""Render curated reader-facing notes between published website versions."""

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys

import yaml


METADATA_PATH = "80 Build/publish_metadata.yaml"
NOTES_PATH = "00 Master/release_notes.yaml"
NOTES_FORMAT_VERSION = 1
VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.([0-9]+)$")


class ReleaseNotesError(RuntimeError):
    """Raised when release-note source or publication history is invalid."""


@dataclass(frozen=True)
class Publication:
    version: str
    published: datetime
    commit: str


def parse_version(value):
    if not isinstance(value, str):
        raise ReleaseNotesError("Release versions must be strings such as '1.20'.")
    match = VERSION_PATTERN.fullmatch(value)
    if not match:
        raise ReleaseNotesError(f"Invalid release version: {value!r}.")
    return int(match.group(1)), int(match.group(2))


def normalize_version(value):
    major, minor = parse_version(value)
    return f"{major}.{minor:02d}"


def load_release_notes(path):
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ReleaseNotesError(f"Could not read release notes: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ReleaseNotesError(f"Could not parse release notes: {exc}") from exc

    if not isinstance(payload, dict) or set(payload) != {"version", "releases"}:
        raise ReleaseNotesError("Release notes must contain only 'version' and 'releases'.")
    if payload["version"] != NOTES_FORMAT_VERSION:
        raise ReleaseNotesError("Unsupported release-notes format version.")
    releases = payload["releases"]
    if not isinstance(releases, dict) or not releases:
        raise ReleaseNotesError("Release notes must contain at least one release.")

    normalized = {}
    for version, entry in releases.items():
        canonical_version = normalize_version(version)
        if canonical_version != version:
            raise ReleaseNotesError(
                f"Release version {version!r} must use canonical form {canonical_version!r}."
            )
        if not isinstance(entry, dict) or set(entry) != {"highlights"}:
            raise ReleaseNotesError(
                f"Release {version} must contain only a 'highlights' list."
            )
        highlights = entry["highlights"]
        if not isinstance(highlights, list) or not highlights:
            raise ReleaseNotesError(f"Release {version} must have at least one highlight.")
        if any(not isinstance(item, str) or not item.strip() for item in highlights):
            raise ReleaseNotesError(f"Release {version} highlights must be non-empty text.")
        cleaned = [item.strip() for item in highlights]
        if len(set(cleaned)) != len(cleaned):
            raise ReleaseNotesError(f"Release {version} contains duplicate highlights.")
        normalized[canonical_version] = cleaned
    return normalized


def publication_history(root):
    commits = _git_lines(root, ["log", "--first-parent", "--format=%H", "--", METADATA_PATH])
    publications = []
    for commit in reversed(commits):
        current = _metadata_from_git(root, f"{commit}:{METADATA_PATH}")
        previous = _metadata_from_git(root, f"{commit}^:{METADATA_PATH}", required=False)
        if previous is None or _valid_transition(previous["version"], current["version"]):
            version = current["version"]
            publications.append(
                Publication(
                    version=f"{version['major']}.{version['minor']:02d}",
                    published=current["published"],
                    commit=commit,
                )
            )
    if len(publications) < 2:
        raise ReleaseNotesError("At least two identifiable publications are required.")
    return publications


def select_publications(publications, from_version=None, to_version=None):
    if from_version is not None:
        parse_version(from_version)
    if to_version is not None:
        parse_version(to_version)

    if from_version is None and to_version is None:
        return len(publications) - 2, len(publications) - 1

    to_index = _publication_index(publications, to_version) if to_version else len(publications) - 1
    if from_version is None:
        if to_index == 0:
            raise ReleaseNotesError(f"Version {to_version} has no earlier publication to compare.")
        from_index = to_index - 1
    else:
        from_index = _publication_index(publications, from_version)

    if from_index >= to_index:
        raise ReleaseNotesError("The starting publication must be earlier than the ending publication.")
    return from_index, to_index


def render_release_notes(publications, notes, from_index, to_index):
    start = publications[from_index]
    end = publications[to_index]
    included = publications[from_index + 1 : to_index + 1]
    missing = [publication.version for publication in included if publication.version not in notes]
    if missing:
        raise ReleaseNotesError(
            "Curated reader-facing notes are missing for Version " + ", ".join(missing) + "."
        )

    lines = [
        "# Camera Settings Release Notes",
        "",
        f"## Version {start.version} → {end.version}",
        "",
    ]
    if len(included) == 1:
        lines.append(f"Published {end.published.strftime('%B %-d, %Y')}")
        lines.append("")
        lines.extend(f"- {highlight}" for highlight in notes[end.version])
    else:
        for publication in included:
            lines.extend(
                [
                    f"### Version {publication.version} — {publication.published.strftime('%B %-d, %Y')}",
                    "",
                    *(f"- {highlight}" for highlight in notes[publication.version]),
                    "",
                ]
            )
        while lines and lines[-1] == "":
            lines.pop()
    return "\n".join(lines) + "\n"


def _publication_index(publications, version):
    canonical_version = normalize_version(version)
    matches = [
        index
        for index, publication in enumerate(publications)
        if publication.version == canonical_version
    ]
    if not matches:
        raise ReleaseNotesError(
            f"Publication Version {canonical_version} was not found in Git history."
        )
    return matches[-1]


def _valid_transition(previous, current):
    old_major, old_minor = previous["major"], previous["minor"]
    new_major, new_minor = current["major"], current["minor"]
    return (new_major == old_major and new_minor == old_minor + 1) or (
        new_major > old_major and new_minor == 0
    )


def _metadata_from_git(root, object_name, required=True):
    result = subprocess.run(
        ["git", "show", object_name],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if not required:
            return None
        raise ReleaseNotesError(result.stderr.strip() or "Git metadata lookup failed.")
    try:
        payload = yaml.safe_load(result.stdout)
    except yaml.YAMLError as exc:
        raise ReleaseNotesError(f"Could not parse {object_name}: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != {"version", "published"}:
        raise ReleaseNotesError(f"Invalid publish metadata at {object_name}.")
    version = payload["version"]
    published = payload["published"]
    if (
        not isinstance(version, dict)
        or set(version) != {"major", "minor"}
        or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in version.values())
        or not isinstance(published, datetime)
    ):
        raise ReleaseNotesError(f"Invalid publish metadata at {object_name}.")
    return payload


def _git_lines(root, arguments):
    result = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        raise ReleaseNotesError(result.stderr.strip() or "Git history lookup failed.")
    return [line for line in result.stdout.splitlines() if line]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render curated reader-facing notes between website publications."
    )
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--from", dest="from_version", help="Starting publication, such as 1.19.")
    parser.add_argument("--to", dest="to_version", help="Ending publication, such as 1.20.")
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    try:
        notes = load_release_notes(root / NOTES_PATH)
        publications = publication_history(root)
        from_index, to_index = select_publications(
            publications,
            from_version=args.from_version,
            to_version=args.to_version,
        )
        output = render_release_notes(publications, notes, from_index, to_index)
    except (OSError, ReleaseNotesError, ValueError) as exc:
        print(f"RELEASE NOTES FAILED: {exc}", file=sys.stderr)
        return 1
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
