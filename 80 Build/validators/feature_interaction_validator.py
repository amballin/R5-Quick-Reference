import yaml

from feature_interactions import CATALOG, validate_catalog
from utilities import flatten

from .common import error


def validate(root):
    path = root / CATALOG
    if not path.is_file():
        return [error("feature_interactions", path, "Feature-interaction catalog is missing.")]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        baseline = yaml.safe_load((root / "00 Master" / "baseline.yaml").read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return [error("feature_interactions", path, f"Feature-interaction sources could not be read: {exc}")]
    known_paths = set(flatten(baseline.get("defaults") or {}))
    return [error("feature_interactions", path, message) for message in validate_catalog(data, known_paths)]
