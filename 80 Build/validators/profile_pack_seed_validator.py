"""Validate the minimum editable starter-card contract for external packs."""

from profile_pack import REQUIRED_STARTER_CARD_IDS

from .common import error, load_yaml_checked, resolved_paths


def validate(paths_or_root):
    paths = resolved_paths(paths_or_root)
    if paths.profile_pack.mode != "external":
        return []
    active = {}
    for source in sorted(paths.profiles_dir.glob("*.yaml")):
        try:
            profile = load_yaml_checked(source) or {}
        except Exception:
            continue
        card_id = profile.get("card_id")
        if isinstance(card_id, str):
            active[card_id] = source
    missing = sorted(REQUIRED_STARTER_CARD_IDS - set(active))
    if not missing:
        return []
    return [
        error(
            "profile_pack_seed",
            paths.profiles_dir,
            "External profile pack is missing required baseline-support cards: "
            + ", ".join(missing),
        )
    ]
