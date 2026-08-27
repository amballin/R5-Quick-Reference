"""Resolve Camera Lab equipment context from canonical project sources."""

from __future__ import annotations

import re

from feature_interactions import evaluate, load_catalog as load_interaction_catalog
from lens_guidance import load_sources, resolved_choices
from utilities import flatten


def _normalized(value):
    words = re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).split()
    return " ".join(word for word in words if word not in {"canon", "simulated"})


def _signature(value):
    return re.sub(r"[^a-z0-9]+", "", _normalized(value))


def choice_key(lens_id, accessory_id=None):
    return f"{lens_id}::{accessory_id or ''}"


def _catalog_lens(detected_name, lenses):
    detected = _normalized(detected_name)
    if not detected:
        return None
    exact = [
        lens
        for lens in lenses
        if _signature(detected) in {_signature(lens.get("name")), _signature(lens.get("short_name"))}
    ]
    if len(exact) == 1:
        return exact[0]
    contained = [
        lens
        for lens in lenses
        if _signature(lens.get("short_name"))
        and _signature(lens.get("short_name")) in _signature(detected)
    ]
    return contained[0] if len(contained) == 1 else None


def _profile_mode(merged):
    value = flatten(merged).get("stabilization.image_stabilization.mode")
    match = re.fullmatch(r"Mode\s+([123])", str(value or "").strip(), flags=re.IGNORECASE)
    return match.group(1) if match else None


def _public_choice(choice):
    accessory = choice.get("accessory")
    return {
        "key": choice_key(choice["lens_id"], choice.get("accessory_id")),
        "lens_id": choice["lens_id"],
        "accessory_id": choice.get("accessory_id"),
        "display_name": choice["display_name"],
        "role": choice["role"],
        "role_label": choice["role_label"],
        "use_when": choice["use_when"],
        "field_check": choice["field_check"],
    }


