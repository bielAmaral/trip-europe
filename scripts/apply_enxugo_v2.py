#!/usr/bin/env python3
"""Enxugo v2: remove duplicações, atualiza voos 5/7 dez, consolida checklists."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

VOOS_CHECKLISTS = """
      <details class="card" id="voos-checklist-curto" style="margin-top:1rem;">
        <summary>Checklist · voo curto (Ryanair / Schengen)</summary>
        <ul>
          <li>Passaporte + <strong>boarding offline</strong> (app/PDF); <strong>terminal</strong> no bilhete</li>
          <li>Bagagem conforme Omio (carry-on + despacho — confira pesos)</li>
          <li>Bateria + powerbank; último bilhete urbano validado antes do aeroporto</li>
          <li>Chegar <strong>~2h antes</strong> da partida; trânsito até o aeroporto com folga</li>
          <li>Após pouso: rota até hotel no app da cidade (BVG, PID, SNCB/STIB…)</li>
        </ul>
      </details>
      <details class="card" id="voos-checklist-intercontinental">
        <summary>Checklist · regresso intercontinental (7 dez · BRU)</summary>
        <ul>
          <li><strong>Alarme 03:00</strong>; sair hotel <strong>~03:45</strong> (Bolt/táxi madrugada)</li>
          <li><strong>IB0604 07:00</strong>: meta <strong>05:00</strong> no aeroporto (2h antes)</li>
          <li>Passaporte, boarding Iberia offline, <strong>seguro</strong> — <a href="#emergencia">Emergência</a></li>
          <li>Na noite de <strong>6 dez</strong>: Bolt agendado · mala pronta · greves/obras SNCB</li>
        </ul>
      </details>
"""

DAY5_FAST = """      <details class="day" id="day-2026-12-05" data-trip-date="2026-12-05" data-budget-eur="60" data-energy="leve">
        <summary><span class="date-tag">5 dez · sáb</span> <span class="city">Praga → Bruxelas (Ryanair PRG→BRU)</span><span class="day-badges" aria-label="Tipos de dia"><span class="dt dt-flight">Aéreo</span><span class="dt dt-transfer">Transferência</span><span class="dt dt-shop">Compras</span></span></summary>
        <div class="body">
          <div class="fast-plan" id="fast-day-2026-12-05" data-budget-eur="60" data-energy="leve">
<div class="fast-plan__meta" aria-label="Meta do dia">
      <span class="fast-plan__badge fast-plan__badge--budget">Teto <strong>€60</strong></span>
      <span class="fast-plan__badge fast-plan__badge--energy"><span class="oper-energy oper-energy--low">leve</span></span>
      <span class="fast-plan__badge fast-plan__badge--style">FAST · voo manhã</span>
      <span class="fast-plan__mode">Ryanair 11:50</span>
    </div>
            <div class="table-scroll fast-plan__table-wrap">
              <table class="data fast-plan-table">
                <thead><tr><th>Horário</th><th>Plano executável</th></tr></thead>
                <tbody>
              <tr><td class="fast-plan__when">06:30–07:30</td><td>Acordar · check-out <strong>Alton</strong></td></tr>
              <tr><td class="fast-plan__when">07:30–08:35</td><td>Metro + autocarro <strong>119</strong> → <strong>PRG</strong></td></tr>
              <tr><td class="fast-plan__when">08:35–11:20</td><td>Check-in Ryanair · segurança (chegar <strong>~09:30</strong>)</td></tr>
              <tr><td class="fast-plan__when">11:50–13:20</td><td>Voo → <strong>BRU Zaventem</strong></td></tr>
              <tr><td class="fast-plan__when">14:00–15:00</td><td>SNCB + STIB → <strong>Rogier</strong> · check-in hotel</td></tr>
              <tr><td class="fast-plan__when">15:00–18:30</td><td><strong>Grand Place</strong> · <strong>Rue Neuve</strong> · <a href="#compras-matriz-dia">compras</a></td></tr>
              <tr><td class="fast-plan__when">18:30–21:00</td><td>Jantar · descanso (Bruges amanhã)</td></tr>
                </tbody>
              </table>
            </div>
<p class="fast-plan__foot fast-plan__foot--warn"><strong>Crítico:</strong> PRG <strong>~09:30</strong> — voo <strong>11:50</strong></p>
          </div>
<p class="note flight-day-checklist-ref">Checklist: <a href="#voos-checklist-curto">voo curto</a> · horários em <a href="#horarios-bilhetes">Omio</a>.</p>
<details class="transit-collapse">
            <summary>Praga → aeroporto · voo · BRU → centro</summary>
            <div class="transit transit--nested">
