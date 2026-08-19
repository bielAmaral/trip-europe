#!/usr/bin/env python3
"""Gera CSV de paradas para Google My Maps + data/mapas-paradas.csv (app)."""
from __future__ import annotations

import csv
import math
import xml.sax.saxutils as xml_escape
from pathlib import Path
from urllib.parse import quote

from mapas_geo import GEO, lookup
from mapas_legs import MODE_PT, leg_maps_url, resolve_leg

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FULL_CSV = DATA / "mapas-paradas.csv"
MYMAPS_CSV = DATA / "mapas-my-maps.csv"
KML_FILE = DATA / "mapas-roteiro.kml"
MAX_ROUTE_SEGMENT_KM = 25.0

# day_id, date, title, stops: order, category, name_pt, address (geocode query)
DAYS = [
    {
        "day_id": "day-2026-11-19",
        "date": "19 nov",
        "title": "Munique — chegada",
        "stops": [
            (1, "airport", "Aeroporto MUC", "Munich Airport, Germany"),
            (2, "transport", "München Hauptbahnhof", "München Hauptbahnhof, Germany"),
            (3, "hotel", "B&B Hotel München-Hbf", "B&B Hotel München-Hbf, Arnulfstraße 30, 80335 München, Germany"),
            (4, "sight", "Marienplatz", "Marienplatz, Munich, Germany"),
            (5, "sight", "Neues Rathaus", "Neues Rathaus, Marienplatz, Munich, Germany"),
            (6, "sight", "Frauenkirche", "Frauenkirche, Munich, Germany"),
            (7, "sight", "Viktualienmarkt", "Viktualienmarkt, Munich, Germany"),
            (8, "sight", "Karlsplatz (Stachus)", "Karlsplatz, Munich, Germany"),
        ],
    },
    {
        "day_id": "day-2026-11-20",
        "date": "20 nov",
        "title": "Munique — Englischer Garten",
        "stops": [
            (1, "hotel", "B&B Hotel München-Hbf", "B&B Hotel München-Hbf, Arnulfstraße 30, München, Germany"),
            (2, "sight", "Hofgarten", "Hofgarten, Munich, Germany"),
            (3, "sight", "Odeonsplatz", "Odeonsplatz, Munich, Germany"),
            (4, "sight", "Siegestor", "Siegestor, Munich, Germany"),
            (5, "sight", "Englischer Garten", "Englischer Garten, Munich, Germany"),
            (6, "sight", "Chinesischer Turm", "Chinesischer Turm, Englischer Garten, Munich, Germany"),
            (7, "sight", "Eisbachwelle", "Eisbachwelle, Munich, Germany"),
            (8, "sight", "Isar (Gärtnerplatz)", "Gärtnerplatz, Munich, Germany"),
            (9, "sight", "Kaufingerstraße", "Kaufingerstraße, Munich, Germany"),
            (10, "night", "Wombat's WomBAR (noite)", "Wombat's City Hostel Munich, Senefelderstraße 1, Munich, Germany"),
        ],
    },
    {
        "day_id": "day-2026-11-21",
        "date": "21 nov",
        "title": "Neuschwanstein (dia inteiro)",
        "stops": [
            (1, "hotel", "B&B Hotel München-Hbf", "B&B Hotel München-Hbf, Arnulfstraße 30, München, Germany"),
            (2, "transport", "München ZOB", "München ZOB, Arnulfstraße, Munich, Germany"),
            (3, "transport", "Füssen Pulverturm (FlixBus)", "Pulverturmstraße 1, 87629 Füssen, Germany"),
            (4, "sight", "Schloss Hohenschwangau", "Schloss Hohenschwangau, Schwangau, Germany"),
            (5, "sight", "Neuschwanstein Castle", "Neuschwanstein Castle, Schwangau, Germany"),
            (6, "sight", "Marienbrücke", "Marienbrücke, Schwangau, Germany"),
            (7, "sight", "Alpsee (opcional)", "Alpsee, 87645 Schwangau, Germany"),
            (8, "transport", "Füssen Pulverturm (volta)", "Pulverturmstraße 1, 87629 Füssen, Germany"),
            (9, "transport", "München ZOB", "München ZOB, Munich, Germany"),
        ],
    },
    {
        "day_id": "day-2026-11-22",
        "date": "22 nov",
        "title": "Munique → Salzburgo",
        "stops": [
            (1, "hotel", "B&B Hotel München-Hbf (check-out)", "B&B Hotel München-Hbf, Arnulfstraße 30, München, Germany"),
            (2, "sight", "Marienplatz (se sobrar tempo)", "Marienplatz, Munich, Germany"),
            (3, "transport", "München ZOB", "München ZOB, Munich, Germany"),
            (4, "transport", "Salzburg P+R Süd (FlixBus)", "Salzburg P+R Süd, Austria"),
            (5, "hotel", "Atel Hotel Lasserhof", "Atel Hotel Lasserhof, Lasserstraße 47, 5020 Salzburg, Austria"),
            (6, "sight", "Mirabellgarten", "Mirabell Palace and Gardens, Salzburg, Austria"),
            (7, "sight", "Getreidegasse", "Getreidegasse, Salzburg, Austria"),
            (8, "sight", "Salzburger Dom", "Salzburg Cathedral, Salzburg, Austria"),
        ],
    },
    {
        "day_id": "day-2026-11-23",
        "date": "23 nov",
        "title": "Salzburgo — Festung",
        "stops": [
            (1, "hotel", "Atel Hotel Lasserhof", "Atel Hotel Lasserhof, Lasserstraße 47, Salzburg, Austria"),
            (2, "sight", "Festung Hohensalzburg", "Hohensalzburg Fortress, Salzburg, Austria"),
            (3, "sight", "Residenzplatz", "Residenzplatz, Salzburg, Austria"),
            (4, "sight", "Salzburger Dom", "Salzburg Cathedral, Salzburg, Austria"),
            (5, "sight", "Getreidegasse", "Getreidegasse, Salzburg, Austria"),
            (6, "sight", "Mozartplatz", "Mozartplatz, Salzburg, Austria"),
            (7, "sight", "Makartsteg", "Makartsteg, Salzburg, Austria"),
            (8, "night", "YoHo Hostel bar", "YoHo International Youth Hostel, Paracelsusstraße 9, Salzburg, Austria"),
        ],
    },
    {
        "day_id": "day-2026-11-24",
        "date": "24 nov",
        "title": "Salzburgo → Viena",
        "stops": [
            (1, "hotel", "Atel Hotel Lasserhof (check-out)", "Atel Hotel Lasserhof, Lasserstraße 47, Salzburg, Austria"),
            (2, "transport", "Salzburg Hauptbahnhof", "Salzburg Hauptbahnhof, Austria"),
            (3, "transport", "Wien Hauptbahnhof (ICE 10:00)", "Wien Hauptbahnhof, Austria"),
            (4, "hotel", "Hotel Zipser", "Hotel Zipser, Lange Gasse 49, 1080 Wien, Austria"),
            (5, "sight", "Prater", "Prater, Vienna, Austria"),
            (6, "sight", "Naschmarkt", "Naschmarkt, Vienna, Austria"),
            (7, "sight", "Donaukanal", "Donaukanal, 1020 Vienna, Austria"),
            (8, "night", "Wombat's WomBAR Naschmarkt", "Wombat's City Hostel Vienna, Rechte Wienzeile 35, Vienna, Austria"),
        ],
    },
    {
        "day_id": "day-2026-11-25",
        "date": "25 nov",
        "title": "Viena — Schönbrunn e anel",
        "stops": [
            (1, "hotel", "Hotel Zipser", "Hotel Zipser, Lange Gasse 49, Wien, Austria"),
            (2, "sight", "Schönbrunn Palace", "Schönbrunn Palace, Vienna, Austria"),
            (3, "sight", "Stadtpark", "Stadtpark, Vienna, Austria"),
            (4, "sight", "Stephansdom", "St. Stephen's Cathedral, Vienna, Austria"),
            (5, "sight", "Graben", "Graben, Vienna, Austria"),
            (6, "sight", "Hofburg", "Hofburg Palace, Vienna, Austria"),
            (7, "sight", "Rathaus", "Vienna City Hall, Austria"),
            (8, "sight", "Parlamento", "Austrian Parliament Building, Vienna, Austria"),
        ],
    },
    {
        "day_id": "day-2026-11-26",
        "date": "26 nov",
        "title": "Viena → Bratislava",
        "stops": [
            (1, "hotel", "Hotel Zipser (check-out)", "Hotel Zipser, Lange Gasse 49, Wien, Austria"),
            (2, "sight", "Josefstadt (manhã livre)", "Josefstädter Straße 1, 1080 Wien, Austria"),
            (3, "transport", "Vienna International Bus Terminal (VIB)", "Vienna International Bus Terminal, Austria"),
            (4, "transport", "Bratislava Most SNP (FlixBus)", "Most SNP, Bratislava, Slovakia"),
            (5, "hotel", "Danubia Gate Hotel", "Danubia Gate Hotel, Dunajská 26, Bratislava, Slovakia"),
            (6, "sight", "Staré Mesto", "Hlavné námestie, Bratislava, Slovakia"),
            (7, "sight", "Bratislava Castle", "Bratislava Castle, Slovakia"),
            (8, "night", "Wild Elephants Hostel", "Wild Elephants Hostel, Námestie SNP 5, Bratislava, Slovakia"),
        ],
    },
    {
        "day_id": "day-2026-11-27",
        "date": "27 nov",
        "title": "Bratislava → Budapeste",
        "stops": [
            (1, "hotel", "Danubia Gate Hotel (check-out)", "Danubia Gate Hotel, Dunajská 26, Bratislava, Slovakia"),
            (2, "transport", "Bratislava Nivy (Mlynské Nivy)", "Bratislava Nivy bus station, Slovakia"),
            (3, "transport", "Budapest Kelenföld (FlixBus)", "Budapest Kelenföld, Hungary"),
            (4, "hotel", "Medos Hotel", "Medos Hotel, Rákóczi út 40, Budapest, Hungary"),
            (5, "sight", "Basílica de Santo Estêvão", "Szent István tér 1, Budapest, Hungary"),
            (6, "sight", "Andrássy út", "Andrássy Avenue, Budapest, Hungary"),
            (7, "sight", "Chain Bridge", "Széchenyi Chain Bridge, Budapest, Hungary"),
            (8, "sight", "Buda Castle (vista)", "Buda Castle, Budapest, Hungary"),
        ],
    },
    {
        "day_id": "day-2026-11-28",
        "date": "28 nov",
        "title": "Budapeste — Pest icónico",
        "stops": [
            (1, "hotel", "Medos Hotel", "Medos Hotel, Rákóczi út 40, Budapest, Hungary"),
            (2, "sight", "Parlamento", "Hungarian Parliament Building, Budapest, Hungary"),
            (3, "sight", "Shoes on the Danube", "Shoes on the Danube Bank, Budapest, Hungary"),
            (4, "sight", "Great Market Hall", "Great Market Hall, Budapest, Hungary"),
            (5, "sight", "Fisherman's Bastion", "Fisherman's Bastion, Budapest, Hungary"),
            (6, "sight", "Matthias Church", "Matthias Church, Budapest, Hungary"),
            (7, "night", "Wombat's WomBAR", "Wombat's City Hostel Budapest, Király utca 20, Budapest, Hungary"),
            (8, "night", "Szimpla Kert", "Szimpla Kert, Budapest, Hungary"),
            (9, "night", "Instant-Fogas", "Instant-Fogas, Budapest, Hungary"),
        ],
    },
    {
        "day_id": "day-2026-11-29",
        "date": "29 nov",
        "title": "Budapeste — descanso",
        "stops": [
            (1, "hotel", "Medos Hotel", "Medos Hotel, Rákóczi út 40, Budapest, Hungary"),
            (2, "sight", "Jewish Quarter (opcional)", "Dohány utca 2, Budapest, Hungary"),
            (3, "sight", "Margaret Bridge", "Margaret Bridge, Budapest, Hungary"),
            (4, "sight", "Margaret Island", "Margaret Island, Budapest, Hungary"),
        ],
    },
    {
        "day_id": "day-2026-11-30",
        "date": "30 nov",
        "title": "Budapeste → Berlim",
        "stops": [
            (1, "hotel", "Medos Hotel (check-out)", "Medos Hotel, Rákóczi út 40, Budapest, Hungary"),
            (2, "sight", "Basílica (último passeio)", "Szent István tér 1, Budapest, Hungary"),
            (3, "airport", "Budapest Airport (BUD)", "Budapest Airport, Hungary"),
            (4, "airport", "Berlin Brandenburg Airport (BER)", "Berlin Brandenburg Airport, Germany"),
            (5, "hotel", "Premier Inn Alexanderplatz", "Premier Inn Berlin Alexanderplatz, Otto-Braun-Straße 69, Berlin, Germany"),
            (6, "sight", "Alexanderplatz", "Alexanderplatz 1, 10178 Berlin, Germany"),
            (7, "sight", "Fernsehturm", "Berlin TV Tower, Germany"),
        ],
    },
    {
        "day_id": "day-2026-12-01",
        "date": "1 dez",
        "title": "Berlim — Mitte",
        "stops": [
            (1, "hotel", "Premier Inn Alexanderplatz", "Premier Inn Berlin Alexanderplatz, Berlin, Germany"),
            (2, "sight", "Brandenburg Gate", "Brandenburg Gate, Berlin, Germany"),
            (3, "sight", "Reichstag", "Reichstag Building, Berlin, Germany"),
            (4, "sight", "Tiergarten", "Tiergarten, Berlin, Germany"),
            (5, "sight", "Holocaust Memorial", "Memorial to the Murdered Jews of Europe, Berlin, Germany"),
            (6, "sight", "Potsdamer Platz", "Potsdamer Platz, Berlin, Germany"),
            (7, "sight", "East Side Gallery", "East Side Gallery, Berlin, Germany"),
            (8, "sight", "Alexanderplatz (volta)", "Alexanderplatz 1, 10178 Berlin, Germany"),
            (9, "night", "Generator Berlin (noite)", "Generator Berlin Alexanderplatz, Otto-Braun-Straße 65, Berlin, Germany"),
        ],
    },
    {
        "day_id": "day-2026-12-02",
        "date": "2 dez",
        "title": "Berlim — compras",
        "stops": [
            (1, "hotel", "Premier Inn Alexanderplatz", "Premier Inn Berlin Alexanderplatz, Berlin, Germany"),
            (2, "sight", "Unter den Linden", "Unter den Linden, Berlin, Germany"),
            (3, "sight", "Berliner Dom", "Berlin Cathedral, Germany"),
            (4, "sight", "Lustgarten", "Lustgarten, Berlin, Germany"),
            (5, "sight", "Museum Island", "Museum Island, Berlin, Germany"),
            (6, "sight", "Gendarmenmarkt", "Gendarmenmarkt, Berlin, Germany"),
            (7, "sight", "Kurfürstendamm", "Kurfürstendamm, Berlin, Germany"),
        ],
    },
    {
        "day_id": "day-2026-12-03",
        "date": "3 dez",
        "title": "Berlim → Praga",
        "stops": [
            (1, "hotel", "Premier Inn Alexanderplatz (check-out)", "Premier Inn Berlin Alexanderplatz, Berlin, Germany"),
            (2, "transport", "Berlin Südkreuz", "Berlin Südkreuz station, Germany"),
            (3, "transport", "Praha Florenc (FlixBus)", "Florenc bus station, Prague, Czechia"),
            (4, "hotel", "Alton Hotel", "Alton Hotel, Legerova 22, Prague, Czechia"),
            (5, "sight", "Wenceslas Square", "Wenceslas Square, Prague, Czechia"),
            (6, "sight", "Old Town Square", "Old Town Square, Prague, Czechia"),
            (7, "sight", "Astronomical Clock", "Prague Astronomical Clock, Czechia"),
        ],
    },
    {
        "day_id": "day-2026-12-04",
        "date": "4 dez",
        "title": "Praga — castelo",
        "stops": [
            (1, "hotel", "Alton Hotel", "Alton Hotel, Legerova 22, Prague, Czechia"),
            (2, "sight", "Charles Bridge", "Charles Bridge, Prague, Czechia"),
            (3, "sight", "Malá Strana", "Malá Strana, Prague, Czechia"),
            (4, "sight", "Prague Castle", "Prague Castle, Czechia"),
            (5, "sight", "Kampa Island", "Kampa Island, Prague, Czechia"),
            (6, "sight", "Na Příkopě", "Na Příkopě, Prague, Czechia"),
            (7, "sight", "Palladium", "Palladium Prague, Czechia"),
            (8, "sight", "Old Town Square (revisit)", "Old Town Square, Prague, Czechia"),
            (9, "night", "Czech Inn bar (Vinohrady)", "Czech Inn, Francouzská 76, Prague, Czechia"),
        ],
    },
    {
        "day_id": "day-2026-12-05",
        "date": "5 dez",
        "title": "Praga → Bruxelas",
        "stops": [
            (1, "hotel", "Alton Hotel (check-out)", "Alton Hotel, Legerova 22, Prague, Czechia"),
            (2, "sight", "Charles Bridge (último passeio)", "Charles Bridge, Prague, Czechia"),
            (3, "airport", "Václav Havel Airport (PRG)", "Václav Havel Airport Prague, Czechia"),
            (4, "airport", "Brussels Airport Zaventem (BRU)", "Brussels Airport, Belgium"),
            (5, "hotel", "Hotel des Colonies", "Hotel des Colonies Brussels, Rue des Croisades 6, Brussels, Belgium"),
            (6, "sight", "Rogier / Rue Neuve", "Rue Neuve, Brussels, Belgium"),
        ],
    },
    {
        "day_id": "day-2026-12-06",
        "date": "6 dez",
        "title": "Bruxelas — descanso + prep voo",
        "stops": [
            (1, "hotel", "Hotel des Colonies", "Hotel des Colonies Brussels, Rue des Croisades 6, Brussels, Belgium"),
            (2, "sight", "Grand Place", "Grand Place, Brussels, Belgium"),
            (3, "sight", "Galeries Royales Saint-Hubert", "Galeries Royales Saint-Hubert, Brussels, Belgium"),
            (4, "sight", "Mont des Arts", "Mont des Arts, Brussels, Belgium"),
            (5, "sight", "Rue Neuve (opcional)", "Rue Neuve, Brussels, Belgium"),
            (6, "hotel", "Hotel des Colonies (prep voo)", "Hotel des Colonies Brussels, Belgium"),
        ],
    },
    {
        "day_id": "day-2026-12-07",
        "date": "7 dez",
        "title": "Bruxelas → Brasil",
        "stops": [
            (1, "hotel", "Hotel des Colonies (check-out)", "Hotel des Colonies Brussels, Belgium"),
            (2, "airport", "Brussels Airport Zaventem (BRU)", "Brussels Airport, Belgium"),
        ],
    },
]

