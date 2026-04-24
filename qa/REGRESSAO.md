# Matriz de smoke e regressão — Roteiro Europa (PWA)

**Objetivo:** cobrir funções, atributos, armazenamento, URLs e acessibilidade, sem perder o equivalente a testes E2E que um humano (ou o browser do Cursor) pode executar.

**Automatizado (CI/local):** `node scripts/qa-assert.mjs` na raiz do repositório.

**Servidor local (browser):** `python3 -m http.server 9876` (use uma porta livre) e abrir `http://127.0.0.1:9876/index.html` — ficheiro `file://` pode restringir clipboard, SW, etc.

---

## 1. Navegação e estado global

| # | Caso | Como verificar | Resultado esperado |
|---|------|----------------|--------------------|
| 1.1 | Carga sem hash | Abrir a página | Corpo com `class="has-app-ui"`, `data-app-tab` = tab guardada em `localStorage` `roteiro-app-tab-v1` ou, na 1.ª visita, tab **Início**; hash pode tornar-se `#!{tab}` (replaceState) |
| 1.2 | Quatro tabs do tablist | Clicar **Início**, **Dias**, **Mapa**, **Mais** | Só a área de conteúdo (`#appMain`) muda; tab bar visível; `location.hash` ≈ `#!inicio` / `#!roteiro` / `#!mapa` / `#!mais` |
| 1.3 | `aria-selected` / `role="tab"` | Inspecionar ou leitor de ecrãs | Só a tab ativa com `aria-selected="true"` |
| 1.4 | `aria-controls` (Mapa) | InSpecionar tab Mapa | Contém `mapa cidades` (mapa + fichas) |
| 1.5 | `localStorage` tab inválida | Remover a chave ou corromper; recarregar | Cai em **inicio** |
| 1.6 | Migração `financas` → `mais` (legado) | `localStorage.setItem('roteiro-app-tab-v1','financas');` recarregar | Lê e grava `mais` (ver `app-shell.js`) |
| 1.7 | Deep link `#!roteiro` | Navegar diretamente a `#!roteiro` | Tab **Dias**, conteúdo de `#dias` visível (lista ou detalhe) |
| 1.8 | Deep link `#cambio` (e outras secções) | Navegar a `#cambio`, `#voos`, `#mapa`, `#dias` | `whichTabForSectionId` aplica; tab correta; (opcional) `target-pulse` / scroll para o elemento |
| 1.9 | `#inicio-hero`, `#indice-toc` | Navegar a esses IDs | Tab **Início** |
| 1.10 | Trocar hash com pesquisa ativa e texto no campo *sem* `app-search-peek` | (Após abrir e fechar o diálogo) | Fechar o diálogo de pesquisa limpa o campo; `hashchange` aplica o tab da nova âncora; não fica preso a `#!` anterior (regressão: v9+) |

---

## 2. Roteiro — lista → detalhe (dias)

| # | Caso | Como | Esperado |
|---|------|------|----------|
| 2.1 | Lista de dias | Tab **Dias** | `#dias` em modo `app-roteiro--lista`; lista `ul.app-dia-list` (se JS correu) |
| 2.2 | Abrir um dia | Clicar numa fila | Um só `details.day` visível; `#!roteiro` ou `#day-2026-…` conforme ações; `app-roteiro--detalhe` |
| 2.3 | Voltar | Botão **Voltar** (barra superior) | Repõe lista; preferencialmente `#!roteiro` |
| 2.4 | `details` guardados | Abrir/dias; recarregar | `localStorage` `roteiro-open-state-v1` (IDs dos details) respeitado, exceto modo lista/detalhe da lista dinâmica do app |
| 2.5 | Links `#day-…` no texto | Clicar link interno para outro dia | Rola/destaca; dia abre |
| 2.6 | 19 (ou n) blocos de dia | Contar no DOM ou `qa-assert` | 19 (ou o número anunciado no título) |

---

## 3. Mapa (SVG) e painel de cidade

| # | Caso | Como | Esperado |
|---|------|------|----------|
| 3.1 | Nós (g.map-node) | Clicar Munique, Praga, etc. | Nó com seleção; `mapCityPanel` com título, hotel, POI, ligação Maps |
| 3.2 | `Copiar morada` | Clicar (em HTTPS/localhost) | `navigator.clipboard`, texto = `data-copy`; feedback “Copiado!” (tempo limitado) |
| 3.3 | Ficha cidades | “Ver ficha · Cidades” com hash (ex. `#city-muc`) | Salta para a secção/mapa; tab coerente |
| 3.4 | `aria-label` / teclado | Tab + Enter em nó | Mesmo que clique (keydown no script inline) |

---

## 4. “Mais” (hub e secções)

