import re
import subprocess
from pathlib import Path

from .common import error, load_yaml_checked


IDENTITY_PATH = Path("00 Master/project_identity.yaml")
EXPECTED_IDENTITY = {
    "schema_version": 1,
    "project_id": "canon-eos-r5-camera-reference",
    "project_name": "Canon EOS R5 Camera Reference",
    "repository_role": "authoritative-source",
    "artifact_type": "source-repository",
}
EXPECTED_CAMERA = {
    "manufacturer": "Canon",
    "model": "EOS R5",
}
AUTHORITATIVE_FILES = [
    "PROJECT_RULES.md",
    "00 Master/baseline.yaml",
    "00 Master/schema.yaml",
    "00 Master/card_layout.yaml",
    "00 Master/setting_access.yaml",
    "50 Field Guide/required_appendices.yaml",
    "50 Field Guide/Appendices/R5 Quick Reference.md",
    "80 Build/build.py",
    "80 Build/validator.py",
]
AUTHORITATIVE_DIRECTORIES = [
    "10 Profiles",
    "20 Templates",
]
PROHIBITED_COMPONENT_PATTERNS = [
    re.compile(r"(?:^| )old(?: |$)"),
    re.compile(r"(?:^| )backups?(?: |$)"),
    re.compile(r"(?:^| )archives?(?: |$)"),
    re.compile(r"(?:^| )build output(?: |$)"),
    re.compile(r"(?:^| )generated(?: outputs?)?(?: |$)"),
    re.compile(r"(?:^| )native wrapper(?: |$)"),
]


def validate(root):
    root = Path(root).resolve()
    issues = []
    issues.extend(_validate_git_root(root))
    issues.extend(_validate_working_directory(root))
    issues.extend(_validate_path(root))
    issues.extend(_validate_components(root))
    issues.extend(_validate_identity(root))
    return issues


def _validate_git_root(root):
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [error("project_identity", root, f"Unable to resolve the Git root: {exc}")]
    if result.returncode != 0 or not result.stdout.strip():
        return [error("project_identity", root, "The selected project root is not a Git repository.")]
    resolved_git_root = Path(result.stdout.strip()).resolve()
    if resolved_git_root != root:
        return [
            error(
                "project_identity",
                root,
                f"Selected root does not match the Git root: {resolved_git_root}",
            )
        ]
    return []


def _validate_working_directory(root):
    working_directory = Path.cwd().resolve()
    if working_directory == root or root in working_directory.parents:
        return []
    return [
        error(
            "project_identity",
            working_directory,
            f"Current working directory must be inside the verified project root: {root}",
        )
    ]


def _validate_path(root):
    issues = []
    for component in root.parts:
        normalized = re.sub(r"[_-]+", " ", component).casefold().strip()
        if any(pattern.search(normalized) for pattern in PROHIBITED_COMPONENT_PATTERNS):
            issues.append(
                error(
                    "project_identity",
                    root,
                    f"Project path contains prohibited archival or generated marker: {component}",
                )
            )
    return issues


def _validate_components(root):
    issues = []
    for relative_path in AUTHORITATIVE_FILES:
        path = root / relative_path
        if not path.is_file():
            issues.append(error("project_identity", path, "Required authoritative source component is missing."))
    for relative_path in AUTHORITATIVE_DIRECTORIES:
        path = root / relative_path
        if not path.is_dir():
            issues.append(error("project_identity", path, "Required authoritative source directory is missing."))
    return issues


def _validate_identity(root):
    identity_path = root / IDENTITY_PATH
    if not identity_path.is_file():
        return [error("project_identity", identity_path, "Machine-readable project identity is missing.")]
    try:
        identity = load_yaml_checked(identity_path)
    except Exception as exc:
        return [error("project_identity", identity_path, f"Project identity YAML error: {exc}")]
    if not isinstance(identity, dict):
        return [error("project_identity", identity_path, "Project identity must be a mapping.")]

    issues = []
    for key, expected in EXPECTED_IDENTITY.items():
        if identity.get(key) != expected:
            issues.append(error("project_identity", identity_path, f"{key} must be {expected!r}."))
    camera = identity.get("camera")
    if not isinstance(camera, dict):
        issues.append(error("project_identity", identity_path, "camera must be a mapping."))
        camera = {}
    for key, expected in EXPECTED_CAMERA.items():
        if camera.get(key) != expected:
            issues.append(error("project_identity", identity_path, f"camera.{key} must be {expected!r}."))

    baseline_path = root / "00 Master/baseline.yaml"
    if not baseline_path.is_file():
        return issues
    try:
        baseline = load_yaml_checked(baseline_path)
    except Exception as exc:
        issues.append(error("project_identity", baseline_path, f"Baseline YAML error: {exc}"))
        return issues
    baseline_camera = baseline.get("camera") if isinstance(baseline, dict) else None
    if not isinstance(baseline_camera, dict):
        issues.append(error("project_identity", baseline_path, "Baseline camera identity is missing."))
        return issues
    for key, expected in EXPECTED_CAMERA.items():
        if baseline_camera.get(key) != expected:
            issues.append(error("project_identity", baseline_path, f"camera.{key} must be {expected!r}."))
        if baseline_camera.get(key) != camera.get(key):
            issues.append(
                error(
                    "project_identity",
                    baseline_path,
                    f"camera.{key} does not agree with {IDENTITY_PATH}.",
                )
            )
    return issues
