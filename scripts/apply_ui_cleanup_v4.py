#!/usr/bin/env python3
"""Enxugo UI v4 — remove secções duplicadas e compactar conteúdo."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

TOC_OLD = """    <nav class="toc reveal app-panel" data-app-panel="inicio" aria-label="Índice" id="indice-toc">
      <h2>Índice</h2>
      <div class="toc-groups">
        <div class="toc-group">
          <p class="toc-group-label" id="toc-lbl-panorama">Panorama e deslocações</p>
          <ul class="toc-group-list" aria-labelledby="toc-lbl-panorama">
            <li><a href="#resumo">Resumo e noites</a></li>
            <li><a href="#mapa">Mapa intercidades</a></li>
            <li><a href="#mapas">Mapas dia a dia (GPS)</a></li>
            <li><a href="#horarios-bilhetes">Horários Omio (bilhetes)</a></li>
            <li><a href="#voos">Voos intercontinentais</a></li>
            <li><a href="#hoteis">Hotéis confirmados (Booking)</a></li>
            <li><a href="#emergencia">Emergência e contactos</a></li>
          </ul>
        </div>
        <div class="toc-group">
          <p class="toc-group-label" id="toc-lbl-dinheiro-cidades">Dinheiro e contexto por cidade</p>
          <ul class="toc-group-list" aria-labelledby="toc-lbl-dinheiro-cidades">
            <li><a href="#cambio">Câmbio e custos (estim.)</a></li>
            <li><a href="#cidades">Detalhes por cidade</a></li>
          </ul>
        </div>
        <div class="toc-group">
          <p class="toc-group-label" id="toc-lbl-dia-compras">Dia a dia e compras</p>
          <ul class="toc-group-list" aria-labelledby="toc-lbl-dia-compras">
            <li><a href="#dias">Roteiro dia a dia</a></li>
            <li><a href="#operacional">Plano operacional · orçamento</a></li>
            <li><a href="#operacional-tabela-dias">Orçamento por dia</a></li>
            <li><a href="#compras">Onde comprar (moda + Apple)</a></li>
          </ul>
        </div>
        <div class="toc-group">
          <p class="toc-group-label" id="toc-lbl-explorar">Comer, beber, noite</p>
          <ul class="toc-group-list" aria-labelledby="toc-lbl-explorar">
            <li><a href="#explorar">Explorar · restaurantes e vida noturna</a></li>
            <li><a href="#explorar-calendario-noite">Calendário · melhores noites</a></li>
            <li><a href="#lgbt-bares">Noite social (atalho)</a></li>
          </ul>
        </div>
        <div class="toc-group">
          <p class="toc-group-label" id="toc-lbl-fecho">Fecho da viagem</p>
          <ul class="toc-group-list" aria-labelledby="toc-lbl-fecho">
            <li><a href="#checklist">Checklist final</a></li>
          </ul>
        </div>
      </div>
    </nav>"""

TOC_NEW = """    <nav class="toc reveal app-panel" data-app-panel="inicio" aria-label="Índice" id="indice-toc">
      <h2>Índice</h2>
      <ul class="toc-compact">
        <li><a href="#dias">Dias</a> · <a href="#mapa">Mapa</a> · <a href="#mapas">GPS</a> · <a href="#explorar">Explorar</a></li>
        <li><a href="#horarios-bilhetes">Omio</a> · <a href="#voos">Voos</a> · <a href="#hoteis">Hotéis</a> · <a href="#emergencia">SOS</a></li>
        <li><a href="#cambio">Câmbio</a> · <a href="#operacional">Orçamento</a> · <a href="#compras">Compras</a> · <a href="#checklist">Checklist</a></li>
      </ul>
    </nav>"""

CIDADES_SECTION_RE = re.compile(
    r'\n    <section id="cidades" class="block app-panel" data-app-panel="mapa">.*?</section>\n',
    re.DOTALL,
)

MAPAS_SECTION_RE = re.compile(
    r'\n    <section id="mapas" class="block mapas-section app-panel" data-app-panel="mapa">.*?</section>\n',
    re.DOTALL,
)

OPER_POR_CIDADE_RE = re.compile(
    r'\n      <div class="card" id="operacional-por-cidade">.*?</div>\n',
    re.DOTALL,
)

CAMBIO_HOTELS_CARD_RE = re.compile(
    r'\n      <div class="card" style="margin-top:1rem;">\n        <h3>Hotéis confirmados \(caixa em R\$\)</h3>.*?</div>\n',
    re.DOTALL,
)

VOOS_CURTOS_RE = re.compile(
    r'\n      <h3>Voos curtos na Europa \(reserva separada\)</h3>.*?</div>\n\n      <details class="card" id="voos-checklist-curto"',
    re.DOTALL,
)

COMPRAS_MAPAS_CARD_RE = re.compile(
    r'\n      <div class="card" style="margin-top:1rem;">\n        <h3>Onde ir no mapa \(âncoras por cidade\)</h3>.*?</div>\n\n      <div class="card" style="margin-top:1rem;" id="compras-apple-stores">',
    re.DOTALL,
)

MAPAS_INLINE = """
      <h3 id="mapas" class="mapas-inline-heading">Índice GPS por dia</h3>
      <p class="lede mapas-inline-lede">Paradas na ordem do FAST — detalhe em cada dia (tab Dias).</p>
      <div id="mapasDiasHost" class="mapas-dias-host" aria-busy="true" aria-live="polite">
        <p class="muted">A carregar paradas…</p>
      </div>
