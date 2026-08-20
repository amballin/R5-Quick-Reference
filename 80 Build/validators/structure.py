from .common import error


REQUIRED_FOLDERS = [
    "00 Master",
    "10 Profiles",
    "20 Templates",
    "40 Assets",
    "60 Assets",
    "80 Build",
    "WORKFLOWS",
]

REQUIRED_FILES = [
    "PROJECT_RULES.md",
    "00 Master/project_identity.yaml",
    "00 Master/project_memory.md",
    "00 Master/decision-log.md",
    "00 Master/baseline.yaml",
    "00 Master/schema.yaml",
    "00 Master/card_layout.yaml",
    "00 Master/setting_access.yaml",
    "00 Master/spreadsheet_layouts.yaml",
    "00 Master/release_notes.yaml",
    "90 Testing/eos_r5_verification_tracker.yaml",
    "90 Testing/eos_r5_verification_status.yaml",
    "20 Templates/card.html",
    "60 Assets/icon-map.yaml",
    "build.py",
    "80 Build/verify_publication.py",
    "80 Build/baseline_impact_check.py",
    "80 Build/release_notes.py",
    "80 Build/validators/release_notes_validator.py",
    "80 Build/validators/project_identity_validator.py",
    "80 Build/workflow_guides.py",
    "WORKFLOWS/index.md",
    "00 Master/specifications/Architecture.md",
    "00 Master/specifications/Profile Specification.md",
    "00 Master/specifications/Card Specification.md",
    "00 Master/specifications/Appendix Specification.md",
    "00 Master/specifications/Asset Specification.md",
    "00 Master/specifications/Build and Validation Specification.md",
]


def validate(root):
    issues = []
    for folder in REQUIRED_FOLDERS:
        path = root / folder
        if not path.is_dir():
            issues.append(error("project_structure", path, "Required folder is missing."))
    for file_path in REQUIRED_FILES:
        path = root / file_path
        if not path.is_file():
            issues.append(error("project_structure", path, "Required file is missing."))
    testing_dir = root / "90 Testing"
    for pattern in ("*.xlsx", "*.numbers"):
        for path in sorted(testing_dir.glob(pattern)):
            issues.append(
                error(
                    "project_structure",
                    path,
                    "Verification workbooks must remain machine-local; Git-tracked YAML is canonical.",
                )
            )
    return issues
