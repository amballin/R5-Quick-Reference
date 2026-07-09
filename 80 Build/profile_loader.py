import yaml


PROFILE_ALIASES = {
    "Normal": "Camera Defaults",
}


def canonical_profile_name(profile_name):
    return PROFILE_ALIASES.get(profile_name, profile_name)


def load_yaml(path):
    """Load a YAML file using the project's existing PyYAML behavior."""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_baseline(paths):
    return load_yaml(paths.baseline_file)


def load_profile(paths, profile_name):
    return load_yaml(paths.profile_file(canonical_profile_name(profile_name)))


def write_merged_profile(paths, profile_name, merged):
    paths.merged_output_dir.mkdir(parents=True, exist_ok=True)
    with open(paths.merged_output_file(profile_name), "w") as file:
        yaml.safe_dump(merged, file, sort_keys=False)
