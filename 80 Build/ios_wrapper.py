import json
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import unquote, urlparse
import re

from generated_output import clean_generated_tree, fresh_copy, numbered_duplicates, remove_numbered_duplicates


IOS_DIR = "ios"
PROJECT_NAME = "Canon R5 Reference"
SCHEME_NAME = "Canon R5 Reference"
RESOURCE_ROOT = "Resources"
WEBSITE_DIR_NAME = "Website"
VALIDATION_REPORT = "IOS_VALIDATION_REPORT.md"
REGRESSION_REPORT = "IOS_WRAPPER_TEST_REPORT.md"
RESOURCE_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".json",
    ".webmanifest",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
}


def website_output_dir(paths):
    return paths.website_output_dir


def ios_resources_dir(paths):
    return paths.root / IOS_DIR / RESOURCE_ROOT / WEBSITE_DIR_NAME


def prepare_website_output(paths):
    """Publish output/merged-build as the canonical Website staging bundle."""
    source = paths.merged_build_output_dir
    target = website_output_dir(paths)
    if not source.exists():
        raise FileNotFoundError(f"Generated website source is missing: {source}")
    remove_numbered_duplicates(source, require_original=False)
    fresh_copy(source, target, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
    clean_generated_tree(target)
    return target


def update_ios_resources(paths):
    """Refresh generated resources consumed by the Xcode folder reference."""
    source = website_output_dir(paths)
    if not source.exists():
        source = prepare_website_output(paths)
    target = ios_resources_dir(paths)
    remove_numbered_duplicates(source, require_original=False)
    fresh_copy(source, target, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
    clean_generated_tree(target)
    return target


def validate_ios_wrapper(paths, write_report=True):
    website = website_output_dir(paths)
    resources = ios_resources_dir(paths)
    checks = []

    _check_exists(checks, "index.html exists", resources / "index.html")
    _check_extension_copied(checks, "all HTML pages copied", website, resources, ".html")
    _check_extension_copied(checks, "CSS copied", website, resources, ".css", optional=True)
    _check_extension_copied(checks, "JS copied", website, resources, ".js", optional=True)
    _check_extension_copied(checks, "SVG copied", website, resources, ".svg", optional=True)
    _check_extension_copied(checks, "PNG copied", website, resources, ".png")
    _check_extension_copied(checks, "JPG copied", website, resources, ".jpg", optional=True)
    _check_extension_copied(checks, "fonts copied", website, resources, ".woff", ".woff2", ".ttf", ".otf", ".eot", optional=True)
    _check_exists(checks, "Cards folder copied", resources / "Cards")
    _check_exists(checks, "Field Guide copied", resources / "appendices")
    _check_exists(checks, "website staging folder copied", website)
    checks.extend(_check_relative_links(resources))
    checks.extend(_check_stale_files(website, resources))
    checks.extend(_check_numbered_duplicates(website, resources))

    if write_report:
        _write_validation_report(_report_path(paths, VALIDATION_REPORT), checks)
    return checks


def build_xcode_project(paths, destination=None, action="build"):
    project = paths.root / IOS_DIR / f"{PROJECT_NAME}.xcodeproj"
    destination = destination or "generic/platform=iOS Simulator"
    command = [
        "xcodebuild",
        "-project",
        str(project),
        "-scheme",
        SCHEME_NAME,
        "-destination",
        destination,
        action,
    ]
    return _run_xcode_command(command)


def run_xcode_tests(paths, destination=None):
    project = paths.root / IOS_DIR / f"{PROJECT_NAME}.xcodeproj"
    destination = destination or "platform=iOS Simulator,name=iPhone 16"
    command = [
        "xcodebuild",
        "-project",
        str(project),
        "-scheme",
        SCHEME_NAME,
        "-destination",
        destination,
        "test",
    ]
    return _run_xcode_command(command)


def write_regression_report(paths, steps):
    lines = ["# iOS Wrapper Test Report", "", f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for step in steps:
        mark = "PASS" if step["ok"] else "FAIL"
        lines.append(f"- {mark}: {step['name']}")
        detail = step.get("detail")
        if detail:
            lines.append(f"  {detail}")
    lines.append("")
    _report_path(paths, REGRESSION_REPORT).write_text("\n".join(lines), encoding="utf-8")


def _report_path(paths, filename):
    report_dir = paths.root / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / filename


def _check_exists(checks, name, path):
    checks.append({"name": name, "ok": path.exists(), "detail": str(path)})


def _check_extension_copied(checks, name, source_root, target_root, *extensions, optional=False):
    source_files = _files_with_extensions(source_root, extensions)
    target_files = _files_with_extensions(target_root, extensions)
    missing = sorted(str(path.relative_to(source_root)) for path in source_files if not (target_root / path.relative_to(source_root)).exists())
    ok = not missing and (bool(source_files) or optional)
    detail = f"{len(target_files)} copied"
    if missing:
        detail = "Missing: " + ", ".join(missing[:10])
    elif not source_files and optional:
        detail = "No generated files of this type were present."
    checks.append({"name": name, "ok": ok, "detail": detail})


def _files_with_extensions(root, extensions):
    if not root.exists():
        return []
    lowered = {extension.lower() for extension in extensions}
    return [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in lowered]


def _check_relative_links(root):
    checks = []
    missing = []
    outside = []
    for path in _files_with_extensions(root, [".html", ".css", ".js", ".json", ".webmanifest"]):
        text = path.read_text(encoding="utf-8", errors="replace")
        for reference in _references(text, path.suffix.lower()):
            if _skip_reference(reference):
                continue
            resolved = _resolve(path.parent, reference)
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                outside.append(f"{path.relative_to(root)} -> {reference}")
                continue
            if not resolved.exists():
                missing.append(f"{path.relative_to(root)} -> {reference}")

    checks.append({
        "name": "relative links preserved",
        "ok": not outside,
        "detail": "No references escape the generated Website folder." if not outside else "; ".join(outside[:10]),
    })
    checks.append({
        "name": "no missing resources",
        "ok": not missing,
        "detail": "All local references resolve." if not missing else "; ".join(missing[:10]),
    })
    return checks


def _check_stale_files(source_root, target_root):
    stale = []
    if target_root.exists():
        for path in target_root.rglob("*"):
            if path.is_file() and not (source_root / path.relative_to(target_root)).exists():
                stale.append(str(path.relative_to(target_root)))
    return [{
        "name": "no stale generated resources",
        "ok": not stale,
        "detail": "Generated resources were refreshed from scratch." if not stale else "; ".join(stale[:10]),
    }]


def _check_numbered_duplicates(*roots):
    found = []
    for root in roots:
        for path in numbered_duplicates(root, require_original=False):
            found.append(f"{root.name}/{path.relative_to(root)}")
    return [{
        "name": "no Finder duplicate resources",
        "ok": not found,
        "detail": "No numbered duplicate generated files remain." if not found else "; ".join(found[:10]),
    }]


def _references(text, suffix):
    patterns = [r"""(?:src|href|poster|action)\s*=\s*["']([^"']+)["']"""]
    if suffix in {".html", ".css"}:
        patterns.append(r"""url\(\s*["']?([^"')]+)["']?\s*\)""")
    refs = []
    for pattern in patterns:
        refs.extend(match.group(1) for match in re.finditer(pattern, text, flags=re.IGNORECASE))
    return refs


def _skip_reference(reference):
    parsed = urlparse(reference)
    return (
        not reference
        or reference.startswith("#")
        or parsed.scheme in {"data", "http", "https", "mailto", "tel", "javascript"}
    )


def _resolve(base_dir, reference):
    path_part = unquote(urlparse(reference).path)
    if path_part in {"", "."}:
        return base_dir.resolve()
    return (base_dir / path_part).resolve()


def _write_validation_report(path, checks):
    lines = ["# iOS Wrapper Validation Report", "", f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for check in checks:
        mark = "PASS" if check["ok"] else "FAIL"
        lines.append(f"- {mark}: {check['name']}")
        if check.get("detail"):
            lines.append(f"  {check['detail']}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_xcode_command(command):
    xcodebuild = shutil.which("xcodebuild")
    if not xcodebuild:
        return {"ok": False, "detail": "xcodebuild was not found."}
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        return {"ok": False, "detail": str(exc)}
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    if len(output) > 4000:
        output = output[-4000:]
    return {"ok": completed.returncode == 0, "detail": output or f"Exited {completed.returncode}"}
