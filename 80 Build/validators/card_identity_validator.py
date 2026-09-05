from collections import Counter
from uuid import UUID

from profile_pack import valid_application_profile_reference_ids

from .common import error, load_yaml_checked, resolved_paths


def _valid_uuid(value):
    if not isinstance(value, str):
        return False
    try:
        return str(UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def validate(paths_or_root):
    paths = resolved_paths(paths_or_root)
    root = paths.application_root
    issues = []
    cards = {}
    titles = {}
    ids = []
    for path in sorted(paths.profiles_dir.glob("*.yaml")):
        try:
            profile = load_yaml_checked(path) or {}
        except Exception:
            continue
        card_id = profile.get("card_id")
        if not _valid_uuid(card_id):
            issues.append(error("card_identity", path, "card_id must be a canonical UUID."))
            continue
        ids.append(card_id)
        cards[card_id] = (path, profile)
        title = profile.get("title")
        if isinstance(title, str):
            titles[title] = card_id
    for duplicate, count in Counter(ids).items():
        if count > 1:
            issues.append(error("card_identity", paths.profiles_dir, f"Duplicate card_id: {duplicate}"))

    for card_id, (path, profile) in cards.items():
        setup = ((profile.get("card") or {}).get("field_setup") or {})
        source_id = setup.get("source_card_id") if isinstance(setup, dict) else None
        if source_id is not None and source_id not in cards:
            issues.append(error("card_identity", path, f"source_card_id references missing card: {source_id}"))
        if isinstance(setup, dict) and "source_profile" in setup:
            issues.append(error("card_identity", path, "Use source_card_id instead of legacy source_profile."))

    for path in (
        paths.controls_file,
        root / "data/canon_r5_custom_controls_current.yaml",
    ):
        try:
            source = load_yaml_checked(path) or {}
        except Exception:
            continue
        modes = source.get("custom_shooting_modes") or {}
        for mode in ("C1", "C2", "C3"):
            mapping = modes.get(mode) or {}
            profile_id = mapping.get("profile_id")
            if profile_id not in cards:
                issues.append(error("card_identity", path, f"{mode} profile_id references missing card: {profile_id}"))
            if "profile_title" in mapping:
                issues.append(error("card_identity", path, f"{mode} uses legacy profile_title instead of profile_id."))

    manifest_path = root / "50 Field Guide" / "required_appendices.yaml"
    valid_appendix_profile_ids = valid_application_profile_reference_ids(paths)
    try:
        manifest = load_yaml_checked(manifest_path) or {}
    except Exception:
        manifest = {}
    for entry in manifest.get("appendices", []) or []:
        if not isinstance(entry, dict):
            continue
        if "profiles" in entry:
            issues.append(error("card_identity", manifest_path, f"Appendix {entry.get('id')} uses legacy profiles instead of profile_ids."))
        for profile_id in entry.get("profile_ids", []) or []:
            if profile_id not in valid_appendix_profile_ids:
                issues.append(error("card_identity", manifest_path, f"Appendix {entry.get('id')} references missing card_id: {profile_id}"))
    return issues
