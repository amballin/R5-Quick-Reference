"""Generate a machine-local review index for unreleased card profiles."""

from html import escape
from pathlib import Path
from urllib.parse import quote
import shutil
import tempfile

from generated_output import clean_generated_tree, mirror_tree
from validators.common import load_yaml_checked


def render_card_candidates(paths):
    """Write a disposable mini-site containing only unreleased cards."""
    final_dir = paths.card_candidates_output_dir
    with tempfile.TemporaryDirectory(prefix="prs-card-candidates-") as staging:
        staging_dir = Path(staging)
        cards_dir = staging_dir / "Cards"
        cards_dir.mkdir(parents=True, exist_ok=True)
        candidates = []

        for profile_path in sorted(paths.profiles_dir.glob("*.yaml"), key=lambda path: path.stem.casefold()):
            profile = load_yaml_checked(profile_path) or {}
            if (profile.get("metadata") or {}).get("release") is True:
                continue
            profile_name = profile.get("title") or profile_path.stem
            source = paths.html_output_file(profile_name)
            if not source.exists():
                continue
            target = cards_dir / source.name
            html = source.read_text(encoding="utf-8", errors="replace")
            html = html.replace('href="../../merged-build/index.html"', 'href="../index.html"')
            target.write_text(html, encoding="utf-8")
            candidates.append(
                {
                    "title": profile_name,
                    "status": (profile.get("metadata") or {}).get("status", "Unreleased"),
                    "path": target,
                }
            )

        _write_index(staging_dir / "index.html", candidates)
        mirror_tree(staging_dir, final_dir, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
        clean_generated_tree(final_dir)

    return {"Card Candidates": len(candidates)}


def _write_index(path, candidates):
    rows = "\n".join(
        (
            '<li><a href="Cards/{href}">{title}</a>'
            '<span>{status}</span></li>'
        ).format(
            href=quote(candidate["path"].name, safe="."),
            title=escape(candidate["title"]),
            status=escape(str(candidate["status"])),
        )
        for candidate in candidates
    )
    if not rows:
        rows = "<li>No unreleased cards were found.</li>"
    path.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Card Candidates</title>
<style>
html{{box-sizing:border-box;background:#edf3f8;color:#172033;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
*,*::before,*::after{{box-sizing:inherit}}
body{{max-width:720px;margin:0 auto;padding:calc(env(safe-area-inset-top,0px) + 28px) 18px calc(env(safe-area-inset-bottom,0px) + 32px)}}
h1{{margin:0 0 6px;font-size:clamp(28px,7vw,40px)}}
p{{margin:0 0 22px;color:#536273;line-height:1.45}}
ul{{list-style:none;margin:0;padding:0;display:grid;gap:10px}}
li{{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 16px;border:1px solid #cbd7e3;border-radius:12px;background:#fff;box-shadow:0 4px 14px rgba(23,32,51,.06)}}
a{{color:#165d9c;font-size:18px;font-weight:700;text-decoration:none}}
span{{color:#667587;font-size:13px}}
</style>
</head>
<body>
<h1>Card Candidates</h1>
<p>Machine-local review copies of profiles that are not released. These files are not part of the publishable website.</p>
<ul>
{rows}
</ul>
</body>
</html>
""",
        encoding="utf-8",
    )
