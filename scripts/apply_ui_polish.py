#!/usr/bin/env python3
"""Extrai CSS inline → styles.css; envolve .transit em <details> colapsável."""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
INDEX = HERE / "index.html"


def extract_inline_css(text: str) -> str:
    m = re.search(
        r"  <style>(.*?)</style>\s*\n  <link rel=\"stylesheet\" href=\"app.css\"",
        text,
        flags=re.DOTALL,
    )
    if not m:
        if 'href="styles.css"' in text:
            print("CSS já extraído (styles.css link presente)")
            return text
        raise SystemExit("Não encontrou bloco <style> inline em index.html")

    css = m.group(1).strip() + "\n"
    (HERE / "styles.css").write_text(css, encoding="utf-8")
    print(f"OK: styles.css ({len(css)} bytes)")

    replacement = (
        '  <link rel="stylesheet" href="styles.css" />\n'
        '  <link rel="stylesheet" href="app.css"'
    )
    return text[: m.start()] + replacement + text[m.end() :]


def wrap_transit_blocks(text: str) -> str:
    pattern = re.compile(
        r'<div class="transit">\s*<strong>([^<]+)</strong>\s*(.*?)\s*</div>',
        flags=re.DOTALL,
    )

    def repl(match: re.Match[str]) -> str:
        title = match.group(1).strip()
        inner = match.group(2).strip()
        summary = re.sub(r"\s*\(referência\)\s*", "", title, flags=re.I).strip()
        return (
            f'<details class="transit-collapse">\n'
            f'            <summary>{summary}</summary>\n'
            f'            <div class="transit transit--nested">\n'
            f"{inner}\n"
            f"            </div>\n"
            f"          </details>"
        )

    new_text, count = pattern.subn(repl, text)
    print(f"OK: {count} blocos transit → transit-collapse")
    return new_text


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    text = extract_inline_css(text)
    if 'class="transit-collapse"' not in text:
        text = wrap_transit_blocks(text)
    else:
        print("transit-collapse já presente — a saltar wrap")
    INDEX.write_text(text, encoding="utf-8")
    print("OK: index.html atualizado")


if __name__ == "__main__":
    main()
