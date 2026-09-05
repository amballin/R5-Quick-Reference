"""Validate the exact owner-controlled application profile catalog boundary."""

from pathlib import Path
from uuid import UUID

from .common import error, load_yaml_checked, resolved_paths


POLICY_RELATIVE = Path("00 Master/profile_catalog_policy.yaml")
EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "authority",
    "identity_field",
    "protected_sources",
    "profiles",
}
EXPECTED_PROTECTED_SOURCES = {
    "policy": "00 Master/profile_catalog_policy.yaml",
    "profile_directory": "10 Profiles",
    "lens_guidance": "00 Master/profile_lens_guidance.yaml",
}


def validate(paths_or_root):
    paths = resolved_paths(paths_or_root)
    root = paths.application_root
    policy_path = root / POLICY_RELATIVE
    issues = []
    try:
        policy = load_yaml_checked(policy_path)
    except Exception as exc:
        return [error("profile_catalog_policy", policy_path, f"Catalog policy is unreadable: {exc}")]
    if not isinstance(policy, dict):
        return [error("profile_catalog_policy", policy_path, "Catalog policy must be a mapping.")]
    if set(policy) != EXPECTED_TOP_LEVEL_KEYS:
        return [error("profile_catalog_policy", policy_path, "Catalog policy fields are incomplete or unexpected.")]
    if policy.get("schema_version") != 1 or isinstance(policy.get("schema_version"), bool):
        issues.append(error("profile_catalog_policy", policy_path, "Catalog policy requires schema_version 1."))
    if policy.get("authority") != "owner_application_fork":
        issues.append(error("profile_catalog_policy", policy_path, "Catalog authority must remain owner_application_fork."))
    if policy.get("identity_field") != "card_id":
        issues.append(error("profile_catalog_policy", policy_path, "Catalog identity must remain the immutable card_id."))
    if policy.get("protected_sources") != EXPECTED_PROTECTED_SOURCES:
        issues.append(error("profile_catalog_policy", policy_path, "Protected catalog source paths changed unexpectedly."))

    entries = policy.get("profiles")
    if not isinstance(entries, list) or not entries:
        issues.append(error("profile_catalog_policy", policy_path, "Catalog policy must list protected profiles."))
        return issues
    filenames = [entry.get("filename") for entry in entries if isinstance(entry, dict)]
    if filenames != sorted(filenames, key=lambda value: str(value).casefold()):
        issues.append(error("profile_catalog_policy", policy_path, "Catalog entries must remain in filename order."))
    expected = {}
    seen_ids = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"filename", "card_id"}:
            issues.append(error("profile_catalog_policy", policy_path, "Each catalog entry requires only filename and card_id."))
            continue
        filename = entry.get("filename")
        card_id = entry.get("card_id")
        if (
            not isinstance(filename, str)
            or Path(filename).name != filename
            or not filename.endswith(".yaml")
        ):
            issues.append(error("profile_catalog_policy", policy_path, f"Catalog filename is invalid: {filename}"))
            continue
        try:
            UUID(card_id)
        except (TypeError, ValueError, AttributeError):
            issues.append(error("profile_catalog_policy", policy_path, f"Catalog card_id is invalid for {filename}."))
            continue
        if filename in expected:
            issues.append(error("profile_catalog_policy", policy_path, f"Duplicate catalog filename: {filename}"))
        if card_id in seen_ids:
            issues.append(error("profile_catalog_policy", policy_path, f"Duplicate catalog card_id: {card_id}"))
        expected[filename] = card_id
        seen_ids.add(card_id)

    profiles_dir = root / EXPECTED_PROTECTED_SOURCES["profile_directory"]
    actual_paths = sorted(profiles_dir.rglob("*.yaml"))
    actual_relatives = {path.relative_to(profiles_dir).as_posix() for path in actual_paths}
    expected_names = set(expected)
    missing = sorted(expected_names - actual_relatives)
    extra = sorted(actual_relatives - expected_names)
    if missing:
        issues.append(error("profile_catalog_policy", profiles_dir, "Protected catalog files are missing or moved: " + ", ".join(missing)))
    if extra:
        issues.append(error("profile_catalog_policy", profiles_dir, "Unregistered catalog files are present: " + ", ".join(extra)))
    for filename in sorted(expected_names & actual_relatives):
        source = profiles_dir / filename
        try:
            profile = load_yaml_checked(source) or {}
        except Exception:
            continue
        if not isinstance(profile, dict) or profile.get("card_id") != expected[filename]:
            issues.append(error("profile_catalog_policy", source, "Catalog filename and protected card_id do not match the policy."))

    guidance_path = root / EXPECTED_PROTECTED_SOURCES["lens_guidance"]
    try:
        guidance = load_yaml_checked(guidance_path) or {}
    except Exception:
        return issues
    if not isinstance(guidance, dict) or not isinstance(guidance.get("profiles"), list):
        issues.append(error("profile_catalog_policy", guidance_path, "Protected lens guidance must contain a profiles list."))
        return issues
    guidance_ids = [entry.get("card_id") for entry in guidance["profiles"] if isinstance(entry, dict)]
    unknown_guidance = sorted({card_id for card_id in guidance_ids if card_id not in seen_ids})
    if unknown_guidance:
        issues.append(error("profile_catalog_policy", guidance_path, "Lens guidance references card IDs outside the protected catalog: " + ", ".join(unknown_guidance)))
    return issues
