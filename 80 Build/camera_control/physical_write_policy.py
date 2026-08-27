"""Body-scoped, machine-local evidence for guarded EOS R5 setting writes."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from .capability_mapping import load_catalog


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_METHOD = "sdk_written_and_verified"


def local_workspace():
    configured = os.environ.get("PRS_LOCAL_WORKSPACE")
    return (
        Path(configured).expanduser().resolve()
        if configured
        else PROJECT_ROOT.parent / f"{PROJECT_ROOT.name} Local"
    )


def default_evidence_path():
    return local_workspace() / "Camera Lab" / "Physical Write Evidence.json"


def qualification_candidates():
    return {
        item["key"]: item
        for item in load_catalog().get("properties") or []
        if item.get("write_qualification_candidate") is True
    }


class PhysicalWriteEvidence:
    """Persist exact verified values for one body, firmware, and SDK context."""

    def __init__(self, path=None):
        self.path = Path(path).expanduser().resolve() if path else default_evidence_path()

    def load(self):
        if not self.path.is_file():
            return {"schema_version": 1, "entries": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("Physical-write evidence file is unreadable or invalid.") from exc
        if payload.get("schema_version") != 1 or not isinstance(payload.get("entries"), list):
            raise ValueError("Physical-write evidence file has an unsupported schema.")
        return payload

    @staticmethod
    def context(camera, sdk):
        return {
            "product_name": camera.get("product_name"),
            "body_id": camera.get("body_id"),
            "firmware_version": camera.get("firmware_version"),
            "edsdk_framework_version": sdk.get("framework_version"),
        }

    def verified_values(self, camera, sdk, property_key):
        context = self.context(camera, sdk)
        values = set()
        for entry in self.load()["entries"]:
            if (
                entry.get("context") == context
                and entry.get("property_key") == property_key
                and entry.get("evidence_method") == EVIDENCE_METHOD
            ):
                values.update(int(value) for value in entry.get("verified_values_raw") or [])
        return values

    def supports(self, camera, sdk, property_key, value_raw):
        return int(value_raw) in self.verified_values(camera, sdk, property_key)

    def record(self, camera, sdk, property_key, values, journal_id):
        payload = self.load()
        context = self.context(camera, sdk)
        entry = next(
            (
                item
                for item in payload["entries"]
                if item.get("context") == context and item.get("property_key") == property_key
            ),
            None,
        )
        verified = sorted(
            {int(value) for value in values}
            | {int(value) for value in (entry or {}).get("verified_values_raw") or []}
        )
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if entry is None:
            entry = {"context": context, "property_key": property_key}
            payload["entries"].append(entry)
        entry.update(
            {
                "verified_values_raw": verified,
                "evidence_method": EVIDENCE_METHOD,
                "qualification_journal_id": journal_id,
                "verified_at": now,
            }
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.path.parent, prefix=".physical-write-evidence-", delete=False
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            staged = Path(handle.name)
        staged.replace(self.path)
        return entry

    def public_summary(self, camera=None, sdk=None):
        payload = self.load()
        entries = payload["entries"]
        if camera is not None and sdk is not None:
            context = self.context(camera, sdk)
            entries = [entry for entry in entries if entry.get("context") == context]
        return {
            "evidence_path": str(self.path),
            "qualified_properties": len(entries),
            "qualified_values": sum(len(entry.get("verified_values_raw") or []) for entry in entries),
        }
