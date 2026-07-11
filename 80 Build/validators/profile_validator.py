from collections import Counter

from .common import error, flatten_paths, load_yaml_checked


LIST_KEYS = ["checklist", "watch_for", "common_mistakes", "notes"]


def validate(root):
    issues = []
    baseline_path = root / "00 Master" / "baseline.yaml"
    baseline_paths = set()
    baseline_values = {}
    try:
        baseline = load_yaml_checked(baseline_path)
        defaults = baseline.get("defaults", {})
        baseline_paths = flatten_paths(defaults)
        baseline_values = _flatten_values(defaults)
    except Exception:
        pass

    profile_paths = sorted((root / "10 Profiles").glob("*.yaml"))
    stems = [path.stem.lower() for path in profile_paths]
    titles = []

    for duplicate in _duplicates(stems):
        issues.append(error("profiles", root / "10 Profiles", f"Duplicate profile filename stem: {duplicate}"))

    for path in profile_paths:
        try:
            data = load_yaml_checked(path)
        except Exception as exc:
            issues.append(error("profiles", path, f"Profile YAML parse error: {exc}"))
            continue
        if not isinstance(data, dict):
            issues.append(error("profiles", path, "Profile must be a mapping."))
            continue
        issues.extend(_required_profile_keys(path, data))
        title = data.get("title")
        if isinstance(title, str):
            titles.append(title.lower())
        overrides = data.get("overrides", {})
        if not isinstance(overrides, dict):
            issues.append(error("profiles", path, "overrides must be a mapping."))
        else:
            issues.extend(_validate_overrides(path, overrides, baseline_paths, baseline_values))
        for key in LIST_KEYS:
            if key in data and not isinstance(data[key], list):
                issues.append(error("profiles", path, f"{key} must be a list."))

    for duplicate in _duplicates(titles):
        issues.append(error("profiles", root / "10 Profiles", f"Duplicate profile title: {duplicate}"))
    return issues


def _required_profile_keys(path, data):
    issues = []
    for key in ("metadata", "title", "inherits"):
        if key not in data:
            issues.append(error("profiles", path, f"Missing required key: {key}."))
        if "metadata" in data and not isinstance(data["metadata"], dict):
            issues.append(error("profiles", path, "metadata must be a mapping."))
        elif "metadata" in data and "release" in data["metadata"] and not isinstance(data["metadata"]["release"], bool):
            issues.append(error("profiles", path, "metadata.release must be a boolean."))
    if "title" in data and not isinstance(data["title"], str):
        issues.append(error("profiles", path, "title must be a string."))
    if "subtitle" in data and data["subtitle"] is not None and not isinstance(data["subtitle"], str):
        issues.append(error("profiles", path, "subtitle must be a string or null."))
    if data.get("inherits") != "baseline":
        issues.append(error("profiles", path, "inherits must be baseline."))
    return issues


def _validate_overrides(path, overrides, baseline_paths, baseline_values):
    issues = []
    override_values = _flatten_values(overrides)
    for override_path, override_value in sorted(override_values.items()):
        if baseline_paths and override_path not in baseline_paths:
            issues.append(error("overrides", path, f"Override path is not present in baseline defaults: {override_path}"))
            continue
        if override_path in baseline_values and not _compatible_type(baseline_values[override_path], override_value):
            expected = type(baseline_values[override_path]).__name__
            actual = type(override_value).__name__
            issues.append(error("overrides", path, f"Override path {override_path} has type {actual}; expected {expected}."))
        elif override_path in baseline_values and baseline_values[override_path] == override_value:
            issues.append(error("overrides", path, f"Override duplicates the baseline value: {override_path}"))
    return issues


def _duplicates(values):
    return [value for value, count in Counter(values).items() if count > 1]


def _flatten_values(data, prefix=""):
    values = {}
    if not isinstance(data, dict):
        return values
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            values.update(_flatten_values(value, name))
        else:
            values[name] = value
    return values


def _compatible_type(expected, actual):
    if expected is None:
        return True
    if isinstance(expected, bool):
        return isinstance(actual, bool)
    if isinstance(expected, int) and not isinstance(expected, bool):
        return isinstance(actual, int) and not isinstance(actual, bool)
    if isinstance(expected, float):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool)
    return isinstance(actual, type(expected))
