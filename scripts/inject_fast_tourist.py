#!/usr/bin/env python3
"""Inject FAST TOURIST hour-by-hour blocks into #dias and strip duplicate slots."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

ENERGY_CLASS = {
    "leve": "oper-energy--low",
    "média": "oper-energy--mid",
    "media": "oper-energy--mid",
    "plena": "oper-energy--high",
    "máxima": "oper-energy--max",
    "maxima": "oper-energy--max",
    "mínima": "oper-energy--low",
    "minima": "oper-energy--low",
}


def fp_block(day_id, budget, energy, rows, *, mode="", cut="", night="", critical="", rain=""):
    ec = ENERGY_CLASS.get(energy.lower(), "oper-energy--mid")
    extra = []
    if mode:
        extra.append(f'<span class="fast-plan__mode">{mode}</span>')
    meta = f"""<div class="fast-plan__meta" aria-label="Meta do dia">
      <span class="fast-plan__badge fast-plan__badge--budget">Teto <strong>€{budget}</strong></span>
      <span class="fast-plan__badge fast-plan__badge--energy"><span class="oper-energy {ec}">{energy}</span></span>
      <span class="fast-plan__badge fast-plan__badge--style">FAST · exterior · 09:00–21:00</span>
      {''.join(extra)}
    </div>"""
    trs = "\n".join(
        f'              <tr><td class="fast-plan__when">{when}</td><td>{plan}</td></tr>'
        for when, plan in rows
    )
    foot = []
    if cut:
        foot.append(f'<p class="fast-plan__foot"><strong>Cortar se atrasar:</strong> {cut}</p>')
    if night:
        foot.append(f'<p class="fast-plan__foot"><strong>Noite:</strong> {night}</p>')
    if critical:
        foot.append(f'<p class="fast-plan__foot fast-plan__foot--warn"><strong>Crítico:</strong> {critical}</p>')
    if rain:
        foot.append(f'<p class="fast-plan__foot"><strong>Plano B chuva:</strong> {rain}</p>')
    return f"""          <div class="fast-plan" id="fast-{day_id}" data-budget-eur="{budget}" data-energy="{energy}">
{meta}
            <div class="table-scroll fast-plan__table-wrap">
              <table class="data fast-plan-table">
                <thead><tr><th>Horário</th><th>Plano executável</th></tr></thead>
                <tbody>
{trs}
                </tbody>
              </table>
            </div>
{chr(10).join(foot)}
          </div>
