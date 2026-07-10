import shutil
import base64
import mimetypes
import os
import re
import time
from html import escape
from pathlib import Path
from urllib.parse import unquote

import yaml


GUIDE_DISPLAY_ORDER = {
    "R5 Quick Reference": 10,
    "Canon EOS R5 Official Icon Reference": 20,
}
APP_TITLE = "R5 Settings"


def render_offline_index(paths):
    """Build the merged offline web bundle with cards and guide pages embedded in the index."""
    output_dir = _staging_output_dir(paths)
    final_dir = paths.merged_build_output_dir
    if output_dir.exists():
        _remove_tree(output_dir)
    cards_dir = output_dir / "Cards"
    cards_dir.mkdir(parents=True, exist_ok=True)

    card_files = _copy_release_cards(paths, cards_dir)
    guides = _release_guides(paths)
    _write_appendices(output_dir / "appendices", guides)
    _write_index(output_dir / "index.html", card_files, guides)
    _write_readme(output_dir / "README.txt")
    (output_dir / ".nojekyll").touch()
    _publish_staging_dir(output_dir, final_dir)
    return {"Merged Build": 1 if (final_dir / "index.html").exists() else 0}


def _copy_files(source_dir, target_dir, pattern):
    if not source_dir.exists():
        return []
    copied = []
    for source in sorted(source_dir.glob(pattern), key=lambda path: path.stem.lower()):
        target = target_dir / source.name
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def _copy_release_cards(paths, target_dir):
    copied = []
    for profile_path in sorted(paths.profiles_dir.glob("*.yaml"), key=lambda path: path.stem.lower()):
        profile = _load_yaml(profile_path)
        if not ((profile.get("metadata") or {}).get("release") is True):
            continue
        profile_name = profile.get("title") or profile_path.stem
        source = paths.phone_png_output_file(profile_name)
        if not source.exists():
            source = paths.png_output_file(profile_name)
        if not source.exists():
            continue
        target = target_dir / source.name
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def _release_guides(paths):
    manifest = _load_yaml(paths.root / "50 Field Guide" / "required_appendices.yaml")
    html_dir = paths.field_guide_html_output_dir
    guides = []
    for entry in manifest.get("appendices", []) or []:
        if entry.get("release") is not True:
            continue
        title = entry.get("title") or Path(entry.get("file", "")).stem
        source = html_dir / f"{Path(entry.get('file', '')).stem}.html"
        if not source.exists():
            continue
        html = _inline_local_images(source, source.read_text(encoding="utf-8", errors="replace"))
        guides.append({"title": title, "filename": source.name, "html": html})
    return sorted(guides, key=lambda guide: (GUIDE_DISPLAY_ORDER.get(guide["title"], 100), guide["title"].lower()))


def _copy_named_files(source_dir, target_dir, filenames, inline_html_assets=False):
    copied = []
    for filename in filenames:
        source = source_dir / filename
        if not source.exists():
            continue
        target = target_dir / source.name
        if inline_html_assets and source.suffix.lower() == ".html":
            html = _inline_local_images(source, source.read_text(encoding="utf-8", errors="replace"))
            target.write_text(html, encoding="utf-8")
        else:
            shutil.copy2(source, target)
        copied.append(target)
    return copied


