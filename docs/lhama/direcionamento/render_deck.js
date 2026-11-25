// Renderiza o deck: páginas em PNG (prévia) e/ou PDF.
// Uso: node render_deck.js <pasta-build> <saida> [png|pdf|ambos] [escala-png=0.5]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = __dirname, B = path.resolve(process.argv[2]), out = path.resolve(process.argv[3]);
  const mode = process.argv[4] || 'png', scale = +(process.argv[5] || 0.5);
  fs.mkdirSync(out, { recursive: true });
  const html = fs.readFileSync(path.join(dir, 'deck.html'), 'utf8').replace(/(src|href)="B\//g, `$1="file://${B}/`);
  const tmp = path.join(dir, '.deck-render.html');
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  const open = async (opts) => {
    const p = await b.newPage(opts);
    await p.goto('file://' + tmp, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(500);
    return p;
  };
  if (mode !== 'pdf') {
    const p = await open({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
    const pages = await p.$$('section.pg');
    for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: path.join(out, `pagina-${String(i + 1).padStart(2, '0')}.png`) });
    console.log(pages.length, 'páginas png');
  }
  if (mode !== 'png') {
    const p = await open({ viewport: { width: 1920, height: 1080 } });
    await p.pdf({ path: path.join(out, 'lhama-direcionamento-visual.pdf'), width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
    console.log('pdf ok');
  }
  await b.close();
})();
