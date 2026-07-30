import json
import os
from pathlib import Path
import shutil
import subprocess

from spreadsheet_ooxml import ensure_active_sheet, ensure_freeze_panes
from validators.common import load_yaml_checked


DEFAULT_NODE = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
DEFAULT_NODE_MODULES = "/Users/andy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"


def generate_camera_setup_tracker(paths, output_path=None, migration_source=None):
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

    preview_dir = runtime_dir / ("working-previews" if migration_source else "previews")
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