"""

MAP_NOTE_OLD = (
    '<p class="note" style="margin-top:0.75rem;margin-bottom:0;"><strong>Horários e preços Omio</strong> (terrestre+ICE <strong>R$ 708,99</strong> + voos UE <strong>R$ 1.570,11</strong> = <strong>R$ 2.279,10</strong>): tabela completa em <a href="#horarios-bilhetes">Horários Omio</a> · totais em <a href="#cambio">Câmbio</a> · paradas GPS em <a href="#mapas">Mapas dia a dia</a>.</p>'
)
MAP_NOTE_NEW = (
    '<p class="note" style="margin-top:0.75rem;margin-bottom:0;">Omio · <a href="#horarios-bilhetes">horários</a> · <a href="#cambio">câmbio</a>.</p>'
)

FICHA_LINK_OLD = 'Ver ficha · Cidades'
FICHA_LINK_NEW = 'Hotéis'

DIAS_LEDE_OLD = '<p class="lede app-dia-lede">Toque num dia — <strong>roteiro do mapa (GPS)</strong> + plano por horário. <a href="#operacional">Orçamento</a> · <a href="#cidades">Cidades</a> · <a href="#compras">Compras</a></p>'
DIAS_LEDE_NEW = '<p class="lede app-dia-lede">Toque num dia — GPS + plano por horário. <a href="#operacional">Orçamento</a> · <a href="#mapa">Mapa</a> · <a href="#compras">Compras</a></p>'

RESUMO_OLD = """      <div class="grid-2">
        <div class="card">
          <h3>Cidades e ordem</h3>
          <p>Munique → Salzburgo → Viena → Bratislava → Budapeste → Berlim → Praga → Bruxelas. Terrestres e voos curtos: <a href="#horarios-bilhetes">Horários Omio</a> · <a href="#voos">Voos</a>.</p>
        </div>
        <div class="card">
          <h3>Distribuição de noites</h3>
          <ul>
            <li><strong>Munique</strong> · 3 noites (19–21 nov)</li>
            <li><strong>Salzburgo</strong> · 2 noites (22–23 nov)</li>
            <li><strong>Viena</strong> · 2 noites (24–25 nov)</li>
            <li><strong>Bratislava</strong> · 1 noite (check-in <strong>26 nov</strong>, saída <strong>27 nov</strong>)</li>
            <li><strong>Budapeste</strong> · 3 noites (27–29 nov)</li>
            <li><strong>Berlim</strong> · 3 noites (30 nov–2 dez)</li>
            <li><strong>Praga</strong> · 2 noites (3–4 dez)</li>
            <li><strong>Bruxelas</strong> · 2 noites (5–6 dez)</li>
          </ul>
          <p><strong>Total:</strong> 18 noites na Europa. O dia <strong>7 dez</strong> é apenas embarque (voo cedo).</p>
        </div>
      </div>"""

RESUMO_NEW = """      <div class="card">
        <p><strong>Munique</strong> (3) → <strong>Salzburgo</strong> (2) → <strong>Viena</strong> (2) → <strong>Bratislava</strong> (1) → <strong>Budapeste</strong> (3) → <strong>Berlim</strong> (3) → <strong>Praga</strong> (2) → <strong>Bruxelas</strong> (2) · <strong>18 noites</strong>. <strong>7 dez</strong> = embarque. <a href="#horarios-bilhetes">Omio</a> · <a href="#voos">Voos</a>.</p>
      </div>"""

CHECKLIST_OLD = """        <ul>
          <li>Terrestres Omio: <strong>Berlim–Praga</strong> FlixBus <strong>3 dez 10:20 Südkreuz</strong> (ou EC Hbf); ICE Salzburg–Viena <strong>24 nov 10:00</strong>; restantes em <a href="#horarios-bilhetes">Horários Omio</a>.</li>
          <li>Hotéis: reservas na app <strong>Booking</strong> offline — B&amp;B Munique, Lasserhof, Zipser, Danubia Gate, Medos, Premier Inn Alex, Alton, Mercure Colonies.</li>
          <li>Voos na Europa: <strong>BUD → BER</strong> <strong>30 nov 15:40–17:10</strong> (<strong>R$ 734,34</strong> Omio) e <strong>PRG → BRU</strong> Ryanair <strong>5 dez 11:50–13:20</strong> (<strong>R$ 835,77</strong> Omio); regresso <strong>7 dez BRU</strong>. Terrestres: ver <a href="#horarios-bilhetes">Horários Omio</a>.</li>
          <li>Neuschwanstein: bilhete com <strong>horário</strong> + comboio de ida e volta planejado.</li>
          <li>Seguro-viagem e confirmações nas apps offline (Iberia, ALL, mapas). Preencher SOS e contactos em <a href="#emergencia">Emergência</a>.</li>
          <li>Adaptador Schuko; camadas quentes para nov–dez.</li>
        </ul>"""

CHECKLIST_NEW = """        <ul>
          <li><a href="#horarios-bilhetes">Bilhetes Omio</a> + <a href="#voos">voos</a> offline na app</li>
          <li><a href="#hoteis">Hotéis Booking</a> offline</li>
          <li>Neuschwanstein: bilhete com horário + ida/volta</li>
          <li><a href="#emergencia">Seguro</a> · SOS · Iberia offline</li>
          <li>Adaptador Schuko · roupa quente nov–dez</li>
        </ul>"""

COMPRAS_LEDE_OLD = '<p class="lede">Use a <strong><a href="#compras-matriz-dia">matriz cidade × janela</a></strong> como vista única (com atalho para cada dia); o <strong><a href="#compras-fallback-tipo">plano B por tipo de produto</a></strong> cobre “se não der nesta cidade”. Nos dias com compras, veja a coluna <strong>Dia no roteiro</strong> abaixo e o plano hora a hora em <a href="#dias">#dias</a> — confira filiais e horários no <strong>Google Maps</strong> (domingos e feriados mudam).</p>'
COMPRAS_LEDE_NEW = '<p class="lede"><a href="#compras-matriz-dia">Matriz</a> · <a href="#compras-fallback-tipo">plano B</a> · horários no <a href="#dias">dia</a> e no Maps.</p>'

HORARIOS_LEDE_OLD = '<p class="lede">Estes horários são os que apareceram nos <strong>prints Omio</strong> (as datas nos prints eram só de exemplo; aqui estão <strong>encaixados nas datas reais</strong> do roteiro). Na reserva final, escolha no Omio a <strong>mesma partida</strong> ou o horário mais próximo <strong>no dia certo</strong> e confira no <strong>bilhete / app</strong> da operadora.</p>'
HORARIOS_LEDE_NEW = '<p class="lede">Horários dos prints Omio, nas <strong>datas reais</strong> do roteiro. Confirme no bilhete.</p>'

HOTEIS_LEDE_OLD = '<p class="lede">Reservas com <strong>cancelamento grátis</strong> conforme aparecer na tela. Totais em <strong>R$</strong> são os valores indicados na app na data de consulta; impostos e taxas podem estar incluídos ou separados por estadia — confira no resumo de cada reserva.</p>'
HOTEIS_LEDE_NEW = '<p class="lede">Booking · cancelamento grátis conforme cada reserva. Totais em R$ na data de consulta.</p>'

EXPLORAR_LEDE_OLD = '<p class="lede">Restaurantes, bares LGBT+, zonas de hostel/vida noturna e um <strong>calendário de melhores noites</strong> alinhado ao roteiro (comboios, voos, dias pesados). Você fica em <strong>hotel</strong> — hostels listados são <strong>pontos sociais</strong> e bairros, não alojamento.</p>\n      <p class="note" style="margin-top:0;"><strong>Confirme horários</strong> no Google Maps ou site oficial perto da data. <strong>La Demence</strong> (Bruxelas) é festa mensal — <a href="https://lademence.com/" rel="noopener noreferrer">lademence.com</a>. <strong>Connection</strong> (Berlim) pode estar em obras.</p>'
EXPLORAR_LEDE_NEW = '<p class="lede">Restaurantes, hostels sociais e <a href="#explorar-calendario-noite">calendário de noites</a>. Hostels = zona social, não alojamento.</p>'

MAP_LEDE_OLD = '<p class="lede">Diagrama <strong>não é carta geográfica à escala</strong>: mostra a <strong>sequência da viagem</strong> e o modo (comboio vs voo). Durações são ordens de grandeza típicas em serviços diretos. <strong>Toque ou use Tab</strong> nos círculos do percurso para ver hotel, estação e sugestões rápidas no painel ao lado (em telas estreitas, abaixo do diagrama).</p>'
MAP_LEDE_NEW = '<p class="lede">Sequência da viagem (comboio vs voo). Toque nos nós para hotel e estação.</p>'

OPER_LEDE_OLD = '<p class="lede">Estratégia de <strong>hub</strong>, ritmo de energia e <strong>orçamento de bolso</strong> para comer, passear, compras e noite. Envelope alvo: <strong>€2.000</strong> (Wise) — <em>fora</em> hotéis, transportes intercidades e voo internacional (já pagos ou em calendário separado). Detalhe hora a hora: <a href="#dias">Roteiro dia a dia</a>.</p>'
OPER_LEDE_NEW = '<p class="lede">Envelope <strong>€2.000</strong> (bolso, Wise) — fora hotéis e transportes. Detalhe: <a href="#dias">dias</a>.</p>'

CAMBIO_LEDE_OLD = '<p class="lede">Estratégia: <strong>converter R$ → EUR na Wise</strong> em parcelas <strong>semanais</strong> até o <strong>início da viagem (18 nov 2026)</strong>. Primeira conversão: <strong>22 abr 2026</strong>. Taxa de exemplo nas contas: <strong>5,90 R$/EUR</strong> (substitua pelo rate Wise real em cada transferência).</p>'
CAMBIO_LEDE_NEW = '<p class="lede">Wise: R$ → EUR em parcelas até <strong>18 nov 2026</strong> (início <strong>22 abr</strong>). Taxa exemplo: <strong>5,90 R$/EUR</strong>.</p>'

VOOS_NOTE_OLD = '<p class="note">Berlim–Praga (<strong>3 dez</strong>): <strong>FlixBus Südkreuz 10:20 → Florenc 14:20</strong> (~<strong>R$ 155,85</strong> Omio); alternativa <strong>EC</strong> Berlin Hbf → hl.n. (DB/ČD). Os voos curtos acima são <strong>independentes</strong> dos bilhetes Iberia transcontinentais. O regresso intercontinental no <strong>7 dez</strong> continua em <strong>BRU</strong> (Iberia).</p>'
VOOS_NOTE_NEW = '<p class="note">Voos curtos UE: <a href="#horarios-bilhetes">Omio</a>. Berlim–Praga Flix <strong>3 dez</strong> na mesma tabela.</p>'


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")

    if TOC_OLD in html:
        html = html.replace(TOC_OLD, TOC_NEW)
    else:
        print("WARN: TOC block not found exactly")

    m = CIDADES_SECTION_RE.search(html)
    if not m:
        raise SystemExit("cidades section not found")
    html = CIDADES_SECTION_RE.sub("\n", html)

    m = MAPAS_SECTION_RE.search(html)
    if not m:
        raise SystemExit("mapas section not found")
    html = MAPAS_SECTION_RE.sub("\n", html)

    if MAP_NOTE_OLD in html:
        html = html.replace(MAP_NOTE_OLD, MAP_NOTE_NEW + "\n" + MAPAS_INLINE)

    html = OPER_POR_CIDADE_RE.sub("\n", html)
    html = CAMBIO_HOTELS_CARD_RE.sub(
        '\n      <p class="note" style="margin-top:1rem;">Hotéis (~<strong>R$ 11.423</strong>): ver <a href="#hoteis">Booking</a>.</p>\n',
        html,
    )
    html = VOOS_CURTOS_RE.sub(
        '\n      <p class="lede">Voos curtos UE: <a href="#horarios-bilhetes">Horários Omio</a>.</p>\n\n      <details class="card" id="voos-checklist-curto"',
        html,
    )
    html = COMPRAS_MAPAS_CARD_RE.sub(
        '\n      <div class="card" style="margin-top:1rem;" id="compras-apple-stores">',
        html,
    )

    for old, new in [
        (RESUMO_OLD, RESUMO_NEW),
        (CHECKLIST_OLD, CHECKLIST_NEW),
        (COMPRAS_LEDE_OLD, COMPRAS_LEDE_NEW),
        (HORARIOS_LEDE_OLD, HORARIOS_LEDE_NEW),
        (HOTEIS_LEDE_OLD, HOTEIS_LEDE_NEW),
        (EXPLORAR_LEDE_OLD, EXPLORAR_LEDE_NEW),
        (MAP_LEDE_OLD, MAP_LEDE_NEW),
        (OPER_LEDE_OLD, OPER_LEDE_NEW),
        (CAMBIO_LEDE_OLD, CAMBIO_LEDE_NEW),
        (DIAS_LEDE_OLD, DIAS_LEDE_NEW),
        (VOOS_NOTE_OLD, VOOS_NOTE_NEW),
        (FICHA_LINK_OLD, FICHA_LINK_NEW),
    ]:
        if old in html:
            html = html.replace(old, new)

    html = html.replace(
        'aria-controls="mapa mapas cidades"',
        'aria-controls="mapa"',
    )
    html = html.replace('href="app.css?v=38"', 'href="app.css?v=39"')
    html = html.replace('app-mapas.js?v=35', 'app-mapas.js?v=36')
    html = html.replace('app-core.js?v=1', 'app-core.js?v=2')

    INDEX.write_text(html, encoding="utf-8")
    print("OK: index.html enxugado (v4)")


if __name__ == "__main__":
    main()
