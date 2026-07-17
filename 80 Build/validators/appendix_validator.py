import re

from .common import error, load_yaml_checked


def validate(root):
    issues = []
    manifest_path = root / "50 Field Guide" / "required_appendices.yaml"
    if not manifest_path.exists():
        return [error("appendices", manifest_path, "required_appendices.yaml is missing.")]

    try:
        manifest = load_yaml_checked(manifest_path) or {}
    except Exception as exc:
        return [error("appendices", manifest_path, f"Appendix manifest parse error: {exc}")]

    appendices = manifest.get("appendices")
    required_sections = manifest.get("required_sections")
    if not isinstance(appendices, list) or not appendices:
        return [error("appendices", manifest_path, "appendices must be a non-empty list.")]
    if not isinstance(required_sections, list) or not required_sections:
        issues.append(error("appendices", manifest_path, "required_sections must be a non-empty list."))
        required_sections = []

    ids = set()
    for entry in appendices:
        if not isinstance(entry, dict):
            issues.append(error("appendices", manifest_path, "Each appendix entry must be a mapping."))
            continue
        if "release" in entry and not isinstance(entry["release"], bool):
            issues.append(error("appendices", manifest_path, f"Appendix {entry.get('id', '<unknown>')} release must be a boolean."))
        if "display_order" in entry and (not isinstance(entry["display_order"], int) or isinstance(entry["display_order"], bool)):
            issues.append(error("appendices", manifest_path, f"Appendix {entry.get('id', '<unknown>')} display_order must be an integer."))
        content_type = entry.get("content_type", "field_guide")
        if content_type not in {"field_guide", "setting_deep_dive"}:
            issues.append(error("appendices", manifest_path, f"Appendix {entry.get('id', '<unknown>')} has invalid content_type: {content_type}"))
        appendix_id = entry.get("id")
        if not appendix_id:
            issues.append(error("appendices", manifest_path, "Appendix entry is missing id."))
        elif appendix_id in ids:
            issues.append(error("appendices", manifest_path, f"Duplicate appendix id: {appendix_id}"))
        else:
            ids.add(appendix_id)

    profile_titles = _profile_titles(root)
    for entry in appendices:
        if not isinstance(entry, dict):
            continue
        issues.extend(_validate_entry(root, manifest_path, entry, required_sections, ids, profile_titles))
    return issues


def _validate_entry(root, manifest_path, entry, required_sections, ids, profile_titles):
    issues = []
    title = entry.get("title")
    relative_file = entry.get("file")
    if not title:
        issues.append(error("appendices", manifest_path, "Appendix entry is missing title."))
    if not relative_file:
        issues.append(error("appendices", manifest_path, f"Appendix {entry.get('id', '<unknown>')} is missing file."))
        return issues

    path = root / "50 Field Guide" / relative_file
    if not path.exists():
        issues.append(error("appendices", path, f"Required appendix is missing: {title or entry.get('id')}"))
        return issues

    content_type = entry.get("content_type", "field_guide")
    expected_folder = "Setting Deep Dives" if content_type == "setting_deep_dive" else "Appendices"
    if not str(relative_file).startswith(f"{expected_folder}/"):
        issues.append(error("appendices", manifest_path, f"Appendix {entry.get('id')} with content_type {content_type} must be stored under {expected_folder}/."))

    text = path.read_text(encoding="utf-8", errors="replace")
    for linked_id in re.findall(r"\]\(appendix:([a-z0-9_]+)\)", text):
        if linked_id not in ids:
            issues.append(error("appendices", path, f"Markdown references missing appendix id: {linked_id}"))
    headings = _headings(text)
    if title and headings and headings[0] != title:
        issues.append(error("appendices", path, f"Top-level heading must be: {title}"))
    skipped_sections = set(entry.get("skip_required_sections", []) or [])
    for section in required_sections:
        if section in skipped_sections:
            continue
        if section not in headings:
            issues.append(error("appendices", path, f"Missing required section heading: {section}"))
    if entry.get("strict_topics"):
        normalized_text = _normalize(text)
        for topic in entry.get("required_topics", []) or []:
            if _normalize(str(topic)) not in normalized_text:
                issues.append(error("appendices", path, f"Missing required topic: {topic}"))

    for profile in entry.get("profiles", []) or []:
        if profile not in profile_titles:
            issues.append(error("appendices", manifest_path, f"Appendix {entry.get('id')} references missing profile: {profile}"))
    for related_id in entry.get("related_appendices", []) or []:
        if related_id not in ids:
            issues.append(error("appendices", manifest_path, f"Appendix {entry.get('id')} references missing appendix id: {related_id}"))
    return issues


def _headings(text):
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped.lstrip("#").strip())
    return headings


def _profile_titles(root):
    titles = set()
    for path in sorted((root / "10 Profiles").glob("*.yaml")):
        try:
            data = load_yaml_checked(path) or {}
        except Exception:
            continue
        title = data.get("title")
        if isinstance(title, str):
            titles.add(title)
    return titles


def _normalize(value):
    return " ".join(value.lower().replace("-", " ").split())
