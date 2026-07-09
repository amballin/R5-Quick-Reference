import html
import json
import os
import re
from textwrap import wrap
from urllib.parse import quote, unquote, urlparse

from validators.common import load_yaml_checked


def render_appendices(paths, include_pdf=False):
    manifest_path = paths.root / "50 Field Guide" / "required_appendices.yaml"
    if not manifest_path.exists():
        return {"Appendix HTML": 0, "Appendix PDF": 0, "Search": 0}

    manifest = load_yaml_checked(manifest_path) or {}
    appendices = manifest.get("appendices", []) or []
    html_dir = paths.field_guide_html_output_dir
    pdf_dir = paths.field_guide_pdf_output_dir
    html_dir.mkdir(parents=True, exist_ok=True)
    if include_pdf:
        pdf_dir.mkdir(parents=True, exist_ok=True)

    search_entries = []
    generated = {"Appendix HTML": 0, "Appendix PDF": 0, "Search": 0}
    for entry in appendices:
        source = paths.root / "50 Field Guide" / entry.get("file", "")
        if not source.exists():
            continue
        title = entry.get("title") or source.stem
        markdown = source.read_text(encoding="utf-8", errors="replace")
        html_path = html_dir / f"{source.stem}.html"
        if entry.get("id") == "canon_r5_official_icon_reference":
            html_path.write_text(_canon_icon_reference_html(paths), encoding="utf-8")
        else:
            rendered_html = _html_document(title, markdown)
            rendered_html = _rewrite_local_image_sources(source, html_path, rendered_html)
            html_path.write_text(rendered_html, encoding="utf-8")
        if include_pdf:
            pdf_path = pdf_dir / f"{source.stem}.pdf"
            _write_simple_pdf(pdf_path, title, _plain_text(markdown))
            generated["Appendix PDF"] += 1
        search_entries.extend(_search_entries(entry, source, html_path, markdown))
        generated["Appendix HTML"] += 1

    search_path = paths.field_guide_search_index_file
    search_path.parent.mkdir(parents=True, exist_ok=True)
    search_path.write_text(json.dumps(search_entries, indent=2), encoding="utf-8")
    generated["Search"] = 1
    return generated


