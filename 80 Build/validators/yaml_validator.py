from .common import all_yaml_files, error, load_yaml_checked


LIST_SHAPED_YAML = {
    ("data", "canon_r5_icons.yaml"),
    ("60 Assets", "icons", "canon_r5_official", "modes.yaml"),
}


def validate(root):
    issues = []
    for path in all_yaml_files(root):
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
    return tuple(path.relative_to(root).parts) in LIST_SHAPED_YAML
