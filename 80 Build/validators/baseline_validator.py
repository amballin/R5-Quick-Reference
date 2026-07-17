from .common import error, load_yaml_checked


ICON_POSITIONS = {"header", "left", "right"}


def validate(root):
    path = root / "00 Master" / "baseline.yaml"
    issues = []
    if not path.exists():
        return [error("baseline", path, "Baseline file is missing.")]
    try:
        data = load_yaml_checked(path)
    except Exception as exc:
        return [error("baseline", path, f"Baseline YAML parse error: {exc}")]
    if not isinstance(data, dict):
        return [error("baseline", path, "Baseline must be a mapping.")]
    if "metadata" not in data:
        issues.append(error("baseline", path, "Missing required key: metadata."))
    elif not isinstance(data["metadata"], dict):
        issues.append(error("baseline", path, "metadata must be a mapping."))
    if "defaults" not in data:
        issues.append(error("baseline", path, "Missing required key: defaults."))
    elif not isinstance(data["defaults"], dict):
        issues.append(error("baseline", path, "defaults must be a mapping."))
    icons = ((data.get("card") or {}).get("icons") or {})
    if not isinstance(icons, dict):
        issues.append(error("baseline", path, "card.icons must be a mapping."))
    else:
        unknown = sorted(set(icons) - ICON_POSITIONS)
        if unknown:
            issues.append(error("baseline", path, f"Unknown card icon positions: {', '.join(unknown)}."))
        if not isinstance(icons.get("header"), str) or not icons["header"].strip():
            issues.append(error("baseline", path, "card.icons.header must define the shared header icon."))
        for position, value in icons.items():
            if value is not None and not isinstance(value, str):
                issues.append(error("baseline", path, f"card.icons.{position} must be a string or null."))
    return issues
