from asset_manager import ProjectPaths
from .common import error, load_yaml_checked


def validate(root):
    issues = []
    paths = ProjectPaths(root)
    layouts = load_yaml_checked(paths.spreadsheet_layouts_file) or {}
    source = load_yaml_checked(paths.verification_tracker_source_file) or {}
    workbooks = layouts.get("workbooks") or {}
    for target in ("matrix", "setup"):
        if target not in workbooks:
            issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, f"Missing {target} layout."))
        elif not isinstance((workbooks[target] or {}).get("revision"), int) or workbooks[target]["revision"] < 1:
            issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, f"{target} revision must be a positive integer."))

    setup = workbooks.get("setup") or {}
    checklist = ((setup.get("sheets") or {}).get("checklist") or {})
    columns = checklist.get("columns") or []
    keys = [column.get("key") for column in columns if isinstance(column, dict)]
    required = {
        "test_id",
        "best_access",
        "menu_location",
        "menu_detail",
        "status",
        "updated_in_project",
    }
    missing = sorted(required - set(keys))
    if missing:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, f"Setup Checklist columns missing: {missing}"))
    if (checklist.get("excel") or {}).get("freeze_columns") != 1:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Setup Checklist must freeze Excel column A."))
    if (checklist.get("numbers") or {}).get("header_columns") != 1:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Setup Checklist must assign Numbers column A as a frozen header column."))
    status_column = next((column for column in columns if column.get("key") == "status"), {})
    if status_column.get("alignment") != "center":
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Setup Checklist Status column I must be centered."))
    menu_column = next((column for column in columns if column.get("key") == "menu_location"), {})
    if menu_column.get("alignment") != "center" or menu_column.get("bold") is not True:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Setup Menu Location must be centered and bold."))
    alignment = checklist.get("banner_alignment") or {}
    if alignment.get("left_px") != 0:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Checklist banner and table must share the zero-pixel left edge."))

    sheets = setup.get("sheets") or {}
    dashboard = sheets.get("dashboard") or {}
    if dashboard.get("active_on_open") is not True:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Dashboard must be active when the Setup workbook opens."))
    if dashboard.get("centered_columns") != ["B", "C", "D", "E", "H"]:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Dashboard centered columns must be B, C, D, E, and H."))
    completion_rules = dashboard.get("completion_rules") or []
    expected_completion_rules = [
        {"operator": "equal", "value": 1, "font_color": "success"},
        {
            "operator": "between",
            "values": [0.0001, 0.9999],
            "font_color": "dark_text",
            "fill": "pale_warning",
            "bold": True,
        },
        {"operator": "equal", "value": 0, "italic": True},
    ]
    if completion_rules != expected_completion_rules:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Dashboard Completion rules must match the approved 100%, partial, and 0% styles."))
    registration = sheets.get("registration") or {}
    if registration.get("freeze_columns") != 1:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "C1-C3 Registration must freeze Excel column A."))
    if (registration.get("numbers") or {}).get("header_columns") != 1:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "C1-C3 Registration must freeze Numbers column A."))
    if (registration.get("numbers") or {}).get("header_rows") != 4:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "C1-C3 Registration must retain four frozen Numbers header rows."))
    if registration.get("column_alignments") != {
        "A": "right",
        "B": "center",
        "F": "center",
        "J": "center",
    }:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "C1-C3 Registration must right-align A and center target columns B, F, and J."))
    if registration.get("outer_borders") != {
        "color": "blue",
        "weight_pt": 3,
        "ranges": ["A:A", "B:E", "F:I", "J:M"],
    }:
        issues.append(
            error(
                "spreadsheet_specs",
                paths.spreadsheet_layouts_file,
                "C1-C3 Registration outer borders must frame A, B:E, F:I, and J:M in 3-point blue.",
            )
        )
    if (sheets.get("metadata") or {}).get("name") != "Metadata":
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Setup Metadata sheet is required."))

    tests = source.get("tests") or []
    ids = [test.get("test_id") for test in tests if isinstance(test, dict)]
    sequences = [test.get("sequence") for test in tests if isinstance(test, dict)]
    if len(ids) != len(set(ids)):
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "Verification Test IDs must be unique."))
    if sequences != list(range(1, len(tests) + 1)):
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "Verification sequences must be consecutive and ordered."))
    my_menu = next((test for test in tests if test.get("test_id") == "SETUP-MM-01"), None)
    if not my_menu or my_menu.get("sequence", 999) > 4:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "The SWITCH My Menu setup must occur by sequence 4."))
    statuses = ((source.get("lists") or {}).get("main_status") or [])
    if "Backup-Settings" not in statuses:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "Main Status must include Backup-Settings."))
    backup_ids = [test.get("test_id") for test in tests if str(test.get("test_id", "")).startswith("BACKUP-SET-")]
    if backup_ids != ["BACKUP-SET-01", "BACKUP-SET-02"]:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "The two required Backup-Settings checkpoints are missing or out of order."))
    for test in tests:
        for key in ("test_id", "phase", "expected_result", "task", "best_access", "menu_location", "menu_detail"):
            if test.get(key) in (None, ""):
                issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, f"{test.get('test_id', '<unknown>')} is missing {key}."))
    return issues
