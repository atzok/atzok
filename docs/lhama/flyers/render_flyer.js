// Renderiza as seções .f de um flyer.html em PNG.
// Uso: node render_flyer.js <flyer.html> <pasta-formas-png> <saida> [escala=0.5]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const src = path.resolve(process.argv[2]), F = path.resolve(process.argv[3]), out = path.resolve(process.argv[4]);
  const scale = +(process.argv[5] || 0.5);
  fs.mkdirSync(out, { recursive: true });
  const tmp = path.join(path.dirname(src), '.render.html');
  fs.writeFileSync(tmp, fs.readFileSync(src, 'utf8').replace(/(src|href)="F\//g, `$1="file://${F}/`));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 3600, height: 1500 }, deviceScaleFactor: scale });
  await p.goto('file://' + tmp, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  for (const el of await p.$$('section.f')) {
    const id = await el.getAttribute('id');
    await el.screenshot({ path: path.join(out, `${id}.png`) });
  }
  await b.close();
  console.log('ok', out);
})();
