#!/usr/bin/env python3
"""Generate the readable tracked HTML version of the finish-day recipe."""

from html import escape
from pathlib import Path
import re
import sys


SOURCE_NAME = "FINISH_DAY.md"
OUTPUT_NAME = "FINISH_DAY.html"


def _inline(text):
    rendered = escape(text)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        rendered,
    )
    return rendered


def _markdown_body(source):
    lines = source.splitlines()
    output = []
    paragraph = []
    list_type = None
    in_code = False
    code_lines = []
    section_open = False

    def close_paragraph():
        if paragraph:
            output.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list():
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    for line in lines:
        if line.startswith("```"):
            close_paragraph()
            close_list()
            if in_code:
                command = "\n".join(code_lines)
                output.append(
                    '<div class="command"><button type="button" aria-label="Copy command">'
                    'Copy</button><pre><code>'
                    f"{escape(command)}</code></pre></div>"
                )
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            close_paragraph()
            close_list()
            continue
        if line.startswith("# "):
            close_paragraph()
            close_list()
            output.append(f"<h1>{_inline(line[2:])}</h1>")
            continue
        if line.startswith("## "):
            close_paragraph()
            close_list()
            if section_open:
                output.append("</section>")
            output.append(f'<section class="step"><h2>{_inline(line[3:])}</h2>')
            section_open = True
            continue
        if line.startswith("### "):
            close_paragraph()
            close_list()
            output.append(f"<h3>{_inline(line[4:])}</h3>")
            continue
        if line.startswith("> "):
            close_paragraph()
            close_list()
            output.append(f'<aside class="warning">{_inline(line[2:])}</aside>')
            continue
        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        bullet = re.match(r"^-\s+(.+)$", line)
        if ordered or bullet:
            close_paragraph()
            wanted = "ol" if ordered else "ul"
            if list_type != wanted:
                close_list()
                output.append(f"<{wanted}>")
                list_type = wanted
            output.append(f"<li>{_inline((ordered or bullet).group(1))}</li>")
            continue
        paragraph.append(line.strip())

    close_paragraph()
    close_list()
    if in_code:
        raise ValueError(f"Unclosed code fence in {SOURCE_NAME}")
    if section_open:
        output.append("</section>")
    return "\n".join(output)


