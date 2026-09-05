"""Validate the exact GitHub application-owner routing boundary."""

from .common import error


CODEOWNERS_RELATIVE = ".github/CODEOWNERS"
EXPECTED_RULES = (
    "/.github/ @amballin",
    "/00\\ Master/profile_catalog_policy.yaml @amballin",
    "/00\\ Master/profile_lens_guidance.yaml @amballin",
    "/10\\ Profiles/ @amballin",
)


def validate(root):
    path = root / CODEOWNERS_RELATIVE
    if not path.is_file():
        return [error("codeowners", path, "The application-owner CODEOWNERS boundary is missing.")]
    try:
        lines = tuple(
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    except (OSError, UnicodeError) as exc:
        return [error("codeowners", path, f"CODEOWNERS is unreadable: {exc}")]
    if lines != EXPECTED_RULES:
        return [
            error(
                "codeowners",
                path,
                "CODEOWNERS must retain the exact @amballin ownership rules for .github, the catalog policy, lens guidance, and 10 Profiles.",
            )
        ]
    return []
