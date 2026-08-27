"""Machine-local journal storage for deliberate guarded-run resume or abort."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SESSION_ID = re.compile(r"^[a-f0-9]{32}$")


def default_journal_root():
    configured = os.environ.get("PRS_LOCAL_WORKSPACE")
    local_workspace = (
        Path(configured).expanduser().resolve()
        if configured
        else PROJECT_ROOT.parent / f"{PROJECT_ROOT.name} Local"
    )
    return local_workspace / "Camera Lab" / "Guarded Runs"


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SessionJournal:
    def __init__(self, root=None):
        self.root = Path(root).expanduser().resolve() if root else default_journal_root()

    def create(self, record):
        payload = dict(record)
        payload["session_id"] = uuid.uuid4().hex
        payload["created_at"] = utc_now()
        payload["updated_at"] = payload["created_at"]
        self.save(payload)
        return payload

    def save(self, record):
        session_id = self._session_id(record.get("session_id"))
        payload = dict(record)
        payload["updated_at"] = utc_now()
        self.root.mkdir(parents=True, exist_ok=True)
        destination = self.root / f"{session_id}.json"
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.root, prefix=".guarded-run-", delete=False
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            staged = Path(handle.name)
        staged.replace(destination)
        return payload

    def load(self, session_id):
        path = self.root / f"{self._session_id(session_id)}.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ValueError(f"Guarded-run session not found: {session_id}") from exc
        if not isinstance(payload, dict) or payload.get("session_id") != session_id:
            raise ValueError("Guarded-run journal is invalid.")
        return payload

    def latest_resumable(self, backend=None):
        if not self.root.is_dir():
            return None
        candidates = []
        for path in self.root.glob("*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if (
                payload.get("status") in {"planned", "confirmed", "in_progress", "failed", "blocked"}
                and (backend is None or payload.get("backend") == backend)
            ):
                candidates.append(payload)
        return max(candidates, key=lambda item: item.get("updated_at", ""), default=None)

    @staticmethod
    def public_summary(record):
        if not record:
            return None
        return {
            "session_id": record.get("session_id"),
            "profile": record.get("profile"),
            "status": record.get("status"),
            "current_step": record.get("current_step", 0),
            "step_count": len(record.get("steps") or []),
            "updated_at": record.get("updated_at"),
        }

    @staticmethod
    def _session_id(value):
        if not isinstance(value, str) or not SESSION_ID.fullmatch(value):
            raise ValueError("Guarded-run session ID is invalid.")
        return value
