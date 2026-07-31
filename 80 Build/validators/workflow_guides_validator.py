from workflow_guides import PAGES, WORKFLOW_DIR, expected_workflow_html, workflow_paths

from .common import error


def validate_source(root):
    issues = []
    for stem in PAGES:
        source, _ = workflow_paths(root, stem)
        if not source.is_file():
            issues.append(error("workflow_guides", source, "Workflow Markdown source is missing."))
            continue
        try:
            expected_workflow_html(root, stem)
        except Exception as exc:
            issues.append(error("workflow_guides", source, f"Could not render workflow guide: {exc}"))
    return issues


def validate(root):
    issues = validate_source(root)
    if issues:
        return issues
    for stem in PAGES:
        source, output = workflow_paths(root, stem)
        if not output.is_file():
            issues.append(error("workflow_guides", output, "Generated workflow HTML is missing."))
            continue
        expected = expected_workflow_html(root, stem)
        if output.read_text(encoding="utf-8") != expected:
            issues.append(
                error(
                    "workflow_guides",
                    output,
                    "Workflow HTML is stale. Run the normal build.",
                )
            )

    published = root / "docs" / WORKFLOW_DIR
    if published.exists():
        issues.append(
            error(
                "workflow_guides",
                published,
                "Local workflow guides must never be copied into docs/.",
            )
        )
    return issues
