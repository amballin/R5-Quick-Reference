from asset_manager import ProjectPaths
from pwa import validate_merged_build_pwa

from .common import ValidationIssue


def validate(root):
    paths = ProjectPaths(root)
    return [
        ValidationIssue(level, "Merged Build PWA", str(paths.merged_build_output_dir), detail)
        for level, _, detail in validate_merged_build_pwa(paths)
    ]