CAT_PT = {
    "hotel": "Hotel",
    "transport": "Transporte",
    "airport": "Aeroporto",
    "sight": "Ponto turístico",
    "food": "Comida",
    "night": "Noite",
}


def sanitize_mymaps_name(text: str) -> str:
    """Nomes simples para o importador do My Maps (evita · e aspas problemáticas)."""
    return (
        text.replace("·", "-")
        .replace("→", "->")
        .replace("'", "")
        .replace('"', "")
        .strip()
    )


def coords_for(address: str) -> tuple[float, float]:
    hit = lookup(address)
    if hit is None:
        raise KeyError(f"Sem coordenadas para: {address!r} — adicione em scripts/mapas_geo.py")
    return hit


def layer_name(day: dict) -> str:
    return sanitize_mymaps_name(f"{day['date']} — {day['title']}")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def route_segments_coords(stops: list[tuple]) -> list[list[tuple[float, float]]]:
    """Trechos de linha no mapa; quebra em aeroportos ou saltos >25 km (Flix/ICE/voo)."""
    segments: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    prev: tuple[float, float] | None = None

    for _order, cat, _name, address in stops:
        lat, lng = coords_for(address)
        pt = (lat, lng)

        if cat == "airport":
            if len(current) >= 2:
                segments.append(current)
            current = []
            prev = None
            continue

        if prev is not None and haversine_km(prev[0], prev[1], lat, lng) > MAX_ROUTE_SEGMENT_KM:
            if len(current) >= 2:
                segments.append(current)
            current = []

        if not current or current[-1] != pt:
            current.append(pt)
        prev = pt

    if len(current) >= 2:
        segments.append(current)
    return segments


