from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ValidationIssue:
    level: str
    area: str
    path: str
    message: str


def error(area, path, message):
    return ValidationIssue("error", area, str(path), message)


def warning(area, path, message):
    return ValidationIssue("warning", area, str(path), message)


class DuplicateKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key ({key})",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


DuplicateKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def load_yaml_checked(path):
    with open(path, "r", encoding="utf-8") as file:
        return yaml.load(file, Loader=DuplicateKeyLoader)


def flatten_paths(data, prefix=""):
    paths = set()
    if not isinstance(data, dict):
        return paths
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            paths.update(flatten_paths(value, name))
        else:
            paths.add(name)
    return paths


def all_yaml_files(root):
    root = Path(root)
    skipped_parts = {".git", "__pycache__", "Backups"}
    return sorted(
        path
        for path in root.glob("**/*.yaml")
        if not any(part in skipped_parts for part in path.relative_to(root).parts)
    )
