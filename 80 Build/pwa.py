import json
import re
import shutil
import time
import zlib
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

from generated_output import clean_generated_tree, numbered_duplicates


PWA_TITLE = "R5 Settings"
THEME_COLOR = "#132742"
CACHE_PREFIX = "photography-reference"
CACHE_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".json",
    ".mjs",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
}


def generate_pwa(paths, build_version=None):
    """Add PWA files to the generated merged-build tree."""
    version = str(build_version or int(time.time()))
    output_dir = paths.merged_build_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    _raise_on_numbered_duplicates(output_dir)

    icon_dir = output_dir / "app-assets"
    icon_dir.mkdir(parents=True, exist_ok=True)

    _write_icon(icon_dir / "icon-192.png", 192)
    _write_icon(icon_dir / "icon-512.png", 512)
    _write_icon(icon_dir / "apple-touch-icon.png", 180)
    _write_manifest(output_dir / "manifest.webmanifest")
    _write_offline_page(output_dir / "offline.html")
    _copy_search_index(paths, output_dir)
    cache_urls = _cache_urls(paths)
    _write_service_worker(output_dir / "service-worker.js", version, cache_urls)
    _inject_pwa_head(output_dir / "index.html")
    _raise_on_numbered_duplicates(output_dir)
    clean_generated_tree(output_dir)
    return {"PWA": 1}


