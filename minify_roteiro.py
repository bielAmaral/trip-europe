#!/usr/bin/env python3
"""
Ao alterar conteúdo PWA, faz bump da constante CACHE em `sw.js` (inclui `app-shell.js` no precache). A entrada publicada na netlify é `index.html` (manifest + service worker). 

Minifica o bloco <style> e o <script> inline de roteiro.html para reduzir bytes
(ficheiro único, útil em telemóvel / offline).

Dependências: rcssmin e rjsmin (extensões C, rápidas e estáveis).
  pip install rcssmin rjsmin
ou, sem instalação global:
  pip install -t _vendor_minify rcssmin rjsmin
  PYTHONPATH=_vendor_minify python3 minify_roteiro.py
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "roteiro.html"
VENDOR = HERE / "_vendor_minify"


def _ensure_minifiers() -> tuple[object, object]:
    try:
        import rcssmin  # type: ignore
        import rjsmin  # type: ignore
    except ImportError:
        sys.path[:0] = [str(VENDOR)]
        try:
            import rcssmin  # type: ignore
            import rjsmin  # type: ignore
        except ImportError:
            pass
        else:
            return rcssmin, rjsmin
        if not any(VENDOR.glob("rcssmin*")):
            print(
                "Instalando rcssmin e rjsmin em _vendor_minify/ …",
                file=sys.stderr,
            )
            VENDOR.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-q",
                    "-t",
                    str(VENDOR),
                    "rcssmin",
                    "rjsmin",
                ],
                check=True,
            )
        sys.path[:0] = [str(VENDOR)]
        import rcssmin  # type: ignore
        import rjsmin  # type: ignore
    return rcssmin, rjsmin


def _strip_html_comments(html: str) -> str:
    """Remove comentários <!-- ... --> (SVG incluído). Sem <pre> no roteiro."""
    return re.sub(r"<!--[\s\S]*?-->", "", html)


def minify_html(html: str, rcssmin: object, rjsmin: object, strip_comments: bool) -> str:
    cssmin = getattr(rcssmin, "cssmin")
    jsmin = getattr(rjsmin, "jsmin")

    def repl_style(m: re.Match[str]) -> str:
        return "<style>" + cssmin(m.group(1)) + "</style>"

    out = re.sub(r"<style>([\s\S]*?)</style>", repl_style, html, count=1, flags=re.I)

    def repl_script(m: re.Match[str]) -> str:
        attrs = m.group(1) or ""
        body = m.group(2) or ""
        if re.search(r"\bsrc\s*=", attrs, re.I):
            return m.group(0)
        return "<script" + attrs + ">" + jsmin(body) + "</script>"

    out = re.sub(r"<script([^>]*)>([\s\S]*?)</script>", repl_script, out, flags=re.I)
    if strip_comments:
        out = _strip_html_comments(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Minifica CSS e JS inline em roteiro.html")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Ficheiro de saída (omissão: sobrescreve roteiro.html)",
    )
    ap.add_argument(
        "--no-strip-comments",
        action="store_true",
        help="Não remover comentários HTML/SVG <!-- -->",
    )
    args = ap.parse_args()

    if not TARGET.is_file():
        print(f"Não encontrado: {TARGET}", file=sys.stderr)
        return 1

    raw = TARGET.read_text(encoding="utf-8")
    before = len(raw.encode("utf-8"))
    rcssmin, rjsmin = _ensure_minifiers()
    out = minify_html(raw, rcssmin, rjsmin, strip_comments=not args.no_strip_comments)
    dest = args.output or TARGET
    dest.write_text(out, encoding="utf-8")
    after = len(out.encode("utf-8"))
    pct = 100.0 * after / before if before else 0.0
    print(f"{TARGET.name}: {before} → {after} bytes ({pct:.1f}% do original)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
