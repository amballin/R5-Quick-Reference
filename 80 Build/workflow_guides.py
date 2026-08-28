#!/usr/bin/env python3
"""Generate the tracked, local-only workflow HTML pages."""

from pathlib import Path

from finish_day_guide import render_guide_html


WORKFLOW_DIR = "WORKFLOWS"
PAGES = {
    "index": "Workflow Index",
    "preflight": "Preflight",
    "other-mac": "Continue on Another Mac",
    "local-build": "Local Build",
    "profile-editor": "Profile Editor",
    "editor-user-guide": "Profile Editor User Guide",
    "camera-lab-user-guide": "Camera Lab User Guide",
    "spreadsheets": "Spreadsheet Workflows",
    "verification-testing": "On-Camera Verification Testing",
    "usb-camera-configuration": "USB Camera Configuration",
    "publish": "Publish the Website",
    "recovery": "Recovery and Troubleshooting",
}


def workflow_paths(root, stem):
    directory = Path(root).resolve() / WORKFLOW_DIR
    return directory / f"{stem}.md", directory / f"{stem}.html"


def expected_workflow_html(root, stem):
    source, _ = workflow_paths(root, stem)
    if stem == "index":
        navigation = '<a href="../FINISH_DAY.html">Finish Day</a>'
    else:
        navigation = (
            '<a href="index.html">Workflow Index</a>'
            '<a href="../FINISH_DAY.html">Finish Day</a>'
        )
    return render_guide_html(
        source.read_text(encoding="utf-8"),
        PAGES[stem],
        f"Generated from WORKFLOWS/{stem}.md. Local project guidance; never published.",
        navigation,
        project_terminal=stem == "index",
    )


def write_workflow_guides(root):
    written = []
    for stem in PAGES:
        source, output = workflow_paths(root, stem)
        if not source.is_file():
            raise FileNotFoundError(f"Workflow source is missing: {source}")
        rendered = expected_workflow_html(root, stem)
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            output.write_text(rendered, encoding="utf-8")
            written.append(output)
    if written:
        print(f"Workflow HTML guides generated: {len(written)}")
    return written


if __name__ == "__main__":
    write_workflow_guides(Path(__file__).resolve().parent.parent)
