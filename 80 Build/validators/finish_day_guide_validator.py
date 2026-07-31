from finish_day_guide import OUTPUT_NAME, SOURCE_NAME, expected_finish_day_html

from .common import error


def validate_source(root):
    source = root / SOURCE_NAME
    issues = []
    if not source.exists():
        issues.append(error("finish_day_guide", source, "The concise finish-day source is missing."))
        return issues
    try:
        expected_finish_day_html(root)
    except (OSError, ValueError) as exc:
        issues.append(error("finish_day_guide", source, f"Could not render the guide: {exc}"))
    return issues


def validate(root):
    source = root / SOURCE_NAME
    output = root / OUTPUT_NAME
    issues = validate_source(root)
    if issues:
        return issues
    if not output.exists():
        issues.append(
            error(
                "finish_day_guide",
                output,
                'Generated guide is missing. Run python3 "80 Build/build.py".',
            )
        )
        return issues
    expected = expected_finish_day_html(root)
    if output.read_text(encoding="utf-8") != expected:
        issues.append(
            error(
                "finish_day_guide",
                output,
                'Generated guide is stale. Run python3 "80 Build/build.py".',
            )
        )
    return issues
