#!/usr/bin/env node
/** Valida expandir FAST em dias específicos (Playwright). */
import { chromium } from "playwright";

const BASE = process.env.ROTEIRO_URL || "http://127.0.0.1:9876/index.html";
const DAYS = [
  "#day-2026-11-21",
  "#day-2026-11-25",
  "#day-2026-11-29",
  "#day-2026-12-01",
  "#day-2026-12-02",
];

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
page.on("console", (m) => {
  if (m.type() === "error") errors.push(m.text());
});

const results = [];

for (const hash of DAYS) {
  await page.goto(BASE + hash, { waitUntil: "networkidle", timeout: 20000 });
  await page.waitForTimeout(800);

  const dayId = hash.replace("#", "");
  const day = page.locator(`#${dayId}`);
  await day.evaluate((el) => {
    el.open = true;
  });

  await page.waitForTimeout(400);

  const pre = await page.evaluate((id) => {
    const plan = document.getElementById("fast-" + id);
    const btn = plan?.querySelector(".fast-plan-expand__toggle");
    const macroRows = plan?.querySelectorAll(".fast-plan-table tbody tr") || [];
    const macroSample = macroRows[0]?.querySelector("td:last-child")?.textContent?.slice(0, 80) || "";
    const dayNote = plan?.querySelector(".fast-plan__day-note")?.textContent?.includes("Lavanderia");
    return {
      hasExpandBtn: !!btn,
      btnText: btn?.textContent?.trim() || "",
      panelHidden: plan?.querySelector(".fast-plan-expand__panel")?.hidden ?? true,
      summaryHidden: plan?.querySelector(".fast-plan__table-wrap")?.hidden ?? false,
      macroCount: macroRows.length,
      macroSample,
      dayNoteBerlin:
        id === "day-2026-12-01" || id === "day-2026-12-02" ? !!dayNote : null,
      hasTourMacro: [...macroRows].some((tr) => /Tour\s/i.test(tr.textContent || "")),
      hasExecutableEvening:
        id === "day-2026-12-01"
          ? [...macroRows].some((tr) => /East Side|Five Guys|Generator/i.test(tr.textContent || ""))
          : id === "day-2026-12-02"
            ? [...macroRows].some((tr) => /Alexa|Ku.damm|mala Praga/i.test(tr.textContent || ""))
            : id === "day-2026-11-29"
              ? [...macroRows].some((tr) => /Margaret|mala Berlim|100E/i.test(tr.textContent || ""))
              : id === "day-2026-11-21"
                ? [...macroRows].some((tr) => /Füssen|Flix|castelo/i.test(tr.textContent || ""))
                : [...macroRows].some((tr) => /Ring|Anker|mala Bratislava/i.test(tr.textContent || "")),
    };
  }, dayId);

  const btn = page.locator(`#fast-${dayId} .fast-plan-expand__toggle`);
  if (await btn.count()) {
    await btn.click();
    await page.waitForTimeout(500);
    await btn.click();
    await page.waitForTimeout(500);
  }

  const post = await page.evaluate((id) => {
    const plan = document.getElementById("fast-" + id);
    const panel = plan?.querySelector(".fast-plan-expand__panel");
    const expandTable = panel?.querySelector(".fast-plan-expand-table");
    const stops = expandTable?.querySelectorAll(".fast-plan-expand__stop") || [];
    const anchors = expandTable?.querySelectorAll(".fast-plan-expand__anchor") || [];
    const cutTags = expandTable?.querySelectorAll(".fast-plan-expand__tag--cut") || [];
    const transit = expandTable?.querySelectorAll(".fast-plan-expand__stop--transit") || [];
    const estimativa = expandTable?.textContent?.includes("estimativa") || false;
    const missingRouteText = expandTable?.textContent?.includes("Sem paradas") || false;
    const walkStops = [...stops].filter((tr) => tr.querySelector("strong")).length;
    return {
      panelOpen: panel && !panel.hidden,
      built: panel?.dataset?.built === "1",
      anchorCount: anchors.length,
      stopCount: stops.length,
      walkStopsWithStrong: walkStops,
      cutTagCount: cutTags.length,
      transitBlockCount: transit.length,
      hasEstimativaLabel: estimativa,
      missingRouteText,
      sampleStop: stops[0]?.textContent?.slice(0, 100) || "",
    };
  }, dayId);

  results.push({
    day: dayId,
    pre,
    post,
    ok:
      pre.hasExpandBtn &&
      pre.panelHidden === false &&
      pre.summaryHidden === true &&
      post.panelOpen &&
      post.stopCount > 5 &&
      !post.missingRouteText &&
      (dayId !== "day-2026-12-01" ||
        post.walkStopsWithStrong > 5),
  });
}

await browser.close();

const failed = results.filter((r) => !r.ok);
const out = { errors, results, pass: failed.length === 0 && errors.length === 0 };
console.log(JSON.stringify(out, null, 2));
process.exit(out.pass ? 0 : 1);
