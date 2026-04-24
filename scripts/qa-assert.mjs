#!/usr/bin/env node
/**
 * Verificações estáticas (sem browser) do roteiro: includes críticos, contagem de dias, ficheiros.
 * Uso: node scripts/qa-assert.mjs
 */
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const html = readFileSync(join(root, "index.html"), "utf8");
const err = (msg) => {
  console.error("QA FAIL: " + msg);
  process.exit(1);
};

const mustHave = [
  "id=\"appMain\"",
  "id=\"dias\"",
  "id=\"mapa\"",
  "id=\"cidades\"",
  "id=\"cambio\"",
  "id=\"compras\"",
  "id=\"tripSearch\"",
  "id=\"tripSearchDialog\"",
  "id=\"appTabInicio\"",
  "id=\"appTabMais\"",
  "id=\"appDiaListHost\"",
  "id=\"mapCityPanel\"",
  "id=\"hojeDestaque\"",
  "class=\"has-app-ui\"",
  "src=\"app-shell.js\"",
  "src=\"app-views.js\"",
  "src=\"app-search-ui.js\"",
  "href=\"app.css\"",
  "data-app-panel=\"inicio\"",
  "data-app-panel=\"mais\"",
  "data-app-panel=\"mapa\"",
  "data-app-panel=\"roteiro\"",
  "roteiroApplyAppTab",
];

for (const s of mustHave) {
  if (!html.includes(s)) err('falta: "' + s + '" em index.html');
}
console.log("QA OK: " + mustHave.length + " marcadores críticos no index.html");

const dayMatches = html.match(/id="day-2026-\d{2}-\d{2}"/g) || [];
if (dayMatches.length < 19) {
  err("esperados 19+ blocos de dia; encontrado " + dayMatches.length);
}
console.log("QA OK: " + dayMatches.length + " IDs day-2026-… (details dia)");

const byTab = { inicio: 0, roteiro: 0, mapa: 0, mais: 0 };
const rePanel = /data-app-panel="(inicio|roteiro|mapa|mais)"/g;
let m;
while ((m = rePanel.exec(html)) !== null) {
  if (byTab[m[1]] !== undefined) byTab[m[1]] += 1;
}
for (const t of Object.keys(byTab)) {
  if (byTab[t] < 1) err("data-app-panel " + t + " deve aparecer ≥1x (contado " + byTab[t] + ")");
}
console.log("QA OK: data-app-panel { inicio: " + byTab.inicio + ", roteiro: " + byTab.roteiro + ", mapa: " + byTab.mapa + ", mais: " + byTab.mais + " }");

const appFiles = ["app.css", "app-shell.js", "app-views.js", "app-search-ui.js", "sw.js", "manifest.webmanifest"];
for (const f of appFiles) {
  if (!existsSync(join(root, f))) err("falta ficheiro: " + f);
}
console.log("QA OK: ficheiros: " + appFiles.join(", "));

console.log("\nAsserções estáticas concluídas. Matriz de regressão: qa/REGRESSAO.md");