def _html_document(title, markdown):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.5;max-width:860px;margin:40px auto;padding:0 24px;color:#172033}}
h1{{font-size:34px}}
h2{{border-bottom:1px solid #d7dee8;padding-bottom:4px;margin-top:32px}}
h3{{margin-top:24px}}
table{{border-collapse:collapse;width:100%;margin:16px 0}}
th,td{{border:1px solid #d7dee8;padding:7px;text-align:left;vertical-align:top}}
code{{background:#eef2f7;padding:2px 4px;border-radius:4px}}
a{{color:#165d9c}}
</style>
</head>
<body>
{_markdown_to_html(markdown)}
</body>
</html>
"""


def _canon_icon_reference_html(paths):
    entries = load_yaml_checked(paths.root / "data" / "canon_r5_icons.yaml") or []
    mode_entries = load_yaml_checked(paths.root / "60 Assets" / "icons" / "canon_r5_official" / "modes.yaml") or []
    subject_to_detect_ids = {
        "subject_to_detect_people",
        "subject_to_detect_animals",
        "subject_to_detect_vehicles",
        "subject_to_detect_none",
    }
    subject_to_detect_order = {
        "subject_to_detect_people": 0,
        "subject_to_detect_animals": 1,
        "subject_to_detect_vehicles": 2,
        "subject_to_detect_none": 3,
    }
    order = [
        "af",
        "subject_to_detect",
        "drive",
        "metering",
        "shutter",
        "exposure",
        "image_quality",
        "white_balance",
        "display",
        "playback",
        "connectivity",
        "flash",
        "special_shooting",
    ]
    titles = {
        "af": "AF Method",
        "subject_to_detect": "Subject to Detect",
        "drive": "Drive",
        "metering": "Metering",
        "shutter": "Shutter",
        "exposure": "Exposure",
        "image_quality": "Image Quality",
        "white_balance": "White Balance",
        "display": "Display",
        "playback": "Playback",
        "connectivity": "Connectivity",
        "flash": "Flash",
        "special_shooting": "Special Shooting",
    }
    by_category = {category: [] for category in order}
    for icon in entries:
        category = "subject_to_detect" if icon.get("id") in subject_to_detect_ids else icon.get("category")
        by_category.setdefault(category, []).append(icon)
    by_category["subject_to_detect"].sort(key=lambda icon: subject_to_detect_order.get(icon.get("id"), 99))

    sections = [_canon_mode_reference_section(paths, mode_entries, "Shooting Modes", lambda icon: str(icon.get("id", "")).startswith("mode-"))]
    sections.append(_canon_mode_reference_section(paths, mode_entries, "Focus Features", lambda icon: str(icon.get("id", "")).startswith("focus-")))
    for category in order:
        icons = by_category.get(category) or []
        if not icons:
            continue
        cards = []
        for icon in icons:
            if icon.get("asset_path"):
                asset_path = paths.root / icon["asset_path"]
                asset = os.path.relpath(asset_path, paths.field_guide_html_output_dir)
                image = f'<img src="{html.escape(asset)}" alt="{html.escape(icon.get("canon_name", ""))}">'
            else:
                image = '<div class="no-asset">screen-only</div>'
            cards.append(
                '<article class="icon-card">'
                f'<div class="icon-frame">{image}</div>'
                '<div>'
                f'<div class="name">{html.escape(icon.get("canon_name", ""))}</div>'
                f'<div class="label">{html.escape(icon.get("display_label", ""))}</div>'
                f'<div class="meta">Where: {html.escape(icon.get("notes", ""))}<br>'
                f'Source: <a href="{html.escape(icon.get("source_url", ""))}">'
                f'{html.escape(icon.get("source_page", ""))}</a></div>'
                '</div>'
                '</article>'
            )
        sections.append(
            f'<section class="category"><h2>{html.escape(titles.get(category, category))}</h2>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Canon EOS R5 Official Icon Reference</title>
<style>
:root{{color-scheme:light;--ink:#191919;--muted:#5c6670;--line:#d8dde3;--panel:#f7f8fa;--accent:#b00020}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:#fff}}
header{{padding:28px 24px 18px;border-bottom:1px solid var(--line)}}
h1{{margin:0 0 8px;font-size:28px;line-height:1.15;letter-spacing:0}}
.subtitle{{margin:0;color:var(--muted);font-size:14px}}
main{{padding:24px 24px 40px}}
.category{{margin:0 0 28px}}
h2{{margin:0 0 12px;font-size:18px;letter-spacing:0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:10px}}
.icon-card{{display:grid;grid-template-columns:52px 1fr;gap:12px;align-items:center;min-height:84px;padding:12px;border:1px solid var(--line);border-radius:8px;background:#fff}}
.icon-frame{{width:52px;height:52px;display:grid;place-items:center;background:var(--panel);border:1px solid #e7eaee;border-radius:6px;overflow:hidden}}
.icon-frame img{{max-width:38px;max-height:38px;display:block}}
.icon-frame img[src*="subject_to_detect_"]{{width:38px;height:38px;object-fit:contain}}
.no-asset{{font-size:11px;color:var(--muted);text-align:center;line-height:1.15;padding:4px}}
.name{{font-weight:650;font-size:14px;line-height:1.2;overflow-wrap:anywhere}}
.label{{margin-top:3px;color:var(--accent);font-size:12px;font-weight:650}}
.meta{{margin-top:6px;color:var(--muted);font-size:11px;line-height:1.25}}
a{{color:inherit}}
@media print{{header,main{{padding-left:18px;padding-right:18px}}.grid{{grid-template-columns:repeat(3,1fr)}}.icon-card{{break-inside:avoid}}}}
</style>
</head>
<body>
<header><h1>Canon EOS R5 Official Icon Reference</h1><p class="subtitle">Official Canon names and extracted assets from Canon EOS R5 Product Manual pages at cam.start.canon.</p></header>
<main>{"".join(sections)}</main>
</body>
</html>
"""


def _canon_mode_reference_section(paths, entries, title, predicate):
    cards = []
    for icon in entries:
        if not isinstance(icon, dict) or not predicate(icon):
            continue
        asset_path = paths.root / "60 Assets" / "icons" / "canon_r5_official" / icon.get("icon", "")
        asset = os.path.relpath(asset_path, paths.field_guide_html_output_dir)
        cards.append(
            '<article class="icon-card">'
            f'<div class="icon-frame"><img src="{html.escape(asset)}" alt="{html.escape(icon.get("canon_name", ""))}"></div>'
            '<div>'
            f'<div class="name">{html.escape(icon.get("canon_name", ""))}</div>'
            f'<div class="label">{html.escape(icon.get("label", ""))}</div>'
            f'<div class="meta">{html.escape(icon.get("plain_description", ""))}<br>'
            f'Source: <a href="{html.escape(icon.get("source", ""))}">Canon EOS R5 manual</a></div>'
            '</div>'
            '</article>'
        )
    if not cards:
        return ""
    return f'<section class="category"><h2>{html.escape(title)}</h2><div class="grid">{"".join(cards)}</div></section>'


def _markdown_to_html(markdown):
    lines = markdown.splitlines()
    out = []
    paragraph = []
    table = []
    list_open = False
    list_tag = None

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list():
        nonlocal list_open, list_tag
        if list_open:
            out.append(f"</{list_tag}>")
            list_open = False
            list_tag = None

    def open_list(tag):
        nonlocal list_open, list_tag
        if list_open and list_tag != tag:
            close_list()
        if not list_open:
            out.append(f"<{tag}>")
            list_open = True
            list_tag = tag

    def flush_table():
        nonlocal table
        if not table:
            return
        out.append("<table>")
        for idx, row in enumerate(table):
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if idx == 1 and all(set(cell.replace(" ", "")) <= {"-", ":"} for cell in cells):
                continue
            tag = "th" if idx == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{_inline(cell)}</{tag}>" for cell in cells) + "</tr>")
        out.append("</table>")
        table = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            flush_paragraph()
            close_list()
            table.append(stripped)
            continue
        flush_table()
        if not stripped:
            flush_paragraph()
            close_list()
        elif stripped.startswith("#"):
            flush_paragraph()
            close_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            out.append(f'<h{level} id="{_anchor(text)}">{_inline(text)}</h{level}>')
        elif stripped.startswith("- "):
            flush_paragraph()
            open_list("ul")
            out.append(f"<li>{_inline(stripped[2:])}</li>")
        elif re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            open_list("ol")
            item_text = re.sub(r"^\d+\.\s+", "", stripped)
            out.append(f"<li>{_inline(item_text)}</li>")
        else:
            paragraph.append(stripped)
    flush_paragraph()
    close_list()
    flush_table()
    return "\n".join(out)


def _inline(text):
    escaped = html.escape(text)
    escaped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _image, escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, escaped)


def _image(match):
    alt = match.group(1)
    src = quote(match.group(2), safe="/:#%")
    if "subject_to_detect_" in src:
        return (
            f'<img src="{src}" alt="{alt}" '
            'class="setting-icon subject-detection-icon" style="width:40px;height:24px;object-fit:contain;vertical-align:middle;">'
        )
    return (
        f'<img src="{src}" alt="{alt}" '
        'class="setting-icon" style="width:22px;height:22px;object-fit:contain;vertical-align:middle;">'
    )


def _rewrite_local_image_sources(source_markdown, html_path, rendered_html):
    def replace(match):
        before = match.group(1)
        src = match.group(2)
        after = match.group(3)
        parsed = urlparse(src)
        if parsed.scheme or src.startswith(("#", "/")):
            return match.group(0)
        source_asset = (source_markdown.parent / unquote(parsed.path)).resolve()
        relative = os.path.relpath(source_asset, html_path.parent)
        relative = quote(relative, safe="/:#%")
        if parsed.query:
            relative = f"{relative}?{parsed.query}"
        if parsed.fragment:
            relative = f"{relative}#{parsed.fragment}"
        return f'<img{before}src="{relative}"{after}>'

    return re.sub(r'<img([^>]*?)src="([^"]+)"([^>]*)>', replace, rendered_html, flags=re.IGNORECASE)


def _link(match):
    label = match.group(1)
    href = match.group(2)
    if href.endswith(".md"):
        href = href[:-3] + ".html"
    return f'<a href="{href}">{label}</a>'


def _anchor(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


def _plain_text(markdown):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", markdown)
    return re.sub(r"`([^`]+)`", r"\1", text).replace("|", " ")


def _search_entries(entry, source, html_path, markdown):
    results = []
    current_heading = entry.get("title") or source.stem
    current = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if current:
                results.append(_search_entry(entry, source, html_path, current_heading, "\n".join(current)))
                current = []
            current_heading = stripped.lstrip("#").strip()
        elif stripped:
            current.append(stripped)
    if current:
        results.append(_search_entry(entry, source, html_path, current_heading, "\n".join(current)))
    return results


def _search_entry(entry, source, html_path, heading, body):
    return {
        "appendix_id": entry.get("id"),
        "title": entry.get("title"),
        "section": heading,
        "source": str(source.relative_to(source.parents[1])),
        "html": f"appendices/{html_path.name}",
        "anchor": _anchor(heading),
        "text": _plain_text(body),
    }


def _write_simple_pdf(path, title, text):
    lines = [title, ""]
    for raw_line in text.splitlines():
        stripped = raw_line.strip("# ").strip()
        lines.extend(wrap(stripped, width=92) or [""])
    pages = [lines[i : i + 48] for i in range(0, len(lines), 48)] or [[]]
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", "", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    page_refs = []
    for page in pages:
        content = _pdf_page_content(page)
        page_ref = len(objects) + 1
        content_ref = len(objects) + 2
        page_refs.append(page_ref)
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_ref} 0 R >>")
        objects.append(f"<< /Length {len(content.encode('latin-1', errors='replace'))} >>\nstream\n{content}\nendstream")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(f'{ref} 0 R' for ref in page_refs)}] /Count {len(page_refs)} >>"
    _write_pdf_objects(path, objects)


def _pdf_page_content(lines):
    parts = ["BT", "/F1 10 Tf", "50 742 Td", "14 TL"]
    for line in lines:
        parts.extend([f"({_pdf_escape(line)}) Tj", "T*"])
    parts.append("ET")
    return "\n".join(parts)


def _pdf_escape(text):
    safe = text.encode("latin-1", errors="replace").decode("latin-1")
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_pdf_objects(path, objects):
    content = ["%PDF-1.4\n"]
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode("latin-1", errors="replace")) for part in content))
        content.append(f"{idx} 0 obj\n{obj}\nendobj\n")
    xref_offset = sum(len(part.encode("latin-1", errors="replace")) for part in content)
    content.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.append(f"{offset:010d} 00000 n \n")
    content.append(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n")
    path.write_bytes("".join(content).encode("latin-1", errors="replace"))
