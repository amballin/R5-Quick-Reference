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
    def native_wrapper_output_dir(self):
        return self.local_workspace_dir / "Native Wrapper" / "Website"

    @property
    def baseline_file(self):
        return self.root / "00 Master" / "baseline.yaml"

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
    def png_output_dir(self):
        return self.output_dir / "cards" / "png"

    @property
    def phone_png_output_dir(self):
        return self.output_dir / "cards" / "phone-png"

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

    def png_output_file(self, profile_name):
        return self.png_output_dir / f"{profile_name}.png"

    def phone_png_output_file(self, profile_name):
        return self.phone_png_output_dir / f"{profile_name}.png"

    def pdf_output_file(self, profile_name):
        return self.pdf_output_dir / f"{profile_name}.pdf"
