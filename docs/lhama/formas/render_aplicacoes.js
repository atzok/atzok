// Renderiza os mockups de aplicacoes.html usando os PNGs de uma pasta.
// Uso: node render_aplicacoes.js <pasta-pngs> <pasta-saida> [escala=0.5]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = __dirname, pngs = path.resolve(process.argv[2]), out = path.resolve(process.argv[3]), scale = +(process.argv[4] || 0.5);
  fs.mkdirSync(out, { recursive: true });
  const html = fs.readFileSync(path.join(dir, 'aplicacoes.html'), 'utf8').replaceAll('src="F/', `src="file://${pngs}/`);
  const tmp = path.join(dir, '.aplicacoes-render.html');
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 3500, height: 2100 }, deviceScaleFactor: scale });
  await p.goto('file://' + tmp);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  for (const id of ['a1', 'a2', 'a3']) await (await p.$('#' + id)).screenshot({ path: path.join(out, `aplicacao-${id}.png`) });
  await b.close();
  fs.unlinkSync(tmp);
  console.log('3 aplicações em', out);
})();