<ul>
              <li><strong>Alton → PRG:</strong> metro <strong>C/A</strong> → <strong>Veleslavín</strong> + autocarro <strong>119</strong> (alt. AE via hl.n.).</li>
              <li><strong>PRG → BRU:</strong> Ryanair <strong>11:50–13:20</strong> (Omio <strong>R$ 835,77</strong>).</li>
              <li><strong>BRU → Rogier:</strong> comboio <strong>SNCB</strong> + <strong>STIB</strong> <em>ou</em> Bolt.</li>
            </ul>
            </div>
          </details>
        </div>
      </details>"""


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")

    # Cursor morto no PWA
    html = re.sub(
        r'\s*<div id="cursorRoot" class="cursor-root" aria-hidden="true">\s*'
        r'<div class="cursor-dot"></div>\s*<div class="cursor-ring"></div>\s*</div>\s*',
        "\n",
        html,
    )

    # Índice dias: só legenda + link operacional
    html = re.sub(
        r'(<div class="card day-index-card" id="indice-dias">.*?<p class="note" style="margin-top:0;">).*?(</p>\s*)<div class="table-scroll">.*?</div>\s*</div>',
        r'\1 Na app, use a <strong>lista de dias</strong> acima. Orçamento e energia: <a href="#operacional-tabela-dias">Plano operacional</a>. Tipos de dia: legenda abaixo em <a href="#dias">#dias</a>.\2</div>',
        html,
        count=1,
        flags=re.DOTALL,
    )

    # shop-day redundante (noite já no fast-plan__foot e calendário)
    html = re.sub(
        r'\s*<div class="shop-day shop-day--compact explorar-night">.*?</div>\s*',
        "\n",
        html,
        flags=re.DOTALL,
    )

    # Checklists de voo nos dias → link
    html = re.sub(
        r'<div class="flight-day-checklist">.*?</div>\s*',
        '<p class="note flight-day-checklist-ref">Checklist: <a href="#voos-checklist-curto">voo curto</a> · <a href="#voos-checklist-intercontinental">intercontinental (7 dez)</a>.</p>\n',
        html,
        flags=re.DOTALL,
    )
    # Dia 7: só link intercontinental
    html = html.replace(
        '<p class="note flight-day-checklist-ref">Checklist: <a href="#voos-checklist-curto">voo curto</a> · <a href="#voos-checklist-intercontinental">intercontinental (7 dez)</a>.</p>',
        '<p class="note flight-day-checklist-ref">Checklist: <a href="#voos-checklist-intercontinental">embarque 7 dez</a>.</p>',
        1,  # only first after day 7 - actually all got same text. Fix day 7 separately below
    )
    # Restore BUD/PRG days to curto-only link (first two occurrences before day 7)
    html = html.replace(
        '<p class="note flight-day-checklist-ref">Checklist: <a href="#voos-checklist-intercontinental">embarque 7 dez</a>.</p>',
        '<p class="note flight-day-checklist-ref">Checklist: <a href="#voos-checklist-curto">voo curto</a> · <a href="#horarios-bilhetes">Horários Omio</a>.</p>',
        2,
    )

    # Voos curtos: tabela resumida + checklists
    html = re.sub(
        r'<h3>Voos curtos na Europa \(reserva separada\)</h3>.*?<p class="note">Berlim–Praga',
        """<h3>Voos curtos na Europa (reserva separada)</h3>
      <p class="lede">Detalhes, bagagem e horários exatos: <a href="#horarios-bilhetes"><strong>Horários Omio</strong></a> (fonte única).</p>
      <div class="table-scroll">
      <table class="data">
        <thead>
          <tr><th>Trecho</th><th>Data · partida</th><th>R$ Omio</th></tr>
        </thead>
        <tbody>
          <tr><td>BUD → BER (Ryanair)</td><td><strong>30 nov · 15:40</strong></td><td><strong>734,34</strong></td></tr>
          <tr><td>PRG → BRU (Ryanair)</td><td><strong>5 dez · 11:50</strong></td><td><strong>835,77</strong></td></tr>
        </tbody>
      </table>
      </div>
