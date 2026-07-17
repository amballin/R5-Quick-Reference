"""Shared internal navigation for generated web pages."""

import html
import json


SITE_NAV_CSS = """
.site-nav{position:sticky;top:0;z-index:10;display:grid;grid-template-columns:minmax(52px,1fr) minmax(0,auto) minmax(52px,1fr);align-items:center;gap:8px;width:100%;padding:calc(env(safe-area-inset-top,0px) + 12px) max(12px,env(safe-area-inset-right,0px)) 11px max(12px,env(safe-area-inset-left,0px));background:var(--site-nav-bg,#132742);color:var(--site-nav-text,#f7fbff);border-bottom:1px solid var(--site-nav-rule,rgba(155,210,255,.22));font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.site-nav__back,.site-nav__home{color:inherit;text-decoration:none;min-height:44px;display:flex;align-items:center}
.site-nav__back{justify-self:start;font-size:15px;font-weight:600}
.site-nav__home{justify-self:center;text-align:center;font-size:20px;font-weight:750;white-space:nowrap}
.site-nav__spacer{min-width:0}
.site-nav__brand{justify-self:end;width:38px;height:38px;display:flex;align-items:center;justify-content:center}
.site-nav__brand img{display:block;max-width:38px;max-height:38px;width:auto;height:auto;object-fit:contain}
.site-nav__meta{grid-column:1/-1;text-align:center;color:var(--site-nav-muted,#b9d5ec);font-size:13px;margin:-5px 0 0}
.site-nav__back:focus-visible,.site-nav__home:focus-visible{outline:2px solid currentColor;outline-offset:2px;border-radius:4px}
.output-mode .site-nav{display:none!important}
@media print{.site-nav{display:none!important}}
@media (max-width:340px){.site-nav__home{font-size:18px}.site-nav__back{font-size:14px}}
"""


def brand_image(src):
    """Return the decorative brand image used at the right of shared headers."""
    safe_src = html.escape(src, quote=True)
    return f'<img src="{safe_src}" alt="" aria-hidden="true" onerror="this.hidden=true">'


def site_navigation(home_url, back_url=None, metadata=None, dynamic_return=False, right_html=""):
    """Return the shared header with internal, relative navigation targets."""
    safe_home = html.escape(home_url, quote=True)
    safe_back = html.escape(back_url or home_url, quote=True)
    back = (
        f'<a class="site-nav__back" href="{safe_back}"><span aria-hidden="true">←</span>&nbsp;Back</a>'
        if back_url is not None else '<span class="site-nav__spacer" aria-hidden="true"></span>'
    )
    meta = f'<p class="site-nav__meta">{html.escape(metadata)}</p>' if metadata else ""
    right = f'<span class="site-nav__brand">{right_html}</span>' if right_html else '<span class="site-nav__spacer" aria-hidden="true"></span>'
    script = _dynamic_return_script(home_url) if dynamic_return else ""
    return (
        '<header class="site-nav" data-site-navigation>'
        f'{back}<a class="site-nav__home" href="{safe_home}">Camera Settings</a>'
        f'{right}'
        f'{meta}</header>{script}'
    )


def _dynamic_return_script(home_url):
    fallback = json.dumps(home_url)
    return f"""<script>
(function () {{
  const back = document.querySelector(".site-nav__back");
  if (!back) return;
  const candidate = new URLSearchParams(window.location.search).get("return");
  const cardReturn = /^\.\.\/Cards\/[^/?#]+\.html$/;
  const appendixReturn = /^[^/?#]+\.html$/;
  if (candidate && (cardReturn.test(candidate) || appendixReturn.test(candidate))) {{
    back.setAttribute("href", candidate);
  }} else {{
    back.setAttribute("href", {fallback});
  }}
}})();
</script>"""
