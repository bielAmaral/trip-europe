"""Extract Mindtrip document from index.html (ASCII-safe)."""
from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

TRANS = str.maketrans({
    "\u00fc": "ue", "\u00f6": "oe", "\u00e4": "ae", "\u00df": "ss",
    "\u00dc": "Ue", "\u00d6": "Oe", "\u00c4": "Ae",
    "\u00e9": "e", "\u00e8": "e", "\u00ea": "e", "\u00e1": "a", "\u00e0": "a",
    "\u00fa": "u", "\u00f3": "o", "\u00ed": "i", "\u00f1": "n", "\u00e7": "c",
    "\u0159": "r", "\u010d": "c", "\u011b": "e", "\u016f": "u", "\u017e": "z",
    "\u0161": "s", "\u00fd": "y", "\u0151": "o", "\u0171": "u",
    "\u2192": "->", "\u2190": "<-", "\u00b7": " · ", "\u20ac": "EUR ",
    "\u2014": " - ", "\u2013": "-", "\u2026": "...", "\u00b1": "+/-",
    "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
    "\u00a0": " ", "\u00ad": "",
})


def clean(raw: str, keep_urls: bool = True) -> str:
    urls: list[str] = []
    if keep_urls:
        urls = re.findall(r'href="(https?://[^"]+)"', raw)
    raw = re.sub(r"<br\s*/?>", " ", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = html_lib.unescape(raw)
    raw = raw.translate(TRANS)
    raw = re.sub(r"\s+", " ", raw).strip()
    out = "".join(c if ord(c) < 128 else "" for c in raw)
    if urls:
        out += " | " + " | ".join(urls)
    return out


def table_rows(fragment: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", fragment, re.DOTALL | re.I):
        cells = []
        for td in re.finditer(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(1), re.DOTALL | re.I):
            raw = td.group(1)
            cells.append(hrefs(raw) if "guruwalk.com" in raw or "btn-maps" in raw else clean(raw))
        if cells:
            rows.append(cells)
    return rows


def hrefs(raw: str) -> str:
    urls = re.findall(r'href="(https?://[^"]+)"', raw)
    text = clean(raw, keep_urls=False)
    if urls:
        text += " | " + " | ".join(urls)
    return text


def md_table(rows: list[list[str]], header: bool = True) -> str:
    if not rows:
        return "_No data_"
    lines: list[str] = []
    body = rows[1:] if header and len(rows) > 1 else rows
    hdr = rows[0] if header else None
    if hdr:
        lines.append("| " + " | ".join(hdr) + " |")
        lines.append("| " + " | ".join("---" for _ in hdr) + " |")
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def table_with_id(html: str, table_id: str) -> list[list[str]]:
    m = re.search(rf'<table[^>]*id="{table_id}"[^>]*>(.*?)</table>', html, re.DOTALL | re.I)
    return table_rows(m.group(0)) if m else []


def table_with_class(html: str, class_name: str, after: str = "") -> list[list[str]]:
    start = html.find(after) if after else 0
    chunk = html[start:]
    m = re.search(rf'<table[^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*"[^>]*>(.*?)</table>', chunk, re.DOTALL | re.I)
    return table_rows(m.group(0)) if m else []


def table_inside_block(html: str, block_id: str) -> list[list[str]]:
    m = re.search(rf'id="{block_id}"[^>]*>(.*?)(?=<div class="explorar-ref-section"|<details |</section>)', html, re.DOTALL | re.I)
    if not m:
        return []
    tm = re.search(r"<table[^>]*>(.*?)</table>", m.group(1), re.DOTALL | re.I)
    return table_rows(tm.group(0)) if tm else []


def section_table(html: str, section_id: str) -> list[list[str]]:
    m = re.search(rf'<section[^>]*id="{section_id}"[^>]*>(.*?)</section>', html, re.DOTALL | re.I)
    if not m:
        return []
    tm = re.search(r"<table[^>]*>(.*?)</table>", m.group(1), re.DOTALL | re.I)
    return table_rows(tm.group(0)) if tm else []


def first_table_after(html: str, marker: str, limit: int = 20000) -> list[list[str]]:
    idx = html.find(marker)
    if idx < 0:
        return []
    chunk = html[idx : idx + limit]
    m = re.search(r"<table[^>]*>(.*?)</table>", chunk, re.DOTALL | re.I)
    if not m:
        return []
    return table_rows(m.group(0))


def extract_list_items(fragment: str) -> list[str]:
    return [clean(li.group(1)) for li in re.finditer(r"<li>(.*?)</li>", fragment, re.DOTALL)]


def _day_chunk(html: str, start: int) -> str:
    rest = html[start + 50 :]
    nxt = re.search(r'<details class="day" id="day-', rest)
    end = start + 50 + nxt.start() if nxt else start + 12000
    return html[start:end]


def extract_days(html: str) -> list[dict]:
    days: list[dict] = []
    for m in re.finditer(
        r'<details class="day" id="day-(\d{4}-\d{2}-\d{2})"[^>]*data-budget-eur="(\d+)"[^>]*data-energy="([^"]+)"',
        html,
    ):
        date, budget, energy = m.group(1), m.group(2), clean(m.group(3), keep_urls=False)
        chunk = _day_chunk(html, m.start())
        sm = re.search(r"<summary>(.*?)</summary>", chunk, re.DOTALL)
        summary = clean(sm.group(1)) if sm else ""
        fp = re.search(r'<div class="fast-plan"[^>]*>(.*?)</div>\s*<details class="transit-collapse">', chunk, re.DOTALL)
        fp_html = fp.group(1) if fp else chunk
        schedule = [
            (clean(w.group(1), keep_urls=False), clean(w.group(2)))
            for w in re.finditer(r'<td class="fast-plan__when">(.*?)</td><td>(.*?)</td>', fp_html, re.DOTALL)
        ]
        feet = [clean(fp.group(1)) for fp in re.finditer(r'<p class="fast-plan__foot[^"]*">(.*?)</p>', fp_html, re.DOTALL)]
        meta = [clean(mb.group(1)) for mb in re.finditer(r'class="fast-plan__badge[^"]*">(.*?)</span>', fp_html, re.DOTALL)]
        mode_m = re.search(r'class="fast-plan__mode">(.*?)</span>', chunk, re.DOTALL)
        mode = clean(mode_m.group(1)) if mode_m else ""
        transit: list[str] = []
        tm = re.search(r"transit-collapse.*?<ul>(.*?)</ul>", chunk, re.DOTALL)
        if tm:
            transit = extract_list_items(tm.group(1))
        warn_m = re.search(r'<span class="warn">(.*?)</span>', chunk, re.DOTALL)
        warn = clean(warn_m.group(1)) if warn_m else ""
        days.append({"date": date, "budget": budget, "energy": energy, "summary": summary,
                     "schedule": schedule, "feet": feet, "meta": meta, "mode": mode,
                     "transit": transit, "warn": warn})
    return days


DEC5_OVERRIDE = {
    "mode": "Ryanair PRG->CRL 12:30 + Flibco to Midi",
    "schedule": [
        ("08:00-08:30", "Albert Legerova 75 - buy lunch kit (2 min from Alton hotel)"),
        ("08:30-09:30", "Check-out Alton - metro C/A to Veleslavin + bus 119 to PRG airport"),
        ("09:30-12:00", "PRG airport - Ryanair check-in (10+23 kg bags per Omio)"),
        ("12:30-14:00", "Flight PRG -> CRL (Charleroi) Ryanair FR69 - PAID R$ 773.64"),
        ("14:30-16:00", "Flibco bus CRL -> Bruxelles-Midi (~1h - buy ahead)"),
        ("16:00-18:00", "Metro 2/6 Midi -> Rogier - Hotel des Colonies check-in"),
        ("18:00-21:00", "Five Guys Rue Neuve 123 (~5 min walk) - meet cousin if planned"),
    ],
    "feet": ["CRITICAL: Flight 12:30 PRG->CRL not BRU.", "CRITICAL: Arrive PRG ~2h before departure"],
}


def apply_overrides(days: list[dict]) -> None:
    for d in days:
        if d["date"] == "2026-12-05":
            d["mode"] = DEC5_OVERRIDE["mode"]
            d["schedule"] = DEC5_OVERRIDE["schedule"]
            d["feet"] = DEC5_OVERRIDE["feet"]


def render_day(d: dict, hotel_hint: str = "") -> list[str]:
    lines = [f"### {d['date']} - {d['summary']}", "",
             f"- **Daily budget cap:** EUR {d['budget']} (1 adult solo, all-in excl. hotel)",
             f"- **Energy level:** {d['energy']}"]
    if d["mode"]:
        lines.append(f"- **Day mode:** {d['mode']}")
    if hotel_hint:
        lines.append(f"- **Hotel:** {hotel_hint}")
    if d["meta"]:
        lines.append(f"- **Tags:** {' | '.join(d['meta'])}")
    lines += ["", "**Schedule (locked):**", "", "| Time | Plan |", "| --- | --- |"]
    for when, plan in d["schedule"]:
        lines.append(f"| {when} | {plan} |")
    lines.append("")
    if d["transit"]:
        lines.append("**Transit / transport detail:**")
        for t in d["transit"]:
            lines.append(f"- {t}")
        if d["warn"]:
            lines.append(f"- WARNING: {d['warn']}")
        lines.append("")
    for foot in d["feet"]:
        lines.append(f"- {foot}")
    lines.append("")
    return lines


HOTELS_BY_DATE = {
    "2026-11-19": "B&B Hotel Muenchen-Hbf (Arnulfstrasse 30) - check-in 19 Nov",
    "2026-11-20": "B&B Hotel Muenchen-Hbf",
    "2026-11-21": "B&B Hotel Muenchen-Hbf (day trip Fussen)",
    "2026-11-22": "B&B -> Atel Hotel Lasserhof Salzburg (check-in 22 Nov)",
    "2026-11-23": "Atel Hotel Lasserhof Salzburg",
    "2026-11-24": "Lasserhof -> Hotel Zipser Vienna (check-in 24 Nov)",
    "2026-11-25": "Hotel Zipser Vienna (Lange Gasse 49)",
    "2026-11-26": "Zipser -> Danubia Gate Bratislava (check-in 26 Nov)",
    "2026-11-27": "Danubia Gate -> Medos Hotel Budapest (check-in 27 Nov)",
    "2026-11-28": "Medos Hotel Budapest",
    "2026-11-29": "Medos Hotel Budapest",
    "2026-11-30": "Medos -> Premier Inn Berlin Alexanderplatz (check-in 30 Nov)",
    "2026-12-01": "Premier Inn Berlin Alexanderplatz",
    "2026-12-02": "Premier Inn Berlin Alexanderplatz",
    "2026-12-03": "Premier Inn -> Alton Prague (check-in 3 Dec)",
    "2026-12-04": "Alton Hotel Prague (Legerova 22)",
    "2026-12-05": "Alton -> Hotel des Colonies Brussels Rogier (check-in 5 Dec)",
    "2026-12-06": "Hotel des Colonies Brussels",
    "2026-12-07": "Hotel des Colonies -> BRU airport 04:30",
}


def build_document(index_path: Path) -> str:
    html = index_path.read_text(encoding="utf-8")
    days = extract_days(html)
    apply_overrides(days)
    lines: list[str] = []
    lines += [
        "# Europe Central Trip 2026 - COMPLETE Mindtrip Master Document", "",
        "## TRAVELER (LOCKED - DO NOT CHANGE)", "",
        "- **1 adult only** - solo traveler, Brazilian passport",
        "- Depart **18 Nov 2026** JFK (KLM) | Return **7 Dec 2026** GRU (Iberia)",
        "- 18 nights: Munich (19-22) -> Salzburg (22-24) -> Vienna (24-26) -> Bratislava (26-27) -> Budapest (27-30) -> Berlin (30 Nov-3 Dec) -> Prague (3-5 Dec) -> Brussels (5-7 Dec)",
        "- **Never** change dates, cities, hotels, paid Omio/Ryanair tickets, or GuruWalk reservation times",
        "- Daily EUR caps are per-person all-in (food, local transport, tips) excluding pre-booked hotels/flights", "",
        "## WHAT MINDTRIP MUST DO", "",
        "1. Build executable day-by-day itinerary from every section below",
        "2. Suggest **3 budget dinner options** near each hotel for **1 person**",
        "3. Validate timing on **21 Nov** (Neuschwanstein) and **5 Dec** (PRG->CRL + Flibco)",
        "4. Do not invent extra tours on 6 Dec Brussels (flight prep day)",
        "5. Keep exterior-first / fast-walking pace unless rain plan B listed", "",
        "---", "", "## DAY 0 - 18 NOV 2026 (IN FLIGHT)", "",
        "| Time | Plan |", "| --- | --- |",
        "| 21:20 | KL 644 depart JFK |", "| 10:30+1 | Arrive Amsterdam AMS (connection) |",
        "| 12:05 | KL 1853 AMS -> MUC |", "| 13:30 | Land Munich MUC - see Day 1 |", "",
        "---", "", "## INTERCONTINENTAL FLIGHTS (KLM + IBERIA - BOOKED)", "",
    ]
    lines.append(md_table(first_table_after(html, 'id="voos"')))
    lines += ["", "### Short-haul flight checklist (Ryanair Schengen)", ""]
    i0 = html.find('id="voos-checklist-curto"')
    i1 = html.find('id="voos-checklist-intercontinental"')
    chk = html[i0:i1] if i0 >= 0 and i1 > i0 else ""
    for item in extract_list_items(chk):
        lines.append(f"- {item}")
    lines += ["", "### Return flight checklist 7 Dec BRU", ""]
    i2 = html.find("</details>", i1) if i1 >= 0 else -1
    chk2 = html[i1:i2] if i1 >= 0 and i2 > i1 else ""
    for item in extract_list_items(chk2):
        lines.append(f"- {item}")
    lines += ["", "---", "", "## GROUND TRANSPORT + SHORT FLIGHTS (OMIO - LOCKED)", "",
              "Paid Ryanair total: BUD->BER R$ 734.34 + PRG->CRL R$ 773.64 = R$ 1,507.98",
              "Pending Omio buses/trains: ~R$ 709", ""]
    lines.append(md_table(first_table_after(html, 'id="horarios-bilhetes"')))
    lines += ["", "---", "", "## HOTELS (BOOKING.COM - LOCKED)", "", "Total indicative: ~R$ 11,423 (verify on Booking)", ""]
    hrows = [r[:5] for r in first_table_after(html, 'id="hoteis"') if r]
    lines.append(md_table(hrows))
    lines += ["", "### Hotel addresses (copy-paste)", "",
              "- B&B Muenchen-Hbf: Arnulfstrasse 30, 80335 Muenchen, Germany",
              "- Atel Hotel Lasserhof: Lasserstrasse 47, 5020 Salzburg, Austria",
              "- Hotel Zipser: Lange Gasse 49, 1080 Wien, Austria",
              "- Danubia Gate: Dunajska 26, 811 01 Bratislava, Slovakia",
              "- Medos Hotel: Rakoczi ut 40, 1072 Budapest, Hungary",
              "- Premier Inn Berlin Alexanderplatz: Otto-Braun-Strasse 69, 10178 Berlin",
              "- Alton Hotel: Legerova 1581/22, 120 00 Praha 2, Czechia",
              "- Hotel des Colonies Brussels: Rue des Croisades 6, 1210 Brussels", "",
              "---", "", "## DAILY BUDGET TABLE", ""]
    lines.append(md_table(table_with_id(html, 'operacional-tabela-dias')))
    lines += ["", "---", "", "## GURUWALK TOURS (17 BOOKED - LOCKED TIMES)", ""]
    lines.append(md_table(table_with_class(html, 'guruwalk-table', 'id="guruwalk"')))
    tips = html[html.find("guruwalk-tips"): html.find("guruwalk-tips") + 2000]
    lines.append("")
    lines.append("**GuruWalk tips:**")
    for item in extract_list_items(tips):
        lines.append(f"- {item}")
    lines += ["", "---", "", "## LUNCH KIT (BAGUETTE + PARMA + CHEESE + SODA)", "",
              "Eat walking 12:00-13:00. Budget ~EUR 6-10/person.", ""]
    lines.append(md_table(table_inside_block(html, 'explorar-almoco-kit')))
    lines += ["", "---", "", "## FIVE GUYS (DINNER NEAR HOTEL)", ""]
    lines.append(md_table(table_inside_block(html, 'explorar-fiveguys')))
    lines += ["", "---", "", "## SOCIAL HOSTELS (NIGHT - NOT FOR SLEEPING)", ""]
    lines.append(md_table(table_with_class(html, 'explorar-hostels-table', 'explorar-hostels-ancora')))
    lines += ["", "---", "", "## STARBUCKS MUGS (1 PER CITY)", ""]
    lines.append(md_table(table_inside_block(html, "explorar-starbucks")))
    lines += ["", "---", "", "## SHOPPING WINDOWS (LOCKED DATES)", ""]
    lines.append(md_table(table_inside_block(html, 'compras-matriz-dia')))
    lines += ["", "### Shopping fallback by product type", ""]
    lines.append(md_table(table_inside_block(html, 'compras-fallback-tipo')))
    lines += ["", "### Apple Store targets (AirPods Pro 3)", "",
              "- Munich: Apple Rosenstrasse (20 Nov window)",
              "- Vienna: Apple Kaerntner Strasse (24-25 Nov)",
              "- Berlin: Apple Kudamm or Mall of Berlin (2 Dec)",
              "- Brussels: Apple Avenue de la Toison d'Or (5-6 Dec before 17:00)",
              "- **No purchases morning of 6 or 7 Dec** - close shopping by 17:00 on 6 Dec", "",
              "---", "", "## GIFTS / SOUVENIRS", "",
              "- Close all gift shopping by **6 Dec 17:00** (Tax Free + packing)",
              "- Brussels chocolates: Neuhaus, Godiva, Leonidas (Rue Neuve / Grand Place)",
              "- 8 Starbucks mugs + 8 magnets - one per city", "",
              "---", "", "## DAY-BY-DAY EXECUTABLE PLAN (PRIMARY)", ""]
    for d in days:
        lines += render_day(d, HOTELS_BY_DATE.get(d["date"], ""))
        lines += ["---", ""]
    lines += ["## EMERGENCY", "", "- EU emergency: **112**",
              "- Travel insurance SOS: _______________",
              "- KLM app (ida EQZEWL) + Iberia app (volta BRU→GRU)", "",
              "## MINDTRIP OUTPUT REQUEST", "",
              "1. Calendar itinerary Nov 18 - Dec 7 2026 for **1 solo adult**",
              "2. Map pins for hotels + GuruWalk meeting points",
              "3. 3 cheap dinners/night near hotel (solo portions)",
              "4. Flag any impossible timing", ""]
    return "\n".join(lines)
