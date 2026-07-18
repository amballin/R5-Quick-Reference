import shutil
import base64
import mimetypes
import os
import re
import tempfile
import time
from html import escape
from pathlib import Path
from urllib.parse import quote, unquote

import yaml

from generated_output import clean_generated_tree, mirror_tree
from html_renderer import shared_header_icon_path
from site_navigation import SITE_NAV_CSS, brand_image, site_navigation


APP_TITLE = "Camera Settings"


def render_offline_index(paths, publish_metadata, include_png=False):
    """Build the merged offline web bundle with cards and guide pages embedded in the index."""
    output_dir = _staging_output_dir(paths)
    final_dir = paths.merged_build_output_dir
    with tempfile.TemporaryDirectory(prefix="prs-merged-build-") as staging:
        output_dir = Path(staging)
        cards_dir = output_dir / "Cards"
        cards_dir.mkdir(parents=True, exist_ok=True)

        card_files = _copy_release_cards(paths, cards_dir, output_dir / "web-assets", include_png=include_png)
        guides = _all_guides(paths)
        _write_appendices(output_dir / "appendices", guides)
        _write_index(output_dir / "index.html", card_files, guides, publish_metadata, paths)
        _write_readme(output_dir / "README.txt")
        (output_dir / ".nojekyll").touch()
        mirror_tree(output_dir, final_dir, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
        clean_generated_tree(final_dir)
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


def _copy_release_cards(paths, target_dir, web_assets_dir, include_png=False):
    copied = []
    for profile_path in sorted(paths.profiles_dir.glob("*.yaml"), key=lambda path: path.stem.lower()):
        profile = _load_yaml(profile_path)
        if not ((profile.get("metadata") or {}).get("release") is True):
            continue
        profile_name = profile.get("title") or profile_path.stem
        html_source = paths.html_output_file(profile_name)
        if not html_source.exists():
            continue
        html_target = target_dir / html_source.name
        html = _published_card_html(paths, html_source, web_assets_dir)
        html_target.write_text(html, encoding="utf-8")
        card = {
            "png_path": None,
            "html_path": html_target,
            "card_type": profile.get("card_type", "profile"),
            "display_category": profile.get("display_category") or (
                "reference" if profile.get("card_type") == "reference" else "subject"
            ),
            "display_order": profile.get("display_order", 100),
            "appendix_links": profile.get("appendix_links") or [],
        }
        if include_png:
            png_source = paths.phone_png_output_file(profile_name)
            if not png_source.exists():
                png_source = paths.png_output_file(profile_name)
            if not png_source.exists():
                continue
            png_target = target_dir / png_source.name
            shutil.copy2(png_source, png_target)
            card["png_path"] = png_target
        copied.append(card)
    return copied


def _published_card_html(paths, source_html, web_assets_dir):
    """Copy a card's local images and rewrite links for a relocatable Pages bundle."""
    html = source_html.read_text(encoding="utf-8", errors="replace")

    def replace_image(match):
        before, src, after = match.groups()
        if src.startswith(("data:", "http://", "https://")):
            return match.group(0)
        source_asset = (source_html.parent / unquote(src)).resolve()
        if not source_asset.is_file():
            return f'<img{before}hidden{after}>'
        try:
            relative_asset = source_asset.relative_to(paths.icon_asset_dir)
        except ValueError:
            relative_asset = Path("misc") / source_asset.name
        target_asset = web_assets_dir / relative_asset
        target_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_asset, target_asset)
        published_src = quote((Path("../web-assets") / relative_asset).as_posix(), safe="/.")
        return f'<img{before}src="{published_src}"{after}>'

    html = re.sub(r'<img([^>]*?)src="([^"]+)"([^>]*)>', replace_image, html, flags=re.IGNORECASE)
    html = html.replace('href="../../merged-build/index.html"', 'href="../index.html"')
    return re.sub(
        r'href="\.\./\.\./field-guide/html/([^"]+)"',
        lambda match: f'href="../appendices/{match.group(1)}"',
        html,
        flags=re.IGNORECASE,
    )


def _all_guides(paths):
    manifest = _load_yaml(paths.root / "50 Field Guide" / "required_appendices.yaml")
    html_dir = paths.field_guide_html_output_dir
    guides = []
    for entry in manifest.get("appendices", []) or []:
        title = entry.get("title") or Path(entry.get("file", "")).stem
        source = html_dir / f"{Path(entry.get('file', '')).stem}.html"
        if not source.exists():
            continue
        html = _inline_local_images(source, source.read_text(encoding="utf-8", errors="replace"))
        guides.append({
            "id": entry.get("id"),
            "title": title,
            "filename": source.name,
            "html": html,
            "release": entry.get("release") is True,
            "content_type": entry.get("content_type", "field_guide"),
            "display_order": entry.get("display_order", 100),
        })
    return sorted(guides, key=lambda guide: (guide["display_order"], guide["title"].lower()))


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


