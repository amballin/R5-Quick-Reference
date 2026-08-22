from collections import Counter
from uuid import UUID

from .common import error, load_yaml_checked


def _valid_uuid(value):
    if not isinstance(value, str):
        return False
    try:
        return str(UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def validate(root):
    issues = []
    cards = {}
    titles = {}
    ids = []
    for path in sorted((root / "10 Profiles").glob("*.yaml")):
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
            issues.append(error("card_identity", root / "10 Profiles", f"Duplicate card_id: {duplicate}"))

    for card_id, (path, profile) in cards.items():
        setup = ((profile.get("card") or {}).get("field_setup") or {})
        source_id = setup.get("source_card_id") if isinstance(setup, dict) else None
        if source_id is not None and source_id not in cards:
            issues.append(error("card_identity", path, f"source_card_id references missing card: {source_id}"))
        if isinstance(setup, dict) and "source_profile" in setup:
            issues.append(error("card_identity", path, "Use source_card_id instead of legacy source_profile."))

    for relative in ("controls.yaml", "data/canon_r5_custom_controls_current.yaml"):
        path = root / relative
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
            if profile_id not in cards:
                issues.append(error("card_identity", manifest_path, f"Appendix {entry.get('id')} references missing card_id: {profile_id}"))
    return issues
