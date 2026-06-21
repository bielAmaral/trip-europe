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
  "id=\"mapas\"",
  "id=\"mapasDiasHost\"",
  "id=\"explorar\"",
  "id=\"explorar-calendario-noite\"",
  "id=\"cidades\"",
  "id=\"operacional\"",
  "id=\"operacional-envelope\"",
  "id=\"cambio\"",
  "id=\"compras\"",
  "id=\"tripSearch\"",
  "id=\"tripSearchDialog\"",
  "id=\"appTabInicio\"",
  "id=\"appTabExplorar\"",
  "id=\"appTabMais\"",
  "id=\"appDiaListHost\"",
  "id=\"mapCityPanel\"",
  "id=\"hojeDestaque\"",
  "class=\"has-app-ui\"",
  "src=\"app-shell.js\"",
  'src="app-mapas.js',
  'src="app-views.js',
  "src=\"app-search-ui.js\"",
  "href=\"app.css\"",
  "href=\"styles.css\"",
  "data-app-panel=\"inicio\"",
  "data-app-panel=\"mais\"",
  "data-app-panel=\"mapa\"",
  "data-app-panel=\"roteiro\"",
  "data-app-panel=\"explorar\"",
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

const fastPlans = html.match(/class="fast-plan"/g) || [];
if (fastPlans.length < 19) {
  err("esperados 19 blocos .fast-plan; encontrado " + fastPlans.length);
}
console.log("QA OK: " + fastPlans.length + " blocos FAST TOURIST (.fast-plan)");

const transitCollapse = html.match(/class="transit-collapse"/g) || [];
if (transitCollapse.length < 15) {
  err("esperados 15+ blocos transit-collapse; encontrado " + transitCollapse.length);
}
console.log("QA OK: " + transitCollapse.length + " blocos transporte colapsável");

if (html.includes("<style>")) {
  err("index.html ainda contém CSS inline — extrair para styles.css");
}
console.log("QA OK: sem CSS inline em index.html");

const byTab = { inicio: 0, roteiro: 0, mapa: 0, explorar: 0, mais: 0 };
const rePanel = /data-app-panel="(inicio|roteiro|mapa|explorar|mais)"/g;
let m;
while ((m = rePanel.exec(html)) !== null) {
  if (byTab[m[1]] !== undefined) byTab[m[1]] += 1;
}
for (const t of Object.keys(byTab)) {
  if (byTab[t] < 1) err("data-app-panel " + t + " deve aparecer ≥1x (contado " + byTab[t] + ")");
}
console.log(
  "QA OK: data-app-panel { inicio: " +
    byTab.inicio +
    ", roteiro: " +
    byTab.roteiro +
    ", mapa: " +
    byTab.mapa +
    ", explorar: " +
    byTab.explorar +
    ", mais: " +
    byTab.mais +
    " }"
);

const appFiles = ["styles.css", "app.css", "app-shell.js", "app-mapas.js", "app-views.js", "app-search-ui.js", "sw.js", "manifest.webmanifest", "data/mapas-paradas.csv", "data/mapas-my-maps.csv", "data/mapas-roteiro.kml"];

const mymaps = readFileSync(join(root, "data/mapas-my-maps.csv"), "utf8");
if (!mymaps.includes("Latitude") || !mymaps.includes("Longitude")) {
  err("mapas-my-maps.csv deve ter colunas Latitude e Longitude");
}
if (!mymaps.includes("Layer")) {
  err("mapas-my-maps.csv deve ter coluna Layer para agrupar por dia");
}
console.log("QA OK: mapas-my-maps.csv com coordenadas GPS e Layer");

const paradas = readFileSync(join(root, "data/mapas-paradas.csv"), "utf8");
if (!paradas.includes("leg_mode") || !paradas.includes("leg_mode_pt")) {
  err("mapas-paradas.csv deve ter colunas leg_mode e leg_mode_pt");
}
if (!paradas.includes(",train,") && !paradas.includes(",walk,")) {
  err("mapas-paradas.csv deve conter modos de transporte (walk/train/…)");
}
console.log("QA OK: mapas-paradas.csv com modos entre paradas");

for (const f of appFiles) {
  if (!existsSync(join(root, f))) err("falta ficheiro: " + f);
}
console.log("QA OK: ficheiros: " + appFiles.join(", "));

console.log("\nAsserções estáticas concluídas. Matriz de regressão: qa/REGRESSAO.md");
