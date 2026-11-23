// Renderiza svg/*.svg em PNG transparente.
// Uso: node render_formas.js <pasta-saida> <lado-maior-px>
//   ex.: node render_formas.js png-baixa 700   |   node render_formas.js png-alta 4000
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = __dirname, out = path.resolve(process.argv[2] || 'png'), px = +(process.argv[3] || 700);
  fs.mkdirSync(out, { recursive: true });
  const files = fs.readdirSync(path.join(dir, 'svg')).filter(f => f.endsWith('.svg')).sort();
  const b = await chromium.launch();
  for (const f of files) {
    const svg = fs.readFileSync(path.join(dir, 'svg', f), 'utf8');
    const [, w, h] = svg.match(/viewBox="0 0 (\d+) (\d+)"/).map(Number);
    const scale = px / Math.max(w, h);
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await p.screenshot({ path: path.join(out, f.replace('.svg', '.png')), omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
    await p.close();
  }
  await b.close();
  console.log(files.length, 'png em', out);
})();
