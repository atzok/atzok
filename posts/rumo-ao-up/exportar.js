// Exporta cada card de cards.html como PNG 1080×1350 em out/<post>/<nn>.png
// Uso: node posts/rumo-ao-up/exportar.js
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

(async () => {
  const dir = __dirname;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1400 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(dir, "cards.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => [...document.images].every((i) => i.complete && i.naturalWidth > 0));
  const ids = await page.$$eval("section.card", (els) => els.map((e) => e.id));
  for (const id of ids) {
    const post = id.replace(/-\d\d$/, "");
    const n = id.slice(-2);
    fs.mkdirSync(path.join(dir, "out", post), { recursive: true });
    await page.locator(`[id="${id}"]`).screenshot({ path: path.join(dir, "out", post, n + ".png") });
  }
  console.log(ids.length + " cards exportados");
  await browser.close();
})();
