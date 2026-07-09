from .common import error, load_yaml_checked


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
    return issues

