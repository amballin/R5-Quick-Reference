"""Identify whether a local application is running from main or a development worktree."""

from __future__ import annotations

from pathlib import Path


def active_branch(project_root):
    root = Path(project_root).resolve()
    dot_git = root / ".git"
    try:
        if dot_git.is_file():
            marker = dot_git.read_text(encoding="utf-8").strip()
            if not marker.startswith("gitdir:"):
                return None
            git_dir = Path(marker.removeprefix("gitdir:").strip())
            if not git_dir.is_absolute():
                git_dir = (root / git_dir).resolve()
        else:
            git_dir = dot_git
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None
    prefix = "ref: refs/heads/"
    return head.removeprefix(prefix) if head.startswith(prefix) else None


def project_context_info(project_root):
    branch = active_branch(project_root)
    if branch == "main":
        return {"kind": "main", "label": "Main project", "branch": branch}
    if branch:
        return {"kind": "prototype", "label": f"Prototype · {branch}", "branch": branch}
    return {"kind": "unknown", "label": "Project context unavailable", "branch": None}
