"""Resolve embedded or external private profile-pack source safely."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
from types import MappingProxyType
from uuid import UUID

import yaml


MANIFEST_FILENAME = "profile-pack.yaml"
MANIFEST_VERSION = 1
PROFILE_PACK_CONTRACT = 1
APPLICATION_PROJECT_ID = "canon-eos-r5-camera-reference"
EXPECTED_APPLICATION_IDENTITY = {
    "schema_version": 1,
    "project_id": APPLICATION_PROJECT_ID,
    "project_name": "Canon EOS R5 Camera Reference",
    "repository_role": "authoritative-source",
    "artifact_type": "source-repository",
}
EXPECTED_CAMERA = {"manufacturer": "Canon", "model": "EOS R5"}

SOURCE_PATHS = {
    "baseline": "00 Master/baseline.yaml",
    "profiles": "10 Profiles",
    "my_menu": "00 Master/my_menu.yaml",
    "my_menu_colors": "00 Master/my_menu_colors.yaml",
    "profile_lens_guidance": "00 Master/profile_lens_guidance.yaml",
    "owned_equipment": "data/owned_equipment.yaml",
    "controls": "controls.yaml",
    "registration_targets": "90 Testing/eos_r5_registration_targets.yaml",
    "verification_status": "90 Testing/eos_r5_verification_status.yaml",
}

# Embedded transition mode deliberately maps mixed legacy sources without moving them.
EMBEDDED_SOURCE_PATHS = {
    **SOURCE_PATHS,
    "owned_equipment": "data/stabilization_reference.yaml",
    "registration_targets": "90 Testing/eos_r5_verification_tracker.yaml",
}

REQUIRED_TOP_LEVEL_KEYS = {
    "manifest_version",
    "pack_id",
    "pack_name",
    "repository_role",
    "artifact_type",
    "camera",
    "compatibility",
    "sources",
    "publication",
}
REQUIRED_COMPATIBILITY_KEYS = {
    "application_project_id",
    "profile_pack_contract",
}
REQUIRED_PUBLICATION_KEYS = {"default_profile_policy"}
PROHIBITED_COMPONENT_PATTERNS = (
    re.compile(r"(?:^| )old(?: |$)"),
    re.compile(r"(?:^| )backups?(?: |$)"),
    re.compile(r"(?:^| )archives?(?: |$)"),
    re.compile(r"(?:^| )build output(?: |$)"),
    re.compile(r"(?:^| )generated(?: outputs?)?(?: |$)"),
    re.compile(r"(?:^| )native wrapper(?: |$)"),
)


class ProfilePackError(RuntimeError):
    """Raised when a profile pack cannot be resolved safely."""


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ProfilePackError("Profile-pack manifest keys must be scalar values.") from exc
        if duplicate:
            raise ProfilePackError(f"Duplicate manifest key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class ProfilePackContext:
    """One resolved source context without authority over either Git repository."""

    application_root: Path
    root: Path
    mode: str
    pack_id: str
    pack_name: str
    manifest: object
    sources: object

    def source(self, key):
        try:
            return self.sources[key]
        except KeyError as exc:
            raise ProfilePackError(f"Unknown profile-pack source key: {key}") from exc

    def fingerprint(self):
        """Hash the manifest contract and exact canonical source bytes."""
        digest = hashlib.sha256()
        if self.mode == "external":
            _hash_item(digest, MANIFEST_FILENAME, self.root / MANIFEST_FILENAME)
        else:
            embedded_manifest = {
                "mode": "embedded-compatibility",
                "application_project_id": APPLICATION_PROJECT_ID,
                "profile_pack_contract": PROFILE_PACK_CONTRACT,
                "sources": EMBEDDED_SOURCE_PATHS,
            }
            digest.update(json.dumps(embedded_manifest, sort_keys=True, separators=(",", ":")).encode("utf-8"))
            digest.update(b"\0")

        for key in sorted(self.sources):
            source = self.sources[key]
            if not source.exists():
                raise ProfilePackError(f"Profile-pack source is missing: {key} ({source})")
            _require_contained_path(self.root, source, key)
            if source.is_dir():
                files = sorted(
                    (path for path in source.rglob("*") if path.is_file()),
                    key=lambda path: path.relative_to(self.root).as_posix(),
                )
                for path in files:
                    _require_contained_path(self.root, path, key)
                    _hash_item(digest, f"{key}/{path.relative_to(self.root).as_posix()}", path)
            elif source.is_file():
                _hash_item(digest, f"{key}/{source.relative_to(self.root).as_posix()}", source)
            else:
                raise ProfilePackError(f"Profile-pack source is not a regular file or directory: {source}")
        return digest.hexdigest()


def resolve_profile_pack(application_root, explicit_root=None):
    """Return external context when explicitly selected, otherwise embedded compatibility."""
    application_root = Path(application_root).resolve()
    if explicit_root is None:
        sources = {
            key: application_root / relative
            for key, relative in EMBEDDED_SOURCE_PATHS.items()
        }
        return ProfilePackContext(
            application_root=application_root,
            root=application_root,
            mode="embedded",
            pack_id=f"embedded:{APPLICATION_PROJECT_ID}",
            pack_name="Embedded Canon EOS R5 sources",
            manifest=None,
            sources=MappingProxyType(sources),
        )
    return _load_external_profile_pack(application_root, explicit_root)


def build_provenance(context):
    """Return path-free revision evidence for one external combined build."""
    if context.mode != "external":
        raise ProfilePackError("Combined build provenance requires an external profile pack.")
    return {
        "schema_version": 1,
        "application": _repository_state(context.application_root),
        "profile_pack": {
            **_repository_state(context.root),
            "pack_id": context.pack_id,
            "manifest_version": MANIFEST_VERSION,
            "contract_version": PROFILE_PACK_CONTRACT,
            "pack_fingerprint": context.fingerprint(),
        },
    }


def profile_pack_revision(context):
    """Return path-free repository identity for backups and guarded transactions."""
    fingerprint = context.fingerprint()
    state = (
        _repository_state(context.root)
        if context.mode == "external"
        else {"commit": None, "dirty_source_fingerprint": fingerprint}
    )
    return {
        "mode": context.mode,
        "pack_id": context.pack_id,
        "pack_name": context.pack_name,
        "commit": state["commit"],
        "dirty_source_fingerprint": state["dirty_source_fingerprint"],
        "pack_fingerprint": fingerprint,
    }


def write_build_provenance(context, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_provenance(context), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def _load_external_profile_pack(application_root, explicit_root):
    root = Path(explicit_root).expanduser().resolve()
    _require_disjoint_roots(application_root, root)
    _require_acceptable_root(root)
    _require_git_root(application_root, "Application")
    _require_git_root(root, "Profile-pack")
    manifest_path = root / MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise ProfilePackError(f"Profile-pack manifest is missing: {manifest_path}")
    _require_contained_path(root, manifest_path, "manifest")
    try:
        manifest = yaml.load(manifest_path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except ProfilePackError:
        raise
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ProfilePackError(f"Could not read profile-pack manifest: {exc}") from exc
    _validate_manifest(manifest)
    _validate_application_identity(application_root, manifest)

    sources = {}
    for key, expected_relative in SOURCE_PATHS.items():
        declared = manifest["sources"][key]
        if declared != expected_relative:
            raise ProfilePackError(
                f"Manifest source '{key}' must be '{expected_relative}' for contract version 1."
            )
        source = _resolve_declared_source(root, declared, key)
        if key == "profiles":
            if not source.is_dir():
                raise ProfilePackError(f"Profile-pack source '{key}' must be a directory: {source}")
            if not any(source.glob("*.yaml")):
                raise ProfilePackError(f"Profile-pack source '{key}' contains no YAML profiles: {source}")
            _require_contained_source_tree(root, source, key)
        elif not source.is_file():
            raise ProfilePackError(f"Profile-pack source '{key}' must be a file: {source}")
        sources[key] = source

    return ProfilePackContext(
        application_root=application_root,
        root=root,
        mode="external",
        pack_id=manifest["pack_id"],
        pack_name=manifest["pack_name"],
        manifest=MappingProxyType(manifest),
        sources=MappingProxyType(sources),
    )


def _validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise ProfilePackError("Profile-pack manifest must be a mapping.")
    _require_exact_keys("manifest", manifest, REQUIRED_TOP_LEVEL_KEYS)
    version = manifest["manifest_version"]
    if version != MANIFEST_VERSION or isinstance(version, bool):
        raise ProfilePackError(f"Unsupported profile-pack manifest version: {version}")
    try:
        pack_uuid = UUID(str(manifest["pack_id"]))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ProfilePackError("Profile-pack ID must be a UUID.") from exc
    if pack_uuid.int == 0:
        raise ProfilePackError("Profile-pack ID must not be the all-zero UUID.")
    if not isinstance(manifest["pack_id"], str):
        raise ProfilePackError("Profile-pack ID must be a UUID string.")
    pack_name = manifest["pack_name"]
    if not isinstance(pack_name, str) or not pack_name.strip():
        raise ProfilePackError("Profile-pack name must be a non-empty string.")
    if (
        pack_name != pack_name.strip()
        or len(pack_name) > 80
        or any(ord(character) < 32 for character in pack_name)
        or "/" in pack_name
        or "\\" in pack_name
    ):
        raise ProfilePackError(
            "Profile-pack name must be a user-friendly label without paths, control characters, or surrounding whitespace."
        )
    if manifest["repository_role"] != "private-profile-pack":
        raise ProfilePackError("Profile-pack repository_role must be private-profile-pack.")
    if manifest["artifact_type"] != "source-repository":
        raise ProfilePackError("Profile-pack artifact_type must be source-repository.")
    if manifest["camera"] != EXPECTED_CAMERA:
        raise ProfilePackError("Profile-pack camera must be Canon EOS R5.")

    compatibility = manifest["compatibility"]
    if not isinstance(compatibility, dict):
        raise ProfilePackError("Profile-pack compatibility must be a mapping.")
    _require_exact_keys("compatibility", compatibility, REQUIRED_COMPATIBILITY_KEYS)
    if compatibility["application_project_id"] != APPLICATION_PROJECT_ID:
        raise ProfilePackError(
            f"Profile pack requires application project {APPLICATION_PROJECT_ID}."
        )
    contract = compatibility["profile_pack_contract"]
    if contract != PROFILE_PACK_CONTRACT or isinstance(contract, bool):
        raise ProfilePackError(f"Unsupported profile-pack contract version: {contract}")

    sources = manifest["sources"]
    if not isinstance(sources, dict):
        raise ProfilePackError("Profile-pack sources must be a mapping.")
    _require_exact_keys("sources", sources, set(SOURCE_PATHS))
    for key, value in sources.items():
        if not isinstance(value, str) or not value.strip():
            raise ProfilePackError(f"Profile-pack source '{key}' must be a non-empty relative path.")

    publication = manifest["publication"]
    if not isinstance(publication, dict):
        raise ProfilePackError("Profile-pack publication must be a mapping.")
    _require_exact_keys("publication", publication, REQUIRED_PUBLICATION_KEYS)
    if publication["default_profile_policy"] != "explicit-release-only":
        raise ProfilePackError("Profile-pack publication policy must be explicit-release-only.")


def _validate_application_identity(application_root, manifest):
    identity_path = application_root / "00 Master" / "project_identity.yaml"
    if not identity_path.is_file():
        raise ProfilePackError(f"Application identity is missing: {identity_path}")
    try:
        identity = yaml.safe_load(identity_path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ProfilePackError(f"Could not read application identity: {exc}") from exc
    for key, expected in EXPECTED_APPLICATION_IDENTITY.items():
        if identity.get(key) != expected:
            raise ProfilePackError(f"Selected application has unexpected {key} identity.")
    if identity.get("camera") != manifest["camera"]:
        raise ProfilePackError("Profile-pack and application camera identities do not match.")


def _require_exact_keys(label, mapping, required):
    actual = set(mapping)
    missing = sorted(required - actual)
    unknown = sorted(actual - required)
    if missing:
        raise ProfilePackError(f"Profile-pack {label} is missing keys: {', '.join(missing)}")
    if unknown:
        raise ProfilePackError(f"Profile-pack {label} has unknown keys: {', '.join(unknown)}")


def _resolve_declared_source(root, declared, key):
    relative = Path(declared)
    if relative.is_absolute() or ".." in relative.parts:
        raise ProfilePackError(f"Profile-pack source '{key}' must stay inside the pack root.")
    source = root / relative
    if not source.exists():
        raise ProfilePackError(f"Profile-pack source is missing: {key} ({source})")
    _require_contained_path(root, source, key)
    return source


def _require_contained_path(root, source, key):
    try:
        resolved = source.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ProfilePackError(f"Profile-pack source '{key}' cannot be resolved safely: {source}") from exc
    if resolved != root and root not in resolved.parents:
        raise ProfilePackError(f"Profile-pack source '{key}' escapes the pack root: {source}")


def _require_acceptable_root(root):
    if not root.is_dir():
        raise ProfilePackError(f"Profile-pack root is not a directory: {root}")
    for component in root.parts:
        normalized = re.sub(r"[_-]+", " ", component).casefold().strip()
        if any(pattern.search(normalized) for pattern in PROHIBITED_COMPONENT_PATTERNS):
            raise ProfilePackError(f"Profile-pack root has a prohibited path component: {component}")


def _require_disjoint_roots(application_root, pack_root):
    if (
        application_root == pack_root
        or application_root in pack_root.parents
        or pack_root in application_root.parents
    ):
        raise ProfilePackError("Application and profile-pack roots must be separate, non-nested repositories.")


def _require_contained_source_tree(root, directory, key):
    for path in directory.rglob("*"):
        if path.is_symlink() or path.is_file():
            _require_contained_path(root, path, key)


def _require_git_root(root, label):
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProfilePackError(f"Could not verify {label.lower()} Git root: {exc}") from exc
    if completed.returncode or not completed.stdout.strip():
        raise ProfilePackError(f"{label} root is not a Git repository: {root}")
    if Path(completed.stdout.strip()).resolve() != root:
        raise ProfilePackError(f"Selected {label.lower()} root does not match its Git root: {root}")


def _hash_item(digest, label, path):
    digest.update(label.encode("utf-8"))
    digest.update(b"\0")
    digest.update(path.read_bytes())
    digest.update(b"\0")


def _repository_state(root):
    root = Path(root)
    commit = _git_output(root, ["rev-parse", "--verify", "HEAD"], allow_failure=True)
    status = _git_output(
        root,
        ["status", "--porcelain=v1", "--untracked-files=all"],
        allow_failure=False,
    )
    state = {"commit": commit or None}
    if status or not commit:
        digest = hashlib.sha256()
        listed = _git_output(
            root,
            ["ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            allow_failure=False,
        )
        for relative in sorted(item for item in listed.split("\0") if item):
            path = root / relative
            if path.is_file():
                _hash_item(digest, relative, path)
        state["dirty_source_fingerprint"] = digest.hexdigest()
    else:
        state["dirty_source_fingerprint"] = None
    return state


def _git_output(root, arguments, allow_failure):
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if completed.returncode:
        if allow_failure:
            return ""
        raise ProfilePackError(f"Could not inspect repository state: {' '.join(arguments)}")
    return completed.stdout.strip()