def _load_yaml(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _write_index(path, card_files, guides):
    cards = "\n".join(_card_details(card) for card in card_files)
    guide_markup = "\n".join(_guide_details(guide) for guide in guides)
    path.write_text(
        f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{APP_TITLE}</title>
<style>
:root{{color-scheme:dark;--bg:#132742;--panel:#1d395b;--text:#f7fbff;--muted:#b9d5ec;--rule:#5b7893;--accent:#9bd2ff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.35}}
#top{{position:sticky;top:0;background:rgba(19,39,66,.96);backdrop-filter:blur(16px);padding:18px 18px 12px;border-bottom:1px solid rgba(155,210,255,.22);z-index:1}}
h1{{font-size:24px;margin:0}}
.sub{{color:var(--muted);font-size:14px;margin-top:4px}}
main{{padding:16px 14px 32px}}
h2{{font-size:18px;color:var(--accent);margin:18px 4px 10px}}
.cards{{display:grid;gap:9px}}
.card{{display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--text);background:var(--panel);border:1px solid rgba(155,210,255,.18);border-radius:10px;padding:13px 14px;min-height:48px;font-weight:700;list-style:none}}
.card::-webkit-details-marker{{display:none}}
.card span{{color:var(--muted);font-weight:400}}
.guides{{display:grid;gap:9px}}
.guide{{display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--text);background:var(--panel);border:1px solid rgba(155,210,255,.18);border-radius:10px;padding:13px 14px;min-height:48px;list-style:none}}
.guide::-webkit-details-marker{{display:none}}
.guide span{{color:var(--muted)}}
.hint{{color:var(--muted);font-size:13px;margin:8px 4px 0}}
details{{display:block}}
details[open]{{padding-bottom:14px;border-bottom:1px solid rgba(155,210,255,.18)}}
.card-image{{display:block;width:100%;max-width:393px;height:auto;margin:12px auto 0;background:#1e3553}}
.guide-panel{{background:#f8fafc;color:#172033;border-radius:10px;padding:16px;overflow:auto}}
.guide-panel h1{{font-size:26px;color:#172033}}
.guide-panel h2{{color:#172033;border-bottom:1px solid #d7dee8}}
.guide-panel h3{{color:#172033}}
.guide-panel table{{border-collapse:collapse;width:100%;font-size:13px}}
.guide-panel th,.guide-panel td{{border:1px solid #d7dee8;padding:6px;text-align:left;vertical-align:top}}
.guide-panel .subtitle{{color:#5c6670;font-size:14px}}
.guide-panel main{{padding:0}}
.guide-panel .category{{margin:0 0 20px}}
.guide-panel .grid{{display:grid;grid-template-columns:1fr;gap:9px}}
.guide-panel .icon-card{{display:grid;grid-template-columns:48px 1fr;gap:10px;align-items:center;min-height:76px;padding:10px;border:1px solid #d7dee8;border-radius:8px;background:#fff}}
.guide-panel .icon-frame{{width:48px;height:48px;display:grid;place-items:center;background:#f2f5f8;border:1px solid #d7dee8;border-radius:6px;overflow:hidden}}
.guide-panel .icon-frame img{{max-width:36px;max-height:36px;display:block}}
.guide-panel .name{{font-weight:700;font-size:14px;line-height:1.2;overflow-wrap:anywhere}}
.guide-panel .label{{color:#9a1025;font-size:12px;font-weight:700;margin-top:3px}}
.guide-panel .meta{{color:#5c6670;font-size:11px;line-height:1.25;margin-top:6px}}
.guide-panel .no-asset{{font-size:11px;color:#5c6670;text-align:center;line-height:1.15;padding:4px}}
</style>
</head>
<body>
<header id="top">
<h1>{APP_TITLE}</h1>
</header>
<main>
<h2>Subject Cards</h2>
<div class="cards">
{cards}
</div>
<div class="hint">Tip: tap a card name to show it inline. No internet is needed.</div>
<h2>Field Guide</h2>
<div class="guides">
{guide_markup}
</div>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _card_details(card):
    label = escape(card.stem)
    image_data = base64.b64encode(card.read_bytes()).decode("ascii")
    return f"""<details>
<summary class="card">{label}<span>Show</span></summary>
<img class="card-image" src="data:image/png;base64,{image_data}" alt="{label} card">
</details>"""


def _guide_details(guide):
    label = escape(guide["title"])
    body = _html_body(guide["html"])
    return f"""<details>
<summary class="guide">{label}<span>Show</span></summary>
<div class="guide-panel">
{body}
</div>
</details>"""


def _write_appendices(target_dir, guides):
    target_dir.mkdir(parents=True, exist_ok=True)
    for guide in guides:
        html = re.sub(r"<a\b([^>]*)>(.*?)</a>", _offline_link, guide["html"], flags=re.IGNORECASE | re.DOTALL)
        (target_dir / guide["filename"]).write_text(html, encoding="utf-8")


def _html_body(html):
    match = re.search(r"<body[^>]*>(.*)</body>", html, flags=re.IGNORECASE | re.DOTALL)
    body = match.group(1) if match else html
    return re.sub(r"<a\b([^>]*)>(.*?)</a>", _offline_link, body, flags=re.IGNORECASE | re.DOTALL)


def _offline_link(match):
    attrs = match.group(1)
    label = match.group(2)
    href = re.search(r'href="([^"]+)"', attrs, flags=re.IGNORECASE)
    if href and href.group(1).startswith("#"):
        return f'<a href="{href.group(1)}">{label}</a>'
    return label


def _inline_local_images(source_html, html):
    def replace(match):
        before = match.group(1)
        src = match.group(2)
        after = match.group(3)
        if src.startswith(("data:", "http://", "https://")):
            return match.group(0)
        asset_path = (source_html.parent / unquote(src)).resolve()
        if not asset_path.exists():
            return match.group(0)
        mime = mimetypes.guess_type(asset_path.name)[0] or "application/octet-stream"
        data = base64.b64encode(asset_path.read_bytes()).decode("ascii")
        return f'<img{before}src="data:{mime};base64,{data}"{after}>'

    return re.sub(r'<img([^>]*?)src="([^"]+)"([^>]*)>', replace, html, flags=re.IGNORECASE)


def _write_readme(path):
    path.write_text(
        "Open index.html on your iPhone for offline access. This index embeds the released cards and field guide appendices directly, so no separate Field Guide folder is required.\n",
        encoding="utf-8",
    )


def _remove_tree(path):
    for attempt in range(3):
        try:
            shutil.rmtree(path)
            return
        except OSError:
            if attempt == 2:
                raise
            time.sleep(0.2)


def _staging_output_dir(paths):
    return paths.merged_build_output_dir.parent / f".{paths.merged_build_output_dir.name}.staging"


def _publish_staging_dir(staging_dir, final_dir):
    if final_dir.exists():
        _remove_tree(final_dir)
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging_dir, final_dir)
