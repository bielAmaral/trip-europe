import { chromium } from "playwright";

const urls = [
  "http://127.0.0.1:8888/#presentes",
  "http://127.0.0.1:8888/",
  "http://127.0.0.1:8888/#!mais",
];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const logs = [];
page.on("console", (m) => logs.push(`[${m.type()}] ${m.text()}`));
page.on("pageerror", (e) => logs.push(`[pageerror] ${e.message}`));

for (const url of urls) {
  logs.length = 0;
  await page.goto(url, { waitUntil: "networkidle", timeout: 15000 });
  await page.waitForTimeout(600);
  const info = await page.evaluate(() => {
    const panels = [...document.querySelectorAll("[data-app-panel]")];
    const visible = panels.filter((p) => !p.hasAttribute("hidden"));
    const hiddenReveal = visible.filter(
      (p) => p.classList.contains("reveal") && !p.classList.contains("is-visible")
    );
    const presentes = document.getElementById("presentes");
    const horarios = document.getElementById("horarios-bilhetes");
    const hero = document.getElementById("inicio-hero");
    function snap(el) {
      if (!el) return null;
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return {
        display: cs.display,
        opacity: cs.opacity,
        visibility: cs.visibility,
        height: r.height,
        top: r.top,
        hidden: el.hasAttribute("hidden"),
        isVisible: el.classList.contains("is-visible"),
      };
    }
    const bodyCs = getComputedStyle(document.body);
    const main = document.getElementById("appMain");
    const mainCs = main ? getComputedStyle(main) : null;
    return {
      url: location.href,
      tab: document.body.getAttribute("data-app-tab"),
      bodyOverflow: bodyCs.overflowY,
      bodyMaxH: bodyCs.maxHeight,
      mainOverflow: mainCs?.overflowY,
      mainH: main?.clientHeight,
      mainScrollH: main?.scrollHeight,
      visiblePanels: visible.length,
      hiddenRevealCount: hiddenReveal.length,
      hiddenRevealIds: hiddenReveal.map((p) => p.id).slice(0, 6),
      hero: snap(hero),
      horarios: snap(horarios),
      presentes: snap(presentes),
      toolbar: snap(document.querySelector(".toolbar--app")),
      textSample: (visible[0]?.innerText || "").slice(0, 60),
      scriptShell: [...document.scripts].some((s) => s.src.includes("app-shell")),
    };
  });
  console.log("\n=== " + url + " ===");
  console.log(JSON.stringify(info, null, 2));
  if (logs.length) console.log("logs:", logs.join("\n"));
}

await page.screenshot({ path: "/tmp/roteiro-blank.png", fullPage: false });
console.log("\nScreenshot: /tmp/roteiro-blank.png");
await browser.close();
