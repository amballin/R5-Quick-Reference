from profile_editor import EXTERNAL_PACK_EDITOR_ENDPOINTS, ProfileEditorModel
from application_version import application_version_info
from asset_manager import ProjectPaths

from .common import error


REQUIRED_FILES = (
    "00 Master/my_menu.yaml",
    "00 Master/my_menu_colors.yaml",
    "80 Build/cx_route_analysis.py",
    "80 Build/my_menu.py",
    "80 Build/my_menu_colors.py",
    "80 Build/my_menu_reference.py",
    "80 Build/baseline_impact.py",
    "80 Build/baseline_impact_check.py",
    "80 Build/baseline_migration.py",
    "80 Build/camera_lab_tracker_import.py",
    "80 Build/profile_editor.py",
    "80 Build/profile_pack_selection.py",
    "80 Build/publication_workflow.py",
    "80 Build/profile_editor/app.js",
    "80 Build/profile_editor/canon_options.yaml",
    "80 Build/profile_editor/control_options.yaml",
    "80 Build/profile_editor/index.html",
    "80 Build/profile_editor/styles.css",
    "80 Build/test_profile_editor.py",
    "80 Build/test_profile_pack_selection.py",
    "80 Build/test_baseline_impact.py",
    "80 Build/test_baseline_impact_check.py",
    "80 Build/test_baseline_migration.py",
    "80 Build/test_cx_route_analysis.py",
)