| # | Conteúdo mínimo | `data-app-panel` |
|----|-------------------|------------------|
| 4.1 | Hub, Omio, voos, hotéis, emergência, câmbio, compras, checklist | `mais` (várias `section`/`#mais-hub`) |
| 4.2 | Âncoras `compras-matriz-dia`, `compras-*` | Ficam dentro de `#compras`; deep link ainda tab **Mais** (`whichTabForSectionId` com `compras-`) |

---

## 5. Pesquisa global

| # | Caso | Esperado |
|---|------|----------|
| 5.1 | Abrir: botão lupa (toolbar) | `dialog#tripSearchDialog` com `showModal` (ou `open`); `aria-expanded="true"` no gatilho; foco no `input#tripSearch` |
| 5.2 | Escrever texto (debounce ~140 ms) | `body.has-trip-search`; `search-miss` nos nós que não batem; **peek** (todos os painéis) quando há cópia |
| 5.3 | Limpar o campo (ou fechar) | Vistas repostas: remoção de `search-miss`; se fechou o diálogo, campo vazio; `app-search-peek` desligado; tab atual restaura painéis |
| 5.4 | Tema / troca de tab com pesquisa (linha 213–220 `app-shell`) | Tab limpa a pesquisa (corpo) ao mudar (comportamento actual) |
| 5.5 | `type="search"` e evento `search` | Limpa quando a UI nativa de “esvaziar” o campo dispara o evento (inline + `searchEl`) |

---

## 6. Tema, scroll e cromo “app”

| # | Caso | Esperado |
|---|------|----------|
| 6.1 | Tema (sol/lua) | `documentElement[data-theme="dark"]` a alternar; `localStorage` `roteiro-theme-v1` = `light`/`dark` |
| 6.2 | `scrollProgress` (desktop/ponteiro fino) | Acompanha o scroll de `#appMain` (não `window` só) em layout `has-app-ui` |
| 6.3 | Móvel `pointer: coarse` | Regra em `app.css` pode esconder a barra de leitura (não exigir para “lido”) |
| 6.4 | FAB “Voltar ao topo` | Só com scroll longo; actua sobre `#appMain` |
| 6.5 | `prefers-reduced-motion` (simular no devtools) | Menos transição/scroll animado; cursor magnético desligado se reduzir movimento |

---

## 7. Destaque “Hoje” (viagem no calendário)

| # | Resultado | Nota |
|---|------------|------|
| 7.1 | Se a data de hoje bater com `data-trip-date` nalgum `details.day` | Cartão `hojeDestaque` deixa de estar `hidden` |
| 7.2 | Botão “Abrir o dia de hoje” | Chama `roteiroApplyAppTab('roteiro',…)`; abre o `details` do dia; scroll |

(Fora da janela Nov–Dez 2026 o bloco fica `hidden` — espreitação: alterar a data de sistema *só* em teste, não exigir em produção.)

---

## 8. Acessibilidade mínima

- Link “Saltar para o conteúdo”
- `aria-live` no painel do mapa, breadcrumb de dia
- `role="region"` / `aria-labelledby` em `#dias` onde estiver
- Foco visível (Outline em CSS) em botões/links; diálogo com título e botão fechar
- Não exigir hover sozinho para ações (mobile)

---

## 9. PWA / rede

| # | Caso | Nota |
|---|------|------|
| 9.1 | `sw.js` registado | Só com serviço permitido; actualizar a versão do `CACHE` ao mudar ficheiros críticos (ex. `v9`) |
| 9.2 | Navegação (network-first no SW) | HTML a partir da rede; fallback a cache se offline (conforme `sw.js` actual) |
| 9.3 | `manifest.webmanifest` | Ícones, `name`, `start_url` |

---

## 10. APIs e edge cases (JavaScript no HTML)

- `labelDataTables()` — `data-label` em `td` em tabelas `.data` (móvel)
- `labelDataTables`, `MapCityPanel` IIFE, `LS_OPEN` details, `runSearch`, `pulseTargetFromHash`, `scrollToElementHighSpeedDecel` expostos (onde aplicável) — sem erros na consola
- `showStorageWarning` com toast se `localStorage` encher/ bloquear

---

## 11. Checklist pós–alteração de ficheiro

- [ ] `node scripts/qa-assert.mjs`
- [ ] `python3 sync_roteiro_from_index.py` (se `roteiro.html` = cópia)
- [ ] Incremento da versão `CACHE` em `sw.js` (se ficheiros precacheables mudaram)
- [ ] Fazer smoke manual das secções 1.–6. (ou com browser do Cursor) numa viewport 390×800

---

*Última geração da matriz: 2026-04; alinhada a `app-shell.js`, `app-views.js`, `app-search-ui.js`, `app.css` e o bloco de script de `index.html`.*
