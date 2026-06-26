#!/usr/bin/env python3
"""Gera PROMPT-MESTRE-ROTEIRO.pdf a partir de docs/PROMPT-MESTRE-ROTEIRO.txt via Chrome headless."""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "PROMPT-MESTRE-ROTEIRO.txt"
HTML_OUT = ROOT / "docs" / "PROMPT-MESTRE-ROTEIRO.html"
PDF_OUT = ROOT / "docs" / "PROMPT-MESTRE-ROTEIRO.pdf"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

PRINT_CSS = """
@page { size: A4; margin: 14mm 12mm; }
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 9.5pt;
  line-height: 1.45;
  color: #111;
  max-width: 100%;
}
h1 { font-size: 18pt; margin: 0 0 0.6em; page-break-after: avoid; }
h2 {
  font-size: 13pt;
  margin: 1.4em 0 0.5em;
  padding-top: 0.3em;
  border-top: 1px solid #ddd;
  page-break-after: avoid;
}
h2:first-of-type { border-top: none; }
h3 { font-size: 11pt; margin: 1em 0 0.4em; page-break-after: avoid; }
p { margin: 0.4em 0; }
blockquote {
  margin: 0.6em 0;
  padding: 0.4em 0 0.4em 0.9em;
  border-left: 3px solid #888;
  color: #333;
}
hr { border: none; border-top: 1px solid #ccc; margin: 1em 0; }
ul, ol { margin: 0.4em 0 0.6em 1.2em; padding: 0; }
li { margin: 0.15em 0; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.6em 0 1em;
  font-size: 8.5pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #bbb;
  padding: 3px 5px;
  vertical-align: top;
  text-align: left;
}
th { background: #f0f0f0; font-weight: 600; }
pre {
  margin: 0.5em 0;
  padding: 0.5em 0.6em;
  background: #f6f6f6;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 7.5pt;
  line-height: 1.35;
  white-space: pre-wrap;
  word-break: break-word;
  page-break-inside: avoid;
}
code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
  background: #f2f2f2;
  padding: 0.05em 0.25em;
  border-radius: 2px;
}
.meta { font-size: 8.5pt; color: #444; margin-bottom: 1em; }
"""


def inline_format(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 2


def is_table_sep(line: str) -> bool:
    s = line.strip().strip("|")
    return bool(re.match(r"^[\s:\-|]+$", s))


def parse_table(lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in lines:
        if is_table_sep(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    parts = ["<table><thead><tr>"]
    for cell in head:
        parts.append(f"<th>{inline_format(cell)}</th>")
    parts.append("</tr></thead>")
    if body:
        parts.append("<tbody>")
        for row in body:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{inline_format(cell)}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")
    parts.append("</table>")
    return "".join(parts)


def md_to_html(source: str) -> str:
    lines = source.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    code_buf: list[str] = []

    def flush_code() -> None:
        nonlocal code_buf
        if code_buf:
            out.append("<pre>" + html.escape("\n".join(code_buf)) + "</pre>")
            code_buf = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if stripped == "---":
            out.append("<hr>")
            i += 1
            continue

        if is_table_row(line):
            table_lines = []
            while i < len(lines) and is_table_row(lines[i]):
                table_lines.append(lines[i])
                i += 1
            out.append(parse_table(table_lines))
            continue

        if stripped.startswith("# "):
            out.append(f"<h1>{inline_format(stripped[2:])}</h1>")
            i += 1
            continue
        if stripped.startswith("## "):
            out.append(f"<h2>{inline_format(stripped[3:])}</h2>")
            i += 1
            continue
        if stripped.startswith("### "):
            out.append(f"<h3>{inline_format(stripped[4:])}</h3>")
            i += 1
            continue

        if stripped.startswith("> "):
            out.append(f"<blockquote><p>{inline_format(stripped[2:])}</p></blockquote>")
            i += 1
            continue

        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(inline_format(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            out.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(
                    inline_format(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                )
                i += 1
            out.append("<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>")
            continue

        if stripped == "":
            i += 1
            continue

        out.append(f"<p>{inline_format(line)}</p>")
        i += 1

    flush_code()
    return "\n".join(out)


def build_html(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>PROMPT MESTRE — Europa Central Nov–Dez 2026</title>
  <style>{PRINT_CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def chrome_to_pdf(html_path: Path, pdf_path: Path) -> None:
    if not CHROME.is_file():
        raise SystemExit(f"Chrome não encontrado: {CHROME}")
    url = html_path.resolve().as_uri()
    cmd = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--print-to-pdf={pdf_path.resolve()}",
        url,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def main() -> int:
    if not SRC.is_file():
        print(f"Ficheiro não encontrado: {SRC}", file=sys.stderr)
        return 1
    text = SRC.read_text(encoding="utf-8")
    body = md_to_html(text)
    HTML_OUT.write_text(build_html(body), encoding="utf-8")
    chrome_to_pdf(HTML_OUT, PDF_OUT)
    size_kb = PDF_OUT.stat().st_size / 1024
    print(f"OK: {PDF_OUT.name} ({size_kb:.0f} KB)")
    print(f"    {HTML_OUT.name} (intermédio)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
