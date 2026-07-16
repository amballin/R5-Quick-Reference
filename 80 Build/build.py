#!/usr/bin/env python3
"""Compatibility entry point for the established build implementation at the repository root."""
from pathlib import Path
import runpy


if __name__ == "__main__":
    root_build = Path(__file__).resolve().parents[1] / "build.py"
    runpy.run_path(str(root_build), run_name="__main__")