"""


PLANS = {
    "day-2026-11-19": dict(
        budget=70,
        energy="leve",
        mode="Chegada ~11h30 · sem saída 09:00",
        rows=[
            ("11:30–14:00", "MUC → <strong>S8/S1 → Hbf</strong> (~40 min) → hotel check-in / bagagem"),
            ("14:00–17:00", "<strong>Marienplatz</strong> → <strong>Neues Rathaus</strong> (fachada) → <strong>Frauenkirche</strong> (exterior) → <strong>Viktualienmarkt</strong> (snack)"),
            ("17:00–21:00", "Pé <strong>Karlsplatz</strong> ou volta hotel · jantar <strong>REWE/McDonald’s Hbf</strong> · <strong>dormir cedo</strong> (jet lag)"),
        ],
        cut="Karlsplatz",
        night="Evitar — jet lag",
        rain="Marienplatz arcadas + Hbf",
    ),
    "day-2026-11-20": dict(
        budget=110,
        energy="plena",
        mode="Janela compras",
        rows=[
            ("09:00–12:00", "<strong>Hofgarten</strong> → <strong>Odeonsplatz</strong> → <strong>Ludwigstraße</strong> / Siegestor (foto)"),
            ("12:00–17:00", "<strong>Englischer Garten</strong> (Eisbach, Chinesischer Turm) → margem <strong>Isar</strong> · almoço padaria/quiosque"),
            ("17:00–21:00", "Compras leves <strong>Kaufingerstraße</strong> · jantar rápido · <strong>mala Füssen amanhã</strong>"),
        ],
        cut="Isar",
        night="<a href=\"#explorar-muc\">Glockenbach</a> — WomBAR → Glockenbach",
    ),
    "day-2026-11-21": dict(
        budget=85,
        energy="máxima",
        mode="Sem noite · Füssen",
        rows=[
            ("07:45", "Saída hotel → <strong>ZOB</strong>"),
            ("08:30–10:30", "Flix <strong>ZOB → Füssen Pulverturm</strong>"),
            ("10:30–17:00", "Pé/shuttle <strong>Hohenschwangau</strong> → <strong>Neuschwanstein</strong> (exterior + <strong>Marienbrücke</strong>) → <strong>Alpsee</strong> (opcional) · lanche to-go"),
            ("17:25–19:25", "Flix volta → ZOB → S-Bahn hotel"),
            ("19:30–21:00", "Jantar leve · <strong>mala Salzburgo</strong>"),
        ],
        cut="Alpsee",
        critical="Bilhete castelo com horário · sair ZOB <strong>07:45</strong>",
        rain="Vista castelo de baixo + Füssen centro",
    ),
    "day-2026-11-22": dict(
        budget=55,
        energy="média",
        rows=[
            ("09:00–12:00", "Check-out / bagagem · máx 1h centro se faltar (<strong>Marienplatz</strong>) · <strong>11:00 → ZOB</strong>"),
            ("13:45–15:45", "Flix <strong>ZOB → Salzburg P+R Süd</strong>"),
            ("16:00–21:00", "Ônibus/táxi → hotel → <strong>Mirabellgarten</strong> → <strong>Getreidegasse/Altstadt</strong> → <strong>Dom</strong> (exterior)"),
        ],
        cut="Mirabell se Flix atrasar",
        night="Leve — transferência",
    ),
    "day-2026-11-23": dict(
        budget=75,
        energy="plena",
        rows=[
            ("09:00–12:00", "<strong>Festung Hohensalzburg</strong> (vistas exterior) → <strong>Dom</strong> / Residenzplatz"),
            ("12:00–17:00", "Loop <strong>Altstadt</strong>: Getreidegasse, Mozartplatz, <strong>Salzach</strong> / Makartsteg"),
            ("17:00–21:00", "Jantar barato · <strong>mala + dormir cedo</strong> (ICE <strong>10:00</strong> amanhã)"),
        ],
        cut="Makartsteg",
        night="<a href=\"#explorar-szg\">YoHo bar</a> (4 min do hotel)",
    ),
    "day-2026-11-24": dict(
        budget=95,
        energy="média",
        rows=[
            ("09:00–09:45", "Café to-go · check-out · <strong>Salzburg Hbf</strong>"),
            ("10:00–12:47", "<strong>ÖBB ICE → Wien Hbf</strong> (tarifa fixa — não perder)"),
            ("13:00–17:00", "Hotel Zipser · <strong>Prater</strong> (exterior) → <strong>Naschmarkt</strong> (snack)"),
            ("17:00–21:00", "<strong>Donaukanal</strong> · jantar <strong>Billa</strong> · compras leves (<a href=\"#compras-matriz-dia\">matriz 24 nov</a>)"),
        ],
        cut="Prater",
        night="<a href=\"#explorar-vie\">WomBAR Naschmarkt</a> + Donaukanal",
    ),
    "day-2026-11-25": dict(
        budget=95,
        energy="plena",
        mode="Compras",
        rows=[
            ("09:00–12:00", "<strong>Schönbrunn</strong> (fachada + jardins, exterior)"),
            ("12:00–17:00", "<strong>Stadtpark</strong> → <strong>Stephansdom</strong> (exterior) → <strong>Graben</strong> → <strong>Hofburg</strong> (pátios exterior)"),
            ("17:00–21:00", "<strong>Rathaus + Parlament</strong> (exterior, luzes) · jantar rápido · mala Bratislava"),
        ],
        cut="Hofburg",
        night="Ring / Donaukanal se faltou dia 6",
    ),
    "day-2026-11-26": dict(
        budget=35,
        energy="leve",
        rows=[
            ("09:00–12:00", "Manhã livre <strong>Josefstadt</strong> · check-out <strong>11:00</strong> · <strong>VIB 12:00</strong>"),
            ("12:35–13:45", "Flix <strong>VIB → Most SNP</strong>"),
            ("14:00–21:00", "Hotel → <strong>Staré Mesto</strong> → <strong>Bratislava Castle</strong> (exterior) · jantar Old Town"),
        ],
        cut="Castle (só Old Town)",
        night="<a href=\"#explorar-bts\">Wild Elephants</a> + Obchodná",
    ),
    "day-2026-11-27": dict(
        budget=50,
        energy="média",
        rows=[
            ("08:30–10:20", "Check-out · <strong>Mlynské Nivy</strong>"),
            ("10:50–13:25", "Flix → <strong>Budapest Kelenföld</strong>"),
            ("14:00–17:00", "Metro → hotel → <strong>Basílica</strong> (exterior) → <strong>Andrássy</strong> (exterior)"),
            ("17:00–21:00", "<strong>Chain Bridge</strong> → vistas <strong>Buda Castle</strong> (Pest, exterior)"),
        ],
        cut="Andrássy",
    ),
    "day-2026-11-28": dict(
        budget=95,
        energy="plena",
        mode="Sábado ruin bars",
        rows=[
            ("09:00–12:00", "<strong>Parlamento</strong> (exterior) → <strong>Shoes on the Danube</strong>"),
            ("12:00–17:00", "<strong>Great Market Hall</strong> (snack) → <strong>Fisherman's Bastion</strong> + <strong>Matthias</strong> (exterior)"),
            ("17:00–21:00", "Buffer · compras moderadas · <strong>noite: Szimpla / Instant</strong>"),
        ],
        cut="Bastion (manter Parlamento + ruin bar)",
        rain="Váci utca comercial",
    ),
    "day-2026-11-29": dict(
        budget=75,
        energy="média",
        mode="Voo amanhã 15:40",
        rows=[
            ("09:00–12:00", "Completar pendências OU <strong>Jewish Quarter</strong> (exterior)"),
            ("12:00–17:00", "<strong>Margaret Bridge</strong> / <strong>Margitsziget</strong> (exterior) · buffer descanso"),
            ("17:00–21:00", "Jantar leve · <strong>mala Berlim</strong> · dormir razoável"),
        ],
        night="Moderada — WomBAR ou ruin bar leve",
        critical="Sem banho térmico longo",
    ),
    "day-2026-11-30": dict(
        budget=40,
        energy="leve",
        mode="Ryanair 15:40",
        rows=[
            ("09:00–12:00", "Check-out · café · último ponto perto hotel (10 min Basílica)"),
            ("~12:30", "<strong>BUD aeroporto</strong> (Ryanair + bagagem)"),
            ("15:40–17:10", "Voo <strong>BUD → BER</strong>"),
            ("18:00–21:00", "Check-in Premier Inn → <strong>Alexanderplatz</strong> + <strong>Fernsehturm</strong> (exterior) · jantar Rewe"),
        ],
        critical="Zero programa pesado de manhã",
    ),
    "day-2026-12-01": dict(
        budget=110,
        energy="plena",
        rows=[
            ("09:00–12:00", "<strong>Brandenburg Gate</strong> → <strong>Reichstag</strong> (exterior) → <strong>Tiergarten</strong>"),
            ("12:00–17:00", "<strong>Holocaust Memorial</strong> → <strong>Potsdamer Platz</strong> → <strong>East Side Gallery</strong> (trecho)"),
            ("17:00–21:00", "Volta Alex · jantar rápido"),
        ],
        cut="Metade East Side",
        night="<a href=\"#explorar-ber\">Generator</a> (pub crawl 21h) ou Kreuzberg",
    ),
    "day-2026-12-02": dict(
        budget=120,
        energy="plena",
        mode="Compras hub",
        rows=[
            ("09:00–12:00", "<strong>Unter den Linden</strong> → <strong>Berliner Dom</strong> (exterior) → <strong>Lustgarten</strong>"),
            ("12:00–17:00", "<strong>Museum Island</strong> (só fachadas) → <strong>Gendarmenmarkt</strong> → compras <strong>Alex / Ku’damm / Primark</strong>"),
            ("17:00–21:00", "Mercados de Natal · jantar · <strong>mala Praga</strong>"),
        ],
        cut="Gendarmenmarkt",
        critical="Dia de maior gasto em compras",
    ),
    "day-2026-12-03": dict(
        budget=50,
        energy="média",
        rows=[
            ("08:00–08:45", "Check-out · S-Bahn <strong>Alex → Südkreuz</strong>"),
            ("10:20–14:20", "Flix <strong>Südkreuz → Florenc</strong>"),
            ("14:30–21:00", "Hotel Alton → <strong>Wenceslas Square</strong> → <strong>Old Town Square</strong> + <strong>Relógio</strong> (exterior)"),
        ],
        cut="Wenceslas",
        critical="Hotel <strong>08:45</strong> · Flix <strong>10:20</strong>",
    ),
    "day-2026-12-04": dict(
        budget=130,
        energy="plena",
        mode="Compras + noite CZ",
        rows=[
            ("09:00–12:00", "<strong>Charles Bridge</strong> (cedo) → subida <strong>Malá Strana</strong>"),
            ("12:00–17:00", "<strong>Prague Castle</strong> (exterior + pátios) → <strong>Kampa</strong> · compras <strong>Na Příkopě / Palladium</strong>"),
            ("17:00–21:00", "Old Town revisit · <strong>noite: <a href=\"#explorar-prg\">Czech Inn</a> + Vinohrady</strong>"),
        ],
        cut="Kampa",
    ),
    "day-2026-12-05": dict(
        budget=60,
        energy="leve",
        mode="Smartwings 17:15",
        rows=[
            ("09:00–12:00", "Check-out · último passeio pé (<strong>Charles Bridge</strong>) ou compra rápida"),
            ("~14:00", "<strong>PRG aeroporto</strong> (Smartwings Plus + bagagem)"),
            ("17:15–18:45", "Voo → <strong>BRU Zaventem</strong>"),
            ("19:30–21:00", "Trem aeroporto → hotel <strong>Rogier</strong> · jantar perto hotel"),
        ],
        critical="PRG <strong>~14:00</strong>",
    ),
    "day-2026-12-06": dict(
        budget=75,
        energy="média",
        mode="Descanso + prep voo",
        rows=[
            ("10:00–13:00", "<strong>Grand Place</strong> + <strong>Galeries Saint-Hubert</strong> (exterior)"),
            ("13:00–15:00", "Almoço (Chez Léon / Exki) · <strong>Mont des Arts</strong> (opcional)"),
            ("15:00–17:00", "<strong>Compras buffer</strong> Rue Neuve / Apple · Tax Free prep"),
            ("17:00–21:00", "Mala 100% · jantar leve · <strong>dormir cedo</strong>"),
        ],
        cut="Parc Cinquantenaire",
        night="Descanso — sem noite pesada (voo 07h)",
        critical="Alarme <strong>03:00</strong> · Bolt ~03:30",
    ),
    "day-2026-12-07": dict(
        budget=20,
        energy="mínima",
        mode="Sem turismo urbano",
        rows=[
            ("04:30–05:00", "Táxi hotel → <strong>BRU Zaventem</strong>"),
            ("07:00", "Voo <strong>BRU → MAD → GRU</strong>"),
            ("No aeroporto", "<strong>Tax Free</strong> + café"),
        ],
        critical="Embarque <strong>07:00</strong> — chegar 2h antes",
    ),
}


def render_plan(day_id, spec):
    return fp_block(day_id, spec["budget"], spec["energy"], spec["rows"], **{k: spec.get(k, "") for k in ("mode", "cut", "night", "critical", "rain")})


def strip_redundant(body: str) -> str:
    body = re.sub(r'\s*<div class="day-timeline-wrap">.*?</div>\s*(?=<div class="slot"|<div class="fast-plan"|<div class="flight|<div class="transit"|<div class="shop-day"|<p class="note")', "\n", body, flags=re.DOTALL)
    body = re.sub(r'\s*<div class="slot">.*?</div>\s*(?=<div class="slot"|<div class="fast-plan"|<div class="flight|<div class="transit"|<div class="shop-day"|<p class="note")', "\n", body, flags=re.DOTALL)
    return body


def inject_day(html: str, day_id: str, plan_html: str) -> str:
    pattern = rf'(<details class="day" id="{re.escape(day_id)}"[^>]*>\s*<summary>.*?</summary>\s*<div class="body">)(.*?)(</div>\s*</details>)'
    m = re.search(pattern, html, flags=re.DOTALL)
    if not m:
        print(f"WARN: {day_id} not found")
        return html
    body = m.group(2)
    body = re.sub(r'\s*<div class="fast-plan"[^>]*>.*?</div>\s*', "\n", body, flags=re.DOTALL)
    body = strip_redundant(body)
    # keep flight-day-checklist, shop-day, transit, note, explorar-night
    new_body = "\n" + plan_html + "\n" + body.lstrip()
    return html[: m.start(2)] + new_body + html[m.end(2) :]


def fix_day06_nesting(html: str) -> str:
    return re.sub(
        r'\n\s+<details class="day" id="day-2026-12-06"',
        '\n      <details class="day" id="day-2026-12-06"',
        html,
        count=1,
    )


def add_data_attrs(html: str) -> str:
    for day_id, spec in PLANS.items():
        html = re.sub(
            rf'(<details class="day" id="{re.escape(day_id)}"[^>]*)(>)',
            rf'\1 data-budget-eur="{spec["budget"]}" data-energy="{spec["energy"]}"\2',
            html,
            count=1,
        )
    return html


def main():
    html = INDEX.read_text(encoding="utf-8")
    for day_id, spec in PLANS.items():
        html = inject_day(html, day_id, render_plan(day_id, spec))
    html = fix_day06_nesting(html)
    html = add_data_attrs(html)
    # lede dias
    html = html.replace(
        '<p class="lede">Cada dia abre ao clicar.',
        '<p class="lede"><strong>FAST TOURIST:</strong> cada dia tem tabela <strong>09:00–21:00</strong> (exterior-only) com teto € e energia. Cada dia abre ao clicar.',
        1,
    )
    INDEX.write_text(html, encoding="utf-8")
    print(f"OK: injected {len(PLANS)} fast-plan blocks")


if __name__ == "__main__":
    main()
