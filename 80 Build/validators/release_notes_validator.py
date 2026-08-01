from release_notes import ReleaseNotesError, load_release_notes

from .common import error


def validate(root):
    path = root / "00 Master/release_notes.yaml"
    try:
        load_release_notes(path)
    except (OSError, ReleaseNotesError, ValueError) as exc:
        return [error("release_notes", path, str(exc))]
    return []
