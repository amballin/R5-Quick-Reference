#!/usr/bin/env python3
import argparse
from pathlib import Path
import shutil
import sys
import time
import traceback

BUILD_DIR = Path(__file__).resolve().parent / "80 Build"
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from asset_manager import ProjectPaths
from appendix_renderer import render_appendices
from baseline import merge
from build_validator import discover_profiles, profile_name_from_path, validate_project
from generated_output import clean_generated_tree, mirror_tree, numbered_duplicates, remove_numbered_duplicates
from html_renderer import render_card, write_html_card
from icon_manager import IconManager
from ios_wrapper import build_xcode_project, prepare_website_output, update_ios_resources, validate_ios_wrapper
from offline_index import render_offline_index
from output_renderer import render_png_pdf
from profile_loader import canonical_profile_name, load_baseline, load_profile, write_merged_profile
from pwa import generate_pwa, validate_merged_build_pwa


PAGES_IGNORE = shutil.ignore_patterns(".DS_Store", "__pycache__")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?")
    parser.add_argument("target", nargs="?")
    parser.add_argument("profile", nargs="?")
    parser.add_argument("--root", default=".")
    parser.add_argument("--pdf", action="store_true", help="Also generate card and appendix PDFs. Off by default.")
    return parser.parse_args()


def build_profile(profile_name, root=".", include_pdf=False):
    profile_name = canonical_profile_name(profile_name)
    paths = ProjectPaths(root)
    baseline = load_baseline(paths)
    profile = load_profile(paths, profile_name)
    merged = merge(baseline["defaults"], profile.get("overrides", {}))
    write_merged_profile(paths, profile_name, merged)
    template = paths.card_template.read_text()
    icon_manager = IconManager(paths)
    html = render_card(template, profile_name, profile, merged, icon_manager, baseline, paths)
    write_html_card(paths, profile_name, html)
    render_png_pdf(paths, profile_name, profile, merged, icon_manager, baseline, include_pdf=include_pdf)
    return {
        "profile": profile_name,
        "html": paths.html_output_file(profile_name),
        "png": paths.png_output_file(profile_name),
        "pdf": paths.pdf_output_file(profile_name) if include_pdf else None,
    }


def profile_names_to_build(paths, requested_profile):
    if requested_profile:
        return [canonical_profile_name(requested_profile)]
    return [profile_name_from_path(path) for path in discover_profiles(paths)]


