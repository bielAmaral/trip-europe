"""Modo de transporte entre paradas consecutivas (mapas dia a dia)."""
from __future__ import annotations

import math
from urllib.parse import quote

Stop = tuple[int, str, str, str]  # order, category, name_pt, address

MODE_PT: dict[str, str] = {
    "walk": "A pé",
    "metro": "Metro",
    "train": "Trem",
    "bus": "Ônibus",
    "tram": "Elétrico",
    "flight": "Voo",
    "funicular": "Funicular",
    "taxi": "Táxi",
}

# Por dia: uma entrada por parada; None na primeira; (mode, hint) nas seguintes.
LEG_DETAILS: dict[str, list[tuple[str, str] | None]] = {
    "day-2026-11-19": [
        None,
        ("train", "S8 ou S1 → Hbf (~40 min)"),
        ("walk", "Check-in · ~5 min do Hbf"),
        ("metro", "S-Bahn ou U5 → Marienplatz"),
        ("walk", "~2 min"),
        ("walk", "~3 min"),
        ("walk", "~2 min"),
        ("walk", "~8 min"),
    ],
    "day-2026-11-20": [
        None,
        ("metro", "U4 Hbf → Odeonsplatz"),
        ("walk", "~3 min ao Hofgarten"),
        ("walk", "Ludwigstraße / Siegestor"),
        ("metro", "U3 ou U6 → parque"),
        ("walk", "Dentro do parque"),
        ("walk", "Eisbach → Chinesischer Turm"),
        ("metro", "U3/U6 → Sendlinger Tor"),
        ("walk", "Kaufingerstraße"),
        ("walk", "Glockenbach"),
    ],
    "day-2026-11-21": [
        None,
        ("walk", "~10 min até ZOB"),
        ("bus", "FlixBus ZOB → Füssen (~2h)"),
        ("bus", "Autocarro/regional → castelos"),
        ("walk", "Subida ao castelo"),
        ("walk", "Marienbrücke"),
        ("walk", "Opcional · lago"),
        ("bus", "Descida → Pulverturm"),
        ("bus", "FlixBus volta (~2h)"),
        ("walk", "ZOB → hotel"),
    ],
    "day-2026-11-22": [
        None,
        ("walk", "Se sobrar tempo"),
        ("walk", "Hotel → ZOB"),
        ("bus", "FlixBus → P+R Süd (~2h)"),
        ("metro", "P+R → hotel / centro"),
        ("walk", "Mirabellgarten"),
        ("walk", "Getreidegasse"),
        ("walk", "Dom"),
    ],
    "day-2026-11-23": [
        None,
        ("walk", "Subida · funicular ou pé"),
        ("walk", "Residenzplatz"),
        ("walk", "Dom"),
        ("walk", "Getreidegasse"),
        ("walk", "Mozartplatz"),
        ("walk", "Makartsteg"),
        ("walk", "Dark Eagle"),
    ],
    "day-2026-11-24": [
        None,
        ("walk", "Check-out → estação"),
        ("train", "ICE Salzburg → Wien Hbf"),
        ("metro", "U1/U2 → hotel Zipser"),
        ("metro", "U2 → Praterstern"),
        ("metro", "U1 + U4 → Naschmarkt"),
        ("metro", "U4/U2 → Donaukanal"),
        ("walk", "Noite no canal"),
    ],
    "day-2026-11-25": [
        None,
        ("metro", "U2 + U4 → Schönbrunn"),
        ("metro", "U4 → Stadtpark"),
        ("metro", "U4 ou a pé (~12 min)"),
        ("walk", "Graben"),
        ("walk", "Hofburg"),
        ("tram", "Elétrico 1/2/D no Ring"),
        ("walk", "Parlamento"),
    ],
    "day-2026-11-26": [
        None,
        ("walk", "Manhã livre"),
        ("metro", "U-Bahn → VIB"),
        ("bus", "FlixBus VIB → Most SNP"),
        ("tram", "Elétrico 93 / 1 / 3 / 7"),
        ("walk", "Staré Mesto"),
        ("walk", "Subida ao castelo"),
        ("walk", "Apollon"),
    ],
    "day-2026-11-27": [
        None,
        ("walk", "Hotel → Nivy"),
        ("bus", "FlixBus → Kelenföld (~2h35)"),
        ("metro", "M4 → Erzsébetváros"),
        ("walk", "Basílica"),
        ("walk", "Andrássy"),
        ("walk", "Ponte das Correntes"),
        ("walk", "Vista Buda"),
    ],
    "day-2026-11-28": [
        None,
        ("metro", "M2/M3 → Parlamento"),
        ("walk", "Margem do Danúbio"),
        ("metro", "M4 → Grande Mercado"),
        ("funicular", "Ponte → funicular ou bus 16"),
        ("walk", "Matthias Church"),
        ("walk", "Szimpla Kert"),
        ("walk", "Instant-Fogas"),
    ],
    "day-2026-11-29": [
        None,
        ("walk", "Bairro judaico"),
        ("tram", "Elétrico 4/6 → Margit"),
        ("walk", "Ilha Margarida"),
    ],
    "day-2026-11-30": [
        None,
        ("walk", "Último passeio"),
        ("bus", "100E → aeroporto BUD"),
        ("flight", "BUD → BER"),
        ("train", "FEX/S9 + U5 → Alexanderplatz"),
        ("walk", "Alexanderplatz"),
        ("walk", "Fernsehturm"),
    ],
    "day-2026-12-01": [
        None,
        ("metro", "U5 → Brandenburger Tor"),
        ("walk", "Portão de Brandemburgo"),
        ("walk", "Reichstag"),
        ("walk", "Tiergarten"),
        ("walk", "Memorial"),
        ("metro", "U1/S → East Side Gallery"),
        ("metro", "U5 volta"),
    ],
    "day-2026-12-02": [
        None,
        ("walk", "Unter den Linden"),
        ("walk", "Berliner Dom"),
        ("walk", "Lustgarten"),
        ("walk", "Museum Island"),
        ("walk", "Gendarmenmarkt"),
        ("metro", "U1/U9 → Ku'damm"),
    ],
    "day-2026-12-03": [
        None,
        ("metro", "S/U → Südkreuz"),
        ("bus", "FlixBus → Florenc (~4h30)"),
        ("metro", "Metro/tram → hotel"),
        ("walk", "Wenceslas Square"),
        ("walk", "Old Town Square"),
        ("walk", "Relógio astronómico"),
    ],
    "day-2026-12-04": [
        None,
        ("walk", "Charles Bridge"),
        ("walk", "Malá Strana"),
        ("walk", "Subida ao castelo"),
        ("walk", "Kampa"),
        ("walk", "Na Příkopě"),
        ("walk", "Palladium"),
        ("walk", "Old Town"),
        ("walk", "Termix"),
    ],
    "day-2026-12-05": [
        None,
        ("walk", "Último passeio"),
        ("metro", "Metro/bus → PRG"),
        ("flight", "PRG → BRU"),
        ("metro", "STIB → hotel Rogier"),
        ("walk", "Rue Neuve"),
    ],
    "day-2026-12-06": [
        None,
        ("walk", "Grand Place opcional"),
        ("metro", "Metro → Midi"),
        ("train", "SNCB → Bruges (~1h)"),
        ("walk", "Markt"),
        ("walk", "Belfry"),
        ("walk", "Rozenhoedkaai"),
        ("train", "SNCB volta → Bruxelas"),
        ("metro", "Metro → hotel"),
    ],
    "day-2026-12-07": [
        None,
        ("metro", "STIB/MIVB → aeroporto BRU"),
    ],
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def infer_leg(prev: Stop, curr: Stop, dist_km: float) -> tuple[str, str]:
    _po, pc, pn, _pa = prev
    _co, cc, cn, _ca = curr
    pn_l, cn_l = pn.lower(), cn.lower()

    if cc == "airport" and pc != "airport":
        if dist_km > 50:
            return "flight", "Voo"
        return "bus", "Autocarro aeroporto"

    if pc == "airport" and cc != "airport":
        if cc == "transport":
            return "train", "Comboio aeroporto"
        if cc == "hotel":
            return "train", "Comboio/metro do aeroporto"
        return "train", "Do aeroporto"

    if cc == "transport":
        if any(x in cn_l for x in ("flix", "zob", "nivy", "florenc", "kelenföld", "pulverturm", "vib", "most snp")):
            if pc in ("hotel", "sight"):
                return "walk" if dist_km < 2.5 else "metro", "Até terminal"
            return "bus", "FlixBus / autocarro"
        if "station" in cn_l or "bahnhof" in cn_l or "midi" in cn_l:
            return "train", "Comboio" if dist_km > 30 else "Metro/comboio urbano"

    if pc == "transport":
        if dist_km > 25:
            return "bus", "FlixBus / longa distância"
        if cc == "hotel":
            return "metro", "Até hotel"
        return "walk" if dist_km < 2 else "metro", ""

    if pc == "sight" and cc == "sight":
        if dist_km < 1.2:
            mins = max(3, int(dist_km * 12))
            return "walk", f"~{mins} min" if dist_km > 0.25 else ""
        if dist_km < 3.5:
            return "walk", f"~{int(dist_km * 12)} min"
        return "metro", "Transporte público"

    if pc == "hotel":
        if dist_km < 1.5:
            return "walk", ""
        if dist_km < 4:
            return "metro", "Metro / bonde"
        return "metro", "Transporte público"

    if dist_km > 25:
        return "bus", ""
    if dist_km > 4:
        return "metro", ""
    return "walk", ""


def resolve_leg(
    day_id: str,
    stop_index: int,
    prev: Stop,
    curr: Stop,
    dist_km: float,
) -> tuple[str, str]:
    legs = LEG_DETAILS.get(day_id)
    if legs and stop_index < len(legs) and legs[stop_index] is not None:
        return legs[stop_index]  # type: ignore[return-value]
    return infer_leg(prev, curr, dist_km)


def travelmode_for_maps(mode: str) -> str:
    if mode == "walk":
        return "walking"
    if mode == "flight":
        return "driving"
    return "transit"


def leg_maps_url(from_addr: str, to_addr: str, mode: str) -> str:
    if mode == "flight":
        return ""
    tm = travelmode_for_maps(mode)
    origin = quote(from_addr)
    dest = quote(to_addr)
    return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}&travelmode={tm}"