def resolve_equipment(
    root,
    profile,
    merged,
    detected_lens_name=None,
    selected_choice_key=None,
    selected_is_mode=None,
    physical_camera=False,
):
    """Resolve one lens/accessory context without guessing missing equipment."""
    guidance, equipment = load_sources(root)
    lenses = list(equipment.get("lenses") or [])
    options = resolved_choices(profile, root, guidance=guidance, equipment=equipment)
    public_options = [_public_choice(choice) for choice in options]
    options_by_key = {item["key"]: choice for item, choice in zip(public_options, options)}
    primary = next((choice for choice in options if choice.get("role") == "primary"), None)
    detected_lens = _catalog_lens(detected_lens_name, lenses)

    requested = None
    if selected_choice_key:
        requested = options_by_key.get(selected_choice_key)
        if requested is None:
            raise ValueError("The selected lens/accessory combination is not authored for this profile.")

    detected_choice = None
    if detected_lens:
        detected_choice = next(
            (
                choice
                for choice in options
                if choice["lens"]["id"] == detected_lens["id"] and not choice.get("accessory")
            ),
            None,
        ) or next((choice for choice in options if choice["lens"]["id"] == detected_lens["id"]), None)

    selected = requested or detected_choice or (None if detected_lens else primary)
    if selected:
        lens = selected["lens"]
        accessory = selected.get("accessory")
        selected_key = choice_key(selected["lens_id"], selected.get("accessory_id"))
        authored_choice = True
    elif detected_lens:
        lens = detected_lens
        accessory = None
        selected_key = None
        authored_choice = False
    else:
        lens = None
        accessory = None
        selected_key = None
        authored_choice = False

    planning_override = bool(
        requested
        and detected_lens
        and requested["lens"]["id"] != detected_lens["id"]
    )
    if requested:
        selection_source = "operator_planning_selection" if planning_override else "operator_selection"
    elif detected_choice or (detected_lens and not selected):
        selection_source = "camera_readback"
    elif primary:
        selection_source = "profile_primary"
    else:
        selection_source = "unresolved"

    supported_modes = list((lens or {}).get("is_modes") or [])
    supported_mode_values = [str(item["value"]) for item in supported_modes]
    profile_mode = _profile_mode(merged)
    if selected_is_mode:
        selected_is_mode = str(selected_is_mode)
        if selected_is_mode not in supported_mode_values:
            raise ValueError("The selected IS mode is not supported by this lens.")
        resolved_mode = selected_is_mode
    else:
        resolved_mode = profile_mode if profile_mode in supported_mode_values else None

    if not lens:
        stabilization = {
            "control": "unresolved",
            "supported_modes": [],
            "profile_mode": profile_mode,
            "selected_mode": None,
            "mode_override": False,
            "summary": "Choose or detect a known lens before evaluating stabilization controls.",
        }
    elif supported_modes:
        stabilization = {
            "control": "lens_mode_switch",
            "supported_modes": supported_modes,
            "profile_mode": profile_mode,
            "selected_mode": resolved_mode,
            "mode_override": bool(resolved_mode and resolved_mode != profile_mode),
            "summary": "Choose a supported mode on the lens's physical IS mode switch.",
        }
    elif lens.get("optical_is"):
        stabilization = {
            "control": "lens_switch_automatic",
            "supported_modes": [],
            "profile_mode": profile_mode,
            "selected_mode": None,
            "mode_override": False,
            "summary": "This lens has IS On/Off but no Mode 1 / 2 / 3 selector; behavior is automatic.",
        }
    else:
        stabilization = {
            "control": "camera_body",
            "supported_modes": [],
            "profile_mode": profile_mode,
            "selected_mode": None,
            "mode_override": False,
            "summary": "This lens has no optical IS; use the EOS R5 body stabilization control.",
        }

    context = {}
    if lens:
        context["lens"] = {
            "id": lens["id"],
            "mount": lens["mount"],
            "has_optical_is": lens["optical_is"],
            "has_is_switch": lens["is_on_off_switch"],
            "is_enabled": flatten(merged).get("stabilization.lens_is") == "On",
        }
    if accessory:
        context["accessory"] = {"id": accessory["id"]}
    interactions = evaluate(
        merged,
        load_interaction_catalog(root),
        context=context,
        surface="camera_lab",
    )
    public_interactions = [
        {
            "id": rule["id"],
            "evidence_class": rule["evidence_class"],
            "message": rule["message"],
            "effects": rule["effects"],
        }
        for rule in interactions
    ]

    detected_matches_selected = bool(
        detected_lens and lens and detected_lens["id"] == lens["id"]
    )
    return {
        "detected_lens_name": detected_lens_name,
        "detected_lens_id": detected_lens.get("id") if detected_lens else None,
        "detected_lens_recognized": bool(detected_lens),
        "selected_choice_key": selected_key,
        "selected_lens_id": lens.get("id") if lens else None,
        "selected_lens_name": lens.get("name") if lens else None,
        "selected_accessory_id": accessory.get("id") if accessory else None,
        "selected_accessory_name": accessory.get("name") if accessory else None,
        "authored_choice": authored_choice,
        "selection_source": selection_source,
        "planning_override": planning_override,
        "detected_matches_selected": detected_matches_selected,
        "physical_camera": physical_camera,
        "options": public_options,
        "selected_guidance": _public_choice(selected) if selected else None,
        "lens": lens,
        "accessory": accessory,
        "stabilization": stabilization,
        "interactions": public_interactions,
    }


def interaction_effects_for_path(interactions, path):
    matches = []
    for interaction in interactions or []:
        for effect in interaction.get("effects") or []:
            if path in (effect.get("setting_paths") or []):
                matches.append(
                    {
                        "id": interaction["id"],
                        "behavior": effect["behavior"],
                        "message": interaction["message"],
                        "evidence_class": interaction["evidence_class"],
                    }
                )
    return matches