def kml_coords_line(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{lng:.6f},{lat:.6f},0" for lat, lng in points)


def maps_search_url(address: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + quote(address)


def maps_dir_url(addresses: list[str]) -> str:
    if len(addresses) < 2:
        return maps_search_url(addresses[0]) if addresses else ""
    origin = quote(addresses[0])
    dest = quote(addresses[-1])
    mid = addresses[1:-1]
    # Google Maps supports limited waypoints
    if len(mid) > 8:
        mid = mid[:8]
    waypoints = "%7C".join(quote(a) for a in mid)
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}&travelmode=walking"
    if waypoints:
        url += f"&waypoints={waypoints}"
    return url


def route_addresses(stops: list[tuple]) -> list[str]:
    """Paradas úteis para rota a pé (exclui aeroportos longos e duplicados)."""
    out = []
    seen = set()
    for _order, cat, _name, addr in stops:
        if cat in ("airport",):
            continue
        if cat == "transport" and len(stops) > 6:
            continue
        key = addr.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(addr)
    return out[:10]


def write_csvs() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    full_fields = [
        "day_id",
        "date",
        "day_title",
        "order",
        "category",
        "category_pt",
        "name_pt",
        "address",
        "latitude",
        "longitude",
        "leg_mode",
        "leg_mode_pt",
        "leg_hint",
        "leg_maps_url",
        "maps_search_url",
        "route_day_url",
    ]

    mymaps_fields = ["Name", "Layer", "Description", "Address", "Latitude", "Longitude"]

    rows_full = []
    rows_mymaps = []

    for day in DAYS:
        route_addrs = route_addresses(day["stops"])
        route_url = maps_dir_url(route_addrs)
        day_layer = layer_name(day)

        prev_stop: tuple | None = None
        prev_addr: str | None = None
        prev_coords: tuple[float, float] | None = None

        for stop_index, (order, cat, name_pt, address) in enumerate(day["stops"]):
            lat, lng = coords_for(address)
            leg_mode = ""
            leg_mode_pt = ""
            leg_hint = ""
            leg_url = ""

            if prev_stop is not None and prev_addr is not None and prev_coords is not None:
                dist = haversine_km(prev_coords[0], prev_coords[1], lat, lng)
                leg_mode, leg_hint = resolve_leg(
                    day["day_id"],
                    stop_index,
                    prev_stop,
                    (order, cat, name_pt, address),
                    dist,
                )
                leg_mode_pt = MODE_PT.get(leg_mode, leg_mode)
                leg_url = leg_maps_url(prev_addr, address, leg_mode)

            rows_full.append(
                {
                    "day_id": day["day_id"],
                    "date": day["date"],
                    "day_title": day["title"],
                    "order": order,
                    "category": cat,
                    "category_pt": CAT_PT.get(cat, cat),
                    "name_pt": name_pt,
                    "address": address,
                    "latitude": f"{lat:.6f}",
                    "longitude": f"{lng:.6f}",
                    "leg_mode": leg_mode,
                    "leg_mode_pt": leg_mode_pt,
                    "leg_hint": leg_hint,
                    "leg_maps_url": leg_url,
                    "maps_search_url": maps_search_url(address),
                    "route_day_url": route_url,
                }
            )
            prev_stop = (order, cat, name_pt, address)
            prev_addr = address
            prev_coords = (lat, lng)
            desc = sanitize_mymaps_name(
                f"{day['date']} - {day['title']} - {CAT_PT.get(cat, cat)} - #{day['day_id']}"
            )
            rows_mymaps.append(
                {
                    "Name": sanitize_mymaps_name(f"{day['date']} {order:02d} - {name_pt}"),
                    "Layer": day_layer,
                    "Description": desc,
                    "Address": address,
                    "Latitude": f"{lat:.6f}",
                    "Longitude": f"{lng:.6f}",
                }
            )

    with FULL_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=full_fields)
        w.writeheader()
        w.writerows(rows_full)

    with MYMAPS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=mymaps_fields)
        w.writeheader()
        w.writerows(rows_mymaps)

    return len(rows_full)


