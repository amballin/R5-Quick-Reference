import os
from pathlib import Path

from profile_pack import resolve_profile_pack


def application_local_workspace(root):
    """Return machine-local application state without applying pack namespacing."""
    root = Path(root).resolve()
    override = os.environ.get("PRS_LOCAL_WORKSPACE")
    if override:
        return Path(override).expanduser().resolve()
    return root.parent / f"{root.name} Local"


class ProjectPaths:
    """Resolve source, publishing, and machine-local workspace paths."""

    def __init__(self, root, profile_pack_root=None, profile_pack_context=None):
        self.root = Path(root).resolve()
        if profile_pack_root is not None and profile_pack_context is not None:
            raise ValueError("Choose profile_pack_root or profile_pack_context, not both.")
        if (
            profile_pack_context is not None
            and profile_pack_context.application_root != self.root
        ):
            raise ValueError("Profile-pack context belongs to a different application root.")
        self.profile_pack = profile_pack_context or resolve_profile_pack(
            self.root,
            explicit_root=profile_pack_root,
        )

    @property
    def application_root(self):
        return self.root

    @property
    def profile_pack_root(self):
        return self.profile_pack.root

    def profile_pack_source(self, key):
        return self.profile_pack.source(key)

    def profile_pack_relative_source(self, key):
        return self.profile_pack_source(key).relative_to(self.profile_pack_root).as_posix()

    def mutable_source_path(self, relative):
        """Resolve an editor write target without crossing the selected pack boundary."""
        relative = Path(relative)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Mutable source path must be pack-relative: {relative}")
        root = self.profile_pack_root.resolve()
        target = (root / relative).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"Mutable source escapes the selected profile pack: {relative}")
        if self.profile_pack.mode == "embedded":
            return target
        exact = {
            source.resolve()
            for key, source in self.profile_pack.sources.items()
            if key != "profiles"
        }
        profiles = self.profiles_dir.resolve()
        if target in exact or (
            target.parent == profiles
            and target.suffix == ".yaml"
        ):
            return target
        raise ValueError(f"External editor target is not owned by the selected profile pack: {relative}")

    @property
    def local_workspace_dir(self):
        base = application_local_workspace(self.root)
        if self.profile_pack.mode == "external":
            return base / "Profile Packs" / self.profile_pack.pack_id
        return base

    @property
    def output_dir(self):
        return self.local_workspace_dir / "Build Output"

    @property
    def backups_dir(self):
        return self.local_workspace_dir / "Backups"

    @property
    def deleted_cards_dir(self):
        return self.local_workspace_dir / "Deleted Cards"

    @property
    def baseline_file(self):
        return self.profile_pack_source("baseline")

    @property
    def card_layout_file(self):
        return self.root / "00 Master" / "card_layout.yaml"

    @property
    def setting_access_file(self):
        return self.root / "00 Master" / "setting_access.yaml"

    @property
    def my_menu_colors_file(self):
        return self.profile_pack_source("my_menu_colors")

    @property
    def my_menu_file(self):
        return self.profile_pack_source("my_menu")

    @property
    def profile_lens_guidance_file(self):
        return self.profile_pack_source("profile_lens_guidance")

    @property
    def owned_equipment_file(self):
        return self.profile_pack_source("owned_equipment")

    @property
    def controls_file(self):
        return self.profile_pack_source("controls")

    @property
    def registration_targets_file(self):
        return self.profile_pack_source("registration_targets")

    @property
    def spreadsheet_layouts_file(self):
        return self.root / "00 Master" / "spreadsheet_layouts.yaml"

    @property
    def verification_tracker_source_file(self):
        if self.profile_pack.mode == "external":
            return self.registration_targets_file
        return self.root / "90 Testing" / "eos_r5_verification_tracker.yaml"

    @property
    def verification_status_file(self):
        return self.profile_pack_source("verification_status")

    def profile_file(self, profile_name):
        return self.profiles_dir / f"{profile_name}.yaml"

    @property
    def card_template(self):
        return self.root / "20 Templates" / "card.html"

    @property
    def profiles_dir(self):
        return self.profile_pack_source("profiles")

    @property
    def merged_output_dir(self):
        return self.output_dir / "cards" / "merged"

    @property
    def html_output_dir(self):
        return self.output_dir / "cards" / "html"

    @property
    def pdf_output_dir(self):
        return self.output_dir / "cards" / "pdf"

    @property
    def merged_build_output_dir(self):
        return self.output_dir / "merged-build"

    @property
    def card_candidates_output_dir(self):
        return self.output_dir / "Card Candidates"

    @property
    def website_output_dir(self):
        return self.output_dir / "website"

    @property
    def pages_output_dir(self):
        if self.profile_pack.mode == "external":
            return self.output_dir / "pages"
        return self.root / "docs"

    @property
    def reports_output_dir(self):
        return self.output_dir / "reports"

    @property
    def subject_settings_summary_file(self):
        return self.reports_output_dir / "Subject Settings Matrix.xlsx"

    @property
    def subject_settings_numbers_file(self):
        return self.reports_output_dir / "Subject Settings Matrix.numbers"

    @property
    def subject_settings_download_manifest_file(self):
        return self.reports_output_dir / "subject-settings-matrix-downloads.json"

    @property
    def setup_tracker_file(self):
        return self.reports_output_dir / "EOS R5 Setup & Verification Tracker.xlsx"

    @property
    def setup_tracker_numbers_file(self):
        return self.reports_output_dir / "EOS R5 Setup & Verification Tracker.numbers"

    @property
    def setup_tracker_download_manifest_file(self):
        return self.reports_output_dir / "eos-r5-setup-verification-downloads.json"

    @property
    def published_spreadsheet_manifest_file(self):
        return self.pages_output_dir / "downloads" / "spreadsheet-releases.json"

    @property
    def verification_working_dir(self):
        return self.local_workspace_dir / "Verification"

    @property
    def setup_tracker_working_file(self):
        return self.verification_working_dir / "EOS R5 On-Camera Verification Tracker.xlsx"

    @property
    def setup_tracker_working_numbers_file(self):
        return self.verification_working_dir / "EOS R5 On-Camera Verification Tracker.numbers"

    @property
    def verification_import_marker_file(self):
        return self.verification_working_dir / ".verification-status-import.json"

    @property
    def field_guide_pdf_output_dir(self):
        return self.output_dir / "field-guide" / "pdf"

    @property
    def field_guide_html_output_dir(self):
        return self.output_dir / "field-guide" / "html"

    @property
    def field_guide_search_index_file(self):
        return self.output_dir / "field-guide" / "search_index.json"

    @property
    def icon_map_file(self):
        return self.root / "60 Assets" / "icon-map.yaml"

    @property
    def icon_asset_dir(self):
        return self.root / "60 Assets"

    def merged_output_file(self, profile_name):
        return self.merged_output_dir / f"{profile_name}.yaml"

    def html_output_file(self, profile_name):
        return self.html_output_dir / f"{profile_name}.html"

    def pdf_output_file(self, profile_name):
        return self.pdf_output_dir / f"{profile_name}.pdf"
