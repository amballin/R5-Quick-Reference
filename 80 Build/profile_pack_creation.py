"""Guarded creation of a private profile pack from embedded owner sources."""

from __future__ import annotations

import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import threading
import time
from uuid import uuid4

import yaml

from asset_manager import ProjectPaths
from profile_pack import (
    APPLICATION_PROJECT_ID,
    EMBEDDED_SOURCE_PATHS,
    EXPECTED_CAMERA,
    MANIFEST_VERSION,
    PROFILE_PACK_CONTRACT,
    PROHIBITED_COMPONENT_PATTERNS,
    SOURCE_PATHS,
    resolve_profile_pack,
)


REVIEW_TTL_SECONDS = 30 * 60
MAX_PENDING_REVIEWS = 20
PACK_NAME_PATTERN = re.compile(r"[^\x00-\x1f/\\]{1,80}")
PACK_INSTRUCTIONS = Path(__file__).resolve().parent / "profile_pack_templates" / "AGENTS.md"
PACK_GITIGNORE = Path(__file__).resolve().parent / "profile_pack_templates" / ".gitignore"


class ProfilePackCreationError(RuntimeError):
    """Raised when a reviewed profile-pack creation cannot complete safely."""


class ProfilePackCreator:
    """Review, stage, validate, and atomically install one new profile pack."""

    def __init__(self, application_root, source_validator=None):
        self.application_root = Path(application_root).resolve()
        self._source_validator = source_validator or self._validate_sources
        self._pending_reviews = {}
        self._lock = threading.RLock()

    def review(self, pack_name, destination, pending_changes):
        if pending_changes != 0:
            raise ProfilePackCreationError(
                "Save or discard every browser draft before creating a profile pack."
            )
        pack_name = self._pack_name(pack_name)
        destination = self._destination(destination)
        self._expire_reviews()
        pack_id = str(uuid4())
        manifest = self._manifest(pack_id, pack_name)
        manifest_yaml = yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)
        source_files = self._source_file_inventory()
        review_token = secrets.token_urlsafe(32)
        self._pending_reviews[review_token] = {
            "created": time.monotonic(),
            "pack_id": pack_id,
            "pack_name": pack_name,
            "destination": destination,
            "manifest": manifest,
            "manifest_yaml": manifest_yaml,
            "source_fingerprint": self._embedded_fingerprint(),
            "source_files": source_files,
        }
        if len(self._pending_reviews) > MAX_PENDING_REVIEWS:
            oldest = min(self._pending_reviews, key=lambda token: self._pending_reviews[token]["created"])
            del self._pending_reviews[oldest]
        return {
            "reviewToken": review_token,
            "packId": pack_id,
            "packName": pack_name,
            "destination": str(destination),
            "manifestYaml": manifest_yaml,
            "sourceFiles": source_files,
            "sourceFileCount": len(source_files),
            "gitAction": "Initialize a local Git repository without a commit, remote, or push.",
        }

    def choose_destination(self, suggested_name):
        """Open the native macOS Save panel and return one new destination path."""
        if not isinstance(suggested_name, str):
            raise ProfilePackCreationError("The suggested profile-pack name must be text.")
        suggested_name = suggested_name.strip() or "My Canon EOS R5 Profiles"
        suggested_name = re.sub(r"[/:\\\x00-\x1f]+", " ", suggested_name).strip()
        suggested_name = suggested_name[:80] or "My Canon EOS R5 Profiles"
        script = """
on run argv
  set suggestedName to item 1 of argv
  try
    set chosenPath to choose file name with prompt "Choose the exact destination for the new private profile pack" default name suggestedName
    return POSIX path of chosenPath
  on error number -128
    return "__PROFILE_PACK_PICKER_CANCELLED__"
  end try
end run
""".strip()
        try:
            completed = subprocess.run(
                ["osascript", "-e", script, "--", suggested_name],
                capture_output=True,
                text=True,
                timeout=5 * 60,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ProfilePackCreationError(
                "The macOS destination chooser could not be opened."
            ) from exc
        selected = completed.stdout.strip()
        if completed.returncode or not selected:
            detail = completed.stderr.strip()
            raise ProfilePackCreationError(
                f"The macOS destination chooser failed: {detail or 'no destination was returned.'}"
            )
        if selected == "__PROFILE_PACK_PICKER_CANCELLED__":
            return {"cancelled": True}
        path = Path(selected).expanduser()
        if not path.is_absolute():
            raise ProfilePackCreationError("The macOS destination chooser returned an invalid path.")
        return {"cancelled": False, "destination": str(path)}

    def create(self, review_token, confirm_create):
        if confirm_create is not True:
            raise ProfilePackCreationError("Creating a profile pack requires explicit confirmation.")
        if not isinstance(review_token, str) or not review_token:
            raise ProfilePackCreationError("The profile-pack creation review is missing or expired.")
        with self._lock:
            self._expire_reviews()
            review = self._pending_reviews.pop(review_token, None)
            if review is None:
                raise ProfilePackCreationError("The profile-pack creation review is missing or expired.")
            destination = self._destination(str(review["destination"]))
            if self._embedded_fingerprint() != review["source_fingerprint"]:
                raise ProfilePackCreationError(
                    "Embedded profile sources changed after review. Review the new profile pack again."
                )
            return self._create_reviewed(review, destination)

    def discard_created(self, root):
        """Remove only a pack created by this service when final registration fails."""
        root = Path(root).resolve()
        manifest = root / "profile-pack.yaml"
        if root.exists() and manifest.is_file():
            shutil.rmtree(root)

    def _create_reviewed(self, review, destination):
        parent = destination.parent
        staging = Path(tempfile.mkdtemp(prefix=".profile-pack-create-", dir=parent))
        installed = False
        complete = False
        try:
            self._write_staged_pack(staging, review)
            self._initialize_git(staging)
            staged_context = resolve_profile_pack(self.application_root, explicit_root=staging)
            errors = list(
                self._source_validator(
                    ProjectPaths(
                        self.application_root,
                        profile_pack_context=staged_context,
                    )
                )
            )
            if errors:
                raise ProfilePackCreationError(
                    "The new profile pack did not pass combined source validation: "
                    + "; ".join(str(error) for error in errors)
                )
            os.replace(staging, destination)
            installed = True
            context = resolve_profile_pack(self.application_root, explicit_root=destination)
            complete = True
            return context
        except ProfilePackCreationError:
            raise
        except Exception as exc:
            raise ProfilePackCreationError(f"Could not create the new profile pack: {exc}") from exc
        finally:
            if staging.exists():
                shutil.rmtree(staging)
            if installed and not complete:
                shutil.rmtree(destination, ignore_errors=True)

    def _write_staged_pack(self, staging, review):
        (staging / "profile-pack.yaml").write_text(
            review["manifest_yaml"], encoding="utf-8"
        )
        shutil.copy2(PACK_INSTRUCTIONS, staging / "AGENTS.md")
        shutil.copy2(PACK_GITIGNORE, staging / ".gitignore")
        for key, destination_relative in SOURCE_PATHS.items():
            source = self.application_root / EMBEDDED_SOURCE_PATHS[key]
            destination = staging / destination_relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

    @staticmethod
    def _initialize_git(staging):
        completed = subprocess.run(
            ["git", "init", "-q", str(staging)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()
            raise ProfilePackCreationError(
                f"Could not initialize the new pack's local Git repository: {detail or 'git init failed.'}"
            )

    def _destination(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ProfilePackCreationError("Choose an exact destination for the new profile pack.")
        expanded = Path(value.strip()).expanduser()
        if not expanded.is_absolute():
            raise ProfilePackCreationError("The new profile-pack destination must be an absolute path.")
        if not expanded.name or expanded.name in {".", ".."}:
            raise ProfilePackCreationError("The new profile-pack destination is invalid.")
        try:
            parent = expanded.parent.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise ProfilePackCreationError(
                "The destination's parent folder must already exist."
            ) from exc
        if not parent.is_dir():
            raise ProfilePackCreationError("The destination's parent must be a folder.")
        destination = parent / expanded.name
        if destination.exists() or destination.is_symlink():
            raise ProfilePackCreationError(
                "The destination already exists. Choose a new empty destination name; nothing will be overwritten."
            )
        if (
            destination == self.application_root
            or self.application_root in destination.parents
            or destination in self.application_root.parents
        ):
            raise ProfilePackCreationError(
                "The private profile pack must be outside and separate from the application repository."
            )
        for component in destination.parts:
            normalized = re.sub(r"[_-]+", " ", component).casefold().strip()
            if any(pattern.search(normalized) for pattern in PROHIBITED_COMPONENT_PATTERNS):
                raise ProfilePackCreationError(
                    f"The destination has a prohibited folder name: {component}"
                )
        if not os.access(parent, os.W_OK):
            raise ProfilePackCreationError("The destination's parent folder is not writable.")
        return destination

    @staticmethod
    def _pack_name(value):
        if not isinstance(value, str):
            raise ProfilePackCreationError("Profile-pack name must be text.")
        if value != value.strip() or not PACK_NAME_PATTERN.fullmatch(value):
            raise ProfilePackCreationError(
                "Profile-pack name must be 1–80 friendly characters without paths, control characters, or surrounding spaces."
            )
        return value

    def _source_file_inventory(self):
        files = [".gitignore", "AGENTS.md", "profile-pack.yaml"]
        for key, destination_relative in SOURCE_PATHS.items():
            source = self.application_root / EMBEDDED_SOURCE_PATHS[key]
            destination = Path(destination_relative)
            if source.is_dir():
                files.extend(
                    sorted(
                        (destination / path.relative_to(source)).as_posix()
                        for path in source.rglob("*")
                        if path.is_file()
                    )
                )
            else:
                files.append(destination.as_posix())
        return sorted(files)

    def _embedded_fingerprint(self):
        return resolve_profile_pack(self.application_root).fingerprint()

    @staticmethod
    def _manifest(pack_id, pack_name):
        return {
            "manifest_version": MANIFEST_VERSION,
            "pack_id": pack_id,
            "pack_name": pack_name,
            "repository_role": "private-profile-pack",
            "artifact_type": "source-repository",
            "camera": dict(EXPECTED_CAMERA),
            "compatibility": {
                "application_project_id": APPLICATION_PROJECT_ID,
                "profile_pack_contract": PROFILE_PACK_CONTRACT,
            },
            "sources": dict(SOURCE_PATHS),
            "publication": {"default_profile_policy": "explicit-release-only"},
        }

    def _expire_reviews(self):
        cutoff = time.monotonic() - REVIEW_TTL_SECONDS
        for token in [
            token
            for token, review in self._pending_reviews.items()
            if review["created"] < cutoff
        ]:
            del self._pending_reviews[token]

    @staticmethod
    def _validate_sources(paths):
        from validator import run

        return [issue.message for issue in run(paths, source_only=True) if issue.level == "error"]
