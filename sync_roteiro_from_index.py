#!/usr/bin/env python3
"""Copia index.html (canónico) -> roteiro.html."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
src = HERE / "index.html"
dst = HERE / "roteiro.html"
dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
print(f"OK: {src.name} -> {dst.name} ({dst.stat().st_size} bytes)")
