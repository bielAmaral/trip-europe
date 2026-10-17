#!/usr/bin/env python3
"""Generate complete Mindtrip markdown + PDF from index.html."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from mindtrip_lib import build_document

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
OUT_MD = ROOT / "docs" / "mindtrip-complete.md"
OUT_PART1 = ROOT / "docs" / "mindtrip-complete-part1.md"
OUT_PART2 = ROOT / "docs" / "mindtrip-complete-part2.md"
PDF_SCRIPT = ROOT / "scripts" / "generate_prompt_pdf.py"


def split_parts(full: str) -> tuple[str, str]:
    marker = "## DAY-BY-DAY EXECUTABLE PLAN (PRIMARY)"
    idx = full.find(marker)
    if idx < 0:
        return full, ""
    # split day section in half by day count
    head = full[:idx]
    tail = full[idx:]
    day_chunks = tail.split("### 2026-")
    if len(day_chunks) < 3:
        return full, ""
    mid = len(day_chunks) // 2
    p1_tail = marker + "\n\n" + "### 2026-" + "### 2026-".join(day_chunks[1 : mid + 1])
    p2_tail = marker + "\n\n(cont.)" + "\n\n### 2026-" + "### 2026-".join(day_chunks[mid + 1 :])
    return head + p1_tail, p2_tail


def main() -> int:
    if not INDEX.is_file():
        raise SystemExit(f"Missing {INDEX}")
    doc = build_document(INDEX)
    OUT_MD.write_text(doc, encoding="utf-8")
    print(f"OK markdown: {OUT_MD} ({OUT_MD.stat().st_size // 1024} KB)")

    part1, part2 = split_parts(doc)
    if part2:
        OUT_PART1.write_text(part1, encoding="utf-8")
        OUT_PART2.write_text(part2, encoding="utf-8")
        print(f"OK part1: {OUT_PART1} ({OUT_PART1.stat().st_size // 1024} KB)")
        print(f"OK part2: {OUT_PART2} ({OUT_PART2.stat().st_size // 1024} KB)")

    for src in [OUT_MD, OUT_PART1, OUT_PART2]:
        if src.is_file():
            subprocess.run([sys.executable, str(PDF_SCRIPT), str(src)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