def _write_index(path, card_files, guides, publish_metadata, paths):
    guide_targets = {guide.get("id"): guide["filename"] for guide in guides if guide.get("id")}
    ordered_cards = sorted(card_files, key=lambda card: (card["display_order"], card["html_path"].stem.lower()))
    cards = "\n".join(
        _card_details(card, guide_targets) for card in ordered_cards
        if card["display_category"] == "subject"
    )
    reference_cards = "\n".join(
        _card_details(card, guide_targets) for card in ordered_cards
        if card["display_category"] == "reference"
    )
    reference_section = (
        '<h2>Reference Cards</h2>\n<div class="cards">\n'
        f'{reference_cards}\n</div>'
        if reference_cards else ""
    )
    guide_markup = "\n".join(
        _guide_details(guide) for guide in guides
        if guide["release"] and guide["content_type"] == "field_guide"
    )
    deep_dive_markup = "\n".join(
        _guide_details(guide) for guide in guides
        if guide["release"] and guide["content_type"] == "setting_deep_dive"
    )
    deep_dive_section = (
        '<h2>Deep Dive</h2>\n<div class="guides">\n'
        f'{deep_dive_markup}\n</div>'
        if deep_dive_markup else ""
    )
    icon_path = shared_header_icon_path(paths)
    logo = ""
    if icon_path is not None:
        logo_data = base64.b64encode(icon_path.read_bytes()).decode("ascii")
        mime = "image/svg+xml" if icon_path.suffix.lower() == ".svg" else "image/png"
        logo = brand_image(f"data:{mime};base64,{logo_data}")
    path.write_text(
        f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Camera Settings">
<meta name="mobile-web-app-capable" content="yes">
<title>{APP_TITLE}</title>
<style>
:root{{color-scheme:dark;--bg:#132742;--panel:#1d395b;--text:#f7fbff;--muted:#b9d5ec;--rule:#5b7893;--accent:#9bd2ff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.35}}
{SITE_NAV_CSS}
main{{width:min(100%,640px);margin:0 auto;padding:16px max(14px,env(safe-area-inset-right,0px)) calc(env(safe-area-inset-bottom,0px) + 32px) max(14px,env(safe-area-inset-left,0px))}}
h2{{font-size:18px;color:var(--accent);margin:18px 4px 10px}}
.cards{{display:grid;gap:9px}}
.card-row{{display:flex;align-items:stretch;gap:8px}}
.card-primary{{display:flex;align-items:center;justify-content:space-between;gap:10px;flex:1;color:var(--text);background:var(--panel);border:1px solid rgba(155,210,255,.18);border-radius:10px;padding:13px 14px;min-height:48px;font-weight:700;text-decoration:none}}
.card-primary span{{color:var(--muted);font-weight:400}}
.card-png{{display:grid;place-items:center;min-width:58px;min-height:48px;color:var(--accent);background:var(--panel);border:1px solid rgba(155,210,255,.18);border-radius:10px;padding:10px;text-decoration:none;font-size:13px;font-weight:700}}
.guides{{display:grid;gap:9px}}
.guide{{display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--text);background:var(--panel);border:1px solid rgba(155,210,255,.18);border-radius:10px;padding:13px 14px;min-height:48px;list-style:none}}
.guide::-webkit-details-marker{{display:none}}
.guide span{{color:var(--muted)}}
.hint{{color:var(--muted);font-size:13px;margin:8px 4px 0}}
.card-links{{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin:10px auto 0}}
.card-links a{{color:var(--accent);background:var(--panel);border:1px solid rgba(155,210,255,.35);border-radius:8px;padding:8px 11px;text-decoration:none}}
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
{site_navigation("index.html", metadata=publish_metadata, right_html=logo)}
<main>
<h2>Subjects</h2>
<div class="cards">
{cards}
</div>
<div class="hint">Tap for details</div>
{reference_section}
<h2>Field Guides</h2>
<div class="guides">
{guide_markup}
</div>
{deep_dive_section}
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _card_details(card, guide_targets):
    html_path = card["html_path"]
    label = escape(html_path.stem)
    html_href = quote(f"Cards/{html_path.name}", safe="/:#%")
    png_path = card.get("png_path")
    png_link = ""
    if png_path:
        png_href = quote(f"Cards/{png_path.name}", safe="/:#%")
        png_link = f'<a class="card-png" href="{png_href}" aria-label="Open {label} PNG">PNG</a>'
    return f"""<div class="card-row">
<a class="card-primary" href="{html_href}">{label}<span>Open</span></a>
{png_link}
</div>"""


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
        html = re.sub(
            r"<a\b([^>]*)>(.*?)</a>",
            lambda match: _offline_link(match, ""),
            guide["html"],
            flags=re.IGNORECASE | re.DOTALL,
        )
        (target_dir / guide["filename"]).write_text(html, encoding="utf-8")


def _html_body(html):
    match = re.search(r"<body[^>]*>(.*)</body>", html, flags=re.IGNORECASE | re.DOTALL)
    body = match.group(1) if match else html
    body = re.sub(
        r'<header\b[^>]*data-site-navigation[^>]*>.*?</header>\s*(?:<script>.*?</script>)?',
        "",
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    main = re.search(r"<main\b[^>]*>(.*)</main>", body, flags=re.IGNORECASE | re.DOTALL)
    if main:
        body = main.group(1)
    return re.sub(
        r"<a\b([^>]*)>(.*?)</a>",
        lambda link: _offline_link(link, "appendices/"),
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )


def _offline_link(match, local_prefix):
    attrs = match.group(1)
    label = match.group(2)
    href = re.search(r'href="([^"]+)"', attrs, flags=re.IGNORECASE)
    if href:
        target = href.group(1)
        if target.startswith("#"):
            return match.group(0)
        if not target.startswith(("http://", "https://", "mailto:")):
            rewritten = re.sub(
                r'href="[^"]+"',
                f'href="{local_prefix}{target}"',
                attrs,
                count=1,
                flags=re.IGNORECASE,
            )
            return f'<a{rewritten}>{label}</a>'
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
    mirror_tree(staging_dir, final_dir, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