def render_guide_html(source, page_title, footer_text, navigation="", project_terminal=False):
    body = _markdown_body(source)
    navigation_html = (
        f'<nav class="guide-nav" aria-label="Workflow navigation">{navigation}</nav>'
        if navigation
        else ""
    )
    terminal_html = ""
    terminal_styles = ""
    terminal_print_style = ""
    terminal_script = ""
    if project_terminal:
        terminal_html = """    <section class="project-terminal" data-project-terminal aria-labelledby="project-terminal-title">
      <div>
        <h2 id="project-terminal-title">Project Terminal</h2>
        <p>Copy the exact command for opening this checkout's repository root in an existing Terminal session.</p>
      </div>
      <div class="terminal-actions">
        <button class="terminal-action terminal-action-secondary" type="button" data-copy-project-root>Copy cd Command</button>
      </div>
      <code data-project-root-command>Determining project root...</code>
      <p class="terminal-status" data-project-terminal-status>Paste the copied command into any open Terminal session.</p>
    </section>
"""
        terminal_styles = """    .project-terminal {
      display: grid;
      gap: 14px;
      background: var(--card);
      border: 1px solid var(--border);
      border-left: 7px solid var(--accent);
      border-radius: 14px;
      box-shadow: 0 8px 24px rgb(0 0 0 / 8%);
      margin: 0 0 22px;
      padding: 18px clamp(18px, 4vw, 28px);
    }
    .project-terminal h2 { margin: 0 0 4px; }
    .project-terminal p { margin: 0; }
    .terminal-actions { display: flex; flex-wrap: wrap; gap: 10px; }
    .terminal-action {
      appearance: none;
      border: 1px solid var(--accent);
      border-radius: 9px;
      background: var(--accent);
      color: #fff;
      cursor: pointer;
      font: inherit;
      font-weight: 750;
      padding: 9px 14px;
      text-decoration: none;
    }
    .terminal-action-secondary {
      background: var(--card);
      border-color: var(--border);
      color: var(--text);
    }
    .terminal-action:disabled { cursor: not-allowed; opacity: .55; }
    .project-terminal > code {
      display: block;
      overflow-x: auto;
      border-radius: 8px;
      background: var(--code);
      color: var(--code-text);
      padding: 11px 13px;
      white-space: nowrap;
    }
    .terminal-status { color: var(--muted); font-size: .9rem; }
"""
        terminal_print_style = "      .project-terminal { display: none; }\n"
        terminal_script = r"""    const terminalPanel = document.querySelector("[data-project-terminal]");
    if (terminalPanel) {
      const commandElement = terminalPanel.querySelector("[data-project-root-command]");
      const copyButton = terminalPanel.querySelector("[data-copy-project-root]");
      const statusElement = terminalPanel.querySelector("[data-project-terminal-status]");
      const shellQuote = (value) => "'" + value.split("'").join("'\\''") + "'";

      if (window.location.protocol === "file:") {
        const projectRootUrl = new URL("../", window.location.href);
        const projectRoot = decodeURIComponent(projectRootUrl.pathname.replace(/\/$/, ""));
        const projectCommand = `cd -- ${shellQuote(projectRoot)}`;
        commandElement.textContent = projectCommand;
        copyButton.addEventListener("click", async () => {
          try {
            await navigator.clipboard.writeText(projectCommand);
          } catch (error) {
            const textarea = document.createElement("textarea");
            textarea.value = projectCommand;
            textarea.setAttribute("readonly", "");
            textarea.style.position = "fixed";
            textarea.style.opacity = "0";
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            textarea.remove();
          }
          copyButton.textContent = "Copied";
          statusElement.textContent = "cd command copied. Paste it into any open Terminal session.";
          window.setTimeout(() => { copyButton.textContent = "Copy cd Command"; }, 1600);
        });
      } else {
        commandElement.textContent = "Open this guide as a local file to determine the checkout path.";
        copyButton.disabled = true;
        statusElement.textContent = "The project-root command is available when this local-only guide is opened from disk.";
      }
    }
"""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(page_title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --page: #f4f6f8;
      --card: #ffffff;
      --text: #17202a;
      --muted: #566573;
      --accent: #9d1d20;
      --code: #17202a;
      --code-text: #f8f9f9;
      --warning: #fff2cc;
      --warning-text: #4d3b00;
      --border: #d5d8dc;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--text);
      font: 18px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ width: min(900px, calc(100% - 28px)); margin: 36px auto 64px; }}
    h1 {{ margin: 0 0 12px; font-size: clamp(2rem, 6vw, 3.4rem); line-height: 1.05; }}
    h1 + p {{ color: var(--muted); font-size: 1.1em; margin-bottom: 30px; }}
    .step {{
      background: var(--card);
      border: 1px solid var(--border);
      border-left: 7px solid var(--accent);
      border-radius: 14px;
      box-shadow: 0 8px 24px rgb(0 0 0 / 8%);
      margin: 18px 0;
      padding: 22px clamp(18px, 4vw, 34px) 28px;
    }}
    h2 {{ margin: 0 0 14px; font-size: clamp(1.35rem, 4vw, 1.8rem); line-height: 1.2; }}
    h3 {{ margin: 24px 0 10px; font-size: clamp(1.1rem, 3.4vw, 1.35rem); line-height: 1.25; }}
    li + li {{ margin-top: 8px; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .9em; }}
    p code, li code, aside code {{
      background: rgb(127 127 127 / 14%);
      border-radius: 5px;
      padding: 2px 5px;
    }}
    .command {{ position: relative; margin: 16px 0; }}
    pre {{
      margin: 0;
      overflow-x: auto;
      border-radius: 10px;
      background: var(--code);
      color: var(--code-text);
      padding: 18px 74px 18px 18px;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .command button {{
      position: absolute;
      right: 9px;
      top: 9px;
      border: 1px solid #808b96;
      border-radius: 7px;
      background: #f8f9f9;
      color: #17202a;
      cursor: pointer;
      font-weight: 700;
      padding: 7px 10px;
    }}
    .warning {{
      border-radius: 10px;
      background: var(--warning);
      color: var(--warning-text);
      font-weight: 650;
      margin-top: 18px;
      padding: 14px 16px;
    }}
    footer {{ color: var(--muted); font-size: .86rem; margin-top: 24px; text-align: center; }}
    a {{ color: var(--accent); font-weight: 700; }}
    .guide-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px 18px;
      margin: 0 0 22px;
    }}
    .guide-nav a {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 14px;
      text-decoration: none;
    }}
{terminal_styles}    @media (prefers-color-scheme: dark) {{
      :root {{
        --page: #111416;
        --card: #1d2327;
        --text: #f2f3f4;
        --muted: #bdc3c7;
        --border: #424949;
      }}
    }}
    @media print {{
      body {{ background: white; color: black; font-size: 12pt; }}
      main {{ margin: 0; width: 100%; }}
      .step {{ break-inside: avoid; box-shadow: none; }}
      .command button {{ display: none; }}
{terminal_print_style}      pre {{ background: #eee; color: black; }}
    }}
  </style>
</head>
<body>
  <main>
{terminal_html}    {navigation_html}
{body}
    <footer>{escape(footer_text)}</footer>
  </main>
  <script>
    for (const button of document.querySelectorAll(".command button")) {{
      button.addEventListener("click", async () => {{
        const command = button.nextElementSibling.innerText;
        await navigator.clipboard.writeText(command);
        button.textContent = "Copied";
        window.setTimeout(() => {{ button.textContent = "Copy"; }}, 1400);
      }});
    }}
{terminal_script}  </script>
</body>
</html>
"""


def render_finish_day_html(source):
    return render_guide_html(
        source,
        "Finish Day: Sync, Spreadsheets, Publish",
        f"Generated from {SOURCE_NAME}. Run the normal build after editing the source.",
        '<a href="WORKFLOWS/index.html">Workflow Index</a>',
    )


def paths_for(root):
    root = Path(root).resolve()
    return root / SOURCE_NAME, root / OUTPUT_NAME


def expected_finish_day_html(root):
    source_path, _ = paths_for(root)
    return render_finish_day_html(source_path.read_text(encoding="utf-8"))


def write_finish_day_html(root):
    _, output_path = paths_for(root)
    rendered = expected_finish_day_html(root)
    if not output_path.exists() or output_path.read_text(encoding="utf-8") != rendered:
        output_path.write_text(rendered, encoding="utf-8")
        print(f"Finish-day HTML guide generated: {output_path}")
    return output_path


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    write_finish_day_html(root)


if __name__ == "__main__":
    main()