def write_kml() -> tuple[int, int]:
    """KML com 19 pastas (1/dia), pins numerados e linhas de rota por trecho urbano."""
    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        "  <Document>",
        "    <name>Roteiro Europa nov-dez 2026</name>",
        "    <description>19 dias FAST TOURIST — pastas por dia + rotas a pé (trechos separados em transfers)</description>",
        "    <Style id=\"routeWalk\">",
        "      <LineStyle><color>ff0d9488</color><width>4</width></LineStyle>",
        "    </Style>",
        "    <Style id=\"routeWalk2\">",
        "      <LineStyle><color>ff2563eb</color><width>4</width></LineStyle>",
        "    </Style>",
    ]

    folder_count = 0
    line_count = 0

    for day in DAYS:
        folder_count += 1
        folder_title = xml_escape.escape(layer_name(day))
        lines.append("    <Folder>")
        lines.append(f"      <name>{folder_title}</name>")
        lines.append(
            f"      <description>{xml_escape.escape(day['day_id'])} — ordem FAST TOURIST</description>"
        )

        for order, cat, name_pt, address in day["stops"]:
            lat, lng = coords_for(address)
            label = xml_escape.escape(sanitize_mymaps_name(f"{order:02d} - {name_pt}"))
            desc = xml_escape.escape(
                f"{CAT_PT.get(cat, cat)} — {address} — #{day['day_id']}"
            )
            lines.append("      <Placemark>")
            lines.append(f"        <name>{label}</name>")
            lines.append(f"        <description>{desc}</description>")
            lines.append("        <Point>")
            lines.append(f"          <coordinates>{lng:.6f},{lat:.6f},0</coordinates>")
            lines.append("        </Point>")
            lines.append("      </Placemark>")

        segments = route_segments_coords(day["stops"])
        for idx, seg in enumerate(segments, start=1):
            line_count += 1
            style = "routeWalk" if idx == 1 else "routeWalk2"
            seg_label = (
                "Rota a pé"
                if len(segments) == 1
                else f"Rota a pé (trecho {idx}/{len(segments)})"
            )
            lines.append("      <Placemark>")
            lines.append(f"        <name>{xml_escape.escape(seg_label)}</name>")
            lines.append(
                "        <description>Linha de referência na ordem FAST — não use como navegação entre cidades distantes.</description>"
            )
            lines.append(f"        <styleUrl>#{style}</styleUrl>")
            lines.append("        <LineString>")
            lines.append("          <tessellate>1</tessellate>")
            lines.append(f"          <coordinates>{kml_coords_line(seg)}</coordinates>")
            lines.append("        </LineString>")
            lines.append("      </Placemark>")

        lines.append("    </Folder>")

    lines.extend(["  </Document>", "</kml>", ""])
    KML_FILE.write_text("\n".join(lines), encoding="utf-8")
    return folder_count, line_count


def main() -> None:
    n = write_csvs()
    folders, routes = write_kml()
    print(
        f"OK: {n} paradas → {FULL_CSV.name}, {MYMAPS_CSV.name}, {KML_FILE.name} "
        f"({folders} pastas/dias, {routes} trechos de rota)"
    )


if __name__ == "__main__":
    main()
