from profile_editor import ProfileEditorModel
from application_version import application_version_info

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
    "80 Build/profile_editor.py",
    "80 Build/publication_workflow.py",
    "80 Build/profile_editor/app.js",
    "80 Build/profile_editor/canon_options.yaml",
    "80 Build/profile_editor/index.html",
    "80 Build/profile_editor/styles.css",
    "80 Build/test_profile_editor.py",
    "80 Build/test_baseline_impact.py",
    "80 Build/test_baseline_impact_check.py",
    "80 Build/test_baseline_migration.py",
    "80 Build/test_cx_route_analysis.py",
)


def validate(root):
    issues = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            issues.append(error("profile_editor", path, "Required profile-editor source is missing."))
    if issues:
        return issues
    try:
        model = ProfileEditorModel(root)
        profiles = model.profile_list()
        if not profiles:
            issues.append(error("profile_editor", root / "10 Profiles", "Profile editor found no profiles."))
        for item in profiles:
            detail = model.profile_detail(item["name"])
            if item["cardType"] == "reference" and detail.get("editableDraft"):
                issues.append(error("profile_editor", root / "10 Profiles" / f"{item['name']}.yaml", "Reference cards must remain read-only in the profile editor."))
            if item["cardType"] == "profile" and not detail.get("sourceFingerprint"):
                issues.append(error("profile_editor", root / "10 Profiles" / f"{item['name']}.yaml", "Writable profiles require a source fingerprint."))
        create_detail = model.profile_draft("create")
        if create_detail.get("metadata") != {"status": "Draft", "release": False}:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "New profiles must begin as unreleased drafts."))
        editor_info = model.editor_info()
        expected_version = application_version_info(root)["version"]
        if editor_info.get("version") != expected_version or len(editor_info.get("build") or "") != 8:
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", "Editor version/build metadata is incomplete."))
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
            issues.append(error("profile_editor", root / "00 Master" / "my_menu_colors.yaml", "Saved My Menu tabs and color assignments must have identical names."))
        cx_detail = model.cx_foundation_detail()
        cx_assignments = cx_detail.get("assignments") or {}
        if set(cx_assignments) != {"C1", "C2", "C3"} or len(set(cx_assignments.values())) != 3:
            issues.append(error("profile_editor", root / "controls.yaml", "Cx Foundation requires three distinct C1-C3 profile assignments."))
        fit = cx_detail.get("fit") or []
        if len(fit) != 3 or {item.get("start") for item in fit} != {"C1", "C2", "C3"}:
            issues.append(error("profile_editor", root / "80 Build" / "cx_route_analysis.py", "Cx Foundation Fit must compare C1, C2, and C3 simultaneously."))
        elif not all(isinstance(item.get("change_count"), int) and isinstance(item.get("recommended"), bool) for item in fit):
            issues.append(error("profile_editor", root / "80 Build" / "cx_route_analysis.py", "Cx Foundation Fit counts and recommendations are incomplete."))
        html = (root / "80 Build" / "profile_editor" / "index.html").read_text(encoding="utf-8")
        script = (root / "80 Build" / "profile_editor" / "app.js").read_text(encoding="utf-8")
        if not (
            html.find('data-view="profiles"')
            < html.find('data-view="cx-foundation"')
            < html.find('data-view="my-menu"')
        ):
            issues.append(error("profile_editor", root / "80 Build" / "profile_editor" / "index.html", "Cx Foundation must follow Profiles and precede My Menu."))
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
    except Exception as exc:
        issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", f"Profile editor readiness failed: {exc}"))
    return issues
