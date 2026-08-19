import { chromium } from "playwright";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const base = "http://127.0.0.1:8888";

const tabs = [
  { url: `${base}/#!inicio`, tab: "inicio", expectId: "inicio-hero" },
  { url: `${base}/#!roteiro`, tab: "roteiro", expectId: "dias" },
  { url: `${base}/#!mapa`, tab: "mapa", expectId: "mapa" },
  { url: `${base}/#!explorar`, tab: "explorar", expectId: "explorar" },
  { url: `${base}/#!mais`, tab: "mais", expectId: "horarios-bilhetes" },
  { url: `${base}/#presentes`, tab: "mais", expectId: "presentes" },
];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
page.on("console", (m) => {
  if (m.type() === "error") errors.push(`console: ${m.text()}`);
});

const results = [];
for (const t of tabs) {
  errors.length = 0;
  try {
    await page.goto(t.url, { waitUntil: "networkidle", timeout: 15000 });
    await page.waitForTimeout(400);
    const info = await page.evaluate((expectId) => {
      const el = document.getElementById(expectId);
      if (!el) return { ok: false, reason: "element missing" };
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const insideExplorar = !!document.getElementById("explorar")?.contains(el);
      return {
        ok: !el.hasAttribute("hidden") && cs.visibility === "visible" && r.height > 20,
        tab: document.body.getAttribute("data-app-tab"),
        hidden: el.hasAttribute("hidden"),
        visibility: cs.visibility,
        display: cs.display,
        height: r.height,
        insideExplorar,
        title: el.querySelector("h1,h2,h3")?.textContent?.trim()?.slice(0, 50) || el.id,
      };
    }, t.expectId);
    results.push({ ...t, ...info, errors: [...errors] });
  } catch (e) {
    results.push({ ...t, ok: false, reason: e.message, errors: [...errors] });
  }
}

// HTML nesting audit
const html = readFileSync(join(root, "index.html"), "utf8");
const ids = [
  "resumo",
  "mapa",
  "horarios-bilhetes",
  "presentes",
  "dias",
  "financas",
];
const nesting = {};
for (const id of ids) {
  const pos = html.indexOf(`id="${id}"`);
  const explorarStart = html.indexOf('id="explorar"');
  const explorarEnd = html.indexOf("</section>", html.indexOf('id="explorar-comida-pratica"'));
  nesting[id] = { pos, insideExplorar: pos > explorarStart && pos < explorarEnd };
}

console.log("=== TAB HEALTH ===");
for (const r of results) {
  console.log(
    `${r.ok ? "OK" : "FAIL"} ${r.url.replace(base, "")} tab=${r.tab || "?"} expect=#${r.expectId} vis=${r.visibility || "-"} h=${r.height ?? "?"} ${r.insideExplorar ? "NESTED_IN_EXPLORAR!" : ""} ${r.errors?.length ? "ERR:" + r.errors.join(";") : ""}`
  );
}
console.log("\n=== NESTING (by position) ===");
console.log(JSON.stringify(nesting, null, 2));

const failed = results.filter((r) => !r.ok);
await browser.close();
process.exit(failed.length ? 1 : 0);
