"""Machine-local, session-scoped manual setting confirmations for Camera Lab."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile

from .session_journal import default_journal_root, utc_now


def default_confirmation_path():
    return default_journal_root().parent / "Manual Confirmations.json"


def _text(value):
    return str(value or "").strip()


def _normalized(value):
    return " ".join(_text(value).casefold().split())


class ManualConfirmationLedger:
    """Persist exact manual evidence without treating it as SDK verification."""

    def __init__(self, path=None):
        self.path = Path(path).expanduser().resolve() if path else default_confirmation_path()

    def record_group(self, run, steps, camera_session_id, current_mode):
        payload = self._load()
        confirmations = payload["confirmations"]
        camera = self._camera_scope(run.get("camera") or {})
        context_source = dict(run.get("preflight") or {})
        equipment = run.get("equipment") or {}
        context_source.update(
            selected_lens_id=equipment.get("selected_lens_id"),
            selected_accessory_id=equipment.get("selected_accessory_id"),
            selected_is_mode=(equipment.get("stabilization") or {}).get("selected_mode"),
        )
        context = self._context_scope(context_source, current_mode)
        for step in steps:
            if step.get("status") not in {"manual_user_confirmed", "camera_verified"}:
                continue
            path = _text(step.get("path"))
            target = _text(step.get("target"))
            if not path or not target:
                continue
            confirmations[:] = [
                item for item in confirmations
                if not (
                    item.get("camera_session_id") == camera_session_id
                    and item.get("camera") == camera
                    and item.get("context") == context
                    and item.get("path") == path
                )
            ]
            confirmations.append(
                {
                    "camera_session_id": camera_session_id,
                    "camera": camera,
                    "context": context,
                    "path": path,
                    "label": _text(step.get("label")),
                    "target": target,
                    "target_normalized": _normalized(target),
                    "evidence_method": step.get("evidence_method") or "manual_group_user_confirmed",
                    "confirmed_at": step.get("completed_at") or utc_now(),
                    "guarded_run_session_id": run.get("session_id"),
                    "profile": (run.get("profile") or {}).get("name"),
                }
            )
        self._save(payload)

    def match(self, camera, camera_session_id, context, path, target):
        scope = self._camera_scope(camera)
        context_scope = self._context_scope(context, context.get("current_mode"))
        target_normalized = _normalized(target)
        matches = [
            item for item in self._load()["confirmations"]
            if item.get("camera_session_id") == camera_session_id
            and item.get("camera") == scope
            and item.get("context") == context_scope
            and item.get("path") == _text(path)
            and item.get("target_normalized") == target_normalized
        ]
        return deepcopy(max(matches, key=lambda item: item.get("confirmed_at", ""), default=None))

    def revoke(self, camera, camera_session_id, context, path, target):
        payload = self._load()
        before = len(payload["confirmations"])
        scope = self._camera_scope(camera)
        context_scope = self._context_scope(context, context.get("current_mode"))
        target_normalized = _normalized(target)
        payload["confirmations"] = [
            item for item in payload["confirmations"]
            if not (
                item.get("camera_session_id") == camera_session_id
                and item.get("camera") == scope
                and item.get("context") == context_scope
                and item.get("path") == _text(path)
                and item.get("target_normalized") == target_normalized
            )
        ]
        self._save(payload)
        return before - len(payload["confirmations"])

    @staticmethod
    def _camera_scope(camera):
        return {
            "product_name": _text(camera.get("product_name")),
            "body_id": _text(camera.get("body_id")),
            "firmware_version": _text(camera.get("firmware_version")),
            "lens_name": _text(camera.get("lens_name")),
        }

    @staticmethod
    def _context_scope(context, current_mode):
        return {
            "still_movie_context": _text(context.get("still_movie_context")),
            "current_mode": _text(current_mode),
            "flash": _text(context.get("flash")),
            "cards": _text(context.get("cards")),
            "selected_lens_id": _text(context.get("selected_lens_id")),
            "selected_accessory_id": _text(context.get("selected_accessory_id")),
            "selected_is_mode": _text(context.get("selected_is_mode")),
        }

    def _load(self):
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {"schema_version": 1, "confirmations": []}
        if payload.get("schema_version") != 1 or not isinstance(payload.get("confirmations"), list):
            return {"schema_version": 1, "confirmations": []}
        return payload

    def _save(self, payload):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.path.parent, prefix=".manual-confirmations-", delete=False
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            staged = Path(handle.name)
        staged.replace(self.path)
