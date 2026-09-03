"""Persist and resolve Profile Editor pack choices in machine-local state."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from asset_manager import application_local_workspace
from profile_pack import ProfilePackError, resolve_profile_pack


SELECTION_VERSION = 1
EMBEDDED_PACK_ID = "embedded"


class ProfilePackSelectionError(RuntimeError):
    """Raised when saved Profile Editor pack selection cannot be trusted."""


class ProfilePackSelectionStore:
    """Own one checkout's private, machine-local profile-pack registry."""

    def __init__(self, application_root):
        self.application_root = Path(application_root).resolve()
        self.path = (
            application_local_workspace(self.application_root)
            / "Profile Packs"
            / "editor-selection.json"
        )

    def selected_context(self):
        data = self._load()
        selected = data["selected_pack_id"]
        if selected is None:
            return resolve_profile_pack(self.application_root)
        record = next((item for item in data["packs"] if item["pack_id"] == selected), None)
        if record is None:
            raise ProfilePackSelectionError(
                "The saved profile-pack selection has no matching registered pack. "
                "Start once with --embedded to choose another pack."
            )
        return self._resolve_record(record, selected=True)

    def select_path(self, root):
        context = self.resolve_path(root)
        self.remember_selected(context)
        return context

    def resolve_path(self, root):
        try:
            return resolve_profile_pack(self.application_root, explicit_root=root)
        except ProfilePackError as exc:
            raise ProfilePackSelectionError(str(exc)) from exc

    def remember_selected(self, context):
        try:
            data = self._load()
        except ProfilePackSelectionError:
            # This method is reached only after an explicit pack selection has
            # resolved successfully. Let that confirmed action repair corrupt
            # machine-local state without weakening fail-closed startup.
            data = self._empty()
        if context.mode == "embedded":
            data["selected_pack_id"] = None
            self._write(data)
            return
        record = {"pack_id": context.pack_id, "root": str(context.root)}
        data["packs"] = [
            item
            for item in data["packs"]
            if item["pack_id"] != context.pack_id and item["root"] != str(context.root)
        ]
        data["packs"].append(record)
        data["packs"].sort(key=lambda item: item["pack_id"])
        data["selected_pack_id"] = context.pack_id
        self._write(data)

    def select_registered(self, pack_id):
        context = self.resolve_registered(pack_id)
        self.remember_selected(context)
        return context

    def resolve_registered(self, pack_id):
        if pack_id == EMBEDDED_PACK_ID:
            return resolve_profile_pack(self.application_root)
        data = self._load()
        record = next((item for item in data["packs"] if item["pack_id"] == pack_id), None)
        if record is None:
            raise ProfilePackSelectionError("The selected profile pack is not registered on this Mac.")
        return self._resolve_record(record, selected=False)

    def select_embedded(self):
        context = resolve_profile_pack(self.application_root)
        self.remember_selected(context)
        return context

    def catalog(self, current_context):
        """Return path-free live labels for the chooser."""
        try:
            data = self._load()
        except ProfilePackSelectionError:
            # Recovery launches still need a usable chooser. Do not trust or
            # expose any record from an invalid registry.
            data = self._empty()
        entries = [
            {
                "pack_id": EMBEDDED_PACK_ID,
                "pack_name": "Embedded Canon EOS R5 sources",
                "mode": "embedded",
                "available": True,
                "active": current_context.mode == "embedded",
                "remembered": True,
            }
        ]
        seen = set()
        for record in data["packs"]:
            pack_id = record["pack_id"]
            seen.add(pack_id)
            try:
                context = self._resolve_record(record, selected=False)
                entries.append(
                    {
                        "pack_id": pack_id,
                        "pack_name": context.pack_name,
                        "mode": "external",
                        "available": True,
                        "active": current_context.mode == "external" and current_context.pack_id == pack_id,
                        "remembered": True,
                    }
                )
            except ProfilePackSelectionError:
                entries.append(
                    {
                        "pack_id": pack_id,
                        "pack_name": f"Unavailable profile pack · {pack_id[:8]}",
                        "mode": "external",
                        "available": False,
                        "active": current_context.mode == "external" and current_context.pack_id == pack_id,
                        "remembered": True,
                    }
                )
        if current_context.mode == "external" and current_context.pack_id not in seen:
            entries.append(
                {
                    "pack_id": current_context.pack_id,
                    "pack_name": current_context.pack_name,
                    "mode": "external",
                    "available": True,
                    "active": True,
                    "remembered": False,
                }
            )
        return {"packs": entries}

    def _resolve_record(self, record, selected):
        try:
            context = resolve_profile_pack(
                self.application_root,
                explicit_root=record["root"],
            )
        except ProfilePackError as exc:
            prefix = "Saved" if selected else "Remembered"
            raise ProfilePackSelectionError(
                f"{prefix} profile pack is unavailable or invalid: {exc}"
            ) from exc
        if context.pack_id != record["pack_id"]:
            raise ProfilePackSelectionError(
                "The profile pack at a remembered location has a different identity."
            )
        return context

    def _load(self):
        if not self.path.exists():
            return self._empty()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ProfilePackSelectionError(
                "The machine-local profile-pack selection is unreadable. "
                "Start once with --embedded to repair the selection."
            ) from exc
        if not isinstance(data, dict) or set(data) != {"version", "selected_pack_id", "packs"}:
            raise ProfilePackSelectionError("The machine-local profile-pack selection has an invalid shape.")
        if data["version"] != SELECTION_VERSION or not isinstance(data["packs"], list):
            raise ProfilePackSelectionError("The machine-local profile-pack selection version is unsupported.")
        selected = data["selected_pack_id"]
        if selected is not None and not isinstance(selected, str):
            raise ProfilePackSelectionError("The saved profile-pack identity is invalid.")
        normalized = []
        seen_ids = set()
        seen_roots = set()
        for record in data["packs"]:
            if not isinstance(record, dict) or set(record) != {"pack_id", "root"}:
                raise ProfilePackSelectionError("A remembered profile-pack entry has an invalid shape.")
            pack_id = record["pack_id"]
            root = record["root"]
            if not isinstance(pack_id, str) or not isinstance(root, str) or not Path(root).is_absolute():
                raise ProfilePackSelectionError("A remembered profile-pack entry is invalid.")
            canonical = str(Path(root).expanduser().resolve())
            if pack_id in seen_ids or canonical in seen_roots:
                raise ProfilePackSelectionError("The machine-local profile-pack selection contains duplicates.")
            seen_ids.add(pack_id)
            seen_roots.add(canonical)
            normalized.append({"pack_id": pack_id, "root": canonical})
        return {"version": SELECTION_VERSION, "selected_pack_id": selected, "packs": normalized}

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".editor-selection-",
            suffix=".json.tmp",
            dir=self.path.parent,
        )
        temporary = Path(temporary_name)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(data, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(self.path)
            directory = os.open(self.path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            temporary.unlink(missing_ok=True)
            raise

    @staticmethod
    def _empty():
        return {"version": SELECTION_VERSION, "selected_pack_id": None, "packs": []}
