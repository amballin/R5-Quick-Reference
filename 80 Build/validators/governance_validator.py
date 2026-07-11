import re
from pathlib import Path

from .common import error


GOVERNING_FILES = [
    "PROJECT_RULES.md",
    "00 Master/project_memory.md",
    "00 Master/decision-log.md",
    "00 Master/specifications/Architecture.md",
    "00 Master/specifications/Profile Specification.md",
    "00 Master/specifications/Card Specification.md",
    "00 Master/specifications/Appendix Specification.md",
    "00 Master/specifications/Asset Specification.md",
    "00 Master/specifications/Build and Validation Specification.md",
    "README.md",
    "HOW_TO.md",
]
RETIRED_REFERENCE = "Codex Project Specification.md"
LINK_PATTERN = re.compile(r"\[[^]]+\]\(([^)]+)\)")
VALID_STATUSES = {"Proposed", "Accepted", "Superseded", "Rejected"}


def validate(root):
    issues = []
    for relative in GOVERNING_FILES:
        path = root / relative
        if not path.exists():
            issues.append(error("governance", path, "Required governing document is missing."))
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if RETIRED_REFERENCE in text:
            issues.append(error("governance", path, f"Stale reference to retired file: {RETIRED_REFERENCE}"))
        issues.extend(_local_link_issues(root, path, text))
    issues.extend(_decision_status_issues(root / "00 Master" / "decision-log.md"))
    return issues


def _local_link_issues(root, path, text):
    issues = []
    for target in LINK_PATTERN.findall(text):
        target = target.split("#", 1)[0].replace("%20", " ")
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            issues.append(error("governance", path, f"Local link leaves project root: {target}"))
            continue
        if not resolved.exists():
            issues.append(error("governance", path, f"Broken local link: {target}"))
    return issues


def _decision_status_issues(path):
    if not path.exists():
        return []
    issues = []
    text = path.read_text(encoding="utf-8", errors="replace")
    decisions = re.split(r"(?m)^## ", text)[1:]
    for decision in decisions:
        title = decision.splitlines()[0].strip()
        match = re.search(r"(?m)^\*\*Status:\*\* ([A-Za-z]+)", decision)
        if not match:
            issues.append(error("governance", path, f"Decision is missing a status: {title}"))
        elif match.group(1) not in VALID_STATUSES:
            issues.append(error("governance", path, f"Invalid decision status for {title}: {match.group(1)}"))
    return issues
