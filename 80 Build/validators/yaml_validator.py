from .common import application_root, error, load_yaml_checked, resolved_yaml_files


LIST_SHAPED_YAML = {
    ("data", "canon_r5_icons.yaml"),
    ("60 Assets", "icons", "canon_r5_official", "modes.yaml"),
}


def validate(paths_or_root):
    root = application_root(paths_or_root)
    issues = []
    for path in resolved_yaml_files(paths_or_root):
        try:
            data = load_yaml_checked(path)
        except Exception as exc:
            issues.append(error("yaml", path, f"YAML parse error: {exc}"))
            continue
        if data is None:
            issues.append(error("yaml", path, "YAML file is empty."))
        elif _allows_top_level_list(root, path):
            if not isinstance(data, list):
                issues.append(error("yaml", path, "Top-level YAML value must be a list."))
        elif not isinstance(data, dict):
            issues.append(error("yaml", path, "Top-level YAML value must be a mapping."))
    return issues


def _allows_top_level_list(root, path):
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    return tuple(relative.parts) in LIST_SHAPED_YAML
