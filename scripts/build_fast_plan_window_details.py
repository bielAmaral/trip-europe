#!/usr/bin/env python3
"""Gera data/fast-plan-window-details.json e aplica textos macro em index.html."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUT_JSON = ROOT / "data" / "fast-plan-window-details.json"

TOUR_PLACEHOLDER = re.compile(
    r"<strong>Rota a pé</strong>\s*—\s*abrir\s*<strong>Passo a passo no mapa</strong>",
    re.I,
)

# Detalhamento por janela (macro + subblocos no expandir). Horários de voo/trem/Flix não alterados.
WINDOW_SPECS: dict[str, dict] = {
    "day-2026-11-19": {
        "dayNotes": [],
        "windows": {
            "18:30–21:00": {
                "macro": (
                    "U-Bahn/S-Bahn hotel → <strong>Karlsplatz (Stachus)</strong> (~5 min) · "
                    "passeio leve 30 min (est.) · volta <strong>Hbf</strong> · jantar "
                    "<strong>REWE</strong> ou <strong>McDonald’s Hbf</strong> · dormir cedo (jet lag)"
                ),
                "blocks": [
                    {
                        "at": "18:30",
                        "durMin": 10,
                        "html": "Deslocação <strong>Hbf → Karlsplatz</strong> — <strong>U4/U5</strong> ou S-Bahn (est. 5 min)",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "18:40",
                        "durMin": 35,
                        "html": "Karlsplatz / Justizpalast — foto rápida, sem pressa",
                        "kind": "optional",
                    },
                    {
                        "at": "19:15",
                        "durMin": 15,
                        "html": "Volta <strong>Karlsplatz → Hbf</strong> (mesma linha)",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "19:30",
                        "durMin": 45,
                        "html": "Jantar leve <strong>REWE Arnulfstraße</strong> ou McDonald’s Hbf",
                        "kind": "food",
                    },
                ],
                "cutFirst": "Karlsplatz — ir direto jantar + hotel",
                "rainAlt": "Marienplatz arcadas + compras Hbf",
            },
        },
    },
    "day-2026-11-20": {
        "windows": {
            "12:15–17:00": {
                "macro": (
                    "<strong>Englischer Garten</strong> (Eisbach + Chinesischer Turm) → "
                    "<strong>U3/U6</strong> até Sendlinger Tor · "
                    "<strong>Asamkirche</strong> + <strong>Sendlinger Tor</strong> · "
                    "almoço no caminho, sem voltar ao hotel"
                ),
                "blocks": [
                    {
                        "at": "12:15",
                        "durMin": 15,
                        "html": "Metro até entrada norte do parque — definir pin no Maps",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "12:30",
                        "durMin": 90,
                        "html": "<strong>Eisbachwelle</strong> → <strong>Chinesischer Turm</strong> — sequência a pé, sem zigue-zague",
                        "kind": "must",
                    },
                    {
                        "at": "14:00",
                        "durMin": 45,
                        "html": "Almoço rápido no parque/quiosque; comprar água antes de sair",
                        "kind": "food",
                    },
                    {
                        "at": "14:45",
                        "durMin": 20,
                        "html": "<strong>U3/U6</strong> Universität → <strong>Sendlinger Tor</strong>",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "15:05",
                        "durMin": 45,
                        "html": "<strong>Asamkirche</strong> (interior se aberta) + <strong>Sendlinger Tor</strong> — ponto barroco curto e fotogênico",
                        "kind": "must",
                    },
                    {
                        "at": "15:50",
                        "durMin": 25,
                        "html": "Caminhar para Kaufingerstraße; deixar compras e souvenir no eixo do centro",
                        "kind": "transit",
                        "estimate": True,
                    },
                ],
                "cutFirst": "Asamkirche; manter parque + almoço",
            },
            "17:00–21:00": {
                "macro": (
                    "Compras <strong>Kaufingerstraße / Neuhauser</strong> (eixo único, pé) · "
                    "jantar <strong>REWE Arnulf</strong> ou <strong>Five Guys</strong> (Maps) · "
                    "mala Füssen · 1 transporte de volta ao hotel"
                ),
                "blocks": [
                    {
                        "at": "17:00",
                        "durMin": 120,
                        "html": "Shopping a pé — não cruzar cidade de novo",
                        "kind": "must",
                    },
                    {
                        "at": "19:00",
                        "durMin": 45,
                        "html": "Jantar rápido no eixo ou REWE hotel",
                        "kind": "food",
                    },
                    {
                        "at": "20:00",
                        "durMin": 60,
                        "html": "Mala + opcional noite Glockenbach (só se energia)",
                        "kind": "buffer",
                    },
                ],
            },
        },
    },
    "day-2026-11-21": {
        "dayNotes": [
            (
                "<strong>Dia crítico:</strong> a volta <strong>Flix 16:00</strong> é única. "
                "Chegar ao Pulverturm até <strong>15:45</strong>; se o castelo atrasar, "
                "cortar o interior antes de cortar o transporte."
            ),
        ],
        "windows": {
            "07:30–07:45": {
                "macro": "Café simples e mochila leve; sair sem despachar bagagem.",
                "blocks": [
                    {
                        "at": "07:30",
                        "durMin": 15,
                        "html": "Café rápido, água, documento e bilhete Flix à mão",
                        "kind": "must",
                    },
                ],
            },
            "07:45": {
                "macro": "Hotel → München ZOB para embarque.",
                "blocks": [
                    {
                        "at": "07:45",
                        "durMin": 15,
                        "html": "Caminhar do B&B Hotel até a plataforma do ZOB; estar lá antes de 07:50",
                        "kind": "transit",
                        "estimate": True,
                    },
                ],
            },
            "08:00–10:15": {
                "macro": "FlixBus München ZOB → Füssen Kemptener Str.; não confundir com a parada de volta.",
                "blocks": [
                    {
                        "at": "08:00",
                        "durMin": 135,
                        "html": "FlixBus até <strong>Füssen Kemptener Str.</strong>; guardar o endereço da volta (<strong>Pulverturm</strong>)",
                        "kind": "transit",
                        "estimate": True,
                    },
                ],
            },
            "11:45–12:15": {
                "macro": "Tourist Info → parada do ônibus 73/78 → Hohenschwangau.",
                "blocks": [
                    {
                        "at": "11:45",
                        "durMin": 30,
                        "html": "Sair do centro, localizar a parada na estação e embarcar no <strong>73/78</strong> para Hohenschwangau",
                        "kind": "transit",
                        "estimate": True,
                    },
                ],
            },
            "12:15–15:00": {
                "macro": "Hohenschwangau → Neuschwanstein → Marienbrücke; lanche do kit.",
                "blocks": [
                    {
                        "at": "12:15",
                        "durMin": 35,
                        "html": "Chegar a Hohenschwangau, confirmar entrada/shuttle e iniciar a subida",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "12:50",
                        "durMin": 75,
                        "html": "Neuschwanstein — interior somente se o slot ~13:00 estiver confirmado; caso contrário, exterior",
                        "kind": "must",
                    },
                    {
                        "at": "14:05",
                        "durMin": 45,
                        "html": "Marienbrücke + fotos; comer o kit sem prolongar a parada",
                        "kind": "must",
                    },
                    {
                        "at": "14:50",
                        "durMin": 10,
                        "html": "Iniciar a descida imediatamente para não comprometer o Flix",
                        "kind": "transit",
                        "estimate": True,
                    },
                ],
                "cutFirst": "Interior do castelo; depois qualquer desvio ao Alpsee",
            },
            "15:00–15:45": {
                "macro": "Descida → 73/78 → caminhada até Pulverturm.",
                "blocks": [
                    {
                        "at": "15:00",
                        "durMin": 30,
                        "html": "Ônibus 73/78 até Füssen e caminhada para <strong>Pulverturm</strong>",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "15:30",
                        "durMin": 15,
                        "html": "Chegar à parada, localizar o ponto exato e aguardar o Flix 16:00",
                        "kind": "must",
                    },
                ],
            },
            "16:00–18:00": {
                "macro": "FlixBus Pulverturm → München ZOB; não planejar passeio na chegada.",
                "blocks": [
                    {
                        "at": "16:00",
                        "durMin": 120,
                        "html": "FlixBus de volta ao ZOB; usar o trecho para descansar",
                        "kind": "transit",
                        "estimate": True,
                    },
                ],
            },
            "18:00–19:30": {
                "macro": "Jantar leve e mala para Salzburgo; dormir cedo.",
                "blocks": [
                    {
                        "at": "18:00",
                        "durMin": 45,
                        "html": "Voltar ao hotel, banho e jantar simples perto da estação",
                        "kind": "food",
                    },
                    {
                        "at": "18:45",
                        "durMin": 45,
                        "html": "Separar mala e kit para o <strong>ICE 1215 às 12:09</strong> do dia seguinte",
                        "kind": "must",
                    },
                ],
            },
        },
    },
    "day-2026-11-22": {
        "windows": {
            "14:30–21:00": {
                "macro": (
                    "Hotel → <strong>Mirabellgarten</strong> (pé, 10 min) → "
                    "<strong>Getreidegasse</strong> → <strong>Dom</strong> (exterior) · "
                    "jantar Altstadt · sem voltar ao hotel até o fim"
                ),
                "blocks": [
                    {
                        "at": "14:30",
                        "durMin": 45,
                        "html": "Check-in Lasserhof · deixar bagagem",
                        "kind": "buffer",
                    },
                    {
                        "at": "15:15",
                        "durMin": 45,
                        "html": "Mirabell + foto Nonnbergweg",
                        "kind": "must",
                    },
                    {
                        "at": "16:00",
                        "durMin": 120,
                        "html": "Loop Altstadt: Getreidegasse, Mozartplatz, Dom",
                        "kind": "must",
                    },
                    {
                        "at": "18:00",
                        "durMin": 90,
                        "html": "Jantar barato na zona já a pé · volta hotel (~15 min)",
                        "kind": "food",
                    },
                    {
                        "at": "19:30",
                        "durMin": 90,
                        "html": "Hotel: banho, separar roupa do dia seguinte e descanso; não abrir outro bairro",
                        "kind": "buffer",
                    },
                ],
                "cutFirst": "Mirabell se ICE/check-in atrasar",
            },
        },
    },
    "day-2026-11-23": {
        "windows": {
            "14:00–21:00": {
                "macro": (
                    "Pé <strong>Makartsteg</strong> → margem <strong>Salzach</strong> · "
                    "<strong>Mozart Geburtshaus</strong> / Getreidegasse · "
                    "jantar leve · mala + dormir cedo (RJX <strong>11:07</strong> amanhã)"
                ),
                "blocks": [
                    {
                        "at": "14:00",
                        "durMin": 45,
                        "html": "<strong>Mozart Geburtshaus</strong> (fachada/entrada curta) + Getreidegasse — só se a Festung não ocupar o horário",
                        "kind": "must",
                    },
                    {
                        "at": "15:15",
                        "durMin": 60,
                        "html": "<strong>Makartsteg</strong> → margem do Salzach — fotos e caminhada linear",
                        "kind": "must",
                    },
                    {
                        "at": "16:15",
                        "durMin": 45,
                        "html": "Souvenir compacto: Mozartkugel/Fürst ou ímã na Getreidegasse; sem desvio",
                        "kind": "optional",
                    },
                    {
                        "at": "17:00",
                        "durMin": 90,
                        "html": "Jantar cedo no centro e voltar ao Lasserhof a pé",
                        "kind": "food",
                    },
                    {
                        "at": "18:30",
                        "durMin": 90,
                        "html": "Mala, documentos e dormir; não abrir novo eixo turístico",
                        "kind": "must",
                    },
                    {
                        "at": "20:00",
                        "durMin": 60,
                        "html": "Descanso no hotel e alarme para o RJX das 11:07",
                        "kind": "buffer",
                    },
                ],
                "cutFirst": "Mozart Geburtshaus/souvenir; manter Makartsteg + jantar",
            },
        },
    },
    "day-2026-11-24": {
        "windows": {
            "17:00–21:00": {
                "macro": (
                    "<strong>U1/U4</strong> → <strong>Donaukanal</strong> (est. 15 min) · "
                    "passeio margem · jantar <strong>Billa</strong> Zipser · compras leves · "
                    "volta 1 linha metro"
                ),
                "blocks": [
                    {
                        "at": "17:00",
                        "durMin": 20,
                        "html": "Zipser → Schwedenplatz / Nestroyplatz (canal)",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "17:20",
                        "durMin": 70,
                        "html": "Donaukanal — mural + bancos",
                        "kind": "must",
                    },
                    {
                        "at": "18:30",
                        "durMin": 45,
                        "html": "Volta hotel + Billa",
                        "kind": "food",
                    },
                    {
                        "at": "19:15",
                        "durMin": 105,
                        "html": "Compras matriz 24 nov / noite a&o bar (opcional)",
                        "kind": "optional",
                    },
                ],
                "cutFirst": "Prater (já feito manhã)",
            },
        },
    },
    "day-2026-11-25": {
        "windows": {
            "12:15–21:00": {
                "macro": (
                    "Almoço <strong>Anker Brot</strong> / Billa · "
                    "<strong>Ring</strong> sentido horário a pé: <strong>Stephansdom</strong> → "
                    "<strong>Graben</strong> → <strong>Hofburg</strong> → "
                    "<strong>Rathaus/Parlament</strong> (fachadas, luzes) · "
                    "Manner/ímã no eixo Graben · jantar · mala Bratislava"
                ),
                "blocks": [
                    {
                        "at": "12:15",
                        "durMin": 45,
                        "html": "Almoço perto do fim do tour (Staatsoper / Karlsplatz)",
                        "kind": "food",
                    },
                    {
                        "at": "12:45",
                        "durMin": 150,
                        "html": "<strong>Ring exterior</strong> — Stephansdom → Graben → Hofburg/Heldenplatz → Rathaus/Parlament, sem zig-zag",
                        "kind": "must",
                    },
                    {
                        "at": "15:15",
                        "durMin": 45,
                        "html": "Rathausplatz/Parlament iluminados e fotos; se houver mercado, uma volta curta",
                        "kind": "must",
                    },
                    {
                        "at": "16:00",
                        "durMin": 30,
                        "html": "Souvenir no próprio eixo: Manner/ímã em Graben-Stephansplatz — cortar se fila",
                        "kind": "optional",
                        "cutFirst": True,
                    },
                    {
                        "at": "16:30",
                        "durMin": 60,
                        "html": "Hotel → separar mala e documentos para Bratislava",
                        "kind": "buffer",
                    },
                    {
                        "at": "17:30",
                        "durMin": 90,
                        "html": "Jantar no centro e voltar cedo; Flix só amanhã às 12:35",
                        "kind": "food",
                    },
                    {
                        "at": "19:00",
                        "durMin": 105,
                        "html": "Hotel: banho, fechar mochila e descanso; sem segundo eixo turístico",
                        "kind": "buffer",
                    },
                ],
                "cutFirst": "Souvenir e interior; manter Ring exterior",
            },
        },
    },
    "day-2026-11-26": {
        "windows": {
            "14:00–21:00": {
                "macro": (
                    "Metro → hotel · <strong>Staré Mesto</strong> (centro a pé) → "
                    "<strong>Castle</strong> (exterior, subida ~20 min) · "
                    "jantar Old Town · 1 ida/volta hotel"
                ),
                "blocks": [
                    {
                        "at": "14:00",
                        "durMin": 60,
                        "html": "Check-in Downtown Backpackers · deixar mochila",
                        "kind": "buffer",
                    },
                    {
                        "at": "15:00",
                        "durMin": 120,
                        "html": "Main Square → Michael's Gate → Castle miradouro",
                        "kind": "must",
                    },
                    {
                        "at": "17:00",
                        "durMin": 90,
                        "html": "Jantar centro (mesma área)",
                        "kind": "food",
                    },
                    {
                        "at": "18:30",
                        "durMin": 150,
                        "html": "Volta a pé hotel · Obchodná leve (opcional)",
                        "kind": "optional",
                    },
                ],
                "cutFirst": "Castle (ficar só Staré Mesto)",
            },
        },
    },
    "day-2026-11-27": {
        "windows": {
            "17:00–21:00": {
                "macro": (
                    "<strong>Shoes on the Danube</strong> → <strong>Chain Bridge</strong> a pé · "
                    "margem Pest com vista <strong>Buda Castle</strong> (exterior) · jantar perto do hotel · "
                    "sem subir Buda hoje"
                ),
                "blocks": [
                    {
                        "at": "17:00",
                        "durMin": 90,
                        "html": "<strong>Shoes on the Danube</strong> (30 min) → <strong>Chain Bridge</strong> (60 min) — luz do fim de tarde",
                        "kind": "must",
                    },
                    {
                        "at": "18:30",
                        "durMin": 45,
                        "html": "Jantar Astoria / Erzsébet körút",
                        "kind": "food",
                    },
                    {
                        "at": "19:15",
                        "durMin": 105,
                        "html": "Descanso pós-viagem — sem ruin bar",
                        "kind": "buffer",
                    },
                ],
            },
        },
    },
    "day-2026-11-28": {
        "windows": {
            "17:00–21:00": {
                "macro": (
                    "Buffer hotel · <strong>Szimpla Kert</strong> ou <strong>Instant</strong> "
                    "(ruin bars — confirmar fila Maps) · jantar leve antes/depois · "
                    "último metro ~23h (est.)"
                ),
                "blocks": [
                    {
                        "at": "17:00",
                        "durMin": 60,
                        "html": "Descanso + troca de roupa",
                        "kind": "buffer",
                    },
                    {
                        "at": "18:00",
                        "durMin": 45,
                        "html": "Jantar rápido Kazinczy / ruin bar food",
                        "kind": "food",
                    },
                    {
                        "at": "19:00",
                        "durMin": 120,
                        "html": "Ruin bar — 1 só se cansado",
                        "kind": "must",
                    },
                ],
                "cutFirst": "Segundo bar",
            },
        },
    },
    "day-2026-11-29": {
        "windows": {
            "09:00–10:45": {
                "macro": "Café, comprar água/lanche no Tesco Kazinczy 16 e caminhar até Madách tér.",
                "blocks": [
                    {
                        "at": "09:00",
                        "durMin": 30,
                        "html": "Café e separar apenas o necessário para o tour",
                        "kind": "food",
                    },
                    {
                        "at": "09:30",
                        "durMin": 20,
                        "html": "Tesco Kazinczy 16 — água e lanche para a tarde",
                        "kind": "must",
                    },
                    {
                        "at": "09:50",
                        "durMin": 35,
                        "html": "Caminhar até <strong>Madách tér / ponto da reserva</strong>; chegar 10 min antes",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "10:25",
                        "durMin": 20,
                        "html": "Buffer no ponto do guia e conferir reserva",
                        "kind": "buffer",
                    },
                ],
            },
            "13:30–17:00": {
                "macro": "Fim do tour no Jewish Quarter → Margaret Bridge/Margitsziget; usar como passeio leve e descanso.",
                "blocks": [
                    {
                        "at": "13:30",
                        "durMin": 25,
                        "html": "Almoço rápido no bairro e elétrico <strong>4/6</strong> rumo a <strong>Margaret Bridge</strong>",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "13:55",
                        "durMin": 20,
                        "html": "Margaret Bridge — travessia curta e vista do Danúbio",
                        "kind": "must",
                    },
                    {
                        "at": "14:15",
                        "durMin": 90,
                        "html": "Margitsziget — caminhada exterior sem tentar dar a volta inteira",
                        "kind": "optional",
                    },
                    {
                        "at": "15:45",
                        "durMin": 75,
                        "html": "Voltar ao Panorama Central, banho e descanso antes de arrumar a mala",
                        "kind": "buffer",
                    },
                ],
                "cutFirst": "Margitsziget; voltar ao hotel após o almoço se estiver cansado",
            },
            "17:00–21:00": {
                "macro": "Jantar cedo, fechar mala para o voo e deixar o 100E preparado.",
                "blocks": [
                    {
                        "at": "17:00",
                        "durMin": 60,
                        "html": "Jantar leve no eixo <strong>Astoria</strong> / Károly körút, perto do hotel",
                        "kind": "food",
                    },
                    {
                        "at": "18:00",
                        "durMin": 90,
                        "html": "Fechar mala, separar passaporte/boarding e confirmar terminal do voo",
                        "kind": "must",
                    },
                    {
                        "at": "19:30",
                        "durMin": 90,
                        "html": "Descanso e sono; não incluir banho termal longo nem ruin bar",
                        "kind": "buffer",
                    },
                ],
            },
        },
    },
    "day-2026-11-30": {
        "windows": {
            "14:00–21:00": {
                "macro": (
                    "BER → hotel: <strong>FEX/S9</strong> + <strong>U5</strong> (ver transit) · "
                    "check-in Premier Inn Alex · "
                    "<strong>Alexanderplatz</strong> + <strong>Fernsehturm</strong> (exterior) · "
                    "jantar <strong>Rewe To Go</strong> Alex ou <strong>Five Guys</strong> Alex 2"
                ),
                "blocks": [
                    {
                        "at": "14:00",
                        "durMin": 75,
                        "html": "Aeroporto → Alex (est. 45–60 min total)",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "15:15",
                        "durMin": 45,
                        "html": "Check-in / banho rápido",
                        "kind": "buffer",
                    },
                    {
                        "at": "16:00",
                        "durMin": 90,
                        "html": "Alex + Fernsehturm World Time — só exterior",
                        "kind": "must",
                    },
                    {
                        "at": "17:30",
                        "durMin": 90,
                        "html": "Jantar Rewe To Go / Five Guys · dormir cedo",
                        "kind": "food",
                    },
                    {
                        "at": "19:00",
                        "durMin": 120,
                        "html": "Hotel: conferir bilhete, carregar telemóvel e dormir; Berlim começa de verdade amanhã",
                        "kind": "buffer",
                    },
                ],
                "cutFirst": "Fernsehturm — só praça",
                "rainAlt": "Alex arcade + Rewe",
            },
        },
    },
    "day-2026-12-01": {
        "dayNotes": [
            (
                "<strong>Lavanderia:</strong> fazer preferencialmente "
                "<strong>2 dez 07:30–09:00</strong> antes do tour Kreuzberg, perto de Alex. "
                "<strong>Schleudertraum</strong> (ou equivalente): endereço/horário "
                "<em>confirmar no Maps</em> antes de ir."
            ),
        ],
        "windows": {
            "10:30–14:00": {
                "macro": (
                    "<strong>Topografia do Terror</strong> ou <strong>cúpula do Reichstag</strong> "
                    "(conforme reserva/local do tour) · almoço <strong>Rewe To Go Friedrichstraße</strong> · "
                    "deslocação ao encontro tour <strong>14:30</strong> — "
                    "<strong>U-Bahn Anton-Wilhelm-Amo</strong> (ponto na reserva; est. 20–25 min do Mitte)"
                ),
                "blocks": [
                    {
                        "at": "10:30",
                        "durMin": 20,
                        "html": "Fim do bloco da manhã em Mitte · banheiro, água e confirmar horário do tour",
                        "kind": "buffer",
                    },
                    {
                        "at": "10:50",
                        "durMin": 45,
                        "html": "Almoço Rewe To Go Friedrichstraße ou snack",
                        "kind": "food",
                    },
                    {
                        "at": "11:35",
                        "durMin": 60,
                        "html": "<strong>Topografia do Terror</strong> por 45–60 min; se houver reserva para a cúpula, usar a cúpula do Reichstag e não fazer os dois",
                        "kind": "must",
                    },
                    {
                        "at": "12:35",
                        "durMin": 35,
                        "html": "U5/U55 ou S-Bahn rumo ao encontro — rota final conforme a reserva; chegar com margem",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "13:10",
                        "durMin": 50,
                        "html": "Buffer no ponto do guia, banheiro e conferência da reserva; bilhete AB ativo",
                        "kind": "must",
                    },
                ],
            },
            "17:30–21:00": {
                "macro": (
                    "Tour termina em Mitte → deslocação até <strong>Warschauer Straße</strong> · "
                    "<strong>East Side Gallery</strong> por 30 min · "
                    "<strong>S-Bahn</strong> → <strong>Alexanderplatz</strong> · "
                    "jantar · <strong>Alexanderplatz à noite</strong> · "
                    "opcional <strong>Generator</strong> às 21h"
                ),
                "blocks": [
                    {
                        "at": "17:30",
                        "durMin": 40,
                        "html": (
                            "Fim do tour em Mitte → seguir a estação indicada pelo guia e "
                            "ir até <strong>Warschauer Straße</strong> — estimativa 30–40 min"
                        ),
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "18:10",
                        "durMin": 30,
                        "html": (
                            "<strong>East Side Gallery</strong> — trecho curto a partir de "
                            "Warschauer Straße; fotos e mural principal"
                        ),
                        "kind": "must",
                        "cutFirst": True,
                    },
                    {
                        "at": "18:40",
                        "durMin": 20,
                        "html": (
                            "<strong>S3/S5/S7/S9</strong> de Warschauer Straße → "
                            "<strong>Alexanderplatz</strong> — não usar U1 como rota direta"
                        ),
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "19:00",
                        "durMin": 75,
                        "html": "Jantar em <strong>Alexanderplatz</strong> — Five Guys Alex 2 ou Rewe Alex",
                        "kind": "food",
                    },
                    {
                        "at": "20:15",
                        "durMin": 30,
                        "html": (
                            "<strong>Alexanderplatz à noite</strong> — Fernsehturm exterior, "
                            "Weltzeituhr e Rotes Rathaus; depois hotel ou "
                            "<strong>Generator</strong> às 21h se houver reserva"
                        ),
                        "kind": "must",
                    },
                ],
                "cutFirst": "East Side Gallery — ir direto a Alexanderplatz se o tour atrasar",
                "rainAlt": "Generator / Alex arcade",
            },
        },
    },
    "day-2026-12-02": {
        "dayNotes": [
            (
                "<strong>Lavanderia (preferida):</strong> "
                "<strong>07:30–09:00</strong> antes do tour — self-service perto Alex; "
                "horário/endereço <em>confirmar no Maps</em>."
            ),
        ],
        "windows": {
            "07:30–09:00": {
                "macro": (
                    "<em>Slot preferido lavanderia</em> (confirmar loja no Maps) · "
                    "terminar secagem antes de sair"
                ),
                "blocks": [
                    {
                        "at": "07:30",
                        "durMin": 90,
                        "html": "Lavanderia + secar roupa (se necessário) — sair até 09:00",
                        "kind": "optional",
                    },
                ],
            },
            "09:00–10:00": {
                "macro": (
                    "Café to-go · caminho até <strong>Moritzplatz</strong> · "
                    "chegar ao encontro do tour (<strong>Kreuzberg</strong> — ver reserva)"
                ),
                "blocks": [
                    {
                        "at": "09:00",
                        "durMin": 30,
                        "html": "Café to-go e preparar a mochila",
                        "kind": "food",
                    },
                    {
                        "at": "09:30",
                        "durMin": 30,
                        "html": "Hotel/Alex → <strong>Moritzplatz</strong> — transporte conforme BVG/Maps",
                        "kind": "transit",
                        "estimate": True,
                    },
                ],
            },
            "13:00–16:00": {
                "macro": (
                    "Almoço Kreuzberg (<strong>Markthalle Neun</strong> área ou Döner) · "
                    "<strong>Oberbaumbrücke</strong> no caminho · "
                    "<strong>U1/U8</strong> → <strong>Alexanderplatz</strong> · pausa hotel / banheiro"
                ),
                "blocks": [
                    {
                        "at": "13:00",
                        "durMin": 45,
                        "html": "Almoço na zona do fim do tour",
                        "kind": "food",
                    },
                    {
                        "at": "13:45",
                        "durMin": 30,
                        "html": "Caminhar até <strong>Oberbaumbrücke</strong> e atravessar pela vista do Spree",
                        "kind": "must",
                    },
                    {
                        "at": "14:15",
                        "durMin": 30,
                        "html": "<strong>U1/U8</strong> rumo Alexanderplatz — no máximo 1 troca",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "14:45",
                        "durMin": 75,
                        "html": "Pausa Alex — banheiro, água e voltar ao hotel apenas se necessário; não recomeçar Mitte",
                        "kind": "buffer",
                    },
                ],
            },
            "16:00–21:00": {
                "macro": (
                    "Compras hub: <strong>Alexa / Primark Alex</strong> → "
                    "<strong>U2</strong> Alex → <strong>Zoologischer Garten</strong> · "
                    "Ku’damm / <strong>Primark</strong> · mercados Natal "
                    "(opcional) · volta U2 · jantar · <strong>mala Praga</strong>"
                ),
                "blocks": [
                    {
                        "at": "16:00",
                        "durMin": 75,
                        "html": "Alexa + Primark Alexanderstraße",
                        "kind": "must",
                    },
                    {
                        "at": "17:15",
                        "durMin": 20,
                        "html": "U2 Alex → Zoologischer Garten",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "17:35",
                        "durMin": 100,
                        "html": "Ku’damm + Primark ocidental",
                        "kind": "must",
                    },
                    {
                        "at": "19:15",
                        "durMin": 45,
                        "html": "U2 volta Alex · jantar Five Guys/Rewe",
                        "kind": "food",
                    },
                    {
                        "at": "20:00",
                        "durMin": 60,
                        "html": "Mala Flix amanhã 10:20",
                        "kind": "must",
                    },
                ],
                "cutFirst": "Gendarmenmarkt / segundo eixo compras",
            },
        },
    },
    "day-2026-12-03": {
        "windows": {
            "14:30–17:30": {
                "macro": (
                    "Florenc → <strong>Metro C</strong> Florenc → <strong>I.P. Pavlova</strong> "
                    "(~2 min, Maps) + pé <strong>Hotel Alton</strong> · check-in · "
                    "jantar leve <strong>Albert Legerova</strong> / Billa perto"
                ),
                "blocks": [
                    {
                        "at": "14:30",
                        "durMin": 40,
                        "html": "Florenc → hotel (PID — validar bilhete)",
                        "kind": "transit",
                        "estimate": True,
                    },
                    {
                        "at": "15:10",
                        "durMin": 60,
                        "html": "Check-in + descanso pós Flix",
                        "kind": "buffer",
                    },
                    {
                        "at": "16:10",
                        "durMin": 50,
                        "html": "Jantar perto hotel — centro velho amanhã com guia",
                        "kind": "food",
                    },
                ],
            },
            "17:30–21:00": {
                "macro": (
                    "Opcional: <strong>Metro C</strong> → <strong>Wenceslas Square</strong> "
                    "(exterior, 30–40 min) · volta hotel · dormir cedo"
                ),
                "blocks": [
                    {
                        "at": "17:30",
                        "durMin": 45,
                        "html": "Wenceslas — só se energia",
                        "kind": "optional",
                        "cutFirst": True,
                    },
                    {
                        "at": "18:15",
                        "durMin": 165,
                        "html": "Hotel — sono para tour 4 dez",
                        "kind": "buffer",
                    },
                ],
                "cutFirst": "Wenceslas inteiro",
            },
        },
    },
    "day-2026-12-04": {
        "windows": {
            "17:45–21:00": {
                "macro": (
                    "Compras <strong>Na Příkopě / Palladium</strong> (mesma zona, pé) · "
                    "jantar mall ou <strong>Billa</strong> · "
                    "noite <a href=\"#explorar-hostels-ancora\">Sophie's</a> + Vinohrady (opcional) · "
                    "1 metro ida/volta hotel"
                ),
                "blocks": [
                    {
                        "at": "17:45",
                        "durMin": 90,
                        "html": "Na Příkopě → Palladium — compras concentradas na mesma zona, sem cruzar a cidade",
                        "kind": "must",
                    },
                    {
                        "at": "19:15",
                        "durMin": 45,
                        "html": "Jantar no Palladium/Na Příkopě; comprar água e lanche do voo",
                        "kind": "food",
                    },
                    {
                        "at": "20:00",
                        "durMin": 30,
                        "html": "Sophie's Hostel apenas se estiver no caminho e houver energia; caso contrário, voltar ao Alton e dormir",
                        "kind": "optional",
                    },
                ],
                "cutFirst": "Vinohrady noite",
            },
        },
    },
    "day-2026-12-05": {
        "windows": {
            "08:00–08:30": {
                "macro": "Kit de almoço no <strong>Albert Legerova 75</strong> — confirmar abertura no Maps",
                "blocks": [
                    {
                        "at": "08:00",
                        "durMin": 30,
                        "html": "Comprar água + kit de voo antes do check-out",
                        "kind": "food",
                    }
                ],
            },
            "08:30–09:30": {
                "macro": "Check-out <strong>Alton</strong> · Metro C/A → <strong>Veleslavín</strong> · ônibus 119 → PRG",
                "blocks": [
                    {
                        "at": "08:30",
                        "durMin": 60,
                        "html": "Hotel → PRG via Metro C/A + ônibus <strong>119</strong> — estimativa, confirmar PID",
                        "kind": "transit",
                        "estimate": True,
                    }
                ],
            },
            "09:30–12:00": {
                "macro": "PRG: bagagem, segurança e espera para Ryanair 12:30",
                "blocks": [
                    {
                        "at": "09:30",
                        "durMin": 150,
                        "html": "Chegar ao terminal, despachar bagagem e passar pela segurança",
                        "kind": "buffer",
                    }
                ],
            },
            "12:30–14:00": {
                "macro": "Voo <strong>PRG → CRL</strong> (Charleroi) · Ryanair FR 69",
                "blocks": [
                    {
                        "at": "12:30",
                        "durMin": 90,
                        "html": "Voo para <strong>Charleroi</strong> — não confundir com Zaventem",
                        "kind": "transit",
                    }
                ],
            },
            "14:30–16:00": {
                "macro": "Ônibus <strong>Flibco</strong> CRL → Bruxelles-Midi (~1h) — horário depende da fila",
                "blocks": [
                    {
                        "at": "14:30",
                        "durMin": 90,
                        "html": "Aeroporto → Midi; reservar margem para desembarque e embarque no ônibus",
                        "kind": "transit",
                        "estimate": True,
                    }
                ],
            },
            "16:00–18:00": {
                "macro": "Midi → <strong>Rogier</strong> · check-in <strong>Colonies</strong> · deixar mala",
                "blocks": [
                    {
                        "at": "16:00",
                        "durMin": 120,
                        "html": "Metro 2/6 até Rogier, check-in e pausa — confirmar recepção",
                        "kind": "buffer",
                        "estimate": True,
                    }
                ],
            },
            "18:00–21:00": {
                "macro": "<strong>Rue Neuve</strong> + jantar <strong>Five Guys</strong> · encontro com a prima",
                "blocks": [
                    {
                        "at": "18:00",
                        "durMin": 180,
                        "html": "Jantar e encontro no eixo Rue Neuve; voltar cedo ao hotel",
                        "kind": "food",
                    }
                ],
            },
        },
    },
    "day-2026-12-06": {
        "dayNotes": [
            "<strong>Domingo:</strong> confirmar no Maps o que estará aberto; tratar compras como buffer, não como compromisso."
        ],
        "windows": {
            "10:00–13:00": {
                "macro": "<strong>Grand Place</strong> → <strong>Galeries Saint-Hubert</strong> → <strong>Manneken Pis</strong>/<strong>Bourse</strong> — circuito central a pé",
                "blocks": [
                    {
                        "at": "10:00",
                        "durMin": 180,
                        "html": "Grand Place → Galeries Saint-Hubert → Manneken Pis → Bourse; confirmar abertura de interiores e usar lojas de chocolate abertas apenas se estiverem no caminho",
                        "kind": "must",
                    }
                ],
            },
            "13:00–15:00": {
                "macro": "Almoço no centro · <strong>Mont des Arts</strong> opcional",
                "blocks": [
                    {
                        "at": "13:00",
                        "durMin": 120,
                        "html": "Almoço Chez Léon/Exki ou equivalente aberto no domingo · Mont des Arts se houver energia",
                        "kind": "food",
                        "estimate": True,
                    }
                ],
            },
            "15:00–17:00": {
                "macro": "Compras buffer na <strong>Rue Neuve</strong> · Tax Free",
                "blocks": [
                    {
                        "at": "15:00",
                        "durMin": 120,
                        "html": "Resolver apenas o que faltou; confirmar lojas abertas e guardar comprovantes",
                        "kind": "optional",
                        "cutFirst": True,
                    }
                ],
            },
            "17:00–21:00": {
                "macro": "Mala 100% · jantar leve · dormir cedo para o voo",
                "blocks": [
                    {
                        "at": "17:00",
                        "durMin": 120,
                        "html": "Fechar mala, separar passaporte/boarding e Tax Free",
                        "kind": "must",
                    },
                    {
                        "at": "19:00",
                        "durMin": 120,
                        "html": "Jantar leve perto do hotel e dormir cedo",
                        "kind": "food",
                    },
                ],
                "cutFirst": "Compras buffer",
            },
        },
    },
    "day-2026-12-07": {
        "windows": {
            "03:00": {
                "macro": "<strong>Alarme</strong> · documentos e bagagem já separados na noite anterior",
                "blocks": [
                    {
                        "at": "03:00",
                        "durMin": 30,
                        "html": "Acordar, banheiro, conferir passaporte e boarding",
                        "kind": "must",
                    }
                ],
            },
            "03:30–04:30": {
                "macro": "Bolt/táxi hotel → <strong>BRU Zaventem</strong> — reserva recomendada",
                "blocks": [
                    {
                        "at": "03:30",
                        "durMin": 60,
                        "html": "Transferência para o aeroporto; não depender de transporte urbano sem confirmar operação noturna",
                        "kind": "transit",
                        "estimate": True,
                    }
                ],
            },
            "05:00–07:00": {
                "macro": "Check-in Iberia · segurança · Tax Free · café",
                "blocks": [
                    {
                        "at": "05:00",
                        "durMin": 120,
                        "html": "Check-in/segurança e chegada ao portão antes do embarque",
                        "kind": "buffer",
                    }
                ],
            },
            "07:00": {
                "macro": "Voo <strong>BRU → MAD → GRU</strong> · IB0604 + IB0271",
                "blocks": [
                    {
                        "at": "07:00",
                        "durMin": 30,
                        "html": "Embarque — conferir portão e conexão no app da Iberia",
                        "kind": "transit",
                    }
                ],
            },
        },
    },
}


def parse_day_chunk(html: str, day_id: str) -> str | None:
    """Return one complete day block, including nested transit/tour details."""
    start_match = re.search(
        rf'<details class="day" id="{re.escape(day_id)}"[^>]*>',
        html,
        flags=re.IGNORECASE,
    )
    if not start_match:
        return None

    tag_re = re.compile(r"</?details\b[^>]*>", re.IGNORECASE)
    depth = 0
    for tag_match in tag_re.finditer(html, start_match.start()):
        tag = tag_match.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return html[start_match.start() : tag_match.end()]
        else:
            depth += 1
    return None


def tour_macros_for_day(day_html: str) -> list[str]:
    routes = re.findall(
        r'<details class="card walk-route[^"]*"[^>]*>.*?<summary>(.*?)</summary>.*?<ol class="walk-route__stops">(.*?)</ol>',
        day_html,
        flags=re.DOTALL,
    )
    macros = []
    for summary, stops_html in routes:
        stop_titles = re.findall(r"<li><strong>([^<]+)</strong>", stops_html)
        n = len(stop_titles)
        summary_plain = re.sub(r"<[^>]+>", "", summary).strip()
        meet = re.search(r"início\s*<strong>([^<]+)</strong>|·\s*<strong>([^<]+)</strong>\s*·", summary, re.I)
        meet_txt = (meet.group(1) or meet.group(2) or "").strip() if meet else ""
        duration = re.search(
            r"~\s*([\d.]+\s*h\d+|[\d.]+\s*h(?:\s+\d+\s*min)?|\d+\s*min)",
            summary_plain,
            re.I,
        )
        dur_txt = duration.group(1).replace(" ", "") if duration else "2–3h"
        first = stop_titles[0] if stop_titles else "parada 1"
        last = stop_titles[-1] if stop_titles else first
        theme = summary_plain.split("—")[1].strip() if "—" in summary_plain else summary_plain[:60]
        macro = (
            f"Tour <em>{theme}</em> — <strong>{n} paradas</strong> (~{dur_txt}) · "
            f"1ª <strong>{first}</strong> → últ. <strong>{last}</strong>"
        )
        if meet_txt:
            macro += f" · encontro <strong>{meet_txt}</strong>"
        macro += " · subhorários no expandir"
        macros.append(macro)
    return macros


def apply_macros(html: str) -> tuple[str, int]:
    changed = 0
    for day_id in re.findall(r'id="(day-2026-\d{2}-\d{2})"', html):
        chunk = parse_day_chunk(html, day_id)
        if not chunk:
            continue
        specs = WINDOW_SPECS.get(day_id, {})
        tour_macros = tour_macros_for_day(chunk)
        tour_i = 0

        def repl_tr(match: re.Match) -> str:
            nonlocal changed, tour_i
            when = match.group(1)
            body = match.group(2)
            new_body = body
            is_tour = bool(TOUR_PLACEHOLDER.search(body)) or body.strip().startswith("Tour <em>")
            if is_tour and tour_i < len(tour_macros):
                new_body = tour_macros[tour_i]
                tour_i += 1
            win = specs.get("windows", {}).get(when, {})
            if win.get("macro"):
                new_body = win["macro"]
            if new_body != body:
                changed += 1
            return f'<tr><td class="fast-plan__when">{when}</td><td>{new_body}</td></tr>'

        new_chunk = re.sub(
            r'<tr><td class="fast-plan__when">([^<]+)</td><td>(.*?)</td></tr>',
            repl_tr,
            chunk,
            flags=re.DOTALL,
        )

        # day notes after fast-plan meta
        notes = specs.get("dayNotes") or []
        if notes:
            notes_html = "".join(
                f'<p class="fast-plan__day-note muted">{n}</p>' for n in notes
            )
            if "fast-plan__day-note" in new_chunk:
                new_chunk = re.sub(
                    r'<p class="fast-plan__day-note muted">.*?</p>',
                    notes_html,
                    new_chunk,
                    count=1,
                    flags=re.DOTALL,
                )
                changed += 1
            elif notes_html.strip():
                new_chunk = re.sub(
                    r"(</div>\s*<div class=\"table-scroll fast-plan__table-wrap\">)",
                    notes_html + r"\n            \1",
                    new_chunk,
                    count=1,
                )
                changed += 1
        if day_id == "day-2026-12-02" and "07:30–09:00" not in new_chunk:
            new_chunk = new_chunk.replace(
                '<tr><td class="fast-plan__when">09:00–09:45</td>',
                (
                    '<tr><td class="fast-plan__when">07:30–09:00</td>'
                    "<td><em>Slot preferido lavanderia</em> (confirmar no Maps) · "
                    "café to-go · rumo <strong>Moritzplatz</strong> até 09:45</td></tr>\n"
                    '              <tr><td class="fast-plan__when">09:00–09:45</td>'
                ),
                1,
            )
            changed += 1

        html = html.replace(chunk, new_chunk, 1)

    return html, changed


def build_json(tour_index: dict[str, list[str]]) -> dict:
    out = {"version": 2, "days": {}}
    for day_id, spec in WINDOW_SPECS.items():
        out["days"][day_id] = {
            "dayNotes": spec.get("dayNotes", []),
            "tourMacros": tour_index.get(day_id, []),
            "windows": spec.get("windows", {}),
        }
    # attach tour-only days (windows empty but tours)
    for day_id in re.findall(r'id="(day-2026-\d{2}-\d{2})"', INDEX.read_text(encoding="utf-8")):
        if day_id not in out["days"] and tour_index.get(day_id):
            out["days"][day_id] = {
                "dayNotes": [],
                "tourMacros": tour_index[day_id],
                "windows": {},
            }
    return out


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    tour_index: dict[str, list[str]] = {}
    for day_id in re.findall(r'id="(day-2026-\d{2}-\d{2})"', html):
        chunk = parse_day_chunk(html, day_id)
        if chunk:
            tour_index[day_id] = tour_macros_for_day(chunk)

    html, n = apply_macros(html)
    INDEX.write_text(html, encoding="utf-8")

    payload = build_json(tour_index)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {n} macro(s) atualizada(s); JSON → {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
