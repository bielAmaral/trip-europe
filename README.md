# Roteiro · Europa Central (site estático / PWA)

Site pessoal do roteiro (HTML + JS + CSS). O ficheiro de entrada é **`index.html`** na raiz do repositório.

## Desenvolvimento local

Abra `index.html` no browser (duplo clique ou um servidor estático opcional):

```bash
cd roteiro-viagem-europa-2025
python3 -m http.server 8080
```

Depois visite `http://localhost:8080/`.

## Netlify

- **Diretório a publicar (Publish directory):** `.` (raiz do projeto; ver `netlify.toml`)
- **Comando de build:** nenhum (site estático; deixe vazio ou `echo "static"`)
- Os ficheiros servidos incluem `index.html`, `app.css`, `app-shell.js`, `app-views.js`, `app-search-ui.js`, `sw.js`, `manifest.webmanifest` e `icons/`

## PWA / Service Worker

- O `sw.js` usa **network-first para navegação** (HTML da rede quando possível, com fallback em cache offline) e **cache com versão** para ativos estáticos; o nome do cache inclui `v10` — incrementar ao alterar ficheiros críticos para forçar atualização em clientes antigos.

## QA (regressão e smoke)

- **Asserções estáticas (sem browser):** `node scripts/qa-assert.mjs` — confirma IDs, contagem de dias, ficheiros da app.
- **Matriz manual / browser:** [qa/REGRESSAO.md](qa/REGRESSAO.md) — funções, `data-app-panel`, pesquisa, PWA, acessibilidade.
- `sw.js` tem `Cache-Control: no-cache` em Netlify (ver `netlify.toml`) para facilitar alterações.

## Cópia `roteiro.html`

Se existir `roteiro.html` como espelho, pode alinhar a partir de `index.html` com:

```bash
python3 sync_roteiro_from_index.py
```
