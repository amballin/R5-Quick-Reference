import re
from urllib.parse import unquote, urlparse

from asset_manager import ProjectPaths
from .common import error


def validate(root):
    issues = []
    paths = ProjectPaths(root)
    profiles = sorted((root / "10 Profiles").glob("*.yaml"))
    output_folders = [
        paths.output_dir,
        paths.html_output_dir,
        paths.merged_output_dir,
        paths.merged_build_output_dir,
        paths.field_guide_html_output_dir,
        paths.pages_output_dir,
    ]
    for path in output_folders:
        if not path.is_dir():
            issues.append(error("build_output", path, "Output folder is missing."))
            continue
        issues.extend(_generated_tree_issues(path))

    for profile in profiles:
        name = profile.stem
        expected = [
            paths.html_output_file(name),
            paths.merged_output_file(name),
        ]
        for path in expected:
            if not path.exists():
                issues.append(error("build_output", path, "Expected generated output is missing."))
        html_path = paths.html_output_file(name)
        if html_path.exists():
            issues.extend(_html_issues(html_path))
    return issues


def _html_issues(path):
    issues = []
    text = path.read_text(encoding="utf-8", errors="replace")
    viewport = 'name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"'
    if viewport not in text:
        issues.append(error("html_viewport", path, "Responsive viewport metadata is missing."))
    if re.search(r'(?:file://|/Users/|[A-Za-z]:\\\\)', text):
        issues.append(error("html_absolute_path", path, "Generated HTML contains an absolute local filesystem path."))
    if re.search(r'\{\{[^}]+\}\}|(?:PLACEHOLDER|TEMPLATE_VARIABLE)', text, flags=re.IGNORECASE):
        issues.append(error("html_template", path, "Generated HTML contains unresolved template text."))
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', text, flags=re.IGNORECASE)
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        issues.append(error("html_duplicate_id", path, f"Duplicate HTML IDs: {', '.join(duplicates)}"))
    for reference in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', text, flags=re.IGNORECASE):
        parsed = urlparse(reference)
        if not reference or reference.startswith("#") or parsed.scheme in {"data", "http", "https", "mailto", "tel"}:
            continue
        target = (path.parent / unquote(parsed.path)).resolve()
        if not target.exists():
            issues.append(error("html_asset", path, f"Referenced local file is missing: {reference}"))
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
