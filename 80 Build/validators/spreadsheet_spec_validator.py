from copy import deepcopy

from asset_manager import ProjectPaths
from camera_setup_tracker import materialize_registration_values
from .common import error, load_yaml_checked


def validate(root):
    issues = []
    paths = ProjectPaths(root)
    layouts = load_yaml_checked(paths.spreadsheet_layouts_file) or {}
    source = load_yaml_checked(paths.verification_tracker_source_file) or {}
    workbooks = layouts.get("workbooks") or {}
    colors = ((layouts.get("shared") or {}).get("colors") or {})
    if colors.get("comparison_highlight") != "#FFFC98":
        issues.append(
            error(
                "spreadsheet_specs",
                paths.spreadsheet_layouts_file,
                "C1-C3 comparison highlighting must use the approved pale yellow #FFFC98.",
            )
        )
    for target in ("matrix", "setup"):
        if target not in workbooks:
            issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, f"Missing {target} layout."))
        elif not isinstance((workbooks[target] or {}).get("revision"), int) or workbooks[target]["revision"] < 1:
            issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, f"{target} revision must be a positive integer."))

    matrix = workbooks.get("matrix") or {}
    if (matrix.get("excel") or {}).get("import_only_rows") != 3:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Subject Settings Matrix must preserve the comparison row after removing its three banner rows in Numbers."))
    if (matrix.get("excel") or {}).get("freeze_rows") != 6:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Subject Settings Matrix must freeze its comparison row, card-start row, and table header below the three-row banner."))
    if (matrix.get("numbers") or {}).get("header_rows") != 3:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Subject Settings Matrix must freeze the comparison row, card-start row, and table header as three Numbers header rows."))
    if matrix.get("comparison_controls") != {
        "row": 4,
        "label_column": "A",
        "first_target_column": "D",
        "default_selection": "self",
        "fill": "comparison_highlight",
        "font_color": "#000000",
        "helper_width_px": 2,
    }:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Subject Settings Matrix comparison controls must begin in frozen row 4, default to self-comparison, and use one narrow same-sheet helper per target."))
    if matrix.get("card_start_controls") != {
        "row": 5,
        "label_column": "A",
        "label": "Card starts from:",
        "default_value": "Camera defaults",
        "empty_value": "—",
        "fill": "pale_blue",
        "font_color": "#17324D",
    }:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Subject Settings Matrix must show the authored card-start route in frozen row 5."))
    registered_profiles = matrix.get("registered_profiles") or {}
    if registered_profiles.get("keys") != ["c1", "c2", "c3"]:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Subject Settings Matrix must include static editable C1, C2, and C3 columns in order."))
    defaults_sheet = registered_profiles.get("defaults_sheet") or {}
    if defaults_sheet != {
        "worksheet": "C1-C3 Defaults",
        "table_name": "CxDefaultsTable",
        "note": "Approved registration targets pending physical verification. Ordinary copy/paste back to the matching C1–C3 column restores both the target values and compatible comparison highlighting.",
        "excel": {"freeze_rows": 2, "freeze_columns": 1},
        "numbers": {
            "header_rows": 2,
            "frozen_header_rows": True,
            "header_columns": 1,
            "frozen_header_columns": True,
        },
    }:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Subject Settings Matrix must keep the approved C1-C3 restoration table with transferable comparison highlighting on the frozen C1-C3 Defaults worksheet."))
    registration_profiles = (source.get("registration") or {}).get("profiles") or []
    registration_keys = [profile.get("key") for profile in registration_profiles if isinstance(profile, dict)]
    if registration_keys != ["c1", "c2", "c3"]:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "Subject Settings Matrix and its defaults table require C1, C2, and C3 registration profiles in order."))

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
        "C": "center",
        "G": "center",
        "K": "center",
    }:
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "C1-C3 Registration must right-align A and center target columns B, C, G, and K."))
    if registration.get("comparison_controls") != {
        "row": 3,
        "label_column": "A",
        "fill": "comparison_highlight",
        "font_color": "#000000",
        "targets": {
            "B": {"source": "default", "default": "B", "helper": "O"},
            "C": {"profile": "c1", "default": "B", "helper": "P"},
            "G": {"profile": "c2", "default": "B", "helper": "Q"},
            "K": {"profile": "c3", "default": "B", "helper": "R"},
        },
    }:
        issues.append(
            error(
                "spreadsheet_specs",
                paths.spreadsheet_layouts_file,
                "C1-C3 Registration must keep Compare to in frozen A3 and give Default, C1, C2, and C3 named-target selectors with self-comparison support.",
            )
        )
    if registration.get("outer_borders") != {
        "color": "blue",
        "weight_pt": 3,
        "ranges": ["A:A", "B:B", "C:F", "G:J", "K:N"],
    }:
        issues.append(
            error(
                "spreadsheet_specs",
                paths.spreadsheet_layouts_file,
                "C1-C3 Registration outer borders must frame A, B, C:F, G:J, and K:N in 3-point blue.",
            )
        )
    if (sheets.get("metadata") or {}).get("name") != "Metadata":
        issues.append(error("spreadsheet_specs", paths.spreadsheet_layouts_file, "Setup Metadata sheet is required."))

    tests = source.get("tests") or []
    registration_rows = ((source.get("registration") or {}).get("rows") or [])
    missing_baseline_keys = [row.get("setting") for row in registration_rows if not row.get("baseline_key")]
    if missing_baseline_keys:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, f"Registration rows missing baseline_key: {missing_baseline_keys}"))
    defaults = (load_yaml_checked(paths.baseline_file) or {}).get("defaults") or {}
    materialized_registration = deepcopy(source.get("registration") or {})
    try:
        materialize_registration_values(materialized_registration, defaults)
    except (KeyError, TypeError, ValueError) as exc:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, f"C1-C3 registration targets cannot be generated: {exc}"))
    else:
        required_targets = ["default_value", "c1", "c2", "c3"]
        incomplete_targets = [
            f"{row.get('setting', '<unknown>')}:{key}"
            for row in materialized_registration.get("rows") or []
            for key in required_targets
            if row.get(key) in (None, "")
        ]
        if incomplete_targets:
            issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, f"Generated C1-C3 registration values are incomplete: {incomplete_targets}"))
        source_rows = {
            row.get("setting"): row
            for row in registration_rows
            if isinstance(row, dict) and row.get("setting")
        }
        redundant_overrides = [
            f"{row.get('setting', '<unknown>')}:{key}"
            for row in materialized_registration.get("rows") or []
            for key in ("c1", "c2", "c3")
            if key in source_rows.get(row.get("setting"), {})
            and row.get(key) == row.get("default_value")
        ]
        if redundant_overrides:
            issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, f"C1-C3 rows must omit values inherited unchanged from the baseline: {redundant_overrides}"))
    ids = [test.get("test_id") for test in tests if isinstance(test, dict)]
    sequences = [test.get("sequence") for test in tests if isinstance(test, dict)]
    if len(ids) != len(set(ids)):
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "Verification Test IDs must be unique."))
    if sequences != list(range(1, len(tests) + 1)):
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "Verification sequences must be consecutive and ordered."))
    switch_menu = next((test for test in tests if test.get("test_id") == "SETUP-MM-01"), None)
    af_case_menu = next((test for test in tests if test.get("test_id") == "SETUP-MM-AF-01"), None)
    if not switch_menu or switch_menu.get("sequence") != 4:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "The dedicated SWITCH My Menu test must be sequence 4."))
    if not af_case_menu or af_case_menu.get("sequence") != 5:
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "The dedicated AF Case My Menu test must immediately follow SWITCH at sequence 5."))
    switch_items = [
        "Subject to detect",
        "Shutter mode",
        "Focus bracketing",
        "IS (Image Stabilizer) mode",
        "Cropping/aspect ratio",
    ]
    if switch_menu and not _contains_in_order(switch_menu.get("menu_detail", ""), switch_items):
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "The SWITCH My Menu test must list all five approved shortcuts in order."))
    af_case_items = ["Servo AF", "Tracking Sensitivity", "Accel./Decel. tracking"]
    if af_case_menu and not _contains_in_order(af_case_menu.get("menu_detail", ""), af_case_items):
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "The AF Case My Menu test must list all three approved shortcuts in order."))
    if af_case_menu and "complete Case 1–4 / Case A selector" not in af_case_menu.get("menu_detail", ""):
        issues.append(error("spreadsheet_specs", paths.verification_tracker_source_file, "The AF Case test must confirm that Servo AF opens the complete Case selector."))
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


def _contains_in_order(text, phrases):
    position = -1
    for phrase in phrases:
        position = text.find(phrase, position + 1)
        if position < 0:
            return False
    return True
