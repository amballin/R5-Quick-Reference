import json
import os
from datetime import datetime
from pathlib import Path
import shutil
import subprocess

from spreadsheet_revisions import (
    registration_definition_fingerprints,
    short_fingerprint,
    source_fingerprint,
    tracker_definition_fingerprints,
    workbook_revision,
)
from spreadsheet_ooxml import (
    enable_automatic_row_heights,
    ensure_active_sheet,
    ensure_freeze_panes,
    prefer_rgb_border_colors,
)
from validators.common import load_yaml_checked


DEFAULT_NODE = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
DEFAULT_NODE_MODULES = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"


def generate_camera_setup_tracker(
    paths,
    output_path=None,
    migration_source=None,
    status_data=None,
):
    """Generate the blank Setup tracker or a migrated local working copy."""
    layouts = load_yaml_checked(paths.spreadsheet_layouts_file) or {}
    source = load_yaml_checked(paths.verification_tracker_source_file) or {}
    layout = ((layouts.get("workbooks") or {}).get("setup") or {})
    output_path = Path(output_path or paths.setup_tracker_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    runtime_dir = paths.reports_output_dir / ".setup-tracker-runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    modules_dir = _artifact_modules(paths)
    node_link = runtime_dir / "node_modules"
    if node_link.is_symlink() or node_link.exists():
        if node_link.is_dir() and not node_link.is_symlink():
            shutil.rmtree(node_link)
        else:
            node_link.unlink()
    node_link.symlink_to(modules_dir, target_is_directory=True)

    is_working_copy = migration_source is not None or status_data is not None
    preview_dir = runtime_dir / ("working-previews" if is_working_copy else "previews")
    preview_dir.mkdir(parents=True, exist_ok=True)
    payload_path = runtime_dir / "payload.json"
    payload = {
        "output": str(output_path),
        "preview_dir": str(preview_dir),
        "runtime_dir": str(runtime_dir),
        "layout": layout,
        "shared_layout": layouts.get("shared") or {},
        "source": source,
        "migration_source": str(Path(migration_source).resolve()) if migration_source else None,
        "status": status_data,
        "workbook_revision": workbook_revision(paths, "setup"),
        "source_fingerprint": source_fingerprint(paths, "setup"),
        "definition_fingerprints": {
            "tests": tracker_definition_fingerprints(source),
            "registration": registration_definition_fingerprints(source),
        },
        "release_label": (
            f"Workbook revision {workbook_revision(paths, 'setup')} • "
            f"Source {short_fingerprint(source_fingerprint(paths, 'setup'))} • "
            f"Generated {datetime.now().astimezone().date().isoformat()}"
        ),
    }
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    command = [
        _node_binary(),
        str(paths.root / "80 Build" / "render_camera_setup_tracker.mjs"),
        str(payload_path),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
    finally:
        payload_path.unlink(missing_ok=True)

    sheets = layout.get("sheets") or {}
    tests = source.get("tests") or []
    registration_rows = ((source.get("registration") or {}).get("rows") or [])
    enable_automatic_row_heights(
        output_path,
        {
            sheets["menu"]["name"]: [(1, 1 + len(tests))],
            sheets["checklist"]["name"]: [(5, 5 + len(tests))],
            sheets["registration"]["name"]: [(4, 4 + len(registration_rows))],
            sheets["sessions"]["name"]: [(4, None)],
        },
    )
    checklist = ((layout.get("sheets") or {}).get("checklist") or {})
    excel = checklist.get("excel") or {}
    ensure_freeze_panes(
        output_path,
        checklist["name"],
        frozen_rows=excel["freeze_rows"],
        frozen_columns=excel["freeze_columns"],
    )
    registration = ((layout.get("sheets") or {}).get("registration") or {})
    ensure_freeze_panes(
        output_path,
        registration["name"],
        frozen_rows=registration["freeze_rows"],
        frozen_columns=registration["freeze_columns"],
    )
    dashboard = ((layout.get("sheets") or {}).get("dashboard") or {})
    if dashboard.get("active_on_open"):
        ensure_active_sheet(output_path, dashboard["name"])
    prefer_rgb_border_colors(output_path)
    return {
        "XLSX": 1 if output_path.exists() else 0,
        "setup_tracker_preview_dir": preview_dir,
        "output": output_path,
    }


def remove_camera_setup_tracker(paths):
    for path in (
        paths.setup_tracker_file,
        paths.setup_tracker_numbers_file,
        paths.setup_tracker_download_manifest_file,
        paths.reports_output_dir / ".setup-tracker-runtime",
    ):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists() or path.is_symlink():
            path.unlink()


def _artifact_modules(paths):
    configured = os.environ.get("PRS_ARTIFACT_TOOL_NODE_MODULES")
    candidates = [
        Path(configured).expanduser() if configured else None,
        paths.root / "node_modules",
        Path(DEFAULT_NODE_MODULES),
    ]
    for candidate in candidates:
        if candidate and (candidate / "@oai" / "artifact-tool").is_dir():
            return candidate.resolve()
    raise RuntimeError(
        "Spreadsheet generation requires @oai/artifact-tool. "
        "Set PRS_ARTIFACT_TOOL_NODE_MODULES to the node_modules directory that contains it."
    )


def _node_binary():
    return os.environ.get("NODE") or shutil.which("node") or DEFAULT_NODE
