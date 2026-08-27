import re

from .common import error, load_yaml_checked


EXPECTED_MENU_LABEL = "IS (Image Stabilizer) mode"
LENS_MARKER = re.compile(r"<!--\s*STABILIZATION_REFERENCE:\s*([a-z0-9_]+)\s*-->")


def validate(root):
    data_path = root / "data" / "stabilization_reference.yaml"
    quick_reference_path = root / "50 Field Guide" / "Appendices" / "R5 Quick Reference.md"
    lens_guide_path = root / "50 Field Guide" / "Appendices" / "Lens Capabilities.md"
    issues = []

    if not data_path.exists():
        return [error("stabilization", data_path, "Structured stabilization reference is missing.")]
    try:
        data = load_yaml_checked(data_path) or {}
    except Exception as exc:
        return [error("stabilization", data_path, f"Stabilization reference parse error: {exc}")]

    issues.extend(_validate_camera(data_path, data.get("camera")))
    issues.extend(_validate_adapter(data_path, data.get("adapter")))
    lenses = data.get("lenses")
    if not isinstance(lenses, list) or not lenses:
        issues.append(error("stabilization", data_path, "lenses must be a non-empty list."))
        lenses = []

    lens_ids = set()
    for lens in lenses:
        issues.extend(_validate_lens(data_path, lens, lens_ids))
    issues.extend(_validate_accessories(data_path, data.get("accessories"), lens_ids))

    if quick_reference_path.exists():
        issues.extend(_validate_quick_reference(quick_reference_path))
    else:
        issues.append(error("stabilization", quick_reference_path, "R5 Quick Reference is missing."))

    if lens_guide_path.exists():
        text = lens_guide_path.read_text(encoding="utf-8", errors="replace")
        markers = LENS_MARKER.findall(text)
        for lens_id in sorted(lens_ids - set(markers)):
            issues.append(error("stabilization", lens_guide_path, f"Add a stabilization reference marker for lens id: {lens_id}"))
        for marker in sorted(set(markers) - lens_ids):
            issues.append(error("stabilization", lens_guide_path, f"Stabilization marker has no matching structured lens: {marker}"))
        if len(markers) != len(set(markers)):
            issues.append(error("stabilization", lens_guide_path, "Each stabilization reference marker must appear exactly once."))
    else:
        issues.append(error("stabilization", lens_guide_path, "Lens Capabilities guide is missing."))
    return issues


def _validate_camera(path, camera):
    if not isinstance(camera, dict):
        return [error("stabilization", path, "camera must be a mapping.")]
    normal_is = camera.get("normal_is")
    if not isinstance(normal_is, dict):
        return [error("stabilization", path, "camera.normal_is must be a mapping.")]
    issues = []
    if normal_is.get("menu_label") != EXPECTED_MENU_LABEL:
        issues.append(error("stabilization", path, f"camera.normal_is.menu_label must be exactly: {EXPECTED_MENU_LABEL}"))
    if EXPECTED_MENU_LABEL not in str(normal_is.get("menu_path", "")):
        issues.append(error("stabilization", path, "camera.normal_is.menu_path must retain Canon's exact menu label."))
    if normal_is.get("menu_page_number_variable") is not True:
        issues.append(error("stabilization", path, "Mark the IS menu page number as variable."))
    for field in ("body_control_available_when", "unavailable_when", "lens_mode_control", "coordination", "source"):
        if not normal_is.get(field):
            issues.append(error("stabilization", path, f"camera.normal_is.{field} is required."))
    return issues


