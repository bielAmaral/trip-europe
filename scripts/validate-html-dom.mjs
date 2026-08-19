import { JSDOM } from "jsdom";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const html = readFileSync(join(dirname(fileURLToPath(import.meta.url)), "..", "index.html"), "utf8");
const dom = new JSDOM(html);
const doc = dom.window.document;

const panelIds = [
  "inicio-hero",
  "indice-toc",
  "resumo",
  "explorar",
  "mapa",
  "horarios-bilhetes",
  "voos",
  "hoteis",
  "emergencia",
  "financas",
  "dias",
  "compras",
  "presentes",
  "checklist",
];

const explorar = doc.getElementById("explorar");
const problems = [];

for (const id of panelIds) {
  const el = doc.getElementById(id);
  if (!el) {
    problems.push(`MISSING #${id}`);
    continue;
  }
  const panel = el.getAttribute("data-app-panel");
  if (!panel) problems.push(`#${id} sem data-app-panel`);
  if (explorar && explorar !== el && explorar.contains(el)) {
    problems.push(`#${id} aninhado em #explorar`);
  }
}

// details.city-block balance inside explorar
const cityBlocks = explorar?.querySelectorAll("details.city-block") || [];
cityBlocks.forEach((d) => {
  if (!d.id) problems.push("city-block sem id");
});

// Unclosed details in explorar?
const openDetails = explorar?.innerHTML.match(/<details\b/gi)?.length || 0;
const closeDetails = explorar?.innerHTML.match(/<\/details>/gi)?.length || 0;
if (openDetails !== closeDetails) {
  problems.push(`#explorar details imbalance: open=${openDetails} close=${closeDetails}`);
}

if (problems.length) {
  console.error("HTML PROBLEMS:");
  problems.forEach((p) => console.error(" -", p));
  process.exit(1);
}
console.log("HTML DOM OK:", panelIds.length, "painéis, explorar details balanced:", openDetails);
