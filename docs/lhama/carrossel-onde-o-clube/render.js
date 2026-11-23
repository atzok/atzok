const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = __dirname, out = process.argv[2] || path.join(dir, 'out'), scale = +(process.argv[3] || 1);
  require('fs').mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 1400 }, deviceScaleFactor: scale });
  await p.goto('file://' + path.join(dir, 'cards.html'));
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(300);
  for (let i = 1; i <= 6; i++) await (await p.$('#c' + i)).screenshot({ path: path.join(out, `card-0${i}.png`) });
  await b.close();
})();
