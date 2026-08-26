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
    "00 Master/application_version.yaml",
    "00 Master/decision-log.md",
    "00 Master/baseline.yaml",
    "00 Master/schema.yaml",
    "00 Master/card_layout.yaml",
    "00 Master/camera_capabilities.yaml",
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
    "80 Build/camera_control/connect_probe.py",
    "80 Build/camera_control/capability_registry.py",
    "80 Build/camera_control/capability_mapping.py",
    "80 Build/camera_control/dev_server.py",
    "80 Build/camera_control/native/edsdk_helper.c",
    "80 Build/camera_control/native/helper.entitlements",
    "80 Build/camera_control/native_backend.py",
    "80 Build/camera_control/service.py",
    "80 Build/camera_control/static/index.html",
    "80 Build/camera_control/static/app.js",
    "80 Build/camera_control/static/styles.css",
    "80 Build/app_wrappers.py",
    "80 Build/application_version.py",
    "80 Build/scripts/build-app-wrappers.sh",
    "80 Build/scripts/complete-development-update.sh",
    "80 Build/scripts/profile-editor-runtime.sh",
    "80 Build/scripts/start-profile-editor.sh",
    "80 Build/scripts/stop-profile-editor.sh",
    "80 Build/test_app_wrappers.py",
    "80 Build/test_application_version.py",
    "80 Build/test_camera_control_connect.py",
    "80 Build/test_camera_control_lab.py",
    "80 Build/release_notes.py",
    "80 Build/validators/release_notes_validator.py",
    "80 Build/validators/application_version_validator.py",
    "80 Build/validators/project_identity_validator.py",
    "80 Build/validators/camera_capability_validator.py",
    "80 Build/workflow_guides.py",
    "Start Camera Lab.command",
    "Start Profile Editor.command",
    "Stop Profile Editor.command",
    "WORKFLOWS/index.md",
    "00 Master/specifications/Architecture.md",
    "00 Master/specifications/Profile Specification.md",
    "00 Master/specifications/Card Specification.md",
    "00 Master/specifications/Appendix Specification.md",
    "00 Master/specifications/Asset Specification.md",
    "00 Master/specifications/Build and Validation Specification.md",
    "00 Master/specifications/USB Camera Configuration Specification.md",
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
