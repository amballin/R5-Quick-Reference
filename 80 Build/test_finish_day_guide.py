#!/usr/bin/env python3
"""Tests for the small local workflow-guide Markdown renderer."""

from pathlib import Path
import sys
import unittest


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from finish_day_guide import render_guide_html


class WorkflowGuideMarkdownTests(unittest.TestCase):
    def test_third_level_heading_renders_as_h3(self):
        rendered = render_guide_html(
            "# Guide\n\n## Section\n\n### Subsection\n\nBody.\n",
            "Guide",
            "Local guide",
        )
        self.assertIn("<h3>Subsection</h3>", rendered)
        self.assertNotIn("### Subsection", rendered)


if __name__ == "__main__":
    unittest.main()