""" + VOOS_CHECKLISTS + """
      <p class="note">Berlim–Praga""",
        html,
        count=1,
        flags=re.DOTALL,
    )

    # Horários Omio — 5 dez Ryanair
    html = html.replace(
        '<tr><td><strong>5 dez</strong></td><td>PRG → BRU</td><td><strong>17:15</strong>→<strong>18:45</strong> (1h30)</td><td>Smartwings <strong>Plus</strong></td><td>Total Omio <strong>R$ 835,77</strong> (base + upgrade Plus: item pessoal, cabine 8 kg, despacho 23 kg, escolha de lugar — confira regras no bilhete). Chegada em <strong>Zaventem</strong>: ligação ao centro/hotel mais simples que via CRL.</td></tr>',
        '<tr><td><strong>5 dez</strong></td><td>PRG → BRU</td><td><strong>11:50</strong>→<strong>13:20</strong> (1h30)</td><td>Ryanair + bagagens</td><td><strong>R$ 835,77</strong> Omio. Chegada <strong>Zaventem</strong> — tarde livre em Bruxelas.</td></tr>',
    )

    # Resumo voos curtos
    html = html.replace(
        "· <strong>PRG → BRU</strong> <strong>5 dez 17h15–18h45</strong> (Smartwings <strong>Plus</strong> no Omio, total <strong>R$ 835,77</strong> = base + upgrade)",
        "· <strong>PRG → BRU</strong> <strong>5 dez 11h50–13h20</strong> (Ryanair + bagagens, <strong>R$ 835,77</strong> Omio)",
    )

    # Iberia 7 dez nota
    html = html.replace(
        "<td>Sair do hotel ~04h30–05h00 para BRU.</td>",
        "<td>Alarme <strong>03:00</strong> · sair hotel ~<strong>03:45</strong> para BRU.</td>",
    )

    # Operacional 5 dez
    html = html.replace(
        "<td>Smartwings 17h15</td>",
        "<td>Ryanair 11h50</td>",
    )

    # Praga cidade
    html = html.replace(
        "Bruxelas (voo <strong>PRG → BRU</strong> Smartwings).",
        "Bruxelas (voo <strong>PRG → BRU</strong> Ryanair <strong>11:50</strong>).",
    )

    # Calendário noite 5 dez
    html = html.replace(
        "<td>Leve se chegar cedo</td><td>Voo PRG→BRU 17h15</td>",
        "<td>Tarde Rue Neuve</td><td>Chegada 13h20</td>",
    )

    # Alarme 6 dez
    html = html.replace(
        "<strong>Crítico:</strong> Regresso ~20h · alarme <strong>04:15</strong>",
        "<strong>Crítico:</strong> Regresso ~20h · alarme <strong>03:00</strong>",
    )

    # Dia 7 fast-plan
    html = html.replace(
        "<tr><td class=\"fast-plan__when\">04:30–05:00</td><td>Táxi hotel → <strong>BRU Zaventem</strong></td></tr>",
        "<tr><td class=\"fast-plan__when\">03:00</td><td><strong>Alarme</strong></td></tr>\n              <tr><td class=\"fast-plan__when\">03:30–04:30</td><td>Bolt/táxi hotel → <strong>BRU Zaventem</strong></td></tr>\n              <tr><td class=\"fast-plan__when\">05:00–07:00</td><td>Check-in Iberia · <strong>Tax Free</strong></td></tr>",
    )
    html = html.replace(
        "<tr><td class=\"fast-plan__when\">No aeroporto</td><td><strong>Tax Free</strong> + café</td></tr>\n",
        "",
    )

    # Substituir bloco dia 5 dez inteiro
    html = re.sub(
        r'<details class="day" id="day-2026-12-05".*?</details>\s*(?=<details class="day" id="day-2026-12-06")',
        DAY5_FAST + "\n      ",
        html,
        count=1,
        flags=re.DOTALL,
    )

    # Cidades: nota obsoleta
    html = html.replace(
        '<p class="note" style="margin-top:0.35rem;">O “mapa dia a dia” dentro de cada cidade é um <strong>resumo em tópicos</strong>; não substitui os detalhes dos <code>details</code> por data em <a href="#dias">#dias</a>.</p>\n\n',
        "",
    )
    html = html.replace(
        "O mapa resumido por dia encaixa-se abaixo em cada ficha.",
        "Use o mapa interativo e o roteiro por data em <a href=\"#dias\">#dias</a>.",
    )

    # Compras lede
    html = html.replace(
        "Nos dias com compras, o <a href=\"#dias\">roteiro dia a dia</a> tem um <strong>bloco compacto</strong> com atalho para esta secção — confira",
        "Nos dias com compras, veja a coluna <strong>Dia no roteiro</strong> abaixo e o plano hora a hora em <a href=\"#dias\">#dias</a> — confira",
    )

    # Checklist final
    html = html.replace(
        "e <strong>PRG → BRU</strong> Smartwings <strong>5 dez 17:15–18:45</strong>",
        "e <strong>PRG → BRU</strong> Ryanair <strong>5 dez 11:50–13:20</strong>",
    )

    # TOC indice-dias label
    html = html.replace(
        '<li><a href="#indice-dias">Legenda: tipos de dia</a></li>',
        '<li><a href="#operacional-tabela-dias">Orçamento por dia</a></li>',
    )

    INDEX.write_text(html, encoding="utf-8")
    print(f"OK: {INDEX.name} enxugado")


if __name__ == "__main__":
    main()
