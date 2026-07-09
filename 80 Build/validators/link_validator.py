from urllib.parse import urlparse

from .common import error, load_yaml_checked


def validate(root):
    issues = []
    guide_dir = root / "70 Canon Guides"
    if guide_dir.exists():
        issues.extend(_validate_canon_guide_links(root, guide_dir))
    return issues


def _validate_canon_guide_links(root, guide_dir):
    issues = []
    index_path = guide_dir / "index.yaml"
    if index_path.exists():
        try:
            index = load_yaml_checked(index_path) or {}
            guides = index.get("guides", {}) or {}
            for name, entry in guides.items():
                if "file" in entry and not (guide_dir / entry["file"]).exists():
                    issues.append(error("links", index_path, f"Guide {name} references missing file: {entry['file']}"))
                if "url" in entry and not _valid_url(entry["url"]):
                    issues.append(error("links", index_path, f"Guide {name} has malformed URL: {entry['url']}"))
        except Exception as exc:
            issues.append(error("links", index_path, f"Could not validate guide links: {exc}"))

    for shortcut in sorted(guide_dir.glob("*.url")):
        text = shortcut.read_text(encoding="utf-8", errors="replace")
        urls = [line.split("=", 1)[1].strip() for line in text.splitlines() if line.startswith("URL=")]
        if not urls:
            issues.append(error("links", shortcut, "Internet shortcut has no URL entry."))
        elif not _valid_url(urls[0]):
            issues.append(error("links", shortcut, f"Internet shortcut has malformed URL: {urls[0]}"))
    return issues


def _valid_url(value):
    parsed = urlparse(str(value))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

