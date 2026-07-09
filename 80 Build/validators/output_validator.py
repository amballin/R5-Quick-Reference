import re

from .common import error


OUTPUT_FOLDERS = {
    "html": "output/cards/html",
    "merged": "output/cards/merged",
    "png": "output/cards/png",
    "merged-build": "output/merged-build",
    "field-guide-html": "output/field-guide/html",
}


def validate(root):
    issues = []
    profiles = sorted((root / "10 Profiles").glob("*.yaml"))
    for folder in OUTPUT_FOLDERS.values():
        path = root / folder
        if not path.is_dir():
            issues.append(error("build_output", path, "Output folder is missing."))
            continue
        issues.extend(_generated_tree_issues(path))

    for profile in profiles:
        name = profile.stem
        expected = [
            root / "output" / "cards" / "html" / f"{name}.html",
            root / "output" / "cards" / "png" / f"{name}.png",
            root / "output" / "cards" / "merged" / f"{name}.yaml",
        ]
        for path in expected:
            if not path.exists():
                issues.append(error("build_output", path, "Expected generated output is missing."))
    return issues


def _generated_tree_issues(path):
    issues = []
    duplicate_paths = _numbered_duplicates(path)
    if duplicate_paths:
        sample = ", ".join(str(item.relative_to(path)) for item in duplicate_paths[:10])
        issues.append(error("build_output", path, f"Generated output contains Finder-style duplicate paths: {sample}"))

    ds_store_paths = sorted(path.rglob(".DS_Store"))
    if ds_store_paths:
        sample = ", ".join(str(item.relative_to(path)) for item in ds_store_paths[:10])
        issues.append(error("build_output", path, f"Generated output contains .DS_Store files: {sample}"))
    return issues


def _numbered_duplicates(root):
    duplicates = []
    for path in root.rglob("*"):
        original = _unsuffixed_original(path)
        if original and original.exists():
            duplicates.append(path)
    return sorted(duplicates, key=lambda item: str(item))


def _unsuffixed_original(path):
    match = re.match(r"^(?P<base>.+?) (?P<number>[0-9]+)(?P<suffix>\.[^.]*)?$", path.name)
    if not match:
        return None
    suffix = match.group("suffix") or ""
    return path.with_name(f"{match.group('base')}{suffix}")
