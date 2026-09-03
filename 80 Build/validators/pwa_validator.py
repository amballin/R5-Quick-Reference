from pwa import validate_merged_build_pwa

from .common import ValidationIssue, resolved_paths


def validate(paths_or_root):
    paths = resolved_paths(paths_or_root)
    return [
        ValidationIssue(level, "Merged Build PWA", str(paths.merged_build_output_dir), detail)
        for level, _, detail in validate_merged_build_pwa(paths)
    ]
