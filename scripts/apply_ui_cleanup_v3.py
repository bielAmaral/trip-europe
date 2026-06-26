#!/usr/bin/env python3
"""Enxugo UI v3: extrair JS, remover duplicados na interface."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

RESUMO_OLD = (
    "<p>Munique → Salzburgo → Viena → Bratislava → Budapeste → Berlim → Praga → Bruxelas. "
    "<strong>FlixBus + ICE (Omio)</strong> nos trechos terrestres com <strong>horários de referência</strong> "
    "na seção <a href=\"#horarios-bilhetes\">Horários Omio</a>; <strong>voos curtos</strong>: "
    "<strong>BUD → BER</strong> <strong>30 nov 15h40–17h10</strong> (Ryanair + bagagens, <strong>R$ 734,34</strong>) · "
    "<strong>PRG → BRU</strong> <strong>5 dez 11h50–13h20</strong> (Ryanair + bagagens, <strong>R$ 835,77</strong> Omio). "
    "Berlim–Praga: <strong>FlixBus Südkreuz → Florenc ~10h20–14h20</strong> (<strong>3 dez</strong>).</p>"
)
RESUMO_NEW = (
    "<p>Munique → Salzburgo → Viena → Bratislava → Budapeste → Berlim → Praga → Bruxelas. "
    "Terrestres e voos curtos: <a href=\"#horarios-bilhetes\">Horários Omio</a> · "
    "<a href=\"#voos\">Voos</a>.</p>"
)

MAPAS_LEDE_OLD = (
    '<p class="lede">Paradas na <strong>ordem do FAST TOURIST</strong>. Em cada dia do roteiro e na tab Mapa vês '
    "<strong>como ir</strong> entre pontos (ex.: <em>Metro — U4 Hbf → Odeonsplatz</em>, "
    "<em>Trem — ICE Salzburg → Wien Hbf</em>) com link para abrir a rota no Maps.</p>"
)
MAPAS_LEDE_NEW = (
    '<p class="lede">Paradas GPS na <strong>ordem do FAST</strong> — abre em cada dia (tab Dias). '
    "Índice rápido abaixo; transporte entre pontos no plano do dia.</p>"
)

SEARCH_HINT_OLD = (
    '<p class="trip-search-hint">A pesquisa abrange todo o conteúdo. Campo vazio repõe a vista; '
    "secções sem correspondência ficam ocultas (exceto na pré-visualização de resultados). Toque fora para fechar.</p>"
)
SEARCH_HINT_NEW = '<p class="trip-search-hint">Campo vazio repõe a vista. Toque fora para fechar.</p>'

INLINE_SCRIPT_RE = re.compile(
    r"  <script>\(function\(\)\{function labelDataTables\(\).*?</script>\n",
    re.DOTALL,
)
HOJE_SCRIPT_RE = re.compile(
    r"  <script>\(function\(\)\{function pad2\(n\).*?hojeDestaqueBtn.*?</script>\n",
    re.DOTALL,
)
INDICE_DIAS_RE = re.compile(
    r'\n      <div class="card day-index-card" id="indice-dias">.*?</div>\n',
    re.DOTALL,
)
TOOLBAR_HINT_RE = re.compile(
    r'\n      <span class="toolbar-hint toolbar-hint--toolbar">.*?</span>',
    re.DOTALL,
)
FLIGHT_REF_RE = re.compile(
    r'\n<p class="note flight-day-checklist-ref">.*?</p>',
    re.DOTALL,
)
FAST_PLAN_ATTRS_RE = re.compile(
    r'(<div class="fast-plan" id="fast-day-[^"]+") data-budget-eur="[^"]*" data-energy="[^"]*"',
)


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")

    if RESUMO_OLD in html:
        html = html.replace(RESUMO_OLD, RESUMO_NEW)
    if MAPAS_LEDE_OLD in html:
        html = html.replace(MAPAS_LEDE_OLD, MAPAS_LEDE_NEW)
    if SEARCH_HINT_OLD in html:
        html = html.replace(SEARCH_HINT_OLD, SEARCH_HINT_NEW)

    html = TOOLBAR_HINT_RE.sub("", html)
    html = INDICE_DIAS_RE.sub("\n", html)
    html = FLIGHT_REF_RE.sub("", html)
    html = FAST_PLAN_ATTRS_RE.sub(r"\1", html)

    if not INLINE_SCRIPT_RE.search(html):
        raise SystemExit("inline script block not found")
    html = INLINE_SCRIPT_RE.sub(
        '  <script src="app-core.js?v=1"></script>\n',
        html,
        count=1,
    )

    html = HOJE_SCRIPT_RE.sub("", html)

    html = html.replace('href="app.css?v=37"', 'href="app.css?v=38"')
    html = html.replace('app-mapas.js?v=34', 'app-mapas.js?v=35')

    INDEX.write_text(html, encoding="utf-8")
    print("OK: index.html atualizado (UI cleanup v3)")


if __name__ == "__main__":
    main()