def _validate_lens(path, lens, lens_ids):
    if not isinstance(lens, dict):
        return [error("stabilization", path, "Each lens must be a mapping.")]
    issues = []
    lens_id = lens.get("id")
    name = lens.get("name") or lens_id or "<unknown>"
    if not isinstance(lens_id, str) or not lens_id:
        issues.append(error("stabilization", path, "Each lens requires a non-empty id."))
    elif lens_id in lens_ids:
        issues.append(error("stabilization", path, f"Duplicate lens id: {lens_id}"))
    else:
        lens_ids.add(lens_id)
    if not lens.get("name"):
        issues.append(error("stabilization", path, f"Lens {name} requires a name."))
    if not lens.get("short_name"):
        issues.append(error("stabilization", path, f"Lens {name} requires a short_name for field cards."))
    if lens.get("mount") not in {"EF", "EF-S", "RF"}:
        issues.append(error("stabilization", path, f"Lens {name}: mount must be EF, EF-S, or RF."))

    for field in ("optical_is", "is_on_off_switch", "is_mode_switch"):
        if not isinstance(lens.get(field), bool):
            issues.append(error("stabilization", path, f"Lens {name}: {field} must be true or false."))

    optical_is = lens.get("optical_is")
    on_off_switch = lens.get("is_on_off_switch")
    mode_switch = lens.get("is_mode_switch")
    modes = lens.get("is_modes")
    if modes is not None and not isinstance(modes, list):
        issues.append(error("stabilization", path, f"Lens {name}: is_modes must be a list when present."))
        modes = []
    if modes and mode_switch is not True:
        issues.append(error("stabilization", path, f"Lens {name}: modes are listed but is_mode_switch is not true."))
    if mode_switch is True and not modes:
        issues.append(error("stabilization", path, f"Lens {name}: a mode switch is documented but no supported modes are listed."))
    if optical_is is False and (on_off_switch is True or mode_switch is True or modes):
        issues.append(error("stabilization", path, f"Lens {name}: a non-IS lens cannot have IS switches or modes."))
    if optical_is is True and not lens.get("control_method"):
        issues.append(error("stabilization", path, f"Lens {name}: optical IS requires a documented control method."))
    if not lens.get("camera_interaction"):
        issues.append(error("stabilization", path, f"Lens {name}: document how lens control interacts with the camera."))

    seen_modes = set()
    for mode in modes or []:
        if not isinstance(mode, dict) or not mode.get("value") or not mode.get("purpose"):
            issues.append(error("stabilization", path, f"Lens {name}: every IS mode requires value and purpose."))
            continue
        value = str(mode["value"])
        if value in seen_modes:
            issues.append(error("stabilization", path, f"Lens {name}: duplicate IS mode {value}."))
        seen_modes.add(value)

    sources = lens.get("sources")
    if not isinstance(sources, list) or not sources:
        issues.append(error("stabilization", path, f"Lens {name}: at least one Canon source is required."))
    else:
        for source in sources:
            if not isinstance(source, dict) or not source.get("title") or not str(source.get("url", "")).startswith("https://"):
                issues.append(error("stabilization", path, f"Lens {name}: every source requires a title and HTTPS URL."))
    return issues


def _validate_adapter(path, adapter):
    if not isinstance(adapter, dict):
        return [error("stabilization", path, "adapter must be a mapping.")]
    issues = []
    if adapter.get("id") != "control_ring_mount_adapter_ef_eos_r":
        issues.append(error("stabilization", path, "Track the owned Control Ring Mount Adapter EF-EOS R exactly."))
    if adapter.get("compatible_mounts") != ["EF", "EF-S"]:
        issues.append(error("stabilization", path, "The control-ring adapter must cover EF and EF-S mounts."))
    if "control ring" not in str(adapter.get("card_note", "")).casefold():
        issues.append(error("stabilization", path, "The adapter card note must state that the control ring remains available."))
    source = adapter.get("source") or {}
    if not source.get("title") or not str(source.get("url", "")).startswith("https://"):
        issues.append(error("stabilization", path, "The adapter requires a Canon title and HTTPS source."))
    return issues


def _validate_accessories(path, accessories, lens_ids):
    if not isinstance(accessories, list):
        return [error("stabilization", path, "accessories must be a list.")]
    issues = []
    seen = set()
    for accessory in accessories:
        if not isinstance(accessory, dict):
            issues.append(error("stabilization", path, "Every accessory must be a mapping."))
            continue
        accessory_id = accessory.get("id")
        if not accessory_id or accessory_id in seen:
            issues.append(error("stabilization", path, f"Accessory ids must be unique and non-empty: {accessory_id}"))
        seen.add(accessory_id)
        compatible = accessory.get("compatible_lens_ids")
        if not isinstance(compatible, list) or not compatible or any(item not in lens_ids for item in compatible):
            issues.append(error("stabilization", path, f"Accessory {accessory_id} requires valid compatible_lens_ids."))
        if not accessory.get("display_suffix") or not accessory.get("card_note"):
            issues.append(error("stabilization", path, f"Accessory {accessory_id} requires display_suffix and card_note."))
        sources = accessory.get("sources")
        if not isinstance(sources, list) or not sources:
            issues.append(error("stabilization", path, f"Accessory {accessory_id} requires Canon sources."))
    return issues


def _validate_quick_reference(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    if EXPECTED_MENU_LABEL not in text:
        issues.append(error("stabilization", path, f"Retain Canon's exact menu label: {EXPECTED_MENU_LABEL}"))
    if re.search(r"(?i)\bShooting\s+\d+\s*(?:>|→)[^\n]*(?:\bIS\b|Image Stabilizer)", text):
        issues.append(error("stabilization", path, "Replace fixed Shooting-menu page numbers with the exact Canon menu label."))
    if re.search(
        r"(?i)(?:camera menu|R5 menu).{0,80}(?:select|choose|set).{0,30}(?:Mode\s*1|1\s*/\s*2\s*/\s*3)",
        text,
    ):
        issues.append(error("stabilization", path, "Do not suggest that lens IS Mode 1 / 2 / 3 is selected in the camera menu."))
    return issues
