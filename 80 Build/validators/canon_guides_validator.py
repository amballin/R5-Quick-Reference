from .common import error, load_yaml_checked


def validate(root):
    guide_dir = root / "70 Canon Guides"
    if not guide_dir.exists():
        return []
    issues = []
    for path in sorted(guide_dir.glob("**/*.yaml")):
        try:
            data = load_yaml_checked(path)
        except Exception as exc:
            issues.append(error("canon_guides", path, f"Canon guide YAML parse error: {exc}"))
            continue
        if not isinstance(data, dict):
            issues.append(error("canon_guides", path, "Canon guide YAML must be a mapping."))
            continue
        if "metadata" not in data and "profile" not in data and "guides" not in data:
            issues.append(error("canon_guides", path, "Missing metadata/profile/guides section."))
    return issues