def validate(root):
    paths = root if isinstance(root, ProjectPaths) else ProjectPaths(root)
    root = paths.application_root
    issues = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            issues.append(error("profile_editor", path, "Required profile-editor source is missing."))
    if issues:
        return issues
    try:
        model = ProfileEditorModel(root, project_paths=paths)
        profiles = model.profile_list()
        if not profiles:
            issues.append(error("profile_editor", paths.profiles_dir, "Profile editor found no profiles."))
        for item in profiles:
            detail = model.profile_detail(item["name"])
            if item["cardType"] == "reference" and detail.get("editableDraft"):
                issues.append(error("profile_editor", paths.profile_file(item["name"]), "Reference cards must remain read-only in the profile editor."))
            if item["cardType"] == "profile" and not detail.get("sourceFingerprint"):
                issues.append(error("profile_editor", paths.profile_file(item["name"]), "Profile sources require a source fingerprint."))
        if paths.profile_pack.mode == "embedded":
            create_detail = model.profile_draft("create")
            if create_detail.get("metadata") != {"status": "Draft", "release": False}:
                issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "New profiles must begin as unreleased drafts."))
        editor_info = model.editor_info()
        expected_version = application_version_info(root)["version"]
        if editor_info.get("version") != expected_version or len(editor_info.get("build") or "") != 8:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "Editor version/build metadata is incomplete."))
        if editor_info.get("read_only") is not False:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "Editor pack access mode is incorrect."))
        expected_access = "guarded-write" if paths.profile_pack.mode == "external" else "embedded"
        if editor_info.get("pack_access") != expected_access:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "Editor guarded pack access metadata is incorrect."))
        evidence_endpoints = {
            "/api/camera-lab-evidence-reviews",
            "/api/camera-lab-evidence-saves",
        }
        if not evidence_endpoints <= EXTERNAL_PACK_EDITOR_ENDPOINTS:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "External guarded editing must allow only the reviewed Camera Lab evidence promotion endpoints."))
        pack_info = editor_info.get("profile_pack") or {}
        if pack_info.get("pack_id") != paths.profile_pack.pack_id or pack_info.get("pack_name") != paths.profile_pack.pack_name:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "Editor selected-pack identity is incomplete."))
        route_catalog = model._my_menu_route_catalog()
        if not route_catalog:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "canon_options.yaml", "My Menu card coverage requires explicit setting identities."))
        declared_paths = {
            setting
            for profile in model.profiles.values()
            for menu in (((profile.get("card") or {}).get("field_setup") or {}).get("my_menus") or [])
            for setting in (menu.get("settings") or [])
        }
        missing_identities = sorted(declared_paths - set(route_catalog))
        if missing_identities:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "canon_options.yaml", f"My Menu card setting identities are missing: {', '.join(missing_identities)}"))
        assignments = model.my_menu_colors.get("assignments") or {}
        saved_names = [tab["name"] for tab in model.my_menu.get("tabs") or []]
        missing_colors = sorted(name for name in saved_names if name not in assignments)
        extra_colors = sorted(name for name in assignments if name not in saved_names)
        if missing_colors or extra_colors:
            issues.append(error("profile_editor", paths.my_menu_colors_file, "Saved My Menu tabs and color assignments must have identical names."))
        cx_detail = model.cx_foundation_detail()
        cx_assignments = cx_detail.get("assignments") or {}
        if set(cx_assignments) != {"C1", "C2", "C3"} or len(set(cx_assignments.values())) != 3:
            issues.append(error("profile_editor", paths.controls_file, "Cx Foundation requires three distinct C1-C3 profile assignments."))
        fit = cx_detail.get("fit") or []
        if len(fit) != 3 or {item.get("start") for item in fit} != {"C1", "C2", "C3"}:
            issues.append(error("profile_editor", root / "80 Build" / "cx_route_analysis.py", "Cx Foundation Fit must compare C1, C2, and C3 simultaneously."))
        elif not all(isinstance(item.get("change_count"), int) and isinstance(item.get("recommended"), bool) for item in fit):
            issues.append(error("profile_editor", root / "80 Build" / "cx_route_analysis.py", "Cx Foundation Fit counts and recommendations are incomplete."))
        html = (root / "80 Build" / "profile_editor" / "index.html").read_text(encoding="utf-8")
        script = (root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")
        styles = (root / "80 Build" / "profile_editor" / "styles.css").read_text(encoding="utf-8")
        if not (
            html.find('data-view="profiles"')
            < html.find('data-view="cx-foundation"')
            < html.find('data-view="my-menu"')
        ):
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "index.html", "Cx Foundation must follow Profiles and precede My Menu."))
        sidebar_order = (
            "today", "profiles", "review-build", "finish-day", "cx-foundation", "my-menu",
            "camera-buttons", "baseline", "deleted-cards", "branch-integration",
            "release-publish", "cleanup-review", "setup-sharing", "dictionary",
        )
        positions = [html.find(f'data-view="{view}"') for view in sidebar_order]
        if -1 in positions or positions != sorted(positions):
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "index.html", "Sidebar workflow groups are not in the required working, setup, and occasional order."))
        button_detail = model.control_editor_detail()
        for group in ("controls", "dials"):
            for item in button_detail.get(group) or []:
                options = (button_detail.get("options") or {}).get(group, {}).get(item.get("control"), {})
                if not options.get("default") or not options.get("assignment_options"):
                    issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "control_options.yaml", f"Camera Buttons defaults/options are missing for {item.get('control')}."))
                if not options.get("iconUrl"):
                    issues.append(error("profile_editor", root / "60 Assets" / "icon-map.yaml", f"Camera Buttons editor/card icon is missing for {item.get('control')}."))
        for endpoint in ("/api/cx-foundation-fit", "/api/cx-assignment-reviews", "/api/cx-selection-reviews", "/api/cx-foundation-saves"):
            if endpoint not in script:
                issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "app.js", f"Cx Foundation browser endpoint is missing: {endpoint}"))
        for endpoint in (
            "/api/publication-status",
            "/api/publication-notes-review",
            "/api/publication-notes-save",
            "/api/publication-review",
            "/api/publication-start",
            "/api/main-editor-launch",
        ):
            if endpoint not in script:
                issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "app.js", f"Publication browser endpoint is missing: {endpoint}"))
        for endpoint in (
            "/api/camera-buttons-preview",
            "/api/camera-buttons-reviews",
            "/api/camera-buttons-saves",
            "/api/camera-lab-evidence-reviews",
            "/api/camera-lab-evidence-saves",
        ):
            if endpoint not in script:
                issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "app.js", f"Guarded editor endpoint is missing: {endpoint}"))
        for element_id in (
            "local-build-progress",
            "local-build-progress-stage",
            "local-build-progress-elapsed",
            "local-build-progress-command",
            "local-build-progress-log",
            "local-build-details",
        ):
            if f'id="{element_id}"' not in html:
                issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "index.html", f"Review & Build progress element is missing: {element_id}"))
        if 'localBuild: "profileEditor.localBuildJob"' not in script or "reconnectLocalBuild" not in script:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "app.js", "Review & Build must retain and reconnect to its guarded local-build job."))
        for marker in (
            '"review-build"',
            "configureExternalEvidenceReview",
            "Camera Lab evidence can be deliberately promoted",
            "elements.sessionSummary.hidden = true",
            'document.querySelector("#pending-review-summary").hidden = true',
            'document.querySelector("#local-build-panel").hidden = true',
        ):
            if marker not in script:
                issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "app.js", f"External-pack evidence-review boundary is missing: {marker}"))
        for element_id in ("pending-review-summary", "local-build-panel"):
            if f'id="{element_id}"' not in html:
                issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "index.html", f"External evidence-review boundary element is missing: {element_id}"))
        if "#session-summary[hidden]" not in styles or "#local-build-panel[hidden]" not in styles:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "styles.css", "External evidence review must visually hide draft and build-only panels."))
    except Exception as exc:
        issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", f"Profile editor readiness failed: {exc}"))
    return issues
