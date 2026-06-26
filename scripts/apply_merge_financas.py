#!/usr/bin/env python3
"""Funde #cambio + #operacional em #financas (Dinheiro & logística)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

FINANCAS = """    <section id="financas" class="block app-panel" data-app-panel="mais" aria-labelledby="financas-heading">
      <span id="cambio" class="visually-hidden" aria-hidden="true"></span>
      <span id="operacional" class="visually-hidden" aria-hidden="true"></span>
      <h2 id="financas-heading">Dinheiro & logística</h2>
      <p class="lede">Wise <strong>26.699,80 R$</strong> → ≈ <strong>4.525 €</strong> (@ 5,90) · bolso <strong>€2.000</strong> · hotéis <a href="#hoteis">~R$ 11.423</a> · Omio <a href="#horarios-bilhetes">R$ 2.279</a>.</p>

      <div class="card" style="margin-top:1rem;">
        <h3 id="financas-wise">Conversão Wise (R$)</h3>
        <ul>
          <li><strong>17.833 R$</strong> disponíveis → converter <strong>60%</strong> = <strong>10.699,80 R$</strong>.</li>
          <li><strong>18 set 2026:</strong> +<strong>20.000 R$</strong> → converter <strong>80%</strong> = <strong>16.000 R$</strong>.</li>
          <li><strong>Total Wise:</strong> <strong>26.699,80 R$</strong> (≈ <strong>4.525 €</strong>) · colchão <strong>11.133 R$</strong> fora do plano.</li>
        </ul>
        <details class="financas-details">
          <summary>Calendário semanal de conversão</summary>
          <div class="table-scroll">
          <table class="data">
            <thead>
              <tr><th>Período</th><th>O quê</th><th>Semanas (≈)</th><th>Valor semanal (≈)</th></tr>
            </thead>
            <tbody>
              <tr><td><strong>22 abr → 17 set 2026</strong></td><td><strong>10.699,80 R$</strong> (60% do 1.º envelope)</td><td><strong>~21</strong></td><td><strong>~505 R$/sem</strong></td></tr>
              <tr><td><strong>18 set → 10 nov 2026</strong></td><td><strong>16.000 R$</strong> (80% do 2.º envelope)</td><td><strong>~8</strong></td><td><strong>~2.000 R$/sem</strong></td></tr>
            </tbody>
          </table>
          </div>
          <p class="note" style="margin-bottom:0;">Termina ~1 semana antes da ida. Na semana de <strong>18 set</strong> alinhe fecho do 1.º montante e arranque do 2.º.</p>
        </details>
      </div>

      <div class="card" style="margin-top:1rem;">
        <h3 id="financas-sobra">Sobra de bolso (após hotéis e Omio)</h3>
        <p style="margin-top:0;"><strong>26.699,80</strong> − <strong>11.423</strong> (hotéis) − <strong>2.279,10</strong> (Omio) = <strong>12.997,70 R$</strong> → <strong>~2.203 €</strong>, alinhado ao envelope <strong>€2.000</strong> (margem ~€200 taxa Wise).</p>
        <p class="note" style="margin-bottom:0;">Voos GRU–MUC / BRU–GRU fora desta conta. PRG→BRU já inclui Zaventem (sem Flibco CRL).</p>
      </div>

      <div class="card oper-envelope" id="operacional-envelope">
        <h3>Envelope €2.000 · como usar</h3>
        <div class="table-scroll">
        <table class="data oper-budget-table">
          <thead>
            <tr><th>Rubrica</th><th>€</th><th>Notas</th></tr>
          </thead>
          <tbody>
            <tr><td>Comidas + cafés + padarias</td><td><strong>~700</strong></td><td>€35–40/dia médio; dias leves menos</td></tr>
            <tr><td>Passeios + entradas + metro</td><td><strong>~250</strong></td><td>Castelo, Festung, museus pontuais</td></tr>
            <tr><td>Compras (moda, Kiko)</td><td><strong>~550</strong></td><td>Pico Berlim + Praga; evitar Budapeste</td></tr>
            <tr><td>Noite LGBT / ruin bars</td><td><strong>~240</strong></td><td>Ver <a href="#explorar-calendario-noite">calendário noite</a></td></tr>
            <tr><td>Buffer / imprevistos</td><td><strong>~260</strong></td><td>Uber, chuva, extra num jantar</td></tr>
            <tr><td><strong>Total</strong></td><td><strong>2.000</strong></td><td>≈ <strong>€105/dia</strong> em 19 dias de viagem</td></tr>
          </tbody>
        </table>
        </div>
        <p class="note" style="margin-bottom:0;"><strong>Regra:</strong> dias de <span class="dt dt-flight">voo</span> ou <span class="dt dt-transfer">transferência</span> gastam menos. Dias <span class="dt dt-shop">compras</span> podem passar de €105 — compensar no dia seguinte.</p>
      </div>

      <h3 id="operacional-dias">Orçamento por dia</h3>
      <div class="table-scroll">
      <table class="data oper-budget-table" id="operacional-tabela-dias">
        <thead>
          <tr><th>Data</th><th>Cidade</th><th>Energia</th><th>Teto €</th><th>Foco</th><th>Dia</th></tr>
        </thead>
        <tbody>
          <tr><td>19 nov</td><td>Munique</td><td><span class="oper-energy oper-energy--low">Leve</span></td><td>70</td><td>Chegada · jet lag</td><td><a href="#day-2026-11-19">#</a></td></tr>
          <tr><td>20 nov</td><td>Munique</td><td><span class="oper-energy oper-energy--high">Pleno</span></td><td>110</td><td>Cidade + compras + Glockenbach</td><td><a href="#day-2026-11-20">#</a></td></tr>
          <tr><td>21 nov</td><td>Füssen</td><td><span class="oper-energy oper-energy--max">Máxima</span></td><td>85</td><td>Castelo · sem noite</td><td><a href="#day-2026-11-21">#</a></td></tr>
          <tr><td>22 nov</td><td>→ Salzburgo</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>55</td><td>Flix 13h45</td><td><a href="#day-2026-11-22">#</a></td></tr>
          <tr><td>23 nov</td><td>Salzburgo</td><td><span class="oper-energy oper-energy--high">Pleno</span></td><td>75</td><td>Altstadt + Festung</td><td><a href="#day-2026-11-23">#</a></td></tr>
          <tr><td>24 nov</td><td>→ Viena</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>95</td><td>ICE 10h00 · compras + Donaukanal</td><td><a href="#day-2026-11-24">#</a></td></tr>
          <tr><td>25 nov</td><td>Viena</td><td><span class="oper-energy oper-energy--high">Pleno</span></td><td>95</td><td>Schönbrunn + compras</td><td><a href="#day-2026-11-25">#</a></td></tr>
          <tr><td>26 nov</td><td>→ Bratislava</td><td><span class="oper-energy oper-energy--low">Leve</span></td><td>35</td><td>Flix tarde</td><td><a href="#day-2026-11-26">#</a></td></tr>
          <tr><td>27 nov</td><td>→ Budapeste</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>50</td><td>Flix manhã</td><td><a href="#day-2026-11-27">#</a></td></tr>
          <tr class="row-highlight"><td><strong>28 nov</strong></td><td>Budapeste</td><td><span class="oper-energy oper-energy--high">Pleno</span></td><td><strong>95</strong></td><td>Ruin bars (sáb) + compras</td><td><a href="#day-2026-11-28">#</a></td></tr>
          <tr><td>29 nov</td><td>Budapeste</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>75</td><td>Urbano · poupar p/ voo</td><td><a href="#day-2026-11-29">#</a></td></tr>
          <tr><td>30 nov</td><td>→ Berlim</td><td><span class="oper-energy oper-energy--low">Leve</span></td><td>40</td><td>Ryanair 15h40</td><td><a href="#day-2026-11-30">#</a></td></tr>
          <tr class="row-highlight"><td><strong>1 dez</strong></td><td>Berlim</td><td><span class="oper-energy oper-energy--high">Pleno</span></td><td><strong>110</strong></td><td>LGBT + mercados</td><td><a href="#day-2026-12-01">#</a></td></tr>
          <tr><td>2 dez</td><td>Berlim</td><td><span class="oper-energy oper-energy--high">Pleno</span></td><td>120</td><td>Compras (hub Alex)</td><td><a href="#day-2026-12-02">#</a></td></tr>
          <tr><td>3 dez</td><td>→ Praga</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>50</td><td>Flix 10h20</td><td><a href="#day-2026-12-03">#</a></td></tr>
          <tr class="row-highlight"><td><strong>4 dez</strong></td><td>Praga</td><td><span class="oper-energy oper-energy--high">Pleno</span></td><td><strong>130</strong></td><td>Compras + Vinohrady</td><td><a href="#day-2026-12-04">#</a></td></tr>
          <tr><td>5 dez</td><td>→ Bruxelas</td><td><span class="oper-energy oper-energy--low">Leve</span></td><td>60</td><td>Ryanair 11h50</td><td><a href="#day-2026-12-05">#</a></td></tr>
          <tr class="row-highlight"><td><strong>6 dez</strong></td><td>Bruges (bate-volta)</td><td><span class="oper-energy oper-energy--mid">Média</span></td><td>75</td><td>Prima Iza · regresso ~20h</td><td><a href="#day-2026-12-06">#</a></td></tr>
          <tr><td>7 dez</td><td>→ Brasil</td><td><span class="oper-energy oper-energy--low">Mínima</span></td><td>20</td><td>Embarque 07h00</td><td><a href="#day-2026-12-07">#</a></td></tr>
        </tbody>
      </table>
      </div>
      <p class="muted" style="margin:0.5rem 0 0;font-size:0.88rem;">* Praga: 1 dia curto (chegada) + 1 dia pleno de compras.</p>
    </section>
