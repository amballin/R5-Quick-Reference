#!/usr/bin/env python3
"""Migrate legacy title-based card references to immutable UUIDs."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from uuid import NAMESPACE_URL, uuid5

import yaml


PROJECT_NAMESPACE = uuid5(NAMESPACE_URL, "https://amballin.github.io/R5-Quick-Reference/card-identity")


def assigned_id(name):
    return str(uuid5(PROJECT_NAMESPACE, name))


def migrate(root, apply=False):
    root = Path(root).resolve()
    profile_dir = root / "10 Profiles"
    paths = sorted(profile_dir.glob("*.yaml"))
    titles = {}
    ids = {}
    loaded = {}
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        title = data.get("title")
        if not isinstance(title, str) or not title:
            raise ValueError(f"Profile title is missing: {path}")
        card_id = data.get("card_id") or assigned_id(path.stem)
        titles[title] = card_id
        ids[path] = card_id
        loaded[path] = data

    changed = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        card_id = ids[path]
        if not re.search(r"^card_id:", text, flags=re.MULTILINE):
            text = f"card_id: {card_id}\n" + text
        data = loaded[path]
        setup = ((data.get("card") or {}).get("field_setup") or {})
        legacy = setup.get("source_profile") if isinstance(setup, dict) else None
        if legacy:
            if legacy not in titles:
                raise ValueError(f"Unknown source_profile {legacy!r}: {path}")
            text = re.sub(
                r"^(\s*)source_profile:\s*.*$",
                rf"\g<1>source_card_id: {titles[legacy]}",
                text,
                count=1,
                flags=re.MULTILINE,
            )
        if text != path.read_text(encoding="utf-8"):
            changed.append(path)
            if apply:
                path.write_text(text, encoding="utf-8")

    for relative in ("controls.yaml", "data/canon_r5_custom_controls_current.yaml"):
        path = root / relative
        text = path.read_text(encoding="utf-8")
        original = text
        for title, card_id in titles.items():
            text = re.sub(
                rf"^(\s*)profile_title:\s*{re.escape(title)}\s*$",
                rf"\g<1>profile_id: {card_id}",
                text,
                flags=re.MULTILINE,
            )
        if text != original:
            changed.append(path)
            if apply:
                path.write_text(text, encoding="utf-8")

    manifest_path = root / "50 Field Guide" / "required_appendices.yaml"
    text = manifest_path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r"^(\s*)profiles:\s*\[\]\s*$", r"\1profile_ids: []", text, flags=re.MULTILINE)
    lines = text.splitlines(keepends=True)
    output = []
    in_profiles = False
    profiles_indent = 0
    for line in lines:
        match = re.match(r"^(\s*)profiles:\s*$", line.rstrip("\n"))
        if match:
            profiles_indent = len(match.group(1))
            output.append(f"{match.group(1)}profile_ids:\n")
            in_profiles = True
            continue
        if in_profiles:
            item = re.match(r"^(\s*)-\s+(.+?)\s*$", line.rstrip("\n"))
            if item and len(item.group(1)) > profiles_indent:
                title = item.group(2).strip("'\"")
                if title not in titles:
                    raise ValueError(f"Unknown appendix profile reference: {title}")
                output.append(f"{item.group(1)}- {titles[title]}\n")
                continue
            if line.strip() and len(line) - len(line.lstrip()) <= profiles_indent:
                in_profiles = False
        output.append(line)
    text = "".join(output)
    if text != original:
        changed.append(manifest_path)
        if apply:
            manifest_path.write_text(text, encoding="utf-8")
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    changed = migrate(args.root, apply=args.apply)
    for path in changed:
        print(path)
    print(f"{'Migrated' if args.apply else 'Would migrate'}: {len(changed)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
