from .common import error, load_yaml_checked


def validate(root):
    path = root / "00 Master" / "my_menu.yaml"
    try:
        from my_menu import MyMenuError, validate_my_menu

        catalog = load_yaml_checked(root / "80 Build" / "profile_editor" / "canon_options.yaml") or {}
        known = {
            item.get("id")
            for section in catalog.get("reference_sections") or []
            for item in section.get("items") or []
            if isinstance(item, dict) and item.get("id")
        }
        validate_my_menu(load_yaml_checked(path) or {}, known)
    except (OSError, ValueError, MyMenuError) as exc:
        return [error("my_menu", path, str(exc))]
    return []
