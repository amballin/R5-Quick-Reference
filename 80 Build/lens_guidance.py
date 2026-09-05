"""Resolve owned-lens choices and lens-specific card compatibility guidance."""

from __future__ import annotations

from pathlib import Path

import yaml

from feature_interactions import evaluate, load_catalog as load_interaction_catalog
from utilities import flatten


ROLE_LABELS = {
    "primary": "Primary",
    "alternative": "Alternative",
    "specialist": "Specialist",
}


class LensGuidanceError(ValueError):
    """Raised when canonical lens guidance cannot be resolved."""


def _load_yaml(path):
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise LensGuidanceError(f"Lens guidance could not be read: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise LensGuidanceError(f"Lens guidance must be a mapping: {path}")
    return data


def _application_root(paths_or_root):
    return getattr(paths_or_root, "application_root", paths_or_root)


def load_sources(paths_or_root):
    root = _application_root(paths_or_root)
    if not hasattr(paths_or_root, "profile_lens_guidance_file"):
        root = Path(root)
    guidance_path = (
        paths_or_root.profile_lens_guidance_file
        if hasattr(paths_or_root, "profile_lens_guidance_file")
        else root / "00 Master" / "profile_lens_guidance.yaml"
    )
    equipment_path = (
        paths_or_root.owned_equipment_file
        if hasattr(paths_or_root, "owned_equipment_file")
        else root / "data" / "stabilization_reference.yaml"
    )
    return _load_yaml(guidance_path), _load_yaml(equipment_path)


def resolved_choices(profile, paths_or_root, guidance=None, equipment=None):
    """Return ordered display choices for one immutable profile identity."""
    card_id = profile.get("card_id")
    if not card_id or profile.get("card_type", "profile") != "profile":
        return []
    if guidance is None or equipment is None:
        loaded_guidance, loaded_equipment = load_sources(paths_or_root)
        guidance = guidance if guidance is not None else loaded_guidance
        equipment = equipment if equipment is not None else loaded_equipment
    entry = next(
        (item for item in guidance.get("profiles") or [] if item.get("card_id") == card_id),
        None,
    )
    if entry is None:
        return []
    lenses = {item.get("id"): item for item in equipment.get("lenses") or []}
    accessories = {item.get("id"): item for item in equipment.get("accessories") or []}
    choices = []
    for configured in entry.get("choices") or []:
        lens = lenses.get(configured.get("lens_id"))
        if lens is None:
            raise LensGuidanceError(f"Unknown lens id: {configured.get('lens_id')}")
        accessory = accessories.get(configured.get("accessory_id"))
        if configured.get("accessory_id") and accessory is None:
            raise LensGuidanceError(f"Unknown accessory id: {configured.get('accessory_id')}")
        display_name = lens["short_name"]
        if accessory:
            display_name = f"{display_name} {accessory['display_suffix']}"
        choices.append(
            {
                **configured,
                "display_name": display_name,
                "role_label": ROLE_LABELS[configured["role"]],
                "lens": lens,
                "accessory": accessory,
            }
        )
    return choices


def compatibility_messages(profile, merged, paths_or_root, surface="card", guidance=None, equipment=None):
    """Return de-duplicated profile and candidate-lens interaction messages."""
    interactions = load_interaction_catalog(_application_root(paths_or_root))
    findings = list(evaluate(merged, interactions, surface=surface))
    merged_fields = flatten(merged)
    for choice in resolved_choices(profile, paths_or_root, guidance=guidance, equipment=equipment):
        lens = choice["lens"]
        accessory = choice.get("accessory")
        context = {
            "lens": {
                "id": lens["id"],
                "mount": lens["mount"],
                "has_optical_is": lens["optical_is"],
                "has_is_switch": lens["is_on_off_switch"],
                "is_enabled": merged_fields.get("stabilization.lens_is") == "On",
            }
        }
        if accessory:
            context["accessory"] = {"id": accessory["id"]}
        findings.extend(evaluate(merged, interactions, context=context, surface=surface))
    messages = []
    seen = set()
    for finding in findings:
        message = finding["message"]
        if message not in seen:
            messages.append(message)
            seen.add(message)
    return messages
