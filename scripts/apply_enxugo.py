#!/usr/bin/env python3
"""Apply enxugo package to index.html (one-shot maintenance script)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

DAY_BRUGES = """      <details class="day" id="day-2026-12-06" data-trip-date="2026-12-06">
        <summary><span class="date-tag">6 dez · dom</span> <span class="city">Bruges — bate-volta (prima Iza)</span><span class="day-badges" aria-label="Tipos de dia"><span class="dt dt-icon">Ícone</span></span></summary>
        <div class="body">
          <div class="slot"><strong>Manhã</strong><p>Comboio cedo <strong>Bruxelles-Nord</strong> ou <strong>Central</strong> → <strong>Brugge</strong> (~1h). Encontro com <strong>Iza</strong>. <strong>Markt</strong>, <strong>Burg</strong>, <strong>Minnewater</strong> — tudo exterior, ritmo de passeio.</p></div>
          <div class="slot"><strong>Tarde</strong><p>Chocolate / waffles leves; canal boat <em>só se couber</em> no tempo. <strong>Regresso a Bruxelas até ~20h00</strong> — dormir no hotel <strong>des Colonies (Rogier)</strong>.</p></div>
          <div class="slot"><strong>Noite</strong><p>Jantar leve perto do hotel, <strong>mala pronta</strong>, alarme ~04h15. <em>Sem</em> Saint-Jacques / festa pesada.</p></div>
          <p class="note">Voo <strong>7 dez 07h00</strong>: zero turismo na manhã do aeroporto.</p>
          <div class="transit">
            <strong>SNCB (referência)</strong>
            <ul>
              <li><strong>Rogier / Nord / Central</strong> → <strong>Brugge:</strong> comboio <strong>IC</strong> (~1h; horário no dia na <strong>SNCB</strong>).</li>
              <li><strong>Brugge centro:</strong> a pé da estação (~12 min) até <strong>Markt</strong>.</li>
              <li><strong>Regresso:</strong> último comboio confortável ~<strong>19h30–20h00</strong> → <strong>Nord</strong> / <strong>Rogier</strong>.</li>
            </ul>
          </div>
        </div>
      </details>"""

def main():
    html = INDEX.read_text(encoding="utf-8")

    # Remove city-day-map blocks
    html = re.sub(
        r'\s*<div class="city-day-map">.*?</div>\s*(?=</div>\s*</details>)',
        "\n",
        html,
        flags=re.DOTALL,
    )

    # Remove operacional fichas (keep operacional section closing)
    html = re.sub(
        r'\s*<h3 id="operacional-fichas">Fichas operacionais</h3>.*?<details class="city-block oper-city" id="oper-bru">.*?</details>\s*(?=</section>\s*<section id="dias")',
        "\n",
        html,
        flags=re.DOTALL,
    )

    # Remove compras-calendario card (keep note from card if needed - merge into matriz note)
    html = re.sub(
        r'\s*<div class="card" style="margin-top:1rem;">\s*<h3 id="compras-calendario">Dias de compras \(calendário\)</h3>.*?</div>\s*(?=<div class="card" style="margin-top:1rem;">\s*<h3 id="compras-fallback-tipo">)',
        "\n",
        html,
        flags=re.DOTALL,
    )

    # compras-calendario links → matriz
    html = html.replace("#compras-calendario", "#compras-matriz-dia")
    html = html.replace("calendário</a>", "matriz</a>")  # may over-replace - check
    html = html.replace(" e no <a href=\"#compras-matriz-dia\">matriz</a>", " na <a href=\"#compras-matriz-dia\">matriz cidade × janela</a>")
    html = html.replace(
        "Use a <strong><a href=\"#compras-matriz-dia\">matriz cidade × janela</a></strong> como vista única (com atalho para cada dia); o <strong><a href=\"#compras-matriz-dia\">matriz</a></strong> repete as janelas por data; o",
        "Use a <strong><a href=\"#compras-matriz-dia\">matriz cidade × janela</a></strong> como vista única (com atalho para cada dia); o",
    )
    html = html.replace(
        "Antes de editar o ficheiro, faça uma <strong>cópia de segurança</strong> (ver nota em <a href=\"#resumo\">Resumo e noites</a>). ",
        "",
    )
    html = html.replace(
        '<a href="#compras-matriz-dia">matriz</a>; <a href="#compras-matriz-dia">matriz</a>',
        '<a href="#compras-matriz-dia">matriz</a>',
    )
    html = html.replace("#compras-matriz-dia\">#compras-matriz-dia", "#compras-matriz-dia\">matriz")

    # Hotel prices - do Berlin before Munich (both had 1816 target but different old values)
    html = html.replace(
        "<td><strong>Premier Inn Berlin Alexanderplatz</strong></td>\n            <td>R$ 1.816</td>",
        "<td><strong>Premier Inn Berlin Alexanderplatz</strong></td>\n            <td>R$ 1.843</td>",
    )
    html = html.replace(
        "<td><strong>B&amp;B Hotel München-Hbf</strong></td>\n            <td>R$ 1.789</td>",
        "<td><strong>B&amp;B Hotel München-Hbf</strong></td>\n            <td>R$ 1.816</td>",
    )
    for old, new in [
        ("R$ 1.232", "R$ 1.250"),
        ("R$ 992", "R$ 1.007"),
        ("R$ 598", "R$ 607"),
        ("R$ 1.815", "R$ 1.841"),
        ("R$ 1.374", "R$ 1.394"),
        ("R$ 1.641", "R$ 1.665"),
    ]:
        html = html.replace(old, new)

    # Financial totals
    html = html.replace("11.257", "11.423")
    html = html.replace("1.908 €", "1.937 €")
    html = html.replace("13.163,70 R$", "12.997,70 R$")
    html = html.replace("~2.231 €", "~2.203 €")
    html = html.replace("−11.423 R$", "−11.423 R$")  # noop after first replace

    # Align envelope narrative in cambio sobra note
    html = html.replace(
        "≈ <strong>2.203 €</strong> (÷ 5,90; comida, metro, Uber, compras…)",
        "≈ <strong>~2.203 €</strong> (÷ 5,90; comida, metro, Uber, compras…) — alinhado ao envelope operacional <strong>€2.000</strong> de bolso (margem ~€200 para taxa real Wise)",
    )

    # Simplify cambio transport card
    html = re.sub(
        r'<div class="card" style="margin-top:1rem;">\s*<h3>Transporte intercidades — valores Omio \(R\$\)</h3>.*?</div>\s*(?=<div class="card" style="margin-top:1rem;">\s*<h3>Quanto sobra)',
        """<div class="card" style="margin-top:1rem;">
        <h3>Transporte intercidades — valores Omio (R$)</h3>
        <p style="margin-top:0;margin-bottom:0;">Terrestre+ICE <strong>R$ 708,99</strong> + voos UE <strong>R$ 1.570,11</strong> = <strong>R$ 2.279,10</strong>. Horários e estações: <a href="#horarios-bilhetes">Horários Omio</a> (fonte única).</p>
      </div>

      """,
        html,
        flags=re.DOTALL,
    )

    # city-bru
    html = html.replace(
        "<p><strong>Estação:</strong> <strong>Rogier</strong> / <strong>Bruxelles-Nord</strong> (compras Rue Neuve, comboios Gent); <strong>Central</strong> e comboio <strong>BRU ↔ centro</strong> como alternativa.</p>",
        "<p><strong>Estação:</strong> <strong>Rogier</strong> / <strong>Bruxelles-Nord</strong> (hotel des Colonies); comboios <strong>Brugge</strong> e <strong>BRU airport</strong> via SNCB.</p>",
    )
    html = html.replace(
        "<p><strong>Foco:</strong> Grand Place, Sainte-Catherine; opcional Gent num dia com regresso cedo.</p>",
        "<p><strong>Foco:</strong> <strong>5 dez</strong> chegada + Grand Place; <strong>6 dez</strong> bate-volta <strong>Bruges</strong> com prima Iza.</p>",
    )

    # operacional table row 6 dez
    html = html.replace(
        '<tr><td>6 dez</td><td>Bruxelas</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>90</td><td>Tax Free prep · Saint-Jacques</td><td><a href="#day-2026-12-06">#</a></td></tr>',
        '<tr class="row-highlight"><td><strong>6 dez</strong></td><td>Bruges (bate-volta)</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>75</td><td>Prima Iza · regresso ~20h</td><td><a href="#day-2026-12-06">#</a></td></tr>',
    )

    # indice-dias row
    html = html.replace(
        '<tr><td>6 dez</td><td>Bruxelas</td><td><span class="dt dt-base">Base</span></td><td><a href="#day-2026-12-06">#</a></td></tr>',
        '<tr><td>6 dez</td><td>Bruges (bate-volta)</td><td><span class="dt dt-icon">Ícone</span></td><td><a href="#day-2026-12-06">#</a></td></tr>',
    )

    # Replace day 2026-12-06 block
    html = re.sub(
        r'<details class="day" id="day-2026-12-06"[^>]*>.*?</details>\s*(?=<details class="day" id="day-2026-12-07")',
        DAY_BRUGES + "\n\n      ",
        html,
        flags=re.DOTALL,
    )

    # indice-dias: add pointer to operacional table, remove duplicate if we keep legend only
    html = html.replace(
        '<div class="card day-index-card" id="indice-dias">\n        <h3>Legenda: tipos de dia</h3>',
        '<div class="card day-index-card" id="indice-dias">\n        <h3>Legenda · tipos de dia</h3>\n        <p class="note" style="margin-top:0;">Tabela de orçamento/energia por data: <a href="#operacional-tabela-dias">Plano operacional</a>. Índice rápido abaixo.</p>',
    )

    # aria-controls remove mais-hub
    html = html.replace(
        'aria-controls="mais-hub horarios-bilhetes voos hoteis emergencia cambio compras checklist"',
        'aria-controls="horarios-bilhetes voos hoteis emergencia cambio compras checklist"',
    )

    # MAP_CITIES bru - update poi for Bruges if present in inline script
    html = html.replace(
        "opcional Gent num dia",
        "bate-volta Bruges (6 dez)",
    )
    html = html.replace(
        "Gent (opcional",
        "Bruges (6 dez",
    )

    INDEX.write_text(html, encoding="utf-8")
    print("OK: index.html updated")


if __name__ == "__main__":
    main()