def _write_manifest(path):
    manifest = {
        "name": "R5 Settings",
        "short_name": "R5 Settings",
        "description": "Offline photography cards and Canon EOS R5 field guide.",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": THEME_COLOR,
        "theme_color": THEME_COLOR,
        "orientation": "portrait",
        "icons": [
            {"src": "app-assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "app-assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "app-assets/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        ],
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _write_offline_page(path):
    path.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="{THEME_COLOR}">
<title>Offline - Camera Settings</title>
<style>
:root{{color-scheme:dark;--bg:{THEME_COLOR};--text:#f7fbff;--muted:#b9d5ec;--panel:#1d395b}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{width:min(34rem,calc(100vw - 32px));background:var(--panel);border:1px solid rgba(155,210,255,.22);border-radius:12px;padding:24px}}
h1{{margin:0 0 8px;font-size:24px}}
p{{margin:0;color:var(--muted);line-height:1.45}}
a{{color:#9bd2ff}}
</style>
</head>
<body>
<main>
<h1>Offline</h1>
<p>The photography reference is available after the first online visit. Return to <a href="index.html">Camera Settings</a> when the cached files are ready.</p>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _write_service_worker(path, version, cache_urls):
    cache_name = f"{CACHE_PREFIX}-{version}"
    path.write_text(
        f"""const CACHE_PREFIX = {json.dumps(CACHE_PREFIX)};
const CACHE_NAME = {json.dumps(cache_name)};
const CACHE_URLS = {json.dumps(cache_urls, indent=2)};

self.addEventListener("install", (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(CACHE_URLS))
      .then(() => self.skipWaiting())
  );
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches.keys()
      .then((names) => Promise.all(
        names
          .filter((name) => name.startsWith(CACHE_PREFIX + "-") && name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      ))
      .then(() => self.clients.claim())
  );
}});

self.addEventListener("fetch", (event) => {{
  const request = event.request;
  const url = new URL(request.url);

  if (url.origin !== self.location.origin || request.method !== "GET") {{
    return;
  }}

  if (request.mode === "navigate") {{
    event.respondWith(
      fetch(request, {{ cache: "reload" }})
        .then((response) => {{
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          return response;
        }})
        .catch(() => caches.match(request).then((cached) => cached || caches.match("./") || caches.match("index.html") || caches.match("offline.html")))
    );
    return;
  }}

  event.respondWith(
    caches.match(request).then((cached) => {{
      if (cached) {{
        return cached;
      }}
      return fetch(request).then((response) => {{
        if (response && response.ok) {{
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }}
        return response;
      }});
    }})
  );
}});
""",
        encoding="utf-8",
    )


def _cache_urls(paths):
    urls = {
        "./",
        "index.html",
        ".nojekyll",
        "manifest.webmanifest",
        "service-worker.js",
        "offline.html",
        "app-assets/icon-192.png",
        "app-assets/icon-512.png",
        "app-assets/apple-touch-icon.png",
    }
    root = paths.merged_build_output_dir
    if root.exists():
        for file_path in root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in CACHE_EXTENSIONS:
                urls.add(_url_for(root, file_path))
    return sorted(urls)


def _url_for(root, path):
    relative = path.relative_to(root).as_posix()
    return "/".join(quote(part) for part in relative.split("/"))


def _inject_pwa_head(index_path):
    if not index_path.exists():
        return
    html = index_path.read_text(encoding="utf-8")
    block = f"""<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="app-assets/apple-touch-icon.png">
<meta name="theme-color" content="{THEME_COLOR}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{PWA_TITLE}">
<script>
if ("serviceWorker" in navigator && location.protocol !== "file:") {{
  window.addEventListener("load", () => {{
    navigator.serviceWorker.register("service-worker.js", {{ updateViaCache: "none" }});
  }});
}}
</script>"""
    html = re.sub(r"\n?<!-- PWA START -->.*?<!-- PWA END -->\n?", "\n", html, flags=re.DOTALL)
    html = html.replace("</head>", f"<!-- PWA START -->\n{block}\n<!-- PWA END -->\n</head>")
    index_path.write_text(html, encoding="utf-8")


def _copy_search_index(paths, output_dir):
    search_index = paths.field_guide_search_index_file
    if search_index.exists():
        shutil.copy2(search_index, output_dir / "search_index.json")


def validate_merged_build_pwa(paths):
    """Validate that the local merged build is a self-contained PWA."""
    output_dir = paths.merged_build_output_dir
    results = []
    required_files = [
        "index.html",
        "manifest.webmanifest",
        "service-worker.js",
        "offline.html",
        "search_index.json",
        "app-assets/apple-touch-icon.png",
        "app-assets/icon-192.png",
        "app-assets/icon-512.png",
    ]
    for relative in required_files:
        if not (output_dir / relative).exists():
            results.append(("error", "merged_build_pwa_missing_file", relative))

    for relative in ["appendices", "app-assets"]:
        if not (output_dir / relative).is_dir():
            results.append(("error", "merged_build_pwa_missing_directory", relative))

    if (output_dir / "manifest.webmanifest").exists():
        results.extend(_validate_manifest(output_dir))
    if (output_dir / "index.html").exists():
        results.extend(_validate_index(output_dir))
    if (output_dir / "service-worker.js").exists():
        results.extend(_validate_service_worker(output_dir))
    results.extend(_validate_referenced_assets(output_dir))
    results.extend(_validate_no_numbered_duplicates(output_dir))
    return results


def _validate_no_numbered_duplicates(output_dir):
    duplicates = numbered_duplicates(output_dir, require_original=False)
    if not duplicates:
        return []
    sample = ", ".join(str(path.relative_to(output_dir)) for path in duplicates[:10])
    return [("error", "merged_build_pwa_numbered_duplicate", sample)]


def _raise_on_numbered_duplicates(output_dir):
    duplicates = numbered_duplicates(output_dir, require_original=False)
    if not duplicates:
        return
    sample = ", ".join(str(path.relative_to(output_dir)) for path in duplicates[:10])
    raise RuntimeError(f"merged-build contains generated duplicate paths before PWA generation: {sample}")


def _validate_manifest(output_dir):
    results = []
    path = output_dir / "manifest.webmanifest"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [("error", "merged_build_pwa_manifest_json", str(exc))]

    for key, value in {"start_url": "./", "scope": "./", "display": "standalone"}.items():
        if manifest.get(key) != value:
            results.append(("error", "merged_build_pwa_manifest_value", f"{key} must be {value}"))

    for icon in manifest.get("icons", []) or []:
        src = icon.get("src", "")
        if not _inside_output(output_dir, src):
            results.append(("error", "merged_build_pwa_manifest_outside", src))
        elif not _resolved_path(output_dir, src).exists():
            results.append(("error", "merged_build_pwa_manifest_missing_icon", src))

    icon_sources = {icon.get("src") for icon in manifest.get("icons", []) or []}
    if "app-assets/apple-touch-icon.png" not in icon_sources:
        results.append(("error", "merged_build_pwa_manifest_apple_icon", "Apple touch icon is missing."))
    return results


def _validate_index(output_dir):
    results = []
    html = (output_dir / "index.html").read_text(encoding="utf-8", errors="replace")
    for needle in [
        'href="manifest.webmanifest"',
        'href="app-assets/apple-touch-icon.png"',
        'navigator.serviceWorker.register("service-worker.js"',
    ]:
        if needle not in html:
            results.append(("error", "merged_build_pwa_index_registration", needle))
    return results


def _validate_service_worker(output_dir):
    results = []
    text = (output_dir / "service-worker.js").read_text(encoding="utf-8", errors="replace")
    for needle in [
        "const CACHE_PREFIX",
        "const CACHE_NAME",
        "const CACHE_URLS",
        "self.addEventListener(\"install\"",
        "self.addEventListener(\"activate\"",
        "caches.delete(name)",
        "request.mode === \"navigate\"",
        "offline.html",
    ]:
        if needle not in text:
            results.append(("error", "merged_build_pwa_service_worker_feature", needle))

    cache_urls = _service_worker_cache_urls(text)
    if cache_urls is None:
        return results + [("error", "merged_build_pwa_service_worker_cache", "CACHE_URLS is not valid JSON.")]
    for url in cache_urls:
        if not _inside_output(output_dir, url):
            results.append(("error", "merged_build_pwa_cache_outside", url))
        elif not _resolved_path(output_dir, url).exists():
            results.append(("error", "merged_build_pwa_cache_missing", url))
    return results


def _validate_referenced_assets(output_dir):
    results = []
    for path in sorted(output_dir.rglob("*")):
        if path.suffix.lower() not in {".html", ".css", ".js", ".webmanifest", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for reference in _references(text, path.suffix.lower()):
            if _skip_reference(reference):
                continue
            if not _inside_output(path.parent, reference, output_dir):
                results.append(("error", "merged_build_pwa_reference_outside", f"{path.relative_to(output_dir)} -> {reference}"))
                continue
            resolved = _resolved_path(path.parent, reference)
            if not resolved.exists():
                results.append(("error", "merged_build_pwa_reference_missing", f"{path.relative_to(output_dir)} -> {reference}"))
    return results


def _references(text, suffix):
    patterns = [r"""(?:src|href|poster|action)\s*=\s*["']([^"']+)["']"""]
    if suffix == ".css":
        patterns.append(r"""url\(\s*["']?([^"')]+)["']?\s*\)""")
    refs = []
    for pattern in patterns:
        refs.extend(match.group(1) for match in re.finditer(pattern, text, flags=re.IGNORECASE))
    if suffix == ".html":
        for style in re.findall(r"<style\b[^>]*>(.*?)</style>", text, flags=re.IGNORECASE | re.DOTALL):
            refs.extend(
                match.group(1)
                for match in re.finditer(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", style, flags=re.IGNORECASE)
            )
    return refs


def _skip_reference(reference):
    parsed = urlparse(reference)
    return (
        not reference
        or reference.startswith("#")
        or parsed.scheme in {"data", "http", "https", "mailto", "tel", "javascript"}
    )


def _service_worker_cache_urls(text):
    match = re.search(r"const\s+CACHE_URLS\s*=\s*(\[.*?\]);", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _inside_output(base_dir, reference, output_dir=None):
    output_dir = (output_dir or base_dir).resolve()
    if reference.startswith("/"):
        return False
    try:
        _resolved_path(base_dir, reference).relative_to(output_dir)
    except ValueError:
        return False
    return True


def _resolved_path(base_dir, reference):
    path_part = unquote(urlparse(reference).path)
    if path_part in {"", "."}:
        return base_dir.resolve()
    return (base_dir / path_part).resolve()


def _write_icon(path, size):
    pixels = _icon_pixels(size)
    _write_png(path, size, size, pixels)


def _icon_pixels(size):
    bg = (19, 39, 66, 255)
    panel = (29, 57, 91, 255)
    accent = (155, 210, 255, 255)
    white = (247, 251, 255, 255)
    pixels = [[bg for _ in range(size)] for _ in range(size)]
    radius = max(18, size // 7)
    margin = size // 9
    _fill_round_rect(pixels, margin, margin, size - margin, size - margin, radius, panel)

    body_x1 = size * 24 // 100
    body_y1 = size * 38 // 100
    body_x2 = size * 76 // 100
    body_y2 = size * 66 // 100
    _fill_round_rect(pixels, body_x1, body_y1, body_x2, body_y2, size // 18, white)
    _fill_rect(pixels, size * 34 // 100, size * 31 // 100, size * 50 // 100, body_y1, white)
    _fill_rect(pixels, size * 57 // 100, size * 33 // 100, size * 68 // 100, size * 38 // 100, accent)
    _fill_circle(pixels, size // 2, size * 52 // 100, size * 13 // 100, bg)
    _fill_circle(pixels, size // 2, size * 52 // 100, size * 8 // 100, accent)
    return pixels


def _fill_rect(pixels, x1, y1, x2, y2, color):
    height = len(pixels)
    width = len(pixels[0])
    for y in range(max(0, y1), min(height, y2)):
        for x in range(max(0, x1), min(width, x2)):
            pixels[y][x] = color


def _fill_round_rect(pixels, x1, y1, x2, y2, radius, color):
    for y in range(y1, y2):
        for x in range(x1, x2):
            dx = max(x1 + radius - x, 0, x - (x2 - radius - 1), 0)
            dy = max(y1 + radius - y, 0, y - (y2 - radius - 1), 0)
            if dx * dx + dy * dy <= radius * radius:
                pixels[y][x] = color


def _fill_circle(pixels, cx, cy, radius, color):
    r2 = radius * radius
    for y in range(max(0, cy - radius), min(len(pixels), cy + radius + 1)):
        for x in range(max(0, cx - radius), min(len(pixels[0]), cx + radius + 1)):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                pixels[y][x] = color


def _write_png(path, width, height, pixels):
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for red, green, blue, alpha in row:
            raw.extend((red, green, blue, alpha))

    def chunk(kind, data):
        return (
            len(data).to_bytes(4, "big")
            + kind
            + data
            + zlib.crc32(kind + data).to_bytes(4, "big")
        )

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes([8, 6, 0, 0, 0])))
    png.extend(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    png.extend(chunk(b"IEND", b""))
    path.write_bytes(png)
