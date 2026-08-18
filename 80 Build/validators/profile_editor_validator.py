from profile_editor import ProfileEditorModel

from .common import error


REQUIRED_FILES = (
    "80 Build/profile_editor.py",
    "80 Build/profile_editor/app.js",
    "80 Build/profile_editor/canon_options.yaml",
    "80 Build/profile_editor/index.html",
    "80 Build/profile_editor/styles.css",
    "80 Build/test_profile_editor.py",
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
    except Exception as exc:
        issues.append(error("profile_editor", root / "80 Build" / "profile_editor.py", f"Profile editor readiness failed: {exc}"))
    return issues
