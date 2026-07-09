#!/usr/bin/env python3
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent / "80 Build"
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

import build
from asset_manager import ProjectPaths
from ios_wrapper import (
    build_xcode_project,
    prepare_website_output,
    run_xcode_tests,
    update_ios_resources,
    validate_ios_wrapper,
    write_regression_report,
)


def main():
    paths = ProjectPaths(".")
    steps = []

    site_status = build.build_site(paths)
    steps.append({"name": "Build Website", "ok": site_status == 0, "detail": f"exit {site_status}"})
    if site_status != 0:
        write_regression_report(paths, steps)
        return 1

    try:
        prepare_website_output(paths)
        update_ios_resources(paths)
        steps.append({"name": "Update iOS resources", "ok": True, "detail": str(paths.root / "ios" / "Resources" / "Website")})
    except Exception as exc:
        steps.append({"name": "Update iOS resources", "ok": False, "detail": str(exc)})
        write_regression_report(paths, steps)
        return 1

    checks = validate_ios_wrapper(paths)
    failed_checks = [check for check in checks if not check["ok"]]
    steps.append({"name": "Run validator", "ok": not failed_checks, "detail": f"{len(checks) - len(failed_checks)}/{len(checks)} checks passed"})
    if failed_checks:
        write_regression_report(paths, steps)
        return 1

    build_result = build_xcode_project(paths)
    steps.append({"name": "Build Xcode project", "ok": build_result["ok"], "detail": build_result["detail"]})
    if not build_result["ok"]:
        write_regression_report(paths, steps)
        return 1

    test_result = run_xcode_tests(paths)
    steps.append({"name": "Run XCTest suite", "ok": test_result["ok"], "detail": test_result["detail"]})
    write_regression_report(paths, steps)
    return 0 if test_result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