"""

def main():
    html = INDEX.read_text(encoding="utf-8")
    pattern = re.compile(
        r'    <section id="cambio".*?</section>\s*\n\s*<section id="operacional".*?</section>\s*\n',
        re.DOTALL,
    )
    if not pattern.search(html):
        raise SystemExit("FAIL: blocos cambio/operacional não encontrados")
    html = pattern.sub(FINANCAS + "\n", html, count=1)

    html = html.replace(
        '<li><a href="#cambio">Câmbio</a> · <a href="#operacional">Orçamento</a> · <a href="#compras">Compras</a> · <a href="#checklist">Checklist</a></li>',
        '<li><a href="#financas">Dinheiro</a> · <a href="#compras">Compras</a> · <a href="#checklist">Checklist</a></li>',
    )
    html = html.replace(
        'Omio · <a href="#horarios-bilhetes">horários</a> · <a href="#cambio">câmbio</a>.',
        'Omio · <a href="#horarios-bilhetes">horários</a> · <a href="#financas">dinheiro</a>.',
    )
    html = html.replace(
        '<a href="#operacional">Orçamento</a>',
        '<a href="#financas">Dinheiro</a>',
    )
    html = html.replace(
        'aria-controls="operacional horarios-bilhetes voos hoteis emergencia cambio compras checklist"',
        'aria-controls="financas horarios-bilhetes voos hoteis emergencia compras checklist"',
    )
    html = html.replace('app.css?v=39', 'app.css?v=40')
    INDEX.write_text(html, encoding="utf-8")
    print("OK: cambio + operacional → financas")


if __name__ == "__main__":
    main()
