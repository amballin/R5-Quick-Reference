#!/usr/bin/env python3
"""Exact, opt-in cleanup review for workflow-owned disposable artifacts."""

from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import re
import secrets
import shutil
import subprocess

from asset_manager import ProjectPaths


class CleanupReviewError(RuntimeError):
    pass


BACKUP_PATTERN = re.compile(r"^(\d{8}-\d{6})-(.+)$")
FIXED_BACKUP_TYPES = {
    "finish-day-docs",
    "profile-editor-cx-foundation",
    "profile-editor-my-menu",
    "profile-editor-my-menu-colors",
    "baseline-migration",
}
PROFILE_BACKUP_PATTERN = re.compile(r"^profile-editor-(create|update|discard|restore)-(.+)$")


class CleanupReview:
    """List only known disposable items and delete exact confirmed selections."""

    def __init__(self, root):
        self.paths = ProjectPaths(root)
        self._review = None

    @staticmethod
    def _inside(path, parent):
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    @staticmethod
    def _size(path):
        if path.is_file() and not path.is_symlink():
            return path.stat().st_size
        total = 0
        if path.is_dir() and not path.is_symlink():
            for child in path.rglob("*"):
                if child.is_file() and not child.is_symlink():
                    total += child.stat().st_size
        return total

    @staticmethod
    def _backup_group(suffix):
        if suffix in FIXED_BACKUP_TYPES:
            return suffix
        match = PROFILE_BACKUP_PATTERN.match(suffix)
        if match:
            return f"profile-editor-{match.group(1)}-{match.group(2)}"
        return None

    @staticmethod
    def _has_recovery_content(path):
        return path.is_dir() and not path.is_symlink() and any(
            child.is_file() and not child.is_symlink() for child in path.rglob("*")
        )

    def _candidate(self, path, kind, reason, group=None):
        stat = path.stat()
        size = self._size(path)
        identity = f"{kind}\0{path.resolve()}\0{stat.st_mtime_ns}\0{size}"
        return {
            "id": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
            "kind": kind,
            "path": str(path.resolve()),
            "name": path.name,
            "sizeBytes": size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "reason": reason,
            "group": group,
        }

    def _is_ignored_source_metadata(self, path):
        relative = path.relative_to(self.paths.root)
        completed = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", str(relative)],
            cwd=self.paths.root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return completed.returncode == 0

    def _inventory(self):
        candidates = []
        protected = []
        groups = {}
        backup_root = self.paths.backups_dir
        if backup_root.is_dir():
            for path in backup_root.iterdir():
                if path.is_symlink():
                    continue
                match = BACKUP_PATTERN.match(path.name)
                if not match:
                    continue
                group = self._backup_group(match.group(2))
                if group:
                    groups.setdefault(group, []).append((match.group(1), path))
        for group, entries in groups.items():
            entries.sort(key=lambda item: item[0], reverse=True)
            successful = [item for item in entries if self._has_recovery_content(item[1])]
            protected_path = successful[0][1] if successful else None
            if protected_path:
                protected.append(
                    self._candidate(
                        protected_path,
                        "protected-backup",
                        "Newest successful recovery backup of this type; always retained.",
                        group,
                    )
                )
            for _timestamp, path in entries:
                if path == protected_path:
                    continue
                candidates.append(
                    self._candidate(
                        path,
                        "superseded-backup",
                        "Superseded by a newer successful workflow backup of the same type.",
                        group,
                    )
                )
        for path in self.paths.root.rglob(".DS_Store"):
            if ".git" in path.parts or path.is_symlink() or not self._is_ignored_source_metadata(path):
                continue
            candidates.append(
                self._candidate(
                    path,
                    "macos-metadata",
                    "Disposable macOS folder metadata; not project source.",
                )
            )
        candidates.sort(key=lambda item: (item["kind"], item["path"]))
        return candidates, protected

    def inspect(self):
        candidates, protected = self._inventory()
        token = secrets.token_urlsafe(24)
        self._review = {"token": token, "candidates": {item["id"]: item for item in candidates}}
        return {
            "reviewToken": token,
            "candidates": candidates,
            "protected": protected,
            "candidateBytes": sum(item["sizeBytes"] for item in candidates),
            "message": (
                "Review exact optional cleanup candidates. Nothing is selected or deleted automatically."
                if candidates
                else "No recognized superseded backups or disposable metadata need cleanup."
            ),
        }

    def delete(self, review_token, candidate_ids, confirmed):
        if confirmed is not True:
            raise CleanupReviewError("Permanent cleanup confirmation is required.")
        if not self._review or not secrets.compare_digest(str(review_token or ""), self._review["token"]):
            raise CleanupReviewError("Cleanup review expired. Refresh and review the candidates again.")
        if not isinstance(candidate_ids, list) or not candidate_ids:
            raise CleanupReviewError("Select at least one cleanup candidate.")
        selected = []
        for candidate_id in candidate_ids:
            item = self._review["candidates"].get(str(candidate_id))
            if not item:
                raise CleanupReviewError("A selected cleanup candidate was not part of the reviewed list.")
            selected.append(item)
        current, _protected = self._inventory()
        current_by_id = {item["id"]: item for item in current}
        if any(item["id"] not in current_by_id for item in selected):
            self._review = None
            raise CleanupReviewError("A cleanup candidate changed after review. Refresh before deleting anything.")
        deleted = []
        recovered = 0
        for item in selected:
            path = Path(item["path"])
            if item["kind"] == "superseded-backup":
                if not self._inside(path, self.paths.backups_dir) or path.is_symlink() or not path.is_dir():
                    raise CleanupReviewError(f"Backup cleanup target is no longer safe: {path}")
                shutil.rmtree(path)
            elif item["kind"] == "macos-metadata":
                if not self._inside(path, self.paths.root) or path.name != ".DS_Store" or path.is_symlink():
                    raise CleanupReviewError(f"Metadata cleanup target is no longer safe: {path}")
                path.unlink()
            else:
                raise CleanupReviewError("Unsupported cleanup candidate type.")
            deleted.append(item)
            recovered += item["sizeBytes"]
        self._review = None
        refreshed = self.inspect()
        refreshed.update(
            {
                "deleted": deleted,
                "deletedBytes": recovered,
                "message": f"Permanently deleted {len(deleted)} reviewed cleanup item{'s' if len(deleted) != 1 else ''}.",
            }
        )
        return refreshed
