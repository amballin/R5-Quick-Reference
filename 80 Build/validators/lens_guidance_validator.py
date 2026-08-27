import yaml

from .common import error


GUIDANCE = "00 Master/profile_lens_guidance.yaml"
EQUIPMENT = "data/stabilization_reference.yaml"
ROLES = {"primary", "alternative", "specialist"}


def validate(root):
    path = root / GUIDANCE
    equipment_path = root / EQUIPMENT
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        equipment = yaml.safe_load(equipment_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [error("lens_guidance", path, f"Lens guidance could not be read: {exc}")]
    issues = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return [error("lens_guidance", path, "Lens guidance must use schema_version 1.")]
    if data.get("camera") != {"manufacturer": "Canon", "model": "EOS R5"}:
        issues.append(error("lens_guidance", path, "Lens guidance must target Canon EOS R5 exactly."))
    profiles = _profile_index(root)
    subject_ids = {
        card_id
        for card_id, profile in profiles.items()
        if profile.get("card_type", "profile") == "profile"
        and profile.get("display_category", "subject") == "subject"
    }
    lenses = {item.get("id"): item for item in (equipment or {}).get("lenses") or []}
    accessories = {item.get("id"): item for item in (equipment or {}).get("accessories") or []}
    entries = data.get("profiles")
    if not isinstance(entries, list):
        return issues + [error("lens_guidance", path, "profiles must be a list.")]
    seen_profiles = set()
    for entry in entries:
        if not isinstance(entry, dict):
            issues.append(error("lens_guidance", path, "Every profile lens entry must be a mapping."))
            continue
        card_id = entry.get("card_id")
        if card_id not in subject_ids:
            issues.append(error("lens_guidance", path, f"Lens guidance references an unknown subject card_id: {card_id}"))
        if card_id in seen_profiles:
            issues.append(error("lens_guidance", path, f"Duplicate lens guidance card_id: {card_id}"))
        seen_profiles.add(card_id)
        choices = entry.get("choices")
        if not isinstance(choices, list) or not choices or len(choices) > 3:
            issues.append(error("lens_guidance", path, f"{card_id}: choices must contain one to three entries."))
            continue
        primary_count = sum(choice.get("role") == "primary" for choice in choices if isinstance(choice, dict))
        if primary_count != 1:
            issues.append(error("lens_guidance", path, f"{card_id}: exactly one lens choice must be primary."))
        choice_keys = set()
        for choice in choices:
            if not isinstance(choice, dict):
                issues.append(error("lens_guidance", path, f"{card_id}: every lens choice must be a mapping."))
                continue
            lens_id = choice.get("lens_id")
            accessory_id = choice.get("accessory_id")
            key = (lens_id, accessory_id)
            if key in choice_keys:
                issues.append(error("lens_guidance", path, f"{card_id}: duplicate lens/accessory choice {key}."))
            choice_keys.add(key)
            if lens_id not in lenses:
                issues.append(error("lens_guidance", path, f"{card_id}: unknown lens id {lens_id}."))
            if choice.get("role") not in ROLES:
                issues.append(error("lens_guidance", path, f"{card_id}: invalid lens role {choice.get('role')}."))
            if not str(choice.get("use_when") or "").strip() or not str(choice.get("field_check") or "").strip():
                issues.append(error("lens_guidance", path, f"{card_id}: every choice requires use_when and field_check."))
            if accessory_id:
                accessory = accessories.get(accessory_id)
                if accessory is None:
                    issues.append(error("lens_guidance", path, f"{card_id}: unknown accessory id {accessory_id}."))
                elif lens_id not in accessory.get("compatible_lens_ids", []):
                    issues.append(error("lens_guidance", path, f"{card_id}: {accessory_id} is incompatible with {lens_id}."))
    if seen_profiles != subject_ids:
        missing = sorted(subject_ids - seen_profiles)
        extra = sorted(seen_profiles - subject_ids)
        if missing:
            issues.append(error("lens_guidance", path, f"Lens guidance is missing subject card_ids: {', '.join(missing)}"))
        if extra:
            issues.append(error("lens_guidance", path, f"Lens guidance has extra card_ids: {', '.join(extra)}"))
    return issues


def _profile_index(root):
    profiles = {}
    for source in sorted((root / "10 Profiles").glob("*.yaml")):
        try:
            profile = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            continue
        card_id = profile.get("card_id")
        if card_id:
            profiles[card_id] = profile
    return profiles
