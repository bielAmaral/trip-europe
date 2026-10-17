#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Google Calendar-friendly .ics from index.html (FAST plan + transport/flights/hotels)."""

from __future__ import annotations

import html as html_lib
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUT = ROOT / "data" / "EuroTrip-2026.ics"

TZ_EU = "Europe/Berlin"
TZ_BR = "America/Sao_Paulo"
TZ_NY = "America/New_York"
PRODID = "-//trip-europe//EuroTrip 2026//PT"


@dataclass
class IcsEvent:
    uid: str
    summary: str
    description: str
    location: str
    dtstart: datetime | None = None
    dtend: datetime | None = None
    dtend_tzid: str | None = None
    all_day_start: date | None = None
    all_day_end: date | None = None
    tzid: str = TZ_EU
    alarm_minutes: int | None = None
    categories: str = ""


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = html_lib.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def fold_ics(text: str) -> str:
    text = text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    lines: list[str] = []
    while len(text) > 73:
        lines.append(text[:73])
        text = " " + text[73:]
    lines.append(text)
    return "\r\n".join(lines)


def fmt_local(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")


def fmt_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def normalize_when(when: str) -> str:
    for ch in ("\u2013", "\u2014", "\u2212"):
        when = when.replace(ch, "-")
    return when.strip()


def parse_time_range(when: str, base: date) -> tuple[datetime, datetime] | None:
    when = normalize_when(when)
    if not when or when.lower() in ("dia", "-", "\u2014"):
        return None
    when = re.sub(r"^~", "", when)
    m = re.match(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$", when)
    if m:
        h1, m1, h2, m2 = map(int, m.groups())
        start = datetime(base.year, base.month, base.day, h1, m1)
        end = datetime(base.year, base.month, base.day, h2, m2)
        if end <= start:
            end += timedelta(days=1)
        return start, end
    m = re.match(r"^(\d{1,2}):(\d{2})$", when)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        start = datetime(base.year, base.month, base.day, h, mi)
        return start, start + timedelta(hours=1, minutes=30)
    return None


def parse_days(html: str) -> list[dict]:
    parts = re.split(r'<details class="day" id="(day-2026-\d{2}-\d{2})"', html)
    days: list[dict] = []
    for i in range(1, len(parts), 2):
        block = parts[i + 1]
        dm = re.search(r'data-trip-date="(\d{4}-\d{2}-\d{2})"', block)
        if not dm:
            continue
        trip_date = date.fromisoformat(dm.group(1))
        city_m = re.search(r'<span class="city">([^<]+)</span>', block)
        city = strip_tags(city_m.group(1)) if city_m else parts[i]
        mode_m = re.search(r'class="fast-plan__mode">([^<]+)', block)
        mode = strip_tags(mode_m.group(1)) if mode_m else ""
        rows = [
            (strip_tags(w), strip_tags(t))
            for w, t in re.findall(
                r'<tr><td class="fast-plan__when">([^<]*)</td><td>(.*?)</td></tr>',
                block,
                re.DOTALL,
            )
        ]
        days.append({"id": parts[i], "date": trip_date, "city": city, "mode": mode, "rows": rows})
    return days


def fixed_transport() -> list[IcsEvent]:
    legs = [
        ("2026-11-22", 12, 9, 14, 10, "Trem ICE Munique -> Salzburgo", "DB ICE (XP)", "Muenchen Hbf", 60),
        ("2026-11-24", 11, 7, 13, 32, "Trem RJX Salzburgo -> Viena", "OBB RJX 63 (Wise)", "Salzburg Hbf", 45),
        ("2026-11-26", 12, 35, 16, 35, "Flix Viena -> Bratislava", "FlixBus (Wise)", "Vienna Erdberg", 45),
        ("2026-11-27", 10, 50, 13, 20, "Flix Bratislava -> Budapeste", "FlixBus (Wise)", "Bratislava", 45),
        ("2026-11-30", 11, 25, 12, 40, "Voo BUD -> BER", "Ryanair FR4098 (Wise)", "BUD", 120),
        ("2026-12-03", 10, 20, 15, 20, "Flix Berlim -> Praga", "FlixBus (comprar)", "Berlin Suedkreuz", 45),
        ("2026-12-05", 12, 30, 14, 15, "Voo PRG -> CRL", "Ryanair (Wise)", "PRG", 120),
        ("2026-12-07", 7, 0, 11, 50, "Voo BRU -> MAD -> GRU", "Iberia IB3203 + IB0267", "BRU", 180),
    ]
    events: list[IcsEvent] = []
    for ds, h1, m1, h2, m2, title, desc, loc, alarm in legs:
        d = date.fromisoformat(ds)
        start = datetime(d.year, d.month, d.day, h1, m1)
        end = datetime(d.year, d.month, d.day, h2, m2)
        if end <= start:
            end += timedelta(days=1)
        events.append(
            IcsEvent(
                uid=f"transport-{ds}-{h1:02d}{m1:02d}@eurotrip2026",
                summary=title,
                description=desc + "\\nVer roteiro: horarios-bilhetes",
                location=loc,
                dtstart=start,
                dtend=end,
                alarm_minutes=alarm,
                categories="Transporte",
            )
        )
    events.append(
        IcsEvent(
            uid="flight-jfk-muc@eurotrip2026",
            summary="Voo JFK -> AMS -> MUC (KLM 644 + 1853)",
            description="Saida JFK 21:20. Conexao AMS. Chegada MUC 13:30 (+1 dia). Loc EQZEWL. ARGO FLEX.",
            location="JFK",
            dtstart=datetime(2026, 11, 18, 21, 20),
            dtend=datetime(2026, 11, 19, 13, 30),
            tzid=TZ_NY,
            dtend_tzid=TZ_EU,
            alarm_minutes=180,
            categories="Voo",
        )
    )
    return events


def fixed_hotels() -> list[IcsEvent]:
    stays = [
        ("2026-11-19", "2026-11-22", "Hotel Munique", "Check-in 19 nov, check-out 22 nov"),
        ("2026-11-22", "2026-11-24", "Hotel Salzburgo", "Check-in 22 nov, check-out 24 nov"),
        ("2026-11-24", "2026-11-26", "Hotel Viena", "Check-in 24 nov, check-out 26 nov"),
        ("2026-11-26", "2026-11-28", "Hotel Bratislava", "Check-in 26 nov, check-out 28 nov"),
        ("2026-11-28", "2026-11-30", "Hotel Budapeste", "Check-in 28 nov, check-out 30 nov"),
        ("2026-11-30", "2026-12-03", "Hotel Berlim", "Check-in 30 nov, check-out 3 dez"),
        ("2026-12-03", "2026-12-05", "Hotel Praga", "Check-in 3 dez, check-out 5 dez"),
        ("2026-12-05", "2026-12-07", "Hotel Bruxelas", "Mercure Rogier, check-out 7 dez"),
    ]
    return [
        IcsEvent(
            uid=f"hotel-{cin}@eurotrip2026",
            summary=title,
            description=desc,
            location="",
            all_day_start=date.fromisoformat(cin),
            all_day_end=date.fromisoformat(cout),
            categories="Hotel",
        )
        for cin, cout, title, desc in stays
    ]


def parse_guruwalk(html: str) -> list[IcsEvent]:
    start = html.find("guruwalk-table")
    if start < 0:
        return []
    chunk = html[start : start + 15000]
    events: list[IcsEvent] = []
    for date_cell, time_cell, tour_cell, notes in re.findall(
        r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>",
        chunk,
        re.DOTALL,
    ):
        date_cell, time_cell, tour_cell, notes = map(strip_tags, (date_cell, time_cell, tour_cell, notes))
        if date_cell.startswith("Data"):
            continue
        d: date | None = None
        if m := re.search(r"(\d{1,2})\s+nov", date_cell, re.I):
            d = date(2026, 11, int(m.group(1)))
        elif "1 dez" in date_cell.lower():
            d = date(2026, 12, 1)
        elif "2 dez" in date_cell.lower():
            d = date(2026, 12, 2)
        elif "3 dez" in date_cell.lower():
            d = date(2026, 12, 3)
        elif "4 dez" in date_cell.lower():
            d = date(2026, 12, 4)
        if not d:
            continue
        if not (tm := re.search(r"(\d{1,2}):(\d{2})", time_cell)):
            continue
        h, mi = int(tm.group(1)), int(tm.group(2))
        start_dt = datetime(d.year, d.month, d.day, h, mi)
        events.append(
            IcsEvent(
                uid=f"guruwalk-{d.isoformat()}-{h:02d}{mi:02d}@eurotrip2026",
                summary=f"GuruWalk: {tour_cell[:70]}",
                description=notes + "\\nChegue 10 min antes.",
                location=notes[:100],
                dtstart=start_dt,
                dtend=start_dt + timedelta(hours=2),
                alarm_minutes=30,
                categories="Tour",
            )
        )
    return events


def day_events(days: list[dict]) -> list[IcsEvent]:
    events: list[IcsEvent] = []
    for day in days:
        d = day["date"]
        desc_lines = [f"{w} - {t}" for w, t in day["rows"] if t]
        day_desc = "\\n".join(desc_lines[:14])
        if day["mode"]:
            day_desc = day["mode"] + "\\n" + day_desc
        events.append(
            IcsEvent(
                uid=f"day-{d.isoformat()}@eurotrip2026",
                summary=f"{day['city']} - EuroTrip 2026",
                description=day_desc,
                location=day["city"],
                all_day_start=d,
                all_day_end=d + timedelta(days=1),
                categories="Dia",
            )
        )
        for idx, (when, what) in enumerate(day["rows"]):
            if not what or len(what) < 4:
                continue
            tr = parse_time_range(when, d)
            if not tr:
                continue
            start, end = tr
            if "12:35" in when and "Flix" in what:
                continue
            if "11:07" in when:
                continue
            if "12:09" in when and "ICE" in what.upper():
                continue
            events.append(
                IcsEvent(
                    uid=f"fast-{d.isoformat()}-{idx}@eurotrip2026",
                    summary=what[:75],
                    description=what,
                    location=day["city"],
                    dtstart=start,
                    dtend=end,
                    categories="Plano",
                )
            )
    return events


def render_event(ev: IcsEvent) -> str:
    lines = ["BEGIN:VEVENT", f"UID:{ev.uid}", f"SUMMARY:{fold_ics(ev.summary)}"]
    if ev.description:
        lines.append(f"DESCRIPTION:{fold_ics(ev.description)}")
    if ev.location:
        lines.append(f"LOCATION:{fold_ics(ev.location)}")
    if ev.categories:
        lines.append(f"CATEGORIES:{ev.categories}")
    if ev.all_day_start and ev.all_day_end:
        lines.append(f"DTSTART;VALUE=DATE:{fmt_date(ev.all_day_start)}")
        lines.append(f"DTEND;VALUE=DATE:{fmt_date(ev.all_day_end)}")
    elif ev.dtstart and ev.dtend:
        tz_end = ev.dtend_tzid or ev.tzid
        lines.append(f"DTSTART;TZID={ev.tzid}:{fmt_local(ev.dtstart)}")
        lines.append(f"DTEND;TZID={tz_end}:{fmt_local(ev.dtend)}")
    lines.append("DTSTAMP:" + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))
    if ev.alarm_minutes:
        lines.extend(
            [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"TRIGGER:-PT{ev.alarm_minutes}M",
                f"DESCRIPTION:{fold_ics(ev.summary)}",
                "END:VALARM",
            ]
        )
    lines.append("END:VEVENT")
    return "\r\n".join(lines)


def main() -> int:
    if not INDEX.is_file():
        print(f"Missing {INDEX}", file=sys.stderr)
        return 1
    html = INDEX.read_text(encoding="utf-8")
    days = parse_days(html)
    events: list[IcsEvent] = []
    events.extend(fixed_hotels())
    events.extend(fixed_transport())
    events.extend(parse_guruwalk(html))
    events.extend(day_events(days))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = "\r\n".join(render_event(e) for e in events)
    cal = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        f"PRODID:{PRODID}\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "X-WR-CALNAME:EuroTrip 2026\r\n"
        f"X-WR-TIMEZONE:{TZ_EU}\r\n"
        "BEGIN:VTIMEZONE\r\n"
        "TZID:Europe/Berlin\r\n"
        "X-LIC-LOCATION:Europe/Berlin\r\n"
        "BEGIN:DAYLIGHT\r\n"
        "TZOFFSETFROM:+0100\r\n"
        "TZOFFSETTO:+0200\r\n"
        "TZNAME:CEST\r\n"
        "DTSTART:19700329T020000\r\n"
        "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\r\n"
        "END:DAYLIGHT\r\n"
        "BEGIN:STANDARD\r\n"
        "TZOFFSETFROM:+0200\r\n"
        "TZOFFSETTO:+0100\r\n"
        "TZNAME:CET\r\n"
        "DTSTART:19701025T030000\r\n"
        "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\r\n"
        "END:STANDARD\r\n"
        "END:VTIMEZONE\r\n"
        f"{body}\r\n"
        "END:VCALENDAR\r\n"
    )
    OUT.write_text(cal, encoding="utf-8")
    print(f"Wrote {len(events)} events -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