def build_profiles(paths, profile_names, include_pdf=False):
    successes = []
    failures = []
    generated = {"HTML": 0, "PNG": 0, "PDF": 0}
    for profile_name in profile_names:
        try:
            result = build_profile(profile_name, paths.root, include_pdf=include_pdf)
            successes.append(result)
            for key in ["HTML", "PNG"]:
                if result[key.lower()].exists():
                    generated[key] += 1
            if include_pdf and result["pdf"] and result["pdf"].exists():
                generated["PDF"] += 1
        except Exception as exc:
            failures.append(
                {
                    "profile": profile_name,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )
    return successes, failures, generated


def write_report(paths, profile_names, validation_results, successes, failures, generated, elapsed):
    lines = [
        "# Build Report",
        "",
        "## Files Modified",
        "",
        "- `build.py`",
        "- `80 Build/asset_manager.py`",
        "- `80 Build/generated_output.py`",
        "- `80 Build/html_renderer.py`",
        "- `80 Build/icon_manager.py`",
        "- `80 Build/ios_wrapper.py`",
        "- `80 Build/offline_index.py`",
        "- `80 Build/pwa.py`",
        "- `80 Build/render_card_outputs.js`",
        "",
        "## Files Created",
        "",
        "- `80 Build/build_validator.py`",
        "- `80 Build/offline_index.py`",
        "- `80 Build/output_renderer.py`",
        "- `80 Build/pwa.py`",
        "- `80 Build/render_card_outputs.js`",
        "- `output/cards/merged/`",
        "- `output/cards/html/`",
        "- `output/cards/png/`",
        "- `output/cards/phone-png/`",
        "- `output/field-guide/html/`",
        "- `output/field-guide/search_index.json`",
        "- `output/merged-build/`",
        "- `docs/`",
        "- `output/reports/BUILD_REPORT.md`",
        "",
        "## Profiles Built",
        "",
    ]
    if profile_names:
        lines.extend(f"- `{name}`" for name in profile_names)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Outputs Generated",
            "",
            *[f"- {key}: {value}" for key, value in generated.items()],
            "",
            "## Validation Results",
            "",
        ]
    )
    if validation_results:
        for level, code, detail in validation_results:
            lines.append(f"- {level.upper()} `{code}`: {detail}")
    else:
        lines.append("- No validation issues found.")

    lines.extend(["", "## Failures", ""])
    if failures:
        for failure in failures:
            lines.append(f"- `{failure['profile']}`: {failure['error']}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Profiles discovered: {len(profile_names)}",
            f"- Successful: {len(successes)}",
            f"- Failed: {len(failures)}",
            f"- Total build time: {elapsed:.2f} seconds",
            "",
            "## Rendering Fixes",
            "",
            "- PNG text rendering wraps long setting values and list items so notes and other long text do not run off the card edge.",
            "- PDF generation is opt-in with `--pdf`; default builds skip card and appendix PDFs.",
            "",
            "## Future Enhancement",
            "",
            "- Incremental rebuild skipping is not implemented yet. The build currently regenerates requested outputs to keep behavior straightforward and reliable.",
            "- Consider adding a small icon on each side of the dynamic island in a future header pass.",
        ]
    )
    paths.reports_output_dir.mkdir(parents=True, exist_ok=True)
    (paths.reports_output_dir / "BUILD_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(profile_count, successes, failures, generated, elapsed):
    print(f"Profiles discovered: {profile_count}")
    print()
    print("Successful:")
    print(f"    {len(successes)}")
    print()
    print("Failed:")
    print(f"    {len(failures)}")
    print()
    print("Generated:")
    print()
    for key in generated:
        print(f"{key}:")
        print(f"    {generated[key]}")
        print()
    print("Total build time:")
    print(f"    {elapsed:.2f} seconds")


def main():
    start = time.perf_counter()
    args = parse_args()
    paths = ProjectPaths(args.root)
    if args.command == "build" and args.target in {"website", "pages", "ios"}:
        status = build_site(
            paths,
            requested_profile=args.profile,
            include_pdf=args.pdf,
            keep_website=args.target in {"website", "ios"},
        )
        if status != 0:
            return status
        if args.target == "website":
            prepare_website_output(paths)
            print(f"Website generated: {paths.website_output_dir}")
            return 0
        if args.target == "pages":
            sync_pages_output(paths)
            print(f"GitHub Pages docs generated: {paths.pages_output_dir}")
            return 0
        prepare_website_output(paths)
        update_ios_resources(paths)
        checks = validate_ios_wrapper(paths)
        failed_checks = [check for check in checks if not check["ok"]]
        if failed_checks:
            print("iOS wrapper validation failed.")
            for check in failed_checks:
                print(f"- {check['name']}: {check['detail']}")
            return 1
        build_result = build_xcode_project(paths)
        if not build_result["ok"]:
            print("Xcode build failed.")
            print(build_result["detail"])
            return 1
        print("iOS wrapper built successfully.")
        return 0
    if args.command == "build":
        print("Unknown build target. Use: python build.py build website, python build.py build pages, or python build.py build ios")
        return 2
    requested_profile = args.command or args.profile
    status = build_site(paths, requested_profile=requested_profile, start=start, include_pdf=args.pdf)
    if status == 0 and requested_profile is None:
        sync_pages_output(paths)
        clean_generated_leftovers(paths, include_pdf=args.pdf, keep_website=False)
        print(f"GitHub Pages docs generated: {paths.pages_output_dir}")
    return status


def build_site(paths, requested_profile=None, start=None, include_pdf=False, keep_website=False):
    start = start or time.perf_counter()
    validation_results = validate_project(paths)
    validation_errors = [result for result in validation_results if result[0] == "error"]
    if validation_errors:
        elapsed = time.perf_counter() - start
        write_report(paths, [], validation_results, [], [], {"HTML": 0, "PNG": 0, "PDF": 0}, elapsed)
        print("Build stopped because validation failed.")
        print()
        for _, code, detail in validation_errors:
            print(f"{code}: {detail}")
        return 1
    clean_generated_leftovers(paths, include_pdf=include_pdf, keep_website=keep_website, full_build=requested_profile is None)
    profile_names = profile_names_to_build(paths, requested_profile)
    appendix_generated = render_appendices(paths, include_pdf=include_pdf)
    successes, failures, generated = build_profiles(paths, profile_names, include_pdf=include_pdf)
    generated.update(appendix_generated)
    generated.update(render_offline_index(paths))
    generated.update(generate_pwa(paths))
    settle_clean_generated_roots(paths.root / "output", paths.merged_build_output_dir)
    pwa_validation_results = validate_merged_build_pwa(paths)
    validation_results.extend(pwa_validation_results)
    pwa_validation_errors = [result for result in pwa_validation_results if result[0] == "error"]
    elapsed = time.perf_counter() - start
    write_report(paths, profile_names, validation_results, successes, failures, generated, elapsed)
    if pwa_validation_errors:
        print("Build stopped because merged-build PWA validation failed.")
        print()
        for _, code, detail in pwa_validation_errors:
            print(f"{code}: {detail}")
        return 1
    print_summary(len(profile_names), successes, failures, generated, elapsed)
    return 1 if failures else 0


def sync_pages_output(paths):
    """Mirror output/merged-build into docs/ for branch-based GitHub Pages."""
    source = paths.merged_build_output_dir
    target = paths.pages_output_dir
    if not source.exists():
        raise FileNotFoundError(f"Generated merged-build output is missing: {source}")
    remove_numbered_duplicates(source, require_original=False)
    mirror_tree(source, target, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
    settle_clean_pages_mirror(source, target)
    mirror_issues = mirror_differences(source, target)
    if mirror_issues:
        sample = ", ".join(mirror_issues[:10])
        raise RuntimeError(f"docs is not an exact mirror of output/merged-build: {sample}")
    duplicates = numbered_duplicates(target, require_original=False)
    if duplicates:
        sample = ", ".join(str(path.relative_to(target)) for path in duplicates[:10])
        raise RuntimeError(f"Numbered duplicate generated files remain in docs: {sample}")
    source_duplicates = numbered_duplicates(source, require_original=False)
    if source_duplicates:
        sample = ", ".join(str(path.relative_to(source)) for path in source_duplicates[:10])
        raise RuntimeError(f"Numbered duplicate generated files remain in output/merged-build: {sample}")


def settle_clean_pages_mirror(source, target):
    for attempt in range(20):
        clean_generated_tree(source)
        clean_generated_tree(target)
        if attempt < 19:
            time.sleep(0.5)


def settle_clean_generated_roots(*roots):
    for attempt in range(20):
        for root in roots:
            clean_generated_tree(root)
        if attempt < 19:
            time.sleep(0.5)


def mirror_differences(source, target):
    source_paths = _mirror_paths(source)
    target_paths = _mirror_paths(target)
    differences = [f"missing in docs: {path}" for path in sorted(source_paths - target_paths)]
    differences.extend(f"extra in docs: {path}" for path in sorted(target_paths - source_paths))
    for relative in sorted(source_paths & target_paths):
        source_path = source / relative
        target_path = target / relative
        if source_path.is_file() and target_path.is_file() and source_path.read_bytes() != target_path.read_bytes():
            differences.append(f"content differs: {relative}")
    return differences


def _mirror_paths(root):
    if not root.exists():
        return set()
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.name != ".DS_Store"
    }


def clean_generated_leftovers(paths, include_pdf=False, keep_website=False, full_build=False):
    obsolete_generated_roots = [
        paths.root / "Website",
        paths.root / "30 Cards" / "HTML",
        paths.root / "30 Cards" / "Merged",
        paths.root / "30 Cards" / "PNG",
        paths.root / "30 Cards" / "Phone PNG",
        paths.root / "30 Cards" / "iPhone",
        paths.root / "50 Field Guide" / "HTML",
        paths.root / "output" / "Website",
        paths.root / "assets",
    ]
    if not keep_website:
        obsolete_generated_roots.append(paths.root / "output" / "Website")
    if full_build:
        obsolete_generated_roots.extend(
            [
                paths.merged_build_output_dir.parent / f".{paths.merged_build_output_dir.name}.staging",
                paths.field_guide_html_output_dir.parent / f".{paths.field_guide_html_output_dir.name}.staging",
            ]
        )
    for root in obsolete_generated_roots:
        if root.exists():
            shutil.rmtree(root)

    obsolete_generated_files = [
        paths.root / ".DS_Store",
        paths.root / "50 Field Guide" / "search_index.json",
        paths.root / "manifest.webmanifest",
        paths.root / "offline.html",
        paths.root / "service-worker.js",
        paths.root / "60 Assets" / ".DS_Store",
        paths.root / "ios" / ".DS_Store",
        paths.root / "output" / ".DS_Store",
        paths.root / "output" / "canon_r5_icon_reference.html",
    ]
    for path in obsolete_generated_files:
        if path.exists():
            path.unlink()

    obsolete_icons = paths.root / "icons"
    if obsolete_icons.exists():
        shutil.rmtree(obsolete_icons)

    generated_roots = [
        paths.root / "output",
        paths.merged_build_output_dir,
        paths.website_output_dir,
        paths.pages_output_dir,
    ]
    for root in generated_roots:
        clean_generated_tree(root)

    if include_pdf:
        return

    for pdf_dir in [paths.pdf_output_dir, paths.field_guide_pdf_output_dir, paths.root / "30 Cards" / "PDF", paths.root / "50 Field Guide" / "PDF"]:
        if pdf_dir.exists():
            shutil.rmtree(pdf_dir)


if __name__ == "__main__":
    raise SystemExit(main())
