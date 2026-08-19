from profile_editor import ProfileEditorModel

from .common import error


REQUIRED_FILES = (
    "80 Build/baseline_impact.py",
    "80 Build/profile_editor.py",
    "80 Build/profile_editor/app.js",
    "80 Build/profile_editor/canon_options.yaml",
    "80 Build/profile_editor/index.html",
    "80 Build/profile_editor/styles.css",
    "80 Build/test_profile_editor.py",
    "80 Build/test_baseline_impact.py",
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
    except Exception as exc:
        issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", f"Profile editor readiness failed: {exc}"))
    return issues
