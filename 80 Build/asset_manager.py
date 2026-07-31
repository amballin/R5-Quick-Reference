import os
from pathlib import Path


class ProjectPaths:
    """Resolve source, publishing, and machine-local workspace paths."""

    def __init__(self, root):
        self.root = Path(root).resolve()

    @property
    def local_workspace_dir(self):
        override = os.environ.get("PRS_LOCAL_WORKSPACE")
        if override:
            return Path(override).expanduser().resolve()
        return self.root.parent / f"{self.root.name} Local"

    @property
    def output_dir(self):
        return self.local_workspace_dir / "Build Output"

    @property
    def backups_dir(self):
        return self.local_workspace_dir / "Backups"

    @property
    def baseline_file(self):
        return self.root / "00 Master" / "baseline.yaml"

    @property
    def card_layout_file(self):
        return self.root / "00 Master" / "card_layout.yaml"

    @property
    def setting_access_file(self):
        return self.root / "00 Master" / "setting_access.yaml"

    @property
    def spreadsheet_layouts_file(self):
        return self.root / "00 Master" / "spreadsheet_layouts.yaml"

    @property
    def verification_tracker_source_file(self):
        return self.root / "90 Testing" / "eos_r5_verification_tracker.yaml"

    @property
    def verification_status_file(self):
        return self.root / "90 Testing" / "eos_r5_verification_status.yaml"

    def profile_file(self, profile_name):
        return self.root / "10 Profiles" / f"{profile_name}.yaml"

    @property
    def card_template(self):
        return self.root / "20 Templates" / "card.html"

    @property
    def profiles_dir(self):
        return self.root / "10 Profiles"

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
    def website_output_dir(self):
        return self.output_dir / "website"

    @property
    def pages_output_dir(self):
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
